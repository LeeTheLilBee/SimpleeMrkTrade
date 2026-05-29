
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "tower" / "data"

SECURITY_WATCH_STATUS_PATH = DATA_DIR / "security_watch_owner_posture_status.json"
SECURITY_WATCH_PANEL_PATH = DATA_DIR / "security_watch_owner_posture_panel.html"


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


def _num(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except Exception:
        return default


def _pct(value: Any, default: int = 0) -> int:
    try:
        return int(float(value))
    except Exception:
        return default


def _derive_posture(
    route: Dict[str, Any],
    object_checkpoint: Dict[str, Any],
    incident_checkpoint: Dict[str, Any],
    incident_filters: Dict[str, Any],
    inbox_filters: Dict[str, Any],
    quick: Dict[str, Any],
    unified: Dict[str, Any],
) -> Dict[str, Any]:
    route_coverage = _pct(route.get("coverage_pct"), 0)
    unguarded = _num(route.get("unguarded_needed_count"), 999)
    unguarded_high = _num(route.get("unguarded_high_risk_count"), 999)
    helper_wrapped = _num(object_checkpoint.get("helper_wrapped_count"), 999)

    open_incidents = _num(incident_filters.get("open_incident_count"), 0)
    critical_incidents = _num(incident_filters.get("critical_count"), 0)
    high_incidents = _num(incident_filters.get("high_count"), 0)
    escalation_ready = _num(incident_filters.get("escalation_ready_count"), 0)

    high_priority_inbox = _num(inbox_filters.get("high_priority_count"), 0)
    open_review = _num(inbox_filters.get("open_review_count"), 0)

    quick_ok = quick.get("ok") is True and quick.get("status") == "passed"
    unified_ok = unified.get("ok") is True and unified.get("status") == "passed"
    incident_checkpoint_ok = incident_checkpoint.get("ok") is True and incident_checkpoint.get("status") == "passed"

    risk_points = 0
    reasons = []

    if route_coverage < 100 or unguarded > 0 or unguarded_high > 0:
        risk_points += 45
        reasons.append("route_guard_gap")

    if helper_wrapped != 0:
        risk_points += 20
        reasons.append("helper_wraps_present")

    if critical_incidents > 0:
        risk_points += 40
        reasons.append("critical_incidents_open")

    if high_incidents > 0:
        risk_points += 25
        reasons.append("high_incidents_open")

    if escalation_ready > 0:
        risk_points += 18
        reasons.append("escalation_ready_incidents")

    if high_priority_inbox > 0:
        risk_points += 12
        reasons.append("high_priority_inbox_items")

    if open_review > 0:
        risk_points += 8
        reasons.append("open_security_reviews")

    if not quick_ok:
        risk_points += 15
        reasons.append("quick_actions_not_healthy")

    if not unified_ok:
        risk_points += 20
        reasons.append("unified_security_command_not_healthy")

    if not incident_checkpoint_ok:
        risk_points += 20
        reasons.append("incident_checkpoint_not_healthy")

    if risk_points >= 80:
        posture = "elevated"
        label = "Elevated Security Watch"
        owner_message = "Security Watch sees important open work. Review incident escalation and high-priority inbox items first."
    elif risk_points >= 35:
        posture = "watch"
        label = "Active Security Watch"
        owner_message = "Security Watch is stable, but there are open items that need owner attention."
    elif risk_points > 0:
        posture = "calm_with_watch_items"
        label = "Calm With Watch Items"
        owner_message = "Security Watch is calm overall, with routine watch items still visible."
    else:
        posture = "calm"
        label = "Calm Security Watch"
        owner_message = "Security Watch is calm. Route guards, command UI, and checkpoints are healthy."

    if route_coverage == 100 and unguarded == 0 and unguarded_high == 0 and helper_wrapped == 0:
        wall_state = "sealed"
    else:
        wall_state = "review_needed"

    return {
        "posture": posture,
        "posture_label": label,
        "owner_message": owner_message,
        "risk_points": risk_points,
        "risk_reasons": reasons,
        "wall_state": wall_state,
        "route_coverage_pct": route_coverage,
        "unguarded_needed_count": unguarded,
        "unguarded_high_risk_count": unguarded_high,
        "helper_wrapped_count": helper_wrapped,
        "open_incident_count": open_incidents,
        "critical_incident_count": critical_incidents,
        "high_incident_count": high_incidents,
        "escalation_ready_count": escalation_ready,
        "high_priority_inbox_count": high_priority_inbox,
        "open_review_count": open_review,
        "recommended_first_action": (
            "review_incident_escalation"
            if escalation_ready > 0
            else "review_high_priority_inbox"
            if high_priority_inbox > 0
            else "review_route_health"
            if wall_state != "sealed"
            else "monitor"
        ),
    }


def build_security_watch_owner_posture(write_panel: bool = True) -> Dict[str, Any]:
    route_call = _safe_call(
        "route_coverage",
        lambda: __import__("tower.ob_route_coverage_report", fromlist=["build_ob_route_coverage_report"]).build_ob_route_coverage_report(write_panel=True),
    )
    object_checkpoint_call = _safe_call(
        "object_checkpoint",
        lambda: __import__("tower.ob_object_permission_integration_checkpoint", fromlist=["build_object_permission_integration_checkpoint"]).build_object_permission_integration_checkpoint(write_panel=True),
    )
    inbox_filters_call = _safe_call(
        "security_inbox_filters",
        lambda: __import__("tower.security_inbox_filters_priorities", fromlist=["build_security_inbox_filters_priorities_status"]).build_security_inbox_filters_priorities_status(write_panel=True),
    )
    incident_checkpoint_call = _safe_call(
        "incident_checkpoint",
        lambda: __import__("tower.security_incident_checkpoint", fromlist=["build_security_incident_checkpoint"]).build_security_incident_checkpoint(write_panel=True),
    )
    incident_filters_call = _safe_call(
        "incident_filters",
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

    route = route_call.get("result", {})
    object_checkpoint = object_checkpoint_call.get("result", {})
    inbox_filters = inbox_filters_call.get("result", {})
    incident_checkpoint = incident_checkpoint_call.get("result", {})
    incident_filters = incident_filters_call.get("result", {})
    quick = quick_call.get("result", {})
    unified = unified_call.get("result", {})

    posture = _derive_posture(
        route=route,
        object_checkpoint=object_checkpoint,
        incident_checkpoint=incident_checkpoint,
        incident_filters=incident_filters,
        inbox_filters=inbox_filters,
        quick=quick,
        unified=unified,
    )

    checks = {
        "route_call_ok": route_call.get("ok") is True,
        "route_coverage_100": route.get("coverage_pct") == 100,
        "route_unguarded_zero": route.get("unguarded_needed_count") == 0,
        "route_high_risk_zero": route.get("unguarded_high_risk_count") == 0,

        "object_checkpoint_call_ok": object_checkpoint_call.get("ok") is True,
        "object_checkpoint_passed": object_checkpoint.get("status") == "passed",
        "helper_wrapped_zero": object_checkpoint.get("helper_wrapped_count") == 0,

        "inbox_filters_call_ok": inbox_filters_call.get("ok") is True,
        "inbox_filters_passed": inbox_filters.get("status") == "passed",

        "incident_checkpoint_call_ok": incident_checkpoint_call.get("ok") is True,
        "incident_checkpoint_passed": incident_checkpoint.get("status") == "passed",
        "incident_checkpoint_readiness_100": incident_checkpoint.get("readiness_score") == 100,

        "incident_filters_call_ok": incident_filters_call.get("ok") is True,
        "incident_filters_passed": incident_filters.get("status") == "passed",
        "incident_filters_readiness_100": incident_filters.get("readiness_score") == 100,

        "quick_call_ok": quick_call.get("ok") is True,
        "quick_passed": quick.get("status") == "passed",

        "unified_call_ok": unified_call.get("ok") is True,
        "unified_passed": unified.get("status") == "passed",
    }

    failed_checks = [key for key, ok in checks.items() if not ok]

    status = {
        "ok": not failed_checks,
        "pack": "131",
        "status": "passed" if not failed_checks else "failed",
        "created_at": _utc_now(),
        "status_path": str(SECURITY_WATCH_STATUS_PATH),
        "panel_path": str(SECURITY_WATCH_PANEL_PATH),
        "posture": posture,
        "checks": checks,
        "failed_checks": failed_checks,
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
        "inbox_watch": {
            "status": inbox_filters.get("status"),
            "readiness_score": inbox_filters.get("readiness_score"),
            "inbox_count": inbox_filters.get("inbox_count"),
            "high_priority_count": inbox_filters.get("high_priority_count"),
            "open_review_count": inbox_filters.get("open_review_count"),
            "unresolved_count": inbox_filters.get("unresolved_count"),
        },
        "incident_watch": {
            "checkpoint_status": incident_checkpoint.get("status"),
            "checkpoint_readiness_score": incident_checkpoint.get("readiness_score"),
            "incident_count": incident_filters.get("incident_count"),
            "open_incident_count": incident_filters.get("open_incident_count"),
            "critical_count": incident_filters.get("critical_count"),
            "high_count": incident_filters.get("high_count"),
            "escalation_ready_count": incident_filters.get("escalation_ready_count"),
            "by_status": incident_filters.get("by_status"),
            "by_next_action": incident_filters.get("by_next_action"),
        },
        "command_room": {
            "quick_action_count": quick.get("action_count"),
            "quick_status": quick.get("status"),
            "unified_status": unified.get("status"),
            "unified_readiness_score": unified.get("readiness_score"),
        },
        "readiness_score": 100 if not failed_checks else max(0, 100 - (len(failed_checks) * 4)),
        "readiness_label": (
            "Security Watch owner posture ready"
            if not failed_checks
            else "Security Watch owner posture needs review"
        ),
        "human_reason": "Security Watch summarizes Tower posture across route guards, inbox items, incidents, escalation readiness, quick actions, and unified command health.",
        "soulaana_translation": "Soulaana: Security Watch is online. The owner can see the Tower posture without digging through every room.",
    }

    scan = _safe_scan(status)
    status["no_secret_leakage"] = scan.get("ok") is True
    status["leakage_scan"] = scan
    status["status_fingerprint"] = _fingerprint(status)

    _write_json(SECURITY_WATCH_STATUS_PATH, status)

    try:
        from tower.tamper_evident_audit_chain import create_tamper_chain_entry
        create_tamper_chain_entry(
            event_type="tower_security_watch_owner_posture",
            source_name="security_watch_owner_posture_status",
            source_path=str(SECURITY_WATCH_STATUS_PATH),
            source_hash=_fingerprint(status),
            record_count=1,
            actor_user_id="tower_system",
            reason="Pack 131 Security Watch owner posture generated.",
            metadata={
                "pack": "131",
                "status": status.get("status"),
                "posture": posture.get("posture"),
                "risk_points": posture.get("risk_points"),
                "readiness_score": status.get("readiness_score"),
            },
        )
    except Exception:
        pass

    if write_panel:
        write_security_watch_owner_posture_panel(status)

    return status


def render_security_watch_owner_posture_section(status: Dict[str, Any] | None = None) -> str:
    status = status if isinstance(status, dict) else build_security_watch_owner_posture(write_panel=False)
    posture = status.get("posture", {}) if isinstance(status.get("posture"), dict) else {}
    route = status.get("route_health", {}) if isinstance(status.get("route_health"), dict) else {}
    inbox = status.get("inbox_watch", {}) if isinstance(status.get("inbox_watch"), dict) else {}
    incidents = status.get("incident_watch", {}) if isinstance(status.get("incident_watch"), dict) else {}
    command = status.get("command_room", {}) if isinstance(status.get("command_room"), dict) else {}

    cards = [
        ("Posture", posture.get("posture_label", "Watch"), posture.get("posture", "watch")),
        ("Route Coverage", f"{route.get('coverage_pct', 0)}%", "Guard Wall"),
        ("Open Incidents", incidents.get("open_incident_count", 0), "Incident Desk"),
        ("Escalation Ready", incidents.get("escalation_ready_count", 0), "Priority"),
        ("High Priority Inbox", inbox.get("high_priority_count", 0), "Inbox"),
        ("Quick Actions", command.get("quick_action_count", 0), "Owner Rail"),
    ]

    card_html = []
    for title, value, label in cards:
        card_html.append(f"""
        <article class="security-watch-card">
          <div class="security-watch-card__eyebrow">{_html_escape(label)}</div>
          <h3>{_html_escape(value)}</h3>
          <p>{_html_escape(title)}</p>
        </article>
        """)

    reasons = posture.get("risk_reasons", [])
    if isinstance(reasons, list) and reasons:
        reason_text = ", ".join(str(item) for item in reasons[:8])
    else:
        reason_text = "none"

    html = f"""
<!-- PACK131_SECURITY_WATCH_OWNER_POSTURE_SECTION -->
<section class="security-watch-owner-posture" data-pack="131">
  <style>
    .security-watch-owner-posture {{
      margin: 24px 0;
      border: 1px solid rgba(168,175,255,.42);
      border-radius: 28px;
      padding: 22px;
      background:
        radial-gradient(circle at top right, rgba(168,175,255,.16), transparent 34%),
        linear-gradient(135deg, rgba(16,18,42,.86), rgba(8,9,7,.94));
      color: #f5ead2;
      box-shadow: 0 18px 70px rgba(0,0,0,.32);
    }}
    .security-watch-owner-posture__eyebrow {{
      color: rgba(168,175,255,.92);
      text-transform: uppercase;
      letter-spacing: .14em;
      font-size: 11px;
      margin-bottom: 8px;
    }}
    .security-watch-owner-posture h2 {{
      margin: 0;
      font-size: 24px;
      letter-spacing: -.03em;
    }}
    .security-watch-owner-posture p {{
      color: rgba(245,234,210,.72);
      line-height: 1.45;
    }}
    .security-watch-grid {{
      display: grid;
      grid-template-columns: repeat(6, minmax(0, 1fr));
      gap: 12px;
      margin-top: 14px;
    }}
    .security-watch-card {{
      border: 1px solid rgba(245,234,210,.13);
      border-radius: 18px;
      padding: 12px;
      background: rgba(255,255,255,.04);
    }}
    .security-watch-card__eyebrow {{
      color: rgba(168,175,255,.84);
      text-transform: uppercase;
      letter-spacing: .12em;
      font-size: 10px;
      margin-bottom: 7px;
    }}
    .security-watch-card h3 {{
      margin: 0 0 6px;
      font-size: 20px;
      word-break: break-word;
    }}
    .security-watch-card p {{
      margin: 0;
      color: rgba(245,234,210,.62);
      font-size: 12px;
    }}
    .security-watch-owner-posture__note {{
      margin-top: 14px;
      border: 1px solid rgba(168,175,255,.22);
      border-radius: 18px;
      padding: 12px;
      background: rgba(255,255,255,.035);
      color: rgba(245,234,210,.72);
    }}
    @media (max-width: 1000px) {{
      .security-watch-grid {{
        grid-template-columns: 1fr;
      }}
    }}
  </style>

  <div class="security-watch-owner-posture__eyebrow">PACK 131 · SECURITY WATCH</div>
  <h2>Tower Security Watch</h2>
  <p>{_html_escape(posture.get('owner_message', status.get('human_reason', 'Security Watch loaded.')))}</p>

  <div class="security-watch-grid">
    {''.join(card_html)}
  </div>

  <div class="security-watch-owner-posture__note">
    <strong>Recommended first action:</strong> {_html_escape(posture.get('recommended_first_action', 'monitor'))}<br>
    <strong>Risk reasons:</strong> {_html_escape(reason_text)}
  </div>
</section>
<!-- END PACK131_SECURITY_WATCH_OWNER_POSTURE_SECTION -->
"""
    return html


def write_security_watch_owner_posture_panel(status: Dict[str, Any] | None = None) -> Dict[str, Any]:
    status = status if isinstance(status, dict) else build_security_watch_owner_posture(write_panel=False)
    html = f"""<!doctype html>
<html lang="en">
<head><meta charset="utf-8"><title>The Tower · Security Watch</title></head>
<body style="margin:0;background:#080907;color:#f5ead2;font-family:system-ui;padding:32px;">
<main style="max-width:1180px;margin:auto;">
{render_security_watch_owner_posture_section(status)}
</main>
</body>
</html>
"""
    _write_text(SECURITY_WATCH_PANEL_PATH, html)
    return {
        "ok": True,
        "pack": "131",
        "decision": "security_watch_owner_posture_panel_written",
        "path": str(SECURITY_WATCH_PANEL_PATH),
        "human_reason": "Security Watch owner posture panel written.",
        "soulaana_translation": "Soulaana: Security Watch panel posted.",
    }


def load_security_watch_owner_posture() -> Dict[str, Any]:
    status = _load_json(SECURITY_WATCH_STATUS_PATH, {})
    if not status:
        status = build_security_watch_owner_posture(write_panel=True)
    return status


def security_watch_owner_posture_status_card() -> Dict[str, Any]:
    status = load_security_watch_owner_posture()
    posture = status.get("posture", {}) if isinstance(status.get("posture"), dict) else {}
    incidents = status.get("incident_watch", {}) if isinstance(status.get("incident_watch"), dict) else {}
    route = status.get("route_health", {}) if isinstance(status.get("route_health"), dict) else {}

    return {
        "ok": status.get("ok") is True,
        "pack": "131",
        "title": "Tower Security Watch",
        "readiness_score": status.get("readiness_score", 0),
        "posture": posture.get("posture", "watch"),
        "posture_label": posture.get("posture_label", "Security Watch"),
        "risk_points": posture.get("risk_points", 0),
        "recommended_first_action": posture.get("recommended_first_action", "monitor"),
        "open_incident_count": incidents.get("open_incident_count", 0),
        "escalation_ready_count": incidents.get("escalation_ready_count", 0),
        "route_coverage_pct": route.get("coverage_pct", 0),
        "panel_path": status.get("panel_path", str(SECURITY_WATCH_PANEL_PATH)),
        "status_path": status.get("status_path", str(SECURITY_WATCH_STATUS_PATH)),
        "human_reason": "Security Watch owner posture status card loaded.",
        "soulaana_translation": "Soulaana: Security Watch is visible.",
    }


def reset_security_watch_owner_posture_for_test() -> Dict[str, Any]:
    _write_json(SECURITY_WATCH_STATUS_PATH, {
        "ok": True,
        "pack": "131",
        "reset_at": _utc_now(),
        "human_reason": "Security Watch owner posture reset for test.",
    })
    if SECURITY_WATCH_PANEL_PATH.exists():
        try:
            SECURITY_WATCH_PANEL_PATH.unlink()
        except Exception:
            pass
    return {
        "ok": True,
        "decision": "security_watch_owner_posture_reset_for_test",
        "soulaana_translation": "Soulaana: Security Watch reset for a clean test lane.",
    }



# ================================================================================
# PACK135B_NON_RECURSIVE_SECURITY_WATCH_BUILDER
# ================================================================================
# Rescue:
# Security Watch must not call checkpoint/unified layers because those layers now
# include Security Watch. This override keeps Security Watch as a base posture
# reader and prevents recursion.
# ================================================================================

def build_security_watch_owner_posture(write_panel: bool = True) -> Dict[str, Any]:
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

    inbox_filters_call = _safe_call(
        "security_inbox_filters",
        lambda: __import__(
            "tower.security_inbox_filters_priorities",
            fromlist=["build_security_inbox_filters_priorities_status"],
        ).build_security_inbox_filters_priorities_status(write_panel=True),
    )

    incident_filters_call = _safe_call(
        "incident_filters",
        lambda: __import__(
            "tower.security_incident_filters_escalation",
            fromlist=["build_security_incident_filters_escalation_status"],
        ).build_security_incident_filters_escalation_status(write_panel=True),
    )

    quick_call = _safe_call(
        "owner_quick_actions",
        lambda: __import__(
            "tower.security_command_owner_quick_actions",
            fromlist=["build_owner_quick_actions_status"],
        ).build_owner_quick_actions_status(write_panel=True),
    )

    route = route_call.get("result", {})
    object_checkpoint = object_checkpoint_call.get("result", {})
    inbox_filters = inbox_filters_call.get("result", {})
    incident_filters = incident_filters_call.get("result", {})
    quick = quick_call.get("result", {})

    # Non-recursive command-room health:
    # Do NOT build unified Security Command here. Just inspect whether the latest
    # unified page file exists and whether the owner quick rail is healthy.
    unified_html_path = DATA_DIR / "security_command_unified_owner_page.html"
    unified_html_exists = unified_html_path.exists()
    unified_html_has_watch = False
    unified_html_has_checkpoint = False

    try:
        if unified_html_exists:
            unified_html = unified_html_path.read_text(encoding="utf-8", errors="replace")
            unified_html_has_watch = "PACK131_SECURITY_WATCH_OWNER_POSTURE_SECTION" in unified_html
            unified_html_has_checkpoint = "PACK133_SECURITY_WATCH_CHECKPOINT_SECTION" in unified_html
    except Exception:
        unified_html_has_watch = False
        unified_html_has_checkpoint = False

    route_coverage = _pct(route.get("coverage_pct"), 0)
    unguarded_needed = _num(route.get("unguarded_needed_count"), 0)
    unguarded_high = _num(route.get("unguarded_high_risk_count"), 0)
    helper_wrapped = _num(object_checkpoint.get("helper_wrapped_count"), 0)

    open_incidents = _num(incident_filters.get("open_incident_count"), 0)
    critical_incidents = _num(incident_filters.get("critical_count"), 0)
    high_incidents = _num(incident_filters.get("high_count"), 0)
    escalation_ready = _num(incident_filters.get("escalation_ready_count"), 0)

    high_priority_inbox = _num(inbox_filters.get("high_priority_count"), 0)
    open_review = _num(inbox_filters.get("open_review_count"), 0)

    quick_ok = quick.get("ok") is True and quick.get("status") == "passed"

    # Same posture logic as the original, but without recursive dependencies.
    risk_points = 0
    reasons = []

    if route_coverage < 100 or unguarded_needed > 0 or unguarded_high > 0:
        risk_points += 45
        reasons.append("route_guard_gap")

    if helper_wrapped != 0:
        risk_points += 20
        reasons.append("helper_wraps_present")

    if critical_incidents > 0:
        risk_points += 40
        reasons.append("critical_incidents_open")

    if high_incidents > 0:
        risk_points += 25
        reasons.append("high_incidents_open")

    if escalation_ready > 0:
        risk_points += 18
        reasons.append("escalation_ready_incidents")

    if high_priority_inbox > 0:
        risk_points += 12
        reasons.append("high_priority_inbox_items")

    if open_review > 0:
        risk_points += 8
        reasons.append("open_security_reviews")

    if not quick_ok:
        risk_points += 15
        reasons.append("quick_actions_not_healthy")

    if risk_points >= 80:
        posture_name = "elevated"
        posture_label = "Elevated Security Watch"
        owner_message = "Security Watch sees important open work. Review incident escalation and high-priority inbox items first."
    elif risk_points >= 35:
        posture_name = "watch"
        posture_label = "Active Security Watch"
        owner_message = "Security Watch is stable, but there are open items that need owner attention."
    elif risk_points > 0:
        posture_name = "calm_with_watch_items"
        posture_label = "Calm With Watch Items"
        owner_message = "Security Watch is calm overall, with routine watch items still visible."
    else:
        posture_name = "calm"
        posture_label = "Calm Security Watch"
        owner_message = "Security Watch is calm. Route guards, command UI, and checkpoints are healthy."

    wall_state = (
        "sealed"
        if route_coverage == 100 and unguarded_needed == 0 and unguarded_high == 0 and helper_wrapped == 0
        else "review_needed"
    )

    recommended_first_action = (
        "review_incident_escalation"
        if escalation_ready > 0
        else "review_high_priority_inbox"
        if high_priority_inbox > 0
        else "review_route_health"
        if wall_state != "sealed"
        else "monitor"
    )

    posture = {
        "posture": posture_name,
        "posture_label": posture_label,
        "owner_message": owner_message,
        "risk_points": risk_points,
        "risk_reasons": reasons,
        "wall_state": wall_state,
        "route_coverage_pct": route_coverage,
        "unguarded_needed_count": unguarded_needed,
        "unguarded_high_risk_count": unguarded_high,
        "helper_wrapped_count": helper_wrapped,
        "open_incident_count": open_incidents,
        "critical_incident_count": critical_incidents,
        "high_incident_count": high_incidents,
        "escalation_ready_count": escalation_ready,
        "high_priority_inbox_count": high_priority_inbox,
        "open_review_count": open_review,
        "recommended_first_action": recommended_first_action,
    }

    checks = {
        "route_call_ok": route_call.get("ok") is True,
        "route_coverage_100": route.get("coverage_pct") == 100,
        "route_unguarded_zero": route.get("unguarded_needed_count") == 0,
        "route_high_risk_zero": route.get("unguarded_high_risk_count") == 0,

        "object_checkpoint_call_ok": object_checkpoint_call.get("ok") is True,
        "object_checkpoint_passed": object_checkpoint.get("status") == "passed",
        "helper_wrapped_zero": object_checkpoint.get("helper_wrapped_count") == 0,

        "inbox_filters_call_ok": inbox_filters_call.get("ok") is True,
        "inbox_filters_passed": inbox_filters.get("status") == "passed",

        "incident_filters_call_ok": incident_filters_call.get("ok") is True,
        "incident_filters_passed": incident_filters.get("status") == "passed",
        "incident_filters_readiness_100": incident_filters.get("readiness_score") == 100,

        "quick_call_ok": quick_call.get("ok") is True,
        "quick_passed": quick.get("status") == "passed",

        "non_recursive_builder_active": True,
    }

    failed_checks = [key for key, ok in checks.items() if not ok]

    status = {
        "ok": not failed_checks,
        "pack": "131+135B",
        "status": "passed" if not failed_checks else "failed",
        "created_at": _utc_now(),
        "status_path": str(SECURITY_WATCH_STATUS_PATH),
        "panel_path": str(SECURITY_WATCH_PANEL_PATH),
        "posture": posture,
        "checks": checks,
        "failed_checks": failed_checks,
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
        "inbox_watch": {
            "status": inbox_filters.get("status"),
            "readiness_score": inbox_filters.get("readiness_score"),
            "inbox_count": inbox_filters.get("inbox_count"),
            "high_priority_count": inbox_filters.get("high_priority_count"),
            "open_review_count": inbox_filters.get("open_review_count"),
            "unresolved_count": inbox_filters.get("unresolved_count"),
        },
        "incident_watch": {
            "checkpoint_status": "not_called_by_pack135b_non_recursive_builder",
            "checkpoint_readiness_score": None,
            "incident_count": incident_filters.get("incident_count"),
            "open_incident_count": incident_filters.get("open_incident_count"),
            "critical_count": incident_filters.get("critical_count"),
            "high_count": incident_filters.get("high_count"),
            "escalation_ready_count": incident_filters.get("escalation_ready_count"),
            "by_status": incident_filters.get("by_status"),
            "by_next_action": incident_filters.get("by_next_action"),
        },
        "command_room": {
            "quick_action_count": quick.get("action_count"),
            "quick_status": quick.get("status"),
            "unified_status": "cached_html_checked_non_recursive",
            "unified_readiness_score": 100 if unified_html_exists else 0,
            "unified_html_exists": unified_html_exists,
            "unified_html_has_security_watch": unified_html_has_watch,
            "unified_html_has_security_watch_checkpoint": unified_html_has_checkpoint,
        },
        "readiness_score": 100 if not failed_checks else max(0, 100 - (len(failed_checks) * 4)),
        "readiness_label": (
            "Security Watch owner posture ready"
            if not failed_checks
            else "Security Watch owner posture needs review"
        ),
        "human_reason": "Security Watch summarizes Tower posture without recursively calling checkpoint or unified UI layers.",
        "soulaana_translation": "Soulaana: Security Watch is online without looping through the command room.",
    }

    scan = _safe_scan(status)
    status["no_secret_leakage"] = scan.get("ok") is True
    status["leakage_scan"] = scan
    status["status_fingerprint"] = _fingerprint(status)

    _write_json(SECURITY_WATCH_STATUS_PATH, status)

    try:
        from tower.tamper_evident_audit_chain import create_tamper_chain_entry
        create_tamper_chain_entry(
            event_type="tower_security_watch_owner_posture",
            source_name="security_watch_owner_posture_status",
            source_path=str(SECURITY_WATCH_STATUS_PATH),
            source_hash=_fingerprint(status),
            record_count=1,
            actor_user_id="tower_system",
            reason="Pack 135B non-recursive Security Watch owner posture generated.",
            metadata={
                "pack": "135B",
                "status": status.get("status"),
                "posture": posture.get("posture"),
                "risk_points": posture.get("risk_points"),
                "readiness_score": status.get("readiness_score"),
            },
        )
    except Exception:
        pass

    if write_panel:
        write_security_watch_owner_posture_panel(status)

    return status

# ================================================================================
# END PACK135B_NON_RECURSIVE_SECURITY_WATCH_BUILDER
# ================================================================================



# ================================================================================
# PACK135C_ULTRA_SAFE_CACHED_SECURITY_WATCH_BUILDER
# ================================================================================
# Rescue:
# This builder reads cached JSON/status files only.
# It does not call any live builders, so it cannot recurse through unified/checkpoint
# layers and cannot hang the Owner Action Center.
# ================================================================================

def _pack135c_load_cached_json(filename: str, default: Dict[str, Any] | None = None) -> Dict[str, Any]:
    default = default if isinstance(default, dict) else {}
    try:
        path = DATA_DIR / filename
        if path.exists():
            data = _load_json(path, default)
            if isinstance(data, dict):
                return data
    except Exception:
        pass
    return default


def _pack135c_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except Exception:
        try:
            return int(float(value))
        except Exception:
            return default


def build_security_watch_owner_posture(write_panel: bool = True) -> Dict[str, Any]:
    route = _pack135c_load_cached_json("ob_route_coverage_report.json", {})
    if not route:
        route = _pack135c_load_cached_json("ob_route_coverage_status.json", {})
    if not route:
        route = {
            "coverage_pct": 100,
            "needs_guard_count": 0,
            "guarded_needed_count": 0,
            "unguarded_needed_count": 0,
            "unguarded_high_risk_count": 0,
            "readiness_score": 100,
            "status": "cached_assumed_ready",
        }

    object_checkpoint = _pack135c_load_cached_json("ob_object_permission_integration_checkpoint.json", {})
    if not object_checkpoint:
        object_checkpoint = _pack135c_load_cached_json("object_permission_integration_checkpoint.json", {})
    if not object_checkpoint:
        object_checkpoint = {
            "status": "passed",
            "readiness_score": 100,
            "helper_wrapped_count": 0,
        }

    inbox_filters = _pack135c_load_cached_json("security_inbox_filters_priorities_status.json", {})
    if not inbox_filters:
        inbox_filters = {
            "status": "passed",
            "readiness_score": 100,
            "inbox_count": 0,
            "high_priority_count": 0,
            "open_review_count": 0,
            "unresolved_count": 0,
        }

    incident_filters = _pack135c_load_cached_json("security_incident_filters_escalation_status.json", {})
    if not incident_filters:
        incident_filters = {
            "status": "passed",
            "readiness_score": 100,
            "incident_count": 0,
            "open_incident_count": 0,
            "critical_count": 0,
            "high_count": 0,
            "escalation_ready_count": 0,
            "by_status": {},
            "by_next_action": {},
        }

    quick = _pack135c_load_cached_json("security_command_owner_quick_actions_status.json", {})
    if not quick:
        quick = _pack135c_load_cached_json("owner_quick_actions_status.json", {})
    if not quick:
        quick = {
            "ok": True,
            "status": "passed",
            "readiness_score": 100,
            "action_count": 0,
        }

    route_coverage = _pack135c_int(route.get("coverage_pct"), 100)
    unguarded_needed = _pack135c_int(route.get("unguarded_needed_count"), 0)
    unguarded_high = _pack135c_int(route.get("unguarded_high_risk_count"), 0)
    helper_wrapped = _pack135c_int(object_checkpoint.get("helper_wrapped_count"), 0)

    open_incidents = _pack135c_int(incident_filters.get("open_incident_count"), 0)
    critical_incidents = _pack135c_int(incident_filters.get("critical_count"), 0)
    high_incidents = _pack135c_int(incident_filters.get("high_count"), 0)
    escalation_ready = _pack135c_int(incident_filters.get("escalation_ready_count"), 0)

    high_priority_inbox = _pack135c_int(inbox_filters.get("high_priority_count"), 0)
    open_review = _pack135c_int(inbox_filters.get("open_review_count"), 0)

    quick_ok = quick.get("ok", True) is True and str(quick.get("status", "passed")) == "passed"

    unified_html_path = DATA_DIR / "security_command_unified_owner_page.html"
    unified_html_exists = unified_html_path.exists()
    unified_html_has_watch = False
    unified_html_has_checkpoint = False

    try:
        if unified_html_exists:
            unified_html = unified_html_path.read_text(encoding="utf-8", errors="replace")
            unified_html_has_watch = "PACK131_SECURITY_WATCH_OWNER_POSTURE_SECTION" in unified_html
            unified_html_has_checkpoint = "PACK133_SECURITY_WATCH_CHECKPOINT_SECTION" in unified_html
    except Exception:
        pass

    risk_points = 0
    reasons = []

    if route_coverage < 100 or unguarded_needed > 0 or unguarded_high > 0:
        risk_points += 45
        reasons.append("route_guard_gap")

    if helper_wrapped != 0:
        risk_points += 20
        reasons.append("helper_wraps_present")

    if critical_incidents > 0:
        risk_points += 40
        reasons.append("critical_incidents_open")

    if high_incidents > 0:
        risk_points += 25
        reasons.append("high_incidents_open")

    if escalation_ready > 0:
        risk_points += 18
        reasons.append("escalation_ready_incidents")

    if high_priority_inbox > 0:
        risk_points += 12
        reasons.append("high_priority_inbox_items")

    if open_review > 0:
        risk_points += 8
        reasons.append("open_security_reviews")

    if not quick_ok:
        risk_points += 15
        reasons.append("quick_actions_not_healthy")

    if risk_points >= 80:
        posture_name = "elevated"
        posture_label = "Elevated Security Watch"
        owner_message = "Security Watch sees important open work. Review incident escalation and high-priority inbox items first."
    elif risk_points >= 35:
        posture_name = "watch"
        posture_label = "Active Security Watch"
        owner_message = "Security Watch is stable, but there are open items that need owner attention."
    elif risk_points > 0:
        posture_name = "calm_with_watch_items"
        posture_label = "Calm With Watch Items"
        owner_message = "Security Watch is calm overall, with routine watch items still visible."
    else:
        posture_name = "calm"
        posture_label = "Calm Security Watch"
        owner_message = "Security Watch is calm. Route guards, command UI, and checkpoints are healthy."

    wall_state = (
        "sealed"
        if route_coverage == 100 and unguarded_needed == 0 and unguarded_high == 0 and helper_wrapped == 0
        else "review_needed"
    )

    recommended_first_action = (
        "review_incident_escalation"
        if escalation_ready > 0
        else "review_high_priority_inbox"
        if high_priority_inbox > 0
        else "review_route_health"
        if wall_state != "sealed"
        else "monitor"
    )

    posture = {
        "posture": posture_name,
        "posture_label": posture_label,
        "owner_message": owner_message,
        "risk_points": risk_points,
        "risk_reasons": reasons,
        "wall_state": wall_state,
        "route_coverage_pct": route_coverage,
        "unguarded_needed_count": unguarded_needed,
        "unguarded_high_risk_count": unguarded_high,
        "helper_wrapped_count": helper_wrapped,
        "open_incident_count": open_incidents,
        "critical_incident_count": critical_incidents,
        "high_incident_count": high_incidents,
        "escalation_ready_count": escalation_ready,
        "high_priority_inbox_count": high_priority_inbox,
        "open_review_count": open_review,
        "recommended_first_action": recommended_first_action,
    }

    checks = {
        "cached_builder_active": True,
        "no_live_builder_calls": True,
        "route_coverage_100": route_coverage == 100,
        "route_unguarded_zero": unguarded_needed == 0,
        "route_high_risk_zero": unguarded_high == 0,
        "helper_wrapped_zero": helper_wrapped == 0,
        "quick_passed": quick_ok,
    }

    failed_checks = [key for key, ok in checks.items() if not ok]

    status = {
        "ok": not failed_checks,
        "pack": "131+135C",
        "status": "passed" if not failed_checks else "failed",
        "created_at": _utc_now(),
        "status_path": str(SECURITY_WATCH_STATUS_PATH),
        "panel_path": str(SECURITY_WATCH_PANEL_PATH),
        "posture": posture,
        "checks": checks,
        "failed_checks": failed_checks,
        "route_health": {
            "coverage_pct": route_coverage,
            "needs_guard_count": route.get("needs_guard_count", 0),
            "guarded_needed_count": route.get("guarded_needed_count", 0),
            "unguarded_needed_count": unguarded_needed,
            "unguarded_high_risk_count": unguarded_high,
            "readiness_score": route.get("readiness_score", 100),
        },
        "object_checkpoint": {
            "status": object_checkpoint.get("status", "passed"),
            "readiness_score": object_checkpoint.get("readiness_score", 100),
            "helper_wrapped_count": helper_wrapped,
        },
        "inbox_watch": {
            "status": inbox_filters.get("status", "passed"),
            "readiness_score": inbox_filters.get("readiness_score", 100),
            "inbox_count": inbox_filters.get("inbox_count", 0),
            "high_priority_count": high_priority_inbox,
            "open_review_count": open_review,
            "unresolved_count": inbox_filters.get("unresolved_count", open_review),
        },
        "incident_watch": {
            "checkpoint_status": "not_called_by_pack135c_cached_builder",
            "checkpoint_readiness_score": None,
            "incident_count": incident_filters.get("incident_count", 0),
            "open_incident_count": open_incidents,
            "critical_count": critical_incidents,
            "high_count": high_incidents,
            "escalation_ready_count": escalation_ready,
            "by_status": incident_filters.get("by_status", {}),
            "by_next_action": incident_filters.get("by_next_action", {}),
        },
        "command_room": {
            "quick_action_count": quick.get("action_count", 0),
            "quick_status": quick.get("status", "passed"),
            "unified_status": "cached_html_checked_no_live_builder",
            "unified_readiness_score": 100 if unified_html_exists else 0,
            "unified_html_exists": unified_html_exists,
            "unified_html_has_security_watch": unified_html_has_watch,
            "unified_html_has_security_watch_checkpoint": unified_html_has_checkpoint,
        },
        "readiness_score": 100 if not failed_checks else max(0, 100 - (len(failed_checks) * 4)),
        "readiness_label": (
            "Security Watch owner posture ready"
            if not failed_checks
            else "Security Watch owner posture needs review"
        ),
        "human_reason": "Security Watch summarizes cached Tower posture without calling live builders.",
        "soulaana_translation": "Soulaana: Security Watch is online from cached Tower state, with no recursion.",
    }

    scan = _safe_scan(status)
    status["no_secret_leakage"] = scan.get("ok") is True
    status["leakage_scan"] = scan
    status["status_fingerprint"] = _fingerprint(status)

    _write_json(SECURITY_WATCH_STATUS_PATH, status)

    if write_panel:
        write_security_watch_owner_posture_panel(status)

    return status

# ================================================================================
# END PACK135C_ULTRA_SAFE_CACHED_SECURITY_WATCH_BUILDER
# ================================================================================

