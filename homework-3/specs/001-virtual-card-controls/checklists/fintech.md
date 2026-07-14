# FinTech Requirement Quality Checklist: Regulated Virtual Card Controls

**Purpose**: Formal pre-Gate-1 review of whether the specification completely, clearly, and
consistently defines FinTech safety, compliance, audit, recovery, and measurable quality requirements
**Created**: 2026-07-15
**Feature**: [spec.md](../spec.md)
**Audience/timing**: Independent FinTech/security/compliance reviewers before specification approval
**Depth**: Formal approval gate
**Model routing**: Economy for mechanical ID/redaction scans; Standard for traceability and scenario
coverage; Advanced only for security, payment-domain, compliance, and gate findings

> This checklist validates the written requirements, not an implementation. Items ask whether the
> specification is implementable and verifiable without hidden decisions.

## Requirement Completeness

- [x] CHK001 Are all allowed and prohibited actions defined for cardholder, operations, compliance,
  and risk-service actors? [Completeness, Spec §Stakeholders and Access Boundaries]
- [x] CHK002 Are lifecycle states, independently sourced restriction flags, effective-status
  precedence, and actor-owned transitions explicitly named? [Completeness, Spec §FR-001–FR-011]
- [x] CHK003 Are requirements present for command acceptance, effective local state, external
  propagation, and user-visible pending state as distinct concepts? [Completeness, Spec §FR-002–FR-006]
- [x] CHK004 Are per-transaction, daily, and monthly limit constraints complete for valid, invalid,
  frozen-card, stale-policy, and concurrent-change conditions? [Completeness, Spec §FR-012–FR-021]
- [x] CHK005 Are transaction requirements complete for all specified statuses, multi-currency amounts,
  stable ordering, paging, empty/stale/unavailable states, and post-freeze settlement? [Completeness,
  Spec §FR-022–FR-030]
- [x] CHK006 Are privileged search, read, emergency freeze, export, denial, and access-expiry
  requirements all bounded by role, case, and business purpose? [Completeness, Spec §FR-031–FR-037]
- [x] CHK007 Are audit requirements documented for successful, denied, duplicate, conflicting,
  corrective, privileged-read, export, and delayed-sink outcomes? [Completeness, Spec §FR-005,
  §FR-021, §FR-037–FR-041]

## Requirement Clarity

- [x] CHK008 Is the distinction between lifecycle, restriction flags, and derived effective statuses
  unambiguous for every composite transition? [Clarity, Spec §FR-002–FR-011]
- [x] CHK009 Is "blocks new authorizations" clearly separated from treatment of transactions already
  authorized before freeze? [Clarity, Spec §FR-003, §FR-030, §EC-022]
- [x] CHK010 Is mandatory step-up verification for every cardholder unfreeze stated without a
  conflicting risk-optional path? [Clarity, Spec §FR-009, §A-004]
- [x] CHK011 Is the boundary between allowed decreases and prohibited increases on a frozen card
  objectively decidable for mixed limit sets? [Clarity, Spec §FR-015–FR-017, §EC-021]
- [x] CHK012 Are exact-money, currency-scale, event-time, timezone, and ordering terms defined well
  enough to avoid incompatible interpretations? [Clarity, Spec §FR-013, §FR-024–FR-027, §NFR-014]
- [x] CHK013 Are final, pending, denied, stale, unavailable, and conflict outcomes distinguishable by
  explicit written criteria rather than subjective wording? [Clarity, Spec §FR-011, §FR-029,
  §NFR-013]

## Requirement Consistency

- [x] CHK014 Do stakeholder prohibitions, unfreeze requirements, `FR-034`, `EC-004`, and Out of Scope
  consistently keep operations/risk release in a separate workflow? [Consistency, Spec
  §Stakeholders, §FR-008, §FR-034, §EC-004, §Out of Scope]
- [x] CHK015 Do freeze acceptance scenarios, propagation requirements, performance targets, and
  recovery targets describe one compatible state timeline? [Consistency, Spec §US1, §FR-003–FR-006,
  §NFR-004, §NFR-011]
- [x] CHK016 Do limit acceptance scenarios, atomicity, versioning, idempotency, and concurrency
  requirements produce one deterministic conflict policy? [Consistency, Spec §US3, §FR-015–FR-020]
- [x] CHK017 Are transaction status evolution and immutable history requirements consistent with audit
  correction and reconciliation rules? [Consistency, Spec §FR-023, §FR-030, §FR-038, §EC-020–EC-022]
