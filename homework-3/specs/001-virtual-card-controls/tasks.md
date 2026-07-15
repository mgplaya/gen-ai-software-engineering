---
description: "Agent-routed documentation tasks for regulated virtual card controls"
---

# Tasks: Regulated Virtual Card Controls

**Input**: Gate-1-approved `spec.md`; Gate-2-approved `plan.md`; `research.md`, `data-model.md`,
`contracts/`, `quickstart.md`, and completed checklists in this feature directory
**Scope**: Complete and validate the Homework 3 documentation package only. The implementation
slices described by these tasks are hypothetical; no source code, executable API/UI, schema,
migration, dependency, or `speckit-implement` run is authorized.
**Approved baselines**: `spec.md` SHA-256
`7cdd28c597f5c0ed440337eefc4a5b229b5eff9f909fa56a6582b5ef4a2a9ed9`; `plan.md` SHA-256
`c92fc44bd86c12d065857c001f99e0215541c94b4b9136fd47ab3fcb8ff73d00`
**Task rule**: `[P]` means the task writes a non-overlapping file and has no unresolved dependency.
All Advanced reviews must be performed by an agent independent from the relevant author.

## Concrete Agent Assignment

Agent IDs below are stable primary owners for this task plan. The runtime may choose the least-cost
available model within the declared tier; it MUST NOT silently promote every task to the strongest
and most expensive model.

| Agent ID | Task-plan role | Tier | Recommended Codex profile | Primary task IDs | Responsibility |
|----------|----------------|------|---------------------------|------------------|----------------|
| `AG-E01` | `codex-docs-ops` | Economy | `gpt-5.6-luna`, Low/Light | T001, T002, T034, T039, T040 | Hashes, trace extraction, mechanical validation, approval/status recording |
| `AG-S01` | `codex-spec-author` | Standard | `gpt-5.6-terra`, Medium | T003–T005, T008, T011–T012, T014, T018, T027–T030 | Publication procedure, specification slices, canonical docs, ChatGPT/Codex rules, README |
| `AG-S02` | `codex-architecture-reliability` | Standard | `gpt-5.6-terra`, Medium | T006, T009, T019–T020 | Future boundaries, propagation, pagination, freshness |
| `AG-S03` | `codex-qa-author` | Standard | `gpt-5.6-terra`, Medium | T007, T010, T013, T017, T021, T026 | Fixtures and story-specific verification design |
| `AG-A01` | `codex-fintech-author` | Advanced | `gpt-5.6-sol`, High | T015–T016, T023 | Spending-risk policy, payment accounting, operations freeze risk |
| `AG-A02` | `codex-security-compliance-author` | Advanced | `gpt-5.6-sol`, High | T022, T024–T025 | Internal authorization, compliance export, audit/evidence semantics |
| `AG-A03` | `codex-release-orchestrator` | Advanced | `gpt-5.6-sol`, High | T035–T036, T038 | Cross-file remediation, Spec Kit analysis, exact gate synthesis |
| `AG-A04` | `codex-fintech-reviewer` | Advanced | `gpt-5.6-sol`, High | T031 | Independent FinTech/payments adversarial review |
| `AG-A05` | `codex-security-compliance-reviewer` | Advanced | `gpt-5.6-sol`, High | T032 | Independent security/compliance/privacy review |
| `AG-S04` | `codex-qa-release-reviewer` | Standard | `gpt-5.6-terra`, Medium | T033, T037 | Independent QA/performance review and final semantic validation |

No primary task has more than one owner. `AG-A04`, `AG-A05`, and `AG-S04` are review-only roles and
must not author the material they validate. Reviewer fields inside individual tasks remain the
required secondary validation roles. The IDs and role names are routing identities, not model names
or claims about observed runtime execution. A runner should record the actual selected model when
that evidence is available; otherwise the profile column remains a cost-aware recommendation.

## Phase 1: Approved Inputs and Traceability Foundation

**Purpose**: Lock provenance and establish the coverage structure before graded artifacts are edited.

- [x] T001 Validate and record the approved baselines in `homework-3/specs/001-virtual-card-controls/reviews/baseline-validation.md`
  - Traces to: OBJ-001–OBJ-006; FR-001–FR-041; NFR-001–NFR-014; EC-001–EC-026; SC-001–SC-008
  - Agent: Documentation provenance checker
  - Model tier: Economy
  - Tier rationale: Hash, path, approval-log, and file-presence checks are mechanical.
  - Inputs: `.specify/memory/approvals.md`, `spec.md`, `plan.md`, `AGENTS.md`
  - Output: `homework-3/specs/001-virtual-card-controls/reviews/baseline-validation.md`
  - Dependencies: None
  - Parallel-safe: No — this establishes the baseline consumed by all remaining tasks.
  - Acceptance criteria: Both hashes match the approval log; Gate 1 and Gate 2 scopes are stated; no implementation authorization is inferred.
  - Reviewer: Documentation QA / Economy

- [x] T002 Extract the full objective-to-requirement-to-scenario-to-success mapping into `homework-3/specs/001-virtual-card-controls/reviews/traceability-matrix.md`
  - Traces to: OBJ-001–OBJ-006, FR-001–FR-041, NFR-001–NFR-014, EC-001–EC-026, SC-001–SC-008
  - Agent: Traceability analyst
  - Model tier: Economy
  - Tier rationale: Identifier extraction and matrix population are bounded transformations.
  - Inputs: Approved `spec.md`, `data-model.md`, `contracts/`, `quickstart.md`
  - Output: `homework-3/specs/001-virtual-card-controls/reviews/traceability-matrix.md`
  - Dependencies: T001
  - Parallel-safe: No — downstream story and review tasks use this shared mapping.
  - Acceptance criteria: Every approved ID appears at least once; every mapping names a scenario, verification oracle, and planned task; no orphan or invented ID exists.
  - Reviewer: QA/requirements reviewer / Standard

- [x] T003 Define the canonical publication and parity procedure in `homework-3/specs/001-virtual-card-controls/reviews/publication-procedure.md`
  - Traces to: SC-008; R-008
  - Agent: Documentation release coordinator
  - Model tier: Standard
  - Tier rationale: The procedure must distinguish semantic equivalence from task synchronization without changing approved behavior.
  - Inputs: Approved `spec.md`, approved `plan.md` R-008, `TASKS.md`, this `tasks.md`
  - Output: `homework-3/specs/001-virtual-card-controls/reviews/publication-procedure.md`
  - Dependencies: T001, T002
  - Parallel-safe: No — it governs all canonical publication work.
  - Acceptance criteria: Procedure preserves the approved product body byte-for-byte or documents a semantic-equivalence method; task parity is checked separately; material drift reopens the appropriate gate.
  - Reviewer: Independent specification-governance reviewer / Advanced

