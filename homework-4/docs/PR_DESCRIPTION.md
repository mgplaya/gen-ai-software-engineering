# Homework 4 — Architect-Led TDD Build Pipeline (spec-driven with GitHub Spec Kit)

## Summary

This PR delivers a **5-agent, research-first, test-driven** pipeline built spec-first
with [GitHub Spec Kit](https://github.com/github/spec-kit), operating on a small
Python `expense_splitter` seeded with **2 intentional bugs + 1 security
vulnerability** (Task 5). From **one command** an **Architect** researches the bugs
and plans the fixes; the run **stops for a human to verify the plan**; then
`--continue` writes **failing TDD tests that reproduce the bugs (RED)**, the **Bug
Fixer** turns them GREEN, and a **Security Verifier** reviews the result. Each
subagent runs on a **deliberately chosen model**.

## Why this shape

Seeded bugs + TDD is the discipline being demonstrated:
- **Reproduce before you fix** — a cheap Test-Author writes tests asserting the
  correct behavior; they must be RED against the buggy code (proving the bug),
  before any fix.
- **Fix, don't weaken** — a separate Bug Fixer turns the tests GREEN without editing
  them, so the fix is provably driven by the failing tests.
- **Verify twice** — a human verifies the Architect's plan at a gate, and a Bug
  Research Verifier machine-checks the research against the real source.
- **Right model for the job** — heavy models for research/verification/security, a
  cheap model for mechanical test authoring, a mid-tier for the fix.

## Pipeline (fixed order + models)

```
Architect (opus-4-8)  — researches bugs + plans fixes
  → [HUMAN VERIFIES THE PLAN]
  → Bug Research Verifier (opus-4-8, read-only)
  → Unit Test Generator (haiku-4-5)  — RED: tests reproduce the bugs
  → Bug Fixer (sonnet-5)             — GREEN: fixes the bugs
  → Security Verifier (opus-4-8, read-only)
```

All four homework-required agents are present (Bug Research Verifier, Bug Fixer,
Security Verifier, Unit Test Generator); the **Architect** (Bug Researcher + Planner)
is added, and the flow is TDD-ordered (failing tests reproduce the bugs before the
fix).

## Model selection (justified per agent)

| Agent | Model | Rationale |
|-------|-------|-----------|
| Architect | opus-4-8 | Highest-leverage, open-ended design reasoning. |
| Bug Research Verifier | opus-4-8 | Approving a bad design is the costly failure. |
| Unit Test Generator | **haiku-4-5** | Mechanical assertion-writing → cheapest model. |
| Bug Fixer | sonnet-5 | Real but bounded algorithmic work. |
| Security Verifier | opus-4-8 | Adversarial review; false negatives are expensive. |

## Enforced permission boundaries

Per-stage `--allowedTools`: verifiers get `Read Glob Grep Write` (no Edit/Bash), the
Architect gets no Bash, only Bug Fixer/Test-Gen get `Edit Bash`. Single
responsibility is a hard boundary, not a prompt.

## Spec Kit artifacts

Under `specs/001-tdd-build-pipeline/`: constitution (v2.1.0, 7 principles incl.
*Research-First, then TDD* and the human gate), `spec.md`, `plan.md` (Constitution
Check passes), `research.md`, `data-model.md`, `contracts/agent-io.md`,
`quickstart.md`, `tasks.md`.

## How to run / verify

See `homework-4/HOWTORUN.md`:

```bash
cd homework-4
python3.11 -m venv .venv && ./.venv/bin/pip install -r requirements.txt
./run-pipeline.sh              # Architect researches bugs, then STOPS for plan verification
./run-pipeline.sh --continue   # verify → RED (reproduce bugs) → GREEN (fix) → security
python -m pytest               # green
```

## Run results (real end-to-end run, `context/bugs/001/pipeline-run.log`)

| Stage | Model | Result |
|-------|-------|--------|
| Architect | opus-4-8 | Researched BUG-1/BUG-2/SEC-1 against source → `research/codebase-research.md` + `implementation-plan.md` (exact before/after fixes). |
| Bug Research Verifier | opus-4-8 | **PASS — Research Quality A (Verified)**; every bug's `file:line` + snippet + root cause confirmed against source. |
| Unit Test Generator (RED) | haiku-4-5 | Wrote tests asserting correct behavior → **RED: 11 failing** (of 29) reproducing BUG-1/BUG-2/SEC-1. |
| Bug Fixer (GREEN) | sonnet-5 | Applied the fix plan → **GREEN: 29/29 passing**, no test files modified. |
| Security Verifier | opus-4-8 | **PASS** — 0 CRITICAL/HIGH/MEDIUM, 2 LOW, 1 INFO; SEC-1 remediated (`eval` removed; untrusted input parsed with `Decimal`, never executed). |

Independently verified after the run:

```
$ python -m pytest -q            → 29 passed
$ expense-splitter 100 3         → 33.34 / 33.33 / 33.33, Total 100.00   (reconciles; BUG-1 fixed)
$ expense-splitter "__import__('os').system('echo PWNED')" 2
                                 → "Invalid amount: ..."  exit 1  (no code executed; SEC-1 fixed)
```

Before the fix (RED), the same commands showed `Total: 99.99` and `eval` executing the
injected code — the seeded bugs, reproduced by the failing tests.

TDD is proven: the **same** tests are RED before implementation (stage 3) and GREEN
after (stage 4), with the tests unchanged between the two.

## Screenshots

Captured from the pipeline running on the seeded-buggy `expense_splitter` (full set
in [`docs/screenshots/`](https://github.com/mgplaya/gen-ai-software-engineering/tree/homework-4-submission/homework-4/docs/screenshots)):

**1. Architect (Bug Researcher + Planner) + the human plan gate** — researches the 3
bugs, writes `research/codebase-research.md` + `implementation-plan.md`, touches no
code, and STOPS for the human to verify the plan.

![Architect stage and plan gate](https://raw.githubusercontent.com/mgplaya/gen-ai-software-engineering/homework-4-submission/homework-4/docs/screenshots/01-architect-gate.png)

**2. Bug Research Verifier — PASS, Research Quality A** — every bug's `file:line` +
root cause confirmed against the real source.

![Bug Research Verifier PASS](https://raw.githubusercontent.com/mgplaya/gen-ai-software-engineering/homework-4-submission/homework-4/docs/screenshots/02-research-verified.png)

**3. TDD RED — the failing tests reproduce the bugs** — run against the seeded buggy
code, `11 failed`. Note the SEC-1 failure: `parse_amount` at `cli.py:25` actually
*executes* the input via `eval()` (`NameError: name 'not_a_number' is not defined`),
proving the injection vulnerability.

![RED — tests reproduce the seeded bugs](https://raw.githubusercontent.com/mgplaya/gen-ai-software-engineering/homework-4-submission/homework-4/docs/screenshots/05-red-tests.png)

**4. Security Verifier PASS + pipeline complete** — after the fix: SEC-1 remediated
(no `eval`); all six artifacts present under `context/bugs/001/`.

![Security verifier and pipeline complete](https://raw.githubusercontent.com/mgplaya/gen-ai-software-engineering/homework-4-submission/homework-4/docs/screenshots/03-security-complete.png)

**5. TDD GREEN — tests pass after the fix** — `29 passed`, with the tests unchanged
from the RED step.

![pytest 29 passed](https://raw.githubusercontent.com/mgplaya/gen-ai-software-engineering/homework-4-submission/homework-4/docs/screenshots/04-pytest-green.png)

The Bug Fixer turned the suite from `11 failed` (RED) to `29 passed` (GREEN) without
editing the tests — full RED→GREEN recorded in
[`context/bugs/001/test-report.md`](https://github.com/mgplaya/gen-ai-software-engineering/blob/homework-4-submission/homework-4/context/bugs/001/test-report.md) and
[`fix-summary.md`](https://github.com/mgplaya/gen-ai-software-engineering/blob/homework-4-submission/homework-4/context/bugs/001/fix-summary.md).

## AI tools used

- **Claude Code (Opus 4.8)** drove the Spec Kit workflow and authored the pipeline.
- The pipeline runs Opus 4.8 / Sonnet 5 / Haiku 4.5 via the `claude` CLI headless —
  real multi-agent execution, one model per role.

## Deliverables checklist

- [x] 5 agent definitions with explicit model in frontmatter (4 required + Architect)
- [x] 4 skills auto-loaded per agent
- [x] Single-command runner with a human plan gate (`--continue`, `--all`, `--only`, `--dry-run`)
- [x] Research-first + TDD (RED before GREEN) enforced by order and permissions
- [x] Spec Kit spec/plan/tasks/constitution committed
- [x] README + HOWTORUN + PR description
- [x] Pipeline run end-to-end; all 6 artifacts + run log present under `context/bugs/001/`
- [x] Sample app fixed + tests green (29 passed); RED→GREEN evidence recorded
- [x] Screenshots captured to `docs/screenshots/` (architect+gate, verifier, security+complete, pytest green)
