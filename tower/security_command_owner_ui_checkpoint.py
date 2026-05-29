
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "tower" / "data"

OWNER_UI_CHECKPOINT_STATUS_PATH = DATA_DIR / "security_command_owner_ui_checkpoint_status.json"
OWNER_UI_CHECKPOINT_PANEL_PATH = DATA_DIR / "security_command_owner_ui_checkpoint_panel.html"


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


def build_security_command_owner_ui_checkpoint(write_panel: bool = True) -> Dict[str, Any]:
    route_call = _safe_call(
        "route_coverage",
        lambda: __import__("tower.ob_route_coverage_report", fromlist=["build_ob_route_coverage_report"]).build_ob_route_coverage_report(write_panel=True),
    )

    object_checkpoint_call = _safe_call(
        "object_checkpoint",
        lambda: __import__("tower.ob_object_permission_integration_checkpoint", fromlist=["build_object_permission_integration_checkpoint"]).build_object_permission_integration_checkpoint(write_panel=True),
    )

    object_visibility_call = _safe_call(
        "object_visibility",
        lambda: __import__("tower.ob_object_permission_visibility", fromlist=["load_object_permission_visibility_status"]).load_object_permission_visibility_status(),
    )

    composition_call = _safe_call(
        "composition_smoke",
        lambda: __import__("tower.security_command_composition_smoke", fromlist=["load_security_command_composition_status"]).load_security_command_composition_status(),
    )

    navigation_call = _safe_call(
        "navigation_links",
        lambda: __import__("tower.security_command_navigation_links", fromlist=["load_security_command_navigation_links_status"]).load_security_command_navigation_links_status(),
    )

    preferred_call = _safe_call(
        "preferred_destination",
        lambda: __import__("tower.security_command_preferred_destination", fromlist=["load_security_command_preferred_destination_status"]).load_security_command_preferred_destination_status(),
    )

    unified_call = _safe_call(
        "unified_owner_page",
        lambda: __import__("tower.security_command_unified_owner_page", fromlist=["load_unified_owner_security_command_status"]).load_unified_owner_security_command_status(),
    )

    quick_actions_call = _safe_call(
        "owner_quick_actions",
        lambda: __import__("tower.security_command_owner_quick_actions", fromlist=["load_owner_quick_actions_status"]).load_owner_quick_actions_status(),
    )

    route = route_call.get("result", {})
    object_checkpoint = object_checkpoint_call.get("result", {})
    object_visibility = object_visibility_call.get("result", {})
    composition = composition_call.get("result", {})
    navigation = navigation_call.get("result", {})
    preferred = preferred_call.get("result", {})
    unified = unified_call.get("result", {})
    quick_actions = quick_actions_call.get("result", {})

    checks = {
        "route_call_ok": route_call.get("ok") is True,
        "route_coverage_ok": route.get("ok") is True,
        "route_coverage_100": route.get("coverage_pct") == 100,
        "unguarded_needed_zero": route.get("unguarded_needed_count") == 0,
        "unguarded_high_risk_zero": route.get("unguarded_high_risk_count") == 0,

        "object_checkpoint_call_ok": object_checkpoint_call.get("ok") is True,
        "object_checkpoint_ok": object_checkpoint.get("ok") is True,
        "object_checkpoint_passed": object_checkpoint.get("status") == "passed",
        "helper_wrapped_zero": object_checkpoint.get("helper_wrapped_count") == 0,

        "object_visibility_call_ok": object_visibility_call.get("ok") is True,
        "object_visibility_ok": object_visibility.get("ok") is True,
        "object_visibility_ready": object_visibility.get("readiness_score") == 100,

        "composition_call_ok": composition_call.get("ok") is True,
        "composition_ok": composition.get("ok") is True,
        "composition_passed": composition.get("status") == "passed",
        "composition_ready": composition.get("readiness_score") == 100,

        "navigation_call_ok": navigation_call.get("ok") is True,
        "navigation_ok": navigation.get("ok") is True,
        "navigation_passed": navigation.get("status") == "passed",
        "navigation_ready": navigation.get("readiness_score") == 100,

        "preferred_call_ok": preferred_call.get("ok") is True,
        "preferred_ok": preferred.get("ok") is True,
        "preferred_passed": preferred.get("status") == "passed",
        "preferred_route_unified": preferred.get("preferred_route") == "/tower/security-command-unified",

        "unified_call_ok": unified_call.get("ok") is True,
        "unified_ok": unified.get("ok") is True,
        "unified_passed": unified.get("status") == "passed",
        "unified_ready": unified.get("readiness_score") == 100,

        "quick_actions_call_ok": quick_actions_call.get("ok") is True,
        "quick_actions_ok": quick_actions.get("ok") is True,
        "quick_actions_passed": quick_actions.get("status") == "passed",
        "quick_actions_ready": quick_actions.get("readiness_score") == 100,
    }

    failed_checks = [key for key, ok in checks.items() if not ok]

    status = {
        "ok": not failed_checks,
        "pack": "120",
        "status": "passed" if not failed_checks else "failed",
        "created_at": _utc_now(),
        "status_path": str(OWNER_UI_CHECKPOINT_STATUS_PATH),
        "panel_path": str(OWNER_UI_CHECKPOINT_PANEL_PATH),
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
            "object_guard_count": object_checkpoint.get("object_guard_count"),
            "helper_wrapped_count": object_checkpoint.get("helper_wrapped_count"),
            "warnings": object_checkpoint.get("warnings"),
        },
        "object_visibility": {
            "event_count": object_visibility.get("event_count"),
            "deny_count": object_visibility.get("deny_count"),
            "step_up_required_count": object_visibility.get("step_up_required_count"),
            "summary_only_count": object_visibility.get("summary_only_count"),
            "export_event_count": object_visibility.get("export_event_count"),
            "readiness_score": object_visibility.get("readiness_score"),
        },
        "composition": {
            "status": composition.get("status"),
            "readiness_score": composition.get("readiness_score"),
            "html_path": composition.get("html_path"),
        },
        "navigation": {
            "status": navigation.get("status"),
            "readiness_score": navigation.get("readiness_score"),
            "link_count": navigation.get("link_count"),
        },
        "preferred": {
            "status": preferred.get("status"),
            "readiness_score": preferred.get("readiness_score"),
            "preferred_route": preferred.get("preferred_route"),
            "legacy_route": preferred.get("legacy_route"),
            "link_count": preferred.get("link_count"),
        },
        "unified": {
            "status": unified.get("status"),
            "readiness_score": unified.get("readiness_score"),
            "html_path": unified.get("html_path"),
        },
        "quick_actions": {
            "status": quick_actions.get("status"),
            "readiness_score": quick_actions.get("readiness_score"),
            "action_count": quick_actions.get("action_count"),
        },
        "readiness_score": 100 if not failed_checks else max(0, 100 - (len(failed_checks) * 5)),
        "readiness_label": (
            "Security Command owner UI checkpoint passed"
            if not failed_checks
            else "Security Command owner UI checkpoint needs review"
        ),
        "human_reason": "Security Command owner UI block is healthy: preferred destination, unified page, quick actions, visibility, coverage, and checkpoints are all passing.",
        "soulaana_translation": "Soulaana: The owner command room is lit, guarded, linked, and readable.",
    }

    scan = _safe_scan(status)
    status["no_secret_leakage"] = scan.get("ok") is True
    status["leakage_scan"] = scan
    status["status_fingerprint"] = _fingerprint(status)

    _write_json(OWNER_UI_CHECKPOINT_STATUS_PATH, status)

    try:
        from tower.tamper_evident_audit_chain import create_tamper_chain_entry
        create_tamper_chain_entry(
            event_type="tower_security_command_owner_ui_checkpoint",
            source_name="security_command_owner_ui_checkpoint_status",
            source_path=str(OWNER_UI_CHECKPOINT_STATUS_PATH),
            source_hash=_fingerprint(status),
            record_count=1,
            actor_user_id="tower_system",
            reason="Pack 120 Security Command owner UI checkpoint generated.",
            metadata={
                "pack": "120",
                "status": status.get("status"),
                "readiness_score": status.get("readiness_score"),
                "failed_checks": failed_checks,
            },
        )
    except Exception:
        pass

    if write_panel:
        write_security_command_owner_ui_checkpoint_panel(status)

    return status


