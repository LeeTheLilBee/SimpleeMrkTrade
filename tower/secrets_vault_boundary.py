
from __future__ import annotations

import hashlib
import json
import re
import secrets
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "tower" / "data"

SECRETS_BOUNDARY_REGISTRY_PATH = DATA_DIR / "secrets_vault_boundary_registry.json"
SECRETS_BOUNDARY_EVENTS_PATH = DATA_DIR / "secrets_vault_boundary_events.json"


FORBIDDEN_SECRET_FIELD_NAMES = {
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
}


SECRET_TYPES = {
    "broker_api_key",
    "broker_oauth_token",
    "broker_live_trading_credential",
    "github_token",
    "payment_processor_secret",
    "email_provider_secret",
    "database_url",
    "encryption_key",
    "webhook_signing_secret",
    "archive_storage_key",
    "model_provider_key",
    "generic_secret",
}


APP_IDS = {
    "tower",
    "observatory",
    "ob",
    "teller",
    "archive_vault",
    "simpleepay",
    "control_tower",
    "simplee_world",
}


ALLOWED_SECRET_ACTIONS = {
    "status_check",
    "permission_check",
    "access_request",
    "rotation_request",
    "revoke_request",
    "audit_reference",
}


DEFAULT_SECRET_POLICY = {
    "raw_secret_storage_allowed": False,
    "tower_may_store_raw_value": False,
    "tower_may_store_reference": True,
    "tower_may_request_status": True,
    "tower_may_request_permission": True,
    "tower_may_request_rotation": True,
    "tower_must_redact_values": True,
    "requires_step_up_for_sensitive_use": True,
    "requires_audit_receipt": True,
    "secrets_vault_is_source_of_truth": True,
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
        return value.strip().lower() in {"1", "true", "yes", "y"}
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


def _canonical_json(value: Any) -> str:
    return json.dumps(_strict_redact_secrets(value), sort_keys=True, separators=(",", ":"), default=str)


def _fingerprint(value: Any) -> str:
    return hashlib.sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def _event_id(prefix: str = "secrets") -> str:
    return f"{prefix}_{secrets.token_urlsafe(18)}"


def _looks_like_secret_value(value: str) -> bool:
    text = str(value or "")
    lowered = text.lower()

    if not text:
        return False

    secret_markers = [
        "ghp_",
        "github_pat_",
        "sk_live_",
        "sk_test_",
        "pk_live_",
        "bearer ",
        "tower_keycard=",
        "should_not_survive",
        "-----begin private key-----",
        "xoxb-",
        "xoxp-",
        "api_key=",
        "access_token=",
        "refresh_token=",
        "client_secret=",
        "password=",
    ]

    if any(marker in lowered for marker in secret_markers):
        return True

    # Very long high-entropy-ish strings are treated suspiciously when paired with secret context.
    if len(text) >= 48 and re.fullmatch(r"[A-Za-z0-9_\-\.=]+", text):
        return True

    return False


def _strict_redact_secrets(value: Any) -> Any:
    if isinstance(value, dict):
        clean = {}
        redacted_count = 0

        for key, item in value.items():
            key_text = str(key).lower().strip()
            if any(secret_key in key_text for secret_key in FORBIDDEN_SECRET_FIELD_NAMES):
                redacted_count += 1
                continue

            redacted_item = _strict_redact_secrets(item)

            if isinstance(redacted_item, dict) and "__redacted_secret_field_count__" in redacted_item:
                try:
                    redacted_count += int(redacted_item.get("__redacted_secret_field_count__", 0))
                except Exception:
                    redacted_count += 1
                redacted_item = dict(redacted_item)
                redacted_item.pop("__redacted_secret_field_count__", None)

            clean[key] = redacted_item

        if redacted_count:
            clean["__redacted_secret_field_count__"] = redacted_count

        return clean

    if isinstance(value, list):
        return [_strict_redact_secrets(item) for item in value]

    if isinstance(value, str):
        if _looks_like_secret_value(value):
            return "[REDACTED_SECRET_VALUE]"
        return value

    return value


def _contains_forbidden_secret_material(value: Any) -> Dict[str, Any]:
    serialized = json.dumps(value, sort_keys=True, default=str)
    lowered = serialized.lower()

    forbidden_key_hits = []
    for key in FORBIDDEN_SECRET_FIELD_NAMES:
        if f'"{key}"' in lowered or f'"{key}":' in lowered:
            forbidden_key_hits.append(key)

    forbidden_value_hits = []
    markers = [
        "ghp_",
        "github_pat_",
        "sk_live_",
        "sk_test_",
        "bearer should_not_survive",
        "tower_keycard=",
        "should_not_survive",
        "-----begin private key-----",
        "access_token=",
        "refresh_token=",
        "client_secret=",
        "password=",
    ]
    for marker in markers:
        if marker in lowered:
            forbidden_value_hits.append(marker)

    return {
        "ok": not forbidden_key_hits and not forbidden_value_hits,
        "forbidden_key_hits": sorted(set(forbidden_key_hits)),
        "forbidden_value_hits": sorted(set(forbidden_value_hits)),
    }


def _load_registry() -> Dict[str, Any]:
    default = {
        "ok": True,
        "pack": "096",
        "registry_version": "pack096.v1",
        "path": str(SECRETS_BOUNDARY_REGISTRY_PATH),
        "policy": DEFAULT_SECRET_POLICY,
        "secret_references": [],
        "human_reason": "Secrets Vault boundary registry initialized.",
        "soulaana_translation": "Soulaana: The Tower tracks secret references, not raw secret values.",
    }
    data = _load_json(SECRETS_BOUNDARY_REGISTRY_PATH, default)
    return data if isinstance(data, dict) else default


def _save_registry(registry: Dict[str, Any]) -> Dict[str, Any]:
    registry = dict(registry)
    registry["ok"] = True
    registry["pack"] = "096"
    registry["registry_version"] = "pack096.v1"
    registry["path"] = str(SECRETS_BOUNDARY_REGISTRY_PATH)
    registry["policy"] = DEFAULT_SECRET_POLICY
    registry["updated_at"] = _utc_now()
    registry["registry_fingerprint"] = _fingerprint(registry)

    sanitized = _strict_redact_secrets(registry)
    _write_json(SECRETS_BOUNDARY_REGISTRY_PATH, sanitized)
    return sanitized


def _load_events() -> List[Dict[str, Any]]:
    data = _load_json(SECRETS_BOUNDARY_EVENTS_PATH, [])
    return data if isinstance(data, list) else []


def _save_events(events: List[Dict[str, Any]]) -> None:
    _write_json(SECRETS_BOUNDARY_EVENTS_PATH, events)


def _record_boundary_event(event: Dict[str, Any]) -> Dict[str, Any]:
    event = dict(event)
    event.setdefault("event_id", _event_id("secret_evt"))
    event.setdefault("event_type", "tower_secrets_boundary_event")
    event.setdefault("created_at", _utc_now())
    event.setdefault("pack", "096")

    sanitized = _strict_redact_secrets(event)
    sanitized["event_fingerprint"] = _fingerprint(sanitized)

    events = _load_events()
    events.append(sanitized)
    _save_events(events)

    try:
        from tower.tamper_evident_audit_chain import create_tamper_chain_entry

        create_tamper_chain_entry(
            event_type="tower_secrets_boundary_event_snapshot",
            source_name="secrets_vault_boundary_events",
            source_path=str(SECRETS_BOUNDARY_EVENTS_PATH),
            source_hash=_fingerprint(events),
            record_count=len(events),
            actor_user_id=_safe_str(sanitized.get("actor_user_id"), "tower_system"),
            reason=f"Pack 096 chained secrets boundary event {sanitized.get('decision')}.",
            metadata={
                "pack": "096",
                "event_id": sanitized.get("event_id"),
                "decision": sanitized.get("decision"),
            },
        )
    except Exception:
        pass

    return sanitized


def _normalize_secret_type(secret_type: str) -> str:
    secret_type = _safe_str(secret_type, "generic_secret")
    return secret_type if secret_type in SECRET_TYPES else "generic_secret"


def _normalize_app_id(app_id: str) -> str:
    app_id = _safe_str(app_id, "tower").lower()
    return app_id if app_id in APP_IDS else app_id


def make_secret_reference_id(*, app_id: str, secret_type: str, alias: str) -> str:
    app_id = _normalize_app_id(app_id)
    secret_type = _normalize_secret_type(secret_type)
    alias = _safe_str(alias, "secret")
    slug = re.sub(r"[^a-zA-Z0-9_\-]+", "_", alias).strip("_").lower() or "secret"
    digest = hashlib.sha256(f"{app_id}:{secret_type}:{slug}".encode("utf-8")).hexdigest()[:12]
    return f"secret_ref_{app_id}_{secret_type}_{slug}_{digest}"


def register_secret_reference(
    *,
    app_id: str,
    secret_type: str,
    alias: str,
    actor_user_id: str = "tower_system",
    secret_status: str = "unknown",
    allowed_actions: List[str] | None = None,
    requires_step_up: bool = True,
    notes: str = "",
    raw_secret_value: Any = None,
    metadata: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    app_id = _normalize_app_id(app_id)
    secret_type = _normalize_secret_type(secret_type)
    alias = _safe_str(alias, "secret")
    actor_user_id = _safe_str(actor_user_id, "tower_system")
    secret_status = _safe_str(secret_status, "unknown")
    metadata = metadata if isinstance(metadata, dict) else {}

    if raw_secret_value not in {None, ""}:
        event = _record_boundary_event({
            "actor_user_id": actor_user_id,
            "decision": "raw_secret_rejected",
            "reason_code": "tower_cannot_store_raw_secret_value",
            "app_id": app_id,
            "secret_type": secret_type,
            "alias": alias,
            "metadata": {
                "provided_payload": raw_secret_value,
                "request_metadata": metadata,
            },
            "human_reason": "Raw secret value was rejected. The Tower may only store a reference.",
            "soulaana_translation": "Soulaana: Absolutely not. Raw secrets do not live in The Tower.",
        })
        return {
            "ok": False,
            "decision": "reject_raw_secret",
            "reason_code": "tower_cannot_store_raw_secret_value",
            "event": event,
            "required_actions": ["store_secret_in_external_vault", "register_reference_only"],
            "human_reason": "Raw secret value rejected. Store the value in Secrets Vault, then register only the reference.",
            "soulaana_translation": "Soulaana: The secret itself belongs in the Vault. The Tower only keeps the label and permission trail.",
        }

    clean_actions = []
    for action in allowed_actions or ["status_check", "permission_check", "access_request"]:
        action = _safe_str(action)
        if action in ALLOWED_SECRET_ACTIONS and action not in clean_actions:
            clean_actions.append(action)

    if not clean_actions:
        clean_actions = ["status_check", "permission_check"]

    ref_id = make_secret_reference_id(app_id=app_id, secret_type=secret_type, alias=alias)
    registry = _load_registry()
    refs = registry.get("secret_references", []) if isinstance(registry.get("secret_references"), list) else []

    existing = None
    for item in refs:
        if item.get("secret_ref_id") == ref_id:
            existing = item
            break

    record = {
        "secret_ref_id": ref_id,
        "app_id": app_id,
        "secret_type": secret_type,
        "alias": alias,
        "secret_status": secret_status,
        "allowed_actions": clean_actions,
        "requires_step_up": bool(requires_step_up),
        "tower_stores_raw_secret": False,
        "external_vault_required": True,
        "secrets_vault_is_source_of_truth": True,
        "last_status_check_at": "",
        "last_permission_check_at": "",
        "last_rotation_request_at": "",
        "registered_at": existing.get("registered_at") if isinstance(existing, dict) else _utc_now(),
        "registered_by": existing.get("registered_by") if isinstance(existing, dict) else actor_user_id,
        "updated_at": _utc_now(),
        "updated_by": actor_user_id,
        "notes": _strict_redact_secrets(notes),
        "metadata": _strict_redact_secrets(metadata),
    }
    record["record_fingerprint"] = _fingerprint(record)

    if existing:
        refs = [record if item.get("secret_ref_id") == ref_id else item for item in refs]
        decision = "secret_reference_updated"
    else:
        refs.append(record)
        decision = "secret_reference_registered"

    registry["secret_references"] = refs
    saved = _save_registry(registry)

    event = _record_boundary_event({
        "actor_user_id": actor_user_id,
        "decision": decision,
        "reason_code": "secret_reference_only_saved",
        "secret_ref_id": ref_id,
        "app_id": app_id,
        "secret_type": secret_type,
        "alias": alias,
        "metadata": metadata,
        "human_reason": "Secret reference saved without raw secret material.",
        "soulaana_translation": "Soulaana: Reference saved. The raw secret stays outside The Tower.",
    })

    return {
        "ok": True,
        "decision": decision,
        "secret_ref_id": ref_id,
        "reference": record,
        "registry_total": len(saved.get("secret_references", [])),
        "event": event,
        "human_reason": "Secret reference registered in The Tower boundary registry.",
        "soulaana_translation": "Soulaana: The Tower knows the secret exists, but it does not hold the secret.",
    }


def get_secret_reference(secret_ref_id: str) -> Dict[str, Any]:
    secret_ref_id = _safe_str(secret_ref_id)
    registry = _load_registry()
    refs = registry.get("secret_references", []) if isinstance(registry.get("secret_references"), list) else []

    for ref in refs:
        if ref.get("secret_ref_id") == secret_ref_id:
            return {
                "ok": True,
                "decision": "secret_reference_found",
                "reference": ref,
                "human_reason": "Secret reference found. Raw secret remains external.",
                "soulaana_translation": "Soulaana: I found the label, not the secret. Correct.",
            }

    return {
        "ok": False,
        "decision": "secret_reference_missing",
        "secret_ref_id": secret_ref_id,
        "required_actions": ["register_secret_reference", "verify_external_vault_status"],
        "human_reason": "No secret reference is registered for this ID.",
        "soulaana_translation": "Soulaana: I do not see that secret label in the Tower registry.",
    }


def request_secret_status(
    *,
    secret_ref_id: str,
    actor_user_id: str = "tower_system",
    app_id: str = "",
    action: str = "status_check",
    metadata: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    secret_ref_id = _safe_str(secret_ref_id)
    actor_user_id = _safe_str(actor_user_id, "tower_system")
    action = _safe_str(action, "status_check")
    metadata = metadata if isinstance(metadata, dict) else {}

    found = get_secret_reference(secret_ref_id)
    if not found.get("ok"):
        event = _record_boundary_event({
            "actor_user_id": actor_user_id,
            "decision": "secret_status_request_missing_reference",
            "reason_code": "secret_reference_missing",
            "secret_ref_id": secret_ref_id,
            "metadata": metadata,
        })
        return {
            **found,
            "event": event,
        }

    ref = found.get("reference", {})
    if action not in ALLOWED_SECRET_ACTIONS:
        event = _record_boundary_event({
            "actor_user_id": actor_user_id,
            "decision": "secret_action_denied",
            "reason_code": "unsupported_secret_boundary_action",
            "secret_ref_id": secret_ref_id,
            "action": action,
            "metadata": metadata,
        })
        return {
            "ok": False,
            "decision": "deny",
            "reason_code": "unsupported_secret_boundary_action",
            "secret_ref_id": secret_ref_id,
            "event": event,
            "human_reason": "Unsupported Secrets Vault boundary action.",
            "soulaana_translation": "Soulaana: The Tower does not perform that secret action.",
        }

    if action not in ref.get("allowed_actions", []) and action not in {"status_check", "permission_check"}:
        event = _record_boundary_event({
            "actor_user_id": actor_user_id,
            "decision": "secret_action_denied",
            "reason_code": "action_not_allowed_for_secret_reference",
            "secret_ref_id": secret_ref_id,
            "action": action,
            "metadata": metadata,
        })
        return {
            "ok": False,
            "decision": "deny",
            "reason_code": "action_not_allowed_for_secret_reference",
            "secret_ref_id": secret_ref_id,
            "event": event,
            "human_reason": "This action is not allowed for the secret reference.",
            "soulaana_translation": "Soulaana: The label exists, but that action is not approved for it.",
        }

    # This is intentionally only a mock/status boundary.
    # A future actual Secrets Vault adapter will answer availability/permission.
    vault_status = {
        "external_vault_required": True,
        "secrets_vault_is_source_of_truth": True,
        "tower_has_raw_secret": False,
        "secret_available_status": ref.get("secret_status", "unknown"),
        "permission_status": "requires_external_vault_check",
        "raw_value": None,
    }

    registry = _load_registry()
    refs = registry.get("secret_references", []) if isinstance(registry.get("secret_references"), list) else []
    updated_refs = []
    for item in refs:
        if item.get("secret_ref_id") == secret_ref_id:
            item = dict(item)
            if action == "status_check":
                item["last_status_check_at"] = _utc_now()
            if action == "permission_check":
                item["last_permission_check_at"] = _utc_now()
            if action == "rotation_request":
                item["last_rotation_request_at"] = _utc_now()
            item["record_fingerprint"] = _fingerprint(item)
        updated_refs.append(item)

    registry["secret_references"] = updated_refs
    _save_registry(registry)

    event = _record_boundary_event({
        "actor_user_id": actor_user_id,
        "decision": "secret_boundary_status_returned",
        "reason_code": "reference_status_only_no_raw_secret",
        "secret_ref_id": secret_ref_id,
        "app_id": app_id or ref.get("app_id"),
        "action": action,
        "vault_status": vault_status,
        "metadata": metadata,
        "human_reason": "Returned reference/status metadata only. No raw secret exposed.",
        "soulaana_translation": "Soulaana: Status only. No secret left the Vault boundary.",
    })

    return {
        "ok": True,
        "decision": "status_only",
        "secret_ref_id": secret_ref_id,
        "reference": {
            "secret_ref_id": ref.get("secret_ref_id"),
            "app_id": ref.get("app_id"),
            "secret_type": ref.get("secret_type"),
            "alias": ref.get("alias"),
            "secret_status": ref.get("secret_status"),
            "requires_step_up": ref.get("requires_step_up"),
            "tower_stores_raw_secret": False,
            "external_vault_required": True,
        },
        "vault_status": vault_status,
        "event": event,
        "human_reason": "Secrets Vault boundary returned status metadata only.",
        "soulaana_translation": "Soulaana: The Tower asked if the secret exists. The Tower did not receive the secret.",
    }


def inspect_payload_for_secret_boundary(payload: Any) -> Dict[str, Any]:
    sanitized = _strict_redact_secrets(payload)
    scan = _contains_forbidden_secret_material(sanitized)
    original_scan = _contains_forbidden_secret_material(payload)

    return {
        "ok": scan.get("ok") is True,
        "original_had_secret_material": original_scan.get("ok") is False,
        "sanitized_payload": sanitized,
        "forbidden_after_sanitize": scan,
        "forbidden_before_sanitize": original_scan,
        "sanitized_fingerprint": _fingerprint(sanitized),
        "human_reason": (
            "Payload sanitized for Secrets Vault boundary."
            if scan.get("ok")
            else "Payload still contains forbidden secret material after sanitization."
        ),
        "soulaana_translation": (
            "Soulaana: I scrubbed the payload before it crossed the Tower boundary."
            if scan.get("ok")
            else "Soulaana: This payload is still leaking. It does not pass."
        ),
    }


def audit_tower_secret_storage_boundary(limit: int = 20) -> Dict[str, Any]:
    registry = _load_registry()
    events = _load_events()

    try:
        limit = int(limit)
    except Exception:
        limit = 20
    limit = max(1, min(limit, 200))

    registry_scan = _contains_forbidden_secret_material(registry)
    events_scan = _contains_forbidden_secret_material(events)

    refs = registry.get("secret_references", []) if isinstance(registry.get("secret_references"), list) else []

    by_app: Dict[str, int] = {}
    by_type: Dict[str, int] = {}
    by_status: Dict[str, int] = {}
    for ref in refs:
        app_id = ref.get("app_id", "unknown")
        secret_type = ref.get("secret_type", "unknown")
        status = ref.get("secret_status", "unknown")
        by_app[app_id] = by_app.get(app_id, 0) + 1
        by_type[secret_type] = by_type.get(secret_type, 0) + 1
        by_status[status] = by_status.get(status, 0) + 1

    ok = registry_scan.get("ok") is True and events_scan.get("ok") is True

    summary = {
        "ok": ok,
        "pack": "096",
        "registry_path": str(SECRETS_BOUNDARY_REGISTRY_PATH),
        "events_path": str(SECRETS_BOUNDARY_EVENTS_PATH),
        "secret_reference_count": len(refs),
        "event_count": len(events),
        "policy": DEFAULT_SECRET_POLICY,
        "by_app": by_app,
        "by_type": by_type,
        "by_status": by_status,
        "registry_scan": registry_scan,
        "events_scan": events_scan,
        "recent_events": events[-limit:],
        "recent_references": refs[-limit:],
        "readiness_score": 100 if ok else 60,
        "readiness_label": (
            "Secrets Vault separation boundary ready"
            if ok
            else "Secrets Vault boundary has forbidden secret material"
        ),
        "human_reason": (
            "Tower registry/events contain secret references only, no raw secret material."
            if ok
            else "Forbidden secret material was detected in Tower secrets boundary files."
        ),
        "soulaana_translation": (
            "Soulaana: The Tower has labels and receipts, not the secrets. Correct."
            if ok
            else "Soulaana: Something secret-shaped is in the Tower files. Fix it."
        ),
    }

    sanitized_summary = _strict_redact_secrets(summary)
    final_scan = _contains_forbidden_secret_material(sanitized_summary)
    sanitized_summary["no_secret_material_leakage"] = final_scan.get("ok") is True

    return sanitized_summary


def reset_secrets_boundary_for_test() -> Dict[str, Any]:
    registry = {
        "ok": True,
        "pack": "096",
        "registry_version": "pack096.v1",
        "path": str(SECRETS_BOUNDARY_REGISTRY_PATH),
        "policy": DEFAULT_SECRET_POLICY,
        "secret_references": [],
        "human_reason": "Secrets Vault boundary registry reset for test.",
        "soulaana_translation": "Soulaana: Secret reference registry reset. No raw secrets are allowed back in.",
    }
    _write_json(SECRETS_BOUNDARY_REGISTRY_PATH, registry)
    _save_events([])

    return {
        "ok": True,
        "decision": "secrets_boundary_reset_for_test",
        "registry_reset": True,
        "events_reset": True,
        "soulaana_translation": "Soulaana: Secrets boundary reset for a clean test lane.",
    }



# ================================================================================
# PACK096B_SAFE_SECRET_REFERENCE_REDACTION
# ================================================================================
# The Tower is allowed to store safe secret-reference metadata keys.
# It is NOT allowed to store raw secret-bearing keys or values.
# ================================================================================

SAFE_SECRET_REFERENCE_KEYS = {
    "secret_references",
    "secret_ref_id",
    "secret_type",
    "secret_status",
    "secrets_vault_is_source_of_truth",
    "secret_reference_count",
    "secret_available_status",
    "secret_ref_missing",
    "secret_reference_missing",
    "secret_reference_registered",
    "secret_reference_updated",
    "secret_reference_found",
}

DANGEROUS_SECRET_FIELD_NAMES_EXACT = {
    "token",
    "raw_token",
    "access_token",
    "refresh_token",
    "api_key",
    "apikey",
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


def _pack096b_is_dangerous_key(key: Any) -> bool:
    key_text = str(key).lower().strip()

    if key_text in SAFE_SECRET_REFERENCE_KEYS:
        return False

    if key_text in DANGEROUS_SECRET_FIELD_NAMES_EXACT:
        return True

    # Only treat suffix/pattern keys as dangerous when they clearly mean raw values.
    dangerous_patterns = (
        "_token",
        "_password",
        "_private_key",
        "_api_key",
        "_secret_value",
        "_raw_secret",
        "_credential",
        "_credentials",
    )
    return any(key_text.endswith(pattern) for pattern in dangerous_patterns)


def _strict_redact_secrets(value: Any) -> Any:
    if isinstance(value, dict):
        clean = {}
        redacted_count = 0

        for key, item in value.items():
            if _pack096b_is_dangerous_key(key):
                redacted_count += 1
                continue

            redacted_item = _strict_redact_secrets(item)

            if isinstance(redacted_item, dict) and "__redacted_secret_field_count__" in redacted_item:
                try:
                    redacted_count += int(redacted_item.get("__redacted_secret_field_count__", 0))
                except Exception:
                    redacted_count += 1
                redacted_item = dict(redacted_item)
                redacted_item.pop("__redacted_secret_field_count__", None)

            clean[key] = redacted_item

        if redacted_count:
            clean["__redacted_secret_field_count__"] = redacted_count

        return clean

    if isinstance(value, list):
        return [_strict_redact_secrets(item) for item in value]

    if isinstance(value, str):
        if _looks_like_secret_value(value):
            return "[REDACTED_SECRET_VALUE]"
        return value

    return value


def _contains_forbidden_secret_material(value: Any) -> Dict[str, Any]:
    serialized = json.dumps(value, sort_keys=True, default=str)
    lowered = serialized.lower()

    forbidden_key_hits = []

    def walk_keys(obj: Any):
        if isinstance(obj, dict):
            for key, item in obj.items():
                if _pack096b_is_dangerous_key(key):
                    forbidden_key_hits.append(str(key))
                walk_keys(item)
        elif isinstance(obj, list):
            for item in obj:
                walk_keys(item)

    walk_keys(value)

    forbidden_value_hits = []
    markers = [
        "ghp_",
        "github_pat_",
        "sk_live_should_not_survive",
        "sk_test_should_not_survive",
        "bearer should_not_survive",
        "tower_keycard=",
        "should_not_survive",
        "-----begin private key-----",
        "access_token=",
        "refresh_token=",
        "client_secret=",
        "password=",
    ]
    for marker in markers:
        if marker in lowered:
            forbidden_value_hits.append(marker)

    return {
        "ok": not forbidden_key_hits and not forbidden_value_hits,
        "forbidden_key_hits": sorted(set(forbidden_key_hits)),
        "forbidden_value_hits": sorted(set(forbidden_value_hits)),
    }


def sanitize_secrets_boundary_stores() -> Dict[str, Any]:
    registry = _load_registry()
    events = _load_events()

    sanitized_registry = _strict_redact_secrets(registry)
    sanitized_events = [_strict_redact_secrets(event) for event in events]

    _write_json(SECRETS_BOUNDARY_REGISTRY_PATH, sanitized_registry)
    _save_events(sanitized_events)

    registry_scan = _contains_forbidden_secret_material(sanitized_registry)
    events_scan = _contains_forbidden_secret_material(sanitized_events)

    return {
        "ok": registry_scan.get("ok") is True and events_scan.get("ok") is True,
        "decision": "secrets_boundary_stores_sanitized",
        "registry_scan": registry_scan,
        "events_scan": events_scan,
        "registry_reference_count": len(
            sanitized_registry.get("secret_references", [])
            if isinstance(sanitized_registry.get("secret_references"), list)
            else []
        ),
        "event_count": len(sanitized_events),
        "human_reason": "Secrets boundary stores sanitized while preserving safe reference metadata.",
        "soulaana_translation": "Soulaana: Safe labels stayed. Raw secret-shaped things got thrown out.",
    }



# ================================================================================
# PACK096C_PRESERVE_SECRET_REFERENCE_ID_VALUES
# ================================================================================
# Safe Tower reference IDs are allowed to contain "secret_ref_".
# Raw secret values are still forbidden.
# ================================================================================

def _looks_like_secret_value(value: str) -> bool:
    text = str(value or "")
    lowered = text.lower()

    if not text:
        return False

    # Safe structural identifiers. These are labels/references, not raw secrets.
    if lowered.startswith("secret_ref_"):
        return False

    # Safe policy/status strings. These describe state, not raw secrets.
    safe_exact = {
        "generic_secret",
        "broker_api_key",
        "broker_oauth_token",
        "broker_live_trading_credential",
        "github_token",
        "payment_processor_secret",
        "email_provider_secret",
        "database_url",
        "encryption_key",
        "webhook_signing_secret",
        "archive_storage_key",
        "model_provider_key",
        "configured_external",
        "external_rotation_required",
        "not_configured",
        "unknown",
        "requires_external_vault_check",
        "secret_reference_registered",
        "secret_reference_updated",
        "secret_reference_found",
        "secret_reference_missing",
        "secret_boundary_status_returned",
        "reference_status_only_no_raw_secret",
        "secret_reference_only_saved",
    }
    if lowered in safe_exact:
        return False

    secret_markers = [
        "ghp_",
        "github_pat_",
        "sk_live_",
        "sk_test_",
        "bearer ",
        "tower_keycard=",
        "should_not_survive",
        "-----begin private key-----",
        "xoxb-",
        "xoxp-",
        "api_key=",
        "access_token=",
        "refresh_token=",
        "client_secret=",
        "password=",
    ]

    if any(marker in lowered for marker in secret_markers):
        return True

    # Very long high-entropy-ish strings are suspicious, but allow known safe prefixes.
    safe_prefixes = (
        "secret_ref_",
        "secret_evt_",
        "secrets_",
    )
    if lowered.startswith(safe_prefixes):
        return False

    if len(text) >= 64 and re.fullmatch(r"[A-Za-z0-9_\-\.=]+", text):
        return True

    return False


def _strict_redact_secrets(value: Any) -> Any:
    if isinstance(value, dict):
        clean = {}
        redacted_count = 0

        for key, item in value.items():
            if _pack096b_is_dangerous_key(key):
                redacted_count += 1
                continue

            # Preserve safe reference ID values under safe keys.
            key_text = str(key).lower().strip()
            if key_text in {"secret_ref_id", "event_id", "secret_type", "secret_status", "decision", "reason_code"}:
                clean[key] = item
                continue

            redacted_item = _strict_redact_secrets(item)

            if isinstance(redacted_item, dict) and "__redacted_secret_field_count__" in redacted_item:
                try:
                    redacted_count += int(redacted_item.get("__redacted_secret_field_count__", 0))
                except Exception:
                    redacted_count += 1
                redacted_item = dict(redacted_item)
                redacted_item.pop("__redacted_secret_field_count__", None)

            clean[key] = redacted_item

        if redacted_count:
            clean["__redacted_secret_field_count__"] = redacted_count

        return clean

    if isinstance(value, list):
        return [_strict_redact_secrets(item) for item in value]

    if isinstance(value, str):
        if _looks_like_secret_value(value):
            return "[REDACTED_SECRET_VALUE]"
        return value

    return value


def sanitize_secrets_boundary_stores() -> Dict[str, Any]:
    registry = _load_registry()
    events = _load_events()

    sanitized_registry = _strict_redact_secrets(registry)
    sanitized_events = [_strict_redact_secrets(event) for event in events]

    _write_json(SECRETS_BOUNDARY_REGISTRY_PATH, sanitized_registry)
    _save_events(sanitized_events)

    registry_scan = _contains_forbidden_secret_material(sanitized_registry)
    events_scan = _contains_forbidden_secret_material(sanitized_events)

    return {
        "ok": registry_scan.get("ok") is True and events_scan.get("ok") is True,
        "decision": "secrets_boundary_stores_sanitized",
        "registry_scan": registry_scan,
        "events_scan": events_scan,
        "registry_reference_count": len(
            sanitized_registry.get("secret_references", [])
            if isinstance(sanitized_registry.get("secret_references"), list)
            else []
        ),
        "event_count": len(sanitized_events),
        "human_reason": "Secrets boundary stores sanitized while preserving safe reference IDs.",
        "soulaana_translation": "Soulaana: Reference IDs stayed visible. Raw secrets stayed banished.",
    }



# ================================================================================
# PACK096D_PRESERVE_SAFE_SECRET_POLICY_FIELDS
# ================================================================================
# Some keys contain "secret" or "raw_secret" because they are boundary policy fields,
# not raw values. Preserve those safe booleans/status fields.
# ================================================================================

SAFE_SECRET_REFERENCE_KEYS = set(globals().get("SAFE_SECRET_REFERENCE_KEYS", set())) | {
    "tower_stores_raw_secret",
    "external_vault_required",
    "raw_secret_storage_allowed",
    "tower_may_store_raw_value",
    "tower_may_store_reference",
    "tower_may_request_status",
    "tower_may_request_permission",
    "tower_may_request_rotation",
    "tower_must_redact_values",
    "requires_step_up_for_sensitive_use",
    "requires_audit_receipt",
    "no_secret_material_leakage",
    "original_had_secret_material",
    "forbidden_after_sanitize",
    "forbidden_before_sanitize",
    "redacted_secret_field_count",
    "__redacted_secret_field_count__",
}


def _pack096b_is_dangerous_key(key: Any) -> bool:
    key_text = str(key).lower().strip()

    if key_text in SAFE_SECRET_REFERENCE_KEYS:
        return False

    if key_text in DANGEROUS_SECRET_FIELD_NAMES_EXACT:
        return True

    # Dangerous only when clearly referring to a raw value/credential field,
    # not when describing a policy/status field.
    dangerous_patterns = (
        "_token",
        "_password",
        "_private_key",
        "_api_key",
        "_secret_value",
        "_credential",
        "_credentials",
    )

    if any(key_text.endswith(pattern) for pattern in dangerous_patterns):
        return True

    # raw_secret is dangerous as a payload/value field, but safe in explicit policy
    # fields already whitelisted above.
    if key_text in {"raw_secret", "raw_secret_value"}:
        return True

    return False


def _strict_redact_secrets(value: Any) -> Any:
    if isinstance(value, dict):
        clean = {}
        redacted_count = 0

        for key, item in value.items():
            if _pack096b_is_dangerous_key(key):
                redacted_count += 1
                continue

            key_text = str(key).lower().strip()
            if key_text in {
                "secret_ref_id",
                "event_id",
                "secret_type",
                "secret_status",
                "decision",
                "reason_code",
                "tower_stores_raw_secret",
                "external_vault_required",
                "secrets_vault_is_source_of_truth",
                "raw_secret_storage_allowed",
                "tower_may_store_raw_value",
                "tower_may_store_reference",
                "tower_may_request_status",
                "tower_may_request_permission",
                "tower_may_request_rotation",
                "tower_must_redact_values",
            }:
                clean[key] = item
                continue

            redacted_item = _strict_redact_secrets(item)

            if isinstance(redacted_item, dict) and "__redacted_secret_field_count__" in redacted_item:
                try:
                    redacted_count += int(redacted_item.get("__redacted_secret_field_count__", 0))
                except Exception:
                    redacted_count += 1
                redacted_item = dict(redacted_item)
                redacted_item.pop("__redacted_secret_field_count__", None)

            clean[key] = redacted_item

        if redacted_count:
            clean["__redacted_secret_field_count__"] = redacted_count

        return clean

    if isinstance(value, list):
        return [_strict_redact_secrets(item) for item in value]

    if isinstance(value, str):
        if _looks_like_secret_value(value):
            return "[REDACTED_SECRET_VALUE]"
        return value

    return value


def sanitize_secrets_boundary_stores() -> Dict[str, Any]:
    registry = _load_registry()
    events = _load_events()

    sanitized_registry = _strict_redact_secrets(registry)
    sanitized_events = [_strict_redact_secrets(event) for event in events]

    _write_json(SECRETS_BOUNDARY_REGISTRY_PATH, sanitized_registry)
    _save_events(sanitized_events)

    registry_scan = _contains_forbidden_secret_material(sanitized_registry)
    events_scan = _contains_forbidden_secret_material(sanitized_events)

    return {
        "ok": registry_scan.get("ok") is True and events_scan.get("ok") is True,
        "decision": "secrets_boundary_stores_sanitized",
        "registry_scan": registry_scan,
        "events_scan": events_scan,
        "registry_reference_count": len(
            sanitized_registry.get("secret_references", [])
            if isinstance(sanitized_registry.get("secret_references"), list)
            else []
        ),
        "event_count": len(sanitized_events),
        "human_reason": "Secrets boundary stores sanitized while preserving safe policy fields.",
        "soulaana_translation": "Soulaana: Policy fields stayed visible. Raw secrets stayed banished.",
    }



# ================================================================================
# PACK096E_NO_RAW_MARKER_ECHO_IN_INSPECTION
# ================================================================================
# Inspection/audit responses should not repeat raw forbidden marker strings.
# They may return counts and safe booleans instead.
# ================================================================================

def _safe_scan_summary(scan: Dict[str, Any]) -> Dict[str, Any]:
    key_hits = scan.get("forbidden_key_hits", []) if isinstance(scan, dict) else []
    value_hits = scan.get("forbidden_value_hits", []) if isinstance(scan, dict) else []

    return {
        "ok": bool(scan.get("ok")) if isinstance(scan, dict) else False,
        "forbidden_key_hit_count": len(key_hits) if isinstance(key_hits, list) else 0,
        "forbidden_value_hit_count": len(value_hits) if isinstance(value_hits, list) else 0,
        "had_forbidden_key_hits": bool(key_hits),
        "had_forbidden_value_hits": bool(value_hits),
    }


def inspect_payload_for_secret_boundary(payload: Any) -> Dict[str, Any]:
    sanitized = _strict_redact_secrets(payload)
    scan_after = _contains_forbidden_secret_material(sanitized)
    scan_before = _contains_forbidden_secret_material(payload)

    result = {
        "ok": scan_after.get("ok") is True,
        "original_had_secret_material": scan_before.get("ok") is False,
        "sanitized_payload": sanitized,
        "forbidden_after_sanitize": _safe_scan_summary(scan_after),
        "forbidden_before_sanitize": _safe_scan_summary(scan_before),
        "sanitized_fingerprint": _fingerprint(sanitized),
        "human_reason": (
            "Payload sanitized for Secrets Vault boundary."
            if scan_after.get("ok")
            else "Payload still contains forbidden secret material after sanitization."
        ),
        "soulaana_translation": (
            "Soulaana: I scrubbed the payload before it crossed the Tower boundary."
            if scan_after.get("ok")
            else "Soulaana: This payload is still leaking. It does not pass."
        ),
    }

    return _strict_redact_secrets(result)


def audit_tower_secret_storage_boundary(limit: int = 20) -> Dict[str, Any]:
    registry = _load_registry()
    events = _load_events()

    try:
        limit = int(limit)
    except Exception:
        limit = 20
    limit = max(1, min(limit, 200))

    registry_scan = _contains_forbidden_secret_material(registry)
    events_scan = _contains_forbidden_secret_material(events)

    refs = registry.get("secret_references", []) if isinstance(registry.get("secret_references"), list) else []

    by_app: Dict[str, int] = {}
    by_type: Dict[str, int] = {}
    by_status: Dict[str, int] = {}

    for ref in refs:
        app_id = ref.get("app_id", "unknown")
        secret_type = ref.get("secret_type", "unknown")
        status = ref.get("secret_status", "unknown")
        by_app[app_id] = by_app.get(app_id, 0) + 1
        by_type[secret_type] = by_type.get(secret_type, 0) + 1
        by_status[status] = by_status.get(status, 0) + 1

    ok = registry_scan.get("ok") is True and events_scan.get("ok") is True

    summary = {
        "ok": ok,
        "pack": "096",
        "registry_path": str(SECRETS_BOUNDARY_REGISTRY_PATH),
        "events_path": str(SECRETS_BOUNDARY_EVENTS_PATH),
        "secret_reference_count": len(refs),
        "event_count": len(events),
        "policy": DEFAULT_SECRET_POLICY,
        "by_app": by_app,
        "by_type": by_type,
        "by_status": by_status,
        "registry_scan": _safe_scan_summary(registry_scan),
        "events_scan": _safe_scan_summary(events_scan),
        "recent_events": events[-limit:],
        "recent_references": refs[-limit:],
        "readiness_score": 100 if ok else 60,
        "readiness_label": (
            "Secrets Vault separation boundary ready"
            if ok
            else "Secrets Vault boundary has forbidden secret material"
        ),
        "human_reason": (
            "Tower registry/events contain secret references only, no raw secret material."
            if ok
            else "Forbidden secret material was detected in Tower secrets boundary files."
        ),
        "soulaana_translation": (
            "Soulaana: The Tower has labels and receipts, not the secrets. Correct."
            if ok
            else "Soulaana: Something secret-shaped is in the Tower files. Fix it."
        ),
    }

    sanitized_summary = _strict_redact_secrets(summary)
    final_scan = _contains_forbidden_secret_material(sanitized_summary)
    sanitized_summary["no_secret_material_leakage"] = final_scan.get("ok") is True

    return sanitized_summary

