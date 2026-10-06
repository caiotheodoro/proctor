# Handoff

Resume point for a fresh session. Update the state table at the end of a session. Do not report effort as elapsed time.

## State

| Item | State |
|---|---|
| Doc spine | committed |
| Pre-registration | `1.0.0` frozen |
| `schema/` | committed; read-only |
| Generator, oracle, score, schema arm, judge client | committed; `make validate` is the gate |
| H1–H3 | scored; all three hold. Figures in `MEASUREMENT_CARD.json` |
| Judge | not run. `make judge` records a blocker when the server is unset |
| Trained arm | not run. `python -m proctor_model.train` refuses without CUDA and does not write a `qlora-grpo` manifest |
| Seed 999 | untouched test split |

## Next

1. `make judge` when `PROCTOR_JUDGE_BASE_URL` points at `Qwen/Qwen2.5-1.5B-Instruct`.
2. Four CUDA seeds via `cloud/modal_train.py` or `python -m proctor_model.train` on a machine with CUDA. Each manifest needs `backend=qlora-grpo` and a float `test_enforce_loss`.
3. Re-run `make card` after either artifact exists. Do not substitute a backend.

## What not to do

- Do not edit `docs/PRE-REGISTRATION.md` after the freeze commit.
- Do not train on the `test` split or on data seed 999.
- Do not quote a trained-arm margin from one seed.
- Do not repair a judge completion that failed to parse.
- Do not put a key, a customer trace, or a tenant id in the tree.
- Do not start two writers on one directory.
- Do not report a proxy backend as `qlora-grpo`.

## Planned paths

A backticked path under one of these prefixes may appear in the docs before the file exists. Delete a prefix once the tree contains that directory and the docs only name files that are real.

planned: `schema/`, `forge/`, `oracle/`, `eval/`, `baselines/`, `model/`, `cloud/`, `tests/`, `artifacts/`, `MEASUREMENT_CARD.json`

**Open:** H4 and the judge loss. Triggers are in `docs/PRE-REGISTRATION.md`.
