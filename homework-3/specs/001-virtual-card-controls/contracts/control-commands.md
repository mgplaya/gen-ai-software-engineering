# Conceptual Contract: Card Control Commands

**Contract type**: Technology-neutral preconditions, outcomes, and invariants
**Not included**: Endpoint, transport, serialization schema, implementation, or UI

## Common Command Envelope

| Field/claim | Contract requirement |
|-------------|----------------------|
| Command identity | Unique for 24 hours and bound to actor ID/role, card ID, action, normalized payload |
| Actor context | Fresh authenticated identity; cardholder ownership or current internal role/case/purpose |
| Expected version | Required state version for freeze/unfreeze and limit-set version for limits |
| Correlation | Opaque identity shared with audit/propagation evidence; no sensitive payload |
| Policy context | Current ownership, card lifecycle/restrictions, issuer policy version, step-up outcome category |
| Intent | One of the actions below with exact normalized values; no implicit partial update |

Same bound command identity returns the stored original outcome. Reuse with changed binding returns
`IDEMPOTENCY_MISMATCH`; the target is unchanged and no target detail is leaked.

Every delivered status/limit attempt—successful state change, approved state no-op, denial, validation
failure, conflict, identity mismatch, unavailable outcome, or retry delivery—MUST have an attributable
sanitized result linked to one audit identity under the approved deduplication semantics. A successful
state change records audit intent in its state-change acceptance boundary. A non-changing result
records attempt evidence without mutating product state. Multiple deliveries of one bound command
identity link to one stored business outcome/event; a distinct already-satisfied freeze command is a
new attributable no-op attempt but creates no duplicate state-transition event.

## Action Contracts

### Add User Freeze

**Preconditions**: current ownership; lifecycle `OPEN`; expected state version; explicit confirmation.

**Acceptance boundary**: `USER_FREEZE`, incremented state version, durable local authorization block,
command outcome, audit intent, and external propagation intent are durable together.

**Outcomes**:

- `SUCCEEDED` when local block is effective and external propagation is confirmed;
- `PENDING_PROPAGATION` when local block is effective but external confirmation is outstanding;
- `CONFLICT`, `DENIED`, `VALIDATION_ERROR`, or `IDEMPOTENCY_MISMATCH` only under their approved
  conditions. This contract does not add a freeze-specific `TEMPORARILY_UNAVAILABLE` path.

When `USER_FREEZE` is already present, a distinct request is a successful state no-op: it returns the
truthful current composite/effective status, creates an attributable attempt/audit outcome, and does
not mutate restrictions, increment state version, create new propagation intent, or consume the
expected-version winner for a distinct state-changing command.

Already authorized transactions are not cancelled by freeze.

### Remove User Freeze

**Preconditions**: current ownership; lifecycle `OPEN`; `USER_FREEZE` exists; mandatory current step-up;
expected state version; no ambiguous authorization/policy/propagation result.

**Postcondition**: remove only `USER_FREEZE`. Effective status becomes `ACTIVE` only when no stronger
restriction remains; otherwise the effective status stays restrictive and is returned truthfully.

`PENDING_PROPAGATION` is prohibited. Ambiguous dependency outcome returns
`TEMPORARILY_UNAVAILABLE` with no state change.

### Add Operations Freeze

**Preconditions**: current operations role; assigned open case with exactly `CUSTOMER_SUPPORT` or
`URGENT_RISK_CONTAINMENT` purpose; current risk-policy version; one `FR-033` enumerated reason;
expected state version. Either enumerated operations purpose may emergency-freeze only when all other
preconditions and the approved reason are present.

**Acceptance/postconditions**: same durable local blocking and propagation contract as user freeze;
adds only `OPS_FREEZE`; never removes another restriction. Release is outside this feature.

### Set Spending Limits

**Preconditions**: current ownership; expected limit version; card billing currency/scale; current
policy bounds; complete per-transaction/daily/monthly set; risk step-up where required.

**Validation**:

- all amounts are exact, positive, within policy, and
  `per-transaction ≤ daily ≤ monthly`;
- set is non-increasing (no component increases) with at least one decrease, or contains an increase,
  relative to current values; unchanged components are permitted;
- when any restriction is active, only a complete non-increasing set with at least one decrease is
  eligible;
- first distinct command for an expected version wins; later distinct commands conflict.

**Postcondition**: all three values and version change atomically or none changes. New decisions use the
set within the consistency target; prior authorizations are unchanged.

## Limit Accounting Contract

| Event | Allowance effect |
|-------|------------------|
| Approved authorization | Hold consumes per-transaction/daily/monthly billing amount |
| Incremental authorization | Adjust existing hold; no duplicate consumption |
| Decline | Consumes nothing |
| Posting | Replaces hold with final billing amount |
| Full/partial authorization reversal | Releases matching held amount |
| Refund | Separate credit; does not replenish historical daily/monthly allowance |
| FX posting adjustment | Replaces authorization-time billing amount with final billing amount; no retroactive decision |
| Daily/monthly boundary | New issuer-billing-timezone calendar period exactly once, including DST |

If consumption meets/exceeds a newly lowered limit, remaining allowance is zero; accepted past
transactions remain valid.

## Result Contract

| Result | State-changing? | Terminal? | Required response content |
|--------|-----------------|-----------|---------------------------|
| `SUCCEEDED` | Requested effect is durable; may be approved no-op | Yes | Sanitized effective composite status/limits, unchanged or new version as applicable, correlation |
| `PENDING_PROPAGATION` | Local freeze only | No | Locally frozen truth, pending external confirmation, correlation |
| `DENIED` | No | Yes | Safe reason/next action; no unauthorized target detail |
| `VALIDATION_ERROR` | No | Yes | Exact safe field/reason categories |
| `CONFLICT` | No | Yes | Current sanitized state/limits and version |
| `IDEMPOTENCY_MISMATCH` | No | Yes | Generic invalid request and correlation |
| `TEMPORARILY_UNAVAILABLE` | No | Yes | No success claim; safe retry guidance |

## Recovery Timelines

- Freeze propagation alerts operations at 60 seconds and escalates unresolved at 15 minutes.
- Non-freeze ambiguous outcomes fail closed and surface for operations review within five minutes.
- Audit evidence follows the separate evidence contract; missing evidence triggers degraded-safe mode.

## Traceability

`OBJ-001`, `OBJ-002`, `OBJ-005`, `OBJ-006`; `FR-001–FR-021`, `FR-033`, `FR-038–FR-041`;
`NFR-003–NFR-009`, `NFR-011`, `NFR-014`; `EC-002–EC-010`, `EC-021`, `EC-023–EC-026`;
`SC-001–SC-003`, `SC-006–SC-007`.
