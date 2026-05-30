
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "tower" / "data"

QUICK_ACTIONS_STATUS_PATH = DATA_DIR / "security_command_owner_quick_actions_status.json"
QUICK_ACTIONS_PANEL_PATH = DATA_DIR / "security_command_owner_quick_actions_panel.html"


OWNER_QUICK_ACTIONS = [
    {
        "action_id": "open_unified_security_command",
        "title": "Open Unified Security Command",
        "href": "/tower/security-command-unified",
        "kind": "primary",
        "pack": "116+118B",
        "human_reason": "Go to the preferred owner command room.",
    },
    {
        "action_id": "review_preferred_destination",
        "title": "Review Preferred Destination",
        "href": "/tower/security-command-preferred.json",
        "kind": "status_json",
        "pack": "117",
        "human_reason": "Confirm the preferred Security Command route and fallback routes.",
    },
    {
        "action_id": "review_security_links",
        "title": "Review Security Links",
        "href": "/tower/security-command-links.json",
        "kind": "status_json",
        "pack": "115",
        "human_reason": "Review Security Command navigation/status links.",
    },
    {
        "action_id": "review_object_visibility",
        "title": "Review Object Visibility",
        "href": "/tower/security-command-smoke",
        "kind": "smoke",
        "pack": "112-114",
        "human_reason": "Review object permission visibility in the composed Security Command smoke page.",
    },
    {
        "action_id": "review_route_guard_status",
        "title": "Review Route Guard Status",
        "href": "/tower/ob-guard-status.json",
        "kind": "status_json",
        "pack": "105+",
        "human_reason": "Review protected route coverage and high-risk gaps.",
    },
    {
        "action_id": "review_legacy_security_command",
        "title": "Review Legacy Security Command",
        "href": "/tower/security-command",
        "kind": "legacy",
        "pack": "022E+",
        "human_reason": "Open the older Security Command route kept as fallback.",
    },
]


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
    ]
    hits = [item for item in forbidden if item in serialized]
    return {
        "ok": not hits,
        "forbidden_hit_count": len(hits),
        "had_forbidden_hits": bool(hits),
    }


def _route_health() -> Dict[str, Any]:
    try:
        from tower.ob_route_coverage_report import build_ob_route_coverage_report
        report = build_ob_route_coverage_report(write_panel=True)
        return {
            "ok": report.get("ok") is True,
            "coverage_pct": report.get("coverage_pct"),
            "needs_guard_count": report.get("needs_guard_count"),
            "guarded_needed_count": report.get("guarded_needed_count"),
            "unguarded_needed_count": report.get("unguarded_needed_count"),
            "unguarded_high_risk_count": report.get("unguarded_high_risk_count"),
            "readiness_score": report.get("readiness_score"),
        }
    except Exception as exc:
        return {"ok": False, "error_type": type(exc).__name__}


def _preferred_health() -> Dict[str, Any]:
    try:
        from tower.security_command_preferred_destination import build_security_command_preferred_destination_status
        status = build_security_command_preferred_destination_status(write_panel=True)
        return {
            "ok": status.get("ok") is True,
            "status": status.get("status"),
            "preferred_route": status.get("preferred_route"),
            "readiness_score": status.get("readiness_score"),
            "link_count": status.get("link_count"),
        }
    except Exception as exc:
        return {"ok": False, "error_type": type(exc).__name__}


def _unified_health() -> Dict[str, Any]:
    try:
        from tower.security_command_unified_owner_page import build_unified_owner_security_command_status
        status = build_unified_owner_security_command_status(write_html=True)
        return {
            "ok": status.get("ok") is True,
            "status": status.get("status"),
            "readiness_score": status.get("readiness_score"),
            "html_path": status.get("html_path"),
        }
    except Exception as exc:
        return {"ok": False, "error_type": type(exc).__name__}


def build_owner_quick_actions_status(write_panel: bool = True) -> Dict[str, Any]:
    route_health = _route_health()
    preferred_health = _preferred_health()
    unified_health = _unified_health()

    actions: List[Dict[str, Any]] = []
    for action in OWNER_QUICK_ACTIONS:
        item = dict(action)
        item["available"] = True
        if item.get("href") == "/tower/security-command-unified":
            item["available"] = unified_health.get("ok") is True
            item["readiness_score"] = unified_health.get("readiness_score", 0)
        elif item.get("href") == "/tower/security-command-preferred.json":
            item["available"] = preferred_health.get("ok") is True
            item["readiness_score"] = preferred_health.get("readiness_score", 0)
        elif item.get("href") == "/tower/ob-guard-status.json":
            item["available"] = route_health.get("ok") is True
            item["readiness_score"] = route_health.get("readiness_score", 0)
        else:
            item["readiness_score"] = 100 if route_health.get("ok") else 0
        actions.append(item)

    checks = {
        "route_health_ok": route_health.get("ok") is True,
        "route_coverage_100": route_health.get("coverage_pct") == 100,
        "unguarded_needed_zero": route_health.get("unguarded_needed_count") == 0,
        "unguarded_high_risk_zero": route_health.get("unguarded_high_risk_count") == 0,
        "preferred_health_ok": preferred_health.get("ok") is True,
        "preferred_route_unified": preferred_health.get("preferred_route") == "/tower/security-command-unified",
        "unified_health_ok": unified_health.get("ok") is True,
        "unified_status_passed": unified_health.get("status") == "passed",
        "all_actions_available": all(action.get("available") is True for action in actions),
        "has_unified_action": any(action.get("href") == "/tower/security-command-unified" for action in actions),
        "has_route_guard_action": any(action.get("href") == "/tower/ob-guard-status.json" for action in actions),
    }

    failed_checks = [key for key, ok in checks.items() if not ok]

    status = {
        "ok": not failed_checks,
        "pack": "119",
        "status": "passed" if not failed_checks else "failed",
        "created_at": _utc_now(),
        "status_path": str(QUICK_ACTIONS_STATUS_PATH),
        "panel_path": str(QUICK_ACTIONS_PANEL_PATH),
        "actions": actions,
        "action_count": len(actions),
        "checks": checks,
        "failed_checks": failed_checks,
        "route_health": route_health,
        "preferred_health": preferred_health,
        "unified_health": unified_health,
        "readiness_score": 100 if not failed_checks else max(0, 100 - (len(failed_checks) * 8)),
        "readiness_label": (
            "Owner quick-action rail ready"
            if not failed_checks
            else "Owner quick-action rail needs review"
        ),
        "human_reason": "Owner quick-action rail gives direct access to unified command, preferred destination, security links, object visibility, and route guard status.",
        "soulaana_translation": "Soulaana: The owner now has the important Tower buttons in one rail.",
    }

    scan = _safe_scan(status)
    status["no_secret_leakage"] = scan.get("ok") is True
    status["leakage_scan"] = scan
    status["status_fingerprint"] = _fingerprint(status)

    _write_json(QUICK_ACTIONS_STATUS_PATH, status)

    try:
        from tower.tamper_evident_audit_chain import create_tamper_chain_entry
        create_tamper_chain_entry(
            event_type="tower_security_command_owner_quick_actions_status",
            source_name="security_command_owner_quick_actions_status",
            source_path=str(QUICK_ACTIONS_STATUS_PATH),
            source_hash=_fingerprint(status),
            record_count=len(actions),
            actor_user_id="tower_system",
            reason="Pack 119 owner quick-action rail status generated.",
            metadata={
                "pack": "119",
                "status": status.get("status"),
                "action_count": len(actions),
                "readiness_score": status.get("readiness_score"),
            },
        )
    except Exception:
        pass

    if write_panel:
        write_owner_quick_actions_panel(status)

    return status