**Checkpoint**: Exact approved inputs are reproducible and every approved identifier has a planned verification path.

## Phase 2: Foundational Documentation Controls

**Purpose**: Prepare shared vocabulary, beginning/ending context, and future implementation boundaries
used by all user-story slices.

- [x] T004 [P] Reconcile the shared state, result, money, time, and data-taxonomy glossary in `homework-3/specs/001-virtual-card-controls/reviews/glossary.md`
  - Traces to: FR-003–FR-004, FR-013–FR-020, FR-023–FR-030, FR-038–FR-041, NFR-002, NFR-014
  - Agent: Domain terminology editor
  - Model tier: Standard
  - Tier rationale: Reconciliation requires bounded semantic judgment across approved artifacts.
  - Inputs: Approved `spec.md`, `data-model.md`, all contracts
  - Output: `homework-3/specs/001-virtual-card-controls/reviews/glossary.md`
  - Dependencies: T002, T003
  - Parallel-safe: Yes — it writes a dedicated file and shares only approved inputs with T005–T007.
  - Acceptance criteria: One approved term exists for every state, result, time, money, actor, and evidence concept; conflicts are listed rather than silently normalized.
  - Reviewer: Payments/domain reviewer / Advanced

- [x] T005 [P] Specify the hypothetical beginning and ending workspace contexts in `homework-3/specs/001-virtual-card-controls/reviews/context-boundaries.md`
  - Traces to: OBJ-001–OBJ-006, A-001–A-008, DEP-001–DEP-006, SC-008
  - Agent: Delivery-context writer
  - Model tier: Standard
  - Tier rationale: The task is a constrained synthesis of already approved scope and dependencies.
  - Inputs: `spec.md` Context and Assumptions, approved `plan.md`, `TASKS.md`
  - Output: `homework-3/specs/001-virtual-card-controls/reviews/context-boundaries.md`
  - Dependencies: T002, T003
  - Parallel-safe: Yes — dedicated output and no decision shared with T004, T006, or T007.
  - Acceptance criteria: Beginning context names existing hypothetical capabilities; ending context names all four graded files and Spec Kit evidence; no implementation artifact is claimed to exist.
  - Reviewer: Requirements reviewer / Standard

- [x] T006 [P] Map future module and integration ownership without defining executable interfaces in `homework-3/specs/001-virtual-card-controls/reviews/future-boundaries.md`
  - Traces to: OBJ-001–OBJ-006, FR-001–FR-041, DEP-001–DEP-006; R-001–R-007
  - Agent: Architecture documentation analyst
  - Model tier: Standard
  - Tier rationale: Approved architecture decisions make this a bounded responsibility-mapping task.
  - Inputs: Approved `plan.md`, `research.md`, `data-model.md`, contracts
  - Output: `homework-3/specs/001-virtual-card-controls/reviews/future-boundaries.md`
  - Dependencies: T002, T003
  - Parallel-safe: Yes — dedicated output and approved architecture is fixed.
  - Acceptance criteria: Every future boundary has one responsibility, inbound/outbound dependency, safe failure posture, and owning requirement IDs; no endpoint, schema, class, or vendor is selected.
  - Reviewer: Independent architecture/risk reviewer / Advanced

- [x] T007 [P] Define the future synthetic fixture and evidence catalog in `homework-3/specs/001-virtual-card-controls/reviews/fixture-catalog.md`
  - Traces to: EC-001–EC-026, SC-001–SC-007, NFR-001–NFR-014
  - Agent: Verification designer
  - Model tier: Standard
  - Tier rationale: Scenario derivation is substantial but tightly constrained by approved oracles.
  - Inputs: Approved `spec.md`, contracts, `quickstart.md`
  - Output: `homework-3/specs/001-virtual-card-controls/reviews/fixture-catalog.md`
  - Dependencies: T002, T003
  - Parallel-safe: Yes — fixture documentation has a distinct output.
  - Acceptance criteria: Catalog covers composite states, exact money, DST/periods, 20-way concurrency, 100,000 transactions, role/case matrices, propagation, evidence recovery, and prohibited-data scans using synthetic masked data only.
  - Reviewer: Independent QA reviewer / Standard

**Checkpoint**: Shared terminology, context, responsibility boundaries, and fixtures are explicit and
introduce no new product behavior.

## Phase 3: User Story 1 — Immediately Freeze a Card (P1)

**Story goal**: Document a future slice that safely freezes an owned open card and truthfully reports
final or pending propagation.
**Independent test**: An owned active-card fixture demonstrates durable local blocking, idempotent
retries, pending propagation recovery, prior-authorization behavior, and one attributable outcome.

- [x] T008 [US1] Specify the future cardholder-freeze command slice in `homework-3/specs/001-virtual-card-controls/task-slices/us1-freeze.md`
  - Traces to: OBJ-001, OBJ-005, OBJ-006; FR-001–FR-006; EC-001–EC-005, EC-015, EC-022, EC-024; SC-001, SC-006–SC-007
  - Agent: Control-domain specification writer
  - Model tier: Standard
  - Tier rationale: The command behavior is fully approved but requires precise decomposition.
  - Inputs: `contracts/control-commands.md`, `data-model.md`, T004, T006
  - Output: `homework-3/specs/001-virtual-card-controls/task-slices/us1-freeze.md` — `Freeze command` subsection
  - Dependencies: T004, T006
  - Parallel-safe: No — it edits the canonical specification and precedes US1 verification text.
  - Acceptance criteria: Slice binds ownership, confirmation, expected version, restriction, local block, audit intent, propagation intent, and result atomically; repeated satisfied freeze is a non-mutating attributable no-op.
  - Reviewer: Payments/risk reviewer / Advanced

- [x] T009 [US1] Specify freeze propagation, retry, reconciliation, and escalation in `homework-3/specs/001-virtual-card-controls/task-slices/us1-freeze.md`
  - Traces to: FR-003, FR-006, FR-041; NFR-004, NFR-008, NFR-011; EC-002, EC-005, EC-019; SC-001, SC-006–SC-007
  - Agent: Reliability specification writer
  - Model tier: Standard
  - Tier rationale: Timelines and failure categories are approved and need careful but bounded mapping.
  - Inputs: `contracts/control-commands.md`, `contracts/internal-access-audit.md`, `research.md` R-003
  - Output: `homework-3/specs/001-virtual-card-controls/task-slices/us1-freeze.md` — `Propagation and recovery` subsection
  - Dependencies: T008
  - Parallel-safe: No — same canonical file and semantic dependency on the command boundary.
  - Acceptance criteria: Only locally safe freeze may be pending; retry is duplicate-safe; alert at 60 seconds and escalation at 15 minutes are assigned; local restriction never weakens.
  - Reviewer: Independent reliability reviewer / Standard

