"""Pipeline integrator / orchestrator.

Wires together the three pipeline agents (transaction_validator,
fraud_detector, settlement_processor) via the file-based messaging
protocol in ``pipeline/``: seeds ``shared/input/`` from
``sample-transactions.json``, runs each agent in order over its addressed
messages, and writes a final ``pipeline-summary.json`` report.

Every hand-off goes through the audit logger. A message that cannot be
read or that fails envelope validation never crashes the run: it is
turned into a terminal ``"error"`` result instead, so one bad file never
blocks the rest of the pipeline.
"""

from __future__ import annotations

import sys
from decimal import Decimal
from pathlib import Path

from agents import fraud_detector, settlement_processor, transaction_validator
from pipeline.audit import log_event
from pipeline.message import create_envelope, utc_now_iso, validate_envelope
from pipeline.protocol import (
    ensure_shared_dirs,
    list_messages,
    move_to,
    read_json,
    write_json,
)

# Statuses that terminate a transaction's journey through the pipeline:
# these route to shared/results/ instead of shared/output/.
TERMINAL_STATUSES = {"rejected", "fraud_review", "error", "settled", "settled_with_flag"}

# Subset of TERMINAL_STATUSES that represent a rejection/failure, used when
# building the summary's rejection_reasons mapping.
_REJECTION_STATUSES = {"rejected", "fraud_review", "error"}

# Subset of TERMINAL_STATUSES that represent a completed settlement, used
# when aggregating settled volume by currency.
_SETTLED_STATUSES = {"settled", "settled_with_flag"}

SUMMARY_FILENAME = "pipeline-summary.json"

PROJECT_ROOT = Path(__file__).resolve().parent
DEFAULT_BASE_DIR = PROJECT_ROOT / "shared"
DEFAULT_SAMPLE_PATH = PROJECT_ROOT / "sample-transactions.json"


def seed_input(base_dir: Path, sample_path: Path) -> int:
    """Wrap each record of the sample JSON array in an envelope and seed input.

    Each record from ``sample_path`` becomes the ``data`` of an envelope
    addressed ``"integrator" -> "transaction_validator"``, written to
    ``base_dir / "input" / f"{message_id}.json"``.

    Args:
        base_dir: Directory containing the shared subdirectories.
        sample_path: Path to a sample-transactions JSON array file.

    Returns:
        The number of transactions seeded.
    """
    transactions = read_json(sample_path)
    input_dir = base_dir / "input"

    for txn in transactions:
        envelope = create_envelope("integrator", "transaction_validator", txn)
        write_json(input_dir / f"{envelope['message_id']}.json", envelope)

    return len(transactions)


def _scan_targeted(base_dir: Path, agent_name: str):
    """Find message files in input/ and output/ addressed to ``agent_name``.

    Peeks at each file by reading it as JSON. A file that cannot be parsed
    (or isn't a dict envelope) is claimed unconditionally, since there is no
    way to know its real target -- it becomes an error result for whichever
    agent scans it first. A file that parses but targets a different agent
    is left alone for a later scan.

    Returns:
        A list of ``(path, envelope_or_none, parse_error_or_none)`` tuples
        for every file claimed by this scan.
    """
    candidates = []
    for subdir in ("input", "output"):
        for path in list_messages(base_dir / subdir):
            try:
                envelope = read_json(path)
                parse_error = None
            except Exception as exc:  # noqa: BLE001 - garbage claimed, not crashed on
                envelope = None
                parse_error = exc

            is_garbage = parse_error is not None
            is_targeted = isinstance(envelope, dict) and envelope.get("target_agent") == agent_name
            if is_garbage or is_targeted:
                candidates.append((path, envelope, parse_error))

    return candidates


def run_agent(base_dir: Path, agent_name: str, process_fn) -> None:
    """Run one agent pass: claim its messages, process them, route results.

    For every message in ``input``/``output`` addressed to ``agent_name``:
    move it into ``processing`` (claiming it), validate the envelope and
    call ``process_fn``. Any exception (parse failure, validation error, or
    an error raised by ``process_fn``) is turned into a terminal ``"error"``
    envelope instead of propagating. The result is routed to ``results``
    (terminal status) or ``output`` (forwarded onward), the processing file
    is removed, and the action is audit-logged.

    Args:
        base_dir: Directory containing the shared subdirectories.
        agent_name: The ``target_agent`` value this pass claims messages for.
        process_fn: The agent's pure ``process_message(message) -> dict``.
    """
    processing_dir = base_dir / "processing"
    output_dir = base_dir / "output"
    results_dir = base_dir / "results"

    for path, envelope, parse_error in _scan_targeted(base_dir, agent_name):
        processing_path = move_to(path, processing_dir)

        try:
            if parse_error is not None:
                raise parse_error
            errors = validate_envelope(envelope)
            if errors:
                raise ValueError("; ".join(errors))
            result = process_fn(envelope)
        except Exception as exc:  # noqa: BLE001 - any failure becomes an error result
            result = create_envelope(
                agent_name,
                "results",
                {
                    "transaction_id": processing_path.stem,
                    "status": "error",
                    "reason": str(exc),
                },
            )

        data = result.get("data", {}) if isinstance(result, dict) else {}
        status = data.get("status", "unknown")
        transaction_id = data.get("transaction_id")

        dest_dir = results_dir if status in TERMINAL_STATUSES else output_dir
        filename = f"{transaction_id or result['message_id']}.json"
        write_json(dest_dir / filename, result)

        processing_path.unlink()

        log_event(base_dir, agent_name, transaction_id or "unknown", status)