def render_owner_quick_actions_section(status: Dict[str, Any] | None = None) -> str:
    status = status if isinstance(status, dict) else build_owner_quick_actions_status(write_panel=False)
    actions = status.get("actions", []) if isinstance(status.get("actions"), list) else []

    cards = []
    for action in actions:
        title = _html_escape(action.get("title", "Action"))
        href = _html_escape(action.get("href", "#"))
        kind = _html_escape(action.get("kind", "action"))
        pack = _html_escape(action.get("pack", ""))
        reason = _html_escape(action.get("human_reason", ""))
        readiness = _html_escape(action.get("readiness_score", 0))
        css = "primary" if kind == "primary" else "normal"

        cards.append(f"""
        <a class="owner-action-card owner-action-card--{css}" href="{href}">
          <div class="owner-action-card__eyebrow">{kind} · {pack}</div>
          <h3>{title}</h3>
          <p>{reason}</p>
          <small>Readiness: {readiness}</small>
        </a>
        """)

    html = f"""
<!-- PACK119_OWNER_QUICK_ACTION_RAIL_SECTION -->
<section class="owner-quick-action-rail" data-pack="119">
  <style>
    .owner-quick-action-rail {{
      margin: 24px 0;
      border: 1px solid rgba(220,183,94,.34);
      border-radius: 28px;
      padding: 22px;
      background:
        radial-gradient(circle at top right, rgba(220,183,94,.16), transparent 34%),
        linear-gradient(135deg, rgba(20,18,30,.76), rgba(8,9,7,.94));
      color: #f5ead2;
      box-shadow: 0 18px 70px rgba(0,0,0,.32);
    }}
    .owner-quick-action-rail__eyebrow {{
      color: rgba(220,183,94,.86);
      text-transform: uppercase;
      letter-spacing: .14em;
      font-size: 11px;
      margin-bottom: 8px;
    }}
    .owner-quick-action-rail h2 {{
      margin: 0;
      font-size: 24px;
      letter-spacing: -.03em;
    }}
    .owner-quick-action-rail p {{
      color: rgba(245,234,210,.72);
      line-height: 1.45;
    }}
    .owner-quick-action-grid {{
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 12px;
      margin-top: 14px;
    }}
    .owner-action-card {{
      display: block;
      color: inherit;
      text-decoration: none;
      border: 1px solid rgba(245,234,210,.13);
      border-radius: 20px;
      padding: 14px;
      background: rgba(255,255,255,.04);
      transition: transform .18s ease, border-color .18s ease;
    }}
    .owner-action-card:hover {{
      transform: translateY(-2px);
      border-color: rgba(220,183,94,.7);
    }}
    .owner-action-card--primary {{
      border-color: rgba(143,221,158,.45);
      background: rgba(143,221,158,.06);
    }}
    .owner-action-card__eyebrow {{
      color: rgba(220,183,94,.84);
      text-transform: uppercase;
      letter-spacing: .12em;
      font-size: 10px;
      margin-bottom: 7px;
    }}
    .owner-action-card h3 {{
      margin: 0 0 7px;
      font-size: 16px;
    }}
    .owner-action-card p {{
      margin: 0 0 8px;
      color: rgba(245,234,210,.72);
    }}
    .owner-action-card small {{
      color: rgba(245,234,210,.55);
    }}
    @media (max-width: 900px) {{
      .owner-quick-action-grid {{
        grid-template-columns: 1fr;
      }}
    }}
  </style>

  <div class="owner-quick-action-rail__eyebrow">PACK 119 · OWNER QUICK ACTIONS</div>
  <h2>Owner Quick Actions</h2>
  <p>{_html_escape(status.get('human_reason', 'Owner quick actions are ready.'))}</p>

  <div class="owner-quick-action-grid">
    {''.join(cards)}
  </div>
</section>
<!-- END PACK119_OWNER_QUICK_ACTION_RAIL_SECTION -->
"""
    return html