- [x] T010 [US1] Define future freeze scenario and invariant checks in `homework-3/specs/001-virtual-card-controls/task-slices/us1-freeze.md`
  - Traces to: FR-001–FR-006, NFR-003–NFR-004, NFR-006–NFR-009, NFR-011, NFR-013; EC-001–EC-005, EC-015, EC-022, EC-024; SC-001, SC-006–SC-007
  - Agent: QA scenario designer
  - Model tier: Standard
  - Tier rationale: The verification matrix is derived from explicit contracts and measurable targets.
  - Inputs: T007–T009, `quickstart.md`
  - Output: `homework-3/specs/001-virtual-card-controls/task-slices/us1-freeze.md` — `Verification` subsection
  - Dependencies: T009
  - Parallel-safe: No — it verifies the completed US1 documentation.
  - Acceptance criteria: Checks cover ownership loss, duplicate/mismatched identity, concurrent version, local-boundary failure, delayed propagation, prior-authorized settlement, message clarity, latency, and audit reconciliation.
  - Reviewer: Independent FinTech QA reviewer / Advanced

**Checkpoint**: US1 is independently implementable and verifiable without unfreeze, limits, history,
or internal oversight.

## Phase 4: User Story 2 — Safely Unfreeze a User-Frozen Card (P1)

**Story goal**: Document fail-closed removal of only the cardholder-owned restriction after mandatory
step-up.
**Independent test**: Composite-state fixtures prove that only `USER_FREEZE` can be removed and no
ambiguous dependency result is shown as success or pending.

- [x] T011 [US2] Specify the future unfreeze authorization and composite-state slice in `homework-3/specs/001-virtual-card-controls/task-slices/us2-unfreeze.md`
  - Traces to: OBJ-001, OBJ-005, OBJ-006; FR-007–FR-011; EC-004, EC-006, EC-010, EC-015, EC-023; SC-002, SC-006–SC-007
  - Agent: Control-domain specification writer
  - Model tier: Standard
  - Tier rationale: Approved state rules make the draft bounded; precision is still required.
  - Inputs: `contracts/control-commands.md`, `data-model.md`, T004, T006
  - Output: `homework-3/specs/001-virtual-card-controls/task-slices/us2-unfreeze.md` — `Unfreeze command` subsection
  - Dependencies: T010
  - Parallel-safe: No — canonical publication is sequential to avoid overlapping edits.
  - Acceptance criteria: Fresh ownership, open lifecycle, user flag, current step-up, and expected version are explicit; only `USER_FREEZE` is removed; stronger/unknown restrictions remain effective.
  - Reviewer: Payments/risk reviewer / Advanced

- [x] T012 [US2] Specify unfreeze fail-closed results and safe messaging in `homework-3/specs/001-virtual-card-controls/task-slices/us2-unfreeze.md`
  - Traces to: FR-008–FR-011, FR-040; NFR-005–NFR-007, NFR-013; EC-004, EC-006, EC-010, EC-023; SC-002, SC-007
  - Agent: Security/content specification writer
  - Model tier: Standard
  - Tier rationale: Result categories and disclosure limits are already normative.
  - Inputs: Approved `spec.md`, `contracts/control-commands.md`, T011
  - Output: `homework-3/specs/001-virtual-card-controls/task-slices/us2-unfreeze.md` — `Failure and messaging` subsection
  - Dependencies: T011
  - Parallel-safe: No — same canonical file and depends on the unfreeze preconditions.
  - Acceptance criteria: Ambiguity yields terminal `TEMPORARILY_UNAVAILABLE` with no mutation; operations/risk/lifecycle details are not leaked; final, denied, and unavailable states are non-color distinguishable.
  - Reviewer: Independent security/privacy reviewer / Advanced

- [x] T013 [US2] Define future unfreeze composite-state and dependency checks in `homework-3/specs/001-virtual-card-controls/task-slices/us2-unfreeze.md`
  - Traces to: FR-007–FR-011, NFR-001, NFR-003, NFR-005–NFR-009, NFR-013; EC-002–EC-004, EC-006, EC-010, EC-015, EC-023–EC-024; SC-002, SC-006–SC-007
  - Agent: QA scenario designer
  - Model tier: Standard
  - Tier rationale: This is a bounded test-design task with explicit pass/fail oracles.
  - Inputs: T007, T011–T012, `data-model.md`
  - Output: `homework-3/specs/001-virtual-card-controls/task-slices/us2-unfreeze.md` — `Verification` subsection
  - Dependencies: T012
  - Parallel-safe: No — same canonical file and completes US2.
  - Acceptance criteria: Every lifecycle/restriction combination, expired step-up, stale session, concurrent command, mismatched retry, dependency failure, read-after-write target, and audit outcome has a deterministic oracle.
  - Reviewer: Independent FinTech QA reviewer / Advanced

**Checkpoint**: US2 cannot weaken any non-user restriction and is independently testable.

## Phase 5: User Story 3 — Configure Spending Limits (P1)

**Story goal**: Document atomic, exact, versioned limit changes and deterministic allowance accounting.
**Independent test**: Valid, boundary, frozen-card, concurrency, idempotency, DST, hold/post/reversal,
refund, and FX fixtures reconcile to one exact effective limit/consumption outcome.

- [x] T014 [US3] Specify the future complete limit-set validation and atomic update slice in `homework-3/specs/001-virtual-card-controls/task-slices/us3-limits.md`
  - Traces to: OBJ-002, OBJ-005, OBJ-006; FR-012–FR-021; EC-006–EC-010, EC-021, EC-024; SC-003, SC-006–SC-007
  - Agent: Payment-controls specification writer
  - Model tier: Standard
  - Tier rationale: Exact approved validations can be decomposed without new product decisions.
  - Inputs: `contracts/control-commands.md`, `data-model.md`, T004, T006
  - Output: `homework-3/specs/001-virtual-card-controls/task-slices/us3-limits.md` — `Limit command` subsection
  - Dependencies: T013
  - Parallel-safe: No — canonical file edits are serialized.
  - Acceptance criteria: Complete set, exact scale/currency, policy/order bounds, expected version, atomicity, step-up, and audit content are explicit; no partial update exists.
  - Reviewer: Payments/domain reviewer / Advanced

