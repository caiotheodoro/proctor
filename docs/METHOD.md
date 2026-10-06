# Method

The population is a program. A request is a record. A tool call is a record. The violation set is recomputed from those records by `evaluate`, which calls no model. That is the whole method. The arms are different predictors of a set the oracle already has.

## Draw

`forge` walks the cells in `CONTRACTS.md` section 6. For each cell it draws a request from `random.Random(data_seed)`, builds the fixture, renders the trace with the cell's one mutation, and asks the oracle for the violation set. The intended class set is empty for `clean` and the singleton of the cell name otherwise. Disagreement regenerates, up to 20 times, then aborts. The task stores the oracle's set, so a later `evaluate` on the same pair returns the same set. The self-check is that second call plus the class-set comparison.

Reseeding is byte-identical: the canonical JSON of a split does not change between processes.

## Score

Each arm maps `(task, trace)` to a list of violations. Loss uses the weights and the two profiles. The bootstrap is paired when two arms are compared, so a task that is hard for both does not inflate the difference.

`flag_everything` predicts every class the contract knows how to price. It is allowed to be right about a violation and still lose, because the false positives are priced. That is why it is the floor and not a straw man made of empty predictions.

`schema_only` predicts only `schema_break`. On `wrong_unit` its recall is defined to be the quantity H3 checks, and the implementation is not given a special case that peeks at the unit.

## Judge and trained arm

Both see the user message described in the contract and do not see `violations`. Parsing is strict JSON. Failure is an empty set, which is a real prediction: on a dirty task it is all false negatives, on a clean task it is a perfect score. That asymmetry is why an empty parse is reported as a parse miss in the artifact (`parse_misses`) and still enters the loss as an empty set.

Training reward is the negative `audit` loss of the parsed completion against the oracle. The oracle is not inside the prompt. Four seeds are four processes. The exclusion assertion runs before any step.

## Card

`proctor card` writes `MEASUREMENT_CARD.json`. Fields that do not exist yet are listed under `unmet` and the verdict is `NOT_VERIFIED`. The command exits 0 when the JSON is well formed, including that verdict. `make validate` does not need a GPU, a key, or a network.