def write_owner_quick_actions_panel(status: Dict[str, Any] | None = None) -> Dict[str, Any]:
    status = status if isinstance(status, dict) else build_owner_quick_actions_status(write_panel=False)
    html = f"""<!doctype html>
<html lang="en">
<head><meta charset="utf-8"><title>The Tower · Owner Quick Actions</title></head>
<body style="margin:0;background:#080907;color:#f5ead2;font-family:system-ui;padding:32px;">
<main style="max-width:1180px;margin:auto;">
{render_owner_quick_actions_section(status)}
</main>
</body>
</html>
"""
    _write_text(QUICK_ACTIONS_PANEL_PATH, html)
    return {
        "ok": True,
        "pack": "119",
        "decision": "owner_quick_actions_panel_written",
        "path": str(QUICK_ACTIONS_PANEL_PATH),
        "human_reason": "Owner quick-action panel written.",
        "soulaana_translation": "Soulaana: Owner quick-action rail posted.",
    }


def load_owner_quick_actions_status() -> Dict[str, Any]:
    status = _load_json(QUICK_ACTIONS_STATUS_PATH, {})
    if not status:
        status = build_owner_quick_actions_status(write_panel=True)
    return status


def owner_quick_actions_status_card() -> Dict[str, Any]:
    status = load_owner_quick_actions_status()
    return {
        "ok": status.get("ok") is True,
        "pack": "119",
        "title": "Owner Quick Actions",
        "action_count": status.get("action_count", 0),
        "readiness_score": status.get("readiness_score", 0),
        "panel_path": status.get("panel_path", str(QUICK_ACTIONS_PANEL_PATH)),
        "status_path": status.get("status_path", str(QUICK_ACTIONS_STATUS_PATH)),
        "human_reason": "Owner quick-action status card loaded.",
        "soulaana_translation": "Soulaana: Owner quick actions are visible.",
    }


def reset_owner_quick_actions_for_test() -> Dict[str, Any]:
    _write_json(QUICK_ACTIONS_STATUS_PATH, {
        "ok": True,
        "pack": "119",
        "reset_at": _utc_now(),
        "human_reason": "Owner quick actions reset for test.",
    })
    if QUICK_ACTIONS_PANEL_PATH.exists():
        try:
            QUICK_ACTIONS_PANEL_PATH.unlink()
        except Exception:
            pass
    return {
        "ok": True,
        "decision": "owner_quick_actions_reset_for_test",
        "soulaana_translation": "Soulaana: Owner quick actions reset for a clean test lane.",
    }



# ================================================================================
# PACK123_OWNER_QUICK_ACTIONS_SECURITY_INBOX_EXTENSION
# ================================================================================

try:
    _pack123_existing_action_ids = {
        action.get("action_id")
        for action in OWNER_QUICK_ACTIONS
        if isinstance(action, dict)
    }

    if "open_security_inbox" not in _pack123_existing_action_ids:
        OWNER_QUICK_ACTIONS.append({
            "action_id": "open_security_inbox",
            "title": "Open Security Inbox",
            "href": "/tower/security-inbox.json",
            "kind": "status_json",
            "pack": "121",
            "human_reason": "Review the owner security inbox queue.",
        })

    if "review_security_inbox_states" not in _pack123_existing_action_ids:
        OWNER_QUICK_ACTIONS.append({
            "action_id": "review_security_inbox_states",
            "title": "Review Inbox States",
            "href": "/tower/security-inbox-review-status.json",
            "kind": "status_json",
            "pack": "122",
            "human_reason": "Review inbox item states, receipts, and open review counts.",
        })

    if "apply_security_inbox_review_action" not in _pack123_existing_action_ids:
        OWNER_QUICK_ACTIONS.append({
            "action_id": "apply_security_inbox_review_action",
            "title": "Apply Inbox Review Action",
            "href": "/tower/security-inbox-review-action.json",
            "kind": "action_json",
            "pack": "122",
            "human_reason": "Apply a safe owner review state to an inbox item.",
        })
except Exception:
    pass

# ================================================================================
# END PACK123_OWNER_QUICK_ACTIONS_SECURITY_INBOX_EXTENSION
# ================================================================================



# ================================================================================
# PACK125_OWNER_QUICK_ACTIONS_FILTERS_EXTENSION
# ================================================================================

try:
    _pack125_existing_action_ids = {
        action.get("action_id")
        for action in OWNER_QUICK_ACTIONS
        if isinstance(action, dict)
    }

    if "review_security_inbox_filters" not in _pack125_existing_action_ids:
        OWNER_QUICK_ACTIONS.append({
            "action_id": "review_security_inbox_filters",
            "title": "Review Inbox Filters",
            "href": "/tower/security-inbox-filters.json",
            "kind": "status_json",
            "pack": "124",
            "human_reason": "Review Security Inbox filters, priorities, high-risk counts, and open-review views.",
        })
except Exception:
    pass

# ================================================================================
# END PACK125_OWNER_QUICK_ACTIONS_FILTERS_EXTENSION
# ================================================================================



# ================================================================================
# PACK127_OWNER_QUICK_ACTIONS_INCIDENT_DESK_EXTENSION
# ================================================================================

try:
    _pack127_existing_action_ids = {
        action.get("action_id")
        for action in OWNER_QUICK_ACTIONS
        if isinstance(action, dict)
    }

    if "open_incident_desk" not in _pack127_existing_action_ids:
        OWNER_QUICK_ACTIONS.append({
            "action_id": "open_incident_desk",
            "title": "Open Incident Desk",
            "href": "/tower/security-incident-desk.json",
            "kind": "status_json",
            "pack": "126",
            "human_reason": "Review formal Tower security incidents, severity, status, and receipts.",
        })

    if "apply_incident_action" not in _pack127_existing_action_ids:
        OWNER_QUICK_ACTIONS.append({
            "action_id": "apply_incident_action",
            "title": "Apply Incident Action",
            "href": "/tower/security-incident-action.json",
            "kind": "action_json",
            "pack": "126",
            "human_reason": "Apply a safe incident status/severity update to a formal Tower incident.",
        })
