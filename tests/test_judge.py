"""Judge parse rule: prose is an empty prediction, and the user message hides the label."""

import json

from proctor_forge.generate import generate
from proctor_judge import StubTransport, judge
from proctor_judge.judge import user_message


def test_prose_around_json_is_a_parse_miss() -> None:
    task, trace = next(iter(generate("dev")))
    transport = StubTransport('sure: {"violations":[]}')
    pred, missed = judge(task, trace, transport)
    assert pred == []
    assert missed is True


def test_user_message_does_not_carry_the_planted_set() -> None:
    task, trace = next(iter(generate("dev")))
    payload = json.loads(user_message(task, trace))
    assert "violations" not in payload
    assert "signature" not in payload


def test_strict_json_is_accepted() -> None:
    task, trace = next(iter(generate("dev")))
    transport = StubTransport(
        '{"violations":[{"class":"schema_break","severity":"LOW","call_index":0}]}'
    )
    pred, missed = judge(task, trace, transport)
    assert missed is False
    assert pred[0].klass == "schema_break"
    assert "violations" not in json.loads(transport.messages[1]["content"])
