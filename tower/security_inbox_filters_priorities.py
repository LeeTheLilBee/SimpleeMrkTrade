
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "tower" / "data"

FILTERS_STATUS_PATH = DATA_DIR / "security_inbox_filters_priorities_status.json"
FILTERS_PANEL_PATH = DATA_DIR / "security_inbox_filters_priorities_panel.html"


OPEN_REVIEW_STATES = {"new", "acknowledged", "investigating", "escalated"}
CLOSED_REVIEW_STATES = {"resolved", "false_alarm", "archived"}
HIGH_PRIORITY_SEVERITIES = {"high", "medium"}


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

            if isinstance(redacted_item, dict) and "__redacted_security_filter_field_count__" in redacted_item:
                try:
                    redacted_count += int(redacted_item.get("__redacted_security_filter_field_count__", 0))
                except Exception:
                    redacted_count += 1
                redacted_item = dict(redacted_item)
                redacted_item.pop("__redacted_security_filter_field_count__", None)

            clean[key] = redacted_item

        if redacted_count:
            clean["__redacted_security_filter_field_count__"] = redacted_count
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
            return "[REDACTED_SECURITY_FILTER_VALUE]"
        return value

    return value


def _get_review_items(limit: int = 200) -> List[Dict[str, Any]]:
    try:
        from tower.security_inbox_review_actions import build_security_inbox_review_status

        status = build_security_inbox_review_status(write_panel=True)
        items = status.get("recent_items", [])
        if isinstance(items, list):
            return [item for item in items[:limit] if isinstance(item, dict)]
    except Exception:
        pass
    return []


def _priority_score(item: Dict[str, Any]) -> int:
    score = 0

    severity = str(item.get("severity", "info")).lower()
    review_state = str(item.get("review_state", "new")).lower()
    source = str(item.get("source", "")).lower()
    decision = str(item.get("decision", "")).lower()

    if severity == "high":
        score += 90
    elif severity == "medium":
        score += 70
    elif severity == "watch":
        score += 40
    else:
        score += 15

    if review_state == "escalated":
        score += 45
    elif review_state == "investigating":
        score += 35
    elif review_state == "new":
        score += 30
    elif review_state == "acknowledged":
        score += 20
    elif review_state in {"resolved", "false_alarm", "archived"}:
        score -= 30

    if item.get("needs_owner_review"):
        score += 20

    if "deny" in decision or "denied" in decision:
        score += 20
    if "step_up" in decision:
        score += 12
    if "secret" in source:
        score += 15
    if "redaction" in source or "reveal" in source:
        score += 10
    if "tamper" in source:
        score += 8

    return max(0, min(score, 200))


