# Low-Level Tasks — US4: Review Card Transactions

These are hypothetical future implementation slices. Homework 3 documents but does not execute them.

## Query and item

- **LL-US4-01 — Return only the owner's sanitized transaction items** (`OBJ-003`, `OBJ-006`; `FR-022–FR-025`, `FR-028`, `FR-030`). Re-evaluate ownership for every request/continuation and expose only immutable opaque identity, masked card, safe label, exact signed amounts/currencies, occurrence and status times, approved statuses, linked refund identity, and freshness. **Done when:** no unauthorized or taxonomy-prohibited field can appear, including in failures.

## Paging

- **LL-US4-02 — Traverse a stable snapshot with bound keyset continuation** (`FR-026–FR-028`; `NFR-010`, `NFR-014`; `EC-011–EC-013`). Bind owner/card/filters/order/source snapshot or `as of` and continue after `occurrence_instant DESC, transaction_id DESC`; default to 50 and cap at 100. **Done when:** arrivals or status changes cause zero duplicate, gap, or reorder and refresh starts a new context.

## Freshness and availability

- **LL-US4-03 — Distinguish fresh, empty, stale, and unavailable truthfully** (`FR-029`; `NFR-006–NFR-007`, `NFR-013`; `EC-014`). A complete healthy snapshot ≤60 seconds may be fresh or empty; a trusted snapshot >60 seconds and ≤15 minutes is `STALE` even if health reports healthy, and any degraded trusted snapshot ≤15 minutes is also `STALE`; absent or >15-minute evidence is `UNAVAILABLE`. **Done when:** every response includes the correct category and exact `as of` where stale, with no fabricated empty state.

## Verification

- **LL-US4-04 — Verify access, traversal, time, status, and privacy** (`EC-001`, `EC-011–EC-015`, `EC-022`, `EC-026`; `SC-004`, `SC-007`). Traverse 100,000 synthetic items with tied times, arrivals, status evolution, refunds, currencies, DST display, ownership changes, and each freshness category. **Done when:** there are zero unauthorized items, prohibited fields, duplicates, gaps, or order drift and the first-page assumed p95 target is measurable.
