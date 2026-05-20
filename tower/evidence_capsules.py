# =============================================================================
# THE TOWER — EVIDENCE CAPSULES
# FILE: tower/evidence_capsules.py
# =============================================================================

import hashlib
import json
import os
import secrets
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from tower.audit import read_recent_audit_events, write_audit_event
from tower.policy_engine import evaluate_policy
from tower.security_events import create_security_event


PROJECT_ROOT = os.environ.get("SIMPLEE_PROJECT_ROOT", "/content/SimpleeMrkTrade_REAL_CLONE")
TOWER_DATA_DIR = Path(PROJECT_ROOT) / "tower" / "data"
EVIDENCE_CAPSULES_PATH = TOWER_DATA_DIR / "evidence_capsules.json"

TOWER_DATA_DIR.mkdir(parents=True, exist_ok=True)


def _now() -> str:
    return datetime.utcnow().isoformat() + "Z"


def _safe_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, default=str)


def _hash_payload(payload: Dict[str, Any]) -> str:
    raw = _safe_json(payload).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def _load_raw() -> Dict[str, Any]:
    if not EVIDENCE_CAPSULES_PATH.exists():
        return {"capsules": []}

    try:
        with EVIDENCE_CAPSULES_PATH.open("r", encoding="utf-8") as f:
            data = json.load(f)

        if not isinstance(data, dict):
            return {"capsules": []}

        if not isinstance(data.get("capsules"), list):
            data["capsules"] = []

        return data
    except Exception:
        return {"capsules": []}


def _save_raw(data: Dict[str, Any]) -> None:
    tmp_path = EVIDENCE_CAPSULES_PATH.with_suffix(".tmp")
    with tmp_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, sort_keys=True, default=str)

    tmp_path.replace(EVIDENCE_CAPSULES_PATH)


def _latest_audit_hash() -> Optional[str]:
    rows = read_recent_audit_events(limit=1)
    if not rows:
        return None
    return rows[-1].get("event_hash")


