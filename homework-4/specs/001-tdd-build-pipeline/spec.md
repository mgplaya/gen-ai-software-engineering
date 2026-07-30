# Feature Specification: Architect-Led TDD Pipeline

**Feature Branch**: `001-tdd-build-pipeline`

**Created**: 2026-07-27

**Status**: Draft

**Input**: User description: "A research-first, test-driven multi-agent pipeline over an app seeded with bugs: an Architect researches the bugs and plans the fixes, a human verifies the plan, then failing tests reproduce the bugs and only afterwards are the bugs fixed; each subagent has an explicitly chosen model."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Research before fixing, human verifies the plan (Priority: P1)

A developer has a small app with known bugs and wants them fixed the disciplined way:
researched first, verified by a human, then test-driven. They run one command; an
Architect produces bug research (`file:line` + root cause) and a fix plan, and the
pipeline stops so the human can verify it. Only after the human continues does the
pipeline write failing tests that reproduce the bugs and then fix them.

**Why this priority**: The research-first + human-gate flow is the whole point of this
pipeline. Without it there is no deliverable. It is the MVP.

**Independent Test**: Run the pipeline; confirm it produces `codebase-research.md`
(bugs) and `implementation-plan.md` (fixes), then halts with a clear "verify the plan"
message before any code is changed.

**Acceptance Scenarios**:

1. **Given** the seeded buggy app + `bug-context.md`, **When** the developer runs the
   pipeline, **Then** the Architect writes `codebase-research.md` and
   `implementation-plan.md` (making no code edits), and the run stops at a human gate.
2. **Given** the human has reviewed the plan, **When** they run `--continue`,
   **Then** the remaining stages run in order and the suite ends green.
3. **Given** the research is judged low quality by the Bug Research Verifier, **When**
   it reports FAIL, **Then** the report states what must change before tests/fixes.

---

### User Story 2 - Failing tests reproduce the bugs before the fix (TDD) (Priority: P2)

A developer wants genuine test-first bug fixing: tests asserting the correct behavior
exist and fail against the buggy code (reproducing the bugs), then the fix makes them
pass without the tests being weakened.

**Why this priority**: TDD is the core engineering discipline being demonstrated;
it depends on US1's research existing first.

**Independent Test**: After the test stage, run the suite and confirm it is RED
(failures reproduce the seeded bugs); after the fix stage, confirm the same tests are
GREEN with no edits to the tests.

**Acceptance Scenarios**:

1. **Given** verified research, **When** the Test Generator runs, **Then** tests exist
   under `tests/` and fail against the buggy code, one failure per seeded bug.
2. **Given** the RED tests, **When** the Bug Fixer runs, **Then** it fixes the code so
   the suite is GREEN and does not modify any test.
3. **Given** a test contradicts the verified plan, **When** the Bug Fixer hits it,
   **Then** it stops and reports BLOCKED rather than editing the test.

---

### User Story 3 - Each agent runs on a deliberately chosen model (Priority: P3)

A reviewer wants to see cost/quality engineering: heavy models where reasoning is
critical (research, verification, security), a cheap model for mechanical test
authoring, a mid-tier model for the fix — each declared and justified.

**Why this priority**: Model-appropriateness is an explicit requirement and a grading
point, but it rides on the pipeline existing.

**Independent Test**: Inspect each `agents/*.agent.md` frontmatter and confirm an
explicit model that matches the role, and that the runner passes it via `--model`.

**Acceptance Scenarios**:

1. **Given** the agent definitions, **When** inspected, **Then** the Architect, Bug
   Research Verifier, and Security Verifier use a heavy model; the Test Generator uses
   a cheap model; the Bug Fixer uses a mid-tier model.
2. **Given** the runner, **When** a stage executes, **Then** it invokes the CLI with
   that agent's declared model.

---

### Edge Cases

- **Human never continues**: the pipeline simply stops after the Architect; nothing is
  changed. Re-running `--continue` resumes from the research.
- **A researched bug isn't real**: the Bug Research Verifier flags it as a discrepancy
  and lowers the quality level rather than proceeding on it.
- **A test passes against the buggy code**: it is not exercising the bug and is a
  broken RED test — a test that cannot fail proves nothing.
