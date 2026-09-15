from __future__ import annotations

from dataclasses import replace

import pytest

from web.ob_canonical_reasoning_context_spine import (
    SpineReason,
    SpineState,
    authority_result,
    build_canonical_context_identity,
    build_canonical_instrument_identity,
    build_canonical_reasoning_context_receipt,
    canonical_context_eligible,
    canonical_context_snapshot,
    verify_canonical_reasoning_context_receipt,
)
from web.ob_reasoning_context_composition import (
    GateVerdict,
    REQUIRED_GATES,
)


def instrument():
    return build_canonical_instrument_identity(
        symbol="AAPL",
        instrument_kind="OPTION",
        contract_id="AAPL-20261218-C-250",
        underlying_symbol="AAPL",
        option_right="CALL",
        strike="250",
        expiration="2026-12-18",
    )


def context():
    return build_canonical_context_identity(
        context_id="CTX-001",
        observation_id="OBS-001",
        observation_version=7,
        lineage_hash="lineage-abc",
        provenance_identity="PROV-001",
        reasoning_target_id="TARGET-001",
        instrument=instrument(),
        operating_mode="PAPER",
        effective_policy_id="POLICY-001",
        effective_policy_hash="policy-hash-001",
        purpose="current analytical reasoning",
    )


def authorities(verdict=GateVerdict.ALLOW):
    return {
        gate: authority_result(
            gate=gate,
            observation_id="OBS-001",
            observation_version=7,
            reasoning_target_id="TARGET-001",
            symbol="AAPL",
            instrument_kind="OPTION",
            verdict=verdict,
            reason=f"{gate} canonical authority result",
            authority_identity=f"AUTH-{gate}",
            authority_hash=f"HASH-{gate}",
        )
        for gate in REQUIRED_GATES
    }


def test_exact_option_identity_is_required():
    with pytest.raises(ValueError):
        build_canonical_instrument_identity(
            symbol="AAPL",
            instrument_kind="OPTION",
        )


def test_all_canonical_allow_results_produce_eligible_receipt():
    receipt = build_canonical_reasoning_context_receipt(
        context=context(),
        authorities=authorities(),
    )

    assert receipt.state is SpineState.ELIGIBLE
    assert receipt.reason is SpineReason.CONTEXT_INTEGRITY_SATISFIED
    assert canonical_context_eligible(receipt)
    assert verify_canonical_reasoning_context_receipt(receipt)


def test_missing_authority_fails_closed():
    items = authorities()
    del items["freshness"]

    receipt = build_canonical_reasoning_context_receipt(
        context=context(),
        authorities=items,
    )

    assert receipt.state is SpineState.UNKNOWN
    assert receipt.reason is SpineReason.MISSING_AUTHORITY
    assert not canonical_context_eligible(receipt)


def test_identity_substitution_fails_closed():
    items = authorities()

    items["quality"] = replace(
        items["quality"],
        observation_version=8,
    )

    receipt = build_canonical_reasoning_context_receipt(
        context=context(),
        authorities=items,
    )

    assert receipt.state is SpineState.UNKNOWN
    assert receipt.reason is SpineReason.IDENTITY_MISMATCH
    assert not canonical_context_eligible(receipt)


def test_upstream_block_propagates():
    items = authorities()

    items["revocation"] = replace(
        items["revocation"],
        verdict=GateVerdict.BLOCK,
        reason="observation revoked",
    )

    receipt = build_canonical_reasoning_context_receipt(
        context=context(),
        authorities=items,
    )

    assert receipt.state is SpineState.BLOCKED
    assert receipt.reason is SpineReason.UPSTREAM_BLOCKED
    assert not canonical_context_eligible(receipt)


def test_upstream_review_propagates():
    items = authorities()

    items["conflict"] = replace(
        items["conflict"],
        verdict=GateVerdict.REVIEW,
        reason="unresolved conflict",
    )

    receipt = build_canonical_reasoning_context_receipt(
        context=context(),
        authorities=items,
    )

    assert receipt.state is SpineState.REVIEW_REQUIRED
    assert receipt.reason is SpineReason.UPSTREAM_REVIEW_REQUIRED
    assert not canonical_context_eligible(receipt)


def test_receipt_is_tamper_evident():
    receipt = build_canonical_reasoning_context_receipt(
        context=context(),
        authorities=authorities(),
    )

    tampered = replace(
        receipt,
        integrity_hash="0" * 64,
    )

    assert not verify_canonical_reasoning_context_receipt(tampered)
    assert not canonical_context_eligible(tampered)


def test_receipt_identity_is_deterministic():
    first = build_canonical_reasoning_context_receipt(
        context=context(),
        authorities=authorities(),
    )

    second = build_canonical_reasoning_context_receipt(
        context=context(),
        authorities=authorities(),
    )

    assert first.receipt_id == second.receipt_id
    assert first.integrity_hash == second.integrity_hash


def test_snapshot_preserves_execution_boundary():
    receipt = build_canonical_reasoning_context_receipt(
        context=context(),
        authorities=authorities(),
    )

    boundary = canonical_context_snapshot(receipt)["authority_boundary"]

    assert boundary["analytical_context_integrity_only"] is True
    assert boundary["trade_recommendation"] is False
    assert boundary["trade_ranking"] is False
    assert boundary["contract_auto_selection"] is False
    assert boundary["broker_submission"] is False
    assert boundary["capital_movement"] is False
    assert boundary["manual_live_unlock"] is False
    assert boundary["hybrid_execution"] is False
    assert boundary["automated_execution"] is False


def test_runtime_contains_no_execution_calls():
    from pathlib import Path
    import web.ob_canonical_reasoning_context_spine as module

    source = Path(module.__file__).read_text(encoding="utf-8")

    forbidden = (
        "placeOrder(",
        "submitOrder(",
        "executeTrade(",
        "autoSelectContract(",
        "broker.submit(",
    )

    for token in forbidden:
        assert token not in source
