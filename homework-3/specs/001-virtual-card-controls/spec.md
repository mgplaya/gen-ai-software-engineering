# Feature Specification: Regulated Virtual Card Controls

**Feature Branch**: `001-virtual-card-controls` (logical Spec Kit identifier; Git branch creation was
skipped because the Spec Kit project is nested inside an existing repository)
**Created**: 2026-07-15
**Status**: Draft
**Input**: Specify regulated virtual card controls for authenticated cardholders: freeze/unfreeze a
virtual card, configure spending limits, and view transactions, with operations and compliance
oversight. Produce documentation only for Homework 3.

## High-Level Objective

- **Outcome**: Enable a verified cardholder to control the risk and visibility of their virtual card
  while giving authorized operations and compliance staff a complete, privacy-safe audit view.
- **Scope boundary**: This feature covers freeze/unfreeze, per-transaction/daily/monthly spending
  limits, transaction viewing, and internal oversight for an existing virtual card; card issuance,
  termination, replacement, disputes, money movement, and implementation are excluded.

## Clarifications

### Session 2026-07-15

- Q: Which regulatory jurisdiction governs the specification? → A: Jurisdiction-neutral regulated
  baseline; jurisdiction-specific legal requirements require later legal/policy approval.
- Q: How may spending limits change while a card is frozen? → A: Valid limit decreases are allowed;
  increases are blocked until the card returns to `ACTIVE` and applicable risk/step-up checks pass.
- Q: Who may release an operations freeze? → A: Release occurs only through a separate risk/case
  workflow outside this feature's scope.
- Q: When is step-up verification required for cardholder unfreeze? → A: It is mandatory for every
  cardholder unfreeze attempt.
- Q: What happens to already authorized pending transactions after freeze? → A: Freeze blocks new
  authorizations, while existing pending transactions may post, reverse, or be refunded.

## Stakeholders and Access Boundaries

| Stakeholder | Goal | Allowed actions/data | Prohibited actions/data |
|-------------|------|----------------------|-------------------------|
| Cardholder | Reduce card risk and understand activity | View and control only owned cards; view masked card identity, limits, status, and owned-card transactions | Access another customer's card; reveal full PAN or CVV; bypass step-up verification |
| Operations analyst | Resolve support and urgent risk cases | For an assigned open case with `CUSTOMER_SUPPORT` or `URGENT_RISK_CONTAINMENT` purpose: search approved opaque IDs, read sanitized state/limits/history, and place an emergency freeze with reason | Export data; release an operations/risk freeze; change customer limits; reveal secrets; erase or alter audit history |
| Compliance reviewer | Investigate and evidence policy adherence | For an assigned open case with `REGULATORY_REVIEW`, `CONTROL_INVESTIGATION`, or `AUDIT_EVIDENCE` purpose: read sanitized evidence and create one scoped case export after step-up | Change card state/limits; use operations actions; perform unrestricted/bulk cross-case export; view prohibited data |
| Fraud/risk service | Supply policy decisions | Return issuer policy ranges, step-up requirements, or a deny/pending decision | Directly change user-visible state without an attributable audited command |

All human actors MUST be authenticated. Internal users MUST have a current role, approved case or
business purpose, and least-privilege access. Cardholder ownership MUST be re-evaluated for every
sensitive operation rather than inferred from a previously rendered screen.

## Mid-Level Objectives

| ID | Observable objective | Success evidence | Priority |
|----|----------------------|------------------|----------|
| OBJ-001 | Cardholders can freeze an active card and unfreeze only a card they froze, with an unambiguous final or pending result | State-transition acceptance scenarios and audit evidence pass | P1 |
| OBJ-002 | Cardholders can set valid per-transaction, daily, and monthly limits within issuer policy without race-induced lost updates | Boundary, step-up, idempotency, and concurrency scenarios pass | P1 |
| OBJ-003 | Cardholders can review a timely, correctly ordered, paginated history of their card transactions without exposure of prohibited card data | Transaction fixtures and access-boundary review pass | P1 |
| OBJ-004 | Authorized operations and compliance users can perform their distinct oversight duties with attributable, case-bound, least-privilege access | Role/permission matrix and internal journey review pass | P2 |
| OBJ-005 | Every attempted control change and privileged read produces tamper-evident, reconcilable evidence without logging secrets | Audit completeness, redaction, retention, and reconciliation reviews pass | P1 |
| OBJ-006 | Safety-relevant actions remain predictable during retries, stale views, concurrency, and dependency failure, within stated service targets | Failure-mode, recovery, reliability, and performance evidence pass | P1 |

## User Scenarios and Acceptance *(mandatory)*

### User Story 1 - Immediately Freeze a Card (Priority: P1)

A cardholder who notices suspicious activity freezes their existing virtual card and receives a
clear result about whether new authorizations are blocked or propagation is still pending.

**Supports**: OBJ-001, OBJ-005, OBJ-006; FR-001–FR-006
**Why this priority**: Freeze is the primary loss-prevention control and has the strictest safe-failure
behavior.
**Independent test**: Use an owned active-card fixture, request freeze, and verify state, repeated
request behavior, authorization effect, user message, and audit event without using other stories.

**Acceptance scenarios**:

1. **Given** an authenticated cardholder owns an active card, **When** they confirm freeze, **Then**
   the card becomes user-frozen, new authorization decisions are blocked within the consistency
   target, the result is shown, and one attributable successful audit event is recorded.
2. **Given** the same freeze command is retried with the same idempotency identity, **When** it is
   received again, **Then** the original result is returned without a second state transition or
   duplicate business audit event.
3. **Given** downstream propagation is unavailable, **When** freeze is confirmed, **Then** the local
   safety state becomes frozen, the cardholder sees `freeze pending external confirmation`, retries
   continue under policy, and operations receives an alert if the recovery target is exceeded.
4. **Given** transactions were authorized before freeze and remain pending, **When** the freeze takes
   effect, **Then** those transactions may still post, reverse, or be refunded, and the cardholder is
   explicitly told that freeze blocks new authorizations rather than cancelling existing ones.

### User Story 2 - Safely Unfreeze a User-Frozen Card (Priority: P1)

A cardholder restores use of a card they previously froze after passing mandatory step-up
verification, without overriding an operations or risk restriction.

**Supports**: OBJ-001, OBJ-005, OBJ-006; FR-007–FR-011
**Why this priority**: Unfreeze restores spending authority and therefore must fail closed.
**Independent test**: Exercise successful, denied, expired-verification, operations-freeze, and
dependency-failure fixtures and verify that only the eligible state changes.

**Acceptance scenarios**:

1. **Given** the owned `OPEN` card has `USER_FREEZE`, no stronger restriction, and current mandatory
   step-up verification, **When** the cardholder confirms unfreeze, **Then** only `USER_FREEZE` is
   removed, the card becomes active within the consistency target, and the transition is audited.
