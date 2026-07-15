# Homework 3: Regulated Virtual Card Controls

## Student and Task Summary

- **Student**: Mykhailo Gorishnyi
- **Course**: Agentic AI
- **Assignment**: Homework 3 — Specification-Driven Design
- **Selected domain**: Regulated virtual-card controls

This documentation-only submission turns the assignment's broad FinTech prompt into an
implementation-ready specification for freezing and unfreezing an existing virtual card, setting
spending limits, viewing transaction history, and supporting case-bound operations and compliance
oversight. It intentionally contains no application code, executable API or UI, schema, migration,
dependency, or deployment.

The canonical graded artifact is [specification.md](specification.md). Supporting agent guidance and
the active ChatGPT/Codex repository rules are in [AGENTS.md](AGENTS.md) (also reachable as
`agents.md` on this filesystem). The Spec Kit provenance package
under [specs/001-virtual-card-controls](specs/001-virtual-card-controls/) preserves the approved
product specification, plan, research decisions, conceptual contracts, checklists, and task routing.

On this case-insensitive APFS workspace, `AGENTS.md` and the assignment-required `agents.md` resolve
to one physical file. Operational and graded guidance remain logically distinct through explicit
delimiters; the operational section has precedence for repository collaboration.

## Rationale

### Why the specification is layered

The document moves from intent to executable detail so that a product reviewer can assess outcomes
without reading implementation notes, while a future engineering or AI agent can work without
inventing policy:

