# PR: Homework 3 — Specification-Driven Design for Regulated Virtual Card Controls

> Draft PR body. Paste this document into the GitHub pull request description after the
> `homework-3` branch is pushed. Screenshot URLs below target that branch.

## ✅ Summary

This PR completes **Homework 3: Specification-Driven Design** as a documentation-only package for
regulated virtual-card controls. It turns the broad assignment seed into an implementation-ready,
traceable specification covering:

- cardholder freeze and fail-closed unfreeze;
- atomic per-transaction, daily, and monthly spending limits;
- stable, authorization-bound transaction history;
- case-scoped operations access and read-only compliance export;
- append-only audit evidence, propagation recovery, privacy, and measurable service targets.

No application source code, executable API/UI, database schema, migration, package manifest,
dependency installation, infrastructure, or deployment artifact was created. The Spec Kit workflow
intentionally stops before implementation because Homework 3 grades the specification package.

## 📦 Assignment deliverables

### 1. Layered canonical specification

[`homework-3/specification.md`](https://github.com/mgplaya/gen-ai-software-engineering/blob/homework-3/homework-3/specification.md) is the canonical graded specification. It
contains:

- one high-level objective and six observable mid-level objectives;
- five prioritized user journeys with independent acceptance scenarios;
- 41 functional requirements, 14 policy/non-functional requirements, 26 feature-specific edge
  cases, and 8 measurable success criteria;
- explicit beginning and ending workspace contexts;
- implementation guardrails for composite card state, exact money and time, authorization,
  idempotency, concurrency, pagination, privacy, audit, and recovery;
- 19 future low-level implementation tasks with task-local acceptance criteria;
- objective-to-requirement-to-task traceability and a one-to-one agent/delivery matrix.

The document uses stable `OBJ`, `FR`, `NFR`, `EC`, `SC`, and `LL-US` identifiers so every important
decision can be traced from intent to future verification evidence.

### 2. Agent guidance and active Codex rules

[`homework-3/AGENTS.md`](https://github.com/mgplaya/gen-ai-software-engineering/blob/homework-3/homework-3/AGENTS.md) contains both the repository collaboration policy and the
assignment-required future-agent guidance.

There is deliberately **no separate editor-specific rules directory or
`.github/copilot-instructions.md` file**. Copilot was only an example in the assignment; this
repository was developed with **ChatGPT/Codex**, and Codex natively reads project instructions from
`AGENTS.md`. Keeping the active rules there avoids duplicating or drifting instructions for an AI
tool that was not used.

The assignment asks for `agents.md`, while the operational Codex filename is `AGENTS.md`. On this
case-insensitive APFS workspace those names resolve to the same physical file. The operational and
graded sections are therefore explicitly delimited in one document, with operational repository
rules taking precedence.

The guidance includes:

- specification-first approval gates and a strict no-code boundary;
- hypothetical future stack assumptions without installing or mandating packages;
- FinTech-safe state, money, time, privacy, authorization, evidence, and failure rules;
- synthetic-data-only testing expectations;
- independent review requirements and cost-aware model routing.

### 3. README and industry-practice rationale

[`homework-3/README.md`](https://github.com/mgplaya/gen-ai-software-engineering/blob/homework-3/homework-3/README.md) identifies the student and assignment, explains the layered
design, justifies assumed performance targets and verification depth, and maps relevant practices to
specific specification sections.

The references include PCI DSS vocabulary, NIST SP 800-53, NIST SP 800-63B, NIST Privacy Framework,
and OWASP ASVS. They are used as control and verification references only. The submission explicitly
does not claim certification, jurisdiction-specific legal compliance, accessibility conformance, or
production readiness.

### 4. Spec Kit provenance and planning package

[`homework-3/specs/001-virtual-card-controls/`](https://github.com/mgplaya/gen-ai-software-engineering/tree/homework-3/homework-3/specs/001-virtual-card-controls) preserves the
adapted GitHub Spec Kit flow:

```text
constitution → specify → clarify → checklist → Gate 1
             → plan → Gate 2 → tasks → analyze → Gate 3 package
```

The package includes the approved working specification and plan, research decisions, conceptual
data model, behavioral contracts, quickstart/validation scenarios, requirements and FinTech
checklists, five user-story task slices, 40 orchestration tasks, traceability evidence, independent
reviews, and final validation reports.

`speckit-implement` was not run.

## 🤖 Agent and model routing

The task plan defines ten stable **routing roles**, not ten model names:

| Tier | Recommended Codex profile | Intended work |
|------|---------------------------|---------------|
| Economy | `gpt-5.6-luna`, Low/Light reasoning | Hashes, extraction, formatting, link/terminology checks, status recording |
| Standard | `gpt-5.6-terra`, Medium reasoning | Bounded specification drafting, architecture mapping, test scenarios, focused QA |
| Advanced | `gpt-5.6-sol`, High reasoning | FinTech, security/compliance, adversarial review, conflict resolution, gate synthesis |

For example, `AG-E01 · codex-docs-ops` is the stable owner role for T001, T002, T034, T039, and
T040. It should normally be instantiated with **GPT-5.6 Luna at Low/Light reasoning**. `AG-E01` is
not itself a model, and the recommended mapping is not presented as proof that a separate runtime
process used that model. Where the runtime does not expose per-agent model evidence, the repository
records the profile honestly as a routing recommendation.

All T001–T040 tasks have exactly one primary owner. Review-only roles are separate from author roles,
and Advanced/Sol is reserved for high-risk judgment rather than being used for every task.

Full assignment table: [`specs/001-virtual-card-controls/tasks.md`](https://github.com/mgplaya/gen-ai-software-engineering/blob/homework-3/homework-3/specs/001-virtual-card-controls/tasks.md#concrete-agent-assignment).

## 🛡️ FinTech and reliability decisions

- **Composite state:** lifecycle and restriction sources are separate; stronger or unknown
  restrictions cannot be removed by cardholder unfreeze.
- **Durable freeze safety:** freeze is accepted only when the local authorization block is durable;
  downstream processor propagation may be pending without weakening the block.
- **Fail-closed risk-increasing actions:** ambiguous unfreeze, limit increase, or compliance export
  never returns success or pending.
- **Exact money and time:** scaled currency amounts, immutable occurrence instants, issuer billing
  calendar, and DST-safe period boundaries are explicit.
- **Idempotency and concurrency:** command identity is actor/card/action/payload-bound; optimistic
  versioning gives one deterministic winner and exact retries reuse the original outcome.
- **Stable history:** snapshot-bound keyset continuation prevents duplicates, skips, and order drift
  during concurrent arrivals or status changes.
- **Least privilege:** ownership/role, open assigned case, purpose, expiry, and exact permission are
  re-evaluated for every sensitive action or page.
- **Auditability:** business evidence is append-only, tamper-evident, sanitized, and reconciled
  separately from diagnostics; missing evidence has explicit alert, recovery, degraded-mode, and
  incident timelines.
- **Sensitive-data boundary:** full PAN, CVV, credentials, raw dependency payloads, unrelated case
  data, and unredacted free text are prohibited from views, logs, evidence, exports, fixtures, and
  prompts.

## 🎯 Assumed measurable targets

These are homework hypotheses to validate before production, not observed SLIs or regulatory
mandates:

- healthy interactive controls and first history page: **p95 ≤ 2 seconds**;
- external freeze confirmation, control consistency, and audit queryability: **p95 ≤ 5 seconds**;
- unresolved propagation alert: **60 seconds**; recovery/escalation: **5/15 minutes**;
- calendar-month availability target: **99.9%** with unsafe fallbacks excluded from success;
- idempotency window: **24 hours**;
- concurrency fixture: **20 same-version commands** with exactly one winner;
- history fixture: **100,000 synthetic transactions across 24 months**, with zero duplicates, skips,
  authorization leaks, prohibited fields, or order drift.

## 🧪 Validation evidence

- Requirements checklist: **20/20 PASS**.
- FinTech checklist: **38/38 PASS**.
- Coverage: **6/6 OBJ, 41/41 FR, 14/14 NFR, 26/26 EC, 8/8 SC**.
- Orchestration: **40/40 tasks**, each with traces, role, model rationale, inputs/output,
  dependencies, parallel-safety, acceptance criteria, and reviewer.
- Concrete routing: **10 role IDs cover T001–T040 exactly once**; author and final-review roles are
  independent.
- Future slices: **19/19 canonical low-level tasks** match the five task-slice documents.
- Spec Kit analysis: **100% normative coverage**, zero unmapped tasks, zero constitutional conflicts,
  and two accepted Low administrative provenance notes.
- Independent FinTech, security/compliance/privacy, and QA/performance reviews: **PASS**, with no open
  Critical, High, Medium, or Low product-quality finding.
- Formatting and repository checks: `git diff --check` passes; graded local links resolve.
- No-code boundary: **PASS**.

Detailed evidence: [`reviews/gate-3-package.md`](https://github.com/mgplaya/gen-ai-software-engineering/blob/homework-3/homework-3/specs/001-virtual-card-controls/reviews/gate-3-package.md) ·
[`reviews/final-validation.md`](https://github.com/mgplaya/gen-ai-software-engineering/blob/homework-3/homework-3/specs/001-virtual-card-controls/reviews/final-validation.md) ·
[`reviews/analyze.md`](https://github.com/mgplaya/gen-ai-software-engineering/blob/homework-3/homework-3/specs/001-virtual-card-controls/reviews/analyze.md)

## ⚠️ Challenges and decisions

- **Broad seed requirements:** converted into explicit actor journeys, normative behavior, edge
  cases, measurable targets, evidence, and future tasks without inventing executable interfaces.
- **Safety versus eventual consistency:** separated durable local authorization blocking from
  downstream propagation so freeze can remain safe while truthfully reporting pending state.
- **Internal access versus privacy:** constrained operations and compliance by case, purpose,
  permission, expiry, step-up, export size, and current versioned field allowlists.
- **Canonical publication:** preserved the approved working specification as provenance while
  synchronizing only six administrative task mappings in the canonical graded document.
- **Editor-rule mismatch:** removed the illustrative Copilot artifact and placed active ChatGPT/Codex
  rules in `AGENTS.md`, the instruction surface actually consumed by Codex.
- **Case-insensitive filesystem:** documented why `AGENTS.md` and assignment-required `agents.md`
  share one inode and separated their logical sections explicitly.
- **Cost-aware orchestration:** separated mechanical, bounded, and high-risk work so GPT-5.6 Sol is
  not the default for every task.

## 🔍 How to review

This PR has no executable test or build command. Review the documentation package in this order:

1. Read [`specification.md`](https://github.com/mgplaya/gen-ai-software-engineering/blob/homework-3/homework-3/specification.md) for product behavior and traceability.
2. Review [`AGENTS.md`](https://github.com/mgplaya/gen-ai-software-engineering/blob/homework-3/homework-3/AGENTS.md) for active Codex rules and future-agent guardrails.
3. Read [`README.md`](https://github.com/mgplaya/gen-ai-software-engineering/blob/homework-3/homework-3/README.md) for rationale, performance assumptions, and industry mapping.
4. Inspect the [Spec Kit plan](https://github.com/mgplaya/gen-ai-software-engineering/blob/homework-3/homework-3/specs/001-virtual-card-controls/plan.md),
   [task routing](https://github.com/mgplaya/gen-ai-software-engineering/blob/homework-3/homework-3/specs/001-virtual-card-controls/tasks.md), and
   [final evidence package](https://github.com/mgplaya/gen-ai-software-engineering/blob/homework-3/homework-3/specs/001-virtual-card-controls/reviews/gate-3-package.md).
5. Confirm that no implementation or production-readiness claim is present.

Optional mechanical checks from the repository root:

```bash
git diff --check
find homework-3 -type f | sort
rg -n "OBJ-|FR-|NFR-|EC-|SC-|LL-US" homework-3/specification.md
rg -n "speckit-implement|Copilot-specific|no application" homework-3
```

## 📸 Screenshots

The screenshots are embedded directly below and render from the `homework-3` branch.

### Spec Kit workflow and cost-aware agent planning

The planning discussion confirms that Codex can run the Spec Kit flow, pause at approval gates, and
stop before implementation. It also records the requirement to route routine tasks away from the
most expensive model.

![Spec Kit workflow and agent-routing decision](https://raw.githubusercontent.com/mgplaya/gen-ai-software-engineering/homework-3/homework-3/docs/screenshots/Screenshot%202026-07-14%20at%2023.43.17.png)

### Clarification example: operations freeze release

The specification did not silently invent who may remove an operations freeze. The ambiguity was
surfaced as a product/security decision, with the recommended separation-of-duties option documented
before the specification was finalized.

![Clarification of operations freeze release authority](https://raw.githubusercontent.com/mgplaya/gen-ai-software-engineering/homework-3/homework-3/docs/screenshots/Screenshot%202026-07-15%20at%2000.44.43.png)

---

🤖 Prepared with ChatGPT/Codex using GitHub Spec Kit. Documentation only; no implementation was
generated.
