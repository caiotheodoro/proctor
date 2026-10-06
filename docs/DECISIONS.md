# Decisions

Append-only. An entry is Decision, Rationale, Evidence, Alternatives rejected. The frozen protocol is not edited to match an entry; the entry points at what moved.

## 2026-10-06 — Spine before source

**Decision.** The doc set lands before any package under `schema/`, `forge/`, `oracle/`, `eval/`, `baselines/`, `model/`, or `cloud/`.

**Rationale.** The git history is the evidence that the protocol preceded the generator. A measurement written after the first plot is a story about the plot.

**Evidence.** This commit contains the markdown spine, `scripts/check_paths.py`, and the Makefile, and it does not contain those packages.

**Alternatives rejected.** Starting from the oracle and back-filling the protocol. Writing the trained arm out of the protocol to finish faster: the personal-ml bar is that a single-run margin is not a result, so H4 stays in the protocol even though it cannot be scored on a laptop.

## 2026-10-06 — Protocol frozen at 1.0.0

**Decision.** `docs/PRE-REGISTRATION.md` revision `1.0.0` is frozen before any package exists. Later edits to that file are not allowed. Amendments are entries in this file.

**Rationale.** A hypothesis that can see the generator is not a pre-registration.

**Evidence.** The freeze commit's path list is this file and `docs/PRE-REGISTRATION.md` only. `git show --stat` on that commit is the check.

**Alternatives rejected.** Freezing after `schema/` landed, which would let the types teach the hypotheses. Leaving the revision at draft while implementation started.

## 2026-10-06 — Model-free arms scored on the test split

**Decision.** Publish H1, H2, and H3 from `make baselines`. Leave the verdict `NOT_VERIFIED` because the judge artifact and the four `qlora-grpo` manifests do not exist.

**Rationale.** The protocol says a missing server does not change H1–H3, and it says a missing trainer does not get a substitute score.

**Evidence.** `MEASUREMENT_CARD.json` after `make baselines`. `flag_everything` enforce mean 117.56. `schema_only` enforce mean 2.71. Paired difference -114.85, interval -119.77 to -110.26. `schema_break` recall 1.0. `wrong_unit` recall 0.0. Audit loss for `schema_only` is 13.57.

**Alternatives rejected.** Dropping H4 from the card so the verdict could read `VERIFIED`. Scoring a smaller model and labeling the manifest `qlora-grpo`.
