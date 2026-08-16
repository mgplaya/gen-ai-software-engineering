# Banking Transaction Pipeline Specification

> Ingest the information from this file, implement the Low-Level Tasks, and generate the code that will satisfy the High and Mid-Level Objectives.

## 1. High-Level Objective

Process banking transactions end-to-end through validation, fraud scoring, and settlement, writing auditable JSON results for every transaction in `shared/results/`.

## 2. Mid-Level Objectives

- Transactions with a missing required field, a non-positive amount, a non-ISO-4217 currency, or an unparseable ISO 8601 timestamp are rejected by the validator with a `reason` field, and never reach fraud scoring or settlement.
- Transactions with a risk score >= 0.7 (amount > $10,000, unusual timing 00:00-05:00 UTC, cross-border, or near-threshold $9,000-$10,000 signals, additively combined) are rejected as `fraud_review`; scores with 0.3 <= score < 0.7 are flagged (`fraud_flag: true`) but continue to settlement; scores below 0.3 continue clean.
- Every settled transaction has a 0.1% settlement fee computed with `decimal.Decimal` and `ROUND_HALF_UP`, quantized to 2 decimal places, and is stamped `status: "settled"` or `status: "settled_with_flag"` for flagged transactions.
- All agent operations are logged to the audit trail (`pipeline/audit.py`) with an ISO 8601 timestamp, agent name, transaction id, and outcome — account numbers masked (e.g. `ACC-****01`), never plaintext.
- Every transaction in `sample-transactions.json` (all 8 records, TXN001-TXN008) produces exactly one result file in `shared/results/`, and the integrator writes a `pipeline-summary.json` aggregating counts by status, rejection reasons, and settled volume per currency. Test coverage across `agents/`, `pipeline/`, `mcp/`, and `integrator.py` is >= 90%, with a hard gate at 80% enforced by the pre-push hook.

## 3. Implementation Notes

- Monetary values MUST use `decimal.Decimal`, parsed from JSON string amounts (e.g. `"25000.00"`) — never `float`. Every arithmetic step (risk thresholds, fee computation, settlement aggregation) stays in `Decimal`.
- Currency codes MUST be validated against an ISO 4217 allowlist: `{"USD", "EUR", "GBP", "JPY", "CHF", "CAD", "AUD"}` (`agents/transaction_validator.py::ISO_4217`). A currency outside this set is rejected.
- Every agent action MUST go through the audit logger (`pipeline/audit.py::log_event`), recording exactly four fields: ISO 8601 timestamp (`utc_now_iso()`, e.g. `2026-03-16T10:00:00Z`), agent name, transaction id, and outcome. The audit log schema has no field for account numbers or free-text descriptions, so they can never leak into it.
- Account numbers and other PII MUST be masked in all log output (e.g. `"ACC-1001"` -> `"ACC-****01"` via `pipeline/audit.py::mask_account`) — never log plaintext account numbers, names, or transaction descriptions. Result files in `shared/results/` retain full transaction data (raw account numbers) for settlement purposes; `shared/` is gitignored.
- Every hand-off between agents uses the standard six-field message envelope (`message_id`, `timestamp`, `source_agent`, `target_agent`, `message_type`, `data`) from `pipeline/message.py`, and travels through the file-based `shared/input/ -> shared/processing/ -> shared/output/ -> shared/results/` protocol (`pipeline/protocol.py`) — no in-memory or network transport between agents.
- Each pipeline agent exposes a pure `process_message(message: dict) -> dict` that never mutates its input's `data` dict.
- A message that cannot be parsed or that fails envelope validation never crashes the pipeline: `integrator.py::run_agent` turns it into a terminal `status: "error"` result instead, so one bad file never blocks the rest of the run.

## 4. Context

### Beginning context
- `sample-transactions.json` — 8 raw transaction records (TXN001-TXN008), each with `transaction_id`, `timestamp`, `source_account`, `destination_account`, `amount` (string), `currency`, `transaction_type`, `description`, and `metadata.country`.
- Empty `shared/` subdirectories: `shared/input/`, `shared/processing/`, `shared/output/`, `shared/results/` (recreated by the integrator on every run).
- No result files, no audit log, no pipeline summary yet.

