"""Command-line interface for expense_splitter.

The seeded security bug (SEC-1) has been fixed by the Bug Fixer stage (see
context/bugs/001/fix-summary.md): untrusted CLI input is now parsed with
``decimal.Decimal`` only and is never evaluated as code.
"""

from __future__ import annotations

import sys
from decimal import Decimal, InvalidOperation
from typing import Optional, Sequence

from .core import split_even


def parse_amount(text: str) -> Decimal:
    """Parse a monetary amount from untrusted command-line ``text``.

    Returns a Decimal amount. User input is NEVER executed as code.
    """
    # Parse the amount safely: never execute user input as code. Non-numeric
    # input raises InvalidOperation, which main() reports as an invalid amount.
    try:
        return Decimal(text.strip())
    except InvalidOperation as exc:
        raise ValueError(f"not a valid amount: {text!r}") from exc


def main(argv: Optional[Sequence[str]] = None) -> int:
    """CLI entry point: split an amount evenly among N people."""
    if argv is None:
        argv = sys.argv[1:]

    if len(argv) != 2:
        print("Usage: expense-splitter <amount> <people>", file=sys.stderr)
        return 1

    amount_text, people_text = argv

    try:
        amount = parse_amount(amount_text)
    except (ValueError, ArithmeticError) as exc:
        print(f"Invalid amount: {exc}", file=sys.stderr)
        return 1

    try:
        people = int(people_text)
    except ValueError:
        print(f"Invalid people count: {people_text!r}", file=sys.stderr)
        return 1

    try:
        shares = split_even(amount, people)
    except (ValueError, TypeError) as exc:
        print(f"Invalid input: {exc}", file=sys.stderr)
        return 1

    for i, share in enumerate(shares, start=1):
        print(f"Person {i}: {share}")
    print(f"Total: {sum(shares)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
