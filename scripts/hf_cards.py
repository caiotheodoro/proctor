"""Render the Hub cards from MEASUREMENT_CARD.json and stage the desk."""

from __future__ import annotations

import json
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CARD_PATH = ROOT / "MEASUREMENT_CARD.json"

ACCOUNT = "caiotheodoro"
DATASET_REPO = f"{ACCOUNT}/proctor-desk"
MODEL_REPO = f"{ACCOUNT}/proctor-qlora-grpo"
GITHUB = "https://github.com/caiotheodoro/proctor"
TAG = "v0.1.0"
CODE = f"{GITHUB}/tree/{TAG}"
SCORED_SEED = 11
SCORED_LOSS = 720 / 252
DESCRIPTION_LIMIT = 150
NOTE_LIMIT = 500
TITLE = "Proctor: oracle-priced agent actions"
DISCLAIMERS = ("synthetic", "not production-validated")
SECRET = re.compile(r"(sk-[A-Za-z0-9]{20,}|Bearer [A-Za-z0-9._-]{20,}|AKIA[0-9A-Z]{16}|oc_sk_)")
ADAPTER_FILES = ("adapter_config.json", "adapter_model.safetensors")

_MOUNTED = False


class GateFailed(RuntimeError):
    """A publish gate failed. Nothing is uploaded."""


def load_card() -> dict:
    return json.loads(CARD_PATH.read_text())


def _published(card: dict) -> dict:
    return card["results"]["published"]


def collection_description(card: dict) -> str:
    pub = _published(card)
    return (
        f"schema_only - flag_everything = {pub['h1_diff']:.2f}, "
        f"95% CI [{pub['h1_lo']:.2f}, {pub['h1_hi']:.2f}]. "
        f"Synthetic, not production-validated. {GITHUB}"
    )


def dataset_note(card: dict) -> str:
    contract = card["contract"]
    pub = _published(card)
    return (
        f"{contract['train_tasks']} train (seed {contract['train_seed']}), "
        f"{contract['dev_tasks']} dev (seed {contract['dev_seed']}), "
        f"{contract['test_tasks']} test (seed {contract['test_seed']}, never trained on). "
        f"Eight tools, six violation classes, oracle labels on every row.\n\n"
        f"schema_only enforce loss {pub['schema_enforce']:.2f} against "
        f"flag_everything {pub['flag_enforce']:.2f}. Paired difference "
        f"{pub['h1_diff']:.2f}, 95% CI [{pub['h1_lo']:.2f}, {pub['h1_hi']:.2f}]. "
        f"The trained arm is {pub['trained_enforce']:.2f}, standard deviation "
        f"{pub['trained_std']:.1f}, and is not a win.\n\n"
        f"Synthetic traces. {card['limitation']}"
    )


def model_note(card: dict) -> str:
    pub = _published(card)
    return (
        "A negative result, published so the row is checkable.\n\n"
        f"Seeds 11, 22, 33, and 44 each scored enforce loss {pub['trained_enforce']:.2f}, "
        f"standard deviation {pub['trained_std']:.1f}, which is {pub['h4_gap']:.2f} above "
        "schema_only. H4 does not hold. This repo is the seed-11 adapter from a "
        "same-recipe rerun. It is uploaded only when that rerun's test loss matches "
        "the scored run.\n\n"
        "Alone it reads as a failed upload. Next to the desk it is the row that "
        "did not beat the schema check."
    )


def _mount() -> None:
    global _MOUNTED
    if _MOUNTED:
        return
    for rel in (
        "schema",
        "forge",
        "oracle",
        "eval",
        "baselines/schema_check",
        "baselines/judge",
        "model",
    ):
        path = str(ROOT / rel)
        if path not in sys.path:
            sys.path.insert(0, path)
    _MOUNTED = True


def _cell(task_id: str, split: str) -> str:
    prefix = f"{split}-"
    if not task_id.startswith(prefix):
        raise GateFailed(f"task id {task_id} is not in split {split}")
    cell, index = task_id[len(prefix) :].rsplit("-", 1)
    if not index.isdigit() or not cell:
        raise GateFailed(f"task id {task_id} has no cell")
    return cell


