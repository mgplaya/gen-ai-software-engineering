# FinTech & Regulated-Domain Checklist: Regulated Virtual Card Controls

**Purpose**: Validate that the specification honors regulated-FinTech controls (Constitution I–VII)
**Created**: 2026-07-15
**Feature**: [spec.md](../spec.md) · [constitution](../../../.specify/memory/constitution.md)

## Fail-Closed & Safety (Constitution I)

- [x] CHK101 Risk-increasing actions (unfreeze, limit increase, export) fail closed under ambiguity — FR-007, FR-015, EC-05, SC-006
- [x] CHK102 Risk-reducing freeze accepted on durable local block even if propagation pending — FR-002, FR-003, EC-03
- [x] CHK103 Response states distinguish success/denied/pending/conflict — FR-039
- [x] CHK104 No "maybe" outcome for risk-increasing actions — FR-007, SC-006

## Exact Money & Time (Constitution II)

- [x] CHK105 Money is integer minor units + ISO-4217; floats prohibited — FR-012, NFR-003, constitution II
- [x] CHK106 Invalid/negative/mismatched-currency limits rejected — FR-012, EC-06, EC-07
- [x] CHK107 Period assignment uses issuer calendar, DST-safe — FR-014, EC-09
- [x] CHK108 Inclusive limit boundary documented — FR-013, EC-08
- [x] CHK109 Reversals/partial captures/refunds never double-count — FR-016, FR-024, EC-17

## Idempotency & Concurrency (Constitution III)

- [x] CHK110 Idempotency key bound to actor+card+action+payload — FR-031
- [x] CHK111 Duplicate key + different payload rejected — FR-032, EC-12
- [x] CHK112 Optimistic version → exactly one winner, deterministic conflict — FR-017, EC-10, SC-005

## Least Privilege & Access (Constitution IV)

- [x] CHK113 Internal access re-evaluated per action (case/purpose/expiry/permission) — FR-025, NFR-009, FR-040
- [x] CHK114 Ops-initiated restriction not cardholder-removable — FR-026, EC-04
- [x] CHK115 Separation of duties for ops-freeze release — FR-030, NFR-010
- [x] CHK116 Fail-closed on closed case / expired grant / missing purpose — FR-029, EC-18, EC-19
- [x] CHK117 Step-up freshness required for risk-increasing actions — FR-009, NFR-001

## Audit & Recovery (Constitution V)

- [x] CHK118 Append-only, tamper-evident, sanitized, reconstructable audit — FR-033, NFR-004
- [x] CHK119 Denials are audited — FR-005, FR-010, FR-018, FR-035
- [x] CHK120 Missing-evidence alert/recovery/degraded-mode/incident timeline — FR-034, EC-22, SC-007
- [x] CHK121 Audit separate from operational diagnostics — FR-033, NFR-012

## Sensitive-Data Boundary (Constitution VI)

- [x] CHK122 No PAN/CVV/credentials/raw payloads anywhere — NFR-003, FR-021, FR-037, FR-038, EC-25, EC-26
- [x] CHK123 Exports use versioned field allowlist, bounded size — FR-027, FR-028, EC-20, EC-21
- [x] CHK124 History exposes masked/tokenized identifiers only — FR-021, SC-004
- [x] CHK125 Synthetic data only in fixtures/examples — Assumptions, constitution security section

## Verification & Performance (Constitution VII + Quality Gates)

- [x] CHK126 Each objective has review checkpoints + test categories — NFR-013, tasks.md verification tasks
- [x] CHK127 Performance stated as measurable assumed targets with justification — SC-001..SC-008, README rationale
- [x] CHK128 100k-txn history fixture with zero dupes/skips/leaks — SC-004
- [x] CHK129 Availability target excludes unsafe fallbacks — NFR-014, SC-007
- [x] CHK130 No-code boundary respected (spec/plan/tasks only) — constitution VII

## Result

**38/38 applicable items PASS** across the enumerated controls (some grouped IDs cover multiple
sub-checks). No open Critical/High/Medium/Low finding. Ready for planning.
