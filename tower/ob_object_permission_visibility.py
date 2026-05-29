
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "tower" / "data"

OBJECT_EVENTS_PATH = DATA_DIR / "ob_object_permission_events.json"
OBJECT_VISIBILITY_STATUS_PATH = DATA_DIR / "ob_object_permission_visibility_status.json"
OBJECT_VISIBILITY_PANEL_PATH = DATA_DIR / "ob_object_permission_visibility_panel.html"


IMPORTANT_DECISIONS = {"deny", "step_up_required", "summary_only"}
IMPORTANT_OBJECT_TYPES = {"export", "report", "analysis", "admin_panel", "tower_object", "mode", "position", "trade"}


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


def _fingerprint(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, default=str).encode("utf-8")
    ).hexdigest()


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
                clean[key] = "[REDACTED_OBJECT_VISIBILITY_SENSITIVE]"
                redacted_count += 1
                continue

            redacted_item = _redact(item)

            if isinstance(redacted_item, dict) and "__redacted_object_visibility_field_count__" in redacted_item:
                try:
                    redacted_count += int(redacted_item.get("__redacted_object_visibility_field_count__", 0))
                except Exception:
                    redacted_count += 1
                redacted_item = dict(redacted_item)
                redacted_item.pop("__redacted_object_visibility_field_count__", None)

            clean[key] = redacted_item

        if redacted_count:
            clean["__redacted_object_visibility_field_count__"] = redacted_count

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
            return "[REDACTED_OBJECT_VISIBILITY_VALUE]"
        return value

    return value


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


def load_object_permission_events() -> List[Dict[str, Any]]:
    data = _load_json(OBJECT_EVENTS_PATH, [])
    return data if isinstance(data, list) else []


def _safe_event_card(event: Dict[str, Any]) -> Dict[str, Any]:
    response = event.get("response", {}) if isinstance(event.get("response"), dict) else {}

    item = {
        "event_id": event.get("event_id", ""),
        "created_at": event.get("created_at", ""),
        "decision": event.get("decision", response.get("decision", "unknown")),
        "reason_code": event.get("reason_code", response.get("reason_code", "")),
        "object_type": event.get("object_type", response.get("object_type", "")),
        "object_id": event.get("object_id", response.get("object_id", "")),
        "action": event.get("action", response.get("action", "")),
        "role": event.get("role", response.get("role", "")),
        "role_family": event.get("role_family", response.get("role_family", "")),
        "user_id": event.get("user_id", response.get("user_id", "")),
        "requires_step_up": response.get("requires_step_up", False),
        "requires_receipt": response.get("requires_receipt", False),
        "requires_archive_handoff": response.get("requires_archive_handoff", False),
        "requires_summary_only": response.get("requires_summary_only", False),
        "required_actions": response.get("required_actions", []),
        "human_reason": response.get("human_reason", ""),
        "soulaana_translation": response.get("soulaana_translation", ""),
    }
    return _redact(item)


