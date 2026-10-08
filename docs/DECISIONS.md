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

## 2026-10-06 — Judge and trained arm stay unmet

**Decision.** Do not score the judge or the trained arm in this tree. The card stays `NOT_VERIFIED`.

**Rationale.** The protocol's substitute rule: a missing server and a missing CUDA runner are unmet claims, not zeros and not a smaller model.

**Evidence.** `make judge` wrote a blocker because `PROCTOR_JUDGE_BASE_URL` is unset. `python -m proctor_model.train` refused: no CUDA on this machine. Modal is logged in and returned a spend-limit error before a container started. AWS `GetCallerIdentity` rejected the local token. No `qlora-grpo` manifest exists.

**Alternatives rejected.** Running `Qwen/Qwen2.5-1.5B-Instruct` on the laptop and calling that the pinned judge. Starting a new GPU instance on a token AWS has already rejected.

## 2026-10-06 — Refuter, attacks A1–A10 that can run offline

**Decision.** Keep the published H1–H3 figures. Fix the one defect the refuter found: `cloud/modal_train.py` used `sys.path` without importing `sys`, which failed lint and therefore `make validate`.

**Rationale.** A refuter that only sees the spec, the card, and the README re-ran the dev split and the parse rule. The attacks that do not need a GPU held. The lint break was real and is fixed in the same change as this entry.

**Evidence.** Second `evaluate` matched the stored set on all 84 dev rows. `schema_only` was empty on `wrong_unit` and `poisoned_description` and a single LOW `schema_break` on that cell. Prose around JSON was a parse miss. Two dev dumps matched, including across a second process. `arg_mismatch` rows were one HIGH violation whose result matches the sent arguments. `JUDGE_SYSTEM` matched the section 8 fence text. README numeric tokens are in the card. Verdict remains `NOT_VERIFIED`.

**Alternatives rejected.** Treating the lint failure as a measurement failure. Editing the frozen protocol to drop the judge line from the unmet list.

## 2026-10-07 — Trained arm scored, H4 withholds a win

**Decision.** Publish the four `qlora-grpo` test enforce losses. H4 does not license a claim that the trained arm beats `schema_only`. The verdict stays `NOT_VERIFIED` because the judge artifact is still absent.

**Rationale.** The pre-registered rule is that a win has to clear the across-seed standard deviation. All four seeds returned the same loss, so that deviation is 0, and the trained loss is higher than `schema_only`.

**Evidence.** `artifacts/train/seed-11/manifest.json`, `seed-22`, `seed-33`, and `seed-44`. Each has `backend` `qlora-grpo`, `data_seed_excluded` 999, and `test_enforce_loss` 2.857142857142857. Published figures: enforce loss 2.86, standard deviation 0.0, gap 0.14. `schema_only` enforce mean remains 2.71.

**Alternatives rejected.** Calling the identical seeds a win because the deviation is zero. Substituting a judge score. Editing `docs/PRE-REGISTRATION.md`.

## 2026-10-07 — Judge scored, every completion is a parse miss

**Decision.** Publish the pinned judge on the test split. All 252 completions are parse misses, so each prediction is empty. The verdict is `VERIFIED` because the judge artifact and the four-seed spread both exist.

**Rationale.** The protocol counts unparseable output as an empty prediction and forbids repairing it. A gateway that does not serve `Qwen/Qwen2.5-1.5B-Instruct` is not a substitute.

**Evidence.** `artifacts/judge/test.json`. `model` is `Qwen/Qwen2.5-1.5B-Instruct`, `override` is false, `parse_misses` is 252, enforce mean is 2.857142857142857, audit mean is 14.285714285714286. One completion, fetched from the same server with the section 8 system text, was a fenced copy of the prompt's JSON skeleton, including the placeholder tokens. Published figures: enforce 2.86, audit 14.29.

**Alternatives rejected.** Stripping markdown fences before `json.loads`. Scoring a different Qwen id. Leaving the verdict `NOT_VERIFIED` after both artifacts existed.