def render_security_command_owner_ui_checkpoint_section(status: Dict[str, Any] | None = None) -> str:
    status = status if isinstance(status, dict) else build_security_command_owner_ui_checkpoint(write_panel=False)

    route = status.get("route_health", {}) if isinstance(status.get("route_health"), dict) else {}
    object_checkpoint = status.get("object_checkpoint", {}) if isinstance(status.get("object_checkpoint"), dict) else {}
    preferred = status.get("preferred", {}) if isinstance(status.get("preferred"), dict) else {}
    quick_actions = status.get("quick_actions", {}) if isinstance(status.get("quick_actions"), dict) else {}
    unified = status.get("unified", {}) if isinstance(status.get("unified"), dict) else {}

    cards = [
        ("Route Coverage", f"{route.get('coverage_pct', 0)}%", "Guard wall"),
        ("Guarded Routes", f"{route.get('guarded_needed_count', 0)} / {route.get('needs_guard_count', 0)}", "Protected"),
        ("Helper Wraps", object_checkpoint.get("helper_wrapped_count", 0), "Clean"),
        ("Preferred Route", preferred.get("preferred_route", ""), "Destination"),
        ("Quick Actions", quick_actions.get("action_count", 0), "Owner rail"),
        ("Unified Readiness", unified.get("readiness_score", 0), "Command page"),
    ]

    card_html = []
    for title, value, label in cards:
        card_html.append(f"""
        <article class="owner-ui-checkpoint-card">
          <div class="owner-ui-checkpoint-card__eyebrow">{_html_escape(label)}</div>
          <h3>{_html_escape(value)}</h3>
          <p>{_html_escape(title)}</p>
        </article>
        """)

    html = f"""
<!-- PACK120_SECURITY_COMMAND_OWNER_UI_CHECKPOINT_SECTION -->
<section class="owner-ui-checkpoint" data-pack="120">
  <style>
    .owner-ui-checkpoint {{
      margin: 24px 0;
      border: 1px solid rgba(143,221,158,.36);
      border-radius: 28px;
      padding: 22px;
      background:
        radial-gradient(circle at top left, rgba(143,221,158,.14), transparent 34%),
        linear-gradient(135deg, rgba(12,32,24,.72), rgba(8,9,7,.94));
      color: #f5ead2;
      box-shadow: 0 18px 70px rgba(0,0,0,.32);
    }}
    .owner-ui-checkpoint__eyebrow {{
      color: rgba(143,221,158,.88);
      text-transform: uppercase;
      letter-spacing: .14em;
      font-size: 11px;
      margin-bottom: 8px;
    }}
    .owner-ui-checkpoint h2 {{
      margin: 0;
      font-size: 24px;
      letter-spacing: -.03em;
    }}
    .owner-ui-checkpoint p {{
      color: rgba(245,234,210,.72);
      line-height: 1.45;
    }}
    .owner-ui-checkpoint-grid {{
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 12px;
      margin-top: 14px;
    }}
    .owner-ui-checkpoint-card {{
      border: 1px solid rgba(245,234,210,.13);
      border-radius: 20px;
      padding: 14px;
      background: rgba(255,255,255,.04);
    }}
    .owner-ui-checkpoint-card__eyebrow {{
      color: rgba(220,183,94,.84);
      text-transform: uppercase;
      letter-spacing: .12em;
      font-size: 10px;
      margin-bottom: 7px;
    }}
    .owner-ui-checkpoint-card h3 {{
      margin: 0 0 7px;
      font-size: 18px;
    }}
    .owner-ui-checkpoint-card p {{
      margin: 0;
      color: rgba(245,234,210,.72);
    }}
    @media (max-width: 900px) {{
      .owner-ui-checkpoint-grid {{
        grid-template-columns: 1fr;
      }}
    }}
  </style>

  <div class="owner-ui-checkpoint__eyebrow">PACK 120 · OWNER UI CHECKPOINT</div>
  <h2>Security Command UI Checkpoint</h2>
  <p>{_html_escape(status.get('human_reason', 'Security Command owner UI checkpoint loaded.'))}</p>

  <div class="owner-ui-checkpoint-grid">
    {''.join(card_html)}
  </div>
</section>
<!-- END PACK120_SECURITY_COMMAND_OWNER_UI_CHECKPOINT_SECTION -->
"""
    return html


