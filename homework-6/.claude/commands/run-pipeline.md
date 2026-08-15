---
description: "Run the multi-agent banking pipeline end-to-end and summarize the results."
---

Run the multi-agent banking pipeline end-to-end.

Steps:
1. Check that `sample-transactions.json` exists at the repo root
   (`/Users/gorishnyi/development/education/set/gen-ai-software-engineering/homework-6/sample-transactions.json`).
   If it is missing, stop and report the problem instead of continuing.
2. Clear the `shared/` directories (`shared/input/`, `shared/processing/`, `shared/output/`,
   `shared/results/`) so this is a clean run. The integrator recreates these on startup, but remove
   any stale files first so leftover results from a previous run cannot be confused with this run's
   output.
3. Run the pipeline: `uv run python integrator.py`.
4. Show a summary of results from `shared/results/`: list every result file, read
   `shared/results/pipeline-summary.json`, and print the counts by status (the terminal statuses
   are `settled`, `settled_with_flag`, `rejected`, `fraud_review`, and `error` — `validated` is only
   an intermediate forwarding status and never appears in `shared/results/`), the rejection
   reasons, and the total settled volume per currency.
5. Report any transactions that were rejected and why: for each result file with
   `status: "rejected"`, `status: "fraud_review"`, or `status: "error"`, print the transaction id and
   its `reason` field.
