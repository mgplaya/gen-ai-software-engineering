# Project Context for AI Agents

This file orients any AI agent (Claude Code or otherwise) working in this repository. Read this
before touching code, tests, or docs — it describes the real system as built, not an aspirational
plan.

## What this project is

A multi-agent banking transaction pipeline built as a Homework 6 capstone. It has **two layers**,
deliberately kept distinct:

1. **Meta-agents** — six Claude Code slash commands in `.claude/commands/` that *generate and
   operate* the pipeline. These are prompts you invoke; they are not part of the running pipeline.
2. **Pipeline agents** — three Python modules under `agents/`, plus the `integrator.py`
   orchestrator, that *are* the running pipeline. These process real transaction data and never
   invoke an LLM themselves — they are deterministic Python functions.

Do not confuse the two: `/generate-pipeline` (a meta-agent) writes `agents/fraud_detector.py` (a
pipeline agent); they are different things with similar names.

### Layer 1 — meta-agents (`.claude/commands/`)

| Command | Role | What it does |
|---|---|---|
| `/write-spec` | Agent 1 — Specification | Produces `specification.md` and `agents.md` (this file) from the course template. |
| `/generate-pipeline` | Agent 2 — Code generation | Implements `pipeline/`, `agents/*.py`, and `integrator.py` from `specification.md`; required to query the context7 MCP server for FastMCP and Python `decimal` docs and log the queries to `research-notes.md`. |
| `/generate-tests` | Agent 3 — Unit tests | Writes the `tests/` suite and iterates until coverage is >= 90% (hard floor 80%, enforced by the coverage-gate hook). |
| `/generate-docs` | Agent 4 — Documentation | Writes `README.md` (with author attribution) and `HOWTORUN.md`. |
| `/run-pipeline` | Operational skill | Runs the pipeline end-to-end (`uv run python integrator.py`) and summarizes `shared/results/`. |
| `/validate-transactions` | Operational skill | Runs the validator's `--dry-run` mode and reports a valid/invalid table without touching `shared/`. |

### Layer 2 — pipeline agents (`agents/*.py`, `integrator.py`)

Three cooperating agents, each a pure `process_message(message: dict) -> dict`, plus an
orchestrator:

- **`agents/transaction_validator.py`** (`AGENT_NAME = "transaction_validator"`) — checks required
  fields, a positive `Decimal` amount, an ISO 4217 currency, and an ISO 8601 timestamp. Rejects
  straight to `results` with a `reason`; on success forwards to `fraud_detector` with
  `status: "validated"`.
- **`agents/fraud_detector.py`** (`AGENT_NAME = "fraud_detector"`) — computes an additive `Decimal`
  risk score (high value, unusual timing, cross-border, near-threshold) and routes by band: `>= 0.7`
  rejects to `results` as `fraud_review`; `0.3` to `< 0.7` flags (`fraud_flag: true`) and forwards;
  `< 0.3` forwards clean. Target on success: `settlement_processor`.
- **`agents/settlement_processor.py`** (`AGENT_NAME = "settlement_processor"`) — computes a 0.1%
  settlement fee with `Decimal`/`ROUND_HALF_UP`, stamps `status: "settled"` or
  `"settled_with_flag"`, and always routes to `results` (it is the last stage).
- **`integrator.py`** — seeds `shared/input/` from `sample-transactions.json`, runs the three
  agents above in order via the file-relay protocol, and writes
  `shared/results/pipeline-summary.json`.

## Message envelope (6 fields)

Every inter-agent message (`pipeline/message.py::create_envelope`) is a JSON object with exactly
these fields:

```json
{
  "message_id": "uuid4-string",
  "timestamp": "2026-03-16T10:00:00Z",
  "source_agent": "transaction_validator",
  "target_agent": "fraud_detector",
  "message_type": "transaction",
  "data": { "transaction_id": "TXN001", "...": "..." }
}
```

`pipeline/message.py::validate_envelope` checks all six fields are present and that `data` is a
dict; `pipeline/message.py::utc_now_iso` is the single source of truth for timestamp formatting.

## File protocol

Agents never call each other directly or share memory. They communicate exclusively by dropping
JSON envelope files into shared stage directories under `shared/`
(`pipeline/protocol.py`):

```
shared/input/       <- integrator seeds one message per transaction here
shared/processing/  <- an agent moves a message here while it works on it (claims it)
shared/output/      <- an agent writes its result here for the next agent to pick up
shared/results/     <- terminal outcomes land here (rejected, fraud_review, error, settled, settled_with_flag)
```

