# Reproduction

Offline, from a clean tree:

```sh
make install
make validate
```

`make validate` runs lint, tests, the leak probe, the privacy gate, the placeholder scan, and the path check. It does not read `.env`. It does not open a socket. It does not need a GPU.

Score the two model-free arms and write the card:

```sh
make baselines
```

That writes `artifacts/flag_everything.json`, `artifacts/schema_only.json`, and `MEASUREMENT_CARD.json`. The verdict remains `NOT_VERIFIED` until the judge artifact and the four training manifests exist. H1 and H3 are still reported.

Judge, when a server is up:

```sh
PROCTOR_JUDGE_BASE_URL=http://127.0.0.1:8000/v1 \
PROCTOR_JUDGE_API_KEY=local \
make judge
```

The model id stays `Qwen/Qwen2.5-1.5B-Instruct` unless `PROCTOR_JUDGE_MODEL` is set. A set override is recorded in the artifact and does not satisfy the pinned-model claim.

Training is `cloud/modal_train.py` on a Modal L4, four seeds, or the same module on an AWS g5 if Modal is down. The command refuses to start on a machine with no CUDA device. Seed 999 is not an argument a caller can pass as a data split; the loader accepts `train` only.

`make replay` is not a separate target. `make baselines` is deterministic from the data seeds and the bootstrap seed, so a second run matches the committed card's `results` block.
