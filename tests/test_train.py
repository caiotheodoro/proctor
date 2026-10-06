"""Seed 999 never enters a training manifest."""

import proctor_model.train as train_mod
import pytest


def test_loop_check_records_the_exclusion(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(train_mod, "ROOT", tmp_path)
    payload = train_mod.train(11, "loop-check")
    assert payload["data_seed_excluded"] == 999
    assert payload["backend"] == "loop-check"
    assert payload["result"] is None
    assert payload["split"] == "train"
    assert not (tmp_path / "artifacts" / "train" / "seed-999").exists()


def test_test_split_and_seed_999_are_refused() -> None:
    with pytest.raises(SystemExit):
        train_mod.refuse_foreign("test")
    with pytest.raises(SystemExit):
        train_mod.train(999, "loop-check")


def test_cuda_refusal_is_not_a_result(monkeypatch) -> None:
    monkeypatch.setattr(train_mod, "cuda_available", lambda: False)
    with pytest.raises(SystemExit, match="without CUDA"):
        train_mod.train(11, "qlora-grpo")
