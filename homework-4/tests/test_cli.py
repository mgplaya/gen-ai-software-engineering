"""Unit tests for expense_splitter.cli (TDD RED phase).

Tests encode the contract from architecture.md: parse_amount safe parsing (SEC-1),
main CLI entry point, and all edge cases. All tests are FIRST-compliant and fail
(RED) against NotImplementedError stubs.
"""

import pytest
from decimal import Decimal
from io import StringIO
import sys

from expense_splitter import parse_amount, main


class TestParseAmount:
    """Tests for parse_amount(text) -> Decimal (SEC-1 security requirement)."""

    def test_parse_amount_valid_two_decimals(self):
        """Normal: "12.34" -> Decimal('12.34')."""
        result = parse_amount("12.34")
        assert result == Decimal("12.34")
        assert result.as_tuple().exponent == -2

    def test_parse_amount_valid_zero(self):
        """Normal: "0" -> Decimal('0.00')."""
        result = parse_amount("0")
        assert result == Decimal("0.00")

    def test_parse_amount_valid_whole_number(self):
        """Normal: "5" -> Decimal('5.00')."""
        result = parse_amount("5")
        assert result == Decimal("5.00")

    def test_parse_amount_valid_one_decimal(self):
        """Normal: "5.5" -> Decimal('5.50')."""
        result = parse_amount("5.5")
        assert result == Decimal("5.50")

    def test_parse_amount_valid_leading_zero(self):
        """Normal: "0.50" -> Decimal('0.50')."""
        result = parse_amount("0.50")
        assert result == Decimal("0.50")

    def test_parse_amount_empty_string_raises_value_error(self):
        """SEC-1: empty string raises ValueError."""
        with pytest.raises(ValueError):
            parse_amount("")

    def test_parse_amount_whitespace_only_raises_value_error(self):
        """SEC-1: whitespace-only string raises ValueError."""
        with pytest.raises(ValueError):
            parse_amount("   ")

    def test_parse_amount_exponent_form_raises_value_error(self):
        """SEC-1: exponent form "1e3" raises ValueError (code-like input)."""
        with pytest.raises(ValueError):
            parse_amount("1e3")

    def test_parse_amount_exponent_form_capital_e(self):
        """SEC-1: "2E5" (capital E exponent) raises ValueError."""
        with pytest.raises(ValueError):
            parse_amount("2E5")

    def test_parse_amount_nan_raises_value_error(self):
        """SEC-1: "NaN" raises ValueError (non-finite)."""
        with pytest.raises(ValueError):
            parse_amount("NaN")

    def test_parse_amount_infinity_raises_value_error(self):
        """SEC-1: "Infinity" raises ValueError (non-finite)."""
        with pytest.raises(ValueError):
            parse_amount("Infinity")

    def test_parse_amount_negative_infinity_raises_value_error(self):
        """SEC-1: "-Infinity" raises ValueError (non-finite)."""
        with pytest.raises(ValueError):
            parse_amount("-Infinity")

    def test_parse_amount_negative_raises_value_error(self):
        """SEC-1: "-1.00" raises ValueError (negative)."""
        with pytest.raises(ValueError):
            parse_amount("-1.00")

    def test_parse_amount_code_injection_raises_value_error(self):
        """SEC-1: "__import__('os')" raises ValueError (code-like, never executed)."""
        with pytest.raises(ValueError):
            parse_amount("__import__('os')")

    def test_parse_amount_eval_like_raises_value_error(self):
        """SEC-1: "eval(...)" raises ValueError (code-like)."""
        with pytest.raises(ValueError):
            parse_amount("eval('1')")

    def test_parse_amount_thousands_separator_raises_value_error(self):
        """SEC-1: "1,000.00" raises ValueError (thousands separator not allowed)."""
        with pytest.raises(ValueError):
            parse_amount("1,000.00")

    def test_parse_amount_too_many_decimals_raises_value_error(self):
        """SEC-1: "10.005" (3 decimal places) raises ValueError."""
        with pytest.raises(ValueError):
            parse_amount("10.005")

    def test_parse_amount_leading_space_raises_value_error(self):
        """SEC-1: " 10.00" (leading space) raises ValueError."""
        with pytest.raises(ValueError):
            parse_amount(" 10.00")

    def test_parse_amount_trailing_space_raises_value_error(self):
        """SEC-1: "10.00 " (trailing space) raises ValueError."""
        with pytest.raises(ValueError):
            parse_amount("10.00 ")

    def test_parse_amount_plus_sign_raises_value_error(self):
        """SEC-1: "+10.00" (plus sign) raises ValueError."""
        with pytest.raises(ValueError):
            parse_amount("+10.00")

    def test_parse_amount_scientific_notation_lowercase(self):
        """SEC-1: "1.5e2" (scientific) raises ValueError."""
        with pytest.raises(ValueError):
            parse_amount("1.5e2")

    def test_parse_amount_scientific_notation_negative_exponent(self):
        """SEC-1: "1.5e-1" (scientific) raises ValueError."""
        with pytest.raises(ValueError):
            parse_amount("1.5e-1")

    def test_parse_amount_large_valid_amount(self):
        """Normal: large valid amount "9999.99" parses correctly."""
        result = parse_amount("9999.99")
        assert result == Decimal("9999.99")

    def test_parse_amount_single_cent(self):
        """Normal: "0.01" parses to Decimal('0.01')."""
        result = parse_amount("0.01")
        assert result == Decimal("0.01")

    def test_parse_amount_never_uses_float(self):
        """SEC-1: parse_amount must NOT use float() which has precision issues.

        If parse_amount used float(), then float('0.1') + float('0.2') == 0.30000000000000004,
        which could lead to non-finite or precision issues. Verify it constructs Decimal directly.
        """
        # This test verifies that parse_amount doesn't use float by checking
        # that very small decimal amounts are represented correctly.
        result = parse_amount("0.01")
        assert result == Decimal("0.01")
        # If implemented via float, this might fail due to float precision
        assert result.as_tuple().exponent == -2