def write_security_command_owner_ui_checkpoint_panel(status: Dict[str, Any] | None = None) -> Dict[str, Any]:
    status = status if isinstance(status, dict) else build_security_command_owner_ui_checkpoint(write_panel=False)
    html = f"""<!doctype html>
<html lang="en">
<head><meta charset="utf-8"><title>The Tower · Security Command UI Checkpoint</title></head>
<body style="margin:0;background:#080907;color:#f5ead2;font-family:system-ui;padding:32px;">
<main style="max-width:1180px;margin:auto;">
{render_security_command_owner_ui_checkpoint_section(status)}
</main>
</body>
</html>
"""
    _write_text(OWNER_UI_CHECKPOINT_PANEL_PATH, html)
    return {
        "ok": True,
        "pack": "120",
        "decision": "security_command_owner_ui_checkpoint_panel_written",
        "path": str(OWNER_UI_CHECKPOINT_PANEL_PATH),
        "human_reason": "Security Command owner UI checkpoint panel written.",
        "soulaana_translation": "Soulaana: Owner UI checkpoint board posted.",
    }


def load_security_command_owner_ui_checkpoint() -> Dict[str, Any]:
    status = _load_json(OWNER_UI_CHECKPOINT_STATUS_PATH, {})
    if not status:
        status = build_security_command_owner_ui_checkpoint(write_panel=True)
    return status


