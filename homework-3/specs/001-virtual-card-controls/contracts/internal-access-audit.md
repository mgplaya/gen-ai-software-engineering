# Behavioral Contract: Internal Access & Audit

**Feature**: [../spec.md](../spec.md) · Conceptual pre/postconditions — **not** API/endpoint code.

## A1 — Ops case-scoped action

- **Pre (all re-evaluated at the moment of use, FR-025, FR-040)**: open assigned case; stated
  purpose; unexpired grant; fresh step-up; exact permission for the action.
- **Post (success)**: action attributed to the case; an `ops`-source restriction (if any) is not
  cardholder-removable (FR-026).
- **Denied (fail-closed)**: closed case / expired grant / missing purpose / insufficient permission
  (FR-029, EC-18, EC-19).
- **Release of ops restriction**: requires a distinct second authorized actor (FR-030, NFR-010).
- **Traces**: FR-025, FR-026, FR-029, FR-030.

## A2 — Compliance export (read-only)

- **Pre**: compliance role; time-boxed grant; stated purpose.
- **Post**: export contains only fields on the **current versioned allowlist**; prohibited fields
  never included; size/volume bounded (paginated or rejected beyond limit).
- **Denied**: request for non-allowlisted field → field omitted or export rejected (never returns
  prohibited data) (FR-027, FR-028, EC-20, EC-21).
- **Traces**: FR-027, FR-028; Constitution VI.

## A3 — Audit evidence (all business actions)

- **Rule**: every freeze, unfreeze, limit change, history access, export, and **denial** emits an
  append-only, tamper-evident, sanitized, attributable AuditEvent, separate from diagnostics.
- **Reconstructable**: the evidence stream alone can reconstruct who did what to which card and when
  (tokenized) (FR-033, FR-035).
- **Traces**: FR-005, FR-010, FR-018, FR-033, FR-035; SC-003.

## A4 — Missing-evidence recovery

- **Rule**: if an action lacks reconciled audit evidence, raise an alert within **60s**, follow a
  defined recovery/degraded-mode path, and open an incident with escalation at **5 / 15 minutes**;
  the action is treated as suspect until reconciled.
- **Traces**: FR-034, EC-22; SC-007.

## Access Decision Matrix

| Condition | Decision |
|-----------|----------|
| Open case + purpose + unexpired grant + fresh step-up + permission | allow (audited) |
| Any one missing/expired/stale | deny, fail-closed (audited) |
| Ops-restriction release by original placer alone | deny (needs second actor) |
| Export field not on allowlist | omit field / reject export |
| Export exceeds size bound | paginate or reject |
