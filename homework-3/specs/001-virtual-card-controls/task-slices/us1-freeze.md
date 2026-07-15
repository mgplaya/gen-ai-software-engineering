# Low-Level Tasks — US1: Immediately Freeze a Card

These are hypothetical future implementation slices. Homework 3 documents but does not execute them.

## Freeze command

- **LL-US1-01 — Authorize and accept a cardholder freeze** (`OBJ-001`, `OBJ-005`, `OBJ-006`; `FR-001–FR-005`). Re-evaluate ownership, require `OPEN`, explicit confirmation, expected version, and a bound command identity. Atomically persist `USER_FREEZE`, incremented version, durable local authorization block, outcome, audit intent, and propagation intent. **Done when:** no accepted result exists without the local block; a satisfied-state request is an attributable no-op with no version or propagation mutation.

## Propagation and recovery

- **LL-US1-02 — Reconcile external freeze propagation** (`FR-003`, `FR-006`, `FR-041`; `NFR-004`, `NFR-008`, `NFR-011`). Publish the durable intent idempotently, return only `SUCCEEDED` or truthful `PENDING_PROPAGATION`, retry without weakening the restriction, alert at 60 seconds, and escalate at 15 minutes. **Done when:** duplicate delivery creates no second transition and unresolved propagation retains the local restriction throughout recovery.

## Verification

- **LL-US1-03 — Verify the freeze safety oracle** (`EC-001–EC-005`, `EC-015`, `EC-022`, `EC-024`; `SC-001`, `SC-006–SC-007`). Cover ownership loss, concurrent versions, duplicate/mismatched identity, local-boundary failure, delayed propagation, and post-freeze settlement of prior authorizations. **Done when:** every fixture has one sanitized outcome/audit identity, no unsafe acceptance, and a distinguishable final or pending message within the assumed targets.
