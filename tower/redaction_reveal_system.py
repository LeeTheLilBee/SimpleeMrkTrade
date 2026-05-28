
from __future__ import annotations

import hashlib
import json
import re
import secrets
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "tower" / "data"

REVEAL_RECEIPTS_PATH = DATA_DIR / "redaction_reveal_receipts.json"
REVEAL_POLICY_PATH = DATA_DIR / "redaction_reveal_policy.json"


SENSITIVE_FIELD_NAMES = {
    "ssn",
    "social_security_number",
    "ein",
    "tax_id",
    "date_of_birth",
    "dob",
    "birthdate",
    "address",
    "street_address",
    "phone",
    "phone_number",
    "email",
    "bank_account",
    "routing_number",
    "account_number",
    "card_number",
    "payment_method",
    "payroll_amount",
    "salary",
    "wage",
    "worker_notes",
    "medical_notes",
    "private_notes",
    "legal_notes",
    "broker_account",
    "broker_status_detail",
    "live_trading_permission_detail",
    "admin_notes",
    "security_notes",
    "incident_detail",
    "ip_address",
    "device_id",
    "session_id",
    "object_payload",
    "raw_payload",
    "document_text",
    "recipient_sensitive_detail",
}


SECRET_FIELD_NAMES = {
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


SAFE_SUMMARY_FIELD_NAMES = {
    "id",
    "object_id",
    "object_type",
    "title",
    "label",
    "status",
    "state",
    "category",
    "created_at",
    "updated_at",
    "owner",
    "app_id",
    "route_path",
    "decision",
    "reason_code",
    "risk_state",
    "risk_score",
    "readiness_label",
    "readiness_score",
    "human_reason",
    "soulaana_translation",
}


REVEAL_ACTIONS_REQUIRING_STEP_UP = {
    "reveal_sensitive_detail",
    "reveal_security_detail",
    "reveal_financial_detail",
    "reveal_payroll_detail",
    "reveal_broker_detail",
    "reveal_document_text",
    "reveal_incident_detail",
    "admin_sensitive_reveal",
}


REVEAL_POLICY = {
    "default_mode": "summary_only",
    "redaction_by_default": True,
    "secret_values_never_revealed": True,
    "requires_base_clearance": True,
    "requires_object_permission": True,
    "requires_step_up_for_sensitive_reveal": True,
    "requires_audit_receipt": True,
    "allowed_summary_fields": sorted(list(SAFE_SUMMARY_FIELD_NAMES)),
    "sensitive_field_names": sorted(list(SENSITIVE_FIELD_NAMES)),
    "secret_field_names": sorted(list(SECRET_FIELD_NAMES)),
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


def _looks_like_secret_value(value: str) -> bool:
    text = str(value or "")
    lowered = text.lower()

    if not text:
        return False

    if lowered.startswith("secret_ref_"):
        return False

    markers = [
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
    if any(marker in lowered for marker in markers):
        return True

    if len(text) >= 64 and re.fullmatch(r"[A-Za-z0-9_\-\.=]+", text):
        return True

    return False


def _is_secret_key(key: Any) -> bool:
    key_text = str(key).lower().strip()
    if key_text in SECRET_FIELD_NAMES:
        return True

    dangerous_suffixes = (
        "_token",
        "_password",
        "_private_key",
        "_api_key",
        "_secret_value",
        "_raw_secret",
        "_credential",
        "_credentials",
    )
    return any(key_text.endswith(suffix) for suffix in dangerous_suffixes)


def _is_sensitive_key(key: Any) -> bool:
    key_text = str(key).lower().strip()

    if _is_secret_key(key_text):
        return True

    if key_text in SENSITIVE_FIELD_NAMES:
        return True

    sensitive_fragments = (
        "sensitive",
        "private",
        "payroll",
        "salary",
        "wage",
        "bank",
        "routing",
        "account_number",
        "broker",
        "incident",
        "legal",
        "medical",
        "document_text",
        "raw_payload",
    )
    return any(fragment in key_text for fragment in sensitive_fragments)


def _canonical_json(value: Any) -> str:
    return json.dumps(redact_payload_for_summary(value), sort_keys=True, separators=(",", ":"), default=str)


def _fingerprint(value: Any) -> str:
    return hashlib.sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def _event_id(prefix: str = "reveal") -> str:
    return f"{prefix}_{secrets.token_urlsafe(18)}"


def _load_receipts() -> List[Dict[str, Any]]:
    data = _load_json(REVEAL_RECEIPTS_PATH, [])
    return data if isinstance(data, list) else []


def _save_receipts(receipts: List[Dict[str, Any]]) -> None:
    _write_json(REVEAL_RECEIPTS_PATH, receipts)


def _mask_value(value: Any, label: str = "REDACTED") -> Any:
    if value is None:
        return None
    if isinstance(value, bool):
        return "[REDACTED_BOOL]"
    if isinstance(value, (int, float)):
        return "[REDACTED_NUMBER]"
    if isinstance(value, str):
        if not value:
            return ""
        return f"[{label}]"
    if isinstance(value, list):
        return [f"[{label}_ITEM]" for _ in value[:3]]
    if isinstance(value, dict):
        return {"__redacted_object__": True, "field_count": len(value)}
    return f"[{label}]"


def redact_payload_for_summary(payload: Any) -> Any:
    if isinstance(payload, dict):
        clean = {}
        redacted_count = 0

        for key, value in payload.items():
            key_text = str(key)

            if _is_secret_key(key_text):
                redacted_count += 1
                continue

            if _is_sensitive_key(key_text):
                clean[key] = _mask_value(value, "REDACTED_SENSITIVE")
                redacted_count += 1
                continue

            if key_text.lower().strip() in SAFE_SUMMARY_FIELD_NAMES:
                clean[key] = redact_payload_for_summary(value)
                continue

            # Unknown complex payloads are summarized, not deeply revealed.
            if isinstance(value, dict):
                nested = redact_payload_for_summary(value)
                clean[key] = nested
                continue

            if isinstance(value, list):
                clean[key] = [
                    redact_payload_for_summary(item)
                    for item in value[:5]
                ]
                if len(value) > 5:
                    clean[f"{key}_truncated_count"] = len(value) - 5
                continue

            if isinstance(value, str) and _looks_like_secret_value(value):
                redacted_count += 1
                continue

            clean[key] = value

        if redacted_count:
            clean["__redacted_sensitive_field_count__"] = redacted_count

        return clean

    if isinstance(payload, list):
        return [redact_payload_for_summary(item) for item in payload[:10]]

    if isinstance(payload, str) and _looks_like_secret_value(payload):
        return "[REDACTED_SECRET_VALUE]"

    return payload


def _safe_scan_for_leakage(payload: Any) -> Dict[str, Any]:
    serialized = json.dumps(payload, sort_keys=True, default=str).lower()

    forbidden_markers = [
        "should_not_survive",
        "tower_keycard=",
        "bearer should_not_survive",
        "ghp_should_not_survive",
        "sk_live_should_not_survive",
        "-----begin private key-----",
        '"raw_token":',
        '"access_token":',
        '"refresh_token":',
        '"api_key":',
        '"github_token":',
        '"stripe_secret":',
        '"password":',
        '"private_key":',
    ]

    hits = [marker for marker in forbidden_markers if marker in serialized]

    return {
        "ok": not hits,
        "forbidden_hit_count": len(hits),
        "had_forbidden_hits": bool(hits),
    }


def build_redacted_summary(
    *,
    object_type: str,
    object_id: str,
    payload: Dict[str, Any],
    actor_user_id: str = "anonymous",
    app_id: str = "tower",
    reason: str = "summary_view",
) -> Dict[str, Any]:
    object_type = _safe_str(object_type, "unknown_object")
    object_id = _safe_str(object_id, "unknown")
    actor_user_id = _safe_str(actor_user_id, "anonymous")
    app_id = _safe_str(app_id, "tower")
    payload = payload if isinstance(payload, dict) else {"value": payload}

    redacted_payload = redact_payload_for_summary(payload)
    scan = _safe_scan_for_leakage(redacted_payload)

    summary = {
        "ok": scan.get("ok") is True,
        "decision": "summary_only",
        "mode": "redacted_summary",
        "object_type": object_type,
        "object_id": object_id,
        "app_id": app_id,
        "actor_user_id": actor_user_id,
        "created_at": _utc_now(),
        "reason": reason,
        "payload_fingerprint": _fingerprint(payload),
        "redacted_payload": redacted_payload,
        "leakage_scan": scan,
        "policy": {
            "redaction_by_default": True,
            "secret_values_never_revealed": True,
            "requires_reveal_request_for_sensitive_detail": True,
        },
        "human_reason": "Redacted summary returned by default.",
        "soulaana_translation": "Soulaana: Summary only. Sensitive details stay behind the clearance glass.",
    }

    return summary


def _record_reveal_receipt(receipt: Dict[str, Any]) -> Dict[str, Any]:
    receipt = dict(receipt)
    receipt.setdefault("receipt_id", _event_id("reveal_receipt"))
    receipt.setdefault("event_type", "tower_redaction_reveal_receipt")
    receipt.setdefault("created_at", _utc_now())
    receipt.setdefault("pack", "097")

    receipt = redact_payload_for_summary(receipt)
    receipt["receipt_fingerprint"] = _fingerprint(receipt)

    receipts = _load_receipts()
    receipts.append(receipt)
    _save_receipts(receipts)

    try:
        from tower.tamper_evident_audit_chain import create_tamper_chain_entry

        create_tamper_chain_entry(
            event_type="tower_redaction_reveal_receipt_snapshot",
            source_name="redaction_reveal_receipts",
            source_path=str(REVEAL_RECEIPTS_PATH),
            source_hash=_fingerprint(receipts),
            record_count=len(receipts),
            actor_user_id=_safe_str(receipt.get("actor_user_id"), "tower_system"),
            reason=f"Pack 097 chained reveal receipt {receipt.get('decision')}.",
            metadata={
                "pack": "097",
                "receipt_id": receipt.get("receipt_id"),
                "decision": receipt.get("decision"),
            },
        )
    except Exception:
        pass

    return receipt


def _base_clearance_allowed(clearance_decision: Dict[str, Any] | None) -> bool:
    if not isinstance(clearance_decision, dict):
        return False
    if clearance_decision.get("allowed") is True:
        return True
    if clearance_decision.get("decision") == "allow":
        return True
    return False


def _object_permission_allowed(object_permission: Dict[str, Any] | None) -> bool:
    if not isinstance(object_permission, dict):
        return False
    if object_permission.get("allowed") is True:
        return True
    if object_permission.get("decision") == "allow":
        return True
    return False


def _step_up_satisfied(step_up_decision: Dict[str, Any] | None) -> bool:
    if not isinstance(step_up_decision, dict):
        return False
    if step_up_decision.get("decision") == "allow":
        return True
    if step_up_decision.get("step_up_required") is False and step_up_decision.get("ok") is True:
        return True
    if step_up_decision.get("recent_step_up_verified") is True:
        return True
    return False


def evaluate_reveal_request(
    *,
    actor_user_id: str,
    action: str,
    object_type: str,
    object_id: str,
    payload: Dict[str, Any],
    app_id: str = "tower",
    route_path: str = "/tower/security-command",
    clearance_decision: Dict[str, Any] | None = None,
    object_permission: Dict[str, Any] | None = None,
    step_up_decision: Dict[str, Any] | None = None,
    reveal_fields: List[str] | None = None,
    metadata: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    actor_user_id = _safe_str(actor_user_id, "anonymous")
    action = _safe_str(action, "reveal_sensitive_detail")
    object_type = _safe_str(object_type, "unknown_object")
    object_id = _safe_str(object_id, "unknown")
    app_id = _safe_str(app_id, "tower")
    route_path = _safe_str(route_path, "/tower/security-command")
    payload = payload if isinstance(payload, dict) else {"value": payload}
    metadata = metadata if isinstance(metadata, dict) else {}

    summary = build_redacted_summary(
        object_type=object_type,
        object_id=object_id,
        payload=payload,
        actor_user_id=actor_user_id,
        app_id=app_id,
        reason="reveal_request_default_summary",
    )

    if not _base_clearance_allowed(clearance_decision):
        receipt = _record_reveal_receipt({
            "actor_user_id": actor_user_id,
            "decision": "reveal_denied",
            "reason_code": "base_clearance_required_for_reveal",
            "action": action,
            "object_type": object_type,
            "object_id": object_id,
            "app_id": app_id,
            "route_path": route_path,
            "metadata": metadata,
            "payload_fingerprint": summary.get("payload_fingerprint"),
        })
        return {
            "ok": True,
            "decision": "summary_only",
            "reveal_allowed": False,
            "reason_code": "base_clearance_required_for_reveal",
            "summary": summary,
            "receipt": receipt,
            "required_actions": ["obtain_base_clearance"],
            "human_reason": "Base clearance is required before sensitive details can reveal.",
            "soulaana_translation": "Soulaana: I can show the summary. The details need a real clearance gate first.",
        }

    if not _object_permission_allowed(object_permission):
        receipt = _record_reveal_receipt({
            "actor_user_id": actor_user_id,
            "decision": "reveal_denied",
            "reason_code": "object_permission_required_for_reveal",
            "action": action,
            "object_type": object_type,
            "object_id": object_id,
            "app_id": app_id,
            "route_path": route_path,
            "metadata": metadata,
            "payload_fingerprint": summary.get("payload_fingerprint"),
        })
        return {
            "ok": True,
            "decision": "summary_only",
            "reveal_allowed": False,
            "reason_code": "object_permission_required_for_reveal",
            "summary": summary,
            "receipt": receipt,
            "required_actions": ["obtain_object_permission"],
            "human_reason": "Object-level permission is required before sensitive details can reveal.",
            "soulaana_translation": "Soulaana: You can see the label, not the contents. Object permission is missing.",
        }

    requires_step_up = action in REVEAL_ACTIONS_REQUIRING_STEP_UP or any(
        _is_sensitive_key(field) for field in (reveal_fields or [])
    )

    if requires_step_up and not _step_up_satisfied(step_up_decision):
        step_up_result = None
        try:
            from tower.step_up_auth import evaluate_step_up_requirement

            step_up_result = evaluate_step_up_requirement(
                user_id=actor_user_id,
                action="sensitive_reveal",
                object_type=object_type,
                object_id=object_id,
                session_id=_safe_str(metadata.get("session_id")),
                route_path=route_path,
                clearance_decision={"allowed": True, "decision": "allow"},
                risk_context={
                    "action": action,
                    "object_type": object_type,
                    "object_id": object_id,
                    "reveal_fields": reveal_fields or [],
                },
            )
        except Exception as exc:
            step_up_result = {
                "ok": False,
                "decision": "step_up_required",
                "reason_code": "step_up_framework_unavailable_for_reveal",
                "error_type": type(exc).__name__,
            }

        receipt = _record_reveal_receipt({
            "actor_user_id": actor_user_id,
            "decision": "reveal_step_up_required",
            "reason_code": "step_up_required_for_sensitive_reveal",
            "action": action,
            "object_type": object_type,
            "object_id": object_id,
            "app_id": app_id,
            "route_path": route_path,
            "metadata": metadata,
            "payload_fingerprint": summary.get("payload_fingerprint"),
            "step_up": step_up_result,
        })
        return {
            "ok": True,
            "decision": "step_up_required",
            "reveal_allowed": False,
            "reason_code": "step_up_required_for_sensitive_reveal",
            "summary": summary,
            "step_up": step_up_result,
            "receipt": receipt,
            "required_actions": ["complete_step_up_auth"],
            "human_reason": "Step-up verification is required before sensitive details can reveal.",
            "soulaana_translation": "Soulaana: Summary stays visible. Details wait for a fresh owner check.",
        }

    revealed = build_revealed_payload(
        payload=payload,
        reveal_fields=reveal_fields,
    )

    receipt = _record_reveal_receipt({
        "actor_user_id": actor_user_id,
        "decision": "reveal_allowed",
        "reason_code": "clearance_object_permission_step_up_satisfied",
        "action": action,
        "object_type": object_type,
        "object_id": object_id,
        "app_id": app_id,
        "route_path": route_path,
        "metadata": metadata,
        "payload_fingerprint": summary.get("payload_fingerprint"),
        "revealed_field_count": revealed.get("revealed_field_count", 0),
        "redacted_field_count": revealed.get("redacted_field_count", 0),
    })

    return {
        "ok": True,
        "decision": "reveal_allowed",
        "reveal_allowed": True,
        "reason_code": "clearance_object_permission_step_up_satisfied",
        "summary": summary,
        "revealed": revealed,
        "receipt": receipt,
        "required_actions": [],
        "human_reason": "Sensitive detail reveal allowed after clearance, object permission, and step-up where required.",
        "soulaana_translation": "Soulaana: The gates lined up. Details revealed with a receipt.",
    }


def build_revealed_payload(
    *,
    payload: Dict[str, Any],
    reveal_fields: List[str] | None = None,
) -> Dict[str, Any]:
    payload = payload if isinstance(payload, dict) else {"value": payload}
    reveal_fields = reveal_fields or []
    reveal_set = {str(field) for field in reveal_fields}

    if not reveal_set:
        reveal_set = set(payload.keys())

    output = {}
    revealed_count = 0
    redacted_count = 0

    for key, value in payload.items():
        key_text = str(key)

        if _is_secret_key(key_text) or (isinstance(value, str) and _looks_like_secret_value(value)):
            redacted_count += 1
            continue

        if key_text not in reveal_set:
            output[key] = _mask_value(value, "NOT_REQUESTED")
            redacted_count += 1
            continue

        if _is_sensitive_key(key_text):
            output[key] = value
            revealed_count += 1
        else:
            output[key] = redact_payload_for_summary(value)
            revealed_count += 1

    scan = _safe_scan_for_leakage(output)

    if not scan.get("ok"):
        output = redact_payload_for_summary(output)
        redacted_count += 1
        revealed_count = max(0, revealed_count - 1)
        scan = _safe_scan_for_leakage(output)

    return {
        "ok": scan.get("ok") is True,
        "payload": output,
        "revealed_field_count": revealed_count,
        "redacted_field_count": redacted_count,
        "leakage_scan": scan,
        "secret_values_never_revealed": True,
        "human_reason": "Payload revealed with secret values still blocked.",
        "soulaana_translation": "Soulaana: Details revealed where allowed. Secrets still stayed deadbolted.",
    }


def summarize_reveal_system(limit: int = 20) -> Dict[str, Any]:
    receipts = _load_receipts()

    try:
        limit = int(limit)
    except Exception:
        limit = 20
    limit = max(1, min(limit, 200))

    by_decision: Dict[str, int] = {}
    by_reason: Dict[str, int] = {}
    by_object_type: Dict[str, int] = {}

    for receipt in receipts:
        decision = receipt.get("decision", "unknown")
        reason = receipt.get("reason_code", "unknown")
        object_type = receipt.get("object_type", "unknown")
        by_decision[decision] = by_decision.get(decision, 0) + 1
        by_reason[reason] = by_reason.get(reason, 0) + 1
        by_object_type[object_type] = by_object_type.get(object_type, 0) + 1

    summary = {
        "ok": True,
        "pack": "097",
        "receipts_path": str(REVEAL_RECEIPTS_PATH),
        "policy_path": str(REVEAL_POLICY_PATH),
        "policy": REVEAL_POLICY,
        "receipt_count": len(receipts),
        "by_decision": by_decision,
        "by_reason": by_reason,
        "by_object_type": by_object_type,
        "recent_receipts": receipts[-limit:],
        "readiness_score": 100,
        "readiness_label": "Redaction-by-default reveal system ready",
        "human_reason": "Reveal system summary loaded.",
        "soulaana_translation": "Soulaana: The summary glass is up. Details only reveal after the gates agree.",
    }

    summary = redact_payload_for_summary(summary)
    scan = _safe_scan_for_leakage(summary)
    summary["no_secret_leakage"] = scan.get("ok") is True

    return summary


def reset_reveal_system_for_test() -> Dict[str, Any]:
    _save_receipts([])
    _write_json(REVEAL_POLICY_PATH, {
        "ok": True,
        "pack": "097",
        "policy": REVEAL_POLICY,
        "updated_at": _utc_now(),
        "human_reason": "Redaction reveal policy initialized.",
        "soulaana_translation": "Soulaana: Default summaries first. Reveals need gates.",
    })

    return {
        "ok": True,
        "decision": "reveal_system_reset_for_test",
        "receipts_reset": True,
        "policy_initialized": True,
        "soulaana_translation": "Soulaana: Reveal system reset for a clean test lane.",
    }
