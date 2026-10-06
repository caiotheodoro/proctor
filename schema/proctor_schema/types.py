"""Frozen types. Field `class` is the JSON name; Python uses `klass`."""

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

Severity = Literal["HIGH", "MED", "LOW"]
ViolationId = Literal[
    "wrong_tool",
    "wrong_unit",
    "schema_break",
    "arg_mismatch",
    "result_mismatch",
    "poisoned_description",
]


class Violation(BaseModel):
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    klass: ViolationId = Field(alias="class")
    severity: Severity
    call_index: int | None

    def sort_key(self) -> tuple[str, str, int]:
        index = -1 if self.call_index is None else self.call_index
        return (self.klass, self.severity, index)


class ToolSpec(BaseModel):
    model_config = ConfigDict(frozen=True)

    name: str
    description: str
    parameters: dict[str, Any]


class Call(BaseModel):
    model_config = ConfigDict(frozen=True)

    tool: str
    args: dict[str, Any]
    result: dict[str, Any]


class Trace(BaseModel):
    model_config = ConfigDict(frozen=True)

    calls: list[Call]


class Task(BaseModel):
    model_config = ConfigDict(frozen=True)

    task_id: str
    signature: str
    request: dict[str, Any]
    tools: list[ToolSpec]
    fixture: dict[str, Any]
    violations: list[Violation]
