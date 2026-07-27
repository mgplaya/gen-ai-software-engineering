"""Unit tests for expense_splitter.core (TDD RED phase).

Tests encode the contract from architecture.md: reconciliation invariant,
even fairness, weighted proportionality, edge cases, and type validation.
All tests are FIRST-compliant and fail (RED) against NotImplementedError stubs.
"""

import pytest
from decimal import Decimal

from expense_splitter import split_even, split_weighted


class TestSplitEven:
    """Tests for split_even(total, people) -> list[Decimal]."""

    def test_split_even_normal_case(self):
        """Normal: 10.00 split evenly among 3 people."""
        result = split_even(Decimal("10.00"), 3)
        assert len(result) == 3
        assert sum(result) == Decimal("10.00")
        # Shares differ by at most 1 cent; largest first (non-increasing)
        assert result[0] >= result[1]
        assert result[1] >= result[2]
        # Each share is a Decimal with 2 fractional digits
        for share in result:
            assert isinstance(share, Decimal)
            assert share.as_tuple().exponent == -2

    def test_split_even_single_person(self):
        """Edge: people=1 -> share equals total."""
        total = Decimal("42.50")
        result = split_even(total, 1)
        assert len(result) == 1
        assert result[0] == total

    def test_split_even_total_zero(self):
        """Edge: total=0 -> all shares are 0.00."""
        result = split_even(Decimal("0.00"), 5)
        assert len(result) == 5
        assert all(share == Decimal("0.00") for share in result)
        assert sum(result) == Decimal("0.00")

    def test_split_even_not_divisible(self):
        """Edge: 10.00 / 3 with remainder; leftover cents to earliest."""
        result = split_even(Decimal("10.00"), 3)
        # 10.00 / 3 = 3.33... -> 3.34, 3.33, 3.33 (total = 10.00)
        assert len(result) == 3
        assert sum(result) == Decimal("10.00")
        assert result[0] == Decimal("3.34")
        assert result[1] == Decimal("3.33")
        assert result[2] == Decimal("3.33")

    def test_split_even_two_people_odd_cents(self):
        """Edge: 5.01 / 2 -> 2.51, 2.50 (leftover to earliest)."""
        result = split_even(Decimal("5.01"), 2)
        assert len(result) == 2
        assert sum(result) == Decimal("5.01")
        assert result[0] == Decimal("2.51")
        assert result[1] == Decimal("2.50")

    def test_split_even_people_zero_raises_value_error(self):
        """Edge: people < 1 raises ValueError."""
        with pytest.raises(ValueError):
            split_even(Decimal("10.00"), 0)

    def test_split_even_people_negative_raises_value_error(self):
        """Edge: people < 0 raises ValueError."""
        with pytest.raises(ValueError):
            split_even(Decimal("10.00"), -5)

    def test_split_even_total_negative_raises_value_error(self):
        """Edge: total < 0 raises ValueError."""
        with pytest.raises(ValueError):
            split_even(Decimal("-5.00"), 3)

    def test_split_even_total_too_many_decimals_raises_value_error(self):
        """Edge: total with >2 fractional digits raises ValueError."""
        with pytest.raises(ValueError):
            split_even(Decimal("10.005"), 3)

    def test_split_even_total_not_decimal_raises_type_error(self):
        """Edge: total not a Decimal raises TypeError."""
        with pytest.raises(TypeError):
            split_even(10.0, 3)

    def test_split_even_people_not_int_raises_type_error(self):
        """Edge: people not an int raises TypeError."""
        with pytest.raises(TypeError):
            split_even(Decimal("10.00"), 3.5)

    def test_split_even_large_amount(self):
        """Edge: large amount (e.g. 9999.99) splits correctly."""
        result = split_even(Decimal("9999.99"), 7)
        assert len(result) == 7
        assert sum(result) == Decimal("9999.99")

    def test_split_even_one_cent(self):
        """Edge: total=0.01 split among 3 -> only first person gets it."""
        result = split_even(Decimal("0.01"), 3)
        assert len(result) == 3
        assert sum(result) == Decimal("0.01")
        assert result[0] == Decimal("0.01")
        assert result[1] == Decimal("0.00")
        assert result[2] == Decimal("0.00")


