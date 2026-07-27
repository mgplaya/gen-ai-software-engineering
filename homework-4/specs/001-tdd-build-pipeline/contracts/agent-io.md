# Contract: Agent Input/Output

**Feature**: [spec.md](../spec.md) | **Date**: 2026-07-27

Each agent is a function over files: it reads fixed inputs and writes one output
artifact (mutating agents also touch `src/`/`tests/`). `run-pipeline.sh` enforces
order, loads skills, and scopes tools.

## Stage 1 — Architect
- **Model**: `claude-opus-4-8` · **Tools**: `Read Glob Grep Edit Write` (no Bash)
- **Loads skill**: `skills/architecture-design.md`
- **Reads**: `context/build/001/feature-request.md`
- **Writes**: `context/build/001/architecture.md` + `src/expense_splitter/**` stubs
  (signatures + docstrings + `raise NotImplementedError`, no logic)
- **MUST NOT**: write tests or real implementation.
- **Then**: HUMAN PLAN GATE — pipeline stops for human verification.

## Stage 2 — Design Verifier (required "Bug Research Verifier" agent)
- **Model**: `claude-opus-4-8` · **Tools**: `Read Glob Grep Write` (read-only)
- **Loads skill**: `skills/research-quality-measurement.md`
- **Reads**: `architecture.md`, `feature-request.md`, `src/**` stubs
- **Writes**: `context/build/001/verified-design.md`
- **Output**: Verification Summary (PASS/FAIL + quality A/B/C/D); Verified Claims;
  Discrepancies; Quality Assessment; References. No code edits.

## Stage 3 — Unit Test Generator (TDD RED)
- **Model**: `claude-haiku-4-5-20251001` (cheap) · **Tools**: `Read Glob Grep Edit Write Bash`
- **Loads skills**: `skills/unit-tests-FIRST.md`, `skills/tdd-red-green.md`
- **Reads**: `architecture.md`, `verified-design.md`, `src/**` stubs
- **Writes**: `tests/**`, `context/build/001/test-report.md`
- **MUST**: tests fail (RED) because implementation is missing; do not implement.
- **Output**: Generated Tests; RED Run Outcome; FIRST Assessment; References.

## Stage 4 — Implementer (TDD GREEN) (required "Bug Fixer" agent)
- **Model**: `claude-sonnet-5` · **Tools**: `Read Glob Grep Edit Write Bash`
- **Loads skill**: `skills/tdd-red-green.md`
- **Reads**: `architecture.md`, `verified-design.md`, `test-report.md`, `src/**`, `tests/**`
- **Writes**: `src/**` (real logic), `context/build/001/implementation-summary.md`
- **MUST**: make the suite GREEN without editing tests; if a test contradicts the
  design, stop with `BLOCKED`.
- **Output**: Functions Implemented; Test Result (RED→GREEN); Overall Status; Manual
  Verification; References.

## Stage 5 — Security Verifier
- **Model**: `claude-opus-4-8` · **Tools**: `Read Glob Grep Write` (read-only)
- **Reads**: `implementation-summary.md`, `architecture.md`, implemented `src/**`
- **Writes**: `context/build/001/security-report.md` only
- **Output**: Scope; Security Requirement Check (PASS/FAIL); Findings (severity,
  `file:line`, remediation); Summary. No code edits.

## Ordering, skill-loading & gate guarantee

The stage order, per-stage tools, and gate are declared in `pipeline.yaml`; the
engine reads it and runs 1 → (gate) → 2 → 3 → 4 → 5. Before each stage it concatenates
the agent definition + its skill files into the system prompt (FR-002 skill
auto-load). The default invocation stops after stage 1; `--continue` runs 2–5. A
non-zero exit from any stage halts the pipeline (FR-001, US1 gate).