- [x] T015 [US3] Specify restricted-card decrease and active-card increase policy in `homework-3/specs/001-virtual-card-controls/task-slices/us3-limits.md`
  - Traces to: FR-016–FR-017, FR-021; EC-006, EC-009–EC-010, EC-021; SC-003, SC-007
  - Agent: Risk-policy specification writer
  - Model tier: Advanced
  - Tier rationale: Increase/decrease classification and risk-increasing failure behavior are safety-critical FinTech judgments.
  - Inputs: Approved `spec.md`, `contracts/control-commands.md`, T014
  - Output: `homework-3/specs/001-virtual-card-controls/task-slices/us3-limits.md` — `Risk policy` subsection
  - Dependencies: T014
  - Parallel-safe: No — same canonical file and policy interpretation must follow the base limit contract.
  - Acceptance criteria: Frozen cards accept only a complete non-increasing set with at least one decrease; any component increase rejects the entire set; ambiguous increases fail closed; unchanged components are permitted.
  - Reviewer: Independent payments/risk reviewer / Advanced

- [x] T016 [US3] Specify future hold, posting, reversal, refund, FX, and billing-period accounting in `homework-3/specs/001-virtual-card-controls/task-slices/us3-limits.md`
  - Traces to: FR-013–FR-016; NFR-014; EC-009, EC-012–EC-013, EC-025–EC-026; SC-003
  - Agent: Payment-accounting specification writer
  - Model tier: Advanced
  - Tier rationale: Exact allowance semantics, FX adjustment, and DST boundaries carry high financial correctness risk.
  - Inputs: `data-model.md` LimitConsumption, `contracts/control-commands.md` Limit Accounting Contract, T015
  - Output: `homework-3/specs/001-virtual-card-controls/task-slices/us3-limits.md` — `Allowance accounting` subsection
  - Dependencies: T015
  - Parallel-safe: No — same canonical file and relies on the approved limit policy slice.
  - Acceptance criteria: Holds consume once, posting replaces holds, reversals release matching holds, refunds do not replenish historical allowance, FX posting does not reverse authorization, and billing periods reset exactly once.
  - Reviewer: Independent payment-accounting reviewer / Advanced

- [x] T017 [US3] Define future exact-money, policy, concurrency, and accounting checks in `homework-3/specs/001-virtual-card-controls/task-slices/us3-limits.md`
  - Traces to: FR-012–FR-021; NFR-003, NFR-005–NFR-009, NFR-014; EC-002–EC-003, EC-006–EC-010, EC-012–EC-013, EC-021, EC-024–EC-026; SC-003, SC-006–SC-007
  - Agent: Payment QA scenario designer
  - Model tier: Standard
  - Tier rationale: Test derivation is bounded by explicit financial oracles; high-risk review is separate.
  - Inputs: T007, T014–T016
  - Output: `homework-3/specs/001-virtual-card-controls/task-slices/us3-limits.md` — `Verification` subsection
  - Dependencies: T016
  - Parallel-safe: No — it verifies the completed US3 slice.
  - Acceptance criteria: Fixtures include currency scale, policy edges, mixed increase/decrease, expired step-up, duplicate/mismatch, 20 same-version commands, DST/month boundary, incremental holds, partial reversals, refunds, and FX deltas with exact reconciliation.
  - Reviewer: Independent payments/risk reviewer / Advanced

**Checkpoint**: US3 is independently implementable with exact and deterministic financial behavior.

## Phase 6: User Story 4 — Review Card Transactions (P1)

**Story goal**: Document an ownership-scoped, privacy-safe, stably paginated transaction history.
**Independent test**: A 100,000-item synthetic traversal has zero unauthorized items, prohibited
fields, duplicates, gaps, or order drift and distinguishes fresh/empty/stale/unavailable truthfully.

- [x] T018 [US4] Specify the future owned transaction-query and sanitized item slice in `homework-3/specs/001-virtual-card-controls/task-slices/us4-transactions.md`
  - Traces to: OBJ-003, OBJ-006; FR-022–FR-025, FR-028, FR-030; EC-001, EC-013, EC-015, EC-022, EC-026; SC-004
  - Agent: Transaction-history specification writer
  - Model tier: Standard
  - Tier rationale: Field and ownership behavior is explicit in the approved history contract.
  - Inputs: `contracts/transaction-history.md`, `data-model.md`, T004, T006
  - Output: `homework-3/specs/001-virtual-card-controls/task-slices/us4-transactions.md` — `Query and item` subsection
  - Dependencies: T017
  - Parallel-safe: No — canonical file edits are serialized.
  - Acceptance criteria: Ownership is rechecked per request/continuation; immutable identity/time, exact signed amounts, statuses, linked refunds, masked identity, safe labels, and taxonomy allowlist are explicit.
  - Reviewer: Independent privacy/data reviewer / Advanced

- [x] T019 [US4] Specify snapshot-bound keyset continuation and ordering in `homework-3/specs/001-virtual-card-controls/task-slices/us4-transactions.md`
  - Traces to: FR-026–FR-028; NFR-010, NFR-014; EC-011–EC-013; SC-004
  - Agent: Data-query specification writer
  - Model tier: Standard
  - Tier rationale: The approved snapshot/keyset decision bounds the design task.
  - Inputs: `contracts/transaction-history.md`, `research.md` R-004, T018
  - Output: `homework-3/specs/001-virtual-card-controls/task-slices/us4-transactions.md` — `Paging` subsection
  - Dependencies: T018
  - Parallel-safe: No — same canonical file and depends on the query context.
  - Acceptance criteria: First-page context, filters, source snapshot/`as of`, immutable descending sort key, 50 default/100 maximum, continuation binding, refresh semantics, and offset prohibition are explicit.
  - Reviewer: Independent data/reliability reviewer / Standard

- [x] T020 [US4] Specify freshness, truthful empty state, and availability in `homework-3/specs/001-virtual-card-controls/task-slices/us4-transactions.md`
  - Traces to: FR-029; NFR-006–NFR-007, NFR-013; EC-014; SC-004, SC-007
  - Agent: Reliability/content specification writer
  - Model tier: Standard
  - Tier rationale: Thresholds and categories are already approved and need consistent presentation.
  - Inputs: `contracts/transaction-history.md`, approved `spec.md`, T019
  - Output: `homework-3/specs/001-virtual-card-controls/task-slices/us4-transactions.md` — `Freshness and availability` subsection
  - Dependencies: T019
  - Parallel-safe: No — same canonical file and completes the query behavior.
  - Acceptance criteria: Healthy complete data ≤60 seconds may be empty/fresh; a trusted snapshot >60 seconds and ≤15 minutes is `STALE` with `as of` whether source health is healthy or degraded; a degraded trusted snapshot ≤15 minutes is also `STALE`; absent or >15-minute data is `UNAVAILABLE`; no category substitutes for another.
  - Reviewer: Independent reliability reviewer / Standard