def write_summary(base_dir: Path, transaction_count: int) -> dict:
    """Aggregate all result envelopes into ``results/pipeline-summary.json``.

    Args:
        base_dir: Directory containing the shared subdirectories.
        transaction_count: Number of transactions originally seeded.

    Returns:
        The summary dict, also written to
        ``base_dir / "results" / "pipeline-summary.json"``.
    """
    results_dir = base_dir / "results"

    by_status: dict[str, int] = {}
    rejection_reasons: dict[str, str] = {}
    settled_volume: dict[str, Decimal] = {}
    results_total = 0

    for path in list_messages(results_dir):
        if path.name == SUMMARY_FILENAME:
            continue

        envelope = read_json(path)
        data = envelope.get("data", {})
        status = data.get("status", "unknown")

        results_total += 1
        by_status[status] = by_status.get(status, 0) + 1

        if status in _REJECTION_STATUSES:
            txn_id = data.get("transaction_id", "unknown")
            rejection_reasons[txn_id] = data.get("reason", "")

        if status in _SETTLED_STATUSES:
            currency = data.get("currency", "unknown")
            amount = Decimal(str(data.get("settled_amount", "0")))
            settled_volume[currency] = settled_volume.get(currency, Decimal("0")) + amount

    summary = {
        "generated_at": utc_now_iso(),
        "transactions_in": transaction_count,
        "results_total": results_total,
        "by_status": by_status,
        "rejection_reasons": rejection_reasons,
        "settled_volume_by_currency": {
            currency: str(total) for currency, total in settled_volume.items()
        },
    }

    write_json(results_dir / SUMMARY_FILENAME, summary)
    return summary


def run_pipeline(base_dir: Path, sample_path: Path) -> dict:
    """Reset shared dirs, seed input, run all three agents, write the summary.

    Args:
        base_dir: Directory to hold the shared subdirectories (cleared first).
        sample_path: Path to a sample-transactions JSON array file.

    Returns:
        The summary dict returned by :func:`write_summary`.
    """
    ensure_shared_dirs(base_dir)
    transaction_count = seed_input(base_dir, sample_path)

    run_agent(base_dir, transaction_validator.AGENT_NAME, transaction_validator.process_message)
    run_agent(base_dir, fraud_detector.AGENT_NAME, fraud_detector.process_message)
    run_agent(base_dir, settlement_processor.AGENT_NAME, settlement_processor.process_message)

    return write_summary(base_dir, transaction_count)


def _detail_for(data: dict) -> str:
    """Build the human-readable detail column for the per-transaction table."""
    reason = data.get("reason")
    if reason:
        return reason

    parts = []
    if "settlement_fee" in data:
        parts.append(f"fee={data['settlement_fee']}")
    if "risk_score" in data:
        parts.append(f"risk={data['risk_score']}")
    return ", ".join(parts)


def main() -> int:
    """CLI entry point: run the pipeline against the real sample file.

    Uses ``<project>/shared`` and ``<project>/sample-transactions.json``.
    Returns 1 (printing an error to stderr) only when the sample file is
    missing; otherwise runs the pipeline, prints a per-transaction table
    plus summary counts, and returns 0.
    """
    if not DEFAULT_SAMPLE_PATH.exists():
        print(f"Error: sample file not found: {DEFAULT_SAMPLE_PATH}", file=sys.stderr)
        return 1

    summary = run_pipeline(DEFAULT_BASE_DIR, DEFAULT_SAMPLE_PATH)

    results_dir = DEFAULT_BASE_DIR / "results"
    rows = []
    for path in list_messages(results_dir):
        if path.name == SUMMARY_FILENAME:
            continue
        envelope = read_json(path)
        data = envelope.get("data", {})
        txn_id = data.get("transaction_id", path.stem)
        status = data.get("status", "unknown")
        rows.append((txn_id, status, _detail_for(data)))
    rows.sort(key=lambda row: row[0])

    print(f"{'TRANSACTION ID':<15}{'STATUS':<20}DETAIL")
    for txn_id, status, detail in rows:
        print(f"{txn_id:<15}{status:<20}{detail}")

    print()
    print(f"Transactions in: {summary['transactions_in']}  Results: {summary['results_total']}")
    for status in sorted(summary["by_status"]):
        print(f"  {status}: {summary['by_status'][status]}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
