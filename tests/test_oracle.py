"""Oracle agreement on every planted cell."""

from proctor_forge.generate import INTENDED, generate
from proctor_oracle import evaluate


def test_dev_cells_match_the_intended_class_and_a_second_evaluate() -> None:
    counts = {cell: 0 for cell in INTENDED}
    for task, trace in generate("dev"):
        cell = task.task_id.split("-")[1]
        classes = {item.klass for item in task.violations}
        assert classes == INTENDED[cell]
        assert evaluate(task, trace) == task.violations
        if cell == "arg_mismatch":
            assert task.violations[0].severity == "HIGH"
            assert task.violations[0].klass == "arg_mismatch"
        if cell == "schema_break":
            assert [item.klass for item in task.violations] == ["schema_break"]
        counts[cell] += 1
    assert counts == {cell: 12 for cell in INTENDED}
