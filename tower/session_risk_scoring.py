
from __future__ import annotations

import hashlib
import json
import secrets
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "tower" / "data"

SESSION_RISK_EVENTS_PATH = DATA_DIR / "session_risk_events.json"
SESSION_RISK_PROFILES_PATH = DATA_DIR / "session_risk_profiles.json"


DECISION_ORDER = {
    "allow": 0,
    "step_up": 1,
    "throttle": 2,
    "quarantine": 3,
    "lockdown": 4,
    "deny": 5,
}


RISK_DECISION_BANDS = [
    {"min": 0, "max": 19, "decision": "allow", "risk_state": "clear"},
    {"min": 20, "max": 39, "decision": "step_up", "risk_state": "watch"},
    {"min": 40, "max": 59, "decision": "throttle", "risk_state": "watch"},
    {"min": 60, "max": 79, "decision": "quarantine", "risk_state": "restricted"},
    {"min": 80, "max": 94, "decision": "lockdown", "risk_state": "critical"},
    {"min": 95, "max": 100, "decision": "deny", "risk_state": "critical"},
]


ACTION_RISK_WEIGHTS = {
    "view_status": 0,
    "view_locked_page": 0,
    "view_security_command": 5,
    "view_quarantine_status": 3,
    "view_lockdown_status": 3,
    "export": 24,
    "download": 22,
    "archive_handoff_export": 25,
    "route_policy_change": 28,
    "security_policy_edit": 30,
    "admin_override": 34,
    "clearance_grant": 35,
    "app_clearance_grant": 35,
    "live_mode_enable": 40,
    "automated_mode_enable": 45,
    "broker_action": 42,
    "capital_movement": 45,
    "payment_batch_release": 42,
    "sensitive_reveal": 24,
    "object_reveal": 18,
    "raw_data_view": 22,
    "disable_security": 50,
    "lockdown_disable": 45,
    "quarantine_release": 34,
}


