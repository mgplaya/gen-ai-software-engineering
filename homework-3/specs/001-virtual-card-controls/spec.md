# Feature Specification: Regulated Virtual Card Controls

**Feature Branch**: `001-virtual-card-controls`

**Created**: 2026-07-15

**Status**: Draft (spec-quality gate passed; clarifications resolved)

**Input**: User description: "Virtual card lifecycle controls for a regulated FinTech issuer:
cardholder freeze/unfreeze, per-transaction/daily/monthly spending limits, transaction history, and
an internal ops/compliance view — auditable, secure, with clear boundaries for sensitive data."

## Overview

Cardholders need direct, trustworthy control over their virtual cards, and the issuer needs an
auditable, least-privilege internal view for operations and compliance. This feature specifies four
capability areas — **freeze/unfreeze**, **spending limits**, **transaction history**, and
**internal oversight** — under the rules of the project [Constitution](../../.specify/memory/constitution.md)
(fail-closed on risk, exact money/time, idempotent versioned writes, least privilege, append-only
audit, sensitive-data boundary).

Objective IDs referenced by requirements:

- **OBJ-1** — Cardholders can instantly and safely freeze a card and see it reflected everywhere.
- **OBJ-2** — Unfreeze is fail-closed: it only succeeds when it is provably safe.
- **OBJ-3** — Per-transaction, daily, and monthly limits are enforced atomically and exactly.
- **OBJ-4** — Transaction history is stable, complete, and authorization-bound under concurrency.
- **OBJ-5** — Internal access is least-privilege, case-scoped, purpose-bound, and time-boxed.
- **OBJ-6** — Every significant action is captured as append-only, tamper-evident, sanitized audit
  evidence with defined recovery.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Cardholder freezes a card (Priority: P1)

A cardholder who suspects their card is compromised freezes it from the app and immediately sees the
card as frozen; no new authorizations succeed once the freeze is durably recorded.

**Why this priority**: Freeze is the single highest-value safety action and the MVP. It is
risk-*reducing*, so it can be accepted the moment a durable local block exists (Constitution I),
making it independently shippable.

**Independent Test**: Freeze a synthetic active card; confirm the card state reads `frozen`,
subsequent authorization attempts are declined by the local block, and an audit event is written —
without any other story implemented.

**Acceptance Scenarios**:

1. **Given** an active card owned by the cardholder, **When** they freeze it, **Then** the card
   state becomes `frozen`, the response confirms success, and an append-only audit event records
   actor, card token, action, and time.
2. **Given** a card whose freeze is durably recorded locally but not yet confirmed downstream,
   **When** the cardholder views the card, **Then** it shows `frozen` with downstream propagation
   `pending` — the block is already effective locally.
3. **Given** a freeze command that is retried with the same idempotency key, **When** it is
   received again, **Then** the original outcome is returned and no duplicate audit event is
   created.

---

### User Story 2 - Cardholder unfreezes a card, fail-closed (Priority: P2)

A cardholder unfreezes a previously frozen card. The unfreeze only succeeds when the system can
positively confirm it is safe and authorized; otherwise it is denied (never "maybe").

**Why this priority**: Unfreeze restores spending ability (risk-*increasing*) and must be
fail-closed (Constitution I). It depends conceptually on freeze but is independently testable.

**Independent Test**: Attempt to unfreeze a synthetic card under (a) confirmed-safe and (b)
ambiguous conditions; confirm success only in (a), explicit denial in (b), each audited.

**Acceptance Scenarios**:

1. **Given** a card frozen by the cardholder with no stronger restriction present and fresh step-up
   authentication, **When** they unfreeze it, **Then** the card becomes `active` and the event is
   audited.
2. **Given** a card that also carries an operations- or fraud-initiated restriction, **When** the
   cardholder attempts to unfreeze, **Then** the request is denied with a reason that does not leak
   case details, the card remains `frozen`, and the denial is audited.
3. **Given** an unfreeze where authorization freshness or restriction state cannot be positively
   confirmed, **When** it is processed, **Then** it fails closed (neither `success` nor `pending`).

---

### User Story 3 - Cardholder sets spending limits (Priority: P3)

A cardholder sets or changes per-transaction, daily, and monthly limits. Authorizations are checked
against all applicable limits atomically and exactly.

