# Specification: Regulated Virtual Card Controls

> Canonical, layered specification for Homework 3. This is the graded artifact. It is
> **documentation only** — no application code, API, UI, schema, or infrastructure is produced
> (see the [Constitution](.specify/memory/constitution.md), Principle VII).
>
> Produced with **GitHub Spec Kit** driven by **Claude Code**. The full process package
> (constitution → specify → clarify → checklist → plan → tasks → analyze) lives under
> [`specs/001-virtual-card-controls/`](specs/001-virtual-card-controls/) as provenance; this file is
> the distilled canonical spec. Stable IDs (`OBJ`, `FR`, `NFR`, `EC`, `SC`, `T`) make every decision
> traceable from intent to future verification.

---

## 1. High-Level Objective

**Give virtual-card cardholders instant, trustworthy control over their cards — freeze/unfreeze,
spending limits, and transaction history — and give the issuer an auditable, least-privilege
operations/compliance view, safe for a regulated environment.**

**Scope boundary (one sentence)**: This feature governs *controls over already-issued cards* —
freeze/unfreeze, limits, history, and internal oversight — and excludes card manufacture,
disputes/chargebacks, rewards, and currency conversion.

## 2. Mid-Level Objectives (observable)

| ID | Objective | Observable "done" signal |
|----|-----------|--------------------------|
| **OBJ-1** | Instant, safe freeze | Card reads `frozen` and declines new authorizations the moment a durable local block exists, even if downstream propagation is `pending`. |
| **OBJ-2** | Fail-closed unfreeze | Unfreeze returns `success` only when provably safe; otherwise `denied` — never a "maybe"/`pending`. |
| **OBJ-3** | Exact, atomic limits | Authorizations are approved/declined exactly against per-transaction/daily/monthly limits with no rounding drift or double-count. |
| **OBJ-4** | Stable history | Paging a card's history yields no duplicates, skips, or order drift under concurrent arrivals, and leaks no prohibited data. |
| **OBJ-5** | Least-privilege oversight | Internal actions succeed only within an open case, valid purpose, unexpired grant, fresh step-up, and exact permission — re-checked per action. |
| **OBJ-6** | Evidentiary audit + recovery | Every significant action and denial produces append-only, tamper-evident, sanitized audit evidence, with a defined recovery path when evidence is missing. |

## 3. Non-Functional & Policy Requirements

