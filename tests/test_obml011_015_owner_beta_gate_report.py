from dataclasses import replace

import pytest

from test_obml006_010_tower_contract_inspection import (
    AS_OF, claim, sources, evaluate,
)
from test_obguard001_005_distinct_source_adverse_review import signals
from web.ob_manual_live_beta_gate_report import (
    SCHEMA_VERSION, REQUIRED_EXTERNAL_GATES, SOURCE_GATES,
    build_owner_beta_gate_report, verify_owner_beta_gate_report,
    owner_beta_gate_reference, owner_beta_gate_contract,
)


def chain(*, owner_fit=False, tmp_path=None, alert=None, presented=None):
    preflight, recovery, bundle, owner = sources(
        owner_fit=owner_fit, tmp_path=tmp_path, alert=alert,
    )
    if presented == "well_formed_claim":
        presented = claim(preflight)
    inspection = evaluate(
        preflight, recovery, bundle, owner, presented=presented,
    )
    kwargs = dict(
        inspection=inspection, preflight=preflight, recovery=recovery,
        source_bundle=bundle, owner_plan=owner, presented=presented,
        as_of_utc=AS_OF,
    )
    return kwargs, build_owner_beta_gate_report(**kwargs)


def test_obml011_missing_tower_and_owner_fit_stays_hold_with_all_external_gates():
    kwargs, result = chain()
    assert result.authority == SCHEMA_VERSION
    assert result.report_state == "HOLD_REAL_TOWER_AND_PROVIDER_GATES"
    assert result.canonical_recommendation_state == "EVIDENCE_PENDING"
    assert "TOWER_HANDOFF_MISSING" in result.upstream_reason_codes
    assert "CANONICAL_OWNER_REVIEW_NOT_READY" in result.upstream_reason_codes
    assert result.external_gate_ids_still_pending == tuple(g for g, _ in REQUIRED_EXTERNAL_GATES)
    assert len(result.gate_records) == len(SOURCE_GATES) + len(REQUIRED_EXTERNAL_GATES)
    assert all(not gate.live_authority_granted and not gate.externally_authenticated for gate in result.gate_records)
    assert verify_owner_beta_gate_report(result, **kwargs)


def test_obml012_full_claim_shape_cannot_grant_server_authority_or_spendability(tmp_path):
    kwargs, result = chain(
        owner_fit=True, tmp_path=tmp_path, presented="well_formed_claim",
    )
    assert result.structural_tower_claim_matches is True
    assert result.gate_records[2].state == "STRUCTURE_ONLY_UNTRUSTED"
    assert result.report_state == "HOLD_REAL_TOWER_AND_PROVIDER_GATES"
    assert not result.tower_server_grant_verified
    assert not result.actual_hosted_beta_access_verified
    assert not result.broker_or_bank_provenance_verified
    assert not result.manual_live_unlocked and not result.actual_broker_fill_verified
    ref = owner_beta_gate_reference(result, **kwargs)
    assert ref["amounts_exposed"] is False and ref["tower_authorization_required"] is True
    assert "nonce-r1" not in repr(result) and "opaque-owner" not in repr(ref)
    assert ref["pending_external_gates"] == list(result.external_gate_ids_still_pending)


@pytest.mark.parametrize("danger", (
    "overreach", "negative_dive", "overtime", "source_conflict", "kill_switch_engaged",
))
def test_obml013_canonical_block_takes_priority_over_well_formed_tower_claim(danger):
    kwargs, result = chain(alert=signals(**{danger: True}), presented="well_formed_claim")
    assert result.report_state == "BLOCKED_CANONICAL_SOURCE"
    assert result.gate_records[0].state == "BLOCKED_CANONICAL_SOURCE"
    assert result.gate_records[2].state == "BLOCKED_UPSTREAM"
    assert result.external_gate_ids_still_pending
    assert not result.safety_block_dismissed and not result.order_api_enabled


def test_obml014_tampered_inspection_source_and_wrong_owner_account_fail_closed(tmp_path):
    kwargs, result = chain(owner_fit=True, tmp_path=tmp_path)
    assert not verify_owner_beta_gate_report(
        replace(result, tower_server_grant_verified=True), **kwargs,
    )
    assert not verify_owner_beta_gate_report(
        replace(result, external_gate_ids_still_pending=()), **kwargs,
    )
    bad_inspection = {**kwargs, "inspection": replace(
        kwargs["inspection"], integrity_hash="0"*64,
    )}
    with pytest.raises(ValueError, match="verified full Tower/source"):
        build_owner_beta_gate_report(**bad_inspection)
    bad_recovery = {**kwargs, "recovery": replace(
        kwargs["recovery"], account_key="personal",
    )}
    with pytest.raises(ValueError, match="verified full Tower/source"):
        build_owner_beta_gate_report(**bad_recovery)
    with pytest.raises(ValueError, match="fully reverified source"):
        owner_beta_gate_reference(
            replace(result, report_state="PRODUCTION_READY"), **kwargs,
        )


def test_obml015_report_is_deterministic_and_no_new_live_authority(tmp_path):
    kwargs, result = chain(owner_fit=True, tmp_path=tmp_path)
    assert result == build_owner_beta_gate_report(**kwargs)
    assert result.paper_rehearsal_is_not_production
    assert all(x.state == "PENDING_INDEPENDENT_PROOF" for x in result.gate_records[3:])
    for name in (
        "tower_server_grant_verified", "manual_live_unlocked",
        "broker_or_bank_provenance_verified", "actual_broker_fill_verified",
        "order_api_enabled", "capital_movement", "safety_block_dismissed",
        "source_truth_mutated", "hybrid_or_automated_enabled", "direct_buybox_access",
    ):
        assert getattr(result, name) is False
    contract = owner_beta_gate_contract()
    assert contract["full_source_lineage_revalidated"] is True
    assert contract["external_gate_evidence_accepted_from_untrusted_caller"] is False
    assert contract["no_additional_authentication_engine"] is True
    assert contract["direct_buybox_access"] is False
    assert contract["teller_owns_financial_readiness"] is True
    for name in ("manual_live_unlock", "broker_submission", "capital_movement",
                 "mode_change", "hybrid_unlock", "automated_unlock"):
        assert contract[name] is False
