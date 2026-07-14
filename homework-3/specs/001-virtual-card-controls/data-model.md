# Conceptual Data Model: Regulated Virtual Card Controls

**Status**: Planning artifact; no schema, migration, API, or code
**Source**: Gate-1-approved `spec.md`

## Modeling Rules

- Names and fields describe required meaning, not storage implementation.
- Money is an exact scaled amount plus billing/original currency; binary floating point is prohibited.
- Time is an unambiguous instant; issuer billing timezone/calendar is separate display/period metadata.
- Identifiers are opaque and immutable within their domain.
- Lifecycle, independently sourced restrictions, and derived effective status are separate.
- Original transaction and audit identities/history are immutable; changes are status/correction events.
- Per-surface classification and allowed fields follow the canonical taxonomy in `spec.md`.

## Relationship Summary

```text
Cardholder 1 ── owns ── * VirtualCard
VirtualCard 1 ── has ── * CardRestriction
VirtualCard 1 ── has current ── 1 SpendingLimitSet
VirtualCard 1 ── accumulates by period ── * LimitConsumption
VirtualCard 1 ── receives ── * ControlCommand
ControlCommand 1 ── creates ── * PropagationAttempt
VirtualCard 1 ── references externally ── * Transaction
Transaction 1 ── has ── * TransactionStatusEvent
Transaction 0..1 ── linked from refund ── * Transaction
InternalCaseAuthorization 1 ── scopes ── * PrivilegedOutcome
ControlCommand/PrivilegedOutcome 1 ── records ── 1 AuditIntent
AuditIntent 1 ── publishes/reconciles ── 1 AuditEvent
InternalCaseAuthorization 1 ── permits ── * ComplianceExport
```

## Entity Definitions

### VirtualCard

| Attribute | Meaning and validation | Classification/access |
|-----------|------------------------|-----------------------|
| Card ID | Immutable opaque identifier; never PAN | Restricted; owned/case-scoped |
| Owner ID | Opaque current cardholder identity | Restricted; authorization use only |
| Masked identity | Issuer-approved display representation | Allowed on approved views only |
| Billing currency | Supported currency governing limits/consumption | Confidential |
| Billing timezone/calendar | Issuer policy used for daily/monthly boundaries | Internal policy |
| Lifecycle | `OPEN` or `TERMINATED` | Confidential |
| State version | Monotonic expected-version value | Confidential |
| Effective status | Derived only from lifecycle and active restrictions | Confidential; never independent source of truth |

### CardRestriction

| Attribute | Meaning and validation |
|-----------|------------------------|
| Restriction ID | Immutable opaque record identity |
| Card ID | Target virtual card |
| Source | Exactly one of `USER`, `OPERATIONS`, `RISK`, or issuer-defined unknown restrictive source |
| Type | `FREEZE` for user/operations; risk restriction type remains policy-owned |
| Active interval | Activation instant and optional release instant |
| Reason | Enumerated safe reason; operations uses only approved `FR-033` values |
| Case/policy references | Required for operations/risk source; opaque and versioned |
| Local block effective time | Must exist before a freeze command is accepted |
| External propagation status | `CONFIRMED` or `PENDING`; retry/escalation metadata separate |

Only the owning source/workflow may release its restriction. This feature can add/remove only the
cardholder's `USER` freeze and add an operations freeze; operations/risk release is out of scope.

### SpendingLimitSet

| Attribute | Meaning and validation |
|-----------|------------------------|
| Card ID/version | One current version per card; optimistic winner rule |
| Currency | Equals card billing currency |
| Per-transaction limit | Exact positive amount within issuer policy |
| Daily limit | Exact positive amount; at least per-transaction amount |
| Monthly limit | Exact positive amount; at least daily amount |
| Policy version/bounds | Exact issuer decision used for validation |
| Effective instant | When new authorization decisions use this version |

The three values are one atomic set. While any restriction exists, a complete set containing any
increase is rejected; a valid non-increasing set with at least one decrease may proceed, with other
components allowed to remain unchanged. Already authorized activity is unchanged.

### LimitConsumption

