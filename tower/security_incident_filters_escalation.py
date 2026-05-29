
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "tower" / "data"

INCIDENT_FILTERS_STATUS_PATH = DATA_DIR / "security_incident_filters_escalation_status.json"
INCIDENT_FILTERS_PANEL_PATH = DATA_DIR / "security_incident_filters_escalation_panel.html"

OPEN_STATUSES = {"new", "triaged", "investigating", "contained", "monitoring"}
CLOSED_STATUSES = {"resolved", "false_alarm", "archived"}
ESCALATION_STATUSES = {"new", "triaged", "investigating", "contained"}
ESCALATION_SEVERITIES = {"critical", "high"}


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

            if isinstance(redacted_item, dict) and "__redacted_incident_filter_field_count__" in redacted_item:
                try:
                    redacted_count += int(redacted_item.get("__redacted_incident_filter_field_count__", 0))
                except Exception:
                    redacted_count += 1
                redacted_item = dict(redacted_item)
                redacted_item.pop("__redacted_incident_filter_field_count__", None)

            clean[key] = redacted_item

        if redacted_count:
            clean["__redacted_incident_filter_field_count__"] = redacted_count
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
            return "[REDACTED_INCIDENT_FILTER_VALUE]"
        return value

    return value


def _get_incidents(limit: int = 200) -> List[Dict[str, Any]]:
    try:
        from tower.security_incident_desk import build_security_incident_desk_status

        status = build_security_incident_desk_status(write_panel=True)
        incidents = status.get("incident_candidates", [])
        if isinstance(incidents, list):
            return [item for item in incidents[:limit] if isinstance(item, dict)]
    except Exception:
        pass
    return []