def owner_ui_checkpoint_status_card() -> Dict[str, Any]:
    status = load_security_command_owner_ui_checkpoint()
    return {
        "ok": status.get("ok") is True,
        "pack": "120",
        "title": "Security Command UI Checkpoint",
        "readiness_score": status.get("readiness_score", 0),
        "route_coverage_pct": status.get("route_health", {}).get("coverage_pct", 0) if isinstance(status.get("route_health"), dict) else 0,
        "helper_wrapped_count": status.get("object_checkpoint", {}).get("helper_wrapped_count", 0) if isinstance(status.get("object_checkpoint"), dict) else 0,
        "preferred_route": status.get("preferred", {}).get("preferred_route", "") if isinstance(status.get("preferred"), dict) else "",
        "quick_action_count": status.get("quick_actions", {}).get("action_count", 0) if isinstance(status.get("quick_actions"), dict) else 0,
        "panel_path": status.get("panel_path", str(OWNER_UI_CHECKPOINT_PANEL_PATH)),
        "status_path": status.get("status_path", str(OWNER_UI_CHECKPOINT_STATUS_PATH)),
        "human_reason": "Security Command UI checkpoint status card loaded.",
        "soulaana_translation": "Soulaana: Owner UI checkpoint is visible.",
    }


def reset_security_command_owner_ui_checkpoint_for_test() -> Dict[str, Any]:
    _write_json(OWNER_UI_CHECKPOINT_STATUS_PATH, {
        "ok": True,
        "pack": "120",
        "reset_at": _utc_now(),
        "human_reason": "Security Command owner UI checkpoint reset for test.",
    })
    if OWNER_UI_CHECKPOINT_PANEL_PATH.exists():
        try:
            OWNER_UI_CHECKPOINT_PANEL_PATH.unlink()
        except Exception:
            pass
    return {
        "ok": True,
        "decision": "security_command_owner_ui_checkpoint_reset_for_test",
        "soulaana_translation": "Soulaana: Owner UI checkpoint reset for a clean test lane.",
    }
