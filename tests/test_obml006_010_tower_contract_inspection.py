from dataclasses import replace

import pytest

from test_obml001_005_owner_manual_source_preflight import make_sources, plan
from test_obguard001_005_distinct_source_adverse_review import signals
from web.ob_account_identity_truth import resolve_account_identity
from web.ob_manual_live_owner_preflight import build_owner_manual_live_preflight
from web.ob_manual_live_tower_contract_inspection import (
    SCHEMA_VERSION, REQUIRED, FORBIDDEN_GRANTS,
    build_tower_contract_inspection, verify_tower_contract_inspection,
    tower_contract_inspection_reference, tower_contract_inspection_contract,
)

AS_OF = "2026-09-24T15:01:00+00:00"


def sources(*, owner_fit=False, tmp_path=None, alert=None):
    recovery, evidence = make_sources(owner_fit=owner_fit, tmp_path=tmp_path, alert=alert)
    owner = plan(recovery, evidence) if owner_fit else None
    preflight = build_owner_manual_live_preflight(recovery, evidence, owner_plan=owner)
    return preflight, recovery, evidence, owner


def claim(preflight, **changes):
    base = dict(
        issuer="THE_TOWER", audience="THE_OBSERVATORY_OBML_OWNER_READINESS",
        principal_id="opaque-owner", principal_role="OWNER",
        owner_session_id="opaque-session",
        session_binding_hash="f"*64, account_key=preflight.account_key,
        account_identity_fingerprint=resolve_account_identity(preflight.account_key)["identity_fingerprint"],
        purpose="OBML_OWNER_REVIEW", permission="OBML_OWNER_REVIEW",
        launch_route="/tower/launch/observatory",
        issued_at_utc="2026-09-24T15:00:00+00:00",
        expires_at_utc="2026-09-24T15:04:00+00:00",
        nonce="nonce-r1", step_up_event_ref="event-r1",
        step_up_at_utc="2026-09-24T14:58:00+00:00",
        revocation_epoch=1, decision_id="tower-decision-r1",
        verified_tower_attestation=True,
        capability_scope={
            "owner_readiness_review_only": True,
            **{name: False for name in FORBIDDEN_GRANTS},
        },
    )
    return {**base, **changes}


def evaluate(preflight, recovery, evidence, owner, presented=None, as_of=AS_OF):
    return build_tower_contract_inspection(
        preflight, recovery, evidence, owner_plan=owner,
        presented=presented, as_of_utc=as_of,
    )


def test_obml006_missing_tower_proof_yields_read_only_gap():
    preflight, recovery, evidence, owner = sources()
    receipt = evaluate(preflight, recovery, evidence, owner)
    assert receipt.authority == SCHEMA_VERSION
    assert receipt.status == "HOLD_TOWER_CONTRACT_OR_SOURCE_GAP"
    assert receipt.missing_required_fields == REQUIRED
    assert receipt.redacted_claim_fingerprint is None
    assert "TOWER_HANDOFF_MISSING" in receipt.reasons
    assert not receipt.tower_owner_permission_verified
    assert verify_tower_contract_inspection(
        receipt, preflight, recovery, evidence, owner_plan=owner,
        presented=None, as_of_utc=AS_OF,
    )


def test_obml007_complete_but_forged_claim_remains_untrusted_and_no_order(tmp_path):
    preflight, recovery, evidence, owner = sources(owner_fit=True, tmp_path=tmp_path)
    presented = claim(preflight)
    result = evaluate(preflight, recovery, evidence, owner, presented)
    assert result.structural_match_only is True
    assert result.status == "HOLD_TOWER_UNTRUSTED_CLAIM"
    assert "CLIENT_PRESENTED_ATTESTATION_IS_NOT_TRUSTED_TOWER_PROOF" in result.reasons
    assert "TOWER_SERVER_VERIFICATION_UNAVAILABLE_IN_OB" in result.reasons
    assert result.present_required_field_count == len(REQUIRED)
    assert not result.claimed_attestation_treated_as_authentication
    assert not result.live_manual_mode_unlocked and not result.broker_order_authorized
    assert not result.broker_api_submission and not result.capital_movement
    assert verify_tower_contract_inspection(
        result, preflight, recovery, evidence, owner_plan=owner,
        presented=presented, as_of_utc=AS_OF,
    )