def create_evidence_capsule(
    user: Dict[str, Any],
    app_name: str,
    action: str = "enter_app",
    mode_name: Optional[str] = None,
    object_type: Optional[str] = None,
    object_id: Optional[str] = None,
    decision: Optional[Dict[str, Any]] = None,
    policy_report: Optional[Dict[str, Any]] = None,
    session_context: Optional[Dict[str, Any]] = None,
    token_context: Optional[Dict[str, Any]] = None,
    object_context: Optional[Dict[str, Any]] = None,
    trigger: str = "manual",
    created_by: str = "tower",
    notes: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Creates an evidence capsule.

    Baby version:
    This makes a little case file that says:
    - who
    - what app
    - what they tried
    - what The Tower decided
    - why
    - what proof was attached
    """

    session_context = session_context or {}
    token_context = token_context or {}
    object_context = object_context or {}

    if policy_report is None:
        try:
            policy_report = evaluate_policy(
                user=user,
                app_name=app_name,
                action=action,
                mode_name=mode_name,
                object_type=object_type,
                object_id=object_id,
                context=session_context,
            ).to_dict()
        except Exception as exc:
            policy_report = {
                "allowed": False,
                "decision": "deny",
                "reason_code": "policy_report_error",
                "human_reason": f"Could not create policy report: {exc}",
                "error": str(exc),
            }

    decision = decision or policy_report

    capsule_id = secrets.token_urlsafe(18)

    base_capsule = {
        "capsule_id": capsule_id,
        "created_at": _now(),
        "created_by": created_by,
        "trigger": trigger,
        "status": "open",
        "notes": notes,

        "user": {
            "user_id": user.get("user_id"),
            "email": user.get("email"),
            "display_name": user.get("display_name"),
            "role": user.get("role"),
            "account_type": user.get("account_type"),
            "status": user.get("status"),
            "risk_state": user.get("risk_state"),
            "trust_score": user.get("trust_score"),
        },

        "request": {
            "app_name": app_name,
            "action": action,
            "mode_name": mode_name,
            "object_type": object_type,
            "object_id": object_id,
        },

        "decision": decision,
        "policy_report": policy_report,

        "risk": {
            "decision_risk_score": decision.get("risk_score") if isinstance(decision, dict) else None,
            "decision_risk_state": decision.get("risk_state") if isinstance(decision, dict) else None,
            "policy_risk_score": policy_report.get("risk_score") if isinstance(policy_report, dict) else None,
            "policy_risk_state": policy_report.get("risk_state") if isinstance(policy_report, dict) else None,
        },

        "context": {
            "session": session_context,
            "token": token_context,
            "object": object_context,
        },

        "audit": {
            "latest_audit_hash_at_creation": _latest_audit_hash(),
        },
    }

    capsule_hash = _hash_payload(base_capsule)
    capsule = dict(base_capsule)
    capsule["capsule_hash"] = capsule_hash

    data = _load_raw()
    data["capsules"].append(capsule)
    _save_raw(data)

    write_audit_event(
        actor_user_id=created_by,
        target_user_id=str(user.get("user_id", "unknown")),
        action="create_evidence_capsule",
        app_name="tower_admin",
        object_type="evidence_capsule",
        object_id=capsule_id,
        result="allow",
        reason_code="evidence_capsule_created",
        human_reason="Tower evidence capsule was created.",
        risk_score=int(capsule.get("risk", {}).get("decision_risk_score") or 20),
        risk_state=str(capsule.get("risk", {}).get("decision_risk_state") or "clear"),
        metadata={
            "capsule_id": capsule_id,
            "capsule_hash": capsule_hash,
            "trigger": trigger,
            "request": capsule.get("request"),
        },
    )

    if str(decision.get("decision") if isinstance(decision, dict) else "").lower() in {"deny", "step_up", "quarantine", "lockdown"}:
        create_security_event(
            user_id=str(user.get("user_id", "unknown")),
            event_type="evidence_capsule_for_security_decision",
            severity="medium",
            source_app=app_name,
            description="Evidence capsule created for a security-relevant Tower decision.",
            recommended_action="review_capsule_if_needed",
            metadata={
                "capsule_id": capsule_id,
                "capsule_hash": capsule_hash,
                "decision": decision.get("decision") if isinstance(decision, dict) else None,
                "reason_code": decision.get("reason_code") if isinstance(decision, dict) else None,
            },
        )

    return capsule


def get_evidence_capsule(capsule_id: str) -> Optional[Dict[str, Any]]:
    data = _load_raw()

    for capsule in data.get("capsules", []):
        if capsule.get("capsule_id") == capsule_id:
            return capsule

    return None


def list_evidence_capsules(limit: int = 25) -> List[Dict[str, Any]]:
    data = _load_raw()
    return data.get("capsules", [])[-limit:]


def verify_evidence_capsule(capsule_id: str) -> Dict[str, Any]:
    """
    Checks whether the capsule hash still matches.

    Baby version:
    This asks:
    "Did somebody secretly change the case file?"
    """

    capsule = get_evidence_capsule(capsule_id)

    if not capsule:
        return {
            "ok": False,
            "reason_code": "evidence_capsule_not_found",
            "human_reason": "Evidence capsule was not found.",
            "capsule_id": capsule_id,
        }

    stored_hash = capsule.get("capsule_hash")
    clean = dict(capsule)
    clean.pop("capsule_hash", None)

    recalculated_hash = _hash_payload(clean)

    ok = stored_hash == recalculated_hash

    return {
        "ok": ok,
        "reason_code": "evidence_capsule_valid" if ok else "evidence_capsule_hash_mismatch",
        "human_reason": "Evidence capsule is valid." if ok else "Evidence capsule hash does not match.",
        "capsule_id": capsule_id,
        "stored_hash": stored_hash,
        "recalculated_hash": recalculated_hash,
    }


def close_evidence_capsule(
    capsule_id: str,
    closed_by: str,
    resolution: str = "reviewed",
    notes: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    """
    Closes an evidence capsule after review.

    Baby version:
    This says, "I looked at the case file."
    """

    data = _load_raw()
    updated = None

    for capsule in data.get("capsules", []):
        if capsule.get("capsule_id") == capsule_id:
            capsule["status"] = "closed"
            capsule["closed_at"] = _now()
            capsule["closed_by"] = closed_by
            capsule["resolution"] = resolution
            if notes:
                capsule["review_notes"] = notes

            clean = dict(capsule)
            clean.pop("capsule_hash", None)
            capsule["capsule_hash"] = _hash_payload(clean)

            updated = capsule
            break

    _save_raw(data)

    if updated:
        write_audit_event(
            actor_user_id=closed_by,
            target_user_id=str(updated.get("user", {}).get("user_id", "unknown")),
            action="close_evidence_capsule",
            app_name="tower_admin",
            object_type="evidence_capsule",
            object_id=capsule_id,
            result="allow",
            reason_code="evidence_capsule_closed",
            human_reason="Tower evidence capsule was closed.",
            risk_score=30,
            risk_state="clear",
            metadata={
                "capsule_id": capsule_id,
                "resolution": resolution,
            },
        )

    return updated


def get_evidence_summary() -> Dict[str, Any]:
    data = _load_raw()
    capsules = data.get("capsules", [])

    summary = {
        "total_capsules": len(capsules),
        "open": 0,
        "closed": 0,
        "by_app": {},
        "by_decision": {},
        "by_trigger": {},
    }

    for capsule in capsules:
        status = capsule.get("status") or "open"
        app_name = capsule.get("request", {}).get("app_name") or "unknown"
        decision = capsule.get("decision", {}).get("decision") or "unknown"
        trigger = capsule.get("trigger") or "unknown"

        if status == "closed":
            summary["closed"] += 1
        else:
            summary["open"] += 1

        summary["by_app"][app_name] = summary["by_app"].get(app_name, 0) + 1
        summary["by_decision"][decision] = summary["by_decision"].get(decision, 0) + 1
        summary["by_trigger"][trigger] = summary["by_trigger"].get(trigger, 0) + 1

    return summary
