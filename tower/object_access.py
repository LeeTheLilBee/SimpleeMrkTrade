# =============================================================================
# THE TOWER — OBJECT-LEVEL ACCESS
# FILE: tower/object_access.py
# =============================================================================

from typing import Any, Dict, List, Optional

from tower.permissions import ClearanceDecision


# =============================================================================
# OBJECT CLASSIFICATIONS
# =============================================================================

CLASS_PUBLIC = "public"
CLASS_USER_PRIVATE = "user_private"
CLASS_INTERNAL = "internal"
CLASS_CONFIDENTIAL = "confidential"
CLASS_RESTRICTED = "restricted"
CLASS_TRUST_INTERNAL = "trust_internal"
CLASS_ADMIN_ONLY = "admin_only"


# =============================================================================
# OBJECT TYPES
# =============================================================================

OBJECT_TRADE_RECORD = "trade_record"
OBJECT_ARCHIVE_FILE = "archive_file"
OBJECT_EXPORT = "export"
OBJECT_USER_PROFILE = "user_profile"
OBJECT_PAYROLL_RECORD = "payroll_record"
OBJECT_TRUST_RECORD = "trust_record"
OBJECT_BROKER_RECORD = "broker_record"
OBJECT_AUDIT_EVENT = "audit_event"
OBJECT_SECURITY_EVENT = "security_event"
OBJECT_DISCLOSURE_RECORD = "disclosure_record"


def _list(value: Any) -> List[str]:
    if value is None:
        return []

    if isinstance(value, list):
        return [str(item) for item in value]

    return [str(value)]


def _is_owner(user: Dict[str, Any]) -> bool:
    return user.get("role") == "owner" or user.get("account_type") == "owner"


def _is_admin(user: Dict[str, Any]) -> bool:
    return user.get("role") in {"owner", "admin"}


def _is_internal_or_trust(user: Dict[str, Any]) -> bool:
    return user.get("account_type") in {"owner", "internal", "trust"}


def _has_consent(user: Dict[str, Any], consent_key: str) -> bool:
    consents = user.get("consents", {}) or {}
    return bool(consents.get(consent_key) is True)


def _deny(
    reason_code: str,
    human_reason: str,
    user: Dict[str, Any],
    obj: Dict[str, Any],
    risk_score: int = 70,
    risk_state: str = "restricted",
    required_actions: Optional[List[str]] = None,
) -> ClearanceDecision:
    return ClearanceDecision(
        allowed=False,
        decision="deny",
        reason_code=reason_code,
        human_reason=human_reason,
        risk_score=risk_score,
        risk_state=risk_state,
        required_actions=required_actions or [],
        audit_required=True,
        metadata={
            "user_id": user.get("user_id"),
            "object_type": obj.get("object_type"),
            "object_id": obj.get("object_id"),
            "classification": obj.get("classification"),
            "app_name": obj.get("app_name"),
        },
    )


def _allow(
    reason_code: str,
    human_reason: str,
    user: Dict[str, Any],
    obj: Dict[str, Any],
    risk_score: int = 20,
    metadata_extra: Optional[Dict[str, Any]] = None,
) -> ClearanceDecision:
    metadata = {
        "user_id": user.get("user_id"),
        "object_type": obj.get("object_type"),
        "object_id": obj.get("object_id"),
        "classification": obj.get("classification"),
        "app_name": obj.get("app_name"),
    }

    if metadata_extra:
        metadata.update(metadata_extra)

    return ClearanceDecision(
        allowed=True,
        decision="allow",
        reason_code=reason_code,
        human_reason=human_reason,
        risk_score=risk_score,
        risk_state="clear",
        required_actions=[],
        audit_required=True,
        metadata=metadata,
    )


