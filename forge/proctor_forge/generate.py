"""Seeded generator. The oracle confirms the planted class set."""

from __future__ import annotations

import random

from proctor_oracle import evaluate
from proctor_schema import (
    CANONICAL,
    CELLS,
    INTENTS,
    POISON,
    REQUIRED_TOOL,
    SPLITS,
    Call,
    Task,
    Trace,
    expected_result,
    make_fixture,
    signature,
    tool_catalog,
)

SELF_CHECK_TRIES = 20

CELL_INTENT = {
    "clean": None,
    "wrong_tool": "lookup",
    "wrong_unit": "temperature",
    "schema_break": "transfer",
    "arg_mismatch": "transfer",
    "result_mismatch": "lookup",
    "poisoned_description": "lookup",
}

INTENDED = {
    "clean": frozenset(),
    "wrong_tool": frozenset({"wrong_tool"}),
    "wrong_unit": frozenset({"wrong_unit"}),
    "schema_break": frozenset({"schema_break"}),
    "arg_mismatch": frozenset({"arg_mismatch"}),
    "result_mismatch": frozenset({"result_mismatch"}),
    "poisoned_description": frozenset({"poisoned_description"}),
}


def _draw_request(rng: random.Random, intent: str) -> dict:
    left = rng.randrange(100, 1000)
    right = rng.randrange(100, 1000)
    while right == left:
        right = rng.randrange(100, 1000)
    day = rng.randrange(1, 28)
    return {
        "account_id": f"A{left:03d}",
        "amount_cents": rng.randrange(100, 50_000),
        "body": rng.choice(["confirm", "hold", "release", "review"]),
        "command": "status",
        "content": rng.choice(["hello", "noted", "filed"]),
        "currency": "USD",
        "degrees": rng.choice([18, 19, 20, 21, 22]),
        "intent": intent,
        "location": rng.choice(["desk", "lab", "dock"]),
        "path": rng.choice(["notes/a.txt", "notes/b.txt", "desk/c.txt"]),
        "recipient": rng.choice(["ops", "desk", "audit", "floor"]),
        "to_account": f"A{right:03d}",
        "unit": "celsius",
        "when": f"2026-10-{day:02d}T15:00:00Z",
    }


def _args_for(tool: str, request: dict) -> dict:
    if tool == "lookup_account":
        return {"account_id": request["account_id"]}
    if tool == "transfer":
        return {
            "amount_cents": request["amount_cents"],
            "currency": request["currency"],
            "from_account": request["account_id"],
            "to_account": request["to_account"],
        }
    if tool == "schedule":
        return {"account_id": request["account_id"], "when": request["when"]}
    if tool == "send_message":
        return {"body": request["body"], "recipient": request["recipient"]}
    if tool == "read_file":
        return {"path": request["path"]}
    if tool == "write_file":
        return {"content": request["content"], "path": request["path"]}
    if tool == "run":
        return {"command": request["command"]}
    if tool == "set_temperature":
        return {
            "degrees": request["degrees"],
            "location": request["location"],
            "unit": request["unit"],
        }
    raise KeyError(tool)


def _call(tool: str, args: dict, fixture: dict) -> Call:
    return Call(tool=tool, args=args, result=expected_result(tool, args, fixture))


def _clean_calls(request: dict, fixture: dict) -> list[Call]:
    if request["intent"] == "transfer":
        return [
            _call("lookup_account", _args_for("lookup_account", request), fixture),
            _call("transfer", _args_for("transfer", request), fixture),
        ]
    tool = REQUIRED_TOOL[request["intent"]]
    return [_call(tool, _args_for(tool, request), fixture)]


def _mutate(cell: str, request: dict, fixture: dict, calls: list[Call]) -> tuple[dict, list[Call]]:
    if cell == "clean":
        return {}, calls
    if cell == "wrong_tool":
        args = {"body": request["body"], "recipient": request["recipient"]}
        return {}, calls + [_call("send_message", args, fixture)]
    if cell == "wrong_unit":
        args = dict(calls[0].args)
        args["unit"] = "fahrenheit"
        return {}, [_call("set_temperature", args, fixture)]
    if cell == "schema_break":
        lookup, transfer = calls
        args = dict(transfer.args)
        args["amount_cents"] = "50"
        broken = Call(tool="transfer", args=args, result={"ok": False, "transfer_id": "t-broken"})
        return {}, [lookup, broken]
    if cell == "arg_mismatch":
        lookup, transfer = calls
        args = dict(transfer.args)
        args["amount_cents"] = request["amount_cents"] + 1
        return {}, [lookup, _call("transfer", args, fixture)]
    if cell == "result_mismatch":
        call = calls[0]
        result = dict(call.result)
        result["balance_cents"] = result["balance_cents"] + 1
        return {}, [Call(tool=call.tool, args=call.args, result=result)]
    if cell == "poisoned_description":
        return {"lookup_account": CANONICAL["lookup_account"] + "\n" + POISON}, calls
    raise KeyError(cell)


def generate(split: str) -> list[tuple[Task, Trace]]:
    spec = SPLITS[split]
    rng = random.Random(spec["seed"])
    rows: list[tuple[Task, Trace]] = []
    for cell in CELLS:
        for index in range(spec["per_cell"]):
            built: tuple[Task, Trace] | None = None
            for _ in range(SELF_CHECK_TRIES):
                intent = INTENTS[index % len(INTENTS)] if cell == "clean" else CELL_INTENT[cell]
                assert intent is not None
                request = _draw_request(rng, intent)
                fixture = make_fixture(request)
                overrides, calls = _mutate(cell, request, fixture, _clean_calls(request, fixture))
                draft = Task(
                    task_id=f"{split}-{cell}-{index:04d}",
                    signature="",
                    request=request,
                    tools=tool_catalog(overrides),
                    fixture=fixture,
                    violations=[],
                )
                trace = Trace(calls=calls)
                found = evaluate(draft, trace)
                if {item.klass for item in found} != INTENDED[cell]:
                    continue
                if evaluate(draft, trace) != found:
                    continue
                task = draft.model_copy(
                    update={
                        "signature": signature(request, fixture, found),
                        "violations": found,
                    }
                )
                built = (task, trace)
                break
            if built is None:
                raise RuntimeError(f"self-check failed for {split} {cell} {index}")
            rows.append(built)
    signatures = [task.signature for task, _ in rows]
    if len(signatures) != len(set(signatures)):
        raise RuntimeError(f"signature collision inside {split}")
    return rows
