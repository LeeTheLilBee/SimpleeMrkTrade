# =============================================================================
# THE TOWER — EXPORT VAULT
# FILE: tower/export_vault.py
# =============================================================================

import hashlib
import json
import os
import secrets
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

from tower.audit import write_audit_event
from tower.clearance_service import check_export_clearance
from tower.evidence_capsules import create_evidence_capsule
from tower.object_access import evaluate_object_access
from tower.policy_engine import evaluate_policy
from tower.redaction import redact_record
from tower.security_events import create_security_event
from tower.user_store import get_user


PROJECT_ROOT = os.environ.get("SIMPLEE_PROJECT_ROOT", "/content/SimpleeMrkTrade_REAL_CLONE")
TOWER_DATA_DIR = Path(PROJECT_ROOT) / "tower" / "data"
EXPORT_VAULT_PATH = TOWER_DATA_DIR / "export_vault.json"

TOWER_DATA_DIR.mkdir(parents=True, exist_ok=True)


EXPORT_STATUS_APPROVED = "approved"
EXPORT_STATUS_DENIED = "denied"
EXPORT_STATUS_STEP_UP = "step_up_required"
EXPORT_STATUS_QUARANTINED = "quarantined"
EXPORT_STATUS_LOCKED = "locked"
EXPORT_STATUS_REVOKED = "revoked"


def _now() -> str:
    return datetime.utcnow().isoformat() + "Z"


def _expires(hours: int = 24) -> str:
    return (datetime.utcnow() + timedelta(hours=hours)).isoformat() + "Z"


def _safe_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, default=str)


def _hash_payload(payload: Dict[str, Any]) -> str:
    raw = _safe_json(payload).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def _load_raw() -> Dict[str, Any]:
    if not EXPORT_VAULT_PATH.exists():
        return {"exports": []}

    try:
        with EXPORT_VAULT_PATH.open("r", encoding="utf-8") as f:
            data = json.load(f)

        if not isinstance(data, dict):
            return {"exports": []}

        if not isinstance(data.get("exports"), list):
            data["exports"] = []

        return data
    except Exception:
        return {"exports": []}


def _save_raw(data: Dict[str, Any]) -> None:
    tmp_path = EXPORT_VAULT_PATH.with_suffix(".tmp")
    with tmp_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, sort_keys=True, default=str)

    tmp_path.replace(EXPORT_VAULT_PATH)



def _normal_export_field_policy(record: Dict[str, Any]) -> Dict[str, str]:
    """
    Field policy for normal exports.

    Baby version:
    Some things should not leave the building in a download,
    even when the owner is requesting the export.
    """

    policy = {}

    def walk(value: Any, path: str = "") -> None:
        if isinstance(value, dict):
            for key, subvalue in value.items():
                child_path = f"{path}.{key}" if path else str(key)
                lowered = str(key).lower()

                if lowered in {
                    "broker_token",
                    "access_token",
                    "refresh_token",
                    "api_key",
                    "password",
                    "password_hash",
                    "secret",
                    "strategy_core",
                }:
                    policy[child_path] = "secret"

                if lowered in {
                    "device_fingerprint",
                    "session_id",
                    "event_hash",
                    "capsule_hash",
                    "signature",
                }:
                    policy[child_path] = "security_sensitive"

                walk(subvalue, child_path)

        elif isinstance(value, list):
            for idx, item in enumerate(value):
                walk(item, f"{path}[{idx}]")

    walk(record)
    return policy


def _force_redact_export_blocked_fields(
    record: Dict[str, Any],
    redaction_report: Dict[str, Any],
    field_policy: Dict[str, str],
) -> Dict[str, Any]:
    """
    Force-redacts export-blocked fields even if the user can view them internally.

    Baby version:
    Some secrets can be seen inside The Tower,
    but they still cannot leave through a normal export.
    """

    blocked_classes = {"secret", "broker_sensitive", "security_sensitive"}
    forced_paths = [
        path for path, data_class in field_policy.items()
        if data_class in blocked_classes
    ]

    def set_path(obj: Any, path: str) -> bool:
        parts = path.split(".")
        current = obj

        for part in parts[:-1]:
            if isinstance(current, dict):
                current = current.get(part)
            else:
                return False

        final = parts[-1]
        if isinstance(current, dict) and final in current:
            current[final] = "[REDACTED]"
            return True

        return False

    forced_redacted = []

    for path in forced_paths:
        if set_path(record, path):
            forced_redacted.append(path)

    if forced_redacted:
        existing_redacted = set(redaction_report.get("redacted_fields") or [])
        existing_visible = list(redaction_report.get("visible_fields") or [])

        for path in forced_redacted:
            existing_redacted.add(path)
            if path in existing_visible:
                existing_visible.remove(path)

        redaction_report["redacted_fields"] = sorted(existing_redacted)
        redaction_report["visible_fields"] = existing_visible
        redaction_report["redacted_count"] = len(redaction_report["redacted_fields"])
        redaction_report["visible_count"] = len(redaction_report["visible_fields"])
        redaction_report["forced_export_redaction"] = True
        redaction_report["forced_export_redacted_fields"] = forced_redacted

    return record


