# Implementation Plan: Regulated Virtual Card Controls

**Branch**: `001-virtual-card-controls` | **Date**: 2026-07-15 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/001-virtual-card-controls/spec.md`

> **No-code boundary (Constitution VII)**: This plan is a *hypothetical* design for planning and
> traceability only. No source, packages, migrations, or infrastructure are created or installed.
> All technology choices below are illustrative assumptions, not commitments.

## Summary

Specify controls over already-issued virtual cards — freeze/unfreeze, spending limits, transaction
history, and internal oversight — with the safety asymmetry, exactness, idempotency, least
privilege, and auditability required by a regulated issuer. The design centers on a **composite card
state** (lifecycle × restriction sources), an **append-only audit stream** separate from
diagnostics, **optimistic-versioned commands** with idempotency keys, and **snapshot-bound keyset
pagination** for history.

## Technical Context

*(Hypothetical assumptions — chosen to make the spec concrete, not to mandate a stack.)*

**Language/Version**: (assumed) a strongly-typed service language with a decimal/integer money type; no runtime installed
**Primary Dependencies**: (assumed) an existing card platform + downstream processor + identity/step-up service — all pre-existing, integrated via internal contracts
**Storage**: (assumed) a transactional store for card state/limits/commands + an append-only audit store; conceptual only (see data-model.md)
**Testing**: documented test categories (unit/integration/e2e) with synthetic fixtures; no test code produced
**Target Platform**: (assumed) issuer backend service behind authenticated cardholder and internal surfaces
**Project Type**: backend service governing existing cards (controls layer)
**Performance Goals**: p95 ≤ 2s interactive control + first history page; ≤ 5s external confirmation/consistency/audit-query (SC-001, SC-002)
**Constraints**: fail-closed on risk; exact money/time; 24h idempotency window; 99.9% monthly availability excluding unsafe fallbacks (SC-006..SC-008)
**Scale/Scope**: history correctness validated at 100k txns / 24 months; 20-way concurrent-command conflict resolution (SC-004, SC-005)

## Constitution Check

*GATE: must pass before Phase 0 and re-checked after Phase 1 design.*

| Principle | Design honors it via | Status |
|-----------|----------------------|--------|
| I. Fail-closed on risk | Command outcome model: risk-increasing → deny on any ambiguity; risk-reducing → accept on durable local block | PASS |
| II. Exact money & time | Integer minor units + ISO-4217; immutable UTC instant + issuer calendar (data-model.md) | PASS |
| III. Idempotent, versioned writes | Command entity with idempotency key + base version; single-winner conflict (contracts/control-commands.md) | PASS |
| IV. Least privilege | Per-action re-evaluation of case/purpose/expiry/permission; separation of duties for ops-freeze release | PASS |
| V. Append-only audit | Separate append-only, tamper-evident audit stream; missing-evidence recovery timeline | PASS |
| VI. Sensitive-data boundary | Tokens/masked PAN only; export allowlist; sanitized notes; no raw payloads | PASS |
| VII. No-code boundary | This plan and all design docs are documentation; no code/packages/infra | PASS |

**Complexity Tracking**: no violations to justify.

## Project Structure

### Documentation (this feature)

```text
specs/001-virtual-card-controls/
├── plan.md              # This file
├── spec.md              # Feature specification (/speckit-specify)
├── research.md          # Phase 0 — decisions & rationale
├── data-model.md        # Phase 1 — conceptual entities & state
├── quickstart.md        # Phase 1 — validation scenarios (synthetic)
├── contracts/           # Phase 1 — behavioral contracts (not API code)
│   ├── control-commands.md
│   ├── transaction-history.md
│   └── internal-access-audit.md
├── checklists/          # requirements.md, fintech.md
├── task-slices/         # us1..us5 low-level task slices
├── reviews/             # clarify, analyze, gate reports
└── tasks.md             # Phase 2 (/speckit-tasks)
```

### Source Code (repository root)

**Not applicable — no code is produced for this deliverable (Constitution VII).** Were this to be
implemented later, the hypothetical layout would be a single backend service:
`controls/` (command handlers), `state/` (composite card state + limits), `history/` (keyset
pagination), `audit/` (append-only stream), `access/` (least-privilege checks), with `tests/`
mirroring the documented test categories.

**Structure Decision**: Documentation-only package under `specs/001-virtual-card-controls/`; graded
deliverables distilled into `homework-3/` (specification.md, AGENTS.md, .claude rules, README.md).

## Phase 0 — Research

See [research.md](research.md): decisions on composite state, durable-vs-propagated freeze, money/
time representation, idempotency+versioning, keyset pagination, audit separation, and access model,
each with rationale and rejected alternatives.

## Phase 1 — Design

- [data-model.md](data-model.md): conceptual entities (Card, Restriction, Limit, Transaction,
  Command, AuditEvent, Case, AccessGrant), their fields, state machine, and invariants.
- [contracts/](contracts/): behavioral contracts for control commands, transaction history, and
  internal access/audit — described as pre/postconditions and outcomes, not endpoint code.
- [quickstart.md](quickstart.md): synthetic validation scenarios mapping to SC-001..SC-008.

**Post-Design Constitution re-check**: PASS (no new violations introduced by the design docs).

## Phase 2 — Tasks

Generated by `/speckit-tasks` into [tasks.md](tasks.md): decomposition into low-level, per-user-story
tasks, each with acceptance criteria and traceability to OBJ/FR/NFR/EC/SC.

**Model routing & parallelism**: each task carries a cost-aware model assignment
(Haiku 4.5 = mechanical, Sonnet 5 = bounded drafting, Opus 4.8 = security-critical design +
adversarial review) and a wave-based parallel execution schedule (6 waves, ~9 sequential slots for
23 tasks). Author and reviewer roles are independent; Opus is reserved for high-risk judgment, never
the default. See [tasks.md — Model Routing & Parallel Execution Plan](tasks.md#model-routing--parallel-execution-plan).
