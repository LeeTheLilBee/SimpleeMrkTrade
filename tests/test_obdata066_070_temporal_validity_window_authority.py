from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import pytest

from web.ob_observation_temporal_validity import (
    MarketSession,
    TemporalReasoningEligibility,
    TemporalValidityState,
    assess_temporal_validity,
    blocked_by_temporal_authority,
    build_temporal_validity_window,
    eligible_for_current_temporal_reasoning,
    temporal_validity_snapshot,
)


ROOT = Path(__file__).resolve().parents[1]


DAY = date(2026, 9, 14)

START = datetime(
    2026,
    9,
    14,
    13,
    30,
    tzinfo=timezone.utc,
)

END = datetime(
    2026,
    9,
    14,
    14,
    30,
    tzinfo=timezone.utc,
)


def regular_window():
    return build_temporal_validity_window(
        valid_from=START,
        valid_until=END,
        trading_date=DAY,
        session=MarketSession.REGULAR,
    )


def test_obdata066_temporal_identity():
    assert [item.value for item in TemporalValidityState] == [
        "VALID_NOW",
        "NOT_YET_VALID",
        "OUT_OF_WINDOW",
        "SESSION_MISMATCH",
        "TRADING_DATE_MISMATCH",
        "UNKNOWN",
    ]

    assert [item.value for item in TemporalReasoningEligibility] == [
        "ELIGIBLE",
        "INELIGIBLE",
        "REVIEW_REQUIRED",
        "UNKNOWN",
    ]

    assert [item.value for item in MarketSession] == [
        "PREMARKET",
        "REGULAR",
        "AFTER_HOURS",
        "CLOSED",
        "ANY",
        "UNKNOWN",
    ]


def test_obdata066_window_requires_timezone_aware_datetimes():
    with pytest.raises(ValueError):
        build_temporal_validity_window(
            valid_from=datetime(2026, 9, 14, 9, 30),
            valid_until=END,
            trading_date=DAY,
            session=MarketSession.REGULAR,
        )

    with pytest.raises(ValueError):
        build_temporal_validity_window(
            valid_from=START,
            valid_until=datetime(2026, 9, 14, 10, 30),
            trading_date=DAY,
            session=MarketSession.REGULAR,
        )


def test_obdata066_window_requires_forward_interval():
    with pytest.raises(ValueError):
        build_temporal_validity_window(
            valid_from=END,
            valid_until=START,
            trading_date=DAY,
            session=MarketSession.REGULAR,
        )


def test_obdata067_inside_window_is_temporally_eligible():
    result = assess_temporal_validity(
        window=regular_window(),
        evaluated_at=START + timedelta(minutes=15),
        current_trading_date=DAY,
        current_session=MarketSession.REGULAR,
    )

    assert result.state is TemporalValidityState.VALID_NOW
    assert (
        result.reasoning_eligibility
        is TemporalReasoningEligibility.ELIGIBLE
    )
    assert eligible_for_current_temporal_reasoning(result)
    assert not blocked_by_temporal_authority(result)


def test_obdata067_before_window_is_ineligible():
    result = assess_temporal_validity(
        window=regular_window(),
        evaluated_at=START - timedelta(seconds=1),
        current_trading_date=DAY,
        current_session=MarketSession.REGULAR,
    )

    assert result.state is TemporalValidityState.NOT_YET_VALID
    assert blocked_by_temporal_authority(result)


def test_obdata067_after_window_is_ineligible():
    result = assess_temporal_validity(
        window=regular_window(),
        evaluated_at=END + timedelta(seconds=1),
        current_trading_date=DAY,
        current_session=MarketSession.REGULAR,
    )

    assert result.state is TemporalValidityState.OUT_OF_WINDOW
    assert not eligible_for_current_temporal_reasoning(result)
    assert blocked_by_temporal_authority(result)


def test_obdata067_window_boundaries_are_inclusive():
    start_result = assess_temporal_validity(
        window=regular_window(),
        evaluated_at=START,
        current_trading_date=DAY,
        current_session=MarketSession.REGULAR,
    )

    end_result = assess_temporal_validity(
        window=regular_window(),
        evaluated_at=END,
        current_trading_date=DAY,
        current_session=MarketSession.REGULAR,
    )

    assert start_result.state is TemporalValidityState.VALID_NOW
    assert end_result.state is TemporalValidityState.VALID_NOW


def test_obdata068_wrong_session_is_ineligible():
    result = assess_temporal_validity(
        window=regular_window(),
        evaluated_at=START + timedelta(minutes=10),
        current_trading_date=DAY,
        current_session=MarketSession.PREMARKET,
    )

    assert result.state is TemporalValidityState.SESSION_MISMATCH
    assert blocked_by_temporal_authority(result)


