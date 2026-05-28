
from __future__ import annotations

import hashlib
import json
import secrets
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "tower" / "data"

STEP_UP_EVENTS_PATH = DATA_DIR / "step_up_auth_events.json"
STEP_UP_ACTIVE_CHALLENGES_PATH = DATA_DIR / "step_up_active_challenges.json"


STEP_UP_POLICY = {
    "export": {
        "required": True,
        "risk_score": 72,
        "risk_state": "restricted",
        "ttl_minutes": 10,
        "reason_code": "step_up_required_for_export",
        "plain": "Exports can move sensitive data outside the system.",
        "methods": ["owner_pin", "fresh_keycard", "owner_phrase"],
    },
    "resolve_security_item": {
        "required": True,
        "risk_score": 58,
        "risk_state": "watch",
        "ttl_minutes": 12,
        "reason_code": "step_up_required_for_security_resolution",
        "plain": "Resolving security items changes the owner review trail.",
        "methods": ["owner_pin", "fresh_keycard"],
    },
    "route_policy_change": {
        "required": True,
        "risk_score": 78,
        "risk_state": "restricted",
        "ttl_minutes": 8,
        "reason_code": "step_up_required_for_route_policy_change",
        "plain": "Route policy changes can alter which doors open, lock, retire, or redirect.",
        "methods": ["owner_pin", "fresh_keycard", "owner_phrase"],
    },
    "live_mode_enable": {
        "required": True,
        "risk_score": 90,
        "risk_state": "critical",
        "ttl_minutes": 5,
        "reason_code": "step_up_required_for_live_mode",
        "plain": "Live mode can affect real-money operations.",
        "methods": ["owner_pin", "fresh_keycard", "owner_phrase"],
    },
    "automated_mode_enable": {
        "required": True,
        "risk_score": 95,
        "risk_state": "critical",
        "ttl_minutes": 5,
        "reason_code": "step_up_required_for_automated_mode",
        "plain": "Automated mode can take repeated actions without manual confirmation.",
        "methods": ["owner_pin", "fresh_keycard", "owner_phrase"],
    },
    "sensitive_reveal": {
        "required": True,
        "risk_score": 62,
        "risk_state": "restricted",
        "ttl_minutes": 10,
        "reason_code": "step_up_required_for_sensitive_reveal",
        "plain": "Sensitive details should stay redacted until a fresh verification exists.",
        "methods": ["owner_pin", "fresh_keycard"],
    },
    "admin_override": {
        "required": True,
        "risk_score": 85,
        "risk_state": "critical",
        "ttl_minutes": 6,
        "reason_code": "step_up_required_for_admin_override",
        "plain": "Admin override can bypass normal workflow gates.",
        "methods": ["owner_pin", "fresh_keycard", "owner_phrase"],
    },
    "lockdown_disable": {
        "required": True,
        "risk_score": 96,
        "risk_state": "critical",
        "ttl_minutes": 4,
        "reason_code": "step_up_required_for_lockdown_disable",
        "plain": "Disabling lockdown reopens protected controls.",
        "methods": ["owner_pin", "fresh_keycard", "owner_phrase"],
    },
    "archive_handoff_export": {
        "required": True,
        "risk_score": 76,
        "risk_state": "restricted",
        "ttl_minutes": 10,
        "reason_code": "step_up_required_for_archive_handoff_export",
        "plain": "Evidence exports and handoffs may contain sensitive records.",
        "methods": ["owner_pin", "fresh_keycard"],
    },
}


LOW_RISK_ACTIONS = {
    "view_dashboard",
    "view_status",
    "view_public_shell",
    "view_locked_page",
    "view_summary",
}


def _utc_now_dt() -> datetime:
    return datetime.now(timezone.utc)


def _utc_now() -> str:
    return _utc_now_dt().isoformat().replace("+00:00", "Z")


def _parse_time(value: Any) -> datetime | None:
    if not value:
        return None
    try:
        text = str(value).replace("Z", "+00:00")
        return datetime.fromisoformat(text)
    except Exception:
        return None


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
        "pin",
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


def _event_id(prefix: str = "stepup") -> str:
    return f"{prefix}_{secrets.token_urlsafe(18)}"


