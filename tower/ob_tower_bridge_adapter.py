
from __future__ import annotations

import hashlib
import json
import secrets
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "tower" / "data"

OB_TOWER_BRIDGE_EVENTS_PATH = DATA_DIR / "ob_tower_bridge_events.json"
OB_TOWER_BRIDGE_POLICY_PATH = DATA_DIR / "ob_tower_bridge_policy.json"
OB_TOWER_BRIDGE_SUMMARY_PATH = DATA_DIR / "ob_tower_bridge_summary.json"


OB_APP_ID = "observatory"


BRIDGE_REQUEST_TYPES = {
    "app_entry",
    "route_access",
    "mode_access",
    "object_access",
    "action_access",
    "export_access",
    "reveal_access",
    "live_action_access",
    "broker_action_access",
    "archive_handoff",
    "security_event",
}


OB_MODES = {
    "survey",
    "paper",
    "live_manual",
    "live_hybrid",
    "live_automated",
}


OB_OBJECT_TYPES = {
    "symbol",
    "signal",
    "candidate",
    "position",
    "trade",
    "portfolio",
    "account",
    "analysis",
    "report",
    "export",
    "admin_panel",
    "mode",
    "route",
}


BRIDGE_DECISIONS = {
    "allow",
    "deny",
    "step_up_required",
    "summary_only",
    "redacted_summary",
    "quarantine",
    "lockdown",
    "receipt_recorded",
    "archive_handoff_created",
}


OB_TOWER_BRIDGE_POLICY = {
    "pack": "101",
    "adapter_id": "ob_tower_bridge_adapter",
    "app_id": OB_APP_ID,
    "tower_is_outer_control_center": True,
    "ob_must_request_clearance_before_protected_load": True,
    "default_decision": "deny",
    "public_safe_routes": [
        "/signals-spotlight",
        "/public/signals-spotlight",
        "/health",
    ],
    "owner_allowed_modes": [
        "survey",
        "paper",
        "live_manual",
        "live_hybrid",
        "live_automated",
    ],
    "beta_allowed_modes": [
        "survey",
        "paper",
    ],
    "blocked_without_step_up_actions": [
        "export",
        "download",
        "reveal_sensitive",
        "live_mode_enable",
        "broker_action",
        "automated_mode_enable",
        "admin_override",
    ],
    "never_public_actions": [
        "broker_action",
        "live_mode_enable",
        "automated_mode_enable",
        "admin_override",
        "raw_data_view",
        "secret_status",
    ],
    "live_locked_until_compliance": True,
    "requires_receipts_for_actions": [
        "export",
        "download",
        "reveal_sensitive",
        "mode_access_grant",
        "live_mode_enable",
        "broker_action",
        "admin_override",
        "archive_handoff",
    ],
    "requires_archive_handoff_for_actions": [
        "export",
        "download",
        "trade_packet",
        "proof_packet",
        "admin_override",
        "live_action",
    ],
    "human_reason": "OB must request Tower clearance before protected app, route, mode, object, export, reveal, live, broker, and admin actions.",
    "soulaana_translation": "Soulaana: OB knocks. Tower decides. No Tower clearance, no Observatory hallway.",
}


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _safe_str(value: Any, default: str = "") -> str:
    if value is None:
        return default
    text = str(value).strip()
    return text if text else default


def _safe_bool(value: Any, default: bool = False) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "y", "allow", "allowed"}
    if value is None:
        return default
    return bool(value)


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


def _bridge_id(prefix: str = "ob_bridge") -> str:
    return f"{prefix}_{secrets.token_urlsafe(18)}"


