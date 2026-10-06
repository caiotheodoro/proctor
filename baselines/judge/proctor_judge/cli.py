"""Run the judge on a split. A missing server is a missing arm, not a score of zero."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from proctor_eval.score import bootstrap_mean, task_loss
from proctor_forge import generate
from proctor_schema import JUDGE_MODEL

from proctor_judge.judge import judge, live_from_env

ROOT = Path(__file__).resolve().parents[3]


def run(split: str = "test") -> dict:
    transport, model, override = live_from_env()
    rows = generate(split)
    preds = []
    misses = 0
    for task, trace in rows:
        pred, missed = judge(task, trace, transport)
        preds.append(pred)
        misses += int(missed)
    losses = {"audit": [], "enforce": []}
    for (task, _), pred in zip(rows, preds, strict=True):
        for profile in ("audit", "enforce"):
            losses[profile].append(task_loss(task.violations, pred, profile))
    return {
        "losses": {profile: bootstrap_mean(values) for profile, values in losses.items()},
        "model": model,
        "n": len(rows),
        "override": override,
        "parse_misses": misses,
        "pinned_model": JUDGE_MODEL,
        "split": split,
    }


def main(argv: list[str] | None = None) -> None:
    args = argv if argv is not None else sys.argv[1:]
    split = "test"
    if "--split" in args:
        split = args[args.index("--split") + 1]
    try:
        payload = run(split)
    except RuntimeError as exc:
        blocked = ROOT / "artifacts" / "judge" / "BLOCKED.json"
        blocked.parent.mkdir(parents=True, exist_ok=True)
        blocked.write_text(json.dumps({"reason": str(exc)}, indent=2) + "\n")
        print(str(exc), file=sys.stderr)
        raise SystemExit(0) from exc
    out = ROOT / "artifacts" / "judge" / f"{split}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(out)


if __name__ == "__main__":
    main()
