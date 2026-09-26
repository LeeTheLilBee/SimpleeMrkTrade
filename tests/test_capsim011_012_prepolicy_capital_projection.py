from dataclasses import replace
from datetime import date, datetime
from zoneinfo import ZoneInfo

import pytest

import web.ob_capital_simulation_authority as capsim
from web.ob_capital_policy_authority import (
    LIMIT_KEYS,
    SCHEMA_VERSION,
    build_prepolicy_capital_projection,
    prepolicy_capital_contract,
    verify_prepolicy_capital_projection,
)
from web.ob_capital_simulation_authority import (
    build_capital_session_loss_ledger,
    build_simulation_capital_state,
)
from web.ob_market_time_authority import build_canonical_market_time, build_market_schedule
from web.ob_multi_simulation_harness import SimulationLane, create_multi_simulation_harness
from web.ob_owner_operating_profile import activate_operating_profile, draft_operating_profile

NY = ZoneInfo("America/New_York")
DAY = date(2026, 9, 24)


def profile(tmp_path, account="trust"):
    return activate_operating_profile(
        "capsim011-test-owner",
        draft_operating_profile(account, "GROWTH", "MODERATE"),
        owner_confirmed=True,
        path=tmp_path / (account + "_profiles.sqlite3"),
    )["profile"]


def market_time():
    schedule = build_market_schedule(
        market="US_EQUITIES", exchange_timezone="America/New_York",
        trading_date=DAY, day_status="OPEN",
        calendar_authority="CAPSIM011_TEST_CALENDAR",
        calendar_reference=DAY.isoformat(),
        calendar_payload={"date": DAY.isoformat(), "status": "OPEN"},
        premarket_open=datetime(2026, 9, 24, 4, tzinfo=NY),
        regular_open=datetime(2026, 9, 24, 9, 30, tzinfo=NY),
        regular_close=datetime(2026, 9, 24, 16, tzinfo=NY),
        after_hours_close=datetime(2026, 9, 24, 20, tzinfo=NY),
    )
    return build_canonical_market_time(
        schedule=schedule, observed_at=datetime(2026, 9, 24, 10, tzinfo=NY)
    )


def evidence(account="trust"):
    harness = create_multi_simulation_harness(
        harness_id="CAPSIM011-015", account_key=account, starting_capital=10000.0,
        control_ref="CONTROL-FROZEN", integrated_ref="ACCEPTED",
        experimental_ref="CAPSIM011-015",
    )
    time = market_time()
    state = build_simulation_capital_state(
        harness, lane=SimulationLane.EXPERIMENTAL
    )
    ledger = build_capital_session_loss_ledger(
        harness, market_time=time, market_time_receipts=(time,)
    )
    return state, ledger


def resign_state(state, **changes):
    provisional = replace(state, **changes)
    digest = capsim.stable_hash(capsim._state_material(provisional))
    return replace(
        provisional,
        snapshot_id="OBCAPSTATE-" + digest[:24], integrity_hash=digest
    )


def test_prepolicy_authority_is_distinct_and_nonexecuting():
    contract = prepolicy_capital_contract()
    assert contract["authority"] == SCHEMA_VERSION
    assert contract["pre_policy"] and contract["restriction_only"]
    assert not contract["imports_effective_policy"]
    assert not contract["effective_policy_promotion"]
    for name in (
        "broker_submission", "capital_movement", "manual_live_unlock",
        "hybrid_unlock", "automated_unlock",
    ):
        assert contract[name] is False


def test_ready_projection_uses_canonical_six_decimal_limits(tmp_path):
    owner = profile(tmp_path)
    state, ledger = evidence()
    projection = build_prepolicy_capital_projection(
        owner, capital_state=state, session_loss=ledger,
    )
    assert verify_prepolicy_capital_projection(projection)
    assert projection.state == "READY"
    assert tuple(dict(projection.limits)) == LIMIT_KEYS
    assert projection.limits == projection.baseline_limits
    assert projection.capacity_factor == 1.0


def test_drawdown_and_cash_can_only_tighten_owner_limits(tmp_path):
    owner = profile(tmp_path)
    state, ledger = evidence()
    restrained = resign_state(
        state, cash=7000.0, equity=9000.0, peak_equity=10000.0,
        max_drawdown_pct=10.0,
    )
    projection = build_prepolicy_capital_projection(
        owner, capital_state=restrained, session_loss=ledger,
    )
    assert projection.state == "READY"
    assert verify_prepolicy_capital_projection(projection)
    assert projection.capacity_factor < 1.0
    for key in LIMIT_KEYS:
        assert 0 < dict(projection.limits)[key] <= dict(projection.baseline_limits)[key]
        assert round(dict(projection.limits)[key], 6) == dict(projection.limits)[key]


def test_zero_cash_is_block_not_fabricated_positive_permission(tmp_path):
    owner = profile(tmp_path)
    state, ledger = evidence()
    restrained = resign_state(state, cash=0.0)
    projection = build_prepolicy_capital_projection(
        owner, capital_state=restrained, session_loss=ledger,
    )
    assert projection.state == "BLOCK"
    assert not projection.limits
    assert "NO_POSITIVE_CAPITAL_CAPACITY" in projection.reasons
    assert verify_prepolicy_capital_projection(projection)


def test_cross_account_or_tampered_evidence_fails_closed(tmp_path):
    owner = profile(tmp_path)
    state, ledger = evidence()
    with pytest.raises(ValueError, match="verified"):
        build_prepolicy_capital_projection(
            owner, capital_state=replace(state, integrity_hash="0" * 64),
            session_loss=ledger,
        )
    with pytest.raises(ValueError, match="verified"):
        build_prepolicy_capital_projection(
            owner, capital_state=state,
            session_loss=replace(ledger, integrity_hash="0" * 64),
        )
    other_state, _ = evidence(account="personal")
    with pytest.raises(ValueError, match="cross account"):
        build_prepolicy_capital_projection(
            owner, capital_state=other_state, session_loss=ledger,
        )


def test_projection_tamper_fails_integrity(tmp_path):
    owner = profile(tmp_path)
    state, ledger = evidence()
    projection = build_prepolicy_capital_projection(
        owner, capital_state=state, session_loss=ledger,
    )
    assert not verify_prepolicy_capital_projection(
        replace(projection, capacity_factor=0.5)
    )
