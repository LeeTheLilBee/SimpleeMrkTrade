from __future__ import annotations

from dataclasses import replace
from datetime import date, datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import pytest

from web.ob_capital_simulation_authority import (
    CapitalAssessmentState,
    CapitalCheckState,
    apply_experimental_open_with_capital_admission,
    assess_capital_proposal,
    build_capital_policy_snapshot,
    build_capital_proposal,
    build_capital_session_loss_ledger,
    build_simulation_capital_state,
    capital_simulation_contract,
    verify_capital_session_loss_ledger,
    verify_experimental_capital_admission,
)
from web.ob_effective_policy import (
    owner_profile_policy_layer,
    policy_source_registry,
    product_phase_policy_layer,
    resolve_effective_policy,
)
from web.ob_market_time_authority import (
    build_canonical_market_time,
    build_market_schedule,
)
from web.ob_multi_simulation_harness import (
    SimulationAction,
    SimulationLane,
    apply_simulation_decision,
    bind_canonical_market_time_to_experimental,
    broadcast_market_frame,
    build_market_frame,
    build_simulation_instrument,
    create_multi_simulation_harness,
    lane_state,
    preview_simulation_open_cost,
)
from web.ob_owner_operating_profile import (
    activate_operating_profile,
    draft_operating_profile,
)


ROOT = Path(__file__).resolve().parents[1]

NY = ZoneInfo(
    "America/New_York"
)

DAY = date(
    2026,
    9,
    24,
)

PARENT = (
    "95fdb4ada22181645b08bbec9cd1fe491061e85a"
)


def effective_policy(
    tmp_path,
):
    profile = activate_operating_profile(
        "capsim-006-owner",
        draft_operating_profile(
            "trust",
            "GROWTH",
            "MODERATE",
        ),
        owner_confirmed=True,
        path=(
            tmp_path
            / "capsim006_profiles.sqlite3"
        ),
    )[
        "profile"
    ]

    return resolve_effective_policy(
        account_key="trust",
        layers=[
            owner_profile_policy_layer(
                profile
            ),
            product_phase_policy_layer(
                "trust"
            ),
        ],
    )


def schedule(
    day=DAY,
):
    return build_market_schedule(
        market="US_EQUITIES",
        exchange_timezone="America/New_York",
        trading_date=day,
        day_status="OPEN",
        calendar_authority="CAPSIM006_TEST_CALENDAR",
        calendar_reference=day.isoformat(),
        calendar_payload={
            "date":
                day.isoformat(),

            "status":
                "OPEN",
        },
        premarket_open=datetime(
            day.year,
            day.month,
            day.day,
            4,
            0,
            tzinfo=NY,
        ),
        regular_open=datetime(
            day.year,
            day.month,
            day.day,
            9,
            30,
            tzinfo=NY,
        ),
        regular_close=datetime(
            day.year,
            day.month,
            day.day,
            16,
            0,
            tzinfo=NY,
        ),
        after_hours_close=datetime(
            day.year,
            day.month,
            day.day,
            20,
            0,
            tzinfo=NY,
        ),
    )


def market_time(
    hour,
    minute,
    *,
    day=DAY,
):
    return build_canonical_market_time(
        schedule=schedule(
            day
        ),
        observed_at=datetime(
            day.year,
            day.month,
            day.day,
            hour,
            minute,
            tzinfo=NY,
        ),
    )


def instrument():
    return build_simulation_instrument(
        symbol="AAPL",
        instrument_kind="OPTION",
        contract_id="AAPL-20261218-C-250",
    )


def frame(
    frame_id,
    hour,
    minute,
    price,
):
    return build_market_frame(
        frame_id=frame_id,
        observed_at=(
            datetime(
                DAY.year,
                DAY.month,
                DAY.day,
                hour,
                minute,
                tzinfo=NY,
            )
            .astimezone(
                ZoneInfo(
                    "UTC"
                )
            )
            .isoformat()
        ),
        instrument=instrument(),
        mark_price=price,
        underlying_price=250.0,
        source_reference=(
            "CAPSIM-SOURCE-"
            + frame_id
        ),
    )


