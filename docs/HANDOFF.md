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
| H4 | scored. Enforce loss 2.86 on seeds 11, 22, 33, and 44. Standard deviation 0.0. Gap above `schema_only` is 0.14. Not a win |
| Judge | scored on test. Pinned model, override false. 252 parse misses. Enforce 2.86, audit 14.29 |
| Trained arm | four `qlora-grpo` manifests, each with float `test_enforce_loss` 2.857142857142857. Seed 999 excluded |
| Seed 999 | untouched test split |

## Next

Both protocol gates are scored. Publish the generated desk and the seed-11 adapter, then the collection. The adapter ships only when its test enforce loss is the scored 720/252. Do not substitute a model on a later rerun.

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

**Open:** nothing in the protocol. H4 and the judge loss are in `MEASUREMENT_CARD.json`. The frozen pre-registration still names the triggers; it is not edited.
