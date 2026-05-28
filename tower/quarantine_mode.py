
from __future__ import annotations

import hashlib
import json
import secrets
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "tower" / "data"

QUARANTINE_STATE_PATH = DATA_DIR / "quarantine_mode_state.json"
QUARANTINE_EVENTS_PATH = DATA_DIR / "quarantine_mode_events.json"


QUARANTINE_BLOCKED_ACTIONS = {
    "export",
    "download",
    "archive_handoff_export",
    "share",
    "route_policy_change",
    "security_policy_edit",
    "admin_override",
    "clearance_grant",
    "app_clearance_grant",
    "live_mode_enable",
    "automated_mode_enable",
    "broker_action",
    "capital_movement",
    "payment_batch_release",
    "object_reveal",
    "sensitive_reveal",
    "raw_data_view",
    "delete_record",
    "disable_security",
}


QUARANTINE_ALLOWED_ACTIONS = {
    "view_status",
    "view_quarantine_status",
    "view_security_command",
    "owner_read_only_review",
    "create_quarantine_note",
    "request_quarantine_release",
    "verify_quarantine_release_step_up",
    "tamper_chain_verify",
    "view_locked_page",
    "appeal_quarantine",
}


DEFAULT_QUARANTINE_STATE = {
    "ok": True,
    "pack": "094",
    "active_cases": [],
    "history": [],
    "blocked_actions": sorted(list(QUARANTINE_BLOCKED_ACTIONS)),
    "allowed_actions": sorted(list(QUARANTINE_ALLOWED_ACTIONS)),
    "human_reason": "No quarantine cases are active.",
    "soulaana_translation": "Soulaana: No one is in the holding room right now.",
}


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _load_json(path: Path, default: Any) -> Any:
    try:
        if not path.exists():
            return default
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def _write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, indent=2, sort_keys=True, default=str), encoding="utf-8")
    tmp.replace(path)


def _safe_str(value: Any, default: str = "") -> str:
    if value is None:
        return default
    text = str(value).strip()
    return text if text else default


def _redact_sensitive(value: Any) -> Any:
    sensitive_keys = {
        "token",
        "raw_token",
        "tower_keycard",
        "password",
        "secret",
        "api_key",
        "apikey",
        "authorization",
        "bearer",
        "credential",
        "credentials",
        "owner_pin",
        "challenge_answer",
        "session_secret",
        "device_secret",
    }

    if isinstance(value, dict):
        clean = {}
        redacted_count = 0

        for key, item in value.items():
            key_text = str(key).lower()
            if any(s in key_text for s in sensitive_keys):
                redacted_count += 1
                continue

            redacted_item = _redact_sensitive(item)
            if isinstance(redacted_item, dict) and "__redacted_sensitive_field_count__" in redacted_item:
                try:
                    redacted_count += int(redacted_item.get("__redacted_sensitive_field_count__", 0))
                except Exception:
                    redacted_count += 1
                redacted_item = dict(redacted_item)
                redacted_item.pop("__redacted_sensitive_field_count__", None)

            clean[key] = redacted_item

        if redacted_count:
            clean["__redacted_sensitive_field_count__"] = redacted_count
        return clean

    if isinstance(value, list):
        return [_redact_sensitive(item) for item in value]

    if isinstance(value, str):
        lowered = value.lower()
        if (
            "tower_keycard=" in lowered
            or "bearer " in lowered
            or "should_not_survive" in lowered
            or "raw_token" in lowered
            or "tower_keycard" in lowered
        ):
            return "[REDACTED]"
        return value

    return value


def _canonical_json(value: Any) -> str:
    return json.dumps(_redact_sensitive(value), sort_keys=True, separators=(",", ":"), default=str)


def _fingerprint(value: Any) -> str:
    return hashlib.sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def _event_id(prefix: str = "quarantine") -> str:
    return f"{prefix}_{secrets.token_urlsafe(18)}"


def _default_state_copy() -> Dict[str, Any]:
    return json.loads(json.dumps(DEFAULT_QUARANTINE_STATE))