def test_obdata068_wrong_trading_date_is_ineligible():
    result = assess_temporal_validity(
        window=regular_window(),
        evaluated_at=START + timedelta(minutes=10),
        current_trading_date=date(2026, 9, 15),
        current_session=MarketSession.REGULAR,
    )

    assert result.state is TemporalValidityState.TRADING_DATE_MISMATCH
    assert blocked_by_temporal_authority(result)


def test_obdata068_any_session_allows_session_match_but_not_date_or_window_override():
    window = build_temporal_validity_window(
        valid_from=START,
        valid_until=END,
        trading_date=DAY,
        session=MarketSession.ANY,
    )

    result = assess_temporal_validity(
        window=window,
        evaluated_at=START + timedelta(minutes=10),
        current_trading_date=DAY,
        current_session=MarketSession.AFTER_HOURS,
    )

    assert result.state is TemporalValidityState.VALID_NOW


def test_obdata068_unknown_current_session_fails_closed():
    result = assess_temporal_validity(
        window=regular_window(),
        evaluated_at=START + timedelta(minutes=10),
        current_trading_date=DAY,
        current_session="UNKNOWN",
    )

    assert result.state is TemporalValidityState.UNKNOWN
    assert result.reasoning_eligibility is TemporalReasoningEligibility.UNKNOWN
    assert blocked_by_temporal_authority(result)


def test_obdata069_snapshot_preserves_temporal_context():
    result = assess_temporal_validity(
        window=regular_window(),
        evaluated_at=START + timedelta(minutes=10),
        current_trading_date=DAY,
        current_session=MarketSession.REGULAR,
    )

    snapshot = temporal_validity_snapshot(
        result
    )

    assert snapshot["state"] == "VALID_NOW"
    assert snapshot["observation_trading_date"] == "2026-09-14"
    assert snapshot["current_trading_date"] == "2026-09-14"
    assert snapshot["observation_session"] == "REGULAR"
    assert snapshot["current_session"] == "REGULAR"


def test_obdata069_module_contains_no_execution_authority():
    source = (
        ROOT
        / "web/ob_observation_temporal_validity.py"
    ).read_text(
        encoding="utf-8"
    )

    forbidden = (
        "placeOrder(",
        "submitOrder(",
        "executeTrade(",
        "broker.submit(",
        "autoSelectContract(",
        "moveCapital(",
        "unlockHybrid(",
        "unlockAutomated(",
        "unlockManualLive(",
    )

    for token in forbidden:
        assert token not in source


def test_obdata069_no_temporal_override_or_cross_session_bypass_api():
    source = (
        ROOT
        / "web/ob_observation_temporal_validity.py"
    ).read_text(
        encoding="utf-8"
    )

    forbidden = (
        "extendValidityWindow(",
        "ignoreValidityWindow(",
        "reuseAcrossSession(",
        "reuseAcrossTradingDate(",
        "forceTemporalValidity(",
        "treatExpiredAsCurrent(",
        "promoteOutOfWindow(",
    )

    for token in forbidden:
        assert token not in source


def test_obdata070_evidence_and_handoff_exist():
    assert (
        ROOT
        / "ob_evidence/authority_foundation/"
        "obdata066_070_temporal_validity_window_authority.json"
    ).is_file()

    assert (
        ROOT
        / "ob_evidence/authority_foundation/"
        "obdata066_070_temporal_validity_window_authority_handoff.md"
    ).is_file()


def test_obdata070_evidence_preserves_authority_boundaries():
    evidence = (
        ROOT
        / "ob_evidence/authority_foundation/"
        "obdata066_070_temporal_validity_window_authority.json"
    ).read_text(
        encoding="utf-8"
    )

    assert '"broker_submission": false' in evidence
    assert '"capital_movement": false' in evidence
    assert '"mode_policy_override": false' in evidence
    assert '"freshness_override": false' in evidence
    assert '"provenance_override": false' in evidence
    assert '"corroboration_override": false' in evidence
    assert '"quality_override": false' in evidence
    assert '"anomaly_override": false' in evidence
    assert '"synthesis_override": false' in evidence
    assert '"conflict_override": false' in evidence
    assert '"lineage_override": false' in evidence
    assert '"lifecycle_override": false' in evidence
    assert '"revocation_override": false' in evidence
    assert '"rehabilitation_override": false' in evidence
    assert '"temporal_window_widening": false' in evidence
    assert '"cross_session_carry_without_authority": false' in evidence
    assert '"cross_date_carry_without_authority": false' in evidence
    assert '"out_of_window_as_current_truth": false' in evidence