- [x] CHK018 Do the jurisdiction-neutral clarification, assumptions, retention target, dependencies,
  and exclusions avoid claiming named-jurisdiction compliance? [Consistency, Spec §Clarifications,
  §NFR-012, §A-008, §DEP-006, §Out of Scope]

## Acceptance Criteria Quality

- [x] CHK019 Can each mid-level objective be objectively evaluated from its stated success evidence,
  scenarios, success criteria, and verification evidence? [Measurability, Spec §Mid-Level Objectives,
  §Verification Strategy, §Success Criteria]
- [x] CHK020 Are all percentile, availability, concurrency, volume, retention, idempotency, and recovery
  targets explicitly measurable and labeled as assumed where evidence is absent? [Measurability,
  Spec §NFR-003–NFR-012]
- [x] CHK021 Does each critical state-changing acceptance scenario state the initial state, actor/action,
  effective state, truthful user outcome, and audit implication? [Acceptance Criteria, Spec §US1–US3]
- [x] CHK022 Are privileged-access acceptance scenarios measurable for both explicitly allowed and
  denied role/case/purpose combinations? [Acceptance Criteria, Spec §US5, §NFR-001, §SC-005]
- [x] CHK023 Can audit completeness and prohibited-data absence be evaluated without relying on vague
  claims such as "secure" or "compliant"? [Measurability, Spec §NFR-002–NFR-003, §SC-006]

## Scenario and Edge-Case Coverage

- [x] CHK024 Are primary, alternate, exception, recovery, and non-functional scenarios documented for
  every state-changing user story? [Coverage, Spec §US1–US3, §EC-002–EC-010, §EC-021–EC-022]
- [x] CHK025 Are empty, stale, unavailable, concurrent-arrival, same-time, DST, status-evolution, and
  access-loss cases documented for transaction history? [Coverage, Spec §EC-001, §EC-011–EC-015,
  §EC-022]
- [x] CHK026 Are duplicate delivery, distinct concurrent commands, stale versions, policy changes, and
  mixed limit changes each given a non-overlapping expected outcome? [Coverage, Spec §EC-002–EC-003,
  §EC-007–EC-010, §EC-021]
- [x] CHK027 Are internal wrong-role, expired-role, closed-case, missing-reason, suspicious-bulk, and
  unauthorized-export scenarios addressed without target-data leakage? [Coverage, Spec §EC-016–EC-018]
- [x] CHK028 Are delayed audit, reconciliation mismatch, corrective event, and external propagation
  recovery requirements documented with owners or escalation timing? [Recovery Coverage, Spec
  §EC-005, §EC-019–EC-020, §NFR-011]

## Security, Privacy, and Compliance Quality

- [x] CHK029 Are authentication, fresh ownership/authorization, least privilege, separation of duties,
  step-up, and fail-closed requirements defined for every sensitive action? [Security Coverage, Spec
  §Stakeholders, §FR-001, §FR-007–FR-010, §FR-017, §FR-031–FR-037]
- [x] CHK030 Is the prohibited-data list consistent across user views, logs, audit, exports, fixtures,
  and dependency failures? [Privacy Consistency, Spec §FR-025, §FR-040, §NFR-002,
  §Implementation Notes]
- [x] CHK031 Are data minimization, classification, access, retention, and case-purpose boundaries
  documented for every key entity? [Privacy Completeness, Spec §Key Entities and Sensitive-Data
  Classification]
- [x] CHK032 Are audit immutability, tamper evidence, correction, attribution, correlation, and
  reconciliation requirements sufficiently explicit for an independent compliance review?
  [Compliance Clarity, Spec §FR-038–FR-041]
- [x] CHK033 Does the specification distinguish assumed internal policy from legal/regulatory mandates
  requiring later jurisdiction-specific approval? [Compliance Boundary, Spec §NFR-012, §A-008,
  §DEP-006]

## Dependencies, Assumptions, and Traceability

- [x] CHK034 Are ownership, processor propagation, risk policy, transaction history, internal identity,
  case management, audit, monitoring, and legal-policy dependencies explicitly identified?
  [Dependency Completeness, Spec §Dependencies]
- [x] CHK035 Does each assumed service target include enough rationale to be challenged or replaced
  during planning without changing hidden product behavior? [Assumption Quality, Spec §Policy and
  Non-Functional Requirements]