2. **Given** `USER_FREEZE` and a stronger operations/risk restriction both exist, **When** verified
   cardholder unfreeze succeeds, **Then** only `USER_FREEZE` is removed and the truthful effective
   status remains restricted.
3. **Given** the card is operations-frozen, risk-restricted, or terminated without `USER_FREEZE`, **When** the cardholder
   requests unfreeze, **Then** no state changes, the user receives a safe reason and support path,
   and the denied attempt is audited.
4. **Given** ownership, policy, verification, or propagation cannot be confirmed, **When** unfreeze is
   requested, **Then** the request fails closed, the prior state remains effective, and no success is
   displayed.

### User Story 3 - Configure Spending Limits (Priority: P1)

A cardholder reviews issuer policy boundaries and sets per-transaction, daily, and monthly limits in
the card billing currency, with protection against invalid values and concurrent edits.

**Supports**: OBJ-002, OBJ-005, OBJ-006; FR-012–FR-021
**Why this priority**: Limits provide preventive control but can also disrupt legitimate purchases if
applied incorrectly.
**Independent test**: Submit valid, boundary, invalid, stale-version, duplicate, and concurrent limit
changes and compare the effective limit set and audit history.

**Acceptance scenarios**:

1. **Given** valid limits within current issuer policy and
   `per-transaction ≤ daily ≤ monthly`, **When** the cardholder confirms the change, **Then** the
   complete limit set becomes effective atomically and the before/after values are audited.
2. **Given** a negative, zero, over-policy, incorrectly scaled, unsupported-currency, or internally
   inconsistent value, **When** it is submitted, **Then** the entire change is rejected with field-level
   guidance and no partial update.
3. **Given** another accepted change occurred after the cardholder loaded the limits, **When** the stale
   update is submitted, **Then** it is rejected as a conflict, current values are returned, and no
   previously accepted value is overwritten.
4. **Given** policy requires step-up verification for a limit increase, **When** verification is absent
   or expired, **Then** no limit changes and the user is prompted to verify; a lower valid limit may
   proceed only under the explicitly approved policy.
5. **Given** the card is in any frozen state, **When** the cardholder submits valid lower limits,
   **Then** the decrease may apply atomically; **When** any submitted limit is an increase, **Then** the
   complete change is rejected until the card returns to `ACTIVE` and applicable checks pass.

### User Story 4 - Review Card Transactions (Priority: P1)

A cardholder reviews recent pending, posted, declined, reversed, and refunded activity for an owned
card in a stable order, with understandable amounts and statuses.

**Supports**: OBJ-003, OBJ-006; FR-022–FR-030
**Why this priority**: Transaction visibility lets users detect suspicious activity and confirm the
effect of card controls.
**Independent test**: Load synthetic mixed-status transactions with tied timestamps, multiple
currencies, reversals, and more than one page, then verify visibility, ordering, masking, and paging.

**Acceptance scenarios**:

1. **Given** transactions exist, **When** the cardholder opens the history, **Then** the newest activity
   appears first with deterministic tie-breaking, correct signed amount/currency/status, masked card
   identity, and no prohibited data.
2. **Given** more results exist than the page size, **When** the next page is requested, **Then** stable
   continuation returns no duplicate or skipped records despite newly arriving transactions.
3. **Given** no transactions match the selected period or status, **When** history is viewed, **Then**
   an explicit empty state is shown and no error is implied.
4. **Given** data is temporarily stale or unavailable, **When** history is viewed, **Then** freshness or
   failure is disclosed and the system does not fabricate an empty state.

### User Story 5 - Perform Internal Oversight (Priority: P2)

An authorized operations analyst investigates a support or risk case and may place an emergency
freeze; a compliance reviewer independently examines sanitized, immutable evidence.

**Supports**: OBJ-004, OBJ-005; FR-031–FR-041
**Why this priority**: Internal oversight is required for regulated operations but does not replace the
cardholder's primary self-service controls.
**Independent test**: Run the same case with operations, compliance, expired-role, wrong-case, and
cardholder actors; compare permitted fields/actions and privileged-access audit records.

**Acceptance scenarios**:

1. **Given** an operations analyst has an active role and assigned case, **When** they inspect the card,
   **Then** only sanitized case-relevant data is visible and the privileged read is audited.
2. **Given** urgent risk and a valid case reason, **When** operations places an emergency freeze,
   **Then** acceptance occurs only after durable local blocking and `OPS_FREEZE` are effective; external
   propagation is final or truthfully pending, the cardholder cannot remove it, and actor/case/reason/
   before/after/result are audited.
3. **Given** a compliance reviewer has an assigned investigation, **When** they inspect or export
   evidence, **Then** the view/export is read-only, minimized, access-controlled, watermarked or
   attributable, and audited.
4. **Given** an actor lacks the required role, case, or business purpose, **When** privileged access is
   attempted, **Then** access is denied without disclosing target existence and the attempt is audited.
5. **Given** operations freeze external propagation is delayed or fails, **When** durable local blocking
   is effective, **Then** the analyst sees `PENDING_PROPAGATION`, reconciliation retries, operations is
   alerted by 60 seconds, and unresolved propagation escalates by 15 minutes without weakening the
   local restriction.

## Requirements *(mandatory)*

### Functional Requirements

#### Card Status Controls

Card status is a composite, not one mutually exclusive value:

- **Lifecycle** is `OPEN` or `TERMINATED`.
- **Restriction flags** are independently sourced: `USER_FREEZE`, `OPS_FREEZE`, and
  `RISK_RESTRICTION`; more than one MAY exist simultaneously.
- **Effective status precedence** is `TERMINATED` > `RISK_RESTRICTED` > `OPS_FROZEN` >
  `USER_FROZEN` > `ACTIVE`. `ACTIVE` means lifecycle `OPEN` with no restriction flag.
- Removing one restriction MUST NOT remove or weaken another source's restriction. Cardholder
  unfreeze removes only `USER_FREEZE`; it yields `ACTIVE` only when no stronger restriction remains.

| Actor/action | Required composite state | Allowed change | Effective result |
|--------------|--------------------------|----------------|------------------|
| Cardholder freeze | `OPEN`; ownership confirmed | Add `USER_FREEZE` if absent | Effective status follows precedence; never weaker |
| Cardholder unfreeze | `OPEN`; `USER_FREEZE` present; step-up current | Remove only `USER_FREEZE` | `ACTIVE` only if no operations/risk flag remains |
| Operations emergency freeze | `OPEN`; active role/case/reason | Add `OPS_FREEZE` if absent | `OPS_FROZEN` unless risk restriction is stronger |
| Any actor attempting to remove operations, risk, lifecycle, or unknown restriction through this feature | Any composite state | Removal/override of those restrictions prohibited; cardholder may still remove only `USER_FREEZE` under its own row | Operations/risk/lifecycle/unknown restrictions remain |

