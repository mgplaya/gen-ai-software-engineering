---
description: "Validate all transactions in sample-transactions.json without processing them, using the validator's dry-run CLI."
---

Validate all transactions in sample-transactions.json without processing them.

Steps:
1. Run the validator in dry-run mode: `uv run python agents/transaction_validator.py --dry-run`
   (defaults to `sample-transactions.json` at the repo root; pass `--sample PATH` to point at a
   different file if asked).
2. Report: total count, valid count, invalid count, and the reasons for rejection for each invalid
   transaction (parsed from the command's printed output — the last line gives
   `Total: N  Valid: N  Invalid: N`, and each invalid row lists its rejection reasons joined with
   "; ").
3. Show a table of results with columns: Transaction ID, Status (VALID/INVALID), Reasons — one row
   per transaction from `sample-transactions.json`, in the order the command printed them.