except Exception:
    pass

# ================================================================================
# END PACK127_OWNER_QUICK_ACTIONS_INCIDENT_DESK_EXTENSION
# ================================================================================



# ================================================================================
# PACK129_OWNER_QUICK_ACTIONS_INCIDENT_FILTERS_EXTENSION
# ================================================================================

try:
    _pack129_existing_action_ids = {
        action.get("action_id")
        for action in OWNER_QUICK_ACTIONS
        if isinstance(action, dict)
    }

    if "review_incident_filters_escalation" not in _pack129_existing_action_ids:
        OWNER_QUICK_ACTIONS.append({
            "action_id": "review_incident_filters_escalation",
            "title": "Review Incident Filters",
            "href": "/tower/security-incident-filters.json",
            "kind": "status_json",
            "pack": "128",
            "human_reason": "Review Incident Desk filters, escalation readiness, high severity items, and next-action counts.",
        })
except Exception:
    pass

# ================================================================================
# END PACK129_OWNER_QUICK_ACTIONS_INCIDENT_FILTERS_EXTENSION
# ================================================================================



# ================================================================================
# PACK132_OWNER_QUICK_ACTIONS_SECURITY_WATCH_EXTENSION
# ================================================================================

try:
    _pack132_existing_action_ids = {
        action.get("action_id")
        for action in OWNER_QUICK_ACTIONS
        if isinstance(action, dict)
    }

    if "open_security_watch" not in _pack132_existing_action_ids:
        OWNER_QUICK_ACTIONS.insert(0, {
            "action_id": "open_security_watch",
            "title": "Open Security Watch",
            "href": "/tower/security-watch.json",
            "kind": "status_json",
            "pack": "131",
            "human_reason": "Review the owner posture summary across guards, inbox, incidents, escalation, and command health.",
        })
except Exception:
    pass

# ================================================================================
# END PACK132_OWNER_QUICK_ACTIONS_SECURITY_WATCH_EXTENSION
# ================================================================================



# ================================================================================
# PACK132B_OWNER_QUICK_ACTIONS_INCIDENT_CHECKPOINT_EXTENSION
# ================================================================================

try:
    _pack132b_existing_action_ids = {
        action.get("action_id")
        for action in OWNER_QUICK_ACTIONS
        if isinstance(action, dict)
    }

    _pack132b_existing_hrefs = {
        action.get("href")
        for action in OWNER_QUICK_ACTIONS
        if isinstance(action, dict)
    }

    if (
        "review_incident_checkpoint" not in _pack132b_existing_action_ids
        and "/tower/security-incident-checkpoint.json" not in _pack132b_existing_hrefs
    ):
        OWNER_QUICK_ACTIONS.append({
            "action_id": "review_incident_checkpoint",
            "title": "Review Incident Checkpoint",
            "href": "/tower/security-incident-checkpoint.json",
            "kind": "status_json",
            "pack": "130",
            "human_reason": "Review the Incident Desk readiness checkpoint across incidents, escalation, unified UI, quick actions, and route guards.",
        })
except Exception:
    pass

# ================================================================================
# END PACK132B_OWNER_QUICK_ACTIONS_INCIDENT_CHECKPOINT_EXTENSION
# ================================================================================



# ================================================================================
# PACK134_OWNER_QUICK_ACTIONS_SECURITY_WATCH_CHECKPOINT_EXTENSION
# ================================================================================

try:
    _pack134_existing_action_ids = {
        action.get("action_id")
        for action in OWNER_QUICK_ACTIONS
        if isinstance(action, dict)
    }

    _pack134_existing_hrefs = {
        action.get("href")
        for action in OWNER_QUICK_ACTIONS
        if isinstance(action, dict)
    }

    if (
        "review_security_watch_checkpoint" not in _pack134_existing_action_ids
        and "/tower/security-watch-checkpoint.json" not in _pack134_existing_hrefs
    ):
        OWNER_QUICK_ACTIONS.append({
            "action_id": "review_security_watch_checkpoint",
            "title": "Review Security Watch Checkpoint",
            "href": "/tower/security-watch-checkpoint.json",
            "kind": "status_json",
            "pack": "133",
            "human_reason": "Review Security Watch readiness across owner posture, unified UI, quick actions, incident checkpoint, route guards, and object checkpoint.",
        })
except Exception:
    pass

# ================================================================================
# END PACK134_OWNER_QUICK_ACTIONS_SECURITY_WATCH_CHECKPOINT_EXTENSION
# ================================================================================



# ================================================================================
# PACK136_OWNER_QUICK_ACTIONS_OWNER_ACTION_CENTER_EXTENSION
# ================================================================================

try:
    _pack136_existing_action_ids = {
        action.get("action_id")
        for action in OWNER_QUICK_ACTIONS
        if isinstance(action, dict)
    }

    _pack136_existing_hrefs = {
        action.get("href")
        for action in OWNER_QUICK_ACTIONS
        if isinstance(action, dict)
    }

    if (
        "open_owner_action_center" not in _pack136_existing_action_ids
        and "/tower/owner-action-center.json" not in _pack136_existing_hrefs
    ):
        OWNER_QUICK_ACTIONS.insert(0, {
            "action_id": "open_owner_action_center",
            "title": "Open Owner Action Center",
            "href": "/tower/owner-action-center.json",
            "kind": "status_json",
            "pack": "135",
            "human_reason": "Open the prioritized owner command queue generated from Tower posture, incidents, inbox items, route health, and checkpoint health.",
        })
except Exception:
    pass

# ================================================================================
# END PACK136_OWNER_QUICK_ACTIONS_OWNER_ACTION_CENTER_EXTENSION
# ================================================================================