def _status_from_decision(decision: Dict[str, Any]) -> str:
    kind = str(decision.get("decision") or "").lower()

    if decision.get("allowed") is True:
        return EXPORT_STATUS_APPROVED

    if kind == "step_up":
        return EXPORT_STATUS_STEP_UP

    if kind == "quarantine":
        return EXPORT_STATUS_QUARANTINED

    if kind == "lockdown":
        return EXPORT_STATUS_LOCKED

    return EXPORT_STATUS_DENIED


def request_export(
    user_id: str,
    app_name: str,
    object_type: str,
    object_id: str,
    record: Dict[str, Any],
    classification: Optional[str] = None,
    export_reason: str = "user_requested_export",
    context: Optional[Dict[str, Any]] = None,
    object_payload: Optional[Dict[str, Any]] = None,
    redaction_style: str = "mask",
    expires_hours: int = 24,
) -> Dict[str, Any]:
    """
    Requests a controlled export.

    Baby version:
    The Tower checks if the user can export.
    If yes, it redacts the record and creates an export package.
    If no, it writes receipts and explains why.
    """

    context = context or {}

    user = get_user(user_id)

    if not user:
        decision = {
            "allowed": False,
            "decision": "deny",
            "reason_code": "export_user_not_found",
            "human_reason": "Tower user was not found. Export denied.",
            "risk_score": 85,
            "risk_state": "restricted",
            "required_actions": ["create_or_verify_user"],
            "metadata": {
                "user_id": user_id,
                "app_name": app_name,
                "object_type": object_type,
                "object_id": object_id,
            },
        }

        return _save_export_record(
            user_id=user_id,
            app_name=app_name,
            object_type=object_type,
            object_id=object_id,
            export_reason=export_reason,
            status=EXPORT_STATUS_DENIED,
            decision=decision,
            policy_report=decision,
            redacted_record=None,
            redaction_report=None,
            expires_hours=expires_hours,
        )

    # If no object payload was provided, build a minimal one from the record/request.
    if object_payload is None:
        object_payload = {
            "object_type": object_type,
            "object_id": object_id,
            "app_name": app_name,
            "classification": classification or record.get("classification") or "restricted",
            "owner_user_id": record.get("owner_user_id"),
            "allowed_user_ids": record.get("allowed_user_ids"),
            "allowed_roles": record.get("allowed_roles"),
            "allowed_account_types": record.get("allowed_account_types"),
            "required_consents": record.get("required_consents"),
            "denied_user_ids": record.get("denied_user_ids"),
        }

    # Object-level access first.
    object_decision = evaluate_object_access(
        user=user,
        obj=object_payload,
        action="export",
        context=context,
    ).to_dict()

    if not object_decision.get("allowed"):
        policy_report = evaluate_policy(
            user=user,
            app_name=app_name,
            action="export",
            object_type=object_type,
            object_id=object_id,
            context=context,
        ).to_dict()

        saved = _save_export_record(
            user_id=user_id,
            app_name=app_name,
            object_type=object_type,
            object_id=object_id,
            export_reason=export_reason,
            status=EXPORT_STATUS_DENIED,
            decision=object_decision,
            policy_report=policy_report,
            redacted_record=None,
            redaction_report=None,
            expires_hours=expires_hours,
        )

        _create_export_evidence(
            user=user,
            saved_export=saved,
            decision=object_decision,
            policy_report=policy_report,
            context=context,
            object_context=object_payload,
        )

        return saved

    # Policy check before step-up.
    # Baby version:
    # If the user is not allowed to export at all, do not waste time asking
    # for step-up. Just deny with the clear reason.
    policy_report = evaluate_policy(
        user=user,
        app_name=app_name,
        action="export",
        object_type=object_type,
        object_id=object_id,
        context=context,
    ).to_dict()

    if policy_report.get("allowed") is not True:
        status = EXPORT_STATUS_DENIED

        saved = _save_export_record(
            user_id=user_id,
            app_name=app_name,
            object_type=object_type,
            object_id=object_id,
            export_reason=export_reason,
            status=status,
            decision=policy_report,
            policy_report=policy_report,
            redacted_record=None,
            redaction_report=None,
            expires_hours=expires_hours,
        )

        _create_export_evidence(
            user=user,
            saved_export=saved,
            decision=policy_report,
            policy_report=policy_report,
            context=context,
            object_context=object_payload,
        )

        return saved

    # Export clearance checks step-up + lockdown/session risk after policy passes.
    clearance = check_export_clearance(
        user_id=user_id,
        app_name=app_name,
        object_type=object_type,
        object_id=object_id,
        context=context,
        object_payload=object_payload,
    )

    if not clearance.get("allowed"):
        status = _status_from_decision(clearance)

        saved = _save_export_record(
            user_id=user_id,
            app_name=app_name,
            object_type=object_type,
            object_id=object_id,
            export_reason=export_reason,
            status=status,
            decision=clearance,
            policy_report=policy_report,
            redacted_record=None,
            redaction_report=None,
            expires_hours=expires_hours,
        )

        _create_export_evidence(
            user=user,
            saved_export=saved,
            decision=clearance,
            policy_report=policy_report,
            context=context,
            object_context=object_payload,
        )

        return saved

    export_field_policy = _normal_export_field_policy(record)

    redacted_record, redaction_report = redact_record(
        record=record,
        user=user,
        classification=classification or object_payload.get("classification"),
        field_policy=export_field_policy,
        redaction_style=redaction_style,
    )

    redacted_record = _force_redact_export_blocked_fields(
        record=redacted_record,
        redaction_report=redaction_report,
        field_policy=export_field_policy,
    )

    saved = _save_export_record(
        user_id=user_id,
        app_name=app_name,
        object_type=object_type,
        object_id=object_id,
        export_reason=export_reason,
        status=EXPORT_STATUS_APPROVED,
        decision=clearance,
        policy_report=policy_report,
        redacted_record=redacted_record,
        redaction_report=redaction_report,
        expires_hours=expires_hours,
    )

    _create_export_evidence(
        user=user,
        saved_export=saved,
        decision=clearance,
        policy_report=policy_report,
        context=context,
        object_context=object_payload,
    )

    return saved


