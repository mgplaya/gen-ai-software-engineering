# Task Slice US1 — Freeze (P1, MVP)

**Story**: [spec.md#user-story-1](../spec.md) · **Tasks**: T008, T009 · **Objective**: OBJ-1

> Future implementation guidance (documented; no code produced now).

## T008 — Freeze command handling

- **Prompt (future)**: "Implement freeze so it succeeds when a durable local authorization block is
  recorded; the card reads `frozen` immediately and declines new authorizations even while downstream
  propagation is `pending`. Emit an audit event. Never require downstream confirmation to report
  frozen."
- **Would touch (hypothetical)**: `controls/freeze`, `state/composite-card-state`, `audit/emit`.
- **Details**: risk-reducing action; outcome `success` with `propagation=pending` allowed; matches
  contracts/control-commands.md C1.
- **Acceptance criteria**:
  - [ ] Freezing an active synthetic card yields `frozen` and a durable local block.
  - [ ] Subsequent synthetic authorizations are declined by the local block.
  - [ ] `propagation=pending` does not weaken the block.
  - [ ] One audit event recorded (actor, card token, action, time).
- **Traces**: FR-001, FR-002, FR-003; EC-03; SC-001, SC-002.

## T009 — Freeze idempotency + audit

- **Prompt (future)**: "Make freeze idempotent on the command's idempotency key; a repeat produces
  no duplicate restriction or audit event and returns the original outcome."
- **Would touch (hypothetical)**: `controls/idempotency`, `audit/emit`.
- **Acceptance criteria**:
  - [ ] Replaying the same freeze key returns the original outcome.
  - [ ] No duplicate restriction or audit event is created (EC-01).
  - [ ] Every attempt (incl. failures) is audited.
- **Traces**: FR-004, FR-005; EC-01.
