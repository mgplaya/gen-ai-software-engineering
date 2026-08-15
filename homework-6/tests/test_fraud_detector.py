from decimal import Decimal

from agents.fraud_detector import (
    AGENT_NAME,
    CURRENCY_HOME_COUNTRIES,
    NEXT_AGENT,
    process_message,
    risk_score,
)
from pipeline.message import create_envelope

VALID_TXN = {
    "transaction_id": "TXN001",
    "timestamp": "2026-03-16T09:00:00Z",
    "source_account": "ACC-1001",
    "destination_account": "ACC-2001",
    "amount": "1500.00",
    "currency": "USD",
    "transaction_type": "transfer",
    "description": "Monthly rent payment",
    "metadata": {"channel": "online", "country": "US"},
    "status": "validated",
}


def _txn(**overrides):
    txn = dict(VALID_TXN)
    txn.update(overrides)
    return txn


def _envelope(**overrides):
    return create_envelope(
        source_agent="transaction_validator",
        target_agent="fraud_detector",
        data=_txn(**overrides),
    )


def test_constants_match_spec():
    assert AGENT_NAME == "fraud_detector"
    assert NEXT_AGENT == "settlement_processor"


def test_currency_home_countries_cover_required_currencies():
    assert CURRENCY_HOME_COUNTRIES["USD"] == {"US"}
    assert CURRENCY_HOME_COUNTRIES["GBP"] == {"GB"}
    assert CURRENCY_HOME_COUNTRIES["JPY"] == {"JP"}
    assert CURRENCY_HOME_COUNTRIES["CHF"] == {"CH"}
    assert CURRENCY_HOME_COUNTRIES["CAD"] == {"CA"}
    assert CURRENCY_HOME_COUNTRIES["AUD"] == {"AU"}
    eu_members = {"DE", "FR", "ES", "IT", "NL", "AT", "BE", "FI", "IE", "PT", "GR"}
    assert eu_members <= CURRENCY_HOME_COUNTRIES["EUR"]


# --- Signals in isolation -----------------------------------------------


def test_risk_score_no_signals_for_clean_transaction():
    score, signals = risk_score(_txn())

    assert score == Decimal("0")
    assert signals == []


def test_risk_score_high_value_signal():
    score, signals = risk_score(_txn(amount="10000.01"))

    assert score == Decimal("0.4")
    assert signals == ["high_value"]


def test_risk_score_near_threshold_signal():
    score, signals = risk_score(_txn(amount="9500.00"))

    assert score == Decimal("0.2")
    assert signals == ["near_threshold"]


def test_risk_score_unusual_timing_signal():
    score, signals = risk_score(_txn(timestamp="2026-03-16T02:00:00Z"))

    assert score == Decimal("0.3")
    assert signals == ["unusual_timing"]


def test_risk_score_cross_border_signal():
    score, signals = risk_score(
        _txn(currency="USD", metadata={"channel": "online", "country": "FR"})
    )

    assert score == Decimal("0.2")
    assert signals == ["cross_border"]


def test_risk_score_cross_border_when_country_missing_from_metadata():
    score, signals = risk_score(_txn(currency="USD", metadata={"channel": "online"}))

    assert score == Decimal("0.2")
    assert signals == ["cross_border"]


# --- Boundaries -----------------------------------------------------------


def test_risk_score_amount_exactly_10000_is_near_threshold_not_high_value():
    score, signals = risk_score(_txn(amount="10000.00"))

    assert score == Decimal("0.2")
    assert signals == ["near_threshold"]


def test_risk_score_amount_exactly_9000_is_near_threshold():
    score, signals = risk_score(_txn(amount="9000.00"))

    assert score == Decimal("0.2")
    assert signals == ["near_threshold"]


def test_risk_score_amount_just_above_10000_is_high_value_only():
    score, signals = risk_score(_txn(amount="10000.01"))

    assert "near_threshold" not in signals
    assert "high_value" in signals


def test_risk_score_timestamp_exactly_05_00_has_no_timing_signal():
    score, signals = risk_score(_txn(timestamp="2026-03-16T05:00:00Z"))

    assert "unusual_timing" not in signals
    assert score == Decimal("0")


def test_risk_score_timestamp_04_59_has_timing_signal():
    score, signals = risk_score(_txn(timestamp="2026-03-16T04:59:00Z"))

    assert "unusual_timing" in signals


