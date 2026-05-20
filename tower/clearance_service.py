# =============================================================================
# THE TOWER — CLEARANCE SERVICE
# FILE: tower/clearance_service.py
# =============================================================================

from typing import Any, Dict, Optional

from tower.clearance import request_clearance
from tower.object_access import evaluate_object_access
from tower.security_events import security_event_from_clearance_decision
from tower.security_state import (
    action_requires_step_up,
    is_action_locked,
    is_app_locked,
    is_mode_locked,
)
from tower.step_up import create_step_up_challenge, get_latest_approved_step_up
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


def _lockdown_decision(
    lock: Dict[str, Any],
    user_id: str,
    app_name: str,
    action: str,
    mode_name: Optional[str] = None,
    object_type: Optional[str] = None,
    object_id: Optional[str] = None,
) -> Dict[str, Any]:
    return {
        "allowed": False,
        "decision": "lockdown",
        "reason_code": lock.get("reason_code", "tower_lockdown_active"),
        "human_reason": lock.get("human_reason", "The Tower has locked this access path."),
        "risk_score": lock.get("risk_score", 100),
        "risk_state": "locked",
        "required_actions": ["owner_review_required", "lockdown_review_required"],
        "audit_required": True,
        "expires_at": None,
        "metadata": {
            "user_id": user_id,
            "app_name": app_name,
            "action": action,
            "mode_name": mode_name,
            "object_type": object_type,
            "object_id": object_id,
            "lock": lock,
        },
    }


def _step_up_decision(
    user_id: str,
    app_name: str,
    action: str,
    mode_name: Optional[str] = None,
    object_type: Optional[str] = None,
    object_id: Optional[str] = None,
    reason_code: str = "step_up_required",
) -> Dict[str, Any]:
    challenge = create_step_up_challenge(
        user_id=user_id,
        app_name=app_name,
        action=action,
        mode_name=mode_name,
        object_type=object_type,
        object_id=object_id,
        reason_code=reason_code,
    )

    return {
        "allowed": False,
        "decision": "step_up",
        "reason_code": reason_code,
        "human_reason": "This action requires step-up authorization before continuing.",
        "risk_score": 70,
        "risk_state": "step_up_required",
        "required_actions": ["complete_step_up"],
        "audit_required": True,
        "expires_at": None,
        "metadata": {
            "user_id": user_id,
            "app_name": app_name,
            "action": action,
            "mode_name": mode_name,
            "object_type": object_type,
            "object_id": object_id,
            "challenge_id": challenge.get("challenge_id"),
        },
    }


def check_user_clearance(
    user_id: str,
    app_name: str,
    action: str = "enter_app",
    mode_name: Optional[str] = None,
    object_type: Optional[str] = None,
    object_id: Optional[str] = None,
    context: Optional[Dict[str, Any]] = None,
    object_payload: Optional[Dict[str, Any]] = None,
    create_security_alerts: bool = True,
) -> Dict[str, Any]:
    """
    The main front-desk function for The Tower.

    Baby version:
    Before it asks the normal yes/no rules, it checks:
    - Is the whole building locked?
    - Is this app locked?
    - Is this mode locked?
    - Is this action locked?
    - Does this action need extra proof?
    """

    context = context or {}

    # -------------------------------------------------------------------------
    # Lockdown check 1: app/global lock
    # -------------------------------------------------------------------------
    app_lock = is_app_locked(app_name)
    if app_lock:
        decision = _lockdown_decision(
            lock=app_lock,
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

    # -------------------------------------------------------------------------
    # Lockdown check 2: mode lock
    # -------------------------------------------------------------------------
    mode_lock = is_mode_locked(mode_name)
    if mode_lock:
        decision = _lockdown_decision(
            lock=mode_lock,
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

    # -------------------------------------------------------------------------
    # Lockdown check 3: action lock
    # -------------------------------------------------------------------------
    action_lock = is_action_locked(action)
    if action_lock:
        decision = _lockdown_decision(
            lock=action_lock,
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

    # -------------------------------------------------------------------------
    # User existence check
    # -------------------------------------------------------------------------
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

    # -------------------------------------------------------------------------
    # Step-up check before sensitive actions.
    # -------------------------------------------------------------------------
    if action_requires_step_up(action):
        approved = get_latest_approved_step_up(
            user_id=user_id,
            app_name=app_name,
            action=action,
            mode_name=mode_name,
            object_type=object_type,
            object_id=object_id,
        )

        if not approved:
            decision = _step_up_decision(
                user_id=user_id,
                app_name=app_name,
                action=action,
                mode_name=mode_name,
                object_type=object_type,
                object_id=object_id,
                reason_code=f"{action}_step_up_required",
            )

            if create_security_alerts:
                security_event_from_clearance_decision(decision)

            return decision

    # -------------------------------------------------------------------------
    # Object-level access check.
    # -------------------------------------------------------------------------
    if object_payload is not None:
        object_decision = evaluate_object_access(
            user=user,
            obj=object_payload,
            action=action,
            context=context,
        ).to_dict()

        object_decision = _stamp_context_on_decision(
            decision=object_decision,
            user_id=user_id,
            app_name=app_name,
            action=action,
            mode_name=mode_name,
            object_type=object_type,
            object_id=object_id,
        )

        if create_security_alerts:
            security_event_from_clearance_decision(object_decision)

        if not object_decision.get("allowed"):
            return object_decision

    # -------------------------------------------------------------------------
    # Normal clearance brain.
    # -------------------------------------------------------------------------
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
    object_payload: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    return check_user_clearance(
        user_id=user_id,
        app_name=app_name,
        action="export",
        object_type=object_type,
        object_id=object_id,
        context=context,
        object_payload=object_payload,
    )
