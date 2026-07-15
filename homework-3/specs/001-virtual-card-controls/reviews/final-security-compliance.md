# Final Security, Compliance, and Privacy Review

**Review type**: Independent, read-only review
**Reviewer role**: Security/compliance/privacy reviewer (Advanced)
**Reviewed artifacts**: `specification.md`, `AGENTS.md`/`agents.md`,
the active ChatGPT/Codex rules in `AGENTS.md`, `README.md`, `tasks.md`, the approved `spec.md` and `plan.md`,
`contracts/internal-access-audit.md`, and `research.md` decision R-009
**Review date**: 2026-07-15
**Source-artifact edits by reviewer**: None

## Executive Result

**PASS — all FSC-001–FSC-003 findings are resolved.**

No Critical finding was identified in the initial review. The one High and two Medium findings were
remediated and independently re-reviewed. No new Critical, High, or Medium finding was identified.

## Findings

### FSC-001 — Audit-event coverage is inconsistent across result categories

- **Severity**: High
- **Status**: Resolved
- **Affected requirements and lines**:
  - `specification.md:55` (`OBJ-005`) requires tamper-evident evidence for every attempted control
    change and privileged read.
  - `specification.md:252-260` defines seven result categories, including `VALIDATION_ERROR`,
    `CONFLICT`, `IDEMPOTENCY_MISMATCH`, `TEMPORARILY_UNAVAILABLE`, and non-terminal
    `PENDING_PROPAGATION`.
  - `specification.md:225-226` (`FR-005`) requires an attributable result record for every freeze
    attempt, but does not state whether that record is the business audit event required by
    `OBJ-005`/`SC-006`.
  - `specification.md:306-307` (`FR-021`) explicitly covers every attempted limit change, while no
    equivalent blanket rule exists for unfreeze attempts.
  - `specification.md:372-380` (`FR-037-FR-041`) covers successful/denied privileged activity and
    reconciliation, but does not close the customer-command result-category gap.
  - `specification.md:429` (`NFR-003`) narrows reconciliation to accepted/denied control attempts and
    privileged outcomes, whereas `specification.md:580-582` (`SC-006`) again says all control attempts
    and privileged accesses.
  - `contracts/internal-access-audit.md:48-53,91-92` binds audit intent to a state change or privileged
    outcome and verifies accepted/denied outcomes, not every customer control result.
  - `agents.md:190-199` repeats the state-change/privileged-outcome boundary.
- **Risk**: A future implementation can reasonably omit business evidence for conflicts, validation
  failures, dependency-unavailable results, some unfreeze failures, or propagation status changes
  while still claiming conformance to the narrower NFR/contract. Conversely, interpreting “every
  attempt” as one new business event per exact retry would violate duplicate-safe replay semantics.
  This makes the promised 100% reconciliation oracle non-deterministic.
- **Recommendation**: Define one normative outcome-to-evidence matrix for every approved result
  category and every command/privileged activity. Distinguish an inbound attempt/result record from
  the deduplicated business audit event: specify when an exact retry references the original event,
  when a new denial event is required, and how `PENDING_PROPAGATION` plus its final reconciliation are
  represented. Align `FR-005`, unfreeze requirements, `FR-021`, `FR-037-FR-041`, `NFR-003`, `SC-006`,
  the internal-access/audit contract, future-agent guidance, and LL task acceptance criteria.
- **Remediation owner**: Product/security specification author; independent compliance reviewer to
  re-run outcome-to-event reconciliation.
- **Re-review evidence**:
  - `specification.md:748-761` now provides one normative matrix covering state-changing success,
    successful no-op, pending propagation, all five non-success terminal categories, exact retry,
    every privileged outcome, replay, correction, and recovery.
  - The matrix assigns one root identity per distinct command/outcome, makes exact retries reference
    the stored root without another business event, and models pending/final propagation evidence as
    immutable linked events.
  - `contracts/internal-access-audit.md:61-66`, `agents.md:195-202`,
    the active ChatGPT/Codex rules in `AGENTS.md`, `task-slices/us5-oversight.md:19`, and
    `specification.md:742` carry the same semantics and require deterministic reconciliation for every
    result category.
  - **Disposition**: The normative matrix resolves the former scope ambiguity without weakening
    duplicate-safe retry behavior. The older accepted/denied wording is now a covered subset, not an
    exclusion of other result categories.

### FSC-002 — Compliance export references an allowlist that is not field-level explicit

- **Severity**: Medium
- **Status**: Resolved
- **Affected requirements and lines**:
  - `specification.md:366-371` (`FR-035-FR-036`) requires sanitized, explicitly allowed export data.
  - `specification.md:388-398` calls the taxonomy canonical, but the compliance row permits broad
    “sanitized transaction/control/audit fields explicitly listed by the case export policy” without
    identifying the actual allowed fields or an approved policy artifact.
  - `contracts/internal-access-audit.md:38-41` claims an “explicit canonical-taxonomy allowlist,” while
    `contracts/internal-access-audit.md:73-85` repeats only category-level descriptions.
  - `agents.md:178-195` and `specification.md:736-742` (`LL-US5-03/04`) direct future work to an
    allowlist but do not resolve its contents.
- **Risk**: A future agent must invent or retrieve an unspecified export schema at implementation
  time. “Sanitized” is not a field-level minimization rule, so different implementations can expose
  materially different merchant, transaction, actor, control, or audit attributes while claiming
  compliance with the canonical taxonomy. The zero-prohibited-category scan alone cannot prove that
  allowed data is necessary for the case purpose.