### Ending context
- One result JSON file per transaction in `shared/results/` (`TXN001.json` ... `TXN008.json`), each a message envelope whose `data` carries the final `status` (`settled`, `settled_with_flag`, `rejected`, `fraud_review`, or `error`) and, where applicable, `reason`, `risk_score`, `risk_signals`, `settlement_fee`, `settled_amount`.
- `shared/results/pipeline-summary.json` — aggregated counts by status, a rejection-reasons map keyed by transaction id, and total settled volume per currency, generated at `utc_now_iso()`.
- `shared/audit.log` — one JSON line per agent action (timestamp, agent, transaction_id, outcome).
- Test suite in `tests/` passing with coverage >= 90% across `agents/`, `pipeline/`, `mcp/`, and `integrator.py`, as measured by `uv run pytest --cov=agents --cov=pipeline --cov=mcp --cov=integrator`.

## 5. Low-Level Tasks

```
Task: Transaction Validator
Prompt: "Create agents/transaction_validator.py with a pure process_message(message: dict) -> dict function that is the first stage of the banking pipeline. It must check that all required fields (transaction_id, timestamp, source_account, destination_account, amount, currency, transaction_type) are present and non-empty, that amount parses as a positive decimal.Decimal, that currency is in an ISO 4217 allowlist (USD, EUR, GBP, JPY, CHF, CAD, AUD), and that timestamp parses as an ISO 8601 string (accepting a trailing 'Z'). On any failure, return a terminal envelope (via pipeline/message.py::create_envelope) targeted at 'results' with status: 'rejected' and a reason field joining all validation errors with '; '. On success, return an envelope targeted at 'fraud_detector' with status: 'validated'. Never mutate the input message's data dict. Also add a --dry-run CLI entry point (argparse, main() under if __name__ == '__main__':) that reads sample-transactions.json (or a --sample PATH) and prints a validation table without writing any files or calling process_message."
File to CREATE: agents/transaction_validator.py
Function to CREATE: process_message(message: dict) -> dict
Details: Checks required fields present/non-empty (missing required field: <field>); amount parses as Decimal and is > 0 (amount must be greater than zero / amount is not a valid number); currency in ISO_4217 = {USD, EUR, GBP, JPY, CHF, CAD, AUD} (unsupported currency: <value>); timestamp parses via datetime.fromisoformat after normalizing a trailing 'Z' to '+00:00' (invalid timestamp: <value>). Rejects TXN006 (currency XYZ) and TXN007 (amount -100.00) from sample-transactions.json. On failure: status="rejected", reason=<errors joined with "; ">, target_agent="results". On success: status="validated", target_agent="fraud_detector".
```

```
Task: Fraud Detector
Prompt: "Create agents/fraud_detector.py with a pure process_message(message: dict) -> dict function that is the second stage of the banking pipeline. It must compute an additive decimal.Decimal risk score for a validated transaction: amount > 10000 adds 0.4 ('high_value'); amount in the inclusive range 9000-10000 adds 0.2 ('near_threshold', mutually exclusive with high_value); a UTC hour in [0, 5) parsed from the ISO 8601 timestamp adds 0.3 ('unusual_timing'); a cross-border transaction (transaction's metadata.country missing or not in the home-country set for its currency: USD->US, EUR->EU member states, GBP->GB, JPY->JP, CHF->CH, CAD->CA, AUD->AU) adds 0.2 ('cross_border'). Always attach risk_score (as a string) and risk_signals (list of triggered signal names) to the outgoing data. If score >= 0.7, return a terminal envelope targeted at 'results' with status: 'fraud_review' and a reason naming the score and signals. If 0.3 <= score < 0.7, attach fraud_flag: true, set status: 'risk_scored', and forward to 'settlement_processor'. If score < 0.3, attach fraud_flag: false, set status: 'risk_scored', and forward to 'settlement_processor'. Never mutate the input message's data dict."
File to CREATE: agents/fraud_detector.py
Function to CREATE: process_message(message: dict) -> dict
Details: Additive Decimal risk score with the table amount > $10,000 => +0.4 (high_value), timing 00:00-05:00 UTC => +0.3 (unusual_timing), cross-border => +0.2 (cross_border), near-threshold $9,000-$10,000 => +0.2 (near_threshold, mutually exclusive with high_value). Bands (inclusive lower bounds): score >= 0.7 rejects as status="fraud_review" (target_agent="results") with reason citing score and signals; 0.3 <= score < 0.7 sets fraud_flag=True, status="risk_scored", forwards to settlement_processor; score < 0.3 sets fraud_flag=False, status="risk_scored", forwards to settlement_processor. risk_score and risk_signals are always attached. Against sample-transactions.json: TXN002 ($25,000) and TXN005 ($75,000) score 0.4 (flagged); TXN003 ($9,999.99) scores 0.2 (clean); TXN004 (02:47 UTC, EUR from DE) scores 0.3 (flagged, not cross-border since DE is in the EUR home set).
```

