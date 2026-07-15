# Low-Level Tasks — US2: Safely Unfreeze a User-Frozen Card

These are hypothetical future implementation slices. Homework 3 documents but does not execute them.

## Unfreeze command

- **LL-US2-01 — Authorize removal of the user restriction only** (`OBJ-001`, `OBJ-005`, `OBJ-006`; `FR-007–FR-011`). Re-evaluate ownership, require `OPEN`, existing `USER_FREEZE`, current mandatory step-up, expected version, and unambiguous dependencies; remove only `USER_FREEZE`. **Done when:** operations, risk, unknown, and lifecycle restrictions cannot be removed and the effective status follows normative precedence.

## Failure and messaging

- **LL-US2-02 — Fail closed and disclose safely** (`FR-008–FR-011`, `FR-040`; `NFR-005–NFR-007`, `NFR-013`). Map denied, stale, expired-verification, conflict, and ambiguous dependency outcomes to approved categories without target or dependency leakage; prohibit `PENDING_PROPAGATION`. **Done when:** ambiguity produces terminal `TEMPORARILY_UNAVAILABLE`, no mutation, and accessible retry/support guidance rather than success.

## Verification

- **LL-US2-03 — Verify composite-state and dependency behavior** (`EC-002–EC-004`, `EC-006`, `EC-010`, `EC-015`, `EC-023–EC-024`; `SC-002`, `SC-006–SC-007`). Exercise every lifecycle/restriction combination, expired step-up, stale session, concurrent command, mismatched retry, and dependency failure. **Done when:** zero fixtures weaken a non-user restriction and every attempt reconciles to one sanitized evidence identity.