def dataset_card(card: dict, counts: dict[str, int]) -> str:
    contract = card["contract"]
    pub = _published(card)
    body = "\n".join(
        [
            "Synthetic operations-desk traces with oracle violation labels. "
            f"{card['limitation']} Synthetic, not production-validated.",
            "",
            f"Code: {CODE}",
            "",
            (
                f"Protocol {contract['protocol']}. "
                f"Train seed {contract['train_seed']}, {counts['train']} tasks. "
                f"Dev seed {contract['dev_seed']}, {counts['dev']} tasks. "
                f"Test seed {contract['test_seed']}, {counts['test']} tasks. "
                f"Seed {contract['test_seed']} is not a training seed."
            ),
            "",
            (
                "On the test split, schema_only enforce loss is "
                f"{pub['schema_enforce']:.2f} and flag_everything is "
                f"{pub['flag_enforce']:.2f}. The paired difference is "
                f"{pub['h1_diff']:.2f}, 95% CI "
                f"[{pub['h1_lo']:.2f}, {pub['h1_hi']:.2f}]. "
                "The trained arm's enforce loss is "
                f"{pub['trained_enforce']:.2f}, across-seed standard deviation "
                f"{pub['trained_std']:.1f}, gap {pub['h4_gap']:.2f}. "
                f"H4 does not hold. The judge recorded {pub['judge_parse_misses']} "
                "parse misses."
            ),
            "",
            "Eight tools, six violation classes. "
            "Each row is one task and the trace the oracle scored.",
            "",
        ]
    )
    return (
        "---\n"
        "license: apache-2.0\n"
        "language:\n"
        "- en\n"
        "tags:\n"
        "- synthetic\n"
        "size_categories:\n"
        "- n<1K\n"
        "pretty_name: Proctor desk\n"
        "---\n"
        "\n"
        "# Proctor desk\n"
        "\n"
        f"{body}"
    )


def model_card(card: dict) -> str:
    pub = _published(card)
    body = "\n".join(
        [
            "A negative result. The adapter does not beat schema_only.",
            "",
            (
                "Four seeds (11, 22, 33, 44) scored test enforce loss "
                f"{pub['trained_enforce']:.2f} with standard deviation "
                f"{pub['trained_std']:.1f}. The gap above schema_only "
                f"({pub['schema_enforce']:.2f}) is {pub['h4_gap']:.2f}, so H4 does not hold. "
                f"This repository is seed {SCORED_SEED}. "
                "The other three checkpoints were not kept. "
                "This file is a same-recipe rerun, and it is uploaded only when "
                "its test enforce loss matches the scored run."
            ),
            "",
            (
                "Base model Qwen/Qwen2.5-1.5B-Instruct. QLoRA rank 8, alpha 16, "
                "dropout 0.05, targets q_proj and v_proj. "
                "Supervised pass 20 steps, then GRPO 10 steps. Seed 999 was excluded."
            ),
            "",
            f"{card['limitation']} Synthetic, not production-validated.",
            "",
            f"Code: {CODE}",
            "",
        ]
    )
    return (
        "---\n"
        "license: apache-2.0\n"
        "base_model: Qwen/Qwen2.5-1.5B-Instruct\n"
        "library_name: peft\n"
        "tags:\n"
        "- lora\n"
        "- synthetic\n"
        "---\n"
        "\n"
        f"# Proctor QLoRA-GRPO, seed {SCORED_SEED}\n"
        "\n"
        f"{body}"
    )


def assert_surface(text: str, card: dict) -> None:
    missing = [item for item in DISCLAIMERS if item not in text.lower()]
    if missing:
        raise GateFailed(f"missing disclaimer: {missing}")
    if card["limitation"] not in text:
        raise GateFailed("limitation is not on the card")
    if CODE not in text:
        raise GateFailed("card does not cite the pinned tag")
    if "/main" in text:
        raise GateFailed("card cites a moving revision")
    if SECRET.search(text):
        raise GateFailed("secret-shaped string on a card")


def assert_card_state(card: dict) -> None:
    if card.get("verdict") != "VERIFIED":
        raise GateFailed("card is not VERIFIED")
    if card.get("unmet"):
        raise GateFailed(f"card still has unmet claims: {card['unmet']}")
    if card["results"]["h4"]["holds"]:
        raise GateFailed("H4 holds; this publish is the negative result")
    pub = _published(card)
    for key in ("h1_diff", "schema_enforce", "flag_enforce", "trained_enforce", "h4_gap"):
        if key not in pub:
            raise GateFailed(f"published.{key} missing")


