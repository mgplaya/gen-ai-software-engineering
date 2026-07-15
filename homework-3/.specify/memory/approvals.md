# Approval Log

## Gate 1 — Feature Specification

- **Decision**: Approved
- **Approved by**: User
- **Recorded**: 2026-07-15
- **Artifact**: `specs/001-virtual-card-controls/spec.md`
- **SHA-256**: `7cdd28c597f5c0ed440337eefc4a5b229b5eff9f909fa56a6582b5ef4a2a9ed9`
- **Scope**: Regulated virtual card controls specification covering cardholder freeze/unfreeze,
  spending limits, transaction history, operations/compliance oversight, FinTech safety, measurable
  non-functional requirements, edge/failure behavior, verification, and traceability.
- **Validation evidence**:
  - `checklists/requirements.md`: 20/20 complete
  - `checklists/fintech.md`: 38/38 complete
  - Independent review: 6 High and 6 Medium findings resolved; no Critical/High/Medium findings remain
- **Effect**: Planning is authorized. Task generation and implementation are not authorized.

Material changes to the approved specification require a new hash, impact analysis, downstream
revalidation, and renewed Gate 1 approval.

## Gate 2 — Technical and Delivery Plan

- **Decision**: Approved
- **Approved by**: User
- **Recorded**: 2026-07-15
- **Artifact**: `specs/001-virtual-card-controls/plan.md`
- **SHA-256**: `c92fc44bd86c12d065857c001f99e0215541c94b4b9136fd47ab3fcb8ff73d00`
- **Scope**: Technical and delivery plan together with its research, conceptual data model,
  behavioral contracts, validation quickstart, architecture decisions, and cost-aware agent/model
  routing constraints.
- **Validation evidence**:
  - Gate 1 specification hash remained unchanged
  - Requirements and FinTech checklists: 58/58 complete
  - Collective coverage: OBJ-001–006, FR-001–041, NFR-001–014, EC-001–026, SC-001–008
  - Independent FinTech/security and plan/traceability reviews: Pass; all Critical, High, and Medium
    findings resolved
- **Effect**: Task generation and cross-artifact analysis are authorized. Implementation remains
  prohibited and out of scope for Homework 3.
- **User-directed amendment**: On 2026-07-15 the user replaced the example Copilot artifact with
  active ChatGPT/Codex rules in `AGENTS.md`. The plan was synchronized to that exact deliverable
  choice without changing product behavior, architecture, or no-code scope; the hash above is the
  amended approved baseline.

Material changes to the approved plan require a new hash, impact analysis, downstream revalidation,
and renewed Gate 2 approval.
