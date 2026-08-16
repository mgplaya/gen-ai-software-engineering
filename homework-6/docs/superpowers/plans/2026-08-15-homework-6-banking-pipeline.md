# Homework 6 — Multi-Agent Banking Pipeline: Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the Homework 6 capstone — four meta-agent slash commands that produce a working three-agent banking transaction pipeline, plus operational skills, a coverage-gate hook, context7 research notes, and a custom FastMCP server.

**Architecture:** Sequential file-relay pipeline: an integrator seeds JSON message files into `shared/input/`, then runs Validator → Fraud Detector → Settlement Processor in order; each agent claims messages addressed to it via `shared/processing/`, and results land in `shared/results/`. Agents are pure `process_message(message: dict) -> dict` functions; shared envelope/protocol/audit code lives in a `pipeline/` package.

**Tech Stack:** Python ≥3.12, uv, pytest + pytest-cov, FastMCP, Claude Code commands & hooks, context7 MCP.

**Spec:** `homework-6/docs/superpowers/specs/2026-08-15-homework-6-banking-pipeline-design.md` — the authoritative source for all rules (validation checks, risk-score table and bands, fee formula, expected sample outcomes).

## Global constraints (apply to every task)

- All monetary math uses `decimal.Decimal` parsed from JSON strings — never float. Risk scores are also Decimal to avoid float-sum drift.
- Currencies validated against an ISO 4217 allowlist; timestamps are ISO 8601 UTC.
- PII: account numbers never appear unmasked in logs (mask style `ACC-****01`); names/descriptions are never logged.
- Coverage: hard gate 80% (hook), target ≥90%.
- Tests never touch the real `shared/` — every path is parameterized by a base directory and tests use `tmp_path`.
- Author name in docs: **Mykhailo Gorishnyi**.
- All commands run via uv from `homework-6/`; the Claude Code session must be launched from `homework-6/` so `.claude/` is picked up.
- Each task follows TDD (failing test → minimal implementation → green → commit) and ends with its own commit on `homework-6-submission`.

---

## Task 1: Project scaffolding + message envelope

**Files:** `pyproject.toml`, `conftest.py` (empty, makes the project root importable for tests), `.gitignore` (ignore `shared/`, caches, venv, coverage artifacts), `pipeline/__init__.py`, `pipeline/message.py`, `tests/test_message.py`

Set up the uv project (deps: fastmcp; dev: pytest, pytest-cov; pytest configured to look in `tests/`). Implement the standard message envelope module:

- A constructor that builds the envelope from the spec: uuid4 `message_id`, ISO 8601 UTC `timestamp`, `source_agent`, `target_agent`, `message_type` (default `"transaction"`), and a `data` dict.
- A UTC-now-as-ISO-string helper (single source of truth for timestamps everywhere).
- An envelope validator returning a list of human-readable errors (missing fields, non-dict input, non-dict `data`); empty list means valid.

**Tests:** envelope has all six required fields; message IDs are unique across calls; timestamp format matches the spec's `...Z` style; validator flags each kind of malformed envelope and passes a good one.

- [ ] Write failing tests → run → implement → green → commit (`feat: project scaffolding and message envelope`)

## Task 2: File protocol

**Files:** `pipeline/protocol.py`, `tests/test_protocol.py`

Utilities for the `shared/` file protocol, all taking an explicit base directory:

- Ensure/reset the four subdirectories (`input`, `processing`, `output`, `results`) — idempotent, clears leftovers so reruns are clean.
- JSON read/write helpers (pretty-printed, UTF-8).
- List message files in a directory (sorted, `.json` only).
- Move a message file between stage directories.

**Tests:** directories created and cleared on rerun; JSON round-trip; sorted listing ignores non-JSON files; move relocates the file and returns its new path.

- [ ] Tests → implement → green → commit (`feat: shared-directory file protocol`)

## Task 3: Audit logger with PII masking

**Files:** `pipeline/audit.py`, `tests/test_audit.py`

