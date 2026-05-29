
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "tower" / "data"

SECURITY_INBOX_STATUS_PATH = DATA_DIR / "security_inbox_owner_queue_status.json"
SECURITY_INBOX_PANEL_PATH = DATA_DIR / "security_inbox_owner_queue_panel.html"

OBJECT_EVENTS_PATH = DATA_DIR / "ob_object_permission_events.json"
REVEAL_RECEIPTS_PATH = DATA_DIR / "redaction_reveal_receipts.json"
SECRETS_EVENTS_PATH = DATA_DIR / "secrets_vault_boundary_events.json"
OWNER_ADMIN_RECEIPTS_PATH = DATA_DIR / "owner_admin_action_receipts.json"
TAMPER_CHAIN_PATH = DATA_DIR / "tamper_evident_audit_chain.json"
SECURITY_REHEARSAL_STATUS_PATH = DATA_DIR / "security_rehearsal_panel_status.json"
OWNER_UI_CHECKPOINT_STATUS_PATH = DATA_DIR / "security_command_owner_ui_checkpoint_status.json"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, indent=2, sort_keys=True, default=str), encoding="utf-8")
    tmp.replace(path)


def _load_json(path: Path, default: Any) -> Any:
    try:
        if not path.exists():
            return default
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(text, encoding="utf-8")
    tmp.replace(path)


def _fingerprint(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, default=str).encode("utf-8")
    ).hexdigest()


def _html_escape(value: Any) -> str:
    text = str(value if value is not None else "")
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#x27;")
    )


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
        "sk_live_",
        "ghp_",
    ]
    hits = [item for item in forbidden if item in serialized]
    return {
        "ok": not hits,
        "forbidden_hit_count": len(hits),
        "had_forbidden_hits": bool(hits),
    }


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

            redacted_item = _redact(item)

            if isinstance(redacted_item, dict) and "__redacted_security_inbox_field_count__" in redacted_item:
                try:
                    redacted_count += int(redacted_item.get("__redacted_security_inbox_field_count__", 0))
                except Exception:
                    redacted_count += 1
                redacted_item = dict(redacted_item)
                redacted_item.pop("__redacted_security_inbox_field_count__", None)

            clean[key] = redacted_item

        if redacted_count:
            clean["__redacted_security_inbox_field_count__"] = redacted_count
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
            return "[REDACTED_SECURITY_INBOX_VALUE]"
        return value

    return value


def _as_list(data: Any) -> List[Any]:
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        for key in ["events", "receipts", "entries", "items", "recent_receipts", "recent_events"]:
            if isinstance(data.get(key), list):
                return data.get(key, [])
        return [data]
    return []


def _event_time(item: Dict[str, Any]) -> str:
    for key in ["created_at", "timestamp", "event_time", "verified_at", "reset_at"]:
        value = item.get(key)
        if isinstance(value, str) and value:
            return value
    return ""


def _event_decision(item: Dict[str, Any]) -> str:
    for key in ["decision", "status", "reason_code", "event_type"]:
        value = item.get(key)
        if isinstance(value, str) and value:
            return value
    return "recorded"


def _event_reason(item: Dict[str, Any]) -> str:
    for key in ["human_reason", "reason_code", "soulaana_translation", "event_type", "decision"]:
        value = item.get(key)
        if isinstance(value, str) and value:
            return value
    return "Security event recorded."


def _severity_for(source: str, item: Dict[str, Any]) -> str:
    text = json.dumps(item, sort_keys=True, default=str).lower()
    decision = _event_decision(item).lower()

    if "lockdown" in text or "raw_secret_rejected" in text or "deny" == decision:
        return "high"
    if "step_up" in text or "quarantine" in text or "rejected" in text or "denied" in text:
        return "medium"
    if "summary_only" in text or "receipt" in text or "export" in text:
        return "watch"
    return "info"