| Attribute | Meaning and validation |
|-----------|------------------------|
| Card/period ID | Opaque card plus issuer billing-timezone daily/monthly interval |
| Period start/end | Local calendar boundaries represented as unambiguous instants |
| Held amount | Approved authorization holds and incremental adjustments |
| Posted amount | Final posted billing amounts replacing matching holds |
| Released amount | Matching full/partial authorization reversals |
| Refund relation | Linked credit evidence; does not replenish historical daily/monthly allowance |
| Last reconciliation | Instant/source version used to derive consumption |

Remaining allowance cannot be negative; when consumption meets/exceeds the limit, it is zero. FX
authorization uses authorization-time billing amount/rate; posting replaces it with final billing
amount without retroactive authorization decisions.

### ControlCommand

| Attribute | Meaning and validation |
|-----------|------------------------|
| Command identity | Bound to actor ID/role, card ID, action, normalized payload |
| Expected version | Required card-state or limit-set version |
| Action | `ADD_USER_FREEZE`, `REMOVE_USER_FREEZE`, `ADD_OPS_FREEZE`, or `SET_LIMITS` |
| Preconditions | Ownership or valid role/case/purpose, lifecycle/restrictions, verification/policy |
| Result | One normative result category from `spec.md` |
| Result state/version | Sanitized effective outcome returned for retries/conflicts |
| Correlation/event identity | Links propagation and audit without sensitive payload |
| Retention | Original outcome available for at least the assumed 24-hour idempotency window |

For one expected version, the first distinct durably accepted command wins. Same bound identity returns
the original result; a changed binding returns `IDEMPOTENCY_MISMATCH` with no state change.

Every attempt result has a sanitized audit identity. State-changing success records audit intent in
the same acceptance boundary; denied/validation/conflict/mismatch/unavailable/no-op outcomes record
attributable attempt evidence without product-state mutation. Retry deliveries for one bound command
share one stored business outcome/event; a distinct already-satisfied freeze is a separately
attributable no-op without a duplicate transition event.

### PropagationAttempt

| Attribute | Meaning and validation |
|-----------|------------------------|
| Command/restriction IDs | Immutable link to accepted freeze |
| Destination | Approved processor/control boundary, named without raw payload |
| Attempt number/time | Monotonic retry evidence |
| Sanitized outcome | Confirmed, retryable failure, non-retryable policy result |
| Next retry/escalation | Supports 60-second alert and 15-minute escalation |

Propagation never weakens durable local restriction. Only accepted freeze may expose
`PENDING_PROPAGATION`.

### Transaction

| Attribute | Meaning and validation |
|-----------|------------------------|
| Transaction ID | Immutable opaque identity |
| Card ID | Owned/case-scoped target |
| Occurrence/authorization instant | Immutable primary ordering time |
| Billing amount/currency | Exact signed value |
| Original amount/currency | Exact value when different |
| Authorization-time FX reference | Rate/source timestamp used for limit decision |
| Safe merchant label | Sanitized display field only |
| Current derived status | Pending/posted/declined/reversed from status events |
| Latest status-event instant | Does not change primary sort position |
| Related original ID | Present for a refund credit transaction |

### TransactionStatusEvent

| Attribute | Meaning and validation |
|-----------|------------------------|
| Event ID | Immutable identity |
| Transaction ID | Original transaction relation |
| Status/time | Timestamped pending/post/decline/reversal evolution |
| Exact amount adjustment | Hold increment, posting replacement, or reversal release |
| Source version | Supports freshness/reconciliation |

A refund is a distinct linked credit `Transaction`, not a status overwrite of the original.

### InternalCaseAuthorization

| Attribute | Meaning and validation |
|-----------|------------------------|
| Case ID/issuer | Existing authoritative case-management identity |
| Actor ID/role | Current assigned operations or compliance actor |
| Purpose | Enumerated purpose allowed for that role |
| Status/expiry | Must be open, assigned, and unexpired on every privileged decision |
| Allowed actions | Exact subset from role×case×purpose matrix |
| Step-up evidence category | Required for compliance export; secret material excluded |

There is no unenumerated "equivalent" authorization. Closure, expiry, reassignment, or role loss ends
access on the next decision.

### PrivilegedOutcome

Conceptual record of every allowed/denied internal search, read, emergency freeze, or export. It binds
actor, role, case, purpose, action, sanitized subject, result category, time, and correlation. It is
not a replacement for the final `AuditEvent`.