@pytest.mark.parametrize(("field", "value", "expected"), (
    ("principal_role", "BETA", "ISSUER_ROLE_AUDIENCE"),
    ("account_key", "personal", "ACCOUNT_IDENTITY_MISMATCH"),
    ("account_identity_fingerprint", "0"*64, "ACCOUNT_IDENTITY_MISMATCH"),
    ("purpose", "OTHER", "ISSUER_ROLE_AUDIENCE"),
    ("audience", "OTHER", "ISSUER_ROLE_AUDIENCE"),
    ("launch_route", "/ob/walkthrough", "ISSUER_ROLE_AUDIENCE"),
    ("issuer", "SELF_ASSERTED", "ISSUER_ROLE_AUDIENCE"),
    ("permission", "AUTO", "ISSUER_ROLE_AUDIENCE"),
    ("issued_at_utc", "2026-09-24T14:00:00+00:00", "TIME_OR_STEP_UP_WINDOW_INVALID"),
    ("expires_at_utc", "2026-09-24T15:00:00+00:00", "TIME_OR_STEP_UP_WINDOW_INVALID"),
    ("step_up_at_utc", "2026-09-24T14:00:00+00:00", "TIME_OR_STEP_UP_WINDOW_INVALID"),
    ("revocation_epoch", -1, "REVOCATION_EPOCH_MALFORMED"),
    ("nonce", "", "REQUIRED_ID_MALFORMED"),
))
def test_obml008_bad_untrusted_claim_stays_denied(field, value, expected):
    preflight, recovery, evidence, owner = sources()
    result = evaluate(preflight, recovery, evidence, owner, claim(preflight, **{field: value}))
    assert expected in " ".join(result.reasons)
    assert result.structural_match_only is False
    assert not result.tower_owner_permission_verified and not result.broker_api_submission


def test_obml008_missing_fields_extra_secret_and_forbidden_caps_do_not_leak():
    preflight, recovery, evidence, owner = sources()
    incomplete = claim(preflight)
    incomplete.pop("owner_session_id")
    a = evaluate(preflight, recovery, evidence, owner, incomplete)
    assert a.missing_required_fields == ("owner_session_id",)
    assert "TOWER_REQUIRED_FIELDS_MISSING" in a.reasons
    secret = claim(preflight, access_token="private-credential-canary")
    b = evaluate(preflight, recovery, evidence, owner, secret)
    assert "RAW_CREDENTIAL_IN_HANDOFF_FORBIDDEN" in b.reasons
    ref = tower_contract_inspection_reference(
        b, preflight, recovery, evidence, owner_plan=owner,
        presented=secret, as_of_utc=AS_OF,
    )
    assert "private-credential-canary" not in repr(b)
    assert "private-credential-canary" not in repr(ref)
    assert ref["amounts_exposed"] is False
    caps = claim(preflight)
    caps["capability_scope"] = {
        **caps["capability_scope"], "broker_order_api": True,
    }
    c = evaluate(preflight, recovery, evidence, owner, caps)
    assert "TOWER_FORBIDDEN_EXECUTION_CAPABILITY_CLAIM" in c.reasons
    assert not c.broker_api_submission


def test_obml009_canonical_block_remains_block_under_claim_and_bad_source_rejected():
    preflight, recovery, evidence, owner = sources(alert=signals(overreach=True))
    result = evaluate(preflight, recovery, evidence, owner, claim(preflight))
    assert result.status == "BLOCKED_CANONICAL_SOURCE"
    assert "UPSTREAM_CANONICAL_SAFETY_BLOCK" in result.reasons
    with pytest.raises(ValueError, match="full canonical preflight"):
        evaluate(replace(preflight, tower_owner_session_authenticated=True),
                 recovery, evidence, owner, claim(preflight))


def test_obml010_integrity_and_no_capability_grants():
    preflight, recovery, evidence, owner = sources()
    receipt = evaluate(preflight, recovery, evidence, owner, claim(preflight))
    assert receipt == evaluate(preflight, recovery, evidence, owner, claim(preflight))
    assert not verify_tower_contract_inspection(
        replace(receipt, tower_owner_permission_verified=True),
        preflight, recovery, evidence, owner_plan=owner,
        presented=claim(preflight), as_of_utc=AS_OF,
    )
    with pytest.raises(ValueError, match="verified full source"):
        tower_contract_inspection_reference(
            replace(receipt, status="LIVE_READY"), preflight, recovery, evidence,
            owner_plan=owner, presented=claim(preflight), as_of_utc=AS_OF,
        )
    c = tower_contract_inspection_contract()
    assert c["requested_tower_contract"] == "TOWER_OBML_OWNER_HANDOFF_REQUEST_V1"
    assert c["presented_claim_can_unlock_manual_live"] is False
    assert c["source_shape_check_is_server_authentication"] is False
    assert c["trusted_issuer_verification_implemented_here"] is False
    for field in ("manual_live_unlock", "hybrid_unlock", "automated_unlock",
                  "broker_submission", "capital_movement", "direct_buybox_access"):
        assert c[field] is False