def fresh_harness():
    return create_multi_simulation_harness(
        harness_id="CAPSIM006-010",
        account_key="trust",
        starting_capital=10000.0,
        control_ref="CONTROL-FROZEN",
        integrated_ref=PARENT,
        experimental_ref="CAPSIM006-010",
    )


def broadcast_and_bind(
    harness,
    market_frame,
    receipt,
):
    harness = broadcast_market_frame(
        harness,
        market_frame,
    )

    harness = (
        bind_canonical_market_time_to_experimental(
            harness,
            frame=market_frame,
            market_time=receipt,
        )
    )

    return harness


def loss_history():
    harness = fresh_harness()

    open_frame = frame(
        "LOSS-OPEN",
        10,
        0,
        5.00,
    )

    open_time = market_time(
        10,
        0,
    )

    harness = broadcast_and_bind(
        harness,
        open_frame,
        open_time,
    )

    harness = apply_simulation_decision(
        harness,
        lane=SimulationLane.EXPERIMENTAL,
        frame=open_frame,
        decision_id="LOSS-OPEN-DECISION",
        action=SimulationAction.OPEN,
        strategy="CAPSIM_TEST",
        reason="create controlled realized-loss history",
        quantity=1,
    )

    close_frame = frame(
        "LOSS-CLOSE",
        10,
        30,
        3.25,
    )

    close_time = market_time(
        10,
        30,
    )

    harness = broadcast_and_bind(
        harness,
        close_frame,
        close_time,
    )

    harness = apply_simulation_decision(
        harness,
        lane=SimulationLane.EXPERIMENTAL,
        frame=close_frame,
        decision_id="LOSS-CLOSE-DECISION",
        action=SimulationAction.CLOSE,
        strategy="CAPSIM_TEST",
        reason="close controlled loss",
        quantity=1,
    )

    return (
        harness,
        (
            open_time,
            close_time,
        ),
    )


def current_bound_frame(
    harness,
    *,
    frame_id="CURRENT-FRAME",
    hour=11,
    minute=0,
    price=5.00,
):
    current_frame = frame(
        frame_id,
        hour,
        minute,
        price,
    )

    current_time = market_time(
        hour,
        minute,
    )

    harness = broadcast_and_bind(
        harness,
        current_frame,
        current_time,
    )

    return (
        harness,
        current_frame,
        current_time,
    )


def test_capsim006_empty_verified_day_has_complete_zero_loss_ledger():
    harness = fresh_harness()

    current = market_time(
        11,
        0,
    )

    ledger = (
        build_capital_session_loss_ledger(
            harness,
            market_time=current,
        )
    )

    assert (
        ledger.coverage_complete
        is True
    )

    assert (
        ledger.entries
        ==
        ()
    )

    assert (
        ledger.net_realized_pnl
        ==
        0.0
    )

    assert (
        ledger.daily_loss_amount
        ==
        0.0
    )

    assert verify_capital_session_loss_ledger(
        ledger
    )


def test_capsim006_verified_close_trade_enters_daily_loss_ledger():
    harness, history = loss_history()

    current = market_time(
        11,
        0,
    )

    ledger = (
        build_capital_session_loss_ledger(
            harness,
            market_time=current,
            market_time_receipts=history,
        )
    )

    assert (
        ledger.coverage_complete
        is True
    )

    assert len(
        ledger.entries
    ) == 1

    assert (
        ledger.entries[0].realized_pnl
        <
        0
    )

    assert (
        ledger.daily_loss_amount
        ==
        round(
            -ledger.net_realized_pnl,
            4,
        )
    )

    assert (
        ledger.gross_realized_loss
        >
        0
    )

    assert verify_capital_session_loss_ledger(
        ledger
    )


def test_capsim006_missing_close_time_receipt_marks_coverage_incomplete():
    harness, _ = loss_history()

    ledger = (
        build_capital_session_loss_ledger(
            harness,
            market_time=market_time(
                11,
                0,
            ),
        )
    )

    assert (
        ledger.coverage_complete
        is False
    )

    assert len(
        ledger.unresolved_close_trade_ids
    ) == 1

    assert verify_capital_session_loss_ledger(
        ledger
    )


