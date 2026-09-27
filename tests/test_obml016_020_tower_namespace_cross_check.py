"""OBML016–020: accepted #80/#82/#84 real wire compatibility never grants OBML."""
from dataclasses import asdict, replace
from datetime import datetime
from hashlib import sha256

import pytest

from test_obml011_015_owner_beta_gate_report import chain
from test_obguard001_005_distinct_source_adverse_review import signals
from tower.obml_account_namespace_source import (
    NamespaceSourceRefused, verify_ob_account_namespace_source,
)
from tower.obml_local_source_nonce_ledger import LocalSQLiteSourceNonceLedger
from web.ob_tower_account_identity_export import create_ob_account_identity_export
from web.ob_manual_live_namespace_cross_check import (
    SCHEMA_VERSION, SOURCE_KEYS, build_owner_namespace_cross_check,
    verify_owner_namespace_cross_check, owner_namespace_cross_check_reference,
    owner_namespace_cross_check_contract,
)

KEY = b"synthetic-only-obml-namespace-cross-check-signing-key-v1-abcdef"
WRONG = b"synthetic-only-obml-namespace-cross-check-WRONG-key-v1-abc"


def inputs(*, tmp_path=None, alert=None):
    args, report = chain(owner_fit=tmp_path is not None, tmp_path=tmp_path, alert=alert)
    return report, args


def actual_tower_source(args, tmp_path, *, account=None, signing_key=KEY, verify_key=KEY):
    account = args["preflight"].account_key if account is None else account
    epoch = int(datetime.fromisoformat(args["as_of_utc"].replace("Z", "+00:00")).timestamp())
    token = create_ob_account_identity_export(account, now_epoch=epoch, signing_secret=signing_key)
    ledger = LocalSQLiteSourceNonceLedger(tmp_path / "source-namespace-nonces.sqlite3")
    receipt = verify_ob_account_namespace_source(
        token, now_epoch=epoch, verification_key=verify_key,
        consume_once=ledger.consume_once,
    )
    return token, receipt, ledger, epoch


def test_obml016_missing_tower_source_keeps_all_real_gates_pending():
    report, args = inputs()
    result = build_owner_namespace_cross_check(report, **args)
    assert result.authority == SCHEMA_VERSION
    assert result.source_cross_check_state == "MISSING_TOWER_NAMESPACE_SOURCE"
    assert result.canonical_beta_report_state == report.report_state
    assert result.external_gate_ids_still_pending == report.external_gate_ids_still_pending
    assert result.source_claim_fingerprint is None
    assert not result.trusted_tower_owner_handoff_verified
    assert verify_owner_namespace_cross_check(result, report, **args)


def test_obml017_actual_export_receiver_durable_source_is_only_claim_correlation(tmp_path):
    report, args = inputs(tmp_path=tmp_path)
    token, receipt, ledger, epoch = actual_tower_source(args, tmp_path)
    assert receipt.signature_verified_with_trusted_injected_key is True
    assert receipt.one_time_nonce_consumed_by_caller_store is True
    assert receipt.manual_live_granted is False and receipt.tower_permission_verified is False
    observed = asdict(receipt)
    assert set(observed) == SOURCE_KEYS
    item = build_owner_namespace_cross_check(report, **args, source_receipt=observed)
    assert item.source_cross_check_state == "CONSISTENT_SOURCE_CLAIM_ONLY"
    assert item.source_claim_not_independently_authenticated_by_ob is True
    assert item.source_claim_fingerprint and token not in repr(item)
    assert item.external_gate_ids_still_pending == report.external_gate_ids_still_pending
    assert item.canonical_beta_report_state == report.report_state
    assert not item.live_manual_mode_unlocked and not item.broker_order_api_authorized
    assert not item.capital_movement and not item.hybrid_or_auto_unlocked
    assert verify_owner_namespace_cross_check(item, report, **args, source_receipt=observed)
    reference = owner_namespace_cross_check_reference(item, report, **args, source_receipt=observed)
    assert reference["amounts_exposed"] is False and reference["owner_or_token_exposed"] is False
    assert reference["pending_external_gates"] == list(report.external_gate_ids_still_pending)
    reopened = LocalSQLiteSourceNonceLedger(tmp_path / "source-namespace-nonces.sqlite3")
    with pytest.raises(NamespaceSourceRefused):
        verify_ob_account_namespace_source(
            token, now_epoch=epoch, verification_key=KEY,
            consume_once=reopened.consume_once,
        )


def test_obml018_wrong_key_expiry_cross_account_and_proof_demo_denied(tmp_path):
    report, args = inputs(tmp_path=tmp_path)
    epoch = int(datetime.fromisoformat(args["as_of_utc"].replace("Z", "+00:00")).timestamp())
    token = create_ob_account_identity_export("trust", now_epoch=epoch, signing_secret=KEY)
    ledger = LocalSQLiteSourceNonceLedger(tmp_path / "bad-source.sqlite3")
    with pytest.raises(NamespaceSourceRefused):
        verify_ob_account_namespace_source(
            token, now_epoch=epoch, verification_key=WRONG,
            consume_once=ledger.consume_once,
        )
    with pytest.raises(NamespaceSourceRefused):
        verify_ob_account_namespace_source(
            token, now_epoch=epoch + 60, verification_key=KEY,
            consume_once=ledger.consume_once,
        )
    _, valid, _, _ = actual_tower_source(args, tmp_path, account="personal")
    item = build_owner_namespace_cross_check(report, **args, source_receipt=asdict(valid))
    assert item.source_cross_check_state == "REJECTED_SOURCE_CLAIM"
    assert item.source_claim_fingerprint is None
    from web.ob_tower_account_identity_export import OBAccountIdentityExportError
    with pytest.raises(OBAccountIdentityExportError):
        create_ob_account_identity_export("proof_demo", now_epoch=epoch, signing_secret=KEY)


