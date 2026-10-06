"""README numbers have to be in the card. The transfer limitation stays in the README."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NUMBER = re.compile(r"\d+(?:\.\d+)?")


def test_readme_states_the_transfer_limitation() -> None:
    readme = (ROOT / "README.md").read_text()
    assert "Transfer to real agent logs is unmeasured." in readme


def test_readme_numbers_are_in_the_card() -> None:
    card_path = ROOT / "MEASUREMENT_CARD.json"
    assert card_path.exists(), "the card is the source of every README number"
    readme_numbers = set(NUMBER.findall((ROOT / "README.md").read_text()))
    card_numbers = set(NUMBER.findall(card_path.read_text()))
    missing = sorted(readme_numbers - card_numbers)
    assert missing == []
    payload = json.loads(card_path.read_text())
    assert payload["verdict"] in {"NOT_VERIFIED", "VERIFIED"}
    assert payload["unmet"] or payload["verdict"] == "VERIFIED"
