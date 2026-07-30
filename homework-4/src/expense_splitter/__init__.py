"""expense_splitter — split a bill among people, exactly.

Public API:
    split_even(total, people)      -> list[Decimal]
    split_weighted(total, weights) -> list[Decimal]
    parse_amount(text)             -> Decimal
    main(argv=None)                -> int

Money is represented as :class:`decimal.Decimal` values with 2 fractional
digits (cents). Splits are computed so the per-person shares always reconcile
exactly with the input total — no cents are created or lost to rounding.
"""

from .core import split_even, split_weighted
from .cli import main, parse_amount

__all__ = ["split_even", "split_weighted", "parse_amount", "main"]