- Account-masking helper producing the spec's `ACC-****01` style (keep prefix and last two characters; degrade safely for short/empty values).
- An audit event writer appending one JSON line per event — timestamp, agent name, transaction ID, outcome — to an `audit.log` under the given base directory. Account numbers and free-text descriptions are never part of an audit entry.

**Tests:** masking cases (normal, short, empty); log file appends valid JSON lines with exactly the four fields.

- [ ] Tests → implement → green → commit (`feat: audit logger with account masking`)

## Task 4: Transaction Validator agent

**Files:** `agents/__init__.py`, `agents/transaction_validator.py`, `tests/test_transaction_validator.py`

Pure validation per the spec: required fields present; amount parses as Decimal and is positive; currency in the ISO 4217 allowlist; timestamp parses as ISO 8601; accounts non-empty. `process_message` returns a rejected result (with joined `reason`) or forwards a `validated` message targeted at the fraud detector.

Also a small `__main__` CLI supporting `--dry-run` (and an optional sample-file argument): validates `sample-transactions.json` without processing and prints a table plus total/valid/invalid counts — this is what `/validate-transactions` invokes.

**Tests:** happy path forwards to `fraud_detector`; each rejection reason individually (negative amount TXN007-style, zero amount, unknown currency `XYZ`, missing field, bad timestamp, non-numeric amount); dry-run CLI reports correct counts on a temp sample file.

- [ ] Tests → implement → green → commit (`feat: transaction validator agent with dry-run CLI`)

## Task 5: Fraud Detector agent

**Files:** `agents/fraud_detector.py`, `tests/test_fraud_detector.py`