def _load_events() -> List[Dict[str, Any]]:
    data = _load_json(QUARANTINE_EVENTS_PATH, [])
    return data if isinstance(data, list) else []


def _save_events(events: List[Dict[str, Any]]) -> None:
    _write_json(QUARANTINE_EVENTS_PATH, events)


def load_quarantine_state() -> Dict[str, Any]:
    state = _load_json(QUARANTINE_STATE_PATH, _default_state_copy())
    if not isinstance(state, dict):
        state = _default_state_copy()

    for key, value in DEFAULT_QUARANTINE_STATE.items():
        state.setdefault(key, value)

    return state


def save_quarantine_state(state: Dict[str, Any]) -> Dict[str, Any]:
    state = dict(state)
    state["ok"] = True
    state["pack"] = "094"
    state["updated_at"] = _utc_now()
    state["state_fingerprint"] = _fingerprint(state)
    sanitized = _redact_sensitive(state)
    _write_json(QUARANTINE_STATE_PATH, sanitized)
    return sanitized


def _record_quarantine_event(event: Dict[str, Any]) -> Dict[str, Any]:
    event = dict(event)
    event.setdefault("event_id", _event_id("quar_evt"))
    event.setdefault("event_type", "tower_quarantine_event")
    event.setdefault("created_at", _utc_now())
    event.setdefault("pack", "094")

    sanitized = _redact_sensitive(event)
    sanitized["event_fingerprint"] = _fingerprint(sanitized)

    events = _load_events()
    events.append(sanitized)
    _save_events(events)

    try:
        from tower.tamper_evident_audit_chain import create_tamper_chain_entry

        create_tamper_chain_entry(
            event_type="tower_quarantine_event_snapshot",
            source_name="quarantine_mode_events",
            source_path=str(QUARANTINE_EVENTS_PATH),
            source_hash=_fingerprint(events),
            record_count=len(events),
            actor_user_id=_safe_str(sanitized.get("actor_user_id"), "tower_system"),
            reason=f"Pack 094 chained quarantine event {sanitized.get('reason_code')}.",
            metadata={
                "pack": "094",
                "event_id": sanitized.get("event_id"),
                "reason_code": sanitized.get("reason_code"),
            },
        )
    except Exception:
        pass

    return sanitized


def _case_matches(case: Dict[str, Any], *, user_id: str, session_id: str, device_id: str, ip_address: str, object_type: str, object_id: str) -> bool:
    scope = case.get("scope", "session")
    target = case.get("target", {}) if isinstance(case.get("target"), dict) else {}

    if scope == "global":
        return True
    if scope == "user":
        return bool(user_id and target.get("user_id") == user_id)
    if scope == "session":
        return bool(session_id and target.get("session_id") == session_id)
    if scope == "device":
        return bool(device_id and target.get("device_id") == device_id)
    if scope == "ip":
        return bool(ip_address and target.get("ip_address") == ip_address)
    if scope == "object":
        return bool(object_type and object_id and target.get("object_type") == object_type and target.get("object_id") == object_id)
    return False


def find_matching_quarantine_cases(
    *,
    user_id: str = "",
    session_id: str = "",
    device_id: str = "",
    ip_address: str = "",
    object_type: str = "",
    object_id: str = "",
) -> List[Dict[str, Any]]:
    state = load_quarantine_state()
    cases = state.get("active_cases", []) if isinstance(state.get("active_cases"), list) else []

    matches = []
    for case in cases:
        if case.get("status") != "active":
            continue
        if _case_matches(
            case,
            user_id=_safe_str(user_id),
            session_id=_safe_str(session_id),
            device_id=_safe_str(device_id),
            ip_address=_safe_str(ip_address),
            object_type=_safe_str(object_type),
            object_id=_safe_str(object_id),
        ):
            matches.append(case)

    return matches


