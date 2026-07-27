# Phase 0 Research: Architect-Led TDD Build Pipeline

**Feature**: [spec.md](./spec.md) | **Date**: 2026-07-27

## Decision 1 — Design-first with a human plan gate

**Decision**: An Architect designs the system and scaffolds interfaces before any
logic is written; the pipeline then STOPS so a human verifies the plan; only
`--continue` proceeds.

**Rationale**: The cheapest place to catch a wrong design is before tests and code
depend on it. A human gate makes "I verify the plan" a first-class step, not an
afterthought. Alternatives (fully autonomous end-to-end) were rejected because they
remove the human checkpoint the methodology requires.

## Decision 2 — TDD split across two agents (RED then GREEN)

**Decision**: The Unit Test Generator writes failing tests first (RED); a separate
Implementer makes them pass (GREEN) without editing tests.

**Rationale**: Separating who writes tests from who writes code prevents the
implementer from weakening tests to go green, and produces two artifacts
(`test-report.md` RED, `implementation-summary.md` GREEN) that together prove the
code was test-driven. Alternative (same agent writes tests + code) was rejected — it
cannot demonstrate RED before GREEN.

## Decision 3 — Model assignment (heavy / cheap / mid)

**Decision**:

| Agent | Model | Why |
|-------|-------|-----|
| Architect | `claude-opus-4-8` | System design is the highest-leverage, most open-ended reasoning; errors propagate everywhere. |
| Design Verifier | `claude-opus-4-8` | Approving an incomplete design is the costly failure; needs strongest reasoning. |
| Unit Test Generator | `claude-haiku-4-5-20251001` | Turning a specified interface into assertions is mechanical → cheapest model (explicit project policy: tests use cheap models). |
| Implementer | `claude-sonnet-5` | Real algorithmic work bounded by a verified design + fixed tests → capable mid-tier. |
| Security Verifier | `claude-opus-4-8` | Adversarial review where false negatives are expensive. |

**Rationale**: Constitution Principle V — spend reasoning where mistakes are
expensive; economize on mechanical work.

## Decision 4 — Target app: expense_splitter, built from scratch

**Decision**: The pipeline builds a tiny `expense_splitter` (even split, weighted
split, safe CLI amount parsing) from scratch — no pre-seeded bugs.

**Rationale**: Crisp, checkable correctness properties (shares sum to total;
proportional weighted shares) make TDD assertions unambiguous, and CLI input parsing
gives a natural security-sensitive requirement (never `eval` untrusted input).
Minimal deps keep a full run fast and cheap.

## Decision 5 — Orchestration via headless CLI with per-stage tool boundaries

**Decision**: `run-pipeline.sh` calls `claude -p` once per stage, injects the agent
definition + its skills into the system prompt, and grants each stage only the tools
its role permits (verifiers: `Read Glob Grep Write`; Architect: no Bash; Implementer
& Test Gen: `+ Edit Bash`).

**Rationale**: One dependency-free command satisfies single-command execution and
skill auto-loading; per-stage `--allowedTools` turns the read-only boundary into a
hard enforcement rather than a prompt suggestion. `--dangerously-skip-permissions`
was rejected (blocked by the environment and unnecessary); `--permission-mode
acceptEdits` + scoped tools is safer and sufficient.
