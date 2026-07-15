# Low-Level Tasks — US3: Configure Spending Limits

These are hypothetical future implementation slices. Homework 3 documents but does not execute them.

## Limit command

- **LL-US3-01 — Validate and atomically replace the complete limit set** (`OBJ-002`, `OBJ-005`, `OBJ-006`; `FR-012–FR-021`). Require exact billing currency/scale, all three positive values, issuer bounds, `per-transaction ≤ daily ≤ monthly`, current policy, expected version, and applicable step-up; change all values and audit intent together or none. **Done when:** no partial update or binary floating-point interpretation is possible and only one distinct same-version command wins.

## Risk policy

- **LL-US3-02 — Enforce restricted-card decrease and active-card increase rules** (`FR-016–FR-017`, `FR-021`; `EC-006`, `EC-009–EC-010`, `EC-021`). While any restriction is active, allow only a complete non-increasing set with at least one decrease and unchanged components permitted; reject the entire set if any component increases. **Done when:** ambiguous or unverified increases fail closed and accepted decreases affect only new decisions.

## Allowance accounting

- **LL-US3-03 — Account for holds, posting, reversals, refunds, FX, and billing periods** (`FR-013–FR-016`; `NFR-014`; `EC-009`, `EC-012–EC-013`, `EC-025–EC-026`). Consume holds once, replace them with final posting amounts, release matching reversals, keep refunds as separate credits without historical replenishment, and reset issuer-timezone periods once. **Done when:** exact reconciliation preserves authorization-time and final FX evidence without retroactively reversing a valid decision.

## Verification

- **LL-US3-04 — Verify exact money, policy, concurrency, and accounting** (`EC-002–EC-003`, `EC-006–EC-010`, `EC-012–EC-013`, `EC-021`, `EC-024–EC-026`; `SC-003`, `SC-006–SC-007`). Use synthetic currency-scale, policy-edge, mixed-change, expired-step-up, duplicate/mismatch, 20-way concurrency, DST/month-boundary, incremental-hold, partial-reversal, refund, and FX fixtures. **Done when:** outcomes are deterministic, exactly one same-version winner exists, and final state/version/evidence reconcile exactly.
