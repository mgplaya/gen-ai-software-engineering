# Documentation Delivery Plan: Regulated Virtual Card Controls

**Branch**: `001-virtual-card-controls` (logical identifier; Git branch not created) |
**Date**: 2026-07-15 | **Spec**: [spec.md](./spec.md)
**Input**: Gate-1-approved feature specification; approval evidence in
`.specify/memory/approvals.md`
**Scope**: Documentation package only; no implementation

## Summary

Produce an executable-quality specification package for regulated virtual card controls: user and
operations freeze, cardholder unfreeze, exact spending limits, stable transaction history, scoped
internal oversight, durable/reconcilable audit, and measurable failure/performance behavior. The plan
uses conceptual architecture, data, contracts, verification, and cost-aware agent routing to make
future implementation tasks precise without creating code, APIs, UI, schemas, or dependencies.

## Planning Context

**Canonical graded specification**: `homework-3/specification.md` after controlled publication
**Approved working specification**: `specs/001-virtual-card-controls/spec.md` at SHA-256
`7cdd28c597f5c0ed440337eefc4a5b229b5eff9f909fa56a6582b5ef4a2a9ed9`
**Spec Kit working directory**: `specs/001-virtual-card-controls/`
**Required deliverables**: `specification.md`, logical `agents.md` guidance plus active ChatGPT/Codex
rules in the combined physical `AGENTS.md`, and `README.md`
**Domain reviewers**: Product/requirements, payments/risk, security, compliance/privacy, reliability,
QA/traceability
**Assumed system context**: Existing identity/ownership, issuer policy, processor authorization and
propagation, ledger history, internal identity/case authority, monitoring, and evidence storage
**Performance targets**: Approved assumed targets in `NFR-003–NFR-014`; not observed production SLIs
**Sensitive-data boundary**: Canonical per-surface allow/prohibit taxonomy from approved spec
**Scale/scope**: Existing virtual cards; 100,000 transactions/card verification fixture; 20 concurrent
same-version commands; 10,000-record compliance export cap; other values remain approved assumptions

### Hypothetical Technical Context

**Language/version vocabulary**: Existing course pattern—Node.js 22, TypeScript 5.7
**Primary framework vocabulary**: NestJS 11 modular backend; no package installation
**Storage assumption**: PostgreSQL-like ACID relational control store; read-only external ledger or
sanitized read projection; separate audit evidence boundary
**Testing vocabulary**: Jest 29, Supertest 7, property/boundary, contract, integration, concurrency,
reconciliation, performance, accessibility/content, and manual compliance reviews
**Architecture**: Hypothetical modular monolith with ports/adapters and transactional outbox
**External integrations**: Vendor-neutral identity/step-up, processor, issuer risk policy, ledger,
case authority, audit/monitoring/alerting
**Project type**: Documentation-only plan for a hypothetical regulated backend service
**Constraints**: No implementation; durable local freeze invariant; exact money/time; fail-closed
risk-increasing writes; no prohibited data; approved result/recovery semantics
**Replaceability**: Every stack/vendor assumption may change during later implementation planning only
after impact analysis; product requirements remain authoritative

## Constitution Check

*GATE: Passed before Phase 0 and repeated after Phase 1 design.*

- [x] Specification remains the source of truth; this plan introduces no product behavior.
- [x] Work remains documentation-only and all deliverables match `TASKS.md`.
- [x] Gate 1 approval is recorded for the exact specification SHA being planned.
- [x] FinTech safety, edge cases, verification, and measurable targets are covered by planned artifacts.
- [x] Every planned artifact has objective/requirement traceability.
- [x] Agent/model routing uses the least expensive reliable tier and independent review.
- [x] No unresolved material question is silently converted into a technical decision.

### Post-Design Recheck

- [x] Data model preserves composite lifecycle/restrictions, exact limit accounting, immutable
  transaction identity, role/case access, command deduplication, and audit/recovery invariants.
- [x] Conceptual contracts use only approved result/state/data behavior and do not choose an API shape.
- [x] Quickstart validates documentation and traceability only; it does not run implementation.
- [x] Security references are control/rationale inputs, not claims of PCI, NIST, OWASP, privacy, or
  jurisdictional compliance.
- [x] Advanced agents are limited to high-risk domain decisions/reviews; mechanical work uses Economy.

## Research and Decision Plan

