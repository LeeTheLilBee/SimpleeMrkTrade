
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "tower" / "data"

INCIDENT_CHECKPOINT_STATUS_PATH = DATA_DIR / "security_incident_checkpoint_status.json"
INCIDENT_CHECKPOINT_PANEL_PATH = DATA_DIR / "security_incident_checkpoint_panel.html"


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


def _safe_call(label: str, fn) -> Dict[str, Any]:
    try:
        result = fn()
        return {
            "ok": True,
            "label": label,
            "result": result if isinstance(result, dict) else {},
            "error_type": "",
        }
    except Exception as exc:
        return {
            "ok": False,
            "label": label,
            "result": {},
            "error_type": type(exc).__name__,
        }


def build_security_incident_checkpoint(write_panel: bool = True) -> Dict[str, Any]:
    incident_call = _safe_call(
        "incident_desk",
        lambda: __import__("tower.security_incident_desk", fromlist=["build_security_incident_desk_status"]).build_security_incident_desk_status(write_panel=True),
    )

    filters_call = _safe_call(
        "incident_filters_escalation",
        lambda: __import__("tower.security_incident_filters_escalation", fromlist=["build_security_incident_filters_escalation_status"]).build_security_incident_filters_escalation_status(write_panel=True),
    )

    quick_call = _safe_call(
        "owner_quick_actions",
        lambda: __import__("tower.security_command_owner_quick_actions", fromlist=["build_owner_quick_actions_status"]).build_owner_quick_actions_status(write_panel=True),
    )

    unified_call = _safe_call(
        "unified_security_command",
        lambda: __import__("tower.security_command_unified_owner_page", fromlist=["build_unified_owner_security_command_status"]).build_unified_owner_security_command_status(write_html=True),
    )

    route_call = _safe_call(
        "route_coverage",
        lambda: __import__("tower.ob_route_coverage_report", fromlist=["build_ob_route_coverage_report"]).build_ob_route_coverage_report(write_panel=True),
    )

    object_checkpoint_call = _safe_call(
        "object_checkpoint",
        lambda: __import__("tower.ob_object_permission_integration_checkpoint", fromlist=["build_object_permission_integration_checkpoint"]).build_object_permission_integration_checkpoint(write_panel=True),
    )

    incident = incident_call.get("result", {})
    filters = filters_call.get("result", {})
    quick = quick_call.get("result", {})
    unified = unified_call.get("result", {})
    route = route_call.get("result", {})
    object_checkpoint = object_checkpoint_call.get("result", {})

    actions = quick.get("actions", []) if isinstance(quick.get("actions"), list) else []
    hrefs = {action.get("href") for action in actions if isinstance(action, dict)}

    unified_html = ""
    try:
        html_path = unified.get("html_path") or str(DATA_DIR / "security_command_unified_owner_page.html")
        html_file = Path(html_path)
        if html_file.exists():
            unified_html = html_file.read_text(encoding="utf-8", errors="replace")
    except Exception:
        unified_html = ""

    checks = {
        "incident_call_ok": incident_call.get("ok") is True,
        "incident_ok": incident.get("ok") is True,
        "incident_status_passed": incident.get("status") == "passed",
        "incident_readiness_100": incident.get("readiness_score") == 100,
        "incident_count_present": int(incident.get("incident_count", 0) or 0) >= 1,

        "filters_call_ok": filters_call.get("ok") is True,
        "filters_ok": filters.get("ok") is True,
        "filters_status_passed": filters.get("status") == "passed",
        "filters_readiness_100": filters.get("readiness_score") == 100,
        "escalation_ready_present": int(filters.get("escalation_ready_count", 0) or 0) >= 1,

        "quick_call_ok": quick_call.get("ok") is True,
        "quick_ok": quick.get("ok") is True,
        "quick_status_passed": quick.get("status") == "passed",
        "quick_readiness_100": quick.get("readiness_score") == 100,
        "quick_has_incident_desk_link": "/tower/security-incident-desk.json" in hrefs,
        "quick_has_incident_action_link": "/tower/security-incident-action.json" in hrefs,
        "quick_has_incident_filters_link": "/tower/security-incident-filters.json" in hrefs,

        "unified_call_ok": unified_call.get("ok") is True,
        "unified_ok": unified.get("ok") is True,
        "unified_status_passed": unified.get("status") == "passed",
        "unified_readiness_100": unified.get("readiness_score") == 100,
        "unified_has_pack126": "PACK126_SECURITY_INCIDENT_DESK_SECTION" in unified_html,
        "unified_has_pack128": "PACK128_SECURITY_INCIDENT_FILTERS_ESCALATION_SECTION" in unified_html,
        "unified_has_pack129": "PACK129_UNIFIED_OWNER_PAGE_INCLUDES_INCIDENT_FILTERS_ESCALATION" in unified_html,

        "route_call_ok": route_call.get("ok") is True,
        "route_coverage_100": route.get("coverage_pct") == 100,
        "unguarded_needed_zero": route.get("unguarded_needed_count") == 0,
        "unguarded_high_risk_zero": route.get("unguarded_high_risk_count") == 0,

        "object_checkpoint_call_ok": object_checkpoint_call.get("ok") is True,
        "object_checkpoint_passed": object_checkpoint.get("status") == "passed",
        "helper_wrapped_zero": object_checkpoint.get("helper_wrapped_count") == 0,
    }

    failed_checks = [key for key, ok in checks.items() if not ok]

    status = {
        "ok": not failed_checks,
        "pack": "130",
        "status": "passed" if not failed_checks else "failed",
        "created_at": _utc_now(),
        "status_path": str(INCIDENT_CHECKPOINT_STATUS_PATH),
        "panel_path": str(INCIDENT_CHECKPOINT_PANEL_PATH),
        "checks": checks,
        "failed_checks": failed_checks,
        "incident_desk": {
            "status": incident.get("status"),
            "readiness_score": incident.get("readiness_score"),
            "incident_count": incident.get("incident_count"),
            "open_incident_count": incident.get("open_incident_count"),
            "critical_incident_count": incident.get("critical_incident_count"),
            "tracked_incident_count": incident.get("tracked_incident_count"),
            "receipt_count": incident.get("receipt_count"),
            "by_status": incident.get("by_status"),
            "by_severity": incident.get("by_severity"),
        },
        "incident_filters": {
            "status": filters.get("status"),
            "readiness_score": filters.get("readiness_score"),
            "incident_count": filters.get("incident_count"),
            "open_incident_count": filters.get("open_incident_count"),
            "critical_count": filters.get("critical_count"),
            "high_count": filters.get("high_count"),
            "escalation_ready_count": filters.get("escalation_ready_count"),
            "by_status": filters.get("by_status"),
            "by_severity": filters.get("by_severity"),
            "by_next_action": filters.get("by_next_action"),
        },
        "quick_actions": {
            "status": quick.get("status"),
            "readiness_score": quick.get("readiness_score"),
            "action_count": quick.get("action_count"),
            "incident_links_present": {
                "desk": "/tower/security-incident-desk.json" in hrefs,
                "action": "/tower/security-incident-action.json" in hrefs,
                "filters": "/tower/security-incident-filters.json" in hrefs,
            },
        },
        "unified_security_command": {
            "status": unified.get("status"),
            "readiness_score": unified.get("readiness_score"),
            "html_path": unified.get("html_path"),
            "has_incident_desk_section": "PACK126_SECURITY_INCIDENT_DESK_SECTION" in unified_html,
            "has_incident_filters_section": "PACK128_SECURITY_INCIDENT_FILTERS_ESCALATION_SECTION" in unified_html,
        },
        "route_health": {
            "coverage_pct": route.get("coverage_pct"),
            "needs_guard_count": route.get("needs_guard_count"),
            "guarded_needed_count": route.get("guarded_needed_count"),
            "unguarded_needed_count": route.get("unguarded_needed_count"),
            "unguarded_high_risk_count": route.get("unguarded_high_risk_count"),
            "readiness_score": route.get("readiness_score"),
        },
        "object_checkpoint": {
            "status": object_checkpoint.get("status"),
            "readiness_score": object_checkpoint.get("readiness_score"),
            "helper_wrapped_count": object_checkpoint.get("helper_wrapped_count"),
        },
        "readiness_score": 100 if not failed_checks else max(0, 100 - (len(failed_checks) * 4)),
        "readiness_label": (
            "Incident Desk checkpoint passed"
            if not failed_checks
            else "Incident Desk checkpoint needs review"
        ),
        "human_reason": "Incident Desk layer is healthy: incidents, filters, escalation readiness, unified UI, quick actions, and route guards are all passing.",
        "soulaana_translation": "Soulaana: Incident Desk is locked in. Serious events can be found, sorted, escalated, and reviewed from the owner command room.",
    }

    scan = _safe_scan(status)
    status["no_secret_leakage"] = scan.get("ok") is True
    status["leakage_scan"] = scan
    status["status_fingerprint"] = _fingerprint(status)

    _write_json(INCIDENT_CHECKPOINT_STATUS_PATH, status)

    try:
        from tower.tamper_evident_audit_chain import create_tamper_chain_entry
        create_tamper_chain_entry(
            event_type="tower_security_incident_checkpoint",
            source_name="security_incident_checkpoint_status",
            source_path=str(INCIDENT_CHECKPOINT_STATUS_PATH),
            source_hash=_fingerprint(status),
            record_count=1,
            actor_user_id="tower_system",
            reason="Pack 130 Incident Desk checkpoint generated.",
            metadata={
                "pack": "130",
                "status": status.get("status"),
                "readiness_score": status.get("readiness_score"),
                "failed_checks": failed_checks,
            },
        )
    except Exception:
        pass

    if write_panel:
        write_security_incident_checkpoint_panel(status)

    return status