- **FR-001**: The system MUST authorize card ownership immediately before accepting a cardholder
  freeze command.
- **FR-002**: The system MUST allow an owned `OPEN` card to add `USER_FREEZE` after explicit
  confirmation, without removing any operations or risk restriction.
- **FR-003**: A freeze MUST NOT be accepted until its restriction and durable local authorization block
  are effective as one safety boundary. After acceptance, no new local authorization MAY be approved
  under the prior unrestricted state. External propagation MUST be tracked separately, and the result
  MUST NOT claim to cancel transactions already authorized before freeze.
- **FR-004**: A repeated freeze when `USER_FREEZE` is already present MUST return the current composite
  and effective status without creating another transition.
- **FR-005**: Every freeze attempt MUST produce an attributable result record with correlation and
  propagation status.
- **FR-006**: User and operations freeze recovery MUST preserve the durable local restriction and
  safest known effective state while external propagation is unavailable.
- **FR-007**: Cardholder unfreeze MUST require ownership, lifecycle `OPEN`, and an existing
  `USER_FREEZE`, and MUST remove only that user-owned restriction flag.
- **FR-008**: Cardholder unfreeze MUST NOT remove or override `OPS_FREEZE`, `RISK_RESTRICTION`,
  `TERMINATED`, or any unknown restrictive state. If another restriction remains, the truthful
  effective status MUST remain restricted rather than becoming `ACTIVE`.
- **FR-009**: The system MUST require a current successful step-up verification for every cardholder
  unfreeze attempt; a normal authenticated session alone is insufficient.
- **FR-010**: Unfreeze MUST fail closed if authorization, policy, verification, or downstream
  propagation cannot be confirmed.
- **FR-011**: The cardholder MUST receive the effective state, safe reason category, and appropriate
  next action after an unfreeze attempt.

Every status and limit command MUST carry an expected state/limit version and a command identity
bound to the authenticated actor ID and role, target card, action, and normalized payload:

- the first distinct command durably accepted for an expected version wins and increments the
  relevant version;
- later distinct commands against that version return `CONFLICT` plus the current sanitized state and
  version and MUST NOT change state;
- retrying the same bound identity returns the stored original outcome;
- reusing an identity with a different actor, target, action, or normalized payload returns
  `IDEMPOTENCY_MISMATCH`, changes no state, and is audited as a security-relevant denial.

| Result category | Terminal? | Trigger/effective state | User or analyst meaning | Retry rule |
|-----------------|-----------|-------------------------|-------------------------|------------|
| `SUCCEEDED` | Yes | Requested change and required local safety state are durable | Final effective state shown | Same identity returns original |
| `PENDING_PROPAGATION` | No | Freeze is locally effective; external confirmation is outstanding | Card is locally frozen; external confirmation pending | Automatic reconciliation; user retry returns same command |
| `DENIED` | Yes | Authorization, ownership, role, case, policy, or verification fails | Safe denial and next action; no state change | Retry only after precondition changes |
| `VALIDATION_ERROR` | Yes | Input violates an explicit rule | Field/reason category; no state change | Corrected intent needs a new identity |
| `CONFLICT` | Yes | Expected version is stale | Current sanitized state/version; no state change | Reload and submit a new command identity |
| `IDEMPOTENCY_MISMATCH` | Yes | Identity binding differs | Generic invalid-request result; no target detail | Never retry that mismatched binding |
| `TEMPORARILY_UNAVAILABLE` | Yes | Non-freeze dependency outcome is unknown/unavailable | No success claim and no state change | New attempt after recovery uses a new identity |

`PENDING_PROPAGATION` is permitted only for a freeze whose local blocking invariant already holds.
Unfreeze, limit increase, and any ambiguous non-freeze write MUST return
`TEMPORARILY_UNAVAILABLE` and fail closed.

#### Spending Limits

Limit accounting uses the issuer's configured billing timezone and calendar:

- a daily period is local `00:00` inclusive to the next local `00:00` exclusive; a monthly period is
  local midnight on calendar day 1 to the next month's day 1. These timezone rules, not a fixed
  24-hour duration, govern DST boundaries;
- an approved authorization hold consumes per-transaction, daily, and monthly allowance in billing
  currency; a decline consumes none;
- incremental authorization adjusts the existing hold; posting replaces the hold with the final
  posted billing amount without double counting;
- full or partial authorization reversal releases the matching held allowance. A later refund is a
  separate related credit and does not replenish historical daily/monthly spend allowance;
- when original and billing currencies differ, the processor's authorization-time billing amount/rate
  governs the authorization decision. A later posting adjustment changes consumed allowance to the
  final billing amount but never retroactively approves or declines the original transaction;
- if final posting or a limit decrease leaves consumed allowance at or above the limit, remaining
  allowance is zero and new authorizations are blocked until consumption falls within a new period or
  an allowed limit increase; previously authorized transactions remain valid.

- **FR-012**: The system MUST present the current per-transaction, daily, and monthly limits together
  with current issuer minimums and maximums before a change is confirmed.
- **FR-013**: All submitted limits MUST use the card billing currency and an exact currency scale; no
  binary floating-point interpretation is permitted.
- **FR-014**: A limit set MUST satisfy issuer ranges and `per-transaction ≤ daily ≤ monthly`.
- **FR-015**: The three-limit set MUST be validated and changed atomically; partial acceptance is
  prohibited.
- **FR-016**: A lower valid limit set MAY be accepted while the card is frozen, MUST affect new
  authorization decisions within the stated consistency target, and MUST NOT retroactively alter an
  already authorized transaction.
- **FR-017**: Any limit increase MUST be rejected while the card is not `ACTIVE`. Once active, an
  increase MUST follow current risk policy and MUST require step-up verification when policy demands
  it.
- **FR-018**: Each change MUST include the version of the limit set the cardholder reviewed; only the
  first distinct command durably accepted for that version MAY change it. Every later distinct command
  for that version MUST return `CONFLICT` without overwriting current values.
- **FR-019**: Retrying the same fully bound command identity MUST return the original result and MUST
  NOT apply a second change; mismatched identity reuse MUST return `IDEMPOTENCY_MISMATCH`.
- **FR-020**: Concurrent distinct commands MUST follow the normative expected-version winner rule,
  and every rejected conflict MUST return the current sanitized effective values and version.
- **FR-021**: Every attempted limit change MUST record sanitized before/after values, actor, policy
  decision, verification outcome category, correlation, and result.

#### Transaction History

A transaction has one immutable transaction ID and authorization/occurrence instant. Posting,
decline, and full/partial reversal are timestamped status events on that identity. A refund is a new
credit transaction with its own identity linked to the original transaction. History sorts by
`authorization_or_occurrence_instant DESC, transaction_id DESC`; status updates do not move the
original transaction in that ordering. Each item shows the occurrence instant, latest status-event
instant, and a history `as of` instant so freshness is an objectively measurable age.