def test_capsim006_tampered_historical_time_receipt_fails_closed():
    harness, history = loss_history()

    forged = replace(
        history[1],
        integrity_hash="0" * 64,
    )

    with pytest.raises(
        ValueError,
        match="unverified canonical market time",
    ):
        build_capital_session_loss_ledger(
            harness,
            market_time=market_time(
                11,
                0,
            ),
            market_time_receipts=(
                history[0],
                forged,
            ),
        )


def test_capsim007_complete_ledger_closes_daily_loss_review(
    tmp_path,
):
    harness, history = loss_history()

    current = market_time(
        11,
        0,
    )

    ledger = (
        build_capital_session_loss_ledger(
            harness,
            market_time=current,
            market_time_receipts=history,
        )
    )

    assessment = assess_capital_proposal(
        policy=build_capital_policy_snapshot(
            effective_policy(
                tmp_path
            )
        ),
        capital_state=build_simulation_capital_state(
            harness,
            lane=SimulationLane.EXPERIMENTAL,
        ),
        proposal=build_capital_proposal(
            account_key="trust",
            lane=SimulationLane.EXPERIMENTAL,
            capital_required=500.0,
            declared_max_loss_amount=50.0,
            risk_reference="CAPSIM006-RISK-50",
        ),
        session_loss=ledger,
    )

    checks = {
        item.name:
            item
        for item
        in assessment.checks
    }

    assert (
        checks[
            "daily_loss_cap"
        ].state
        is CapitalCheckState.PASS
    )

    assert (
        assessment.state
        is CapitalAssessmentState.ALLOW
    )

    assert (
        assessment.session_loss_ledger_id
        ==
        ledger.ledger_id
    )


def test_capsim007_incomplete_ledger_makes_assessment_unknown(
    tmp_path,
):
    harness, _ = loss_history()

    ledger = (
        build_capital_session_loss_ledger(
            harness,
            market_time=market_time(
                11,
                0,
            ),
        )
    )

    assessment = assess_capital_proposal(
        policy=build_capital_policy_snapshot(
            effective_policy(
                tmp_path
            )
        ),
        capital_state=build_simulation_capital_state(
            harness,
            lane=SimulationLane.EXPERIMENTAL,
        ),
        proposal=build_capital_proposal(
            account_key="trust",
            lane=SimulationLane.EXPERIMENTAL,
            capital_required=500.0,
            declared_max_loss_amount=50.0,
            risk_reference="CAPSIM006-RISK-50",
        ),
        session_loss=ledger,
    )

    assert (
        assessment.state
        is CapitalAssessmentState.UNKNOWN
    )

    assert (
        "daily_loss_cap"
        in assessment.unknown_checks
    )


def test_capsim007_projected_daily_loss_can_block_while_trade_loss_limit_passes(
    tmp_path,
):
    harness, history = loss_history()

    ledger = (
        build_capital_session_loss_ledger(
            harness,
            market_time=market_time(
                11,
                0,
            ),
            market_time_receipts=history,
        )
    )

    assessment = assess_capital_proposal(
        policy=build_capital_policy_snapshot(
            effective_policy(
                tmp_path
            )
        ),
        capital_state=build_simulation_capital_state(
            harness,
            lane=SimulationLane.EXPERIMENTAL,
        ),
        proposal=build_capital_proposal(
            account_key="trust",
            lane=SimulationLane.EXPERIMENTAL,
            capital_required=500.0,
            declared_max_loss_amount=80.0,
            risk_reference="CAPSIM006-RISK-80",
        ),
        session_loss=ledger,
    )

    checks = {
        item.name:
            item
        for item
        in assessment.checks
    }

    assert (
        checks[
            "max_loss_per_trade"
        ].state
        is CapitalCheckState.PASS
    )

    assert (
        checks[
            "daily_loss_cap"
        ].state
        is CapitalCheckState.BLOCK
    )

    assert (
        assessment.state
        is CapitalAssessmentState.BLOCK
    )


