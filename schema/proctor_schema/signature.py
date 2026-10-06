"""Task signature. SHA-256 over canonical JSON of the ground-truth fields."""

from __future__ import annotations

import hashlib
from typing import Any

from proctor_schema.fixture import canonical_json, public_fixture
from proctor_schema.types import Violation


def signature(request: dict[str, Any], fixture: dict[str, Any], violations: list[Violation]) -> str:
    ordered = sorted(violations, key=lambda item: item.sort_key())
    payload = {
        "fixture_public": public_fixture(fixture),
        "request": request,
        "violations": [
            {"call_index": item.call_index, "class": item.klass, "severity": item.severity}
            for item in ordered
        ],
    }
    return hashlib.sha256(canonical_json(payload).encode()).hexdigest()
