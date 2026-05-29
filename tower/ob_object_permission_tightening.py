
from __future__ import annotations

import hashlib
import json
import secrets
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "tower" / "data"

OBJECT_POLICY_PATH = DATA_DIR / "ob_object_permission_policy.json"
OBJECT_EVENTS_PATH = DATA_DIR / "ob_object_permission_events.json"
OBJECT_STATUS_PATH = DATA_DIR / "ob_object_permission_status.json"
OBJECT_PANEL_PATH = DATA_DIR / "ob_object_permission_panel.html"


OB_OBJECT_TYPES = {
    "symbol",
    "position",
    "trade",
    "export",
    "report",
    "analysis",
    "admin_panel",
    "tower_object",
    "mode",
    "route",
}


PUBLIC_SAFE_OBJECT_TYPES = {
    "symbol",
    "route",
}


SENSITIVE_OBJECT_TYPES = {
    "position",
    "trade",
    "export",
    "report",
    "analysis",
    "admin_panel",
    "tower_object",
    "mode",
}


HIGH_RISK_OBJECT_TYPES = {
    "export",
    "admin_panel",
    "tower_object",
    "mode",
}


OWNER_ROLES = {"owner", "master", "admin_owner"}
ADMIN_ROLES = {"owner", "master", "admin_owner", "admin"}
BETA_ROLES = {"beta", "tester", "member", "user", "starter", "free", "pro", "elite"}


