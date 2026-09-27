"""OBML016–020: redacted OB-side correlation of Tower source namespace observation.

Tower source receipts are NOT an owner authorization bearer token and are not
cryptographically authenticated to OB by this adapter. The canonical Tower
service alone validates the raw signed source and atomically consumes its nonce.
This observational adapter can only flag claim consistency with a separately
reverified OB beta gate report. Every real external gate remains PENDING.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime
from hashlib import sha256
import json
from typing import Mapping

from web.ob_account_identity_truth import resolve_account_identity
from web.ob_manual_live_beta_gate_report import (
    OwnerBetaGateReport, REQUIRED_EXTERNAL_GATES, verify_owner_beta_gate_report,
)
from web.ob_manual_live_owner_preflight import (
    ManualLiveSourceBundle, OwnerManualLivePreflight, OwnerReviewPlan,
)
from web.ob_manual_live_tower_contract_inspection import TowerContractInspection
from web.ob_recovery_review import RecoveryReview

SCHEMA_VERSION = "OB_OWNER_MANUAL_LIVE_NAMESPACE_CROSS_CHECK_V1"
SOURCE_RECEIPT_AUTHORITY = "TOWER_OBML_OB_ACCOUNT_NAMESPACE_SOURCE_RECEIPT_V1"
SOURCE_AUTHORITY = "OB_TOWER_ACCOUNT_IDENTITY_EXPORT_V1"
ISSUER = "observatory-account-identity"
AUDIENCE = "tower-obml-account-check"
SOURCE_KEYS = frozenset((
    "authority", "source_authority", "account_key",
    "account_identity_fingerprint", "issuer", "audience",
    "issued_at_epoch", "expires_at_epoch",
    "signature_verified_with_trusted_injected_key",
    "one_time_nonce_consumed_by_caller_store",
    "owner_authentication_verified", "tower_session_verified",
    "tower_permission_verified", "tower_step_up_verified",
    "tower_revocation_verified", "broker_account_verified",
    "real_capital_verified", "manual_live_granted",
    "broker_order_api_authorized", "capital_movement_authorized",
))
FALSE_CAPABILITIES = (
    "owner_authentication_verified", "tower_session_verified",
    "tower_permission_verified", "tower_step_up_verified",
    "tower_revocation_verified", "broker_account_verified",
    "real_capital_verified", "manual_live_granted",
    "broker_order_api_authorized", "capital_movement_authorized",
)


def _hash(value: object) -> str:
    return sha256(json.dumps(
        value, sort_keys=True, ensure_ascii=True, separators=(",", ":"),
        allow_nan=False,
    ).encode()).hexdigest()


def _report_epoch(value: str) -> int:
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if dt.tzinfo is None or dt.utcoffset() is None:
            raise ValueError("naive timestamp")
        return int(dt.timestamp())
    except (ValueError, TypeError, AttributeError, OverflowError) as exc:
        raise ValueError("source checkpoint requires explicit aware report time") from exc


@dataclass(frozen=True)
class OwnerNamespaceCrossCheck:
    checkpoint_id: str
    authority: str
    account_key: str
    beta_report_id: str
    beta_report_hash: str
    source_cross_check_state: str
    source_claim_fingerprint: str | None
    source_claim_not_independently_authenticated_by_ob: bool
    canonical_beta_report_state: str
    external_gate_ids_still_pending: tuple[str, ...]
    owner_review_is_not_live_permission: bool
    trusted_tower_owner_handoff_verified: bool
    actual_hosted_tower_crossing_verified: bool
    broker_or_bank_account_authenticated: bool
    actual_manual_broker_order_reconciled: bool
    live_manual_mode_unlocked: bool
    broker_order_api_authorized: bool
    capital_movement: bool
    hybrid_or_auto_unlocked: bool
    direct_buybox_access: bool
    integrity_hash: str


def _material(value: OwnerNamespaceCrossCheck) -> dict[str, object]:
    return {
        key: getattr(value, key)
        for key in OwnerNamespaceCrossCheck.__dataclass_fields__
        if key not in ("checkpoint_id", "integrity_hash")
    }


def _source_claim(
    source_receipt: Mapping[str, object] | None, *,
    account_key: str, as_of_epoch: int,
) -> tuple[str, str | None]:
    if source_receipt is None:
        return "MISSING_TOWER_NAMESPACE_SOURCE", None
    if not isinstance(source_receipt, Mapping) or set(source_receipt) != SOURCE_KEYS:
        return "REJECTED_SOURCE_CLAIM", None
    identity = resolve_account_identity(account_key)
    issued = source_receipt.get("issued_at_epoch")
    expires = source_receipt.get("expires_at_epoch")
    if (
        source_receipt.get("authority") != SOURCE_RECEIPT_AUTHORITY
        or source_receipt.get("source_authority") != SOURCE_AUTHORITY
        or source_receipt.get("issuer") != ISSUER
        or source_receipt.get("audience") != AUDIENCE
        or source_receipt.get("account_key") != account_key
        or source_receipt.get("account_identity_fingerprint") != identity["identity_fingerprint"]
        or source_receipt.get("signature_verified_with_trusted_injected_key") is not True
        or source_receipt.get("one_time_nonce_consumed_by_caller_store") is not True
        or any(source_receipt.get(flag) is not False for flag in FALSE_CAPABILITIES)
        or type(issued) is not int or type(expires) is not int
        or not 0 < expires - issued <= 60
        or not issued <= as_of_epoch < expires
    ):
        return "REJECTED_SOURCE_CLAIM", None
    # Only a digest of nonsecret namespace metadata is retained; even this
    # remains a structural claim, NOT Tower issuer/session authentication.
    fingerprint = _hash((
        source_receipt["authority"], account_key,
        source_receipt["account_identity_fingerprint"], issued, expires,
    ))
    return "CONSISTENT_SOURCE_CLAIM_ONLY", fingerprint


def _build(
    report: OwnerBetaGateReport, inspection: TowerContractInspection,
    preflight: OwnerManualLivePreflight, recovery: RecoveryReview,
    source_bundle: ManualLiveSourceBundle, *,
    owner_plan: OwnerReviewPlan | None = None,
    presented: dict[str, object] | None = None,
    as_of_utc: str,
    source_receipt: Mapping[str, object] | None = None,
) -> OwnerNamespaceCrossCheck:
    if not verify_owner_beta_gate_report(
        report, inspection, preflight, recovery, source_bundle,
        owner_plan=owner_plan, presented=presented, as_of_utc=as_of_utc,
    ):
        raise ValueError("namespace cross-check needs independently verified OBML beta source lineage")
    if report.account_key != preflight.account_key:
        raise ValueError("namespace cross-check account mismatch")
    expected_pending = tuple(code for code, _ in REQUIRED_EXTERNAL_GATES)
    if report.external_gate_ids_still_pending != expected_pending:
        raise ValueError("OBML beta report external gate mismatch")
    claim_state, claim_hash = _source_claim(
        source_receipt, account_key=report.account_key,
        as_of_epoch=_report_epoch(report.as_of_utc),
    )
    provisional = OwnerNamespaceCrossCheck(
        checkpoint_id="PENDING", authority=SCHEMA_VERSION,
        account_key=report.account_key,
        beta_report_id=report.report_id, beta_report_hash=report.integrity_hash,
        source_cross_check_state=claim_state, source_claim_fingerprint=claim_hash,
        source_claim_not_independently_authenticated_by_ob=True,
        canonical_beta_report_state=report.report_state,
        external_gate_ids_still_pending=expected_pending,
        owner_review_is_not_live_permission=True,
        trusted_tower_owner_handoff_verified=False,
        actual_hosted_tower_crossing_verified=False,
        broker_or_bank_account_authenticated=False,
        actual_manual_broker_order_reconciled=False,
        live_manual_mode_unlocked=False, broker_order_api_authorized=False,
        capital_movement=False, hybrid_or_auto_unlocked=False,
        direct_buybox_access=False, integrity_hash="PENDING",
    )
    digest = _hash(_material(provisional))
    return replace(provisional, checkpoint_id="OBMLNS-" + digest[:24], integrity_hash=digest)


def verify_owner_namespace_cross_check(
    value: OwnerNamespaceCrossCheck, report: OwnerBetaGateReport,
    inspection: TowerContractInspection, preflight: OwnerManualLivePreflight,
    recovery: RecoveryReview, source_bundle: ManualLiveSourceBundle, *,
    owner_plan: OwnerReviewPlan | None = None,
    presented: dict[str, object] | None = None, as_of_utc: str,
    source_receipt: Mapping[str, object] | None = None,
) -> bool:
    if not isinstance(value, OwnerNamespaceCrossCheck) or value.authority != SCHEMA_VERSION:
        return False
    if value.source_claim_not_independently_authenticated_by_ob is not True or value.owner_review_is_not_live_permission is not True:
        return False
    if any(getattr(value, field) is not False for field in (
        "trusted_tower_owner_handoff_verified", "actual_hosted_tower_crossing_verified",
        "broker_or_bank_account_authenticated", "actual_manual_broker_order_reconciled",
        "live_manual_mode_unlocked", "broker_order_api_authorized", "capital_movement",
        "hybrid_or_auto_unlocked", "direct_buybox_access",
    )):
        return False
    try:
        return value == _build(
            report, inspection, preflight, recovery, source_bundle,
            owner_plan=owner_plan, presented=presented, as_of_utc=as_of_utc,
            source_receipt=source_receipt,
        )
    except (ValueError, TypeError, AttributeError, KeyError, OverflowError):
        return False


def build_owner_namespace_cross_check(
    report: OwnerBetaGateReport, inspection: TowerContractInspection,
    preflight: OwnerManualLivePreflight, recovery: RecoveryReview,
    source_bundle: ManualLiveSourceBundle, *,
    owner_plan: OwnerReviewPlan | None = None,
    presented: dict[str, object] | None = None, as_of_utc: str,
    source_receipt: Mapping[str, object] | None = None,
) -> OwnerNamespaceCrossCheck:
    value = _build(
        report, inspection, preflight, recovery, source_bundle,
        owner_plan=owner_plan, presented=presented, as_of_utc=as_of_utc,
        source_receipt=source_receipt,
    )
    if not verify_owner_namespace_cross_check(
        value, report, inspection, preflight, recovery, source_bundle,
        owner_plan=owner_plan, presented=presented, as_of_utc=as_of_utc,
        source_receipt=source_receipt,
    ):
        raise ValueError("namespace checkpoint failed independent source verification")
    return value


def owner_namespace_cross_check_reference(
    value: OwnerNamespaceCrossCheck, report: OwnerBetaGateReport,
    inspection: TowerContractInspection, preflight: OwnerManualLivePreflight,
    recovery: RecoveryReview, source_bundle: ManualLiveSourceBundle, *,
    owner_plan: OwnerReviewPlan | None = None,
    presented: dict[str, object] | None = None, as_of_utc: str,
    source_receipt: Mapping[str, object] | None = None,
) -> dict[str, object]:
    if not verify_owner_namespace_cross_check(
        value, report, inspection, preflight, recovery, source_bundle,
        owner_plan=owner_plan, presented=presented, as_of_utc=as_of_utc,
        source_receipt=source_receipt,
    ):
        raise ValueError("namespace checkpoint reference needs reverified full beta/source lineage")
    return {
        "authority": SCHEMA_VERSION,
        "checkpoint_id": value.checkpoint_id,
        "integrity_hash": value.integrity_hash,
        "account_key": value.account_key,
        "source_cross_check_state": value.source_cross_check_state,
        "canonical_beta_report_state": value.canonical_beta_report_state,
        "pending_external_gates": list(value.external_gate_ids_still_pending),
        "source_claim_not_independently_authenticated_by_ob": True,
        "owner_or_token_exposed": False, "amounts_exposed": False,
        "manual_live_unlocked": False, "broker_submission": False,
        "capital_movement": False, "tower_owner_clearance_required": True,
    }


def owner_namespace_cross_check_contract() -> dict[str, object]:
    return {
        "authority": SCHEMA_VERSION,
        "upstream_beta_report": "OB_OWNER_BETA_GATE_REPORT_V1",
        "source_receipt_authority": SOURCE_RECEIPT_AUTHORITY,
        "source_claim_is_not_tower_owner_permission": True,
        "source_claim_authenticated_to_ob": False,
        "full_ob_beta_lineage_recomputed": True,
        "real_ob_source_token_validation_remains_tower_owned": True,
        "untrusted_source_claim_cannot_reduce_external_pending_gates": True,
        "live_manual_mode_unlock": False, "broker_order_api": False,
        "capital_movement": False, "hybrid_or_auto_unlock": False,
        "direct_buybox_access": False, "teller_owns_acquisition_readiness": True,
        "production_key_or_nonce_store_configured": False,
        "paid_infrastructure_provisioned": False,
    }
