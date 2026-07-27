# Quickstart: Running the Architect-Led TDD Pipeline

**Feature**: [spec.md](./spec.md) | **Date**: 2026-07-27

## Prerequisites

- Python 3.11+ and `pytest` (`pip install -r requirements.txt`)
- Claude Code CLI (`claude`) installed and authenticated

## Step 1 — Design (Architect), then STOP for your review

```bash
cd homework-4
./run-pipeline.sh
```

Produces `context/build/001/architecture.md` and stub interfaces under
`src/expense_splitter/` (each function `raise NotImplementedError`), then halts at
the human plan gate.

## Step 2 — Verify the plan (human)

Read `context/build/001/architecture.md` (and the stubs). Confirm the interfaces,
invariants, edge cases, security requirement, and Build Sequence look right.

## Step 3 — Continue: verify design → RED tests → GREEN impl → security

```bash
./run-pipeline.sh --continue
```

Runs, in order:
1. **Design Verifier** → `verified-design.md`
2. **Unit Test Generator** → `tests/` + `test-report.md` (tests FAIL = RED)
3. **Implementer** → fills `src/` + `implementation-summary.md` (tests PASS = GREEN)
4. **Security Verifier** → `security-report.md`

## Step 4 — Confirm the build

```bash
python -m pytest              # all green
```

## Options

```bash
./run-pipeline.sh --all                    # run all 5 stages without stopping
./run-pipeline.sh --only test-author       # run one stage
./run-pipeline.sh --dry-run                # print the plan, call nothing
```

Stages for `--only`: `architect`, `design-verifier`, `test-author`, `implementer`,
`security-verifier`.
