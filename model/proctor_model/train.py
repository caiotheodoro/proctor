"""Training entry. Seed 999 is refused. A non-CUDA machine does not produce a result."""

from __future__ import annotations

import json
import sys
from collections.abc import Callable
from pathlib import Path

from proctor_forge import generate
from proctor_schema import JUDGE_MODEL, MODEL_SEEDS

ROOT = Path(__file__).resolve().parents[2]


def load_train() -> list:
    rows = generate("train")
    for task, _ in rows:
        if task.task_id.startswith("test"):
            raise SystemExit("seed 999 is untouched: a test row reached the loader")
    return rows


def refuse_foreign(split: str) -> None:
    if split != "train":
        raise SystemExit("training accepts the train split only; seed 999 stays untouched")


def cuda_available() -> bool:
    try:
        import torch
    except ImportError:
        return False
    return bool(torch.cuda.is_available())


def manifest_for(seed: int, backend: str, rows: int) -> dict:
    return {
        "backend": backend,
        "data_seed_excluded": 999,
        "model": JUDGE_MODEL,
        "model_seed": seed,
        "result": None,
        "rows": rows,
        "split": "train",
    }


def write_manifest(seed: int, payload: dict) -> Path:
    path = ROOT / "artifacts" / "train" / f"seed-{seed}" / "manifest.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    return path


def train(
    seed: int,
    backend: str,
    on_adapter: Callable[[Path], None] | None = None,
) -> dict:
    if seed not in MODEL_SEEDS:
        raise SystemExit(f"refusing model seed {seed}; allowed seeds are {MODEL_SEEDS}")
    refuse_foreign("train")
    rows = load_train()
    payload = manifest_for(seed, backend, len(rows))
    if backend == "loop-check":
        write_manifest(seed, payload)
        return payload
    if backend != "qlora-grpo":
        raise SystemExit(f"unknown backend {backend}; a substitute is not a result")
    if not cuda_available():
        raise SystemExit("refusing to train without CUDA; the laptop is not a training device")
    payload["test_enforce_loss"] = _qlora_grpo(seed, rows, on_adapter)
    payload["backend"] = "qlora-grpo"
    write_manifest(seed, payload)
    return payload


def _save_adapter(model, tokenizer, seed: int) -> Path:
    path = ROOT / "artifacts" / "train" / f"seed-{seed}" / "adapter"
    path.mkdir(parents=True, exist_ok=True)
    model.save_pretrained(path)
    tokenizer.save_pretrained(path)
    return path