**Why this priority**: Limits are core spend-control value and exercise the exact-money/exact-time
and atomic-enforcement rules. Independently testable via authorization simulations.

**Independent Test**: Set synthetic limits, replay a sequence of synthetic authorizations across a
day/month boundary, and confirm each is approved/declined exactly per the limits with no drift or
double-count.

**Acceptance Scenarios**:

1. **Given** a per-transaction limit of 50.00 USD, **When** a 50.00 USD authorization arrives,
   **Then** it is approved and a 50.01 USD authorization is declined for exceeding the limit.
2. **Given** a daily limit and prior approved spend in the same issuer-calendar day, **When** a new
   authorization would push cumulative spend over the daily limit, **Then** it is declined and the
   remaining allowance is unchanged.
3. **Given** a limit *decrease* (risk-reducing), **When** submitted, **Then** it takes effect
   atomically; **Given** a limit *increase* (risk-increasing) with unconfirmed authorization,
   **Then** it fails closed.
4. **Given** two concurrent limit-change commands with the same base version, **When** both are
   processed, **Then** exactly one wins and the other receives a deterministic conflict.

---

### User Story 4 - Cardholder views transaction history (Priority: P4)

A cardholder browses a stable, paginated history of their card's transactions, correct even while
new transactions arrive and statuses change.

**Why this priority**: History is high-usage and read-heavy; correctness under concurrency (no
duplicates, skips, or order drift) is the interesting constraint.

**Independent Test**: Against a synthetic 100k-transaction fixture, page through history while
injecting new arrivals and status changes; confirm zero duplicates, skips, or order drift and no
prohibited fields.

**Acceptance Scenarios**:

1. **Given** a card with transactions, **When** the cardholder opens history, **Then** the first
   page returns most-recent-first with masked/tokenized identifiers only.
2. **Given** an active pagination session, **When** new transactions arrive between page requests,
   **Then** continuation returns the next items with no duplicates or skips relative to the session
   snapshot.
3. **Given** the cardholder is not the owner of a card, **When** they request its history, **Then**
   access is denied and audited.

---

### User Story 5 - Internal ops/compliance oversight (Priority: P5)

An operations agent working an assigned case can apply a case-scoped control, and a compliance
reviewer can produce a read-only, field-allowlisted export — both least-privilege and audited.

**Why this priority**: Realistic regulated feature needs an internal view, but it is the most
privilege-sensitive and is layered last so cardholder value ships first.

**Independent Test**: With a synthetic open case, confirm an ops action is permitted only within
case scope/expiry and a compliance export contains only allowlisted fields, each fully audited;
confirm denials when scope/purpose/expiry fail.

**Acceptance Scenarios**:

1. **Given** an ops agent with an open assigned case and valid purpose, **When** they place a
   case-scoped freeze, **Then** it succeeds, is attributed to the case, and cannot be released by a
   cardholder unfreeze.
2. **Given** a compliance reviewer with a time-boxed grant, **When** they export a card's activity,
   **Then** the export includes only current allowlisted fields, excludes prohibited data, and is
   audited with purpose and scope.
3. **Given** any internal actor whose case is closed, grant is expired, or purpose is missing,
   **When** they attempt access, **Then** it is denied and audited (fail-closed).

---

### Edge Cases

Each edge case states the expected user-visible outcome and the audit/compliance implication.

