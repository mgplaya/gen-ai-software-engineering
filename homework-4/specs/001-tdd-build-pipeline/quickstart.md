# Quickstart: Running the Architect-Led TDD Pipeline

**Feature**: [spec.md](./spec.md) | **Date**: 2026-07-27

## Prerequisites

- Python 3.11+ and `pytest` (`pip install -r requirements.txt`)
- Claude Code CLI (`claude`) installed and authenticated

## Step 1 — Research the bugs (Architect), then STOP for your review

```bash
cd homework-4
./run-pipeline.sh
```

Produces `context/bugs/001/research/codebase-research.md` (each seeded bug with
`file:line` + root cause + correct behavior) and `context/bugs/001/implementation-plan.md`
(exact before/after fixes), then halts at the human plan gate.

## Step 2 — Verify the plan (human)

Read `codebase-research.md` and `implementation-plan.md`. Confirm the bugs, root
causes, correct behaviors, and the proposed fixes look right.

## Step 3 — Continue: verify → RED (reproduce bugs) → GREEN (fix) → security

```bash
./run-pipeline.sh --continue
```

Runs, in order:
1. **Bug Research Verifier** → `research/verified-research.md`
2. **Unit Test Generator** → `tests/` + `test-report.md` (tests FAIL = RED, reproducing the bugs)
3. **Bug Fixer** → fixes `src/` + `fix-summary.md` (tests PASS = GREEN)
4. **Security Verifier** → `security-report.md`

## Step 4 — Confirm the build

```bash
python -m pytest              # all green
```

## Options

```bash
./run-pipeline.sh --list                   # show the workflow (pipeline.yaml)
./run-pipeline.sh --all                    # run all 5 stages without stopping
./run-pipeline.sh --only test-author       # run one stage by id
./run-pipeline.sh --dry-run                # print the plan, call nothing
```

Stage ids: `architect`, `research-verifier`, `test-author`, `bug-fixer`,
`security-verifier`.

Stages for `--only`: `architect`, `research-verifier`, `test-author`, `bug-fixer`,
`security-verifier`.
