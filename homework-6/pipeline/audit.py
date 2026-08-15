"""Audit logging with PII masking.

Every agent in the pipeline that needs to record an audit trail entry goes
through this module. Entries are intentionally narrow — timestamp, agent
name, transaction ID, outcome — so that account numbers and free-text
descriptions can never end up in the audit log.
"""

from __future__ import annotations

import json
from pathlib import Path

from pipeline.message import utc_now_iso

ACCOUNT_PREFIX = "ACC-"
MASK = "****"


def mask_account(account: str) -> str:
    """Mask an account number for safe display/logging.

    Keeps an ``ACC-`` prefix when present, replaces the middle with ``****``,
    and keeps the last two characters of the account body, e.g.
    ``"ACC-1001"`` -> ``"ACC-****01"``.

    Degrades safely (returns ``"****"``) for empty or falsy values, and for
    values whose body (after stripping any ``ACC-`` prefix) is two characters
    or shorter. Never raises.

    Args:
        account: The account number to mask.

    Returns:
        The masked account string.
    """
    if not account:
        return MASK

    prefix = ""
    body = account
    if body.startswith(ACCOUNT_PREFIX):
        prefix = ACCOUNT_PREFIX
        body = body[len(ACCOUNT_PREFIX):]

    if len(body) <= 2:
        return MASK

    return f"{prefix}{MASK}{body[-2:]}"


def log_event(base_dir: Path, agent: str, transaction_id: str, outcome: str) -> dict:
    """Append one audit entry as a JSON line to ``base_dir / 'audit.log'``.

    The entry has exactly four fields: timestamp (from ``utc_now_iso``),
    agent, transaction_id, outcome. Account numbers and free-text
    descriptions must never be passed in here; the schema has no field for
    them.

    Args:
        base_dir: Directory containing (or to contain) ``audit.log``.
        agent: Name of the agent recording the event.
        transaction_id: Identifier of the transaction being audited.
        outcome: Outcome label for the event (e.g. "approved", "rejected").

    Returns:
        The entry dict that was appended to the log.
    """
    entry = {
        "timestamp": utc_now_iso(),
        "agent": agent,
        "transaction_id": transaction_id,
        "outcome": outcome,
    }

    log_path = base_dir / "audit.log"
    with log_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")

    return entry
