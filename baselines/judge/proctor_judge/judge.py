"""Judge arm. The model observes. Code parses. Unparseable text is an empty prediction."""

from __future__ import annotations

import json
import os
import urllib.request
from typing import Protocol

from proctor_schema import JUDGE_MODEL, JUDGE_SYSTEM, Task, Trace, Violation, canonical_json


class Transport(Protocol):
    def complete(self, messages: list[dict[str, str]]) -> str: ...


class StubTransport:
    def __init__(self, text: str) -> None:
        self.text = text
        self.messages: list[dict[str, str]] = []

    def complete(self, messages: list[dict[str, str]]) -> str:
        self.messages = messages
        return self.text


class LiveTransport:
    def __init__(self, base_url: str, api_key: str, model: str) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.model = model

    def complete(self, messages: list[dict[str, str]]) -> str:
        body = json.dumps({"messages": messages, "model": self.model, "temperature": 0}).encode()
        request = urllib.request.Request(
            self.base_url + "/chat/completions",
            data=body,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        with urllib.request.urlopen(request, timeout=120) as response:
            payload = json.loads(response.read().decode())
        return payload["choices"][0]["message"]["content"]


def user_message(task: Task, trace: Trace) -> str:
    return canonical_json(
        {
            "fixture": task.fixture,
            "request": task.request,
            "tools": [tool.model_dump(mode="json") for tool in task.tools],
            "trace": trace.model_dump(mode="json"),
        }
    )


def parse_completion(text: str) -> tuple[list[Violation], bool]:
    try:
        data = json.loads(text)
        items = data["violations"]
        if not isinstance(items, list):
            return [], True
        return [Violation.model_validate(item) for item in items], False
    except (KeyError, TypeError, ValueError, json.JSONDecodeError):
        return [], True


def judge(task: Task, trace: Trace, transport: Transport) -> tuple[list[Violation], bool]:
    raw = transport.complete(
        [
            {"role": "system", "content": JUDGE_SYSTEM},
            {"role": "user", "content": user_message(task, trace)},
        ]
    )
    return parse_completion(raw)


def live_from_env() -> tuple[LiveTransport, str, bool]:
    base = os.environ.get("PROCTOR_JUDGE_BASE_URL", "")
    if not base:
        raise RuntimeError("PROCTOR_JUDGE_BASE_URL is unset")
    model = os.environ.get("PROCTOR_JUDGE_MODEL") or JUDGE_MODEL
    override = "PROCTOR_JUDGE_MODEL" in os.environ and os.environ["PROCTOR_JUDGE_MODEL"] != ""
    if os.environ.get("PROCTOR_JUDGE_MODEL") == JUDGE_MODEL:
        override = False
    return LiveTransport(base, os.environ.get("PROCTOR_JUDGE_API_KEY", ""), model), model, override
