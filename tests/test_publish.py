"""Hub cards are rendered from the measurement card, and a drifted loss is refused."""

import json

import pytest
from hf_cards import (
    DESCRIPTION_LIMIT,
    SCORED_LOSS,
    GateFailed,
    assert_scored_manifest,
    collection_description,
    collection_gates,
    load_card,
    stage_dataset,
    stage_model,
)


def test_collection_description_is_derived_and_short() -> None:
    card = load_card()
    text = collection_description(card)
    assert len(text) <= DESCRIPTION_LIMIT
    assert f"{card['results']['published']['h1_diff']:.2f}" in text
    assert "synthetic" in text.lower()
    assert "not production-validated" in text.lower()
    collection_gates(card)


def test_dataset_counts_match_the_card(tmp_path) -> None:
    counts = stage_dataset(tmp_path)
    card = load_card()
    assert counts["train"] == card["contract"]["train_tasks"]
    assert counts["dev"] == card["contract"]["dev_tasks"]
    assert counts["test"] == card["contract"]["test_tasks"]
    readme = (tmp_path / "README.md").read_text()
    assert f"{card['results']['published']['schema_enforce']:.2f}" in readme
    assert "/main" not in readme
    assert "v0.1.0" in readme


def test_a_different_loss_is_not_the_scored_run(tmp_path) -> None:
    adapter = tmp_path / "adapter"
    adapter.mkdir()
    (adapter / "adapter_config.json").write_text("{}\n")
    (adapter / "adapter_model.safetensors").write_bytes(b"not-a-real-tensor")
    manifest = {
        "backend": "qlora-grpo",
        "data_seed_excluded": 999,
        "model_seed": 11,
        "test_enforce_loss": SCORED_LOSS + 1,
    }
    with pytest.raises(GateFailed, match="not the scored run"):
        stage_model(tmp_path / "out", adapter, manifest)


def test_scored_loss_is_accepted(tmp_path) -> None:
    adapter = tmp_path / "adapter"
    adapter.mkdir()
    (adapter / "adapter_config.json").write_text("{}\n")
    (adapter / "adapter_model.safetensors").write_bytes(b"not-a-real-tensor")
    manifest = {
        "backend": "qlora-grpo",
        "data_seed_excluded": 999,
        "model_seed": 11,
        "test_enforce_loss": json.loads(json.dumps(SCORED_LOSS)),
    }
    assert_scored_manifest(manifest)
    stage_model(tmp_path / "out", adapter, manifest)
    text = (tmp_path / "out" / "README.md").read_text()
    assert "H4 does not hold" in text
    assert "not production-validated" in text
