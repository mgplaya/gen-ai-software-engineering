# Homework 4 — Architect-Led TDD Build Pipeline

**Author / Student**: Mykhailo Gorishnyi (`mgplaya`)
**Course**: GenAI and Agentic AI for Software Engineering
**Method**: Spec-Driven Development with [GitHub Spec Kit](https://github.com/github/spec-kit)

A **5-agent, design-first, test-driven** pipeline. An **Architect** designs a small
Python app and describes the build sequence; a **human verifies the plan**; then the
pipeline writes **failing tests first (RED)** and only afterwards **implements the
code (GREEN)**, finishing with a **security review**. Everything runs from **one
command** with a human gate in the middle. Each agent runs on a **deliberately
chosen model**.

---

## The pipeline

```mermaid
flowchart TD
  FR["feature-request.md"] --> A["1. Architect<br/>(opus-4-8) — design + stubs"]
  A --> G{"HUMAN verifies<br/>the plan"}
  G --> V["2. Design Verifier<br/>(opus-4-8, read-only)"]
  V --> T["3. Unit Test Generator<br/>(haiku-4-5) — TDD RED"]
  T --> I["4. Implementer<br/>(sonnet-5) — TDD GREEN"]
  I --> S["5. Security Verifier<br/>(opus-4-8, read-only)"]
```

**Fixed order** (Constitution VII — *Design-First, then TDD*): design → **human
verify** → verify design → failing tests → implementation → security review.

### Workflow definition

The workflow is **declarative** in [`pipeline.yaml`](./pipeline.yaml) — the single
source of truth for the ordered stages, each stage's tool boundary, and the human
gate. [`run-pipeline.sh`](./run-pipeline.sh) is a thin engine that reads it (each
stage's **model** comes from its `agents/*.agent.md` frontmatter, and its **skills**
from that file's `skills:` list). Inspect it with `./run-pipeline.sh --list`.

## Run it

```bash
cd homework-4
python3.11 -m venv .venv && ./.venv/bin/pip install -r requirements.txt   # first time
./run-pipeline.sh                 # runs the Architect, then STOPS for your review
#   ... read context/build/001/architecture.md and the src/ stubs ...
./run-pipeline.sh --continue      # verify design → RED tests → GREEN impl → security
python -m pytest                  # confirm the build is green
```

`run-pipeline.sh` invokes the Claude Code CLI headless (`claude -p`) once per agent,
**auto-loading each agent's skills** and granting each stage **only the tools its
role permits**. See [HOWTORUN.md](./HOWTORUN.md).

## The 5 agents & why each model

Each agent declares its model in its `agents/*.agent.md` frontmatter. Choices follow
Constitution Principle V — *Model-Appropriateness* (heavy where reasoning is
critical, cheap for mechanical work):

| # | Agent | Model | Why this model |
|---|-------|-------|----------------|
| 1 | **Architect** | `claude-opus-4-8` (heavy) | System design is the highest-leverage, most open-ended reasoning; a wrong interface propagates into tests and code. |
| 2 | **Design Verifier** *(the required "Bug Research Verifier")* | `claude-opus-4-8` (heavy) | Approving an incomplete/inconsistent design is the costly failure mode; needs the strongest reasoning. |
| 3 | **Unit Test Generator** (TDD RED) | `claude-haiku-4-5-20251001` (**cheap**) | Turning a specified interface into assertions is mechanical → the cheapest model, per the "tests use light models" policy. |
| 4 | **Implementer** *(the required "Bug Fixer")* (TDD GREEN) | `claude-sonnet-5` (mid) | Real algorithmic work, but bounded by a verified design and a fixed test suite → capable mid-tier. |
| 5 | **Security Verifier** | `claude-opus-4-8` (heavy) | Adversarial review where a missed vulnerability is expensive. |

> The four homework-required agents (Bug Research Verifier, Bug Fixer, Security
> Verifier, Unit Test Generator) are all present; the **Architect** is added, and the
> flow is reordered into design-first TDD (tests before implementation).

## The 4 skills (auto-loaded per agent)

| Skill | Used by | Purpose |
|-------|---------|---------|
| [`architecture-design.md`](./skills/architecture-design.md) | Architect | Required design sections + stub-scaffolding rules + quality bar. |
| [`research-quality-measurement.md`](./skills/research-quality-measurement.md) | Design Verifier | A/B/C/D quality levels + required `verified-design.md` sections. |
| [`unit-tests-FIRST.md`](./skills/unit-tests-FIRST.md) | Unit Test Generator | FIRST properties (Fast, Independent, Repeatable, Self-validating, Timely). |
| [`tdd-red-green.md`](./skills/tdd-red-green.md) | Test Generator + Implementer | RED/GREEN discipline shared across the two TDD agents. |

## Enforced permission boundaries

`run-pipeline.sh` grants each stage only the tools it needs. Verifier stages get
`Read Glob Grep Write` (**no Edit, no Bash**), so they physically cannot mutate code
or run commands; the Architect gets no Bash; only the Implementer and Test Generator
get `Edit Bash`. Constitution Principle II is a hard boundary, not a request.

## What gets built

A tiny `expense_splitter` (even split, weighted split, safe CLI amount parsing),
designed and built from scratch by the pipeline — the Architect scaffolds stubs, the
Implementer fills them. The [feature request](./context/build/001/feature-request.md)
is the only human-authored input to the build.

## How Spec Kit was used

Built spec-first. Artifacts under [specs/001-tdd-build-pipeline/](./specs/001-tdd-build-pipeline/):
constitution (7 principles) → `spec.md` (3 user stories, 12 FRs) → `plan.md`
(Constitution Check passes) → research / data-model / contracts / quickstart →
`tasks.md`.

## Artifacts produced by a run (under `context/build/001/`)

- `architecture.md` — Architect's design + build sequence (+ `src/` stubs)
- `verified-design.md` — Design Verifier (quality level)
- `test-report.md` — RED evidence (failing tests written first)
- `implementation-summary.md` — GREEN evidence (stubs filled, tests pass)
- `security-report.md` — findings with severity/`file:line`/remediation
- `pipeline-run.log` — full transcript

## Repository layout

```
homework-4/
├── pipeline.yaml              # ← declarative workflow (stages, tools, gate)
├── run-pipeline.sh            # thin engine that reads pipeline.yaml (single command + gate)
├── agents/                    # 5 agent definitions (model in frontmatter)
├── skills/                    # architecture-design, research-quality, FIRST, tdd-red-green
├── context/build/001/         # feature request + all pipeline artifacts
├── src/expense_splitter/      # stubs (Architect) → implementation (Implementer)
├── tests/                     # tests written first (RED → GREEN)
├── specs/001-tdd-build-pipeline/  # Spec Kit spec/plan/tasks/design
├── .specify/                  # Spec Kit infrastructure
├── docs/screenshots/          # evidence
└── HOWTORUN.md
```

## AI tools used

- **Claude Code (Opus 4.8)** orchestrated the build, driving the Spec Kit workflow.
- The **pipeline** runs Claude Opus 4.8 / Sonnet 5 / Haiku 4.5 via the `claude` CLI
  headless — real multi-agent execution, one model per role.