- [x] T021 [US4] Define future transaction access, paging, time, status, and privacy checks in `homework-3/specs/001-virtual-card-controls/task-slices/us4-transactions.md`
  - Traces to: FR-022–FR-030; NFR-002, NFR-006–NFR-007, NFR-010, NFR-013–NFR-014; EC-001, EC-011–EC-015, EC-022, EC-026; SC-004, SC-007
  - Agent: Data/QA scenario designer
  - Model tier: Standard
  - Tier rationale: Explicit scale and classification oracles make test design bounded.
  - Inputs: T007, T018–T020
  - Output: `homework-3/specs/001-virtual-card-controls/task-slices/us4-transactions.md` — `Verification` subsection
  - Dependencies: T020
  - Parallel-safe: No — it verifies the completed US4 slice.
  - Acceptance criteria: 100,000 items, tied times, arrivals, status evolution, linked refunds, multiple currencies, DST display, changed ownership, page bounds, prohibited-data scan, 2-second first-page target, healthy-but-old `STALE`, degraded `STALE`, and `UNAVAILABLE` all have objective pass criteria.
  - Reviewer: Independent privacy/performance reviewer / Advanced

**Checkpoint**: US4 is independently implementable and its traversal/privacy oracle is complete.

## Phase 7: User Story 5 — Perform Internal Oversight (P2)

**Story goal**: Document case-bound operations and compliance capabilities with distinct permissions,
safe emergency freeze, controlled export, and complete evidence.
**Independent test**: The full role×case×purpose×action matrix and abuse boundaries allow only
explicit cells, leak no target data, and reconcile every outcome to one audit identity.

- [x] T022 [US5] Specify the future internal-authorization decision and matrix in `homework-3/specs/001-virtual-card-controls/task-slices/us5-oversight.md`
  - Traces to: OBJ-004, OBJ-005; FR-031–FR-032, FR-034–FR-037; NFR-001; EC-004, EC-015–EC-018; SC-005–SC-006
  - Agent: Security authorization specification writer
  - Model tier: Advanced
  - Tier rationale: Least privilege, target non-disclosure, and separation of duties are high-risk controls.
  - Inputs: `contracts/internal-access-audit.md`, `data-model.md`, T004, T006
  - Output: `homework-3/specs/001-virtual-card-controls/task-slices/us5-oversight.md` — `Internal authorization` subsection
  - Dependencies: T021
  - Parallel-safe: No — canonical edits are serialized and this matrix governs later US5 slices.
  - Acceptance criteria: Every search/read/freeze/export decision rechecks role, authoritative open assigned case, enumerated purpose, expiry, exact permission, and step-up where required; all unspecified cells deny without target leakage.
  - Reviewer: Independent security/compliance reviewer / Advanced

- [x] T023 [US5] Specify future operations emergency-freeze and abuse controls in `homework-3/specs/001-virtual-card-controls/task-slices/us5-oversight.md`
  - Traces to: FR-031–FR-034, FR-037, FR-041; NFR-001, NFR-004, NFR-011; EC-005, EC-016–EC-018; SC-005–SC-007
  - Agent: Operations-risk specification writer
  - Model tier: Advanced
  - Tier rationale: Emergency controls and abuse thresholds have direct fraud and availability consequences.
  - Inputs: `contracts/internal-access-audit.md`, `contracts/control-commands.md`, T022
  - Output: `homework-3/specs/001-virtual-card-controls/task-slices/us5-oversight.md` — `Operations controls` subsection
  - Dependencies: T022
  - Parallel-safe: No — same canonical file and permission matrix dependency.
  - Acceptance criteria: Only allowed operations purposes plus current policy and enumerated reason can add `OPS_FREEZE`; durable local block precedes acceptance; release/export/limit changes are impossible; 20/21-subject threshold behavior is deterministic.
  - Reviewer: Independent fraud/risk reviewer / Advanced

- [x] T024 [US5] Specify the future compliance read and scoped export slice in `homework-3/specs/001-virtual-card-controls/task-slices/us5-oversight.md`
  - Traces to: FR-031–FR-032, FR-035–FR-040; NFR-001–NFR-003, NFR-012; EC-016, EC-018–EC-020; SC-005–SC-007
  - Agent: Compliance/privacy specification writer
  - Model tier: Advanced
  - Tier rationale: Export minimization, retention assumptions, and evidence access require regulated-domain judgment.
  - Inputs: `contracts/internal-access-audit.md`, `research.md` R-005/R-009, T022
  - Output: `homework-3/specs/001-virtual-card-controls/task-slices/us5-oversight.md` — `Compliance evidence and export` subsection
  - Dependencies: T023
  - Parallel-safe: No — canonical edits are serialized and export behavior depends on the shared matrix.
  - Acceptance criteria: Read-only case-scoped evidence, one-case current-step-up export, ≤10,000 sanitized records, 24-hour expiry, attribution/watermark, no operations export, hold-aware assumed retention, and audited denials are explicit.
  - Reviewer: Independent compliance/privacy reviewer / Advanced

- [x] T025 [US5] Specify audit intent, evidence, diagnostics, recovery, and degraded-safe mode in `homework-3/specs/001-virtual-card-controls/task-slices/us5-oversight.md`
  - Traces to: OBJ-005–OBJ-006; FR-037–FR-041; NFR-002–NFR-003, NFR-007, NFR-011–NFR-012; EC-019–EC-020; SC-006–SC-007
  - Agent: Audit/reliability specification writer
  - Model tier: Advanced
  - Tier rationale: Evidence atomicity, privacy, correction, and safe degradation are high-impact cross-cutting controls.
  - Inputs: `contracts/internal-access-audit.md`, `research.md` R-002/R-003/R-005, T024
  - Output: `homework-3/specs/001-virtual-card-controls/task-slices/us5-oversight.md` — `Audit and recovery` subsection
  - Dependencies: T024
  - Parallel-safe: No — same canonical file and evidence behavior follows privileged outcomes.
  - Acceptance criteria: One durable intent/event identity per outcome, idempotent replay, linked corrections, separate sanitized diagnostics, 5-second alert, 5-minute recovery, 15-minute incident, and approved degraded-safe permissions are explicit.
  - Reviewer: Independent security/compliance reviewer / Advanced

