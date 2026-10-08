"""Score the model-free arms and write the card."""

from __future__ import annotations

import json
import statistics
import sys
from pathlib import Path

from proctor_forge import generate
from proctor_schema_check import schema_only

from proctor_eval.score import (
    bootstrap_mean,
    build_card,
    flag_everything,
    paired_diff,
    recall,
    task_loss,
    write_card,
)

ROOT = Path(__file__).resolve().parents[2]
ARTIFACTS = ROOT / "artifacts"


def _round(value: float) -> float:
    return round(value, 6)


def _arm_block(values_by_profile: dict[str, list[float]]) -> dict:
    return {
        profile: {key: _round(val) for key, val in bootstrap_mean(values).items()}
        for profile, values in values_by_profile.items()
    }


def score_baselines() -> dict:
    rows = generate("test")
    golds = [task.violations for task, _ in rows]
    flag_preds = [flag_everything(task, trace) for task, trace in rows]
    schema_preds = [schema_only(task, trace) for task, trace in rows]
    flag_losses = {"audit": [], "enforce": []}
    schema_losses = {"audit": [], "enforce": []}
    for gold, flag_pred, schema_pred in zip(golds, flag_preds, schema_preds, strict=True):
        for profile in ("audit", "enforce"):
            flag_losses[profile].append(task_loss(gold, flag_pred, profile))
            schema_losses[profile].append(task_loss(gold, schema_pred, profile))
    h1 = paired_diff(schema_losses["enforce"], flag_losses["enforce"])
    schema_audit = bootstrap_mean(schema_losses["audit"])
    h3_break = recall(golds, schema_preds, "schema_break")
    h3_unit = recall(golds, schema_preds, "wrong_unit")
    results = {
        "flag_everything": _arm_block(flag_losses),
        "h1": {
            "diff": _round(float(h1["diff"])),
            "hi": _round(float(h1["hi"])),
            "holds": bool(h1["holds"]),
            "lo": _round(float(h1["lo"])),
        },
        "h2": {
            "holds": schema_audit["mean"] > 0,
            "mean": _round(schema_audit["mean"]),
        },
        "h3": {
            "holds": h3_break == 1 and h3_unit == 0,
            "schema_break_recall": h3_break,
            "wrong_unit_recall": h3_unit,
        },
        "n": len(rows),
        "schema_only": _arm_block(schema_losses),
        "split": "test",
    }
    results["published"] = {
        "flag_audit": round(results["flag_everything"]["audit"]["mean"], 2),
        "flag_enforce": round(results["flag_everything"]["enforce"]["mean"], 2),
        "h1_diff": round(results["h1"]["diff"], 2),
        "h1_hi": round(results["h1"]["hi"], 2),
        "h1_lo": round(results["h1"]["lo"], 2),
        "schema_audit": round(results["schema_only"]["audit"]["mean"], 2),
        "schema_enforce": round(results["schema_only"]["enforce"]["mean"], 2),
    }
    return results


def trained_losses(artifacts: Path) -> list[float] | None:
    """Enforce losses for seeds 11, 22, 33, 44, or None when any manifest is unfit."""
    losses: list[float] = []
    for seed in (11, 22, 33, 44):
        path = artifacts / "train" / f"seed-{seed}" / "manifest.json"
        if not path.exists():
            return None
        item = json.loads(path.read_text())
        loss = item.get("test_enforce_loss")
        if (
            item.get("backend") != "qlora-grpo"
            or item.get("data_seed_excluded") != 999
            or not isinstance(loss, float)
        ):
            return None
        losses.append(loss)
    return losses


def unmet_claims(artifacts: Path) -> list[str]:
    unmet = []
    judge = artifacts / "judge" / "test.json"
    if not judge.exists():
        unmet.append(
            "judge arm has not been run against the pinned model Qwen/Qwen2.5-1.5B-Instruct"
        )
    else:
        payload = json.loads(judge.read_text())
        if payload.get("model") != "Qwen/Qwen2.5-1.5B-Instruct" or payload.get("override"):
            unmet.append("judge artifact is not the pinned model without an override")
    if trained_losses(artifacts) is None:
        unmet.append(
            "trained arm across-seed standard deviation is absent; "
            "four qlora-grpo manifests are required and seed 999 stays untouched"
        )
    return unmet


def attach_trained(results: dict | None, artifacts: Path) -> dict | None:
    losses = trained_losses(artifacts)
    if results is None or losses is None:
        return results
    schema_mean = float(results["schema_only"]["enforce"]["mean"])
    mean = sum(losses) / len(losses)
    spread = statistics.stdev(losses)
    gap = mean - schema_mean
    out = dict(results)
    out["h4"] = {
        "gap": _round(gap),
        "holds": (schema_mean - mean) > spread,
        "losses": [_round(loss) for loss in losses],
        "mean": _round(mean),
        "std": _round(spread),
    }
    published = dict(out.get("published") or {})
    published["h4_gap"] = round(gap, 2)
    published["trained_enforce"] = round(mean, 2)
    published["trained_std"] = round(spread, 2)
    out["published"] = published
    return out


def attach_judge(results: dict | None, artifacts: Path) -> dict | None:
    path = artifacts / "judge" / "test.json"
    if results is None or not path.exists():
        return results
    payload = json.loads(path.read_text())
    if (
        payload.get("model") != "Qwen/Qwen2.5-1.5B-Instruct"
        or payload.get("override")
        or payload.get("split") != "test"
    ):
        return results
    out = dict(results)
    audit = payload["losses"]["audit"]
    enforce = payload["losses"]["enforce"]
    out["judge"] = {
        "audit": {key: _round(float(val)) for key, val in audit.items()},
        "enforce": {key: _round(float(val)) for key, val in enforce.items()},
        "model": payload["model"],
        "n": payload["n"],
        "override": False,
        "parse_misses": payload["parse_misses"],
    }
    published = dict(out.get("published") or {})
    published["judge_audit"] = round(float(audit["mean"]), 2)
    published["judge_enforce"] = round(float(enforce["mean"]), 2)
    published["judge_parse_misses"] = payload["parse_misses"]
    out["published"] = published
    return out


def emit_card(results: dict | None = None) -> None:
    ARTIFACTS.mkdir(parents=True, exist_ok=True)
    if results is None and (ARTIFACTS / "baselines.json").exists():
        results = json.loads((ARTIFACTS / "baselines.json").read_text())
    scored = attach_judge(attach_trained(results, ARTIFACTS), ARTIFACTS)
    payload = build_card(scored, unmet_claims(ARTIFACTS))
    write_card(payload)


def baselines() -> None:
    results = score_baselines()
    ARTIFACTS.mkdir(parents=True, exist_ok=True)
    (ARTIFACTS / "baselines.json").write_text(json.dumps(results, indent=2, sort_keys=True) + "\n")
    (ARTIFACTS / "flag_everything.json").write_text(
        json.dumps(results["flag_everything"], indent=2, sort_keys=True) + "\n"
    )
    (ARTIFACTS / "schema_only.json").write_text(
        json.dumps(results["schema_only"], indent=2, sort_keys=True) + "\n"
    )
    emit_card(results)


def main(argv: list[str] | None = None) -> None:
    command = (argv or sys.argv[1:])[:1]
    if command == ["baselines"]:
        baselines()
        return
    if command == ["card"]:
        emit_card()
        return
    raise SystemExit("usage: python -m proctor_eval.cli baselines|card")


if __name__ == "__main__":
    main()
