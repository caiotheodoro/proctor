#!/usr/bin/env python3
"""Group the desk and the adapter into one Hugging Face collection.

Dry-run by default. --push requires both Hub repos to already exist.

  uv run python scripts/publish_collection.py
  uv run python scripts/publish_collection.py --push
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from hf_cards import (  # noqa: E402
    ACCOUNT,
    DATASET_REPO,
    GITHUB,
    MODEL_REPO,
    NOTE_LIMIT,
    TITLE,
    GateFailed,
    collection_description,
    collection_gates,
    dataset_note,
    load_card,
    model_note,
)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--push", action="store_true")
    args = ap.parse_args()
    card = load_card()
    try:
        collection_gates(card)
    except GateFailed as exc:
        print(f"gate failed: {exc}", file=sys.stderr)
        return 1

    desc = collection_description(card)
    items = (
        (DATASET_REPO, "dataset", dataset_note(card)),
        (MODEL_REPO, "model", model_note(card)),
    )
    print(f"{TITLE}\n{desc}\n({len(desc)} chars)")
    for repo, kind, note in items:
        print(f"  {kind:8} {repo}  note {len(note)}/{NOTE_LIMIT}")
    if GITHUB not in desc:
        print("description dropped the repository", file=sys.stderr)
        return 1
    if not args.push:
        print("dry run: nothing sent")
        return 0

    from huggingface_hub import (
        HfApi,
        add_collection_item,
        create_collection,
        get_collection,
        update_collection_metadata,
    )

    api = HfApi()
    for repo, kind, _note in items:
        api.repo_info(repo, repo_type=kind)
    collection = create_collection(TITLE, namespace=ACCOUNT, description=desc, exists_ok=True)
    slug = collection.slug
    update_collection_metadata(slug, description=desc)
    for repo, kind, note in items:
        add_collection_item(slug, item_id=repo, item_type=kind, note=note, exists_ok=True)
    fresh = get_collection(slug)
    print(f"https://huggingface.co/collections/{slug}")
    print(f"items: {len(fresh.items)}")
    if len(fresh.items) < len(items):
        print(f"expected at least {len(items)} items, got {len(fresh.items)}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
