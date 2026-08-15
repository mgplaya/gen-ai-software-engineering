---
description: "Agent 1 (Specification meta-agent) - generate specification.md for the banking pipeline from the course template and update agents.md with project context."
---

You are Agent 1, the Specification meta-agent for the Homework 6 banking pipeline. Your job is to
produce a complete `specification.md` at the repo root (`/Users/gorishnyi/development/education/set/gen-ai-software-engineering/homework-6/specification.md`)
and to extend `agents.md` (same directory) with project-specific context. Do not write any pipeline
code in this command — that is Agent 2's job (`/generate-pipeline`).

Before writing, read what already exists so the spec describes the real system rather than a
placeholder:
- `sample-transactions.json` — the 8 sample transactions (TXN001-TXN008) that drive the pipeline.
- `agents/transaction_validator.py`, `agents/fraud_detector.py`, `agents/settlement_processor.py` —
  the three pipeline agents, if already implemented.
- `pipeline/message.py`, `pipeline/protocol.py`, `pipeline/audit.py` — shared envelope, file-protocol,
  and audit-logging helpers.
- `integrator.py` — the orchestrator.
- `mcp/server.py` and `mcp.json` — the custom FastMCP server and MCP server configuration.
- `docs/superpowers/specs/2026-08-15-homework-6-banking-pipeline-design.md` if present — the design
  decisions already made for this project (stack, third agent choice, fraud-scoring bands, etc.).

## 1. Write `specification.md`

Follow the course specification template exactly (see `../homework-3/specification-TEMPLATE-example.md`
for the template shape). Produce these five sections, in this order:

### (1) High-Level Objective
One sentence describing what the pipeline does, e.g. "Process banking transactions end-to-end
through validation, fraud scoring, and settlement, writing auditable JSON results for every
transaction in `shared/results/`."

### (2) Mid-Level Objectives (4-5 items)
Concrete, testable requirements for this specific pipeline. Include at minimum:
- Transactions with a missing required field, non-positive amount, non-ISO-4217 currency, or
  unparseable ISO 8601 timestamp are rejected by the validator with a `reason` field.
- Transactions with a risk score >= 0.7 (amount > $10,000, unusual timing 00:00-05:00 UTC,
  cross-border, or near-threshold $9,000-$10,000 signals) are rejected as `fraud_review`; scores
  with 0.3 <= score < 0.7 are flagged but continue to settlement.
- Every settled transaction has a 0.1% settlement fee computed with `decimal.Decimal` and
  `ROUND_HALF_UP`, quantized to 2 decimal places.
- All agent operations are logged to the audit trail with an ISO 8601 timestamp, agent name,
  transaction id, and outcome — account numbers masked, never plaintext.
- Every transaction in `sample-transactions.json` produces exactly one result file in
  `shared/results/`, and the integrator writes a `pipeline-summary.json` aggregating counts by
  status, rejection reasons, and settled volume per currency.

### (3) Implementation Notes
State explicitly:
- Monetary values MUST use `decimal.Decimal` parsed from JSON string amounts — never `float`.
- Currency codes MUST be validated against an ISO 4217 allowlist (USD, EUR, GBP, JPY, etc.).
- Every agent action MUST go through the audit logger (`pipeline/audit.py`) recording ISO 8601
  timestamp, agent name, transaction id, and outcome.
- Account numbers and other PII MUST be masked in all log output (e.g. `ACC-****01`) — never log
  plaintext account numbers or names. Result files retain full transaction data for settlement;
  `shared/` is gitignored.

### (4) Context
- **Beginning context**: `sample-transactions.json` (raw transaction records), empty `shared/`
  subdirectories (`input/`, `processing/`, `output/`, `results/`).
- **Ending context**: one result JSON per transaction in `shared/results/`, a
  `shared/results/pipeline-summary.json` report, and test coverage >= 90% as measured by
  `uv run pytest --cov=agents --cov=pipeline --cov=mcp --cov=integrator`.

### (5) Low-Level Tasks
One entry per pipeline agent, plus one for the integrator. Use this exact format for every entry
(do not deviate from the four labeled fields):

```
Task: [Agent Name]
Prompt: "[Exact prompt you will give Claude Code]"
File to CREATE: [file path]
Function to CREATE: [function signature]
Details: [what the agent checks, transforms, or decides]
```

Write one task block for each of:
1. **Transaction Validator** — `File to CREATE: agents/transaction_validator.py`,
   `Function to CREATE: process_message(message: dict) -> dict`. Details: checks required fields
   present, amount parses as a positive `Decimal`, currency is in the ISO 4217 allowlist, timestamp
   parses as ISO 8601; on failure returns a `results`-targeted envelope with `status: "rejected"`
   and a `reason`; on success returns an envelope targeted at the fraud detector with
   `status: "validated"`.
2. **Fraud Detector** — `File to CREATE: agents/fraud_detector.py`,
   `Function to CREATE: process_message(message: dict) -> dict`. Details: computes an additive risk
   score (amount > $10,000 => +0.4, timing 00:00-05:00 UTC => +0.3, cross-border => +0.2,
   near-threshold $9,000-$10,000 => +0.2); score >= 0.7 rejects as `fraud_review`; 0.3 <= score < 0.7
   flags and continues; below 0.3 is clean; the score is always attached to the message.
3. **Settlement Processor** — `File to CREATE: agents/settlement_processor.py`,
   `Function to CREATE: process_message(message: dict) -> dict`. Details: computes a 0.1%
   settlement fee with `Decimal`/`ROUND_HALF_UP` quantized to 2 places, stamps `status: "settled"`
   (or `settled_with_flag` for flagged transactions), writes the final outcome to `shared/results/`.
4. **Integrator** — `File to CREATE: integrator.py`,
   `Function to CREATE: run_pipeline(base_dir: Path, sample_path: Path) -> dict`. Details: recreates
   `shared/` subdirectories, seeds one input message per transaction from
   `sample-transactions.json`, runs the three agents in order via the file-relay protocol, and
   writes `shared/results/pipeline-summary.json` with counts by status, rejection reasons, and
   settled volume per currency.

## 2. Update `agents.md`

Create `agents.md` at the repo root if it does not already exist, or extend it if it does. Add (or
update) a section with project-specific context for this banking pipeline, covering:
- The three pipeline agents and their responsibilities (validator, fraud detector, settlement
  processor) and the file-relay protocol they communicate through
  (`shared/input/` -> `shared/processing/` -> `shared/output/` -> `shared/results/`).
- The non-negotiable domain rules: `decimal.Decimal` for all money, ISO 4217 currency codes, ISO
  8601 timestamps everywhere, PII masking (no plaintext account numbers in logs or audit output).
- How to run the pipeline (`uv run python integrator.py`) and the validator's dry-run mode
  (`uv run python agents/transaction_validator.py --dry-run`).
- The coverage requirement (`uv run pytest --cov=agents --cov=pipeline --cov=mcp --cov=integrator`,
  hard floor 80% enforced by the pre-push hook, target >= 90%).

## 3. Finish

Print a short summary of what was written to `specification.md` and `agents.md` (section list and
line counts), and remind the user that `/generate-pipeline` is the next step.