| ID | Scenario | Expected behavior |
|----|----------|-------------------|
| EC-01 | Freeze on already-frozen card | Idempotent success; no duplicate audit event; state unchanged. |
| EC-02 | Unfreeze on already-active card | Idempotent success; no state change; audited once. |
| EC-03 | Local freeze durable, downstream propagation failing | Card reads `frozen` + `pending`; retry/alert on unresolved propagation; block remains effective. |
| EC-04 | Cardholder unfreeze while ops/fraud restriction present | Denied without leaking case detail; card stays `frozen`; denial audited. |
| EC-05 | Ambiguous authorization freshness on unfreeze | Fail closed (neither success nor pending); audited as denied. |
| EC-06 | Negative, zero, or non-integer-minor-unit limit | Rejected as invalid; no state change; validation reason returned. |
| EC-07 | Limit currency mismatches card currency | Rejected; amounts never implicitly converted. |
| EC-08 | Authorization exactly equal to a limit | Approved (limit is inclusive); documented boundary. |
| EC-09 | Authorization at daily/monthly period boundary (incl. DST) | Assigned to the correct issuer-calendar period; no double-count. |
| EC-10 | Concurrent limit changes, same base version | Exactly one winner; loser gets deterministic conflict; no lost update. |
| EC-11 | Duplicate command (same idempotency key) | Original outcome replayed; no repeated side effects. |
| EC-12 | Duplicate key, different payload | Rejected as idempotency conflict; original outcome preserved. |
| EC-13 | Empty transaction history | Explicit empty state; no error; audited read. |
| EC-14 | New transactions arrive mid-pagination | Snapshot-bound continuation; no duplicates/skips/order drift. |
| EC-15 | Transaction status changes mid-pagination | Continuation stable to snapshot; status reflected on refresh, not mid-session reorder. |
| EC-16 | History request by non-owner | Denied; audited; no data disclosed. |
| EC-17 | Reversal/partial-capture/refund events | Represented distinctly; do not corrupt cumulative limit counters. |
| EC-18 | Ops action outside assigned case scope | Denied (fail-closed); audited with reason. |
| EC-19 | Expired ops/compliance grant | Denied; audited; requires re-grant. |
| EC-20 | Compliance export requesting a non-allowlisted field | Field omitted or export rejected; never returns prohibited data. |
| EC-21 | Export exceeding max size/volume | Bounded/paginated or rejected with guidance; never unbounded dump. |
| EC-22 | Missing/unreconciled audit evidence for an action | Alert raised; defined recovery/degraded-mode/incident timeline; action treated as suspect. |
| EC-23 | Rapid freeze/unfreeze oscillation (fraud-ish) | Rate/velocity guard; each transition still audited; no state corruption. |
| EC-24 | Stale read of card state after a change | Reads converge within the stated consistency window; risk actions re-check at commit. |
| EC-25 | Free-text/notes field on any action | Sanitized; never stores PAN/CVV/credentials/unrelated case data. |
| EC-26 | Downstream processor returns raw sensitive payload | Payload never surfaced/stored; only sanitized, tokenized references retained. |

## Requirements *(mandatory)*

### Functional Requirements

**Freeze (OBJ-1)**

- **FR-001**: Cardholders MUST be able to freeze a card they own.
- **FR-002**: A freeze MUST be accepted only when the local authorization block is durably recorded.
- **FR-003**: Once locally durable, the card MUST read `frozen` and the local block MUST decline new
  authorizations even if downstream propagation is still `pending`.
- **FR-004**: Freeze MUST be idempotent for repeated identical commands (no duplicate effect/audit).
- **FR-005**: Every freeze (and failed attempt) MUST emit a sanitized append-only audit event.

**Unfreeze (OBJ-2)**

- **FR-006**: Cardholders MUST be able to unfreeze a card they froze.
- **FR-007**: Unfreeze MUST fail closed: it succeeds only when authorization freshness and
  restriction state are positively confirmed safe; otherwise it returns neither `success` nor
  `pending`.
- **FR-008**: A cardholder unfreeze MUST NOT remove a stronger or unknown restriction (e.g.,
  ops/fraud-initiated); such attempts MUST be denied without leaking case detail.
- **FR-009**: Unfreeze of a risk-increasing nature MUST require fresh step-up authentication.
- **FR-010**: Every unfreeze attempt (success or denial) MUST be audited with a non-leaking reason.

**Spending limits (OBJ-3)**

- **FR-011**: Cardholders MUST be able to set per-transaction, daily, and monthly limits.
- **FR-012**: Limits MUST be expressed in integer minor units with the card's ISO-4217 currency;
  invalid (negative/zero/mismatched-currency/non-integer) limits MUST be rejected.
- **FR-013**: Each authorization MUST be evaluated atomically against all applicable limits; an
  authorization equal to a limit is approved (inclusive boundary).
- **FR-014**: Cumulative daily/monthly spend MUST be assigned to periods by the issuer billing
  calendar/timezone with DST-safe boundaries.
- **FR-015**: Limit *decreases* MUST apply atomically; limit *increases* MUST fail closed when
  authorization cannot be positively confirmed.
