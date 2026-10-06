# Handoff

Resume point for a fresh session. Update the state table at the end of a session. Do not report effort as elapsed time.

## State

| Item | State |
|---|---|
| Doc spine | this commit |
| Pre-registration | `1.0.0-draft` until the freeze commit |
| `schema/` | not started |
| Generator, oracle, score, arms | not started |
| `make validate` | spine gates only |
| H1–H3 | not scored |
| Judge | not run |
| Trained arm | not run; card will stay `NOT_VERIFIED` without four `qlora-grpo` manifests |
| Seed 999 | reserved; no loader exists yet |

## Next

1. Freeze: a commit that touches only `docs/PRE-REGISTRATION.md` and `docs/DECISIONS.md`.
2. Implement `schema/` from `CONTRACTS.md`, with a round-trip test. Nothing else in that commit.
3. Fan out owners. One owner per directory. Nobody edits `schema/` or the frozen protocol.
4. Integrate: leak probe, card, `make validate` green with no network.
5. `make baselines`.
6. Judge and training only on the runners named in `CONTRACTS.md` section 10. If they are unreachable, write the blocker into the card's `unmet` list and stop. Do not substitute a model.

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