def test_risk_score_non_z_offset_local_hour_in_window_but_utc_hour_is_not():
    # 02:00 at +05:00 is 21:00 UTC the previous day -- outside [0, 5), so
    # unusual_timing must NOT fire even though the local hour (2) is inside
    # the window. This guards against using the local hour instead of the
    # UTC hour.
    score, signals = risk_score(_txn(timestamp="2026-03-16T02:00:00+05:00"))

    assert "unusual_timing" not in signals
    assert score == Decimal("0")


def test_risk_score_non_z_offset_utc_hour_in_window():
    # 08:00 at +05:00 is 03:00 UTC, inside [0, 5), so unusual_timing must
    # fire based on the UTC hour even though the local hour (8) is outside
    # the window.
    score, signals = risk_score(_txn(timestamp="2026-03-16T08:00:00+05:00"))

    assert "unusual_timing" in signals
    assert score == Decimal("0.3")


def test_risk_score_eur_from_de_is_not_cross_border():
    score, signals = risk_score(
        _txn(currency="EUR", metadata={"channel": "online", "country": "DE"})
    )

    assert score == Decimal("0")
    assert "cross_border" not in signals


# --- Stacked signals --------------------------------------------------------


def test_risk_score_stacked_signals_high_value_night_cross_border():
    score, signals = risk_score(
        _txn(
            amount="15000.00",
            timestamp="2026-03-16T02:00:00Z",
            currency="USD",
            metadata={"channel": "online", "country": "FR"},
        )
    )

    assert score == Decimal("0.9")
    assert set(signals) == {"high_value", "unusual_timing", "cross_border"}


# --- process_message bands --------------------------------------------------


def test_process_message_clean_transaction_forwarded_with_flag_false():
    message = _envelope()

    result = process_message(message)

    assert result["target_agent"] == "settlement_processor"
    assert result["data"]["status"] == "risk_scored"
    assert result["data"]["fraud_flag"] is False
    assert result["data"]["risk_score"] == "0"
    assert result["data"]["risk_signals"] == []


def test_process_message_band_boundary_score_exactly_0_3_is_flagged_and_forwarded():
    # unusual_timing alone contributes exactly 0.3, giving a score of exactly
    # 0.3 with no other signals in play.
    message = _envelope(timestamp="2026-03-16T02:00:00Z")

    result = process_message(message)

    assert result["data"]["risk_score"] == "0.3"
    assert result["target_agent"] == "settlement_processor"
    assert result["data"]["status"] == "risk_scored"
    assert result["data"]["fraud_flag"] is True


def test_process_message_band_boundary_score_exactly_0_7_is_rejected():
    # near_threshold (0.2) + unusual_timing (0.3) + cross_border (0.2) = 0.7
    message = _envelope(
        amount="9500.00",
        timestamp="2026-03-16T02:00:00Z",
        currency="USD",
        metadata={"channel": "online", "country": "FR"},
    )

    result = process_message(message)

    assert result["data"]["risk_score"] == "0.7"
    assert result["target_agent"] == "results"
    assert result["data"]["status"] == "fraud_review"
    assert "reason" in result["data"]
    assert "0.7" in result["data"]["reason"]


def test_process_message_below_0_3_is_clean_and_forwarded():
    message = _envelope(amount="500.00")

    result = process_message(message)

    assert result["data"]["fraud_flag"] is False
    assert result["data"]["status"] == "risk_scored"
    assert result["target_agent"] == "settlement_processor"


def test_process_message_stacked_signals_score_0_9_is_rejected():
    message = _envelope(
        amount="15000.00",
        timestamp="2026-03-16T02:00:00Z",
        currency="USD",
        metadata={"channel": "online", "country": "FR"},
    )

    result = process_message(message)

    assert result["data"]["risk_score"] == "0.9"
    assert result["target_agent"] == "results"
    assert result["data"]["status"] == "fraud_review"
    assert set(result["data"]["risk_signals"]) == {
        "high_value",
        "unusual_timing",
        "cross_border",
    }


def test_process_message_never_mutates_input_data_dict():
    original_data = _txn()
    message = create_envelope(
        source_agent="transaction_validator",
        target_agent="fraud_detector",
        data=original_data,
    )

    process_message(message)

    assert "risk_score" not in original_data
    assert "risk_signals" not in original_data
    assert "fraud_flag" not in original_data
    assert message["data"] is original_data
