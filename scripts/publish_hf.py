#!/usr/bin/env python3
"""Stage the desk and the seed-11 adapter, then upload them. Dry-run by default.

  uv run python scripts/publish_hf.py --dry-run
  uv run python scripts/publish_hf.py --push --only dataset
  uv run python scripts/publish_hf.py --push --only model

The model upload refuses an adapter whose test enforce loss is not the scored
run. A different number is a different experiment.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from hf_cards import (  # noqa: E402
    DATASET_REPO,
    MODEL_REPO,
    ROOT,
    GateFailed,
    collection_gates,
    load_card,
    stage_dataset,
    stage_model,
)

BUILD = ROOT / "build" / "hf"
ADAPTER = ROOT / "artifacts" / "train" / "seed-11" / "adapter"
MANIFEST = ROOT / "artifacts" / "train" / "seed-11" / "manifest.json"


def _push(repo_id: str, kind: str, folder: Path) -> None:
    from huggingface_hub import HfApi

    api = HfApi()
    api.create_repo(repo_id, repo_type=kind, exist_ok=True, private=False)
    api.upload_folder(
        folder_path=str(folder),
        repo_id=repo_id,
        repo_type=kind,
        commit_message=f"publish: {kind} from {repo_id}",
    )
    print(f"uploaded {folder} -> {repo_id}")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    mode = ap.add_mutually_exclusive_group()
    mode.add_argument("--dry-run", action="store_true", help="stage only")
    mode.add_argument("--push", action="store_true", help="upload after the gates pass")
    ap.add_argument("--only", choices=["dataset", "model"])
    args = ap.parse_args()
    if not args.dry_run and not args.push:
        args.dry_run = True

    card = load_card()
    try:
        collection_gates(card)
    except GateFailed as exc:
        print(f"gate failed: {exc}", file=sys.stderr)
        return 1

    want_dataset = args.only in (None, "dataset")
    want_model = args.only in (None, "model")

    if want_dataset:
        dest = BUILD / "proctor-desk"
        counts = stage_dataset(dest, card)
        print(f"dataset staged {counts} -> {dest}")

    if want_model:
        if not ADAPTER.is_dir() or not MANIFEST.is_file():
            print("model: seed-11 adapter is not on disk")
            if args.push:
                return 1
        else:
            manifest = json.loads(MANIFEST.read_text())
            dest = BUILD / "proctor-qlora-grpo"
            try:
                stage_model(dest, ADAPTER, manifest, card)
            except GateFailed as exc:
                print(f"model gate failed: {exc}", file=sys.stderr)
                return 1
            print(f"model staged seed {manifest['model_seed']} -> {dest}")

    if args.dry_run:
        print("dry run: nothing uploaded")
        return 0

    if want_dataset:
        _push(DATASET_REPO, "dataset", BUILD / "proctor-desk")
    if want_model and (BUILD / "proctor-qlora-grpo").is_dir():
        _push(MODEL_REPO, "model", BUILD / "proctor-qlora-grpo")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
