---
description: "Task list for the Architect-Led TDD Build Pipeline"
---

# Tasks: Architect-Led TDD Build Pipeline

**Input**: Design documents from `specs/001-tdd-build-pipeline/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/agent-io.md

**Tests**: Test tasks ARE included — TDD (tests-first) is the core of this feature.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: US1 (research-first + gate), US2 (TDD), US3 (models)

## Path Conventions

Single project rooted at `homework-4/` — `agents/`, `skills/`, `src/`, `tests/`,
`context/bugs/001/`.

---

## Phase 1: Setup

- [x] T001 Create dirs: `agents/`, `skills/`, `context/bugs/001/`, `docs/screenshots/`
- [x] T002 [P] `pyproject.toml` (pytest, `pythonpath=["src"]`) + `requirements.txt`
- [x] T003 [P] `.gitignore` (`.venv`, `__pycache__`, `.pytest_cache`)

## Phase 2: Author ALL agent definitions BEFORE running (Constitution: FR-011)

- [x] T004 [US3] `agents/architect.agent.md` — model `claude-opus-4-8`, loads architecture-design skill, researches bugs + plans fixes
- [x] T005 [US3] `agents/research-verifier.agent.md` — Bug Research Verifier, `claude-opus-4-8`, read-only
- [x] T006 [US3] `agents/unit-test-generator.agent.md` — RED, `claude-haiku-4-5-20251001` (cheap), loads FIRST + tdd-red-green
- [x] T007 [US3] `agents/bug-fixer.agent.md` — Bug Fixer GREEN, `claude-sonnet-5`, loads tdd-red-green
- [x] T008 [US3] `agents/security-verifier.agent.md` — `claude-opus-4-8`, report-only

## Phase 3: Skills

- [x] T009 [P] `skills/architecture-design.md` (Architect rubric + required sections)
- [x] T010 [P] `skills/tdd-red-green.md` (RED/GREEN discipline for stages 3 & 4)
- [x] T011 [P] `skills/research-quality-measurement.md` (design-quality A/B/C/D)
- [x] T012 [P] `skills/unit-tests-FIRST.md` (FIRST properties)

## Phase 4: Orchestration + seed input

- [x] T013 [US1] `context/bugs/001/bug-context.md` (human seed brief)
- [x] T014 [US1] `run-pipeline.sh`: fixed order Architect→Verify→RED→GREEN→Security, auto-load skills, per-stage `--allowedTools`
- [x] T015 [US1] Human plan gate: default stops after Architect; `--continue` runs 2..5; `--all` bypasses; `--only <stage>`; `--dry-run`
- [x] T016 [US1] Verify `--dry-run` shows correct order, models, skills, tool boundaries

## Phase 5: User Story 1 — Research-first + human gate (RUN)

**Independent Test**: `./run-pipeline.sh` yields codebase-research.md + implementation-plan.md, then halts.

- [ ] T017 [US1] Run Stage 1 (Architect) → `codebase-research.md` + `implementation-plan.md` (bugs researched + fixes planned)
- [ ] T018 [US1] **Human verifies the plan** (review codebase-research.md + implementation-plan.md) ← gate

## Phase 6: User Story 2 — TDD RED→GREEN (RUN, after --continue)

**Independent Test**: suite RED after stage 3, GREEN after stage 4, tests unchanged.

- [ ] T019 [US1] Run Stage 2 (Bug Research Verifier) → `verified-research.md` (quality level)
- [ ] T020 [US2] Run Stage 3 (Unit Test Generator) → tests under `tests/`, confirm RED, `test-report.md`
- [ ] T021 [US2] Run Stage 4 (Bug Fixer) → apply fixes, suite GREEN, `fix-summary.md`
- [ ] T022 [US2] Confirm the RED tests were not edited between RED and GREEN

## Phase 7: User Story 2/3 — Security + verification (RUN)

- [ ] T023 [US2] Run Stage 5 (Security Verifier) → `security-report.md` (requirement honored + findings)
- [ ] T024 [US3] Confirm verifier stages made no source/test edits (permission boundary held)

## Phase 8: Polish

- [ ] T025 [P] README (architecture, per-agent model justification, author info)
- [ ] T026 [P] HOWTORUN (staged run around the gate)
- [ ] T027 Screenshots → `docs/screenshots/`
- [ ] T028 PR description

---

## Dependencies & Execution Order

- Phases 1–4 (author everything) MUST complete before any run (FR-011).
- Run order is fixed by the pipeline; the human gate sits between T018 and T019.
- Polish last.

## Notes

- Authoring agents (T004–T008) is `[P]`-friendly; executing them (T017–T023) is
  strictly ordered.
- T024 is a Constitution Principle II gate (verifier read-only boundary).
