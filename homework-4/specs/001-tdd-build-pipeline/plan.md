# Implementation Plan: Architect-Led TDD Build Pipeline

**Branch**: `001-tdd-build-pipeline` | **Date**: 2026-07-27 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/001-tdd-build-pipeline/spec.md`

## Summary

Build a five-agent, design-first, test-driven pipeline. An **Architect** (heavy
model) designs a small Python `expense_splitter` from a feature request, scaffolds
stub interfaces, and describes the build sequence. Execution then **stops at a human
plan gate**. On `--continue`, a **Design Verifier** checks the design, a **Unit Test
Generator** (cheap model) writes failing tests (RED), an **Implementer** (mid model)
fills the stubs until the tests pass (GREEN), and a **Security Verifier** reviews the
result. One shell command (`run-pipeline.sh`) drives it via the Claude Code CLI,
auto-loading each agent's skills and granting each stage only the tools its role
permits.

## Technical Context

**Language/Version**: Python 3.11+ (target app, built from scratch); Bash
(orchestrator); Markdown (agents, skills, artifacts).

**Primary Dependencies**: Standard library only at runtime; `pytest` for tests;
Claude Code CLI (`claude`) for agent execution.

**Storage**: Flat files — `src/`, `tests/`, and artifacts under `context/build/001/`.

**Testing**: `pytest` via `python -m pytest`, `pythonpath = ["src"]`.

**Target Platform**: Local dev machine (macOS/Linux) with the Claude CLI.

**Project Type**: CLI/library mini-app produced by agentic tooling (single project).

**Performance Goals**: A full run completes in a few minutes; the app runs in ms.

**Constraints**: no network for the app; minimal deps; verifiers read-only; one
command with a human gate after design.

**Scale/Scope**: one feature area (expense splitting), ~3 functions, 5 agents, 4
skills, ~6 artifacts.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Compliance in this plan |
|-----------|-------------------------|
| I. Artifact-Driven Handoff | Named input→output artifacts per stage under `context/build/001/`. ✅ |
| II. Single Responsibility | Architect scaffolds stubs; verifiers read-only (no Edit/Bash); only Implementer writes `src/` logic; only Test Gen writes `tests/`. Enforced via per-stage `--allowedTools`. ✅ |
| III. Verification Before Trust | Human plan gate after Architect + machine Design Verifier before implementation. ✅ |
| IV. FIRST tests | Test Gen applies `unit-tests-FIRST` + `tdd-red-green`; RED proven before GREEN. ✅ |
| V. Model-Appropriateness | opus for Architect/Design-Verifier/Security; haiku for Test Gen; sonnet for Implementer; declared in frontmatter. ✅ |
| VI. Single-Command (staged) | `run-pipeline.sh` runs all stages; stops at the gate; `--continue` resumes. ✅ |
| VII. Design-First, then TDD | Fixed order design → verify → RED → GREEN → security. ✅ |

**Result**: PASS. Complexity Tracking empty.

## Project Structure

### Documentation (this feature)

```text
specs/001-tdd-build-pipeline/
├── plan.md              # This file
├── spec.md              # Feature spec
├── research.md          # Phase 0 decisions
├── data-model.md        # Phase 1 artifacts/entities
├── quickstart.md        # Phase 1 run guide
├── contracts/agent-io.md
├── checklists/requirements.md
└── tasks.md             # Phase 2 tasks
```

### Source Code (homework-4 root)

```text
homework-4/
├── run-pipeline.sh                # single command + human gate
├── agents/
│   ├── architect.agent.md         # stage 1 (opus)
│   ├── research-verifier.agent.md # stage 2 Design Verifier (opus)
│   ├── unit-test-generator.agent.md # stage 3 RED (haiku)
│   ├── bug-fixer.agent.md         # stage 4 Implementer GREEN (sonnet)
│   └── security-verifier.agent.md # stage 5 (opus)
├── skills/
│   ├── architecture-design.md
│   ├── research-quality-measurement.md
│   ├── unit-tests-FIRST.md
│   └── tdd-red-green.md
├── context/build/001/
│   ├── feature-request.md         # human seed input
│   ├── architecture.md            # Architect output (+ src/ stubs)
│   ├── verified-design.md         # Design Verifier output
│   ├── test-report.md             # Test Gen output (RED)
│   ├── implementation-summary.md  # Implementer output (GREEN)
│   └── security-report.md         # Security Verifier output
├── src/expense_splitter/          # stubs -> implementation
├── tests/                         # tests written first (RED -> GREEN)
├── pyproject.toml                 # pytest config
├── README.md / HOWTORUN.md
└── docs/screenshots/
```

**Structure Decision**: Single project. The target app is produced by the pipeline
(stubs by the Architect, logic by the Implementer); the agentic tooling lives beside
it so the "system that builds" and the "system being built" are one reviewable tree.

## Phase 0 — Research (see research.md)

Decisions: the design-first + human-gate flow, TDD red/green split across two agents,
model assignment (heavy/cheap/mid), and orchestration via headless CLI with per-stage
tool boundaries.

## Phase 1 — Design (see data-model.md, contracts/agent-io.md, quickstart.md)

Artifact schema, strict per-agent I/O + permission boundaries, and the staged run
instructions around the human gate.

## Complexity Tracking

> No constitution violations. No entries required.
