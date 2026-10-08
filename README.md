# Proctor

A wrong call costs more than a schema error, and a detector that flags every call is the floor that has to be beaten.

On the 252-task test split, `flag_everything` scores 117.56 expected loss when a false block is expensive and 23.51 when a missed call is expensive. `schema_only` scores 2.71 and 13.57 on those same profiles. The paired difference on the enforce profile is -114.85, and the 95% interval runs from -119.77 to -110.26, entirely below 0. `schema_only` recall is 1.0 on `schema_break` and 0.0 on `wrong_unit`. The schema check beats the floor where false blocks dominate, and it stays blind to a unit that the schema already allows.

Proctor builds a synthetic operations desk — eight tools, six violation classes — and recomputes the violation set with a program. No model sits inside that program. `flag_everything` predicts every class the contract prices. `schema_only` predicts only a broken argument. The trained arm, QLoRA then GRPO on `Qwen/Qwen2.5-1.5B-Instruct`, scores 2.86 enforce loss on each of seeds 11, 22, 33, and 44. The across-seed standard deviation is 0.0. That loss sits 0.14 above `schema_only`, so H4 does not license a win. The same model as a prompted judge scored the test split and missed the parse on all 252 completions, so every prediction is empty. That arm's enforce loss is 2.86 and its audit loss is 14.29. The card's verdict is `VERIFIED`.

Traces are forge-rendered. Transfer to real agent logs is unmeasured.

The test split is data seed 999, 36 of each of the seven cells. That seed is not used for training and not used to choose a result. Model seeds, when the trained arm runs, are 11, 22, 33, and 44. Severity weights are 5, 2, and 1. The audit profile prices a miss at 5 and a false block at 1. The enforce profile prices a miss at 1 and a false block at 5. The interval is a 95% bootstrap with 1000 resamples.

## Status

| Item | State |
|---|---|
| Protocol | `1.0.0`, frozen |
| H1, H2, H3 on the test split | all three hold; figures are in `MEASUREMENT_CARD.json` |
| Judge `Qwen/Qwen2.5-1.5B-Instruct` | 252 parse misses; enforce 2.86; audit 14.29 |
| Trained arm, four seeds, QLoRA then GRPO | enforce loss 2.86, across-seed standard deviation 0.0, gap 0.14, not a win |
| Card verdict | `VERIFIED` |

## Published

The code is [github.com/caiotheodoro/proctor](https://github.com/caiotheodoro/proctor) at tag `v0.1.0`. The desk is [caiotheodoro/proctor-desk](https://huggingface.co/datasets/caiotheodoro/proctor-desk). The seed-11 adapter is [caiotheodoro/proctor-qlora-grpo](https://huggingface.co/caiotheodoro/proctor-qlora-grpo). The collection is [Proctor: oracle-priced agent actions](https://huggingface.co/collections/caiotheodoro/proctor-oracle-priced-agent-actions-6ac7cff4a4cc3304ff39f12c).

## Run

```sh
make install
make validate
make baselines
```

`make validate` needs no key and no GPU. The hypotheses, the cells, and the stopping rule are in `docs/PRE-REGISTRATION.md`. The conflict is in `docs/ETHICS.md`: the author works on an AI gateway, and no hypothesis calls one.

Apache-2.0.