class TestSplitWeighted:
    """Tests for split_weighted(total, weights) -> list[Decimal]."""

    def test_split_weighted_normal_case(self):
        """Normal: 10.00 split by weights 1:2:3."""
        weights = [Decimal("1"), Decimal("2"), Decimal("3")]
        result = split_weighted(Decimal("10.00"), weights)
        assert len(result) == 3
        assert sum(result) == Decimal("10.00")
        # Each share is a Decimal with 2 fractional digits
        for share in result:
            assert isinstance(share, Decimal)
            assert share.as_tuple().exponent == -2

    def test_split_weighted_proportional(self):
        """Normal: verify shares are proportional to weights."""
        # 10.00 split by 1:2 -> approx 3.33:6.67, but exact cents matter
        weights = [Decimal("1"), Decimal("2")]
        result = split_weighted(Decimal("10.00"), weights)
        assert len(result) == 2
        assert sum(result) == Decimal("10.00")
        # First share should be less than second (1 < 2)
        assert result[0] < result[1]

    def test_split_weighted_single_weight(self):
        """Edge: single weight -> entire amount to one person."""
        result = split_weighted(Decimal("42.50"), [Decimal("1")])
        assert len(result) == 1
        assert result[0] == Decimal("42.50")

    def test_split_weighted_total_zero(self):
        """Edge: total=0 -> all shares are 0.00."""
        result = split_weighted(Decimal("0.00"), [Decimal("1"), Decimal("2"), Decimal("3")])
        assert len(result) == 3
        assert all(share == Decimal("0.00") for share in result)

    def test_split_weighted_zero_weight_allowed(self):
        """Edge: individual zero weight is allowed if sum > 0."""
        weights = [Decimal("0"), Decimal("1"), Decimal("1")]
        result = split_weighted(Decimal("10.00"), weights)
        assert len(result) == 3
        assert sum(result) == Decimal("10.00")
        assert result[0] == Decimal("0.00")

    def test_split_weighted_int_weights(self):
        """Edge: weights can be ints, not just Decimals."""
        result = split_weighted(Decimal("10.00"), [1, 2, 3])
        assert len(result) == 3
        assert sum(result) == Decimal("10.00")

    def test_split_weighted_mixed_weights(self):
        """Edge: weights can be mixed int and Decimal."""
        result = split_weighted(Decimal("10.00"), [1, Decimal("2"), 3])
        assert len(result) == 3
        assert sum(result) == Decimal("10.00")

    def test_split_weighted_largest_remainder(self):
        """Normal: largest remainder method distributes leftover cents."""
        # 10.00 / 3 equal weights -> 3.33 each, 1 cent leftover to largest remainder
        weights = [Decimal("1"), Decimal("1"), Decimal("1")]
        result = split_weighted(Decimal("10.00"), weights)
        assert len(result) == 3
        assert sum(result) == Decimal("10.00")
        # At least one person gets 3.34 (the extra cent)
        assert Decimal("3.34") in result

    def test_split_weighted_empty_weights_raises_value_error(self):
        """Edge: empty weights raises ValueError."""
        with pytest.raises(ValueError):
            split_weighted(Decimal("10.00"), [])

    def test_split_weighted_all_zero_weights_raises_value_error(self):
        """Edge: all weights zero raises ValueError (sum is 0)."""
        with pytest.raises(ValueError):
            split_weighted(Decimal("10.00"), [Decimal("0"), Decimal("0")])

    def test_split_weighted_negative_weight_raises_value_error(self):
        """Edge: negative weight raises ValueError."""
        with pytest.raises(ValueError):
            split_weighted(Decimal("10.00"), [Decimal("1"), Decimal("-1")])

    def test_split_weighted_total_negative_raises_value_error(self):
        """Edge: total < 0 raises ValueError."""
        with pytest.raises(ValueError):
            split_weighted(Decimal("-5.00"), [Decimal("1"), Decimal("2")])

    def test_split_weighted_total_too_many_decimals_raises_value_error(self):
        """Edge: total with >2 fractional digits raises ValueError."""
        with pytest.raises(ValueError):
            split_weighted(Decimal("10.005"), [Decimal("1")])

    def test_split_weighted_total_not_decimal_raises_type_error(self):
        """Edge: total not a Decimal raises TypeError."""
        with pytest.raises(TypeError):
            split_weighted(10.0, [Decimal("1")])

    def test_split_weighted_bad_weight_type_raises_type_error(self):
        """Edge: weight not int or Decimal raises TypeError."""
        with pytest.raises(TypeError):
            split_weighted(Decimal("10.00"), [Decimal("1"), "2", Decimal("3")])

    def test_split_weighted_large_weights(self):
        """Edge: large weight values (e.g. 1000:2000) reconcile exactly."""
        result = split_weighted(Decimal("10.00"), [1000, 2000])
        assert len(result) == 2
        assert sum(result) == Decimal("10.00")

    def test_split_weighted_unequal_split(self):
        """Normal: verify unequal split (e.g. 1:3 ratio)."""
        weights = [Decimal("1"), Decimal("3")]
        result = split_weighted(Decimal("4.00"), weights)
        assert len(result) == 2
        assert sum(result) == Decimal("4.00")
        # Approx 1:3 ratio (1.00, 3.00 or close due to Decimal arithmetic)
        assert result[1] > result[0]
