# =============================================================================
# THE TOWER — ADMIN ACTION GATE
# FILE: tower/admin_action_gate.py
# =============================================================================

import hashlib
import json
import os
import secrets
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from tower.audit import write_audit_event
from tower.clearance_service import check_tower_admin_clearance, check_user_clearance
from tower.evidence_capsules import create_evidence_capsule
from tower.policy_engine import evaluate_policy
from tower.security_events import create_security_event
from tower.security_state import action_requires_step_up
from tower.step_up import approve_step_up_challenge, create_step_up_challenge, get_latest_approved_step_up, consume_step_up_challenge
from tower.user_store import get_user


PROJECT_ROOT = os.environ.get("SIMPLEE_PROJECT_ROOT", "/content/SimpleeMrkTrade_REAL_CLONE")
TOWER_DATA_DIR = Path(PROJECT_ROOT) / "tower" / "data"
ADMIN_ACTIONS_PATH = TOWER_DATA_DIR / "admin_actions.json"

TOWER_DATA_DIR.mkdir(parents=True, exist_ok=True)


ADMIN_ACTION_APPROVED = "approved"
ADMIN_ACTION_DENIED = "denied"
ADMIN_ACTION_STEP_UP = "step_up_required"
ADMIN_ACTION_LOCKED = "locked"
ADMIN_ACTION_QUARANTINED = "quarantined"
ADMIN_ACTION_EXECUTED = "executed"
ADMIN_ACTION_REVOKED = "revoked"


DANGEROUS_ADMIN_ACTIONS = {
    "change_permissions",
    "grant_export",
    "revoke_export",
    "lock_user",
    "unlock_user",
    "quarantine_user",
    "revoke_user",
    "approve_beta_user",
    "change_beta_status",
    "change_user_role",
    "change_account_type",
    "approve_live_mode",
    "approve_automated_mode",
    "kill_switch_change",
    "global_lockdown_change",
    "mode_lockdown_change",
    "app_lockdown_change",
    "revoke_clearance_token",
    "revoke_session",
    "delete_record",
    "export_admin_data",
    "view_security_sensitive",
}


CRITICAL_ADMIN_ACTIONS = {
    "approve_live_mode",
    "approve_automated_mode",
    "global_lockdown_change",
    "kill_switch_change",
    "change_user_role",
    "change_account_type",
    "revoke_user",
    "delete_record",
}


def _now() -> str:
    return datetime.utcnow().isoformat() + "Z"


def _safe_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, default=str)


def _hash_payload(payload: Dict[str, Any]) -> str:
    return hashlib.sha256(_safe_json(payload).encode("utf-8")).hexdigest()


def _load_raw() -> Dict[str, Any]:
    if not ADMIN_ACTIONS_PATH.exists():
        return {"admin_actions": []}

    try:
        with ADMIN_ACTIONS_PATH.open("r", encoding="utf-8") as f:
            data = json.load(f)

        if not isinstance(data, dict):
            return {"admin_actions": []}

        if not isinstance(data.get("admin_actions"), list):
            data["admin_actions"] = []

        return data
    except Exception:
        return {"admin_actions": []}


def _save_raw(data: Dict[str, Any]) -> None:
    tmp_path = ADMIN_ACTIONS_PATH.with_suffix(".tmp")
    with tmp_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, sort_keys=True, default=str)

    tmp_path.replace(ADMIN_ACTIONS_PATH)


def _is_admin_user(user: Dict[str, Any]) -> bool:
    return user.get("role") in {"owner", "admin"}


def _risk_for_admin_action(admin_action: str) -> Dict[str, Any]:
    if admin_action in CRITICAL_ADMIN_ACTIONS:
        return {
            "risk_score": 95,
            "risk_state": "critical_admin_action",
            "severity": "critical",
        }

    if admin_action in DANGEROUS_ADMIN_ACTIONS:
        return {
            "risk_score": 75,
            "risk_state": "sensitive_admin_action",
            "severity": "high",
        }

    return {
        "risk_score": 35,
        "risk_state": "admin_action",
        "severity": "medium",
    }


