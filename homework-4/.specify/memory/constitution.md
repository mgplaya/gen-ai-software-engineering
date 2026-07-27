<!--
Sync Impact Report
Version change: 1.0.0 → 2.0.0
Bump rationale: MAJOR. The pipeline is redefined from a bug-fix flow into a
design-first, TDD build flow led by an Architect, with a human plan-verification
gate. Principles were re-authored accordingly.
Modified principles:
  - I. Artifact-Driven Handoff (kept, updated artifact chain)
  - II. Single Responsibility per Agent (kept, updated permission map)
  - III. Verification Before Trust (kept, now includes human plan gate)
  - IV. Test Discipline — FIRST (kept)
  - V. Model-Appropriateness (kept, explicit "cheap for tests / heavy for design")
  - VI. Reproducible Single-Command Execution (kept, now staged around the gate)
Added principles:
  - VII. Design-First, Then TDD (NON-NEGOTIABLE) — the core new principle
Added sections: none (structure preserved).
Removed sections: seeded-bug constraints (the app is now built from scratch, clean).
Templates requiring updates:
  - .specify/templates/plan-template.md ✅ Constitution Check gate still applies
  - specs/001-agent-bug-pipeline/* ✅ rewritten to the TDD build pipeline
Follow-up TODOs: none.
-->

# Architect-Led TDD Build Pipeline — Constitution

## Core Principles

### I. Artifact-Driven Handoff (NON-NEGOTIABLE)

Every agent communicates ONLY through durable, human-readable Markdown artifacts on
disk plus the source tree — never hidden state. Each agent reads its declared inputs
and writes exactly one declared report artifact (agents that produce code also touch
the source/test tree). The contract chain is:
`feature-request.md` → `architecture.md` (+ stubs) → `verified-design.md` →
`test-report.md` (RED) → `implementation-summary.md` (GREEN) → `security-report.md`.
Rationale: durable artifacts make the run auditable, resumable, and gradable, and let
any stage be re-run without re-running upstream stages.

### II. Single Responsibility per Agent

Each agent has one job and a bounded permission set. The **Architect** designs and
scaffolds interfaces (stubs only, no logic). The **Design Verifier** and **Security
Verifier** are READ-ONLY and MUST NOT edit code. The **Unit Test Generator** writes
only under `tests/`. The **Implementer** (the required "Bug Fixer" agent in its
build role) is the only agent that writes real logic under `src/`. Rationale:
separating who designs, who tests, who implements, and who reviews prevents any one
agent from grading its own work.

### III. Verification Before Trust (human + machine)

The design is verified before a single line of logic is implemented. A **human plan
gate** is mandatory: after the Architect produces the design, execution STOPS and a
human verifies the plan before the pipeline continues. In addition, the Design
Verifier machine-checks the architecture for completeness and consistency using the
research-quality rubric. Rationale: the cheapest place to catch a wrong design is
before implementation and tests are built on top of it.

### IV. Test Discipline — FIRST (NON-NEGOTIABLE)

Unit tests MUST satisfy FIRST (Fast, Independent, Repeatable, Self-validating,
Timely). In this pipeline tests are written **before** the implementation exists, so
they MUST first fail for the right reason (missing implementation), then pass
unchanged once the implementation lands. Rationale: a test that never demonstrably
failed proves nothing.

### V. Model-Appropriateness (explicit per agent)

Every agent MUST declare an explicit model in its `*.agent.md` frontmatter, matched
to its cognitive load, and justified in the README:
- **Heavy models** (strongest reasoning) for the hardest, most correctness-critical
  work: system design (Architect), design verification, and security review.
- **Light / cheap models** for lower-reasoning mechanical work — in particular
  **writing tests** — to keep runs economical.
- **Mid-tier models** for implementation.
Rationale: spend reasoning where mistakes are expensive; economize where they are
not.

### VI. Reproducible Single-Command Execution (staged around the gate)

The pipeline runs from ONE command that starts every agent in the correct order and
loads each agent's skills automatically. Execution is staged around the human gate:
the first invocation runs the Architect and stops; a `--continue` invocation runs the
remaining stages. Every run is reproducible from a clean checkout. Rationale: a
one-command, deterministic, gated pipeline is the graded deliverable.

### VII. Design-First, Then TDD (NON-NEGOTIABLE)

We design before we build, and we test before we implement. The fixed order is:
**Architect designs → human verifies the plan → design is machine-verified → failing
tests are written (RED) → implementation makes them pass (GREEN) → security review**.
No agent may implement production logic before the design is verified and the failing
tests exist. Rationale: this is the methodology the homework is demonstrating; skipping
straight to code is precisely what this pipeline exists to prevent.

## Pipeline Constraints

- **Skills are authoritative rubrics.** Architecture quality uses the
  `architecture-design` skill; TDD discipline uses the `tdd-red-green` skill; design
  quality uses `research-quality-measurement`; test quality uses `unit-tests-FIRST`.
  Agents MUST apply the relevant skill rather than inventing ad-hoc criteria.
- **The app is built clean, from scratch.** The target (`expense_splitter`) starts as
  Architect-authored stubs raising `NotImplementedError`; the Implementer fills them
  in. There are no pre-seeded bugs.
- **Security is designed-in, not seeded.** The Architect MUST call out at least one
  security-sensitive requirement (e.g. never `eval` untrusted CLI input); the Security
  Verifier confirms the implementation honors it.
- **Report-only agents produce no code edits.** Design Verifier and Security Verifier
  output reports only, with findings, severity where relevant, and `file:line`.

## Development Workflow

- Built spec-first with GitHub Spec Kit: constitution → `/speckit-specify` →
  `/speckit-plan` → `/speckit-tasks` → implement.
- Every implementation task MUST trace to a functional requirement in `spec.md`.
- All agent definitions ("what each agent does") MUST be authored and reviewed
  BEFORE the pipeline is run for the first time.
- Documentation (README, HOWTORUN) and screenshots are part of "done".

## Governance

This constitution supersedes ad-hoc practices for this homework. Amendments require a
Sync Impact Report entry, a semantic version bump, and a note in the PR. Versioning:
MAJOR for principle removal/redefinition, MINOR for added principles or materially
expanded guidance, PATCH for clarifications. All PRs MUST verify that agent behavior
and pipeline order comply with these principles; unjustified complexity is grounds
for revision.

**Version**: 2.0.0 | **Ratified**: 2026-07-27 | **Last Amended**: 2026-07-27
