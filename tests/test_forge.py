"""Generator: reseed identity and the leak probe."""

from proctor_forge.generate import generate
from proctor_forge.leak_probe import overlap
from proctor_schema import canonical_json


def _dump(split: str) -> str:
    rows = [
        {"task": task.model_dump(mode="json"), "trace": trace.model_dump(mode="json")}
        for task, trace in generate(split)
    ]
    return canonical_json(rows)


def test_reseed_is_byte_identical() -> None:
    assert _dump("dev") == _dump("dev")


def test_train_and_test_signatures_are_disjoint() -> None:
    train = {task.signature for task, _ in generate("train")}
    test = {task.signature for task, _ in generate("test")}
    assert overlap(train, train) == 1.0
    assert overlap(train, test) == 0.0
    assert len(test) == 252
