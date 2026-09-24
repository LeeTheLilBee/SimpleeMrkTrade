from __future__ import annotations

from dataclasses import replace

import pytest

from web.ob_capital_simulation_authority import (
    CapitalAssessmentState,
    CapitalCheckState,
    build_capital_policy_snapshot,
    build_capital_proposal,
    build_simulation_capital_state,
    capital_simulation_contract,
    capital_simulation_snapshot,
    assess_capital_proposal,
    verify_capital_policy_snapshot,
    verify_capital_proposal,
    verify_capital_simulation_assessment,
    verify_simulation_capital_state,
)
from web.ob_effective_policy import (
    owner_profile_policy_layer,
    policy_source_registry,
    product_phase_policy_layer,
    resolve_effective_policy,
)
from web.ob_multi_simulation_harness import (
    SimulationLane,
    create_multi_simulation_harness,
)
from web.ob_owner_operating_profile import (
    activate_operating_profile,
    draft_operating_profile,
)


def effective_policy(
    tmp_path,
    *,
    account_key="trust",
    risk_level="MODERATE",
):
    profile = activate_operating_profile(
        "capsim-test-owner",
        draft_operating_profile(
            account_key,
            "GROWTH",
            risk_level,
        ),
        owner_confirmed=True,
        path=(
            tmp_path
            / (
                "capsim_"
                + account_key
                + "_"
                + risk_level.lower()
                + ".sqlite3"
            )
        ),
    )[
        "profile"
    ]

    return resolve_effective_policy(
        account_key=account_key,
        layers=[
            owner_profile_policy_layer(
                profile
            ),
            product_phase_policy_layer(
                account_key
            ),
        ],
    )


def harness(
    *,
    account_key="trust",
):
    return create_multi_simulation_harness(
        harness_id="CAPSIM-001-005",
        account_key=account_key,
        starting_capital=10000.0,
        control_ref="CONTROL-FROZEN",
        integrated_ref=(
            "9b6f5ffebd83cd4fa501458d9470b3742d99937a"
        ),
        experimental_ref="CAPSIM001-005",
    )


def policy_snapshot(
    tmp_path,
):
    return build_capital_policy_snapshot(
        effective_policy(
            tmp_path
        )
    )


def capital_state():
    return build_simulation_capital_state(
        harness(),
        lane=SimulationLane.EXPERIMENTAL,
    )


def proposal(
    *,
    capital_required=500.0,
    declared_max_loss_amount=100.0,
    account_key="trust",
    lane=SimulationLane.EXPERIMENTAL,
):
    return build_capital_proposal(
        account_key=account_key,
        lane=lane,
        capital_required=capital_required,
        declared_max_loss_amount=declared_max_loss_amount,
        risk_reference=(
            "CAPSIM-DECLARED-RISK-001"
            if declared_max_loss_amount
            is not None
            else None
        ),
    )


def test_capsim001_contract_is_simulation_only():
    contract = (
        capital_simulation_contract()
    )

    assert (
        contract[
            "schema_version"
        ]
        ==
        "OB_CAPITAL_SIMULATION_V1"
    )

    assert (
        contract[
            "effective_policy_authority"
        ]
        ==
        "OB_EFFECTIVE_POLICY_V1"
    )

    assert (
        contract[
            "simulation_only"
        ]
        is True
    )


def test_capsim001_capital_policy_source_remains_pending():
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


def test_capsim001_policy_snapshot_binds_real_effective_policy_limits(
    tmp_path,
):
    policy = effective_policy(
        tmp_path
    )

    snapshot = (
        build_capital_policy_snapshot(
            policy
        )
    )

    assert (
        snapshot.account_key
        ==
        "trust"
    )

    assert (
        snapshot.effective_policy_id
        ==
        policy[
            "policy_id"
        ]
    )

    assert (
        snapshot.effective_policy_hash
        ==
        policy[
            "policy_fingerprint"
        ]
    )

    assert (
        snapshot.max_loss_per_trade_pct
        ==
        1.0
    )

    assert (
        snapshot.max_position_allocation_pct
        ==
        10.0
    )

    assert (
        snapshot.daily_loss_cap_pct
        ==
        2.5
    )

    assert verify_capital_policy_snapshot(
        snapshot
    )


def test_capsim001_policy_snapshot_is_tamper_evident(
    tmp_path,
):
    snapshot = policy_snapshot(
        tmp_path
    )

    forged = replace(
        snapshot,
        max_position_allocation_pct=99.0,
    )

    assert not verify_capital_policy_snapshot(
        forged
    )