def evaluate_object_access(
    user: Dict[str, Any],
    obj: Dict[str, Any],
    action: str = "view",
    context: Optional[Dict[str, Any]] = None,
) -> ClearanceDecision:
    """
    Checks if a user can access a specific object.

    Baby version:
    The Tower asks:
    "Can this exact person touch this exact thing?"
    """

    context = context or {}

    user_id = str(user.get("user_id", ""))
    role = str(user.get("role", "user"))
    account_type = str(user.get("account_type", "public_user"))
    status = str(user.get("status", "locked"))

    object_id = str(obj.get("object_id", ""))
    object_type = str(obj.get("object_type", "unknown"))
    classification = str(obj.get("classification", CLASS_RESTRICTED))
    owner_user_id = obj.get("owner_user_id")
    app_name = obj.get("app_name")

    allowed_user_ids = _list(obj.get("allowed_user_ids"))
    allowed_roles = _list(obj.get("allowed_roles"))
    allowed_account_types = _list(obj.get("allowed_account_types"))
    required_consents = _list(obj.get("required_consents"))
    denied_user_ids = _list(obj.get("denied_user_ids"))

    # -------------------------------------------------------------------------
    # Rule 1: locked/revoked/quarantined users cannot touch sensitive objects.
    # -------------------------------------------------------------------------
    if status in {"locked", "revoked"}:
        return _deny(
            reason_code="object_user_locked_or_revoked",
            human_reason="This user is locked or revoked. Object access is denied.",
            user=user,
            obj=obj,
            risk_score=100,
            risk_state="locked",
            required_actions=["owner_review_required"],
        )

    if status == "quarantined" and classification != CLASS_PUBLIC:
        return _deny(
            reason_code="object_user_quarantined",
            human_reason="This user is quarantined. Sensitive object access is paused.",
            user=user,
            obj=obj,
            risk_score=90,
            risk_state="quarantined",
            required_actions=["security_review_required"],
        )

    # -------------------------------------------------------------------------
    # Rule 2: explicit deny always wins.
    # -------------------------------------------------------------------------
    if user_id in denied_user_ids:
        return _deny(
            reason_code="object_explicit_user_deny",
            human_reason="This user is explicitly denied from this object.",
            user=user,
            obj=obj,
            risk_score=90,
            risk_state="restricted",
            required_actions=["owner_review_required"],
        )

    # -------------------------------------------------------------------------
    # Rule 3: owner role can view most things, but not blindly export everything.
    # -------------------------------------------------------------------------
    if _is_owner(user) and action != "export":
        return _allow(
            reason_code="object_owner_override_allowed",
            human_reason="Owner-level object access granted.",
            user=user,
            obj=obj,
            risk_score=15,
            metadata_extra={"owner_override": True, "action": action},
        )

    # -------------------------------------------------------------------------
    # Rule 4: public objects can be viewed by active users.
    # -------------------------------------------------------------------------
    if classification == CLASS_PUBLIC and action == "view":
        return _allow(
            reason_code="object_public_view_allowed",
            human_reason="Public object view access granted.",
            user=user,
            obj=obj,
            risk_score=5,
            metadata_extra={"action": action},
        )

    # -------------------------------------------------------------------------
    # Rule 5: user-private objects belong to the owner_user_id.
    # -------------------------------------------------------------------------
    if classification == CLASS_USER_PRIVATE:
        if owner_user_id and str(owner_user_id) == user_id:
            return _allow(
                reason_code="object_user_owner_allowed",
                human_reason="User owns this object. Access granted.",
                user=user,
                obj=obj,
                risk_score=15,
                metadata_extra={"action": action},
            )

        if user_id in allowed_user_ids:
            return _allow(
                reason_code="object_user_allowlist_allowed",
                human_reason="User is allowlisted for this object.",
                user=user,
                obj=obj,
                risk_score=20,
                metadata_extra={"action": action},
            )

        return _deny(
            reason_code="object_private_owner_required",
            human_reason="This private object belongs to another user.",
            user=user,
            obj=obj,
            risk_score=75,
            risk_state="restricted",
            required_actions=["object_owner_or_allowlist_required"],
        )

    # -------------------------------------------------------------------------
    # Rule 6: admin-only objects require admin or owner.
    # -------------------------------------------------------------------------
    if classification == CLASS_ADMIN_ONLY:
        if _is_admin(user):
            return _allow(
                reason_code="object_admin_allowed",
                human_reason="Admin-level object access granted.",
                user=user,
                obj=obj,
                risk_score=25,
                metadata_extra={"action": action},
            )

        return _deny(
            reason_code="object_admin_required",
            human_reason="This object requires admin access.",
            user=user,
            obj=obj,
            risk_score=85,
            risk_state="restricted",
            required_actions=["admin_access_required"],
        )

    # -------------------------------------------------------------------------
    # Rule 7: trust/internal records require internal/trust/owner account.
    # -------------------------------------------------------------------------
    if classification == CLASS_TRUST_INTERNAL:
        if _is_internal_or_trust(user):
            return _allow(
                reason_code="object_internal_trust_allowed",
                human_reason="Internal/trust object access granted.",
                user=user,
                obj=obj,
                risk_score=35,
                metadata_extra={"action": action},
            )

        return _deny(
            reason_code="object_internal_trust_required",
            human_reason="This object requires internal/trust clearance.",
            user=user,
            obj=obj,
            risk_score=95,
            risk_state="locked",
            required_actions=["internal_trust_clearance_required"],
        )

    # -------------------------------------------------------------------------
    # Rule 8: allowed roles/account types can grant access.
    # -------------------------------------------------------------------------
    if allowed_roles and role in allowed_roles:
        return _allow(
            reason_code="object_role_allowed",
            human_reason="User role is allowed for this object.",
            user=user,
            obj=obj,
            risk_score=30,
            metadata_extra={"action": action},
        )

    if allowed_account_types and account_type in allowed_account_types:
        return _allow(
            reason_code="object_account_type_allowed",
            human_reason="User account type is allowed for this object.",
            user=user,
            obj=obj,
            risk_score=30,
            metadata_extra={"action": action},
        )

    if allowed_user_ids and user_id in allowed_user_ids:
        return _allow(
            reason_code="object_user_allowlist_allowed",
            human_reason="User is allowlisted for this object.",
            user=user,
            obj=obj,
            risk_score=25,
            metadata_extra={"action": action},
        )

    # -------------------------------------------------------------------------
    # Rule 9: required consents must be accepted.
    # -------------------------------------------------------------------------
    for consent_key in required_consents:
        if not _has_consent(user, consent_key):
            return _deny(
                reason_code="object_required_consent_missing",
                human_reason=f"This object requires consent first: {consent_key}.",
                user=user,
                obj=obj,
                risk_score=60,
                risk_state="restricted",
                required_actions=[f"accept_{consent_key}"],
            )

    # -------------------------------------------------------------------------
    # Rule 10: restricted/confidential default deny.
    # -------------------------------------------------------------------------
    if classification in {CLASS_INTERNAL, CLASS_CONFIDENTIAL, CLASS_RESTRICTED}:
        return _deny(
            reason_code="object_restricted_default_deny",
            human_reason="This object is restricted. No matching object-level permission was found.",
            user=user,
            obj=obj,
            risk_score=80,
            risk_state="restricted",
            required_actions=["object_level_permission_required"],
        )

    # -------------------------------------------------------------------------
    # Safe default: deny.
    # -------------------------------------------------------------------------
    return _deny(
        reason_code="object_default_deny",
        human_reason="Object access denied by default.",
        user=user,
        obj=obj,
        risk_score=70,
        risk_state="restricted",
        required_actions=["object_access_review_required"],
    )
