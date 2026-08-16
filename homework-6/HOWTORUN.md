# How to Run

Numbered steps from a clean checkout of `homework-6/` to a full demo. Every command below was run
against this repository and the "Expected" line shows the actual output produced (trimmed where
noted), not a hypothetical.

## 1. Prerequisites

- **[`uv`](https://docs.astral.sh/uv/)** installed (manages the Python 3.12+ environment and all
  dependencies — no manual `venv`/`pip` needed).
- **Node.js + `npx`** available on `PATH` — required only to run the `context7` MCP server
  (`npx -y @upstash/context7-mcp@latest`). Verified in this environment with `node v26.3.0` /
  `npx 11.16.0`.
- **Claude Code** — optional, only needed for the MCP servers (step 7) and slash commands (step 8).
  Everything else in this guide is plain `uv run` commands runnable from any shell.

All commands below are run from the repo root:
`/Users/gorishnyi/development/education/set/gen-ai-software-engineering/homework-6/`.

## 2. Install dependencies

```
uv sync
```

**Expected:** `uv` resolves and installs the project's dependencies (`fastmcp`) and dev dependencies
(`pytest`, `pytest-cov`) into `.venv`. Actual output on a synced environment:

```
Resolved 77 packages in 4ms
Checked 71 packages in 13ms
```

(On a genuinely clean checkout with no `.venv` yet, `uv sync` additionally prints lines like
`Creating virtual environment` and `Installed N packages`.)

## 3. Run the pipeline end-to-end

```
uv run python integrator.py
```

**Expected:** a per-transaction table for all 8 transactions in `sample-transactions.json`, then
summary counts. Actual output:

```
TRANSACTION ID STATUS              DETAIL
TXN001         settled             fee=1.50, risk=0
TXN002         settled_with_flag   fee=25.00, risk=0.4
TXN003         settled             fee=10.00, risk=0.2
TXN004         settled_with_flag   fee=0.50, risk=0.3
TXN005         settled_with_flag   fee=75.00, risk=0.4
TXN006         rejected            unsupported currency: 'XYZ'
TXN007         rejected            amount must be greater than zero
TXN008         settled             fee=3.20, risk=0

Transactions in: 8  Results: 8
  rejected: 2
  settled: 3
  settled_with_flag: 3
```

This also writes one result file per transaction plus an aggregate summary to `shared/results/`
(`shared/` is gitignored and fully recreated on every run):

```
ls shared/results/
```

```
TXN001.json  TXN002.json  TXN003.json  TXN004.json  TXN005.json  TXN006.json  TXN007.json  TXN008.json  pipeline-summary.json
```

`shared/results/pipeline-summary.json` (actual content from the run above):

```json
{
  "generated_at": "2026-08-15T00:35:46Z",
  "transactions_in": 8,
  "results_total": 8,
  "by_status": {
    "settled": 3,
    "settled_with_flag": 3,
    "rejected": 2
  },
  "rejection_reasons": {
    "TXN006": "unsupported currency: 'XYZ'",
    "TXN007": "amount must be greater than zero"
  },
  "settled_volume_by_currency": {
    "USD": "114585.29",
    "EUR": "499.50"
  }
}
```

## 4. Dry-run validation (no files written)

```
uv run python agents/transaction_validator.py --dry-run
```

**Expected:** the same 6 valid / 2 invalid split as the full run, but only a validation table —
nothing is written to `shared/`. Actual output:

```
TRANSACTION ID      STATUS    REASONS
TXN001              VALID
TXN002              VALID
TXN003              VALID
TXN004              VALID
TXN005              VALID
TXN006              INVALID   unsupported currency: 'XYZ'
TXN007              INVALID   amount must be greater than zero
TXN008              VALID
Total: 8  Valid: 6  Invalid: 2
```

## 5. Run tests with coverage

```
uv run pytest --cov=agents --cov=pipeline --cov=mcp --cov=integrator
```

**Expected:** all tests pass and overall coverage clears the 80% gate (target 90%). Actual output:

```
collected 101 items

tests/test_audit.py .........                                            [  8%]
tests/test_fraud_detector.py .......................                     [ 31%]
tests/test_integrator.py ...........                                     [ 42%]
tests/test_mcp_server.py .........                                       [ 51%]
tests/test_message.py ...........                                       [ 62%]
tests/test_protocol.py ...........                                       [ 73%]
tests/test_settlement_processor.py ..........                           [ 83%]
tests/test_transaction_validator.py .................                   [100%]

Name                              Stmts   Miss  Cover
-----------------------------------------------------
agents/__init__.py                    0      0   100%
agents/fraud_detector.py             68      4    94%
agents/settlement_processor.py       22      1    95%
agents/transaction_validator.py      81      2    98%
integrator.py                       127      2    98%
mcp/server.py                        44      4    91%
pipeline/__init__.py                  0      0   100%
pipeline/audit.py                    23      0   100%
pipeline/message.py                  18      0   100%
pipeline/protocol.py                 23      0   100%
-----------------------------------------------------
TOTAL                               406     13    97%
============================= 101 passed in 0.70s ==============================
```

## 6. Coverage gate demo (`.claude/hooks/coverage-gate.sh`)

The hook is wired as a `PreToolUse` hook on every `Bash` tool call (`.claude/settings.json`). It
only acts on `git push` commands; everything else passes through instantly. Called directly here
outside Claude Code, feeding it the same JSON payload the hook receives from the harness:

**Pass at the default 80% gate:**

```
echo '{"tool_input": {"command": "git push origin main"}}' | .claude/hooks/coverage-gate.sh
```

Actual output (exit code 0):

```
coverage gate passed (>= 80%) — push allowed
```

**Blocked with an artificially high gate:**

```
echo '{"tool_input": {"command": "git push origin main"}}' | COVERAGE_GATE_MIN=99 .claude/hooks/coverage-gate.sh
```

Actual output (exit code 2), last 20 lines of the `pytest --cov` run on stderr:

```
BLOCKED: test coverage below 99% — git push denied.
---- last 20 lines of pytest --cov output ----
...
TOTAL                               406     13    97%
FAIL Required test coverage of 99% not reached. Total coverage: 96.80%
101 passed in 0.53s
```

(`echo $?` after the second command reports `2`, confirming the push is blocked.)

## 7. MCP servers (`mcp.json` / `.mcp.json`)

Both files configure the same two servers:

```json
{
  "mcpServers": {
    "context7": { "command": "npx", "args": ["-y", "@upstash/context7-mcp@latest"] },
    "pipeline-status": { "command": "uv", "args": ["run", "python", "mcp/server.py"] }
  }
}
```

**Known constraint:** after adding or changing `mcp.json`, you must **restart the Claude Code
session** (launched from this `homework-6/` directory) before the servers are callable —
`claude mcp list` reporting "Connected" is not sufficient on its own; newly added servers may also
need a one-time approval on first connect (`claude mcp list` shows this as "Pending approval — run
`claude` to approve").

Once connected, example interactions:

- **`get_transaction_status`** tool, e.g. `get_transaction_status(transaction_id="TXN001")` →
  returns the flattened result for TXN001 from `shared/results/TXN001.json` (after step 3 has run,
  this is `{"transaction_id": "TXN001", "status": "settled", "settlement_fee": "1.50", ...}`;
  before any run, or for an unknown id, it returns `{"transaction_id": "...", "status": "not_found"}`).
- **`list_pipeline_results`** tool → returns `{"count": 8, "results": [...]}` aggregating every
  file in `shared/results/` (skipping `pipeline-summary.json`).
- **`pipeline://summary`** resource → returns the raw text of
  `shared/results/pipeline-summary.json` (or a friendly "No pipeline run yet..." message if step 3
  hasn't been run yet).

These were not re-invoked live in this pass (that requires a Claude Code session restart from
`homework-6/`), but `mcp/server.py`'s underlying functions (`load_result`, `summarize`,
`summary_text`) are covered directly by `tests/test_mcp_server.py` and exercised against the same
`shared/results/` produced in step 3 above.

## 8. Slash commands (when Claude Code runs from `homework-6/`)

Six commands are defined in `.claude/commands/`:

| Command | Role |
|---|---|
| `/write-spec` | Agent 1 — generates `specification.md` and `agents.md` from the course template. |
| `/generate-pipeline` | Agent 2 — implements `pipeline/`, `agents/*.py`, `integrator.py` from `specification.md`, using context7 for FastMCP/`decimal` lookups. |
| `/generate-tests` | Agent 3 — writes the `tests/` suite and iterates until coverage clears 90% (hard floor 80%). |
| `/generate-docs` | Agent 4 — generates `README.md` and `HOWTORUN.md` (this file). |
| `/run-pipeline` | Runs `uv run python integrator.py` end-to-end and summarizes `shared/results/`, including any rejected/fraud_review/error transactions and why. |
| `/validate-transactions` | Runs the validator's `--dry-run` mode and reports a valid/invalid table without touching `shared/`. |