- [x] T026 [US5] Define future internal authorization, abuse, export, evidence, and recovery checks in `homework-3/specs/001-virtual-card-controls/task-slices/us5-oversight.md`
  - Traces to: FR-031–FR-041; NFR-001–NFR-004, NFR-011–NFR-013; EC-004–EC-006, EC-015–EC-020, EC-023–EC-024; SC-005–SC-007
  - Agent: Security/compliance QA designer
  - Model tier: Standard
  - Tier rationale: Matrix and timeline test design is bounded; independent Advanced review owns risky judgments.
  - Inputs: T007, T022–T025
  - Output: `homework-3/specs/001-virtual-card-controls/task-slices/us5-oversight.md` — `Verification` subsection
  - Dependencies: T025
  - Parallel-safe: No — it verifies the completed US5 slice.
  - Acceptance criteria: Full role/case-status/purpose/action matrix, 20/21 search subjects, 10,000/10,001 records, step-up expiry, delayed/duplicate evidence, correction, degraded-safe decisions, taxonomy scan, and retention/hold review have objective outcomes.
  - Reviewer: Independent security/compliance reviewer / Advanced

**Checkpoint**: US5 is independently implementable; operations and compliance powers remain distinct,
case-bound, attributable, and privacy-safe.

## Phase 8: Graded Artifact Publication

**Purpose**: Publish the required Homework 3 files from approved and task-validated inputs.

- [x] T027 Publish the approved product body and synchronized low-level task section in `homework-3/specification.md`
  - Traces to: OBJ-001–OBJ-006, FR-001–FR-041, NFR-001–NFR-014, EC-001–EC-026, SC-001–SC-008; R-008
  - Agent: Canonical specification editor
  - Model tier: Standard
  - Tier rationale: Publication is controlled synthesis with a predefined parity procedure.
  - Inputs: Approved `spec.md`, T003, `homework-3/specs/001-virtual-card-controls/task-slices/*.md`, this `tasks.md`
  - Output: `homework-3/specification.md`; this is the sole canonical-publication step
  - Dependencies: T026
  - Parallel-safe: No — it consolidates the canonical graded artifact.
  - Acceptance criteria: Product body remains semantically equivalent to approved `spec.md`; layered objective/context/guardrail/edge/verification/performance content is intact; substantial low-level tasks have acceptance criteria and complete ID traceability.
  - Reviewer: Independent requirements/traceability reviewer / Advanced

- [x] T028 [P] Produce future-agent stack, workflow, FinTech, edge-case, security, and verification guidance in `homework-3/agents.md`
  - Traces to: OBJ-001–OBJ-006; FR-001–FR-041; NFR-001–NFR-014; EC-001–EC-026; SC-001–SC-008
  - Agent: Engineering-guidance writer
  - Model tier: Standard
  - Tier rationale: Concrete guidance is derived from the approved plan and contracts.
  - Inputs: Approved `plan.md`, `research.md`, `data-model.md`, contracts, T004–T007
  - Output: `homework-3/agents.md`
  - Dependencies: T027
  - Parallel-safe: Yes — distinct graded file and fixed approved inputs.
  - Acceptance criteria: Guidance states replaceable Node.js/TypeScript/NestJS/Jest/Supertest assumptions, exact money/time/state rules, authorization/audit/privacy defaults, verification expectations, edge-case behavior, approval gates, and prohibition on secrets/production data; it documents the logically distinct graded section combined with operational `AGENTS.md` on case-insensitive APFS.
  - Reviewer: Independent FinTech/security reviewer / Advanced

- [x] T029 Reconcile active ChatGPT/Codex repository rules in the graded section of `homework-3/AGENTS.md`
  - Traces to: NFR-001–NFR-014; FR-003, FR-008–FR-010, FR-013–FR-020, FR-025–FR-026, FR-031–FR-041
  - Agent: `AG-S01` / `codex-spec-author` acting as ChatGPT/Codex rules writer
  - Model tier: Standard
  - Tier rationale: The artifact condenses approved constraints but must avoid conflicts and unsafe omissions.
  - Inputs: existing operational `AGENTS.md`, approved `plan.md`, contracts, T004–T007, T028
  - Output: `homework-3/AGENTS.md` — clearly delimited active ChatGPT/Codex repository-rules section
  - Dependencies: T028
  - Parallel-safe: No — T028 and T029 share the one physical `AGENTS.md`/`agents.md` file on case-insensitive APFS.
  - Acceptance criteria: Codex reads the rules through `AGENTS.md`; the rules are concise, actionable, consistent with the graded `agents.md` section, enforce spec-first gates and FinTech-safe defaults, and never authorize implementation for Homework 3.
  - Reviewer: Independent AI-governance/security reviewer / Advanced

- [x] T030 [P] Produce the homework rationale and industry-practice mapping in `homework-3/README.md`
  - Traces to: OBJ-001–OBJ-006, NFR-001–NFR-014, SC-001–SC-008; R-001–R-009
  - Agent: Technical writer
  - Model tier: Standard
  - Tier rationale: The README requires clear synthesis and source-to-section mapping, not high-risk policy creation.
  - Inputs: `TASKS.md`, approved spec/plan, `research.md`, contracts, T004–T007
  - Output: `homework-3/README.md`
  - Dependencies: T027
  - Parallel-safe: Yes — distinct graded file and fixed inputs.
  - Acceptance criteria: Includes student/task summary using the repository Git author name, rationale for layering/performance/verification, and section-level mapping of payment, security, identity, audit, privacy, reliability, and accessibility practices with official sources and non-compliance disclaimers.
  - Reviewer: Independent compliance/technical reviewer / Standard; link scan / Economy

**Checkpoint**: `specification.md`, the combined physical `AGENTS.md`/`agents.md` artifact containing
active ChatGPT/Codex rules, and `README.md` all exist as documentation-only graded artifacts.

## Phase 9: Independent Review and Cross-Artifact Analysis

**Purpose**: Keep material authorship separate from domain, quality, and consistency validation.