def _qlora_grpo(
    seed: int,
    rows: list,
    on_adapter: Callable[[Path], None] | None = None,
) -> float:
    """4-bit QLoRA supervised pass, then GRPO. Returns test-split enforce loss.

    A manifest is written only after this returns a float. An import error or a
    trainer error leaves no qlora-grpo manifest, so the card stays unmet.
    """
    import torch
    from datasets import Dataset
    from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
    from proctor_eval.score import task_loss
    from proctor_forge import generate as generate_split
    from proctor_judge.judge import parse_completion, user_message
    from proctor_schema import JUDGE_SYSTEM
    from transformers import (
        AutoModelForCausalLM,
        AutoTokenizer,
        BitsAndBytesConfig,
        Trainer,
        TrainingArguments,
    )

    tokenizer = AutoTokenizer.from_pretrained(JUDGE_MODEL)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    model = AutoModelForCausalLM.from_pretrained(
        JUDGE_MODEL,
        quantization_config=BitsAndBytesConfig(
            bnb_4bit_compute_dtype=torch.bfloat16,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_use_double_quant=True,
            load_in_4bit=True,
        ),
        device_map="auto",
    )
    model = prepare_model_for_kbit_training(model)
    model = get_peft_model(
        model,
        LoraConfig(
            r=8,
            lora_alpha=16,
            lora_dropout=0.05,
            bias="none",
            task_type="CAUSAL_LM",
            target_modules=["q_proj", "v_proj"],
        ),
    )
    texts = []
    for task, trace in rows:
        dumped = [item.model_dump(mode="json", by_alias=True) for item in task.violations]
        target = json.dumps({"violations": dumped})
        texts.append(f"{JUDGE_SYSTEM}\n{user_message(task, trace)}\n{target}")
    encoded = tokenizer(texts, truncation=True, max_length=1024, padding=True)
    dataset = Dataset.from_dict(encoded)

    def collate(features: list[dict]) -> dict:
        batch = tokenizer.pad(features, return_tensors="pt")
        batch["labels"] = batch["input_ids"].clone()
        return batch

    trainer = Trainer(
        model=model,
        args=TrainingArguments(
            output_dir=str(ROOT / "artifacts" / "train" / f"seed-{seed}" / "sft"),
            per_device_train_batch_size=1,
            gradient_accumulation_steps=4,
            max_steps=20,
            learning_rate=2e-4,
            logging_steps=5,
            save_strategy="no",
            report_to=[],
            seed=seed,
            bf16=True,
        ),
        train_dataset=dataset,
        data_collator=collate,
    )
    trainer.train()

    from trl import GRPOConfig, GRPOTrainer

    prompts = [f"{JUDGE_SYSTEM}\n{user_message(task, trace)}" for task, trace in rows]

    by_prompt = {prompt: pair for prompt, pair in zip(prompts, rows, strict=True)}

    def reward(
        completions: list[str],
        prompts: list[str] | None = None,
        **_kwargs: object,
    ) -> list[float]:
        if prompts is None:
            raise RuntimeError("GRPO did not pass prompts")
        scores: list[float] = []
        for completion, prompt in zip(completions, prompts, strict=True):
            task, _trace = by_prompt[prompt]
            pred, _missed = parse_completion(completion)
            scores.append(-task_loss(task.violations, pred, "audit"))
        return scores

    grpo = GRPOTrainer(
        model=model,
        reward_funcs=reward,
        args=GRPOConfig(
            output_dir=str(ROOT / "artifacts" / "train" / f"seed-{seed}" / "grpo"),
            per_device_train_batch_size=1,
            generation_batch_size=4,
            max_steps=10,
            num_generations=4,
            learning_rate=1e-5,
            seed=seed,
            report_to=[],
            logging_steps=1,
        ),
        train_dataset=Dataset.from_dict({"prompt": prompts}),
    )
    grpo.train()

    # Checkpointing disables the KV cache, which makes the 252 greedy decodes
    # recompute every prefix. Training is finished, so turn the cache back on.
    model.gradient_checkpointing_disable()
    model.config.use_cache = True
    adapter_path = _save_adapter(model, tokenizer, seed)
    if on_adapter is not None:
        on_adapter(adapter_path)

    losses: list[float] = []
    for index, (task, trace) in enumerate(generate_split("test"), start=1):
        messages = [
            {"role": "system", "content": JUDGE_SYSTEM},
            {"role": "user", "content": user_message(task, trace)},
        ]
        device = next(model.parameters()).device
        inputs = tokenizer.apply_chat_template(
            messages,
            return_tensors="pt",
            add_generation_prompt=True,
            return_dict=True,
        )
        inputs = {key: value.to(device) for key, value in inputs.items()}
        prompt_len = inputs["input_ids"].shape[-1]
        with torch.no_grad():
            output = model.generate(**inputs, max_new_tokens=256, do_sample=False)
        text = tokenizer.decode(output[0][prompt_len:], skip_special_tokens=True)
        pred, _missed = parse_completion(text)
        losses.append(task_loss(task.violations, pred, "enforce"))
        if index == 1 or index % 36 == 0:
            print(f"eval {index} {len(losses)}", flush=True)
    return sum(losses) / len(losses)


def main(argv: list[str] | None = None) -> None:
    args = argv if argv is not None else sys.argv[1:]
    backend = "qlora-grpo"
    seeds: list[int] = list(MODEL_SEEDS)
    if "--backend" in args:
        backend = args[args.index("--backend") + 1]
    if "--seed" in args:
        seeds = [int(args[args.index("--seed") + 1])]
    try:
        for seed in seeds:
            train(seed, backend)
    except SystemExit as exc:
        blocked = ROOT / "artifacts" / "train" / "BLOCKED.json"
        blocked.parent.mkdir(parents=True, exist_ok=True)
        blocked.write_text(json.dumps({"reason": str(exc)}, indent=2) + "\n")
        print(str(exc), file=sys.stderr)
        raise


if __name__ == "__main__":
    main()
