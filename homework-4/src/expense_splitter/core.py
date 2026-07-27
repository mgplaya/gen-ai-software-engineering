"""Core splitting logic for expense_splitter.

All amounts are :class:`decimal.Decimal` values quantized to 2 fractional
digits (cents). The invariant every function here must preserve is that the
returned shares sum *exactly* to the input total.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Sequence


def split_even(total: Decimal, people: int) -> list[Decimal]:
    """Split ``total`` evenly among ``people`` people.

    Returns a list of ``people`` share amounts, each a Decimal quantized to
    2 fractional digits (cents). The shares MUST sum exactly to ``total``.
    When ``total`` does not divide evenly into whole cents, the leftover
    cents are distributed one-per-person to the earliest people, so the
    largest shares come first and no cent is created or lost.

    Args:
        total: The bill amount. Must be a non-negative Decimal with at most
            2 fractional digits.
        people: The number of people to split among. Must be an integer >= 1.

    Returns:
        A list of length ``people`` of Decimal shares summing to ``total``.

    Raises:
        ValueError: If ``people`` < 1, if ``total`` is negative, or if
            ``total`` has more than 2 fractional digits.
        TypeError: If ``total`` is not a Decimal or ``people`` is not an int.
    """
    raise NotImplementedError("split_even")


def split_weighted(total: Decimal, weights: Sequence[Decimal | int]) -> list[Decimal]:
    """Split ``total`` among people in proportion to ``weights``.

    Each person's share is proportional to their weight relative to the sum
    of all weights. Shares are quantized to 2 fractional digits (cents) and
    MUST sum exactly to ``total``: any leftover cents from rounding are
    distributed to the people with the largest fractional remainders (ties
    broken by earliest index), so the result reconciles exactly.

    Args:
        total: The bill amount. Must be a non-negative Decimal with at most
            2 fractional digits.
        weights: A non-empty sequence of positive weights (int or Decimal).
            The sum of weights must be > 0.

    Returns:
        A list, the same length as ``weights``, of Decimal shares summing to
        ``total``.

    Raises:
        ValueError: If ``weights`` is empty, if any weight is negative, if the
            weights sum to 0, or if ``total`` is negative / has more than 2
            fractional digits.
        TypeError: If ``total`` is not a Decimal or a weight is not int/Decimal.
    """
    raise NotImplementedError("split_weighted")
