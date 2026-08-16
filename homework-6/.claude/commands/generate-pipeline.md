---
description: "Agent 2 (Code-generation meta-agent) - implement the banking pipeline from specification.md, using context7 for FastMCP and Python decimal docs, logging queries to research-notes.md."
---

You are Agent 2, the Code-generation meta-agent for the Homework 6 banking pipeline. Implement the
pipeline described in `specification.md` (produced by `/write-spec`). If `specification.md` does not
exist yet, stop and tell the user to run `/write-spec` first.

## What to build

Implement these components in the repo root
(`/Users/gorishnyi/development/education/set/gen-ai-software-engineering/homework-6/`):

1. **`pipeline/` shared package** — internals every agent uses:
   - `pipeline/message.py` — the standard JSON message envelope: `message_id` (uuid4), ISO 8601
     `timestamp`, `source_agent`, `target_agent`, `message_type: "transaction"`, and a `data` payload
     carrying the transaction fields plus `status`/`reason`/`risk_score` as agents add them.
   - `pipeline/protocol.py` — the file-based communication protocol: create/clear the
     `shared/input/`, `shared/processing/`, `shared/output/`, `shared/results/` directories; read and
     write JSON message files; move a message file between stage directories while an agent works on
     it.
   - `pipeline/audit.py` — the audit logger: every agent action is recorded with an ISO 8601
     timestamp, agent name, transaction id, and outcome; account numbers are masked
     (e.g. `ACC-****01`) before anything is logged — never log plaintext account numbers or names.

2. **Three pipeline agents** in `agents/`, each exposing a pure `process_message(message: dict) -> dict`:
   - `agents/transaction_validator.py` — validates required fields, positive `decimal.Decimal`
     amount, ISO 4217 currency, ISO 8601 timestamp; forwards valid transactions, routes invalid ones
     straight to `shared/results/` with a rejection reason. Also give it a `--dry-run` CLI entry
     point (`main()` behind `if __name__ == "__main__":`) that reads `sample-transactions.json` and
     prints a validation table without writing any files, so `agents/transaction_validator.py
     --dry-run` works standalone.
   - `agents/fraud_detector.py` — computes the additive risk score and routes to fraud rejection,
     flagged-continue, or clean per the bands in `specification.md`.
   - `agents/settlement_processor.py` — computes the settlement fee with `Decimal` and
     `ROUND_HALF_UP`, writes the final result to `shared/results/`.

3. **`integrator.py`** at the repo root — the orchestrator: recreates `shared/` subdirectories,
   seeds `shared/input/` from `sample-transactions.json`, runs the three agents in order via the
   file protocol, and writes `shared/results/pipeline-summary.json` (counts by status, rejection
   reasons, settled volume per currency). Confirm it runs cleanly end-to-end with
   `uv run python integrator.py`.

Use the file protocol and message envelope exactly as specified — do not invent an alternate
in-memory or network transport between agents; the whole point of this pipeline is the
`shared/input -> processing -> output -> results` file relay.

## Required: use context7 while coding

You MUST use the context7 MCP server while implementing this pipeline — do not skip this step or
rely purely on prior knowledge. Specifically:

1. Call context7's `resolve-library-id` then `get-library-docs` to look up **FastMCP** documentation
   before or while touching anything MCP-related (`mcp/server.py`, `mcp.json`).
2. Call context7's `resolve-library-id` then `get-library-docs` to look up **Python's `decimal`
   module** documentation before or while implementing the money-handling code (fraud detector's
   thresholds, settlement processor's fee rounding).

After each context7 query, append an entry to `research-notes.md` at the repo root (create the file
if it does not exist) in this format:

```markdown
## Query N: <short description>
- Search: <what you searched for>
- context7 library ID: <the library ID context7 returned>
- Applied: <the specific insight or code pattern you used as a result>
```

You must end up with at least 2 documented queries (one for FastMCP, one for `decimal`) in
`research-notes.md` — this is a graded requirement, not optional. If a context7 query fails or
returns nothing useful, still record the attempt and what you fell back to.

## Verification before finishing

- Run `uv run python integrator.py` and confirm all 8 transactions in `sample-transactions.json`
  produce a result file in `shared/results/`, plus `shared/results/pipeline-summary.json`.
- Confirm `uv run python agents/transaction_validator.py --dry-run` runs standalone and prints a
  validation table.
- Confirm `research-notes.md` has at least 2 context7 query entries with library ID and applied
  insight filled in — not placeholders.

Report what was created/changed, the pipeline run outcome, and the research-notes.md entries you
added.
