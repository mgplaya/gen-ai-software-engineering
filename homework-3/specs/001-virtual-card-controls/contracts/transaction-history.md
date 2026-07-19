# Behavioral Contract: Transaction History

**Feature**: [../spec.md](../spec.md) · Conceptual pre/postconditions — **not** API/endpoint code.

## H1 — Open history (first page)

- **Pre**: requester is the card owner (re-checked at read time, FR-040).
- **Post**: returns most-recent-first entries with masked/tokenized references only; establishes a
  pagination **snapshot** and returns a continuation cursor.
- **Empty**: if no transactions, return an explicit empty state (not an error) (FR-022, EC-13).
- **Traces**: FR-019, FR-021, FR-023; SC-001.

## H2 — Continue pagination (keyset)

- **Rule**: continuation uses the cursor `(occurred_at, txn_id)` bound to the session snapshot.
- **Guarantees within a session**: no duplicates, no skips, no order drift, even as new
  transactions arrive or statuses change (FR-020, EC-14, EC-15).
- **Status changes**: reflected on an explicit refresh, not by reordering an in-flight session.
- **Traces**: FR-020, FR-024; SC-004.

## H3 — Authorization binding

- **Rule**: non-owner requests are `denied` and audited; no transaction data is disclosed
  (FR-023, EC-16).
- **Data**: entries expose only masked/tokenized identifiers; prohibited fields never returned
  (FR-021, Constitution VI).

## Event Representation

| Type | Meaning | Counter effect |
|------|---------|----------------|
| authorization | Original hold/charge attempt | adds to cumulative if approved |
| capture (incl. partial) | Settlement (≤ authorized) | reconciles; no double-count (FR-016) |
| reversal | Auth released | subtracts previously added |
| refund | Post-settlement return | distinct entry; documented counter effect |

## Correctness Fixture (validation)

- **Fixture**: 100,000 synthetic transactions across 24 months, with interleaved arrivals and status
  changes during pagination.
- **Pass**: zero duplicates, skips, order drift, authorization leaks, or prohibited fields
  (SC-004).
