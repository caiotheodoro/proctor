# Red team

Attacks on this repo's own claims. Each one is a test or a check a reviewer can run. An attack that lands becomes a `docs/DECISIONS.md` entry or a retraction at the top of `README.md`.

## A1 — The self-check is a tautology

The generator could store whatever the oracle returns and call that agreement. The gate requires two comparisons: the oracle class set equals the intended cell, and a second `evaluate` equals the stored set. A mutation that also trips a second class fails the first comparison. Test: plant `schema_break` with a string amount and assert the class set is exactly `{schema_break}`.

## A2 — `flag_everything` is tuned to the oracle's severity so the floor looks beatable

The floor's severities are the contract's table, not a fitted vector. Test: on a clean task the floor's loss is strictly positive on both profiles, and on a `schema_break` task the floor still emits the semantic classes.

## A3 — `schema_only` peeks at the unit or the description

The arm may read schemas and arguments only. Test: a `wrong_unit` trace and a `poisoned_description` trace both produce an empty prediction, and a string `amount_cents` produces one `schema_break` at LOW.

## A4 — Seed 999 leaks into training

The train manifest records `data_seed_excluded: 999` and the loader raises if any row's split is `test`. Test: a fixture row tagged `test` aborts before a backend is constructed. The leak probe prints `0.0` on `train` intersected with `test`.

## A5 — A single training seed becomes the headline

H4 forbids a win whose margin does not exceed the across-seed standard deviation, and forbids the win when fewer than four manifests with `backend=qlora-grpo` exist. Test: the card's verdict is `NOT_VERIFIED` when those manifests are absent, even if H1 and H3 hold.

## A6 — The judge's prose is repaired until it parses

Unparseable output is an empty prediction. There is no retry and no regex scrape of a JSON substring wrapped in prose. Test: a stub that returns `sure: {"violations":[]}` yields an empty list and increments `parse_misses`.

## A7 — Float or key-order drift breaks the reseeds

Signatures and expected ids use canonical JSON. Test: `generate("test")` dumped twice is byte-identical, including a second process.

## A8 — The README cites a number the card does not contain

`tests/test_claims.py` extracts numeric tokens from `README.md` and requires each one to appear in `MEASUREMENT_CARD.json` once that file exists. A result typed into the README ahead of the artifact fails the test. Digits inside an `http` URL, and a `vX.Y.Z` revision tag, are not measurements.

## A9 — The conflict writes the hypothesis

H1 compares two arms that do not call a vendor. H3 is a recall on a class a schema check is supposed to catch and a class it is supposed to miss. Neither arm is a TrueFoundry API. `docs/ETHICS.md` is the disclosure. A reviewer who wants the opposite outcome can re-run `make validate` and `proctor score` offline.

## A10 — Result equality ignores argument identity

`result_mismatch` compares the canonical result of the arguments that were actually sent, not the arguments that should have been sent. Otherwise an `arg_mismatch` would always double-count. Test: the amount-plus-one transfer, with a recomputed result, is exactly `{arg_mismatch}`.
