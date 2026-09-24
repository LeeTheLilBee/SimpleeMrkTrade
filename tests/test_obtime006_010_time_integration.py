from __future__ import annotations

from dataclasses import replace
from datetime import date, datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import pytest

from web.ob_authority_registry import (
    PENDING_AUTHORITY_SLOTS,
    authority_registry_contract,
    build_canonical_authority_registry,
    declarative_registry,
    resolve_authority_reference,
    validate_canonical_authority_registry,
)
from web.ob_market_time_authority import (
    MarketTimeState,
    build_canonical_market_time,
    build_market_schedule,
)
from web.ob_multi_simulation_harness import (
    SimulationLane,
    bind_canonical_market_time_to_experimental,
    broadcast_market_frame,
    build_market_frame,
    build_simulation_instrument,
    create_multi_simulation_harness,
    lane_state,
    simulation_contract,
    verify_lane_receipt_chain,
)
from web.ob_operating_mode import (
    build_initial_mode_state,
    operating_mode_time_context_projection,
    validate_mode_state,
)


ROOT = Path(__file__).resolve().parents[1]

NY = ZoneInfo(
    "America/New_York"
)

DAY = date(
    2026,
    9,
    21,
)

SEALED_PARENT = (
    "b5e7711113c5f0cb7d7f6ba2078bb2c93a661cf0"
)


def schedule():
    return build_market_schedule(
        market="US_EQUITIES",
        exchange_timezone="America/New_York",
        trading_date=DAY,
        day_status="OPEN",
        calendar_authority="TEST_CALENDAR",
        calendar_reference="TEST-2026-09-21",
        calendar_payload={
            "date":
                "2026-09-21",

            "status":
                "OPEN",

            "regular_open":
                "09:30",

            "regular_close":
                "16:00",
        },
        premarket_open=datetime(
            2026,
            9,
            21,
            4,
            0,
            tzinfo=NY,
        ),
        regular_open=datetime(
            2026,
            9,
            21,
            9,
            30,
            tzinfo=NY,
        ),
        regular_close=datetime(
            2026,
            9,
            21,
            16,
            0,
            tzinfo=NY,
        ),
        after_hours_close=datetime(
            2026,
            9,
            21,
            20,
            0,
            tzinfo=NY,
        ),
    )


def market_time(
    hour=10,
    minute=0,
):
    return build_canonical_market_time(
        schedule=schedule(),
        observed_at=datetime(
            2026,
            9,
            21,
            hour,
            minute,
            tzinfo=NY,
        ),
    )


def harness():
    return create_multi_simulation_harness(
        harness_id="OBTIME-INTEGRATION-HARNESS",
        account_key="PROOF-DEMO",
        starting_capital=10000.0,
        control_ref=SEALED_PARENT,
        integrated_ref=SEALED_PARENT,
        experimental_ref="OBTIME006-010",
    )


def frame():
    instrument = build_simulation_instrument(
        symbol="AAPL",
        instrument_kind="OPTION",
        contract_id="AAPL-20261218-C-250",
    )

    return build_market_frame(
        frame_id="FRAME-TIME-001",
        observed_at="2026-09-21T14:00:00Z",
        instrument=instrument,
        mark_price=2.0,
        underlying_price=250.0,
        source_reference="SOURCE-TIME-001",
    )


def broadcast():
    h = harness()
    f = frame()

    return (
        broadcast_market_frame(
            h,
            f,
        ),
        f,
    )


def test_obtime006_verified_time_binds_to_experimental_only():
    h, f = broadcast()

    bound = (
        bind_canonical_market_time_to_experimental(
            h,
            frame=f,
            market_time=market_time(),
        )
    )

    control = lane_state(
        bound,
        SimulationLane.CONTROL,
    )

    integrated = lane_state(
        bound,
        SimulationLane.INTEGRATED,
    )

    experimental = lane_state(
        bound,
        SimulationLane.EXPERIMENTAL,
    )

    assert control.time_bindings == ()
    assert integrated.time_bindings == ()

    assert len(
        experimental.time_bindings
    ) == 1

    binding = (
        experimental.time_bindings[0]
    )

    assert (
        binding.frame_id
        == f.frame_id
    )

    assert (
        binding.authority
        == "OB_MARKET_TIME_V1"
    )

    assert (
        binding.trading_date
        == "2026-09-21"
    )

    assert (
        binding.market_session
        == "REGULAR"
    )

    assert verify_lane_receipt_chain(
        experimental
    )


