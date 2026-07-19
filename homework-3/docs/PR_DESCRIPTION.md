# PR: Homework 3 — Specification-Driven Design for Regulated Virtual Card Controls

> Draft PR body. Paste into the GitHub pull request description after the `homework-3` branch is
> pushed. Blob/screenshot links target that branch.

## ✅ Summary

Completes **Homework 3: Specification-Driven Design** as a **documentation-only** package for
regulated virtual-card controls, built with **GitHub Spec Kit driven by Claude Code**. It turns the
broad assignment seed into an implementation-ready, fully-traceable specification covering:

- cardholder freeze and fail-closed unfreeze;
- atomic per-transaction / daily / monthly spending limits;
- stable, authorization-bound transaction history;
- least-privilege, case-scoped ops access and read-only compliance export;
- append-only audit evidence, propagation recovery, privacy, and measurable service targets.

**No** application source, API/UI, schema, migration, package manifest, dependency install,
infrastructure, or deployment artifact was created. The Spec Kit flow intentionally stops before
implementation — Homework 3 grades the specification package.

## 📦 Deliverables

| # | File | What it is |
|---|------|-----------|
| 1 | [`specification.md`](../specification.md) | Canonical layered spec: 1 high-level + 6 observable mid-level objectives, 40 FR, 14 NFR, 26 edge cases, 8 success criteria, begin/end context, implementation-note guardrails, and 23 future low-level tasks with acceptance criteria — edge cases, verification, and performance integrated, not appended. |
| 2 | [`AGENTS.md`](../AGENTS.md) | Agent/AI guidance: hypothetical stack, banking domain rules, style, testing/verification expectations, security/compliance, edge-case posture. |
| 3 | [`CLAUDE.md`](../CLAUDE.md) | Editor/AI rules — the file Claude Code auto-loads as project rules (Always/Never/naming/workflow). |
| 4 | [`README.md`](../README.md) | Student summary, rationale (incl. how performance targets + verification depth were chosen), and industry-practice mapping with file/section references. |
| — | [`specs/001-virtual-card-controls/`](../specs/001-virtual-card-controls/) | Full Spec Kit process package (provenance). |
| — | [`.specify/memory/constitution.md`](../.specify/memory/constitution.md) | Project constitution — 7 regulated-FinTech principles governing the package. |

## 🛠️ Spec Kit workflow (Claude Code)

Scaffolded with `specify init --here --integration claude` **inside `homework-3/`** (self-contained),
then driven through the gated flow:

```text
constitution → specify → clarify → checklist → plan → tasks → analyze   (implement NOT run)
```

- **Constitution** (v1.0.0): fail-closed on risk, exact money/time, idempotent versioned writes,
  least privilege, append-only audit, sensitive-data boundary, no-code boundary.
- **Clarify**: surfaced one genuine ambiguity — *who may release an operations-initiated freeze* —
  resolved as **separation of duties** (distinct second authorized actor), encoded in FR-030/NFR-010.
- **Analyze**: 100% requirement→task coverage, zero orphans, zero constitutional conflicts; two
  accepted Low administrative notes.

## 🛡️ FinTech & reliability decisions

- **Composite state**: lifecycle × restriction sources; a cardholder unfreeze can never clear an
  ops/fraud restriction (strongest restriction governs).
- **Safety asymmetry**: freeze is effective on a durable local block (propagation may be `pending`);
  risk-increasing actions (unfreeze, limit increase, export) **fail closed** on any ambiguity.
- **Exact money/time**: integer minor units + ISO-4217; immutable UTC + issuer-calendar, DST-safe
  periods; inclusive limit boundary.
- **Idempotency & concurrency**: keys bound to actor+card+action+payload; optimistic versioning →
  exactly one winner + deterministic conflict.
- **Stable history**: snapshot-bound keyset pagination — no duplicates/skips/order drift.
- **Least privilege**: per-action re-evaluation of ownership/case/purpose/expiry/step-up/permission.
- **Auditability**: append-only, tamper-evident, sanitized; denials audited; missing-evidence
  recovery timeline.
- **Sensitive-data boundary**: no PAN/CVV/credentials/raw payloads anywhere; tokens/masked PAN only;
  export allowlist.

## 🤖 Model routing & parallel execution (cost-aware)

The task plan assigns every task a **model tier** and schedules work in **6 parallel waves**
(~9 sequential slots for 23 tasks):

| Tier | Model | Intended work |
|------|-------|---------------|
| Economy | Claude Haiku 4.5, low effort | 7 mechanical tasks (conventions, pattern-following audit/validation docs, matrix assembly) |
| Standard | Claude Sonnet 5, medium | 12 bounded drafting tasks (story specs, contracts application, QA catalog) |
| Advanced | Claude Opus 4.8, high | 4 security-critical design tasks (composite state, idempotency/concurrency, fail-closed unfreeze, separation of duties) + 9 adversarial reviews + the final analyze gate |

