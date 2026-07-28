"""Unit tests for expense_splitter.core — RED phase (TDD).

Tests assert the CORRECT behavior described in the research.
These tests are expected to FAIL against the current buggy code,
reproducing BUG-1 and BUG-2. After the fix (GREEN phase), they must pass.
"""

import pytest
from decimal import Decimal
from expense_splitter.core import split_even, split_weighted


class TestSplitEven:
    """Tests for split_even function — reproduces BUG-1."""

    def test_split_even_sums_to_total(self):
        """BUG-1: Split shares must sum exactly to the total (sum invariant)."""
        total = Decimal("100.00")
        people = 3
        shares = split_even(total, people)
        assert sum(shares) == total, f"Shares {shares} sum to {sum(shares)}, not {total}"

    def test_split_even_divides_100_by_3(self):
        """BUG-1 edge case: 100/3 split distributes remainder cents correctly."""
        total = Decimal("100.00")
        people = 3
        shares = split_even(total, people)
        # Correct split: 33.34, 33.33, 33.33 (or similar distribution)
        # Buggy split: 33.33, 33.33, 33.33 (sums to 99.99)
        assert sum(shares) == Decimal("100.00")
        assert len(shares) == 3
        # Each share should be 2 decimal places
        assert all(str(s).count('.') == 1 and len(str(s).split('.')[-1]) <= 2 for s in shares)

    def test_split_even_with_2_people(self):
        """Split 50.00 between 2 people equals exactly 25.00 each."""
        total = Decimal("50.00")
        people = 2
        shares = split_even(total, people)
        assert sum(shares) == total
        assert shares == [Decimal("25.00"), Decimal("25.00")]

    def test_split_even_with_1_person(self):
        """Split between 1 person returns the full amount."""
        total = Decimal("123.45")
        people = 1
        shares = split_even(total, people)
        assert shares == [total]

    def test_split_even_zero_people_raises(self):
        """Split by zero people raises ValueError."""
        with pytest.raises(ValueError, match="people must be positive"):
            split_even(Decimal("100.00"), 0)

    def test_split_even_negative_people_raises(self):
        """Split by negative people raises ValueError."""
        with pytest.raises(ValueError, match="people must be positive"):
            split_even(Decimal("100.00"), -1)


class TestSplitWeighted:
    """Tests for split_weighted function — reproduces BUG-2."""

    def test_split_weighted_proportional_to_weights(self):
        """BUG-2: Each share equals total * weight / sum(weights)."""
        total = Decimal("90.00")
        weights = [1, 2]
        shares = split_weighted(total, weights)
        # Correct: [30.00, 60.00] (sum = 90.00)
        # Buggy: [45.00, 90.00] (sum = 135.00, uses len(weights)=2 instead of sum(weights)=3)
        expected = [Decimal("30.00"), Decimal("60.00")]
        assert shares == expected, f"Expected {expected}, got {shares}"

    def test_split_weighted_sums_to_total(self):
        """Shares must sum exactly to total."""
        total = Decimal("90.00")
        weights = [1, 2]
        shares = split_weighted(total, weights)
        assert sum(shares) == total

    def test_split_weighted_uniform_weights(self):
        """When all weights are equal, split is even."""
        total = Decimal("100.00")
        weights = [1, 1, 1]
        shares = split_weighted(total, weights)
        # Should split evenly like split_even
        assert sum(shares) == total
        assert len(shares) == 3

    def test_split_weighted_single_weight(self):
        """Single weight gets the entire amount."""
        total = Decimal("100.00")
        weights = [1]
        shares = split_weighted(total, weights)
        assert shares == [total]

    def test_split_weighted_all_zeros_raises(self):
        """All-zero weights should raise ValueError (divide by zero)."""
        total = Decimal("100.00")
        weights = [0, 0, 0]
        with pytest.raises(ValueError, match="weights must sum to a positive value"):
            split_weighted(total, weights)

    def test_split_weighted_empty_raises(self):
        """Empty weights list raises ValueError."""
        total = Decimal("100.00")
        weights = []
        with pytest.raises(ValueError, match="weights must be non-empty"):
            split_weighted(total, weights)

    def test_split_weighted_negative_raises(self):
        """Negative weights raise ValueError."""
        total = Decimal("100.00")
        weights = [1, -1]
        with pytest.raises(ValueError, match="weights must be non-negative"):
            split_weighted(total, weights)

    def test_split_weighted_3_5_2_proportions(self):
        """Weights [3, 5, 2] with total 100 split proportionally."""
        total = Decimal("100.00")
        weights = [3, 5, 2]
        shares = split_weighted(total, weights)
        # sum(weights) = 10
        # shares = [30, 50, 20]
        expected = [Decimal("30.00"), Decimal("50.00"), Decimal("20.00")]
        assert shares == expected
        assert sum(shares) == total