def test_capsim008_obsim_open_preview_matches_actual_fill_math():
    harness = fresh_harness()

    current_frame = frame(
        "PREVIEW-FRAME",
        11,
        0,
        5.00,
    )

    harness = broadcast_market_frame(
        harness,
        current_frame,
    )

    preview = preview_simulation_open_cost(
        current_frame,
        quantity=1,
    )

    updated = apply_simulation_decision(
        harness,
        lane=SimulationLane.EXPERIMENTAL,
        frame=current_frame,
        decision_id="PREVIEW-OPEN",
        action=SimulationAction.OPEN,
        strategy="PREVIEW_TEST",
        reason="verify preview math",
        quantity=1,
    )

    trade = (
        lane_state(
            updated,
            SimulationLane.EXPERIMENTAL,
        )
        .trades[-1]
    )

    assert (
        trade.fill_price
        ==
        preview[
            "fill_price"
        ]
    )

    assert (
        trade.commission
        ==
        preview[
            "commission"
        ]
    )

    assert (
        trade.gross_value
        ==
        preview[
            "gross_value"
        ]
    )

    assert (
        -trade.cash_effect
        ==
        preview[
            "total_cost"
        ]
    )


def test_capsim008_admission_requires_current_frame_time_binding(
    tmp_path,
):
    harness, history = loss_history()

    current_frame = frame(
        "UNBOUND-CURRENT",
        11,
        0,
        5.00,
    )

    current_time = market_time(
        11,
        0,
    )

    harness = broadcast_market_frame(
        harness,
        current_frame,
    )

    with pytest.raises(
        ValueError,
        match="exactly one canonical time binding",
    ):
        apply_experimental_open_with_capital_admission(
            harness,
            effective_policy=effective_policy(
                tmp_path
            ),
            frame=current_frame,
            market_time=current_time,
            market_time_receipts=history,
            decision_id="UNBOUND-OPEN",
            strategy="CAPSIM_TEST",
            reason="must fail without OBTIME binding",
            quantity=1,
            declared_max_loss_amount=50.0,
            risk_reference="UNBOUND-RISK",
        )


def test_capsim009_blocked_admission_returns_exact_unchanged_harness(
    tmp_path,
):
    harness, history = loss_history()

    harness, current_frame, current_time = (
        current_bound_frame(
            harness
        )
    )

    before = harness

    returned, admission, assessment = (
        apply_experimental_open_with_capital_admission(
            harness,
            effective_policy=effective_policy(
                tmp_path
            ),
            frame=current_frame,
            market_time=current_time,
            market_time_receipts=history,
            decision_id="BLOCKED-OPEN",
            strategy="CAPSIM_TEST",
            reason="projected daily loss should block",
            quantity=1,
            declared_max_loss_amount=80.0,
            risk_reference="BLOCKED-RISK",
        )
    )

    assert returned == before

    assert (
        admission.admitted
        is False
    )

    assert (
        admission.harness_mutated
        is False
    )

    assert (
        assessment.state
        is CapitalAssessmentState.BLOCK
    )

    assert verify_experimental_capital_admission(
        admission
    )


def test_capsim009_allowed_admission_calls_existing_experimental_open_path(
    tmp_path,
):
    harness, history = loss_history()

    harness, current_frame, current_time = (
        current_bound_frame(
            harness
        )
    )

    control_before = lane_state(
        harness,
        SimulationLane.CONTROL,
    )

    integrated_before = lane_state(
        harness,
        SimulationLane.INTEGRATED,
    )

    experimental_before = lane_state(
        harness,
        SimulationLane.EXPERIMENTAL,
    )

    updated, admission, assessment = (
        apply_experimental_open_with_capital_admission(
            harness,
            effective_policy=effective_policy(
                tmp_path
            ),
            frame=current_frame,
            market_time=current_time,
            market_time_receipts=history,
            decision_id="ALLOWED-OPEN",
            strategy="CAPSIM_TEST",
            reason="verified capital admission",
            quantity=1,
            declared_max_loss_amount=50.0,
            risk_reference="ALLOWED-RISK",
            evidence_refs=(
                "UPSTREAM-EVIDENCE-001",
            ),
        )
    )

    assert (
        assessment.state
        is CapitalAssessmentState.ALLOW
    )

    assert (
        admission.admitted
        is True
    )

    assert (
        admission.harness_mutated
        is True
    )

    assert verify_experimental_capital_admission(
        admission
    )

    assert (
        lane_state(
            updated,
            SimulationLane.CONTROL,
        )
        ==
        control_before
    )

    assert (
        lane_state(
            updated,
            SimulationLane.INTEGRATED,
        )
        ==
        integrated_before
    )

    experimental_after = lane_state(
        updated,
        SimulationLane.EXPERIMENTAL,
    )

    assert (
        experimental_after
        !=
        experimental_before
    )

    decision = [
        item
        for item
        in experimental_after.decisions
        if (
            item.decision_id
            ==
            "ALLOWED-OPEN"
        )
    ][0]

    assert (
        assessment.assessment_id
        in decision.evidence_refs
    )

    assert (
        "UPSTREAM-EVIDENCE-001"
        in decision.evidence_refs
    )