- **FR-016**: Reversals, partial captures, and refunds MUST adjust cumulative counters correctly and
  never double-count.
- **FR-017**: Concurrent limit changes MUST use optimistic version checks yielding exactly one
  winner and a deterministic conflict for losers.
- **FR-018**: Every limit change (success/denial/conflict) MUST be audited.

**Transaction history (OBJ-4)**

- **FR-019**: Cardholders MUST be able to view their card's transaction history, most-recent-first.
- **FR-020**: History MUST be paginated with snapshot-bound keyset continuation so concurrent
  arrivals/status changes cause no duplicates, skips, or order drift within a session.
- **FR-021**: History entries MUST expose only masked/tokenized identifiers and MUST NOT include
  prohibited sensitive fields (Constitution VI).
- **FR-022**: History MUST present an explicit empty state when there are no transactions.
- **FR-023**: History access MUST be authorization-bound to the owner; non-owner access MUST be
  denied and audited.
- **FR-024**: Reversal/partial-capture/refund events MUST be represented distinctly from original
  authorizations.

**Internal oversight (OBJ-5)**

- **FR-025**: Operations actions MUST require an open assigned case, stated purpose, valid
  (unexpired) grant, and the exact permission, re-evaluated at the moment of use.
- **FR-026**: An operations-initiated restriction MUST NOT be removable by a cardholder unfreeze.
- **FR-027**: Compliance export MUST be read-only and limited to a current, versioned field
  allowlist; prohibited fields MUST never be included.
- **FR-028**: Compliance export MUST be bounded in size/volume (paginated or rejected beyond the
  limit); no unbounded data dump.
- **FR-029**: Internal access with a closed case, missing purpose, or expired grant MUST be denied
  (fail-closed) and audited.
- **FR-030**: Who may *release* an operations-initiated freeze MUST follow separation of duties
  (see Clarifications): release requires a second authorized ops/compliance actor, never the
  original placer alone and never the cardholder.

**Cross-cutting: audit, idempotency, privacy, recovery (OBJ-6)**

- **FR-031**: All state-changing commands MUST carry an idempotency key bound to
  actor+card+action+payload; identical replays within the window return the original outcome.
- **FR-032**: A duplicate idempotency key with a different payload MUST be rejected as a conflict.
- **FR-033**: Audit evidence MUST be append-only, tamper-evident, attributable, sanitized, and
  independently reconstructable, and MUST be separate from operational diagnostics.
- **FR-034**: Missing/unreconciled audit evidence MUST trigger a defined alert, recovery,
  degraded-mode, and incident timeline.
- **FR-035**: Access-denial events MUST themselves be audited.
- **FR-036**: Card state MUST be composite: lifecycle (active/frozen/closed) is separate from
  restriction sources (cardholder/ops/fraud), and the strongest applicable restriction governs.
- **FR-037**: Free-text/notes on any action MUST be sanitized to exclude prohibited data.
- **FR-038**: Downstream-processor raw payloads MUST never be surfaced or stored; only sanitized,
  tokenized references are retained.
- **FR-039**: Every action's response MUST clearly distinguish `success`, `denied`, `pending`
  (propagation only, for risk-reducing actions), and `conflict`.
- **FR-040**: All reads that expose card/transaction data MUST re-check authorization at the time of
  the read, not only at session start.

### Non-Functional & Policy Requirements

- **NFR-001** (Security): Risk-increasing actions require fresh step-up authentication (NIST
  SP 800-63B-style assurance); session presence is insufficient.
- **NFR-002** (Privacy): Data minimization — display/export the least data for the stated purpose;
  default to masked/tokenized references (NIST Privacy Framework).
- **NFR-003** (Sensitive data): No PAN/CVV/track data/credentials/raw payloads in views, logs,
  audit, exports, fixtures, or prompts (PCI DSS vocabulary; Constitution VI).
- **NFR-004** (Auditability): 100% of business-significant actions produce audit evidence; evidence
  is queryable within the stated window.
- **NFR-005** (Reliability): Freeze safety must hold under downstream propagation failure (degraded
  mode); unsafe fallbacks are excluded from success accounting.
- **NFR-006** (Consistency): Reads converge within a stated time-to-consistency window; risk actions
  re-verify at commit.
