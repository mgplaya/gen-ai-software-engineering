"""Settlement processor agent.

Third and terminal stage of the pipeline: computes the settlement fee for a
risk-scored transaction and records the settled amount, then routes the
result to ``results``. Every transaction that reaches this agent has already
passed validation (positive, Decimal-parseable amount) and fraud scoring.
"""

from __future__ import annotations

import sys
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path

if __package__ in (None, ""):
    # Allow running as a plain script (``python agents/settlement_processor.py``)
    # by putting the project root on sys.path so ``pipeline`` resolves.
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from pipeline.message import create_envelope

AGENT_NAME = "settlement_processor"

# 0.1% settlement fee, per the settlement spec.
FEE_RATE = Decimal("0.001")

TWO_PLACES = Decimal("0.01")


def settle(txn: dict) -> dict:
    """Compute the settlement fee and settled amount for a transaction.

    Pure: never mutates the given ``txn`` dict. Returns a new dict (a
    shallow copy of ``txn``) with the following added/overwritten:

    - ``settlement_fee`` (str): ``amount * FEE_RATE``, quantized to 2 decimal
      places with ROUND_HALF_UP.
    - ``settled_amount`` (str): ``amount - settlement_fee``, quantized to 2
      decimal places with ROUND_HALF_UP.
    - ``status``: ``"settled_with_flag"`` if ``txn["fraud_flag"]`` is truthy,
      else ``"settled"``.
    """
    amount = Decimal(str(txn["amount"]))
    fee = (amount * FEE_RATE).quantize(TWO_PLACES, rounding=ROUND_HALF_UP)
    settled_amount = (amount - fee).quantize(TWO_PLACES, rounding=ROUND_HALF_UP)

    result = dict(txn)
    result["settlement_fee"] = str(fee)
    result["settled_amount"] = str(settled_amount)
    result["status"] = "settled_with_flag" if txn.get("fraud_flag") else "settled"

    return result


def process_message(message: dict) -> dict:
    """Settle a risk-scored transaction message and route it to results.

    Never mutates the input message's ``data`` dict. Always returns a
    terminal envelope targeted at ``"results"``: this agent is always the
    last stage of the pipeline.
    """
    settled = settle(message["data"])
    return create_envelope(AGENT_NAME, "results", settled)
