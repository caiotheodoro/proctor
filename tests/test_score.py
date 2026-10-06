"""Floor and schema arm. The schema arm does not peek."""

from proctor_eval import flag_everything, task_loss
from proctor_forge.generate import generate
from proctor_schema_check import schema_only


def _row(cell: str):
    for task, trace in generate("dev"):
        if task.task_id.split("-")[1] == cell:
            return task, trace
    raise AssertionError(cell)


def test_floor_is_positive_on_a_clean_task() -> None:
    task, trace = _row("clean")
    pred = flag_everything(task, trace)
    assert task_loss(task.violations, pred, "audit") > 0
    assert task_loss(task.violations, pred, "enforce") > 0


def test_schema_only_catches_schema_break_and_is_silent_on_wrong_unit() -> None:
    broken, broken_trace = _row("schema_break")
    unit, unit_trace = _row("wrong_unit")
    poisoned, poisoned_trace = _row("poisoned_description")
    found = schema_only(broken, broken_trace)
    assert [item.klass for item in found] == ["schema_break"]
    assert found[0].severity == "LOW"
    assert schema_only(unit, unit_trace) == []
    assert schema_only(poisoned, poisoned_trace) == []