- [x] T031 [P] Review state controls, exact limit accounting, propagation safety, and FinTech failure semantics in `homework-3/specs/001-virtual-card-controls/reviews/final-fintech.md`
  - Traces to: OBJ-001–OBJ-002, OBJ-005–OBJ-006; FR-001–FR-021, FR-033, FR-038–FR-041; NFR-003–NFR-009, NFR-011, NFR-014; EC-002–EC-010, EC-019, EC-021–EC-026; SC-001–SC-003, SC-006–SC-007
  - Agent: Independent FinTech/payments reviewer
  - Model tier: Advanced
  - Tier rationale: Adversarial review of money movement controls and safe failures requires senior domain judgment.
  - Inputs: `specification.md`, combined `AGENTS.md`/`agents.md`, control contract, traceability matrix
  - Output: `homework-3/specs/001-virtual-card-controls/reviews/final-fintech.md`
  - Dependencies: T027–T030
  - Parallel-safe: Yes — dedicated report and non-overlapping review domain.
  - Acceptance criteria: Findings include severity, affected IDs/files, evidence, owner, and resolution state; no Critical/High issue is omitted or softened.
  - Reviewer: Planning orchestrator / Advanced for finding completeness only

- [x] T032 [P] Review authorization, privacy taxonomy, audit, export, retention assumptions, and compliance claims in `homework-3/specs/001-virtual-card-controls/reviews/final-security-compliance.md`
  - Traces to: OBJ-004–OBJ-006; FR-025, FR-031–FR-041; NFR-001–NFR-003, NFR-011–NFR-012; EC-015–EC-020; SC-005–SC-007
  - Agent: Independent security/compliance reviewer
  - Model tier: Advanced
  - Tier rationale: Access, evidence, privacy, and regulatory-claim errors carry high impact.
  - Inputs: All four graded artifacts, internal-access contract, `research.md` R-009, traceability matrix
  - Output: `homework-3/specs/001-virtual-card-controls/reviews/final-security-compliance.md`
  - Dependencies: T027–T030
  - Parallel-safe: Yes — dedicated report and non-overlapping review domain.
  - Acceptance criteria: Role/case/purpose/action boundaries, prohibited-data coverage, evidence semantics, hold-aware assumptions, and source limitations are checked; findings have severity/owner/status.
  - Reviewer: Planning orchestrator / Advanced for finding completeness only

- [x] T033 [P] Review edge cases, measurable targets, independent testability, accessibility, and task executability in `homework-3/specs/001-virtual-card-controls/reviews/final-qa-performance.md`
  - Traces to: OBJ-001–OBJ-006; NFR-003–NFR-014; EC-001–EC-026; SC-001–SC-008
  - Agent: Independent QA/reliability reviewer
  - Model tier: Standard
  - Tier rationale: Targets and oracles are explicit; review is broad but bounded.
  - Inputs: All graded artifacts, `quickstart.md`, fixture catalog, this `tasks.md`
  - Output: `homework-3/specs/001-virtual-card-controls/reviews/final-qa-performance.md`
  - Dependencies: T027–T030
  - Parallel-safe: Yes — dedicated report and non-overlapping review domain.
  - Acceptance criteria: Every story has an independent oracle; every numerical target has measurement semantics; all ECs and SCs are covered; tasks are actionable without implementation guesses.
  - Reviewer: Planning orchestrator / Standard for finding completeness only

- [x] T034 [P] Run mechanical links, placeholders, taxonomy terms, checklist format, and task-field validation in `homework-3/specs/001-virtual-card-controls/reviews/final-mechanical.md`
  - Traces to: NFR-002, SC-008; task-format policy
  - Agent: Documentation QA checker
  - Model tier: Economy
  - Tier rationale: Pattern, link, placeholder, formatting, and required-field checks are mechanical.
  - Inputs: All graded and Spec Kit Markdown artifacts
  - Output: `homework-3/specs/001-virtual-card-controls/reviews/final-mechanical.md`
  - Dependencies: T027–T030
  - Parallel-safe: Yes — dedicated report and read-only checks.
  - Acceptance criteria: All local links resolve; no unintended TODO/TBD/template marker or trailing whitespace remains; every task has checkbox, sequential ID, valid labels, path, routing fields, dependencies, parallel rationale, and acceptance criteria.
  - Reviewer: QA analyst / Standard

- [x] T035 Reconcile all review findings in the affected graded artifacts and record dispositions in `homework-3/specs/001-virtual-card-controls/reviews/final-findings.md`
  - Traces to: OBJ-001–OBJ-006; FR-001–FR-041; NFR-001–NFR-014; EC-001–EC-026; SC-001–SC-008; each finding record also copies its exact affected IDs
  - Agent: Documentation reconciliation lead
  - Model tier: Advanced
  - Tier rationale: Cross-file conflict resolution can affect approved semantics and gate validity.
  - Inputs: T031–T034 reports, approval log, publication procedure, graded artifacts
  - Output: Corrected graded artifacts and `specs/001-virtual-card-controls/reviews/final-findings.md`
  - Dependencies: T031, T032, T033, T034
  - Parallel-safe: No — one owner must reconcile cross-file changes and assess gate impact.
  - Acceptance criteria: Every finding is resolved, explicitly accepted as a remaining risk, or escalated; any product/plan semantic change stops publication and triggers renewed upstream approval.
  - Reviewer: Independent consistency reviewer / Advanced

- [x] T036 Run Spec Kit cross-artifact consistency analysis and record the final result in `homework-3/specs/001-virtual-card-controls/reviews/analyze.md`
  - Traces to: OBJ-001–OBJ-006, FR-001–FR-041, NFR-001–NFR-014, EC-001–EC-026, SC-001–SC-008
  - Agent: Cross-artifact analysis orchestrator
  - Model tier: Advanced
  - Tier rationale: Analysis must prioritize and resolve conflicts across approved and graded artifacts.
  - Inputs: Approved spec/plan, this `tasks.md`, graded artifacts, T002, T035
  - Output: `homework-3/specs/001-virtual-card-controls/reviews/analyze.md`
  - Dependencies: T035
  - Parallel-safe: No — analysis runs only on the reconciled complete package.
  - Acceptance criteria: No unresolved Critical/High inconsistency, coverage gap, constitutional violation, unauthorized scope expansion, or model-routing violation; Medium/Low items have explicit dispositions.
  - Reviewer: Independent traceability/FinTech reviewer / Advanced

