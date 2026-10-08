"""README numbers have to be in the card. The transfer limitation stays in the README."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NUMBER = re.compile(r"\d+(?:\.\d+)?")
URL = re.compile(r"https?://\S+")
TAG = re.compile(r"\bv\d+\.\d+\.\d+\b")


def measurement_numbers(text: str) -> set[str]:
    return set(NUMBER.findall(TAG.sub(" ", URL.sub(" ", text))))


def test_url_and_tag_digits_are_not_measurements() -> None:
    text = "see https://example.com/a3304ff39 and tag v0.1.0. the loss is 9.99"
    assert measurement_numbers(text) == {"9.99"}


def test_readme_states_the_transfer_limitation() -> None:
    readme = (ROOT / "README.md").read_text()
    assert "Transfer to real agent logs is unmeasured." in readme


def test_readme_numbers_are_in_the_card() -> None:
    card_path = ROOT / "MEASUREMENT_CARD.json"
    assert card_path.exists(), "the card is the source of every README number"
    readme_numbers = measurement_numbers((ROOT / "README.md").read_text())
    card_numbers = set(NUMBER.findall(card_path.read_text()))
    missing = sorted(readme_numbers - card_numbers)
    assert missing == []
    payload = json.loads(card_path.read_text())
    assert payload["verdict"] in {"NOT_VERIFIED", "VERIFIED"}
    assert payload["unmet"] or payload["verdict"] == "VERIFIED"
