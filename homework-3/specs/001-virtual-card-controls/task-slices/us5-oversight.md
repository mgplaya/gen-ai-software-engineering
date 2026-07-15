# Low-Level Tasks — US5: Perform Internal Oversight

These are hypothetical future implementation slices. Homework 3 documents but does not execute them.

## Internal authorization

- **LL-US5-01 — Enforce current role, case, purpose, and action authorization** (`OBJ-004`, `OBJ-005`; `FR-031–FR-032`, `FR-034–FR-037`; `NFR-001`). Re-evaluate authoritative identity, active least-privilege role, assigned open unexpired case, enumerated purpose, and exact permission for every search/read/freeze/export. **Done when:** all unspecified cells deny without confirming target existence and every allowed/denied outcome is attributable.

## Operations controls

- **LL-US5-02 — Place an emergency operations freeze and enforce abuse limits** (`FR-031–FR-034`, `FR-037`, `FR-041`; `NFR-001`, `NFR-004`, `NFR-011`). Require an allowed operations purpose, current risk policy, enumerated reason, expected version, and durable local block before adding only `OPS_FREEZE`; deny release, export, or limit changes. **Done when:** the 20/21-subject boundary, 15-minute search block, 60-second propagation alert, and 15-minute escalation are deterministic.

## Compliance evidence and export

- **LL-US5-03 — Provide scoped read-only evidence and export** (`FR-031–FR-032`, `FR-035–FR-040`; `NFR-001–NFR-003`, `NFR-012`). Bind one export to one assigned open compliance case, approved purpose, current step-up, a current approved/versioned purpose-bound field allowlist, ≤10,000 records, 24-hour expiry, attribution/watermark, correlation, and audit intent. **Done when:** absent/stale/mismatched allowlist policy, cross-case, operations, oversized, expired, and non-step-up exports deny; approved abuse/policy failures alert without target leakage.

## Audit and recovery

- **LL-US5-04 — Reconcile immutable audit evidence separately from diagnostics** (`OBJ-005–OBJ-006`; `FR-037–FR-041`; `NFR-002–NFR-003`, `NFR-007`, `NFR-011–NFR-012`). Give every distinct command/privileged outcome one root audit identity; exact retries reference the original without a second business event, while pending propagation and final reconciliation use immutable linked evidence under that root. Publish/replay idempotently, create linked corrections, and keep diagnostics sanitized and non-authoritative. **Done when:** every result category reconciles deterministically, absence alerts at five seconds, recovery completes by five minutes or remains degraded-safe, and a 15-minute absence becomes an incident.

## Verification

- **LL-US5-05 — Verify internal authorization, abuse, export, evidence, and recovery** (`EC-004–EC-006`, `EC-015–EC-020`, `EC-023–EC-024`; `SC-005–SC-007`). Cover the full role×case-status×purpose×action matrix, 20/21 subjects, 10,000/10,001 records, step-up expiry, delayed/duplicate evidence, correction, degraded-safe decisions, taxonomy, retention, deletion, and holds. **Done when:** all allowed cells succeed, all denied cells leak no target data, and 100% of outcomes reconcile to one evidence identity with zero prohibited categories.