def collection_gates(card: dict) -> None:
    assert_card_state(card)
    desc = collection_description(card)
    if len(desc) > DESCRIPTION_LIMIT:
        raise GateFailed(f"description is {len(desc)} chars")
    if GITHUB not in desc:
        raise GateFailed("description does not cite the repository")
    missing = [item for item in DISCLAIMERS if item not in desc.lower()]
    if missing:
        raise GateFailed(f"description missing {missing}")
    diff = f"{_published(card)['h1_diff']:.2f}"
    if diff not in desc:
        raise GateFailed("description dropped the derived difference")
    for note in (dataset_note(card), model_note(card)):
        if len(note) > NOTE_LIMIT:
            raise GateFailed(f"note is {len(note)} chars")


def stage_dataset(dest: Path, card: dict | None = None) -> dict[str, int]:
    _mount()
    from proctor_forge import generate
    from proctor_schema import CELLS, SPLITS

    card = load_card() if card is None else card
    assert_card_state(card)
    dest.mkdir(parents=True, exist_ok=True)
    counts: dict[str, int] = {}
    signatures: dict[str, set[str]] = {}
    for split, spec in SPLITS.items():
        rows = generate(split)
        if len(rows) != spec["per_cell"] * len(CELLS):
            raise GateFailed(f"{split} has {len(rows)} rows")
        signatures[split] = set()
        target = dest / f"{split}.jsonl"
        lines: list[str] = []
        for task, trace in rows:
            if task.signature in signatures[split]:
                raise GateFailed(f"duplicate signature in {split}")
            signatures[split].add(task.signature)
            payload = {
                "cell": _cell(task.task_id, split),
                "split": split,
                "task": task.model_dump(mode="json", by_alias=True),
                "trace": trace.model_dump(mode="json"),
            }
            lines.append(json.dumps(payload, sort_keys=True, separators=(",", ":")))
        target.write_text("\n".join(lines) + "\n")
        counts[split] = len(rows)
    contract = card["contract"]
    expected = {
        "train": contract["train_tasks"],
        "dev": contract["dev_tasks"],
        "test": contract["test_tasks"],
    }
    if counts != expected:
        raise GateFailed(f"counts {counts} do not match the card {expected}")
    overlap = set.intersection(*signatures.values()) if signatures else set()
    if overlap:
        raise GateFailed(f"splits share {len(overlap)} signatures")
    body = target_text(dest)
    if SECRET.search(body):
        raise GateFailed("secret-shaped string in the staged desk")
    readme = dataset_card(card, counts)
    assert_surface(readme, card)
    (dest / "README.md").write_text(readme)
    return counts


def target_text(dest: Path) -> str:
    parts = []
    for path in sorted(dest.glob("*.jsonl")):
        parts.append(path.read_text())
    return "\n".join(parts)


def scored_loss_ok(value: float) -> bool:
    return abs(float(value) - SCORED_LOSS) < 1e-9


def assert_scored_manifest(manifest: dict) -> None:
    if manifest.get("backend") != "qlora-grpo":
        raise GateFailed("manifest backend is not qlora-grpo")
    if manifest.get("model_seed") != SCORED_SEED:
        raise GateFailed(f"manifest seed is not {SCORED_SEED}")
    if manifest.get("data_seed_excluded") != 999:
        raise GateFailed("manifest did not exclude seed 999")
    loss = manifest.get("test_enforce_loss")
    if not isinstance(loss, (int, float)) or isinstance(loss, bool):
        raise GateFailed("manifest has no float test_enforce_loss")
    if not scored_loss_ok(loss):
        raise GateFailed(f"loss {loss} is not the scored run")


def stage_model(dest: Path, adapter_dir: Path, manifest: dict, card: dict | None = None) -> None:
    card = load_card() if card is None else card
    assert_card_state(card)
    assert_scored_manifest(manifest)
    dest.mkdir(parents=True, exist_ok=True)
    for name in ADAPTER_FILES:
        src = adapter_dir / name
        if not src.is_file() or src.stat().st_size <= 0:
            raise GateFailed(f"adapter is missing {name}")
    for item in adapter_dir.iterdir():
        if item.is_file():
            shutil.copyfile(item, dest / item.name)
    readme = model_card(card)
    assert_surface(readme, card)
    (dest / "README.md").write_text(readme)