Security, privacy, audit, reliability, and performance are first-class (not afterthoughts). Full
text in [`specs/001-virtual-card-controls/spec.md`](specs/001-virtual-card-controls/spec.md#non-functional--policy-requirements).

| ID | Category | Requirement (summary) |
|----|----------|-----------------------|
| NFR-001 | Security | Risk-increasing actions require **fresh step-up** auth (NIST SP 800-63B-style); session alone insufficient. |
| NFR-002 | Privacy | Data minimization; default to masked/tokenized references (NIST Privacy Framework). |
| NFR-003 | Sensitive data | No PAN/CVV/track/credentials/raw payloads in views, logs, audit, exports, fixtures, or prompts (PCI DSS vocabulary). |
| NFR-004 | Auditability | 100% of business actions produce queryable audit evidence. |
| NFR-005 | Reliability | Freeze safety holds under downstream propagation failure (degraded mode); unsafe fallbacks excluded from success. |
| NFR-006 | Consistency | Reads converge within a stated window; risk actions re-verify at commit. |
| NFR-007 | Concurrency | Deterministic single-winner resolution for concurrent writes. |
| NFR-008 | Performance | Interactive actions + first history page meet stated latency targets (§9). |
| NFR-009 | Least privilege | Internal access is case-scoped, purpose-bound, time-boxed, re-evaluated per action (NIST SP 800-53 AC family). |
| NFR-010 | Separation of duties | Ops-restriction release needs a distinct second authorized actor. |
| NFR-011 | Idempotency | Explicit, uniform replay window/semantics (24h). |
| NFR-012 | Observability | Diagnostics separate from audit; never carry prohibited data. |
| NFR-013 | Verification | Each objective has review checkpoints + documented test categories + synthetic fixtures. |
| NFR-014 | Availability | Control surface meets a monthly availability target excluding unsafe fallbacks. |

## 4. Implementation Notes (guardrails an agent MUST NOT violate)

These are conventions, not code. They bind any future implementation.

- **Composite card state** (FR-036): lifecycle (`active`/`frozen`/`closed`) is orthogonal to
  restriction sources (`cardholder`/`ops`/`fraud`). The **strongest applicable restriction governs**;
  a cardholder unfreeze can never clear an ops/fraud restriction.
- **Safety asymmetry** (FR-002/003/007/015): risk-*reducing* actions succeed on a durable local
  block (propagation may be `pending`); risk-*increasing* actions **fail closed** on any ambiguity.
- **Exact money** (FR-012): integer minor units + explicit ISO-4217 currency. **No floating-point
  money** anywhere — including examples and fixtures.
- **Exact time** (FR-014): immutable UTC occurrence instant; daily/monthly periods assigned by the
  **issuer billing calendar**, DST-safe. Inclusive limit boundary (`amount == limit` → approved).
- **Idempotency & concurrency** (FR-017/031/032): every state-changing command carries an
  idempotency key bound to `actor+card+action+payload` and a `base_version`; identical replays return
  the original outcome; same key + different payload → `conflict`; concurrent same-version writes →
  exactly one winner + deterministic `conflict`.
- **Outcome vocabulary** (FR-039): responses are exactly one of `success | denied | pending |
  conflict`; `pending` is reserved for downstream propagation of risk-reducing actions only.
- **Pagination** (FR-020): snapshot-bound keyset continuation ordered by `(occurred_at, txn_id)`,
  most-recent-first.
- **Audit** (FR-033): append-only, tamper-evident, sanitized, attributable, reconstructable; separate
  store from operational diagnostics; **denials are audited too**.
- **Sensitive-data boundary** (FR-021/037/038): tokens or masked PAN (≤ first-6/last-4) only; exports
  use a versioned field allowlist; notes are sanitized; raw processor payloads are never stored.
- **Authorization freshness** (FR-040): reads re-check authorization at read time, not just at
  session start.

## 5. Context

### Beginning context (what exists before work starts — hypothetical)

- An existing card platform that has already *issued* the virtual cards (this feature only controls
  them).
- A downstream card processor reachable via an internal integration (may lag; may fail).
- An identity/authentication service capable of **step-up** authentication.
- A known issuer billing calendar/timezone per program.
- No controls, limits, history view, oversight surface, or audit stream for these capabilities yet.
- Files present: this specification package under `homework-3/` (no source tree).

### Ending context (what exists after — deliverables)

- This canonical `specification.md` plus `AGENTS.md`, Claude Code rules (`.claude/`), and `README.md`.
- A full Spec Kit process package under `specs/001-virtual-card-controls/` (spec, plan, research,
  data-model, contracts, quickstart, checklists, task slices, tasks, reviews).
- A conceptual data model + behavioral contracts + validation scenarios describing the target
  behavior.
- **No** application source, API/UI, schema, migration, package manifest, or deployment artifact.

## 6. Functional Requirements (by objective)

Full normative text: [`specs/001-virtual-card-controls/spec.md`](specs/001-virtual-card-controls/spec.md#functional-requirements).
Summary of the 40 requirements:

- **Freeze — OBJ-1 (FR-001..FR-005)**: own-card freeze; accept on durable local block; frozen +
  block effective while propagation pending; idempotent; audited.
- **Unfreeze — OBJ-2 (FR-006..FR-010)**: own-card unfreeze; fail-closed; cannot clear stronger/unknown
  restriction; fresh step-up; every attempt audited with non-leaking reason.
- **Limits — OBJ-3 (FR-011..FR-018)**: set per-txn/daily/monthly; validate integer minor units +
  currency; atomic inclusive-boundary evaluation; issuer-calendar periods; reversal/refund handling;
  decrease-atomic/increase-fail-closed; single-winner concurrency; audited.
- **History — OBJ-4 (FR-019..FR-024)**: owner-only, most-recent-first; snapshot keyset pagination;
  masked/tokenized only; explicit empty state; distinct reversal/refund events.
- **Oversight — OBJ-5 (FR-025..FR-030)**: per-action least-privilege checks; ops restriction not
  cardholder-removable; read-only allowlisted bounded export; fail-closed on closed case/expired
  grant; **separation-of-duties release** (FR-030).
- **Cross-cutting — OBJ-6 (FR-031..FR-040)**: idempotency; conflict on payload mismatch; append-only
  audit incl. denials; missing-evidence recovery; composite state; sanitized notes; no raw payloads;
  outcome vocabulary; read-time authorization.

## 7. Edge Cases & Failure Modes

26 enumerated cases (EC-01..EC-26), each with expected user-visible outcome **and** audit/compliance
implication — full table in
[`spec.md`](specs/001-virtual-card-controls/spec.md#edge-cases). Highlights:

| ID | Scenario | Expected behavior |
|----|----------|-------------------|
| EC-03 | Local freeze durable, propagation failing | Card `frozen` + `pending`; block effective; alert on unresolved propagation. |
| EC-04 | Cardholder unfreeze with ops/fraud restriction | Denied, no case-detail leak, stays frozen, audited. |
| EC-05 | Ambiguous unfreeze freshness | Fail closed (never `pending`), audited as denied. |
| EC-08/09 | Limit boundary / period + DST | `amount == limit` approved; correct issuer-calendar period; no double-count. |
| EC-10 | Concurrent limit changes | One winner; loser `conflict`; no lost update. |
| EC-12 | Same idempotency key, different payload | `conflict`; original outcome preserved. |
| EC-14/15 | History changes mid-pagination | Snapshot-bound; no dupes/skips/order drift. |
| EC-20/21 | Export non-allowlisted field / oversize | Omit/reject; bounded; never prohibited data. |
| EC-22 | Missing audit evidence | Alert ≤ 60s; recovery/degraded-mode; incident 5/15 min. |
| EC-25/26 | Free-text / raw processor payload | Sanitized; never stores prohibited data. |

## 8. Verification

How each mid-level objective is known to be met (documentation of intent — no test code produced):

- **Review checkpoints**: spec-quality gate ([requirements checklist](specs/001-virtual-card-controls/checklists/requirements.md)),
  FinTech gate ([fintech checklist](specs/001-virtual-card-controls/checklists/fintech.md)), and a
  final cross-artifact [analysis](specs/001-virtual-card-controls/reviews/analyze.md).
- **Test categories (as documentation)**: unit (limit math, period assignment, state transitions),
  integration (freeze→propagation→pending, unfreeze fail-closed, access checks), and e2e (cardholder
  and oversight journeys), each with **synthetic** fixtures.
- **Fixtures**: a 100k-transaction / 24-month synthetic history (SC-004); a 20 same-version
  concurrent-command set (SC-005); a fail-closed set for risk-increasing actions (SC-006); an
  idempotent-replay set (SC-008). Scenarios: [quickstart.md](specs/001-virtual-card-controls/quickstart.md).
- **Acceptance criteria**: every low-level task (§10) ends with a checkable definition of done.
- **Reconciliation**: audit evidence is periodically reconciled against actions; gaps trigger the
  missing-evidence recovery path (EC-22).
- **Traceability**: [traceability matrix](specs/001-virtual-card-controls/reviews/traceability-matrix.md)
  — 6/6 OBJ, 40/40 FR, 14/14 NFR, 26/26 EC, 8/8 SC covered; 0 orphans.

## 9. Expected Performance (assumed targets)

Labeled **assumed targets** for FinTech UX/ops — to validate against real SLIs before production, not
observed measurements or regulatory mandates. Rationale in the [README](README.md#why-these-performance-targets).

| ID | Target | Why reasonable |
|----|--------|----------------|
| SC-001 | Freeze reflected `frozen` **p95 ≤ 2s** | Safety action must feel instant; 2s p95 is a common interactive UX ceiling. |
| SC-002 | External confirmation / consistency / audit query **p95 ≤ 5s** | Allows a downstream round-trip while staying within user patience. |
| SC-003 | **100%** business actions produce audit evidence | Auditability is binary in a regulated context. |
| SC-004 | 100k/24-month history: **0** dupes/skips/leaks | Correctness at realistic history scale. |
| SC-005 | 20 same-version commands → **exactly 1** winner | Proves single-winner concurrency. |
| SC-006 | **0** risk-increasing actions succeed under ambiguity | Encodes fail-closed. |
| SC-007 | Propagation alert **60s**; recovery **5/15 min**; **99.9%** monthly availability | Fast detection; standard high-availability ops envelope. |
| SC-008 | **24h** idempotency window; 100% replay fidelity | Covers typical retry/settlement horizon. |

## 10. Low-Level Tasks (future implementation slices)

23 documented tasks (T001–T023), organized by user story, each tied to a mid-level objective and
ending with acceptance criteria. Full list: [`tasks.md`](specs/001-virtual-card-controls/tasks.md);
per-story detail under [`task-slices/`](specs/001-virtual-card-controls/task-slices/).

| Phase | Tasks | Serves |
|-------|-------|--------|
| Setup | T001 money/time conventions, T002 command envelope | OBJ-3, OBJ-6 |
| Foundational | T003 composite state, T004 idempotency/concurrency, T005 audit stream, T006 access eval, T007 data boundary | OBJ-1..OBJ-6 |
| US1 Freeze | T008 freeze handling, T009 idempotency+audit | OBJ-1 |
| US2 Unfreeze | T010 fail-closed logic, T011 restriction protection + SoD, T012 audit | OBJ-2 |
| US3 Limits | T013 validation, T014 atomic evaluation, T015 risk asymmetry+concurrency | OBJ-3 |
| US4 History | T016 keyset pagination, T017 authz + masking | OBJ-4 |
| US5 Oversight | T018 case-scoped authz, T019 compliance export | OBJ-5 |
| Polish | T020 evidence recovery, T021 velocity guard, T022 verification catalog, T023 traceability | OBJ-6 + cross-cutting |

**Model routing & parallelism (cost-aware)**: every task carries a recommended model tier and the
schedule runs in 6 parallel waves (~9 sequential slots for 23 tasks) — full table in
[`tasks.md → Model Routing & Parallel Execution Plan`](specs/001-virtual-card-controls/tasks.md#model-routing--parallel-execution-plan):

| Tier | Model | Authors | Used for |
|------|-------|---------|----------|
| Economy | Claude Haiku 4.5 (low effort) | T001, T002, T009, T012, T013, T021, T023 | Mechanical/pattern-following docs and assembly |
| Standard | Claude Sonnet 5 (medium) | T005–T008, T014–T020, T022 | Bounded drafting within an established pattern |
| Advanced | Claude Opus 4.8 (high) | T003, T004, T010, T011 | Security-critical state/concurrency/fail-closed/SoD design |

Opus additionally performs 9 **adversarial reviews** (audit, access, data-boundary, money-math,
privilege, export, recovery) and the final analyze gate; author and reviewer roles are always
independent. Opus is never the default author; Haiku never authors a security decision.

**Example (T014 — atomic authorization evaluation)**
- *Prompt (future)*: "Evaluate each authorization atomically against per-transaction/daily/monthly
  limits with an inclusive boundary; assign cumulative spend to issuer-calendar periods (DST-safe);
  adjust for reversals/partial captures/refunds without double-count."
- *Acceptance criteria*: 50.00 approved / 50.01 declined against a 50.00 limit; counters reset at
  issuer midnight incl. DST; reversal/partial-capture/refund adjust counters correctly.
- *Traces*: FR-013, FR-014, FR-016; EC-08, EC-09, EC-17.

## 11. Assumptions & Out of Scope

- Card issuance, downstream processor, and identity/step-up service pre-exist and are reused.
- Performance/consistency numbers are assumed targets (§9), to validate before production.
- All scenario/fixture data is synthetic.
- **Out of scope**: card manufacture, disputes/chargebacks, rewards, multi-currency conversion, and
  any executable implementation.

---

### Provenance

Spec Kit process package: [`specs/001-virtual-card-controls/`](specs/001-virtual-card-controls/) ·
Constitution: [`.specify/memory/constitution.md`](.specify/memory/constitution.md) ·
Agent guidance: [`AGENTS.md`](AGENTS.md) · Rationale & industry mapping: [`README.md`](README.md).
`speckit-implement` was intentionally not run (no-code boundary).
