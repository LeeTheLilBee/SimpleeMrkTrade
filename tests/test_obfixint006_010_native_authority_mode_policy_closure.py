
from __future__ import annotations

from dataclasses import dataclass

import pytest

from web.ob_canonical_reasoning_context_spine import (
    GateVerdict,
    authority_result,
    build_canonical_context_identity,
    build_canonical_instrument_identity,
    build_canonical_reasoning_context_receipt,
)
from web.ob_foundation_integrity_certification import (
    certify_foundation_integrity,
)
from web.ob_foundation_integration_closure import (
    build_verified_authority_artifact,
)


def _context():
    instrument = build_canonical_instrument_identity(
        symbol="AAPL",
        instrument_kind="OPTION",
        contract_id="AAPL-20261218-C-250",
        underlying_symbol="AAPL",
        option_right="CALL",
        strike="250",
        expiration="2026-12-18",
    )

    return build_canonical_context_identity(
        context_id="CTX-006-010",
        observation_id="OBS-006-010",
        observation_version=1,
        lineage_hash="lineage-006-010",
        provenance_identity="prov-006-010",
        reasoning_target_id="TARGET-006-010",
        instrument=instrument,
        operating_mode="PAPER",
        effective_policy_id="POLICY-006-010",
        effective_policy_hash="HASH-006-010",
        purpose="analytical reasoning",
    )


def _legacy_authorities():
    return {
        gate: authority_result(
            gate=gate,
            observation_id="OBS-006-010",
            observation_version=1,
            reasoning_target_id="TARGET-006-010",
            symbol="AAPL",
            instrument_kind="OPTION",
            verdict=GateVerdict.ALLOW,
            reason="caller allow",
            authority_identity=f"LEGACY-{gate}",
            authority_hash=f"HASH-{gate}",
        )
        for gate in (
            "source_provenance",
            "freshness",
            "corroboration",
            "quality",
            "effective_observation",
            "conflict",
            "lineage",
            "current_version",
            "lifecycle",
            "revocation",
            "rehabilitation",
            "temporal_validity",
            "instrument_binding",
        )
    }


def test_legacy_context_is_explicitly_uncertified():
    receipt = build_canonical_reasoning_context_receipt(
        context=_context(),
        authorities=_legacy_authorities(),
    )

    assert receipt.certified_native_authority is False
    assert receipt.certified_authority_hash is None


def test_plain_dict_cannot_be_native_authority():
    with pytest.raises(ValueError):
        build_verified_authority_artifact(
            gate="freshness",
            observation_id="OBS-006-010",
            observation_version=1,
            reasoning_target_id="TARGET-006-010",
            symbol="AAPL",
            instrument_kind="OPTION",
            native_authority={"status": "BLOCKED"},
        )


@dataclass(frozen=True)
class FakeAuthority:
    status: str = "ALLOW"


def test_arbitrary_dataclass_cannot_be_native_authority():
    with pytest.raises(ValueError):
        build_verified_authority_artifact(
            gate="freshness",
            observation_id="OBS-006-010",
            observation_version=1,
            reasoning_target_id="TARGET-006-010",
            symbol="AAPL",
            instrument_kind="OPTION",
            native_authority=FakeAuthority(),
        )


def test_foundation_certification_rejects_legacy_context_before_downstream_chain():
    receipt = build_canonical_reasoning_context_receipt(
        context=_context(),
        authorities=_legacy_authorities(),
    )

    with pytest.raises(
        ValueError,
        match="certified native authority context",
    ):
        certify_foundation_integrity(
            context_receipt=receipt,
            candidate_set=None,
            independence_receipt=None,
            requirement_set=None,
            sufficiency_receipt=None,
            conclusion_receipt=None,
        )



def test_certified_builder_does_not_accept_caller_verdict():
    import inspect

    from web.ob_foundation_integration_closure import (
        build_verified_authority_artifact,
    )

    signature = inspect.signature(
        build_verified_authority_artifact
    )

    assert "verdict" not in signature.parameters
    assert "reason" not in signature.parameters
