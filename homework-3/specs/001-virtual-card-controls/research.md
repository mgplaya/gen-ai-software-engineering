# Phase 0 Research and Decision Record: Regulated Virtual Card Controls

**Date**: 2026-07-15
**Input**: Gate-1-approved `spec.md` (`SHA-256: 7cdd28c597f5c0ed440337eefc4a5b229b5eff9f909fa56a6582b5ef4a2a9ed9`)
**Scope**: Documentation-only planning; all technical choices below are hypothetical, replaceable
assumptions and MUST NOT be interpreted as new product requirements.

## Decision R-001 — Architectural Shape

**Decision**: Describe a hypothetical modular monolith with ports/adapters. Conceptual boundaries are:
cardholder/internal presentation, Control Application, Authorization and Policy, Control Store,
Processor Propagation, Transaction History Query, Compliance Evidence/Export, Reconciliation, Audit
Evidence, and sanitized Diagnostics/Alerts.

**Rationale**: The approved behavior needs explicit ownership, durable state transitions, and failure
boundaries, but Homework 3 does not justify distributed deployment complexity. The architecture is
implementable as one service while preserving module seams for later extraction.

**Alternatives considered**:

- **Microservices**: independent scaling is possible, but distributed transaction, propagation, and
  audit failure surfaces add unapproved complexity.
- **Single undifferentiated module**: simpler initially, but obscures authorization, evidence, and
  external-boundary responsibilities required by the spec.

## Decision R-002 — Durable Control State

**Decision**: Assume one ACID relational control store for lifecycle/restriction flags, limit state,
command identity/outcome, version predicates, and same-boundary audit/propagation intent. Describe a
transactional outbox pattern conceptually; do not create schemas or migrations.

**Rationale**: `FR-003`, `FR-018–FR-020`, `FR-038–FR-041`, `NFR-004`, `NFR-008`, and `NFR-009` require
atomic durable local blocking, exactly one expected-version winner, idempotent outcomes, and durable
evidence intent.

**Alternatives considered**:

- **Event sourcing**: richer history, but projection, correction, privacy, and operational complexity
  exceed the homework need.
- **Separate state/audit databases on the command path**: cannot naturally guarantee the approved
  same-acceptance-boundary invariant.
- **In-memory state**: incompatible with durability, recovery, and concurrency requirements.

## Decision R-003 — External Propagation and Recovery

**Decision**: Model processor propagation and audit publication as asynchronous, idempotent adapters
driven by durable intent and reconciliation timers. The synchronous command path exposes only the
approved normative result categories.

**Rationale**: Freeze can truthfully return `PENDING_PROPAGATION` only after local safety is durable;
other ambiguous writes fail closed. This preserves the approved result and recovery model without
blocking indefinitely on external systems.

**Alternative considered**: waiting synchronously for every downstream confirmation would undermine
the approved pending/fail-safe model and latency assumptions.

## Decision R-004 — Transaction History Read Model

**Decision**: Use a read-only ledger/processor port with snapshot-bound keyset continuation tied to
owner, card, filters, normative ordering, and `as of` context. If the external source cannot provide a
stable snapshot, assume a sanitized issuer-owned read projection.

**Rationale**: Offset pagination cannot satisfy `FR-026–FR-029` and `NFR-010` when transactions arrive
or change status during traversal.

**Alternatives considered**:

- **Offset pagination**: rejected because it permits duplicates/gaps.
- **Copy all processor data into the control store**: increases sensitive-data and synchronization
  scope without an approved need.

## Decision R-005 — Audit Evidence vs Diagnostics

**Decision**: Keep business audit evidence and diagnostic logging as separate conceptual contracts and
stores. Corrections are new linked events; original evidence meaning is immutable. Diagnostics never
substitute for business evidence.

**Rationale**: The approved taxonomy, recovery deadlines, retention assumptions, and access purposes
differ materially between evidence and operational troubleshooting.

**Alternative considered**: a generic application log is easier to start but cannot satisfy explicit
attribution, reconciliation, correction, access, retention, and tamper-evidence requirements.

## Decision R-006 — Contract Artifact Format

**Decision**: Create conceptual Markdown contracts for command envelopes/results, state invariants,
limit accounting, transaction queries/items/cursors, internal authorization/exports, audit events,
data taxonomy, and recovery timelines.

**Rationale**: The homework requires implementable documentation but explicitly prohibits APIs and
implementation. Prose tables and scenarios capture preconditions/postconditions without selecting an
HTTP shape, serialization format, or vendor.

**Alternatives considered**:

- **OpenAPI/JSON Schema**: executable interface design exceeds the approved documentation scope.
- **Narrative only**: insufficiently precise for traceable tasks and verification.

## Decision R-007 — Illustrative Future Stack

**Decision**: For `agents.md` and hypothetical path conventions, assume the existing course pattern:
Node.js 22, TypeScript 5.7, NestJS 11, Jest 29, and Supertest 7, with a PostgreSQL-like ACID relational
store and vendor-neutral identity, processor, case, queue/outbox, monitoring, and audit integrations.

**Rationale**: Homework 1 and Homework 2 already use this Node/NestJS/TypeScript family. Reusing the
course vocabulary reduces incidental decisions while relational semantics fit durability/concurrency
requirements better than the prior in-memory exercises.