def _save_export_record(
    user_id: str,
    app_name: str,
    object_type: str,
    object_id: str,
    export_reason: str,
    status: str,
    decision: Dict[str, Any],
    policy_report: Dict[str, Any],
    redacted_record: Optional[Dict[str, Any]],
    redaction_report: Optional[Dict[str, Any]],
    expires_hours: int = 24,
) -> Dict[str, Any]:
    export_id = secrets.token_urlsafe(18)

    package = {
        "export_id": export_id,
        "created_at": _now(),
        "expires_at": _expires(expires_hours),
        "status": status,
        "user_id": user_id,
        "app_name": app_name,
        "object_type": object_type,
        "object_id": object_id,
        "export_reason": export_reason,
        "decision": decision,
        "policy_report": policy_report,
        "redaction_report": redaction_report,
        "record": redacted_record,
    }

    package_hash = _hash_payload(package)
    package["export_hash"] = package_hash

    data = _load_raw()
    data["exports"].append(package)
    _save_raw(data)

    result = "allow" if status == EXPORT_STATUS_APPROVED else "deny"

    write_audit_event(
        actor_user_id=user_id,
        target_user_id=user_id,
        action="request_export",
        app_name=app_name,
        object_type=object_type,
        object_id=object_id,
        result=result,
        reason_code=f"export_{status}",
        human_reason=f"Tower export request completed with status: {status}.",
        risk_score=int(decision.get("risk_score") or 25),
        risk_state=str(decision.get("risk_state") or "clear"),
        metadata={
            "export_id": export_id,
            "export_hash": package_hash,
            "status": status,
            "reason_code": decision.get("reason_code"),
            "redaction_report": redaction_report,
        },
    )

    if status != EXPORT_STATUS_APPROVED:
        create_security_event(
            user_id=user_id,
            event_type=f"export_{status}",
            severity="medium" if status in {EXPORT_STATUS_DENIED, EXPORT_STATUS_STEP_UP} else "high",
            source_app=app_name,
            description=f"Export request ended with status: {status}.",
            recommended_action=", ".join(decision.get("required_actions", [])) or "review_export_request",
            metadata={
                "export_id": export_id,
                "object_type": object_type,
                "object_id": object_id,
                "decision": decision,
            },
        )

    return package