def test_obtime006_binding_does_not_mutate_control_or_integrated():
    h, f = broadcast()

    control_before = lane_state(
        h,
        "CONTROL",
    )

    integrated_before = lane_state(
        h,
        "INTEGRATED",
    )

    bound = (
        bind_canonical_market_time_to_experimental(
            h,
            frame=f,
            market_time=market_time(),
        )
    )

    assert (
        lane_state(
            bound,
            "CONTROL",
        )
        == control_before
    )

    assert (
        lane_state(
            bound,
            "INTEGRATED",
        )
        == integrated_before
    )


def test_obtime007_frame_time_mismatch_fails_closed():
    h, f = broadcast()

    with pytest.raises(
        ValueError,
        match="does not match",
    ):
        bind_canonical_market_time_to_experimental(
            h,
            frame=f,
            market_time=market_time(
                hour=10,
                minute=1,
            ),
        )


def test_obtime007_tampered_time_receipt_fails_closed():
    h, f = broadcast()

    forged = replace(
        market_time(),
        integrity_hash="0" * 64,
    )

    with pytest.raises(
        ValueError,
        match="verified canonical market time",
    ):
        bind_canonical_market_time_to_experimental(
            h,
            frame=f,
            market_time=forged,
        )


def test_obtime007_duplicate_frame_binding_fails_closed():
    h, f = broadcast()

    receipt = market_time()

    first = (
        bind_canonical_market_time_to_experimental(
            h,
            frame=f,
            market_time=receipt,
        )
    )

    with pytest.raises(
        ValueError,
        match="already has canonical time binding",
    ):
        bind_canonical_market_time_to_experimental(
            first,
            frame=f,
            market_time=receipt,
        )


def test_obtime007_schedule_date_mismatch_cannot_bind():
    h, f = broadcast()

    mismatch = build_canonical_market_time(
        schedule=schedule(),
        observed_at=datetime(
            2026,
            9,
            22,
            10,
            0,
            tzinfo=NY,
        ),
    )

    assert (
        mismatch.state
        is MarketTimeState.SCHEDULE_DATE_MISMATCH
    )

    with pytest.raises(
        ValueError,
        match="schedule-date mismatch",
    ):
        bind_canonical_market_time_to_experimental(
            h,
            frame=f,
            market_time=mismatch,
        )


def test_obtime008_mode_time_projection_does_not_mutate_mode_state():
    state = build_initial_mode_state(
        account_key="trust",
        mode="PAPER",
        owner_authorized=True,
        reason="OBTIME006-010 test",
        recorded_at="2026-09-21T13:00:00+00:00",
    )

    before = dict(
        state
    )

    projection = (
        operating_mode_time_context_projection(
            state,
            market_time(),
        )
    )

    assert state == before

    validate_mode_state(
        state
    )

    assert (
        state["canonical_time_claimed"]
        is False
    )

    assert (
        projection["canonical_time_claimed"]
        is True
    )

    assert (
        projection["time_authority"]
        == "OB_MARKET_TIME_V1"
    )

    assert (
        projection[
            "market_time_reference"
        ][
            "market_session"
        ]
        == "REGULAR"
    )

    assert (
        projection["mode_state_mutated"]
        is False
    )

    assert (
        projection["broker_submission"]
        is False
    )

    assert (
        projection["capital_movement"]
        is False
    )


def test_obtime008_mode_projection_rejects_tampered_time():
    state = build_initial_mode_state(
        account_key="trust",
        mode="PAPER",
        owner_authorized=True,
        reason="tamper-test",
    )

    forged = replace(
        market_time(),
        integrity_hash="0" * 64,
    )

    with pytest.raises(
        ValueError,
        match="verified canonical market time",
    ):
        operating_mode_time_context_projection(
            state,
            forged,
        )


def test_obtime009_registry_activates_temporal_context():
    registry = (
        build_canonical_authority_registry()
    )

    record = (
        registry[
            "authority_records"
        ][
            "temporal_context"
        ]
    )

    assert (
        record["authority_id"]
        == "OB_MARKET_TIME_V1"
    )

    assert (
        record["implementation_ref"]
        == "web/ob_market_time_authority.py"
    )

    assert (
        record["execution_authority"]
        is False
    )

    assert (
        record["broker_submission"]
        is False
    )

    assert (
        record["capital_movement"]
        is False
    )

    assert (
        "temporal_context"
        not in PENDING_AUTHORITY_SLOTS
    )