### AuditIntent and AuditEvent

| Attribute | AuditIntent | AuditEvent |
|-----------|-------------|------------|
| Identity | Globally unique and durably recorded at outcome acceptance | Same idempotency identity |
| Content | Actor/role, opaque subject, action, enumerated reason, sanitized before/after, policy/result, time, correlation | Immutable published evidence with same original meaning |
| State | Pending/published/recovery/incident | Original or linked corrective event |
| Access | Security/compliance control functions | Assigned-case/control readers per taxonomy |
| Retention | Until published and reconciled under control policy | Assumed seven years; hold-aware disposition |

Replay is duplicate-safe. Missing queryable evidence alerts at five seconds, must recover by five
minutes, and becomes a security/control incident at 15 minutes. Corrections create linked events.

### ComplianceExport

Bound to one active assigned compliance case, enumerated purpose, current step-up outcome, allowed
field set, no more than 10,000 sanitized records, actor/correlation, creation/24-hour expiry, watermark
or equivalent attribution, and audit intent. Cross-case and operations exports are prohibited.

## Derived Effective Status

| Condition | Effective status |
|-----------|------------------|
| Lifecycle `TERMINATED` | `TERMINATED` |
| `RISK` restriction active | `RISK_RESTRICTED` |
| No risk restriction; `OPERATIONS` freeze active | `OPS_FROZEN` |
| No stronger restriction; `USER` freeze active | `USER_FROZEN` |
| Lifecycle `OPEN`; no restriction active | `ACTIVE` |

Unknown restriction source is fail-safe restrictive and cannot be removed through this feature.

## Command State Model

```text
RECEIVED
  ├── invalid/unauthorized/precondition failure → terminal non-changing result + attempt evidence
  ├── stale expected version                   → CONFLICT + attempt evidence
  ├── mismatched command binding               → IDEMPOTENCY_MISMATCH + attempt evidence
  ├── already USER_FREEZE (approved no-op)     → SUCCEEDED
  │     └── no restriction/version/propagation mutation; attributable no-op evidence
  └── state-changing acceptance with audit intent
        ├── non-freeze                         → SUCCEEDED
        └── freeze + durable local block
              ├── processor confirmed         → SUCCEEDED
              └── confirmation outstanding    → PENDING_PROPAGATION
                                                    ├── reconciled
                                                    └── escalated
```

The approved no-op does not consume the expected-version winner for a distinct state-changing command.
`TEMPORARILY_UNAVAILABLE` is terminal/non-changing for ambiguous non-freeze dependency outcomes.

## Invariants and Verification Mapping

| ID | Invariant | Source | Planned evidence |
|----|-----------|--------|------------------|
| DM-001 | Accepted freeze and durable local block share one acceptance boundary | FR-003, FR-033, NFR-004 | State/transaction boundary review and failure scenarios |
| DM-002 | Removing user freeze never removes stronger restrictions | FR-007–FR-008 | Composite-state transition matrix |
| DM-003 | Limit set is exact, ordered, versioned, and atomic | FR-012–FR-020 | Money/period/property/concurrency fixtures |
| DM-004 | One expected version has at most one distinct accepted winner | FR-018–FR-020, NFR-009 | 20-way concurrency schedule |
| DM-005 | Command binding mismatch produces no state transition | FR-019, NFR-008 | Identity permutation/reconciliation matrix |
| DM-006 | Transaction ordering identity is immutable across status events | FR-023–FR-030 | Snapshot paging traversal and linked-refund fixtures |
| DM-007 | Every privileged outcome has current role/case/purpose scope | FR-031–FR-037, NFR-001 | Negative authorization matrix |
| DM-008 | Every accepted/denied outcome has one reconciled audit identity | FR-038–FR-041, NFR-003 | Outcome-to-event reconciliation and replay |
| DM-009 | No surface contains taxonomy-prohibited data | FR-025, FR-040, NFR-002 | Allowed-field/category scan and privacy review |
| DM-010 | Retention/deletion never overrides an active policy/legal hold | NFR-012 | Entity disposition matrix review |

## Design Boundary

This model is complete enough to derive future documentation tasks. It intentionally omits storage
tables, indexes, serialized schemas, endpoints, classes, migrations, and vendor configuration.
