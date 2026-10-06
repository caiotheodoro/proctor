"""Modal L4 entry. `modal run cloud/modal_train.py::probe` checks the GPU. Training is `::train`."""

from __future__ import annotations

import sys

import modal

image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install(
        "torch",
        "transformers",
        "peft",
        "bitsandbytes",
        "trl",
        "datasets",
        "accelerate",
        "pydantic>=2.7",
        index_url="https://download.pytorch.org/whl/cu124",
        extra_index_url="https://pypi.org/simple",
    )
    .add_local_dir(
        ".",
        remote_path="/root/proctor",
        ignore=[".venv", ".git", "artifacts", ".worktrees", "**/__pycache__", "**/*.pyc"],
    )
)

app = modal.App("proctor-train")
_PATHS = [
    "/root/proctor/schema",
    "/root/proctor/forge",
    "/root/proctor/oracle",
    "/root/proctor/eval",
    "/root/proctor/baselines/schema_check",
    "/root/proctor/baselines/judge",
    "/root/proctor/model",
]


def _mount_path() -> None:
    for path in reversed(_PATHS):
        if path not in sys.path:
            sys.path.insert(0, path)


@app.function(image=image, gpu="L4", timeout=600)
def probe() -> dict:
    import torch

    return {
        "cuda": torch.cuda.is_available(),
        "device": torch.cuda.get_device_name(0) if torch.cuda.is_available() else None,
    }


@app.function(image=image, gpu="L4", timeout=60 * 60 * 6)
def train_seed(seed: int) -> dict:
    _mount_path()
    from proctor_model.train import train

    return train(seed, "qlora-grpo")


@app.local_entrypoint()
def main(mode: str = "probe") -> None:
    if mode == "probe":
        print(probe.remote())
        return
    if mode != "train":
        raise SystemExit("mode is probe or train")
    for seed in (11, 22, 33, 44):
        print(train_seed.remote(seed))
