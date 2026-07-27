# Feature Specification: Architect-Led TDD Build Pipeline

**Feature Branch**: `001-tdd-build-pipeline`

**Created**: 2026-07-27

**Status**: Draft

**Input**: User description: "A design-first, test-driven multi-agent pipeline: an Architect designs the system, a human verifies the plan, then failing tests are written and only afterwards is the code implemented; each subagent has an explicitly chosen model."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Design before build, human verifies the plan (Priority: P1)

A developer wants a small system built the disciplined way: designed first, verified
by a human, then test-driven. They run one command; an Architect produces a concrete
design (interfaces + build sequence) and the pipeline stops so the human can verify
the plan. Only after the human continues does the pipeline write failing tests and
then implement the code.

**Why this priority**: The design-first + human-gate flow is the whole point of this
pipeline. Without it there is no deliverable. It is the MVP.

**Independent Test**: Run the pipeline; confirm it produces `architecture.md` with a
Build Sequence and stub interfaces, then halts with a clear "verify the plan"
message before any implementation exists.

**Acceptance Scenarios**:

1. **Given** a feature request, **When** the developer runs the pipeline, **Then**
   the Architect writes `architecture.md` and scaffolds `src/` stubs that only
   `raise NotImplementedError`, and the run stops at a human plan gate.
2. **Given** the human has reviewed the plan, **When** they run `--continue`,
   **Then** the remaining stages run in order and the build ends green.
3. **Given** the design is judged low quality by the Design Verifier, **When** it
   reports FAIL, **Then** the report states what must change before tests/impl.

---

### User Story 2 - Tests are written before the implementation (TDD) (Priority: P2)

A developer wants genuine test-first development: the tests exist and fail before any
implementation, then the implementation makes them pass without the tests being
weakened.

**Why this priority**: TDD is the core engineering discipline being demonstrated;
it depends on US1's design existing first.

**Independent Test**: After the test stage, run the suite and confirm it is RED
(fails because the code is unimplemented); after the implement stage, confirm the
same tests are GREEN with no edits to the tests.

**Acceptance Scenarios**:

1. **Given** verified stubs, **When** the Test Generator runs, **Then** tests exist
   under `tests/` and fail because functions raise `NotImplementedError`.
2. **Given** the RED tests, **When** the Implementer runs, **Then** it fills the
   stubs so the suite is GREEN and does not modify any test.
3. **Given** a test contradicts the verified design, **When** the Implementer hits
   it, **Then** it stops and reports BLOCKED rather than editing the test.

---

### User Story 3 - Each agent runs on a deliberately chosen model (Priority: P3)

A reviewer wants to see cost/quality engineering: heavy models where reasoning is
critical (design, verification, security), a cheap model for mechanical test
authoring, a mid-tier model for implementation — each declared and justified.

**Why this priority**: Model-appropriateness is an explicit requirement and a grading
point, but it rides on the pipeline existing.

**Independent Test**: Inspect each `agents/*.agent.md` frontmatter and confirm an
explicit model that matches the role, and that the runner passes it via `--model`.

**Acceptance Scenarios**:

1. **Given** the agent definitions, **When** inspected, **Then** the Architect,
   Design Verifier, and Security Verifier use a heavy model; the Test Generator uses
   a cheap model; the Implementer uses a mid-tier model.
2. **Given** the runner, **When** a stage executes, **Then** it invokes the CLI with
   that agent's declared model.

---

### Edge Cases

- **Human never continues**: the pipeline simply stops after the Architect; nothing
  is implemented. Re-running `--continue` resumes from the design.
- **Stubs missing a name the tests need**: the Test Generator records it as a
  discrepancy instead of implementing it.
- **Tests pass before implementation**: treated as a broken RED step — a test that
  cannot fail proves nothing.
- **Security requirement violated by the implementation**: the Security Verifier
  reports it (with severity + remediation); it never edits code.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The pipeline MUST run from a single command that executes the agents in
  the fixed order Architect → Design Verifier → Unit Test Generator (RED) →
  Implementer (GREEN) → Security Verifier, auto-loading each agent's skills.
- **FR-002**: The pipeline MUST insert a human verification gate after the Architect:
  the default invocation stops after design; a `--continue` invocation runs the rest.
- **FR-003**: The Architect MUST design toward the feature request, scaffold stub
  interfaces (signatures + docstrings + `raise NotImplementedError`, no logic), name
  at least one security-sensitive requirement, and describe the build sequence in
  `architecture.md`.
- **FR-004**: The Design Verifier MUST verify every interface reference against the
  scaffolded stubs and rate design quality using the `research-quality-measurement`
  skill, writing `verified-design.md`; it MUST NOT edit code.
- **FR-005**: The Unit Test Generator MUST write FIRST-compliant tests against the
  designed interfaces BEFORE implementation, run them, and confirm they FAIL (RED),
  writing `test-report.md`; it MUST NOT implement logic.
- **FR-006**: The Implementer MUST fill the stubs so the tests pass (GREEN) without
  editing tests, and write `implementation-summary.md`; if a test contradicts the
  design it MUST stop and report BLOCKED.
- **FR-007**: The Security Verifier MUST confirm the Architect's security-sensitive
  requirement is honored and scan the implemented code, writing `security-report.md`
  only, with each finding carrying severity, `file:line`, and remediation.
- **FR-008**: Each agent MUST declare an explicit, role-appropriate model in its
  definition; test authoring MUST use a light/cheap model and system design MUST use
  a heavy model.
- **FR-009**: Verifier agents (Design Verifier, Security Verifier) MUST be read-only
  with respect to source and tests.
- **FR-010**: Every stage MUST read/write durable Markdown artifacts so a stage can
  be re-run independently and a reviewer can audit the run.
- **FR-011**: All agent definitions MUST be authored before the pipeline is run for
  the first time.
- **FR-012**: After a completed run, the target app's test suite MUST be green and
  the tests MUST have been demonstrably RED before implementation.

### Key Entities *(include if feature involves data)*

- **Feature Request**: the human-authored brief the Architect designs toward.
- **Architecture**: the design — interfaces, invariants, edge cases, security
  requirement, project structure, and build sequence (`architecture.md`) + stubs.
- **Verified Design**: the Design Verifier's quality-rated confirmation
  (`verified-design.md`).
- **Test Report**: the RED evidence — failing tests written first (`test-report.md`).
- **Implementation Summary**: the GREEN evidence — stubs filled, tests passing
  (`implementation-summary.md`).
- **Security Report**: severity-rated findings on the implemented code
  (`security-report.md`).
- **Agent**: a single-responsibility worker with a declared model, input artifacts,
  one output artifact, and a permission boundary.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A reviewer can produce a verified design and then a green build using
  one command plus one `--continue`, with a human plan gate in between.
- **SC-002**: The test suite is demonstrably RED before implementation and GREEN
  after, with the tests unchanged between the two.
- **SC-003**: Every agent has an explicit model matching its role (heavy for
  design/verify/security, cheap for tests, mid for implementation).
- **SC-004**: All five stages produce their expected report artifact; each references
  real files/lines.
- **SC-005**: The Security Verifier confirms untrusted input is never executed and
  every finding has severity, location, and remediation.

## Assumptions

- The reviewer has the Claude Code CLI installed and authenticated.
- The target app is intentionally minimal (a handful of functions) so one TDD pass
  completes quickly and cheaply.
- The feature request (`context/build/001/feature-request.md`) is the human-provided
  input; the Architect owns all design decisions from there.
