"""OBML006–010: inspect untrusted Tower handoff shape without granting authority.

Tower PR #68 is a request, not an implemented server-verification endpoint.
Only Tower's trusted server can authenticate issuer/session/step-up, consume nonce,
check revocation and authorize an owner review. This code is a defensive,
read-only compatibility and gap report, never a token or permission validator.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime, timezone, timedelta
from hashlib import sha256
import json

from web.ob_account_identity_truth import resolve_account_identity
from web.ob_manual_live_owner_preflight import (
    ManualLiveSourceBundle, OwnerManualLivePreflight, OwnerReviewPlan,
    verify_owner_manual_live_preflight,
)
from web.ob_recovery_review import RecoveryReview

SCHEMA_VERSION = "OB_OWNER_MANUAL_LIVE_TOWER_CONTRACT_INSPECTION_V1"
REQUEST_VERSION = "TOWER_OBML_OWNER_HANDOFF_REQUEST_V1"
REQUIRED = (
    "issuer", "audience", "principal_id", "principal_role", "owner_session_id",
    "session_binding_hash", "account_key", "account_identity_fingerprint",
    "purpose", "permission", "launch_route", "issued_at_utc", "expires_at_utc",
    "nonce", "step_up_event_ref", "step_up_at_utc", "revocation_epoch",
    "decision_id", "verified_tower_attestation",
)
# These are *shape* constraints, not authentication or an independent Tower policy.
EXPECTED = {
    "issuer": "THE_TOWER",
    "audience": "THE_OBSERVATORY_OBML_OWNER_READINESS",
    "principal_role": "OWNER",
    "purpose": "OBML_OWNER_REVIEW",
    "permission": "OBML_OWNER_REVIEW",
    "launch_route": "/tower/launch/observatory",
}
FORBIDDEN_GRANTS = (
    "trade_intent_creation", "order_authorized", "broker_order_api",
    "automatic_execution", "hybrid_execution", "capital_movement",
    "protected_floor_release", "safety_clearance_override",
)
SECRET_FIELDS = frozenset((
    "access_token", "refresh_token", "session_cookie", "password",
    "private_key", "broker_token", "broker_api_key", "raw_keycard",
))
PENDING_AUTHENTICATION = (
    "TOWER_SERVER_VERIFICATION_UNAVAILABLE_IN_OB",
    "ISSUER_SIGNATURE_NOT_VERIFIED_BY_TRUSTED_SERVER",
    "OWNER_SESSION_AND_STEP_UP_NOT_VERIFIED_BY_TOWER",
    "NONCE_CONSUMPTION_AND_REVOCATION_NOT_VERIFIED_BY_TOWER",
    "PROVIDER_ACCOUNT_AND_LIVE_TRADING_GATES_REMAIN_CLOSED",
)


def _digest(value: object) -> str:
    return sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()).hexdigest()


def _instant(value: object) -> datetime | None:
    if not isinstance(value, str):
        return None
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return dt.astimezone(timezone.utc) if dt.tzinfo and dt.utcoffset() is not None else None
    except ValueError:
        return None


@dataclass(frozen=True)
class TowerContractInspection:
    inspection_id: str
    authority: str
    preflight_id: str
    preflight_hash: str
    account_key: str
    requested_contract: str
    presented_claim_present: bool
    structural_match_only: bool
    status: str
    reasons: tuple[str, ...]
    present_required_field_count: int
    missing_required_fields: tuple[str, ...]
    redacted_claim_fingerprint: str | None
    claimed_attestation_treated_as_authentication: bool
    tower_owner_permission_verified: bool
    live_manual_mode_unlocked: bool
    broker_order_authorized: bool
    broker_api_submission: bool
    capital_movement: bool
    safety_override: bool
    integrity_hash: str


def _material(value: TowerContractInspection) -> dict[str, object]:
    return {
        k: getattr(value, k)
        for k in TowerContractInspection.__dataclass_fields__
        if k not in ("inspection_id", "integrity_hash")
    }


def _build(
    preflight: OwnerManualLivePreflight, recovery: RecoveryReview,
    source_bundle: ManualLiveSourceBundle, *,
    owner_plan: OwnerReviewPlan | None = None,
    presented: dict[str, object] | None = None,
    as_of_utc: str,
) -> TowerContractInspection:
    if not verify_owner_manual_live_preflight(
        preflight, recovery, source_bundle, owner_plan=owner_plan,
    ):
        raise ValueError("OBML Tower intake requires full canonical preflight and recovery lineage")
    as_of = _instant(as_of_utc)
    if as_of is None:
        raise ValueError("inspection timestamp must be explicit and UTC-aware")
    if not isinstance(presented, (dict, type(None))):
        raise ValueError("presented Tower handoff must be an untrusted object or missing")
    claim = presented or {}
    reasons = set(PENDING_AUTHENTICATION)
    if preflight.status.startswith("BLOCKED"):
        reasons.add("UPSTREAM_CANONICAL_SAFETY_BLOCK")
    if owner_plan is None:
        reasons.add("OWNER_REVIEW_PLAN_NOT_PRESENT")
    if preflight.canonical_mode != "MANUAL_LIVE_1":
        reasons.add("CANONICAL_MODE_NOT_MANUAL_LIVE_1")
    if not presented:
        reasons.add("TOWER_HANDOFF_MISSING")
    missing = tuple(k for k in REQUIRED if k not in claim)
    if missing:
        reasons.add("TOWER_REQUIRED_FIELDS_MISSING")
    if any(k in claim for k in SECRET_FIELDS):
        reasons.add("RAW_CREDENTIAL_IN_HANDOFF_FORBIDDEN")
    if any(claim.get(k) != v for k, v in EXPECTED.items()):
        reasons.add("TOWER_CLAIM_ISSUER_ROLE_AUDIENCE_PURPOSE_PERMISSION_OR_ROUTE_MISMATCH")
    identity = resolve_account_identity(preflight.account_key)
    if (
        identity.get("known") is not True or
        claim.get("account_key") != preflight.account_key or
        claim.get("account_identity_fingerprint") != identity.get("identity_fingerprint")
    ):
        reasons.add("TOWER_ACCOUNT_IDENTITY_MISMATCH")
    for key in ("principal_id", "owner_session_id", "session_binding_hash",
                "nonce", "step_up_event_ref", "decision_id"):
        value = claim.get(key)
        if not isinstance(value, str) or not value or value.strip() != value:
            reasons.add("TOWER_REQUIRED_ID_MALFORMED")
    rev = claim.get("revocation_epoch")
    if type(rev) is not int or rev < 0:
        reasons.add("TOWER_REVOCATION_EPOCH_MALFORMED")
    issued = _instant(claim.get("issued_at_utc"))
    expires = _instant(claim.get("expires_at_utc"))
    step_up = _instant(claim.get("step_up_at_utc"))
    if (
        issued is None or expires is None or step_up is None or
        not step_up <= issued <= as_of < expires or
        expires - issued > timedelta(minutes=5) or
        issued - step_up > timedelta(minutes=5)
    ):
        reasons.add("TOWER_CLAIM_TIME_OR_STEP_UP_WINDOW_INVALID")
    caps = claim.get("capability_scope")
    if not isinstance(caps, dict) or any(caps.get(k) is not False for k in FORBIDDEN_GRANTS):
        reasons.add("TOWER_FORBIDDEN_EXECUTION_CAPABILITY_CLAIM")
    if not isinstance(caps, dict) or caps.get("owner_readiness_review_only") is not True:
        reasons.add("TOWER_REVIEW_ONLY_SCOPE_MISSING")
    # No OB-side test of the asserted verified_tower_attestation field could
    # authenticate the issuer: even a syntactically plausible claim stays HOLD.
    if claim.get("verified_tower_attestation") is not None:
        reasons.add("CLIENT_PRESENTED_ATTESTATION_IS_NOT_TRUSTED_TOWER_PROOF")
    else:
        reasons.add("TOWER_SERVER_ATTESTATION_UNAVAILABLE")
    shape_errors = reasons.difference(PENDING_AUTHENTICATION).difference((
        "CLIENT_PRESENTED_ATTESTATION_IS_NOT_TRUSTED_TOWER_PROOF",
        "TOWER_SERVER_ATTESTATION_UNAVAILABLE",
        "UPSTREAM_CANONICAL_SAFETY_BLOCK",
        "OWNER_REVIEW_PLAN_NOT_PRESENT",
        "CANONICAL_MODE_NOT_MANUAL_LIVE_1",
    ))
    # Exclude credential and identifier values from output; digest only
    # a redacted structural profile, not a user-controlled token or keycard.
    fingerprint = _digest({
        "keys": sorted(claim.keys()),
        "shape_errors": sorted(shape_errors),
        "expected_matches": sorted(k for k, v in EXPECTED.items() if claim.get(k) == v),
        "account_fingerprint_match": claim.get("account_identity_fingerprint") == identity.get("identity_fingerprint"),
        "caps_forbidden_are_false": isinstance(caps, dict) and all(caps.get(k) is False for k in FORBIDDEN_GRANTS),
    }) if presented else None
    provisional = TowerContractInspection(
        inspection_id="PENDING", authority=SCHEMA_VERSION,
        preflight_id=preflight.preflight_id, preflight_hash=preflight.integrity_hash,
        account_key=preflight.account_key, requested_contract=REQUEST_VERSION,
        presented_claim_present=presented is not None,
        structural_match_only=presented is not None and not shape_errors,
        status=("BLOCKED_CANONICAL_SOURCE" if preflight.status.startswith("BLOCKED") else
                "HOLD_TOWER_UNTRUSTED_CLAIM" if presented is not None and not shape_errors else
                "HOLD_TOWER_CONTRACT_OR_SOURCE_GAP"),
        reasons=tuple(sorted(reasons)), present_required_field_count=len(REQUIRED) - len(missing),
        missing_required_fields=missing, redacted_claim_fingerprint=fingerprint,
        claimed_attestation_treated_as_authentication=False,
        tower_owner_permission_verified=False, live_manual_mode_unlocked=False,
        broker_order_authorized=False, broker_api_submission=False,
        capital_movement=False, safety_override=False, integrity_hash="PENDING",
    )
    digest = _digest(_material(provisional))
    return replace(provisional, inspection_id="OBMLTWR-" + digest[:24], integrity_hash=digest)


def verify_tower_contract_inspection(
    value: TowerContractInspection, preflight: OwnerManualLivePreflight,
    recovery: RecoveryReview, source_bundle: ManualLiveSourceBundle, *,
    owner_plan: OwnerReviewPlan | None = None,
    presented: dict[str, object] | None = None,
    as_of_utc: str,
) -> bool:
    if not isinstance(value, TowerContractInspection) or value.authority != SCHEMA_VERSION:
        return False
    if any(getattr(value, k) is not False for k in (
        "claimed_attestation_treated_as_authentication", "tower_owner_permission_verified",
        "live_manual_mode_unlocked", "broker_order_authorized", "broker_api_submission",
        "capital_movement", "safety_override",
    )):
        return False
    try:
        return value == _build(
            preflight, recovery, source_bundle, owner_plan=owner_plan,
            presented=presented, as_of_utc=as_of_utc,
        )
    except (ValueError, TypeError, AttributeError, KeyError):
        return False


def build_tower_contract_inspection(
    preflight: OwnerManualLivePreflight, recovery: RecoveryReview,
    source_bundle: ManualLiveSourceBundle, *, owner_plan: OwnerReviewPlan | None = None,
    presented: dict[str, object] | None = None, as_of_utc: str,
) -> TowerContractInspection:
    value = _build(
        preflight, recovery, source_bundle, owner_plan=owner_plan,
        presented=presented, as_of_utc=as_of_utc,
    )
    if not verify_tower_contract_inspection(
        value, preflight, recovery, source_bundle, owner_plan=owner_plan,
        presented=presented, as_of_utc=as_of_utc,
    ):
        raise ValueError("OBML Tower inspection failed source-bound recomputation")
    return value


def tower_contract_inspection_reference(
    value: TowerContractInspection, preflight: OwnerManualLivePreflight,
    recovery: RecoveryReview, source_bundle: ManualLiveSourceBundle, *,
    owner_plan: OwnerReviewPlan | None = None,
    presented: dict[str, object] | None = None, as_of_utc: str,
) -> dict[str, object]:
    if not verify_tower_contract_inspection(
        value, preflight, recovery, source_bundle, owner_plan=owner_plan,
        presented=presented, as_of_utc=as_of_utc,
    ):
        raise ValueError("Tower contract reference requires verified full source lineage")
    return {
        "authority": SCHEMA_VERSION, "inspection_id": value.inspection_id,
        "integrity_hash": value.integrity_hash, "account_key": value.account_key,
        "status": value.status, "reason_codes": list(value.reasons),
        "missing_required_fields": list(value.missing_required_fields),
        "claim_shape_only": value.structural_match_only, "amounts_exposed": False,
        "tower_owner_permission_verified": False, "broker_submission": False,
        "capital_movement": False, "tower_authorization_required": True,
    }


def tower_contract_inspection_contract() -> dict[str, object]:
    return {
        "authority": SCHEMA_VERSION,
        "requested_tower_contract": REQUEST_VERSION,
        "tower_source_pr": 68, "upstream_authority": "OB_OWNER_MANUAL_LIVE_SOURCE_PREFLIGHT_V1",
        "required_fields": list(REQUIRED), "forbidden_grants": list(FORBIDDEN_GRANTS),
        "source_shape_check_is_server_authentication": False,
        "presented_claim_can_unlock_manual_live": False,
        "trusted_issuer_verification_implemented_here": False,
        "nonce_replay_or_revocation_verification_implemented_here": False,
        "owner_places_any_eventual_order_at_broker_application": True,
        "manual_live_unlock": False, "hybrid_unlock": False, "automated_unlock": False,
        "broker_submission": False, "capital_movement": False,
        "direct_buybox_access": False, "teller_owns_acquisition_readiness": True,
    }
