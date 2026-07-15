# Quickstart & Validation Scenarios (Synthetic)

**Feature**: [spec.md](spec.md) · **Date**: 2026-07-15

> These are documented validation scenarios, not executable tests. All data is synthetic. Each maps
> to a Success Criterion (SC) and the requirements it exercises.

## Preconditions (hypothetical fixtures)

- Synthetic cardholder `CH-001` owning card `TKN-CARD-001` (currency USD, `active`).
- Synthetic ops agent `OPS-001` with open case `CASE-77` and a 30-minute grant.
- Synthetic compliance reviewer `CMP-001` with a time-boxed export grant.
- Synthetic transaction fixture: 100,000 events across 24 months on `TKN-CARD-001`.

## Scenario 1 — Freeze reflects quickly (SC-001, SC-002)

1. `CH-001` freezes `TKN-CARD-001`.
2. Expect: state `frozen` within p95 ≤ 2s; downstream confirmation/consistency within p95 ≤ 5s;
   audit event present. (FR-001..FR-005)

## Scenario 2 — Fail-closed unfreeze (SC-006)

1. Add a synthetic `ops` restriction (via `OPS-001`/`CASE-77`).
2. `CH-001` attempts unfreeze.
3. Expect: `denied`, no case detail leaked, card stays `frozen`, denial audited. Never `pending`.
   (FR-007, FR-008, EC-04, EC-05)

## Scenario 3 — Exact limit enforcement (FR-013, EC-08, EC-09)

1. Set per-transaction limit 50.00 USD (5000 minor units).
2. Replay authorizations: 50.00 → approved; 50.01 → declined.
3. Cross a daily boundary at issuer midnight (incl. a DST day): counters reset correctly, no
   double-count.

## Scenario 4 — Concurrency single-winner (SC-005)

1. Submit 20 limit-change commands with the same `base_version`.
2. Expect: exactly one `success`, nineteen `conflict`; zero lost updates. (FR-017, EC-10)

## Scenario 5 — Idempotent replay (SC-008)

1. Send a freeze; within 24h replay the identical command (same idempotency key + payload).
2. Expect: original outcome returned; zero duplicate side effects/audit. (FR-004, FR-031)
3. Replay with a *different* payload under the same key → `conflict`. (FR-032, EC-12)

## Scenario 6 — Stable history at scale (SC-004)

1. Page through the 100k/24-month fixture while injecting new arrivals + status changes.
2. Expect: zero duplicates, skips, order drift, authorization leaks, or prohibited fields.
   (FR-019..FR-024)

## Scenario 7 — Least-privilege oversight (FR-025, FR-029)

1. `OPS-001` acts within `CASE-77` (open, unexpired) → allowed, audited.
2. Close `CASE-77`; retry → `denied` (fail-closed), audited. (EC-18, EC-19)

## Scenario 8 — Compliance export allowlist (FR-027, FR-028)

1. `CMP-001` exports `TKN-CARD-001` activity.
2. Expect: only current allowlisted fields; prohibited fields absent; size bounded; audited with
   purpose/scope. Request for a non-allowlisted field → omitted/rejected. (EC-20, EC-21)

## Scenario 9 — Missing-evidence recovery (SC-007)

1. Simulate an action whose audit evidence fails to reconcile.
2. Expect: alert ≤ 60s; recovery/degraded-mode path; incident escalation at 5/15 min. (FR-034, EC-22)

## Coverage map

| Scenario | Success Criteria |
|----------|------------------|
| 1 | SC-001, SC-002, SC-003 |
| 2 | SC-006 |
| 3 | (FR-013/014 boundary correctness) |
| 4 | SC-005 |
| 5 | SC-008 |
| 6 | SC-004 |
| 7 | SC-003 |
| 8 | SC-003 |
| 9 | SC-007 |
