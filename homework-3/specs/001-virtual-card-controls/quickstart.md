# Documentation Validation Quickstart

**Purpose**: Reproduce the Phase 0/1 documentation checks before Gate 2
**Scope**: Read-only validation of Markdown/JSON artifacts; no application, API, UI, database, package,
or implementation is created or executed.

## 1. Establish the Approved Baseline

1. Read `.specify/memory/constitution.md` and `AGENTS.md`.
2. Read `.specify/memory/approvals.md` and identify the Gate 1 artifact/hash.
3. Compute SHA-256 for `specs/001-virtual-card-controls/spec.md`.
4. Pass only when it equals
   `7cdd28c597f5c0ed440337eefc4a5b229b5eff9f909fa56a6582b5ef4a2a9ed9`.

Any mismatch stops validation: assess semantic impact and renew Gate 1 before planning continues.

## 2. Confirm Required Planning Artifacts

Expected Phase 0/1 files:

- `spec.md`
- `plan.md`
- `research.md`
- `data-model.md`
- `contracts/control-commands.md`
- `contracts/transaction-history.md`
- `contracts/internal-access-audit.md`
- `checklists/requirements.md`
- `checklists/fintech.md`
- `quickstart.md`

`tasks.md`, canonical graded deliverables, and all source-code artifacts MUST remain absent at Gate 2.

## 3. Re-run the Constitution Check

Pass conditions:

- every artifact is documentation-only;
- approved product behavior is unchanged and traceable;
- technical choices are labeled replaceable plan assumptions;
- every material artifact has an independent reviewer role;
- model allocation uses Economy/Standard before Advanced where risk permits;
- no plan/task/contract authorizes `speckit-implement`.

## 4. Review Product-to-Design Traceability

Walk each objective in the `spec.md` Traceability Summary and confirm:

1. related entities/invariants exist in `data-model.md`;
2. related pre/postconditions exist in one conceptual contract;
3. verification oracles exist in the spec, contract, or this quickstart;
4. `plan.md` identifies a future artifact/task workstream and reviewer;
5. no plan/design statement introduces a new actor capability, state transition, data field exposure,
   service target, or retention obligation.

Pass when `OBJ-001–OBJ-006`, `FR-001–FR-041`, `NFR-001–NFR-014`, and `EC-001–EC-026` have no orphaned
approved behavior.

## 5. Walk Critical Invariants

### Composite Card State

- lifecycle is separate from restriction sources;
- precedence is termination > risk > operations > user > active;
- cardholder unfreeze removes only `USER_FREEZE`;
- operations/risk/lifecycle removal remains out of scope.

### Freeze Safety

- user/operations freeze acceptance includes durable local blocking;
- only freeze may return `PENDING_PROPAGATION`;
- 60-second alert and 15-minute escalation are present;
- prior-authorized pending transactions may still settle.

### Limits and Commands

- exact billing currency/scale and calendar periods are specified;
- hold/post/reversal/refund/FX effects are deterministic;
- all-decrease-only rule applies while restricted;
- one expected version yields at most one distinct accepted winner;
- command identity mismatch changes no state.

### Transaction History

- occurrence time/status time/`as of` are separate;
- refund has a distinct linked identity;
- snapshot/keyset continuation preserves no-gap/no-duplicate traversal;
- empty, stale, and unavailable have objective thresholds.

### Internal Access and Evidence

- role/case/purpose/action/export matrix has explicit denials;
- abuse thresholds are deterministic;
- canonical data taxonomy applies to every surface;
- audit intent shares the business-outcome acceptance boundary;
- replay/correction/recovery/degraded-safe semantics are complete.

## 6. Validate Research Boundaries

For every external source in `research.md`, verify:

- official direct link and version/release are stated;
- supported practice is named;
- limitations state that guidance is not certification or jurisdictional legal compliance;
- no source overrides approved product requirements;
- draft/unstable source is not presented as stable baseline.

## 7. Validate Agent/Model Routing

Confirm each planned workstream states:

- primary role and tier;
- why that is the least expensive reliable tier;
- independent reviewer for material/high-risk output;
- parallel-safety and non-overlapping file boundary;
- Advanced tier is absent from mechanical formatting, IDs, links, and status work.

## 8. Mechanical Quality Checks

Run or reproduce equivalent read-only checks:

- no `TODO`, `TBD`, or `[NEEDS CLARIFICATION]` markers;
- no unexplained template placeholders;
- all relative Markdown links resolve;
- `.specify/feature.json` points to `specs/001-virtual-card-controls`;
- requirements checklist is 20/20 and FinTech checklist is 38/38;
- FinTech findings `FTR-001–FTR-012` are independently resolved;
- Markdown has no unintended trailing whitespace;
- Git status contains no Homework 3 implementation/source files.

## 9. Gate 2 Evidence Package

Present to the user:

- plan and generated artifact paths/hashes;
- Constitution Check and quickstart results;
- planning decisions and alternatives;
- technical assumptions and feasibility risks;
- agent/model allocation and independent-review evidence;
- exact statement that task generation is not yet authorized.

Gate 2 passes only on explicit user approval. After approval, `speckit-tasks` may generate the
documentation task breakdown; `speckit-implement` remains prohibited for Homework 3.

## Phase 1 Validation Execution Record — 2026-07-15

**Executed by**: Primary planning orchestrator
**Independent reviewers**: FinTech/security/compliance reviewer; plan/traceability reviewer
**Review separation**: Reviewers performed read-only analysis; the primary author applied remediation;
reviewers independently rechecked their findings.

| Check | Recorded result |
|-------|-----------------|
| Gate 1 provenance | `spec.md` SHA-256 equals approved `7cdd28c597f5c0ed440337eefc4a5b229b5eff9f909fa56a6582b5ef4a2a9ed9` |
| Required Phase 0/1 artifacts | Present: plan, research, data model, three contracts, quickstart, two checklists |
| Premature artifacts | Absent: `tasks.md`, canonical graded deliverables, application/source/package/schema/migration files |
| Requirement checklists | 58/58 complete: requirements 20/20; FinTech 38/38 |
| Coverage | Collectively covers OBJ-001–OBJ-006, FR-001–FR-041, NFR-001–NFR-014, EC-001–EC-026, SC-001–SC-008 |
| Relative links | All local Markdown links resolve |
| Placeholders | No unexplained template placeholder or unresolved `NEEDS CLARIFICATION`/TODO/TBD marker; this quickstart's literal marker names are instructions only |
| Formatting | No unintended trailing whitespace in Phase 0/1 artifacts |
| Feature pointer | `.specify/feature.json` resolves to `specs/001-virtual-card-controls` |
| No-code boundary | No Homework 3 application implementation; `.agents/` and `.specify/` contain Spec Kit workflow infrastructure only |
| External sources | Official pages/version claims checked for PCI DSS 4.0.1, NIST SP 800-53 Release 5.2.0, NIST SP 800-63B-4, OWASP ASVS 5.0.0, and stable NIST Privacy Framework 1.0 |
| Domain design review | Four Medium findings `P1-001–P1-004` remediated and independently verified; no Critical/High/Medium remain |
| Plan/traceability review | One Critical, two High, three Medium, and two Low findings remediated and independently verified; no Critical/High/Medium findings remain |

### Remaining Non-Blocking Feasibility Assumptions

- Authorization processing must synchronously honor the durable local restriction boundary; otherwise
  approved `FR-003`/`NFR-004` requires architecture reassessment and specification re-approval.
- The transaction source must support stable snapshots/keyset continuation or require the sanitized
  issuer read projection documented in R-004.
- Performance, traffic, policy ranges, vendors, retention, and jurisdiction remain explicitly assumed
  inputs requiring pre-production validation.
- The physical Git branch remains `main`; `001-virtual-card-controls` is the Spec Kit logical identifier
  because the nested-project Git hook skipped branch creation.
