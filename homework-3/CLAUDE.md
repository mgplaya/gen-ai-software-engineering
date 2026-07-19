# Claude Code Rules — Regulated Virtual Card Controls (homework-3)

Editor/AI rules deliverable for Homework 3. Claude Code auto-loads this file as project rules when
working in `homework-3/`. It is the terse operational companion to the fuller
[`AGENTS.md`](AGENTS.md) and the authoritative [`Constitution`](.specify/memory/constitution.md).

## Golden rule

**This is a documentation-only spec package. Never write application code, APIs, UIs, DB schemas,
migrations, package manifests, or infrastructure.** If a task implies implementation, stop and
confirm scope. `speckit-implement` is intentionally not run.

## Always

- Use integer minor units + ISO-4217 for money; immutable UTC + issuer-calendar (DST-safe) periods.
- Fail closed on risk-increasing actions (unfreeze, limit increase, export); accept risk-reducing
  actions on a durable local block (propagation may be `pending`).
- Bind every state-changing command to an idempotency key (`actor+card+action+payload`) and a
  `base_version`; prefer idempotent writes; resolve concurrency to exactly one winner.
- Reference cards by token or masked PAN (≤ first-6/last-4). Audit every action **and denial**.
- Re-check authorization at the moment of use (ownership/case/purpose/expiry/step-up/permission).
- Keep stable IDs (`OBJ/FR/NFR/EC/SC/T`); append new numbers, never renumber; add a `Traces:` line
  to each task; keep internal links resolving; ensure `git diff --check` passes.

## Never

- Never emit or log full PAN, CVV, track data, credentials, raw processor payloads, unrelated case
  data, or unredacted free text — anywhere, including examples/fixtures/prompts.
- Never use floating-point money.
- Never let a cardholder action clear an ops/fraud restriction; never allow ops-restriction release
  by a single actor (separation of duties).
- Never return `success`/`pending` for a risk-increasing action under ambiguity.
- Never claim certification, legal/jurisdictional compliance, accessibility conformance, or
  production readiness. Frameworks (PCI DSS, NIST 800-53/800-63B, NIST Privacy, OWASP ASVS) are
  references only.
- Never introduce real/production data; synthetic fixtures only.

## Naming & patterns

- Feature dir: `specs/001-virtual-card-controls/`. Requirement IDs are uppercase-hyphenated
  (`FR-013`). Outcomes are exactly `success | denied | pending | conflict`.
- Card state is composite (lifecycle × restriction sources); strongest restriction governs.

## Workflow

Follow the gated Spec Kit flow (constitution → specify → clarify → checklist → plan → tasks →
analyze) and keep the constitution authoritative — if an artifact conflicts with a principle, fix
the artifact. Route work cost-aware (mechanical=low, drafting=medium, security/compliance/gate
review=high).
