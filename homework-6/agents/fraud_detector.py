"""Fraud detector agent.

Second stage of the pipeline: applies an additive Decimal risk score to a
validated transaction, then routes it based on the resulting risk band.
Transactions scoring at or above the "fraud_review" threshold are rejected
straight to results; the rest are forwarded to the settlement processor
carrying their score, triggered signals, and a fraud flag.
"""

from __future__ import annotations

import sys
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path

if __package__ in (None, ""):
    # Allow running as a plain script (``python agents/fraud_detector.py``)
    # by putting the project root on sys.path so ``pipeline`` resolves.
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from pipeline.message import create_envelope

AGENT_NAME = "fraud_detector"
NEXT_AGENT = "settlement_processor"

# Score thresholds and increments, per the risk-score spec table.
HIGH_VALUE_THRESHOLD = Decimal("10000")
NEAR_THRESHOLD_LOW = Decimal("9000")
HIGH_VALUE_SCORE = Decimal("0.4")
NEAR_THRESHOLD_SCORE = Decimal("0.2")
UNUSUAL_TIMING_SCORE = Decimal("0.3")
CROSS_BORDER_SCORE = Decimal("0.2")

# Risk bands (inclusive lower bounds).
FRAUD_REVIEW_THRESHOLD = Decimal("0.7")
FRAUD_FLAG_THRESHOLD = Decimal("0.3")

EU_MEMBER_COUNTRIES = {
    "DE",
    "FR",
    "ES",
    "IT",
    "NL",
    "AT",
    "BE",
    "FI",
    "IE",
    "PT",
    "GR",
}

# Currency -> set of "home" countries for that currency. A transaction is
# cross-border when its metadata country is missing, or is not in the home
# set for its currency.
CURRENCY_HOME_COUNTRIES: dict[str, set[str]] = {
    "USD": {"US"},
    "EUR": set(EU_MEMBER_COUNTRIES),
    "GBP": {"GB"},
    "JPY": {"JP"},
    "CHF": {"CH"},
    "CAD": {"CA"},
    "AUD": {"AU"},
}


def _parse_utc_hour(timestamp: str) -> int | None:
    """Return the UTC hour of an ISO 8601 timestamp, or None if unparseable.

    Offset-aware timestamps (including non-Z offsets such as "+05:00", which
    the upstream validator also accepts) are converted to UTC before reading
    the hour. Naive timestamps (no offset) are treated as already UTC.
    """
    text = timestamp[:-1] + "+00:00" if timestamp.endswith("Z") else timestamp
    try:
        parsed = datetime.fromisoformat(text)
    except (ValueError, TypeError):
        return None

    if parsed.tzinfo is not None:
        parsed = parsed.astimezone(timezone.utc)
    return parsed.hour


def _is_cross_border(txn: dict) -> bool:
    currency = txn.get("currency")
    home_countries = CURRENCY_HOME_COUNTRIES.get(currency)
    if home_countries is None:
        # Unknown currency: treat as cross-border, since there is no home
        # set it could possibly belong to.
        return True

    country = (txn.get("metadata") or {}).get("country")
    if not country:
        return True

    return country not in home_countries


def risk_score(txn: dict) -> tuple[Decimal, list[str]]:
    """Compute the additive Decimal risk score for a transaction.

    Returns the total score and the ordered list of triggered signal names.
    high_value and near_threshold are mutually exclusive: an amount strictly
    greater than 10000 triggers high_value; an amount in [9000, 10000]
    (inclusive on both ends) triggers near_threshold instead.
    """
    score = Decimal("0")
    signals: list[str] = []

    # amount is assumed to be a numeric-parseable Decimal string, per the
    # upstream validator's guarantee; an unparseable amount raises
    # decimal.InvalidOperation rather than being silently absorbed.
    amount = Decimal(str(txn.get("amount", "0")))
    if amount > HIGH_VALUE_THRESHOLD:
        score += HIGH_VALUE_SCORE
        signals.append("high_value")
    elif NEAR_THRESHOLD_LOW <= amount <= HIGH_VALUE_THRESHOLD:
        score += NEAR_THRESHOLD_SCORE
        signals.append("near_threshold")

    hour = _parse_utc_hour(txn.get("timestamp", ""))
    if hour is not None and 0 <= hour < 5:
        score += UNUSUAL_TIMING_SCORE
        signals.append("unusual_timing")

    if _is_cross_border(txn):
        score += CROSS_BORDER_SCORE
        signals.append("cross_border")

    return score, signals


def process_message(message: dict) -> dict:
    """Score a transaction message for fraud risk and route it accordingly.

    Never mutates the input message's ``data`` dict. Always attaches
    ``risk_score`` (as a string) and ``risk_signals`` to the data. Bands
    (inclusive lower bounds):

    - score >= 0.7: terminal envelope targeted at "results" with
      ``status: "fraud_review"`` and a ``reason`` naming the score and
      signals.
    - 0.3 <= score < 0.7: ``fraud_flag: True``, ``status: "risk_scored"``,
      forwarded to NEXT_AGENT.
    - score < 0.3: ``fraud_flag: False``, ``status: "risk_scored"``,
      forwarded to NEXT_AGENT.
    """
    txn = dict(message.get("data", {}))
    score, signals = risk_score(txn)

    txn["risk_score"] = str(score)
    txn["risk_signals"] = signals

    if score >= FRAUD_REVIEW_THRESHOLD:
        txn["status"] = "fraud_review"
        txn["reason"] = (
            f"risk score {score} triggered fraud review "
            f"(signals: {', '.join(signals)})"
        )
        return create_envelope(AGENT_NAME, "results", txn)

    txn["fraud_flag"] = score >= FRAUD_FLAG_THRESHOLD
    txn["status"] = "risk_scored"
    return create_envelope(AGENT_NAME, NEXT_AGENT, txn)