def _needs_owner_review(source: str, item: Dict[str, Any]) -> bool:
    severity = _severity_for(source, item)
    text = json.dumps(item, sort_keys=True, default=str).lower()
    if severity in {"high", "medium"}:
        return True
    if "owner" in text and ("receipt" in text or "admin" in text or "export" in text):
        return True
    return False


def _make_inbox_item(source: str, item: Dict[str, Any], index: int) -> Dict[str, Any]:
    safe_item = _redact(item if isinstance(item, dict) else {"value": item})
    item_id_source = {
        "source": source,
        "index": index,
        "event_id": safe_item.get("event_id") or safe_item.get("receipt_id") or safe_item.get("id") or "",
        "created_at": _event_time(safe_item),
        "decision": _event_decision(safe_item),
    }

    return {
        "inbox_item_id": "security_inbox_" + _fingerprint(item_id_source)[:18],
        "source": source,
        "created_at": _event_time(safe_item),
        "decision": _event_decision(safe_item),
        "severity": _severity_for(source, safe_item),
        "needs_owner_review": _needs_owner_review(source, safe_item),
        "human_reason": _event_reason(safe_item),
        "object_type": safe_item.get("object_type", ""),
        "object_id": safe_item.get("object_id", ""),
        "actor_user_id": safe_item.get("actor_user_id", safe_item.get("user_id", "")),
        "route_path": safe_item.get("route_path", ""),
        "event_type": safe_item.get("event_type", ""),
        "safe_summary": {
            key: safe_item.get(key)
            for key in [
                "decision",
                "status",
                "reason_code",
                "object_type",
                "object_id",
                "action",
                "route_path",
                "event_type",
                "pack",
                "readiness_score",
            ]
            if key in safe_item
        },
    }


def _collect_from_path(source: str, path: Path, limit: int = 40) -> Dict[str, Any]:
    data = _load_json(path, [])
    items = _as_list(data)
    recent = items[-limit:] if len(items) > limit else items

    inbox_items = []
    for idx, item in enumerate(recent):
        if isinstance(item, dict):
            inbox_items.append(_make_inbox_item(source, item, idx))
        else:
            inbox_items.append(_make_inbox_item(source, {"value": item}, idx))

    return {
        "source": source,
        "path": str(path),
        "exists": path.exists(),
        "raw_count": len(items),
        "collected_count": len(inbox_items),
        "items": inbox_items,
    }


