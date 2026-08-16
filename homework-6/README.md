# Multi-Agent Banking Transaction Pipeline

**Created by Mykhailo Gorishnyi**

## What this is

This project is a Homework 6 capstone built by **four meta-agents** — Claude Code slash commands
that each generate one layer of the deliverable — and the **three-agent transaction pipeline** they
produced. The pipeline validates, fraud-scores, and settles banking transactions read from
`sample-transactions.json`, passing each transaction between agents as a JSON message envelope
through file-based `shared/` stage directories (no in-memory or network transport between agents).
Every monetary value is handled with `decimal.Decimal` (never `float`), currencies are checked
against an ISO 4217 allowlist, and every agent action is written to an audit trail with account
numbers masked before logging.

Running `uv run python integrator.py` seeds all 8 sample transactions, runs them through the
validator, fraud detector, and settlement processor in turn, and writes one result file per
transaction plus an aggregated `pipeline-summary.json` to `shared/results/`. Results are also
queryable live through a custom FastMCP server (`mcp/server.py`) that exposes the same data as MCP
tools and a resource.

## Agent responsibilities

### Pipeline agents (the running system, `agents/` + `integrator.py`)

- **Transaction Validator** (`agents/transaction_validator.py`) — checks that required fields are
  present, the amount parses as a positive `Decimal`, the currency is in the ISO 4217 allowlist
  (`USD`, `EUR`, `GBP`, `JPY`, `CHF`, `CAD`, `AUD`), and the timestamp is valid ISO 8601. Invalid
  transactions are routed straight to `shared/results/` with `status: "rejected"` and a `reason`;
  valid ones are forwarded to the fraud detector with `status: "validated"`.
- **Fraud Detector** (`agents/fraud_detector.py`) — computes an additive `Decimal` risk score
  (high value > $10,000, unusual timing 00:00–05:00 UTC, cross-border, near-threshold
  $9,000–$10,000). A score `>= 0.7` is rejected to `shared/results/` as `status: "fraud_review"`; a
  score from `0.3` to `< 0.7` is forwarded with `fraud_flag: true`; below `0.3` it is forwarded
  clean — both forwarded cases go on to the settlement processor.
- **Settlement Processor** (`agents/settlement_processor.py`) — computes a 0.1% settlement fee with
  `Decimal` and `ROUND_HALF_UP`, quantized to two decimal places, and always writes the final result
  to `shared/results/` as `status: "settled"` or `status: "settled_with_flag"` (for transactions
  the fraud detector flagged).
- **Integrator** (`integrator.py`) — the orchestrator: recreates the `shared/` subdirectories,
  seeds one message per transaction from `sample-transactions.json` into `shared/input/`, runs the
  three agents above in order over the file-relay protocol, and writes
  `shared/results/pipeline-summary.json` (counts by status, rejection reasons, settled volume per
  currency).

### Meta-agents (`.claude/commands/`, generate and operate the system above)

- **`/write-spec`** (Agent 1 — Specification) — produces `specification.md` (the five-section
  course template) and `agents.md` from the course template, describing the pipeline before any
  code exists.
- **`/generate-pipeline`** (Agent 2 — Code generation) — implements `pipeline/`, `agents/*.py`, and
  `integrator.py` from `specification.md`; required to query the context7 MCP server for FastMCP
  and Python `decimal` documentation, logged in `research-notes.md`.
- **`/generate-tests`** (Agent 3 — Unit tests) — writes the `tests/` suite (per-agent unit tests,
  shared-module tests, one full-pipeline integration test) and iterates until coverage clears the
  90% target, never below the 80% hard gate.
- **`/generate-docs`** (Agent 4 — Documentation, this command) — writes this `README.md` and
  `HOWTORUN.md` from the real specification and code, with author attribution.

Two further operational slash commands wrap the pipeline for day-to-day use once it exists:
`/run-pipeline` (runs `integrator.py` end-to-end and summarizes `shared/results/`) and
`/validate-transactions` (runs the validator's `--dry-run` mode without touching `shared/`).

## Architecture: the file-relay flow

```
sample-transactions.json
        |
        v
  integrator.py   (seeds one envelope per transaction, target = transaction_validator)
        |
        v
  shared/input/
        |
        v
  shared/processing/  <-- claimed by transaction_validator
        |
        +--[invalid: missing field / bad amount / bad currency / bad timestamp]--+
        |                                                                        |
        | [valid: status=validated, target=fraud_detector]                      v
        v                                                            shared/results/
  shared/output/                                                    (status: rejected)
        |
        v
  shared/processing/  <-- claimed by fraud_detector
        |
        +--[risk_score >= 0.7]--------------------------------------------------+
        |                                                                        |
        | [risk_score < 0.7: status=risk_scored, +fraud_flag if 0.3-0.7,        v
        |  target=settlement_processor]                               shared/results/
        v                                                          (status: fraud_review)
  shared/output/
        |
        v
  shared/processing/  <-- claimed by settlement_processor
        |
        v [always terminal]
  shared/results/
  (status: settled | settled_with_flag)
        |
        v
  shared/results/pipeline-summary.json
  (counts by status, rejection reasons, settled volume per currency)
```

A message that fails to parse or fails envelope validation at any stage becomes a terminal
`status: "error"` result in `shared/results/` instead of crashing the run — one bad file never
blocks the rest of the pipeline (`integrator.py::run_agent`).

## Tech stack

| Component | Technology |
|---|---|
| Language / runtime | Python >= 3.12 |
| Package / environment manager | [`uv`](https://docs.astral.sh/uv/) |
| Pipeline dependency | `fastmcp` |
| Test tooling | `pytest`, `pytest-cov` |
| MCP servers | `context7` (`npx -y @upstash/context7-mcp@latest`), custom `pipeline-status` (`mcp/server.py`, built with FastMCP) |
| Automation | Claude Code slash commands (`.claude/commands/`), `PreToolUse` coverage-gate hook (`.claude/hooks/coverage-gate.sh`) |

## Where to go next

- **How to run everything** (install, pipeline run, dry-run validation, tests/coverage, MCP
  servers, hook demo, slash commands): see [`HOWTORUN.md`](HOWTORUN.md).
- **Tests and coverage**: `uv run pytest --cov=agents --cov=pipeline --cov=mcp --cov=integrator`
  — currently 101 tests passing at 97% overall coverage (gate 80%, target 90%).
- **MCP servers**: configured in `mcp.json` / `.mcp.json` — `context7` for framework docs and the
  custom `pipeline-status` server (`mcp/server.py`) exposing `get_transaction_status`,
  `list_pipeline_results`, and the `pipeline://summary` resource.
- **Coverage gate hook**: `.claude/hooks/coverage-gate.sh` runs on every `Bash` tool call, and blocks
  (`exit 2`) any `git push` if coverage drops below `COVERAGE_GATE_MIN` (default 80%).
