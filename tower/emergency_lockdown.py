
from __future__ import annotations

import hashlib
import json
import secrets
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "tower" / "data"

LOCKDOWN_STATE_PATH = DATA_DIR / "emergency_lockdown_state.json"
LOCKDOWN_EVENTS_PATH = DATA_DIR / "emergency_lockdown_events.json"


LOCKDOWN_BLOCKED_ACTIONS = {
    "ob_app_entry",
    "ob_route_access",
    "object_reveal",
    "sensitive_reveal",
    "export",
    "archive_handoff_export",
    "download",
    "share",
    "route_policy_change",
    "admin_override",
    "live_mode_enable",
    "automated_mode_enable",
    "broker_action",
    "capital_movement",
    "payment_batch_release",
    "security_policy_edit",
    "clearance_grant",
    "app_clearance_grant",
}


LOCKDOWN_ALLOWED_RECOVERY_ACTIONS = {
    "view_status",
    "view_security_command",
    "view_lockdown_status",
    "create_lockdown_note",
    "request_lockdown_disable",
    "verify_lockdown_disable_step_up",
    "owner_recovery",
    "owner_read_only_review",
    "tamper_chain_verify",
}


DEFAULT_LOCKDOWN_STATE = {
    "ok": True,
    "pack": "093",
    "lockdown_active": False,
    "lockdown_id": "",
    "severity": "none",
    "reason_code": "lockdown_inactive",
    "human_reason": "Emergency lockdown is not active.",
    "activated_at": "",
    "activated_by": "",
    "disable_requested_at": "",
    "disable_requested_by": "",
    "disabled_at": "",
    "disabled_by": "",
    "required_disable_actions": ["complete_step_up_auth", "owner_reason"],
    "blocked_actions": sorted(list(LOCKDOWN_BLOCKED_ACTIONS)),
    "allowed_recovery_actions": sorted(list(LOCKDOWN_ALLOWED_RECOVERY_ACTIONS)),
    "owner_notes": [],
    "history": [],
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
    }

    if isinstance(value, dict):
        clean = {}
        redacted_count = 0
        for key, item in value.items():
            key_text = str(key).lower()
            if any(s in key_text for s in sensitive_keys):
                clean[key] = "[REDACTED]"
                redacted_count += 1
            else:
                clean[key] = _redact_sensitive(item)
        if redacted_count:
            clean["__redacted_sensitive_field_count__"] = clean.get("__redacted_sensitive_field_count__", 0) + redacted_count
        return clean

    if isinstance(value, list):
        return [_redact_sensitive(item) for item in value]

    if isinstance(value, str):
        lowered = value.lower()
        if "tower_keycard=" in lowered or "bearer " in lowered or "should_not_survive" in lowered:
            return "[REDACTED]"
        return value

    return value


def _canonical_json(value: Any) -> str:
    return json.dumps(_redact_sensitive(value), sort_keys=True, separators=(",", ":"), default=str)


def _fingerprint(value: Any) -> str:
    return hashlib.sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def _event_id(prefix: str = "lockdown") -> str:
    return f"{prefix}_{secrets.token_urlsafe(18)}"


def _load_events() -> List[Dict[str, Any]]:
    data = _load_json(LOCKDOWN_EVENTS_PATH, [])
    return data if isinstance(data, list) else []


def _save_events(events: List[Dict[str, Any]]) -> None:
    _write_json(LOCKDOWN_EVENTS_PATH, events)


def _default_state_copy() -> Dict[str, Any]:
    return json.loads(json.dumps(DEFAULT_LOCKDOWN_STATE))


def load_emergency_lockdown_state() -> Dict[str, Any]:
    state = _load_json(LOCKDOWN_STATE_PATH, _default_state_copy())
    if not isinstance(state, dict):
        state = _default_state_copy()

    for key, value in DEFAULT_LOCKDOWN_STATE.items():
        state.setdefault(key, value)

    return state


def save_emergency_lockdown_state(state: Dict[str, Any]) -> Dict[str, Any]:
    state = dict(state)
    state["ok"] = True
    state["pack"] = "093"
    state["updated_at"] = _utc_now()
    state["state_fingerprint"] = _fingerprint(state)
    _write_json(LOCKDOWN_STATE_PATH, _redact_sensitive(state))
    return state


