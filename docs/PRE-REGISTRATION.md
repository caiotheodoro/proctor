# Pre-registration

Revision: `1.0.0-draft`

This file is the protocol. Arms, cells, sample sizes, statistics, hypotheses, and stopping rules do not change because a result was inconvenient. After the freeze commit, this file is not edited. A change is a dated entry in `docs/DECISIONS.md` naming what changed, why, and which number it used to be.

## Populations

The three splits in `CONTRACTS.md` section 6 are the only populations. `test` (data seed 999, 252 tasks, 36 per cell) is the only split a reported loss may use. `dev` (seed 777, 84 tasks) may be read while debugging the harness and may not be used to choose a model seed, a threshold, or a prompt. `train` (seed 7, 420 tasks) is the only split the trained arm may fit on.

No task is added after freeze. No class is added after freeze. No arm is added after freeze.

## Hypotheses

All four are scored on `test`. No optional stopping. No second look that drops a cell.

- **H1 (primary).** On `enforce`, the paired difference `schema_only` minus `flag_everything` has a 95% interval entirely below 0. The floor is the thing the schema check has to beat, and the profile is the one where a false block is expensive.
- **H2.** On `audit`, `schema_only` expected loss is greater than 0. The oracle's own loss is 0 by construction; this hypothesis says the schema check does not reach it.
- **H3 (primary).** `schema_only` recall on `schema_break` is 1, and its recall on `wrong_unit` is 0, on the gold items in those cells.
- **H4.** No claim that `trained` beats `schema_only` is made unless the difference in test expected loss on `enforce` exceeds the standard deviation of that loss across model seeds 11, 22, 33, and 44. Until those four artifacts exist, H4 is unmet and the card stays `NOT_VERIFIED`.

H1 and H3 do not depend on a model. H4 does. The judge arm is reported and is not a hypothesis. A missing judge server does not change H1–H3.

## Statistics

Expected loss and recall are defined in `CONTRACTS.md` section 9. Bootstrap: 1000 resamples, seed 11011, percentile 95% interval. The paired interval resamples task indices once.

The generator self-check is not a statistic. It is a pipeline gate: intended class set equals the oracle class set, or the draw is discarded, and 20 failures in a row abort the build.

The leak probe prints `1.0` for a split intersected with itself and `0.0` for `train` intersected with `test`. A non-zero cross-split overlap aborts the build.

## Judge

One model id: `Qwen/Qwen2.5-1.5B-Instruct`. Temperature 0. One completion per task. The system text is `CONTRACTS.md` section 8, byte for byte. Unparseable output is an empty prediction and is counted. The judge does not see the planted violation list. The prompt is built from `request`, `tools`, `fixture`, and `trace` only.

## Training

Base weights are the same id as the judge, loaded 4-bit, adapted with QLoRA, then updated with GRPO against the oracle on the train split only. Seeds 11, 22, 33, 44. Seed 999 is excluded by an assertion that runs before the first optimizer step and fails the process if a test-split row is present. Checkpoints live in separate directories. The laptop is not a training device.

## Stopping and exclusions

A task that fails the self-check 20 times aborts; it is not dropped quietly. A run that cannot reach the judge server records the arm unmet and still publishes H1–H3. A run that cannot reach Modal or an AWS g5 records the trained arm unmet. Neither case is filled with a proxy model.

## What this protocol does not claim

Forge-rendered traces are the population. Real agent logs are outside it. Jailbreak intent is outside it, because that label is not a program. A TrueFoundry tenant is not a condition of any hypothesis.

**Open:** H4, until `artifacts/train/seed-11/`, `artifacts/train/seed-22/`, `artifacts/train/seed-33/`, and `artifacts/train/seed-44/` each contain a manifest whose `backend` is `qlora-grpo` and whose `data_seed_excluded` is 999. Trigger: those four files exist and `proctor card` is re-run.

**Open:** the judge arm's loss, until `artifacts/judge/test.json` exists for the pinned model. Trigger: `proctor judge --split test` against a reachable server.