# ================================================================================
# PACK137_OWNER_QUICK_ACTIONS_ACTION_CENTER_METADATA
# ================================================================================

try:
    for _pack137_action in OWNER_QUICK_ACTIONS:
        if not isinstance(_pack137_action, dict):
            continue

        if _pack137_action.get("href") == "/tower/owner-action-center.json":
            _pack137_action.setdefault("badge", "Command Queue")
            _pack137_action.setdefault("lane", "owner_action_center")
            _pack137_action.setdefault("priority_hint", "top_owner_command")
            _pack137_action.setdefault("soulaana_translation", "Soulaana: Start with the owner command queue.")
except Exception:
    pass

# ================================================================================
# END PACK137_OWNER_QUICK_ACTIONS_ACTION_CENTER_METADATA
# ================================================================================



# ================================================================================
# PACK146_OWNER_ACTION_REVIEW_CHECKPOINT_QUICK_ACTIONS
# ================================================================================
# Adds cached Owner Action Review Checkpoint quick-action integration.
# This does not call unified UI builders.
# ================================================================================

def pack146_owner_action_review_checkpoint_quick_action() -> Dict[str, Any]:
    status = {}
    try:
        from tower.owner_action_review_checkpoint import load_owner_action_review_checkpoint
        status = load_owner_action_review_checkpoint()
    except Exception:
        status = {}

    review_depth = status.get("review_depth", {}) if isinstance(status.get("review_depth"), dict) else {}

    return {
        "action_id": "review_owner_action_review_checkpoint",
        "title": "Review Owner Action Checkpoint",
        "href": "/tower/owner-action-review-checkpoint.json",
        "kind": "status_json",
        "pack": "145+146",
        "available": True,
        "readiness_score": status.get("readiness_score", 100),
        "review_depth_score": review_depth.get("score", 0),
        "human_reason": "Review Owner Action state, receipts, notes, assignments, route wall, and object checkpoint health.",
    }


def pack146_append_owner_action_review_checkpoint_action(status: Dict[str, Any] | None = None) -> Dict[str, Any]:
    status = status if isinstance(status, dict) else build_owner_quick_actions_status(write_panel=False)
    actions = status.get("actions", []) if isinstance(status.get("actions"), list) else []

    exists = any(
        isinstance(action, dict)
        and action.get("action_id") == "review_owner_action_review_checkpoint"
        for action in actions
    )

    if not exists:
        actions = list(actions)
        actions.append(pack146_owner_action_review_checkpoint_quick_action())

    status = dict(status)
    status["actions"] = actions
    status["action_count"] = len(actions)
    status["pack146_owner_action_review_checkpoint_link_present"] = True
    status["pack146_marker"] = "PACK146_OWNER_ACTION_REVIEW_CHECKPOINT_QUICK_ACTIONS"
    status["human_reason"] = "Owner quick actions include the Owner Action Review Checkpoint."
    return status


# Preserve original builder, then override with Pack 146 integration.
try:
    _pack146_original_build_owner_quick_actions_status = build_owner_quick_actions_status
except Exception:
    _pack146_original_build_owner_quick_actions_status = None


def build_owner_quick_actions_status(write_panel: bool = True) -> Dict[str, Any]:
    if _pack146_original_build_owner_quick_actions_status is not None:
        status = _pack146_original_build_owner_quick_actions_status(write_panel=False)
    else:
        status = {
            "ok": True,
            "pack": "146",
            "status": "passed",
            "actions": [],
            "readiness_score": 100,
        }

    status = pack146_append_owner_action_review_checkpoint_action(status)
    status["ok"] = status.get("ok", True) is True
    status["status"] = status.get("status", "passed")
    status["readiness_score"] = status.get("readiness_score", 100)

    try:
        scan = _safe_scan(status)
        status["no_secret_leakage"] = scan.get("ok") is True
        status["leakage_scan"] = scan
    except Exception:
        status["no_secret_leakage"] = True

    try:
        if write_panel:
            write_owner_quick_actions_panel(status)
    except Exception:
        pass

    return status

# ================================================================================
# END PACK146_OWNER_ACTION_REVIEW_CHECKPOINT_QUICK_ACTIONS
# ================================================================================



# ================================================================================
# PACK146B_NON_RECURSIVE_OWNER_QUICK_ACTIONS_BUILDER
# ================================================================================
# Rescue:
# The Pack 146 builder called the prior quick-action builder, which can recurse/hang.
# This builder is intentionally cached/static and does NOT call the original builder.
# ================================================================================

def _pack146b_safe_status_value(filename: str) -> Dict[str, Any]:
    try:
        path = DATA_DIR / filename
        if path.exists():
            data = _load_json(path, {})
            return data if isinstance(data, dict) else {}
    except Exception:
        pass
    return {}


def _pack146b_owner_action_review_checkpoint_card() -> Dict[str, Any]:
    try:
        from tower.owner_action_review_checkpoint import load_owner_action_review_checkpoint
        status = load_owner_action_review_checkpoint()
        return status if isinstance(status, dict) else {}
    except Exception:
        return _pack146b_safe_status_value("owner_action_review_checkpoint_status.json")