def build_object_permission_visibility_status(limit: int = 100, write_panel: bool = True) -> Dict[str, Any]:
    try:
        limit = int(limit)
    except Exception:
        limit = 100
    limit = max(1, min(limit, 300))

    events = load_object_permission_events()
    cards = [_safe_event_card(event) for event in events]

    by_decision: Dict[str, int] = {}
    by_object_type: Dict[str, int] = {}
    by_role_family: Dict[str, int] = {}
    by_reason: Dict[str, int] = {}

    for card in cards:
        decision = card.get("decision", "unknown")
        object_type = card.get("object_type", "unknown")
        role_family = card.get("role_family", "unknown")
        reason = card.get("reason_code", "unknown")

        by_decision[decision] = by_decision.get(decision, 0) + 1
        by_object_type[object_type] = by_object_type.get(object_type, 0) + 1
        by_role_family[role_family] = by_role_family.get(role_family, 0) + 1
        by_reason[reason] = by_reason.get(reason, 0) + 1

    denied_events = [card for card in cards if card.get("decision") == "deny"]
    step_up_events = [card for card in cards if card.get("decision") == "step_up_required"]
    summary_only_events = [card for card in cards if card.get("decision") == "summary_only"]
    export_events = [card for card in cards if card.get("object_type") in {"export", "report"}]
    admin_events = [card for card in cards if card.get("object_type") in {"admin_panel", "tower_object"}]
    live_mode_events = [
        card for card in cards
        if card.get("object_type") == "mode" or "live_mode" in str(card.get("reason_code", ""))
    ]

    important_events = [
        card for card in cards
        if card.get("decision") in IMPORTANT_DECISIONS
        or card.get("object_type") in IMPORTANT_OBJECT_TYPES
        or card.get("requires_step_up")
        or card.get("requires_archive_handoff")
    ]

    status = {
        "ok": True,
        "pack": "112",
        "created_at": _utc_now(),
        "events_path": str(OBJECT_EVENTS_PATH),
        "status_path": str(OBJECT_VISIBILITY_STATUS_PATH),
        "panel_path": str(OBJECT_VISIBILITY_PANEL_PATH),
        "event_count": len(events),
        "visible_event_count": len(cards),
        "important_event_count": len(important_events),
        "deny_count": len(denied_events),
        "step_up_required_count": len(step_up_events),
        "summary_only_count": len(summary_only_events),
        "export_event_count": len(export_events),
        "admin_event_count": len(admin_events),
        "live_mode_event_count": len(live_mode_events),
        "by_decision": by_decision,
        "by_object_type": by_object_type,
        "by_role_family": by_role_family,
        "by_reason": by_reason,
        "recent_events": cards[-limit:],
        "recent_important_events": important_events[-limit:],
        "recent_denied_events": denied_events[-limit:],
        "recent_step_up_events": step_up_events[-limit:],
        "recent_export_events": export_events[-limit:],
        "recent_summary_only_events": summary_only_events[-limit:],
        "recent_live_mode_events": live_mode_events[-limit:],
        "readiness_score": 100,
        "readiness_label": "OB object permission visibility ready",
        "human_reason": "Object permission denies, step-up requests, exports, summaries, and live-mode locks are visible to The Tower.",
        "soulaana_translation": "Soulaana: Object decisions are no longer hidden in the walls. The Tower can see them.",
    }

    status = _redact(status)
    scan = _safe_scan(status)
    status["no_secret_leakage"] = scan.get("ok") is True
    status["leakage_scan"] = scan
    status["status_fingerprint"] = _fingerprint(status)

    _write_json(OBJECT_VISIBILITY_STATUS_PATH, status)

    try:
        from tower.tamper_evident_audit_chain import create_tamper_chain_entry

        create_tamper_chain_entry(
            event_type="tower_ob_object_permission_visibility_status",
            source_name="ob_object_permission_visibility_status",
            source_path=str(OBJECT_VISIBILITY_STATUS_PATH),
            source_hash=_fingerprint(status),
            record_count=len(events),
            actor_user_id="tower_system",
            reason="Pack 112 object permission visibility status generated.",
            metadata={
                "pack": "112",
                "deny_count": status.get("deny_count"),
                "step_up_required_count": status.get("step_up_required_count"),
                "export_event_count": status.get("export_event_count"),
                "summary_only_count": status.get("summary_only_count"),
            },
        )
    except Exception:
        pass

    if write_panel:
        write_object_permission_visibility_panel(status)

    return status


