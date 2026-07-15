# Task Slice US2 — Unfreeze, fail-closed (P2)

**Story**: [spec.md#user-story-2](../spec.md) · **Tasks**: T010, T011, T012 · **Objective**: OBJ-2

> Future implementation guidance (documented; no code produced now).

## T010 — Fail-closed unfreeze decision

- **Prompt (future)**: "Implement unfreeze so it succeeds only when step-up is fresh AND restriction
  state is positively confirmed safe. On any ambiguity, deny — never return `pending`."
- **Would touch (hypothetical)**: `controls/unfreeze`, `access/step-up`, `state/restrictions`.
- **Acceptance criteria**:
  - [ ] Confirmed-safe + fresh step-up → card becomes `active`.
  - [ ] Ambiguous freshness/state → `denied` (never `success`/`pending`) (EC-05).
  - [ ] Risk-increasing nature requires fresh step-up (FR-009).
- **Traces**: FR-006, FR-007, FR-009; EC-05; SC-006.

## T011 — Stronger-restriction protection + separation of duties

- **Prompt (future)**: "Prevent a cardholder unfreeze from clearing an ops/fraud restriction.
  Require a distinct second authorized ops/compliance actor to release an ops-initiated freeze."
- **Would touch (hypothetical)**: `state/restrictions`, `access/separation-of-duties`.
- **Acceptance criteria**:
  - [ ] Cardholder unfreeze with ops/fraud restriction present → `denied`, card stays `frozen`,
    no case detail leaked (EC-04).
  - [ ] Ops-restriction release by the original placer alone → `denied` (needs second actor).
- **Traces**: FR-008, FR-026, FR-030, NFR-010; EC-04.

## T012 — Unfreeze audit

- **Prompt (future)**: "Audit every unfreeze attempt with a non-leaking reason."
- **Acceptance criteria**:
  - [ ] Success and denial both audited; denial reason contains no case detail.
- **Traces**: FR-010, FR-035.
