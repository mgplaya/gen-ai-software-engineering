# Homework 3 — Specification-Driven Design: Regulated Virtual Card Controls

**Student**: Mykhailo Gorishnyi
**Assignment**: [Homework 3 — Specification-Driven Design](TASKS.md)
**Method**: [GitHub Spec Kit](https://github.com/github/spec-kit) driven by **Claude Code**
(constitution → specify → clarify → checklist → plan → tasks → analyze; implementation intentionally
not run)

## Summary

This submission is a **documentation-only specification package** for regulated virtual-card
controls: cardholder **freeze/unfreeze**, **per-transaction/daily/monthly spending limits**,
**transaction history**, and an internal **operations/compliance** view. It turns the broad
assignment seed into an implementation-ready, fully-traceable specification with edge cases,
verification, and performance targets treated as first-class — **no application code, API, UI,
schema, or infrastructure** was produced (see [Constitution](.specify/memory/constitution.md),
Principle VII).

### Deliverables

| # | File | What it is |
|---|------|-----------|
| 1 | [`specification.md`](specification.md) | Canonical layered spec (objectives → non-functional/policy → implementation notes → begin/end context → 23 low-level tasks → edge cases → verification → performance). |
| 2 | [`AGENTS.md`](AGENTS.md) | Agent/AI guidelines: hypothetical stack, banking domain rules, style, testing/verification, security/compliance, edge-case posture. |
| 3 | [`CLAUDE.md`](CLAUDE.md) | Editor/AI rules — the file Claude Code auto-loads as project rules (Always/Never/naming/workflow). |
| 4 | `README.md` (this file) | Student summary, rationale, and industry-practice mapping. |
| — | [`specs/001-virtual-card-controls/`](specs/001-virtual-card-controls/) | Full Spec Kit process package (spec, plan, research, data-model, contracts, quickstart, checklists, task slices, tasks, reviews) as provenance. |
| — | [`.specify/memory/constitution.md`](.specify/memory/constitution.md) | Project constitution (7 principles) governing the whole package. |

## Rationale — why the specification is written this way

- **Layered, not prose-heavy.** The [spec](specification.md) separates a single high-level objective
  from six **observable** mid-level objectives (§2), then binds every downstream requirement and task
  to them with stable IDs so a grader (or an AI agent) can execute it without guessing.
- **Constitution first.** The regulated concerns that are easy to bolt on as an afterthought —
  fail-closed safety, exact money/time, idempotency/concurrency, least privilege, append-only audit,
  the sensitive-data boundary — are encoded as **binding principles** in the
  [constitution](.specify/memory/constitution.md) and re-checked at each Spec Kit gate. Requirements
  then *implement* those principles rather than restating them ad hoc.
- **Safety asymmetry made explicit.** The hardest FinTech decision here is eventual consistency vs.
  safety. The spec separates a **durable local authorization block** (freeze is effective
  immediately) from **downstream propagation** (which may be `pending`), so freeze stays safe while
  truthfully reporting state — and every risk-*increasing* action fails closed
  ([specification.md §4](specification.md#4-implementation-notes-guardrails-an-agent-must-not-violate),
  FR-002/003/007).
- **Edge cases, verification, and performance are integrated, not appended.** 26 edge cases each
  carry an expected outcome *and* an audit implication ([§7](specification.md#7-edge-cases--failure-modes));
  verification lists review checkpoints, documented test categories, and synthetic fixtures
  ([§8](specification.md#8-verification)); performance is stated as measurable targets
  ([§9](specification.md#9-expected-performance-assumed-targets)).

### Why these performance targets

All numbers are **assumed targets** (labeled as such), to validate against real SLIs before
production — not observed measurements or regulatory mandates:

- **p95 ≤ 2s** to reflect a freeze (SC-001) — a safety action must feel instant; 2s p95 is a common
  interactive-UX ceiling.
- **p95 ≤ 5s** for external confirmation / cross-surface consistency / audit queryability (SC-002) —
  room for one downstream round-trip while staying within user patience.
- **60s** propagation alert; **5/15 min** recovery/escalation; **99.9%** monthly availability with
  unsafe fallbacks excluded (SC-007) — fast detection plus a standard high-availability ops envelope
  that never counts an unsafe fallback as success.
- **24h** idempotency window (SC-008) — covers a typical retry/settlement horizon.
- **100,000 transactions / 24 months** history fixture and **20 same-version** concurrency fixture
  (SC-004/005) — realistic scale to prove no duplicates/skips/leaks and single-winner concurrency.

### Why this verification depth

Because it is a regulated feature, auditability is treated as binary (100% of actions produce
evidence, SC-003) and denials are audited too. Verification is documented as unit/integration/e2e
**categories with synthetic fixtures** (no test code, per the no-code boundary), and a final
[cross-artifact analysis](specs/001-virtual-card-controls/reviews/analyze.md) enforces 100%
traceability (6/6 OBJ, 40/40 FR, 14/14 NFR, 26/26 EC, 8/8 SC; zero orphans).

## Industry best practices — and where they appear

| Practice | Reference | Where in this package |
|----------|-----------|-----------------------|
| Least privilege / separation of duties | NIST SP 800-53 AC-5/AC-6 | Constitution IV; FR-025, FR-029, FR-030, NFR-009, NFR-010; [internal-access-audit contract](specs/001-virtual-card-controls/contracts/internal-access-audit.md) |
| Step-up authentication assurance | NIST SP 800-63B | Constitution "Security & Compliance"; NFR-001, FR-009 |
| Data minimization / privacy | NIST Privacy Framework | Constitution VI; NFR-002; FR-021/037/038 |
| Cardholder-data handling boundary | PCI DSS vocabulary | Constitution VI; NFR-003; [fintech checklist](specs/001-virtual-card-controls/checklists/fintech.md) CHK122–125 |
| Verification depth / requirement testability | OWASP ASVS | NFR-013; [requirements checklist](specs/001-virtual-card-controls/checklists/requirements.md) |
| Append-only, tamper-evident audit | Regulated-audit practice | Constitution V; FR-033/034/035; contract A3/A4 |
| Exact money (integer minor units, no floats) | Payments engineering | Constitution II; FR-012; [data-model](specs/001-virtual-card-controls/data-model.md) |
| Idempotency + optimistic concurrency | Distributed-systems practice | Constitution III; FR-017/031/032; [control-commands contract](specs/001-virtual-card-controls/contracts/control-commands.md) |
| Snapshot-bound keyset pagination | Scale-safe read design | FR-020; [transaction-history contract](specs/001-virtual-card-controls/contracts/transaction-history.md) |
| Fail-closed / safety asymmetry | Risk engineering | Constitution I; FR-007/015; SC-006 |
| Spec-driven development with gates | GitHub Spec Kit | whole `specs/001-virtual-card-controls/` flow + [reviews](specs/001-virtual-card-controls/reviews/) |

> **Disclaimer**: These frameworks are used as **control and verification references only**. This
> submission does **not** claim certification, jurisdiction-specific legal compliance, accessibility
> conformance, or production readiness.

## How the package was produced

Scaffolded with `specify init --here --integration claude` inside `homework-3/`, then driven through
the Spec Kit phases with Claude Code:

```text
constitution → specify → clarify → checklist → plan → tasks → analyze   (implement NOT run)
```

The clarify phase surfaced one genuine ambiguity — *who may release an operations-initiated freeze* —
resolved as **separation of duties** (a distinct second authorized actor), encoded in FR-030/NFR-010
([clarify record](specs/001-virtual-card-controls/reviews/clarify.md)).

## How to review

1. Read [`specification.md`](specification.md) for behavior and traceability.
2. Read [`AGENTS.md`](AGENTS.md) and [`CLAUDE.md`](CLAUDE.md) for agent/editor rules.
3. Inspect the Spec Kit package: [plan](specs/001-virtual-card-controls/plan.md),
   [tasks](specs/001-virtual-card-controls/tasks.md),
   [analysis](specs/001-virtual-card-controls/reviews/analyze.md),
   [traceability](specs/001-virtual-card-controls/reviews/traceability-matrix.md).
4. Confirm no implementation or production-readiness claim is present.

Optional mechanical checks from `homework-3/`:

```bash
git diff --check
rg -n "OBJ-|FR-|NFR-|EC-|SC-" specification.md
find . -type f -name '*.md' | sort
```
