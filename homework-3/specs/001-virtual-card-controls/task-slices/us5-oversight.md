# Task Slice US5 — Internal oversight (P5)

**Story**: [spec.md#user-story-5](../spec.md) · **Tasks**: T018, T019 · **Objective**: OBJ-5

> Future implementation guidance (documented; no code produced now).

## T018 — Ops case-scoped action authorization

- **Prompt (future)**: "Authorize each ops action by re-evaluating, at the moment of use: open
  assigned case, stated purpose, unexpired grant, fresh step-up, and the exact permission. Fail
  closed on any gap. Attribute the action to the case; an ops restriction is not cardholder-removable."
- **Would touch (hypothetical)**: `access/case-scope`, `access/authorize-action`, `state/restrictions`.
- **Acceptance criteria**:
  - [ ] Action within open case + valid grant → allowed + audited.
  - [ ] Closed case / expired grant / missing purpose → `denied` (fail-closed) + audited
    (EC-18, EC-19).
  - [ ] Ops restriction cannot be cleared by cardholder unfreeze.
- **Traces**: FR-025, FR-026, FR-029, FR-040; EC-18, EC-19.

## T019 — Compliance export

- **Prompt (future)**: "Produce read-only compliance exports limited to a current, versioned field
  allowlist; exclude prohibited fields; bound size (paginate or reject beyond the limit); audit with
  purpose and scope."
- **Would touch (hypothetical)**: `export/allowlist`, `export/paginate`, `audit/emit`.
- **Acceptance criteria**:
  - [ ] Export contains only current allowlisted fields; prohibited fields absent (EC-20).
  - [ ] Oversize export → paginated or rejected with guidance; never unbounded (EC-21).
  - [ ] Export audited with purpose/scope; non-allowlisted field request → omitted/rejected.
- **Traces**: FR-027, FR-028; EC-20, EC-21.
