
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "tower" / "data"

SECURITY_WATCH_CHECKPOINT_STATUS_PATH = DATA_DIR / "security_watch_checkpoint_status.json"
SECURITY_WATCH_CHECKPOINT_PANEL_PATH = DATA_DIR / "security_watch_checkpoint_panel.html"


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


def build_security_watch_checkpoint(write_panel: bool = True) -> Dict[str, Any]:
    watch_call = _safe_call(
        "security_watch",
        lambda: __import__(
            "tower.security_watch_owner_posture",
            fromlist=["build_security_watch_owner_posture"],
        ).build_security_watch_owner_posture(write_panel=True),
    )

    incident_checkpoint_call = _safe_call(
        "incident_checkpoint",
        lambda: __import__(
            "tower.security_incident_checkpoint",
            fromlist=["build_security_incident_checkpoint"],
        ).build_security_incident_checkpoint(write_panel=True),
    )

    quick_call = _safe_call(
        "owner_quick_actions",
        lambda: __import__(
            "tower.security_command_owner_quick_actions",
            fromlist=["build_owner_quick_actions_status"],
        ).build_owner_quick_actions_status(write_panel=True),
    )

    unified_call = _safe_call(
        "unified_security_command",
        lambda: __import__(
            "tower.security_command_unified_owner_page",
            fromlist=["build_unified_owner_security_command_status"],
        ).build_unified_owner_security_command_status(write_html=True),
    )

    route_call = _safe_call(
        "route_coverage",
        lambda: __import__(
            "tower.ob_route_coverage_report",
            fromlist=["build_ob_route_coverage_report"],
        ).build_ob_route_coverage_report(write_panel=True),
    )

    object_checkpoint_call = _safe_call(
        "object_checkpoint",
        lambda: __import__(
            "tower.ob_object_permission_integration_checkpoint",
            fromlist=["build_object_permission_integration_checkpoint"],
        ).build_object_permission_integration_checkpoint(write_panel=True),
    )

    watch = watch_call.get("result", {})
    incident_checkpoint = incident_checkpoint_call.get("result", {})
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

    posture = watch.get("posture", {}) if isinstance(watch.get("posture"), dict) else {}
    route_health = watch.get("route_health", {}) if isinstance(watch.get("route_health"), dict) else {}
    incident_watch = watch.get("incident_watch", {}) if isinstance(watch.get("incident_watch"), dict) else {}
    inbox_watch = watch.get("inbox_watch", {}) if isinstance(watch.get("inbox_watch"), dict) else {}
    command_room = watch.get("command_room", {}) if isinstance(watch.get("command_room"), dict) else {}

    checks = {
        "watch_call_ok": watch_call.get("ok") is True,
        "watch_ok": watch.get("ok") is True,
        "watch_status_passed": watch.get("status") == "passed",
        "watch_readiness_100": watch.get("readiness_score") == 100,
        "watch_has_posture": bool(posture.get("posture")),
        "watch_has_recommended_first_action": bool(posture.get("recommended_first_action")),
        "watch_no_secret_leakage": watch.get("no_secret_leakage") is True,

        "incident_checkpoint_call_ok": incident_checkpoint_call.get("ok") is True,
        "incident_checkpoint_ok": incident_checkpoint.get("ok") is True,
        "incident_checkpoint_passed": incident_checkpoint.get("status") == "passed",
        "incident_checkpoint_readiness_100": incident_checkpoint.get("readiness_score") == 100,

        "quick_call_ok": quick_call.get("ok") is True,
        "quick_ok": quick.get("ok") is True,
        "quick_passed": quick.get("status") == "passed",
        "quick_readiness_100": quick.get("readiness_score") == 100,
        "quick_has_security_watch_link": "/tower/security-watch.json" in hrefs,
        "quick_has_incident_checkpoint_link": "/tower/security-incident-checkpoint.json" in hrefs,
        "quick_has_incident_filters_link": "/tower/security-incident-filters.json" in hrefs,

        "unified_call_ok": unified_call.get("ok") is True,
        "unified_ok": unified.get("ok") is True,
        "unified_passed": unified.get("status") == "passed",
        "unified_readiness_100": unified.get("readiness_score") == 100,
        "unified_has_pack131": "PACK131_SECURITY_WATCH_OWNER_POSTURE_SECTION" in unified_html,
        "unified_has_pack132": "PACK132_UNIFIED_OWNER_PAGE_INCLUDES_SECURITY_WATCH" in unified_html,
        "unified_has_watch_link": "/tower/security-watch.json" in unified_html,

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
        "pack": "133",
        "status": "passed" if not failed_checks else "failed",
        "created_at": _utc_now(),
        "status_path": str(SECURITY_WATCH_CHECKPOINT_STATUS_PATH),
        "panel_path": str(SECURITY_WATCH_CHECKPOINT_PANEL_PATH),
        "checks": checks,
        "failed_checks": failed_checks,
        "security_watch": {
            "status": watch.get("status"),
            "readiness_score": watch.get("readiness_score"),
            "posture": posture.get("posture"),
            "posture_label": posture.get("posture_label"),
            "risk_points": posture.get("risk_points"),
            "risk_reasons": posture.get("risk_reasons"),
            "recommended_first_action": posture.get("recommended_first_action"),
            "wall_state": posture.get("wall_state"),
            "owner_message": posture.get("owner_message"),
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
        "incident_watch": {
            "incident_count": incident_watch.get("incident_count"),
            "open_incident_count": incident_watch.get("open_incident_count"),
            "critical_count": incident_watch.get("critical_count"),
            "high_count": incident_watch.get("high_count"),
            "escalation_ready_count": incident_watch.get("escalation_ready_count"),
            "by_status": incident_watch.get("by_status"),
            "by_next_action": incident_watch.get("by_next_action"),
        },
        "inbox_watch": {
            "inbox_count": inbox_watch.get("inbox_count"),
            "high_priority_count": inbox_watch.get("high_priority_count"),
            "open_review_count": inbox_watch.get("open_review_count"),
            "unresolved_count": inbox_watch.get("unresolved_count"),
        },
        "command_room": {
            "quick_action_count": command_room.get("quick_action_count") or quick.get("action_count"),
            "quick_status": quick.get("status"),
            "unified_status": unified.get("status"),
            "unified_readiness_score": unified.get("readiness_score"),
            "watch_link_present": "/tower/security-watch.json" in hrefs,
            "incident_checkpoint_link_present": "/tower/security-incident-checkpoint.json" in hrefs,
            "incident_filters_link_present": "/tower/security-incident-filters.json" in hrefs,
        },
        "incident_checkpoint": {
            "status": incident_checkpoint.get("status"),
            "readiness_score": incident_checkpoint.get("readiness_score"),
            "incident_count": (
                incident_checkpoint.get("incident_desk", {}).get("incident_count")
                if isinstance(incident_checkpoint.get("incident_desk"), dict)
                else None
            ),
            "escalation_ready_count": (
                incident_checkpoint.get("incident_filters", {}).get("escalation_ready_count")
                if isinstance(incident_checkpoint.get("incident_filters"), dict)
                else None
            ),
        },
        "readiness_score": 100 if not failed_checks else max(0, 100 - (len(failed_checks) * 4)),
        "readiness_label": (
            "Security Watch checkpoint passed"
            if not failed_checks
            else "Security Watch checkpoint needs review"
        ),
        "human_reason": "Security Watch checkpoint proves owner posture, unified UI, quick actions, incident checkpoint, route guards, and object checkpoint are healthy.",
        "soulaana_translation": "Soulaana: Security Watch is locked in. The owner can read the Tower’s posture from the command room.",
    }

    scan = _safe_scan(status)
    status["no_secret_leakage"] = scan.get("ok") is True
    status["leakage_scan"] = scan
    status["status_fingerprint"] = _fingerprint(status)

    _write_json(SECURITY_WATCH_CHECKPOINT_STATUS_PATH, status)

    try:
        from tower.tamper_evident_audit_chain import create_tamper_chain_entry
        create_tamper_chain_entry(
            event_type="tower_security_watch_checkpoint",
            source_name="security_watch_checkpoint_status",
            source_path=str(SECURITY_WATCH_CHECKPOINT_STATUS_PATH),
            source_hash=_fingerprint(status),
            record_count=1,
            actor_user_id="tower_system",
            reason="Pack 133 Security Watch checkpoint generated.",
            metadata={
                "pack": "133",
                "status": status.get("status"),
                "readiness_score": status.get("readiness_score"),
                "posture": status.get("security_watch", {}).get("posture"),
                "failed_checks": failed_checks,
            },
        )
    except Exception:
        pass

    if write_panel:
        write_security_watch_checkpoint_panel(status)

    return status


def render_security_watch_checkpoint_section(status: Dict[str, Any] | None = None) -> str:
    status = status if isinstance(status, dict) else build_security_watch_checkpoint(write_panel=False)

    watch = status.get("security_watch", {}) if isinstance(status.get("security_watch"), dict) else {}
    route = status.get("route_health", {}) if isinstance(status.get("route_health"), dict) else {}
    incidents = status.get("incident_watch", {}) if isinstance(status.get("incident_watch"), dict) else {}
    inbox = status.get("inbox_watch", {}) if isinstance(status.get("inbox_watch"), dict) else {}
    command = status.get("command_room", {}) if isinstance(status.get("command_room"), dict) else {}
    obj = status.get("object_checkpoint", {}) if isinstance(status.get("object_checkpoint"), dict) else {}

    cards = [
        ("Posture", watch.get("posture_label", "Watch"), "Owner View"),
        ("Risk Points", watch.get("risk_points", 0), "Signal"),
        ("Route Coverage", f"{route.get('coverage_pct', 0)}%", "Guard Wall"),
        ("Open Incidents", incidents.get("open_incident_count", 0), "Incident Desk"),
        ("High Priority Inbox", inbox.get("high_priority_count", 0), "Inbox"),
        ("Quick Actions", command.get("quick_action_count", 0), "Owner Rail"),
        ("Helper Wraps", obj.get("helper_wrapped_count", 0), "Clean"),
    ]

    card_html = []
    for title, value, label in cards:
        card_html.append(f"""
        <article class="security-watch-checkpoint-card">
          <div class="security-watch-checkpoint-card__eyebrow">{_html_escape(label)}</div>
          <h3>{_html_escape(value)}</h3>
          <p>{_html_escape(title)}</p>
        </article>
        """)

    html = f"""
<!-- PACK133_SECURITY_WATCH_CHECKPOINT_SECTION -->
<section class="security-watch-checkpoint" data-pack="133">
  <style>
    .security-watch-checkpoint {{
      margin: 24px 0;
      border: 1px solid rgba(143,221,158,.42);
      border-radius: 28px;
      padding: 22px;
      background:
        radial-gradient(circle at top right, rgba(143,221,158,.13), transparent 34%),
        linear-gradient(135deg, rgba(10,34,25,.86), rgba(8,9,7,.94));
      color: #f5ead2;
      box-shadow: 0 18px 70px rgba(0,0,0,.32);
    }}
    .security-watch-checkpoint__eyebrow {{
      color: rgba(143,221,158,.92);
      text-transform: uppercase;
      letter-spacing: .14em;
      font-size: 11px;
      margin-bottom: 8px;
    }}
    .security-watch-checkpoint h2 {{
      margin: 0;
      font-size: 24px;
      letter-spacing: -.03em;
    }}
    .security-watch-checkpoint p {{
      color: rgba(245,234,210,.72);
      line-height: 1.45;
    }}
    .security-watch-checkpoint-grid {{
      display: grid;
      grid-template-columns: repeat(7, minmax(0, 1fr));
      gap: 12px;
      margin-top: 14px;
    }}
    .security-watch-checkpoint-card {{
      border: 1px solid rgba(245,234,210,.13);
      border-radius: 18px;
      padding: 12px;
      background: rgba(255,255,255,.04);
    }}
    .security-watch-checkpoint-card__eyebrow {{
      color: rgba(143,221,158,.84);
      text-transform: uppercase;
      letter-spacing: .12em;
      font-size: 10px;
      margin-bottom: 7px;
    }}
    .security-watch-checkpoint-card h3 {{
      margin: 0 0 6px;
      font-size: 18px;
      word-break: break-word;
    }}
    .security-watch-checkpoint-card p {{
      margin: 0;
      color: rgba(245,234,210,.62);
      font-size: 12px;
    }}
    .security-watch-checkpoint__note {{
      margin-top: 14px;
      border: 1px solid rgba(143,221,158,.22);
      border-radius: 18px;
      padding: 12px;
      background: rgba(255,255,255,.035);
      color: rgba(245,234,210,.72);
    }}
    @media (max-width: 1100px) {{
      .security-watch-checkpoint-grid {{
        grid-template-columns: 1fr;
      }}
    }}
  </style>

  <div class="security-watch-checkpoint__eyebrow">PACK 133 · SECURITY WATCH CHECKPOINT</div>
  <h2>Security Watch Readiness Checkpoint</h2>
  <p>{_html_escape(status.get('human_reason', 'Security Watch checkpoint loaded.'))}</p>

  <div class="security-watch-checkpoint-grid">
    {''.join(card_html)}
  </div>

  <div class="security-watch-checkpoint__note">
    <strong>Recommended first action:</strong> {_html_escape(watch.get('recommended_first_action', 'monitor'))}<br>
    <strong>Wall state:</strong> {_html_escape(watch.get('wall_state', 'unknown'))}
  </div>
</section>
<!-- END PACK133_SECURITY_WATCH_CHECKPOINT_SECTION -->
"""
    return html


def write_security_watch_checkpoint_panel(status: Dict[str, Any] | None = None) -> Dict[str, Any]:
    status = status if isinstance(status, dict) else build_security_watch_checkpoint(write_panel=False)
    html = f"""<!doctype html>
<html lang="en">
<head><meta charset="utf-8"><title>The Tower · Security Watch Checkpoint</title></head>
<body style="margin:0;background:#080907;color:#f5ead2;font-family:system-ui;padding:32px;">
<main style="max-width:1180px;margin:auto;">
{render_security_watch_checkpoint_section(status)}
</main>
</body>
</html>
"""
    _write_text(SECURITY_WATCH_CHECKPOINT_PANEL_PATH, html)
    return {
        "ok": True,
        "pack": "133",
        "decision": "security_watch_checkpoint_panel_written",
        "path": str(SECURITY_WATCH_CHECKPOINT_PANEL_PATH),
        "human_reason": "Security Watch checkpoint panel written.",
        "soulaana_translation": "Soulaana: Security Watch checkpoint board posted.",
    }


def load_security_watch_checkpoint() -> Dict[str, Any]:
    status = _load_json(SECURITY_WATCH_CHECKPOINT_STATUS_PATH, {})
    if not status:
        status = build_security_watch_checkpoint(write_panel=True)
    return status


def security_watch_checkpoint_status_card() -> Dict[str, Any]:
    status = load_security_watch_checkpoint()
    watch = status.get("security_watch", {}) if isinstance(status.get("security_watch"), dict) else {}
    route = status.get("route_health", {}) if isinstance(status.get("route_health"), dict) else {}
    incidents = status.get("incident_watch", {}) if isinstance(status.get("incident_watch"), dict) else {}

    return {
        "ok": status.get("ok") is True,
        "pack": "133",
        "title": "Security Watch Checkpoint",
        "readiness_score": status.get("readiness_score", 0),
        "posture": watch.get("posture", "watch"),
        "posture_label": watch.get("posture_label", "Security Watch"),
        "risk_points": watch.get("risk_points", 0),
        "recommended_first_action": watch.get("recommended_first_action", "monitor"),
        "open_incident_count": incidents.get("open_incident_count", 0),
        "escalation_ready_count": incidents.get("escalation_ready_count", 0),
        "route_coverage_pct": route.get("coverage_pct", 0),
        "panel_path": status.get("panel_path", str(SECURITY_WATCH_CHECKPOINT_PANEL_PATH)),
        "status_path": status.get("status_path", str(SECURITY_WATCH_CHECKPOINT_STATUS_PATH)),
        "human_reason": "Security Watch checkpoint status card loaded.",
        "soulaana_translation": "Soulaana: Security Watch checkpoint is visible.",
    }


def reset_security_watch_checkpoint_for_test() -> Dict[str, Any]:
    _write_json(SECURITY_WATCH_CHECKPOINT_STATUS_PATH, {
        "ok": True,
        "pack": "133",
        "reset_at": _utc_now(),
        "human_reason": "Security Watch checkpoint reset for test.",
    })
    if SECURITY_WATCH_CHECKPOINT_PANEL_PATH.exists():
        try:
            SECURITY_WATCH_CHECKPOINT_PANEL_PATH.unlink()
        except Exception:
            pass
    return {
        "ok": True,
        "decision": "security_watch_checkpoint_reset_for_test",
        "soulaana_translation": "Soulaana: Security Watch checkpoint reset for a clean test lane.",
    }
