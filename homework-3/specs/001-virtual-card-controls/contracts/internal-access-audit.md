# Conceptual Contract: Internal Access, Audit Evidence, and Recovery

**Contract type**: Technology-neutral authorization, export, evidence, taxonomy, and recovery behavior
**Not included**: Identity vendor, endpoint, file format, storage technology, or monitoring product

## Current Authorization Decision

Every privileged search, read, freeze, or export re-evaluates:

- active actor identity and least-privilege role;
- authoritative case issuer, assignment, open status, enumerated purpose, and unexpired authorization;
- exact role×purpose×action permission;
- step-up outcome for compliance export;
- operations search and compliance export abuse thresholds.

No self-asserted or unenumerated "equivalent" purpose/authorization is accepted.

## Permission Matrix

| Role | Search/read | Emergency freeze | Change limits | Release restriction | Export |
|------|-------------|------------------|---------------|---------------------|--------|
| Cardholder | Owned card/history | Own user freeze | Owned card per policy | Own user flag only | No internal export |
| Operations | Assigned open case with `CUSTOMER_SUPPORT` or `URGENT_RISK_CONTAINMENT` | Add `OPS_FREEZE` under either purpose only with case, current policy, and enumerated reason | Never | Never through this feature | Never |
| Compliance | Assigned open case with `REGULATORY_REVIEW`, `CONTROL_INVESTIGATION`, or `AUDIT_EVIDENCE` | Never | Never | Never | One assigned case under its enumerated purpose after step-up; ≤10,000 sanitized records |

Wrong role/case/purpose, closed/expired/reassigned case, free-form operations freeze reason, operations
export, cross-case export, and oversized export are deterministic denials without target leakage.

## Abuse Boundaries

- More than 20 distinct card subjects by one operations actor in rolling five minutes denies further
  search for 15 minutes and alerts security operations.
- Compliance export beyond one case or 10,000 records is denied and alerted.
- Approved bulk investigations use separate tooling outside this feature.

## Compliance Export

An allowed export is bound to one actor/role, one assigned open case, enumerated purpose, current
step-up outcome category, explicit canonical-taxonomy allowlist, no more than 10,000 records, creation
and 24-hour expiry, attribution/watermark, correlation, and audit intent. Operations and unrelated-case
fields are prohibited.

## Audit Intent/Event Contract

| Element | Requirement |
|---------|-------------|
| Identity | Globally unique, shared by durable intent and published/replayed event |
| Acceptance | Durable audit intent recorded in same boundary as state change or privileged outcome |
| Content | Actor/role, opaque subject, action, enumerated reason/case, sanitized before/after, policy/result, time, correlation |
| Replay | Idempotent by event identity; duplicate delivery creates no duplicate business event |
| Correction | New linked corrective event; original meaning remains immutable |
| Protection | Append-only/tamper-evident evidence; unauthorized read/change/delete denied and audited; alerts are mandatory only for approved abuse/recovery conditions |
| Access | Assigned compliance/control readers under current case/purpose; canonical field allowlist |
| Retention | Assumed seven years with approved hold/deletion/disposition policy |

Diagnostic logs/alerts are separate: correlation, service/result/error category, timing, and sanitized
component metadata only. They contain no raw business payload or taxonomy-prohibited category and are
never the sole financial-control evidence.

## Recovery State and Timelines

| Time/condition | Required outcome and owner |
|----------------|----------------------------|
| Evidence queryability ≤5 seconds p95 | Normal evidence path |
| Evidence absent at 5 seconds | Security/compliance operations alert; duplicate-safe recovery active |
| Still absent at 5 minutes | Recovery deadline missed; degraded-safe mode remains and owner escalates |
| Still absent at 15 minutes | Security/control incident declared |

Degraded-safe mode rejects unfreeze, limit increases, privileged exports, and other risk-increasing
writes. It permits durable local freezes and authorized reads only when their audit intent can be
durably recorded.

## Canonical Data Taxonomy Application

Every surface uses the one approved taxonomy from `spec.md`:

- cardholder: owned masked card/transaction/control fields only;
- operations: assigned-case sanitized state, limits, and history; no export;
- compliance: assigned-case allowed evidence/export fields;
- business audit: opaque identities and enumerated/sanitized evidence fields;
- diagnostics: correlation/health/result fields only;
- fixtures/prompts/docs: clearly synthetic masked data only.

Zero occurrences of each prohibited category are required across views, evidence, diagnostics,
exports, failures, fixtures, prompts, and documents.

## Verification Oracles

- Complete role × open/closed/expired/reassigned case × purpose × action negative matrix.
- Boundary checks at 20/21 distinct operations subjects and 10,000/10,001 export records.
- Outcome-to-audit reconciliation: exactly one event identity per accepted/denied outcome.
- Duplicate replay, delayed sink, correction, five-minute recovery, and 15-minute incident timelines.
- Surface allowlist plus prohibited-category scan and independent privacy/compliance review.

## Traceability

`OBJ-004`, `OBJ-005`, `OBJ-006`; `FR-031–FR-041`; `NFR-001–NFR-003`, `NFR-011–NFR-013`;
`EC-004–EC-006`, `EC-015–EC-020`, `EC-023–EC-024`; `SC-005–SC-007`.