def test_obtime009_pending_obtime_is_retired_alias():
    resolution = (
        resolve_authority_reference(
            "PENDING_OBTIME"
        )
    )

    assert (
        resolution["resolution"]
        == "RETIRED_ALIAS"
    )

    assert (
        resolution[
            "resolved_authority_id"
        ]
        == "OB_MARKET_TIME_V1"
    )


def test_obtime009_temporal_context_reference_is_active():
    by_concept = (
        resolve_authority_reference(
            "temporal_context"
        )
    )

    by_id = (
        resolve_authority_reference(
            "OB_MARKET_TIME_V1"
        )
    )

    assert (
        by_concept["resolution"]
        == "ACTIVE_CONCEPT"
    )

    assert (
        by_id["resolution"]
        == "ACTIVE_AUTHORITY_ID"
    )


def test_obtime010_active_authority_may_remain_deferred_for_consumer():
    registry = declarative_registry()

    assert (
        "temporal_context"
        in registry[
            "authority_records"
        ]
    )

    still_deferred_consumers = (
        "market_candidate_truth",
        "options_research",
        "account_identity_truth_taxonomy",
        "owner_fit_eligibility",
    )

    for concept in still_deferred_consumers:
        assert (
            "temporal_context"
            in registry[
                "authority_records"
            ][
                concept
            ][
                "deferred_integrations"
            ]
        )

    assert (
        "temporal_context"
        not in registry[
            "authority_records"
        ][
            "decision_context"
        ][
            "deferred_integrations"
        ]
    )

    validation = (
        validate_canonical_authority_registry(
            registry
        )
    )

    assert (
        validation["valid"]
        is True
    )


def test_obtime010_unknown_deferred_integration_fails_closed():
    registry = declarative_registry()

    registry[
        "authority_records"
    ][
        "market_candidate_truth"
    ][
        "deferred_integrations"
    ].append(
        "FAKE_TIME_AUTHORITY"
    )

    validation = (
        validate_canonical_authority_registry(
            registry
        )
    )

    assert (
        validation["valid"]
        is False
    )

    assert (
        "unknown_deferred_integration:"
        "market_candidate_truth:"
        "FAKE_TIME_AUTHORITY"
        in validation[
            "errors"
        ]
    )


def test_obtime010_registry_contract_declares_deferred_semantics():
    contract = authority_registry_contract()

    assert (
        contract[
            "deferred_integration_may_reference_pending_slot"
        ]
        is True
    )

    assert (
        contract[
            "deferred_integration_may_reference_active_concept"
        ]
        is True
    )

    assert (
        contract[
            "unknown_deferred_integration_allowed"
        ]
        is False
    )


def test_obtime010_source_provenance_pending_slot_is_preserved():
    assert set(
        PENDING_AUTHORITY_SLOTS
    ) == {
        "source_provenance",
    }

    assert (
        PENDING_AUTHORITY_SLOTS[
            "source_provenance"
        ][
            "authority_id"
        ]
        == "PENDING_OBDATA011_015"
    )


def test_obtime010_simulation_contract_preserves_authority_boundary():
    contract = simulation_contract()

    assert (
        contract[
            "canonical_market_time_authority_available"
        ]
        == "OB_MARKET_TIME_V1"
    )

    assert (
        contract[
            "canonical_market_time_binding_scope"
        ]
        == "EXPERIMENTAL_ONLY"
    )

    assert (
        contract[
            "simulation_performance_grants_live_authority"
        ]
        is False
    )

    for key in (
        "execution_authority",
        "broker_submission",
        "capital_movement",
        "automatic_contract_selection",
        "manual_live_unlock",
        "hybrid_unlock",
        "automated_unlock",
    ):
        assert contract[
            key
        ] is False


def test_obtime010_modified_modules_have_no_execution_path():
    files = (
        ROOT
        / "web/ob_multi_simulation_harness.py",

        ROOT
        / "web/ob_operating_mode.py",

        ROOT
        / "web/ob_market_time_authority.py",
    )

    forbidden = (
        "submitOrder(",
        "executeTrade(",
        "broker.submit(",
        "moveCapital(",
        "unlockManualLive(",
        "unlockHybrid(",
        "unlockAutomated(",
    )

    for path in files:
        source = path.read_text(
            encoding="utf-8"
        )

        for token in forbidden:
            assert token not in source


def test_obtime010_evidence_and_handoff_exist():
    assert (
        ROOT
        / "ob_evidence/time/"
        "obtime006_010_time_integration.json"
    ).is_file()

    assert (
        ROOT
        / "ob_evidence/time/"
        "obtime006_010_time_integration_handoff.md"
    ).is_file()