def _requires_admin_step_up(admin_action: str) -> bool:
    if admin_action in DANGEROUS_ADMIN_ACTIONS:
        return True

    if action_requires_step_up(admin_action):
        return True

    return False


def _status_from_decision(decision: Dict[str, Any]) -> str:
    kind = str(decision.get("decision") or "").lower()

    if decision.get("allowed") is True:
        return ADMIN_ACTION_APPROVED

    if kind == "step_up":
        return ADMIN_ACTION_STEP_UP

    if kind == "lockdown":
        return ADMIN_ACTION_LOCKED

    if kind == "quarantine":
        return ADMIN_ACTION_QUARANTINED

    return ADMIN_ACTION_DENIED


def request_admin_action(
    actor_user_id: str,
    admin_action: str,
    target_user_id: Optional[str] = None,
    target_app: str = "tower_admin",
    object_type: Optional[str] = None,
    object_id: Optional[str] = None,
    requested_changes: Optional[Dict[str, Any]] = None,
    reason: str = "admin_requested_action",
    context: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Requests permission to do an admin action.

    Baby version:
    This is the locked command desk.
    Admin asks. The Tower checks. Then it returns an approval package or denial.
    """

    context = context or {}
    requested_changes = requested_changes or {}

    actor = get_user(actor_user_id)
    target = get_user(target_user_id) if target_user_id else None

    action_risk = _risk_for_admin_action(admin_action)

    if not actor:
        decision = {
            "allowed": False,
            "decision": "deny",
            "reason_code": "admin_actor_not_found",
            "human_reason": "Admin actor was not found.",
            "risk_score": 90,
            "risk_state": "restricted",
            "required_actions": ["verify_admin_actor"],
            "metadata": {
                "actor_user_id": actor_user_id,
                "admin_action": admin_action,
                "target_user_id": target_user_id,
            },
        }

        return _save_admin_action(
            actor_user_id=actor_user_id,
            target_user_id=target_user_id,
            admin_action=admin_action,
            target_app=target_app,
            object_type=object_type,
            object_id=object_id,
            requested_changes=requested_changes,
            reason=reason,
            status=ADMIN_ACTION_DENIED,
            decision=decision,
            policy_report=decision,
            context=context,
        )

    if not _is_admin_user(actor):
        decision = {
            "allowed": False,
            "decision": "deny",
            "reason_code": "admin_role_required",
            "human_reason": "This action requires owner/admin role.",
            "risk_score": 90,
            "risk_state": "restricted",
            "required_actions": ["admin_role_required"],
            "metadata": {
                "actor_user_id": actor_user_id,
                "admin_action": admin_action,
                "target_user_id": target_user_id,
            },
        }

        saved = _save_admin_action(
            actor_user_id=actor_user_id,
            target_user_id=target_user_id,
            admin_action=admin_action,
            target_app=target_app,
            object_type=object_type,
            object_id=object_id,
            requested_changes=requested_changes,
            reason=reason,
            status=ADMIN_ACTION_DENIED,
            decision=decision,
            policy_report=decision,
            context=context,
        )

        _create_admin_action_evidence(actor, saved, decision, decision, context)
        return saved

    # Check Tower admin entry first.
    tower_clearance = check_tower_admin_clearance(
        user_id=actor_user_id,
        action="enter_admin",
        context=context,
    )

    if not tower_clearance.get("allowed"):
        status = _status_from_decision(tower_clearance)

        saved = _save_admin_action(
            actor_user_id=actor_user_id,
            target_user_id=target_user_id,
            admin_action=admin_action,
            target_app=target_app,
            object_type=object_type,
            object_id=object_id,
            requested_changes=requested_changes,
            reason=reason,
            status=status,
            decision=tower_clearance,
            policy_report=tower_clearance,
            context=context,
        )

        _create_admin_action_evidence(actor, saved, tower_clearance, tower_clearance, context)
        return saved

    # Policy report for explanation.
    policy_report = evaluate_policy(
        user=actor,
        app_name="tower_admin",
        action="enter_admin",
        context=context,
    ).to_dict()

    # Dangerous admin actions need action-specific step-up.
    if _requires_admin_step_up(admin_action):
        approved = get_latest_approved_step_up(
            user_id=actor_user_id,
            app_name="tower_admin",
            action=admin_action,
            object_type=object_type,
            object_id=object_id,
            reason_code=f"{admin_action}_admin_step_up_required",
        )

        if not approved:
            challenge = create_step_up_challenge(
                user_id=actor_user_id,
                app_name="tower_admin",
                action=admin_action,
                object_type=object_type,
                object_id=object_id,
                reason_code=f"{admin_action}_admin_step_up_required",
            )

            decision = {
                "allowed": False,
                "decision": "step_up",
                "reason_code": f"{admin_action}_admin_step_up_required",
                "human_reason": "This admin action requires step-up authorization before continuing.",
                "risk_score": action_risk.get("risk_score"),
                "risk_state": "step_up_required",
                "required_actions": ["complete_step_up"],
                "metadata": {
                    "actor_user_id": actor_user_id,
                    "target_user_id": target_user_id,
                    "admin_action": admin_action,
                    "target_app": target_app,
                    "object_type": object_type,
                    "object_id": object_id,
                    "challenge_id": challenge.get("challenge_id"),
                    "action_risk": action_risk,
                },
            }

            saved = _save_admin_action(
                actor_user_id=actor_user_id,
                target_user_id=target_user_id,
                admin_action=admin_action,
                target_app=target_app,
                object_type=object_type,
                object_id=object_id,
                requested_changes=requested_changes,
                reason=reason,
                status=ADMIN_ACTION_STEP_UP,
                decision=decision,
                policy_report=policy_report,
                context=context,
            )

            _create_admin_action_evidence(actor, saved, decision, policy_report, context)
            return saved

    if _requires_admin_step_up(admin_action):
        approved_to_consume = get_latest_approved_step_up(
            user_id=actor_user_id,
            app_name="tower_admin",
            action=admin_action,
            object_type=object_type,
            object_id=object_id,
            reason_code=f"{admin_action}_admin_step_up_required",
        )

        if approved_to_consume:
            consume_step_up_challenge(
                challenge_id=approved_to_consume.get("challenge_id"),
                used_by=actor_user_id,
                use_reason=f"{admin_action}_admin_step_up_consumed",
            )

    decision = {
        "allowed": True,
        "decision": "allow",
        "reason_code": "admin_action_gate_approved",
        "human_reason": "Admin action approved by The Tower.",
        "risk_score": action_risk.get("risk_score"),
        "risk_state": action_risk.get("risk_state"),
        "required_actions": [],
        "metadata": {
            "actor_user_id": actor_user_id,
            "target_user_id": target_user_id,
            "target_user_status": target.get("status") if target else None,
            "admin_action": admin_action,
            "target_app": target_app,
            "object_type": object_type,
            "object_id": object_id,
            "action_risk": action_risk,
        },
    }

    saved = _save_admin_action(
        actor_user_id=actor_user_id,
        target_user_id=target_user_id,
        admin_action=admin_action,
        target_app=target_app,
        object_type=object_type,
        object_id=object_id,
        requested_changes=requested_changes,
        reason=reason,
        status=ADMIN_ACTION_APPROVED,
        decision=decision,
        policy_report=policy_report,
        context=context,
    )

    _create_admin_action_evidence(actor, saved, decision, policy_report, context)
    return saved


def mark_admin_action_executed(
    admin_action_id: str,
    executed_by: str,
    execution_result: Optional[Dict[str, Any]] = None,
) -> Optional[Dict[str, Any]]:
    """
    Marks an approved admin action as executed.

    Baby version:
    This says, "The approved command was actually carried out."
    """

    data = _load_raw()
    updated = None

    for item in data.get("admin_actions", []):
        if item.get("admin_action_id") == admin_action_id:
            item["status"] = ADMIN_ACTION_EXECUTED
            item["executed_at"] = _now()
            item["executed_by"] = executed_by
            item["execution_result"] = execution_result or {}

            clean = dict(item)
            clean.pop("admin_action_hash", None)
            item["admin_action_hash"] = _hash_payload(clean)
            updated = item
            break

    _save_raw(data)

    if updated:
        write_audit_event(
            actor_user_id=executed_by,
            target_user_id=updated.get("target_user_id"),
            action="mark_admin_action_executed",
            app_name="tower_admin",
            object_type="admin_action",
            object_id=admin_action_id,
            result="allow",
            reason_code="admin_action_executed",
            human_reason="Approved admin action was marked executed.",
            risk_score=int(updated.get("decision", {}).get("risk_score") or 50),
            risk_state=str(updated.get("decision", {}).get("risk_state") or "admin_action"),
            metadata={
                "admin_action_id": admin_action_id,
                "admin_action": updated.get("admin_action"),
                "execution_result": execution_result or {},
            },
        )

    return updated


def revoke_admin_action(
    admin_action_id: str,
    revoked_by: str,
    reason: str = "admin_action_revoked",
) -> Optional[Dict[str, Any]]:
    data = _load_raw()
    updated = None

    for item in data.get("admin_actions", []):
        if item.get("admin_action_id") == admin_action_id:
            item["status"] = ADMIN_ACTION_REVOKED
            item["revoked_at"] = _now()
            item["revoked_by"] = revoked_by
            item["revoke_reason"] = reason

            clean = dict(item)
            clean.pop("admin_action_hash", None)
            item["admin_action_hash"] = _hash_payload(clean)
            updated = item
            break

    _save_raw(data)

    if updated:
        write_audit_event(
            actor_user_id=revoked_by,
            target_user_id=updated.get("target_user_id"),
            action="revoke_admin_action",
            app_name="tower_admin",
            object_type="admin_action",
            object_id=admin_action_id,
            result="allow",
            reason_code=reason,
            human_reason="Tower admin action package was revoked.",
            risk_score=70,
            risk_state="restricted",
            metadata={
                "admin_action_id": admin_action_id,
                "admin_action": updated.get("admin_action"),
            },
        )

    return updated


def _save_admin_action(
    actor_user_id: str,
    target_user_id: Optional[str],
    admin_action: str,
    target_app: str,
    object_type: Optional[str],
    object_id: Optional[str],
    requested_changes: Dict[str, Any],
    reason: str,
    status: str,
    decision: Dict[str, Any],
    policy_report: Dict[str, Any],
    context: Dict[str, Any],
) -> Dict[str, Any]:
    admin_action_id = secrets.token_urlsafe(18)

    package = {
        "admin_action_id": admin_action_id,
        "created_at": _now(),
        "status": status,
        "actor_user_id": actor_user_id,
        "target_user_id": target_user_id,
        "admin_action": admin_action,
        "target_app": target_app,
        "object_type": object_type,
        "object_id": object_id,
        "requested_changes": requested_changes,
        "reason": reason,
        "decision": decision,
        "policy_report": policy_report,
        "context": context,
    }

    package["admin_action_hash"] = _hash_payload(package)

    data = _load_raw()
    data["admin_actions"].append(package)
    _save_raw(data)

    result = "allow" if status == ADMIN_ACTION_APPROVED else "deny"

    write_audit_event(
        actor_user_id=actor_user_id,
        target_user_id=target_user_id,
        action="request_admin_action",
        app_name="tower_admin",
        object_type="admin_action",
        object_id=admin_action_id,
        result=result,
        reason_code=f"admin_action_{status}",
        human_reason=f"Admin action request completed with status: {status}.",
        risk_score=int(decision.get("risk_score") or 50),
        risk_state=str(decision.get("risk_state") or "admin_action"),
        metadata={
            "admin_action_id": admin_action_id,
            "admin_action": admin_action,
            "target_app": target_app,
            "object_type": object_type,
            "object_id": object_id,
            "status": status,
            "decision_reason_code": decision.get("reason_code"),
        },
    )

    if status != ADMIN_ACTION_APPROVED:
        create_security_event(
            user_id=actor_user_id,
            event_type=f"admin_action_{status}",
            severity="high" if status in {ADMIN_ACTION_STEP_UP, ADMIN_ACTION_LOCKED, ADMIN_ACTION_QUARANTINED} else "medium",
            source_app="tower_admin",
            description=f"Admin action request ended with status: {status}.",
            recommended_action=", ".join(decision.get("required_actions", [])) or "review_admin_action",
            metadata={
                "admin_action_id": admin_action_id,
                "admin_action": admin_action,
                "target_user_id": target_user_id,
                "decision": decision,
            },
        )

    return package


def _create_admin_action_evidence(
    actor: Dict[str, Any],
    saved_action: Dict[str, Any],
    decision: Dict[str, Any],
    policy_report: Dict[str, Any],
    context: Dict[str, Any],
) -> Dict[str, Any]:
    return create_evidence_capsule(
        user=actor,
        app_name="tower_admin",
        action=saved_action.get("admin_action"),
        object_type=saved_action.get("object_type") or "admin_action",
        object_id=saved_action.get("object_id") or saved_action.get("admin_action_id"),
        decision=decision,
        policy_report=policy_report,
        session_context=context,
        object_context={
            "admin_action_id": saved_action.get("admin_action_id"),
            "target_user_id": saved_action.get("target_user_id"),
            "target_app": saved_action.get("target_app"),
            "requested_changes": saved_action.get("requested_changes"),
            "admin_action_hash": saved_action.get("admin_action_hash"),
        },
        token_context={
            "admin_action_id": saved_action.get("admin_action_id"),
            "admin_action_status": saved_action.get("status"),
        },
        trigger="admin_action_gate",
        created_by="tower_admin_action_gate",
        notes=f"Evidence capsule for admin action {saved_action.get('admin_action_id')}.",
    )


def get_admin_action(admin_action_id: str) -> Optional[Dict[str, Any]]:
    data = _load_raw()

    for item in data.get("admin_actions", []):
        if item.get("admin_action_id") == admin_action_id:
            return item

    return None


def list_admin_actions(limit: int = 25) -> List[Dict[str, Any]]:
    data = _load_raw()
    return data.get("admin_actions", [])[-limit:]


def verify_admin_action(admin_action_id: str) -> Dict[str, Any]:
    item = get_admin_action(admin_action_id)

    if not item:
        return {
            "ok": False,
            "reason_code": "admin_action_not_found",
            "human_reason": "Admin action package was not found.",
            "admin_action_id": admin_action_id,
        }

    stored = item.get("admin_action_hash")
    clean = dict(item)
    clean.pop("admin_action_hash", None)

    recalculated = _hash_payload(clean)
    ok = stored == recalculated

    return {
        "ok": ok,
        "reason_code": "admin_action_valid" if ok else "admin_action_hash_mismatch",
        "human_reason": "Admin action package is valid." if ok else "Admin action package hash does not match.",
        "admin_action_id": admin_action_id,
        "stored_hash": stored,
        "recalculated_hash": recalculated,
        "status": item.get("status"),
    }


def get_admin_action_summary() -> Dict[str, Any]:
    data = _load_raw()
    actions = data.get("admin_actions", [])

    summary = {
        "total_admin_actions": len(actions),
        "approved": 0,
        "denied": 0,
        "step_up_required": 0,
        "locked": 0,
        "quarantined": 0,
        "executed": 0,
        "revoked": 0,
        "by_action": {},
        "by_actor": {},
    }

    for item in actions:
        status = item.get("status") or "unknown"
        action = item.get("admin_action") or "unknown"
        actor = item.get("actor_user_id") or "unknown"

        if status in summary:
            summary[status] += 1

        summary["by_action"][action] = summary["by_action"].get(action, 0) + 1
        summary["by_actor"][actor] = summary["by_actor"].get(actor, 0) + 1

    return summary
