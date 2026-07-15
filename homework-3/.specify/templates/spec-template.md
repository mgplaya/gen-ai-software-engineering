# Feature Specification: [FEATURE NAME]

**Feature Branch**: `[###-feature-name]`  
**Created**: [DATE]  
**Status**: Draft  
**Input**: User description: "$ARGUMENTS"

## High-Level Objective

- **Outcome**: [One crisp user/business outcome]
- **Scope boundary**: [One sentence stating what is and is not covered]

## Stakeholders and Access Boundaries

| Stakeholder | Goal | Allowed actions/data | Prohibited actions/data |
|-------------|------|----------------------|-------------------------|
| [Role] | [Goal] | [Authorized scope] | [Boundary] |

## Mid-Level Objectives

| ID | Observable objective | Success evidence | Priority |
|----|----------------------|------------------|----------|
| OBJ-001 | [Testable what, not implementation how] | [Observable evidence] | P1 |

## User Scenarios and Acceptance *(mandatory)*

### User Story 1 - [Brief title] (Priority: P1)

[Describe the journey in plain language.]

**Supports**: [OBJ/requirement IDs]  
**Why this priority**: [Value and risk rationale]  
**Independent test**: [How to validate this story in isolation]

**Acceptance scenarios**:

1. **Given** [initial state], **When** [action], **Then** [user-visible result and audit/ops result].

[Add independently testable stories as needed.]

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST [specific capability].

### Policy and Non-Functional Requirements

| ID | Area | Requirement/target | Measurement or evidence | Assumption rationale |
|----|------|--------------------|-------------------------|----------------------|
| NFR-001 | Security | [MUST requirement] | [How verified] | [N/A or rationale] |
| NFR-002 | Privacy | [MUST requirement] | [How verified] | [N/A or rationale] |
| NFR-003 | Audit | [MUST requirement] | [How verified] | [N/A or rationale] |
| NFR-004 | Reliability | [Measurable target] | [How measured] | [Why reasonable] |
| NFR-005 | Performance | [p95/p99, throughput, or time target] | [How measured] | [Label assumed] |
| NFR-006 | Consistency | [Read-after-write or reconciliation target] | [How measured] | [Why reasonable] |

### Key Entities and Sensitive-Data Classification

| Entity | Purpose | Key attributes (conceptual) | Classification | Retention/access notes |
|--------|---------|-----------------------------|----------------|------------------------|
| [Entity] | [Purpose] | [No implementation schema] | [Public/Internal/Confidential/Restricted] | [Policy] |

## Edge Cases and Failure Modes *(mandatory)*

| ID | Condition/failure | Expected user-visible behavior | Audit/ops/compliance outcome | Related requirements |
|----|-------------------|--------------------------------|------------------------------|----------------------|
| EC-001 | [Scoped condition] | [Deterministic result] | [Event/escalation/no sensitive data] | [IDs] |

The table MUST cover applicable empty states, invalid boundaries, stale data, partial dependency
failure, retries, duplicate and concurrent requests, permission violations, suspicious patterns,
and recovery/reconciliation behavior.

## Implementation Notes and Guardrails

Describe hypothetical implementation constraints without producing code:

- sensitive-data and logging boundaries;
- authorization and least-privilege rules;
- money, currency, time, and identifier conventions;
- idempotency, concurrency, and retry semantics;
- error taxonomy and user-safe messages;
- audit event requirements and immutability expectations;
- pagination, rate limits, consistency, and performance guardrails;
- prohibited shortcuts and explicit non-goals.

## Context

### Beginning Context

- [Files, services, policies, data stores, and known state assumed to exist before work.]

### Ending Context

- [Documents and hypothetical system state expected after all tasks are complete.]

## Verification Strategy

| Objective/requirement | Verification category | Fixture/evidence | Pass condition | Reviewer role |
|-----------------------|-----------------------|------------------|----------------|---------------|
| [ID] | [Review/unit/integration/e2e/reconciliation/performance/compliance] | [Synthetic input/report] | [Objective check] | [Independent role] |

## Low-Level Task Requirements

The final low-level tasks MUST be substantial, independently checkable implementation slices even
though this homework does not implement them. Each task MUST trace to objective/requirement IDs and
declare agent role, model tier, rationale, inputs, output, dependencies, parallel-safety, and
acceptance criteria. The detailed task list is generated after the plan is approved and is then
incorporated or referenced here without creating a competing source of truth.

## Success Criteria *(mandatory)*

- **SC-001**: [Technology-agnostic, measurable user/business outcome].

## Assumptions, Dependencies, and Out of Scope

### Assumptions

- **A-001**: [Explicit assumption, including whether a target is hypothetical].

### Dependencies

- **DEP-001**: [External policy, service, data, or reviewer dependency].

### Out of Scope

- Actual source code, APIs, UI, executable prototypes, scaffolding, migrations, and dependency
  installation for Homework 3.

## Traceability Summary

| Objective | Requirements | Stories/edge cases | Success criteria | Verification | Tasks |
|-----------|--------------|--------------------|------------------|--------------|-------|
| OBJ-001 | [IDs] | [IDs] | [IDs] | [IDs] | [IDs after task generation] |

## Open Questions

- [Question that materially affects scope, safety, verification, or targets; remove or resolve before Gate 1.]