- **NFR-007** (Concurrency): Deterministic single-winner resolution for concurrent writes to a card.
- **NFR-008** (Performance): Interactive control actions and first history page meet stated latency
  targets (see Success Criteria).
- **NFR-009** (Least privilege): Internal access is case-scoped, purpose-bound, time-boxed, and
  re-evaluated per action (NIST SP 800-53 AC family).
- **NFR-010** (Separation of duties): Release of ops-initiated restrictions requires a distinct
  second authorized actor.
- **NFR-011** (Idempotency): Replay window and semantics are explicit and uniformly applied.
- **NFR-012** (Observability): Operational diagnostics are separate from audit evidence and never
  contain prohibited data.
- **NFR-013** (Verification): Every mid-level objective has documented review checkpoints and test
  categories (unit/integration/e2e as documentation) with synthetic fixtures.
- **NFR-014** (Availability): Control surface meets a stated monthly availability target with unsafe
  fallbacks excluded from the success metric.

### Key Entities *(include if feature involves data)*

- **Card**: A virtual card identified by a token (never full PAN). Holds composite state: lifecycle
  status, restriction sources, currency, and a monotonic version for optimistic concurrency.
- **Restriction**: A block on a card attributed to a source (cardholder/ops/fraud), with placer
  identity, reason class (non-leaking), and lifecycle. Strongest applicable restriction governs.
- **Limit**: Per-transaction / daily / monthly ceilings in integer minor units + currency, with
  effective period semantics tied to the issuer calendar.
- **Transaction**: An authorization/settlement event with immutable occurrence instant, amount
  (minor units + currency), type (auth/capture/reversal/refund), and masked/tokenized references.
- **Command**: A state-changing request carrying actor, card, action, payload, idempotency key, and
  base version.
- **AuditEvent**: Append-only, tamper-evident, sanitized record of a business-significant action or
  denial, attributable to an actor and (for internal actors) a case.
- **Case**: An internal work item scoping ops/compliance access, with assignment, purpose, and
  expiry.
- **AccessGrant**: A time-boxed, purpose-bound authorization for an internal actor to act within a
  case.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A cardholder can freeze a card and see it reflected as `frozen` in **≤ 2 seconds
  (p95)** under healthy conditions.
- **SC-002**: External freeze confirmation, control consistency across surfaces, and audit
  queryability complete within **≤ 5 seconds (p95)**.
- **SC-003**: **100%** of business-significant actions and denials produce a retrievable audit
  event (no gaps in a reconciliation sample).
- **SC-004**: Against a **100,000-transaction / 24-month synthetic fixture**, paging the full
  history yields **zero** duplicates, skips, order-drift, authorization leaks, or prohibited fields.
- **SC-005**: In a **20 same-version concurrent-command** fixture, **exactly one** command wins and
  all others receive a deterministic conflict (zero lost updates).
- **SC-006**: **0** risk-increasing actions (unfreeze, limit increase, export) return `success` or
  `pending` under ambiguous authorization in the fail-closed test set.
- **SC-007**: Unresolved downstream freeze propagation raises an alert within **60 seconds**, with
  recovery/escalation steps at **5 / 15 minutes**; control-surface availability target is
  **99.9%** monthly with unsafe fallbacks excluded.
- **SC-008**: Idempotent replays within a **24-hour** window return the original outcome in
  **100%** of the replay test set, with **0** duplicate side effects.

## Assumptions

- Card issuance/creation and the downstream processor already exist; this feature governs *controls*
  over existing cards, not card manufacture.
- An identity/authentication service capable of step-up exists and is reused.
- The issuer billing calendar and timezone are known per program.
- Performance/consistency numbers are **assumed targets** for FinTech UX/ops (justified in the
  README), to be validated against real SLIs before production — not observed measurements or
  regulatory mandates.
- All data used in scenarios and fixtures is synthetic.
- Scope excludes disputes/chargebacks, rewards, card manufacture, and multi-currency conversion.

## Clarifications

Resolved in the `/speckit-clarify` phase (see
[`reviews/analyze.md`](reviews/analyze.md) and the PR screenshots):

- **Q: Who may release an operations-initiated freeze?** → **Decision (separation of duties)**: a
  second authorized ops/compliance actor, distinct from the original placer; never the original
  placer alone and never the cardholder. Encoded in **FR-030 / NFR-010**.