- **The fix leaves a security gap**: the Security Verifier reports it (with severity +
  remediation); it never edits code.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The pipeline MUST run from a single command that executes the agents in
  the fixed order Architect → Bug Research Verifier → Unit Test Generator (RED) →
  Bug Fixer (GREEN) → Security Verifier, auto-loading each agent's skills.
- **FR-002**: The pipeline MUST insert a human verification gate after the Architect:
  the default invocation stops after research; a `--continue` invocation runs the rest.
- **FR-003**: The Architect MUST investigate the seeded bugs against the real source,
  name at least one security-sensitive requirement, and write `codebase-research.md`
  (each bug: `file:line`, root cause, correct behavior) and `implementation-plan.md`
  (exact before/after fixes + Build Sequence). It MUST NOT edit code.
- **FR-004**: The Bug Research Verifier MUST verify every bug claim against the real
  source and rate research quality using the `research-quality-measurement` skill,
  writing `verified-research.md`; it MUST NOT edit code.
- **FR-005**: The Unit Test Generator MUST write FIRST-compliant tests asserting the
  correct behavior, run them, and confirm they FAIL (RED) against the buggy code,
  writing `test-report.md`; it MUST NOT edit `src/`.
- **FR-006**: The Bug Fixer MUST apply the fixes so the tests pass (GREEN) without
  editing tests, and write `fix-summary.md`; if a test contradicts the plan it MUST
  stop and report BLOCKED.
- **FR-007**: The Security Verifier MUST confirm the security-sensitive requirement is
  honored and scan the fixed code, writing `security-report.md` only, with each
  finding carrying severity, `file:line`, and remediation.
- **FR-008**: Each agent MUST declare an explicit, role-appropriate model in its
  definition; test authoring MUST use a light/cheap model and bug research MUST use a
  heavy model.
- **FR-009**: Verifier agents (Bug Research Verifier, Security Verifier) and the
  Architect MUST be read-only with respect to source and tests.
- **FR-010**: Every stage MUST read/write durable Markdown artifacts so a stage can be
  re-run independently and a reviewer can audit the run.
- **FR-011**: All agent definitions MUST be authored before the pipeline is run for
  the first time.
- **FR-012**: The app MUST ship with at least 2 intentional functional bugs and at
  least 1 intentional security vulnerability, and after a completed run the test suite
  MUST be green with those tests demonstrably RED (reproducing the bugs) beforehand.

### Key Entities *(include if feature involves data)*

- **Bug Context**: the human-authored description of the seeded defects
  (`bug-context.md`) the Architect investigates.
- **Codebase Research**: the confirmed bugs — `file:line`, root cause, correct
  behavior (`codebase-research.md`).
- **Implementation Plan**: the ordered fixes (before/after) + Build Sequence
  (`implementation-plan.md`).
- **Verified Research**: the Bug Research Verifier's quality-rated confirmation
  (`verified-research.md`).
- **Test Report**: the RED evidence — failing tests reproducing the bugs
  (`test-report.md`).
- **Fix Summary**: the GREEN evidence — bugs fixed, tests passing (`fix-summary.md`).
- **Security Report**: severity-rated findings on the fixed code
  (`security-report.md`).
- **Agent**: a single-responsibility worker with a declared model, input artifacts,
  one output artifact, and a permission boundary.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A reviewer can produce verified research and then a green fix using one
  command plus one `--continue`, with a human plan gate in between.
- **SC-002**: The test suite is demonstrably RED (reproducing the bugs) before the fix
  and GREEN after, with the tests unchanged between the two.
- **SC-003**: Every agent has an explicit model matching its role (heavy for
  research/verify/security, cheap for tests, mid for the fix).
- **SC-004**: All five stages produce their expected report artifact; each references
  real files/lines.
- **SC-005**: The Security Verifier confirms untrusted input is never executed and
  every finding has severity, location, and remediation.

## Assumptions

- The reviewer has the Claude Code CLI installed and authenticated.
- The target app is intentionally minimal (a handful of functions) so one TDD pass
  completes quickly and cheaply.
- `bug-context.md` (the seeded defects) is the human-provided input; the Architect
  derives the research and fix plan from there and the real source.
