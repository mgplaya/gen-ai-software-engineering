# Phase 1 Data Model: Artifacts & Entities

**Feature**: [spec.md](./spec.md) | **Date**: 2026-07-27

No database; the "data model" is the durable artifacts exchanged between agents plus
the target app's entities.

## Pipeline Artifacts (under `context/bugs/001/`)

```mermaid
flowchart LR
  FR[bug-context.md + buggy src/] --> A[research/codebase-research.md<br/>+ implementation-plan.md]
  A --> V[research/verified-research.md]
  A --> T[test-report.md RED]
  V --> T
  T --> I[fix-summary.md GREEN]
  I --> S[security-report.md]
```

| Artifact | Produced by | Consumed by | Required sections |
|----------|-------------|-------------|-------------------|
| `bug-context.md` | Human (seed) | Architect | goal, capabilities, non-functional, security, done |
| `research/codebase-research.md` | **Architect** | Bug Research Verifier, Test Gen | Overview; Public Interface; Behaviors & Invariants; Edge Cases; Security-Sensitive Requirements; References |
| `implementation-plan.md` | **Architect** | Bug Fixer, Test Gen | Test command; Per-Bug Fix (before/after); Build Sequence |
| `research/verified-research.md` | **Bug Research Verifier** | human gate, Test Gen | Verification Summary; Verified Claims; Discrepancies; Quality Assessment; References |
| `test-report.md` | **Unit Test Generator** | Bug Fixer | Generated Tests; RED Run Outcome; FIRST Assessment; References |
| `fix-summary.md` | **Bug Fixer** | Security Verifier | Changes Made; Test Result (RED→GREEN); Overall Status; Manual Verification; References |
| `security-report.md` | **Security Verifier** | human | Scope; Security Requirement Check; Findings (severity/`file:line`/remediation); Summary |

Bold rows are the five agents' outputs.

## Target App Entities

- **Bill**: a `total` amount to divide.
- **EvenSplit**: dividing `total` among `n` so shares sum exactly to `total`.
- **WeightedSplit**: dividing `total` by weights, proportional to `sum(weights)`.
- **AmountInput**: an untrusted CLI string parsed safely (never executed).

## Invariants (testable — written as RED tests first)

- **INV-1**: `sum(split_evenly(total, n)) == total`.
- **INV-2**: `split_by_weights(total, w)[i] == total * w[i] / sum(w)`.
- **INV-3**: `parse_amount(s)` never executes `s`; non-numeric input raises a
  controlled error.

## Permission Boundaries

| Agent | May read | May write |
|-------|----------|-----------|
| Architect | bug-context | `research/codebase-research.md` + `implementation-plan.md` + the buggy `src/` (no logic) |
| Bug Research Verifier | research + buggy src | `research/verified-research.md` only |
| Unit Test Generator | plan + research + buggy src | `tests/**` + `test-report.md` |
| Bug Fixer | plan + tests + buggy src | `src/**` logic + `fix-summary.md` |
| Security Verifier | implemented src + fix-summary | `security-report.md` only |