| Decision ID | Question | Resolution/evidence | Owner agent/tier | Exit criterion |
|-------------|----------|---------------------|------------------|----------------|
| R-001 | Architecture shape | Modular monolith with ports/adapters; `research.md` | Architecture analyst / Standard; risk review / Advanced | Boundaries cover requirements without distributed overdesign |
| R-002 | Durable atomic control/evidence intent | ACID control store + conceptual transactional outbox | Data/domain analyst / Standard; payments review / Advanced | Freeze/version/idempotency/audit invariants are representable |
| R-003 | Dependency propagation/recovery | Async idempotent adapters and reconciliation | Reliability analyst / Standard | Approved result/timeline semantics mapped |
| R-004 | Stable transaction paging | Snapshot-bound keyset port or sanitized projection | Data/QA analyst / Standard | FR-026–FR-029 and NFR-010 are feasible |
| R-005 | Audit vs diagnostic boundary | Separate evidence and sanitized diagnostics | Security/compliance / Advanced | Taxonomy, correction, retention, recovery stay distinct |
| R-006 | Contract format | Conceptual Markdown tables/scenarios only | Contract analyst / Standard | Implementable pre/postconditions without API design |
| R-007 | Future stack assumption | Course-consistent Node/NestJS/TypeScript vocabulary + relational store | Repository analyst / Economy; architecture review / Standard | `agents.md` can state concrete replaceable conventions |
| R-008 | Canonical publication | After Gate 2: generate/analyze tasks, then publish approved product body + synchronized low-level-task section | Documentation lead / Standard | Canonical graded spec contains required tasks without product semantic drift |
| R-009 | Security/control references | PCI DSS 4.0.1; NIST 800-53 5.2.0; NIST 800-63B-4; OWASP ASVS 5.0.0; NIST Privacy Framework 1.0 | Security researcher / Advanced | Sources are official, versioned, limited, and non-legal |

All decisions and alternatives are documented in [research.md](./research.md). No unresolved planning
clarification remains. Feasibility assumptions are recorded there and must be validated before any
future production implementation.

## Artifact Plan

```text
specs/001-virtual-card-controls/
├── spec.md                         # Approved Spec Kit working specification
├── plan.md                         # This Gate-2 delivery plan
├── research.md                     # Phase 0 decisions, sources, alternatives, limitations
├── data-model.md                   # Conceptual entities, relationships, invariants, lifecycle
├── quickstart.md                   # Documentation validation walkthrough
├── contracts/
│   ├── control-commands.md         # Status/limit commands, versions, results, accounting
│   ├── transaction-history.md      # Identity, status, time, snapshot/cursor, freshness
│   └── internal-access-audit.md    # Role/case matrix, exports, evidence, taxonomy, recovery
├── checklists/
│   ├── requirements.md             # Initial specification quality evidence
│   └── fintech.md                  # Formal independent FinTech review evidence
└── tasks.md                        # Generated only after Gate 2

homework-3/
├── specification.md                # Canonical graded product body + validated low-level tasks
├── AGENTS.md / agents.md           # Operational + graded guidance + active ChatGPT/Codex rules
└── README.md                       # Graded rationale/practice mapping; task-generated
```

**Canonicalization decision**: Until controlled publication, the approved `spec.md` plus approval-log
hash is authoritative. After Gate 2, `tasks.md` is generated and analyzed first; a later documentation
task publishes `specification.md` as the semantically unchanged approved product body plus a clearly
delimited low-level-task section synchronized from validated `tasks.md`. Product-body equivalence and
task parity/traceability are validated separately. The graded file then becomes canonical. Any product
semantic change updates the working spec first, invalidates affected approvals, and is re-approved;
adding the already-planned downstream task section does not silently change product behavior.

## Agent and Model Allocation

| Workstream | Primary agent role | Model tier | Tier rationale | Independent reviewer | Parallel-safe with |
|------------|--------------------|------------|----------------|----------------------|--------------------|
| Architecture/reliability ADRs R-001–R-008 | Architecture/reliability researcher | Standard | Bounded technical alternatives from approved requirements | Independent architecture/risk reviewer / Advanced | Security source research after shared scope fixed |
| Security/control references R-009 | Security researcher | Advanced | Version/applicability judgment affects regulated-domain claims | Separate security/compliance reviewer / Advanced | Architecture ADR research |
| Requirement/ID extraction and link scan | Traceability assistant | Economy | Mechanical bounded mapping | QA analyst / Standard | Terminology and formatting scans |
| Conceptual data/state/accounting model | Domain/data analyst | Standard | Structured derivation from approved requirements | Payments/risk reviewer / Advanced | Transaction contract after shared terms fixed |
| Control-command and transaction contracts | Contract/QA analyst | Standard | Clear pre/postconditions and scenario mapping | Security/privacy reviewer / Advanced | Separate contract files |
| Internal access, audit, taxonomy, recovery contract | Security/compliance analyst | Advanced | High-risk authorization/evidence judgment | Separate security/compliance reviewer / Advanced | Data model and other contracts after taxonomy fixed |
| Quickstart/checklist/terminology validation | Documentation QA | Economy | Mechanical checklist and link work | QA reviewer / Standard | All non-overlapping draft artifacts |
| Combined `AGENTS.md`/`agents.md` and active ChatGPT/Codex rules | Engineering-guidance writer | Standard | Concrete conventions in the instruction file Codex actually reads | FinTech/security reviewer / Advanced | README after shared glossary |
| README rationale and practice mapping | Technical writer | Standard | Synthesis with cited sources | Compliance/technical reviewer / Standard; Economy link scan | Agent/rules drafting |
| Cross-artifact reconciliation and Gate 2 synthesis | Planning orchestrator | Advanced | Resolves high-impact conflicts and gate evidence | Independent consistency reviewer / Advanced | None; runs after drafts |

