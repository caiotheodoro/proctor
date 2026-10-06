"""Modal L4 entry. Imported only when Modal is installed and a run is requested."""

from __future__ import annotations

import sys


def main() -> None:
    try:
        import modal
    except ImportError as exc:
        raise SystemExit("modal is not installed; the trained arm stays unmet") from exc
    app = modal.App("proctor-train")
    image = modal.Image.debian_slim(python_version="3.11").pip_install(
        "torch",
        "transformers",
        "peft",
        "bitsandbytes",
        "trl",
        "pydantic>=2.7",
    )

    @app.function(image=image, gpu="L4", timeout=60 * 60 * 6)
    def run_seed(seed: int) -> dict:
        from proctor_model.train import train

        return train(seed, "qlora-grpo")

    with app.run():
        for seed in (11, 22, 33, 44):
            print(run_seed.remote(seed))


if __name__ == "__main__":
    try:
        main()
    except SystemExit as exc:
        print(str(exc), file=sys.stderr)
        raise
