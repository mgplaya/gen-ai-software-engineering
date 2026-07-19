# Task Slice US3 — Spending limits (P3)

**Story**: [spec.md#user-story-3](../spec.md) · **Tasks**: T013, T014, T015 · **Objective**: OBJ-3

> Future implementation guidance (documented; no code produced now).

## T013 — Limit validation

- **Prompt (future)**: "Validate limit changes: integer minor units ≥ 1, currency equal to the
  card's, scope ∈ {per_transaction, daily, monthly}. Reject invalid input with a reason; no float
  money."
- **Would touch (hypothetical)**: `state/limits`, `controls/validate`.
- **Acceptance criteria**:
  - [ ] Negative/zero/non-integer/mismatched-currency limits → `denied` with reason (EC-06, EC-07).
  - [ ] No floating-point money anywhere.
- **Traces**: FR-011, FR-012; EC-06, EC-07.

## T014 — Atomic authorization evaluation

- **Prompt (future)**: "Evaluate each authorization atomically against per-transaction, daily, and
  monthly limits with an inclusive boundary; assign cumulative spend to issuer-calendar periods
  (DST-safe); adjust for reversals/partial captures/refunds without double-count."
- **Would touch (hypothetical)**: `state/limits`, `history/counters`.
- **Acceptance criteria**:
  - [ ] 50.00 approved / 50.01 declined against a 50.00 per-transaction limit (EC-08).
  - [ ] Daily/monthly counters reset at issuer midnight incl. DST days (EC-09).
  - [ ] Reversal/partial-capture/refund adjust counters correctly (EC-17).
- **Traces**: FR-013, FR-014, FR-016; EC-08, EC-09, EC-17.

## T015 — Risk asymmetry + concurrency + audit

- **Prompt (future)**: "Apply limit decreases atomically; fail-closed on increases when authorization
  is unconfirmed. Resolve concurrent same-version changes to exactly one winner + deterministic
  conflict. Audit all outcomes."
- **Acceptance criteria**:
  - [ ] Decrease applies atomically; increase under ambiguity → `denied`.
  - [ ] 20 same-version changes → 1 `success`, 19 `conflict` (EC-10, SC-005).
  - [ ] All changes audited.
- **Traces**: FR-015, FR-017, FR-018; EC-10; SC-005.