DEFAULT_OBJECT_PERMISSION_POLICY = {
    "pack": "108",
    "policy_id": "ob_object_permission_policy",
    "object_permissions_enabled": True,
    "default_decision": "deny",
    "symbol_policy": {
        "public_symbols_allowed": True,
        "symbol_must_be_normalized": True,
        "blocked_symbols": [],
    },
    "position_policy": {
        "owner_can_view_all": True,
        "beta_can_view_own_only": True,
        "requires_object_owner_match": True,
        "requires_receipt_for_edit_close": True,
    },
    "trade_policy": {
        "owner_can_view_all": True,
        "beta_can_view_own_only": True,
        "requires_object_owner_match": True,
    },
    "export_policy": {
        "owner_only": True,
        "requires_step_up": True,
        "requires_receipt": True,
        "requires_archive_handoff": True,
    },
    "admin_policy": {
        "owner_or_admin_only": True,
        "requires_step_up_for_mutation": True,
        "requires_receipt": True,
    },
    "live_mode_policy": {
        "locked_until_compliance": True,
        "owner_preview_allowed": False,
    },
    "human_reason": "OB object-level permissions are enforced after route guard approval.",
    "soulaana_translation": "Soulaana: The hallway can open, but the object still needs its own key.",
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


def _event_id(prefix: str = "ob_object_perm") -> str:
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
        "document_text",
        "raw_payload",
        "private_notes",
        "bank_account",
        "routing_number",
        "account_number",
        "ssn",
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
                clean[key] = "[REDACTED_OB_OBJECT_SENSITIVE]"
                redacted_count += 1
                continue

            redacted_item = _redact(item)

            if isinstance(redacted_item, dict) and "__redacted_ob_object_field_count__" in redacted_item:
                try:
                    redacted_count += int(redacted_item.get("__redacted_ob_object_field_count__", 0))
                except Exception:
                    redacted_count += 1
                redacted_item = dict(redacted_item)
                redacted_item.pop("__redacted_ob_object_field_count__", None)

            clean[key] = redacted_item

        if redacted_count:
            clean["__redacted_ob_object_field_count__"] = redacted_count

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
            return "[REDACTED_OB_OBJECT_VALUE]"
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


def _role_family(role: str, user_id: str = "") -> str:
    role = _safe_str(role).lower()
    user_id = _safe_str(user_id).lower()

    if role in OWNER_ROLES or user_id in {"owner_solice", "solice", "solice_bowdre", "bowdre.solice@gmail.com"}:
        return "owner"
    if role in ADMIN_ROLES:
        return "admin"
    if role in BETA_ROLES:
        return "beta"
    if role == "public":
        return "public"
    return "unknown"


def initialize_object_permission_policy() -> Dict[str, Any]:
    policy = dict(DEFAULT_OBJECT_PERMISSION_POLICY)
    policy["updated_at"] = _utc_now()
    policy["policy_fingerprint"] = _fingerprint(policy)
    _write_json(OBJECT_POLICY_PATH, _redact(policy))
    return _redact(policy)


def _load_events() -> List[Dict[str, Any]]:
    data = _load_json(OBJECT_EVENTS_PATH, [])
    return data if isinstance(data, list) else []


def _save_events(events: List[Dict[str, Any]]) -> None:
    _write_json(OBJECT_EVENTS_PATH, events)


def _record_object_event(event: Dict[str, Any]) -> Dict[str, Any]:
    event = dict(event)
    event.setdefault("event_id", _event_id("ob_object_perm_evt"))
    event.setdefault("event_type", "tower_ob_object_permission_event")
    event.setdefault("created_at", _utc_now())
    event.setdefault("pack", "108")

    event = _redact(event)
    event["event_fingerprint"] = _fingerprint(event)

    events = _load_events()
    events.append(event)
    _save_events(events)

    try:
        from tower.tamper_evident_audit_chain import create_tamper_chain_entry

        create_tamper_chain_entry(
            event_type="tower_ob_object_permission_event_snapshot",
            source_name="ob_object_permission_events",
            source_path=str(OBJECT_EVENTS_PATH),
            source_hash=_fingerprint(events),
            record_count=len(events),
            actor_user_id=_safe_str(event.get("user_id"), "tower_system"),
            reason=f"Pack 108 chained OB object permission event {event.get('decision')}.",
            metadata={
                "pack": "108",
                "event_id": event.get("event_id"),
                "object_type": event.get("object_type"),
                "object_id": event.get("object_id"),
                "decision": event.get("decision"),
            },
        )
    except Exception:
        pass

    return event


def normalize_ob_object(
    *,
    object_type: str,
    object_id: str,
    object_payload: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    object_type = _safe_str(object_type, "route").lower()
    object_id = _safe_str(object_id, "")
    payload = object_payload if isinstance(object_payload, dict) else {}

    if object_type not in OB_OBJECT_TYPES:
        object_type = "route"

    normalized_id = object_id

    if object_type == "symbol":
        normalized_id = object_id.strip().upper()

    owner_user_id = (
        payload.get("owner_user_id")
        or payload.get("user_id")
        or payload.get("created_by")
        or payload.get("account_user_id")
        or ""
    )

    status = _safe_str(payload.get("status"), "")
    vehicle = _safe_str(payload.get("vehicle"), "")

    obj = {
        "ok": True,
        "pack": "108",
        "object_type": object_type,
        "object_id": normalized_id,
        "owner_user_id": _safe_str(owner_user_id),
        "status": status,
        "vehicle": vehicle,
        "object_payload": _redact(payload),
        "object_fingerprint": "",
    }
    obj["object_fingerprint"] = _fingerprint(obj)
    return _redact(obj)


def evaluate_ob_object_permission(
    *,
    user_id: str,
    role: str,
    object_type: str,
    object_id: str,
    action: str = "view",
    object_payload: Dict[str, Any] | None = None,
    route_path: str = "",
    metadata: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    initialize_object_permission_policy()

    user_id = _safe_str(user_id, "anonymous")
    role = _safe_str(role, "public")
    action = _safe_str(action, "view").lower()
    route_path = _safe_str(route_path)
    metadata = metadata if isinstance(metadata, dict) else {}

    obj = normalize_ob_object(
        object_type=object_type,
        object_id=object_id,
        object_payload=object_payload,
    )

    role_family = _role_family(role, user_id)
    decision_data = _base_object_decision(
        user_id=user_id,
        role=role,
        role_family=role_family,
        action=action,
        obj=obj,
        route_path=route_path,
    )

    decision = decision_data.get("decision", "deny")

    response = {
        "ok": decision in {"allow", "step_up_required", "summary_only"},
        "pack": "108",
        "object_permission_id": _event_id("ob_object_perm"),
        "created_at": _utc_now(),
        "user_id": user_id,
        "role": role,
        "role_family": role_family,
        "route_path": route_path,
        "object_type": obj.get("object_type"),
        "object_id": obj.get("object_id"),
        "action": action,
        "decision": decision,
        "allowed": decision == "allow",
        "reason_code": decision_data.get("reason_code"),
        "requires_step_up": decision == "step_up_required" or decision_data.get("requires_step_up") is True,
        "requires_receipt": decision_data.get("requires_receipt") is True,
        "requires_archive_handoff": decision_data.get("requires_archive_handoff") is True,
        "requires_summary_only": decision == "summary_only",
        "required_actions": decision_data.get("required_actions", []),
        "object": obj,
        "metadata": _redact(metadata),
        "human_reason": decision_data.get("human_reason"),
        "soulaana_translation": decision_data.get("soulaana_translation"),
    }

    response = _redact(response)
    scan = _safe_scan(response)
    response["no_secret_leakage"] = scan.get("ok") is True
    response["leakage_scan"] = scan
    response["response_fingerprint"] = _fingerprint(response)

    event = _record_object_event({
        "user_id": user_id,
        "role": role,
        "role_family": role_family,
        "object_type": response.get("object_type"),
        "object_id": response.get("object_id"),
        "action": action,
        "decision": response.get("decision"),
        "reason_code": response.get("reason_code"),
        "response": response,
    })
    response["event"] = event

    return response


def _base_object_decision(
    *,
    user_id: str,
    role: str,
    role_family: str,
    action: str,
    obj: Dict[str, Any],
    route_path: str,
) -> Dict[str, Any]:
    object_type = obj.get("object_type", "route")
    object_id = obj.get("object_id", "")
    owner_user_id = obj.get("owner_user_id", "")

    mutation_actions = {"edit", "close", "delete", "approve", "grant", "override", "download", "export", "reveal", "enable"}
    is_mutation = action in mutation_actions

    if object_type == "symbol":
        if not object_id:
            return {
                "decision": "deny",
                "reason_code": "symbol_missing",
                "human_reason": "Symbol object is missing an identifier.",
                "soulaana_translation": "Soulaana: No symbol, no star chart.",
                "required_actions": ["provide_symbol"],
            }
        return {
            "decision": "allow",
            "reason_code": "symbol_object_allowed",
            "human_reason": "Symbol object access allowed.",
            "soulaana_translation": "Soulaana: Symbol object cleared.",
            "required_actions": ["continue_to_object"],
        }

    if object_type in {"position", "trade"}:
        if role_family == "owner":
            requires_receipt = is_mutation
            return {
                "decision": "allow",
                "reason_code": f"{object_type}_owner_access_allowed",
                "human_reason": f"Owner access allowed for {object_type} object.",
                "soulaana_translation": "Soulaana: Owner object key accepted.",
                "requires_receipt": requires_receipt,
                "required_actions": ["continue_to_object"],
            }

        if role_family == "beta":
            if owner_user_id and owner_user_id == user_id:
                if is_mutation:
                    return {
                        "decision": "step_up_required",
                        "reason_code": f"{object_type}_mutation_requires_step_up",
                        "human_reason": f"{object_type.title()} mutation requires step-up.",
                        "soulaana_translation": "Soulaana: You can touch your object, but this move needs a second key.",
                        "requires_step_up": True,
                        "requires_receipt": True,
                        "required_actions": ["complete_tower_step_up", "retry_object_action"],
                    }

                return {
                    "decision": "allow",
                    "reason_code": f"{object_type}_owner_match_allowed",
                    "human_reason": f"User may view their own {object_type} object.",
                    "soulaana_translation": "Soulaana: Object belongs to this lane. Cleared.",
                    "required_actions": ["continue_to_object"],
                }

            return {
                "decision": "deny",
                "reason_code": f"{object_type}_owner_mismatch",
                "human_reason": f"User cannot access another user's {object_type} object.",
                "soulaana_translation": "Soulaana: Wrong object lane. Door stays shut.",
                "required_actions": ["deny_object_access"],
            }

        return {
            "decision": "deny",
            "reason_code": f"{object_type}_role_not_allowed",
            "human_reason": f"Role cannot access {object_type} object.",
            "soulaana_translation": "Soulaana: This object is not for this role.",
            "required_actions": ["deny_object_access"],
        }

    if object_type in {"export", "report"}:
        if role_family != "owner":
            return {
                "decision": "deny",
                "reason_code": "export_owner_only",
                "human_reason": "Export/report objects are owner-only.",
                "soulaana_translation": "Soulaana: Export objects do not leave through beta doors.",
                "required_actions": ["deny_export_access"],
                "requires_receipt": True,
                "requires_archive_handoff": True,
            }

        return {
            "decision": "step_up_required",
            "reason_code": "export_requires_step_up",
            "human_reason": "Export/report object requires Tower step-up before access.",
            "soulaana_translation": "Soulaana: Export is a powerful object. Fresh verification first.",
            "requires_step_up": True,
            "requires_receipt": True,
            "requires_archive_handoff": True,
            "required_actions": ["complete_tower_step_up", "record_export_receipt", "create_archive_handoff"],
        }

    if object_type == "analysis":
        if role_family in {"owner", "admin", "beta"}:
            return {
                "decision": "summary_only",
                "reason_code": "analysis_summary_first",
                "human_reason": "Analysis object starts in summary-only mode.",
                "soulaana_translation": "Soulaana: Summary glass first. Details need another key.",
                "required_actions": ["show_redacted_summary", "request_reveal_if_needed"],
            }

        return {
            "decision": "deny",
            "reason_code": "analysis_role_not_allowed",
            "human_reason": "Role cannot access analysis object.",
            "soulaana_translation": "Soulaana: Analysis door is closed.",
            "required_actions": ["deny_object_access"],
        }

    if object_type in {"admin_panel", "tower_object"}:
        if role_family not in {"owner", "admin"}:
            return {
                "decision": "deny",
                "reason_code": "admin_object_owner_or_admin_only",
                "human_reason": "Admin/Tower object requires owner/admin role.",
                "soulaana_translation": "Soulaana: This is Tower glass. Not a beta hallway.",
                "required_actions": ["deny_admin_object_access"],
                "requires_receipt": True,
            }

        if is_mutation or action in {"view", "open"}:
            return {
                "decision": "step_up_required",
                "reason_code": "admin_object_requires_step_up",
                "human_reason": "Admin/Tower object requires step-up before access.",
                "soulaana_translation": "Soulaana: Admin object has a second lock.",
                "requires_step_up": True,
                "requires_receipt": True,
                "required_actions": ["complete_tower_step_up", "record_admin_receipt"],
            }

    if object_type == "mode":
        if str(object_id).lower() in {"live_manual", "live_hybrid", "live_automated"}:
            return {
                "decision": "deny",
                "reason_code": "live_mode_object_locked_until_compliance",
                "human_reason": "Live mode object is locked until compliance and production controls are ready.",
                "soulaana_translation": "Soulaana: Live mode remains sealed.",
                "required_actions": ["deny_live_mode_object_access"],
                "requires_receipt": True,
            }

        if role_family in {"owner", "admin", "beta"}:
            return {
                "decision": "allow",
                "reason_code": "mode_object_allowed",
                "human_reason": "Mode object access allowed.",
                "soulaana_translation": "Soulaana: Mode object cleared.",
                "required_actions": ["continue_to_object"],
            }

    if object_type == "route":
        return {
            "decision": "allow",
            "reason_code": "route_object_allowed",
            "human_reason": "Route object access allowed after route guard.",
            "soulaana_translation": "Soulaana: Route object cleared.",
            "required_actions": ["continue_to_object"],
        }

    return {
        "decision": "deny",
        "reason_code": "object_type_not_supported",
        "human_reason": "Object type is not supported by OB object permission tightening.",
        "soulaana_translation": "Soulaana: Unknown object. Door stays shut.",
        "required_actions": ["deny_object_access"],
    }


def check_symbol_permission(*, user_id: str, role: str, symbol: str, action: str = "view", metadata: Dict[str, Any] | None = None) -> Dict[str, Any]:
    return evaluate_ob_object_permission(
        user_id=user_id,
        role=role,
        object_type="symbol",
        object_id=symbol,
        action=action,
        metadata=metadata or {},
    )


def check_position_permission(
    *,
    user_id: str,
    role: str,
    position_id: str,
    action: str = "view",
    object_payload: Dict[str, Any] | None = None,
    metadata: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    return evaluate_ob_object_permission(
        user_id=user_id,
        role=role,
        object_type="position",
        object_id=position_id,
        action=action,
        object_payload=object_payload or {},
        metadata=metadata or {},
    )


def check_trade_permission(
    *,
    user_id: str,
    role: str,
    trade_id: str,
    action: str = "view",
    object_payload: Dict[str, Any] | None = None,
    metadata: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    return evaluate_ob_object_permission(
        user_id=user_id,
        role=role,
        object_type="trade",
        object_id=trade_id,
        action=action,
        object_payload=object_payload or {},
        metadata=metadata or {},
    )


def check_export_permission(
    *,
    user_id: str,
    role: str,
    export_id: str,
    action: str = "export",
    object_payload: Dict[str, Any] | None = None,
    metadata: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    return evaluate_ob_object_permission(
        user_id=user_id,
        role=role,
        object_type="export",
        object_id=export_id,
        action=action,
        object_payload=object_payload or {},
        metadata=metadata or {},
    )


def summarize_ob_object_permissions(limit: int = 80) -> Dict[str, Any]:
    initialize_object_permission_policy()
    events = _load_events()

    try:
        limit = int(limit)
    except Exception:
        limit = 80
    limit = max(1, min(limit, 300))

    by_decision: Dict[str, int] = {}
    by_object_type: Dict[str, int] = {}
    by_role_family: Dict[str, int] = {}
    by_reason: Dict[str, int] = {}

    for event in events:
        decision = event.get("decision", "unknown")
        object_type = event.get("object_type", "unknown")
        role_family = event.get("role_family", "unknown")
        reason = event.get("reason_code", "unknown")

        by_decision[decision] = by_decision.get(decision, 0) + 1
        by_object_type[object_type] = by_object_type.get(object_type, 0) + 1
        by_role_family[role_family] = by_role_family.get(role_family, 0) + 1
        by_reason[reason] = by_reason.get(reason, 0) + 1

    status = {
        "ok": True,
        "pack": "108",
        "policy_path": str(OBJECT_POLICY_PATH),
        "events_path": str(OBJECT_EVENTS_PATH),
        "status_path": str(OBJECT_STATUS_PATH),
        "panel_path": str(OBJECT_PANEL_PATH),
        "event_count": len(events),
        "by_decision": by_decision,
        "by_object_type": by_object_type,
        "by_role_family": by_role_family,
        "by_reason": by_reason,
        "recent_events": events[-limit:],
        "readiness_score": 100,
        "readiness_label": "OB object-level permission tightening ready",
        "human_reason": "OB object permission status loaded.",
        "soulaana_translation": "Soulaana: Object keys are active behind the route doors.",
    }

    status = _redact(status)
    scan = _safe_scan(status)
    status["no_secret_leakage"] = scan.get("ok") is True
    status["leakage_scan"] = scan
    status["status_fingerprint"] = _fingerprint(status)

    _write_json(OBJECT_STATUS_PATH, status)
    write_ob_object_permission_panel(status)
    return status


def write_ob_object_permission_panel(status: Dict[str, Any] | None = None) -> Dict[str, Any]:
    status = status if isinstance(status, dict) else _load_json(OBJECT_STATUS_PATH, {})
    events = status.get("recent_events", []) if isinstance(status.get("recent_events"), list) else []

    cards = []
    for event in events[-24:]:
        decision = event.get("decision", "unknown")
        object_type = event.get("object_type", "object")
        object_id = event.get("object_id", "")
        role_family = event.get("role_family", "role")
        cards.append(f"""
        <article class="card {decision}">
          <div class="eyebrow">{decision} · {object_type} · {role_family}</div>
          <h2>{object_id}</h2>
          <p>{event.get('reason_code', '')}</p>
        </article>
        """)

    html = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>The Tower · OB Object Permissions</title>
  <style>
    body {{
      margin: 0;
      min-height: 100vh;
      background: #080907;
      color: #f5ead2;
      font-family: Inter, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }}
    main {{
      max-width: 1180px;
      margin: 0 auto;
      padding: 42px 22px;
    }}
    .hero {{
      border: 1px solid rgba(220,183,94,.36);
      border-radius: 30px;
      padding: 30px;
      background: linear-gradient(135deg, rgba(75,48,18,.74), rgba(12,13,10,.96));
      box-shadow: 0 22px 90px rgba(0,0,0,.42);
    }}
    h1 {{
      margin: 0 0 10px;
      font-size: 34px;
      letter-spacing: -.04em;
    }}
    .hero p {{
      margin: 0;
      color: rgba(245,234,210,.76);
      line-height: 1.55;
    }}
    .stats {{
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 14px;
      margin: 20px 0;
    }}
    .stat {{
      border: 1px solid rgba(245,234,210,.14);
      border-radius: 20px;
      padding: 16px;
      background: rgba(255,255,255,.045);
    }}
    .stat b {{
      display: block;
      font-size: 24px;
    }}
    .grid {{
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 16px;
      margin-top: 18px;
    }}
    .card {{
      border: 1px solid rgba(245,234,210,.14);
      border-radius: 24px;
      padding: 18px;
      background: rgba(255,255,255,.045);
    }}
    .card.allow {{
      border-color: rgba(143,221,158,.34);
    }}
    .card.deny {{
      border-color: rgba(255,128,128,.50);
    }}
    .card.step_up_required, .card.summary_only {{
      border-color: rgba(220,183,94,.45);
    }}
    .eyebrow {{
      color: rgba(220,183,94,.84);
      text-transform: uppercase;
      letter-spacing: .12em;
      font-size: 11px;
      margin-bottom: 8px;
    }}
    h2 {{
      margin: 0 0 8px;
      font-size: 18px;
    }}
    .card p {{
      color: rgba(245,234,210,.72);
      line-height: 1.45;
    }}
  </style>
</head>
<body>
<main>
  <section class="hero">
    <h1>The Tower · OB Object Permissions</h1>
    <p>{status.get('human_reason', 'OB object permissions loaded.')}</p>
  </section>
  <section class="stats">
    <div class="stat"><b>{status.get('event_count', 0)}</b><span>Object Events</span></div>
    <div class="stat"><b>{status.get('by_decision', {}).get('allow', 0) if isinstance(status.get('by_decision'), dict) else 0}</b><span>Allowed</span></div>
    <div class="stat"><b>{status.get('by_decision', {}).get('deny', 0) if isinstance(status.get('by_decision'), dict) else 0}</b><span>Denied</span></div>
    <div class="stat"><b>{status.get('readiness_score', 0)}</b><span>Readiness</span></div>
  </section>
  <section class="grid">{''.join(cards)}</section>
</main>
</body>
</html>
"""
    OBJECT_PANEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    OBJECT_PANEL_PATH.write_text(html, encoding="utf-8")

    return {
        "ok": True,
        "decision": "ob_object_permission_panel_written",
        "path": str(OBJECT_PANEL_PATH),
        "human_reason": "OB object permission HTML panel written.",
        "soulaana_translation": "Soulaana: Object permission board posted.",
    }


def reset_ob_object_permissions_for_test() -> Dict[str, Any]:
    _save_events([])
    initialize_object_permission_policy()
    _write_json(OBJECT_STATUS_PATH, {
        "ok": True,
        "pack": "108",
        "event_count": 0,
        "human_reason": "OB object permission status reset for test.",
    })

    if OBJECT_PANEL_PATH.exists():
        try:
            OBJECT_PANEL_PATH.unlink()
        except Exception:
            pass

    return {
        "ok": True,
        "decision": "ob_object_permissions_reset_for_test",
        "events_reset": True,
        "policy_initialized": True,
        "soulaana_translation": "Soulaana: Object permissions reset for a clean test lane.",
    }