def test_obml018_reject_expired_or_malformed_claim_without_leaking_secret(tmp_path):
    report, args = inputs(tmp_path=tmp_path)
    _, receipt, _, _ = actual_tower_source(args, tmp_path)
    claim = asdict(receipt)
    for bad in (
        {**claim, "expires_at_epoch": claim["issued_at_epoch"]},
        {**claim, "one_time_nonce_consumed_by_caller_store": False},
        {**claim, "owner_authentication_verified": True},
        {**claim, "manual_live_granted": True},
        {**claim, "capital_movement_authorized": True},
        {**claim, "account_identity_fingerprint": "0"*64},
        {**claim, "raw_token": "secret-should-never-echo"},
        {"access_token": "secret-should-never-echo"},
    ):
        item = build_owner_namespace_cross_check(report, **args, source_receipt=bad)
        assert item.source_cross_check_state == "REJECTED_SOURCE_CLAIM"
        assert item.source_claim_fingerprint is None
        assert "secret-should-never-echo" not in repr(item)
        assert item.external_gate_ids_still_pending == report.external_gate_ids_still_pending
        assert not item.live_manual_mode_unlocked


def test_obml019_forged_matching_source_receipt_does_not_authenticate_to_ob(tmp_path):
    report, args = inputs(tmp_path=tmp_path)
    _, receipt, _, _ = actual_tower_source(args, tmp_path)
    # Deliberately forge an identical in-memory mapping. OB cannot prove it came
    # from the Tower verifier without a separate trusted issuer/transport.
    forged_claim = {**asdict(receipt)}
    correlated = build_owner_namespace_cross_check(report, **args, source_receipt=forged_claim)
    assert correlated.source_cross_check_state == "CONSISTENT_SOURCE_CLAIM_ONLY"
    assert correlated.source_claim_not_independently_authenticated_by_ob is True
    assert correlated.trusted_tower_owner_handoff_verified is False
    assert all((
        not correlated.actual_hosted_tower_crossing_verified,
        not correlated.broker_or_bank_account_authenticated,
        not correlated.live_manual_mode_unlocked,
        not correlated.capital_movement,
    ))


def test_obml019_canonical_safety_block_cannot_be_overridden_by_good_namespace(tmp_path):
    report, args = inputs(tmp_path=tmp_path, alert=signals(overreach=True))
    _, source, _, _ = actual_tower_source(args, tmp_path)
    item = build_owner_namespace_cross_check(report, **args, source_receipt=asdict(source))
    assert report.report_state == "BLOCKED_CANONICAL_SOURCE"
    assert item.canonical_beta_report_state == "BLOCKED_CANONICAL_SOURCE"
    assert item.source_cross_check_state == "CONSISTENT_SOURCE_CLAIM_ONLY"
    assert item.external_gate_ids_still_pending == report.external_gate_ids_still_pending
    assert not item.live_manual_mode_unlocked


def test_obml020_revalidation_detects_tampered_report_and_forged_clearance(tmp_path):
    report, args = inputs(tmp_path=tmp_path)
    _, receipt, _, _ = actual_tower_source(args, tmp_path)
    claim = asdict(receipt)
    result = build_owner_namespace_cross_check(report, **args, source_receipt=claim)
    assert not verify_owner_namespace_cross_check(
        replace(result, trusted_tower_owner_handoff_verified=True),
        report, **args, source_receipt=claim,
    )
    assert not verify_owner_namespace_cross_check(
        replace(result, external_gate_ids_still_pending=()),
        report, **args, source_receipt=claim,
    )
    assert not verify_owner_namespace_cross_check(
        replace(result, source_cross_check_state="OWNER_CLEARED"),
        report, **args, source_receipt=claim,
    )
    with pytest.raises(ValueError, match="independently verified OBML beta"):
        build_owner_namespace_cross_check(
            replace(report, tower_server_grant_verified=True), **args,
            source_receipt=claim,
        )
    with pytest.raises(ValueError, match="reverified full beta"):
        owner_namespace_cross_check_reference(
            replace(result, integrity_hash="0"*64),
            report, **args, source_receipt=claim,
        )
    c = owner_namespace_cross_check_contract()
    assert c["source_claim_authenticated_to_ob"] is False
    assert c["real_ob_source_token_validation_remains_tower_owned"] is True
    assert c["full_ob_beta_lineage_recomputed"] is True
    assert c["untrusted_source_claim_cannot_reduce_external_pending_gates"] is True
    assert c["direct_buybox_access"] is False
    for name in ("live_manual_mode_unlock", "broker_order_api", "capital_movement",
                 "hybrid_or_auto_unlock", "production_key_or_nonce_store_configured",
                 "paid_infrastructure_provisioned"):
        assert c[name] is False