- **FR-022**: A cardholder MUST see only transactions belonging to an owned card.
- **FR-023**: History MUST distinguish pending, posted, declined, and reversed transaction states,
  represent refunds as linked credit transactions, and show freshness as an `as of` instant.
- **FR-024**: Each item MUST show a safe merchant label, occurrence time and latest status-event time
  with timezone, signed billing amount/currency, original amount/currency when different, status, and
  masked card identity.
- **FR-025**: Transaction history MUST comply with the canonical surface taxonomy: only its allowed
  minimum fields MAY appear and every listed prohibited category MUST be absent.
- **FR-026**: Results MUST use the normative occurrence-instant and immutable-identifier sort key;
  later status updates MUST NOT reorder the original transaction.
- **FR-027**: Pagination MUST use a stable continuation position, default to 50 items, and allow no more
  than 100 items per page.
- **FR-028**: The cardholder MUST be able to constrain history by an allowed date range and transaction
  status without exposing query details about other cards.
- **FR-029**: An empty result is valid only when the transaction source is healthy and the requested
  range is completely evaluated. A result is `STALE` when its trusted source `as of` instant is older
  than 60 seconds but no older than 15 minutes or source health is degraded; it MUST show that instant.
  With no trusted snapshot or age over 15 minutes, the result is `UNAVAILABLE`, not empty or stale.
- **FR-030**: A transaction authorized before freeze MAY later post or reverse, and a related refund
  MAY appear. Status events MUST preserve the original identity/history; a refund MUST use a distinct
  linked identity.

#### Operations, Compliance, and Audit

| Role | Search/read | Freeze | Change limits | Release ops/risk restriction | Export |
|------|-------------|--------|---------------|------------------------------|--------|
| Cardholder | Owned card only | Add/remove own user freeze | Owned card per policy | Never | No internal export |
| Operations | Assigned open operations case and enumerated purpose only | Add operations freeze with case/reason | Never | Never in this feature | Never |
| Compliance | Assigned open compliance case and enumerated purpose only | Never | Never | Never | Assigned case only, after step-up, maximum 10,000 sanitized records |

An internal case authorization is valid only when its issuer is the existing case-management authority,
status is open, assignment includes the current actor, purpose is one of the enumerated role purposes,
and expiry is in the future. No "equivalent" unenumerated authorization is accepted by this feature.

- **FR-031**: Internal access MUST require an active least-privilege role and a valid assigned open case
  with the enumerated purpose for that role; an unenumerated or self-asserted business purpose MUST be
  denied.
- **FR-032**: Operations and compliance permissions MUST be distinct and MUST be re-evaluated for each
  privileged action or read.
- **FR-033**: Operations MAY add `OPS_FREEZE` only with a valid assigned open case, current issuer risk
  policy version, and one enumerated reason: `CUSTOMER_REPORTED_COMPROMISE`,
  `SUSPECTED_ACCOUNT_TAKEOVER`, `FRAUD_MONITORING_ESCALATION`, or `PROCESSOR_SECURITY_INCIDENT`.
  Free-form/`OTHER` reasons MUST be denied. Acceptance, external propagation, pending truthfulness,
  recovery, and escalation MUST satisfy the same durable local blocking invariant as a cardholder
  freeze.
- **FR-034**: No actor MAY release an operations/risk restriction through this feature. Release MUST
  occur through a separate authorized risk/case workflow; operations also MUST NOT change cardholder
  limits through this feature.
- **FR-035**: Compliance access MUST be read-only and limited to sanitized evidence needed for the
  assigned investigation. Export additionally requires current step-up verification.
- **FR-036**: Only compliance MAY export through this feature. Each export MUST be bound to one assigned
  open case and approved purpose, contain at most 10,000 explicitly allowed sanitized records, be
  attributable/watermarked, expire after 24 hours, and remain access-controlled under retention and
  hold policy. Operations export and cross-case export MUST be denied.
- **FR-037**: Every successful or denied privileged read, search, action, and export MUST be audited.
- **FR-038**: Business audit records MUST be append-only and tamper-evident and MUST retain original
  event meaning when corrections or reconciliations occur.
- **FR-039**: Audit records MUST include event time, actor/role, subject opaque identifier, action,
  sanitized before/after state when relevant, reason/case, correlation, policy outcome, and result.
- **FR-040**: Business audit, diagnostic logs/alerts, exports, dependency failures, fixtures, prompts,
  and documents MUST each comply with the canonical surface taxonomy and its allowed exceptions.
- **FR-041**: The system MUST reconcile accepted control commands with effective card state and MUST
  surface unresolved mismatches to operations within the recovery target.

Internal search abuse controls are assumed policy targets for this homework: more than 20 distinct
card subjects queried by one operations actor in a rolling five-minute window MUST deny subsequent
searches for 15 minutes and alert security operations. Compliance exports above 10,000 records or
outside one assigned case MUST be denied and alerted. Approved bulk investigations require separate
bulk tooling outside this feature rather than bypassing these controls.

The following taxonomy is canonical; surface requirements MUST reference it rather than inventing a
weaker prohibited-data list:

| Surface | Allowed minimum data | Always prohibited |
|---------|----------------------|-------------------|
| Cardholder view | Owned opaque card/transaction IDs, masked card identity, safe merchant label, exact amounts/currencies, status/times, limits | Full PAN, CVV, credentials, verification material, other-customer data, raw dependency payloads, unredacted free-form personal data |
| Operations view | Case ID, opaque customer/card/transaction IDs, masked identity, sanitized state/limit/history and reason codes | Compliance-only evidence, full PAN/CVV, credentials/verification material, raw payloads, free-form personal data not required by the case |
| Compliance view/export | Case ID, opaque subject/actor IDs, sanitized transaction/control/audit fields explicitly listed by the case export policy | Full PAN/CVV, credentials/verification material, raw payloads, unrelated-case records, unrestricted free text |
| Business audit | Opaque actor/subject IDs, role, action, enumerated reason, sanitized before/after, policy/result, time, correlation | Full PAN/CVV, credentials/verification material, raw payloads, authentication responses, unredacted free text |
| Diagnostic logs/alerts | Correlation/event IDs, service/result/error category, timing, sanitized component metadata | Raw business payloads, full PAN/CVV, credentials/verification material, personal/merchant free text |
| Fixtures, prompts, and documents | Clearly synthetic opaque IDs, masked card identity, fictional safe labels and exact test amounts | Any production/personal data, realistic secrets, full PAN/CVV, raw captured payloads |

