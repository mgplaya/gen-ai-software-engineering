"""Transaction validator agent.

First stage of the pipeline: applies pure validation rules to an incoming
transaction (required fields, positive Decimal amount, ISO 4217 currency,
ISO 8601 timestamp) before forwarding it to the fraud detector. Rejected
transactions short-circuit straight to results.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path

if __package__ in (None, ""):
    # Allow running as a plain script (``python agents/transaction_validator.py``)
    # by putting the project root on sys.path so ``pipeline`` resolves.
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from pipeline.message import create_envelope

AGENT_NAME = "transaction_validator"
NEXT_AGENT = "fraud_detector"

REQUIRED_FIELDS = (
    "transaction_id",
    "timestamp",
    "source_account",
    "destination_account",
    "amount",
    "currency",
    "transaction_type",
)

# ISO 4217 currency codes accepted by the pipeline.
ISO_4217 = {"USD", "EUR", "GBP", "JPY", "CHF", "CAD", "AUD"}

DEFAULT_SAMPLE_PATH = Path(__file__).resolve().parent.parent / "sample-transactions.json"


def _is_missing(value) -> bool:
    if value is None:
        return True
    if isinstance(value, str) and not value.strip():
        return True
    return False


def _parses_as_iso_timestamp(value) -> bool:
    if not isinstance(value, str):
        return False
    text = value[:-1] + "+00:00" if value.endswith("Z") else value
    try:
        datetime.fromisoformat(text)
        return True
    except (ValueError, TypeError):
        return False


def validation_errors(txn: dict) -> list[str]:
    """Return human-readable validation errors for a transaction dict.

    Pure rule checks only: required fields present/non-empty, amount parses
    as a positive ``decimal.Decimal``, currency is in the ISO 4217 allowlist,
    timestamp parses as ISO 8601 (accepting a trailing "Z"). An empty list
    means the transaction is valid.
    """
    errors: list[str] = []

    for field in REQUIRED_FIELDS:
        if _is_missing(txn.get(field)):
            errors.append(f"missing required field: {field}")

    amount = txn.get("amount")
    if not _is_missing(amount):
        try:
            if Decimal(str(amount)) <= 0:
                errors.append("amount must be greater than zero")
        except InvalidOperation:
            errors.append(f"amount is not a valid number: {amount!r}")

    currency = txn.get("currency")
    if not _is_missing(currency) and (
        not isinstance(currency, str) or currency not in ISO_4217
    ):
        # The isinstance guard runs first so an unhashable currency (e.g. a
        # list) never reaches the ``in ISO_4217`` membership test.
        errors.append(f"unsupported currency: {currency!r}")

    timestamp = txn.get("timestamp")
    if not _is_missing(timestamp) and not _parses_as_iso_timestamp(timestamp):
        errors.append(f"invalid timestamp: {timestamp!r}")

    return errors


def process_message(message: dict) -> dict:
    """Validate a transaction message and route it to the next stage.

    Never mutates the input message's ``data`` dict. On validation failure,
    returns a terminal envelope targeted at ``"results"`` with
    ``status: "rejected"`` and a ``reason`` joining all errors with "; ".
    On success, returns an envelope targeted at ``NEXT_AGENT`` with
    ``status: "validated"``.
    """
    txn = dict(message.get("data", {}))
    errors = validation_errors(txn)

    if errors:
        txn["status"] = "rejected"
        txn["reason"] = "; ".join(errors)
        return create_envelope(AGENT_NAME, "results", txn)

    txn["status"] = "validated"
    return create_envelope(AGENT_NAME, NEXT_AGENT, txn)


def main() -> int:
    """CLI entry point: validate a sample-transactions file without processing.

    Supports ``--dry-run`` (validate only, never calls ``process_message``)
    and an optional ``--sample PATH`` (defaults to the project's
    ``sample-transactions.json``). Prints a table of transaction id /
    VALID or INVALID / reasons, followed by a total/valid/invalid summary
    line. Always returns 0.
    """
    parser = argparse.ArgumentParser(
        prog="transaction_validator",
        description="Validate transactions without processing them.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate transactions without processing them (the only supported mode).",
    )
    parser.add_argument(
        "--sample",
        type=Path,
        default=DEFAULT_SAMPLE_PATH,
        help="Path to a sample-transactions JSON file.",
    )
    args = parser.parse_args()
    # args.dry_run is accepted (and always passed by /validate-transactions)
    # for interface compatibility, but not branched on: this CLI only ever
    # validates, never processes, so it is inherently a dry run either way.

    with args.sample.open("r", encoding="utf-8") as f:
        transactions = json.load(f)

    valid_count = 0
    invalid_count = 0

    print(f"{'TRANSACTION ID':<20}{'STATUS':<10}REASONS")
    for txn in transactions:
        errors = validation_errors(txn)
        txn_id = txn.get("transaction_id", "?")
        if errors:
            invalid_count += 1
            print(f"{txn_id:<20}{'INVALID':<10}{'; '.join(errors)}")
        else:
            valid_count += 1
            print(f"{txn_id:<20}{'VALID':<10}".rstrip())

    total = len(transactions)
    print(f"Total: {total}  Valid: {valid_count}  Invalid: {invalid_count}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
