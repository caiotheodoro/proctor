"""Schema arm file, kept next to the score tests' behavioral claim."""

from proctor_schema_check import schema_only


def test_unknown_tool_is_silent() -> None:
    from proctor_schema import Call, Task, Trace, make_fixture, tool_catalog

    request = {
        "account_id": "A100",
        "amount_cents": 10,
        "body": "confirm",
        "command": "status",
        "content": "hello",
        "currency": "USD",
        "degrees": 21,
        "intent": "lookup",
        "location": "desk",
        "path": "notes/a.txt",
        "recipient": "ops",
        "to_account": "A200",
        "unit": "celsius",
        "when": "2026-10-07T15:00:00Z",
    }
    task = Task(
        task_id="unknown",
        signature="x",
        request=request,
        tools=tool_catalog(),
        fixture=make_fixture(request),
        violations=[],
    )
    trace = Trace(calls=[Call(tool="drop_table", args={}, result={})])
    assert schema_only(task, trace) == []