def build_security_inbox_owner_queue(limit_per_source: int = 40, write_panel: bool = True) -> Dict[str, Any]:
    try:
        limit_per_source = int(limit_per_source)
    except Exception:
        limit_per_source = 40
    limit_per_source = max(1, min(limit_per_source, 120))

    sources = [
        _collect_from_path("object_permission_events", OBJECT_EVENTS_PATH, limit_per_source),
        _collect_from_path("redaction_reveal_receipts", REVEAL_RECEIPTS_PATH, limit_per_source),
        _collect_from_path("secrets_boundary_events", SECRETS_EVENTS_PATH, limit_per_source),
        _collect_from_path("owner_admin_receipts", OWNER_ADMIN_RECEIPTS_PATH, limit_per_source),
        _collect_from_path("tamper_audit_chain", TAMPER_CHAIN_PATH, limit_per_source),
        _collect_from_path("security_rehearsal_status", SECURITY_REHEARSAL_STATUS_PATH, limit_per_source),
        _collect_from_path("owner_ui_checkpoint_status", OWNER_UI_CHECKPOINT_STATUS_PATH, limit_per_source),
    ]

    all_items: List[Dict[str, Any]] = []
    for source in sources:
        all_items.extend(source.get("items", []))

    severity_order = {"high": 0, "medium": 1, "watch": 2, "info": 3}
    all_items = sorted(
        all_items,
        key=lambda item: (
            severity_order.get(item.get("severity", "info"), 9),
            item.get("created_at", ""),
        ),
        reverse=False,
    )

    by_source: Dict[str, int] = {}
    by_severity: Dict[str, int] = {}
    by_decision: Dict[str, int] = {}
    owner_review_count = 0

    for item in all_items:
        by_source[item.get("source", "unknown")] = by_source.get(item.get("source", "unknown"), 0) + 1
        by_severity[item.get("severity", "info")] = by_severity.get(item.get("severity", "info"), 0) + 1
        by_decision[item.get("decision", "recorded")] = by_decision.get(item.get("decision", "recorded"), 0) + 1
        if item.get("needs_owner_review"):
            owner_review_count += 1

    checks = {
        "sources_collected": len(sources) >= 7,
        "has_owner_ui_checkpoint_source": any(source.get("source") == "owner_ui_checkpoint_status" for source in sources),
        "all_items_safe_list": isinstance(all_items, list),
        "status_path_ready": True,
        "panel_path_ready": True,
    }

    failed_checks = [key for key, ok in checks.items() if not ok]

    status = {
        "ok": not failed_checks,
        "pack": "121",
        "status": "passed" if not failed_checks else "failed",
        "created_at": _utc_now(),
        "status_path": str(SECURITY_INBOX_STATUS_PATH),
        "panel_path": str(SECURITY_INBOX_PANEL_PATH),
        "sources": [
            {
                "source": source.get("source"),
                "path": source.get("path"),
                "exists": source.get("exists"),
                "raw_count": source.get("raw_count"),
                "collected_count": source.get("collected_count"),
            }
            for source in sources
        ],
        "source_count": len(sources),
        "inbox_count": len(all_items),
        "owner_review_count": owner_review_count,
        "by_source": by_source,
        "by_severity": by_severity,
        "by_decision": by_decision,
        "recent_items": all_items[:80],
        "checks": checks,
        "failed_checks": failed_checks,
        "readiness_score": 100 if not failed_checks else max(0, 100 - (len(failed_checks) * 10)),
        "readiness_label": (
            "Tower Security Inbox owner queue ready"
            if not failed_checks
            else "Tower Security Inbox owner queue needs review"
        ),
        "human_reason": "Tower Security Inbox collects important security events into one owner review queue without exposing secrets.",
        "soulaana_translation": "Soulaana: The Tower has an inbox now. Suspicious, important, and owner-review events have somewhere to land.",
    }

    status = _redact(status)
    scan = _safe_scan(status)
    status["no_secret_leakage"] = scan.get("ok") is True
    status["leakage_scan"] = scan
    status["status_fingerprint"] = _fingerprint(status)

    _write_json(SECURITY_INBOX_STATUS_PATH, status)

    try:
        from tower.tamper_evident_audit_chain import create_tamper_chain_entry
        create_tamper_chain_entry(
            event_type="tower_security_inbox_owner_queue",
            source_name="security_inbox_owner_queue_status",
            source_path=str(SECURITY_INBOX_STATUS_PATH),
            source_hash=_fingerprint(status),
            record_count=int(status.get("inbox_count", 0) or 0),
            actor_user_id="tower_system",
            reason="Pack 121 Tower Security Inbox owner queue generated.",
            metadata={
                "pack": "121",
                "status": status.get("status"),
                "inbox_count": status.get("inbox_count"),
                "owner_review_count": status.get("owner_review_count"),
                "readiness_score": status.get("readiness_score"),
            },
        )
    except Exception:
        pass

    if write_panel:
        write_security_inbox_owner_queue_panel(status)

    return status


