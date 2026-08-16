# Homework 6 — AI-Powered Multi-Agent Banking Pipeline: Design

**Date:** 2026-08-15
**Author:** Mykhailo Gorishnyi
**Status:** Approved

## Goal

Complete the Homework 6 capstone: four meta-agents (Claude Code slash commands) that generate a multi-agent banking transaction processing pipeline, plus operational skills, a coverage-gate hook, context7 MCP usage, and a custom FastMCP server. The deliverable is both the meta-agents and the working pipeline they produce.

## Decisions made

| Decision | Choice |
|---|---|
| Stack | Python + uv + pytest (matches homework-5's FastMCP/uv setup) |
| Third pipeline agent | Settlement Processor |
| Coverage gate | Claude Code `PreToolUse` hook in `.claude/settings.json`, blocks `git push` below 80% |
| Meta-agent realization | Four slash commands in `.claude/commands/` |
| Pipeline execution model | Sequential file-relay: integrator runs agents in order; JSON message files flow through `shared/` directories |

## Architecture & directory layout

Everything lives in `homework-6/`, self-contained. Claude Code must be launched from this directory so its `.claude/` is picked up.

```
homework-6/
├── .claude/
│   ├── settings.json            # coverage-gate PreToolUse hook on git push
│   └── commands/
│       ├── write-spec.md        # Agent 1 (meta): generates specification.md from template
│       ├── generate-pipeline.md # Agent 2 (meta): builds pipeline code, uses context7
│       ├── generate-tests.md    # Agent 3 (meta): writes tests to ≥90% coverage
│       ├── generate-docs.md     # Agent 4 (meta): README/HOWTORUN with author name
│       ├── run-pipeline.md      # Task 3 skill: end-to-end run + results summary
│       └── validate-transactions.md  # Task 3 skill: dry-run validation table
├── mcp.json                     # context7 + pipeline-status servers
├── mcp/server.py                # custom FastMCP server
├── integrator.py                # orchestrator
├── agents/
│   ├── transaction_validator.py
│   ├── fraud_detector.py
│   └── settlement_processor.py
├── pipeline/                    # shared internals: message model, file protocol, audit log
├── shared/                      # runtime dirs (gitignored): input/ processing/ output/ results/
├── tests/                       # pytest, tmp_path-isolated
├── specification.md             # produced by /write-spec
├── agents.md                    # project agent context, extended by /write-spec
├── research-notes.md            # 2+ documented context7 queries
├── README.md, HOWTORUN.md       # produced by /generate-docs
├── docs/screenshots/            # 5 required screenshots
└── pyproject.toml, uv.lock      # uv project; deps: fastmcp; dev: pytest, pytest-cov
```

Two layers, deliberately distinct:

- **Meta-agents** — the six slash commands (four generator agents + two operational skills).
- **Pipeline agents** — the three Python modules the meta-agents produce.

The `pipeline/` package holds what all agents share — the message dataclass/schema, the input→processing→output file-move protocol, and the PII-safe audit logger — so each agent module contains only business logic in a pure `process_message(message: dict) -> dict`.

## Data flow & agent logic

The integrator loads `sample-transactions.json`, wraps each record in the standard message envelope (uuid4 `message_id`, ISO 8601 timestamp, `source_agent`/`target_agent`, `message_type: "transaction"`), and drops one JSON file per transaction into `shared/input/`. It then runs the three agents in order. Each agent picks up every message addressed to it, moves the file to `shared/processing/` while working, and writes its result to `shared/output/` for the next agent. Rejected transactions short-circuit straight to `shared/results/` with a `reason` field.

All amounts are handled as `decimal.Decimal`, parsed from the JSON string values — never float.

### Transaction Validator
- Required fields present; amount is a parseable positive decimal (rejects TXN007's `-100.00`); currency is ISO 4217 from an allowlist (rejects TXN006's `XYZ`); timestamp parses as ISO 8601; accounts non-empty.
- Valid → `status: "validated"`, forwarded to fraud detector. Invalid → rejected result with reason.

### Fraud Detector
Additive risk score:

| Signal | Score | Sample hit |
|---|---|---|
| Amount > $10,000 | +0.4 | TXN002, TXN005 |
| Unusual timing 00:00–05:00 UTC | +0.3 | TXN004 (02:47) |
| Cross-border (metadata country ≠ currency home country) | +0.2 | — |
| Near-threshold amount $9,000–$10,000 | +0.2 | TXN003 (9999.99) |

Bands (inclusive lower bounds): score ≥ 0.7 → rejected as `fraud_review`; 0.3 ≤ score < 0.7 → flagged but continues; score < 0.3 → clean. The risk score is always attached to the message. The cross-border check uses a currency→home-country map maintained alongside the ISO 4217 allowlist (USD→US, EUR→EU member set, GBP→GB, JPY→JP).

### Settlement Processor
- Computes a 0.1% settlement fee with `Decimal` and `ROUND_HALF_UP`, quantized to 2 decimal places.
- Stamps `status: "settled"` (or `settled_with_flag` for flagged transactions) and writes the final outcome to `shared/results/`.

### Summary & audit
After the run, the integrator writes `shared/results/pipeline-summary.json` (counts by status, rejection reasons, total settled volume per currency) and prints a human-readable summary table. Every agent action goes through the audit logger: ISO 8601 timestamp, agent name, transaction ID, outcome — account numbers masked (`ACC-****01`), no names or descriptions logged.

### Expected outcome for the 8 sample transactions
- TXN001, TXN008: clean → settled.
- TXN002 ($25k), TXN005 ($75k): risk 0.4 → flagged → `settled_with_flag`.
- TXN003 ($9,999.99): near-threshold 0.2 → clean → settled.
- TXN004 (02:47 UTC, EUR from DE): timing 0.3; not cross-border (DE is in the EUR home set) → flagged → `settled_with_flag`.
- TXN006 (currency `XYZ`): rejected by validator.
- TXN007 (negative amount): rejected by validator.

All 8 transactions appear in `shared/results/`.

## Error handling

- Malformed message files (unparseable JSON, missing envelope fields) move to `shared/results/` as `status: "error"` with the parse-failure reason. The pipeline never crashes on bad input; one bad transaction never blocks the rest.
- The integrator exits non-zero only if the pipeline itself fails (e.g., `sample-transactions.json` missing).
- The integrator idempotently recreates/clears `shared/` subdirectories at startup so reruns are clean.
- Agents validate their input envelope even mid-pipeline, so a corrupted hand-off surfaces as an error result rather than a stack trace.

## Meta-agents, skills, hook, MCP

### Four meta-agent slash commands
- **`/write-spec`** (Agent 1): generates `specification.md` following the homework-3 template structure — High-Level Objective, Mid-Level Objectives, Implementation Notes, Context, Low-Level Tasks in the exact `Task/Prompt/File to CREATE/Function to CREATE/Details` format, one entry per pipeline agent. Also updates `agents.md` with project context.
- **`/generate-pipeline`** (Agent 2): implements the pipeline from `specification.md`; explicitly directs Claude to query context7 for FastMCP and Python `decimal` documentation and to append each query (search, library ID, applied insight) to `research-notes.md`.
- **`/generate-tests`** (Agent 3): writes pytest tests for each agent plus the integration path, runs `pytest --cov`, iterates until coverage ≥ 90%.
- **`/generate-docs`** (Agent 4): generates `README.md` (with **"Created by Mykhailo Gorishnyi"**, system description, per-agent bullets, ASCII pipeline diagram, tech-stack table) and `HOWTORUN.md` (numbered setup-to-demo steps).

### Task 3 operational skills
- **`/run-pipeline`**: check sample file exists → clear `shared/` → `uv run python integrator.py` → summarize results → list rejections with reasons.
- **`/validate-transactions`**: runs `uv run python agents/transaction_validator.py --dry-run` (the validator module supports this via a small `__main__` block) and prints a total/valid/invalid table with rejection reasons.

### Coverage gate hook
In `homework-6/.claude/settings.json`: a `PreToolUse` hook matching the `Bash` tool. The hook script inspects the command; if it contains `git push`, it runs:

```
uv run pytest --cov=agents --cov=pipeline --cov=mcp --cov-fail-under=80 -q
```

and exits with code 2 (block; stderr fed back to Claude) when coverage is below 80%. Non-push commands pass through instantly.

### MCP
`mcp.json` configures both servers:
- **context7**: `npx -y @upstash/context7-mcp@latest`
- **pipeline-status**: `uv run python mcp/server.py`

The FastMCP server follows the homework-5 pattern:
- Tool `get_transaction_status(transaction_id: str)` — reads that transaction's result file from `shared/results/`.
- Tool `list_pipeline_results()` — aggregates all result files into a summary.
- Resource `pipeline://summary` — returns `pipeline-summary.json` as text.

Known constraint (from prior experience): after adding/changing `mcp.json`, the Claude Code session must restart before the servers are callable, even if `claude mcp list` shows Connected.

## Testing

- **Unit tests per agent**: `process_message` as a pure function — valid/invalid/edge inputs: negative amount, bad currency, threshold boundaries at exactly $10,000 and 05:00 UTC, fee-rounding cases.
- **Shared internals**: message model, file protocol moves, audit-log masking.
- **Integration test**: runs the full integrator against a copy of `sample-transactions.json` in `tmp_path`. All `shared/` paths are parameterized through a base-dir argument — never hardcoded — so tests never touch the real `shared/`.
- **MCP server tests**: call the tool functions directly against a `tmp_path` results dir.
- **Targets**: ≥ 90% coverage; hard gate at 80% via the hook.

## Deliverable workflow (grading path)

1. Run the meta-agent commands in order: `/write-spec` → `/generate-pipeline` → `/generate-tests` → `/generate-docs`.
2. Capture the 5 required screenshots along the way into `docs/screenshots/`:
   - `pipeline-run.png` — full terminal output of `uv run python integrator.py`
   - `test-coverage.png` — coverage report ≥ 80% (ideally ≥ 90%)
   - `skill-run-pipeline.png` — `/run-pipeline` executing
   - `hook-trigger.png` — coverage gate firing (attempt a push with coverage artificially lowered, or show the gate output)
   - `mcp-interaction.png` — a context7 query result plus a `get_transaction_status` call
3. Open a PR from a `homework-6-submission` branch with all screenshots embedded in the description (spec produced, pipeline run, tests/coverage, skill/hook in action, MCP usage, README with author name).

## Out of scope

- Polling/daemon-style concurrent agents (rejected in favor of deterministic sequential relay).
- Real sanctions/AML data, real currency conversion, persistence beyond the `shared/` filesystem.
- Git-native pre-push hooks (the Claude Code settings.json hook is the deliverable).