def _incident_sort_score(item: Dict[str, Any]) -> int:
    score = 0

    severity = str(item.get("severity", "medium")).lower()
    status = str(item.get("incident_status", "new")).lower()
    priority = int(item.get("priority_score", 0) or 0)

    if severity == "critical":
        score += 120
    elif severity == "high":
        score += 95
    elif severity == "medium":
        score += 65
    elif severity == "low":
        score += 35
    else:
        score += 10

    if status == "new":
        score += 35
    elif status == "triaged":
        score += 25
    elif status == "investigating":
        score += 30
    elif status == "contained":
        score += 28
    elif status == "monitoring":
        score += 18
    elif status in CLOSED_STATUSES:
        score -= 45

    score += min(priority // 3, 50)

    if item.get("incident_state_source") == "saved_state":
        score += 5

    return max(0, min(score, 240))


def _escalation_readiness(item: Dict[str, Any]) -> Dict[str, Any]:
    severity = str(item.get("severity", "medium")).lower()
    status = str(item.get("incident_status", "new")).lower()
    score = int(item.get("incident_sort_score", _incident_sort_score(item)) or 0)

    reasons = []

    if severity == "critical":
        reasons.append("critical_severity")
    elif severity == "high":
        reasons.append("high_severity")

    if status in {"new", "triaged"}:
        reasons.append("needs_owner_triage")
    elif status == "investigating":
        reasons.append("investigation_active")
    elif status == "contained":
        reasons.append("containment_needs_resolution_or_monitoring")

    if score >= 150:
        reasons.append("high_priority_score")

    is_ready = bool(reasons) and status in ESCALATION_STATUSES and severity in {"critical", "high", "medium"}

    next_action = "review"
    if status == "new":
        next_action = "triage"
    elif status == "triaged":
        next_action = "investigate_or_contain"
    elif status == "investigating":
        next_action = "contain_or_resolve"
    elif status == "contained":
        next_action = "monitor_or_resolve"
    elif status in CLOSED_STATUSES:
        next_action = "archive_or_keep_for_record"

    label = "Escalation Ready" if is_ready else "Monitor"

    return {
        "is_escalation_ready": is_ready,
        "escalation_reasons": reasons,
        "next_action": next_action,
        "escalation_label": label,
    }


def _enrich(item: Dict[str, Any]) -> Dict[str, Any]:
    safe = dict(item)
    safe["incident_sort_score"] = _incident_sort_score(safe)
    safe.update(_escalation_readiness(safe))
    return safe


def _sort(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    enriched = [_enrich(item) for item in items]
    return sorted(
        enriched,
        key=lambda item: (
            int(item.get("incident_sort_score", 0) or 0),
            str(item.get("updated_at", "") or item.get("created_at", "")),
        ),
        reverse=True,
    )


def _filter(items: List[Dict[str, Any]], view: str) -> List[Dict[str, Any]]:
    view = str(view or "").strip().lower()

    if view == "critical":
        return [item for item in items if str(item.get("severity", "")).lower() == "critical"]

    if view == "high":
        return [item for item in items if str(item.get("severity", "")).lower() == "high"]

    if view == "open":
        return [item for item in items if str(item.get("incident_status", "")).lower() in OPEN_STATUSES]

    if view == "triaged":
        return [item for item in items if str(item.get("incident_status", "")).lower() == "triaged"]

    if view == "investigating":
        return [item for item in items if str(item.get("incident_status", "")).lower() == "investigating"]

    if view == "contained":
        return [item for item in items if str(item.get("incident_status", "")).lower() == "contained"]

    if view == "resolved":
        return [item for item in items if str(item.get("incident_status", "")).lower() == "resolved"]

    if view == "closed":
        return [item for item in items if str(item.get("incident_status", "")).lower() in CLOSED_STATUSES]

    if view == "escalation_ready":
        return [item for item in items if item.get("is_escalation_ready") is True]

    return items


def _count_by(items: List[Dict[str, Any]], field: str) -> Dict[str, int]:
    counts: Dict[str, int] = {}
    for item in items:
        value = str(item.get(field, "") or "unknown")
        counts[value] = counts.get(value, 0) + 1
    return counts


def build_security_incident_filters_escalation_status(write_panel: bool = True) -> Dict[str, Any]:
    base = _get_incidents(limit=240)
    sorted_items = _sort(base)

    views = {
        "all": sorted_items,
        "critical": _filter(sorted_items, "critical"),
        "high": _filter(sorted_items, "high"),
        "open": _filter(sorted_items, "open"),
        "triaged": _filter(sorted_items, "triaged"),
        "investigating": _filter(sorted_items, "investigating"),
        "contained": _filter(sorted_items, "contained"),
        "resolved": _filter(sorted_items, "resolved"),
        "closed": _filter(sorted_items, "closed"),
        "escalation_ready": _filter(sorted_items, "escalation_ready"),
    }

    view_counts = {key: len(value) for key, value in views.items()}
    escalation_ready_items = views["escalation_ready"]

    by_status = _count_by(sorted_items, "incident_status")
    by_severity = _count_by(sorted_items, "severity")
    by_source = _count_by(sorted_items, "source")
    by_next_action = _count_by(sorted_items, "next_action")

    checks = {
        "incidents_loaded": isinstance(base, list),
        "sort_scores_generated": all("incident_sort_score" in item for item in sorted_items),
        "escalation_flags_generated": all("is_escalation_ready" in item for item in sorted_items),
        "has_all_view": "all" in views,
        "has_open_view": "open" in views,
        "has_escalation_ready_view": "escalation_ready" in views,
        "view_counts_ready": isinstance(view_counts, dict),
        "status_counts_ready": isinstance(by_status, dict),
        "severity_counts_ready": isinstance(by_severity, dict),
        "next_action_counts_ready": isinstance(by_next_action, dict),
    }

    failed_checks = [key for key, ok in checks.items() if not ok]

    status = {
        "ok": not failed_checks,
        "pack": "128",
        "status": "passed" if not failed_checks else "failed",
        "created_at": _utc_now(),
        "status_path": str(INCIDENT_FILTERS_STATUS_PATH),
        "panel_path": str(INCIDENT_FILTERS_PANEL_PATH),
        "incident_count": len(sorted_items),
        "open_incident_count": view_counts.get("open", 0),
        "critical_count": view_counts.get("critical", 0),
        "high_count": view_counts.get("high", 0),
        "triaged_count": view_counts.get("triaged", 0),
        "investigating_count": view_counts.get("investigating", 0),
        "contained_count": view_counts.get("contained", 0),
        "resolved_count": view_counts.get("resolved", 0),
        "closed_count": view_counts.get("closed", 0),
        "escalation_ready_count": view_counts.get("escalation_ready", 0),
        "view_counts": view_counts,
        "views_available": sorted(views.keys()),
        "by_status": by_status,
        "by_severity": by_severity,
        "by_source": by_source,
        "by_next_action": by_next_action,
        "top_incidents": sorted_items[:60],
        "escalation_ready_items": escalation_ready_items[:60],
        "checks": checks,
        "failed_checks": failed_checks,
        "readiness_score": 100 if not failed_checks else max(0, 100 - (len(failed_checks) * 10)),
        "readiness_label": (
            "Incident Desk filters/escalation readiness ready"
            if not failed_checks
            else "Incident Desk filters/escalation readiness needs review"
        ),
        "human_reason": "Incident Desk filters and escalation readiness are ready so serious incidents rise above routine security noise.",
        "soulaana_translation": "Soulaana: The Incident Desk can now show what needs owner attention first.",
    }

    status = _redact(status)
    scan = _safe_scan(status)
    status["no_secret_leakage"] = scan.get("ok") is True
    status["leakage_scan"] = scan
    status["status_fingerprint"] = _fingerprint(status)

    _write_json(INCIDENT_FILTERS_STATUS_PATH, status)

    try:
        from tower.tamper_evident_audit_chain import create_tamper_chain_entry
        create_tamper_chain_entry(
            event_type="tower_security_incident_filters_escalation",
            source_name="security_incident_filters_escalation_status",
            source_path=str(INCIDENT_FILTERS_STATUS_PATH),
            source_hash=_fingerprint(status),
            record_count=int(status.get("incident_count", 0) or 0),
            actor_user_id="tower_system",
            reason="Pack 128 Incident Desk filters/escalation readiness generated.",
            metadata={
                "pack": "128",
                "status": status.get("status"),
                "incident_count": status.get("incident_count"),
                "escalation_ready_count": status.get("escalation_ready_count"),
                "readiness_score": status.get("readiness_score"),
            },
        )
    except Exception:
        pass

    if write_panel:
        write_security_incident_filters_escalation_panel(status)

    return status


def render_security_incident_filters_escalation_section(status: Dict[str, Any] | None = None) -> str:
    status = status if isinstance(status, dict) else build_security_incident_filters_escalation_status(write_panel=False)
    incidents = status.get("top_incidents", []) if isinstance(status.get("top_incidents"), list) else []

    cards = []
    for item in incidents[:24]:
        if not isinstance(item, dict):
            continue

        severity = _html_escape(item.get("severity", "medium"))
        incident_status = _html_escape(item.get("incident_status", "new"))
        next_action = _html_escape(item.get("next_action", "review"))
        score = _html_escape(item.get("incident_sort_score", 0))
        incident_id = _html_escape(item.get("incident_id", ""))
        reason = _html_escape(item.get("human_reason", "Security incident recorded."))
        esc = "ESCALATE" if item.get("is_escalation_ready") else "MONITOR"

        cards.append(f"""
        <article class="incident-filter-card incident-filter-card--{severity}">
          <div class="incident-filter-card__eyebrow">{esc} · P{score} · {severity} · {incident_status}</div>
          <h3>{incident_id}</h3>
          <p>{reason}</p>
          <small>Next: {next_action}</small>
        </article>
        """)

    if not cards:
        cards.append("""
        <article class="incident-filter-card incident-filter-card--info">
          <div class="incident-filter-card__eyebrow">MONITOR · P0 · INFO</div>
          <h3>No incidents yet</h3>
          <p>Incident filters are ready. Incidents will appear here once the Incident Desk has candidates.</p>
        </article>
        """)

    html = f"""
<!-- PACK128_SECURITY_INCIDENT_FILTERS_ESCALATION_SECTION -->
<section class="security-incident-filters-escalation" data-pack="128">
  <style>
    .security-incident-filters-escalation {{
      margin: 24px 0;
      border: 1px solid rgba(255,168,128,.4);
      border-radius: 28px;
      padding: 22px;
      background:
        radial-gradient(circle at top right, rgba(255,168,128,.15), transparent 34%),
        linear-gradient(135deg, rgba(42,19,10,.84), rgba(8,9,7,.94));
      color: #f5ead2;
      box-shadow: 0 18px 70px rgba(0,0,0,.32);
    }}
    .security-incident-filters-escalation__eyebrow {{
      color: rgba(255,168,128,.92);
      text-transform: uppercase;
      letter-spacing: .14em;
      font-size: 11px;
      margin-bottom: 8px;
    }}
    .security-incident-filters-escalation h2 {{
      margin: 0;
      font-size: 24px;
      letter-spacing: -.03em;
    }}
    .security-incident-filters-escalation p {{
      color: rgba(245,234,210,.72);
      line-height: 1.45;
    }}
    .incident-filter-stats {{
      display: grid;
      grid-template-columns: repeat(5, minmax(0, 1fr));
      gap: 12px;
      margin-top: 14px;
    }}
    .incident-filter-stat {{
      border: 1px solid rgba(245,234,210,.13);
      border-radius: 18px;
      padding: 12px;
      background: rgba(255,255,255,.04);
    }}
    .incident-filter-stat b {{
      display: block;
      font-size: 22px;
    }}
    .incident-filter-stat span {{
      color: rgba(245,234,210,.62);
      font-size: 12px;
    }}
    .incident-filter-grid {{
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 12px;
      margin-top: 14px;
    }}
    .incident-filter-card {{
      border: 1px solid rgba(245,234,210,.13);
      border-radius: 20px;
      padding: 14px;
      background: rgba(255,255,255,.04);
    }}
    .incident-filter-card--critical {{
      border-color: rgba(255,80,80,.82);
    }}
    .incident-filter-card--high {{
      border-color: rgba(255,128,128,.65);
    }}
    .incident-filter-card--medium {{
      border-color: rgba(220,183,94,.62);
    }}
    .incident-filter-card--low {{
      border-color: rgba(168,175,255,.52);
    }}
    .incident-filter-card--info {{
      border-color: rgba(143,221,158,.34);
    }}
    .incident-filter-card__eyebrow {{
      color: rgba(255,168,128,.9);
      text-transform: uppercase;
      letter-spacing: .12em;
      font-size: 10px;
      margin-bottom: 7px;
    }}
    .incident-filter-card h3 {{
      margin: 0 0 7px;
      font-size: 16px;
      word-break: break-word;
    }}
    .incident-filter-card p {{
      margin: 0 0 8px;
      color: rgba(245,234,210,.72);
    }}
    .incident-filter-card small {{
      color: rgba(245,234,210,.55);
      word-break: break-word;
    }}
    @media (max-width: 1000px) {{
      .incident-filter-stats,
      .incident-filter-grid {{
        grid-template-columns: 1fr;
      }}
    }}
  </style>

  <div class="security-incident-filters-escalation__eyebrow">PACK 128 · INCIDENT FILTERS + ESCALATION</div>
  <h2>Incident Filters & Escalation Readiness</h2>
  <p>{_html_escape(status.get('human_reason', 'Incident filters loaded.'))}</p>

  <div class="incident-filter-stats">
    <div class="incident-filter-stat"><b>{_html_escape(status.get('incident_count', 0))}</b><span>Total Incidents</span></div>
    <div class="incident-filter-stat"><b>{_html_escape(status.get('open_incident_count', 0))}</b><span>Open</span></div>
    <div class="incident-filter-stat"><b>{_html_escape(status.get('critical_count', 0))}</b><span>Critical</span></div>
    <div class="incident-filter-stat"><b>{_html_escape(status.get('high_count', 0))}</b><span>High</span></div>
    <div class="incident-filter-stat"><b>{_html_escape(status.get('escalation_ready_count', 0))}</b><span>Escalation Ready</span></div>
  </div>

  <div class="incident-filter-grid">
    {''.join(cards)}
  </div>
</section>
<!-- END PACK128_SECURITY_INCIDENT_FILTERS_ESCALATION_SECTION -->
"""
    return html


def write_security_incident_filters_escalation_panel(status: Dict[str, Any] | None = None) -> Dict[str, Any]:
    status = status if isinstance(status, dict) else build_security_incident_filters_escalation_status(write_panel=False)
    html = f"""<!doctype html>
<html lang="en">
<head><meta charset="utf-8"><title>The Tower · Incident Filters</title></head>
<body style="margin:0;background:#080907;color:#f5ead2;font-family:system-ui;padding:32px;">
<main style="max-width:1180px;margin:auto;">
{render_security_incident_filters_escalation_section(status)}
</main>
</body>
</html>
"""
    _write_text(INCIDENT_FILTERS_PANEL_PATH, html)
    return {
        "ok": True,
        "pack": "128",
        "decision": "security_incident_filters_escalation_panel_written",
        "path": str(INCIDENT_FILTERS_PANEL_PATH),
        "human_reason": "Incident filters/escalation panel written.",
        "soulaana_translation": "Soulaana: Incident filters board posted.",
    }


def load_security_incident_filters_escalation_status() -> Dict[str, Any]:
    status = _load_json(INCIDENT_FILTERS_STATUS_PATH, {})
    if not status:
        status = build_security_incident_filters_escalation_status(write_panel=True)
    return status


def security_incident_filters_escalation_status_card() -> Dict[str, Any]:
    status = load_security_incident_filters_escalation_status()
    return {
        "ok": status.get("ok") is True,
        "pack": "128",
        "title": "Incident Filters & Escalation",
        "readiness_score": status.get("readiness_score", 0),
        "incident_count": status.get("incident_count", 0),
        "open_incident_count": status.get("open_incident_count", 0),
        "critical_count": status.get("critical_count", 0),
        "high_count": status.get("high_count", 0),
        "escalation_ready_count": status.get("escalation_ready_count", 0),
        "panel_path": status.get("panel_path", str(INCIDENT_FILTERS_PANEL_PATH)),
        "status_path": status.get("status_path", str(INCIDENT_FILTERS_STATUS_PATH)),
        "human_reason": "Incident filters/escalation status card loaded.",
        "soulaana_translation": "Soulaana: Incident filters are visible.",
    }


def reset_security_incident_filters_escalation_for_test() -> Dict[str, Any]:
    _write_json(INCIDENT_FILTERS_STATUS_PATH, {
        "ok": True,
        "pack": "128",
        "reset_at": _utc_now(),
        "human_reason": "Incident filters/escalation reset for test.",
    })
    if INCIDENT_FILTERS_PANEL_PATH.exists():
        try:
            INCIDENT_FILTERS_PANEL_PATH.unlink()
        except Exception:
            pass
    return {
        "ok": True,
        "decision": "security_incident_filters_escalation_reset_for_test",
        "soulaana_translation": "Soulaana: Incident filters reset for a clean test lane.",
    }
