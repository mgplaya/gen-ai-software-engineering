# How to Run — Homework 4 (Architect-Led TDD Build Pipeline)

## 1. Prerequisites

- **Python 3.11+** (3.9+ works)
- **Claude Code CLI** (`claude`) installed and authenticated — the pipeline runs
  agents via `claude -p`. Verify with `claude --version`.

## 2. Environment setup

```bash
cd homework-4
python3.11 -m venv .venv
./.venv/bin/pip install -r requirements.txt   # installs pytest
```

## 3. Run — Step A: design, then STOP for your review

```bash
./run-pipeline.sh
```

This runs **only the Architect** and then halts at the human plan gate:
- writes `context/build/001/architecture.md` (design + build sequence),
- scaffolds stub interfaces under `src/expense_splitter/` (each function
  `raise NotImplementedError` — no logic yet).

## 4. Verify the plan (this is your gate)

Open and review:
```bash
context/build/001/architecture.md
src/expense_splitter/*.py            # the stubs
```
Check the public interfaces, invariants, edge cases, the security-sensitive
requirement, and the Build Sequence. Only continue when you are satisfied.

## 5. Run — Step B: continue the TDD build

```bash
./run-pipeline.sh --continue
```

Runs the remaining stages in order, with no manual steps between:
1. **Design Verifier** (`claude-opus-4-8`, read-only) → `verified-design.md`
2. **Unit Test Generator** (`claude-haiku-4-5`) → `tests/` + `test-report.md` — tests **FAIL (RED)**
3. **Implementer** (`claude-sonnet-5`) → fills `src/` + `implementation-summary.md` — tests **PASS (GREEN)**
4. **Security Verifier** (`claude-opus-4-8`, read-only) → `security-report.md`

The full transcript is saved to `context/build/001/pipeline-run.log`.

## 6. Confirm the build

```bash
python -m pytest        # all green
```

You can also confirm the RED→GREEN story: `test-report.md` shows the tests failing
before implementation; `implementation-summary.md` shows them passing after, with the
tests unchanged.

## 7. Options

```bash
./run-pipeline.sh --all                    # run all 5 stages without stopping at the gate
./run-pipeline.sh --only architect         # run a single stage
./run-pipeline.sh --only test-author       # design-verifier | test-author | implementer | security-verifier
./run-pipeline.sh --dry-run                # show the plan (order/models/skills/tools), call nothing
./run-pipeline.sh --help
```

## 8. Testing guide

- Framework: **pytest**, configured in `pyproject.toml` (`pythonpath = ["src"]`,
  `testpaths = ["tests"]`).
- Run everything: `python -m pytest` (or `./.venv/bin/python -m pytest`).
- The generated tests satisfy **FIRST** and are deterministic.

## 9. Troubleshooting

- **`claude: command not found`** — install Claude Code and ensure it is on `PATH`.
- **A stage fails** — the pipeline halts. Re-run just that stage with
  `--only <stage>` after fixing the cause.
- **`ModuleNotFoundError: expense_splitter`** — run pytest from `homework-4/`
  (pytest reads `pythonpath = ["src"]`), or set `PYTHONPATH=src` for direct CLI runs.