def test_capsim001_rejects_effective_policy_with_capital_authority(
    tmp_path,
):
    policy = effective_policy(
        tmp_path
    )

    forged = {
        **policy,
        "capital_movement":
            True,
    }

    with pytest.raises(
        ValueError,
        match="forbidden authority",
    ):
        build_capital_policy_snapshot(
            forged
        )


def test_capsim002_builds_hash_bound_experimental_capital_state():
    state = capital_state()

    assert (
        state.lane
        is SimulationLane.EXPERIMENTAL
    )

    assert (
        state.account_key
        ==
        "trust"
    )

    assert (
        state.starting_capital
        ==
        10000.0
    )

    assert (
        state.cash
        ==
        10000.0
    )

    assert (
        state.equity
        ==
        10000.0
    )

    assert (
        state.max_drawdown_pct
        ==
        0.0
    )

    assert (
        state.receipt_chain_valid
        is True
    )

    assert verify_simulation_capital_state(
        state
    )


def test_capsim002_capital_state_is_tamper_evident():
    state = capital_state()

    forged = replace(
        state,
        cash=999999.0,
    )

    assert not verify_simulation_capital_state(
        forged
    )


def test_capsim003_capital_proposal_is_hash_bound():
    item = proposal()

    assert (
        item.capital_required
        ==
        500.0
    )

    assert (
        item.declared_max_loss_amount
        ==
        100.0
    )

    assert verify_capital_proposal(
        item
    )

    forged = replace(
        item,
        capital_required=50.0,
    )

    assert not verify_capital_proposal(
        forged
    )


def test_capsim003_declared_loss_requires_risk_reference():
    with pytest.raises(
        ValueError,
        match="risk_reference",
    ):
        build_capital_proposal(
            account_key="trust",
            lane="EXPERIMENTAL",
            capital_required=500.0,
            declared_max_loss_amount=100.0,
            risk_reference=None,
        )


def test_capsim003_passes_known_checks_but_reviews_missing_daily_ledger(
    tmp_path,
):
    assessment = assess_capital_proposal(
        policy=policy_snapshot(
            tmp_path
        ),
        capital_state=capital_state(),
        proposal=proposal(),
    )

    assert (
        assessment.state
        is CapitalAssessmentState.REVIEW_REQUIRED
    )

    check_map = {
        item.name:
            item
        for item
        in assessment.checks
    }

    assert (
        check_map[
            "cash_available"
        ].state
        is CapitalCheckState.PASS
    )

    assert (
        check_map[
            "position_allocation"
        ].state
        is CapitalCheckState.PASS
    )

    assert (
        check_map[
            "max_loss_per_trade"
        ].state
        is CapitalCheckState.PASS
    )

    assert (
        check_map[
            "daily_loss_cap"
        ].state
        is CapitalCheckState.REVIEW
    )

    assert (
        assessment.review_checks
        ==
        (
            "daily_loss_cap",
        )
    )

    assert verify_capital_simulation_assessment(
        assessment
    )


def test_capsim003_position_allocation_violation_blocks(
    tmp_path,
):
    assessment = assess_capital_proposal(
        policy=policy_snapshot(
            tmp_path
        ),
        capital_state=capital_state(),
        proposal=proposal(
            capital_required=1500.0,
            declared_max_loss_amount=100.0,
        ),
    )

    assert (
        assessment.state
        is CapitalAssessmentState.BLOCK
    )

    assert (
        "position_allocation"
        in assessment.blocking_checks
    )


def test_capsim003_per_trade_loss_violation_blocks(
    tmp_path,
):
    assessment = assess_capital_proposal(
        policy=policy_snapshot(
            tmp_path
        ),
        capital_state=capital_state(),
        proposal=proposal(
            capital_required=500.0,
            declared_max_loss_amount=150.0,
        ),
    )

    assert (
        assessment.state
        is CapitalAssessmentState.BLOCK
    )

    assert (
        "max_loss_per_trade"
        in assessment.blocking_checks
    )


def test_capsim003_insufficient_cash_blocks(
    tmp_path,
):
    assessment = assess_capital_proposal(
        policy=policy_snapshot(
            tmp_path
        ),
        capital_state=capital_state(),
        proposal=proposal(
            capital_required=11000.0,
            declared_max_loss_amount=100.0,
        ),
    )

    assert (
        assessment.state
        is CapitalAssessmentState.BLOCK
    )

    assert (
        "cash_available"
        in assessment.blocking_checks
    )


