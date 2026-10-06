#!/usr/bin/env python3
"""Every backticked repo path in the docs must exist, or be declared planned."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = [*ROOT.glob("*.md"), *ROOT.glob("docs/**/*.md")]
TOP_DIRS = (
    "docs",
    "scripts",
    "schema",
    "forge",
    "oracle",
    "eval",
    "baselines",
    "model",
    "cloud",
    "tests",
    "artifacts",
)
TOP_FILES = {
    "README.md",
    "CONTRACTS.md",
    "AGENTS.md",
    "LICENSE",
    "llms.txt",
    "Makefile",
    "pyproject.toml",
    ".env.example",
    ".gitignore",
    "MEASUREMENT_CARD.json",
    "uv.lock",
}
PATH_RE = re.compile(r"`([^`\n]+)`")


def planned() -> tuple[set[str], tuple[str, ...]]:
    handoff = ROOT / "docs" / "HANDOFF.md"
    exact: set[str] = set()
    prefixes: list[str] = []
    if not handoff.exists():
        return exact, tuple(prefixes)
    for line in handoff.read_text().splitlines():
        if "planned:" not in line:
            continue
        payload = line.split("planned:", 1)[1]
        for raw in payload.split(","):
            token = raw.strip().strip("`").strip()
            if not token:
                continue
            if token.endswith("/"):
                prefixes.append(token)
            else:
                exact.add(token)
    return exact, tuple(prefixes)


def is_repo_path(token: str) -> bool:
    if any(ch in token for ch in "*<>{}|"):
        return False
    if token.startswith(("http://", "https://", "/")):
        return False
    if " " in token:
        return False
    if token in TOP_FILES:
        return True
    head = token.split("/", 1)[0]
    return "/" in token and head in TOP_DIRS


def main() -> int:
    exact, prefixes = planned()
    missing: dict[str, str] = {}
    for doc in DOCS:
        text = doc.read_text()
        for match in PATH_RE.finditer(text):
            raw = match.group(1).strip()
            token = raw[:-1] if raw.endswith("/") and raw != "/" else raw
            if not is_repo_path(token) or token in missing:
                continue
            covered = (ROOT / token).exists() or token in exact
            if not covered:
                covered = any(token.startswith(prefix) for prefix in prefixes)
            if covered:
                continue
            missing[token] = str(doc.relative_to(ROOT))
    for token, doc in sorted(missing.items()):
        print(f"check-paths: {doc} names `{token}` which does not exist and is not planned")
    if missing:
        print("check-paths: failed", file=sys.stderr)
        return 1
    print("check-paths: clean")
    return 0


if __name__ == "__main__":
    sys.exit(main())