Advanced tier MUST NOT be used for ID extraction, formatting, link checking, status updates, or simple
template population. Parallel work begins only after shared terms/decisions are fixed and must use
non-overlapping output files.

## Traceability and Verification Plan

| Artifact | Inputs | Requirements/objectives covered | Validation | Approval needed |
|----------|--------|---------------------------------|------------|-----------------|
| `research.md` | Approved spec, constitution, official sources, repo stack evidence | All objectives; NFR-001–NFR-014; architecture feasibility | Source/version/limitation review; no-compliance-claim scan | Gate 2 |
| `data-model.md` | Entity table, state/result/accounting rules | OBJ-001–OBJ-006; FR-001–FR-041 | Invariant/state/ownership/retention matrix review | Gate 2 |
| `contracts/control-commands.md` | Status/limit requirements and ECs | OBJ-001, OBJ-002, OBJ-005, OBJ-006 | Pre/postcondition, version/idempotency, result, recovery coverage | Gate 2 |
| `contracts/transaction-history.md` | Transaction requirements and ECs | OBJ-003, OBJ-006 | Identity/time/order/snapshot/freshness/privacy coverage | Gate 2 |
| `contracts/internal-access-audit.md` | Internal roles, taxonomy, evidence/recovery | OBJ-004–OBJ-006; NFR-001–NFR-003, NFR-011–NFR-012 | Role×case×purpose×action negative review; evidence/taxonomy reconciliation | Gate 2 |
| `quickstart.md` | All Phase 0/1 artifacts and checklists | SC-008 and all traceability | Documentation-only walkthrough; zero unresolved placeholders/findings | Gate 2 |
| Future `specification.md` | Approved `spec.md`, validated `tasks.md`, approval provenance | Entire approved product specification plus required low-level tasks | Product-body semantic equivalence and task parity/traceability reviewed separately | Gate 3 package |
| Combined `AGENTS.md` / logical `agents.md` / ChatGPT-Codex rules | Constitution, plan, contracts | Domain/stack/verification/edge/security guidance | Conflict, scope, prohibited-action, and active-instruction review | Gate 3 package |
| Future `README.md` | Approved package and research sources | Rationale and best-practice mapping | Link/section/source/assumption review | Gate 3 package |

## Dependencies and Execution Order

1. **Completed prerequisite**: constitution v1.0.0, Gate-1-approved specification, clarification,
   requirements checklist, and independent FinTech checklist.
2. **Phase 0**: resolve architecture, persistence, propagation, history, evidence, contract, stack,
   canonicalization, and control-reference decisions in `research.md`.
3. **Phase 1 shared foundation**: derive `data-model.md` terminology and invariants.
4. **Phase 1 parallel contracts**: author the three non-overlapping conceptual contract files from the
   fixed shared model.
5. **Phase 1 validation**: execute `quickstart.md` walkthrough, cross-check traceability, and rerun the
   Constitution Check.
6. **Gate 2**: present exact plan/design artifacts, findings, assumptions, feasibility risks, and hash
   evidence; wait for explicit user approval.
7. **Post-Gate 2 only**: generate agent-routed `tasks.md`, run consistency analysis, and resolve
   findings; task generation does not authorize application implementation.
8. **Documentation task execution**: publish canonical `specification.md` with the approved product body
   plus synchronized low-level tasks, then produce the combined `AGENTS.md`/logical `agents.md` with
   active ChatGPT/Codex rules and `README.md` according to the validated task order.
9. **Gate 3**: validate the complete graded package, canonical/provenance parity, and unresolved risks;
   wait for explicit final approval.
10. **Homework stop condition**: after final approved documentation package, never run
   `speckit-implement`.

## Complexity and Exceptions

| Decision | Why needed | Less costly/simpler alternative rejected because | Approver |
|----------|------------|--------------------------------------------------|----------|
| Advanced review of FinTech/access/audit decisions | Incorrect control semantics create regulated-domain risk | Standard-only review lacks the required high-risk independent judgment | Gate 2 user approval pending |
| Conceptual relational store/outbox assumption | Required to make durability/version/evidence invariants implementable | In-memory or unrelated stores cannot represent approved atomicity/recovery guarantees | Gate 2 user approval pending |
| Sanitized transaction read projection as fallback | Stable snapshot may not exist at processor boundary | Offset paging violates approved duplicate/gap rules | Gate 2 user approval pending |

## Gate 2 Exit Criteria

- [x] All planning decisions trace to the approved specification.
- [x] Research questions are resolved or explicitly recorded as replaceable/non-blocking assumptions.
- [x] Deliverables, ownership, model tiers, dependencies, and validation are complete.
- [x] Post-design Constitution Check passes.
- [ ] User explicitly approves this plan before tasks are generated.
