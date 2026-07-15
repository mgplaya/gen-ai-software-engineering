---
description: "Task list for Regulated Virtual Card Controls (future implementation; documented only)"
---

# Tasks: Regulated Virtual Card Controls

**Input**: Design documents from `specs/001-virtual-card-controls/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

> **No-code boundary (Constitution VII)**: These are the **future** low-level implementation tasks
> the spec would drive. They are documented with acceptance criteria for traceability and grading;
> **no code is written in this deliverable** and `/speckit-implement` is intentionally not run.

## Format: `[ID] [P?] [Story] Description → Acceptance criteria (Traces)`

- **[P]**: parallel-safe (different area, no dependency).
- **[Story]**: US1..US5 (or FOUND/POLISH for shared work).
- Each task ends with a checkable definition of done and the OBJ/FR/NFR/EC/SC it serves.

---

## Phase 1: Setup (Shared)

- [ ] T001 [P] Establish money/time conventions doc (integer minor units + ISO-4217; UTC instant +
  issuer calendar). **DoD**: convention documented and referenced by all money/time tasks; no float
  money anywhere. (Traces: FR-012, FR-014; Constitution II)
- [ ] T002 [P] Establish command envelope convention (actor+card+action+payload, idempotency_key,
  base_version, outcome enum). **DoD**: envelope fields fixed; outcome enum = success/denied/pending/
  conflict. (Traces: FR-031, FR-039)

## Phase 2: Foundational (Blocking Prerequisites)

- [ ] T003 [US-ALL] Define composite card state model (lifecycle × restriction sources; strongest
  governs). **DoD**: state machine matches data-model.md; cardholder cannot clear ops/fraud source.
  (Traces: FR-036, FR-026; OBJ-1, OBJ-2)
- [ ] T004 [US-ALL] Define optimistic-concurrency + idempotency mechanism. **DoD**: same-version
  concurrent writes → one winner + deterministic conflict; identical replay → original outcome;
  different payload/same key → conflict. (Traces: FR-017, FR-031, FR-032; SC-005, SC-008)
- [ ] T005 [US-ALL] Define append-only audit stream (tamper-evident, sanitized, attributable,
  separate from diagnostics). **DoD**: every business action + denial produces one reconstructable
  event; no prohibited fields. (Traces: FR-033, FR-035, NFR-012; SC-003)
- [ ] T006 [US-ALL] Define least-privilege access evaluation (ownership/role, case, purpose, expiry,
  step-up, permission — re-evaluated per action). **DoD**: each sensitive action re-checks all
  factors at use time; fail-closed on any gap. (Traces: FR-025, FR-029, FR-040, NFR-009)
- [ ] T007 [US-ALL] Define sensitive-data boundary + masking/tokenization rules. **DoD**: only
  tokens/masked PAN in views/logs/audit/exports/fixtures; raw payloads never stored. (Traces:
  FR-021, FR-037, FR-038, NFR-002, NFR-003; Constitution VI)

**Checkpoint**: shared foundations defined; user stories can proceed.

---

## Phase 3: User Story 1 — Freeze (P1) 🎯 MVP

- [ ] T008 [US1] Specify freeze command handling (durable local block; propagation may be pending).
  **DoD**: freeze returns success on durable block; card reads frozen + pending allowed; matches
  contracts/control-commands.md C1. (Traces: FR-001, FR-002, FR-003; EC-03; SC-001, SC-002)
- [ ] T009 [P] [US1] Specify freeze idempotency + audit. **DoD**: repeat freeze → no duplicate
  restriction/audit; every attempt audited. (Traces: FR-004, FR-005; EC-01)

**Checkpoint**: US1 independently demonstrable (freeze + audit).

---

## Phase 4: User Story 2 — Unfreeze, fail-closed (P2)

- [ ] T010 [US2] Specify fail-closed unfreeze decision logic. **DoD**: success only when step-up
  fresh AND restriction state positively safe; ambiguity → denied (never pending). (Traces: FR-006,
  FR-007, FR-009; EC-05; SC-006)
- [ ] T011 [US2] Specify stronger-restriction protection + separation-of-duties release. **DoD**:
  cardholder cannot clear ops/fraud restriction; ops-release needs distinct second actor. (Traces:
  FR-008, FR-026, FR-030, NFR-010; EC-04)
- [ ] T012 [P] [US2] Specify unfreeze audit (success + non-leaking denial). **DoD**: all outcomes
  audited without case-detail leakage. (Traces: FR-010, FR-035)

**Checkpoint**: US2 independently demonstrable (safe vs denied unfreeze).

---

## Phase 5: User Story 3 — Spending limits (P3)

- [ ] T013 [US3] Specify limit validation (integer minor units, currency match, scope). **DoD**:
  negative/zero/non-integer/mismatched-currency rejected with reason. (Traces: FR-011, FR-012;
  EC-06, EC-07)
- [ ] T014 [US3] Specify atomic authorization evaluation across per-txn/daily/monthly with inclusive
  boundary + issuer-calendar periods. **DoD**: 50.00 approved / 50.01 declined; correct period
  assignment incl. DST; no double-count. (Traces: FR-013, FR-014, FR-016; EC-08, EC-09, EC-17)
- [ ] T015 [P] [US3] Specify limit risk-asymmetry + concurrency + audit. **DoD**: decrease atomic;
  increase fail-closed when unconfirmed; concurrent changes → one winner/conflict; all audited.
  (Traces: FR-015, FR-017, FR-018; EC-10; SC-005)

**Checkpoint**: US3 independently demonstrable (limit enforcement).

---

## Phase 6: User Story 4 — Transaction history (P4)

- [ ] T016 [US4] Specify snapshot-bound keyset pagination (most-recent-first; no dupes/skips/order
  drift). **DoD**: matches contracts/transaction-history.md; empty state explicit. (Traces: FR-019,
  FR-020, FR-022, FR-024; EC-13, EC-14, EC-15; SC-004)
- [ ] T017 [P] [US4] Specify history authorization binding + masked data. **DoD**: non-owner denied
  + audited; only masked/tokenized fields returned. (Traces: FR-021, FR-023, FR-040; EC-16)

**Checkpoint**: US4 independently demonstrable (stable history at scale).

---

## Phase 7: User Story 5 — Internal oversight (P5)

- [ ] T018 [US5] Specify ops case-scoped action authorization (all factors re-evaluated; fail-closed
  on gaps). **DoD**: allowed within open case/valid grant; denied on closed case/expired/missing
  purpose. (Traces: FR-025, FR-029; EC-18, EC-19)
- [ ] T019 [US5] Specify compliance export (versioned allowlist, bounded size, audited). **DoD**:
  only allowlisted fields; prohibited fields absent; oversize → paginate/reject; audited with
  purpose/scope. (Traces: FR-027, FR-028; EC-20, EC-21)

**Checkpoint**: US5 independently demonstrable (least-privilege oversight + export).

---

## Phase 8: Polish & Cross-Cutting

- [ ] T020 [P] Specify missing-evidence recovery (alert 60s; recovery/degraded-mode; incident
  5/15m). **DoD**: matches contracts/internal-access-audit.md A4. (Traces: FR-034; EC-22; SC-007)
- [ ] T021 [P] Specify velocity/oscillation guard (rapid freeze/unfreeze). **DoD**: guarded; each
  transition audited; no state corruption. (Traces: EC-23)
- [ ] T022 [P] Author verification catalog (test categories + synthetic fixtures per objective).
  **DoD**: every OBJ has documented review checkpoint + unit/integration/e2e categories. (Traces:
  NFR-013; SC-003, SC-004, SC-005, SC-008)
- [ ] T023 Assemble traceability matrix (OBJ→FR/NFR→task→SC/EC). **DoD**: 100% coverage; zero
  orphans. (Traces: all; Constitution Quality Gates)

---

## Dependencies & Execution Order

- **Setup (T001–T002)** → no deps.
- **Foundational (T003–T007)** → after Setup; **blocks all user stories**.
- **User stories (T008–T019)** → after Foundational; US1..US5 independently deliverable; priority
  order P1→P5.
- **Polish (T020–T023)** → after the stories they cover.

## Parallel Opportunities

- T001/T002 parallel. Within Foundational, T005/T006/T007 parallel after T003/T004.
- `[P]` tasks within a story touch different concerns and are parallel-safe.
- US1..US5 can be staffed in parallel once Foundational is complete.

## Model Routing & Parallel Execution Plan

Cost-aware routing for a future agent-driven implementation, per [AGENTS.md](../../AGENTS.md) §8:
the most capable tier is **reserved for high-risk judgment**, not used for every task. Tiers are
**routing recommendations** (stable roles), not proof that a given runtime process used that model.

### Tiers

| Tier | Model (recommended) | Reasoning effort | Intended work |
|------|--------------------|------------------|---------------|
| Economy | **Claude Haiku 4.5** | low | Mechanical/pattern-following docs, convention capture, matrix assembly, link/format checks |
| Standard | **Claude Sonnet 5** | medium | Bounded specification drafting within an established pattern; scenario/QA authoring |
| Advanced | **Claude Opus 4.8** | high | Security/compliance-critical design, fail-closed logic, adversarial review, gate synthesis |

### Task → model assignment

Author and reviewer are always **different roles** (independence). Adversarial review by Opus is
mandatory wherever money, privilege, or fail-closed semantics are decided.

| Task | Author tier | Reviewer | Why this tier |
|------|-------------|----------|---------------|
| T001 money/time conventions | Haiku | Sonnet | Capturing fixed conventions (minor units, ISO-4217, UTC/issuer calendar) — mechanical. |
| T002 command envelope | Haiku | Sonnet | Enumerating fixed envelope fields + outcome enum — mechanical. |
| T003 composite card state | **Opus** | Sonnet (consistency) | Core security state model; wrong design enables privilege bypass (FR-036). |
| T004 idempotency + concurrency | **Opus** | Sonnet (consistency) | Correctness-critical single-winner/replay semantics (SC-005, SC-008). |
| T005 audit stream | Sonnet | **Opus (adversarial)** | Pattern is set by constitution V; tamper-evidence choices need hostile review. |
| T006 access evaluation | Sonnet | **Opus (adversarial)** | Least-privilege factors enumerated in FR-025; bypass hunting needs Opus. |
| T007 sensitive-data boundary | Sonnet | **Opus (adversarial)** | Allowlist/masking rules bounded by constitution VI; leak hunting needs Opus. |
| T008 freeze handling | Sonnet | Sonnet (peer) | Bounded drafting against contract C1; risk-reducing path. |
| T009 freeze idempotency + audit | Haiku | Sonnet | Applies T004/T005 patterns to one command — mechanical. |
| T010 fail-closed unfreeze | **Opus** | Sonnet (consistency) | The safety-asymmetry heart of the spec (FR-007, SC-006). |
| T011 restriction protection + SoD | **Opus** | Sonnet (consistency) | Separation-of-duties release; insider-risk decision (FR-030). |
| T012 unfreeze audit | Haiku | Sonnet | Applies audit pattern to one command — mechanical. |
| T013 limit validation | Haiku | Sonnet | Enumerable validation rules (EC-06/07) — mechanical. |
| T014 atomic authorization evaluation | Sonnet | **Opus (adversarial)** | Money math + DST periods; review hunts double-count/boundary bugs. |
| T015 limit risk-asymmetry + concurrency | Sonnet | **Opus (adversarial)** | Combines fail-closed + single-winner; review checks race/ambiguity handling. |
| T016 keyset pagination | Sonnet | Sonnet (peer) | Standard snapshot-keyset pattern per contract H1/H2. |
| T017 history authz + masking | Sonnet | **Opus (adversarial)** | Data-exposure surface; review hunts leak paths (EC-16). |
| T018 ops case-scoped authz | Sonnet | **Opus (adversarial)** | Privilege surface; review hunts scope/expiry bypasses (EC-18/19). |
| T019 compliance export | Sonnet | **Opus (adversarial)** | Privacy-critical allowlist/bounding (EC-20/21). |
| T020 evidence recovery | Sonnet | **Opus (adversarial)** | Incident timelines bounded by SC-007; review checks degraded-mode gaps. |
| T021 velocity guard | Haiku | Sonnet | Single bounded guard rule (EC-23) — mechanical. |
| T022 verification catalog | Sonnet | Sonnet (peer) | Test-category/fixture documentation per NFR-013. |
| T023 traceability matrix | Haiku | **Opus (gate)** | Assembly is mechanical; the final coverage gate (analyze) is Opus. |

**Distribution**: 7 × Haiku · 12 × Sonnet · 4 × Opus-authored — plus Opus concentrated in 9
adversarial/gate reviews. Opus is never the default author; Haiku never authors a security decision.

### Parallel execution waves

Wall-clock is bounded by the dependency chain, not the task count. Within a wave, tasks run
concurrently (different agents), consistent with the `[P]` markers and phase dependencies above:

| Wave | Tasks (concurrent) | Gate to next wave |
|------|--------------------|-------------------|
| W1 | T001 ∥ T002 | conventions fixed |
| W2 | T003 ∥ T004 | state + concurrency models approved (Opus) |
| W3 | T005 ∥ T006 ∥ T007 | foundations reviewed (Opus adversarial) |
| W4 | US1 (T008→T009) ∥ US2 (T010→T011, T012∥) ∥ US3 (T013→T014→T015) ∥ US4 (T016∥T017) ∥ US5 (T018∥T019) | each story's checkpoint independently |
| W5 | T020 ∥ T021 ∥ T022 | polish reviewed |
| W6 | T023 → final analyze gate (Opus) | package done |

Longest chain: W1→W2→W3→W4(US3: 3 sequential tasks)→W5→W6 ≈ **9 sequential task slots** for 23
tasks + reviews — reviews of wave N run concurrently with authoring of wave N+1 where they don't
gate it.

## Low-level task ↔ user-story slice map

| Slice | Tasks | Doc |
|-------|-------|-----|
| US1 Freeze | T008, T009 | [task-slices/us1-freeze.md](task-slices/us1-freeze.md) |
| US2 Unfreeze | T010, T011, T012 | [task-slices/us2-unfreeze.md](task-slices/us2-unfreeze.md) |
| US3 Limits | T013, T014, T015 | [task-slices/us3-limits.md](task-slices/us3-limits.md) |
| US4 History | T016, T017 | [task-slices/us4-transactions.md](task-slices/us4-transactions.md) |
| US5 Oversight | T018, T019 | [task-slices/us5-oversight.md](task-slices/us5-oversight.md) |

**Total**: 23 documented low-level tasks (19 story/foundational + 4 polish), each with acceptance
criteria and traceability. No code produced.
