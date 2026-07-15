# Task Slice US4 — Transaction history (P4)

**Story**: [spec.md#user-story-4](../spec.md) · **Tasks**: T016, T017 · **Objective**: OBJ-4

> Future implementation guidance (documented; no code produced now).

## T016 — Snapshot-bound keyset pagination

- **Prompt (future)**: "Implement history as most-recent-first keyset pagination bound to a session
  snapshot ordered by (occurred_at, txn_id), so concurrent arrivals/status changes cause no
  duplicates, skips, or order drift. Return an explicit empty state when there are none. Represent
  reversals/partial-captures/refunds distinctly."
- **Would touch (hypothetical)**: `history/pagination`, `history/cursor`.
- **Acceptance criteria**:
  - [ ] First page most-recent-first; continuation via cursor stable to snapshot (EC-14, EC-15).
  - [ ] Empty history → explicit empty state, not an error (EC-13).
  - [ ] Full paging of the 100k/24-month fixture → zero dupes/skips/order-drift (SC-004).
- **Traces**: FR-019, FR-020, FR-022, FR-024; EC-13, EC-14, EC-15; SC-004.

## T017 — Authorization binding + masked data

- **Prompt (future)**: "Bind history reads to the owner, re-checked at read time; deny + audit
  non-owner access; expose only masked/tokenized identifiers."
- **Would touch (hypothetical)**: `access/authorize-read`, `history/serialize`.
- **Acceptance criteria**:
  - [ ] Non-owner request → `denied` + audited; no data disclosed (EC-16).
  - [ ] Entries contain only masked/tokenized fields; no prohibited fields (SC-004).
- **Traces**: FR-021, FR-023, FR-040; EC-16.