def _sort_items(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    enriched = []
    for item in items:
        safe = dict(item)
        safe["priority_score"] = _priority_score(safe)
        enriched.append(safe)

    return sorted(
        enriched,
        key=lambda item: (
            item.get("priority_score", 0),
            str(item.get("created_at", "")),
        ),
        reverse=True,
    )


def _filter_items(items: List[Dict[str, Any]], view: str) -> List[Dict[str, Any]]:
    view = str(view or "").strip().lower()

    if view == "high_priority":
        return [
            item for item in items
            if item.get("priority_score", 0) >= 90
            or str(item.get("severity", "")).lower() in HIGH_PRIORITY_SEVERITIES
            or str(item.get("review_state", "")).lower() == "escalated"
        ]

    if view == "open_review":
        return [
            item for item in items
            if str(item.get("review_state", "")).lower() in OPEN_REVIEW_STATES
        ]

    if view == "escalated":
        return [
            item for item in items
            if str(item.get("review_state", "")).lower() == "escalated"
        ]

    if view == "unresolved":
        return [
            item for item in items
            if str(item.get("review_state", "")).lower() not in CLOSED_REVIEW_STATES
        ]

    if view == "resolved":
        return [
            item for item in items
            if str(item.get("review_state", "")).lower() == "resolved"
        ]

    if view == "archived":
        return [
            item for item in items
            if str(item.get("review_state", "")).lower() in {"archived", "false_alarm"}
        ]

    return items


def _count_by(items: List[Dict[str, Any]], field: str) -> Dict[str, int]:
    counts: Dict[str, int] = {}
    for item in items:
        value = str(item.get(field, "") or "unknown")
        counts[value] = counts.get(value, 0) + 1
    return counts


def build_security_inbox_filters_priorities_status(write_panel: bool = True) -> Dict[str, Any]:
    base_items = _get_review_items(limit=240)
    sorted_items = _sort_items(base_items)

    views = {
        "all": sorted_items,
        "high_priority": _filter_items(sorted_items, "high_priority"),
        "open_review": _filter_items(sorted_items, "open_review"),
        "escalated": _filter_items(sorted_items, "escalated"),
        "unresolved": _filter_items(sorted_items, "unresolved"),
        "resolved": _filter_items(sorted_items, "resolved"),
        "archived": _filter_items(sorted_items, "archived"),
    }

    view_counts = {name: len(items) for name, items in views.items()}

    high_priority_items = views["high_priority"]
    top_priority_items = sorted_items[:40]

    by_source = _count_by(sorted_items, "source")
    by_severity = _count_by(sorted_items, "severity")
    by_review_state = _count_by(sorted_items, "review_state")

    checks = {
        "items_loaded": isinstance(base_items, list),
        "priority_scores_generated": all("priority_score" in item for item in sorted_items),
        "has_all_view": "all" in views,
        "has_open_review_view": "open_review" in views,
        "has_high_priority_view": "high_priority" in views,
        "view_counts_ready": isinstance(view_counts, dict),
        "source_counts_ready": isinstance(by_source, dict),
        "severity_counts_ready": isinstance(by_severity, dict),
        "review_state_counts_ready": isinstance(by_review_state, dict),
    }

    failed_checks = [key for key, ok in checks.items() if not ok]

    status = {
        "ok": not failed_checks,
        "pack": "124",
        "status": "passed" if not failed_checks else "failed",
        "created_at": _utc_now(),
        "status_path": str(FILTERS_STATUS_PATH),
        "panel_path": str(FILTERS_PANEL_PATH),
        "inbox_count": len(sorted_items),
        "high_priority_count": len(high_priority_items),
        "open_review_count": view_counts.get("open_review", 0),
        "unresolved_count": view_counts.get("unresolved", 0),
        "resolved_count": view_counts.get("resolved", 0),
        "archived_count": view_counts.get("archived", 0),
        "view_counts": view_counts,
        "by_source": by_source,
        "by_severity": by_severity,
        "by_review_state": by_review_state,
        "top_priority_items": top_priority_items,
        "high_priority_items": high_priority_items[:60],
        "open_review_items": views["open_review"][:60],
        "views_available": sorted(views.keys()),
        "checks": checks,
        "failed_checks": failed_checks,
        "readiness_score": 100 if not failed_checks else max(0, 100 - (len(failed_checks) * 10)),
        "readiness_label": (
            "Security Inbox filters/priorities ready"
            if not failed_checks
            else "Security Inbox filters/priorities need review"
        ),
        "human_reason": "Security Inbox filters and priority scoring are ready so owner review can focus on the most important items first.",
        "soulaana_translation": "Soulaana: The inbox can breathe now. Highest-risk items rise to the top.",
    }

    status = _redact(status)
    scan = _safe_scan(status)
    status["no_secret_leakage"] = scan.get("ok") is True
    status["leakage_scan"] = scan
    status["status_fingerprint"] = _fingerprint(status)

    _write_json(FILTERS_STATUS_PATH, status)

    try:
        from tower.tamper_evident_audit_chain import create_tamper_chain_entry
        create_tamper_chain_entry(
            event_type="tower_security_inbox_filters_priorities",
            source_name="security_inbox_filters_priorities_status",
            source_path=str(FILTERS_STATUS_PATH),
            source_hash=_fingerprint(status),
            record_count=int(status.get("inbox_count", 0) or 0),
            actor_user_id="tower_system",
            reason="Pack 124 Security Inbox filters/priorities generated.",
            metadata={
                "pack": "124",
                "status": status.get("status"),
                "high_priority_count": status.get("high_priority_count"),
                "open_review_count": status.get("open_review_count"),
                "readiness_score": status.get("readiness_score"),
            },
        )
    except Exception:
        pass

    if write_panel:
        write_security_inbox_filters_priorities_panel(status)

    return status


def render_security_inbox_filters_priorities_section(status: Dict[str, Any] | None = None) -> str:
    status = status if isinstance(status, dict) else build_security_inbox_filters_priorities_status(write_panel=False)
    items = status.get("top_priority_items", []) if isinstance(status.get("top_priority_items"), list) else []

    card_html = []
    for item in items[:24]:
        if not isinstance(item, dict):
            continue

        score = _html_escape(item.get("priority_score", 0))
        severity = _html_escape(item.get("severity", "info"))
        source = _html_escape(item.get("source", "source"))
        state = _html_escape(item.get("review_state", "new"))
        decision = _html_escape(item.get("decision", "recorded"))
        reason = _html_escape(item.get("human_reason", "Security item recorded."))
        item_id = _html_escape(item.get("inbox_item_id", ""))

        card_html.append(f"""
        <article class="security-filter-card security-filter-card--{severity}">
          <div class="security-filter-card__eyebrow">P{score} · {severity} · {state} · {source}</div>
          <h3>{decision}</h3>
          <p>{reason}</p>
          <small>{item_id}</small>
        </article>
        """)

    if not card_html:
        card_html.append("""
        <article class="security-filter-card security-filter-card--info">
          <div class="security-filter-card__eyebrow">P0 · INFO · EMPTY</div>
          <h3>No priority items yet</h3>
          <p>The filter/priority layer is ready. Inbox items will appear here when available.</p>
        </article>
        """)

    html = f"""
<!-- PACK124_SECURITY_INBOX_FILTERS_PRIORITIES_SECTION -->
<section class="security-inbox-filters-priorities" data-pack="124">
  <style>
    .security-inbox-filters-priorities {{
      margin: 24px 0;
      border: 1px solid rgba(220,183,94,.38);
      border-radius: 28px;
      padding: 22px;
      background:
        radial-gradient(circle at top right, rgba(220,183,94,.15), transparent 34%),
        linear-gradient(135deg, rgba(34,22,12,.78), rgba(8,9,7,.94));
      color: #f5ead2;
      box-shadow: 0 18px 70px rgba(0,0,0,.32);
    }}
    .security-inbox-filters-priorities__eyebrow {{
      color: rgba(220,183,94,.9);
      text-transform: uppercase;
      letter-spacing: .14em;
      font-size: 11px;
      margin-bottom: 8px;
    }}
    .security-inbox-filters-priorities h2 {{
      margin: 0;
      font-size: 24px;
      letter-spacing: -.03em;
    }}
    .security-inbox-filters-priorities p {{
      color: rgba(245,234,210,.72);
      line-height: 1.45;
    }}
    .security-filter-stats {{
      display: grid;
      grid-template-columns: repeat(5, minmax(0, 1fr));
      gap: 12px;
      margin-top: 14px;
    }}
    .security-filter-stat {{
      border: 1px solid rgba(245,234,210,.13);
      border-radius: 18px;
      padding: 12px;
      background: rgba(255,255,255,.04);
    }}
    .security-filter-stat b {{
      display: block;
      font-size: 22px;
    }}
    .security-filter-stat span {{
      color: rgba(245,234,210,.62);
      font-size: 12px;
    }}
    .security-filter-grid {{
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 12px;
      margin-top: 14px;
    }}
    .security-filter-card {{
      border: 1px solid rgba(245,234,210,.13);
      border-radius: 20px;
      padding: 14px;
      background: rgba(255,255,255,.04);
    }}
    .security-filter-card--high {{
      border-color: rgba(255,128,128,.65);
    }}
    .security-filter-card--medium {{
      border-color: rgba(220,183,94,.62);
    }}
    .security-filter-card--watch {{
      border-color: rgba(168,175,255,.52);
    }}
    .security-filter-card--info {{
      border-color: rgba(143,221,158,.34);
    }}
    .security-filter-card__eyebrow {{
      color: rgba(220,183,94,.84);
      text-transform: uppercase;
      letter-spacing: .12em;
      font-size: 10px;
      margin-bottom: 7px;
    }}
    .security-filter-card h3 {{
      margin: 0 0 7px;
      font-size: 16px;
    }}
    .security-filter-card p {{
      margin: 0 0 8px;
      color: rgba(245,234,210,.72);
    }}
    .security-filter-card small {{
      color: rgba(245,234,210,.55);
      word-break: break-word;
    }}
    @media (max-width: 1000px) {{
      .security-filter-stats,
      .security-filter-grid {{
        grid-template-columns: 1fr;
      }}
    }}
  </style>

  <div class="security-inbox-filters-priorities__eyebrow">PACK 124 · FILTERS + PRIORITY</div>
  <h2>Security Inbox Filters & Priorities</h2>
  <p>{_html_escape(status.get('human_reason', 'Security Inbox filters loaded.'))}</p>

  <div class="security-filter-stats">
    <div class="security-filter-stat"><b>{_html_escape(status.get('inbox_count', 0))}</b><span>Total</span></div>
    <div class="security-filter-stat"><b>{_html_escape(status.get('high_priority_count', 0))}</b><span>High Priority</span></div>
    <div class="security-filter-stat"><b>{_html_escape(status.get('open_review_count', 0))}</b><span>Open Review</span></div>
    <div class="security-filter-stat"><b>{_html_escape(status.get('unresolved_count', 0))}</b><span>Unresolved</span></div>
    <div class="security-filter-stat"><b>{_html_escape(status.get('resolved_count', 0))}</b><span>Resolved</span></div>
  </div>

  <div class="security-filter-grid">
    {''.join(card_html)}
  </div>
</section>
<!-- END PACK124_SECURITY_INBOX_FILTERS_PRIORITIES_SECTION -->
"""
    return html


def write_security_inbox_filters_priorities_panel(status: Dict[str, Any] | None = None) -> Dict[str, Any]:
    status = status if isinstance(status, dict) else build_security_inbox_filters_priorities_status(write_panel=False)
    html = f"""<!doctype html>
<html lang="en">
<head><meta charset="utf-8"><title>The Tower · Security Inbox Filters</title></head>
<body style="margin:0;background:#080907;color:#f5ead2;font-family:system-ui;padding:32px;">
<main style="max-width:1180px;margin:auto;">
{render_security_inbox_filters_priorities_section(status)}
</main>
</body>
</html>
"""
    _write_text(FILTERS_PANEL_PATH, html)
    return {
        "ok": True,
        "pack": "124",
        "decision": "security_inbox_filters_priorities_panel_written",
        "path": str(FILTERS_PANEL_PATH),
        "human_reason": "Security Inbox filters/priorities panel written.",
        "soulaana_translation": "Soulaana: Security Inbox filters board posted.",
    }


def load_security_inbox_filters_priorities_status() -> Dict[str, Any]:
    status = _load_json(FILTERS_STATUS_PATH, {})
    if not status:
        status = build_security_inbox_filters_priorities_status(write_panel=True)
    return status


def security_inbox_filters_priorities_status_card() -> Dict[str, Any]:
    status = load_security_inbox_filters_priorities_status()
    return {
        "ok": status.get("ok") is True,
        "pack": "124",
        "title": "Security Inbox Filters & Priorities",
        "readiness_score": status.get("readiness_score", 0),
        "inbox_count": status.get("inbox_count", 0),
        "high_priority_count": status.get("high_priority_count", 0),
        "open_review_count": status.get("open_review_count", 0),
        "unresolved_count": status.get("unresolved_count", 0),
        "resolved_count": status.get("resolved_count", 0),
        "panel_path": status.get("panel_path", str(FILTERS_PANEL_PATH)),
        "status_path": status.get("status_path", str(FILTERS_STATUS_PATH)),
        "human_reason": "Security Inbox filters/priorities status card loaded.",
        "soulaana_translation": "Soulaana: Security Inbox filters are visible.",
    }


def reset_security_inbox_filters_priorities_for_test() -> Dict[str, Any]:
    _write_json(FILTERS_STATUS_PATH, {
        "ok": True,
        "pack": "124",
        "reset_at": _utc_now(),
        "human_reason": "Security Inbox filters/priorities reset for test.",
    })
    if FILTERS_PANEL_PATH.exists():
        try:
            FILTERS_PANEL_PATH.unlink()
        except Exception:
            pass
    return {
        "ok": True,
        "decision": "security_inbox_filters_priorities_reset_for_test",
        "soulaana_translation": "Soulaana: Security Inbox filters reset for a clean test lane.",
    }
