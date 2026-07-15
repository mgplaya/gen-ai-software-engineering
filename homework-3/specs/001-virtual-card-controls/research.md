# Phase 0 Research: Regulated Virtual Card Controls

**Date**: 2026-07-15 · **Feature**: [spec.md](spec.md) · **Plan**: [plan.md](plan.md)

Each decision records the choice, rationale, and rejected alternatives. All are conceptual (no code).

## R1 — Composite card state (lifecycle × restriction sources)

- **Decision**: Model card state as two orthogonal dimensions: lifecycle (`active`/`frozen`/`closed`)
  and a set of restriction sources (`cardholder`/`ops`/`fraud`). The strongest applicable
  restriction governs whether authorizations pass.
- **Rationale**: Prevents a cardholder unfreeze from silently clearing an ops/fraud block
  (Constitution I, IV; FR-026, FR-036).
- **Rejected**: A single enum status — collapses independent sources and enables privilege bypass.

## R2 — Durable local block vs downstream propagation

- **Decision**: A freeze is effective the instant a **durable local authorization block** is
  recorded; downstream processor propagation may report `pending` without weakening the block.
- **Rationale**: Freeze is risk-reducing; waiting for eventual downstream confirmation would delay
  safety. Truthfully reporting `pending` avoids over-claiming (FR-002, FR-003, EC-03, NFR-005).
- **Rejected**: Requiring downstream confirmation before "frozen" — slower and less safe.

## R3 — Exact money and time

- **Decision**: Integer minor units + explicit ISO-4217 currency for all amounts; immutable UTC
  occurrence instant per transaction; period assignment via the issuer billing calendar with DST-safe
  boundaries.
- **Rationale**: Eliminates float drift and timezone-based limit evasion (Constitution II; FR-012,
  FR-014, EC-07, EC-09).
- **Rejected**: Floating-point money; viewer-local period boundaries.

## R4 — Idempotency + optimistic concurrency

- **Decision**: Every command carries an idempotency key bound to actor+card+action+payload and a
  base version. Identical replays within a 24h window return the original outcome; concurrent writes
  resolve to exactly one winner via version check.
- **Rationale**: Retries and races are normal; correctness must not depend on their absence
  (Constitution III; FR-031, FR-032, FR-017, SC-005, SC-008).
- **Rejected**: Last-write-wins (lost updates); server-generated keys (can't dedupe client retries).

## R5 — Transaction history pagination

- **Decision**: Snapshot-bound **keyset** pagination ordered by (occurrence instant, tiebreaker id),
  most-recent-first. A pagination session pins a snapshot so concurrent arrivals/status changes do
  not cause duplicates, skips, or order drift.
- **Rationale**: Offset pagination drifts under concurrent writes at 100k-row scale (FR-020, EC-14,
  EC-15, SC-004).
- **Rejected**: Offset/limit pagination; unstable sort keys.

## R6 — Audit separated from diagnostics

- **Decision**: Business audit evidence is an append-only, tamper-evident, sanitized stream, distinct
  from operational logs/metrics. Denials are audited. Missing evidence triggers a defined
  alert/recovery/incident timeline.
- **Rationale**: Regulators and disputes need a reconstructable business trail; diagnostics have
  different retention/content rules and must not carry prohibited data (Constitution V; FR-033,
  FR-034, FR-035, NFR-012).
- **Rejected**: Reusing application logs as the audit trail.

## R7 — Least-privilege internal access

- **Decision**: Per-action authorization re-evaluates ownership/role, open assigned case, purpose,
  grant expiry, step-up freshness, and exact permission. Ops-freeze release requires a distinct
  second authorized actor (separation of duties).
- **Rationale**: Standing broad access is an insider-risk and audit weakness (Constitution IV; FR-025,
  FR-029, FR-030, NFR-009, NFR-010; NIST SP 800-53 AC-5/AC-6).
- **Rejected**: Role-implied standing access; self-release of ops restrictions.

## R8 — Sensitive-data handling

- **Decision**: Reference cards by token or masked PAN (≤ first-6/last-4, only where justified);
  exports use a versioned field allowlist and are size-bounded; notes are sanitized; raw processor
  payloads are never surfaced or stored.
- **Rationale**: Minimizes blast radius of any leak (Constitution VI; FR-021, FR-027, FR-028, FR-037,
  FR-038, NFR-002, NFR-003).
- **Rejected**: Full PAN anywhere; unbounded exports; storing raw downstream payloads.

## R9 — Performance/consistency targets (assumed)

- **Decision**: Adopt SC-001..SC-008 as assumed targets (p95 2s/5s, 60s alert, 5/15m recovery, 99.9%
  monthly, 24h idempotency, 100k/24-month fixture).
- **Rationale**: Reasonable FinTech UX/ops envelopes; justified in the README; to be validated against
  real SLIs before production (NFR-008, NFR-014).
- **Rejected**: Vague "fast/reliable" with no numbers.