- **Recommendation**: Enumerate the exact compliance view/export field allowlist in the canonical
  taxonomy, including conditional fields per enumerated purpose, or name a separately approved,
  versioned policy artifact as a required dependency and require fail-closed behavior when it is
  absent/stale. Keep the 10,000-record cap, one-case binding, step-up, watermark, expiry, target
  non-disclosure, and audit requirements unchanged.
- **Remediation owner**: Privacy/compliance policy owner with product-security review.
- **Re-review evidence**:
  - `specification.md:763-766` selects the approved alternative from the recommendation: the exact
    field allowlist is an issuer-owned, current, approved, versioned, purpose-bound policy dependency,
    not an implementation-time decision. Missing, stale, actor/case/purpose-mismatched, or
    export-version-mismatched policy fails closed without target disclosure.
  - `contracts/internal-access-audit.md:36-42`, `agents.md:184-185`,
    the active ChatGPT/Codex rules in `AGENTS.md`, `task-slices/us5-oversight.md:13-15`, and
    `specification.md:738,791` consistently require that dependency before export.
  - The existing one-case, step-up, 10,000-record, 24-hour expiry, attribution/watermark, taxonomy,
    audit, abuse-alert, and no-target-leakage controls remain intact.
  - **Disposition**: The dependency is explicit and fail-closed; a future implementation cannot invent
    its own export fields or proceed with absent/stale policy.

### FSC-003 — The operational/graded `AGENTS.md` relationship is described inconsistently

- **Severity**: Medium
- **Status**: Resolved
- **Affected requirements and lines**:
  - `AGENTS.md:22-23` says graded `agents.md` is an artifact distinct from operational `AGENTS.md`.
  - `AGENTS.md:97-103` says the case-insensitive filesystem makes both names resolve to one combined
    physical artifact.
  - `README.md:16-20` presents `agents.md` as the supporting guidance without explaining the combined
    delivery.
  - `tasks.md:405-415` (`T028`) requests `homework-3/agents.md` without recording the same-file exception
    in its output/acceptance criteria.
- **Evidence**: On the reviewed workspace, `AGENTS.md` and `agents.md` have the same inode and identical
  contents, so the compatibility note is factually correct; the earlier “distinct artifact” statement
  is not.
- **Risk**: A future agent or evaluator can interpret the operational section as requiring a second
  file, overwrite the combined artifact, or treat the graded section as operational authority without
  respecting its delimiter. This is a governance and submission-integrity ambiguity, not a filesystem
  exploit.
- **Recommendation**: State consistently that the two are logically distinct sections/deliverables
  combined in one physical file solely because of the case-insensitive filesystem. Update the scope
  rule, T028 acceptance criteria, and README description; retain explicit delimiters and precedence.
- **Remediation owner**: Documentation/workflow owner.
- **Re-review evidence**:
  - `AGENTS.md:22-23` now says the graded guidance is a logically distinct section sharing one physical
    file with operational guidance and requires delimiters plus operational precedence.
  - `AGENTS.md:97-103` retains the matching compatibility note.
  - `README.md:16-24` explains the combined delivery and precedence to evaluators.
  - `tasks.md:405-415` (`T028`) records the APFS exception in acceptance criteria while still treating
    the guidance as the task's logical graded output.
  - **Disposition**: The former contradiction is removed. `AGENTS.md` and `agents.md` remain the same
    physical file with clearly bounded logical sections.

## Controls Verified Without Finding

- **Role/case/purpose/action**: `FR-031-FR-037` and the internal-access contract require current role,
  authoritative assigned open unexpired case, enumerated purpose, exact permission, per-action
  re-evaluation, and export step-up. Operations and compliance duties are separated.
- **Target non-disclosure**: Wrong-role/case/purpose, expired/reassigned cases, unspecified permission
  cells, cross-case export, and idempotency mismatch deny without confirming target existence or
  returning target detail. The 20/21 search and 10,000/10,001 export boundaries are testable.
- **Operations controls**: Operations cannot export, change limits, or release restrictions; an
  emergency freeze requires an enumerated reason and the same durable-local-block invariant as a user
  freeze.
- **Audit versus diagnostics**: The package consistently keeps append-only/tamper-evident business
  evidence separate from sanitized diagnostics, makes corrections linked events, requires
  idempotent replay, and states that diagnostics cannot substitute for evidence.
- **Recovery**: Missing evidence has named 5-second alert, 5-minute recovery/degraded-safe, and
  15-minute incident points. Risk-increasing writes and exports fail closed while durable freezes and
  authorized reads remain conditional on durable audit intent.
- **Sensitive-data prohibitions**: Full PAN, CVV, credentials, verification material, raw dependency
  payloads, unrelated-case/customer data, unsafe free text, and production/personal fixture data are
  prohibited across the named surfaces. Synthetic/masked fixture guidance is consistent.
- **Retention limitations**: Seven-year audit retention and 24-month cardholder history are labeled
  assumptions; jurisdiction, legal hold, deletion, and disposition remain subject to legal/policy
  approval.
- **Compliance-claim limitations**: R-009 and README correctly treat PCI DSS, NIST, OWASP ASVS, and
  the NIST Privacy Framework as control/verification references rather than certification, legal
  advice, or production-readiness claims. Applicability and assurance decisions are explicitly
  deferred to qualified stakeholders.

## Re-review Conclusion

The remediation satisfies all four original pass conditions. Role/case/purpose/action authorization,
target non-disclosure, export minimization, outcome-to-evidence reconciliation, evidence/diagnostic
separation, retention assumptions, and compliance-claim limitations remain mutually consistent.

**Final security/compliance/privacy verdict: PASS.**
