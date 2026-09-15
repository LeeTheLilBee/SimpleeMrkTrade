from __future__ import annotations

from dataclasses import replace

import pytest

from web.ob_candidate_admission_receipt_binding import (
    admit_receipt_bound_evidence,
    bind_candidate_identity,
    empty_receipt_bound_candidate_set,
    evidence_item_from_context_receipt,
    receipt_bound_candidate_snapshot,
    verify_candidate_admission_receipt,
    verify_receipt_bound_candidate_set,
)
from web.ob_canonical_reasoning_context_spine import (
    authority_result,
    build_canonical_context_identity,
    build_canonical_instrument_identity,
    build_canonical_reasoning_context_receipt,
)
from web.ob_reasoning_context_composition import (
    GateVerdict,
    REQUIRED_GATES,
)


def context_receipt():
    instrument = build_canonical_instrument_identity(
        symbol="AAPL",
        instrument_kind="OPTION",
        contract_id="AAPL-20261218-C-250",
        underlying_symbol="AAPL",
        option_right="CALL",
        strike="250",
        expiration="2026-12-18",
    )

    context = build_canonical_context_identity(
        context_id="CTX-001",
        observation_id="OBS-001",
        observation_version=3,
        lineage_hash="LINEAGE-001",
        provenance_identity="PROV-001",
        reasoning_target_id="TARGET-001",
        instrument=instrument,
        operating_mode="PAPER",
        effective_policy_id="POLICY-001",
        effective_policy_hash="POLICY-HASH-001",
        purpose="analytical reasoning",
    )

    authorities = {
        gate: authority_result(
            gate=gate,
            observation_id="OBS-001",
            observation_version=3,
            reasoning_target_id="TARGET-001",
            symbol="AAPL",
            instrument_kind="OPTION",
            verdict=GateVerdict.ALLOW,
            reason=f"{gate} allow",
            authority_identity=f"AUTH-{gate}",
            authority_hash=f"HASH-{gate}",
        )
        for gate in REQUIRED_GATES
    }

    return build_canonical_reasoning_context_receipt(
        context=context,
        authorities=authorities,
    )


def build_bound():
    receipt = context_receipt()

    identity = bind_candidate_identity(
        candidate_id="CANDIDATE-001",
        purpose="candidate evidence",
        context_receipt=receipt,
    )

    bound_set = empty_receipt_bound_candidate_set(identity)

    item = evidence_item_from_context_receipt(
        identity=identity,
        context_receipt=receipt,
    )

    return receipt, identity, bound_set, item


def test_candidate_identity_is_derived_from_context_receipt():
    receipt, identity, _, _ = build_bound()

    assert identity.context_receipt_id == receipt.receipt_id
    assert identity.candidate.reasoning_target_id == "TARGET-001"
    assert identity.candidate.target_symbol == "AAPL"
    assert identity.candidate.target_instrument_kind == "OPTION"
    assert identity.contract_id == "AAPL-20261218-C-250"


def test_receipt_bound_admission_succeeds():
    _, _, bound_set, item = build_bound()

    result = admit_receipt_bound_evidence(
        bound_set=bound_set,
        bound_item=item,
    )

    assert len(result.evidence_set.items) == 1
    assert len(result.admission_receipts) == 1
    assert verify_candidate_admission_receipt(
        result.admission_receipts[0]
    )
    assert verify_receipt_bound_candidate_set(result)


def test_context_receipt_substitution_is_blocked():
    _, _, bound_set, item = build_bound()

    forged = replace(
        item,
        context_receipt_id="OBCTX-FORGED",
    )

    with pytest.raises(ValueError):
        admit_receipt_bound_evidence(
            bound_set=bound_set,
            bound_item=forged,
        )


def test_set_integrity_is_tamper_evident():
    _, _, bound_set, item = build_bound()

    result = admit_receipt_bound_evidence(
        bound_set=bound_set,
        bound_item=item,
    )

    forged = replace(
        result,
        set_integrity_hash="0" * 64,
    )

    assert not verify_receipt_bound_candidate_set(forged)


def test_duplicate_evidence_remains_blocked():
    _, _, bound_set, item = build_bound()

    result = admit_receipt_bound_evidence(
        bound_set=bound_set,
        bound_item=item,
    )

    with pytest.raises(ValueError):
        admit_receipt_bound_evidence(
            bound_set=result,
            bound_item=item,
        )


def test_snapshot_preserves_authority_boundary():
    _, _, bound_set, item = build_bound()

    result = admit_receipt_bound_evidence(
        bound_set=bound_set,
        bound_item=item,
    )

    boundary = receipt_bound_candidate_snapshot(
        result
    )["authority_boundary"]

    assert boundary["candidate_evidence_admission_only"] is True
    assert boundary["analytical_conclusion"] is False
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
    import web.ob_candidate_admission_receipt_binding as module

    source = Path(module.__file__).read_text(encoding="utf-8")

    for token in (
        "placeOrder(",
        "submitOrder(",
        "executeTrade(",
        "autoSelectContract(",
        "broker.submit(",
    ):
        assert token not in source
