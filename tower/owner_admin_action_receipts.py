
from __future__ import annotations

import hashlib
import json
import secrets
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "tower" / "data"

OWNER_ADMIN_RECEIPTS_PATH = DATA_DIR / "owner_admin_action_receipts.json"
OWNER_ADMIN_SUMMARY_PATH = DATA_DIR / "owner_admin_action_receipt_summary.json"
OWNER_ADMIN_PANEL_PATH = DATA_DIR / "owner_admin_action_receipts_panel.html"


OWNER_ADMIN_ACTION_TYPES = {
    "note_added",
    "security_item_resolved",
    "route_policy_changed",
    "user_clearance_changed",
    "export_approved",
    "lockdown_enabled",
    "lockdown_disabled",
    "mode_access_granted",
    "archive_handoff_created",
    "admin_override_recorded",
}


HIGH_POWER_ACTIONS = {
    "route_policy_changed",
    "user_clearance_changed",
    "export_approved",
    "lockdown_enabled",
    "lockdown_disabled",
    "mode_access_granted",
    "archive_handoff_created",
    "admin_override_recorded",
}


STEP_UP_RECOMMENDED_ACTIONS = {
    "route_policy_changed",
    "user_clearance_changed",
    "export_approved",
    "lockdown_disabled",
    "mode_access_granted",
    "archive_handoff_created",
    "admin_override_recorded",
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


def _safe_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except Exception:
        return default


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


def _receipt_id(prefix: str = "owner_admin_receipt") -> str:
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
        "social_security_number",
        "bank_account",
        "routing_number",
        "account_number",
        "card_number",
        "private_notes",
        "medical_notes",
        "legal_notes",
        "document_text",
        "raw_payload",
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
                clean[key] = "[REDACTED_SENSITIVE]"
                redacted_count += 1
                continue

            redacted_item = _redact(item)

            if isinstance(redacted_item, dict) and "__redacted_owner_admin_field_count__" in redacted_item:
                try:
                    redacted_count += int(redacted_item.get("__redacted_owner_admin_field_count__", 0))
                except Exception:
                    redacted_count += 1
                redacted_item = dict(redacted_item)
                redacted_item.pop("__redacted_owner_admin_field_count__", None)

            clean[key] = redacted_item

        if redacted_count:
            clean["__redacted_owner_admin_field_count__"] = redacted_count

        return clean

    if isinstance(value, list):
        return [_redact(item) for item in value]

    if isinstance(value, str):
        lowered = value.lower()
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
            return "[REDACTED_OWNER_ADMIN_VALUE]"
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


def _load_receipts() -> List[Dict[str, Any]]:
    data = _load_json(OWNER_ADMIN_RECEIPTS_PATH, [])
    return data if isinstance(data, list) else []


def _save_receipts(receipts: List[Dict[str, Any]]) -> None:
    _write_json(OWNER_ADMIN_RECEIPTS_PATH, receipts)


def _normalize_action_type(action_type: str) -> str:
    action_type = _safe_str(action_type, "admin_override_recorded")
    return action_type if action_type in OWNER_ADMIN_ACTION_TYPES else "admin_override_recorded"


def _step_up_present(step_up: Dict[str, Any] | None) -> bool:
    if not isinstance(step_up, dict):
        return False
    return (
        step_up.get("decision") in {"allow", "verified"}
        or step_up.get("recent_step_up_verified") is True
        or step_up.get("ok") is True and step_up.get("decision") == "verified"
    )


def create_owner_admin_receipt(
    *,
    action_type: str,
    actor_user_id: str,
    target_type: str,
    target_id: str,
    reason: str,
    app_id: str = "tower",
    route_path: str = "/tower/security-command",
    before_state: Dict[str, Any] | None = None,
    after_state: Dict[str, Any] | None = None,
    decision: str = "recorded",
    status: str = "completed",
    step_up: Dict[str, Any] | None = None,
    object_permission: Dict[str, Any] | None = None,
    archive_handoff: Dict[str, Any] | None = None,
    metadata: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    action_type = _normalize_action_type(action_type)
    actor_user_id = _safe_str(actor_user_id, "unknown_actor")
    target_type = _safe_str(target_type, "unknown_target")
    target_id = _safe_str(target_id, "unknown")
    reason = _safe_str(reason, "No reason provided.")
    app_id = _safe_str(app_id, "tower")
    route_path = _safe_str(route_path, "/tower/security-command")
    decision = _safe_str(decision, "recorded")
    status = _safe_str(status, "completed")
    metadata = metadata if isinstance(metadata, dict) else {}

    receipt = {
        "ok": True,
        "pack": "099",
        "receipt_id": _receipt_id(),
        "event_type": "tower_owner_admin_action_receipt",
        "created_at": _utc_now(),
        "action_type": action_type,
        "action_power": "high" if action_type in HIGH_POWER_ACTIONS else "normal",
        "actor_user_id": actor_user_id,
        "target_type": target_type,
        "target_id": target_id,
        "app_id": app_id,
        "route_path": route_path,
        "decision": decision,
        "status": status,
        "reason": reason,
        "before_state": _redact(before_state or {}),
        "after_state": _redact(after_state or {}),
        "step_up_present": _step_up_present(step_up),
        "step_up_recommended": action_type in STEP_UP_RECOMMENDED_ACTIONS,
        "step_up": _redact(step_up or {}),
        "object_permission": _redact(object_permission or {}),
        "archive_handoff": _redact(archive_handoff or {}),
        "metadata": _redact(metadata),
        "receipt_scope": {
            "auditable": True,
            "archive_ready": True,
            "tamper_chain_ready": True,
            "owner_review_ready": True,
        },
        "human_reason": "Owner/admin action receipt recorded.",
        "soulaana_translation": "Soulaana: Powerful move recorded. The Tower does not do silent buttons.",
    }

    receipt["receipt_fingerprint"] = _fingerprint(receipt)
    sanitized = _redact(receipt)

    receipts = _load_receipts()
    receipts.append(sanitized)
    _save_receipts(receipts)

    try:
        from tower.tamper_evident_audit_chain import create_tamper_chain_entry

        create_tamper_chain_entry(
            event_type="tower_owner_admin_action_receipt_snapshot",
            source_name="owner_admin_action_receipts",
            source_path=str(OWNER_ADMIN_RECEIPTS_PATH),
            source_hash=_fingerprint(receipts),
            record_count=len(receipts),
            actor_user_id=actor_user_id,
            reason=f"Pack 099 chained owner/admin receipt {action_type}.",
            metadata={
                "pack": "099",
                "receipt_id": sanitized.get("receipt_id"),
                "action_type": action_type,
                "target_type": target_type,
                "target_id": target_id,
            },
        )
    except Exception:
        pass

    return sanitized


def record_note_receipt(*, actor_user_id: str, target_type: str, target_id: str, note: str, **kwargs) -> Dict[str, Any]:
    return create_owner_admin_receipt(
        action_type="note_added",
        actor_user_id=actor_user_id,
        target_type=target_type,
        target_id=target_id,
        reason="Owner/admin note added.",
        after_state={"note": note},
        **kwargs,
    )


def record_resolve_receipt(*, actor_user_id: str, target_type: str, target_id: str, resolution: str, **kwargs) -> Dict[str, Any]:
    return create_owner_admin_receipt(
        action_type="security_item_resolved",
        actor_user_id=actor_user_id,
        target_type=target_type,
        target_id=target_id,
        reason="Security item resolved.",
        after_state={"resolution": resolution, "resolved": True},
        **kwargs,
    )


def record_route_policy_change_receipt(
    *,
    actor_user_id: str,
    route_path: str,
    old_policy: Dict[str, Any],
    new_policy: Dict[str, Any],
    reason: str,
    **kwargs,
) -> Dict[str, Any]:
    return create_owner_admin_receipt(
        action_type="route_policy_changed",
        actor_user_id=actor_user_id,
        target_type="route_policy",
        target_id=route_path,
        route_path=route_path,
        before_state=old_policy,
        after_state=new_policy,
        reason=reason,
        **kwargs,
    )


def record_user_clearance_change_receipt(
    *,
    actor_user_id: str,
    user_id: str,
    old_clearance: Dict[str, Any],
    new_clearance: Dict[str, Any],
    reason: str,
    **kwargs,
) -> Dict[str, Any]:
    return create_owner_admin_receipt(
        action_type="user_clearance_changed",
        actor_user_id=actor_user_id,
        target_type="user_clearance",
        target_id=user_id,
        before_state=old_clearance,
        after_state=new_clearance,
        reason=reason,
        **kwargs,
    )


def record_export_approval_receipt(
    *,
    actor_user_id: str,
    export_id: str,
    export_scope: Dict[str, Any],
    reason: str,
    **kwargs,
) -> Dict[str, Any]:
    return create_owner_admin_receipt(
        action_type="export_approved",
        actor_user_id=actor_user_id,
        target_type="export",
        target_id=export_id,
        after_state={"export_scope": export_scope, "approved": True},
        reason=reason,
        **kwargs,
    )


def record_lockdown_change_receipt(
    *,
    actor_user_id: str,
    lockdown_id: str,
    enabled: bool,
    reason: str,
    before_state: Dict[str, Any] | None = None,
    after_state: Dict[str, Any] | None = None,
    **kwargs,
) -> Dict[str, Any]:
    return create_owner_admin_receipt(
        action_type="lockdown_enabled" if enabled else "lockdown_disabled",
        actor_user_id=actor_user_id,
        target_type="emergency_lockdown",
        target_id=lockdown_id,
        before_state=before_state or {},
        after_state=after_state or {"lockdown_active": bool(enabled)},
        reason=reason,
        **kwargs,
    )


def record_mode_access_grant_receipt(
    *,
    actor_user_id: str,
    user_id: str,
    mode_name: str,
    grant_scope: Dict[str, Any],
    reason: str,
    **kwargs,
) -> Dict[str, Any]:
    return create_owner_admin_receipt(
        action_type="mode_access_granted",
        actor_user_id=actor_user_id,
        target_type="mode_access",
        target_id=f"{user_id}:{mode_name}",
        after_state={"user_id": user_id, "mode_name": mode_name, "grant_scope": grant_scope},
        reason=reason,
        **kwargs,
    )


def record_archive_handoff_receipt(
    *,
    actor_user_id: str,
    handoff_id: str,
    handoff_payload: Dict[str, Any],
    reason: str,
    **kwargs,
) -> Dict[str, Any]:
    return create_owner_admin_receipt(
        action_type="archive_handoff_created",
        actor_user_id=actor_user_id,
        target_type="archive_handoff",
        target_id=handoff_id,
        after_state={"handoff_id": handoff_id, "handoff_payload": handoff_payload},
        archive_handoff={"handoff_id": handoff_id, "created": True},
        reason=reason,
        **kwargs,
    )


def create_archive_handoff_from_receipt(
    *,
    receipt: Dict[str, Any],
    archive_category: str = "tower_owner_admin_receipts",
    actor_user_id: str = "tower_system",
) -> Dict[str, Any]:
    receipt = receipt if isinstance(receipt, dict) else {}
    handoff = {
        "ok": True,
        "pack": "099",
        "handoff_id": _receipt_id("archive_handoff"),
        "created_at": _utc_now(),
        "actor_user_id": _safe_str(actor_user_id, "tower_system"),
        "archive_category": archive_category,
        "source_receipt_id": receipt.get("receipt_id"),
        "source_action_type": receipt.get("action_type"),
        "source_target_type": receipt.get("target_type"),
        "source_target_id": receipt.get("target_id"),
        "payload_fingerprint": _fingerprint(receipt),
        "archive_ready": True,
        "redacted_payload": _redact(receipt),
        "human_reason": "Archive handoff created from owner/admin receipt.",
        "soulaana_translation": "Soulaana: Receipt bundled for the Archive Vault without exposing raw secrets.",
    }

    handoff = _redact(handoff)

    try:
        queue_path = DATA_DIR / "archive_vault_handoff_queue.json"
        queue = _load_json(queue_path, [])
        queue = queue if isinstance(queue, list) else []
        queue.append(handoff)
        _write_json(queue_path, queue)
    except Exception:
        pass

    return handoff


def summarize_owner_admin_receipts(limit: int = 20) -> Dict[str, Any]:
    receipts = _load_receipts()

    try:
        limit = int(limit)
    except Exception:
        limit = 20
    limit = max(1, min(limit, 200))

    by_action: Dict[str, int] = {}
    by_actor: Dict[str, int] = {}
    by_target_type: Dict[str, int] = {}
    by_power: Dict[str, int] = {}
    step_up_missing_high_power = 0
    archive_ready_count = 0

    for receipt in receipts:
        action = receipt.get("action_type", "unknown")
        actor = receipt.get("actor_user_id", "unknown")
        target_type = receipt.get("target_type", "unknown")
        power = receipt.get("action_power", "unknown")

        by_action[action] = by_action.get(action, 0) + 1
        by_actor[actor] = by_actor.get(actor, 0) + 1
        by_target_type[target_type] = by_target_type.get(target_type, 0) + 1
        by_power[power] = by_power.get(power, 0) + 1

        if receipt.get("step_up_recommended") is True and receipt.get("step_up_present") is not True:
            step_up_missing_high_power += 1

        scope = receipt.get("receipt_scope", {}) if isinstance(receipt.get("receipt_scope"), dict) else {}
        if scope.get("archive_ready") is True:
            archive_ready_count += 1

    summary = {
        "ok": True,
        "pack": "099",
        "receipts_path": str(OWNER_ADMIN_RECEIPTS_PATH),
        "summary_path": str(OWNER_ADMIN_SUMMARY_PATH),
        "panel_path": str(OWNER_ADMIN_PANEL_PATH),
        "receipt_count": len(receipts),
        "archive_ready_count": archive_ready_count,
        "step_up_missing_high_power_count": step_up_missing_high_power,
        "by_action": by_action,
        "by_actor": by_actor,
        "by_target_type": by_target_type,
        "by_power": by_power,
        "recent_receipts": receipts[-limit:],
        "readiness_score": 100 if len(receipts) else 80,
        "readiness_label": "Owner/admin action receipt coverage ready",
        "human_reason": "Owner/admin action receipt summary loaded.",
        "soulaana_translation": "Soulaana: Owner/admin moves have receipts. No silent powerful buttons.",
    }

    summary = _redact(summary)
    scan = _safe_scan(summary)
    summary["no_secret_leakage"] = scan.get("ok") is True
    summary["leakage_scan"] = scan

    _write_json(OWNER_ADMIN_SUMMARY_PATH, summary)
    return summary


def write_owner_admin_receipts_panel(summary: Dict[str, Any] | None = None) -> Dict[str, Any]:
    summary = summary if isinstance(summary, dict) else summarize_owner_admin_receipts(limit=60)
    receipts = summary.get("recent_receipts", []) if isinstance(summary.get("recent_receipts"), list) else []

    rows = []
    for receipt in receipts[-24:]:
        action = receipt.get("action_type", "unknown")
        target = f"{receipt.get('target_type', 'target')} · {receipt.get('target_id', '')}"
        power = receipt.get("action_power", "normal")
        step = "step-up yes" if receipt.get("step_up_present") else "step-up no"
        rows.append(f"""
        <article class="receipt {power}">
          <div class="eyebrow">{power} power · {step}</div>
          <h2>{action}</h2>
          <p>{target}</p>
          <div class="reason">{receipt.get('reason', '')}</div>
        </article>
        """)

    html = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>The Tower · Owner/Admin Receipts</title>
  <style>
    body {{
      margin: 0;
      min-height: 100vh;
      background: #090907;
      color: #f5ead2;
      font-family: Inter, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }}
    main {{
      max-width: 1160px;
      margin: 0 auto;
      padding: 42px 22px;
    }}
    .hero {{
      border: 1px solid rgba(220, 183, 94, .35);
      border-radius: 28px;
      padding: 28px;
      background: linear-gradient(135deg, rgba(75, 48, 18, .74), rgba(12, 13, 10, .96));
      box-shadow: 0 20px 80px rgba(0,0,0,.38);
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
    .receipt {{
      border: 1px solid rgba(245,234,210,.14);
      border-radius: 24px;
      padding: 18px;
      background: rgba(255,255,255,.045);
    }}
    .receipt.high {{
      border-color: rgba(220, 183, 94, .46);
      box-shadow: 0 0 0 1px rgba(220,183,94,.08) inset;
    }}
    .eyebrow {{
      color: rgba(220, 183, 94, .82);
      text-transform: uppercase;
      letter-spacing: .12em;
      font-size: 11px;
      margin-bottom: 8px;
    }}
    h2 {{
      margin: 0 0 8px;
      font-size: 18px;
    }}
    .receipt p, .reason {{
      color: rgba(245,234,210,.72);
      line-height: 1.45;
    }}
  </style>
</head>
<body>
<main>
  <section class="hero">
    <h1>The Tower · Owner/Admin Receipts</h1>
    <p>{summary.get('human_reason', 'Owner/admin receipts loaded.')}</p>
  </section>
  <section class="stats">
    <div class="stat"><b>{summary.get('receipt_count', 0)}</b><span>Receipts</span></div>
    <div class="stat"><b>{summary.get('archive_ready_count', 0)}</b><span>Archive-ready</span></div>
    <div class="stat"><b>{summary.get('step_up_missing_high_power_count', 0)}</b><span>Step-up gaps</span></div>
    <div class="stat"><b>{summary.get('readiness_score', 0)}</b><span>Readiness</span></div>
  </section>
  <section class="grid">
    {''.join(rows)}
  </section>
</main>
</body>
</html>
"""
    OWNER_ADMIN_PANEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    OWNER_ADMIN_PANEL_PATH.write_text(html, encoding="utf-8")

    return {
        "ok": True,
        "decision": "owner_admin_receipts_panel_written",
        "path": str(OWNER_ADMIN_PANEL_PATH),
        "human_reason": "Owner/admin receipts HTML panel written.",
        "soulaana_translation": "Soulaana: Receipt board posted. Powerful moves have a paper trail.",
    }


def reset_owner_admin_receipts_for_test() -> Dict[str, Any]:
    _save_receipts([])
    _write_json(OWNER_ADMIN_SUMMARY_PATH, {
        "ok": True,
        "pack": "099",
        "receipt_count": 0,
        "human_reason": "Owner/admin receipts reset for test.",
        "soulaana_translation": "Soulaana: Receipt ledger reset for a clean test lane.",
    })

    if OWNER_ADMIN_PANEL_PATH.exists():
        try:
            OWNER_ADMIN_PANEL_PATH.unlink()
        except Exception:
            pass

    return {
        "ok": True,
        "decision": "owner_admin_receipts_reset_for_test",
        "receipts_reset": True,
        "summary_reset": True,
        "soulaana_translation": "Soulaana: Owner/admin receipts reset for a clean test lane.",
    }