Author and reviewer roles are always independent; Opus is reserved for high-risk judgment, never the
default author; Haiku never authors a security decision. Tiers are routing recommendations for a
future agent-driven implementation, honestly labeled as such. Full table:
[`tasks.md → Model Routing & Parallel Execution Plan`](../specs/001-virtual-card-controls/tasks.md#model-routing--parallel-execution-plan).

## 🎯 Assumed measurable targets

Homework hypotheses to validate before production — not observed SLIs or regulatory mandates:

- interactive controls + first history page **p95 ≤ 2s**; external confirmation/consistency/audit
  **p95 ≤ 5s**;
- propagation alert **60s**, recovery/escalation **5/15 min**, **99.9%** monthly availability
  (unsafe fallbacks excluded);
- **24h** idempotency window; **20 same-version** concurrency fixture (exactly one winner);
- **100,000 synthetic transactions / 24 months** history fixture with zero duplicates, skips,
  leaks, prohibited fields, or order drift.

## 🧪 Validation evidence

- Requirements checklist: **16/16 PASS**; FinTech checklist: **38/38 applicable PASS**.
- Coverage: **6/6 OBJ, 40/40 FR, 14/14 NFR, 26/26 EC, 8/8 SC**; **0** orphan tasks.
- Cross-artifact analysis: **PASS** (two accepted Low administrative notes).
- Mechanical: local links resolve; graded docs have no trailing whitespace; **no** source/API/UI/
  schema/migration/manifest present (no-code boundary held); `speckit-implement` not run.

Detail: [`reviews/final-validation.md`](../specs/001-virtual-card-controls/reviews/final-validation.md) ·
[`reviews/analyze.md`](../specs/001-virtual-card-controls/reviews/analyze.md) ·
[`reviews/traceability-matrix.md`](../specs/001-virtual-card-controls/reviews/traceability-matrix.md)

## ⚠️ Challenges & decisions

- **Broad seed → concrete spec**: converted into explicit actor journeys, normative behavior, edge
  cases, measurable targets, evidence, and future tasks without inventing executable interfaces.
- **Safety vs eventual consistency**: separated durable local blocking from downstream propagation so
  freeze stays safe while truthfully reporting `pending`.
- **Internal access vs privacy**: constrained ops/compliance by case, purpose, permission, expiry,
  step-up, export size, and a versioned field allowlist.
- **`agents.md` casing**: assignment names `agents.md`; the AI-tool convention is `AGENTS.md`. On
  case-insensitive APFS they are one file; documented explicitly.
- **Editor rules for Claude Code**: provided `CLAUDE.md` (auto-loaded project rules) as the
  editor/AI-rules deliverable, matching the tool actually used.

## 🔍 How to review

1. [`specification.md`](../specification.md) — behavior + traceability.
2. [`AGENTS.md`](../AGENTS.md) and [`CLAUDE.md`](../CLAUDE.md) — agent/editor rules.
3. Spec Kit package: [plan](../specs/001-virtual-card-controls/plan.md),
   [tasks](../specs/001-virtual-card-controls/tasks.md),
   [analysis](../specs/001-virtual-card-controls/reviews/analyze.md).
4. Confirm no implementation or production-readiness claim is present.

## 📸 Screenshots

Embedded below; they render from the `homework-3` branch
([`docs/screenshots/`](screenshots/)).

### 1. Spec-driven kickoff: plan-first contract + Spec Kit exploration

The session starts from the assignment seed with an explicit **plan → user validates → write**
contract and the instruction to use GitHub Spec Kit. Claude Code explores `homework-3/` (files,
branches, TASKS.md) before proposing anything.

![Spec Kit kickoff and exploration in Claude Code](https://raw.githubusercontent.com/mgplaya/gen-ai-software-engineering/homework-3/homework-3/docs/screenshots/Screenshot%202026-07-15%20at%2017.04.49.png)

### 2. User validation gates: decisions stay with the student

Key decisions (how to land the work in git, review order for the graded artifacts) are surfaced as
structured questions instead of being assumed — the package is written only after explicit
validation, and git actions wait for approval.

![Structured user-validation questions and review order](https://raw.githubusercontent.com/mgplaya/gen-ai-software-engineering/homework-3/homework-3/docs/screenshots/Screenshot%202026-07-15%20at%2017.04.12.png)

### 3. Cost-aware model routing recorded into the plan

The task plan's model routing (Haiku = mechanical, Sonnet = bounded drafting, Opus =
security-critical design + adversarial review; author ≠ reviewer) being summarized and committed
into `tasks.md` / `plan.md` / `specification.md`.

![Model routing tiers written into the task plan](https://raw.githubusercontent.com/mgplaya/gen-ai-software-engineering/homework-3/homework-3/docs/screenshots/Screenshot%202026-07-15%20at%2017.48.36.png)

---

🤖 Prepared with Claude Code using GitHub Spec Kit. Documentation only; no implementation was
generated.