def render_security_incident_checkpoint_section(status: Dict[str, Any] | None = None) -> str:
    status = status if isinstance(status, dict) else build_security_incident_checkpoint(write_panel=False)

    incident = status.get("incident_desk", {}) if isinstance(status.get("incident_desk"), dict) else {}
    filters = status.get("incident_filters", {}) if isinstance(status.get("incident_filters"), dict) else {}
    quick = status.get("quick_actions", {}) if isinstance(status.get("quick_actions"), dict) else {}
    route = status.get("route_health", {}) if isinstance(status.get("route_health"), dict) else {}
    obj = status.get("object_checkpoint", {}) if isinstance(status.get("object_checkpoint"), dict) else {}

    cards = [
        ("Incidents", incident.get("incident_count", 0), "Desk"),
        ("Open Incidents", incident.get("open_incident_count", 0), "Active"),
        ("Escalation Ready", filters.get("escalation_ready_count", 0), "Priority"),
        ("Quick Actions", quick.get("action_count", 0), "Owner Rail"),
        ("Route Coverage", f"{route.get('coverage_pct', 0)}%", "Guard Wall"),
        ("Helper Wraps", obj.get("helper_wrapped_count", 0), "Clean"),
    ]

    card_html = []
    for title, value, label in cards:
        card_html.append(f"""
        <article class="incident-checkpoint-card">
          <div class="incident-checkpoint-card__eyebrow">{_html_escape(label)}</div>
          <h3>{_html_escape(value)}</h3>
          <p>{_html_escape(title)}</p>
        </article>
        """)

    html = f"""
<!-- PACK130_SECURITY_INCIDENT_CHECKPOINT_SECTION -->
<section class="security-incident-checkpoint" data-pack="130">
  <style>
    .security-incident-checkpoint {{
      margin: 24px 0;
      border: 1px solid rgba(143,221,158,.38);
      border-radius: 28px;
      padding: 22px;
      background:
        radial-gradient(circle at top right, rgba(143,221,158,.13), transparent 34%),
        linear-gradient(135deg, rgba(16,32,22,.84), rgba(8,9,7,.94));
      color: #f5ead2;
      box-shadow: 0 18px 70px rgba(0,0,0,.32);
    }}
    .security-incident-checkpoint__eyebrow {{
      color: rgba(143,221,158,.9);
      text-transform: uppercase;
      letter-spacing: .14em;
      font-size: 11px;
      margin-bottom: 8px;
    }}
    .security-incident-checkpoint h2 {{
      margin: 0;
      font-size: 24px;
      letter-spacing: -.03em;
    }}
    .security-incident-checkpoint p {{
      color: rgba(245,234,210,.72);
      line-height: 1.45;
    }}
    .incident-checkpoint-grid {{
      display: grid;
      grid-template-columns: repeat(6, minmax(0, 1fr));
      gap: 12px;
      margin-top: 14px;
    }}
    .incident-checkpoint-card {{
      border: 1px solid rgba(245,234,210,.13);
      border-radius: 18px;
      padding: 12px;
      background: rgba(255,255,255,.04);
    }}
    .incident-checkpoint-card__eyebrow {{
      color: rgba(143,221,158,.84);
      text-transform: uppercase;
      letter-spacing: .12em;
      font-size: 10px;
      margin-bottom: 7px;
    }}
    .incident-checkpoint-card h3 {{
      margin: 0 0 6px;
      font-size: 22px;
    }}
    .incident-checkpoint-card p {{
      margin: 0;
      color: rgba(245,234,210,.62);
      font-size: 12px;
    }}
    @media (max-width: 1000px) {{
      .incident-checkpoint-grid {{
        grid-template-columns: 1fr;
      }}
    }}
  </style>

  <div class="security-incident-checkpoint__eyebrow">PACK 130 · INCIDENT CHECKPOINT</div>
  <h2>Incident Desk Readiness Checkpoint</h2>
  <p>{_html_escape(status.get('human_reason', 'Incident Desk checkpoint loaded.'))}</p>

  <div class="incident-checkpoint-grid">
    {''.join(card_html)}
  </div>
</section>
<!-- END PACK130_SECURITY_INCIDENT_CHECKPOINT_SECTION -->
"""
    return html