A business audit intent with globally unique event identity and correlation MUST be durably recorded in
the same acceptance boundary as each state change or privileged access outcome. Delivery/replay MUST
be idempotent on that event identity. If queryable audit evidence is absent after five seconds,
security/compliance operations owns the alert; automated recovery MUST complete within five minutes.
At 15 minutes unresolved absence becomes a security/control incident. Until reconciled, degraded-safe
mode MUST reject unfreeze, limit increases, privileged exports, and other risk-increasing writes while
still permitting durable local freezes and authorized reads whose audit intent can be recorded.

### Policy and Non-Functional Requirements

All numerical service targets below are **assumed targets for this homework**, not observed production
SLIs or legal mandates. They are chosen to make safety and user experience objectively reviewable and
MUST be validated against real issuer, processor, traffic, and regulatory context before production.

Unless a target states otherwise, latency is measured from durable authenticated command/read receipt
to the truthful response category, over a calendar month, separately for healthy and degraded
dependencies. Percentiles require at least 1,000 eligible samples; below that threshold every sample
and the maximum are reported without claiming a percentile. Availability is
`service-successful requests / service-eligible valid requests`. The numerator contains successful
reads, `SUCCEEDED` writes, and locally safe freeze `PENDING_PROPAGATION` outcomes. Invalid-business
outcomes (`DENIED`, `VALIDATION_ERROR`, `CONFLICT`, `IDEMPOTENCY_MISMATCH`), malformed/unauthorized
requests, and approved maintenance are excluded from both numerator and denominator and measured
separately. `TEMPORARILY_UNAVAILABLE`, internal errors/timeouts, and dependency failures remain in the
denominator and not the numerator. All clocks use an unambiguous instant.

| ID | Area | Requirement/target | Measurement or evidence | Assumption rationale |
|----|------|--------------------|-------------------------|----------------------|
| NFR-001 | Authorization and abuse boundary | 100% of sensitive commands/privileged reads have current ownership or valid role/case/purpose evidence; operations search beyond 20 distinct subjects/five minutes and compliance export beyond one case/10,000 records are deterministically denied and alerted | Full negative authorization matrix, threshold boundaries, and audit reconciliation | Any silent cross-customer, role, or bulk-access bypass is unacceptable |
| NFR-002 | Sensitive data | 0 occurrences of any surface-prohibited category from the canonical taxonomy across views, audit, logs, alerts, exports, dependency failures, fixtures, prompts, and documents | Automated pattern/category scan plus manual allowed-field review per surface | One measurable taxonomy prevents a weaker surface-specific privacy oracle |
| NFR-003 | Audit completeness | 100% of accepted/denied control attempts and privileged outcomes reconcile to one attributable business audit event identity; evidence is queryable within 5 seconds at p95, recovered within 5 minutes, or escalated as an incident at 15 minutes | Synthetic outcome-to-event reconciliation including duplicate replay and missing-sink recovery | Regulated operations require prompt, complete, duplicate-safe evidence |
| NFR-004 | Freeze safety | Hard invariant: no user or operations freeze is accepted before durable local authorization blocking is effective; external propagation is confirmed within 5 seconds at p95 and unresolved propagation alerts operations by 60 seconds | Controlled local-boundary, dependency, propagation, and recovery scenarios for both freeze sources | Freeze is an urgent loss-prevention action; a percentile cannot permit an unsafe accepted tail |
| NFR-005 | Unfreeze/limits consistency | Successful unfreeze and limit changes become observable and effective for new decisions within 5 seconds at p95; ambiguous results never display success | Read-after-write and decision-point probes | Balances interactive UX with distributed propagation |
| NFR-006 | Interactive latency | Final status for 95% of control commands appears within 2 seconds when dependencies are healthy; transaction first page appears within 2 seconds at p95 | Synthetic journey timing | Two seconds is an assumed responsive mobile/web threshold |
| NFR-007 | Reliability | Calendar-month availability target is 99.9% under the strict service-success numerator/eligible-valid denominator; `TEMPORARILY_UNAVAILABLE`, internal/dependency error, and timeout outcomes count as unavailable; unsafe unfreeze or limit increase is never substituted for availability | Classified SLI ledger plus failure-injection review with explicit numerator/denominator examples | Safety takes precedence over optimistic or fail-closed-as-success accounting |
| NFR-008 | Idempotency | For 24 hours, the same fully bound command identity produces one business transition and original outcome; mismatched reuse produces 0 transitions and `IDEMPOTENCY_MISMATCH` | Duplicate and mismatched-binding reconciliation | Covers client/network retries and detects unsafe identity reuse |
| NFR-009 | Concurrency | For at least 20 concurrent distinct commands sharing one expected version, exactly one may win, all others conflict, and no accepted update is lost | Concurrent command fixture and final-state/version/audit reconciliation | Assumed stress level for pathological retries and automation |
| NFR-010 | Transaction scale | Stable paging supports at least 24 months of cardholder-visible history and 100,000 synthetic transactions for one card without duplicate/skip defects | Large fixture paging traversal | Covers unusually active cards while bounding initial scope |
| NFR-011 | Recovery | User/operations freeze propagation mismatches are retried and reconciled or escalated within 15 minutes; ambiguous non-freeze outcomes surface within 5 minutes; missing audit evidence recovers within 5 minutes or becomes an incident at 15 minutes | Failure/recovery timeline review with named operations and security/compliance owners | Freeze deserves sustained retry; audit and other writes require explicit safe escalation |
| NFR-012 | Retention | Under the jurisdiction-neutral baseline, business audit evidence is retained for an assumed 7 years and cardholder transaction visibility for an assumed 24 months; actual periods require jurisdiction-specific legal/policy approval and deletion/hold rules | Policy review and retention matrix | Explicit assumptions prevent an invented legal claim from becoming policy |
| NFR-013 | Accessibility and clarity | 100% of critical states can be conveyed without color alone; user messages distinguish final, pending, denied, stale, and unavailable outcomes | Content/accessibility review | Safety controls must not rely on ambiguous visual cues |
| NFR-014 | Time and money | Monetary values preserve exact currency scale; event timestamps use an unambiguous instant and display the user's timezone with DST-safe formatting | Boundary fixtures for currencies, DST, and tied timestamps | Prevents financial rounding and ordering errors |

### Key Entities and Sensitive-Data Classification

