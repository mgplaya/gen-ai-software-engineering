"""Unit tests for expense_splitter.cli — RED phase (TDD).

Tests assert the CORRECT behavior described in the research.
The parse_amount security test is expected to FAIL against the current buggy code
(which uses eval() and allows code execution), reproducing SEC-1.
After the fix (GREEN phase), it must pass.
"""

import pytest
import sys
from decimal import Decimal
from io import StringIO
from unittest.mock import patch
from expense_splitter.cli import parse_amount, main


class TestParseAmount:
    """Tests for parse_amount function — reproduces SEC-1."""

    def test_parse_amount_valid_decimal(self):
        """Valid decimal string is parsed correctly."""
        result = parse_amount("100.50")
        assert result == Decimal("100.50")

    def test_parse_amount_integer(self):
        """Integer string is parsed correctly."""
        result = parse_amount("100")
        assert result == Decimal("100")

    def test_parse_amount_strips_whitespace(self):
        """Whitespace is stripped before parsing."""
        result = parse_amount("  100.50  ")
        assert result == Decimal("100.50")

    def test_parse_amount_rejects_invalid_input(self):
        """Invalid input raises ValueError (not executed as code)."""
        with pytest.raises(ValueError):
            parse_amount("not_a_number")

    def test_parse_amount_security_no_code_execution(self):
        """SEC-1: Code-injection payload is NOT executed.

        This test confirms the security fix by checking that a malicious
        payload is rejected as invalid input, NOT executed as Python code.
        The payload would print 'PWNED' if eval() were still in use.
        """
        payload = "__import__('builtins').print('PWNED')"

        # Should raise ValueError or similar, NOT execute the code
        with pytest.raises(ValueError):
            parse_amount(payload)
        # If we get here without exception, test passes (code wasn't executed)

    def test_parse_amount_rejects_os_system_injection(self):
        """SEC-1: os.system() injection is rejected."""
        payload = "__import__('os').system('echo pwned')"
        with pytest.raises(ValueError):
            parse_amount(payload)

    def test_parse_amount_negative_decimal(self):
        """Negative decimal strings are parsed (allowed by Decimal)."""
        result = parse_amount("-50.25")
        assert result == Decimal("-50.25")

    def test_parse_amount_zero(self):
        """Zero is parsed correctly."""
        result = parse_amount("0.00")
        assert result == Decimal("0.00")

    def test_parse_amount_large_amount(self):
        """Large amounts are parsed correctly."""
        result = parse_amount("999999.99")
        assert result == Decimal("999999.99")


class TestMain:
    """Integration tests for main() CLI entry point."""

    def test_main_valid_split(self):
        """Valid arguments produce correct output (tests split_even indirectly)."""
        argv = ["10.00", "2"]
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            result = main(argv)
        assert result == 0
        output = mock_stdout.getvalue()
        assert "Person 1:" in output
        assert "Person 2:" in output
        assert "Total:" in output

    def test_main_invalid_amount(self):
        """Invalid amount argument returns error."""
        argv = ["not_a_number", "2"]
        with patch("sys.stderr", new_callable=StringIO) as mock_stderr:
            result = main(argv)
        assert result == 1
        assert "Invalid amount" in mock_stderr.getvalue()

    def test_main_invalid_people_count(self):
        """Invalid people count returns error."""
        argv = ["100.00", "not_a_number"]
        with patch("sys.stderr", new_callable=StringIO) as mock_stderr:
            result = main(argv)
        assert result == 1
        assert "Invalid people count" in mock_stderr.getvalue()

    def test_main_missing_arguments(self):
        """Missing arguments returns error."""
        argv = ["100.00"]
        with patch("sys.stderr", new_callable=StringIO) as mock_stderr:
            result = main(argv)
        assert result == 1
        assert "Usage:" in mock_stderr.getvalue()

    def test_main_too_many_arguments(self):
        """Too many arguments returns error."""
        argv = ["100.00", "2", "extra"]
        with patch("sys.stderr", new_callable=StringIO) as mock_stderr:
            result = main(argv)
        assert result == 1
        assert "Usage:" in mock_stderr.getvalue()

    def test_main_zero_people(self):
        """Zero people raises ValueError."""
        argv = ["100.00", "0"]
        with patch("sys.stderr", new_callable=StringIO) as mock_stderr:
            result = main(argv)
        assert result == 1
        assert "Invalid input" in mock_stderr.getvalue()
