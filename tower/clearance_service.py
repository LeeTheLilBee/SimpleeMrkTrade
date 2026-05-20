# =============================================================================
# THE TOWER — CLEARANCE SERVICE
# FILE: tower/clearance_service.py
# =============================================================================

from typing import Any, Dict, Optional

from tower.clearance import request_clearance
from tower.security_events import security_event_from_clearance_decision
from tower.user_store import get_user


def _stamp_context_on_decision(
    decision: Dict[str, Any],
    user_id: str,
    app_name: str,
    action: str,
    mode_name: Optional[str] = None,
    object_type: Optional[str] = None,
    object_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Adds missing context to a Tower decision.

    Baby version:
    Before making a security sticky note, we stamp:
    who, what app, what door, what object.
    """

    decision = dict(decision)
    metadata = dict(decision.get("metadata") or {})

    metadata.setdefault("user_id", user_id)
    metadata.setdefault("app_name", app_name)
    metadata.setdefault("action", action)

    if mode_name is not None:
        metadata.setdefault("mode_name", mode_name)

    if object_type is not None:
        metadata.setdefault("object_type", object_type)

    if object_id is not None:
        metadata.setdefault("object_id", object_id)

    decision["metadata"] = metadata
    return decision


def check_user_clearance(
    user_id: str,
    app_name: str,
    action: str = "enter_app",
    mode_name: Optional[str] = None,
    object_type: Optional[str] = None,
    object_id: Optional[str] = None,
    context: Optional[Dict[str, Any]] = None,
    create_security_alerts: bool = True,
) -> Dict[str, Any]:
    """
    Main front-desk function for The Tower.

    Baby version:
    You say:
        "Can beta_001 enter OB Paper Mode?"

    The Tower:
    1. Finds the user
    2. Checks the rules
    3. Writes the receipt
    4. Creates a security alert if needed
    5. Gives you the answer
    """

    context = context or {}
    user = get_user(user_id)

    if not user:
        missing_user_decision = {
            "allowed": False,
            "decision": "deny",
            "reason_code": "user_not_found",
            "human_reason": "Tower user was not found. Access is denied.",
            "risk_score": 80,
            "risk_state": "restricted",
            "required_actions": ["create_or_verify_user"],
            "audit_required": True,
            "expires_at": None,
            "metadata": {
                "user_id": user_id,
                "app_name": app_name,
                "action": action,
                "mode_name": mode_name,
                "object_type": object_type,
                "object_id": object_id,
            },
        }

        if create_security_alerts:
            security_event_from_clearance_decision(missing_user_decision)

        return missing_user_decision

    decision = request_clearance(
        user=user,
        app_name=app_name,
        action=action,
        mode_name=mode_name,
        object_type=object_type,
        object_id=object_id,
        context=context,
        write_audit=True,
    )

    decision = _stamp_context_on_decision(
        decision=decision,
        user_id=user_id,
        app_name=app_name,
        action=action,
        mode_name=mode_name,
        object_type=object_type,
        object_id=object_id,
    )

    if create_security_alerts:
        security_event_from_clearance_decision(decision)

    return decision


def check_ob_mode_clearance(
    user_id: str,
    mode_name: str,
    context: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Shortcut for Observatory mode checks.
    """

    return check_user_clearance(
        user_id=user_id,
        app_name="observatory",
        action="enter_app",
        mode_name=mode_name,
        context=context,
    )


def check_tower_admin_clearance(
    user_id: str,
    action: str = "enter_admin",
    context: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Shortcut for Tower admin checks.
    """

    return check_user_clearance(
        user_id=user_id,
        app_name="tower_admin",
        action=action,
        context=context,
    )


def check_export_clearance(
    user_id: str,
    app_name: str,
    object_type: str,
    object_id: str,
    context: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Shortcut for export checks.
    """

    return check_user_clearance(
        user_id=user_id,
        app_name=app_name,
        action="export",
        object_type=object_type,
        object_id=object_id,
        context=context,
    )