| Entity | Purpose | Key attributes (conceptual) | Classification | Retention/access notes |
|--------|---------|-----------------------------|----------------|------------------------|
| Virtual Card | Existing controllable payment instrument | Opaque card ID, masked identity, owner ID, billing currency, lifecycle, restriction flags, state version | Restricted | Owned masked view; case-scoped internal view; lifecycle policy controls retention |
| Card Control State | Composite restrictions and propagation | Lifecycle, source flags, effective status, reason category, version, effective time, propagation status | Confidential | Owned cardholder and case-scoped role views; history preserved through audit events |
| Spending Limit Set | Current issuer/cardholder controls | Per-transaction, daily, monthly exact amounts, currency, period policy, consumed allowance, version, policy bounds | Confidential | Owned cardholder and case-scoped operations view; only cardholder changes |
| Transaction | Immutable payment identity plus status events | Opaque transaction ID, occurrence/status times, amounts/currencies, safe merchant label, status, relation ID | Restricted | Owned/cardholder or case-scoped access; assumed 24-month cardholder visibility |
| Control Command | Deduplicated requested action | Bound command ID, actor/role, target, normalized intent, expected version, result, correlation | Confidential | Actor sees own result; case-scoped control reviewers; minimum 24-hour deduplication then policy retention/deletion |
| Audit Event | Attributable evidence | Event ID, actor/role, subject ID, action, sanitized before/after, case/reason, policy/result, times, correlation | Restricted | Compliance/control readers with assigned case; append-only; assumed seven years subject to hold/deletion policy |
| Internal Case | Bounds privileged access | Opaque case ID, enumerated purpose, assignment, status, expiry | Restricted | Assigned internal actor/control functions only; expires on closure/expiry under case policy |

| Entity | Cardholder | Operations | Compliance | Service/control functions | Retention/disposition owner |
|--------|------------|------------|------------|---------------------------|-----------------------------|
| Virtual Card / Control State | Owned masked view and own allowed commands | Assigned case read; emergency freeze | Assigned case read-only | Authorization/risk decisions using minimum fields | Issuer card-lifecycle policy owner |
| Spending Limit Set | Owned view/change | Assigned case read-only | Assigned case read-only when evidence requires | Authorization/risk evaluation | Issuer financial-control policy owner |
| Transaction | Owned history | Assigned operations case read-only | Assigned case read/export allowed fields | Ledger/reconciliation processing | Ledger/retention policy owner; legal holds override ordinary deletion |
| Control Command | Own sanitized outcome | Assigned case/control review | Assigned investigation evidence | Idempotency and reconciliation | Control owner; at least 24-hour deduplication, then approved deletion/retention schedule |
| Audit Event | No raw internal audit access through this feature | Assigned case minimum read | Assigned case read/export | Security/compliance monitoring and reconciliation | Compliance records owner; assumed seven years, hold-aware deletion after expiry |
| Internal Case | No access | Own assigned operations case | Own assigned compliance case | Case authority and access control | Case-management owner; access ends immediately on close/expiry |

## Edge Cases and Failure Modes *(mandatory)*

| ID | Condition/failure | Expected user-visible behavior | Audit/ops/compliance outcome | Related requirements |
|----|-------------------|--------------------------------|------------------------------|----------------------|
| EC-001 | Cardholder has no eligible virtual cards | Explicit empty state and eligibility/support guidance | No sensitive target data; ordinary read trace only | FR-001, FR-022 |
| EC-002 | Duplicate freeze/unfreeze/limit command | Original result returned; no confusing second transition | One business outcome linked to all delivery attempts | FR-004, FR-019, NFR-008 |
| EC-003 | Two distinct status/limit commands use the same expected version concurrently | First durably accepted command wins and increments version; all others receive `CONFLICT` with current sanitized state/version | Every attempt has a distinct correlated result; no accepted update is lost | FR-005, FR-018–FR-020, NFR-009 |
| EC-004 | Any actor tries to release an operations/risk/terminated restriction through this feature | No change; cardholder receives a safe reason/support path and internal users are directed to the separate risk/case workflow | Denied attempt audited; no internal risk details leaked | FR-008, FR-011, FR-034 |
| EC-005 | User or operations freeze is locally effective but processor confirmation is delayed | `Frozen—external confirmation pending`; no success claim about external propagation | Retry/reconcile; operations alert at 60 seconds and escalation at 15 minutes | FR-003, FR-006, FR-033, NFR-004, NFR-011 |
| EC-006 | Unfreeze or limit increase dependency times out | `TEMPORARILY_UNAVAILABLE`; no state change and never a success/pending claim | Failed-closed result and sanitized dependency category audited | FR-010, FR-017, NFR-007 |
| EC-007 | Limits are zero, negative, over policy, wrong scale/currency, or inconsistent | Entire set rejected with field-level correction; old limits remain | Validation category audited; never log unsafe raw input | FR-013–FR-015 |
| EC-008 | Policy bounds changed after screen load | Stale request rejected; current bounds and values shown | Policy/version conflict recorded | FR-012, FR-018 |
| EC-009 | Limit decrease or final posting leaves consumed allowance at/above the limit | Remaining allowance becomes zero; new authorizations are blocked until a permitted reset/increase; accepted past transactions remain unchanged | Limit/accounting change and derived effect are attributable | FR-014, FR-016 |
| EC-010 | Step-up verification expires during confirmation | No high-risk change; user asked to verify again | Expired outcome category audited, not the secret/challenge response | FR-009, FR-017, FR-040 |
| EC-011 | New transactions arrive while paging | Current continuation remains stable with no duplicate/skip; refresh starts a new snapshot | Paging defect fixture retained as evidence | FR-026, FR-027, NFR-010 |
| EC-012 | Same-time transactions, billing-period DST shift, or display-timezone change | Normative sort remains deterministic; period boundaries use issuer billing timezone; display includes offset/timezone | Original occurrence/status instants and period assignment remain unchanged | FR-024, FR-026, NFR-014 |
| EC-013 | Pending transaction posts/reverses or later receives a refund | Status-event time and `as of` freshness update; refund appears as a distinct linked credit without rewriting original identity/order | Evolution remains reconcilable | FR-023, FR-026, FR-030 |
| EC-014 | Transaction source is healthy/complete, degraded with a ≤15-minute trusted snapshot, or lacks a trusted snapshot/has one >15 minutes | Respectively show empty/fresh data, `STALE` with exact `as of`, or `UNAVAILABLE`; never substitute one category for another | Availability/freshness outcome measured without customer data | FR-029, NFR-006–NFR-007 |
| EC-015 | Card ownership changes or session is stale | Re-authorization denies access/action; cached target details are not reused | Denial audited where security-relevant | FR-001, FR-022, NFR-001 |
| EC-016 | Internal role expires or case closes mid-session | Next privileged read/action is denied without target disclosure | Denied privileged attempt audited and session access revoked | FR-031, FR-032, FR-037 |
| EC-017 | Operations submits emergency freeze without valid case/reason | No state change and clear internal validation guidance | Denied attempt recorded for oversight | FR-033, FR-037 |
| EC-018 | Operations exceeds 20 distinct card subjects in five minutes, or compliance export exceeds one case/10,000 records | Deterministic denial; operations search is blocked 15 minutes; oversized/cross-case export is rejected | Security operations alerted with actor/case/correlation and no prohibited data | FR-031, FR-036, FR-037, NFR-001 |
| EC-019 | Audit sink is delayed after a durable audit intent | Truthful command result remains; degraded-safe mode blocks risk-increasing writes/exports if evidence stays missing | Alert owner at 5 seconds, duplicate-safe recovery by 5 minutes, security/control incident at 15 minutes | FR-038–FR-041, NFR-003, NFR-011 |
| EC-020 | Audit correction or late reconciliation is required | No cardholder-visible history is silently rewritten | New corrective event references the original; original remains intact | FR-038, FR-041 |
| EC-021 | Limit change on a frozen card mixes decreases and an increase | Entire set is rejected; current values remain and the user is told activation plus applicable verification is required for an increase | Rejection category and card state are audited without verification secrets | FR-015–FR-017 |
| EC-022 | A transaction was authorized before freeze and settles afterward | History shows its truthful posted/reversed/refunded evolution and explains that freeze blocks new authorizations only | Authorization time and later status remain reconcilable; no false freeze-bypass incident is created solely from settlement | FR-003, FR-023, FR-030 |
| EC-023 | Card has both user and operations/risk restrictions when cardholder unfreezes | Only `USER_FREEZE` is removed after step-up; effective state remains restricted and is shown truthfully | Before/after composite flags, effective status, actor, and result are audited | FR-007–FR-011 |
| EC-024 | Same command identity is reused with different actor, card, action, or normalized payload | `IDEMPOTENCY_MISMATCH`; no state or target detail is exposed | Security-relevant denial linked to identity/correlation is audited | FR-019, NFR-008 |
| EC-025 | Daily/monthly period resets across DST or month boundary | Allowance moves to the new issuer-billing-timezone period exactly once at local boundary; no duplicated/skipped period | Old/new period IDs, boundary instant, consumed allowance, and decision reconcile | FR-014, NFR-014 |
| EC-026 | Foreign-currency hold posts at a different final billing amount | Authorization uses authorization-time billing amount/rate; posting replaces hold consumption with final billing amount without retroactive authorization reversal; remaining allowance may become zero | Original/final billing amounts, rate timestamps, adjustment, and result remain attributable | FR-013–FR-016, NFR-014 |