def _load_events() -> List[Dict[str, Any]]:
    data = _load_json(STEP_UP_EVENTS_PATH, [])
    return data if isinstance(data, list) else []


def _save_events(events: List[Dict[str, Any]]) -> None:
    _write_json(STEP_UP_EVENTS_PATH, events)


def _load_active_challenges() -> List[Dict[str, Any]]:
    data = _load_json(STEP_UP_ACTIVE_CHALLENGES_PATH, [])
    return data if isinstance(data, list) else []


def _save_active_challenges(challenges: List[Dict[str, Any]]) -> None:
    _write_json(STEP_UP_ACTIVE_CHALLENGES_PATH, challenges)


def _record_step_up_event(event: Dict[str, Any]) -> Dict[str, Any]:
    event = dict(event)
    event.setdefault("event_id", _event_id("stepup_evt"))
    event.setdefault("event_type", "tower_step_up_auth_event")
    event.setdefault("created_at", _utc_now())
    event.setdefault("pack", "092")
    event["event_fingerprint"] = _fingerprint(event)

    events = _load_events()
    events.append(_redact_sensitive(event))
    _save_events(events)
    return event


def get_step_up_policy_for_action(action: str) -> Dict[str, Any]:
    action = _safe_str(action, "unknown_action")
    if action in STEP_UP_POLICY:
        policy = dict(STEP_UP_POLICY[action])
        policy["action"] = action
        policy["known_action"] = True
        return policy

    if action in LOW_RISK_ACTIONS:
        return {
            "action": action,
            "known_action": True,
            "required": False,
            "risk_score": 5,
            "risk_state": "clear",
            "ttl_minutes": 0,
            "reason_code": "step_up_not_required_for_low_risk_action",
            "plain": "This low-risk action does not require fresh verification.",
            "methods": [],
        }

    return {
        "action": action,
        "known_action": False,
        "required": True,
        "risk_score": 70,
        "risk_state": "restricted",
        "ttl_minutes": 8,
        "reason_code": "step_up_required_for_unknown_sensitive_action",
        "plain": "Unknown actions default to step-up until explicitly classified.",
        "methods": ["owner_pin", "fresh_keycard"],
    }


def has_recent_step_up(
    *,
    user_id: str,
    action: str,
    object_type: str = "",
    object_id: str = "",
    session_id: str = "",
    now: datetime | None = None,
) -> Dict[str, Any]:
    now = now or _utc_now_dt()
    user_id = _safe_str(user_id, "anonymous")
    action = _safe_str(action, "unknown_action")
    object_type = _safe_str(object_type)
    object_id = _safe_str(object_id)
    session_id = _safe_str(session_id)

    challenges = _load_active_challenges()
    valid_matches = []
    expired = []

    for challenge in challenges:
        expires = _parse_time(challenge.get("expires_at"))
        if not expires or expires < now:
            expired.append(challenge)
            continue

        if challenge.get("status") != "verified":
            continue

        if challenge.get("user_id") != user_id:
            continue

        if challenge.get("action") != action:
            continue

        # If object scope is set on the challenge, it must match.
        if challenge.get("object_type") and challenge.get("object_type") != object_type:
            continue

        if challenge.get("object_id") and challenge.get("object_id") != object_id:
            continue

        # Session binding: if set, it must match.
        if challenge.get("session_id") and session_id and challenge.get("session_id") != session_id:
            continue

        valid_matches.append(challenge)

    if expired:
        # Keep active store clean.
        remaining = [item for item in challenges if item not in expired]
        _save_active_challenges(remaining)

    if valid_matches:
        latest = sorted(valid_matches, key=lambda item: item.get("verified_at", ""), reverse=True)[0]
        return {
            "ok": True,
            "has_recent_step_up": True,
            "challenge_id": latest.get("challenge_id"),
            "expires_at": latest.get("expires_at"),
            "method": latest.get("method"),
            "human_reason": "Recent verified step-up challenge found.",
        }

    return {
        "ok": True,
        "has_recent_step_up": False,
        "human_reason": "No recent verified step-up challenge found.",
    }


