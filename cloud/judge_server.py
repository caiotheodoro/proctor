"""OpenAI-compatible server for the pinned judge weights. Greedy decode only."""

from __future__ import annotations

import torch
import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
from transformers import AutoModelForCausalLM, AutoTokenizer

MODEL = "Qwen/Qwen2.5-1.5B-Instruct"

app = FastAPI()
tokenizer = AutoTokenizer.from_pretrained(MODEL)
model = AutoModelForCausalLM.from_pretrained(MODEL, torch_dtype=torch.bfloat16, device_map="cuda")
model.eval()


class Message(BaseModel):
    role: str
    content: str


class Request(BaseModel):
    model: str
    messages: list[Message]
    temperature: float = 0


@app.get("/v1/models")
def models() -> dict:
    return {"data": [{"id": MODEL}]}


@app.post("/v1/chat/completions")
def complete(body: Request) -> dict:
    messages = [{"role": item.role, "content": item.content} for item in body.messages]
    encoded = tokenizer.apply_chat_template(
        messages,
        return_tensors="pt",
        add_generation_prompt=True,
        return_dict=True,
    )
    encoded = {key: value.to(model.device) for key, value in encoded.items()}
    prompt_len = encoded["input_ids"].shape[-1]
    with torch.no_grad():
        output = model.generate(**encoded, max_new_tokens=512, do_sample=False)
    text = tokenizer.decode(output[0][prompt_len:], skip_special_tokens=True)
    return {"choices": [{"message": {"role": "assistant", "content": text}}]}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