## Implementation Notes and Guardrails

These are constraints for a hypothetical future implementation, not implementation work for this
homework.

- Treat the external card identifier as opaque. Display only an issuer-approved masked form; never
  expose or log full PAN or CVV.
- Represent money as exact scaled amounts paired with an ISO 4217 currency. Never use binary
  floating-point arithmetic for monetary comparisons.
- Store event time as an unambiguous instant; separately render the actor's timezone and offset.
- Model lifecycle separately from independently sourced restriction flags and derive effective status
  using the normative precedence table; a command removes only its explicitly authorized source flag.
- Enforce the normative command-identity binding and expected-version winner rules for status and limit
  writes throughout the assumed 24-hour retry window.
- Separate command acceptance, effective local safety state, and external propagation status so a
  pending dependency cannot be misrepresented as complete.
- Use only the normative result categories and safe reason subcategories; never return dependency
  internals or confirm the existence of unauthorized resources.
- Keep business audit events distinct from diagnostic logs. Audit events are append-only and
  reconcilable; diagnostic logs are sanitized, access-controlled, time-bounded, and never the sole
  evidence of a financial control change.
- Use stable cursor/continuation pagination bound to ordering and filters. Offset-only paging is not
  acceptable where newly arriving transactions could create duplicates or gaps.
- All examples and future test fixtures MUST be synthetic, clearly labeled, and use masked card data.
- No framework, programming language, database, vendor, API shape, or UI design is selected at the
  specification stage.

## Context

### Beginning Context

- The repository contains only the Homework 3 brief, templates, Spec Kit workflow, and approved
  constitution; no Homework 3 application exists.
- A hypothetical issuer already provides authenticated customer identity, card ownership, existing
  virtual cards, authorization processing, transaction records, risk policy, and internal identity/
  case management.
- Exact regulatory jurisdiction, production traffic, issuer policy ranges, and observed service
  levels are not supplied; related targets and retention periods are explicit assumptions.
- The feature begins with an existing card in a known effective state and a versioned current limit
  set; issuance and identity onboarding are outside scope.

### Ending Context

- `homework-3/specification.md` contains the approved canonical layered specification and traceable
  future implementation tasks.
- `homework-3/agents.md` contains future-agent FinTech, verification, and workflow constraints.
- One approved editor/AI rules artifact and `homework-3/README.md` complete the graded package.
- Spec Kit working artifacts contain the approved spec, plan, research/decision records, checklists,
  agent-routed tasks, and consistency analysis.
- No source code, executable API/UI, database, dependency, or deployed service has been created.

## Verification Strategy

| Objective/requirement | Verification category | Fixture/evidence | Pass condition | Reviewer role |
|-----------------------|-----------------------|------------------|----------------|---------------|
| OBJ-001 / FR-001–FR-011 | Composite-state and integration scenario design | Every lifecycle/restriction combination; same-version/mismatched commands; user/operations propagation delays | Each command changes only its owned flag, preserves stronger restrictions, meets local blocking invariant, and has one result/audit outcome | QA agent (Standard), reviewed by FinTech risk agent (Advanced) |
| OBJ-002 / FR-012–FR-021 | Accounting boundary, property, and concurrency scenario design | Currency/scale/rate, daily/monthly/DST resets, holds/posting/reversal/refund, policy bounds, 20 same-version commands | Allowance is exact and deterministic; invalid sets never partially apply; exactly one same-version winner fully reconciles | QA agent (Standard), reviewed by payment-domain agent (Advanced) |
| OBJ-003 / FR-022–FR-030 | Access, paging, and data-quality scenario design | 100,000 synthetic mixed-state/linked transactions, tied occurrence/status times, DST, multi-currency, mid-page arrivals | No prohibited fields, duplicates, gaps, ambiguous amount/time/identity, or false empty state | Data/QA agent (Standard), privacy reviewer (Advanced) |
| OBJ-004 / FR-031–FR-037 / NFR-001 | Authorization matrix and manual compliance review | Role × open/closed/expired case × enumerated purpose × action; rate/export thresholds | Only explicitly allowed cells succeed, deterministic abuse boundaries hold, and all privileged outcomes are audited | Security reviewer (Advanced) independent of author |
| OBJ-005 / FR-038–FR-041 / NFR-002–NFR-003 | Audit reconciliation and taxonomy review | Command/access corpus, delayed sink and duplicate replay, canonical prohibited-data scan per surface | 100% outcome/event coverage, duplicate-safe recovery deadlines, zero prohibited categories, originals preserved | Compliance reviewer (Advanced), scan executed by Economy agent |
| OBJ-006 / NFR-003–NFR-011 | Performance, reliability, and recovery scenario design | Healthy/degraded dependency timelines, duplicate storms, propagation mismatch | Every assumed percentile, availability, concurrency, and recovery target has a measurable probe and safe failure oracle | Reliability reviewer (Standard), risk sign-off (Advanced) |
| NFR-012 | Policy review | Retention matrix with legal/policy owner and hold/deletion cases | Assumptions are clearly labeled and cannot be mistaken for jurisdiction-specific legal advice | Compliance reviewer (Advanced) |
| NFR-013–NFR-014 | Content, accessibility, money/time boundary review | Critical-state copy set, non-color cues, currency/DST fixtures | Messages remain distinguishable and values retain exact meaning | UX/QA reviewer (Standard) |

