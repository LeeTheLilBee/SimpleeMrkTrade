# =============================================================================
# THE TOWER — CLEARANCE SERVICE
# FILE: tower/clearance_service.py
# MARKER: PACK_008E_SESSION_RISK_ENFORCED_FIRST
# =============================================================================

from typing import Any, Dict, Optional

from tower.clearance import request_clearance
from tower.clearance_tokens import issue_clearance_token
from tower.object_access import evaluate_object_access
from tower.security_events import security_event_from_clearance_decision
from tower.security_state import (
    action_requires_step_up,
    is_action_locked,
    is_app_locked,
    is_mode_locked,
)
from tower.step_up import create_step_up_challenge, get_latest_approved_step_up, consume_step_up_challenge
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


def _alert_if_needed(decision: Dict[str, Any], create_security_alerts: bool = True) -> None:
    if create_security_alerts:
        security_event_from_clearance_decision(decision)


def _make_step_up_decision(
    user_id: str,
    app_name: str,
    action: str,
    mode_name: Optional[str] = None,
    object_type: Optional[str] = None,
    object_id: Optional[str] = None,
    reason_code: str = "step_up_required",
    extra_metadata: Optional[Dict[str, Any]] = None,
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

    metadata = {
        "user_id": user_id,
        "app_name": app_name,
        "action": action,
        "mode_name": mode_name,
        "object_type": object_type,
        "object_id": object_id,
        "challenge_id": challenge.get("challenge_id"),
    }

    if extra_metadata:
        metadata.update(extra_metadata)

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
        "metadata": metadata,
    }


def _make_lockdown_decision(
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
        "risk_score": int(lock.get("risk_score") or 100),
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


def _issue_token_if_allowed(
    decision: Dict[str, Any],
    user_id: str,
    app_name: str,
    action: str,
    mode_name: Optional[str],
    object_type: Optional[str],
    object_id: Optional[str],
) -> Dict[str, Any]:
    if decision.get("allowed") is not True:
        return decision

    if decision.get("clearance_token"):
        return decision

    token = issue_clearance_token(
        user_id=user_id,
        app_name=app_name,
        action=action,
        mode_name=mode_name,
        object_type=object_type,
        object_id=object_id,
        issued_by="tower_clearance_service",
        reason_code="clearance_service_token_issued",
        risk_state=decision.get("risk_state", "clear"),
        risk_score=int(decision.get("risk_score") or 10),
        metadata={
            "source_decision_reason_code": decision.get("reason_code"),
            "source_decision": decision,
        },
    )

    decision["clearance_token"] = {
        "token_id": token.get("token_id"),
        "scope": token.get("scope"),
        "expires_at": token.get("expires_at"),
        "status": token.get("status"),
    }

    return decision


def _check_session_risk_first(
    user_id: str,
    app_name: str,
    action: str,
    mode_name: Optional[str],
    object_type: Optional[str],
    object_id: Optional[str],
    context: Dict[str, Any],
) -> Optional[Dict[str, Any]]:
    session_risk = context.get("session_risk") or {}
    session_risk_score = int(session_risk.get("risk_score") or 0)
    session_risk_state = session_risk.get("risk_state") or "clear"

    if session_risk_state == "quarantine_recommended" or session_risk_score >= 90:
        return {
            "allowed": False,
            "decision": "quarantine",
            "reason_code": "session_risk_quarantine_recommended",
            "human_reason": "This session is too risky. Access is paused for review.",
            "risk_score": session_risk_score,
            "risk_state": "quarantined",
            "required_actions": ["security_review_required", "step_up_required"],
            "audit_required": True,
            "expires_at": None,
            "metadata": {
                "user_id": user_id,
                "app_name": app_name,
                "action": action,
                "mode_name": mode_name,
                "object_type": object_type,
                "object_id": object_id,
                "session_risk": session_risk,
            },
        }

    if session_risk_state == "step_up_required" or session_risk_score >= 70:
        approved = get_latest_approved_step_up(
            user_id=user_id,
            app_name=app_name,
            action=action,
            mode_name=mode_name,
            object_type=object_type,
            object_id=object_id,
            reason_code="session_risk_step_up_required",
        )

        if not approved:
            return _make_step_up_decision(
                user_id=user_id,
                app_name=app_name,
                action=action,
                mode_name=mode_name,
                object_type=object_type,
                object_id=object_id,
                reason_code="session_risk_step_up_required",
                extra_metadata={"session_risk": session_risk},
            )

        consume_step_up_challenge(
            challenge_id=approved.get("challenge_id"),
            used_by=user_id,
            use_reason="session_risk_step_up_consumed",
        )

    return None


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
    context = context or {}

    # 1. Session risk MUST be first.
    session_decision = _check_session_risk_first(
        user_id=user_id,
        app_name=app_name,
        action=action,
        mode_name=mode_name,
        object_type=object_type,
        object_id=object_id,
        context=context,
    )

    if session_decision is not None:
        _alert_if_needed(session_decision, create_security_alerts)
        return session_decision

    # 2. Lockdowns.
    for lock in [is_app_locked(app_name), is_mode_locked(mode_name), is_action_locked(action)]:
        if lock:
            decision = _make_lockdown_decision(
                lock=lock,
                user_id=user_id,
                app_name=app_name,
                action=action,
                mode_name=mode_name,
                object_type=object_type,
                object_id=object_id,
            )
            _alert_if_needed(decision, create_security_alerts)
            return decision

    # 3. User lookup.
    user = get_user(user_id)

    if not user:
        decision = {
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
        _alert_if_needed(decision, create_security_alerts)
        return decision

    # 4. Sensitive action step-up.
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
            decision = _make_step_up_decision(
                user_id=user_id,
                app_name=app_name,
                action=action,
                mode_name=mode_name,
                object_type=object_type,
                object_id=object_id,
                reason_code=f"{action}_step_up_required",
            )
            _alert_if_needed(decision, create_security_alerts)
            return decision

    # 5. Object-level access.
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

        _alert_if_needed(object_decision, create_security_alerts)

        if not object_decision.get("allowed"):
            return object_decision

    # 6. Normal permission brain.
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

    # 7. Token only after allow.
    decision = _issue_token_if_allowed(
        decision=decision,
        user_id=user_id,
        app_name=app_name,
        action=action,
        mode_name=mode_name,
        object_type=object_type,
        object_id=object_id,
    )

    _alert_if_needed(decision, create_security_alerts)
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
