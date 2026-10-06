# Proctor

A wrong call costs more than a schema error, and a detector that flags every call is the floor that has to be beaten.

Proctor builds a synthetic operations desk — eight tools, six violation classes — and recomputes the violation set with a program. No model sits inside that program. `flag_everything` predicts every class the contract prices. `schema_only` predicts only a broken argument. The gap between those two, under an enforce profile where a false block is expensive and an audit profile where a missed transfer is expensive, is the measurement. A prompted open-weight judge and a model trained against the oracle are further arms. They are not the floor.

Traces are forge-rendered. Transfer to real agent logs is unmeasured.

The test split is 252 tasks, data seed 999, 36 of each of the seven cells. That seed is not used for training and not used to choose a result. Model seeds, when the trained arm runs, are 11, 22, 33, and 44. Severity weights are 5, 2, and 1. The audit profile prices a miss at 5 and a false block at 1. The enforce profile prices a miss at 1 and a false block at 5. The interval is a 95% bootstrap with 1000 resamples.

## Status

| Item | State |
|---|---|
| Protocol | draft until the freeze commit; then binding |
| `flag_everything` and `schema_only` on the test split | not in the tree yet |
| Judge `Qwen/Qwen2.5-1.5B-Instruct` | not run |
| Trained arm, four seeds, QLoRA then GRPO | not run |
| Card verdict | `NOT_VERIFIED` until the judge artifact and the four-seed spread both exist |

H1 asks whether `schema_only` beats `flag_everything` on enforce. H3 asks whether `schema_only` catches every `schema_break` and no `wrong_unit`. Neither number is written here until `MEASUREMENT_CARD.json` contains it.

## Run

```sh
make install
make validate
make baselines
```

`make validate` needs no key and no GPU. The hypotheses, the cells, and the stopping rule are in `docs/PRE-REGISTRATION.md`. The conflict is in `docs/ETHICS.md`: the author works on an AI gateway, and no hypothesis calls one.

Apache-2.0.
