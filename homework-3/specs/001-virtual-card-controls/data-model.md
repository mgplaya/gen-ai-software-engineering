# Phase 1 Data Model (Conceptual): Regulated Virtual Card Controls

**Date**: 2026-07-15 · **Feature**: [spec.md](spec.md)

> Conceptual only — attributes describe *meaning*, not storage schema or types. No migrations.

## Entities

### Card

| Attribute | Meaning |
|-----------|---------|
| card_token | Opaque reference; never full PAN (Constitution VI). |
| masked_pan | Optional display value (≤ first-6/last-4) where justified. |
| owner_ref | Cardholder who owns the card (tokenized). |
| currency | ISO-4217; all limits/amounts share it. |
| lifecycle_status | `active` / `frozen` / `closed`. |
| restrictions | Set of Restriction (see below). |
| version | Monotonic integer for optimistic concurrency. |

**Invariant**: effective spendability = `lifecycle_status == active` AND no active restriction from
any source. Strongest restriction governs (FR-036).

### Restriction

| Attribute | Meaning |
|-----------|---------|
| source | `cardholder` / `ops` / `fraud`. |
| placer_ref | Actor (and case, for internal) that placed it. |
| reason_class | Non-leaking category (never free-text case detail). |
| status | `active` / `released`. |
| propagation | `confirmed` / `pending` (downstream). |

**Invariant**: a `cardholder` unfreeze may release only `cardholder`-source restrictions; releasing
an `ops` restriction requires a distinct second authorized actor (FR-026, FR-030).

### Limit

| Attribute | Meaning |
|-----------|---------|
| scope | `per_transaction` / `daily` / `monthly`. |
| amount_minor | Integer minor units (≥ 1). |
| currency | Must equal card currency (FR-012). |
| period_calendar | Issuer billing calendar/timezone for daily/monthly (FR-014). |

### Transaction

| Attribute | Meaning |
|-----------|---------|
| txn_id | Tokenized id; stable sort tiebreaker. |
| occurred_at | Immutable UTC instant. |
| amount_minor + currency | Exact money. |
| type | `authorization` / `capture` / `reversal` / `refund`. |
| status | e.g. `approved` / `declined` / `reversed`. |
| masked_refs | Only masked/tokenized references (FR-021). |

**Invariant**: reversals/partial-captures/refunds adjust cumulative counters without double-count
(FR-016, FR-024, EC-17).

### Command

| Attribute | Meaning |
|-----------|---------|
| actor_ref, card_token, action | Who/what/which. |
| payload | Action parameters (e.g., new limit). |
| idempotency_key | Bound to actor+card+action+payload (FR-031). |
| base_version | Card version the command expects (FR-017). |
| outcome | `success` / `denied` / `pending` / `conflict` (FR-039). |

### AuditEvent

| Attribute | Meaning |
|-----------|---------|
| seq | Append-only monotonic sequence. |
| actor_ref, case_ref? | Attribution (case for internal actors). |
| action, target_token | What happened, to which card (tokenized). |
| result | `success` / `denied` (+ non-leaking reason). |
| integrity_tag | Tamper-evidence (e.g., chained hash). |
| occurred_at | UTC instant. |

**Invariant**: append-only; sanitized; separate from diagnostics; reconstructable (FR-033).

### Case

Internal work item: `case_id`, `assignee_ref`, `purpose`, `status` (`open`/`closed`), scope.

### AccessGrant

Time-boxed authorization: `grantee_ref`, `case_ref`, `purpose`, `permissions`, `expires_at`,
`step_up_at`. Re-evaluated per action (FR-025, FR-040).

## Card State Machine

```text
            freeze (cardholder|ops|fraud)                 unfreeze (authorized + safe)
 active  ─────────────────────────────────▶  frozen  ─────────────────────────────────▶ active
   │                                            │
   │                                            │  cardholder unfreeze w/ stronger restriction present
   │                                            └───────────────▶ denied (stays frozen, audited)  [FR-008, EC-04]
   │
   └── close (out of scope for controls) ─────────────────▶ closed (terminal)
```

- Freeze is accepted on durable local block; `propagation=pending` allowed (R2, FR-002/003).
- Unfreeze is fail-closed: denied on any ambiguity or stronger restriction (R1, FR-007/008).

## Cross-entity Invariants (traceability)

| Invariant | Requirements |
|-----------|--------------|
| Composite state; strongest restriction wins | FR-036, FR-008, FR-026 |
| Exact money/time; inclusive limit boundary | FR-012, FR-013, FR-014 |
| Idempotent + single-winner concurrency | FR-017, FR-031, FR-032 |
| Masked/tokenized data only | FR-021, FR-037, FR-038 |
| Append-only sanitized audit incl. denials | FR-033, FR-035 |