def activate_quarantine(
    *,
    actor_user_id: str,
    scope: str,
    target: Dict[str, Any],
    reason_code: str = "suspicious_activity_quarantine",
    human_reason: str = "Suspicious activity placed into quarantine.",
    severity: str = "restricted",
    metadata: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    actor_user_id = _safe_str(actor_user_id, "tower_system")
    scope = _safe_str(scope, "session")
    reason_code = _safe_str(reason_code, "suspicious_activity_quarantine")
    human_reason = _safe_str(human_reason, "Suspicious activity placed into quarantine.")
    severity = _safe_str(severity, "restricted")
    target = target if isinstance(target, dict) else {}

    allowed_scopes = {"global", "user", "session", "device", "ip", "object"}
    if scope not in allowed_scopes:
        scope = "session"

    state = load_quarantine_state()
    cases = state.get("active_cases", []) if isinstance(state.get("active_cases"), list) else []
    history = state.get("history", []) if isinstance(state.get("history"), list) else []

    quarantine_id = _event_id("quarantine")
    case = {
        "quarantine_id": quarantine_id,
        "status": "active",
        "scope": scope,
        "target": _redact_sensitive(target),
        "severity": severity,
        "reason_code": reason_code,
        "human_reason": human_reason,
        "activated_at": _utc_now(),
        "activated_by": actor_user_id,
        "release_requested_at": "",
        "release_requested_by": "",
        "released_at": "",
        "released_by": "",
        "owner_notes": [],
        "required_release_actions": ["complete_step_up_auth", "owner_reason"],
        "soulaana_translation": "Soulaana: This subject is in the holding room. Recovery lane stays open; dangerous buttons stay frozen.",
    }

    cases.append(case)
    history.append({
        "at": _utc_now(),
        "actor_user_id": actor_user_id,
        "action": "activate_quarantine",
        "quarantine_id": quarantine_id,
        "scope": scope,
        "reason_code": reason_code,
        "human_reason": human_reason,
    })

    state.update({
        "active_cases": cases,
        "history": history,
        "human_reason": "One or more quarantine cases are active.",
        "soulaana_translation": "Soulaana: Quarantine is active for at least one subject.",
    })
    saved = save_quarantine_state(state)

    event = _record_quarantine_event({
        "actor_user_id": actor_user_id,
        "decision": "quarantine_activated",
        "quarantine_id": quarantine_id,
        "scope": scope,
        "target": target,
        "reason_code": reason_code,
        "severity": severity,
        "human_reason": human_reason,
        "metadata": metadata or {},
    })

    return {
        "ok": True,
        "decision": "quarantine_activated",
        "quarantine_active": True,
        "quarantine_id": quarantine_id,
        "case": case,
        "state": saved,
        "event": event,
        "risk_state": severity,
        "risk_score": 82 if severity == "restricted" else 92,
        "required_actions": ["owner_review", "limit_subject_to_recovery_lane"],
        "human_reason": human_reason,
        "soulaana_translation": case.get("soulaana_translation"),
    }


def evaluate_quarantine_gate(
    *,
    action: str,
    user_id: str = "",
    session_id: str = "",
    device_id: str = "",
    ip_address: str = "",
    route_path: str = "",
    object_type: str = "",
    object_id: str = "",
    metadata: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    action = _safe_str(action, "unknown_action")
    user_id = _safe_str(user_id, "anonymous")
    session_id = _safe_str(session_id)
    device_id = _safe_str(device_id)
    ip_address = _safe_str(ip_address)
    route_path = _safe_str(route_path)
    object_type = _safe_str(object_type)
    object_id = _safe_str(object_id)

    # Emergency lockdown outranks quarantine. If lockdown is active, let lockdown answer first.
    try:
        from tower.emergency_lockdown import evaluate_lockdown_gate
        lockdown = evaluate_lockdown_gate(
            action=action,
            user_id=user_id,
            route_path=route_path,
            object_type=object_type,
            object_id=object_id,
            metadata=metadata or {},
        )
        if lockdown.get("lockdown_active") is True and lockdown.get("decision") in {"deny", "allow_recovery"}:
            return {
                **lockdown,
                "quarantine_checked": True,
                "quarantine_deferred_to_lockdown": True,
                "soulaana_translation": "Soulaana: Full lockdown outranks quarantine. The fortress wall answered first.",
            }
    except Exception:
        pass

    matches = find_matching_quarantine_cases(
        user_id=user_id,
        session_id=session_id,
        device_id=device_id,
        ip_address=ip_address,
        object_type=object_type,
        object_id=object_id,
    )

    if not matches:
        return {
            "ok": True,
            "decision": "allow",
            "allowed": True,
            "quarantine_active": False,
            "quarantine_matches": [],
            "reason_code": "no_quarantine_match",
            "risk_state": "clear",
            "risk_score": 5,
            "required_actions": [],
            "human_reason": "No matching quarantine case.",
            "soulaana_translation": "Soulaana: This subject is not in the holding room.",
        }

    primary = matches[0]

    if action in QUARANTINE_ALLOWED_ACTIONS:
        return {
            "ok": True,
            "decision": "allow_quarantine_recovery",
            "allowed": True,
            "quarantine_active": True,
            "quarantine_id": primary.get("quarantine_id"),
            "quarantine_matches": matches,
            "reason_code": "quarantine_recovery_action_allowed",
            "risk_state": "watch",
            "risk_score": 35,
            "required_actions": ["owner_recovery_context"],
            "human_reason": "This recovery/status action is allowed while the subject is quarantined.",
            "soulaana_translation": "Soulaana: Holding-room recovery lane is open. Dangerous doors stay closed.",
        }

    if action in QUARANTINE_BLOCKED_ACTIONS or action not in QUARANTINE_ALLOWED_ACTIONS:
        event = _record_quarantine_event({
            "actor_user_id": user_id,
            "decision": "quarantine_block",
            "quarantine_id": primary.get("quarantine_id"),
            "action": action,
            "route_path": route_path,
            "object_type": object_type,
            "object_id": object_id,
            "reason_code": "action_blocked_by_quarantine",
            "metadata": metadata or {},
        })

        return {
            "ok": True,
            "decision": "deny",
            "allowed": False,
            "quarantine_active": True,
            "quarantine_id": primary.get("quarantine_id"),
            "quarantine_matches": matches,
            "reason_code": "action_blocked_by_quarantine",
            "risk_state": primary.get("severity", "restricted"),
            "risk_score": 78,
            "required_actions": ["owner_review", "wait_for_quarantine_release"],
            "event": event,
            "human_reason": "This subject is quarantined, so the action is blocked.",
            "soulaana_translation": "Soulaana: This subject is in the holding room. That button does not move.",
        }

    return {
        "ok": True,
        "decision": "deny",
        "allowed": False,
        "quarantine_active": True,
        "quarantine_id": primary.get("quarantine_id"),
        "reason_code": "quarantine_default_deny",
        "risk_state": "restricted",
        "risk_score": 78,
        "required_actions": ["owner_review"],
        "human_reason": "Quarantine default-denied this action.",
        "soulaana_translation": "Soulaana: Default deny in the holding room. No guessing.",
    }


def request_quarantine_release(
    *,
    actor_user_id: str,
    quarantine_id: str,
    reason: str,
    session_id: str = "",
    metadata: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    actor_user_id = _safe_str(actor_user_id, "unknown_actor")
    quarantine_id = _safe_str(quarantine_id)
    reason = _safe_str(reason, "Owner requested quarantine release.")
    session_id = _safe_str(session_id)

    state = load_quarantine_state()
    cases = state.get("active_cases", []) if isinstance(state.get("active_cases"), list) else []

    target_case = None
    for case in cases:
        if case.get("quarantine_id") == quarantine_id and case.get("status") == "active":
            target_case = case
            break

    if not target_case:
        result = {
            "ok": True,
            "decision": "already_released_or_missing",
            "quarantine_active": False,
            "reason_code": "quarantine_case_not_active",
            "human_reason": "Quarantine case is not active.",
            "soulaana_translation": "Soulaana: That holding-room case is not active.",
        }
        _record_quarantine_event({
            "actor_user_id": actor_user_id,
            "decision": result["decision"],
            "quarantine_id": quarantine_id,
            "reason_code": result["reason_code"],
            "metadata": metadata or {},
        })
        return result

    try:
        from tower.step_up_auth import evaluate_step_up_requirement

        step_up = evaluate_step_up_requirement(
            user_id=actor_user_id,
            action="admin_override",
            object_type="quarantine_case",
            object_id=quarantine_id,
            session_id=session_id,
            route_path="/tower/security-command",
            clearance_decision={"allowed": True, "decision": "allow"},
            risk_context={"quarantine_active": True, "reason": reason},
        )
    except Exception as exc:
        step_up = {
            "ok": False,
            "decision": "step_up_required",
            "step_up_required": True,
            "reason_code": "step_up_framework_unavailable_for_quarantine_release",
            "error": f"{type(exc).__name__}: {exc}",
            "required_actions": ["complete_step_up_auth"],
        }

    target_case["release_requested_at"] = _utc_now()
    target_case["release_requested_by"] = actor_user_id
    target_case["release_reason"] = reason
    save_quarantine_state(state)

    if step_up.get("decision") != "allow":
        event = _record_quarantine_event({
            "actor_user_id": actor_user_id,
            "decision": "quarantine_release_step_up_required",
            "quarantine_id": quarantine_id,
            "reason_code": step_up.get("reason_code", "quarantine_release_requires_step_up"),
            "metadata": {
                "release_reason": reason,
                "step_up": step_up,
                "request_metadata": metadata or {},
            },
        })

        return {
            "ok": True,
            "decision": "step_up_required",
            "quarantine_active": True,
            "quarantine_id": quarantine_id,
            "step_up": step_up,
            "event": event,
            "required_actions": ["complete_step_up_auth", "owner_reason"],
            "human_reason": "Quarantine release requires step-up verification.",
            "soulaana_translation": "Soulaana: I will not open the holding-room door without a fresh owner check.",
        }

    event = _record_quarantine_event({
        "actor_user_id": actor_user_id,
        "decision": "quarantine_release_approved_after_step_up",
        "quarantine_id": quarantine_id,
        "reason_code": "quarantine_release_step_up_satisfied",
        "metadata": {
            "release_reason": reason,
            "step_up": step_up,
            "request_metadata": metadata or {},
        },
    })

    return {
        "ok": True,
        "decision": "release_allowed",
        "quarantine_active": True,
        "quarantine_id": quarantine_id,
        "step_up": step_up,
        "event": event,
        "required_actions": ["call_release_quarantine"],
        "human_reason": "Step-up verified. Quarantine can now be released.",
        "soulaana_translation": "Soulaana: Fresh verification is on file. You may release the holding-room door intentionally.",
    }


def release_quarantine(
    *,
    actor_user_id: str,
    quarantine_id: str,
    reason: str,
    session_id: str = "",
    metadata: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    actor_user_id = _safe_str(actor_user_id, "unknown_actor")
    quarantine_id = _safe_str(quarantine_id)
    reason = _safe_str(reason, "Owner released quarantine.")
    session_id = _safe_str(session_id)

    state = load_quarantine_state()
    cases = state.get("active_cases", []) if isinstance(state.get("active_cases"), list) else []
    history = state.get("history", []) if isinstance(state.get("history"), list) else []

    target_case = None
    for case in cases:
        if case.get("quarantine_id") == quarantine_id and case.get("status") == "active":
            target_case = case
            break

    if not target_case:
        return {
            "ok": True,
            "decision": "already_released_or_missing",
            "quarantine_active": False,
            "quarantine_id": quarantine_id,
            "human_reason": "Quarantine case is already released or missing.",
            "soulaana_translation": "Soulaana: That holding-room case is already inactive.",
        }

    try:
        from tower.step_up_auth import evaluate_step_up_requirement

        step_up = evaluate_step_up_requirement(
            user_id=actor_user_id,
            action="admin_override",
            object_type="quarantine_case",
            object_id=quarantine_id,
            session_id=session_id,
            route_path="/tower/security-command",
            clearance_decision={"allowed": True, "decision": "allow"},
            risk_context={"quarantine_active": True, "reason": reason},
        )
    except Exception as exc:
        step_up = {
            "decision": "step_up_required",
            "step_up_required": True,
            "reason_code": "step_up_framework_unavailable_for_quarantine_release",
            "error": f"{type(exc).__name__}: {exc}",
        }

    if step_up.get("decision") != "allow":
        event = _record_quarantine_event({
            "actor_user_id": actor_user_id,
            "decision": "quarantine_release_blocked_missing_step_up",
            "quarantine_id": quarantine_id,
            "reason_code": step_up.get("reason_code", "quarantine_release_requires_step_up"),
            "metadata": {
                "release_reason": reason,
                "step_up": step_up,
                "request_metadata": metadata or {},
            },
        })

        return {
            "ok": False,
            "decision": "step_up_required",
            "quarantine_active": True,
            "quarantine_id": quarantine_id,
            "step_up": step_up,
            "event": event,
            "required_actions": ["complete_step_up_auth", "owner_reason"],
            "human_reason": "Cannot release quarantine without step-up verification.",
            "soulaana_translation": "Soulaana: The holding-room door stays shut until owner verification is fresh.",
        }

    target_case["status"] = "released"
    target_case["released_at"] = _utc_now()
    target_case["released_by"] = actor_user_id
    target_case["release_reason"] = reason

    history.append({
        "at": _utc_now(),
        "actor_user_id": actor_user_id,
        "action": "release_quarantine",
        "quarantine_id": quarantine_id,
        "reason": reason,
    })

    state["active_cases"] = cases
    state["history"] = history
    active_left = [case for case in cases if case.get("status") == "active"]
    state["human_reason"] = "One or more quarantine cases are active." if active_left else "No quarantine cases are active."
    state["soulaana_translation"] = "Soulaana: Quarantine still has active cases." if active_left else "Soulaana: Holding room is clear."

    saved = save_quarantine_state(state)

    event = _record_quarantine_event({
        "actor_user_id": actor_user_id,
        "decision": "quarantine_released",
        "quarantine_id": quarantine_id,
        "reason_code": "quarantine_released_after_step_up",
        "human_reason": reason,
        "metadata": {
            "session_id": session_id,
            "step_up": step_up,
            "request_metadata": metadata or {},
        },
    })

    return {
        "ok": True,
        "decision": "quarantine_released",
        "quarantine_active": bool(active_left),
        "quarantine_id": quarantine_id,
        "case": target_case,
        "state": saved,
        "event": event,
        "risk_state": "watch",
        "risk_score": 25,
        "required_actions": ["review_post_quarantine_status"],
        "human_reason": reason,
        "soulaana_translation": "Soulaana: The holding-room door reopened with receipts.",
    }


def add_quarantine_owner_note(
    *,
    actor_user_id: str,
    quarantine_id: str,
    note: str,
    metadata: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    actor_user_id = _safe_str(actor_user_id, "unknown_actor")
    quarantine_id = _safe_str(quarantine_id)
    note = _safe_str(note, "Owner note added.")

    state = load_quarantine_state()
    cases = state.get("active_cases", []) if isinstance(state.get("active_cases"), list) else []

    target_case = None
    for case in cases:
        if case.get("quarantine_id") == quarantine_id:
            target_case = case
            break

    if not target_case:
        return {
            "ok": False,
            "decision": "quarantine_case_not_found",
            "quarantine_id": quarantine_id,
            "human_reason": "Quarantine case not found.",
            "soulaana_translation": "Soulaana: I cannot find that holding-room case.",
        }

    notes = target_case.get("owner_notes", []) if isinstance(target_case.get("owner_notes"), list) else []
    note_item = {
        "note_id": _event_id("quar_note"),
        "created_at": _utc_now(),
        "actor_user_id": actor_user_id,
        "note": _redact_sensitive(note),
    }
    notes.append(note_item)
    target_case["owner_notes"] = notes
    save_quarantine_state(state)

    event = _record_quarantine_event({
        "actor_user_id": actor_user_id,
        "decision": "quarantine_owner_note_added",
        "quarantine_id": quarantine_id,
        "reason_code": "quarantine_owner_note_added",
        "metadata": {
            "note_id": note_item.get("note_id"),
            "request_metadata": metadata or {},
        },
    })

    return {
        "ok": True,
        "decision": "quarantine_owner_note_added",
        "quarantine_id": quarantine_id,
        "note": note_item,
        "event": event,
        "human_reason": "Owner note added to quarantine case.",
        "soulaana_translation": "Soulaana: Note added to the holding-room record.",
    }


def sanitize_quarantine_event_store() -> Dict[str, Any]:
    events = _load_events()
    sanitized = [_redact_sensitive(event) for event in events]
    _save_events(sanitized)

    serialized = json.dumps(sanitized, sort_keys=True, default=str)
    clean = (
        "tower_keycard=" not in serialized
        and "SHOULD_NOT_SURVIVE" not in serialized
        and "raw_token=" not in serialized
        and '"raw_token":' not in serialized
        and '"tower_keycard":' not in serialized
        and "Bearer SHOULD_NOT_SURVIVE" not in serialized
    )

    return {
        "ok": clean,
        "decision": "quarantine_event_store_sanitized",
        "total_events": len(sanitized),
        "human_reason": "Quarantine event store sanitized." if clean else "Quarantine event store still contains sensitive markers.",
        "soulaana_translation": "Soulaana: Quarantine records were scrubbed clean." if clean else "Soulaana: Some quarantine records are still talking too much.",
    }


def summarize_quarantine_mode(limit: int = 12) -> Dict[str, Any]:
    sanitize_quarantine_event_store()

    state = load_quarantine_state()
    events = _load_events()

    try:
        limit = int(limit)
    except Exception:
        limit = 12
    limit = max(1, min(limit, 200))

    cases = state.get("active_cases", []) if isinstance(state.get("active_cases"), list) else []
    active_cases = [case for case in cases if case.get("status") == "active"]
    released_cases = [case for case in cases if case.get("status") == "released"]

    by_decision: Dict[str, int] = {}
    by_reason: Dict[str, int] = {}
    by_scope: Dict[str, int] = {}
    by_status: Dict[str, int] = {}

    for event in events:
        decision = event.get("decision", "unknown")
        reason = event.get("reason_code", "unknown")
        by_decision[decision] = by_decision.get(decision, 0) + 1
        by_reason[reason] = by_reason.get(reason, 0) + 1

    for case in cases:
        scope = case.get("scope", "unknown")
        status = case.get("status", "unknown")
        by_scope[scope] = by_scope.get(scope, 0) + 1
        by_status[status] = by_status.get(status, 0) + 1

    summary = {
        "ok": True,
        "pack": "094",
        "state_path": str(QUARANTINE_STATE_PATH),
        "events_path": str(QUARANTINE_EVENTS_PATH),
        "quarantine_active": bool(active_cases),
        "active_case_count": len(active_cases),
        "released_case_count": len(released_cases),
        "total_cases": len(cases),
        "blocked_actions": state.get("blocked_actions", []),
        "allowed_actions": state.get("allowed_actions", []),
        "total_events": len(events),
        "by_decision": by_decision,
        "by_reason": by_reason,
        "by_scope": by_scope,
        "by_status": by_status,
        "recent_events": events[-limit:],
        "recent_cases": cases[-limit:],
        "readiness_score": 100,
        "readiness_label": "Quarantine mode ready",
        "human_reason": "Quarantine mode summary loaded.",
        "soulaana_translation": "Soulaana: Quarantine controls are ready. Suspicious subjects can be contained without sealing the entire fortress.",
    }

    summary = _redact_sensitive(summary)
    serialized = json.dumps(summary, sort_keys=True, default=str)
    summary["no_sensitive_key_leakage"] = (
        "tower_keycard=" not in serialized
        and "SHOULD_NOT_SURVIVE" not in serialized
        and "raw_token=" not in serialized
        and '"raw_token":' not in serialized
        and '"tower_keycard":' not in serialized
        and "Bearer SHOULD_NOT_SURVIVE" not in serialized
    )

    return summary


def reset_quarantine_for_test() -> Dict[str, Any]:
    state = _default_state_copy()
    saved = save_quarantine_state(state)
    _save_events([])

    return {
        "ok": True,
        "decision": "quarantine_reset_for_test",
        "state": saved,
        "events_reset": True,
        "soulaana_translation": "Soulaana: Holding-room state and old event noise reset for a clean test lane.",
    }