```
Task: Settlement Processor
Prompt: "Create agents/settlement_processor.py with a pure process_message(message: dict) -> dict function that is the third and terminal stage of the banking pipeline. It must compute a 0.1% settlement fee on the transaction's decimal.Decimal amount, quantized to 2 decimal places with ROUND_HALF_UP, and a settled_amount equal to amount minus that fee (also quantized to 2 places with ROUND_HALF_UP). Set status: 'settled_with_flag' if the incoming data's fraud_flag is truthy, else status: 'settled'. Always return a terminal envelope targeted at 'results' (via pipeline/message.py::create_envelope), since this agent is always the pipeline's last stage. Never mutate the input message's data dict — return a new dict with settlement_fee, settled_amount, and status added."
File to CREATE: agents/settlement_processor.py
Function to CREATE: process_message(message: dict) -> dict
Details: FEE_RATE = Decimal('0.001') (0.1%); settlement_fee = (amount * FEE_RATE).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP); settled_amount = (amount - settlement_fee).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP); status = 'settled_with_flag' if txn.get('fraud_flag') else 'settled'. Always routes to target_agent='results' since settlement is the final stage — no further forwarding.
```

```
Task: Integrator
Prompt: "Create integrator.py at the repo root as the pipeline orchestrator with a run_pipeline(base_dir: Path, sample_path: Path) -> dict function. It must recreate the shared/ subdirectories (input, processing, output, results) via pipeline/protocol.py::ensure_shared_dirs, seed one input message per record from sample-transactions.json (each wrapped in a standard envelope addressed 'integrator' -> 'transaction_validator'), then run transaction_validator, fraud_detector, and settlement_processor in order via the file-relay protocol — each pass claims every message in input/ or output/ addressed to that agent, moves it to processing/, calls the agent's process_message, and routes the result to results/ (if its status is one of the terminal statuses: rejected, fraud_review, error, settled, settled_with_flag) or back to output/ (to be picked up by the next agent), logging every hand-off via pipeline/audit.py::log_event. Any exception during processing (parse failure, envelope validation error, or an error raised by process_message) must be caught and turned into a terminal status: 'error' result instead of crashing the run. Finally, aggregate every file in results/ into shared/results/pipeline-summary.json with counts by status, a rejection-reasons map (for rejected/fraud_review/error), and total settled volume per currency (for settled/settled_with_flag), and return that summary dict. Add a main() CLI entry point that runs the pipeline against the real sample-transactions.json and shared/, then prints a per-transaction status table and summary counts."
File to CREATE: integrator.py
Function to CREATE: run_pipeline(base_dir: Path, sample_path: Path) -> dict
Details: TERMINAL_STATUSES = {rejected, fraud_review, error, settled, settled_with_flag} route to shared/results/; any other status (e.g. validated, risk_scored) routes to shared/output/ for the next agent to pick up. Seeds all 8 transactions from sample-transactions.json into shared/input/. Runs agents in order: transaction_validator -> fraud_detector -> settlement_processor. write_summary aggregates results_total, by_status counts, rejection_reasons (transaction_id -> reason, for rejected/fraud_review/error), and settled_volume_by_currency (summed Decimal per currency, for settled/settled_with_flag), timestamped generated_at via utc_now_iso(). A parse error or envelope-validation failure on any message becomes a status: "error" result rather than crashing the run, so one bad file never blocks the other 7 transactions.
```