def _create_export_evidence(
    user: Dict[str, Any],
    saved_export: Dict[str, Any],
    decision: Dict[str, Any],
    policy_report: Dict[str, Any],
    context: Optional[Dict[str, Any]] = None,
    object_context: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    return create_evidence_capsule(
        user=user,
        app_name=saved_export.get("app_name"),
        action="export",
        object_type=saved_export.get("object_type"),
        object_id=saved_export.get("object_id"),
        decision=decision,
        policy_report=policy_report,
        session_context=context or {},
        object_context=object_context or {},
        token_context={
            "export_id": saved_export.get("export_id"),
            "export_hash": saved_export.get("export_hash"),
            "export_status": saved_export.get("status"),
        },
        trigger="export_vault_request",
        created_by="tower_export_vault",
        notes=f"Evidence capsule for export request {saved_export.get('export_id')}.",
    )


def get_export(export_id: str) -> Optional[Dict[str, Any]]:
    data = _load_raw()

    for export in data.get("exports", []):
        if export.get("export_id") == export_id:
            return export

    return None


def list_exports(limit: int = 25) -> List[Dict[str, Any]]:
    data = _load_raw()
    return data.get("exports", [])[-limit:]


def revoke_export(
    export_id: str,
    revoked_by: str,
    reason: str = "export_revoked",
) -> Optional[Dict[str, Any]]:
    data = _load_raw()
    updated = None

    for export in data.get("exports", []):
        if export.get("export_id") == export_id:
            export["status"] = EXPORT_STATUS_REVOKED
            export["revoked_at"] = _now()
            export["revoked_by"] = revoked_by
            export["revoke_reason"] = reason

            clean = dict(export)
            clean.pop("export_hash", None)
            export["export_hash"] = _hash_payload(clean)
            updated = export
            break

    _save_raw(data)

    if updated:
        write_audit_event(
            actor_user_id=revoked_by,
            target_user_id=updated.get("user_id"),
            action="revoke_export",
            app_name=updated.get("app_name"),
            object_type=updated.get("object_type"),
            object_id=updated.get("object_id"),
            result="allow",
            reason_code=reason,
            human_reason="Tower export was revoked.",
            risk_score=70,
            risk_state="restricted",
            metadata={
                "export_id": export_id,
            },
        )

    return updated


def verify_export(export_id: str) -> Dict[str, Any]:
    export = get_export(export_id)

    if not export:
        return {
            "ok": False,
            "reason_code": "export_not_found",
            "human_reason": "Export was not found.",
            "export_id": export_id,
        }

    stored_hash = export.get("export_hash")
    clean = dict(export)
    clean.pop("export_hash", None)

    recalculated = _hash_payload(clean)

    ok = stored_hash == recalculated

    return {
        "ok": ok,
        "reason_code": "export_valid" if ok else "export_hash_mismatch",
        "human_reason": "Export package is valid." if ok else "Export package hash does not match.",
        "export_id": export_id,
        "stored_hash": stored_hash,
        "recalculated_hash": recalculated,
        "status": export.get("status"),
    }


def get_export_summary() -> Dict[str, Any]:
    data = _load_raw()
    exports = data.get("exports", [])

    summary = {
        "total_exports": len(exports),
        "approved": 0,
        "denied": 0,
        "step_up_required": 0,
        "quarantined": 0,
        "locked": 0,
        "revoked": 0,
        "by_app": {},
        "by_object_type": {},
    }

    for export in exports:
        status = export.get("status") or "unknown"
        app_name = export.get("app_name") or "unknown"
        object_type = export.get("object_type") or "unknown"

        if status in summary:
            summary[status] += 1

        summary["by_app"][app_name] = summary["by_app"].get(app_name, 0) + 1
        summary["by_object_type"][object_type] = summary["by_object_type"].get(object_type, 0) + 1

    return summary