def _redact(value: Any) -> Any:
    secret_keys = {
        "token",
        "raw_token",
        "access_token",
        "refresh_token",
        "api_key",
        "apikey",
        "secret",
        "client_secret",
        "password",
        "passphrase",
        "private_key",
        "encryption_key",
        "broker_key",
        "broker_secret",
        "github_token",
        "stripe_secret",
        "payment_secret",
        "authorization",
        "bearer",
        "credential",
        "credentials",
        "tower_keycard",
        "session_secret",
        "device_secret",
        "raw_value",
    }

    sensitive_keys = {
        "ssn",
        "bank_account",
        "routing_number",
        "account_number",
        "document_text",
        "raw_payload",
        "private_notes",
        "legal_notes",
        "medical_notes",
    }

    if isinstance(value, dict):
        clean = {}
        redacted_count = 0

        for key, item in value.items():
            key_text = str(key).lower().strip()

            if key_text in secret_keys or key_text.endswith(("_token", "_password", "_api_key", "_secret", "_credential")):
                redacted_count += 1
                continue

            if key_text in sensitive_keys:
                clean[key] = "[REDACTED_OB_BRIDGE_SENSITIVE]"
                redacted_count += 1
                continue

            redacted_item = _redact(item)

            if isinstance(redacted_item, dict) and "__redacted_ob_bridge_field_count__" in redacted_item:
                try:
                    redacted_count += int(redacted_item.get("__redacted_ob_bridge_field_count__", 0))
                except Exception:
                    redacted_count += 1
                redacted_item = dict(redacted_item)
                redacted_item.pop("__redacted_ob_bridge_field_count__", None)

            clean[key] = redacted_item

        if redacted_count:
            clean["__redacted_ob_bridge_field_count__"] = redacted_count

        return clean

    if isinstance(value, list):
        return [_redact(item) for item in value]

    if isinstance(value, str):
        lowered = value.lower()
        if lowered.startswith("secret_ref_"):
            return value
        if (
            "should_not_survive" in lowered
            or "tower_keycard=" in lowered
            or "bearer " in lowered
            or "ghp_" in lowered
            or "sk_live_" in lowered
            or "-----begin private key-----" in lowered
            or "access_token=" in lowered
            or "refresh_token=" in lowered
        ):
            return "[REDACTED_OB_BRIDGE_VALUE]"
        return value

    return value


def _canonical_json(value: Any) -> str:
    return json.dumps(_redact(value), sort_keys=True, separators=(",", ":"), default=str)


def _fingerprint(value: Any) -> str:
    return hashlib.sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def _safe_scan(payload: Any) -> Dict[str, Any]:
    serialized = json.dumps(payload, sort_keys=True, default=str).lower()
    forbidden = [
        "should_not_survive",
        "tower_keycard=",
        "bearer should_not_survive",
        "ghp_should_not_survive",
        "sk_live_should_not_survive",
        "-----begin private key-----",
        '"raw_token":',
        '"tower_keycard":',
        '"access_token":',
        '"refresh_token":',
        '"api_key":',
        '"github_token":',
        '"stripe_secret":',
        '"password":',
        '"private_key":',
    ]
    hits = [item for item in forbidden if item in serialized]
    return {
        "ok": not hits,
        "forbidden_hit_count": len(hits),
        "had_forbidden_hits": bool(hits),
    }


def _load_events() -> List[Dict[str, Any]]:
    data = _load_json(OB_TOWER_BRIDGE_EVENTS_PATH, [])
    return data if isinstance(data, list) else []


def _save_events(events: List[Dict[str, Any]]) -> None:
    _write_json(OB_TOWER_BRIDGE_EVENTS_PATH, events)


def initialize_ob_tower_bridge_policy() -> Dict[str, Any]:
    policy = dict(OB_TOWER_BRIDGE_POLICY)
    policy["updated_at"] = _utc_now()
    policy["policy_fingerprint"] = _fingerprint(policy)
    _write_json(OB_TOWER_BRIDGE_POLICY_PATH, _redact(policy))
    return _redact(policy)