def test_capsim009_capital_admission_never_changes_control_or_integrated(
    tmp_path,
):
    harness, history = loss_history()

    harness, current_frame, current_time = (
        current_bound_frame(
            harness,
            frame_id="ISOLATION-CURRENT",
            hour=11,
            minute=15,
        )
    )

    control_before = lane_state(
        harness,
        "CONTROL",
    )

    integrated_before = lane_state(
        harness,
        "INTEGRATED",
    )

    updated, _, _ = (
        apply_experimental_open_with_capital_admission(
            harness,
            effective_policy=effective_policy(
                tmp_path
            ),
            frame=current_frame,
            market_time=current_time,
            market_time_receipts=history,
            decision_id="ISOLATION-OPEN",
            strategy="CAPSIM_TEST",
            reason="prove lane isolation",
            quantity=1,
            declared_max_loss_amount=50.0,
            risk_reference="ISOLATION-RISK",
        )
    )

    assert (
        lane_state(
            updated,
            "CONTROL",
        )
        ==
        control_before
    )

    assert (
        lane_state(
            updated,
            "INTEGRATED",
        )
        ==
        integrated_before
    )


def test_capsim010_pending_obcap_remains_pending():
    source = (
        policy_source_registry()[
            "CAPITAL_POLICY"
        ]
    )

    assert (
        source[
            "source_authority"
        ]
        ==
        "PENDING_OBCAP"
    )

    assert (
        source[
            "status"
        ]
        ==
        "PENDING"
    )

    assert (
        source[
            "runtime_allowed"
        ]
        is False
    )


def test_capsim010_contract_declares_canonical_daily_loss_and_experimental_only_admission():
    contract = (
        capital_simulation_contract()
    )

    assert (
        contract[
            "daily_loss_canonical_authority"
        ]
        is True
    )

    assert (
        contract[
            "daily_loss_authority"
        ]
        ==
        "OB_CAPITAL_SIMULATION_V1"
    )

    assert (
        contract[
            "session_loss_basis"
        ]
        ==
        "NET_REALIZED_PNL_BY_OBTIME_TRADING_DATE"
    )

    assert (
        contract[
            "session_loss_receipt_coverage_required"
        ]
        is True
    )

    assert (
        contract[
            "projected_daily_loss_includes_declared_trade_loss"
        ]
        is True
    )

    assert (
        contract[
            "experimental_open_admission"
        ]
        is True
    )

    assert (
        contract[
            "experimental_open_admission_scope"
        ]
        ==
        "EXPERIMENTAL_ONLY"
    )

    assert (
        contract[
            "delegates_existing_obsim_open_path"
        ]
        is True
    )


def test_capsim010_live_authority_remains_false():
    contract = (
        capital_simulation_contract()
    )

    for key in (
        "execution_authority",
        "broker_submission",
        "capital_movement",
        "automatic_contract_selection",
        "manual_live_unlock",
        "hybrid_unlock",
        "automated_unlock",
        "simulation_performance_grants_live_authority",
    ):
        assert (
            contract[
                key
            ]
            is False
        )


def test_capsim010_files_exist():
    assert (
        ROOT
        / "ob_evidence/simulation/"
        "capsim006_010_session_loss_experimental_admission.json"
    ).is_file()

    assert (
        ROOT
        / "ob_evidence/simulation/"
        "capsim006_010_session_loss_experimental_admission_handoff.md"
    ).is_file()