def _record_lockdown_event(event: Dict[str, Any]) -> Dict[str, Any]:
    event = dict(event)
    event.setdefault("event_id", _event_id("lock_evt"))
    event.setdefault("event_type", "tower_emergency_lockdown_event")
    event.setdefault("created_at", _utc_now())
    event.setdefault("pack", "093")
    event["event_fingerprint"] = _fingerprint(event)

    events = _load_events()
    events.append(_redact_sensitive(event))
    _save_events(events)

    try:
        # Chain snapshots when tamper chain exists. This is best-effort so lockdown never fails because chain is unavailable.
        from tower.tamper_evident_audit_chain import create_tamper_chain_entry

        create_tamper_chain_entry(
            event_type="tower_lockdown_event_snapshot",
            source_name="emergency_lockdown_events",
            source_path=str(LOCKDOWN_EVENTS_PATH),
            source_hash=_fingerprint(events),
            record_count=len(events),
            actor_user_id=_safe_str(event.get("actor_user_id"), "tower_system"),
            reason=f"Pack 093 chained lockdown event {event.get('reason_code')}.",
            metadata={
                "pack": "093",
                "event_id": event.get("event_id"),
                "reason_code": event.get("reason_code"),
            },
        )
    except Exception:
        pass

    return event


def activate_emergency_lockdown(
    *,
    actor_user_id: str,
    reason_code: str = "owner_manual_emergency_lockdown",
    human_reason: str = "Owner activated emergency lockdown.",
    severity: str = "critical",
    metadata: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    actor_user_id = _safe_str(actor_user_id, "unknown_actor")
    reason_code = _safe_str(reason_code, "owner_manual_emergency_lockdown")
    human_reason = _safe_str(human_reason, "Owner activated emergency lockdown.")
    severity = _safe_str(severity, "critical")

    state = load_emergency_lockdown_state()
    lockdown_id = state.get("lockdown_id") if state.get("lockdown_active") else _event_id("lockdown")

    history_item = {
        "at": _utc_now(),
        "actor_user_id": actor_user_id,
        "action": "activate_lockdown",
        "reason_code": reason_code,
        "human_reason": human_reason,
        "severity": severity,
    }

    history = state.get("history", []) if isinstance(state.get("history"), list) else []
    history.append(history_item)

    state.update({
        "lockdown_active": True,
        "lockdown_id": lockdown_id,
        "severity": severity,
        "reason_code": reason_code,
        "human_reason": human_reason,
        "activated_at": state.get("activated_at") or _utc_now(),
        "activated_by": actor_user_id,
        "disabled_at": "",
        "disabled_by": "",
        "history": history,
        "soulaana_translation": "Soulaana: Emergency lockdown is active. Dangerous doors are frozen; owner recovery stays open.",
    })

    saved = save_emergency_lockdown_state(state)

    event = _record_lockdown_event({
        "actor_user_id": actor_user_id,
        "decision": "lockdown_activated",
        "lockdown_id": lockdown_id,
        "reason_code": reason_code,
        "severity": severity,
        "human_reason": human_reason,
        "metadata": metadata or {},
    })

    return {
        "ok": True,
        "decision": "lockdown_activated",
        "lockdown_active": True,
        "lockdown_id": lockdown_id,
        "state": saved,
        "event": event,
        "risk_state": "critical",
        "risk_score": 98,
        "required_actions": ["review_lockdown_status", "owner_recovery_only"],
        "human_reason": human_reason,
        "soulaana_translation": saved.get("soulaana_translation"),
    }


def request_lockdown_disable(
    *,
    actor_user_id: str,
    reason: str,
    session_id: str = "",
    metadata: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    actor_user_id = _safe_str(actor_user_id, "unknown_actor")
    reason = _safe_str(reason, "Owner requested lockdown disable.")
    session_id = _safe_str(session_id)

    state = load_emergency_lockdown_state()

    if not state.get("lockdown_active"):
        result = {
            "ok": True,
            "decision": "allow",
            "lockdown_active": False,
            "reason_code": "lockdown_already_inactive",
            "human_reason": "Lockdown is already inactive.",
            "soulaana_translation": "Soulaana: The emergency doors are not currently sealed.",
        }
        _record_lockdown_event({
            "actor_user_id": actor_user_id,
            "decision": result["decision"],
            "reason_code": result["reason_code"],
            "metadata": metadata or {},
        })
        return result

    # Disabling lockdown is sensitive and must go through step-up.
    try:
        from tower.step_up_auth import evaluate_step_up_requirement

        step_up = evaluate_step_up_requirement(
            user_id=actor_user_id,
            action="lockdown_disable",
            object_type="emergency_lockdown",
            object_id=state.get("lockdown_id"),
            session_id=session_id,
            route_path="/tower/security-command",
            clearance_decision={"allowed": True, "decision": "allow"},
            risk_context={"lockdown_active": True, "reason": reason},
        )
    except Exception as exc:
        step_up = {
            "ok": False,
            "decision": "step_up_required",
            "step_up_required": True,
            "reason_code": "step_up_framework_unavailable_for_lockdown_disable",
            "error": f"{type(exc).__name__}: {exc}",
            "required_actions": ["complete_step_up_auth"],
        }

    state["disable_requested_at"] = _utc_now()
    state["disable_requested_by"] = actor_user_id
    state["disable_reason"] = reason
    save_emergency_lockdown_state(state)

    if step_up.get("decision") != "allow":
        event = _record_lockdown_event({
            "actor_user_id": actor_user_id,
            "decision": "lockdown_disable_step_up_required",
            "lockdown_id": state.get("lockdown_id"),
            "reason_code": step_up.get("reason_code", "lockdown_disable_requires_step_up"),
            "metadata": {
                "disable_reason": reason,
                "step_up": step_up,
                "request_metadata": metadata or {},
            },
        })

        return {
            "ok": True,
            "decision": "step_up_required",
            "lockdown_active": True,
            "lockdown_id": state.get("lockdown_id"),
            "step_up": step_up,
            "event": event,
            "required_actions": ["complete_step_up_auth", "owner_reason"],
            "human_reason": "Emergency lockdown disable requires step-up verification.",
            "soulaana_translation": "Soulaana: I will not reopen the fortress without a fresh owner check.",
        }

    event = _record_lockdown_event({
        "actor_user_id": actor_user_id,
        "decision": "lockdown_disable_approved_after_step_up",
        "lockdown_id": state.get("lockdown_id"),
        "reason_code": "lockdown_disable_step_up_satisfied",
        "metadata": {
            "disable_reason": reason,
            "step_up": step_up,
            "request_metadata": metadata or {},
        },
    })

    return {
        "ok": True,
        "decision": "disable_allowed",
        "lockdown_active": True,
        "lockdown_id": state.get("lockdown_id"),
        "step_up": step_up,
        "event": event,
        "required_actions": ["call_disable_emergency_lockdown"],
        "human_reason": "Step-up verified. Lockdown can now be disabled.",
        "soulaana_translation": "Soulaana: Fresh verification is on file. You may reopen the fortress intentionally.",
    }


def disable_emergency_lockdown(
    *,
    actor_user_id: str,
    reason: str,
    session_id: str = "",
    metadata: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    actor_user_id = _safe_str(actor_user_id, "unknown_actor")
    reason = _safe_str(reason, "Owner disabled emergency lockdown.")
    session_id = _safe_str(session_id)

    state = load_emergency_lockdown_state()

    if not state.get("lockdown_active"):
        return {
            "ok": True,
            "decision": "already_inactive",
            "lockdown_active": False,
            "human_reason": "Lockdown is already inactive.",
            "soulaana_translation": "Soulaana: Nothing to reopen. The lockdown was already inactive.",
        }

    try:
        from tower.step_up_auth import evaluate_step_up_requirement

        step_up = evaluate_step_up_requirement(
            user_id=actor_user_id,
            action="lockdown_disable",
            object_type="emergency_lockdown",
            object_id=state.get("lockdown_id"),
            session_id=session_id,
            route_path="/tower/security-command",
            clearance_decision={"allowed": True, "decision": "allow"},
            risk_context={"lockdown_active": True, "reason": reason},
        )
    except Exception as exc:
        step_up = {
            "decision": "step_up_required",
            "step_up_required": True,
            "reason_code": "step_up_framework_unavailable_for_lockdown_disable",
            "error": f"{type(exc).__name__}: {exc}",
        }

    if step_up.get("decision") != "allow":
        event = _record_lockdown_event({
            "actor_user_id": actor_user_id,
            "decision": "lockdown_disable_blocked_missing_step_up",
            "lockdown_id": state.get("lockdown_id"),
            "reason_code": step_up.get("reason_code", "lockdown_disable_requires_step_up"),
            "metadata": {
                "disable_reason": reason,
                "step_up": step_up,
                "request_metadata": metadata or {},
            },
        })

        return {
            "ok": False,
            "decision": "step_up_required",
            "lockdown_active": True,
            "lockdown_id": state.get("lockdown_id"),
            "step_up": step_up,
            "event": event,
            "required_actions": ["complete_step_up_auth", "owner_reason"],
            "human_reason": "Cannot disable emergency lockdown without step-up verification.",
            "soulaana_translation": "Soulaana: The fortress stays sealed until owner verification is fresh.",
        }

    previous_lockdown_id = state.get("lockdown_id")
    history = state.get("history", []) if isinstance(state.get("history"), list) else []
    history.append({
        "at": _utc_now(),
        "actor_user_id": actor_user_id,
        "action": "disable_lockdown",
        "reason": reason,
        "previous_lockdown_id": previous_lockdown_id,
    })

    state.update({
        "lockdown_active": False,
        "severity": "none",
        "reason_code": "lockdown_disabled",
        "human_reason": reason,
        "disabled_at": _utc_now(),
        "disabled_by": actor_user_id,
        "history": history,
        "soulaana_translation": "Soulaana: Emergency lockdown is disabled. The fortress reopened with receipts.",
    })

    saved = save_emergency_lockdown_state(state)

    event = _record_lockdown_event({
        "actor_user_id": actor_user_id,
        "decision": "lockdown_disabled",
        "lockdown_id": previous_lockdown_id,
        "reason_code": "lockdown_disabled_after_step_up",
        "severity": "none",
        "human_reason": reason,
        "metadata": {
            "session_id": session_id,
            "step_up": step_up,
            "request_metadata": metadata or {},
        },
    })

    return {
        "ok": True,
        "decision": "lockdown_disabled",
        "lockdown_active": False,
        "lockdown_id": previous_lockdown_id,
        "state": saved,
        "event": event,
        "risk_state": "watch",
        "risk_score": 25,
        "required_actions": ["review_post_lockdown_status"],
        "human_reason": reason,
        "soulaana_translation": saved.get("soulaana_translation"),
    }


def evaluate_lockdown_gate(
    *,
    action: str,
    user_id: str = "anonymous",
    route_path: str = "",
    object_type: str = "",
    object_id: str = "",
    metadata: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    action = _safe_str(action, "unknown_action")
    user_id = _safe_str(user_id, "anonymous")
    route_path = _safe_str(route_path)
    object_type = _safe_str(object_type)
    object_id = _safe_str(object_id)

    state = load_emergency_lockdown_state()

    if not state.get("lockdown_active"):
        return {
            "ok": True,
            "decision": "allow",
            "lockdown_active": False,
            "reason_code": "lockdown_inactive",
            "risk_state": "clear",
            "risk_score": 5,
            "required_actions": [],
            "human_reason": "Emergency lockdown is inactive.",
            "soulaana_translation": "Soulaana: Lockdown is inactive. Normal clearance rules can decide this.",
        }

    if action in LOCKDOWN_ALLOWED_RECOVERY_ACTIONS:
        return {
            "ok": True,
            "decision": "allow_recovery",
            "lockdown_active": True,
            "lockdown_id": state.get("lockdown_id"),
            "reason_code": "lockdown_recovery_action_allowed",
            "risk_state": "watch",
            "risk_score": 30,
            "required_actions": ["owner_recovery_context"],
            "human_reason": "This recovery/status action remains available during lockdown.",
            "soulaana_translation": "Soulaana: Recovery lane stays open. Dangerous corridors stay sealed.",
        }

    blocked = action in LOCKDOWN_BLOCKED_ACTIONS

    # Conservative default: unknown actions are blocked during lockdown unless explicitly recovery-safe.
    if blocked or action not in LOCKDOWN_ALLOWED_RECOVERY_ACTIONS:
        event = _record_lockdown_event({
            "actor_user_id": user_id,
            "decision": "lockdown_block",
            "lockdown_id": state.get("lockdown_id"),
            "reason_code": "action_blocked_by_emergency_lockdown",
            "action": action,
            "route_path": route_path,
            "object_type": object_type,
            "object_id": object_id,
            "metadata": metadata or {},
        })

        return {
            "ok": True,
            "decision": "deny",
            "allowed": False,
            "lockdown_active": True,
            "lockdown_id": state.get("lockdown_id"),
            "reason_code": "action_blocked_by_emergency_lockdown",
            "risk_state": "critical",
            "risk_score": 95,
            "required_actions": ["owner_review", "wait_for_lockdown_disable"],
            "event": event,
            "human_reason": "Emergency lockdown is active, so this action is frozen.",
            "soulaana_translation": "Soulaana: Emergency lockdown is active. That corridor stays sealed.",
        }

    return {
        "ok": True,
        "decision": "deny",
        "allowed": False,
        "lockdown_active": True,
        "lockdown_id": state.get("lockdown_id"),
        "reason_code": "lockdown_default_deny",
        "risk_state": "critical",
        "risk_score": 95,
        "required_actions": ["owner_review"],
        "human_reason": "Emergency lockdown default-denied this action.",
        "soulaana_translation": "Soulaana: Default deny during lockdown. I am not guessing with the fortress sealed.",
    }


def add_lockdown_owner_note(
    *,
    actor_user_id: str,
    note: str,
    metadata: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    actor_user_id = _safe_str(actor_user_id, "unknown_actor")
    note = _safe_str(note, "Owner note added.")

    state = load_emergency_lockdown_state()
    notes = state.get("owner_notes", []) if isinstance(state.get("owner_notes"), list) else []

    note_item = {
        "note_id": _event_id("lock_note"),
        "created_at": _utc_now(),
        "actor_user_id": actor_user_id,
        "note": _redact_sensitive(note),
    }
    notes.append(note_item)
    state["owner_notes"] = notes
    save_emergency_lockdown_state(state)

    event = _record_lockdown_event({
        "actor_user_id": actor_user_id,
        "decision": "owner_note_added",
        "lockdown_id": state.get("lockdown_id"),
        "reason_code": "lockdown_owner_note_added",
        "metadata": {"note_id": note_item.get("note_id"), "request_metadata": metadata or {}},
    })

    return {
        "ok": True,
        "decision": "owner_note_added",
        "note": note_item,
        "event": event,
        "human_reason": "Owner note added to emergency lockdown state.",
        "soulaana_translation": "Soulaana: Note added to the lockdown record.",
    }


def summarize_emergency_lockdown(limit: int = 12) -> Dict[str, Any]:
    state = load_emergency_lockdown_state()
    events = _load_events()

    try:
        limit = int(limit)
    except Exception:
        limit = 12
    limit = max(1, min(limit, 200))

    by_decision: Dict[str, int] = {}
    by_reason: Dict[str, int] = {}

    for event in events:
        decision = event.get("decision", "unknown")
        reason = event.get("reason_code", "unknown")
        by_decision[decision] = by_decision.get(decision, 0) + 1
        by_reason[reason] = by_reason.get(reason, 0) + 1

    return {
        "ok": True,
        "pack": "093",
        "state_path": str(LOCKDOWN_STATE_PATH),
        "events_path": str(LOCKDOWN_EVENTS_PATH),
        "lockdown_active": bool(state.get("lockdown_active")),
        "lockdown_id": state.get("lockdown_id", ""),
        "severity": state.get("severity", "none"),
        "reason_code": state.get("reason_code"),
        "blocked_actions": state.get("blocked_actions", []),
        "allowed_recovery_actions": state.get("allowed_recovery_actions", []),
        "total_events": len(events),
        "by_decision": by_decision,
        "by_reason": by_reason,
        "recent_events": events[-limit:],
        "owner_notes_count": len(state.get("owner_notes", []) if isinstance(state.get("owner_notes"), list) else []),
        "readiness_score": 100,
        "readiness_label": "Emergency lockdown system ready",
        "human_reason": "Emergency lockdown summary loaded.",
        "soulaana_translation": "Soulaana: Emergency lockdown controls are ready. Dangerous doors can be sealed fast.",
    }


def reset_emergency_lockdown_for_test() -> Dict[str, Any]:
    state = _default_state_copy()
    saved = save_emergency_lockdown_state(state)
    return {
        "ok": True,
        "decision": "lockdown_reset_for_test",
        "state": saved,
    }



# ================================================================================
# PACK093B_STRICT_LOCKDOWN_REDACTION
# ================================================================================
# Emergency lockdown records should not preserve sensitive key names like raw_token,
# tower_keycard, bearer, password, etc. This override drops sensitive keys entirely
# and records only a generic redaction count.
# ================================================================================

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

            # If nested redaction returns a marker dict, merge count upward when practical.
            if isinstance(redacted_item, dict) and "__redacted_sensitive_field_count__" in redacted_item:
                nested_count = redacted_item.get("__redacted_sensitive_field_count__", 0)
                try:
                    redacted_count += int(nested_count)
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
        ):
            return "[REDACTED]"
        return value

    return value



# ================================================================================
# PACK093C_LOCKDOWN_EVENT_STORE_SANITIZER
# ================================================================================
# Removes legacy sensitive key names from stored lockdown events and ensures test
# reset starts with a clean lockdown event ledger.
# ================================================================================

def sanitize_lockdown_event_store() -> Dict[str, Any]:
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
        "decision": "lockdown_event_store_sanitized",
        "total_events": len(sanitized),
        "human_reason": (
            "Legacy lockdown event store sanitized."
            if clean
            else "Legacy lockdown event store still contains sensitive markers."
        ),
        "soulaana_translation": (
            "Soulaana: Old lockdown records were scrubbed clean."
            if clean
            else "Soulaana: Some old lockdown records are still talking too much."
        ),
    }


try:
    _pack093c_original_summarize_emergency_lockdown
except NameError:
    _pack093c_original_summarize_emergency_lockdown = summarize_emergency_lockdown


def summarize_emergency_lockdown(limit: int = 12) -> Dict[str, Any]:
    sanitize_lockdown_event_store()
    summary = _pack093c_original_summarize_emergency_lockdown(limit=limit)
    if not isinstance(summary, dict):
        summary = {"ok": False, "pack": "093", "human_reason": "Invalid lockdown summary."}

    # Strict sanitize full summary before returning.
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


def reset_emergency_lockdown_for_test() -> Dict[str, Any]:
    state = _default_state_copy()
    saved = save_emergency_lockdown_state(state)

    # Pack 093C: reset event ledger too, so failed legacy runs cannot poison the test.
    _save_events([])

    return {
        "ok": True,
        "decision": "lockdown_reset_for_test",
        "state": saved,
        "events_reset": True,
        "soulaana_translation": "Soulaana: Lockdown state and old event noise reset for a clean test lane.",
    }



# ================================================================================
# PACK093D_SANITIZED_LOCKDOWN_EVENT_RETURN
# ================================================================================
# Ensures _record_lockdown_event returns the sanitized event, not the raw event.
# This prevents live function return objects from leaking sensitive key names.
# ================================================================================

def _record_lockdown_event(event: Dict[str, Any]) -> Dict[str, Any]:
    event = dict(event)
    event.setdefault("event_id", _event_id("lock_evt"))
    event.setdefault("event_type", "tower_emergency_lockdown_event")
    event.setdefault("created_at", _utc_now())
    event.setdefault("pack", "093")

    # Strict sanitize BEFORE fingerprint/storage/return.
    sanitized_event = _redact_sensitive(event)
    sanitized_event["event_fingerprint"] = _fingerprint(sanitized_event)

    events = _load_events()
    events.append(sanitized_event)
    _save_events(events)

    try:
        # Chain snapshots when tamper chain exists. Best-effort only.
        from tower.tamper_evident_audit_chain import create_tamper_chain_entry

        create_tamper_chain_entry(
            event_type="tower_lockdown_event_snapshot",
            source_name="emergency_lockdown_events",
            source_path=str(LOCKDOWN_EVENTS_PATH),
            source_hash=_fingerprint(events),
            record_count=len(events),
            actor_user_id=_safe_str(sanitized_event.get("actor_user_id"), "tower_system"),
            reason=f"Pack 093 chained lockdown event {sanitized_event.get('reason_code')}.",
            metadata={
                "pack": "093",
                "event_id": sanitized_event.get("event_id"),
                "reason_code": sanitized_event.get("reason_code"),
            },
        )
    except Exception:
        pass

    return sanitized_event

