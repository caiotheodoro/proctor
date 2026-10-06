# Architecture

`CONTRACTS.md` is the norm. Packages implement it and do not redefine it.

| Path | Owns | May import |
|---|---|---|
| `schema/` | types, catalog, weights, profiles, splits, argument validation, expected result, signature | nothing in this repo |
| `forge/` | seeded generator and the self-check loop | `schema` |
| `oracle/` | `evaluate(task, trace)` | `schema` |
| `eval/` | loss, bootstrap, `flag_everything`, the card | `schema` |
| `baselines/schema_check/` | the `schema_only` arm | `schema` |
| `baselines/judge/` | prompt, parse, stub transport, live transport | `schema` |
| `model/` | SFT then GRPO, seed exclusion | `schema`, `forge`, `oracle`, `eval` |
| `cloud/` | Modal L4 entry point that calls `model/` | `model` |
| `tests/` | one file per owner, plus integration | the package under test |

`schema/` is read-only after the wave that introduces it. `docs/PRE-REGISTRATION.md` is read-only after the freeze commit. `docs/DECISIONS.md` is append-only.

The generator and the oracle meet only at types and at the self-check. The generator states an intended class set. The oracle returns a violation set. They agree, or the draw is discarded. The scorer never calls a model. The judge and the trained arm both emit the same JSON shape; code parses it.

`flag_everything` lives in `eval/` because it is the floor of the score, not a baseline someone might forget to run. `schema_only` lives under `baselines/` because it is the incumbent.

No package reads the environment except `baselines/judge/` (the live server) and `model/` (to refuse the laptop). Tests use a stub transport and never a network.