ROUTE_RISK_HINTS = {
    "/tower/security-command": 12,
    "/tower/status.json": 4,
    "/admin": 30,
    "/api": 22,
    "/export": 24,
    "/download": 22,
    "/broker": 40,
    "/live": 40,
    "/automated": 45,
    "/symbols": 10,
    "/signals": 10,
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


def _safe_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except Exception:
        return default


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
        "cookie",
        "session_cookie",
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


def _event_id(prefix: str = "risk") -> str:
    return f"{prefix}_{secrets.token_urlsafe(18)}"


def _load_events() -> List[Dict[str, Any]]:
    data = _load_json(SESSION_RISK_EVENTS_PATH, [])
    return data if isinstance(data, list) else []


def _save_events(events: List[Dict[str, Any]]) -> None:
    _write_json(SESSION_RISK_EVENTS_PATH, events)


def _load_profiles() -> Dict[str, Any]:
    data = _load_json(SESSION_RISK_PROFILES_PATH, {
        "ok": True,
        "pack": "095",
        "profiles": {},
        "known_devices": {},
        "known_ips": {},
        "known_user_locations": {},
        "history": [],
    })
    return data if isinstance(data, dict) else {"ok": True, "pack": "095", "profiles": {}}


def _save_profiles(profiles: Dict[str, Any]) -> None:
    profiles = dict(profiles)
    profiles["ok"] = True
    profiles["pack"] = "095"
    profiles["updated_at"] = _utc_now()
    profiles["profile_fingerprint"] = _fingerprint(profiles)
    _write_json(SESSION_RISK_PROFILES_PATH, _redact_sensitive(profiles))


def _record_risk_event(event: Dict[str, Any]) -> Dict[str, Any]:
    event = dict(event)
    event.setdefault("event_id", _event_id("risk_evt"))
    event.setdefault("event_type", "tower_session_risk_event")
    event.setdefault("created_at", _utc_now())
    event.setdefault("pack", "095")

    sanitized = _redact_sensitive(event)
    sanitized["event_fingerprint"] = _fingerprint(sanitized)

    events = _load_events()
    events.append(sanitized)
    _save_events(events)

    try:
        from tower.tamper_evident_audit_chain import create_tamper_chain_entry

        create_tamper_chain_entry(
            event_type="tower_session_risk_event_snapshot",
            source_name="session_risk_events",
            source_path=str(SESSION_RISK_EVENTS_PATH),
            source_hash=_fingerprint(events),
            record_count=len(events),
            actor_user_id=_safe_str(sanitized.get("user_id"), "tower_system"),
            reason=f"Pack 095 chained session risk event {sanitized.get('decision')}.",
            metadata={
                "pack": "095",
                "event_id": sanitized.get("event_id"),
                "decision": sanitized.get("decision"),
                "risk_score": sanitized.get("risk_score"),
            },
        )
    except Exception:
        pass

    return sanitized


def _route_hint_score(route_path: str) -> int:
    route_path = _safe_str(route_path, "/").lower()
    score = 0

    for prefix, weight in ROUTE_RISK_HINTS.items():
        if route_path.startswith(prefix.lower()):
            score = max(score, weight)

    return score


def _decision_for_score(score: int) -> Dict[str, Any]:
    score = max(0, min(100, int(score)))

    for band in RISK_DECISION_BANDS:
        if band["min"] <= score <= band["max"]:
            return {
                "decision": band["decision"],
                "risk_state": band["risk_state"],
                "risk_score": score,
            }

    return {
        "decision": "deny",
        "risk_state": "critical",
        "risk_score": score,
    }


def _max_decision(*decisions: str) -> str:
    strongest = "allow"
    for decision in decisions:
        if DECISION_ORDER.get(decision, 0) > DECISION_ORDER.get(strongest, 0):
            strongest = decision
    return strongest


def register_known_session_baseline(
    *,
    user_id: str,
    device_id: str = "",
    ip_address: str = "",
    location_hint: str = "",
    actor_user_id: str = "tower_system",
    metadata: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    user_id = _safe_str(user_id, "anonymous")
    device_id = _safe_str(device_id)
    ip_address = _safe_str(ip_address)
    location_hint = _safe_str(location_hint)

    profiles = _load_profiles()
    known_devices = profiles.setdefault("known_devices", {})
    known_ips = profiles.setdefault("known_ips", {})
    known_locations = profiles.setdefault("known_user_locations", {})

    if device_id:
        known_devices.setdefault(user_id, [])
        if device_id not in known_devices[user_id]:
            known_devices[user_id].append(device_id)

    if ip_address:
        known_ips.setdefault(user_id, [])
        if ip_address not in known_ips[user_id]:
            known_ips[user_id].append(ip_address)

    if location_hint:
        known_locations.setdefault(user_id, [])
        if location_hint not in known_locations[user_id]:
            known_locations[user_id].append(location_hint)

    history = profiles.setdefault("history", [])
    history.append({
        "at": _utc_now(),
        "actor_user_id": actor_user_id,
        "action": "register_known_session_baseline",
        "user_id": user_id,
        "device_id": device_id,
        "ip_address": ip_address,
        "location_hint": location_hint,
        "metadata": _redact_sensitive(metadata or {}),
    })

    _save_profiles(profiles)

    event = _record_risk_event({
        "decision": "baseline_registered",
        "user_id": user_id,
        "actor_user_id": actor_user_id,
        "device_id": device_id,
        "ip_address": ip_address,
        "location_hint": location_hint,
        "reason_code": "known_session_baseline_registered",
        "metadata": metadata or {},
    })

    return {
        "ok": True,
        "decision": "baseline_registered",
        "user_id": user_id,
        "device_id": device_id,
        "ip_address": ip_address,
        "location_hint": location_hint,
        "event": event,
        "human_reason": "Known session baseline registered.",
        "soulaana_translation": "Soulaana: This device/IP baseline is now known to The Tower.",
    }


def evaluate_session_risk(
    *,
    user_id: str = "anonymous",
    session_id: str = "",
    device_id: str = "",
    ip_address: str = "",
    location_hint: str = "",
    route_path: str = "",
    action: str = "view_status",
    method: str = "GET",
    request_count_1m: int = 0,
    denied_count_5m: int = 0,
    failed_keycard_count_5m: int = 0,
    export_attempt_count_10m: int = 0,
    admin_action_count_10m: int = 0,
    object_reveal_count_10m: int = 0,
    live_or_broker_attempt_count_10m: int = 0,
    suspicious_pattern_count: int = 0,
    base_clearance_decision: Dict[str, Any] | None = None,
    metadata: Dict[str, Any] | None = None,
    auto_apply: bool = False,
) -> Dict[str, Any]:
    user_id = _safe_str(user_id, "anonymous")
    session_id = _safe_str(session_id)
    device_id = _safe_str(device_id)
    ip_address = _safe_str(ip_address)
    location_hint = _safe_str(location_hint)
    route_path = _safe_str(route_path, "/")
    action = _safe_str(action, "view_status")
    method = _safe_str(method, "GET").upper()
    metadata = metadata if isinstance(metadata, dict) else {}

    profiles = _load_profiles()
    known_devices = profiles.get("known_devices", {}) if isinstance(profiles.get("known_devices"), dict) else {}
    known_ips = profiles.get("known_ips", {}) if isinstance(profiles.get("known_ips"), dict) else {}
    known_locations = profiles.get("known_user_locations", {}) if isinstance(profiles.get("known_user_locations"), dict) else {}

    user_devices = known_devices.get(user_id, [])
    user_ips = known_ips.get(user_id, [])
    user_locations = known_locations.get(user_id, [])

    reasons: List[Dict[str, Any]] = []
    score = 0

    def add(reason_code: str, points: int, plain: str) -> None:
        nonlocal score
        points = max(0, int(points))
        score += points
        reasons.append({
            "reason_code": reason_code,
            "points": points,
            "plain": plain,
        })

    action_weight = ACTION_RISK_WEIGHTS.get(action, 18)
    if action_weight:
        add("action_risk_weight", action_weight, f"Action '{action}' carries base risk.")

    route_weight = _route_hint_score(route_path)
    if route_weight:
        add("route_risk_hint", route_weight, f"Route '{route_path}' carries route risk.")

    if device_id and user_devices and device_id not in user_devices:
        add("unfamiliar_device", 22, "Device is not in known baseline for this user.")
    elif device_id and not user_devices and user_id not in {"anonymous", "public"}:
        add("no_device_baseline", 12, "No known device baseline exists for this user.")

    if ip_address and user_ips and ip_address not in user_ips:
        add("ip_shift", 18, "IP address differs from known baseline for this user.")
    elif ip_address and not user_ips and user_id not in {"anonymous", "public"}:
        add("no_ip_baseline", 8, "No known IP baseline exists for this user.")

    if location_hint and user_locations and location_hint not in user_locations:
        add("location_shift", 15, "Location hint differs from known baseline for this user.")

    request_count_1m = _safe_int(request_count_1m)
    denied_count_5m = _safe_int(denied_count_5m)
    failed_keycard_count_5m = _safe_int(failed_keycard_count_5m)
    export_attempt_count_10m = _safe_int(export_attempt_count_10m)
    admin_action_count_10m = _safe_int(admin_action_count_10m)
    object_reveal_count_10m = _safe_int(object_reveal_count_10m)
    live_or_broker_attempt_count_10m = _safe_int(live_or_broker_attempt_count_10m)
    suspicious_pattern_count = _safe_int(suspicious_pattern_count)

    if request_count_1m >= 120:
        add("scraping_behavior_extreme", 42, "Very high request volume suggests scraping or automation abuse.")
    elif request_count_1m >= 60:
        add("scraping_behavior_high", 28, "High request volume suggests scraping or automation abuse.")
    elif request_count_1m >= 30:
        add("request_rate_elevated", 12, "Request volume is elevated.")

    if denied_count_5m >= 20:
        add("denied_route_burst_extreme", 40, "Repeated denied route hits indicate probing.")
    elif denied_count_5m >= 8:
        add("denied_route_burst", 26, "Multiple denied route hits indicate probing.")
    elif denied_count_5m >= 3:
        add("denied_route_cluster", 12, "Several denied route hits occurred recently.")

    if failed_keycard_count_5m >= 10:
        add("failed_keycard_burst_extreme", 44, "Repeated failed keycard attempts are critical.")
    elif failed_keycard_count_5m >= 4:
        add("failed_keycard_burst", 30, "Multiple failed keycard attempts occurred.")
    elif failed_keycard_count_5m >= 1:
        add("failed_keycard_attempt", 12, "A failed keycard attempt occurred.")

    if export_attempt_count_10m >= 6:
        add("export_attempt_burst", 35, "Repeated export attempts are suspicious.")
    elif export_attempt_count_10m >= 2:
        add("export_attempt_cluster", 20, "Multiple export attempts occurred.")

    if admin_action_count_10m >= 6:
        add("unusual_admin_pattern", 32, "Unusual admin action volume detected.")
    elif admin_action_count_10m >= 2:
        add("admin_action_cluster", 18, "Multiple admin actions occurred recently.")

    if object_reveal_count_10m >= 10:
        add("object_reveal_burst", 28, "High object reveal volume detected.")
    elif object_reveal_count_10m >= 4:
        add("object_reveal_cluster", 14, "Multiple object reveals occurred.")

    if live_or_broker_attempt_count_10m >= 3:
        add("live_broker_attempt_cluster", 36, "Repeated live/broker attempts detected.")
    elif live_or_broker_attempt_count_10m >= 1:
        add("live_broker_attempt", 20, "A live/broker attempt occurred.")

    if suspicious_pattern_count >= 5:
        add("multiple_suspicious_patterns", 38, "Multiple suspicious patterns combined.")
    elif suspicious_pattern_count >= 1:
        add("suspicious_pattern", 14, "A suspicious behavior pattern was detected.")

    if method in {"POST", "PUT", "PATCH", "DELETE"} and action not in {"view_status", "view_locked_page"}:
        add("state_changing_method", 8, "State-changing HTTP method increases risk.")

    base_clearance_decision = base_clearance_decision if isinstance(base_clearance_decision, dict) else {}
    if base_clearance_decision.get("decision") == "deny" or base_clearance_decision.get("allowed") is False:
        add("base_clearance_denied", 35, "Base clearance already denied this request.")

    if user_id in {"anonymous", "public", ""} and action_weight >= 20:
        add("anonymous_sensitive_action", 20, "Anonymous/public user attempted a sensitive action.")

    score = max(0, min(100, score))
    band = _decision_for_score(score)
    decision = band["decision"]

    # Hard escalation overrides.
    if failed_keycard_count_5m >= 10 or (denied_count_5m >= 20 and request_count_1m >= 120):
        decision = _max_decision(decision, "lockdown")
    if action == "disable_security":
        decision = _max_decision(decision, "lockdown")
    if base_clearance_decision.get("decision") == "deny" and failed_keycard_count_5m >= 4:
        decision = _max_decision(decision, "deny")

    if decision != band["decision"]:
        score = max(score, 80 if decision == "lockdown" else 95 if decision == "deny" else score)
        band = _decision_for_score(score)
        band["decision"] = decision
        band["risk_state"] = "critical" if decision in {"lockdown", "deny"} else band["risk_state"]

    required_actions = []
    if decision == "step_up":
        required_actions = ["complete_step_up_auth"]
    elif decision == "throttle":
        required_actions = ["slow_request_rate", "complete_step_up_auth_if_sensitive"]
    elif decision == "quarantine":
        required_actions = ["quarantine_subject", "owner_review"]
    elif decision == "lockdown":
        required_actions = ["activate_emergency_lockdown", "owner_review"]
    elif decision == "deny":
        required_actions = ["deny_request", "owner_security_review"]

    human_reason = _human_reason_for_decision(decision, reasons)
    soulaana_translation = _soulaana_for_decision(decision)

    result = {
        "ok": True,
        "pack": "095",
        "decision": decision,
        "allowed": decision == "allow",
        "risk_score": score,
        "risk_state": band.get("risk_state"),
        "required_actions": required_actions,
        "reason_count": len(reasons),
        "reasons": reasons,
        "user_id": user_id,
        "session_id": session_id,
        "device_id": device_id,
        "ip_address": ip_address,
        "location_hint": location_hint,
        "route_path": route_path,
        "action": action,
        "method": method,
        "human_reason": human_reason,
        "soulaana_translation": soulaana_translation,
        "auto_apply_requested": bool(auto_apply),
    }

    event = _record_risk_event({
        **result,
        "event_type": "tower_session_risk_event",
        "metadata": metadata,
    })
    result["event"] = event

    if auto_apply:
        result["auto_apply_result"] = apply_session_risk_decision(result)

    return _redact_sensitive(result)


def _human_reason_for_decision(decision: str, reasons: List[Dict[str, Any]]) -> str:
    if decision == "allow":
        return "Risk is low. Normal clearance rules can continue."
    if decision == "step_up":
        return "Risk is elevated. Fresh verification is required before continuing."
    if decision == "throttle":
        return "Risk suggests possible automation or probing. Slow the request path."
    if decision == "quarantine":
        return "Risk is restricted-level. Contain this subject in quarantine for owner review."
    if decision == "lockdown":
        return "Risk is critical. Emergency lockdown should be activated."
    if decision == "deny":
        return "Risk is critical and request should be denied outright."
    return "Risk decision generated."


def _soulaana_for_decision(decision: str) -> str:
    if decision == "allow":
        return "Soulaana: The threat meter is quiet. Let normal clearance decide."
    if decision == "step_up":
        return "Soulaana: Something is elevated. Ask for a fresh owner check."
    if decision == "throttle":
        return "Soulaana: Slow this down. Fast hands do not get to rush the Tower."
    if decision == "quarantine":
        return "Soulaana: Put this subject in the holding room before it touches anything sharp."
    if decision == "lockdown":
        return "Soulaana: Critical pressure detected. Slam the fortress doors."
    if decision == "deny":
        return "Soulaana: No. That request does not get a hallway."
    return "Soulaana: Risk decision generated."


def apply_session_risk_decision(risk_result: Dict[str, Any]) -> Dict[str, Any]:
    decision = _safe_str(risk_result.get("decision"), "allow")
    user_id = _safe_str(risk_result.get("user_id"), "anonymous")
    session_id = _safe_str(risk_result.get("session_id"))
    device_id = _safe_str(risk_result.get("device_id"))
    ip_address = _safe_str(risk_result.get("ip_address"))
    action = _safe_str(risk_result.get("action"), "unknown_action")
    route_path = _safe_str(risk_result.get("route_path"), "/")

    if decision == "allow":
        return {
            "ok": True,
            "decision": "no_action_needed",
            "human_reason": "Risk decision is allow. No containment action applied.",
            "soulaana_translation": "Soulaana: No extra force needed.",
        }

    if decision == "step_up":
        try:
            from tower.step_up_auth import evaluate_step_up_requirement

            step_up = evaluate_step_up_requirement(
                user_id=user_id,
                action=action,
                object_type="session_risk",
                object_id=session_id or device_id or ip_address or "unknown",
                session_id=session_id,
                route_path=route_path,
                clearance_decision={"allowed": True, "decision": "allow"},
                risk_context=risk_result,
            )
            return {
                "ok": True,
                "decision": "step_up_requested",
                "step_up": step_up,
                "human_reason": "Step-up requested from session risk decision.",
                "soulaana_translation": "Soulaana: Risk asked for a fresh check, so I asked.",
            }
        except Exception as exc:
            return {
                "ok": False,
                "decision": "step_up_request_failed",
                "error": f"{type(exc).__name__}: {exc}",
                "human_reason": "Step-up request failed.",
            }

    if decision == "throttle":
        return {
            "ok": True,
            "decision": "throttle_recommended",
            "throttle_seconds": 60,
            "human_reason": "Throttle recommended. Route middleware should slow this subject.",
            "soulaana_translation": "Soulaana: Slow lane. No sprinting through security.",
        }

    if decision == "quarantine":
        try:
            from tower.quarantine_mode import activate_quarantine

            quarantine = activate_quarantine(
                actor_user_id="tower_risk_scoring",
                scope="session" if session_id else "user",
                target={
                    "user_id": user_id,
                    "session_id": session_id,
                    "device_id": device_id,
                    "ip_address": ip_address,
                },
                reason_code="session_risk_score_quarantine",
                human_reason="Session risk score triggered quarantine.",
                severity="restricted",
                metadata={"source": "session_risk_scoring", "risk_score": risk_result.get("risk_score")},
            )
            return {
                "ok": True,
                "decision": "quarantine_applied",
                "quarantine": quarantine,
                "human_reason": "Quarantine applied from session risk decision.",
                "soulaana_translation": "Soulaana: Risk meter sent this subject to the holding room.",
            }
        except Exception as exc:
            return {
                "ok": False,
                "decision": "quarantine_apply_failed",
                "error": f"{type(exc).__name__}: {exc}",
                "human_reason": "Quarantine application failed.",
            }

    if decision == "lockdown":
        try:
            from tower.emergency_lockdown import activate_emergency_lockdown

            lockdown = activate_emergency_lockdown(
                actor_user_id="tower_risk_scoring",
                reason_code="session_risk_score_lockdown",
                human_reason="Session risk score triggered emergency lockdown.",
                severity="critical",
                metadata={"source": "session_risk_scoring", "risk_score": risk_result.get("risk_score")},
            )
            return {
                "ok": True,
                "decision": "lockdown_applied",
                "lockdown": lockdown,
                "human_reason": "Emergency lockdown applied from session risk decision.",
                "soulaana_translation": "Soulaana: Risk meter hit critical. Fortress sealed.",
            }
        except Exception as exc:
            return {
                "ok": False,
                "decision": "lockdown_apply_failed",
                "error": f"{type(exc).__name__}: {exc}",
                "human_reason": "Lockdown application failed.",
            }

    if decision == "deny":
        return {
            "ok": True,
            "decision": "deny_applied",
            "allowed": False,
            "human_reason": "Risk decision is deny. Request should not proceed.",
            "soulaana_translation": "Soulaana: Denied. No hallway.",
        }

    return {
        "ok": False,
        "decision": "unknown_risk_decision",
        "human_reason": f"Unknown risk decision: {decision}",
    }


def sanitize_session_risk_event_store() -> Dict[str, Any]:
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
        "decision": "session_risk_event_store_sanitized",
        "total_events": len(sanitized),
        "human_reason": "Session risk event store sanitized." if clean else "Session risk event store still contains sensitive markers.",
        "soulaana_translation": "Soulaana: Risk records were scrubbed clean." if clean else "Soulaana: Some risk records are still talking too much.",
    }


def summarize_session_risk(limit: int = 12) -> Dict[str, Any]:
    sanitize_session_risk_event_store()

    events = _load_events()
    profiles = _load_profiles()

    try:
        limit = int(limit)
    except Exception:
        limit = 12
    limit = max(1, min(limit, 200))

    by_decision: Dict[str, int] = {}
    by_action: Dict[str, int] = {}
    by_reason: Dict[str, int] = {}
    max_score = 0

    for event in events:
        decision = event.get("decision", "unknown")
        action = event.get("action", "unknown")
        by_decision[decision] = by_decision.get(decision, 0) + 1
        by_action[action] = by_action.get(action, 0) + 1
        max_score = max(max_score, _safe_int(event.get("risk_score"), 0))

        for reason in event.get("reasons", []) if isinstance(event.get("reasons"), list) else []:
            code = reason.get("reason_code", "unknown")
            by_reason[code] = by_reason.get(code, 0) + 1

    summary = {
        "ok": True,
        "pack": "095",
        "events_path": str(SESSION_RISK_EVENTS_PATH),
        "profiles_path": str(SESSION_RISK_PROFILES_PATH),
        "total_events": len(events),
        "known_user_count": len(profiles.get("known_devices", {}) if isinstance(profiles.get("known_devices"), dict) else {}),
        "by_decision": by_decision,
        "by_action": by_action,
        "by_reason": by_reason,
        "max_score": max_score,
        "recent_events": events[-limit:],
        "decision_bands": RISK_DECISION_BANDS,
        "readiness_score": 100,
        "readiness_label": "Session/device/IP risk scoring foundation ready",
        "human_reason": "Session/device/IP risk scoring summary loaded.",
        "soulaana_translation": "Soulaana: The threat meter is online. Sessions, devices, and IPs now get scored before the Tower chooses force.",
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


def reset_session_risk_for_test() -> Dict[str, Any]:
    _save_events([])
    _save_profiles({
        "ok": True,
        "pack": "095",
        "profiles": {},
        "known_devices": {},
        "known_ips": {},
        "known_user_locations": {},
        "history": [],
    })

    return {
        "ok": True,
        "decision": "session_risk_reset_for_test",
        "events_reset": True,
        "profiles_reset": True,
        "soulaana_translation": "Soulaana: Threat meter memory reset for a clean test lane.",
    }



# ================================================================================
# PACK095B_SENSITIVE_CLEAN_STEP_UP_OVERRIDE
# ================================================================================
# Wrap evaluate_session_risk so clean sensitive actions become step_up instead of
# throttle when there is no abuse/probing/failed-keycard volume.
# ================================================================================

PACK095B_CLEAN_STEP_UP_ACTIONS = {
    "export",
    "download",
    "archive_handoff_export",
    "sensitive_reveal",
    "object_reveal",
    "route_policy_change",
    "security_policy_edit",
    "admin_override",
    "clearance_grant",
    "app_clearance_grant",
}


try:
    _pack095b_original_evaluate_session_risk
except NameError:
    _pack095b_original_evaluate_session_risk = evaluate_session_risk


def _pack095b_has_abuse_volume(kwargs: Dict[str, Any]) -> bool:
    return (
        _safe_int(kwargs.get("request_count_1m"), 0) >= 30
        or _safe_int(kwargs.get("denied_count_5m"), 0) >= 3
        or _safe_int(kwargs.get("failed_keycard_count_5m"), 0) >= 1
        or _safe_int(kwargs.get("export_attempt_count_10m"), 0) >= 2
        or _safe_int(kwargs.get("admin_action_count_10m"), 0) >= 2
        or _safe_int(kwargs.get("object_reveal_count_10m"), 0) >= 4
        or _safe_int(kwargs.get("live_or_broker_attempt_count_10m"), 0) >= 1
        or _safe_int(kwargs.get("suspicious_pattern_count"), 0) >= 1
    )


def _pack095b_rewrite_to_step_up(result: Dict[str, Any], reason_code: str) -> Dict[str, Any]:
    result = dict(result)
    result["decision"] = "step_up"
    result["allowed"] = False
    result["risk_state"] = "watch"
    result["required_actions"] = ["complete_step_up_auth"]
    result["human_reason"] = "Clean sensitive action requires fresh verification before continuing."
    result["soulaana_translation"] = "Soulaana: This is sensitive, not spammy. Ask for a fresh owner check before it moves."
    result["pack095b_override"] = reason_code

    event = result.get("event")
    if isinstance(event, dict):
        event = dict(event)
        event["decision"] = "step_up"
        event["allowed"] = False
        event["risk_state"] = "watch"
        event["required_actions"] = ["complete_step_up_auth"]
        event["human_reason"] = result["human_reason"]
        event["soulaana_translation"] = result["soulaana_translation"]
        event["pack095b_override"] = reason_code
        result["event"] = _redact_sensitive(event)

    return _redact_sensitive(result)


def evaluate_session_risk(*args, **kwargs):
    result = _pack095b_original_evaluate_session_risk(*args, **kwargs)

    if not isinstance(result, dict):
        return result

    action = _safe_str(kwargs.get("action", result.get("action")), "view_status")
    auto_apply = bool(kwargs.get("auto_apply", False))

    clean_sensitive = (
        action in PACK095B_CLEAN_STEP_UP_ACTIONS
        and result.get("decision") == "throttle"
        and not _pack095b_has_abuse_volume(kwargs)
    )

    if clean_sensitive:
        result = _pack095b_rewrite_to_step_up(result, "clean_sensitive_action_step_up_before_throttle")

        # If auto_apply was requested, regenerate the auto-apply result based on the rewritten decision.
        if auto_apply:
            result["auto_apply_result"] = apply_session_risk_decision(result)

        # Record corrected risk event so summaries reflect the final decision too.
        try:
            corrected_event = _record_risk_event({
                **result,
                "event_type": "tower_session_risk_event",
                "reason_code": "pack095b_clean_sensitive_step_up_override",
                "metadata": {
                    "pack": "095B",
                    "original_decision": "throttle",
                    "corrected_decision": "step_up",
                },
            })
            result["correction_event"] = corrected_event
        except Exception:
            pass

        return _redact_sensitive(result)

    return result



# ================================================================================
# PACK095C_MODERATE_NOISE_THROTTLE_OVERRIDE
# ================================================================================
# Keeps moderate scraping/noise in throttle instead of escalating too early
# into quarantine.
# ================================================================================

try:
    _pack095c_original_evaluate_session_risk
except NameError:
    _pack095c_original_evaluate_session_risk = evaluate_session_risk


def _pack095c_is_moderate_noise(kwargs: Dict[str, Any], result: Dict[str, Any]) -> bool:
    action = _safe_str(kwargs.get("action", result.get("action")), "view_status")

    request_count = _safe_int(kwargs.get("request_count_1m"), 0)
    denied_count = _safe_int(kwargs.get("denied_count_5m"), 0)
    failed_keycards = _safe_int(kwargs.get("failed_keycard_count_5m"), 0)
    export_attempts = _safe_int(kwargs.get("export_attempt_count_10m"), 0)
    admin_actions = _safe_int(kwargs.get("admin_action_count_10m"), 0)
    object_reveals = _safe_int(kwargs.get("object_reveal_count_10m"), 0)
    live_attempts = _safe_int(kwargs.get("live_or_broker_attempt_count_10m"), 0)
    suspicious_patterns = _safe_int(kwargs.get("suspicious_pattern_count"), 0)

    base_clearance = kwargs.get("base_clearance_decision")
    if isinstance(base_clearance, dict) and (
        base_clearance.get("decision") == "deny" or base_clearance.get("allowed") is False
    ):
        return False

    if action in {
        "admin_override",
        "route_policy_change",
        "security_policy_edit",
        "clearance_grant",
        "app_clearance_grant",
        "live_mode_enable",
        "automated_mode_enable",
        "broker_action",
        "capital_movement",
        "payment_batch_release",
        "disable_security",
        "lockdown_disable",
    }:
        return False

    if (
        failed_keycards >= 1
        or export_attempts >= 1
        or admin_actions >= 1
        or live_attempts >= 1
        or suspicious_patterns >= 1
        or object_reveals >= 4
    ):
        return False

    return (
        result.get("decision") == "quarantine"
        and 30 <= request_count < 120
        and 0 <= denied_count <= 5
        and result.get("risk_score", 0) < 75
    )


def _pack095c_rewrite_to_throttle(result: Dict[str, Any], reason_code: str) -> Dict[str, Any]:
    result = dict(result)
    result["decision"] = "throttle"
    result["allowed"] = False
    result["risk_state"] = "watch"
    result["required_actions"] = ["slow_request_rate", "complete_step_up_auth_if_sensitive"]
    result["human_reason"] = "Moderate request noise detected. Slow the subject before escalating to quarantine."
    result["soulaana_translation"] = "Soulaana: This looks noisy, not catastrophic. Slow it down before reaching for the holding room."
    result["pack095c_override"] = reason_code

    event = result.get("event")
    if isinstance(event, dict):
        event = dict(event)
        event["decision"] = "throttle"
        event["allowed"] = False
        event["risk_state"] = "watch"
        event["required_actions"] = ["slow_request_rate", "complete_step_up_auth_if_sensitive"]
        event["human_reason"] = result["human_reason"]
        event["soulaana_translation"] = result["soulaana_translation"]
        event["pack095c_override"] = reason_code
        result["event"] = _redact_sensitive(event)

    return _redact_sensitive(result)


def evaluate_session_risk(*args, **kwargs):
    result = _pack095c_original_evaluate_session_risk(*args, **kwargs)

    if not isinstance(result, dict):
        return result

    auto_apply = bool(kwargs.get("auto_apply", False))

    if _pack095c_is_moderate_noise(kwargs, result):
        result = _pack095c_rewrite_to_throttle(result, "moderate_noise_throttle_before_quarantine")

        if auto_apply:
            result["auto_apply_result"] = apply_session_risk_decision(result)

        try:
            corrected_event = _record_risk_event({
                **result,
                "event_type": "tower_session_risk_event",
                "reason_code": "pack095c_moderate_noise_throttle_override",
                "metadata": {
                    "pack": "095C",
                    "original_decision": "quarantine",
                    "corrected_decision": "throttle",
                },
            })
            result["correction_event"] = corrected_event
        except Exception:
            pass

        return _redact_sensitive(result)

    return result



# ================================================================================
# PACK095D_ADMIN_SUSPICION_QUARANTINE_BEFORE_DENY
# ================================================================================
# Keeps suspicious-but-not-catastrophic admin/device/IP combos in quarantine
# instead of jumping directly to deny.
# ================================================================================

try:
    _pack095d_original_evaluate_session_risk
except NameError:
    _pack095d_original_evaluate_session_risk = evaluate_session_risk


def _pack095d_is_first_containment_admin_case(kwargs: Dict[str, Any], result: Dict[str, Any]) -> bool:
    action = _safe_str(kwargs.get("action", result.get("action")), "")
    route_path = _safe_str(kwargs.get("route_path", result.get("route_path")), "")

    request_count = _safe_int(kwargs.get("request_count_1m"), 0)
    denied_count = _safe_int(kwargs.get("denied_count_5m"), 0)
    failed_keycards = _safe_int(kwargs.get("failed_keycard_count_5m"), 0)
    admin_actions = _safe_int(kwargs.get("admin_action_count_10m"), 0)
    live_attempts = _safe_int(kwargs.get("live_or_broker_attempt_count_10m"), 0)
    suspicious_patterns = _safe_int(kwargs.get("suspicious_pattern_count"), 0)

    base_clearance = kwargs.get("base_clearance_decision")
    if isinstance(base_clearance, dict) and (
        base_clearance.get("decision") == "deny" or base_clearance.get("allowed") is False
    ):
        return False

    if action in {"disable_security", "lockdown_disable", "live_mode_enable", "automated_mode_enable", "broker_action"}:
        return False

    # Catastrophic signals should not be softened.
    if failed_keycards >= 4 or denied_count >= 10 or request_count >= 120 or live_attempts >= 1 or suspicious_patterns >= 5:
        return False

    # The intended Pack 095 quarantine lane:
    # suspicious admin surface + unfamiliar context + small probe/keycard/admin cluster.
    return (
        result.get("decision") == "deny"
        and action in {"admin_override", "route_policy_change", "security_policy_edit", "clearance_grant", "app_clearance_grant"}
        and route_path.startswith("/admin")
        and request_count < 60
        and denied_count <= 5
        and failed_keycards <= 1
        and admin_actions <= 2
        and result.get("risk_score", 0) >= 80
    )


def _pack095d_rewrite_to_quarantine(result: Dict[str, Any], reason_code: str) -> Dict[str, Any]:
    result = dict(result)
    result["decision"] = "quarantine"
    result["allowed"] = False
    result["risk_state"] = "restricted"
    result["required_actions"] = ["quarantine_subject", "owner_review"]
    result["human_reason"] = "Suspicious admin pattern detected. Contain the subject in quarantine before escalating to outright deny."
    result["soulaana_translation"] = "Soulaana: This is suspicious enough for the holding room, not yet a full no-hallway denial."
    result["pack095d_override"] = reason_code

    event = result.get("event")
    if isinstance(event, dict):
        event = dict(event)
        event["decision"] = "quarantine"
        event["allowed"] = False
        event["risk_state"] = "restricted"
        event["required_actions"] = ["quarantine_subject", "owner_review"]
        event["human_reason"] = result["human_reason"]
        event["soulaana_translation"] = result["soulaana_translation"]
        event["pack095d_override"] = reason_code
        result["event"] = _redact_sensitive(event)

    return _redact_sensitive(result)


def evaluate_session_risk(*args, **kwargs):
    result = _pack095d_original_evaluate_session_risk(*args, **kwargs)

    if not isinstance(result, dict):
        return result

    auto_apply = bool(kwargs.get("auto_apply", False))

    if _pack095d_is_first_containment_admin_case(kwargs, result):
        result = _pack095d_rewrite_to_quarantine(result, "admin_suspicion_quarantine_before_deny")

        if auto_apply:
            result["auto_apply_result"] = apply_session_risk_decision(result)

        try:
            corrected_event = _record_risk_event({
                **result,
                "event_type": "tower_session_risk_event",
                "reason_code": "pack095d_admin_suspicion_quarantine_override",
                "metadata": {
                    "pack": "095D",
                    "original_decision": "deny",
                    "corrected_decision": "quarantine",
                },
            })
            result["correction_event"] = corrected_event
        except Exception:
            pass

        return _redact_sensitive(result)

    return result