def render_security_inbox_owner_queue_section(status: Dict[str, Any] | None = None) -> str:
    status = status if isinstance(status, dict) else build_security_inbox_owner_queue(write_panel=False)
    items = status.get("recent_items", []) if isinstance(status.get("recent_items"), list) else []

    card_html = []
    for item in items[:24]:
        if not isinstance(item, dict):
            continue
        severity = _html_escape(item.get("severity", "info"))
        source = _html_escape(item.get("source", "source"))
        decision = _html_escape(item.get("decision", "recorded"))
        reason = _html_escape(item.get("human_reason", "Security event recorded."))
        obj = _html_escape(item.get("object_id", "") or item.get("route_path", "") or item.get("event_type", ""))
        review = "REVIEW" if item.get("needs_owner_review") else "LOGGED"

        card_html.append(f"""
        <article class="security-inbox-card security-inbox-card--{severity}">
          <div class="security-inbox-card__eyebrow">{review} · {severity} · {source}</div>
          <h3>{decision}</h3>
          <p>{reason}</p>
          <small>{obj}</small>
        </article>
        """)

    if not card_html:
        card_html.append("""
        <article class="security-inbox-card security-inbox-card--info">
          <div class="security-inbox-card__eyebrow">LOGGED · INFO · EMPTY</div>
          <h3>No inbox items yet</h3>
          <p>The Security Inbox is ready. Events will appear here as Tower systems record them.</p>
        </article>
        """)

    html = f"""
<!-- PACK121_SECURITY_INBOX_OWNER_QUEUE_SECTION -->
<section class="security-inbox-owner-queue" data-pack="121">
  <style>
    .security-inbox-owner-queue {{
      margin: 24px 0;
      border: 1px solid rgba(220,183,94,.34);
      border-radius: 28px;
      padding: 22px;
      background:
        radial-gradient(circle at top left, rgba(220,183,94,.13), transparent 34%),
        linear-gradient(135deg, rgba(23,20,13,.78), rgba(8,9,7,.94));
      color: #f5ead2;
      box-shadow: 0 18px 70px rgba(0,0,0,.32);
    }}
    .security-inbox-owner-queue__eyebrow {{
      color: rgba(220,183,94,.86);
      text-transform: uppercase;
      letter-spacing: .14em;
      font-size: 11px;
      margin-bottom: 8px;
    }}
    .security-inbox-owner-queue h2 {{
      margin: 0;
      font-size: 24px;
      letter-spacing: -.03em;
    }}
    .security-inbox-owner-queue p {{
      color: rgba(245,234,210,.72);
      line-height: 1.45;
    }}
    .security-inbox-stats {{
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 12px;
      margin-top: 14px;
    }}
    .security-inbox-stat {{
      border: 1px solid rgba(245,234,210,.13);
      border-radius: 18px;
      padding: 12px;
      background: rgba(255,255,255,.04);
    }}
    .security-inbox-stat b {{
      display: block;
      font-size: 22px;
    }}
    .security-inbox-stat span {{
      color: rgba(245,234,210,.62);
      font-size: 12px;
    }}
    .security-inbox-grid {{
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 12px;
      margin-top: 14px;
    }}
    .security-inbox-card {{
      border: 1px solid rgba(245,234,210,.13);
      border-radius: 20px;
      padding: 14px;
      background: rgba(255,255,255,.04);
    }}
    .security-inbox-card--high {{
      border-color: rgba(255,128,128,.58);
    }}
    .security-inbox-card--medium {{
      border-color: rgba(220,183,94,.58);
    }}
    .security-inbox-card--watch {{
      border-color: rgba(168,175,255,.48);
    }}
    .security-inbox-card--info {{
      border-color: rgba(143,221,158,.32);
    }}
    .security-inbox-card__eyebrow {{
      color: rgba(220,183,94,.84);
      text-transform: uppercase;
      letter-spacing: .12em;
      font-size: 10px;
      margin-bottom: 7px;
    }}
    .security-inbox-card h3 {{
      margin: 0 0 7px;
      font-size: 16px;
    }}
    .security-inbox-card p {{
      margin: 0 0 8px;
      color: rgba(245,234,210,.72);
    }}
    .security-inbox-card small {{
      color: rgba(245,234,210,.55);
    }}
    @media (max-width: 900px) {{
      .security-inbox-stats,
      .security-inbox-grid {{
        grid-template-columns: 1fr;
      }}
    }}
  </style>

  <div class="security-inbox-owner-queue__eyebrow">PACK 121 · SECURITY INBOX</div>
  <h2>Tower Security Inbox</h2>
  <p>{_html_escape(status.get('human_reason', 'Tower Security Inbox loaded.'))}</p>

  <div class="security-inbox-stats">
    <div class="security-inbox-stat"><b>{_html_escape(status.get('inbox_count', 0))}</b><span>Inbox Items</span></div>
    <div class="security-inbox-stat"><b>{_html_escape(status.get('owner_review_count', 0))}</b><span>Owner Review</span></div>
    <div class="security-inbox-stat"><b>{_html_escape(status.get('source_count', 0))}</b><span>Sources</span></div>
    <div class="security-inbox-stat"><b>{_html_escape(status.get('readiness_score', 0))}</b><span>Readiness</span></div>
  </div>

  <div class="security-inbox-grid">
    {''.join(card_html)}
  </div>
</section>
<!-- END PACK121_SECURITY_INBOX_OWNER_QUEUE_SECTION -->
"""
    return html


