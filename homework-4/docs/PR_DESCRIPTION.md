# Homework 4 — Architect-Led TDD Build Pipeline (spec-driven with GitHub Spec Kit)

## Summary

This PR delivers a **5-agent, design-first, test-driven** pipeline built spec-first
with [GitHub Spec Kit](https://github.com/github/spec-kit). From **one command** an
**Architect** designs a small Python app and describes the build sequence; the run
**stops for a human to verify the plan**; then `--continue` writes **failing tests
first (RED)**, **implements** the code until green (GREEN), and runs a **security
review**. Each subagent runs on a **deliberately chosen model**.

## Why this shape

Design-first + TDD is the engineering discipline being demonstrated:
- **Design before code** — the Architect produces interfaces + a build sequence a
  human verifies *before* anything is implemented.
- **Tests before implementation** — a cheap Test-Author agent writes tests that must
  be RED; a separate Implementer turns them GREEN without editing the tests, so the
  code is provably test-driven.
- **Right model for the job** — heavy models for design/verification/security, a
  cheap model for mechanical test authoring, a mid-tier for implementation.

## Pipeline (fixed order + models)

```
Architect (opus-4-8)
  → [HUMAN VERIFIES THE PLAN]
  → Design Verifier (opus-4-8, read-only)
  → Unit Test Generator (haiku-4-5)  — TDD RED
  → Implementer (sonnet-5)           — TDD GREEN
  → Security Verifier (opus-4-8, read-only)
```

All four homework-required agents are present (Bug Research Verifier → Design
Verifier, Bug Fixer → Implementer, Security Verifier, Unit Test Generator); the
**Architect is added** and the flow is reordered into design-first TDD.

## Model selection (justified per agent)

| Agent | Model | Rationale |
|-------|-------|-----------|
| Architect | opus-4-8 | Highest-leverage, open-ended design reasoning. |
| Design Verifier | opus-4-8 | Approving a bad design is the costly failure. |
| Unit Test Generator | **haiku-4-5** | Mechanical assertion-writing → cheapest model. |
| Implementer | sonnet-5 | Real but bounded algorithmic work. |
| Security Verifier | opus-4-8 | Adversarial review; false negatives are expensive. |

## Enforced permission boundaries

Per-stage `--allowedTools`: verifiers get `Read Glob Grep Write` (no Edit/Bash), the
Architect gets no Bash, only Implementer/Test-Gen get `Edit Bash`. Single
responsibility is a hard boundary, not a prompt.

## Spec Kit artifacts

Under `specs/001-tdd-build-pipeline/`: constitution (v2.0.0, 7 principles incl.
*Design-First, then TDD* and the human gate), `spec.md`, `plan.md` (Constitution
Check passes), `research.md`, `data-model.md`, `contracts/agent-io.md`,
`quickstart.md`, `tasks.md`.

## How to run / verify

See `homework-4/HOWTORUN.md`:

```bash
cd homework-4
python3.11 -m venv .venv && ./.venv/bin/pip install -r requirements.txt
./run-pipeline.sh              # Architect designs, then STOPS for plan verification
./run-pipeline.sh --continue   # verify → RED tests → GREEN impl → security
python -m pytest               # green
```

## Run results

<!-- Fill after the gated run:
- Design quality level from verified-design.md
- RED: N tests failing (from test-report.md)
- GREEN: N passed (from implementation-summary.md)
- Security: requirement PASS + finding counts (from security-report.md)
- Attach context/build/001/pipeline-run.log
-->

_Filled after running the pipeline through the human gate._

## AI tools used

- **Claude Code (Opus 4.8)** drove the Spec Kit workflow and authored the pipeline.
- The pipeline runs Opus 4.8 / Sonnet 5 / Haiku 4.5 via the `claude` CLI headless —
  real multi-agent execution, one model per role.

## Deliverables checklist

- [x] 5 agent definitions with explicit model in frontmatter (4 required + Architect)
- [x] 4 skills auto-loaded per agent
- [x] Single-command runner with a human plan gate (`--continue`, `--all`, `--only`, `--dry-run`)
- [x] Design-first + TDD (RED before GREEN) enforced by order and permissions
- [x] Spec Kit spec/plan/tasks/constitution committed
- [x] README + HOWTORUN + PR description
- [ ] Pipeline run through the gate; artifacts + run log attached
- [ ] Screenshots captured to `docs/screenshots/`