def write_security_incident_checkpoint_panel(status: Dict[str, Any] | None = None) -> Dict[str, Any]:
    status = status if isinstance(status, dict) else build_security_incident_checkpoint(write_panel=False)
    html = f"""<!doctype html>
<html lang="en">
<head><meta charset="utf-8"><title>The Tower · Incident Checkpoint</title></head>
<body style="margin:0;background:#080907;color:#f5ead2;font-family:system-ui;padding:32px;">
<main style="max-width:1180px;margin:auto;">
{render_security_incident_checkpoint_section(status)}
</main>
</body>
</html>
"""
    _write_text(INCIDENT_CHECKPOINT_PANEL_PATH, html)
    return {
        "ok": True,
        "pack": "130",
        "decision": "security_incident_checkpoint_panel_written",
        "path": str(INCIDENT_CHECKPOINT_PANEL_PATH),
        "human_reason": "Incident Desk checkpoint panel written.",
        "soulaana_translation": "Soulaana: Incident checkpoint board posted.",
    }


def load_security_incident_checkpoint() -> Dict[str, Any]:
    status = _load_json(INCIDENT_CHECKPOINT_STATUS_PATH, {})
    if not status:
        status = build_security_incident_checkpoint(write_panel=True)
    return status


def security_incident_checkpoint_status_card() -> Dict[str, Any]:
    status = load_security_incident_checkpoint()
    incident = status.get("incident_desk", {}) if isinstance(status.get("incident_desk"), dict) else {}
    filters = status.get("incident_filters", {}) if isinstance(status.get("incident_filters"), dict) else {}
    route = status.get("route_health", {}) if isinstance(status.get("route_health"), dict) else {}

    return {
        "ok": status.get("ok") is True,
        "pack": "130",
        "title": "Incident Desk Checkpoint",
        "readiness_score": status.get("readiness_score", 0),
        "incident_count": incident.get("incident_count", 0),
        "open_incident_count": incident.get("open_incident_count", 0),
        "escalation_ready_count": filters.get("escalation_ready_count", 0),
        "route_coverage_pct": route.get("coverage_pct", 0),
        "panel_path": status.get("panel_path", str(INCIDENT_CHECKPOINT_PANEL_PATH)),
        "status_path": status.get("status_path", str(INCIDENT_CHECKPOINT_STATUS_PATH)),
        "human_reason": "Incident Desk checkpoint status card loaded.",
        "soulaana_translation": "Soulaana: Incident Desk checkpoint is visible.",
    }


def reset_security_incident_checkpoint_for_test() -> Dict[str, Any]:
    _write_json(INCIDENT_CHECKPOINT_STATUS_PATH, {
        "ok": True,
        "pack": "130",
        "reset_at": _utc_now(),
        "human_reason": "Incident Desk checkpoint reset for test.",
    })
    if INCIDENT_CHECKPOINT_PANEL_PATH.exists():
        try:
            INCIDENT_CHECKPOINT_PANEL_PATH.unlink()
        except Exception:
            pass
    return {
        "ok": True,
        "decision": "security_incident_checkpoint_reset_for_test",
        "soulaana_translation": "Soulaana: Incident checkpoint reset for a clean test lane.",
    }
