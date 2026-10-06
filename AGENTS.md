# proctor — operating rules

A wrong tool call has a price. `flag_everything` is the floor. `README.md` is the argument. `CONTRACTS.md` is what is measured. This file is how work is done.

## Rules

**1. The protocol is binding.** `docs/PRE-REGISTRATION.md` freezes before any model is called and before any package exists. After that commit the file is not edited. A change is a dated `docs/DECISIONS.md` entry.

**2. No transcribed numbers.** A figure in `README.md` is copied from `MEASUREMENT_CARD.json`. `tests/test_claims.py` fails when a README number is absent from the card, once the card exists. Unknowns are `**Open:**` plus the trigger that resolves them. The words that scanners ban do not appear in the docs.

**3. The oracle is a program.** `evaluate` calls no model. The generator's self-check compares the intended class set to the oracle, then calls the oracle again. The judge observes. Code parses. An unparseable completion is an empty prediction, not a repaired one.

**4. Seed 999 is untouched.** It is the test split's data seed. It is not a model seed. The loader raises if a training row is tagged `test`. Four model seeds or no trained-arm claim.

**5. Keys stay in the environment.** `.env` is gitignored. `.env.example` has names and no values. `make privacy-gate` scans tracked files for key-shaped strings.

**6. One writer per directory.** Owners are in `docs/ARCHITECTURE.md`. `schema/` and the frozen protocol are not on that list.

## What not to do

- Do not train on the laptop, and do not label another backend `qlora-grpo`.
- Do not add a cell, an arm, or a tool after freeze without a decision entry that marks every affected table post-hoc.
- Do not put a customer trace, a tenant name, or an email in the tree.
- Do not report effort as elapsed time.
- Do not start two writers on one directory.
