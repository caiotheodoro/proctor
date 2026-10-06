# Targets are the table of contents. validate needs no key and no GPU.
.PHONY: help install lint test validate privacy-gate check-no-tbd check-paths leak-probe \
        baselines judge card

help: ## List targets.
	@grep -E '^[a-z0-9-]+:.*?## .*$$' $(MAKEFILE_LIST) | sed 's/:.*## /\t/'

install: ## uv sync with the dev group.
	uv sync --group dev

lint: ## ruff over packages, tests, and scripts. Scripts only until packages exist.
	@targets="scripts"; \
	for d in schema forge oracle eval baselines model tests; do \
	  if [ -d $$d ]; then targets="$$targets $$d"; fi; \
	done; \
	uv run ruff check $$targets; \
	uv run ruff format --check $$targets

test: ## pytest. Skips with a notice until tests exist.
	@if ls tests/test_*.py >/dev/null 2>&1; then uv run pytest -q; else echo "test: no tests yet"; fi

leak-probe: ## 1.0 on a split with itself, 0.0 on train intersect test. Skips until the CLI exists.
	@if [ -f forge/proctor_forge/generate.py ]; then uv run python -m proctor_forge.leak_probe; else echo "leak-probe: generator not built yet"; fi

privacy-gate: ## Fail if a key-shaped string is in a tracked or untracked non-ignored file.
	@files="$$(git ls-files -co --exclude-standard)"; \
	if [ -z "$$files" ]; then echo "privacy-gate: no files"; exit 0; fi; \
	if echo "$$files" | xargs grep -nE '(sk-[A-Za-z0-9]{20,}|Bearer [A-Za-z0-9._-]{20,}|AKIA[0-9A-Z]{16})' -- 2>/dev/null; then \
	  echo "privacy-gate: secret-looking string found" >&2; exit 1; fi; \
	echo "privacy-gate: clean"

check-no-tbd: ## Fail on placeholder markers in markdown.
	@if grep -rnE '\b(TBD|TODO)\b' docs *.md --include='*.md'; then \
	  echo "check-no-tbd: placeholder found" >&2; exit 1; fi
	@echo "check-no-tbd: clean"

check-paths: ## Backticked repo paths exist or are declared planned in docs/HANDOFF.md.
	python3 scripts/check_paths.py

validate: ## Exit condition.
	$(MAKE) lint
	$(MAKE) test
	$(MAKE) leak-probe
	$(MAKE) privacy-gate
	$(MAKE) check-no-tbd
	$(MAKE) check-paths

baselines: ## Score flag_everything and schema_only on the test split and write the card.
	uv run python -m proctor_eval.cli baselines

judge: ## Score the pinned judge. Needs PROCTOR_JUDGE_BASE_URL.
	uv run python -m proctor_judge.cli --split test

card: ## Rewrite MEASUREMENT_CARD.json from artifacts already on disk.
	uv run python -m proctor_eval.cli card