1. [High-Level Objective](specification.md#high-level-objective) defines the outcome and the scope
   boundary.
2. [Mid-Level Objectives](specification.md#mid-level-objectives) make success observable and connect
   it to evidence.
3. [User Scenarios and Acceptance](specification.md#user-scenarios-and-acceptance-mandatory) and
   [Requirements](specification.md#requirements-mandatory) translate that intent into actor-specific
   behavior and normative rules.
4. [Policy and Non-Functional Requirements](specification.md#policy-and-non-functional-requirements),
   [Edge Cases and Failure Modes](specification.md#edge-cases-and-failure-modes-mandatory), and
   [Implementation Notes and Guardrails](specification.md#implementation-notes-and-guardrails) make
   security, privacy, audit, reliability, exact-money, and failure behavior explicit rather than
   leaving them as implementation guesses.
5. [Beginning and Ending Context](specification.md#context) distinguishes assumed external
   capabilities from the documentation actually produced by this homework.
6. [Verification Strategy](specification.md#verification-strategy),
   [Success Criteria](specification.md#success-criteria-mandatory), and
   [Low-Level Tasks](specification.md#low-level-future-implementation-tasks) connect every objective to measurable evidence
   and independently reviewable work.

Stable identifiers (`OBJ`, `FR`, `NFR`, `EC`, and `SC`) provide traceability across these layers. The
low-level tasks also identify the responsible agent role, least-expensive reliable model tier,
dependencies, parallel-safety, output, acceptance criteria, and independent reviewer. This keeps
routine transformations inexpensive while reserving advanced review for ambiguous FinTech,
security, privacy, or compliance decisions.

The stable agent IDs are routing roles rather than model names. For the current Codex family, the
recommended profiles are `gpt-5.6-luna` with Low/Light reasoning for Economy work,
`gpt-5.6-terra` with Medium reasoning for Standard work, and `gpt-5.6-sol` with High reasoning for
Advanced work. These profiles describe intended routing; they are not presented as observed runtime
facts unless execution evidence exposes the selected model.

### How the performance targets were chosen

Every numerical target in
[Policy and Non-Functional Requirements](specification.md#policy-and-non-functional-requirements) is
explicitly an **assumed homework target**, not an observed production SLI or a regulatory mandate.
The targets were selected to expose different types of engineering risk and make future validation
objective:

| Target | Why it is included | Planned evidence |
|--------|--------------------|------------------|
| 2 seconds at p95 for healthy control responses and the first transaction page | A concrete interactive-response hypothesis that can be measured instead of saying “fast” | Synthetic journey timing with a defined sample rule |
| 5 seconds at p95 for external freeze confirmation, control consistency, and audit queryability | Separates durable local acceptance from downstream visibility and evidence publication | Read-after-write, decision-point, propagation, and evidence probes |
| Alert at 60 seconds; recovery/escalation at 5 and 15 minutes | Makes delayed propagation and missing evidence operationally owned rather than silently eventual | Failure-timeline and reconciliation scenarios |
| 99.9% calendar-month availability | Forces an explicit success numerator and eligible-request denominator without counting unsafe fallbacks as success | Classified SLI ledger and failure-injection review |
| 24-hour idempotency and 20-way same-version concurrency | Exercises duplicate delivery and lost-update protection under a bounded pathological workload | Duplicate/mismatched replay and deterministic concurrency fixture |
| 24 months and 100,000 synthetic transactions per card | Tests stable pagination and unusually active-card history without claiming unbounded scale | Complete snapshot-bound traversal with no duplicate or skipped records |

Freeze safety remains a hard invariant: a freeze cannot be accepted until durable local authorization
blocking is effective. A percentile is never used to excuse an unsafe tail. Conversely, unfreeze,
limit increase, and ambiguous non-freeze writes fail closed. Production adoption would require the
issuer to replace or confirm every assumption using real traffic, processor capabilities, risk
policy, user research, and observed service levels.

### Why verification is this detailed

Verification depth follows consequence rather than document length. Routine formatting can be
checked mechanically, while actions that restore spending authority, expose customer data, or create
regulatory evidence require negative tests and independent specialist review. The
[Verification Strategy](specification.md#verification-strategy) therefore specifies:

- composite lifecycle/restriction-state and ownership scenarios for freeze and unfreeze;
- exact currency, foreign-exchange, hold/post/reversal/refund, billing-period, timezone, and DST
  boundaries for spending limits;
- duplicate identity, mismatched identity, and 20-way optimistic-concurrency reconciliation;
- a 100,000-item snapshot traversal with tied timestamps and concurrent arrivals;
- complete role × case state × purpose × action denial matrices and abuse boundaries;
- outcome-to-audit reconciliation, duplicate replay, delayed publication, linked correction, and
  recovery/incident timelines;
- automated prohibited-data category scanning plus manual allowlist and privacy review;
- content review proving that final, pending, denied, stale, and unavailable states remain distinct
  and are not conveyed by color alone.

All planned fixtures are synthetic and masked. The submission documents these future verification
oracles; it does not claim that executable tests or production measurements were run.

## Industry Best-Practice Mapping

The sources below provide vocabulary and review prompts. The mapping is intentionally section-level
so a reviewer can see where each practice affects product behavior rather than finding a detached
compliance checklist.

| Practice | Where it appears in the specification | Reference and limitation |
|----------|---------------------------------------|--------------------------|
| Payment-data minimization; no full PAN/CVV in views, logs, evidence, exports, fixtures, or prompts | [Stakeholders and Access Boundaries](specification.md#stakeholders-and-access-boundaries), [Key Entities and Sensitive-Data Classification](specification.md#key-entities-and-sensitive-data-classification), [Implementation Notes and Guardrails](specification.md#implementation-notes-and-guardrails), NFR-002 | [PCI SSC Document Library](https://www.pcisecuritystandards.org/document_library/) and [PCI DSS v4.0.1 publication notice](https://blog.pcisecuritystandards.org/just-published-pci-dss-v-4-0-1); applicability and Cardholder Data Environment scope require issuer/acquirer and qualified-assessor review |
| Least privilege, separation of duties, current authorization, and protected audit evidence | [Stakeholders and Access Boundaries](specification.md#stakeholders-and-access-boundaries), FR-031–FR-041, NFR-001–NFR-003, [Internal Access and Audit contract](specs/001-virtual-card-controls/contracts/internal-access-audit.md) | [NIST SP 800-53 Rev. 5](https://csrc.nist.gov/Pubs/sp/800/53/r5/upd1/Final), especially the AC, IA, and AU control families used as vocabulary; it is a tailorable catalog, not this product's compliance baseline |
| Mandatory step-up for cardholder unfreeze and compliance export; session, intent, replay, and throttling considerations | User Story 2, FR-009–FR-010, FR-035, FR-040, NFR-008, and EC-010 | [NIST SP 800-63B-4](https://pages.nist.gov/800-63-4/sp800-63b.html); the document does not choose an assurance level for this feature, which remains an issuer-risk decision |
| Application-security verification for authentication, authorization, sensitive data, safe errors, and logging | FR-001–FR-041, NFR-001–NFR-003, [Edge Cases and Failure Modes](specification.md#edge-cases-and-failure-modes-mandatory), and [Verification Strategy](specification.md#verification-strategy) | [OWASP ASVS 5.0.0](https://owasp.org/www-project-application-security-verification-standard/) and its [official repository](https://github.com/OWASP/ASVS); ASVS is verification guidance, not payment certification or legal approval |
| Privacy-risk governance through purpose limitation, data inventory/classification, scoped access, retention ownership, and monitoring | [Stakeholders and Access Boundaries](specification.md#stakeholders-and-access-boundaries), [Key Entities and Sensitive-Data Classification](specification.md#key-entities-and-sensitive-data-classification), NFR-002 and NFR-012 | [NIST Privacy Framework 1.0](https://www.nist.gov/privacy-framework); it is a voluntary planning vocabulary and does not determine jurisdiction-specific privacy duties |
| Exact money and unambiguous time handling | NFR-014, EC-009, EC-012–EC-013, EC-025–EC-026, and [Control Commands contract](specs/001-virtual-card-controls/contracts/control-commands.md#limit-accounting-contract) | Domain safety guardrails derived from the approved feature analysis; no external accounting or legal-conformance claim is made |
| Idempotent commands, optimistic concurrency, stable snapshot pagination, and truthful freshness | NFR-008–NFR-010, EC-002–EC-003, EC-011–EC-014, [Control Commands contract](specs/001-virtual-card-controls/contracts/control-commands.md), and [Transaction History contract](specs/001-virtual-card-controls/contracts/transaction-history.md) | Reliability patterns selected in [research decisions R-002–R-004](specs/001-virtual-card-controls/research.md); processor feasibility and production load remain to be validated |
| Append-only, duplicate-safe, reconcilable business evidence separated from sanitized diagnostics | FR-038–FR-041, NFR-003 and NFR-011, EC-019–EC-020, and [Internal Access and Audit contract](specs/001-virtual-card-controls/contracts/internal-access-audit.md#audit-intentevent-contract) | Informed by PCI DSS logging concepts and NIST SP 800-53 AU controls above; retention and evidentiary sufficiency require jurisdiction and records-owner approval |
| Accessible, unambiguous critical-state communication | NFR-013, user-story outcomes, and the content/accessibility row in [Verification Strategy](specification.md#verification-strategy) | Product-safety requirement: states must not rely on color and final/pending/denied/stale/unavailable copy must differ; no conformance to a named accessibility standard is claimed |

## Compliance, Legal, and Production-Readiness Disclaimer

This is an educational, jurisdiction-neutral specification. It does **not** claim PCI DSS
certification, NIST or OWASP compliance, legal compliance, regulatory approval, accessibility
certification, processor certification, or production readiness. The cited publications are control
and verification references only.

Before implementation or deployment, qualified issuer risk, security, privacy, compliance, legal,
accessibility, payments, operations, and assessor stakeholders must determine applicability and
approve jurisdiction, Cardholder Data Environment scope, authentication assurance, policy ranges,
retention/deletion and legal-hold rules, evidence requirements, vendors, processor feasibility,
traffic assumptions, SLOs, incident ownership, and accessibility criteria. Any resulting material
change must return through specification impact analysis and approval before downstream work.
