"""Command-line interface for expense_splitter.

Parses an amount and a number of people from untrusted CLI input and prints
each person's share plus the reconciled total. Amount parsing is done with
:class:`decimal.Decimal` only — user input is NEVER evaluated as code.
"""

from __future__ import annotations

import re
import sys
from decimal import Decimal, InvalidOperation
from typing import Sequence

from .core import split_even

_AMOUNT_RE = re.compile(r"^\d+(\.\d{1,2})?$")


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
    if not _AMOUNT_RE.match(text):
        raise ValueError(f"invalid amount: {text!r}")
    try:
        amount = Decimal(text)
    except InvalidOperation as exc:
        raise ValueError(f"invalid amount: {text!r}") from exc
    return amount.quantize(Decimal("0.01"))


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
    if argv is None:
        argv = sys.argv[1:]

    if len(argv) != 2:
        print("usage: expense-splitter <amount> <people>", file=sys.stderr)
        return 1

    amount_text, people_text = argv

    try:
        amount = parse_amount(amount_text)
    except ValueError as exc:
        print(f"invalid amount: {exc}", file=sys.stderr)
        return 1

    if not re.match(r"^-?\d+$", people_text):
        print(f"invalid people count: {people_text!r}", file=sys.stderr)
        return 1
    people = int(people_text)

    try:
        shares = split_even(amount, people)
    except ValueError as exc:
        print(f"invalid people count: {exc}", file=sys.stderr)
        return 1

    for i, share in enumerate(shares, start=1):
        print(f"Person {i}: {share}")
    print(f"Total: {sum(shares)}")
    return 0
