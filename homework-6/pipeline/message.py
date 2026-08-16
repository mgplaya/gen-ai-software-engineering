"""Standard message envelope used for all inter-agent communication.

Every agent in the pipeline exchanges messages wrapped in this envelope so
that routing, tracing, and validation stay consistent across the whole
system.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

REQUIRED_FIELDS = (
    "message_id",
    "timestamp",
    "source_agent",
    "target_agent",
    "message_type",
    "data",
)


def utc_now_iso() -> str:
    """Return the current UTC time as an ISO 8601 string, e.g. ``2026-03-16T10:00:00Z``.

    This is the single source of truth for timestamp formatting: every
    module that needs "now" as a string should call this instead of
    formatting a timestamp itself.
    """
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def create_envelope(
    source_agent: str,
    target_agent: str,
    data: dict,
    message_type: str = "transaction",
) -> dict:
    """Build a standard message envelope.

    Args:
        source_agent: Name of the agent sending the message.
        target_agent: Name of the agent the message is addressed to.
        data: Payload dict carried by the message.
        message_type: Category of message, defaults to "transaction".

    Returns:
        A dict with exactly the six envelope fields: message_id, timestamp,
        source_agent, target_agent, message_type, data.
    """
    return {
        "message_id": str(uuid.uuid4()),
        "timestamp": utc_now_iso(),
        "source_agent": source_agent,
        "target_agent": target_agent,
        "message_type": message_type,
        "data": data,
    }


def validate_envelope(envelope) -> list[str]:
    """Validate a message envelope.

    Args:
        envelope: The value to validate as an envelope.

    Returns:
        A list of human-readable error strings. An empty list means the
        envelope is valid.
    """
    if not isinstance(envelope, dict):
        return ["envelope must be a dict"]

    errors: list[str] = []

    for field in REQUIRED_FIELDS:
        if field not in envelope:
            errors.append(f"missing required field: {field}")

    if "data" in envelope and not isinstance(envelope["data"], dict):
        errors.append("data must be a dict")

    return errors
