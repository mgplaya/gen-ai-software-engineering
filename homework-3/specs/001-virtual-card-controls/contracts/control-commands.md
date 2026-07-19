# Behavioral Contract: Control Commands (Freeze / Unfreeze / Limits)

**Feature**: [../spec.md](../spec.md) · Conceptual pre/postconditions — **not** API/endpoint code.

All commands carry: `actor_ref`, `card_token`, `action`, `payload`, `idempotency_key`,
`base_version`. All emit an AuditEvent (success or denial). Outcomes are one of
`success | denied | pending | conflict` (FR-039).

## C1 — Freeze (risk-reducing)

- **Pre**: actor owns card (or is authorized internal actor); card not `closed`.
- **Post (success)**: a restriction of the actor's source is `active`; `lifecycle_status=frozen`;
  local authorization block durable; `propagation` may be `pending`.
- **Idempotency**: repeat with same key → original outcome, no duplicate restriction/audit (FR-004,
  EC-01).
- **Traces**: FR-001, FR-002, FR-003, FR-005; SC-001, SC-002.

## C2 — Unfreeze (risk-increasing, fail-closed)

- **Pre**: fresh step-up authentication; restriction state positively known.
- **Post (success)**: only the actor's own source restriction released; if no other active
  restriction → `lifecycle_status=active`.
- **Denied when**: a stronger/unknown restriction exists (FR-008, EC-04); step-up stale or state
  ambiguous → **fail closed**, neither `success` nor `pending` (FR-007, EC-05).
- **Ops-release**: releasing an `ops` restriction requires a distinct second authorized actor
  (FR-030, separation of duties).
- **Traces**: FR-006..FR-010, FR-030; SC-006.

## C3 — Set/Change Limit

- **Pre**: `amount_minor ≥ 1`; `currency == card.currency`; scope ∈ {per_transaction, daily,
  monthly}.
- **Post (success)**: limit updated atomically; card `version` incremented.
- **Validation**: negative/zero/non-integer/mismatched-currency → `denied` (FR-012, EC-06, EC-07).
- **Risk asymmetry**: decrease applies atomically; increase fails closed when authorization
  unconfirmed (FR-015).
- **Concurrency**: two same-`base_version` changes → one `success`, one `conflict` (FR-017, EC-10,
  SC-005).
- **Traces**: FR-011..FR-018; SC-005.

## C4 — Authorization Evaluation (system-driven, read of limits/state)

- **Rule**: an incoming authorization is `approved` iff card is spendable AND `amount ≤ per_txn` AND
  `daily_cumulative + amount ≤ daily` AND `monthly_cumulative + amount ≤ monthly`, all evaluated
  atomically; boundary is inclusive (FR-013, EC-08).
- **Periods**: cumulative counters assigned by issuer calendar, DST-safe (FR-014, EC-09).
- **Adjustments**: reversal/partial-capture/refund adjust counters without double-count (FR-016).

## Outcome & Idempotency Matrix

| Situation | Outcome |
|-----------|---------|
| Valid risk-reducing action, durable local block | `success` (propagation may be `pending`) |
| Valid risk-increasing action, positively safe | `success` |
| Risk-increasing action, any ambiguity | `denied` (fail closed) — never `pending` |
| Replay, same idempotency key + payload | original outcome (no new side effect) |
| Same key, different payload | `conflict` (FR-032, EC-12) |
| Concurrent same-version writes | one `success`, others `conflict` |
