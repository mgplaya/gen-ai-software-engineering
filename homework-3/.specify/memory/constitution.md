<!--
Sync Impact Report
- Version change: template (unratified) -> 1.0.0
- Added principles:
  - I. Specification Is the Source of Truth
  - II. Documentation-Only Scope and End-to-End Traceability
  - III. Explicit Human Approval Gates (NON-NEGOTIABLE)
  - IV. FinTech Safety and Measurable Verification
  - V. Cost-Aware Agent Orchestration with Independent Review
- Added sections:
  - Homework Deliverables and Constraints
  - Specification Workflow and Quality Gates
- Removed sections: none; template placeholders were resolved
- Templates requiring updates:
  - ✅ .specify/templates/plan-template.md
  - ✅ .specify/templates/spec-template.md
  - ✅ .specify/templates/tasks-template.md
  - ✅ .specify/templates/checklist-template.md
- Runtime guidance reviewed:
  - ✅ AGENTS.md
  - ✅ ../AGENTS.md
  - ✅ TASKS.md
- Follow-up TODOs: none
-->
# Homework 3 Specification Package Constitution

## Core Principles

### I. Specification Is the Source of Truth

The approved specification MUST be the authoritative statement of product intent, scope,
requirements, constraints, and measurable outcomes. Plans and tasks MUST trace to requirement
or objective identifiers and MUST NOT introduce behavior absent from the approved specification.
Any material requirement change MUST be made in the specification first, then propagated to
affected downstream artifacts and revalidated.

Rationale: a specification-driven submission is graded on clarity and traceability; allowing plans
or tasks to become an independent source of requirements creates contradictions and hidden scope.

### II. Documentation-Only Scope and End-to-End Traceability

Homework 3 MUST produce documentation only. Source code, executable prototypes, application
scaffolding, migrations, dependency installation, and implemented APIs or UIs are prohibited.
Hypothetical system components MAY be described when necessary to make tasks implementable.
Every low-level task MUST reference the mid-level objective, requirement, policy, or verification
criterion it serves, and every in-scope requirement MUST be covered by at least one task and one
verification method.

Rationale: the graded artifact is the executable-quality specification package, not a working
application. Traceability demonstrates that the package could guide later implementation without
guessing.

### III. Explicit Human Approval Gates (NON-NEGOTIABLE)

Work MUST progress through explicit human approval gates. Silence, partial feedback, acceptance of
one artifact, or permission to continue discovery MUST NOT be treated as approval of a later phase.
The specification MUST be approved before planning; the plan MUST be approved before task
generation; the complete package MUST pass consistency analysis and receive final approval before
the workflow is considered complete. A material change invalidates the approval of the changed
artifact and affected downstream artifacts.

Rationale: human review is the control boundary that prevents an agent from amplifying an incorrect
assumption across generated artifacts.

### IV. FinTech Safety and Measurable Verification

The specification MUST define domain-specific security, privacy, authorization, auditability,
data-handling, concurrency/idempotency, reliability, and error-semantics requirements. It MUST
include concrete edge cases and failure modes with expected user-visible and operations/compliance
outcomes. Performance and consistency targets MUST be measurable and explicitly labeled as assumed
when not derived from observed data. Each mid-level objective MUST have an objective verification
method, and high-risk requirements MUST receive an independent security or compliance review.

Rationale: vague safety language is not executable in a regulated environment and cannot be
reliably tested, audited, or approved.

### V. Cost-Aware Agent Orchestration with Independent Review

Tasks MUST be decomposed by domain responsibility, risk, context, dependency, and independently
verifiable output in addition to complexity and iteration. Each task MUST declare an agent role,
model tier (Economy, Standard, or Advanced), tier rationale, inputs, output, dependencies,
parallel-safety, and acceptance criteria. The least expensive reliable tier MUST be used: Economy
for mechanical transformations, Standard for bounded drafting and analysis, and Advanced only for
ambiguous or high-risk product, architecture, FinTech, security, compliance, or gate decisions.
Material artifacts MUST receive review by a role independent from their primary author.

Rationale: targeted escalation preserves quality while avoiding the cost and latency of using the
strongest model for routine tasks.

## Homework Deliverables and Constraints

The authoritative assignment brief is `TASKS.md`. The final package MUST contain:

- `specification.md`: layered product specification with objectives, requirements, non-functional
  and policy constraints, implementation guardrails, beginning and ending context, edge cases,
  verification, assumed performance targets, and traceable low-level tasks;
- `agents.md`: domain and engineering guidance for future AI implementers;
- one editor/AI rules artifact in an assignment-approved location;
- `README.md`: student/task summary, rationale, target-selection rationale, verification depth,
  and mapped industry practices.

Spec Kit working artifacts under `.specify/` and `specs/` MAY supplement the graded files, but MUST
NOT create competing authoritative versions. The final `homework-3/specification.md` is the canonical
graded specification. Sensitive financial data MUST never be added to examples, fixtures, prompts,
logs, or repository documents; all examples MUST use clearly synthetic and masked values.

## Specification Workflow and Quality Gates

The workflow MUST use the relevant Spec Kit phases:

1. Establish and validate this constitution.
2. Create the product specification with assumptions and open questions recorded.
3. Clarify material ambiguity and run requirement-quality checklists.
4. Gate 1: obtain explicit approval of the validated specification.
5. Create the delivery/technical plan and re-run the Constitution Check.
6. Gate 2: obtain explicit approval of the validated plan.
7. Generate low-level tasks with requirement traceability and agent/model assignments.
8. Analyze cross-artifact consistency, coverage, risk, and assignment suitability.
9. Gate 3: obtain explicit final approval of the complete documentation package.
10. Stop. `speckit-implement` MUST NOT be run for Homework 3.

Before every gate, the agent MUST report the artifact scope, validation evidence, resolved findings,
unresolved questions, assumptions, risks, and the exact approval requested. Parallel work is allowed
only for tasks with non-overlapping outputs and no unresolved shared decision. Status and decisions
MUST be recorded in repository artifacts rather than relying on chat history.

## Governance

This constitution governs all Homework 3 Spec Kit artifacts and supersedes conflicting generated
defaults. Amendments require a documented rationale, impact analysis, semantic version change, and
explicit user approval. MAJOR versions remove or redefine a governing principle or approval model;
MINOR versions add a principle or materially expand obligations; PATCH versions clarify wording
without changing obligations.

Every specification, plan, task list, checklist, and final package review MUST include a Constitution
Check. Noncompliance MUST be resolved before the next approval gate; exceptions are not permitted for
the documentation-only boundary or explicit approval gates. `AGENTS.md` provides repository-level
runtime guidance, while this constitution is the authority for Homework 3 artifact governance.

**Version**: 1.0.0 | **Ratified**: 2026-07-15 | **Last Amended**: 2026-07-15