## Low-Level Task Requirements

The post-plan task list MUST provide many small, implementable future slices covering status controls,
limits, transaction history, internal oversight, audit, safety, verification, performance, and
documentation. Each task MUST trace to objective/requirement IDs and declare agent role, model tier,
tier rationale, exact inputs/output, dependencies, parallel-safety, acceptance criteria, and an
independent reviewer for material work. Homework 3 will document those tasks but MUST NOT execute
implementation tasks.

## Success Criteria *(mandatory)*

- **SC-001**: In scenario review, 100% of eligible cardholders can freeze an active owned card and
  receive a truthful final or pending status only after the durable local blocking invariant holds.
- **SC-002**: Across every composite-state fixture, 0 cardholder unfreeze attempts remove an operations,
  risk, unknown, or lifecycle restriction; only the user-owned flag may be removed.
- **SC-003**: 100% of accepted limit fixtures preserve exact currency meaning, satisfy issuer/order
  and accounting-period/status rules, apply atomically, and yield exactly one winner per expected
  version under the concurrency scenario.
- **SC-004**: Complete traversal of 100,000 synthetic transactions yields 0 unauthorized records,
  prohibited fields, duplicates, or skipped records.
- **SC-005**: The internal authorization matrix permits 100% of explicitly authorized operations and
  denies 100% of wrong-role, wrong-case, expired, and unauthorized operations without target leakage.
- **SC-006**: Audit reconciliation maps 100% of control attempts and privileged accesses to exactly one
  attributable event identity, meets recovery/escalation deadlines, and finds 0 occurrences of any
  surface-prohibited data category.
- **SC-007**: Every high-risk failure mode has a specified safe state, user/analyst message, audit
  implication, recovery owner, and measurable escalation or consistency target.
- **SC-008**: A traceability review maps every objective to requirements, scenarios, verification,
  future tasks, and success criteria with no orphaned in-scope requirement.

## Assumptions, Dependencies, and Out of Scope

### Assumptions

- **A-001**: Virtual cards, cardholder identity, ownership, and authentication already exist.
- **A-002**: The issuer can represent `OPEN`/`TERMINATED` lifecycle separately from independently
  sourced user, operations, and risk restrictions, or can preserve equivalent composite semantics and
  normative precedence without losing source ownership.
- **A-003**: Per-transaction, daily, and monthly limits use the card billing currency and issuer billing
  timezone/calendar; specific ranges and processor conversion rates are policy/data inputs rather than
  hard-coded constants.
- **A-004**: Step-up verification is mandatory for every cardholder unfreeze. Risk policy may also
  require it for limit increases; this feature enforces the outcome but does not define the
  authentication mechanism.
- **A-005**: Performance, volume, availability, consistency, idempotency, recovery, and retention
  numbers are hypothetical targets selected for specification completeness.
- **A-006**: Internal staff access is integrated with the existing identity/case authority and can
  enforce the enumerated role purposes, assignment, open status, expiry, step-up, and rate boundaries.
- **A-007**: The cardholder-facing history covers an assumed 24 months; older evidence may remain
  accessible only through approved internal processes.
- **A-008**: The specification uses a jurisdiction-neutral regulated baseline. It does not claim
  compliance with any named jurisdiction; applicable legal and regulatory requirements must be
  selected and approved before production use.

### Dependencies

- **DEP-001**: Existing card ownership and authentication authority.
- **DEP-002**: Authorization processor/card-control propagation capability.
- **DEP-003**: Issuer limit policy and fraud/risk decisions.
- **DEP-004**: Transaction ledger or processor history with stable immutable identities.
- **DEP-005**: Internal identity, case management, audit storage, monitoring, and alert ownership.
- **DEP-006**: Compliance/legal approval of jurisdiction-specific access and retention policy.

### Out of Scope

- Card issuance, card details reveal, activation, termination, replacement, wallet provisioning, PIN,
  physical cards, disputes/chargebacks, refunds initiation, transfers, and payments initiation.
- Release or adjudication of an operations/risk restriction; that action belongs to a separate
  authorized risk/case workflow with its own approval and audit requirements.
- Defining fraud models, processor internals, customer onboarding/KYC, staff provisioning, or legal
  conclusions for a specific jurisdiction.
- Actual source code, APIs, UI, executable prototypes, scaffolding, database migrations, dependencies,
  production configuration, or deployment for Homework 3.

## Traceability Summary

| Objective | Requirements | Stories/edge cases | Success criteria | Verification | Tasks |
|-----------|--------------|--------------------|------------------|--------------|-------|
| OBJ-001 | FR-001–FR-011; NFR-004–NFR-009 | US1, US2; EC-002–EC-006, EC-010, EC-015, EC-023–EC-024 | SC-001, SC-002 | Composite-state, command-result, and propagation scenarios | Assigned after Gate 2 |
| OBJ-002 | FR-012–FR-021; NFR-008–NFR-009, NFR-014 | US3; EC-002–EC-003, EC-007–EC-010, EC-021, EC-024–EC-026 | SC-003 | Accounting boundary/property/concurrency scenarios | Assigned after Gate 2 |
| OBJ-003 | FR-022–FR-030; NFR-002, NFR-010, NFR-014 | US4; EC-011–EC-015, EC-022 | SC-004 | Access/paging/data-quality/privacy scenarios | Assigned after Gate 2 |
| OBJ-004 | FR-031–FR-037; NFR-001–NFR-002 | US5; EC-005, EC-016–EC-018 | SC-005 | Role/case/purpose matrix and manual review | Assigned after Gate 2 |
| OBJ-005 | FR-005, FR-021, FR-037–FR-041; NFR-002–NFR-003, NFR-011–NFR-012 | All stories; EC-002–EC-026 | SC-006 | Audit recovery/reconciliation/taxonomy review | Assigned after Gate 2 |
| OBJ-006 | FR-003, FR-006, FR-010, FR-016, FR-018–FR-020, FR-027–FR-030, FR-033, FR-041; NFR-003–NFR-014 | All stories; EC-002–EC-026 | SC-001, SC-003, SC-004, SC-007 | Performance/reliability/recovery and boundary scenarios | Assigned after Gate 2 |

## Open Questions

No unresolved question blocks the draft. Product, policy, retention, and service-level choices not
provided by the assignment are explicitly recorded as assumptions and remain subject to Gate 1
review.
