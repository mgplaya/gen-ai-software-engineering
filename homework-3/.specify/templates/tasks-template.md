---
description: "Agent-routed task list template for the Homework 3 documentation package"
---

# Tasks: [FEATURE NAME]

**Input**: Approved design documents from `/specs/[###-feature-name]/`  
**Prerequisites**: approved `spec.md`, approved `plan.md`, applicable research and checklists  
**Scope**: Task definitions describe future implementable slices, but Homework 3 executes only the
documentation tasks required to produce and validate the specification package.

## Required Task Format

```text
- [ ] T### [P?] [Story/Concern] Task title
  - Traces to: OBJ/FR/NFR/EC/SC IDs
  - Agent: role
  - Model tier: Economy | Standard | Advanced
  - Tier rationale: why this is the least expensive reliable tier
  - Inputs: exact approved artifacts/sections
  - Output: exact file/section or review report
  - Dependencies: task IDs or None
  - Parallel-safe: Yes/No — reason
  - Acceptance criteria: observable check(s)
  - Reviewer: independent role and tier, when material
```

`[P]` is allowed only when outputs do not overlap and no unresolved shared decision exists. Tasks
MUST be ordered by dependencies and grouped into independently verifiable delivery phases. Every
in-scope requirement MUST have both task and verification coverage.

## Phase 1: Approved Inputs and Traceability Foundation

**Purpose**: Confirm Gate 2 inputs and establish IDs/mappings before parallel drafting.

- [ ] T001 Validate exact approved spec and plan versions using the required format above.
- [ ] T002 Build the objective-to-requirement-to-verification coverage matrix.

**Checkpoint**: No unresolved material requirement or missing identifier blocks decomposition.

## Phase 2: Canonical Specification Package

**Purpose**: Produce the graded documentation artifacts from approved inputs.

### Specification Workstreams

- [ ] TXXX [P] [Product] Draft or reconcile objectives, stories, scope, and acceptance behavior.
- [ ] TXXX [P] [FinTech] Draft or reconcile policy, security, audit, and data boundaries.
- [ ] TXXX [P] [Quality] Draft or reconcile edge cases, failure modes, verification, and targets.

### Agent Guidance Workstreams

- [ ] TXXX [P] [Agents] Produce `agents.md` from approved domain and workflow constraints.
- [ ] TXXX [P] [Rules] Produce the editor/AI rules artifact without conflicting instructions.

### Rationale Workstream

- [ ] TXXX [README] Produce `README.md` with target rationale and mapped industry practices.

**Checkpoint**: All required graded files exist, trace to approved requirements, and contain no code.

## Phase 3: Independent Domain and Quality Review

**Purpose**: Separate authorship from validation for material artifacts.

- [ ] TXXX [P] [Security] Review sensitive-data, authorization, abuse, and logging boundaries.
- [ ] TXXX [P] [Compliance] Review auditability, retention assumptions, and ops/compliance behavior.
- [ ] TXXX [P] [QA] Review edge-case coverage and objective verification.
- [ ] TXXX [P] [Performance] Review measurable assumed targets and rationale.
- [ ] TXXX [Traceability] Verify every objective and requirement has task and verification coverage.

**Checkpoint**: Findings are recorded with severity, owner, affected IDs, and resolution status.

## Phase 4: Reconciliation and Spec Kit Analysis

- [ ] TXXX Resolve review findings in the canonical artifacts and propagate material changes.
- [ ] TXXX Re-run relevant checklists and Constitution Check.
- [ ] TXXX Run cross-artifact consistency analysis and resolve critical/high findings.
- [ ] TXXX Verify task assignments use the least expensive reliable model tier.

**Checkpoint**: No unresolved critical/high inconsistency, coverage gap, or constitutional violation.

## Phase 5: Final Package Gate

- [ ] TXXX Assemble the approval summary: scope, evidence, resolved findings, remaining risks, and
  exact artifacts/versions.
- [ ] TXXX Obtain explicit Gate 3 approval and record the decision.
- [ ] TXXX Stop the workflow; do not run `speckit-implement` for Homework 3.

## Dependencies and Parallel Execution

- Phase 1 blocks all artifact drafting.
- Phase 2 workstreams may run in parallel only after shared terminology and scope are approved.
- Phase 3 reviewers may run in parallel because they produce separate finding reports.
- Phase 4 starts after all material reviews complete and owns cross-file reconciliation.
- Phase 5 starts only after analysis passes.

## Task List Validation

- [ ] Every task uses the required format and has one primary owner.
- [ ] Every task references exact objective/requirement/concern IDs.
- [ ] Advanced tier is reserved for ambiguity, high-risk judgment, or gate synthesis.
- [ ] Material author and reviewer roles are independent.
- [ ] Parallel markers are justified by non-overlapping outputs and resolved shared decisions.
- [ ] Acceptance criteria are objective and checkable.
- [ ] No task executes implementation code for Homework 3.
