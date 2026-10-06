"""Schema check. Catches schema_break and stays silent on every other class."""

from __future__ import annotations

from proctor_schema import SCHEMAS, Task, Trace, Violation, validate_args


def schema_only(task: Task, trace: Trace) -> list[Violation]:
    del task
    found: list[Violation] = []
    for index, call in enumerate(trace.calls):
        if call.tool not in SCHEMAS:
            continue
        if validate_args(call.tool, call.args):
            continue
        found.append(
            Violation.model_validate(
                {"class": "schema_break", "severity": "LOW", "call_index": index}
            )
        )
    return found