**Limitations**: No package is installed, no source path is created, PostgreSQL/queue vendors and
versions are not selected, and the stack remains a plan assumption replaceable after impact review.

**Alternative considered**: a language/vendor-neutral plan would reduce assumptions but would make
the required tech-stack guidance and future file-level tasks less concrete.

## Decision R-008 — Canonical Graded Artifact

**Decision**: After Gate 2, generate and analyze `tasks.md` first. Then publish
`homework-3/specification.md` as the exact approved product body plus a clearly delimited low-level-task
section synchronized from the validated `tasks.md`. Validate product-body semantic equivalence against
the Gate 1 hash separately from task parity/traceability. The graded file then becomes canonical;
Spec Kit `spec.md` and `tasks.md` remain provenance/mirrors that MUST be reconciled explicitly.

**Rationale**: `TASKS.md` requires the canonical graded specification itself to contain substantial
low-level tasks. Publishing after task validation satisfies that requirement without mutating the
Gate-1-approved product semantics or maintaining competing authoritative drafts. The current
`Status: Draft` header is left untouched because changing the approved file would change its hash;
approval truth is recorded in `.specify/memory/approvals.md`.

**Alternatives considered**:

- Publishing the approved product body unchanged would omit the assignment-required task section.
- Editing both files throughout drafting risks silent divergence.
- Adding the validated downstream task section is not a silent product-semantic change; any product
  body change still invalidates Gate 1 and requires re-approval.

## Decision R-009 — Security, Payment-Data, Identity, and Privacy References

**Decision**: Use the following as non-jurisdictional control and verification references, never as a
claim of certification or legal compliance:

1. **PCI DSS v4.0.1** — Requirements 3, 7, 8, and 10 inform account-data minimization/protection,
   need-to-know access, identification/authentication, and logging/monitoring. Source:
   [PCI SSC Document Library](https://www.pcisecuritystandards.org/document_library/) and
   [PCI SSC v4.0.1 publication notice](https://blog.pcisecuritystandards.org/just-published-pci-dss-v-4-0-1).
   Applicability and Cardholder Data Environment scope require issuer/acquirer and assessor review.
2. **NIST SP 800-53 Rev. 5, Release 5.2.0** — AC-2/3/5/6, IA-2, and AU-2/3/9/12 provide control
   vocabulary for account/access enforcement, separation of duties, least privilege, identity, audit
   content/protection/generation. Source:
   [NIST SP 800-53 Rev. 5](https://csrc.nist.gov/Pubs/sp/800/53/r5/upd1/Final). It is a tailorable
   control catalog, not a product compliance baseline.
3. **NIST SP 800-63B-4** — informs current reauthentication/step-up, authenticator assurance, session,
   replay resistance, authentication intent, and rate-limiting considerations. Source:
   [NIST SP 800-63B-4](https://pages.nist.gov/800-63-4/sp800-63b.html). It does not prescribe a specific
   assurance level for virtual-card unfreeze; issuer risk must do so.
4. **OWASP ASVS 5.0.0** — version-pinned application-security verification vocabulary for
   authentication/session, authorization, sensitive data, safe errors, and logging. Source:
   [OWASP ASVS](https://owasp.org/www-project-application-security-verification-standard/) and
   [official repository](https://github.com/OWASP/ASVS). It is guidance, not a payment or legal
   certification.
5. **NIST Privacy Framework 1.0** — stable voluntary privacy-risk vocabulary for inventory, purpose,
   governance, access, retention, and monitoring. Source:
   [NIST Privacy Framework](https://www.nist.gov/privacy-framework). Draft revisions do not replace
   the stable planning baseline; jurisdiction-specific duties remain deferred to legal review.

## Verification Design Decision

Document, but do not execute, the following future evidence:

- composite-state table and actor-owned transition review;
- exact-money, billing-period/DST, hold/post/reversal/refund, and FX boundary fixtures;
- 20-way expected-version schedule plus idempotency mismatch reconciliation;
- owner/role/case/purpose/action negative matrix and abuse/export thresholds;
- 100,000-item snapshot paging traversal with tied timestamps and concurrent arrivals;
- outcome-to-audit event reconciliation with delayed sink, duplicate replay, correction, and incident
  timelines;
- canonical prohibited-data category scan per surface plus manual privacy review;
- healthy/degraded SLI ledger for 2-second, 5-second, 60-second, 5-minute, and 15-minute targets;
- accessibility/content review distinguishing final, pending, denied, stale, and unavailable states.

## Non-Blocking Assumptions and Feasibility Risks

- Jurisdiction, production traffic, policy ranges, vendors, and observed SLOs intentionally remain
  approved assumptions requiring pre-production validation.
- The authorization processor must synchronously honor the durable local restriction boundary. If it
  cannot, `FR-003`/`NFR-004` feasibility must be escalated and the specification re-approved.
- Stable transaction snapshots must exist at the processor/ledger boundary or require the sanitized
  issuer read projection described in R-004.
- Student name and final editor-rules location are package-completion inputs, not planning blockers;
  `.github/copilot-instructions.md` is the recommended rules artifact.

## Research Completion

All planning unknowns are either resolved as replaceable technical decisions above or explicitly
recorded as non-blocking approved assumptions. No `NEEDS CLARIFICATION` item remains.
