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
