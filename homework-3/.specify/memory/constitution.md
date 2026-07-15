<!--
Sync Impact Report
- Version change: (template) → 1.0.0
- Ratified: 2026-07-15
- Modified principles: initial adoption (all seven principles newly defined)
- Added sections: Core Principles (I–VII), Security & Compliance Standards,
  Verification & Quality Gates, Governance
- Removed sections: none
- Templates requiring updates:
  - ✅ .specify/templates/plan-template.md — Constitution Check gate reads from this file (no edit needed)
  - ✅ .specify/templates/spec-template.md — mandatory sections align with Principles I–VII
  - ✅ .specify/templates/tasks-template.md — task categories cover audit, security, verification
- Follow-up TODOs: none
-->

# Virtual Card Controls Constitution

This constitution governs the **specification package** for regulated virtual-card controls
(Homework 3). It is binding on every specification, plan, task, checklist, and review artifact in
this feature. It encodes the non-negotiable rules a regulated FinTech feature must satisfy so that
requirements can be traced from intent to future verification evidence without guesswork.

## Core Principles

### I. Fail-Closed on Risk-Increasing Actions (NON-NEGOTIABLE)

Any action that *increases* risk — unfreezing a card, raising a spending limit, or exporting
compliance data — MUST fail closed. When authorization, durability, or freshness cannot be
positively confirmed, the system MUST deny the action and MUST NOT return `success` or `pending`.
Risk-*reducing* actions (freeze, lower a limit) MAY be accepted the moment a durable local block is
recorded, even while downstream propagation is still pending.
**Rationale**: In payments, an ambiguous "maybe unfrozen" is a financial-loss and fraud vector; a
false "still frozen" is merely a retry. Safety asymmetry must be explicit, not incidental.

### II. Exact Money and Time (NON-NEGOTIABLE)

Monetary amounts MUST be represented as integer minor units with an explicit ISO-4217 currency;
floating-point money is prohibited anywhere in the spec, fixtures, or examples. Every transaction
carries an immutable occurrence instant (UTC) plus the issuer billing calendar/timezone used to
assign it to a daily or monthly period. Period boundaries MUST be DST-safe and defined against the
issuer calendar, never the viewer's locale.
**Rationale**: Rounding drift and timezone ambiguity are classic sources of limit-evasion,
reconciliation breaks, and disputed charges.

### III. Idempotent, Versioned Writes (NON-NEGOTIABLE)

Every state-changing command MUST carry a client-supplied idempotency key bound to
actor + card + action + payload. Replaying an identical command inside the idempotency window MUST
return the original outcome without repeating side effects. Concurrent writes to the same card MUST
use optimistic version checks so that exactly one command wins and losers receive a deterministic
conflict, never a lost update.
**Rationale**: Retries, double-taps, and race conditions are normal at scale; correctness cannot
depend on them not happening.

### IV. Least Privilege and Case-Scoped Access

Every sensitive read or action MUST re-evaluate, at the moment of use: ownership/role, an open
assigned case (for internal actors), stated purpose, grant expiry, step-up freshness, and the exact
permission required. Internal operations and compliance access are read-mostly, case-scoped, and
time-boxed; no standing broad access to cardholder data is permitted.
**Rationale**: Regulated environments require provable, minimal, purpose-bound access — not
role-implied trust.

### V. Append-Only, Tamper-Evident Audit

Business-significant events (freeze, unfreeze, limit change, history access, export, access denial)
MUST produce append-only, tamper-evident audit evidence that is sanitized, attributable, and
independently reconstructable. Audit evidence is separate from operational diagnostics/logs. Missing
or unreconciled evidence MUST trigger a defined alert, recovery, degraded-mode, and incident
timeline.
**Rationale**: If it is not auditable, it did not happen — regulators and disputes require a
reconstructable trail.

### VI. Sensitive-Data Boundary (NON-NEGOTIABLE)

Full PAN, CVV, track/chip data, credentials/secrets, raw downstream-processor payloads, unrelated
case data, and unredacted free text MUST NEVER appear in views, logs, audit evidence, exports,
fixtures, test data, prompts, or examples. Card references use tokens or masked PAN (first-6/last-4
at most, only where justified). Exports use an explicit, versioned field allowlist.
**Rationale**: Data-handling failures are the highest-severity, least-recoverable class of FinTech
incident.

### VII. Specification-First, No-Code Boundary

For this deliverable, no application source, executable API/UI, database schema, migration, package
manifest, dependency install, infrastructure, or deployment artifact may be produced. Work stops at
an implementation-ready specification package. Design documents describe hypothetical structure and
targets; they never install or mandate a concrete runtime.
**Rationale**: Homework 3 grades the specification. Clarity, layering, and traceability are the
product; premature code would obscure them.

## Security & Compliance Standards

- **Reference frameworks (as vocabulary and control references only, not certification claims)**:
  PCI DSS data-handling vocabulary, NIST SP 800-53 control families, NIST SP 800-63B for step-up
  assurance, NIST Privacy Framework for data minimization, OWASP ASVS for verification depth.
- **Authentication & step-up**: risk-increasing actions require fresh, re-verified authentication;
  session presence alone is insufficient.
- **Data minimization**: collect, display, and export the least data needed for the stated purpose;
  default to masked/tokenized references.
- **Synthetic data only**: all fixtures, examples, and scenarios use clearly synthetic,
  non-production values. Real cardholder data is prohibited.
- **No jurisdiction/legal claims**: the package does not assert regulatory certification, legal
  compliance for a specific jurisdiction, accessibility conformance, or production readiness.

## Verification & Quality Gates

- **Traceability**: every high-level objective decomposes to mid-level objectives → functional and
  non-functional requirements → low-level tasks, each with stable IDs (`OBJ`, `FR`, `NFR`, `EC`,
  `SC`, `LL`). No requirement may be orphaned; no task may exist without a parent requirement.
- **Acceptance criteria**: each low-level task ends with a checkable definition of done phrased so an
  implementer (human or agent) can verify it without re-reading the whole spec.
- **Edge cases as first-class**: empty states, partial/downstream failures, concurrency, invalid
  limits, stale reads, permission boundaries, and fraud-ish patterns are enumerated with expected
  user-visible outcome *and* audit/compliance implication.
- **Performance as targets**: latency percentiles, consistency windows, pagination, availability,
  and volume limits are stated as measurable **assumed targets** with justification — never "should
  be fast".
- **Gate reviews**: the package is validated at gates — spec quality (before plan), plan/design
  consistency, and a final cross-artifact analysis (coverage 100%, zero orphans, zero conflicts)
  before the package is considered done.

## Governance

- This constitution supersedes ad-hoc conventions for the virtual-card-controls feature. Where any
  spec, plan, or task conflicts with a principle here, the constitution wins and the artifact MUST
  be corrected.
- **Amendments** require: a written rationale, a semantic-version bump (MAJOR for
  incompatible principle removal/redefinition, MINOR for new principle/section, PATCH for
  clarifications), and a Sync Impact Report noting affected templates.
- **Compliance review**: every gate review and the final analysis MUST verify that the artifacts
  honor Principles I–VII; any violation is a blocking finding.
- **Runtime guidance**: `AGENTS.md` and the Claude Code rules (`homework-3/.claude/`) operationalize
  this constitution for AI collaborators and MUST stay consistent with it.

**Version**: 1.0.0 | **Ratified**: 2026-07-15 | **Last Amended**: 2026-07-15
