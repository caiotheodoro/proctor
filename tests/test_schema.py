"""Round-trip and contract checks for the frozen schema."""

from proctor_schema import (
    CANONICAL,
    JUDGE_SYSTEM,
    Call,
    Task,
    Trace,
    Violation,
    canonical_json,
    expected_result,
    make_fixture,
    signature,
    tool_catalog,
    validate_args,
)


def _request() -> dict:
    return {
        "account_id": "A100",
        "amount_cents": 5000,
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


def test_violation_round_trip_uses_class_alias() -> None:
    item = Violation.model_validate({"class": "schema_break", "severity": "LOW", "call_index": 0})
    raw = item.model_dump(mode="json", by_alias=True)
    assert raw == {"class": "schema_break", "severity": "LOW", "call_index": 0}
    assert Violation.model_validate(raw) == item


def test_task_round_trip() -> None:
    request = _request()
    fixture = make_fixture(request)
    call = Call(
        tool="lookup_account",
        args={"account_id": "A100"},
        result=expected_result("lookup_account", {"account_id": "A100"}, fixture),
    )
    task = Task(
        task_id="round",
        signature="abc",
        request=request,
        tools=tool_catalog(),
        fixture=fixture,
        violations=[],
    )
    trace = Trace(calls=[call])
    again = Task.model_validate(task.model_dump(mode="json"))
    assert again == task
    assert Trace.model_validate(trace.model_dump(mode="json")) == trace


def test_bool_is_not_an_integer_argument() -> None:
    assert (
        validate_args(
            "transfer",
            {
                "from_account": "A100",
                "to_account": "A200",
                "amount_cents": True,
                "currency": "USD",
            },
        )
        is False
    )


def test_string_amount_fails_schema() -> None:
    assert (
        validate_args(
            "transfer",
            {
                "from_account": "A100",
                "to_account": "A200",
                "amount_cents": "50",
                "currency": "USD",
            },
        )
        is False
    )


def test_expected_transfer_id_is_stable_under_key_order() -> None:
    request = _request()
    fixture = make_fixture(request)
    args_a = {
        "amount_cents": 5000,
        "currency": "USD",
        "from_account": "A100",
        "to_account": "A200",
    }
    args_b = {
        "to_account": "A200",
        "from_account": "A100",
        "currency": "USD",
        "amount_cents": 5000,
    }
    assert expected_result("transfer", args_a, fixture) == expected_result(
        "transfer", args_b, fixture
    )


def test_signature_depends_on_sorted_violations_not_insertion_order() -> None:
    request = _request()
    fixture = make_fixture(request)
    first = Violation.model_validate({"class": "wrong_tool", "severity": "HIGH", "call_index": 1})
    second = Violation.model_validate({"class": "schema_break", "severity": "LOW", "call_index": 0})
    assert signature(request, fixture, [first, second]) == signature(
        request, fixture, [second, first]
    )


def test_canonical_descriptions_match_the_catalog_strings() -> None:
    tools = tool_catalog()
    assert [tool.name for tool in tools] == list(CANONICAL)
    assert tools[0].description == CANONICAL["lookup_account"]


def test_judge_system_text_matches_the_contract_block() -> None:
    assert "You observe. You do not choose an action." in JUDGE_SYSTEM
    assert "poisoned_description" in JUDGE_SYSTEM
    assert canonical_json({"b": 1, "a": 2}) == '{"a":2,"b":1}'