`integrator.py::TERMINAL_STATUSES = {"rejected", "fraud_review", "error", "settled",
"settled_with_flag"}` decides `results/` vs `output/` routing for every processed message. A file
that fails to parse or fails envelope validation is turned into a `status: "error"` result rather
than crashing the run — one bad file never blocks the rest of the pipeline. `shared/` is gitignored
and fully recreated (cleared, not appended to) at the start of every run by
`pipeline/protocol.py::ensure_shared_dirs`.

## Non-negotiable conventions

- **`decimal.Decimal`, never `float`**, for every monetary value — amounts are parsed from JSON
  string values (e.g. `"25000.00"`), and every downstream computation (risk thresholds, fee
  calculation, settlement aggregation) stays in `Decimal`.
- **ISO 4217 currency codes** — validated against the allowlist in
  `agents/transaction_validator.py::ISO_4217 = {"USD", "EUR", "GBP", "JPY", "CHF", "CAD", "AUD"}`.
  Anything else is rejected.
- **ISO 8601 timestamps everywhere** — `pipeline/message.py::utc_now_iso()` is the only place that
  formats "now"; incoming transaction timestamps are parsed via `datetime.fromisoformat` after
  normalizing a trailing `"Z"` to `"+00:00"`.
- **PII masking** — account numbers are never logged in plaintext.
  `pipeline/audit.py::mask_account` turns `"ACC-1001"` into `"ACC-****01"`. The audit log schema
  (`pipeline/audit.py::log_event`) has exactly four fields — timestamp, agent, transaction_id,
  outcome — so there is no field for account numbers, names, or free-text descriptions to leak
  into.
- **TDD** — write the failing test first, then the implementation. Every module in `agents/`,
  `pipeline/`, `mcp/`, and `integrator.py` has a corresponding test module in `tests/`. Tests use
  `tmp_path` for every filesystem operation; no test reads or writes the project's real `shared/`.
- **Pure functions** — every agent's `process_message(message: dict) -> dict` never mutates its
  input's `data` dict; it returns a new dict.

## Running things (`uv` commands)

- Install dependencies: `uv sync`
- Run the full pipeline: `uv run python integrator.py`
- Validate without processing: `uv run python agents/transaction_validator.py --dry-run` (or
  `--sample PATH` for a different file)
- Run the test suite with coverage: `uv run pytest --cov=agents --cov=pipeline --cov=mcp --cov=integrator`
- Run the custom MCP server directly: `uv run python mcp/server.py`

## Coverage gate

A `PreToolUse` hook (`.claude/settings.json`, matcher `Bash`) runs
`.claude/hooks/coverage-gate.sh` before every Bash command. The script inspects the command
(shell-aware tokenization, not a substring match); if — and only if — it is a `git push` invocation,
it runs `uv run pytest --cov=agents --cov=pipeline --cov=mcp --cov=integrator --cov-fail-under=$COVERAGE_GATE_MIN -q`
(`COVERAGE_GATE_MIN` defaults to **80**) and exits 2 (blocking the push, with the last 20 lines of
pytest output on stderr) if coverage is below that floor. Non-push commands pass through instantly.
**80% is the hard gate; the project targets >= 90%** (current measured coverage is 97% across
`agents/`, `pipeline/`, `mcp/`, and `integrator.py`). Any agent adding code must keep coverage above
the gate, ideally at or above the 90% target, before attempting a push.

## MCP servers (`mcp.json` / `.mcp.json`)

Two MCP servers are configured:

- **`context7`** (`npx -y @upstash/context7-mcp@latest`) — used during code generation
  (`/generate-pipeline`) to look up framework documentation (FastMCP, Python `decimal`). Queries and
  their applied insights are logged in `research-notes.md`.
- **`pipeline-status`** (`uv run python mcp/server.py`) — a custom FastMCP server
  (`mcp/server.py`) exposing:
  - Tool `get_transaction_status(transaction_id: str) -> dict` — looks up one transaction's result
    from `shared/results/`, returning `{"transaction_id", "status", ...}` or
    `{"status": "not_found"}` if no result file exists yet.
  - Tool `list_pipeline_results() -> dict` — aggregates every result file into
    `{"count": N, "results": [...]}`.
  - Resource `pipeline://summary` — returns `shared/results/pipeline-summary.json` as raw text (or a
    friendly fallback message if no run has happened yet).

**Known constraint**: after adding or changing `mcp.json`, restart the Claude Code session before
the servers are callable — `claude mcp list` reporting "Connected" is not sufficient on its own.