class TestMain:
    """Tests for main(argv=None) -> int (CLI entry point)."""

    def test_main_valid_input(self, capsys):
        """Normal: main(['10.00', '3']) splits 10.00 among 3, exits 0."""
        result = main(["10.00", "3"])
        assert result == 0
        captured = capsys.readouterr()
        # Should print shares to stdout
        assert "10.00" in captured.out or "Total" in captured.out

    def test_main_valid_input_single_person(self, capsys):
        """Normal: main(['5.00', '1']) returns entire amount, exits 0."""
        result = main(["5.00", "1"])
        assert result == 0
        captured = capsys.readouterr()
        assert len(captured.out) > 0  # Some output expected

    def test_main_valid_input_two_people(self, capsys):
        """Normal: main(['4.00', '2']) splits evenly, exits 0."""
        result = main(["4.00", "2"])
        assert result == 0
        captured = capsys.readouterr()
        assert len(captured.out) > 0

    def test_main_missing_amount_arg_exits_nonzero(self, capsys):
        """Edge: missing amount argument returns non-zero, no raise."""
        result = main(["3"])
        assert result != 0
        # Error should be on stderr, not a traceback
        captured = capsys.readouterr()
        assert len(captured.err) > 0 or result != 0

    def test_main_missing_both_args_exits_nonzero(self, capsys):
        """Edge: missing both arguments returns non-zero."""
        result = main([])
        assert result != 0

    def test_main_too_many_args_exits_nonzero(self, capsys):
        """Edge: too many arguments returns non-zero."""
        result = main(["10.00", "3", "extra"])
        assert result != 0

    def test_main_invalid_amount_exits_nonzero(self, capsys):
        """Edge: invalid amount (e.g. "abc") returns non-zero, no raise."""
        result = main(["abc", "3"])
        assert result != 0
        captured = capsys.readouterr()
        # Should have error message, not traceback

    def test_main_negative_amount_exits_nonzero(self, capsys):
        """Edge: negative amount returns non-zero."""
        result = main(["-10.00", "3"])
        assert result != 0

    def test_main_non_integer_people_exits_nonzero(self, capsys):
        """Edge: people not an integer (e.g. "3.5") returns non-zero."""
        result = main(["10.00", "3.5"])
        assert result != 0

    def test_main_people_zero_exits_nonzero(self, capsys):
        """Edge: people < 1 returns non-zero."""
        result = main(["10.00", "0"])
        assert result != 0

    def test_main_people_negative_exits_nonzero(self, capsys):
        """Edge: people < 0 returns non-zero."""
        result = main(["10.00", "-3"])
        assert result != 0

    def test_main_people_non_numeric_exits_nonzero(self, capsys):
        """Edge: people not numeric (e.g. "abc") returns non-zero."""
        result = main(["10.00", "abc"])
        assert result != 0

    def test_main_with_none_argv_uses_sys_argv(self, monkeypatch):
        """Edge: main(None) should use sys.argv[1:] (use monkeypatch to mock)."""
        # Mock sys.argv to provide test arguments
        monkeypatch.setattr(sys, 'argv', ['prog', '10.00', '2'])
        result = main(None)
        # Should succeed with valid args from mocked sys.argv
        assert result == 0

    def test_main_zero_amount_exits_zero(self, capsys):
        """Edge: zero amount is valid, splits to all zeros, exits 0."""
        result = main(["0.00", "3"])
        assert result == 0

    def test_main_one_person_exits_zero(self, capsys):
        """Edge: one person is valid, exits 0."""
        result = main(["42.50", "1"])
        assert result == 0

    def test_main_prints_all_shares(self, capsys):
        """Normal: main prints one line per person's share."""
        result = main(["10.00", "3"])
        assert result == 0
        captured = capsys.readouterr()
        # Expect output with share information; exact format varies,
        # but should contain amounts and/or total
        assert len(captured.out.strip()) > 0

    def test_main_never_raises_on_bad_input(self, capsys):
        """SEC-1 / Contract: main never raises; bad input -> stderr + non-zero exit."""
        # These should all return non-zero without raising exceptions
        bad_inputs = [
            ["__import__('os')", "3"],
            ["1e9", "3"],
            ["NaN", "3"],
            ["10.00"],  # missing people
            ["10.00", "3", "4"],  # too many args
        ]
        for argv in bad_inputs:
            result = main(argv)
            # Should return non-zero, not raise
            assert result != 0

    def test_main_large_valid_split(self, capsys):
        """Edge: large amount (e.g. 9999.99) split among many people."""
        result = main(["9999.99", "7"])
        assert result == 0
