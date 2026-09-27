"""OBSIM026–030: explicit owner cadence hint and stale declared-live source denial.

All test records are synthetic fixtures. A source-kind label never authenticates
a price feed, grants a Tower session, or enables live/manual broker placement.
"""
from dataclasses import replace
from datetime import datetime, timedelta

import pytest

from test_obsim016_020_on_demand_session import BASE, harness, start, step
from web.ob_on_demand_simulation_session import (
    DECLARED_LIVE_MAX_SOURCE_AGE_SECONDS,
    LocalSimulationReportStore, SessionStatus, SourceKind,
    inspect_owner_session_due, pause_session, resume_session,
    session_contract, start_session, stop_session, tick_session,
)


def test_due_hint_reads_clock_without_scheduling_or_mutating(tmp_path):
    s = start()
    waiting = inspect_owner_session_due(s, now=BASE + timedelta(seconds=29))
    assert waiting["state"] == "WAIT_INTERVAL"
    assert waiting["due_in_seconds"] == 1
    ready = inspect_owner_session_due(s, now=BASE + timedelta(seconds=30))
    assert ready["state"] == "READY_FOR_EXPLICIT_INPUT"
    assert ready["due_in_seconds"] is None
    for result in (waiting, ready):
        assert result["next_input_present"] is False
        assert result["automatic_tick_scheduled"] is False
        assert result["market_source_authenticated"] is False
        assert result["owner_identity_authenticated_here"] is False
        assert result["simulation_only"] is True
        assert result["broker_submission"] is False
        assert result["manual_live_unlock"] is False
    assert s.reports == () and s.steps == ()
    assert not list(tmp_path.iterdir())


def test_pause_resume_and_stop_never_backfill_due_reports(tmp_path):
    store = LocalSimulationReportStore(tmp_path)
    s = start()
    p = pause_session(s)
    assert inspect_owner_session_due(
        p, now=BASE + timedelta(seconds=600),
    )["state"] == "PAUSED"
    resumed = resume_session(p, now=BASE + timedelta(seconds=600))
    assert inspect_owner_session_due(
        resumed, now=BASE + timedelta(seconds=629),
    )["state"] == "WAIT_INTERVAL"
    assert inspect_owner_session_due(
        resumed, now=BASE + timedelta(seconds=630),
    )["state"] == "READY_FOR_EXPLICIT_INPUT"
    assert resumed.steps == () and resumed.reports == ()
    finished = stop_session(resumed, now=BASE + timedelta(seconds=631), store=store)
    assert inspect_owner_session_due(
        finished, now=BASE + timedelta(seconds=900),
    )["state"] == "STOPPED"
    assert not list((tmp_path / finished.session_id).glob("[0-9]*.json"))


def test_clock_rollback_fails_before_any_status_claim():
    with pytest.raises(ValueError, match="clock cannot move backwards"):
        inspect_owner_session_due(start(), now=BASE - timedelta(seconds=1))
    with pytest.raises(ValueError, match="timezone-aware"):
        inspect_owner_session_due(start(), now=datetime(2026, 9, 26, 12))


def test_max_beta_ticks_never_claim_unbounded_continuation():
    s = start()
    synthetic = (step("EXHAUSTED"),) * 120
    s = replace(s, steps=synthetic)
    result = inspect_owner_session_due(s, now=BASE + timedelta(seconds=31))
    assert result["state"] == "BOUNDED_BETA_EXHAUSTED"
    assert result["automatic_tick_scheduled"] is False


def test_stale_declared_live_observation_is_rejected_before_replay_or_file_write(tmp_path):
    store = LocalSimulationReportStore(tmp_path)
    s = start_session(
        session_id="STALE-LIVE-001",
        initial_harness=harness(),
        source_kind=SourceKind.LIVE_OBSERVED,
        now=BASE,
    )
    original = s
    with pytest.raises(ValueError, match="declared live observation is stale"):
        tick_session(s, step("STALE-OBS"), now=BASE + timedelta(seconds=30), store=store)
    assert s == original
    assert not (tmp_path / s.session_id / "0001.json").exists()


def test_fresh_declared_live_is_still_unverified_and_simulation_only(tmp_path):
    store = LocalSimulationReportStore(tmp_path)
    explicit = step("DECLARED-LIVE-001")
    observed = datetime.fromisoformat(explicit.frame.observed_at)
    s = start_session(
        session_id="DECLARED-LIVE-001",
        initial_harness=harness(),
        source_kind=SourceKind.LIVE_OBSERVED,
        now=observed - timedelta(seconds=30),
    )
    result = tick_session(
        s, explicit, now=observed + timedelta(seconds=30), store=store,
    )
    report = result.reports[0]
    assert report["source_kind"] == "LIVE_OBSERVED"
    assert report["source_freshness"] == "FRESH_DECLARED_UNVERIFIED"
    assert report["source_claim_verified"] is False
    assert report["source_provider_authenticated"] is False
    assert report["source_age_seconds"] == 30
    assert report["simulation_only"] is True
    for flag in ("broker_submission", "capital_movement", "manual_live_unlock",
                 "hybrid_unlock", "automated_unlock", "winner_selected"):
        assert report[flag] is False
    assert store.load_ticks(s.session_id) == (report,)


def test_future_declared_live_frame_cannot_be_used_as_current(tmp_path):
    store = LocalSimulationReportStore(tmp_path)
    explicit = step("FUTURE-OBS")
    observed = datetime.fromisoformat(explicit.frame.observed_at)
    s = start_session(
        session_id="FUTURE-OBS", initial_harness=harness(),
        source_kind=SourceKind.LIVE_OBSERVED,
        now=observed - timedelta(seconds=90),
    )
    with pytest.raises(ValueError, match="observation from the future"):
        tick_session(
            s, explicit, now=observed - timedelta(seconds=30), store=store,
        )
    assert not (tmp_path / s.session_id / "0001.json").exists()


def test_explicit_old_historical_replay_remains_historical_not_live(tmp_path):
    store = LocalSimulationReportStore(tmp_path)
    result = tick_session(
        start(), step("OLD-HISTORICAL"),
        now=BASE + timedelta(seconds=30), store=store,
    )
    assert result.reports[0]["source_kind"] == "HISTORICAL"
    assert result.reports[0]["source_freshness"] == "HISTORICAL"
    assert result.reports[0]["source_claim_verified"] is False
    assert result.reports[0]["source_provider_authenticated"] is False


def test_documented_source_limit_does_not_grant_trading():
    contract = session_contract()
    assert contract["declared_live_max_source_age_seconds"] == (
        DECLARED_LIVE_MAX_SOURCE_AGE_SECONDS == 120
    )
    assert contract["stale_declared_live_input_advances_simulation"] is False
    assert contract["owner_due_hint_is_timer_or_permission"] is False
    for flag in ("broker_submission", "capital_movement", "manual_live_unlock",
                 "hybrid_unlock", "automated_unlock"):
        assert contract[flag] is False
