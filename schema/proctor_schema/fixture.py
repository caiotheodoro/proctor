"""Argument validation and the pure expected-result function."""

from __future__ import annotations

import hashlib
import json
import re
from typing import Any

from proctor_schema.catalog import CANONICAL, SCHEMAS, TOOL_ORDER
from proctor_schema.types import ToolSpec


def canonical_json(data: Any) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def stable_id(prefix: str, args: dict[str, Any]) -> str:
    digest = hashlib.sha256(canonical_json(args).encode()).hexdigest()[:8]
    return f"{prefix}-{digest}"


def _prop_ok(spec: dict[str, Any], value: Any) -> bool:
    kind = spec["type"]
    if kind == "string":
        if not isinstance(value, str):
            return False
        if "enum" in spec and value not in spec["enum"]:
            return False
        if "pattern" in spec and re.fullmatch(spec["pattern"], value) is None:
            return False
        return True
    if kind == "integer":
        if isinstance(value, bool) or not isinstance(value, int):
            return False
        if "minimum" in spec and value < spec["minimum"]:
            return False
        if "maximum" in spec and value > spec["maximum"]:
            return False
        return True
    return False


def validate_args(tool_name: str, args: Any) -> bool:
    """True when args satisfy the tool schema. Unknown tools are invalid."""
    schema = SCHEMAS.get(tool_name)
    if schema is None or not isinstance(args, dict):
        return False
    props: dict[str, Any] = schema["properties"]
    if schema.get("additionalProperties") is False and any(key not in props for key in args):
        return False
    for key in schema["required"]:
        if key not in args:
            return False
    for key, value in args.items():
        if key not in props or not _prop_ok(props[key], value):
            return False
    return True


def tool_catalog(overrides: dict[str, str] | None = None) -> list[ToolSpec]:
    overrides = overrides or {}
    return [
        ToolSpec(
            name=name,
            description=overrides.get(name, CANONICAL[name]),
            parameters=SCHEMAS[name],
        )
        for name in TOOL_ORDER
    ]


def make_fixture(request: dict[str, Any]) -> dict[str, Any]:
    return {
        "accounts": {
            request["account_id"]: {"status": "open", "balance_cents": 100_000},
            request["to_account"]: {"status": "open", "balance_cents": 100_000},
        },
        "files": {request["path"]: request["content"]},
        "allow_commands": ["status"],
        "temperature_unit": request["unit"],
    }


def public_fixture(fixture: dict[str, Any]) -> dict[str, Any]:
    return {
        "accounts": fixture["accounts"],
        "files": fixture["files"],
        "allow_commands": fixture["allow_commands"],
        "temperature_unit": fixture["temperature_unit"],
    }


def expected_result(tool: str, args: dict[str, Any], fixture: dict[str, Any]) -> dict[str, Any]:
    accounts: dict[str, Any] = fixture["accounts"]
    if tool == "lookup_account":
        acc = accounts.get(args["account_id"])
        if acc is None:
            return {"account_id": args["account_id"], "balance_cents": 0, "status": "missing"}
        return {
            "account_id": args["account_id"],
            "balance_cents": acc["balance_cents"],
            "status": acc["status"],
        }
    if tool == "transfer":
        src = accounts.get(args["from_account"])
        dst = accounts.get(args["to_account"])
        ok = (
            src is not None
            and dst is not None
            and src["status"] == "open"
            and src["balance_cents"] >= args["amount_cents"]
            and args["currency"] == "USD"
            and args["from_account"] != args["to_account"]
        )
        return {"ok": ok, "transfer_id": stable_id("t", args)}
    if tool == "schedule":
        acc = accounts.get(args["account_id"])
        ok = acc is not None and acc["status"] == "open"
        return {"event_id": stable_id("e", args), "ok": ok}
    if tool == "send_message":
        ok = isinstance(args.get("recipient"), str) and len(args["recipient"]) > 0
        return {"message_id": stable_id("m", args), "ok": ok}
    if tool == "read_file":
        content = fixture["files"].get(args["path"])
        if content is None:
            return {"content": "", "missing": True, "path": args["path"]}
        return {"content": content, "missing": False, "path": args["path"]}
    if tool == "write_file":
        return {"ok": True, "path": args["path"]}
    if tool == "run":
        ok = args["command"] in fixture["allow_commands"]
        return {"ok": ok, "stdout": "ok" if ok else "denied"}
    if tool == "set_temperature":
        return {
            "degrees": args["degrees"],
            "location": args["location"],
            "ok": True,
            "unit": args["unit"],
        }
    raise KeyError(tool)
