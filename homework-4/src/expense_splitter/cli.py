"""Command-line interface for expense_splitter.

Parses an amount and a number of people from untrusted CLI input and prints
each person's share plus the reconciled total. Amount parsing is done with
:class:`decimal.Decimal` only — user input is NEVER evaluated as code.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Sequence


def parse_amount(text: str) -> Decimal:
    """Safely parse a monetary amount from untrusted text.

    Converts ``text`` to a Decimal quantized to 2 fractional digits. Parsing
    uses :class:`decimal.Decimal` construction only — it MUST NOT use
    ``eval``, ``exec``, ``float()`` of unbounded precision, or any mechanism
    that could execute ``text`` as code. Rejects anything that is not a plain
    decimal number (e.g. ``"1e9"`` exponent forms, ``NaN``, ``Infinity``,
    code-like input, empty/whitespace, or negative values).

    Args:
        text: Raw amount string from the command line (untrusted).

    Returns:
        A non-negative Decimal with exactly 2 fractional digits.

    Raises:
        ValueError: If ``text`` is not a well-formed, finite, non-negative
            decimal amount with at most 2 fractional digits.
    """
    raise NotImplementedError("parse_amount")


def main(argv: Sequence[str] | None = None) -> int:
    """CLI entry point: split an amount evenly among N people.

    Usage: ``expense-splitter <amount> <people>``. Parses ``amount`` via
    :func:`parse_amount`, ``people`` as a positive int, computes the even
    split via :func:`expense_splitter.core.split_even`, prints one line per
    person's share followed by the reconciled total, and returns an exit code.

    Args:
        argv: Argument vector excluding the program name. Defaults to
            ``sys.argv[1:]`` when ``None``.

    Returns:
        Process exit code: ``0`` on success, non-zero on a usage or input
        error (invalid amount, invalid people count). Never raises on bad
        user input — errors are reported to stderr and mapped to an exit code.
    """
    raise NotImplementedError("main")