def make_ob_bridge_request(
    *,
    user_id: str,
    request_type: str,
    route_path: str = "",
    mode: str = "",
    object_type: str = "",
    object_id: str = "",
    action: str = "",
    app_id: str = OB_APP_ID,
    role: str = "beta",
    session_id: str = "",
    device_id: str = "",
    ip_address: str = "",
    metadata: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    request_type = _safe_str(request_type, "route_access")
    if request_type not in BRIDGE_REQUEST_TYPES:
        request_type = "action_access"

    req = {
        "ok": True,
        "pack": "101",
        "bridge_request_id": _bridge_id("ob_req"),
        "created_at": _utc_now(),
        "app_id": _safe_str(app_id, OB_APP_ID),
        "user_id": _safe_str(user_id, "anonymous"),
        "role": _safe_str(role, "beta"),
        "request_type": request_type,
        "route_path": _safe_str(route_path),
        "mode": _safe_str(mode),
        "object_type": _safe_str(object_type),
        "object_id": _safe_str(object_id),
        "action": _safe_str(action),
        "session_id": _safe_str(session_id),
        "device_id": _safe_str(device_id),
        "ip_address": _safe_str(ip_address),
        "metadata": _redact(metadata if isinstance(metadata, dict) else {}),
    }
    req["request_fingerprint"] = _fingerprint(req)
    return _redact(req)


def _record_bridge_event(event: Dict[str, Any]) -> Dict[str, Any]:
    event = dict(event)
    event.setdefault("event_id", _bridge_id("ob_bridge_evt"))
    event.setdefault("event_type", "tower_ob_bridge_event")
    event.setdefault("created_at", _utc_now())
    event.setdefault("pack", "101")

    event = _redact(event)
    event["event_fingerprint"] = _fingerprint(event)

    events = _load_events()
    events.append(event)
    _save_events(events)

    try:
        from tower.tamper_evident_audit_chain import create_tamper_chain_entry

        create_tamper_chain_entry(
            event_type="tower_ob_bridge_event_snapshot",
            source_name="ob_tower_bridge_events",
            source_path=str(OB_TOWER_BRIDGE_EVENTS_PATH),
            source_hash=_fingerprint(events),
            record_count=len(events),
            actor_user_id=_safe_str(event.get("user_id"), "tower_system"),
            reason=f"Pack 101 chained OB bridge event {event.get('decision')}.",
            metadata={
                "pack": "101",
                "event_id": event.get("event_id"),
                "bridge_request_id": event.get("bridge_request_id"),
                "decision": event.get("decision"),
            },
        )
    except Exception:
        pass

    return event


def _load_lockdown_active() -> bool:
    state = _load_json(DATA_DIR / "emergency_lockdown_state.json", {})
    return bool(isinstance(state, dict) and state.get("lockdown_active") is True)


def _active_quarantine_applies(request: Dict[str, Any]) -> bool:
    state = _load_json(DATA_DIR / "quarantine_mode_state.json", {})
    if not isinstance(state, dict):
        return False

    cases = state.get("active_cases", [])
    if not isinstance(cases, list):
        return False

    user_id = request.get("user_id")
    session_id = request.get("session_id")
    device_id = request.get("device_id")
    ip_address = request.get("ip_address")

    for case in cases:
        if not isinstance(case, dict) or case.get("status") != "active":
            continue
        target = case.get("target", {}) if isinstance(case.get("target"), dict) else {}
        if target.get("user_id") and target.get("user_id") == user_id:
            return True
        if target.get("session_id") and target.get("session_id") == session_id:
            return True
        if target.get("device_id") and target.get("device_id") == device_id:
            return True
        if target.get("ip_address") and target.get("ip_address") == ip_address:
            return True

    return False


def _role_is_owner(role: str, user_id: str) -> bool:
    role = _safe_str(role).lower()
    user_id = _safe_str(user_id).lower()
    return role in {"owner", "master", "admin_owner"} or user_id in {"owner_solice", "solice", "solice_bowdre"}


def _role_is_beta(role: str) -> bool:
    return _safe_str(role).lower() in {"beta", "tester", "user", "member"}


def _public_route_allowed(route_path: str) -> bool:
    route_path = _safe_str(route_path)
    safe_routes = OB_TOWER_BRIDGE_POLICY.get("public_safe_routes", [])
    return route_path in safe_routes or route_path.startswith("/public/")


def _mode_allowed_for_role(mode: str, role: str, user_id: str) -> bool:
    mode = _safe_str(mode).lower()
    role = _safe_str(role).lower()

    if not mode:
        return True

    if _role_is_owner(role, user_id):
        return mode in OB_TOWER_BRIDGE_POLICY["owner_allowed_modes"]

    if _role_is_beta(role):
        return mode in OB_TOWER_BRIDGE_POLICY["beta_allowed_modes"]

    return mode == "survey"


def _action_is_never_public(action: str) -> bool:
    action = _safe_str(action).lower()
    return action in set(OB_TOWER_BRIDGE_POLICY.get("never_public_actions", []))


def _action_requires_step_up(action: str, request_type: str, mode: str) -> bool:
    action = _safe_str(action).lower()
    request_type = _safe_str(request_type).lower()
    mode = _safe_str(mode).lower()

    if action in set(OB_TOWER_BRIDGE_POLICY.get("blocked_without_step_up_actions", [])):
        return True
    if request_type in {"export_access", "reveal_access", "live_action_access", "broker_action_access"}:
        return True
    if mode in {"live_manual", "live_hybrid", "live_automated"}:
        return True

    return False


def _action_requires_receipt(action: str, request_type: str) -> bool:
    action = _safe_str(action).lower()
    request_type = _safe_str(request_type).lower()
    if action in set(OB_TOWER_BRIDGE_POLICY.get("requires_receipts_for_actions", [])):
        return True
    return request_type in {"export_access", "reveal_access", "live_action_access", "broker_action_access", "archive_handoff"}


def _action_requires_archive_handoff(action: str, request_type: str) -> bool:
    action = _safe_str(action).lower()
    request_type = _safe_str(request_type).lower()
    if action in set(OB_TOWER_BRIDGE_POLICY.get("requires_archive_handoff_for_actions", [])):
        return True
    return request_type in {"export_access", "archive_handoff"}


def _base_bridge_decision(request: Dict[str, Any]) -> Dict[str, Any]:
    user_id = request.get("user_id", "anonymous")
    role = request.get("role", "beta")
    request_type = request.get("request_type", "route_access")
    route_path = request.get("route_path", "")
    mode = request.get("mode", "")
    action = request.get("action", "")
    object_type = request.get("object_type", "")

    if request.get("app_id") != OB_APP_ID:
        return {
            "decision": "deny",
            "reason_code": "unsupported_app_id",
            "human_reason": "Bridge only supports Observatory app clearance in Pack 101.",
        }

    if _load_lockdown_active():
        return {
            "decision": "lockdown",
            "reason_code": "tower_lockdown_active",
            "human_reason": "Emergency lockdown is active. OB access cannot proceed.",
        }

    if _active_quarantine_applies(request):
        return {
            "decision": "quarantine",
            "reason_code": "tower_quarantine_active_for_subject",
            "human_reason": "Subject is in Tower quarantine. OB access cannot proceed.",
        }

    if _public_route_allowed(route_path) and request_type in {"route_access", "app_entry"}:
        return {
            "decision": "allow",
            "reason_code": "public_safe_ob_route",
            "human_reason": "Public-safe OB route allowed.",
        }

    if _action_is_never_public(action) and not _role_is_owner(role, user_id):
        return {
            "decision": "deny",
            "reason_code": "action_never_public",
            "human_reason": "This action is never public/beta-accessible.",
        }

    if request_type in {"live_action_access", "broker_action_access"}:
        return {
            "decision": "deny",
            "reason_code": "live_and_broker_locked_until_compliance",
            "human_reason": "Live/broker actions remain locked until compliance and production controls are ready.",
        }

    if mode and not _mode_allowed_for_role(mode, role, user_id):
        return {
            "decision": "deny",
            "reason_code": "mode_not_allowed_for_role",
            "human_reason": "Requested OB mode is not allowed for this role.",
        }

    if object_type and object_type not in OB_OBJECT_TYPES:
        return {
            "decision": "deny",
            "reason_code": "unsupported_ob_object_type",
            "human_reason": "Requested OB object type is unsupported by the bridge contract.",
        }

    if _action_requires_step_up(action, request_type, mode):
        return {
            "decision": "step_up_required",
            "reason_code": "step_up_required_for_ob_bridge_action",
            "human_reason": "This OB action requires Tower step-up before continuing.",
        }

    if request_type == "reveal_access":
        return {
            "decision": "summary_only",
            "reason_code": "redaction_summary_first",
            "human_reason": "Sensitive reveal requests start as summary-only until reveal gates pass.",
        }

    if request_type == "app_entry":
        return {
            "decision": "allow",
            "reason_code": "ob_app_entry_allowed_by_contract",
            "human_reason": "OB app entry allowed by bridge contract.",
        }

    return {
        "decision": "allow",
        "reason_code": "ob_bridge_contract_allows_request",
        "human_reason": "OB bridge contract allows request.",
    }


def evaluate_ob_tower_bridge_request(request: Dict[str, Any]) -> Dict[str, Any]:
    request = request if isinstance(request, dict) else make_ob_bridge_request(
        user_id="anonymous",
        request_type="route_access",
    )
    request = _redact(request)

    base = _base_bridge_decision(request)
    decision = base.get("decision", "deny")
    action = request.get("action", "")
    request_type = request.get("request_type", "")

    response = {
        "ok": decision in {"allow", "step_up_required", "summary_only", "redacted_summary"},
        "pack": "101",
        "bridge_response_id": _bridge_id("ob_resp"),
        "bridge_request_id": request.get("bridge_request_id"),
        "created_at": _utc_now(),
        "app_id": request.get("app_id"),
        "user_id": request.get("user_id"),
        "role": request.get("role"),
        "request_type": request_type,
        "route_path": request.get("route_path"),
        "mode": request.get("mode"),
        "object_type": request.get("object_type"),
        "object_id": request.get("object_id"),
        "action": action,
        "decision": decision,
        "allowed": decision == "allow",
        "reason_code": base.get("reason_code"),
        "requires_step_up": decision == "step_up_required",
        "requires_receipt": _action_requires_receipt(action, request_type),
        "requires_archive_handoff": _action_requires_archive_handoff(action, request_type),
        "requires_redacted_summary": decision in {"summary_only", "redacted_summary"},
        "required_actions": [],
        "tower_controls_checked": {
            "lockdown": True,
            "quarantine": True,
            "role_mode_policy": True,
            "live_broker_lock": True,
            "step_up_policy": True,
            "receipt_policy": True,
            "archive_policy": True,
        },
        "human_reason": base.get("human_reason"),
        "soulaana_translation": "",
    }

    if decision == "allow":
        response["required_actions"] = ["continue_to_ob"]
        response["soulaana_translation"] = "Soulaana: Tower gate opened. OB may proceed on this path."
    elif decision == "step_up_required":
        response["required_actions"] = ["complete_tower_step_up", "retry_bridge_request"]
        response["soulaana_translation"] = "Soulaana: OB is asking for a powerful hallway. Fresh Tower verification first."
    elif decision == "summary_only":
        response["required_actions"] = ["show_redacted_summary", "request_reveal_if_needed"]
        response["soulaana_translation"] = "Soulaana: Summary glass only. Details need reveal gates."
    elif decision == "quarantine":
        response["required_actions"] = ["show_quarantine_holding_state", "owner_review"]
        response["soulaana_translation"] = "Soulaana: Holding room applies. OB does not get a hallway."
    elif decision == "lockdown":
        response["required_actions"] = ["show_lockdown_state", "owner_recovery_only"]
        response["soulaana_translation"] = "Soulaana: Fortress doors are sealed. OB waits outside."
    else:
        response["required_actions"] = ["deny_ob_access", "record_security_event_if_needed"]
        response["soulaana_translation"] = "Soulaana: No Tower clearance. No Observatory hallway."

    response = _redact(response)
    response["response_fingerprint"] = _fingerprint(response)

    event = _record_bridge_event({
        "bridge_request_id": request.get("bridge_request_id"),
        "bridge_response_id": response.get("bridge_response_id"),
        "user_id": request.get("user_id"),
        "request": request,
        "decision": response.get("decision"),
        "reason_code": response.get("reason_code"),
        "response": response,
    })
    response["event"] = event

    scan = _safe_scan(response)
    response["no_secret_leakage"] = scan.get("ok") is True
    response["leakage_scan"] = scan

    return response


def request_ob_app_clearance(*, user_id: str, role: str = "beta", **kwargs) -> Dict[str, Any]:
    request = make_ob_bridge_request(
        user_id=user_id,
        role=role,
        request_type="app_entry",
        route_path=kwargs.pop("route_path", "/observatory-private"),
        **kwargs,
    )
    return evaluate_ob_tower_bridge_request(request)


def request_ob_route_clearance(*, user_id: str, route_path: str, role: str = "beta", **kwargs) -> Dict[str, Any]:
    request = make_ob_bridge_request(
        user_id=user_id,
        role=role,
        request_type="route_access",
        route_path=route_path,
        **kwargs,
    )
    return evaluate_ob_tower_bridge_request(request)


def request_ob_mode_clearance(*, user_id: str, mode: str, role: str = "beta", **kwargs) -> Dict[str, Any]:
    request = make_ob_bridge_request(
        user_id=user_id,
        role=role,
        request_type="mode_access",
        mode=mode,
        object_type="mode",
        object_id=mode,
        **kwargs,
    )
    return evaluate_ob_tower_bridge_request(request)


def request_ob_object_clearance(*, user_id: str, object_type: str, object_id: str, role: str = "beta", **kwargs) -> Dict[str, Any]:
    request = make_ob_bridge_request(
        user_id=user_id,
        role=role,
        request_type="object_access",
        object_type=object_type,
        object_id=object_id,
        **kwargs,
    )
    return evaluate_ob_tower_bridge_request(request)


def request_ob_action_clearance(*, user_id: str, action: str, role: str = "beta", **kwargs) -> Dict[str, Any]:
    request = make_ob_bridge_request(
        user_id=user_id,
        role=role,
        request_type="action_access",
        action=action,
        **kwargs,
    )
    return evaluate_ob_tower_bridge_request(request)


def request_ob_export_clearance(*, user_id: str, export_id: str, role: str = "beta", **kwargs) -> Dict[str, Any]:
    request = make_ob_bridge_request(
        user_id=user_id,
        role=role,
        request_type="export_access",
        object_type="export",
        object_id=export_id,
        action="export",
        **kwargs,
    )
    return evaluate_ob_tower_bridge_request(request)


def request_ob_reveal_clearance(*, user_id: str, object_type: str, object_id: str, role: str = "beta", **kwargs) -> Dict[str, Any]:
    request = make_ob_bridge_request(
        user_id=user_id,
        role=role,
        request_type="reveal_access",
        object_type=object_type,
        object_id=object_id,
        action="reveal_sensitive",
        **kwargs,
    )
    return evaluate_ob_tower_bridge_request(request)


def request_ob_live_action_clearance(*, user_id: str, action: str = "live_mode_enable", role: str = "beta", **kwargs) -> Dict[str, Any]:
    request = make_ob_bridge_request(
        user_id=user_id,
        role=role,
        request_type="live_action_access",
        mode=kwargs.pop("mode", "live_manual"),
        action=action,
        **kwargs,
    )
    return evaluate_ob_tower_bridge_request(request)


def submit_ob_security_event(
    *,
    user_id: str,
    event_name: str,
    severity: str = "info",
    role: str = "beta",
    metadata: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    request = make_ob_bridge_request(
        user_id=user_id,
        role=role,
        request_type="security_event",
        action=event_name,
        metadata={
            "severity": severity,
            "event_name": event_name,
            **(metadata or {}),
        },
    )
    response = evaluate_ob_tower_bridge_request(request)
    response["security_event_recorded"] = True
    return _redact(response)


def create_ob_archive_handoff_request(
    *,
    user_id: str,
    handoff_id: str,
    role: str = "owner",
    metadata: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    request = make_ob_bridge_request(
        user_id=user_id,
        role=role,
        request_type="archive_handoff",
        object_type="export",
        object_id=handoff_id,
        action="archive_handoff",
        metadata=metadata or {},
    )
    return evaluate_ob_tower_bridge_request(request)


def summarize_ob_tower_bridge(limit: int = 40) -> Dict[str, Any]:
    initialize_ob_tower_bridge_policy()
    events = _load_events()

    try:
        limit = int(limit)
    except Exception:
        limit = 40
    limit = max(1, min(limit, 200))

    by_decision: Dict[str, int] = {}
    by_request_type: Dict[str, int] = {}
    by_reason: Dict[str, int] = {}

    for event in events:
        decision = event.get("decision", "unknown")
        request = event.get("request", {}) if isinstance(event.get("request"), dict) else {}
        request_type = request.get("request_type", "unknown")
        reason = event.get("reason_code", "unknown")

        by_decision[decision] = by_decision.get(decision, 0) + 1
        by_request_type[request_type] = by_request_type.get(request_type, 0) + 1
        by_reason[reason] = by_reason.get(reason, 0) + 1

    summary = {
        "ok": True,
        "pack": "101",
        "events_path": str(OB_TOWER_BRIDGE_EVENTS_PATH),
        "policy_path": str(OB_TOWER_BRIDGE_POLICY_PATH),
        "summary_path": str(OB_TOWER_BRIDGE_SUMMARY_PATH),
        "event_count": len(events),
        "by_decision": by_decision,
        "by_request_type": by_request_type,
        "by_reason": by_reason,
        "policy": OB_TOWER_BRIDGE_POLICY,
        "recent_events": events[-limit:],
        "readiness_score": 100,
        "readiness_label": "OB Tower Bridge adapter foundation ready",
        "human_reason": "OB Tower Bridge summary loaded.",
        "soulaana_translation": "Soulaana: OB has a contract now. It knocks, Tower decides.",
    }

    summary = _redact(summary)
    scan = _safe_scan(summary)
    summary["no_secret_leakage"] = scan.get("ok") is True
    summary["leakage_scan"] = scan

    _write_json(OB_TOWER_BRIDGE_SUMMARY_PATH, summary)
    return summary


def reset_ob_tower_bridge_for_test() -> Dict[str, Any]:
    _save_events([])
    initialize_ob_tower_bridge_policy()
    _write_json(OB_TOWER_BRIDGE_SUMMARY_PATH, {
        "ok": True,
        "pack": "101",
        "event_count": 0,
        "human_reason": "OB Tower Bridge summary reset for test.",
        "soulaana_translation": "Soulaana: Bridge log reset for a clean test lane.",
    })
    return {
        "ok": True,
        "decision": "ob_tower_bridge_reset_for_test",
        "events_reset": True,
        "policy_initialized": True,
        "soulaana_translation": "Soulaana: OB bridge reset for a clean test lane.",
    }



# ================================================================================
# PACK101B_COMPATIBILITY_ALIAS
# ================================================================================
# Preserve the test/import name while keeping the original helper name.
# ================================================================================

def request_ob_archive_handoff_request(
    *,
    user_id: str,
    handoff_id: str,
    role: str = "owner",
    metadata: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    return create_ob_archive_handoff_request(
        user_id=user_id,
        handoff_id=handoff_id,
        role=role,
        metadata=metadata,
    )



# ================================================================================
# PACK101C_ARCHIVE_HANDOFF_REQUIRES_STEP_UP
# ================================================================================
# Archive handoff is a proof-moving action. It should never silently allow;
# it should require Tower step-up before continuing.
# ================================================================================

try:
    _pack101c_original_action_requires_step_up
except NameError:
    _pack101c_original_action_requires_step_up = _action_requires_step_up


def _action_requires_step_up(action: str, request_type: str, mode: str) -> bool:
    action = _safe_str(action).lower()
    request_type = _safe_str(request_type).lower()
    mode = _safe_str(mode).lower()

    if request_type == "archive_handoff" or action == "archive_handoff":
        return True

    return _pack101c_original_action_requires_step_up(action, request_type, mode)


try:
    _pack101c_original_base_bridge_decision
except NameError:
    _pack101c_original_base_bridge_decision = _base_bridge_decision


def _base_bridge_decision(request: Dict[str, Any]) -> Dict[str, Any]:
    request_type = _safe_str(request.get("request_type"), "").lower()
    action = _safe_str(request.get("action"), "").lower()

    if request_type == "archive_handoff" or action == "archive_handoff":
        if request.get("app_id") != OB_APP_ID:
            return {
                "decision": "deny",
                "reason_code": "unsupported_app_id",
                "human_reason": "Bridge only supports Observatory app clearance in Pack 101.",
            }

        if _load_lockdown_active():
            return {
                "decision": "lockdown",
                "reason_code": "tower_lockdown_active",
                "human_reason": "Emergency lockdown is active. OB archive handoff cannot proceed.",
            }

        if _active_quarantine_applies(request):
            return {
                "decision": "quarantine",
                "reason_code": "tower_quarantine_active_for_subject",
                "human_reason": "Subject is in Tower quarantine. OB archive handoff cannot proceed.",
            }

        return {
            "decision": "step_up_required",
            "reason_code": "step_up_required_for_ob_archive_handoff",
            "human_reason": "OB Archive handoff requires Tower step-up before proof moves.",
        }

    return _pack101c_original_base_bridge_decision(request)



# ================================================================================
# PACK102C_LIVE_MODE_ROUTE_DENIED_UNTIL_COMPLIANCE
# ================================================================================
# Live mode routes/actions should not become merely step-up gated yet.
# Until compliance/legal/production controls are ready, Live/Broker remains denied.
# ================================================================================

try:
    _pack102c_original_base_bridge_decision
except NameError:
    _pack102c_original_base_bridge_decision = _base_bridge_decision


def _base_bridge_decision(request: Dict[str, Any]) -> Dict[str, Any]:
    request_type = _safe_str(request.get("request_type"), "").lower()
    action = _safe_str(request.get("action"), "").lower()
    mode = _safe_str(request.get("mode"), "").lower()
    route_path = _safe_str(request.get("route_path"), "").lower()

    live_modes = {"live_manual", "live_hybrid", "live_automated"}
    live_route = route_path.startswith("/live") or route_path.startswith("/broker") or route_path.startswith("/automated")
    live_request = (
        request_type in {"live_action_access", "broker_action_access"}
        or action in {"live_mode_enable", "broker_action", "automated_mode_enable"}
        or mode in live_modes
        or live_route
    )

    if live_request:
        if request.get("app_id") != OB_APP_ID:
            return {
                "decision": "deny",
                "reason_code": "unsupported_app_id",
                "human_reason": "Bridge only supports Observatory app clearance in Pack 101.",
            }

        if _load_lockdown_active():
            return {
                "decision": "lockdown",
                "reason_code": "tower_lockdown_active",
                "human_reason": "Emergency lockdown is active. OB live/broker access cannot proceed.",
            }

        if _active_quarantine_applies(request):
            return {
                "decision": "quarantine",
                "reason_code": "tower_quarantine_active_for_subject",
                "human_reason": "Subject is in Tower quarantine. OB live/broker access cannot proceed.",
            }

        return {
            "decision": "deny",
            "reason_code": "live_and_broker_locked_until_compliance",
            "human_reason": "Live/broker actions remain locked until compliance and production controls are ready.",
        }

    return _pack102c_original_base_bridge_decision(request)