def write_security_inbox_owner_queue_panel(status: Dict[str, Any] | None = None) -> Dict[str, Any]:
    status = status if isinstance(status, dict) else build_security_inbox_owner_queue(write_panel=False)
    html = f"""<!doctype html>
<html lang="en">
<head><meta charset="utf-8"><title>The Tower · Security Inbox</title></head>
<body style="margin:0;background:#080907;color:#f5ead2;font-family:system-ui;padding:32px;">
<main style="max-width:1180px;margin:auto;">
{render_security_inbox_owner_queue_section(status)}
</main>
</body>
</html>
"""
    _write_text(SECURITY_INBOX_PANEL_PATH, html)
    return {
        "ok": True,
        "pack": "121",
        "decision": "security_inbox_owner_queue_panel_written",
        "path": str(SECURITY_INBOX_PANEL_PATH),
        "human_reason": "Tower Security Inbox panel written.",
        "soulaana_translation": "Soulaana: Security Inbox panel posted.",
    }


def load_security_inbox_owner_queue() -> Dict[str, Any]:
    status = _load_json(SECURITY_INBOX_STATUS_PATH, {})
    if not status:
        status = build_security_inbox_owner_queue(write_panel=True)
    return status


def security_inbox_owner_queue_status_card() -> Dict[str, Any]:
    status = load_security_inbox_owner_queue()
    return {
        "ok": status.get("ok") is True,
        "pack": "121",
        "title": "Tower Security Inbox",
        "readiness_score": status.get("readiness_score", 0),
        "inbox_count": status.get("inbox_count", 0),
        "owner_review_count": status.get("owner_review_count", 0),
        "source_count": status.get("source_count", 0),
        "panel_path": status.get("panel_path", str(SECURITY_INBOX_PANEL_PATH)),
        "status_path": status.get("status_path", str(SECURITY_INBOX_STATUS_PATH)),
        "human_reason": "Tower Security Inbox status card loaded.",
        "soulaana_translation": "Soulaana: Security Inbox is visible.",
    }


def reset_security_inbox_owner_queue_for_test() -> Dict[str, Any]:
    _write_json(SECURITY_INBOX_STATUS_PATH, {
        "ok": True,
        "pack": "121",
        "reset_at": _utc_now(),
        "human_reason": "Tower Security Inbox reset for test.",
    })
    if SECURITY_INBOX_PANEL_PATH.exists():
        try:
            SECURITY_INBOX_PANEL_PATH.unlink()
        except Exception:
            pass
    return {
        "ok": True,
        "decision": "security_inbox_owner_queue_reset_for_test",
        "soulaana_translation": "Soulaana: Security Inbox reset for a clean test lane.",
    }