def test_capsim003_missing_max_loss_requires_review(
    tmp_path,
):
    assessment = assess_capital_proposal(
        policy=policy_snapshot(
            tmp_path
        ),
        capital_state=capital_state(),
        proposal=proposal(
            capital_required=500.0,
            declared_max_loss_amount=None,
        ),
    )

    assert (
        assessment.state
        is CapitalAssessmentState.REVIEW_REQUIRED
    )

    assert (
        "max_loss_per_trade"
        in assessment.review_checks
    )

    assert (
        "daily_loss_cap"
        in assessment.review_checks
    )


def test_capsim004_cross_account_assessment_fails_closed(
    tmp_path,
):
    with pytest.raises(
        ValueError,
        match="account boundary",
    ):
        assess_capital_proposal(
            policy=policy_snapshot(
                tmp_path
            ),
            capital_state=capital_state(),
            proposal=proposal(
                account_key="personal",
            ),
        )


def test_capsim004_cross_lane_assessment_fails_closed(
    tmp_path,
):
    with pytest.raises(
        ValueError,
        match="lane boundary",
    ):
        assess_capital_proposal(
            policy=policy_snapshot(
                tmp_path
            ),
            capital_state=capital_state(),
            proposal=proposal(
                lane=SimulationLane.INTEGRATED,
            ),
        )


def test_capsim004_assessment_is_tamper_evident(
    tmp_path,
):
    assessment = assess_capital_proposal(
        policy=policy_snapshot(
            tmp_path
        ),
        capital_state=capital_state(),
        proposal=proposal(),
    )

    forged = replace(
        assessment,
        state=CapitalAssessmentState.ALLOW,
    )

    assert not verify_capital_simulation_assessment(
        forged
    )


def test_capsim004_snapshot_preserves_review_and_block_details(
    tmp_path,
):
    assessment = assess_capital_proposal(
        policy=policy_snapshot(
            tmp_path
        ),
        capital_state=capital_state(),
        proposal=proposal(
            capital_required=1500.0,
            declared_max_loss_amount=150.0,
        ),
    )

    snapshot = (
        capital_simulation_snapshot(
            assessment
        )
    )

    assert (
        snapshot[
            "state"
        ]
        ==
        "BLOCK"
    )

    assert (
        "position_allocation"
        in snapshot[
            "blocking_checks"
        ]
    )

    assert (
        "max_loss_per_trade"
        in snapshot[
            "blocking_checks"
        ]
    )

    assert (
        "daily_loss_cap"
        in snapshot[
            "review_checks"
        ]
    )


def test_capsim005_contract_refuses_execution_and_live_authority():
    contract = (
        capital_simulation_contract()
    )

    assert (
        contract[
            "capital_policy_source_status"
        ]
        ==
        "PENDING"
    )

    assert (
        contract[
            "pending_capital_policy_authority"
        ]
        ==
        "PENDING_OBCAP"
    )

    assert (
        contract[
            "daily_loss_canonical_authority"
        ]
        is False
    )

    assert (
        contract[
            "future_daily_loss_authority"
        ]
        ==
        "PENDING_CAPSIM006_010"
    )

    for key in (
        "policy_widening",
        "effective_policy_mutation",
        "simulation_lane_mutation",
        "portfolio_policy_authority",
        "position_selection_authority",
        "strategy_selection_authority",
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


def test_capsim005_module_contains_no_execution_surface():
    from pathlib import Path
    import web.ob_capital_simulation_authority as module

    source = Path(
        module.__file__
    ).read_text(
        encoding="utf-8"
    )

    forbidden = (
        "placeOrder(",
        "submitOrder(",
        "executeTrade(",
        "broker.submit(",
        "moveCapital(",
        "autoSelectContract(",
        "unlockManualLive(",
        "unlockHybrid(",
        "unlockAutomated(",
    )

    for token in forbidden:
        assert token not in source


def test_capsim005_evidence_and_handoff_exist():
    from pathlib import Path

    root = (
        Path(__file__).resolve().parents[1]
    )

    assert (
        root
        / "ob_evidence/simulation/"
        "capsim001_005_capital_simulation_authority.json"
    ).is_file()

    assert (
        root
        / "ob_evidence/simulation/"
        "capsim001_005_capital_simulation_authority_handoff.md"
    ).is_file()