- [x] CHK036 Does every objective map to functional/non-functional requirements, stories/edge cases,
  success criteria, verification, and a reserved future task mapping? [Traceability, Spec
  §Traceability Summary]
- [x] CHK037 Are implementation guardrails clearly separated from premature framework, vendor, schema,
  API-shape, and UI decisions? [Scope Consistency, Spec §Implementation Notes and Guardrails]
- [x] CHK038 Are future task requirements explicit about requirement IDs, role/tier routing,
  dependencies, parallel safety, acceptance criteria, and independent review? [Task Readiness, Spec
  §Low-Level Task Requirements]

## Findings

| Finding ID | Checklist item | Severity | Affected requirement IDs | Resolution/owner | Status |
|------------|----------------|----------|--------------------------|------------------|--------|
| FTR-001 | CHK002, CHK008 | High | FR-002–FR-008, A-002 | Added separate lifecycle/restriction flags, precedence, source-owned transitions, and narrowed prohibition row | Resolved—independently verified 2026-07-15 |
| FTR-002 | CHK015, CHK021, CHK024 | High | FR-003–FR-006, FR-033, NFR-004, NFR-011 | Added hard durable-local-block invariant and user/operations propagation/recovery scenarios | Resolved—independently verified 2026-07-15 |
| FTR-003 | CHK004 | High | FR-012–FR-017, NFR-014 | Defined billing periods/timezone, consumption, reversals/refunds, rate timing, posting adjustment, and reset fixtures | Resolved—independently verified 2026-07-15 |
| FTR-004 | CHK001, CHK006, CHK022, CHK027 | High | FR-031–FR-037 | Added role/case/purpose/action matrix, compliance-only export, deterministic abuse controls, and authoritative emergency-freeze reason codes/policy version | Resolved—independently verified 2026-07-15 |
| FTR-005 | CHK016 | High | FR-018–FR-020, NFR-008–NFR-009 | Added bound command identity, expected-version winner, conflict, and mismatch rules | Resolved—independently verified 2026-07-15 |
| FTR-006 | CHK013 | Medium | FR-011, FR-029, NFR-013 | Added normative command results plus objective 60-second stale and 15-minute unavailable read criteria | Resolved—independently verified 2026-07-15 |
| FTR-007 | CHK012 | Medium | FR-023–FR-030, NFR-014 | Defined transaction identity, occurrence/status/as-of times, sort key, and linked refund semantics | Resolved—independently verified 2026-07-15 |
| FTR-008 | CHK028 | Medium | FR-038–FR-041, NFR-003, NFR-011 | Defined durable intent, duplicate-safe replay, owners, 5-minute recovery, 15-minute incident, and degraded-safe mode | Resolved—independently verified 2026-07-15 |
| FTR-009 | CHK030 | High | FR-025, FR-036, FR-040, NFR-002 | Added canonical surface data taxonomy and one zero-occurrence oracle | Resolved—independently verified 2026-07-15 |
| FTR-010 | CHK031 | Medium | Key Entities, NFR-012 | Added entity-role-purpose access and retention/disposition owner matrix | Resolved—independently verified 2026-07-15 |
| FTR-011 | CHK020 | Medium | NFR-001, NFR-003–NFR-011 | Added measurement rules and strict availability numerator/denominator excluding fail-closed unavailable outcomes from success | Resolved—independently verified 2026-07-15 |
| FTR-012 | CHK036 | Medium | Traceability Summary | Mapped NFR-001/NFR-002 and EC-021–EC-026 to relevant objectives/verification | Resolved—independently verified 2026-07-15 |

## Independent Review Verdict

- Initial review: 0 Critical, 6 High, and 6 Medium findings.
- First remediation review: 8 findings resolved; 1 High and 3 Medium residuals remained.
- Final targeted review: all 12 findings resolved; no new Critical or High contradiction introduced.
- Gate recommendation: ready for formal Gate 1 specification approval.
- Review independence: dedicated FinTech/security/compliance reviewer performed read-only review; the
  primary author applied changes and the reviewer verified remediation.

## Completion Rules

- Mark an item `[x]` only when the cited requirement text provides objective evidence.
- Record missing, ambiguous, inconsistent, or unmeasurable content as a finding; do not silently infer.
- Critical/high findings block Gate 1. Medium findings require resolution or explicit user disposition.
- Material fixes must update the spec, requirements checklist, and affected traceability before review
  is repeated.