def write_object_permission_visibility_panel(status: Dict[str, Any] | None = None) -> Dict[str, Any]:
    status = status if isinstance(status, dict) else _load_json(OBJECT_VISIBILITY_STATUS_PATH, {})
    important = status.get("recent_important_events", []) if isinstance(status.get("recent_important_events"), list) else []

    cards = []
    for event in important[-30:]:
        decision = event.get("decision", "unknown")
        object_type = event.get("object_type", "object")
        object_id = event.get("object_id", "")
        reason = event.get("reason_code", "")
        role_family = event.get("role_family", "")
        required = event.get("required_actions", [])
        required_text = ", ".join(required[:3]) if isinstance(required, list) else ""

        css = "neutral"
        if decision == "deny":
            css = "deny"
        elif decision == "step_up_required":
            css = "step"
        elif decision == "summary_only":
            css = "summary"
        elif decision == "allow":
            css = "allow"

        cards.append(f"""
        <article class="card {css}">
          <div class="eyebrow">{decision} · {object_type} · {role_family}</div>
          <h2>{object_id}</h2>
          <p>{reason}</p>
          <small>{required_text}</small>
        </article>
        """)

    html = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>The Tower · Object Permission Visibility</title>
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
      grid-template-columns: repeat(5, minmax(0, 1fr));
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
      border-color: rgba(255,128,128,.55);
    }}
    .card.step {{
      border-color: rgba(220,183,94,.55);
    }}
    .card.summary {{
      border-color: rgba(168,175,255,.48);
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
    small {{
      color: rgba(245,234,210,.58);
    }}
  </style>
</head>
<body>
<main>
  <section class="hero">
    <h1>The Tower · Object Permission Visibility</h1>
    <p>{status.get('human_reason', 'Object permission visibility loaded.')}</p>
  </section>
  <section class="stats">
    <div class="stat"><b>{status.get('event_count', 0)}</b><span>Events</span></div>
    <div class="stat"><b>{status.get('deny_count', 0)}</b><span>Denied</span></div>
    <div class="stat"><b>{status.get('step_up_required_count', 0)}</b><span>Step-up</span></div>
    <div class="stat"><b>{status.get('export_event_count', 0)}</b><span>Exports</span></div>
    <div class="stat"><b>{status.get('summary_only_count', 0)}</b><span>Summary-only</span></div>
  </section>
  <section class="grid">{''.join(cards)}</section>
</main>
</body>
</html>
"""
    OBJECT_VISIBILITY_PANEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    OBJECT_VISIBILITY_PANEL_PATH.write_text(html, encoding="utf-8")

    return {
        "ok": True,
        "decision": "object_permission_visibility_panel_written",
        "path": str(OBJECT_VISIBILITY_PANEL_PATH),
        "human_reason": "Object permission visibility panel written.",
        "soulaana_translation": "Soulaana: Object visibility board posted.",
    }


def load_object_permission_visibility_status() -> Dict[str, Any]:
    status = _load_json(OBJECT_VISIBILITY_STATUS_PATH, {})
    if not status:
        status = build_object_permission_visibility_status(write_panel=True)
    return status


def object_permission_visibility_status_card() -> Dict[str, Any]:
    status = load_object_permission_visibility_status()
    return {
        "ok": status.get("ok") is True,
        "pack": "112",
        "title": "OB Object Permissions",
        "readiness_score": status.get("readiness_score", 0),
        "event_count": status.get("event_count", 0),
        "deny_count": status.get("deny_count", 0),
        "step_up_required_count": status.get("step_up_required_count", 0),
        "export_event_count": status.get("export_event_count", 0),
        "summary_only_count": status.get("summary_only_count", 0),
        "panel_path": status.get("panel_path", str(OBJECT_VISIBILITY_PANEL_PATH)),
        "status_path": status.get("status_path", str(OBJECT_VISIBILITY_STATUS_PATH)),
        "human_reason": "OB object permission visibility status card loaded.",
        "soulaana_translation": "Soulaana: Object permission decisions are visible.",
    }


def reset_object_permission_visibility_for_test() -> Dict[str, Any]:
    _write_json(OBJECT_VISIBILITY_STATUS_PATH, {
        "ok": True,
        "pack": "112",
        "event_count": 0,
        "reset_at": _utc_now(),
        "human_reason": "Object permission visibility reset for test.",
    })
    if OBJECT_VISIBILITY_PANEL_PATH.exists():
        try:
            OBJECT_VISIBILITY_PANEL_PATH.unlink()
        except Exception:
            pass
    return {
        "ok": True,
        "decision": "object_permission_visibility_reset_for_test",
        "soulaana_translation": "Soulaana: Object permission visibility reset for a clean test lane.",
    }