Additive Decimal risk score exactly per the spec table: high value (>$10,000, +0.4), near-threshold ($9,000–$10,000 inclusive, +0.2 — mutually exclusive with high value), unusual timing (00:00–04:59 UTC, +0.3), cross-border (metadata country not in the currency's home-country set, +0.2; the currency→home-country map lives here). Bands: ≥0.7 rejected as `fraud_review` with reason; 0.3–<0.7 flagged (`fraud_flag: true`) but forwarded; <0.3 clean. Score and triggered signals always attached to the message; survivors are targeted at the settlement processor.

**Tests:** each signal in isolation; boundary cases (exactly $10,000 → near-threshold; exactly 05:00 → no timing signal); band boundaries (score exactly 0.3 → flagged, 0.7 → rejected); EUR-from-DE is *not* cross-border; a stacked case (high value + night + cross-border = 0.9) is rejected.

- [ ] Tests → implement → green → commit (`feat: fraud detector agent with additive risk scoring`)

## Task 6: Settlement Processor agent

**Files:** `agents/settlement_processor.py`, `tests/test_settlement_processor.py`

Computes a 0.1% settlement fee with Decimal `ROUND_HALF_UP` quantized to 2 places, records fee and settled amount, and stamps `settled` (clean) or `settled_with_flag` (fraud-flagged). Always terminal — results go to `shared/results/`.

**Tests:** fee arithmetic on plain amounts; the rounding edge (9999.99 → fee 10.00, not 9.99); flagged vs clean status; output message is terminal.

- [ ] Tests → implement → green → commit (`feat: settlement processor agent`)

## Task 7: Integrator / orchestrator

**Files:** `integrator.py`, `tests/test_integrator.py`

The orchestrator: resets `shared/`, wraps each record of `sample-transactions.json` in an envelope addressed to the validator and seeds `shared/input/`, then runs the three agents in order. For each agent: claim messages addressed to it (from `input`/`output`) into `processing`, call `process_message`, route the result — terminal statuses (`rejected`, `fraud_review`, `error`, `settled`, `settled_with_flag`) to `results/` (file named by transaction ID), everything else onward to `output/`. Unreadable or invalid-envelope files become `error` results instead of crashing; one bad message never blocks the rest. Every action goes through the audit logger. Finally it writes `shared/results/pipeline-summary.json` (counts by status, rejection reasons, settled volume per currency) and prints a human-readable summary table; `main()` exits non-zero only if `sample-transactions.json` is missing.

**Tests:** full integration run against a `tmp_path` copy of the real sample — asserts the spec's expected outcome (3 settled: TXN001/TXN003/TXN008; 3 settled_with_flag: TXN002/TXN004/TXN005; 2 rejected: TXN006/TXN007; all 8 in results plus summary file); a malformed JSON file becomes an `error` result; audit log exists and contains no raw account numbers; summary aggregates match.

- [ ] Tests → implement → green → run the real pipeline once locally → commit (`feat: pipeline integrator and summary report`)

## Task 8: Custom FastMCP server + mcp.json

**Files:** `mcp/server.py` (no `__init__.py` — must not shadow the installed `mcp` SDK that FastMCP depends on), `mcp.json`, `.mcp.json` (same content, so Claude Code actually loads it), `tests/test_mcp_server.py`

FastMCP server `pipeline-status` following the homework-5 pattern: thin decorated tools/resource delegating to plain helpers that take an explicit results directory (helpers are what tests target; the shared dir is overridable via an environment variable):

- Tool `get_transaction_status(transaction_id)` — reads that transaction's result file; graceful `not_found` answer.
- Tool `list_pipeline_results()` — aggregates all result files (skipping the summary file) into a count + per-transaction status list.
- Resource `pipeline://summary` — returns `pipeline-summary.json` as text, with a friendly "no run yet" fallback.

`mcp.json` configures both context7 (`npx -y @upstash/context7-mcp@latest`) and pipeline-status (`uv run python mcp/server.py`). Known constraint: servers become callable only after a Claude Code session restart.

**Tests:** helper-level — status found / not found; results listing skips the summary file; summary text fallback and pass-through.

- [ ] Tests → implement → green → commit (`feat: pipeline-status FastMCP server and mcp.json`)

## Task 9: Coverage gate hook

**Files:** `.claude/settings.json`, `.claude/hooks/coverage-gate.sh` (executable)

A `PreToolUse` hook matched to the Bash tool. The script reads the hook JSON from stdin, extracts the command, and passes through instantly unless it contains `git push`. On a push it runs pytest with coverage over `agents`, `pipeline`, and `mcp` with fail-under at the threshold (default 80, overridable via an environment variable so the blocking behavior can be demonstrated for the screenshot), and exits with the blocking code (2) plus an explanatory stderr message when coverage is short.

**Verification (manual, no pytest):** pipe a fabricated hook JSON containing a `git push` command into the script — exit 0 at current coverage; rerun with the threshold raised to 99 — exit 2 with the BLOCKED message; pipe a non-push command — instant exit 0.

- [ ] Write script + settings → verify all three cases → commit (`feat: coverage gate hook blocking git push below 80%`)

## Task 10: Six slash commands (four meta-agents + two skills)

**Files:** `.claude/commands/write-spec.md`, `generate-pipeline.md`, `generate-tests.md`, `generate-docs.md`, `run-pipeline.md`, `validate-transactions.md`

Each is a markdown prompt with a frontmatter description:

- `/write-spec` (Agent 1) — generate `specification.md` per the course template (all 5 sections, Low-Level Tasks in the exact `Task/Prompt/File to CREATE/Function to CREATE/Details` format, one per pipeline agent) and update `agents.md`.
- `/generate-pipeline` (Agent 2) — implement the pipeline from `specification.md`; explicitly instructs querying context7 for FastMCP and Python decimal docs and appending each query to `research-notes.md`.
- `/generate-tests` (Agent 3) — write pytest suites per agent + integration, run coverage, iterate until ≥90%.
- `/generate-docs` (Agent 4) — generate `README.md` (with "Created by Mykhailo Gorishnyi", agent bullets, ASCII diagram, tech-stack table) and `HOWTORUN.md`.
- `/run-pipeline` — the five steps from TASKS.md: check sample file, clear `shared/`, run the integrator, summarize results, report rejections with reasons.
- `/validate-transactions` — run the validator's `--dry-run` CLI and present the totals table.

**Verification:** all six files exist with descriptions; the two Task-3 skills contain the step lists TASKS.md requires.

- [ ] Write files → verify → commit (`feat: meta-agent and operational slash commands`)

## Task 11: specification.md + agents.md

**Files:** `specification.md`, `agents.md`

The Agent-1 deliverables, written to match what `/write-spec` produces: `specification.md` with all five template sections (High-Level Objective; 4–5 testable Mid-Level Objectives; Implementation Notes covering Decimal/ISO 4217/audit/PII; Context with beginning and ending state; Low-Level Tasks — one entry per pipeline agent plus the integrator, each in the exact required format with the actual prompt, file, and function names from Tasks 4–7). `agents.md` describes the project for AI agents: the two-layer architecture (meta-agents vs pipeline agents), message protocol, conventions, and commands.

**Verification:** every section of the TASKS.md structure is present; Low-Level Task entries name the real files/functions built in Tasks 4–7.

- [ ] Write both docs → verify against TASKS.md checklist → commit (`docs: specification and agents context`)

## Task 12: research-notes.md via live context7 queries

**Files:** `research-notes.md`

Make at least two real context7 queries and document them in the TASKS.md entry format (search, returned library ID, applied insight):

1. FastMCP — tool/resource decorator patterns (validates Task 8's server structure).
2. Python decimal — quantize/ROUND_HALF_UP usage (validates Task 6's fee math).

The notes record the *actual* library IDs and insights returned, not invented ones. If context7 tools aren't callable in the executing session (per known constraint, `.mcp.json` needs a session restart), stop and report — the user restarts the session, then this task completes.

- [ ] Run queries → write notes → commit (`docs: context7 research notes`)

## Task 13: README.md + HOWTORUN.md

**Files:** `README.md`, `HOWTORUN.md`

The Agent-4 deliverables: README with author line **Created by Mykhailo Gorishnyi**, 1–2 paragraphs on what the system does, one bullet per agent (all three pipeline agents + the four meta-agents), an ASCII architecture diagram of the file-relay flow, and a tech-stack table. HOWTORUN with numbered steps from clean checkout to full demo: install uv, sync, run pipeline, dry-run validation, tests + coverage, MCP servers (restart caveat), hook demonstration, slash commands.

**Verification:** author name present; diagram shows all four `shared/` stages; HOWTORUN steps actually work when followed.

- [ ] Write docs → follow HOWTORUN end-to-end once → commit (`docs: README and HOWTORUN`)

## Task 14: Final verification + submission checklist

No new code. Run everything and prepare the submission:

- [ ] Full test run with coverage report — confirm ≥90% (gate is 80%).
- [ ] `uv run python integrator.py` — all 8 transactions in `shared/results/` + summary, matching the spec's expected outcomes.
- [ ] Hook demo: verify pass-through and a blocked push (threshold raised) for the screenshot.
- [ ] Self-check every row of the TASKS.md Success Criteria table.
- [ ] **User actions (manual):** capture the 5 screenshots into `docs/screenshots/` — `pipeline-run.png`, `test-coverage.png`, `skill-run-pipeline.png` (run `/run-pipeline` in a restarted session), `hook-trigger.png`, `mcp-interaction.png` (context7 query + `get_transaction_status` call) — then open the PR from `homework-6-submission` with all screenshots embedded in the description.
- [ ] Final commit of any remaining artifacts (`chore: final verification artifacts`).

---

## Self-review notes

- Spec coverage: every TASKS.md deliverable maps to a task — spec/agents.md (11), pipeline + integrator (4–7), skills (10), hook (9), mcp.json + server (8), research notes (12), tests (4–8), README/HOWTORUN (13), screenshots/PR (14).
- The `mcp/` directory deliberately has no `__init__.py` and coverage/imports treat it as a path, so it never shadows the installed `mcp` SDK package FastMCP depends on.
- Naming used consistently across tasks: agents expose `process_message`; terminal statuses are `rejected`, `fraud_review`, `error`, `settled`, `settled_with_flag`; result files are named by transaction ID.
