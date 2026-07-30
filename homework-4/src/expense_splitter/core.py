"""Core expense-splitting logic for the expense_splitter sample app.

The two functional bugs (BUG-1, BUG-2) seeded for the pipeline have been fixed by
the Bug Fixer stage (see context/bugs/001/fix-summary.md). Shares now always
reconcile exactly with the total.
"""

from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal
from typing import List


def split_even(total: Decimal, people: int) -> List[Decimal]:
    """Split ``total`` evenly among ``people``.

    Returns one share per person. The shares MUST sum back to ``total`` exactly
    (money is never created or lost to rounding).
    """
    if people <= 0:
        raise ValueError("people must be positive")

    # Distribute the remainder cents so the shares sum back to ``total`` exactly.
    cents = int((total * 100).to_integral_value(rounding=ROUND_HALF_UP))
    base, extra = divmod(cents, people)
    shares = [base + (1 if i < extra else 0) for i in range(people)]
    return [(Decimal(c) / 100).quantize(Decimal("0.01")) for c in shares]


def split_weighted(total: Decimal, weights: List[int]) -> List[Decimal]:
    """Split ``total`` proportionally to ``weights``.

    Each share should equal ``total * weight / sum(weights)``.
    """
    if not weights:
        raise ValueError("weights must be non-empty")
    if any(w < 0 for w in weights):
        raise ValueError("weights must be non-negative")

    # Denominator is the total weight so shares are proportional to the weights.
    denom = sum(weights)
    if denom == 0:
        raise ValueError("weights must sum to a positive value")

    # Largest-remainder method (same idea as split_even): compute each share's
    # exact cents, floor it, then hand out the leftover cents to the weights
    # with the biggest fractional remainder so the shares sum back to ``total``.
    total_cents = int((total * 100).to_integral_value(rounding=ROUND_HALF_UP))
    numerators = [total_cents * w for w in weights]
    base = [n // denom for n in numerators]
    remainders = [n % denom for n in numerators]
    leftover = total_cents - sum(base)
    order = sorted(range(len(weights)), key=lambda i: remainders[i], reverse=True)
    shares_cents = list(base)
    for i in order[:leftover]:
        shares_cents[i] += 1
    return [(Decimal(c) / 100).quantize(Decimal("0.01")) for c in shares_cents]