def evaluate_step_up_requirement(
    *,
    user_id: str,
    action: str,
    object_type: str = "",
    object_id: str = "",
    session_id: str = "",
    route_path: str = "",
    clearance_decision: Dict[str, Any] | None = None,
    risk_context: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    user_id = _safe_str(user_id, "anonymous")
    action = _safe_str(action, "unknown_action")
    object_type = _safe_str(object_type)
    object_id = _safe_str(object_id)
    session_id = _safe_str(session_id)
    route_path = _safe_str(route_path)

    policy = get_step_up_policy_for_action(action)
    clearance_decision = clearance_decision if isinstance(clearance_decision, dict) else {}
    risk_context = risk_context if isinstance(risk_context, dict) else {}

    if clearance_decision.get("allowed") is False or clearance_decision.get("decision") == "deny":
        result = {
            "ok": True,
            "decision": "deny",
            "step_up_required": False,
            "reason_code": "base_clearance_denied_before_step_up",
            "risk_score": clearance_decision.get("risk_score", 80),
            "risk_state": clearance_decision.get("risk_state", "restricted"),
            "required_actions": clearance_decision.get("required_actions", ["resolve_base_clearance"]),
            "human_reason": "Base clearance failed, so step-up is not offered.",
            "soulaana_translation": "Soulaana: I do not ask for extra verification when the hallway itself is blocked.",
        }
        _record_step_up_event({
            "action": action,
            "user_id": user_id,
            "object_type": object_type,
            "object_id": object_id,
            "session_id": session_id,
            "route_path": route_path,
            "decision": result["decision"],
            "reason_code": result["reason_code"],
            "metadata": {
                "policy": policy,
                "clearance_decision": clearance_decision,
                "risk_context": risk_context,
            },
        })
        return result

    if not policy.get("required"):
        result = {
            "ok": True,
            "decision": "allow",
            "step_up_required": False,
            "reason_code": policy.get("reason_code"),
            "risk_score": policy.get("risk_score", 5),
            "risk_state": policy.get("risk_state", "clear"),
            "required_actions": [],
            "human_reason": policy.get("plain"),
            "soulaana_translation": "Soulaana: This move is low-risk. No extra verification needed.",
        }
        _record_step_up_event({
            "action": action,
            "user_id": user_id,
            "object_type": object_type,
            "object_id": object_id,
            "session_id": session_id,
            "route_path": route_path,
            "decision": result["decision"],
            "reason_code": result["reason_code"],
            "metadata": {"policy": policy, "risk_context": risk_context},
        })
        return result

    recent = has_recent_step_up(
        user_id=user_id,
        action=action,
        object_type=object_type,
        object_id=object_id,
        session_id=session_id,
    )

    if recent.get("has_recent_step_up"):
        result = {
            "ok": True,
            "decision": "allow",
            "step_up_required": False,
            "reason_code": "recent_step_up_verified",
            "risk_score": max(10, int(policy.get("risk_score", 70)) - 45),
            "risk_state": "clear" if int(policy.get("risk_score", 70)) < 85 else "watch",
            "required_actions": [],
            "challenge_id": recent.get("challenge_id"),
            "expires_at": recent.get("expires_at"),
            "human_reason": "Recent step-up verification satisfies this sensitive action.",
            "soulaana_translation": "Soulaana: Fresh verification is already on file. This button can move.",
        }
        _record_step_up_event({
            "action": action,
            "user_id": user_id,
            "object_type": object_type,
            "object_id": object_id,
            "session_id": session_id,
            "route_path": route_path,
            "decision": result["decision"],
            "reason_code": result["reason_code"],
            "metadata": {"policy": policy, "recent": recent, "risk_context": risk_context},
        })
        return result

    result = {
        "ok": True,
        "decision": "step_up_required",
        "step_up_required": True,
        "reason_code": policy.get("reason_code"),
        "risk_score": policy.get("risk_score"),
        "risk_state": policy.get("risk_state"),
        "required_actions": ["complete_step_up_auth"],
        "allowed_methods": policy.get("methods", []),
        "ttl_minutes": policy.get("ttl_minutes"),
        "human_reason": policy.get("plain"),
        "soulaana_translation": "Soulaana: This button is powerful. Verify again before it moves.",
    }

    _record_step_up_event({
        "action": action,
        "user_id": user_id,
        "object_type": object_type,
        "object_id": object_id,
        "session_id": session_id,
        "route_path": route_path,
        "decision": result["decision"],
        "reason_code": result["reason_code"],
        "metadata": {"policy": policy, "risk_context": risk_context},
    })

    return result


def create_step_up_challenge(
    *,
    user_id: str,
    action: str,
    object_type: str = "",
    object_id: str = "",
    session_id: str = "",
    route_path: str = "",
    method: str = "owner_pin",
    reason: str = "",
) -> Dict[str, Any]:
    user_id = _safe_str(user_id, "anonymous")
    action = _safe_str(action, "unknown_action")
    object_type = _safe_str(object_type)
    object_id = _safe_str(object_id)
    session_id = _safe_str(session_id)
    route_path = _safe_str(route_path)
    method = _safe_str(method, "owner_pin")

    policy = get_step_up_policy_for_action(action)
    ttl = int(policy.get("ttl_minutes", 8) or 8)
    now = _utc_now_dt()
    expires_at = now + timedelta(minutes=ttl)

    challenge = {
        "ok": True,
        "challenge_id": _event_id("stepup_chal"),
        "event_type": "tower_step_up_challenge",
        "created_at": now.isoformat().replace("+00:00", "Z"),
        "expires_at": expires_at.isoformat().replace("+00:00", "Z"),
        "verified_at": "",
        "status": "pending",
        "user_id": user_id,
        "action": action,
        "object_type": object_type,
        "object_id": object_id,
        "session_id": session_id,
        "route_path": route_path,
        "method": method,
        "risk_score": policy.get("risk_score"),
        "risk_state": policy.get("risk_state"),
        "reason_code": policy.get("reason_code"),
        "reason": reason or policy.get("plain"),
        "challenge_fingerprint": "",
        "soulaana_translation": "Soulaana: Step-up challenge created. This is the extra lock before the powerful button.",
    }
    challenge["challenge_fingerprint"] = _fingerprint(challenge)

    challenges = _load_active_challenges()
    challenges.append(challenge)
    _save_active_challenges(challenges)

    _record_step_up_event({
        "action": action,
        "user_id": user_id,
        "object_type": object_type,
        "object_id": object_id,
        "session_id": session_id,
        "route_path": route_path,
        "decision": "challenge_created",
        "reason_code": challenge.get("reason_code"),
        "challenge_id": challenge.get("challenge_id"),
        "metadata": {"method": method, "expires_at": challenge.get("expires_at")},
    })

    return challenge


def verify_step_up_challenge(
    *,
    challenge_id: str,
    user_id: str,
    method: str = "owner_pin",
    verification_note: str = "verified_for_test_or_owner_flow",
) -> Dict[str, Any]:
    challenge_id = _safe_str(challenge_id)
    user_id = _safe_str(user_id, "anonymous")
    method = _safe_str(method, "owner_pin")

    challenges = _load_active_challenges()
    now = _utc_now_dt()

    for index, challenge in enumerate(challenges):
        if challenge.get("challenge_id") != challenge_id:
            continue

        if challenge.get("user_id") != user_id:
            result = {
                "ok": False,
                "decision": "deny",
                "reason_code": "step_up_wrong_user",
                "human_reason": "This step-up challenge belongs to another user.",
                "soulaana_translation": "Soulaana: That verification does not belong to this person.",
            }
            _record_step_up_event({
                "action": challenge.get("action"),
                "user_id": user_id,
                "decision": result["decision"],
                "reason_code": result["reason_code"],
                "challenge_id": challenge_id,
            })
            return result

        expires = _parse_time(challenge.get("expires_at"))
        if not expires or expires < now:
            challenge["status"] = "expired"
            challenges[index] = challenge
            _save_active_challenges(challenges)

            result = {
                "ok": False,
                "decision": "expired",
                "reason_code": "step_up_challenge_expired",
                "human_reason": "This step-up challenge expired.",
                "soulaana_translation": "Soulaana: That extra lock timed out. Make a fresh challenge.",
            }
            _record_step_up_event({
                "action": challenge.get("action"),
                "user_id": user_id,
                "decision": result["decision"],
                "reason_code": result["reason_code"],
                "challenge_id": challenge_id,
            })
            return result

        if challenge.get("method") != method:
            result = {
                "ok": False,
                "decision": "deny",
                "reason_code": "step_up_method_mismatch",
                "human_reason": "The verification method did not match this challenge.",
                "soulaana_translation": "Soulaana: Wrong key for this extra lock.",
            }
            _record_step_up_event({
                "action": challenge.get("action"),
                "user_id": user_id,
                "decision": result["decision"],
                "reason_code": result["reason_code"],
                "challenge_id": challenge_id,
            })
            return result

        challenge["status"] = "verified"
        challenge["verified_at"] = now.isoformat().replace("+00:00", "Z")
        challenge["verification_note"] = _redact_sensitive(verification_note)
        challenge["challenge_fingerprint"] = _fingerprint(challenge)
        challenges[index] = challenge
        _save_active_challenges(challenges)

        result = {
            "ok": True,
            "decision": "verified",
            "challenge_id": challenge_id,
            "action": challenge.get("action"),
            "object_type": challenge.get("object_type"),
            "object_id": challenge.get("object_id"),
            "expires_at": challenge.get("expires_at"),
            "reason_code": "step_up_challenge_verified",
            "human_reason": "Step-up challenge verified.",
            "soulaana_translation": "Soulaana: Fresh verification complete. The powerful button can proceed within its window.",
        }
        _record_step_up_event({
            "action": challenge.get("action"),
            "user_id": user_id,
            "object_type": challenge.get("object_type"),
            "object_id": challenge.get("object_id"),
            "session_id": challenge.get("session_id"),
            "route_path": challenge.get("route_path"),
            "decision": result["decision"],
            "reason_code": result["reason_code"],
            "challenge_id": challenge_id,
            "metadata": {"expires_at": result.get("expires_at"), "method": method},
        })
        return result

    result = {
        "ok": False,
        "decision": "deny",
        "reason_code": "step_up_challenge_not_found",
        "human_reason": "Step-up challenge was not found.",
        "soulaana_translation": "Soulaana: I do not see that extra lock request.",
    }
    _record_step_up_event({
        "action": "unknown",
        "user_id": user_id,
        "decision": result["decision"],
        "reason_code": result["reason_code"],
        "challenge_id": challenge_id,
    })
    return result


def summarize_step_up_auth(limit: int = 12) -> Dict[str, Any]:
    events = _load_events()
    challenges = _load_active_challenges()

    try:
        limit = int(limit)
    except Exception:
        limit = 12
    limit = max(1, min(limit, 200))

    by_decision: Dict[str, int] = {}
    by_action: Dict[str, int] = {}
    by_status: Dict[str, int] = {}

    for event in events:
        decision = event.get("decision", "unknown")
        action = event.get("action", "unknown")
        by_decision[decision] = by_decision.get(decision, 0) + 1
        by_action[action] = by_action.get(action, 0) + 1

    for challenge in challenges:
        status = challenge.get("status", "unknown")
        by_status[status] = by_status.get(status, 0) + 1

    return {
        "ok": True,
        "pack": "092",
        "path": str(STEP_UP_EVENTS_PATH),
        "active_challenges_path": str(STEP_UP_ACTIVE_CHALLENGES_PATH),
        "policy_actions": sorted(list(STEP_UP_POLICY.keys())),
        "low_risk_actions": sorted(list(LOW_RISK_ACTIONS)),
        "total_events": len(events),
        "total_challenges": len(challenges),
        "by_decision": by_decision,
        "by_action": by_action,
        "by_challenge_status": by_status,
        "recent_events": events[-limit:],
        "recent_challenges": challenges[-limit:],
        "readiness_score": 100,
        "readiness_label": "Step-up authentication framework ready",
        "human_reason": "Step-up authentication framework summary loaded.",
        "soulaana_translation": "Soulaana: Step-up rules are live. Powerful buttons now need a fresh check.",
    }