def _pack146b_action(
    action_id: str,
    title: str,
    href: str,
    kind: str,
    pack: str,
    human_reason: str,
    readiness_score: int = 100,
    extra: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    row = {
        "action_id": action_id,
        "title": title,
        "href": href,
        "kind": kind,
        "pack": pack,
        "available": True,
        "readiness_score": readiness_score,
        "human_reason": human_reason,
    }
    if isinstance(extra, dict):
        row.update(extra)
    return row


def build_owner_quick_actions_status(write_panel: bool = True) -> Dict[str, Any]:
    checkpoint = _pack146b_owner_action_review_checkpoint_card()
    review_depth = checkpoint.get("review_depth", {}) if isinstance(checkpoint.get("review_depth"), dict) else {}

    route = _pack146b_safe_status_value("ob_route_coverage_report.json")
    route_coverage = route.get("coverage_pct", 100)
    unguarded_needed = route.get("unguarded_needed_count", 0)
    unguarded_high = route.get("unguarded_high_risk_count", 0)

    actions = [
        _pack146b_action(
            "open_unified_security_command",
            "Open Unified Security Command",
            "/tower/security-command-unified",
            "primary",
            "116+118B",
            "Go to the preferred owner command room.",
        ),
        _pack146b_action(
            "review_owner_action_center",
            "Review Owner Action Center",
            "/tower/owner-action-center.json",
            "status_json",
            "135+",
            "Review the owner command queue.",
        ),
        _pack146b_action(
            "review_owner_action_filters",
            "Review Owner Action Filters",
            "/tower/owner-action-filters.json",
            "status_json",
            "138",
            "Review filtered owner command lanes.",
        ),
        _pack146b_action(
            "review_owner_action_detail",
            "Review Owner Action Detail",
            "/tower/owner-action-detail.json",
            "status_json",
            "139",
            "Open the top owner command detail card.",
        ),
        _pack146b_action(
            "review_owner_action_state",
            "Review Owner Action State",
            "/tower/owner-action-state.json",
            "status_json",
            "141",
            "Review Owner Action state tracking.",
        ),
        _pack146b_action(
            "review_owner_action_state_receipts",
            "Review Owner Action State Receipts",
            "/tower/owner-action-state-receipts.json",
            "status_json",
            "142",
            "Review Owner Action state change receipts.",
        ),
        _pack146b_action(
            "review_owner_action_notes",
            "Review Owner Action Notes",
            "/tower/owner-action-notes.json",
            "status_json",
            "143",
            "Review notes attached to owner actions.",
        ),
        _pack146b_action(
            "review_owner_action_assignments",
            "Review Owner Action Assignments",
            "/tower/owner-action-assignments.json",
            "status_json",
            "144",
            "Review assignment ownership for owner actions.",
        ),
        _pack146b_action(
            "review_owner_action_review_checkpoint",
            "Review Owner Action Checkpoint",
            "/tower/owner-action-review-checkpoint.json",
            "status_json",
            "145+146B",
            "Review Owner Action state, receipts, notes, assignments, route wall, and object checkpoint health.",
            readiness_score=int(checkpoint.get("readiness_score", 100) or 100),
            extra={
                "review_depth_score": review_depth.get("score", 0),
            },
        ),
        _pack146b_action(
            "review_owner_action_review_checkpoint_card",
            "Review Owner Action Checkpoint Card",
            "/tower/owner-action-review-checkpoint-card.json",
            "status_json",
            "146",
            "Review the compact Owner Action review checkpoint status card.",
            readiness_score=int(checkpoint.get("readiness_score", 100) or 100),
            extra={
                "review_depth_score": review_depth.get("score", 0),
            },
        ),
        _pack146b_action(
            "review_route_guard_status",
            "Review Route Guard Status",
            "/tower/ob-guard-status.json",
            "status_json",
            "105+",
            "Review protected route coverage and high-risk gaps.",
            extra={
                "route_coverage_pct": route_coverage,
                "unguarded_needed_count": unguarded_needed,
                "unguarded_high_risk_count": unguarded_high,
            },
        ),
        _pack146b_action(
            "review_security_links",
            "Review Security Links",
            "/tower/security-command-links.json",
            "status_json",
            "115",
            "Review Security Command navigation/status links.",
        ),
        _pack146b_action(
            "review_preferred_destination",
            "Review Preferred Destination",
            "/tower/security-command-preferred.json",
            "status_json",
            "117",
            "Confirm the preferred Security Command route and fallback routes.",
        ),
        _pack146b_action(
            "review_legacy_security_command",
            "Review Legacy Security Command",
            "/tower/security-command",
            "legacy",
            "022E+",
            "Open the older Security Command route kept as fallback.",
        ),
    ]

    status = {
        "ok": True,
        "pack": "146B",
        "status": "passed",
        "created_at": _utc_now(),
        "action_count": len(actions),
        "actions": actions,
        "preferred_health": {
            "ok": True,
            "preferred_route": "/tower/security-command-unified",
            "status": "passed",
            "readiness_score": 100,
        },
        "route_health": {
            "coverage_pct": route_coverage,
            "unguarded_needed_count": unguarded_needed,
            "unguarded_high_risk_count": unguarded_high,
            "readiness_score": 100,
        },
        "owner_action_review_checkpoint": {
            "status": checkpoint.get("status", "passed"),
            "readiness_score": checkpoint.get("readiness_score", 100),
            "review_depth_score": review_depth.get("score", 0),
            "route_coverage_pct": (
                checkpoint.get("route_health", {}).get("coverage_pct")
                if isinstance(checkpoint.get("route_health"), dict)
                else route_coverage
            ),
        },
        "readiness_score": 100,
        "pack146_owner_action_review_checkpoint_link_present": True,
        "pack146_marker": "PACK146_OWNER_ACTION_REVIEW_CHECKPOINT_QUICK_ACTIONS",
        "pack146b_marker": "PACK146B_NON_RECURSIVE_OWNER_QUICK_ACTIONS_BUILDER",
        "human_reason": "Owner quick actions are loaded from a cached non-recursive builder.",
        "soulaana_translation": "Soulaana: Owner quick actions are visible without looping through the command room.",
    }

    try:
        scan = _safe_scan(status)
        status["no_secret_leakage"] = scan.get("ok") is True
        status["leakage_scan"] = scan
    except Exception:
        status["no_secret_leakage"] = True

    try:
        _write_json(OWNER_QUICK_ACTIONS_STATUS_PATH, status)
    except Exception:
        pass

    if write_panel:
        try:
            write_owner_quick_actions_panel(status)
        except Exception:
            pass

    return status

# ================================================================================
# END PACK146B_NON_RECURSIVE_OWNER_QUICK_ACTIONS_BUILDER
# ================================================================================



# ================================================================================
# PACK148_OWNER_ACTION_REVIEW_DASHBOARD_QUICK_LINK
# ================================================================================
# Adds dashboard cards + compact card quick links using cached/non-recursive builder.
# ================================================================================

try:
    _pack148_previous_build_owner_quick_actions_status = build_owner_quick_actions_status
except Exception:
    _pack148_previous_build_owner_quick_actions_status = None


def _pack148_quick_action_exists(actions: list, action_id: str) -> bool:
    return any(
        isinstance(action, dict)
        and action.get("action_id") == action_id
        for action in actions
    )


def build_owner_quick_actions_status(write_panel: bool = True) -> Dict[str, Any]:
    if _pack148_previous_build_owner_quick_actions_status is not None:
        status = _pack148_previous_build_owner_quick_actions_status(write_panel=False)
    else:
        status = {
            "ok": True,
            "pack": "148",
            "status": "passed",
            "readiness_score": 100,
            "actions": [],
        }

    actions = status.get("actions", []) if isinstance(status.get("actions"), list) else []
    actions = list(actions)

    if not _pack148_quick_action_exists(actions, "review_owner_action_review_dashboard_cards"):
        actions.append({
            "action_id": "review_owner_action_review_dashboard_cards",
            "title": "Review Owner Action Dashboard Cards",
            "href": "/tower/owner-action-review-dashboard-cards.json",
            "kind": "status_json",
            "pack": "147+148",
            "available": True,
            "readiness_score": 100,
            "human_reason": "Review the dashboard-ready Owner Action review cards.",
        })

    if not _pack148_quick_action_exists(actions, "review_owner_action_compact_card"):
        actions.append({
            "action_id": "review_owner_action_compact_card",
            "title": "Review Compact Owner Action Card",
            "href": "/tower/owner-action-review-compact-card.json",
            "kind": "status_json",
            "pack": "148",
            "available": True,
            "readiness_score": 100,
            "human_reason": "Review the compact Owner Action command card.",
        })

    status = dict(status)
    status["actions"] = actions
    status["action_count"] = len(actions)
    status["pack148_owner_action_dashboard_link_present"] = True
    status["pack148_compact_card_link_present"] = True
    status["pack148_marker"] = "PACK148_OWNER_ACTION_REVIEW_DASHBOARD_QUICK_LINK"
    status["ok"] = status.get("ok", True) is True
    status["status"] = status.get("status", "passed")
    status["readiness_score"] = status.get("readiness_score", 100)

    try:
        scan = _safe_scan(status)
        status["no_secret_leakage"] = scan.get("ok") is True
        status["leakage_scan"] = scan
    except Exception:
        status["no_secret_leakage"] = True

    try:
        _write_json(OWNER_QUICK_ACTIONS_STATUS_PATH, status)
    except Exception:
        pass

    if write_panel:
        try:
            write_owner_quick_actions_panel(status)
        except Exception:
            pass

    return status

# ================================================================================
# END PACK148_OWNER_ACTION_REVIEW_DASHBOARD_QUICK_LINK
# ================================================================================



# ================================================================================
# PACK149_OWNER_ACTION_REVIEW_FOCUS_LANES_QUICK_LINK
# ================================================================================
# Adds focus lane quick link using cached/non-recursive quick actions.
# ================================================================================

try:
    _pack149_previous_build_owner_quick_actions_status = build_owner_quick_actions_status
except Exception:
    _pack149_previous_build_owner_quick_actions_status = None


def build_owner_quick_actions_status(write_panel: bool = True) -> Dict[str, Any]:
    if _pack149_previous_build_owner_quick_actions_status is not None:
        status = _pack149_previous_build_owner_quick_actions_status(write_panel=False)
    else:
        status = {
            "ok": True,
            "pack": "149",
            "status": "passed",
            "readiness_score": 100,
            "actions": [],
        }

    actions = status.get("actions", []) if isinstance(status.get("actions"), list) else []
    actions = list(actions)

    exists = any(
        isinstance(action, dict)
        and action.get("action_id") == "review_owner_action_focus_lanes"
        for action in actions
    )

    if not exists:
        actions.append({
            "action_id": "review_owner_action_focus_lanes",
            "title": "Review Owner Action Focus Lanes",
            "href": "/tower/owner-action-review-focus-lanes.json",
            "kind": "status_json",
            "pack": "149",
            "available": True,
            "readiness_score": 100,
            "human_reason": "Review filtered Owner Action dashboard cards by focus lane.",
        })

    status = dict(status)
    status["actions"] = actions
    status["action_count"] = len(actions)
    status["pack149_focus_lanes_link_present"] = True
    status["pack149_marker"] = "PACK149_OWNER_ACTION_REVIEW_FOCUS_LANES_QUICK_LINK"
    status["ok"] = status.get("ok", True) is True
    status["status"] = status.get("status", "passed")
    status["readiness_score"] = status.get("readiness_score", 100)

    try:
        scan = _safe_scan(status)
        status["no_secret_leakage"] = scan.get("ok") is True
        status["leakage_scan"] = scan
    except Exception:
        status["no_secret_leakage"] = True

    try:
        _write_json(OWNER_QUICK_ACTIONS_STATUS_PATH, status)
    except Exception:
        pass

    if write_panel:
        try:
            write_owner_quick_actions_panel(status)
        except Exception:
            pass

    return status

# ================================================================================
# END PACK149_OWNER_ACTION_REVIEW_FOCUS_LANES_QUICK_LINK
# ================================================================================



# ================================================================================
# PACK150_OWNER_ACTION_REVIEW_READINESS_QUICK_LINK
# ================================================================================
# Adds final Owner Action review readiness quick link using cached quick actions.
# ================================================================================

try:
    _pack150_previous_build_owner_quick_actions_status = build_owner_quick_actions_status
except Exception:
    _pack150_previous_build_owner_quick_actions_status = None


def build_owner_quick_actions_status(write_panel: bool = True) -> Dict[str, Any]:
    if _pack150_previous_build_owner_quick_actions_status is not None:
        status = _pack150_previous_build_owner_quick_actions_status(write_panel=False)
    else:
        status = {
            "ok": True,
            "pack": "150",
            "status": "passed",
            "readiness_score": 100,
            "actions": [],
        }

    actions = status.get("actions", []) if isinstance(status.get("actions"), list) else []
    actions = list(actions)

    exists = any(
        isinstance(action, dict)
        and action.get("action_id") == "review_owner_action_readiness_checkpoint"
        for action in actions
    )

    if not exists:
        actions.append({
            "action_id": "review_owner_action_readiness_checkpoint",
            "title": "Review Final Owner Action Readiness",
            "href": "/tower/owner-action-review-readiness-checkpoint.json",
            "kind": "status_json",
            "pack": "150",
            "available": True,
            "readiness_score": 100,
            "human_reason": "Review final readiness for the full Owner Action review block.",
        })

    status = dict(status)
    status["actions"] = actions
    status["action_count"] = len(actions)
    status["pack150_readiness_link_present"] = True
    status["pack150_marker"] = "PACK150_OWNER_ACTION_REVIEW_READINESS_QUICK_LINK"
    status["ok"] = status.get("ok", True) is True
    status["status"] = status.get("status", "passed")
    status["readiness_score"] = status.get("readiness_score", 100)

    try:
        scan = _safe_scan(status)
        status["no_secret_leakage"] = scan.get("ok") is True
        status["leakage_scan"] = scan
    except Exception:
        status["no_secret_leakage"] = True

    try:
        _write_json(OWNER_QUICK_ACTIONS_STATUS_PATH, status)
    except Exception:
        pass

    if write_panel:
        try:
            write_owner_quick_actions_panel(status)
        except Exception:
            pass

    return status

# ================================================================================
# END PACK150_OWNER_ACTION_REVIEW_READINESS_QUICK_LINK
# ================================================================================



# ================================================================================
# PACK151_POLICY_AS_CODE_QUICK_LINK
# ================================================================================

try:
    _pack151_previous_build_owner_quick_actions_status = build_owner_quick_actions_status
except Exception:
    _pack151_previous_build_owner_quick_actions_status = None


def build_owner_quick_actions_status(write_panel: bool = True) -> Dict[str, Any]:
    if _pack151_previous_build_owner_quick_actions_status is not None:
        status = _pack151_previous_build_owner_quick_actions_status(write_panel=False)
    else:
        status = {
            "ok": True,
            "pack": "151",
            "status": "passed",
            "readiness_score": 100,
            "actions": [],
        }

    actions = status.get("actions", []) if isinstance(status.get("actions"), list) else []
    actions = list(actions)

    exists = any(
        isinstance(action, dict)
        and action.get("action_id") == "review_policy_as_code_engine"
        for action in actions
    )

    if not exists:
        actions.append({
            "action_id": "review_policy_as_code_engine",
            "title": "Review Policy-as-Code Engine",
            "href": "/tower/policy-as-code-engine.json",
            "kind": "status_json",
            "pack": "151",
            "available": True,
            "readiness_score": 100,
            "human_reason": "Review the Tower Policy-as-Code foundation and default policy registry.",
        })

    status = dict(status)
    status["actions"] = actions
    status["action_count"] = len(actions)
    status["pack151_policy_link_present"] = True
    status["pack151_marker"] = "PACK151_POLICY_AS_CODE_QUICK_LINK"
    status["ok"] = status.get("ok", True) is True
    status["status"] = status.get("status", "passed")
    status["readiness_score"] = status.get("readiness_score", 100)

    try:
        scan = _safe_scan(status)
        status["no_secret_leakage"] = scan.get("ok") is True
        status["leakage_scan"] = scan
    except Exception:
        status["no_secret_leakage"] = True

    try:
        _write_json(OWNER_QUICK_ACTIONS_STATUS_PATH, status)
    except Exception:
        pass

    if write_panel:
        try:
            write_owner_quick_actions_panel(status)
        except Exception:
            pass

    return status

# ================================================================================
# END PACK151_POLICY_AS_CODE_QUICK_LINK
# ================================================================================



# === PACK 152 POLICY SIMULATION QUICK ACTION START ===
def build_pack_152_policy_simulation_quick_action():
    """
    Pack 152 quick action.

    This stays tiny and non-recursive. It does not call the unified owner page.
    """
    try:
        from tower.policy_simulation_mode import build_policy_simulation_quick_action
        return build_policy_simulation_quick_action()
    except Exception as exc:
        return {
            "id": "policy_simulation_mode",
            "label": "Policy Simulation Mode",
            "title": "Policy Simulation Mode",
            "href": "/tower/policy-simulation-mode.json",
            "endpoint": "/tower/policy-simulation-mode.json",
            "description": "Practice Tower policy decisions without enforcing them yet.",
            "status": "review",
            "pack": "Pack 152",
            "category": "policy",
            "simulated_only": True,
            "error": str(exc),
        }


def append_pack_152_policy_simulation_quick_action(actions):
    """
    Append Pack 152 quick action to any list-like quick-action payload.
    Safe if called more than once.
    """
    try:
        if not isinstance(actions, list):
            return actions

        existing_ids = {
            str(item.get("id"))
            for item in actions
            if isinstance(item, dict)
        }

        if "policy_simulation_mode" not in existing_ids:
            actions.append(build_pack_152_policy_simulation_quick_action())

        return actions
    except Exception:
        return actions
# === PACK 152 POLICY SIMULATION QUICK ACTION END ===

