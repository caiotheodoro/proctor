"""Modal L4 entry. `modal run cloud/modal_train.py::probe` checks the GPU. Training is `::train`."""

from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

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
        ignore=[
            ".venv",
            ".git",
            "artifacts",
            ".worktrees",
            "build",
            "dist",
            "**/__pycache__",
            "**/*.pyc",
        ],
    )
)

app = modal.App("proctor-train")
volume = modal.Volume.from_name("proctor-artifacts", create_if_missing=True)
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


@app.function(image=image, gpu="L4", timeout=60 * 60 * 6, volumes={"/artifacts": volume})
def train_seed(seed: int) -> dict:
    _mount_path()
    from proctor_model.train import train

    def _keep(adapter_path: Path) -> None:
        dest = Path("/artifacts") / f"seed-{seed}" / "adapter"
        if dest.exists():
            shutil.rmtree(dest)
        shutil.copytree(adapter_path, dest)
        volume.commit()

    payload = train(seed, "qlora-grpo", on_adapter=_keep)
    path = Path("/artifacts") / f"seed-{seed}" / "manifest.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    volume.commit()
    return payload


@app.local_entrypoint()
def main(mode: str = "probe", seed: int = 0) -> None:
    if mode == "probe":
        print(probe.remote())
        return
    if mode != "train":
        raise SystemExit("mode is probe or train")
    if seed:
        call = train_seed.spawn(seed)
        print({"spawned": seed, "call_id": call.object_id})
        return
    seeds = (11, 22, 33, 44)
    for item in seeds:
        payload = train_seed.remote(item)
        path = Path("artifacts") / "train" / f"seed-{item}" / "manifest.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
        print(payload)
