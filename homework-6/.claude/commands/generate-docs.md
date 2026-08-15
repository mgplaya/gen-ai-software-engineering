---
description: "Agent 4 (Documentation meta-agent) - generate README.md and HOWTORUN.md for the banking pipeline, with author attribution, architecture diagram, and tech-stack table."
---

You are Agent 4, the Documentation meta-agent for the Homework 6 banking pipeline. Generate
`README.md` and `HOWTORUN.md` at the repo root
(`/Users/gorishnyi/development/education/set/gen-ai-software-engineering/homework-6/`), describing
the system as it actually exists — read `specification.md`, `agents/`, `pipeline/`, `integrator.py`,
`mcp/server.py`, and `.claude/commands/` before writing so the docs match the real code, not a
generic template.

## `README.md` must contain

1. The line **"Created by Mykhailo Gorishnyi"** (author attribution) near the top, e.g. directly
   under the title.
2. **1-2 paragraphs** describing what the system does: a multi-agent banking transaction pipeline
   that validates, fraud-scores, and settles transactions from `sample-transactions.json`, passing
   JSON messages through `shared/` stage directories, and exposes results via a custom FastMCP
   server.
3. **One bullet per agent** — seven total:
   - Three pipeline agents: Transaction Validator (`agents/transaction_validator.py`), Fraud
     Detector (`agents/fraud_detector.py`), Settlement Processor (`agents/settlement_processor.py`) —
     one bullet each describing what it checks/computes/decides.
   - Four meta-agents: `/write-spec` (Agent 1, specification), `/generate-pipeline` (Agent 2, code
     generation, uses context7), `/generate-tests` (Agent 3, unit tests, coverage gate), `/generate-docs`
     (Agent 4, this command) — one bullet each.
4. An **ASCII architecture diagram** showing the flow through the `shared/` stages, for example:

   ```
   sample-transactions.json
             |
             v
       integrator.py  (seeds one message per transaction)
             |
             v
       shared/input/ --------> transaction_validator --------> shared/output/
                                       |                              |
                                  (invalid: reject)                   v
                                       |                       shared/input/
                                       v                              |
                                 shared/results/                      v
                                                              fraud_detector
                                                                      |
                                                          (rejected: fraud_review)
                                                                      |
                                                                      v
                                                              shared/output/
                                                                      |
                                                                      v
                                                          settlement_processor
                                                                      |
                                                                      v
                                                              shared/results/
                                                                      |
                                                                      v
                                                    pipeline-summary.json
   ```

   Adjust the diagram to match the actual file-move sequence in `pipeline/protocol.py` and
   `integrator.py` if it differs from this sketch.
5. A **tech-stack table** covering: language/runtime (Python 3.12+, `uv`), pipeline package
   (`fastmcp`), test tooling (`pytest`, `pytest-cov`), MCP servers (context7, custom `pipeline-status`
   FastMCP server in `mcp/server.py`), and the Claude Code automation layer (slash commands in
   `.claude/commands/`, coverage-gate hook in `.claude/hooks/coverage-gate.sh`).

## `HOWTORUN.md` must contain

Numbered steps from a clean checkout to a full demo, including at minimum:

1. Prerequisites: `uv` installed, Python 3.12+.
2. Install dependencies: `uv sync` (run from
   `/Users/gorishnyi/development/education/set/gen-ai-software-engineering/homework-6/`).
3. Run the full pipeline: `uv run python integrator.py`.
4. Inspect results: list `shared/results/` and view `shared/results/pipeline-summary.json`.
5. Run the validator dry-run: `uv run python agents/transaction_validator.py --dry-run`.
6. Run the test suite with coverage: `uv run pytest --cov=agents --cov=pipeline --cov=mcp --cov=integrator`.
7. Use the Claude Code slash commands: `/run-pipeline` for an end-to-end run with a results summary,
   `/validate-transactions` for a dry-run validation table.
8. (Optional) Restart the Claude Code session after any `mcp.json` change, then confirm the MCP
   servers with `claude mcp list`, and query the `pipeline-status` server's `get_transaction_status`
   tool or `pipeline://summary` resource.

## Verification before finishing

- Run `grep -n "Mykhailo Gorishnyi" README.md` and confirm it matches.
- Confirm README.md has exactly one bullet per agent (7 bullets total across the two groups), an
  ASCII diagram, and a tech-stack table.
- Confirm HOWTORUN.md steps are numbered and every command referenced (`uv sync`,
  `uv run python integrator.py`, `uv run python agents/transaction_validator.py --dry-run`,
  `uv run pytest --cov=agents --cov=pipeline --cov=mcp --cov=integrator`) is copy-pasteable as-is.

Report what was written to each file and the verification grep output.
