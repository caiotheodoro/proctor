"""Deploy the pinned judge. Base URL is the printed host plus `/v1`."""

from __future__ import annotations

import subprocess

import modal

image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install(
        "torch",
        "transformers",
        "accelerate",
        "fastapi",
        "uvicorn",
        index_url="https://download.pytorch.org/whl/cu124",
        extra_index_url="https://pypi.org/simple",
    )
    .add_local_file("cloud/judge_server.py", "/root/judge_server.py")
)
app = modal.App("proctor-judge")


@app.function(image=image, gpu="L4", timeout=60 * 60, scaledown_window=180)
@modal.web_server(port=8000, startup_timeout=900)
def serve() -> None:
    subprocess.Popen(["python", "/root/judge_server.py"])