- [x] T037 Re-run checklists, Constitution Check, canonical parity, and no-code-boundary validation in `homework-3/specs/001-virtual-card-controls/reviews/final-validation.md`
  - Traces to: SC-001–SC-008; Constitution; Homework 3 scope
  - Agent: Documentation release QA
  - Model tier: Standard
  - Tier rationale: Product-body semantic equivalence and Constitution alignment require bounded judgment; an Economy subtask may perform hashes, links, totals, and file-presence checks.
  - Inputs: All approved, graded, review, and checklist artifacts; T036
  - Output: `homework-3/specs/001-virtual-card-controls/reviews/final-validation.md`
  - Dependencies: T036
  - Parallel-safe: No — it validates the exact final package.
  - Acceptance criteria: Checklist totals pass; approved hashes/provenance are intact unless formally re-approved; product-body equivalence and task parity pass separately; all links resolve; no code/dependency/schema/migration exists.
  - Reviewer: Independent QA/requirements reviewer / Standard

**Checkpoint**: The package has no unresolved Critical/High issue and exact validation evidence is
reproducible.

## Phase 10: Gate 3 and Homework Stop Condition

- [x] T038 Assemble the exact Gate 3 approval package in `homework-3/specs/001-virtual-card-controls/reviews/gate-3-package.md`
  - Traces to: OBJ-001–OBJ-006; FR-001–FR-041; NFR-001–NFR-014; EC-001–EC-026; SC-001–SC-008
  - Agent: Approval-gate synthesizer
  - Model tier: Advanced
  - Tier rationale: Gate synthesis must accurately represent scope, evidence, residual risks, and version provenance.
  - Inputs: T035–T037, all graded artifacts, approval log
  - Output: `homework-3/specs/001-virtual-card-controls/reviews/gate-3-package.md`
  - Dependencies: T037
  - Parallel-safe: No — it summarizes the exact final validated state.
  - Acceptance criteria: Package lists artifact paths/hashes, coverage/checklist/review evidence, resolved findings, remaining assumptions/risks, no-code statement, and exact approval scope.
  - Reviewer: Independent gate/consistency reviewer / Advanced

- [ ] T039 Obtain explicit Gate 3 approval and record the exact decision in `.specify/memory/approvals.md`
  - Traces to: SC-008; workflow governance
  - Agent: Approval recorder
  - Model tier: Economy
  - Tier rationale: Recording an explicit user decision and hashes is mechanical; interpreting silence is forbidden.
  - Inputs: T038 and explicit user response
  - Output: `.specify/memory/approvals.md`
  - Dependencies: T038
  - Parallel-safe: No — requires the user's explicit approval of the exact package.
  - Acceptance criteria: Approval is recorded only after an unambiguous user decision and binds exact artifacts/hashes; rejection or requested change remains unapproved.
  - Reviewer: Documentation QA / Economy

- [ ] T040 Record the Homework 3 stop condition and final handoff in `homework-3/specs/001-virtual-card-controls/reviews/final-handoff.md`
  - Traces to: OBJ-001–OBJ-006; SC-008; Constitution II–III; Homework 3 out-of-scope boundary
  - Agent: Documentation release coordinator
  - Model tier: Economy
  - Tier rationale: Final status and prohibition recording are bounded administrative work.
  - Inputs: T039, `AGENTS.md`, `TASKS.md`
  - Output: `homework-3/specs/001-virtual-card-controls/reviews/final-handoff.md`
  - Dependencies: T039
  - Parallel-safe: No — it is the terminal workflow action.
  - Acceptance criteria: Handoff states that documentation is complete, lists remaining pre-production assumptions, and explicitly prohibits `speckit-implement`, source creation, dependency installation, deployment, or claims of production compliance.
  - Reviewer: Documentation QA / Economy

## Dependencies and Story Completion Order

```text
T001 → T002 → T003
              ├─ T004 ─┐
              ├─ T005  │
              ├─ T006 ─┼→ T008–T010 (US1)
              └─ T007 ─┘       ↓
                         T011–T013 (US2)
                                ↓
                         T014–T017 (US3)
                                ↓
                         T018–T021 (US4)
                                ↓
                         T022–T026 (US5)
                                ↓
                         T027 → T028 → T029; T030 after T027
                                ↓
                         T031/T032/T033/T034
                                ↓
                         T035 → T036 → T037 → T038 → T039 → T040
```

- US1 is the suggested future MVP because it delivers the primary loss-prevention control.
- US2 depends on the shared composite-state model and should follow US1, though its behavior remains
  independently testable.
- US3 and US4 are behaviorally independent after the foundation, but canonical `specification.md`
  edits are serialized to prevent write overlap and drift.
- US5 follows the cardholder slices so its emergency-freeze and evidence tasks can verify rather than
  redefine their shared state/audit semantics.
- T028 and T030 may run in parallel after story documentation is fixed because their outputs do not
  overlap. T029 must follow T028 because both update the same physical `AGENTS.md`/`agents.md` file.
- T031–T034 may run in parallel because reviewers write separate reports and do not edit source artifacts.

## Parallel Execution Examples

### Foundation

After T003, assign T004, T005, T006, and T007 to separate agents. Each writes a distinct review file;
all shared decisions are already approved.

### Graded Artifacts

After T027 fixes canonical product/task wording, T028 (`agents.md`) and T030 (`README.md`) may proceed
in parallel. T029 follows T028 because both names resolve to the same physical `AGENTS.md` file.

### Independent Reviews

After T027–T030, run T031–T034 concurrently with distinct reviewer roles and output reports. Reviewers
must not edit the artifacts they assess; T035 owns remediation.

## Delivery Strategy

1. **Foundation first**: Freeze exact approvals, traceability, vocabulary, context, boundaries, and fixtures.
2. **MVP documentation**: Complete US1 and prove its independent freeze safety oracle.
3. **Incremental stories**: Add US2–US5 in priority order without changing previously approved semantics.
4. **Publish once**: Consolidate the validated low-level slices into canonical `specification.md`.
5. **Independent assurance**: Draft the other graded artifacts, run separated domain reviews, reconcile,
   then execute cross-artifact analysis and final validation.
6. **Stop at Gate 3**: Record explicit package approval and end the homework workflow without implementation.

## Task List Validation

- [x] Every task uses a Markdown checkbox, sequential `T###` ID, exact output path, routing fields,
  dependencies, parallel rationale, acceptance criteria, and reviewer.
- [x] Every user-story task has a `[US#]` label; setup/foundation/polish/gate tasks do not.
- [x] `[P]` appears only for distinct output files with fixed shared decisions.
- [x] Every OBJ, FR, NFR, EC, and SC family has task and verification coverage.
- [x] Economy handles mechanical work; Standard handles bounded drafting/design; Advanced is reserved
  for FinTech, security/compliance, cross-artifact reconciliation, and gate judgment.
- [x] Material authors and final reviewers are independent.
- [x] No task authorizes application code, executable API/UI, schema, migration, dependency, deployment,
  or `speckit-implement` work.
