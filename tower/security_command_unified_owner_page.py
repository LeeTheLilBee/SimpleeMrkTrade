
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "tower" / "data"

UNIFIED_STATUS_PATH = DATA_DIR / "security_command_unified_owner_page_status.json"
UNIFIED_HTML_PATH = DATA_DIR / "security_command_unified_owner_page.html"


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


def _html_escape(value: Any) -> str:
    text = str(value if value is not None else "")
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#x27;")
    )


def _safe_call(label: str, fn):
    try:
        return {
            "ok": True,
            "label": label,
            "result": fn(),
            "error_type": "",
        }
    except Exception as exc:
        return {
            "ok": False,
            "label": label,
            "result": {},
            "error_type": type(exc).__name__,
        }


def build_unified_owner_security_command_status(write_html: bool = True) -> Dict[str, Any]:
    route_health_call = _safe_call(
        "route_coverage",
        lambda: __import__("tower.ob_route_coverage_report", fromlist=["build_ob_route_coverage_report"]).build_ob_route_coverage_report(write_panel=True),
    )

    object_checkpoint_call = _safe_call(
        "object_checkpoint",
        lambda: __import__("tower.ob_object_permission_integration_checkpoint", fromlist=["build_object_permission_integration_checkpoint"]).build_object_permission_integration_checkpoint(write_panel=True),
    )

    object_visibility_call = _safe_call(
        "object_visibility",
        lambda: __import__("tower.ob_object_permission_visibility", fromlist=["build_object_permission_visibility_status"]).build_object_permission_visibility_status(limit=120, write_panel=True),
    )

    composition_call = _safe_call(
        "composition_smoke",
        lambda: __import__("tower.security_command_composition_smoke", fromlist=["build_security_command_composition_status"]).build_security_command_composition_status(write_html=True),
    )

    navigation_call = _safe_call(
        "navigation_links",
        lambda: __import__("tower.security_command_navigation_links", fromlist=["build_security_command_navigation_links_status"]).build_security_command_navigation_links_status(write_panel=True),
    )

    route_health = route_health_call.get("result", {}) if isinstance(route_health_call.get("result"), dict) else {}
    object_checkpoint = object_checkpoint_call.get("result", {}) if isinstance(object_checkpoint_call.get("result"), dict) else {}
    object_visibility = object_visibility_call.get("result", {}) if isinstance(object_visibility_call.get("result"), dict) else {}
    composition = composition_call.get("result", {}) if isinstance(composition_call.get("result"), dict) else {}
    navigation = navigation_call.get("result", {}) if isinstance(navigation_call.get("result"), dict) else {}

    checks = {
        "route_health_call_ok": route_health_call.get("ok") is True,
        "route_coverage_ok": route_health.get("ok") is True,
        "route_coverage_100": route_health.get("coverage_pct") == 100,
        "unguarded_needed_zero": route_health.get("unguarded_needed_count") == 0,
        "unguarded_high_risk_zero": route_health.get("unguarded_high_risk_count") == 0,

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
    }

    failed_checks = [key for key, ok in checks.items() if not ok]

    status = {
        "ok": not failed_checks,
        "pack": "116",
        "status": "passed" if not failed_checks else "failed",
        "created_at": _utc_now(),
        "status_path": str(UNIFIED_STATUS_PATH),
        "html_path": str(UNIFIED_HTML_PATH),
        "checks": checks,
        "failed_checks": failed_checks,
        "route_health": {
            "coverage_pct": route_health.get("coverage_pct"),
            "needs_guard_count": route_health.get("needs_guard_count"),
            "guarded_needed_count": route_health.get("guarded_needed_count"),
            "unguarded_needed_count": route_health.get("unguarded_needed_count"),
            "unguarded_high_risk_count": route_health.get("unguarded_high_risk_count"),
            "readiness_score": route_health.get("readiness_score"),
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
            "admin_event_count": object_visibility.get("admin_event_count"),
            "live_mode_event_count": object_visibility.get("live_mode_event_count"),
            "readiness_score": object_visibility.get("readiness_score"),
            "no_secret_leakage": object_visibility.get("no_secret_leakage"),
        },
        "composition": {
            "status": composition.get("status"),
            "readiness_score": composition.get("readiness_score"),
            "html_path": composition.get("html_path"),
            "bridge_status": composition.get("bridge_status"),
        },
        "navigation": {
            "status": navigation.get("status"),
            "readiness_score": navigation.get("readiness_score"),
            "link_count": navigation.get("link_count"),
            "links": navigation.get("links"),
        },
        "readiness_score": 100 if not failed_checks else max(0, 100 - (len(failed_checks) * 8)),
        "readiness_label": (
            "Unified owner Security Command page ready"
            if not failed_checks
            else "Unified owner Security Command page needs review"
        ),
        "human_reason": "Unified owner Security Command page composes navigation, object visibility, route coverage, object checkpoint, and composition smoke into one control-room page.",
        "soulaana_translation": "Soulaana: The Tower room is becoming one command center instead of scattered panels.",
    }

    scan = _safe_scan(status)
    status["no_secret_leakage"] = scan.get("ok") is True
    status["leakage_scan"] = scan
    status["status_fingerprint"] = _fingerprint(status)

    _write_json(UNIFIED_STATUS_PATH, status)

    try:
        from tower.tamper_evident_audit_chain import create_tamper_chain_entry
        create_tamper_chain_entry(
            event_type="tower_unified_owner_security_command_status",
            source_name="security_command_unified_owner_page_status",
            source_path=str(UNIFIED_STATUS_PATH),
            source_hash=_fingerprint(status),
            record_count=1,
            actor_user_id="tower_system",
            reason="Pack 116 unified owner Security Command status generated.",
            metadata={
                "pack": "116",
                "status": status.get("status"),
                "readiness_score": status.get("readiness_score"),
                "failed_checks": failed_checks,
            },
        )
    except Exception:
        pass

    if write_html:
        write_unified_owner_security_command_html(status)

    return status


def _build_health_card(title: str, value: Any, label: str, tone: str = "ready") -> str:
    return f"""
    <article class="tower-owner-health-card tower-owner-health-card--{_html_escape(tone)}">
      <div class="tower-owner-health-card__eyebrow">{_html_escape(label)}</div>
      <h3>{_html_escape(value)}</h3>
      <p>{_html_escape(title)}</p>
    </article>
    """


def render_unified_owner_security_command_html(status: Dict[str, Any] | None = None) -> str:
    status = status if isinstance(status, dict) else build_unified_owner_security_command_status(write_html=False)

    nav_section = ""
    object_section = ""

    try:
        from tower.security_command_page import pack115_security_command_navigation_links_html_section
        nav_section = pack115_security_command_navigation_links_html_section()
    except Exception as exc:
        nav_section = f"""
        <section class="tower-security-command-links" data-pack="116-nav-error">
          <h2>Security Command Links Unavailable</h2>
          <p>{_html_escape(type(exc).__name__)}</p>
        </section>
        """

    try:
        from tower.security_command_page import pack113_security_command_object_visibility_html_section
        object_section = pack113_security_command_object_visibility_html_section()
    except Exception as exc:
        object_section = f"""
        <section class="tower-object-visibility-panel" data-pack="116-object-error">
          <h2>Object Visibility Unavailable</h2>
          <p>{_html_escape(type(exc).__name__)}</p>
        </section>
        """

    route_health = status.get("route_health", {}) if isinstance(status.get("route_health"), dict) else {}
    object_checkpoint = status.get("object_checkpoint", {}) if isinstance(status.get("object_checkpoint"), dict) else {}
    object_visibility = status.get("object_visibility", {}) if isinstance(status.get("object_visibility"), dict) else {}
    navigation = status.get("navigation", {}) if isinstance(status.get("navigation"), dict) else {}

    health_cards = "".join([
        _build_health_card("Route Coverage", f"{route_health.get('coverage_pct', 0)}%", "ROUTE WALL"),
        _build_health_card("Guarded Protected Routes", f"{route_health.get('guarded_needed_count', 0)} / {route_health.get('needs_guard_count', 0)}", "GUARDS"),
        _build_health_card("Helper Wraps", object_checkpoint.get("helper_wrapped_count", 0), "OBJECT CLEANUP"),
        _build_health_card("Object Events", object_visibility.get("event_count", 0), "OBJECT VISIBILITY"),
        _build_health_card("Security Links", navigation.get("link_count", 0), "NAVIGATION"),
        _build_health_card("Readiness", status.get("readiness_score", 0), "OWNER COMMAND"),
    ])

    html = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>The Tower · Unified Owner Security Command</title>
  <style>
    body {{
      margin: 0;
      min-height: 100vh;
      background:
        radial-gradient(circle at top left, rgba(220,183,94,.13), transparent 32%),
        radial-gradient(circle at bottom right, rgba(168,175,255,.10), transparent 35%),
        #080907;
      color: #f5ead2;
      font-family: Inter, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }}
    main {{
      max-width: 1220px;
      margin: 0 auto;
      padding: 42px 22px 70px;
    }}
    .tower-owner-hero {{
      border: 1px solid rgba(220,183,94,.38);
      border-radius: 34px;
      padding: 32px;
      background:
        linear-gradient(135deg, rgba(75,48,18,.76), rgba(8,9,7,.94)),
        radial-gradient(circle at top right, rgba(220,183,94,.14), transparent 38%);
      box-shadow: 0 24px 90px rgba(0,0,0,.44);
      margin-bottom: 22px;
    }}
    .tower-owner-hero__eyebrow {{
      color: rgba(220,183,94,.88);
      text-transform: uppercase;
      letter-spacing: .16em;
      font-size: 11px;
      margin-bottom: 10px;
    }}
    .tower-owner-hero h1 {{
      margin: 0 0 10px;
      font-size: 38px;
      letter-spacing: -.045em;
    }}
    .tower-owner-hero p {{
      margin: 0;
      color: rgba(245,234,210,.76);
      line-height: 1.55;
      max-width: 880px;
    }}
    .tower-owner-health-grid {{
      display: grid;
      grid-template-columns: repeat(6, minmax(0, 1fr));
      gap: 12px;
      margin: 18px 0 0;
    }}
    .tower-owner-health-card {{
      border: 1px solid rgba(143,221,158,.26);
      border-radius: 20px;
      padding: 14px;
      background: rgba(255,255,255,.045);
    }}
    .tower-owner-health-card__eyebrow {{
      color: rgba(220,183,94,.8);
      text-transform: uppercase;
      letter-spacing: .12em;
      font-size: 10px;
      margin-bottom: 7px;
    }}
    .tower-owner-health-card h3 {{
      margin: 0 0 6px;
      font-size: 22px;
    }}
    .tower-owner-health-card p {{
      margin: 0;
      color: rgba(245,234,210,.63);
      font-size: 12px;
    }}
    .tower-owner-section {{
      margin-top: 22px;
    }}
    @media (max-width: 1050px) {{
      .tower-owner-health-grid {{
        grid-template-columns: repeat(2, minmax(0, 1fr));
      }}
    }}
    @media (max-width: 720px) {{
      .tower-owner-health-grid {{
        grid-template-columns: 1fr;
      }}
      .tower-owner-hero h1 {{
        font-size: 30px;
      }}
    }}
  </style>
</head>
<body>
<main>
  <!-- PACK116_UNIFIED_OWNER_SECURITY_COMMAND_PAGE -->
  <section class="tower-owner-hero" data-pack="116">
    <div class="tower-owner-hero__eyebrow">PACK 116 · UNIFIED OWNER COMMAND</div>
    <h1>The Tower Security Command</h1>
    <p>{_html_escape(status.get('human_reason', 'Unified Security Command loaded.'))}</p>
    <div class="tower-owner-health-grid">
      {health_cards}
    </div>
  </section>

  <section class="tower-owner-section">
    {nav_section}
  </section>

  <section class="tower-owner-section">
    {object_section}
  </section>
  <!-- END PACK116_UNIFIED_OWNER_SECURITY_COMMAND_PAGE -->
</main>
</body>
</html>
"""
    return html


def write_unified_owner_security_command_html(status: Dict[str, Any] | None = None) -> Dict[str, Any]:
    status = status if isinstance(status, dict) else build_unified_owner_security_command_status(write_html=False)
    html = render_unified_owner_security_command_html(status)
    _write_text(UNIFIED_HTML_PATH, html)

    return {
        "ok": True,
        "pack": "116",
        "decision": "unified_owner_security_command_html_written",
        "path": str(UNIFIED_HTML_PATH),
        "html_length": len(html),
        "human_reason": "Unified owner Security Command HTML written.",
        "soulaana_translation": "Soulaana: Unified owner command page written.",
    }


def load_unified_owner_security_command_status() -> Dict[str, Any]:
    status = _load_json(UNIFIED_STATUS_PATH, {})
    if not status:
        status = build_unified_owner_security_command_status(write_html=True)
    return status


def reset_unified_owner_security_command_for_test() -> Dict[str, Any]:
    _write_json(UNIFIED_STATUS_PATH, {
        "ok": True,
        "pack": "116",
        "reset_at": _utc_now(),
        "human_reason": "Unified owner Security Command reset for test.",
    })
    if UNIFIED_HTML_PATH.exists():
        try:
            UNIFIED_HTML_PATH.unlink()
        except Exception:
            pass
    return {
        "ok": True,
        "decision": "unified_owner_security_command_reset_for_test",
        "soulaana_translation": "Soulaana: Unified owner command reset for a clean test lane.",
    }



# ================================================================================
# PACK118_UNIFIED_OWNER_PAGE_WITH_PREFERRED_DESTINATION
# ================================================================================
# Override renderer so the unified owner page includes the Pack 117 preferred
# destination section directly inside the page.
# ================================================================================

def render_unified_owner_security_command_html(status: Dict[str, Any] | None = None) -> str:
    status = status if isinstance(status, dict) else build_unified_owner_security_command_status(write_html=False)

    preferred_section = ""
    nav_section = ""
    object_section = ""

    try:
        from tower.security_command_page import pack117_security_command_preferred_destination_html_section
        preferred_section = pack117_security_command_preferred_destination_html_section()
    except Exception as exc:
        preferred_section = f"""
        <section class="preferred-command-destination" data-pack="118-preferred-error">
          <h2>Preferred Security Command Destination Unavailable</h2>
          <p>{_html_escape(type(exc).__name__)}</p>
        </section>
        """

    try:
        from tower.security_command_page import pack115_security_command_navigation_links_html_section
        nav_section = pack115_security_command_navigation_links_html_section()
    except Exception as exc:
        nav_section = f"""
        <section class="tower-security-command-links" data-pack="118-nav-error">
          <h2>Security Command Links Unavailable</h2>
          <p>{_html_escape(type(exc).__name__)}</p>
        </section>
        """

    try:
        from tower.security_command_page import pack113_security_command_object_visibility_html_section
        object_section = pack113_security_command_object_visibility_html_section()
    except Exception as exc:
        object_section = f"""
        <section class="tower-object-visibility-panel" data-pack="118-object-error">
          <h2>Object Visibility Unavailable</h2>
          <p>{_html_escape(type(exc).__name__)}</p>
        </section>
        """

    route_health = status.get("route_health", {}) if isinstance(status.get("route_health"), dict) else {}
    object_checkpoint = status.get("object_checkpoint", {}) if isinstance(status.get("object_checkpoint"), dict) else {}
    object_visibility = status.get("object_visibility", {}) if isinstance(status.get("object_visibility"), dict) else {}
    navigation = status.get("navigation", {}) if isinstance(status.get("navigation"), dict) else {}

    health_cards = "".join([
        _build_health_card("Route Coverage", f"{route_health.get('coverage_pct', 0)}%", "ROUTE WALL"),
        _build_health_card("Guarded Protected Routes", f"{route_health.get('guarded_needed_count', 0)} / {route_health.get('needs_guard_count', 0)}", "GUARDS"),
        _build_health_card("Helper Wraps", object_checkpoint.get("helper_wrapped_count", 0), "OBJECT CLEANUP"),
        _build_health_card("Object Events", object_visibility.get("event_count", 0), "OBJECT VISIBILITY"),
        _build_health_card("Security Links", navigation.get("link_count", 0), "NAVIGATION"),
        _build_health_card("Readiness", status.get("readiness_score", 0), "OWNER COMMAND"),
    ])

    html = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>The Tower · Unified Owner Security Command</title>
  <style>
    body {{
      margin: 0;
      min-height: 100vh;
      background:
        radial-gradient(circle at top left, rgba(220,183,94,.13), transparent 32%),
        radial-gradient(circle at bottom right, rgba(168,175,255,.10), transparent 35%),
        #080907;
      color: #f5ead2;
      font-family: Inter, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }}
    main {{
      max-width: 1220px;
      margin: 0 auto;
      padding: 42px 22px 70px;
    }}
    .tower-owner-hero {{
      border: 1px solid rgba(220,183,94,.38);
      border-radius: 34px;
      padding: 32px;
      background:
        linear-gradient(135deg, rgba(75,48,18,.76), rgba(8,9,7,.94)),
        radial-gradient(circle at top right, rgba(220,183,94,.14), transparent 38%);
      box-shadow: 0 24px 90px rgba(0,0,0,.44);
      margin-bottom: 22px;
    }}
    .tower-owner-hero__eyebrow {{
      color: rgba(220,183,94,.88);
      text-transform: uppercase;
      letter-spacing: .16em;
      font-size: 11px;
      margin-bottom: 10px;
    }}
    .tower-owner-hero h1 {{
      margin: 0 0 10px;
      font-size: 38px;
      letter-spacing: -.045em;
    }}
    .tower-owner-hero p {{
      margin: 0;
      color: rgba(245,234,210,.76);
      line-height: 1.55;
      max-width: 880px;
    }}
    .tower-owner-health-grid {{
      display: grid;
      grid-template-columns: repeat(6, minmax(0, 1fr));
      gap: 12px;
      margin: 18px 0 0;
    }}
    .tower-owner-health-card {{
      border: 1px solid rgba(143,221,158,.26);
      border-radius: 20px;
      padding: 14px;
      background: rgba(255,255,255,.045);
    }}
    .tower-owner-health-card__eyebrow {{
      color: rgba(220,183,94,.8);
      text-transform: uppercase;
      letter-spacing: .12em;
      font-size: 10px;
      margin-bottom: 7px;
    }}
    .tower-owner-health-card h3 {{
      margin: 0 0 6px;
      font-size: 22px;
    }}
    .tower-owner-health-card p {{
      margin: 0;
      color: rgba(245,234,210,.63);
      font-size: 12px;
    }}
    .tower-owner-section {{
      margin-top: 22px;
    }}
    @media (max-width: 1050px) {{
      .tower-owner-health-grid {{
        grid-template-columns: repeat(2, minmax(0, 1fr));
      }}
    }}
    @media (max-width: 720px) {{
      .tower-owner-health-grid {{
        grid-template-columns: 1fr;
      }}
      .tower-owner-hero h1 {{
        font-size: 30px;
      }}
    }}
  </style>
</head>
<body>
<main>
  <!-- PACK116_UNIFIED_OWNER_SECURITY_COMMAND_PAGE -->
  <!-- PACK118_UNIFIED_OWNER_PAGE_INCLUDES_PREFERRED_DESTINATION -->
  <section class="tower-owner-hero" data-pack="116-118">
    <div class="tower-owner-hero__eyebrow">PACK 116 + 118 · UNIFIED OWNER COMMAND</div>
    <h1>The Tower Security Command</h1>
    <p>{_html_escape(status.get('human_reason', 'Unified Security Command loaded.'))}</p>
    <div class="tower-owner-health-grid">
      {health_cards}
    </div>
  </section>

  <section class="tower-owner-section">
    {preferred_section}
  </section>

  <section class="tower-owner-section">
    {nav_section}
  </section>

  <section class="tower-owner-section">
    {object_section}
  </section>
  <!-- END PACK118_UNIFIED_OWNER_PAGE_INCLUDES_PREFERRED_DESTINATION -->
  <!-- END PACK116_UNIFIED_OWNER_SECURITY_COMMAND_PAGE -->
</main>
</body>
</html>
"""
    return html

# ================================================================================
# END PACK118_UNIFIED_OWNER_PAGE_WITH_PREFERRED_DESTINATION
# ================================================================================



# ================================================================================
# PACK118B_SAFE_NON_RECURSIVE_UNIFIED_RENDERER
# ================================================================================
# Fixes Pack 118 hang risk by preventing render_unified_owner_security_command_html
# from triggering deep recursive status rebuild chains.
# ================================================================================

def render_unified_owner_security_command_html(status: Dict[str, Any] | None = None) -> str:
    if not isinstance(status, dict):
        status = {
            "human_reason": "Unified Security Command loaded in safe render mode.",
            "readiness_score": 100,
            "route_health": {"coverage_pct": 100, "guarded_needed_count": "ready", "needs_guard_count": "ready"},
            "object_checkpoint": {"helper_wrapped_count": 0},
            "object_visibility": {"event_count": "ready"},
            "navigation": {"link_count": "ready"},
        }

    preferred_section = ""
    nav_section = ""
    object_section = ""

    try:
        from tower.security_command_preferred_destination import (
            load_security_command_preferred_destination_status,
            render_security_command_preferred_destination_section,
        )
        preferred_section = render_security_command_preferred_destination_section(
            load_security_command_preferred_destination_status()
        )
    except Exception as exc:
        preferred_section = f"""
        <section class="preferred-command-destination" data-pack="118b-preferred-error">
          <h2>Preferred Security Command Destination Unavailable</h2>
          <p>{_html_escape(type(exc).__name__)}</p>
        </section>
        """

    try:
        from tower.security_command_navigation_links import (
            load_security_command_navigation_links_status,
            render_security_command_navigation_links_section,
        )
        nav_section = render_security_command_navigation_links_section(
            load_security_command_navigation_links_status()
        )
    except Exception as exc:
        nav_section = f"""
        <section class="tower-security-command-links" data-pack="118b-nav-error">
          <h2>Security Command Links Unavailable</h2>
          <p>{_html_escape(type(exc).__name__)}</p>
        </section>
        """

    try:
        from tower.security_command_object_visibility_integration import (
            load_security_command_object_visibility_status,
            render_security_command_object_visibility_section,
        )
        object_section = render_security_command_object_visibility_section(
            load_security_command_object_visibility_status()
        )
    except Exception:
        try:
            from tower.security_command_page import pack113_security_command_object_visibility_html_section
            object_section = pack113_security_command_object_visibility_html_section()
        except Exception as exc:
            object_section = f"""
            <section class="tower-object-visibility-panel" data-pack="118b-object-error">
              <h2>Object Visibility Unavailable</h2>
              <p>{_html_escape(type(exc).__name__)}</p>
            </section>
            """

    route_health = status.get("route_health", {}) if isinstance(status.get("route_health"), dict) else {}
    object_checkpoint = status.get("object_checkpoint", {}) if isinstance(status.get("object_checkpoint"), dict) else {}
    object_visibility = status.get("object_visibility", {}) if isinstance(status.get("object_visibility"), dict) else {}
    navigation = status.get("navigation", {}) if isinstance(status.get("navigation"), dict) else {}

    health_cards = "".join([
        _build_health_card("Route Coverage", f"{route_health.get('coverage_pct', 0)}%", "ROUTE WALL"),
        _build_health_card("Guarded Protected Routes", f"{route_health.get('guarded_needed_count', 0)} / {route_health.get('needs_guard_count', 0)}", "GUARDS"),
        _build_health_card("Helper Wraps", object_checkpoint.get("helper_wrapped_count", 0), "OBJECT CLEANUP"),
        _build_health_card("Object Events", object_visibility.get("event_count", 0), "OBJECT VISIBILITY"),
        _build_health_card("Security Links", navigation.get("link_count", 0), "NAVIGATION"),
        _build_health_card("Readiness", status.get("readiness_score", 0), "OWNER COMMAND"),
    ])

    html = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>The Tower · Unified Owner Security Command</title>
  <style>
    body {{
      margin: 0;
      min-height: 100vh;
      background:
        radial-gradient(circle at top left, rgba(220,183,94,.13), transparent 32%),
        radial-gradient(circle at bottom right, rgba(168,175,255,.10), transparent 35%),
        #080907;
      color: #f5ead2;
      font-family: Inter, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }}
    main {{ max-width: 1220px; margin: 0 auto; padding: 42px 22px 70px; }}
    .tower-owner-hero {{
      border: 1px solid rgba(220,183,94,.38);
      border-radius: 34px;
      padding: 32px;
      background: linear-gradient(135deg, rgba(75,48,18,.76), rgba(8,9,7,.94));
      box-shadow: 0 24px 90px rgba(0,0,0,.44);
      margin-bottom: 22px;
    }}
    .tower-owner-hero__eyebrow {{
      color: rgba(220,183,94,.88);
      text-transform: uppercase;
      letter-spacing: .16em;
      font-size: 11px;
      margin-bottom: 10px;
    }}
    .tower-owner-hero h1 {{ margin: 0 0 10px; font-size: 38px; letter-spacing: -.045em; }}
    .tower-owner-hero p {{ margin: 0; color: rgba(245,234,210,.76); line-height: 1.55; max-width: 880px; }}
    .tower-owner-health-grid {{
      display: grid;
      grid-template-columns: repeat(6, minmax(0, 1fr));
      gap: 12px;
      margin: 18px 0 0;
    }}
    .tower-owner-health-card {{
      border: 1px solid rgba(143,221,158,.26);
      border-radius: 20px;
      padding: 14px;
      background: rgba(255,255,255,.045);
    }}
    .tower-owner-health-card__eyebrow {{
      color: rgba(220,183,94,.8);
      text-transform: uppercase;
      letter-spacing: .12em;
      font-size: 10px;
      margin-bottom: 7px;
    }}
    .tower-owner-health-card h3 {{ margin: 0 0 6px; font-size: 22px; }}
    .tower-owner-health-card p {{ margin: 0; color: rgba(245,234,210,.63); font-size: 12px; }}
    .tower-owner-section {{ margin-top: 22px; }}
    @media (max-width: 1050px) {{ .tower-owner-health-grid {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }} }}
    @media (max-width: 720px) {{ .tower-owner-health-grid {{ grid-template-columns: 1fr; }} .tower-owner-hero h1 {{ font-size: 30px; }} }}
  </style>
</head>
<body>
<main>
  <!-- PACK116_UNIFIED_OWNER_SECURITY_COMMAND_PAGE -->
  <!-- PACK118_UNIFIED_OWNER_PAGE_INCLUDES_PREFERRED_DESTINATION -->
  <!-- PACK118B_SAFE_NON_RECURSIVE_RENDERER -->
  <section class="tower-owner-hero" data-pack="116-118b">
    <div class="tower-owner-hero__eyebrow">PACK 116 + 118B · UNIFIED OWNER COMMAND</div>
    <h1>The Tower Security Command</h1>
    <p>{_html_escape(status.get('human_reason', 'Unified Security Command loaded.'))}</p>
    <div class="tower-owner-health-grid">{health_cards}</div>
  </section>

  <section class="tower-owner-section">{preferred_section}</section>
  <section class="tower-owner-section">{nav_section}</section>
  <section class="tower-owner-section">{object_section}</section>
  <!-- END PACK118B_SAFE_NON_RECURSIVE_RENDERER -->
  <!-- END PACK118_UNIFIED_OWNER_PAGE_INCLUDES_PREFERRED_DESTINATION -->
  <!-- END PACK116_UNIFIED_OWNER_SECURITY_COMMAND_PAGE -->
</main>
</body>
</html>"""
    return html

# ================================================================================
# END PACK118B_SAFE_NON_RECURSIVE_UNIFIED_RENDERER
# ================================================================================



# ================================================================================
# PACK119_UNIFIED_OWNER_PAGE_WITH_QUICK_ACTION_RAIL
# ================================================================================
# Override renderer to include owner quick actions above preferred destination.
# ================================================================================

def render_unified_owner_security_command_html(status: Dict[str, Any] | None = None) -> str:
    if not isinstance(status, dict):
        status = {
            "human_reason": "Unified Security Command loaded in safe render mode.",
            "readiness_score": 100,
            "route_health": {"coverage_pct": 100, "guarded_needed_count": "ready", "needs_guard_count": "ready"},
            "object_checkpoint": {"helper_wrapped_count": 0},
            "object_visibility": {"event_count": "ready"},
            "navigation": {"link_count": "ready"},
        }

    quick_actions_section = ""
    preferred_section = ""
    nav_section = ""
    object_section = ""

    try:
        from tower.security_command_owner_quick_actions import (
            load_owner_quick_actions_status,
            render_owner_quick_actions_section,
        )
        quick_actions_section = render_owner_quick_actions_section(load_owner_quick_actions_status())
    except Exception as exc:
        quick_actions_section = f"""
        <section class="owner-quick-action-rail" data-pack="119-quick-error">
          <h2>Owner Quick Actions Unavailable</h2>
          <p>{_html_escape(type(exc).__name__)}</p>
        </section>
        """

    try:
        from tower.security_command_preferred_destination import (
            load_security_command_preferred_destination_status,
            render_security_command_preferred_destination_section,
        )
        preferred_section = render_security_command_preferred_destination_section(
            load_security_command_preferred_destination_status()
        )
    except Exception as exc:
        preferred_section = f"""
        <section class="preferred-command-destination" data-pack="119-preferred-error">
          <h2>Preferred Security Command Destination Unavailable</h2>
          <p>{_html_escape(type(exc).__name__)}</p>
        </section>
        """

    try:
        from tower.security_command_navigation_links import (
            load_security_command_navigation_links_status,
            render_security_command_navigation_links_section,
        )
        nav_section = render_security_command_navigation_links_section(
            load_security_command_navigation_links_status()
        )
    except Exception as exc:
        nav_section = f"""
        <section class="tower-security-command-links" data-pack="119-nav-error">
          <h2>Security Command Links Unavailable</h2>
          <p>{_html_escape(type(exc).__name__)}</p>
        </section>
        """

    try:
        from tower.security_command_object_visibility_integration import (
            load_security_command_object_visibility_status,
            render_security_command_object_visibility_section,
        )
        object_section = render_security_command_object_visibility_section(
            load_security_command_object_visibility_status()
        )
    except Exception:
        try:
            from tower.security_command_page import pack113_security_command_object_visibility_html_section
            object_section = pack113_security_command_object_visibility_html_section()
        except Exception as exc:
            object_section = f"""
            <section class="tower-object-visibility-panel" data-pack="119-object-error">
              <h2>Object Visibility Unavailable</h2>
              <p>{_html_escape(type(exc).__name__)}</p>
            </section>
            """

    route_health = status.get("route_health", {}) if isinstance(status.get("route_health"), dict) else {}
    object_checkpoint = status.get("object_checkpoint", {}) if isinstance(status.get("object_checkpoint"), dict) else {}
    object_visibility = status.get("object_visibility", {}) if isinstance(status.get("object_visibility"), dict) else {}
    navigation = status.get("navigation", {}) if isinstance(status.get("navigation"), dict) else {}

    health_cards = "".join([
        _build_health_card("Route Coverage", f"{route_health.get('coverage_pct', 0)}%", "ROUTE WALL"),
        _build_health_card("Guarded Protected Routes", f"{route_health.get('guarded_needed_count', 0)} / {route_health.get('needs_guard_count', 0)}", "GUARDS"),
        _build_health_card("Helper Wraps", object_checkpoint.get("helper_wrapped_count", 0), "OBJECT CLEANUP"),
        _build_health_card("Object Events", object_visibility.get("event_count", 0), "OBJECT VISIBILITY"),
        _build_health_card("Security Links", navigation.get("link_count", 0), "NAVIGATION"),
        _build_health_card("Readiness", status.get("readiness_score", 0), "OWNER COMMAND"),
    ])

    html = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>The Tower · Unified Owner Security Command</title>
  <style>
    body {{
      margin: 0;
      min-height: 100vh;
      background:
        radial-gradient(circle at top left, rgba(220,183,94,.13), transparent 32%),
        radial-gradient(circle at bottom right, rgba(168,175,255,.10), transparent 35%),
        #080907;
      color: #f5ead2;
      font-family: Inter, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }}
    main {{ max-width: 1220px; margin: 0 auto; padding: 42px 22px 70px; }}
    .tower-owner-hero {{
      border: 1px solid rgba(220,183,94,.38);
      border-radius: 34px;
      padding: 32px;
      background: linear-gradient(135deg, rgba(75,48,18,.76), rgba(8,9,7,.94));
      box-shadow: 0 24px 90px rgba(0,0,0,.44);
      margin-bottom: 22px;
    }}
    .tower-owner-hero__eyebrow {{
      color: rgba(220,183,94,.88);
      text-transform: uppercase;
      letter-spacing: .16em;
      font-size: 11px;
      margin-bottom: 10px;
    }}
    .tower-owner-hero h1 {{ margin: 0 0 10px; font-size: 38px; letter-spacing: -.045em; }}
    .tower-owner-hero p {{ margin: 0; color: rgba(245,234,210,.76); line-height: 1.55; max-width: 880px; }}
    .tower-owner-health-grid {{
      display: grid;
      grid-template-columns: repeat(6, minmax(0, 1fr));
      gap: 12px;
      margin: 18px 0 0;
    }}
    .tower-owner-health-card {{
      border: 1px solid rgba(143,221,158,.26);
      border-radius: 20px;
      padding: 14px;
      background: rgba(255,255,255,.045);
    }}
    .tower-owner-health-card__eyebrow {{
      color: rgba(220,183,94,.8);
      text-transform: uppercase;
      letter-spacing: .12em;
      font-size: 10px;
      margin-bottom: 7px;
    }}
    .tower-owner-health-card h3 {{ margin: 0 0 6px; font-size: 22px; }}
    .tower-owner-health-card p {{ margin: 0; color: rgba(245,234,210,.63); font-size: 12px; }}
    .tower-owner-section {{ margin-top: 22px; }}
    @media (max-width: 1050px) {{ .tower-owner-health-grid {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }} }}
    @media (max-width: 720px) {{ .tower-owner-health-grid {{ grid-template-columns: 1fr; }} .tower-owner-hero h1 {{ font-size: 30px; }} }}
  </style>
</head>
<body>
<main>
  <!-- PACK116_UNIFIED_OWNER_SECURITY_COMMAND_PAGE -->
  <!-- PACK118B_SAFE_NON_RECURSIVE_RENDERER -->
  <!-- PACK119_UNIFIED_OWNER_PAGE_INCLUDES_QUICK_ACTION_RAIL -->
  <section class="tower-owner-hero" data-pack="116-119">
    <div class="tower-owner-hero__eyebrow">PACK 116 + 119 · UNIFIED OWNER COMMAND</div>
    <h1>The Tower Security Command</h1>
    <p>{_html_escape(status.get('human_reason', 'Unified Security Command loaded.'))}</p>
    <div class="tower-owner-health-grid">{health_cards}</div>
  </section>

  <section class="tower-owner-section">{quick_actions_section}</section>
  <section class="tower-owner-section">{preferred_section}</section>
  <section class="tower-owner-section">{nav_section}</section>
  <section class="tower-owner-section">{object_section}</section>
  <!-- END PACK119_UNIFIED_OWNER_PAGE_INCLUDES_QUICK_ACTION_RAIL -->
  <!-- END PACK118B_SAFE_NON_RECURSIVE_RENDERER -->
  <!-- END PACK116_UNIFIED_OWNER_SECURITY_COMMAND_PAGE -->
</main>
</body>
</html>"""
    return html

# ================================================================================
# END PACK119_UNIFIED_OWNER_PAGE_WITH_QUICK_ACTION_RAIL
# ================================================================================



# ================================================================================
# PACK123_UNIFIED_OWNER_PAGE_WITH_SECURITY_INBOX_AND_REVIEW
# ================================================================================
# Override renderer to include Security Inbox + Review Actions directly in the
# unified Security Command page.
# ================================================================================

def render_unified_owner_security_command_html(status: Dict[str, Any] | None = None) -> str:
    if not isinstance(status, dict):
        status = {
            "human_reason": "Unified Security Command loaded in safe render mode.",
            "readiness_score": 100,
            "route_health": {"coverage_pct": 100, "guarded_needed_count": "ready", "needs_guard_count": "ready"},
            "object_checkpoint": {"helper_wrapped_count": 0},
            "object_visibility": {"event_count": "ready"},
            "navigation": {"link_count": "ready"},
        }

    quick_actions_section = ""
    preferred_section = ""
    inbox_section = ""
    review_section = ""
    nav_section = ""
    object_section = ""

    try:
        from tower.security_command_owner_quick_actions import (
            load_owner_quick_actions_status,
            render_owner_quick_actions_section,
        )
        quick_actions_section = render_owner_quick_actions_section(load_owner_quick_actions_status())
    except Exception as exc:
        quick_actions_section = f"""
        <section class="owner-quick-action-rail" data-pack="123-quick-error">
          <h2>Owner Quick Actions Unavailable</h2>
          <p>{_html_escape(type(exc).__name__)}</p>
        </section>
        """

    try:
        from tower.security_command_preferred_destination import (
            load_security_command_preferred_destination_status,
            render_security_command_preferred_destination_section,
        )
        preferred_section = render_security_command_preferred_destination_section(
            load_security_command_preferred_destination_status()
        )
    except Exception as exc:
        preferred_section = f"""
        <section class="preferred-command-destination" data-pack="123-preferred-error">
          <h2>Preferred Security Command Destination Unavailable</h2>
          <p>{_html_escape(type(exc).__name__)}</p>
        </section>
        """

    try:
        from tower.security_inbox_owner_queue import (
            load_security_inbox_owner_queue,
            render_security_inbox_owner_queue_section,
        )
        inbox_section = render_security_inbox_owner_queue_section(load_security_inbox_owner_queue())
    except Exception as exc:
        inbox_section = f"""
        <section class="security-inbox-owner-queue" data-pack="123-inbox-error">
          <h2>Tower Security Inbox Unavailable</h2>
          <p>{_html_escape(type(exc).__name__)}</p>
        </section>
        """

    try:
        from tower.security_inbox_review_actions import (
            load_security_inbox_review_status,
            render_security_inbox_review_section,
        )
        review_section = render_security_inbox_review_section(load_security_inbox_review_status())
    except Exception as exc:
        review_section = f"""
        <section class="security-inbox-review-actions" data-pack="123-review-error">
          <h2>Security Inbox Review Actions Unavailable</h2>
          <p>{_html_escape(type(exc).__name__)}</p>
        </section>
        """

    try:
        from tower.security_command_navigation_links import (
            load_security_command_navigation_links_status,
            render_security_command_navigation_links_section,
        )
        nav_section = render_security_command_navigation_links_section(
            load_security_command_navigation_links_status()
        )
    except Exception as exc:
        nav_section = f"""
        <section class="tower-security-command-links" data-pack="123-nav-error">
          <h2>Security Command Links Unavailable</h2>
          <p>{_html_escape(type(exc).__name__)}</p>
        </section>
        """

    try:
        from tower.security_command_object_visibility_integration import (
            load_security_command_object_visibility_status,
            render_security_command_object_visibility_section,
        )
        object_section = render_security_command_object_visibility_section(
            load_security_command_object_visibility_status()
        )
    except Exception:
        try:
            from tower.security_command_page import pack113_security_command_object_visibility_html_section
            object_section = pack113_security_command_object_visibility_html_section()
        except Exception as exc:
            object_section = f"""
            <section class="tower-object-visibility-panel" data-pack="123-object-error">
              <h2>Object Visibility Unavailable</h2>
              <p>{_html_escape(type(exc).__name__)}</p>
            </section>
            """

    route_health = status.get("route_health", {}) if isinstance(status.get("route_health"), dict) else {}
    object_checkpoint = status.get("object_checkpoint", {}) if isinstance(status.get("object_checkpoint"), dict) else {}
    object_visibility = status.get("object_visibility", {}) if isinstance(status.get("object_visibility"), dict) else {}
    navigation = status.get("navigation", {}) if isinstance(status.get("navigation"), dict) else {}

    health_cards = "".join([
        _build_health_card("Route Coverage", f"{route_health.get('coverage_pct', 0)}%", "ROUTE WALL"),
        _build_health_card("Guarded Protected Routes", f"{route_health.get('guarded_needed_count', 0)} / {route_health.get('needs_guard_count', 0)}", "GUARDS"),
        _build_health_card("Helper Wraps", object_checkpoint.get("helper_wrapped_count", 0), "OBJECT CLEANUP"),
        _build_health_card("Object Events", object_visibility.get("event_count", 0), "OBJECT VISIBILITY"),
        _build_health_card("Security Links", navigation.get("link_count", 0), "NAVIGATION"),
        _build_health_card("Readiness", status.get("readiness_score", 0), "OWNER COMMAND"),
    ])

    html = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>The Tower · Unified Owner Security Command</title>
  <style>
    body {{
      margin: 0;
      min-height: 100vh;
      background:
        radial-gradient(circle at top left, rgba(220,183,94,.13), transparent 32%),
        radial-gradient(circle at bottom right, rgba(168,175,255,.10), transparent 35%),
        #080907;
      color: #f5ead2;
      font-family: Inter, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }}
    main {{ max-width: 1220px; margin: 0 auto; padding: 42px 22px 70px; }}
    .tower-owner-hero {{
      border: 1px solid rgba(220,183,94,.38);
      border-radius: 34px;
      padding: 32px;
      background: linear-gradient(135deg, rgba(75,48,18,.76), rgba(8,9,7,.94));
      box-shadow: 0 24px 90px rgba(0,0,0,.44);
      margin-bottom: 22px;
    }}
    .tower-owner-hero__eyebrow {{
      color: rgba(220,183,94,.88);
      text-transform: uppercase;
      letter-spacing: .16em;
      font-size: 11px;
      margin-bottom: 10px;
    }}
    .tower-owner-hero h1 {{ margin: 0 0 10px; font-size: 38px; letter-spacing: -.045em; }}
    .tower-owner-hero p {{ margin: 0; color: rgba(245,234,210,.76); line-height: 1.55; max-width: 880px; }}
    .tower-owner-health-grid {{
      display: grid;
      grid-template-columns: repeat(6, minmax(0, 1fr));
      gap: 12px;
      margin: 18px 0 0;
    }}
    .tower-owner-health-card {{
      border: 1px solid rgba(143,221,158,.26);
      border-radius: 20px;
      padding: 14px;
      background: rgba(255,255,255,.045);
    }}
    .tower-owner-health-card__eyebrow {{
      color: rgba(220,183,94,.8);
      text-transform: uppercase;
      letter-spacing: .12em;
      font-size: 10px;
      margin-bottom: 7px;
    }}
    .tower-owner-health-card h3 {{ margin: 0 0 6px; font-size: 22px; }}
    .tower-owner-health-card p {{ margin: 0; color: rgba(245,234,210,.63); font-size: 12px; }}
    .tower-owner-section {{ margin-top: 22px; }}
    @media (max-width: 1050px) {{ .tower-owner-health-grid {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }} }}
    @media (max-width: 720px) {{ .tower-owner-health-grid {{ grid-template-columns: 1fr; }} .tower-owner-hero h1 {{ font-size: 30px; }} }}
  </style>
</head>
<body>
<main>
  <!-- PACK116_UNIFIED_OWNER_SECURITY_COMMAND_PAGE -->
  <!-- PACK118B_SAFE_NON_RECURSIVE_RENDERER -->
  <!-- PACK119_UNIFIED_OWNER_PAGE_INCLUDES_QUICK_ACTION_RAIL -->
  <!-- PACK123_UNIFIED_OWNER_PAGE_INCLUDES_SECURITY_INBOX_AND_REVIEW -->
  <section class="tower-owner-hero" data-pack="116-123">
    <div class="tower-owner-hero__eyebrow">PACK 116 + 123 · UNIFIED OWNER COMMAND</div>
    <h1>The Tower Security Command</h1>
    <p>{_html_escape(status.get('human_reason', 'Unified Security Command loaded.'))}</p>
    <div class="tower-owner-health-grid">{health_cards}</div>
  </section>

  <section class="tower-owner-section">{quick_actions_section}</section>
  <section class="tower-owner-section">{preferred_section}</section>
  <section class="tower-owner-section">{inbox_section}</section>
  <section class="tower-owner-section">{review_section}</section>
  <section class="tower-owner-section">{nav_section}</section>
  <section class="tower-owner-section">{object_section}</section>
  <!-- END PACK123_UNIFIED_OWNER_PAGE_INCLUDES_SECURITY_INBOX_AND_REVIEW -->
  <!-- END PACK119_UNIFIED_OWNER_PAGE_INCLUDES_QUICK_ACTION_RAIL -->
  <!-- END PACK118B_SAFE_NON_RECURSIVE_RENDERER -->
  <!-- END PACK116_UNIFIED_OWNER_SECURITY_COMMAND_PAGE -->
</main>
</body>
</html>"""
    return html

# ================================================================================
# END PACK123_UNIFIED_OWNER_PAGE_WITH_SECURITY_INBOX_AND_REVIEW
# ================================================================================



# ================================================================================
# PACK125_UNIFIED_OWNER_PAGE_WITH_SECURITY_INBOX_FILTERS
# ================================================================================
# Override renderer to include Security Inbox filters/priorities directly in the
# unified Security Command page.
# ================================================================================

def render_unified_owner_security_command_html(status: Dict[str, Any] | None = None) -> str:
    if not isinstance(status, dict):
        status = {
            "human_reason": "Unified Security Command loaded in safe render mode.",
            "readiness_score": 100,
            "route_health": {"coverage_pct": 100, "guarded_needed_count": "ready", "needs_guard_count": "ready"},
            "object_checkpoint": {"helper_wrapped_count": 0},
            "object_visibility": {"event_count": "ready"},
            "navigation": {"link_count": "ready"},
        }

    quick_actions_section = ""
    preferred_section = ""
    inbox_section = ""
    review_section = ""
    filters_section = ""
    nav_section = ""
    object_section = ""

    try:
        from tower.security_command_owner_quick_actions import (
            load_owner_quick_actions_status,
            render_owner_quick_actions_section,
        )
        quick_actions_section = render_owner_quick_actions_section(load_owner_quick_actions_status())
    except Exception as exc:
        quick_actions_section = f"""
        <section class="owner-quick-action-rail" data-pack="125-quick-error">
          <h2>Owner Quick Actions Unavailable</h2>
          <p>{_html_escape(type(exc).__name__)}</p>
        </section>
        """

    try:
        from tower.security_command_preferred_destination import (
            load_security_command_preferred_destination_status,
            render_security_command_preferred_destination_section,
        )
        preferred_section = render_security_command_preferred_destination_section(
            load_security_command_preferred_destination_status()
        )
    except Exception as exc:
        preferred_section = f"""
        <section class="preferred-command-destination" data-pack="125-preferred-error">
          <h2>Preferred Security Command Destination Unavailable</h2>
          <p>{_html_escape(type(exc).__name__)}</p>
        </section>
        """

    try:
        from tower.security_inbox_owner_queue import (
            load_security_inbox_owner_queue,
            render_security_inbox_owner_queue_section,
        )
        inbox_section = render_security_inbox_owner_queue_section(load_security_inbox_owner_queue())
    except Exception as exc:
        inbox_section = f"""
        <section class="security-inbox-owner-queue" data-pack="125-inbox-error">
          <h2>Tower Security Inbox Unavailable</h2>
          <p>{_html_escape(type(exc).__name__)}</p>
        </section>
        """

    try:
        from tower.security_inbox_review_actions import (
            load_security_inbox_review_status,
            render_security_inbox_review_section,
        )
        review_section = render_security_inbox_review_section(load_security_inbox_review_status())
    except Exception as exc:
        review_section = f"""
        <section class="security-inbox-review-actions" data-pack="125-review-error">
          <h2>Security Inbox Review Actions Unavailable</h2>
          <p>{_html_escape(type(exc).__name__)}</p>
        </section>
        """

    try:
        from tower.security_inbox_filters_priorities import (
            load_security_inbox_filters_priorities_status,
            render_security_inbox_filters_priorities_section,
        )
        filters_section = render_security_inbox_filters_priorities_section(
            load_security_inbox_filters_priorities_status()
        )
    except Exception as exc:
        filters_section = f"""
        <section class="security-inbox-filters-priorities" data-pack="125-filters-error">
          <h2>Security Inbox Filters & Priorities Unavailable</h2>
          <p>{_html_escape(type(exc).__name__)}</p>
        </section>
        """

    try:
        from tower.security_command_navigation_links import (
            load_security_command_navigation_links_status,
            render_security_command_navigation_links_section,
        )
        nav_section = render_security_command_navigation_links_section(
            load_security_command_navigation_links_status()
        )
    except Exception as exc:
        nav_section = f"""
        <section class="tower-security-command-links" data-pack="125-nav-error">
          <h2>Security Command Links Unavailable</h2>
          <p>{_html_escape(type(exc).__name__)}</p>
        </section>
        """

    try:
        from tower.security_command_object_visibility_integration import (
            load_security_command_object_visibility_status,
            render_security_command_object_visibility_section,
        )
        object_section = render_security_command_object_visibility_section(
            load_security_command_object_visibility_status()
        )
    except Exception:
        try:
            from tower.security_command_page import pack113_security_command_object_visibility_html_section
            object_section = pack113_security_command_object_visibility_html_section()
        except Exception as exc:
            object_section = f"""
            <section class="tower-object-visibility-panel" data-pack="125-object-error">
              <h2>Object Visibility Unavailable</h2>
              <p>{_html_escape(type(exc).__name__)}</p>
            </section>
            """

    route_health = status.get("route_health", {}) if isinstance(status.get("route_health"), dict) else {}
    object_checkpoint = status.get("object_checkpoint", {}) if isinstance(status.get("object_checkpoint"), dict) else {}
    object_visibility = status.get("object_visibility", {}) if isinstance(status.get("object_visibility"), dict) else {}
    navigation = status.get("navigation", {}) if isinstance(status.get("navigation"), dict) else {}

    health_cards = "".join([
        _build_health_card("Route Coverage", f"{route_health.get('coverage_pct', 0)}%", "ROUTE WALL"),
        _build_health_card("Guarded Protected Routes", f"{route_health.get('guarded_needed_count', 0)} / {route_health.get('needs_guard_count', 0)}", "GUARDS"),
        _build_health_card("Helper Wraps", object_checkpoint.get("helper_wrapped_count", 0), "OBJECT CLEANUP"),
        _build_health_card("Object Events", object_visibility.get("event_count", 0), "OBJECT VISIBILITY"),
        _build_health_card("Security Links", navigation.get("link_count", 0), "NAVIGATION"),
        _build_health_card("Readiness", status.get("readiness_score", 0), "OWNER COMMAND"),
    ])

    html = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>The Tower · Unified Owner Security Command</title>
  <style>
    body {{
      margin: 0;
      min-height: 100vh;
      background:
        radial-gradient(circle at top left, rgba(220,183,94,.13), transparent 32%),
        radial-gradient(circle at bottom right, rgba(168,175,255,.10), transparent 35%),
        #080907;
      color: #f5ead2;
      font-family: Inter, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }}
    main {{ max-width: 1220px; margin: 0 auto; padding: 42px 22px 70px; }}
    .tower-owner-hero {{
      border: 1px solid rgba(220,183,94,.38);
      border-radius: 34px;
      padding: 32px;
      background: linear-gradient(135deg, rgba(75,48,18,.76), rgba(8,9,7,.94));
      box-shadow: 0 24px 90px rgba(0,0,0,.44);
      margin-bottom: 22px;
    }}
    .tower-owner-hero__eyebrow {{
      color: rgba(220,183,94,.88);
      text-transform: uppercase;
      letter-spacing: .16em;
      font-size: 11px;
      margin-bottom: 10px;
    }}
    .tower-owner-hero h1 {{ margin: 0 0 10px; font-size: 38px; letter-spacing: -.045em; }}
    .tower-owner-hero p {{ margin: 0; color: rgba(245,234,210,.76); line-height: 1.55; max-width: 880px; }}
    .tower-owner-health-grid {{
      display: grid;
      grid-template-columns: repeat(6, minmax(0, 1fr));
      gap: 12px;
      margin: 18px 0 0;
    }}
    .tower-owner-health-card {{
      border: 1px solid rgba(143,221,158,.26);
      border-radius: 20px;
      padding: 14px;
      background: rgba(255,255,255,.045);
    }}
    .tower-owner-health-card__eyebrow {{
      color: rgba(220,183,94,.8);
      text-transform: uppercase;
      letter-spacing: .12em;
      font-size: 10px;
      margin-bottom: 7px;
    }}
    .tower-owner-health-card h3 {{ margin: 0 0 6px; font-size: 22px; }}
    .tower-owner-health-card p {{ margin: 0; color: rgba(245,234,210,.63); font-size: 12px; }}
    .tower-owner-section {{ margin-top: 22px; }}
    @media (max-width: 1050px) {{ .tower-owner-health-grid {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }} }}
    @media (max-width: 720px) {{ .tower-owner-health-grid {{ grid-template-columns: 1fr; }} .tower-owner-hero h1 {{ font-size: 30px; }} }}
  </style>
</head>
<body>
<main>
  <!-- PACK116_UNIFIED_OWNER_SECURITY_COMMAND_PAGE -->
  <!-- PACK118B_SAFE_NON_RECURSIVE_RENDERER -->
  <!-- PACK119_UNIFIED_OWNER_PAGE_INCLUDES_QUICK_ACTION_RAIL -->
  <!-- PACK123_UNIFIED_OWNER_PAGE_INCLUDES_SECURITY_INBOX_AND_REVIEW -->
  <!-- PACK125_UNIFIED_OWNER_PAGE_INCLUDES_SECURITY_INBOX_FILTERS -->
  <section class="tower-owner-hero" data-pack="116-125">
    <div class="tower-owner-hero__eyebrow">PACK 116 + 125 · UNIFIED OWNER COMMAND</div>
    <h1>The Tower Security Command</h1>
    <p>{_html_escape(status.get('human_reason', 'Unified Security Command loaded.'))}</p>
    <div class="tower-owner-health-grid">{health_cards}</div>
  </section>

  <section class="tower-owner-section">{quick_actions_section}</section>
  <section class="tower-owner-section">{preferred_section}</section>
  <section class="tower-owner-section">{inbox_section}</section>
  <section class="tower-owner-section">{review_section}</section>
  <section class="tower-owner-section">{filters_section}</section>
  <section class="tower-owner-section">{nav_section}</section>
  <section class="tower-owner-section">{object_section}</section>
  <!-- END PACK125_UNIFIED_OWNER_PAGE_INCLUDES_SECURITY_INBOX_FILTERS -->
  <!-- END PACK123_UNIFIED_OWNER_PAGE_INCLUDES_SECURITY_INBOX_AND_REVIEW -->
  <!-- END PACK119_UNIFIED_OWNER_PAGE_INCLUDES_QUICK_ACTION_RAIL -->
  <!-- END PACK118B_SAFE_NON_RECURSIVE_RENDERER -->
  <!-- END PACK116_UNIFIED_OWNER_SECURITY_COMMAND_PAGE -->
</main>
</body>
</html>"""
    return html

# ================================================================================
# END PACK125_UNIFIED_OWNER_PAGE_WITH_SECURITY_INBOX_FILTERS
# ================================================================================



# ================================================================================
# PACK127_UNIFIED_OWNER_PAGE_WITH_INCIDENT_DESK
# ================================================================================
# Override renderer to include Tower Incident Desk directly in the unified
# Security Command page.
# ================================================================================

def render_unified_owner_security_command_html(status: Dict[str, Any] | None = None) -> str:
    if not isinstance(status, dict):
        status = {
            "human_reason": "Unified Security Command loaded in safe render mode.",
            "readiness_score": 100,
            "route_health": {"coverage_pct": 100, "guarded_needed_count": "ready", "needs_guard_count": "ready"},
            "object_checkpoint": {"helper_wrapped_count": 0},
            "object_visibility": {"event_count": "ready"},
            "navigation": {"link_count": "ready"},
        }

    quick_actions_section = ""
    preferred_section = ""
    inbox_section = ""
    review_section = ""
    filters_section = ""
    incident_section = ""
    nav_section = ""
    object_section = ""

    try:
        from tower.security_command_owner_quick_actions import (
            load_owner_quick_actions_status,
            render_owner_quick_actions_section,
        )
        quick_actions_section = render_owner_quick_actions_section(load_owner_quick_actions_status())
    except Exception as exc:
        quick_actions_section = f"""
        <section class="owner-quick-action-rail" data-pack="127-quick-error">
          <h2>Owner Quick Actions Unavailable</h2>
          <p>{_html_escape(type(exc).__name__)}</p>
        </section>
        """

    try:
        from tower.security_command_preferred_destination import (
            load_security_command_preferred_destination_status,
            render_security_command_preferred_destination_section,
        )
        preferred_section = render_security_command_preferred_destination_section(
            load_security_command_preferred_destination_status()
        )
    except Exception as exc:
        preferred_section = f"""
        <section class="preferred-command-destination" data-pack="127-preferred-error">
          <h2>Preferred Security Command Destination Unavailable</h2>
          <p>{_html_escape(type(exc).__name__)}</p>
        </section>
        """

    try:
        from tower.security_inbox_owner_queue import (
            load_security_inbox_owner_queue,
            render_security_inbox_owner_queue_section,
        )
        inbox_section = render_security_inbox_owner_queue_section(load_security_inbox_owner_queue())
    except Exception as exc:
        inbox_section = f"""
        <section class="security-inbox-owner-queue" data-pack="127-inbox-error">
          <h2>Tower Security Inbox Unavailable</h2>
          <p>{_html_escape(type(exc).__name__)}</p>
        </section>
        """

    try:
        from tower.security_inbox_review_actions import (
            load_security_inbox_review_status,
            render_security_inbox_review_section,
        )
        review_section = render_security_inbox_review_section(load_security_inbox_review_status())
    except Exception as exc:
        review_section = f"""
        <section class="security-inbox-review-actions" data-pack="127-review-error">
          <h2>Security Inbox Review Actions Unavailable</h2>
          <p>{_html_escape(type(exc).__name__)}</p>
        </section>
        """

    try:
        from tower.security_inbox_filters_priorities import (
            load_security_inbox_filters_priorities_status,
            render_security_inbox_filters_priorities_section,
        )
        filters_section = render_security_inbox_filters_priorities_section(
            load_security_inbox_filters_priorities_status()
        )
    except Exception as exc:
        filters_section = f"""
        <section class="security-inbox-filters-priorities" data-pack="127-filters-error">
          <h2>Security Inbox Filters & Priorities Unavailable</h2>
          <p>{_html_escape(type(exc).__name__)}</p>
        </section>
        """

    try:
        from tower.security_incident_desk import (
            load_security_incident_desk_status,
            render_security_incident_desk_section,
        )
        incident_section = render_security_incident_desk_section(load_security_incident_desk_status())
    except Exception as exc:
        incident_section = f"""
        <section class="security-incident-desk" data-pack="127-incident-error">
          <h2>Tower Incident Desk Unavailable</h2>
          <p>{_html_escape(type(exc).__name__)}</p>
        </section>
        """

    try:
        from tower.security_command_navigation_links import (
            load_security_command_navigation_links_status,
            render_security_command_navigation_links_section,
        )
        nav_section = render_security_command_navigation_links_section(
            load_security_command_navigation_links_status()
        )
    except Exception as exc:
        nav_section = f"""
        <section class="tower-security-command-links" data-pack="127-nav-error">
          <h2>Security Command Links Unavailable</h2>
          <p>{_html_escape(type(exc).__name__)}</p>
        </section>
        """

    try:
        from tower.security_command_object_visibility_integration import (
            load_security_command_object_visibility_status,
            render_security_command_object_visibility_section,
        )
        object_section = render_security_command_object_visibility_section(
            load_security_command_object_visibility_status()
        )
    except Exception:
        try:
            from tower.security_command_page import pack113_security_command_object_visibility_html_section
            object_section = pack113_security_command_object_visibility_html_section()
        except Exception as exc:
            object_section = f"""
            <section class="tower-object-visibility-panel" data-pack="127-object-error">
              <h2>Object Visibility Unavailable</h2>
              <p>{_html_escape(type(exc).__name__)}</p>
            </section>
            """

    route_health = status.get("route_health", {}) if isinstance(status.get("route_health"), dict) else {}
    object_checkpoint = status.get("object_checkpoint", {}) if isinstance(status.get("object_checkpoint"), dict) else {}
    object_visibility = status.get("object_visibility", {}) if isinstance(status.get("object_visibility"), dict) else {}
    navigation = status.get("navigation", {}) if isinstance(status.get("navigation"), dict) else {}

    health_cards = "".join([
        _build_health_card("Route Coverage", f"{route_health.get('coverage_pct', 0)}%", "ROUTE WALL"),
        _build_health_card("Guarded Protected Routes", f"{route_health.get('guarded_needed_count', 0)} / {route_health.get('needs_guard_count', 0)}", "GUARDS"),
        _build_health_card("Helper Wraps", object_checkpoint.get("helper_wrapped_count", 0), "OBJECT CLEANUP"),
        _build_health_card("Object Events", object_visibility.get("event_count", 0), "OBJECT VISIBILITY"),
        _build_health_card("Security Links", navigation.get("link_count", 0), "NAVIGATION"),
        _build_health_card("Readiness", status.get("readiness_score", 0), "OWNER COMMAND"),
    ])

    html = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>The Tower · Unified Owner Security Command</title>
  <style>
    body {{
      margin: 0;
      min-height: 100vh;
      background:
        radial-gradient(circle at top left, rgba(220,183,94,.13), transparent 32%),
        radial-gradient(circle at bottom right, rgba(168,175,255,.10), transparent 35%),
        #080907;
      color: #f5ead2;
      font-family: Inter, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }}
    main {{ max-width: 1220px; margin: 0 auto; padding: 42px 22px 70px; }}
    .tower-owner-hero {{
      border: 1px solid rgba(220,183,94,.38);
      border-radius: 34px;
      padding: 32px;
      background: linear-gradient(135deg, rgba(75,48,18,.76), rgba(8,9,7,.94));
      box-shadow: 0 24px 90px rgba(0,0,0,.44);
      margin-bottom: 22px;
    }}
    .tower-owner-hero__eyebrow {{
      color: rgba(220,183,94,.88);
      text-transform: uppercase;
      letter-spacing: .16em;
      font-size: 11px;
      margin-bottom: 10px;
    }}
    .tower-owner-hero h1 {{ margin: 0 0 10px; font-size: 38px; letter-spacing: -.045em; }}
    .tower-owner-hero p {{ margin: 0; color: rgba(245,234,210,.76); line-height: 1.55; max-width: 880px; }}
    .tower-owner-health-grid {{
      display: grid;
      grid-template-columns: repeat(6, minmax(0, 1fr));
      gap: 12px;
      margin: 18px 0 0;
    }}
    .tower-owner-health-card {{
      border: 1px solid rgba(143,221,158,.26);
      border-radius: 20px;
      padding: 14px;
      background: rgba(255,255,255,.045);
    }}
    .tower-owner-health-card__eyebrow {{
      color: rgba(220,183,94,.8);
      text-transform: uppercase;
      letter-spacing: .12em;
      font-size: 10px;
      margin-bottom: 7px;
    }}
    .tower-owner-health-card h3 {{ margin: 0 0 6px; font-size: 22px; }}
    .tower-owner-health-card p {{ margin: 0; color: rgba(245,234,210,.63); font-size: 12px; }}
    .tower-owner-section {{ margin-top: 22px; }}
    @media (max-width: 1050px) {{ .tower-owner-health-grid {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }} }}
    @media (max-width: 720px) {{ .tower-owner-health-grid {{ grid-template-columns: 1fr; }} .tower-owner-hero h1 {{ font-size: 30px; }} }}
  </style>
</head>
<body>
<main>
  <!-- PACK116_UNIFIED_OWNER_SECURITY_COMMAND_PAGE -->
  <!-- PACK118B_SAFE_NON_RECURSIVE_RENDERER -->
  <!-- PACK119_UNIFIED_OWNER_PAGE_INCLUDES_QUICK_ACTION_RAIL -->
  <!-- PACK123_UNIFIED_OWNER_PAGE_INCLUDES_SECURITY_INBOX_AND_REVIEW -->
  <!-- PACK125_UNIFIED_OWNER_PAGE_INCLUDES_SECURITY_INBOX_FILTERS -->
  <!-- PACK127_UNIFIED_OWNER_PAGE_INCLUDES_INCIDENT_DESK -->
  <section class="tower-owner-hero" data-pack="116-127">
    <div class="tower-owner-hero__eyebrow">PACK 116 + 127 · UNIFIED OWNER COMMAND</div>
    <h1>The Tower Security Command</h1>
    <p>{_html_escape(status.get('human_reason', 'Unified Security Command loaded.'))}</p>
    <div class="tower-owner-health-grid">{health_cards}</div>
  </section>

  <section class="tower-owner-section">{quick_actions_section}</section>
  <section class="tower-owner-section">{preferred_section}</section>
  <section class="tower-owner-section">{inbox_section}</section>
  <section class="tower-owner-section">{review_section}</section>
  <section class="tower-owner-section">{filters_section}</section>
  <section class="tower-owner-section">{incident_section}</section>
  <section class="tower-owner-section">{nav_section}</section>
  <section class="tower-owner-section">{object_section}</section>
  <!-- END PACK127_UNIFIED_OWNER_PAGE_INCLUDES_INCIDENT_DESK -->
  <!-- END PACK125_UNIFIED_OWNER_PAGE_INCLUDES_SECURITY_INBOX_FILTERS -->
  <!-- END PACK123_UNIFIED_OWNER_PAGE_INCLUDES_SECURITY_INBOX_AND_REVIEW -->
  <!-- END PACK119_UNIFIED_OWNER_PAGE_INCLUDES_QUICK_ACTION_RAIL -->
  <!-- END PACK118B_SAFE_NON_RECURSIVE_RENDERER -->
  <!-- END PACK116_UNIFIED_OWNER_SECURITY_COMMAND_PAGE -->
</main>
</body>
</html>"""
    return html

# ================================================================================
# END PACK127_UNIFIED_OWNER_PAGE_WITH_INCIDENT_DESK
# ================================================================================



# ================================================================================
# PACK129_UNIFIED_OWNER_PAGE_WITH_INCIDENT_FILTERS_ESCALATION
# ================================================================================
# Override renderer to include Incident Filters & Escalation directly in the unified
# Security Command page.
# ================================================================================

def render_unified_owner_security_command_html(status: Dict[str, Any] | None = None) -> str:
    if not isinstance(status, dict):
        status = {
            "human_reason": "Unified Security Command loaded in safe render mode.",
            "readiness_score": 100,
            "route_health": {"coverage_pct": 100, "guarded_needed_count": "ready", "needs_guard_count": "ready"},
            "object_checkpoint": {"helper_wrapped_count": 0},
            "object_visibility": {"event_count": "ready"},
            "navigation": {"link_count": "ready"},
        }

    quick_actions_section = ""
    preferred_section = ""
    inbox_section = ""
    review_section = ""
    filters_section = ""
    incident_section = ""
    incident_filters_section = ""
    nav_section = ""
    object_section = ""

    try:
        from tower.security_command_owner_quick_actions import (
            load_owner_quick_actions_status,
            render_owner_quick_actions_section,
        )
        quick_actions_section = render_owner_quick_actions_section(load_owner_quick_actions_status())
    except Exception as exc:
        quick_actions_section = f"""
        <section class="owner-quick-action-rail" data-pack="129-quick-error">
          <h2>Owner Quick Actions Unavailable</h2>
          <p>{_html_escape(type(exc).__name__)}</p>
        </section>
        """

    try:
        from tower.security_command_preferred_destination import (
            load_security_command_preferred_destination_status,
            render_security_command_preferred_destination_section,
        )
        preferred_section = render_security_command_preferred_destination_section(
            load_security_command_preferred_destination_status()
        )
    except Exception as exc:
        preferred_section = f"""
        <section class="preferred-command-destination" data-pack="129-preferred-error">
          <h2>Preferred Security Command Destination Unavailable</h2>
          <p>{_html_escape(type(exc).__name__)}</p>
        </section>
        """

    try:
        from tower.security_inbox_owner_queue import (
            load_security_inbox_owner_queue,
            render_security_inbox_owner_queue_section,
        )
        inbox_section = render_security_inbox_owner_queue_section(load_security_inbox_owner_queue())
    except Exception as exc:
        inbox_section = f"""
        <section class="security-inbox-owner-queue" data-pack="129-inbox-error">
          <h2>Tower Security Inbox Unavailable</h2>
          <p>{_html_escape(type(exc).__name__)}</p>
        </section>
        """

    try:
        from tower.security_inbox_review_actions import (
            load_security_inbox_review_status,
            render_security_inbox_review_section,
        )
        review_section = render_security_inbox_review_section(load_security_inbox_review_status())
    except Exception as exc:
        review_section = f"""
        <section class="security-inbox-review-actions" data-pack="129-review-error">
          <h2>Security Inbox Review Actions Unavailable</h2>
          <p>{_html_escape(type(exc).__name__)}</p>
        </section>
        """

    try:
        from tower.security_inbox_filters_priorities import (
            load_security_inbox_filters_priorities_status,
            render_security_inbox_filters_priorities_section,
        )
        filters_section = render_security_inbox_filters_priorities_section(
            load_security_inbox_filters_priorities_status()
        )
    except Exception as exc:
        filters_section = f"""
        <section class="security-inbox-filters-priorities" data-pack="129-filters-error">
          <h2>Security Inbox Filters & Priorities Unavailable</h2>
          <p>{_html_escape(type(exc).__name__)}</p>
        </section>
        """

    try:
        from tower.security_incident_desk import (
            load_security_incident_desk_status,
            render_security_incident_desk_section,
        )
        incident_section = render_security_incident_desk_section(load_security_incident_desk_status())
    except Exception as exc:
        incident_section = f"""
        <section class="security-incident-desk" data-pack="129-incident-error">
          <h2>Tower Incident Desk Unavailable</h2>
          <p>{_html_escape(type(exc).__name__)}</p>
        </section>
        """

    try:
        from tower.security_incident_filters_escalation import (
            load_security_incident_filters_escalation_status,
            render_security_incident_filters_escalation_section,
        )
        incident_filters_section = render_security_incident_filters_escalation_section(
            load_security_incident_filters_escalation_status()
        )
    except Exception as exc:
        incident_filters_section = f"""
        <section class="security-incident-filters-escalation" data-pack="129-incident-filters-error">
          <h2>Incident Filters & Escalation Unavailable</h2>
          <p>{_html_escape(type(exc).__name__)}</p>
        </section>
        """

    try:
        from tower.security_command_navigation_links import (
            load_security_command_navigation_links_status,
            render_security_command_navigation_links_section,
        )
        nav_section = render_security_command_navigation_links_section(
            load_security_command_navigation_links_status()
        )
    except Exception as exc:
        nav_section = f"""
        <section class="tower-security-command-links" data-pack="129-nav-error">
          <h2>Security Command Links Unavailable</h2>
          <p>{_html_escape(type(exc).__name__)}</p>
        </section>
        """

    try:
        from tower.security_command_object_visibility_integration import (
            load_security_command_object_visibility_status,
            render_security_command_object_visibility_section,
        )
        object_section = render_security_command_object_visibility_section(
            load_security_command_object_visibility_status()
        )
    except Exception:
        try:
            from tower.security_command_page import pack113_security_command_object_visibility_html_section
            object_section = pack113_security_command_object_visibility_html_section()
        except Exception as exc:
            object_section = f"""
            <section class="tower-object-visibility-panel" data-pack="129-object-error">
              <h2>Object Visibility Unavailable</h2>
              <p>{_html_escape(type(exc).__name__)}</p>
            </section>
            """

    route_health = status.get("route_health", {}) if isinstance(status.get("route_health"), dict) else {}
    object_checkpoint = status.get("object_checkpoint", {}) if isinstance(status.get("object_checkpoint"), dict) else {}
    object_visibility = status.get("object_visibility", {}) if isinstance(status.get("object_visibility"), dict) else {}
    navigation = status.get("navigation", {}) if isinstance(status.get("navigation"), dict) else {}

    health_cards = "".join([
        _build_health_card("Route Coverage", f"{route_health.get('coverage_pct', 0)}%", "ROUTE WALL"),
        _build_health_card("Guarded Protected Routes", f"{route_health.get('guarded_needed_count', 0)} / {route_health.get('needs_guard_count', 0)}", "GUARDS"),
        _build_health_card("Helper Wraps", object_checkpoint.get("helper_wrapped_count", 0), "OBJECT CLEANUP"),
        _build_health_card("Object Events", object_visibility.get("event_count", 0), "OBJECT VISIBILITY"),
        _build_health_card("Security Links", navigation.get("link_count", 0), "NAVIGATION"),
        _build_health_card("Readiness", status.get("readiness_score", 0), "OWNER COMMAND"),
    ])

    html = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>The Tower · Unified Owner Security Command</title>
  <style>
    body {{
      margin: 0;
      min-height: 100vh;
      background:
        radial-gradient(circle at top left, rgba(220,183,94,.13), transparent 32%),
        radial-gradient(circle at bottom right, rgba(168,175,255,.10), transparent 35%),
        #080907;
      color: #f5ead2;
      font-family: Inter, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }}
    main {{ max-width: 1220px; margin: 0 auto; padding: 42px 22px 70px; }}
    .tower-owner-hero {{
      border: 1px solid rgba(220,183,94,.38);
      border-radius: 34px;
      padding: 32px;
      background: linear-gradient(135deg, rgba(75,48,18,.76), rgba(8,9,7,.94));
      box-shadow: 0 24px 90px rgba(0,0,0,.44);
      margin-bottom: 22px;
    }}
    .tower-owner-hero__eyebrow {{
      color: rgba(220,183,94,.88);
      text-transform: uppercase;
      letter-spacing: .16em;
      font-size: 11px;
      margin-bottom: 10px;
    }}
    .tower-owner-hero h1 {{ margin: 0 0 10px; font-size: 38px; letter-spacing: -.045em; }}
    .tower-owner-hero p {{ margin: 0; color: rgba(245,234,210,.76); line-height: 1.55; max-width: 880px; }}
    .tower-owner-health-grid {{
      display: grid;
      grid-template-columns: repeat(6, minmax(0, 1fr));
      gap: 12px;
      margin: 18px 0 0;
    }}
    .tower-owner-health-card {{
      border: 1px solid rgba(143,221,158,.26);
      border-radius: 20px;
      padding: 14px;
      background: rgba(255,255,255,.045);
    }}
    .tower-owner-health-card__eyebrow {{
      color: rgba(220,183,94,.8);
      text-transform: uppercase;
      letter-spacing: .12em;
      font-size: 10px;
      margin-bottom: 7px;
    }}
    .tower-owner-health-card h3 {{ margin: 0 0 6px; font-size: 22px; }}
    .tower-owner-health-card p {{ margin: 0; color: rgba(245,234,210,.63); font-size: 12px; }}
    .tower-owner-section {{ margin-top: 22px; }}
    @media (max-width: 1050px) {{ .tower-owner-health-grid {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }} }}
    @media (max-width: 720px) {{ .tower-owner-health-grid {{ grid-template-columns: 1fr; }} .tower-owner-hero h1 {{ font-size: 30px; }} }}
  </style>
</head>
<body>
<main>
  <!-- PACK116_UNIFIED_OWNER_SECURITY_COMMAND_PAGE -->
  <!-- PACK118B_SAFE_NON_RECURSIVE_RENDERER -->
  <!-- PACK119_UNIFIED_OWNER_PAGE_INCLUDES_QUICK_ACTION_RAIL -->
  <!-- PACK123_UNIFIED_OWNER_PAGE_INCLUDES_SECURITY_INBOX_AND_REVIEW -->
  <!-- PACK125_UNIFIED_OWNER_PAGE_INCLUDES_SECURITY_INBOX_FILTERS -->
  <!-- PACK127_UNIFIED_OWNER_PAGE_INCLUDES_INCIDENT_DESK -->
  <!-- PACK129_UNIFIED_OWNER_PAGE_INCLUDES_INCIDENT_FILTERS_ESCALATION -->
  <section class="tower-owner-hero" data-pack="116-129">
    <div class="tower-owner-hero__eyebrow">PACK 116 + 129 · UNIFIED OWNER COMMAND</div>
    <h1>The Tower Security Command</h1>
    <p>{_html_escape(status.get('human_reason', 'Unified Security Command loaded.'))}</p>
    <div class="tower-owner-health-grid">{health_cards}</div>
  </section>

  <section class="tower-owner-section">{quick_actions_section}</section>
  <section class="tower-owner-section">{preferred_section}</section>
  <section class="tower-owner-section">{inbox_section}</section>
  <section class="tower-owner-section">{review_section}</section>
  <section class="tower-owner-section">{filters_section}</section>
  <section class="tower-owner-section">{incident_section}</section>
  <section class="tower-owner-section">{incident_filters_section}</section>
  <section class="tower-owner-section">{nav_section}</section>
  <section class="tower-owner-section">{object_section}</section>
  <!-- END PACK129_UNIFIED_OWNER_PAGE_INCLUDES_INCIDENT_FILTERS_ESCALATION -->
  <!-- END PACK127_UNIFIED_OWNER_PAGE_INCLUDES_INCIDENT_DESK -->
  <!-- END PACK125_UNIFIED_OWNER_PAGE_INCLUDES_SECURITY_INBOX_FILTERS -->
  <!-- END PACK123_UNIFIED_OWNER_PAGE_INCLUDES_SECURITY_INBOX_AND_REVIEW -->
  <!-- END PACK119_UNIFIED_OWNER_PAGE_INCLUDES_QUICK_ACTION_RAIL -->
  <!-- END PACK118B_SAFE_NON_RECURSIVE_RENDERER -->
  <!-- END PACK116_UNIFIED_OWNER_SECURITY_COMMAND_PAGE -->
</main>
</body>
</html>"""
    return html

# ================================================================================
# END PACK129_UNIFIED_OWNER_PAGE_WITH_INCIDENT_FILTERS_ESCALATION
# ================================================================================



# ================================================================================
# PACK132_UNIFIED_OWNER_PAGE_WITH_SECURITY_WATCH
# ================================================================================
# Override renderer to include Security Watch directly in the unified Security
# Command page near the top.
# ================================================================================

def render_unified_owner_security_command_html(status: Dict[str, Any] | None = None) -> str:
    if not isinstance(status, dict):
        status = {
            "human_reason": "Unified Security Command loaded in safe render mode.",
            "readiness_score": 100,
            "route_health": {"coverage_pct": 100, "guarded_needed_count": "ready", "needs_guard_count": "ready"},
            "object_checkpoint": {"helper_wrapped_count": 0},
            "object_visibility": {"event_count": "ready"},
            "navigation": {"link_count": "ready"},
        }

    security_watch_section = ""
    quick_actions_section = ""
    preferred_section = ""
    inbox_section = ""
    review_section = ""
    filters_section = ""
    incident_section = ""
    incident_filters_section = ""
    nav_section = ""
    object_section = ""

    try:
        from tower.security_watch_owner_posture import (
            load_security_watch_owner_posture,
            render_security_watch_owner_posture_section,
        )
        security_watch_section = render_security_watch_owner_posture_section(
            load_security_watch_owner_posture()
        )
    except Exception as exc:
        security_watch_section = f"""
        <section class="security-watch-owner-posture" data-pack="132-watch-error">
          <h2>Tower Security Watch Unavailable</h2>
          <p>{_html_escape(type(exc).__name__)}</p>
        </section>
        """

    try:
        from tower.security_command_owner_quick_actions import (
            load_owner_quick_actions_status,
            render_owner_quick_actions_section,
        )
        quick_actions_section = render_owner_quick_actions_section(load_owner_quick_actions_status())
    except Exception as exc:
        quick_actions_section = f"""
        <section class="owner-quick-action-rail" data-pack="132-quick-error">
          <h2>Owner Quick Actions Unavailable</h2>
          <p>{_html_escape(type(exc).__name__)}</p>
        </section>
        """

    try:
        from tower.security_command_preferred_destination import (
            load_security_command_preferred_destination_status,
            render_security_command_preferred_destination_section,
        )
        preferred_section = render_security_command_preferred_destination_section(
            load_security_command_preferred_destination_status()
        )
    except Exception as exc:
        preferred_section = f"""
        <section class="preferred-command-destination" data-pack="132-preferred-error">
          <h2>Preferred Security Command Destination Unavailable</h2>
          <p>{_html_escape(type(exc).__name__)}</p>
        </section>
        """

    try:
        from tower.security_inbox_owner_queue import (
            load_security_inbox_owner_queue,
            render_security_inbox_owner_queue_section,
        )
        inbox_section = render_security_inbox_owner_queue_section(load_security_inbox_owner_queue())
    except Exception as exc:
        inbox_section = f"""
        <section class="security-inbox-owner-queue" data-pack="132-inbox-error">
          <h2>Tower Security Inbox Unavailable</h2>
          <p>{_html_escape(type(exc).__name__)}</p>
        </section>
        """

    try:
        from tower.security_inbox_review_actions import (
            load_security_inbox_review_status,
            render_security_inbox_review_section,
        )
        review_section = render_security_inbox_review_section(load_security_inbox_review_status())
    except Exception as exc:
        review_section = f"""
        <section class="security-inbox-review-actions" data-pack="132-review-error">
          <h2>Security Inbox Review Actions Unavailable</h2>
          <p>{_html_escape(type(exc).__name__)}</p>
        </section>
        """

    try:
        from tower.security_inbox_filters_priorities import (
            load_security_inbox_filters_priorities_status,
            render_security_inbox_filters_priorities_section,
        )
        filters_section = render_security_inbox_filters_priorities_section(
            load_security_inbox_filters_priorities_status()
        )
    except Exception as exc:
        filters_section = f"""
        <section class="security-inbox-filters-priorities" data-pack="132-filters-error">
          <h2>Security Inbox Filters & Priorities Unavailable</h2>
          <p>{_html_escape(type(exc).__name__)}</p>
        </section>
        """

    try:
        from tower.security_incident_desk import (
            load_security_incident_desk_status,
            render_security_incident_desk_section,
        )
        incident_section = render_security_incident_desk_section(load_security_incident_desk_status())
    except Exception as exc:
        incident_section = f"""
        <section class="security-incident-desk" data-pack="132-incident-error">
          <h2>Tower Incident Desk Unavailable</h2>
          <p>{_html_escape(type(exc).__name__)}</p>
        </section>
        """

    try:
        from tower.security_incident_filters_escalation import (
            load_security_incident_filters_escalation_status,
            render_security_incident_filters_escalation_section,
        )
        incident_filters_section = render_security_incident_filters_escalation_section(
            load_security_incident_filters_escalation_status()
        )
    except Exception as exc:
        incident_filters_section = f"""
        <section class="security-incident-filters-escalation" data-pack="132-incident-filters-error">
          <h2>Incident Filters & Escalation Unavailable</h2>
          <p>{_html_escape(type(exc).__name__)}</p>
        </section>
        """

    try:
        from tower.security_command_navigation_links import (
            load_security_command_navigation_links_status,
            render_security_command_navigation_links_section,
        )
        nav_section = render_security_command_navigation_links_section(
            load_security_command_navigation_links_status()
        )
    except Exception as exc:
        nav_section = f"""
        <section class="tower-security-command-links" data-pack="132-nav-error">
          <h2>Security Command Links Unavailable</h2>
          <p>{_html_escape(type(exc).__name__)}</p>
        </section>
        """

    try:
        from tower.security_command_object_visibility_integration import (
            load_security_command_object_visibility_status,
            render_security_command_object_visibility_section,
        )
        object_section = render_security_command_object_visibility_section(
            load_security_command_object_visibility_status()
        )
    except Exception:
        try:
            from tower.security_command_page import pack113_security_command_object_visibility_html_section
            object_section = pack113_security_command_object_visibility_html_section()
        except Exception as exc:
            object_section = f"""
            <section class="tower-object-visibility-panel" data-pack="132-object-error">
              <h2>Object Visibility Unavailable</h2>
              <p>{_html_escape(type(exc).__name__)}</p>
            </section>
            """

    route_health = status.get("route_health", {}) if isinstance(status.get("route_health"), dict) else {}
    object_checkpoint = status.get("object_checkpoint", {}) if isinstance(status.get("object_checkpoint"), dict) else {}
    object_visibility = status.get("object_visibility", {}) if isinstance(status.get("object_visibility"), dict) else {}
    navigation = status.get("navigation", {}) if isinstance(status.get("navigation"), dict) else {}

    health_cards = "".join([
        _build_health_card("Route Coverage", f"{route_health.get('coverage_pct', 0)}%", "ROUTE WALL"),
        _build_health_card("Guarded Protected Routes", f"{route_health.get('guarded_needed_count', 0)} / {route_health.get('needs_guard_count', 0)}", "GUARDS"),
        _build_health_card("Helper Wraps", object_checkpoint.get("helper_wrapped_count", 0), "OBJECT CLEANUP"),
        _build_health_card("Object Events", object_visibility.get("event_count", 0), "OBJECT VISIBILITY"),
        _build_health_card("Security Links", navigation.get("link_count", 0), "NAVIGATION"),
        _build_health_card("Readiness", status.get("readiness_score", 0), "OWNER COMMAND"),
    ])

    html = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>The Tower · Unified Owner Security Command</title>
  <style>
    body {{
      margin: 0;
      min-height: 100vh;
      background:
        radial-gradient(circle at top left, rgba(220,183,94,.13), transparent 32%),
        radial-gradient(circle at bottom right, rgba(168,175,255,.10), transparent 35%),
        #080907;
      color: #f5ead2;
      font-family: Inter, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }}
    main {{ max-width: 1220px; margin: 0 auto; padding: 42px 22px 70px; }}
    .tower-owner-hero {{
      border: 1px solid rgba(220,183,94,.38);
      border-radius: 34px;
      padding: 32px;
      background: linear-gradient(135deg, rgba(75,48,18,.76), rgba(8,9,7,.94));
      box-shadow: 0 24px 90px rgba(0,0,0,.44);
      margin-bottom: 22px;
    }}
    .tower-owner-hero__eyebrow {{
      color: rgba(220,183,94,.88);
      text-transform: uppercase;
      letter-spacing: .16em;
      font-size: 11px;
      margin-bottom: 10px;
    }}
    .tower-owner-hero h1 {{ margin: 0 0 10px; font-size: 38px; letter-spacing: -.045em; }}
    .tower-owner-hero p {{ margin: 0; color: rgba(245,234,210,.76); line-height: 1.55; max-width: 880px; }}
    .tower-owner-health-grid {{
      display: grid;
      grid-template-columns: repeat(6, minmax(0, 1fr));
      gap: 12px;
      margin: 18px 0 0;
    }}
    .tower-owner-health-card {{
      border: 1px solid rgba(143,221,158,.26);
      border-radius: 20px;
      padding: 14px;
      background: rgba(255,255,255,.045);
    }}
    .tower-owner-health-card__eyebrow {{
      color: rgba(220,183,94,.8);
      text-transform: uppercase;
      letter-spacing: .12em;
      font-size: 10px;
      margin-bottom: 7px;
    }}
    .tower-owner-health-card h3 {{ margin: 0 0 6px; font-size: 22px; }}
    .tower-owner-health-card p {{ margin: 0; color: rgba(245,234,210,.63); font-size: 12px; }}
    .tower-owner-section {{ margin-top: 22px; }}
    @media (max-width: 1050px) {{ .tower-owner-health-grid {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }} }}
    @media (max-width: 720px) {{ .tower-owner-health-grid {{ grid-template-columns: 1fr; }} .tower-owner-hero h1 {{ font-size: 30px; }} }}
  </style>
</head>
<body>
<main>
  <!-- PACK116_UNIFIED_OWNER_SECURITY_COMMAND_PAGE -->
  <!-- PACK118B_SAFE_NON_RECURSIVE_RENDERER -->
  <!-- PACK119_UNIFIED_OWNER_PAGE_INCLUDES_QUICK_ACTION_RAIL -->
  <!-- PACK123_UNIFIED_OWNER_PAGE_INCLUDES_SECURITY_INBOX_AND_REVIEW -->
  <!-- PACK125_UNIFIED_OWNER_PAGE_INCLUDES_SECURITY_INBOX_FILTERS -->
  <!-- PACK127_UNIFIED_OWNER_PAGE_INCLUDES_INCIDENT_DESK -->
  <!-- PACK129_UNIFIED_OWNER_PAGE_INCLUDES_INCIDENT_FILTERS_ESCALATION -->
  <!-- PACK132_UNIFIED_OWNER_PAGE_INCLUDES_SECURITY_WATCH -->
  <section class="tower-owner-hero" data-pack="116-132">
    <div class="tower-owner-hero__eyebrow">PACK 116 + 132 · UNIFIED OWNER COMMAND</div>
    <h1>The Tower Security Command</h1>
    <p>{_html_escape(status.get('human_reason', 'Unified Security Command loaded.'))}</p>
    <div class="tower-owner-health-grid">{health_cards}</div>
  </section>

  <section class="tower-owner-section">{security_watch_section}</section>
  <section class="tower-owner-section">{quick_actions_section}</section>
  <section class="tower-owner-section">{preferred_section}</section>
  <section class="tower-owner-section">{inbox_section}</section>
  <section class="tower-owner-section">{review_section}</section>
  <section class="tower-owner-section">{filters_section}</section>
  <section class="tower-owner-section">{incident_section}</section>
  <section class="tower-owner-section">{incident_filters_section}</section>
  <section class="tower-owner-section">{nav_section}</section>
  <section class="tower-owner-section">{object_section}</section>
  <!-- END PACK132_UNIFIED_OWNER_PAGE_INCLUDES_SECURITY_WATCH -->
  <!-- END PACK129_UNIFIED_OWNER_PAGE_INCLUDES_INCIDENT_FILTERS_ESCALATION -->
  <!-- END PACK127_UNIFIED_OWNER_PAGE_INCLUDES_INCIDENT_DESK -->
  <!-- END PACK125_UNIFIED_OWNER_PAGE_INCLUDES_SECURITY_INBOX_FILTERS -->
  <!-- END PACK123_UNIFIED_OWNER_PAGE_INCLUDES_SECURITY_INBOX_AND_REVIEW -->
  <!-- END PACK119_UNIFIED_OWNER_PAGE_INCLUDES_QUICK_ACTION_RAIL -->
  <!-- END PACK118B_SAFE_NON_RECURSIVE_RENDERER -->
  <!-- END PACK116_UNIFIED_OWNER_SECURITY_COMMAND_PAGE -->
</main>
</body>
</html>"""
    return html

# ================================================================================
# END PACK132_UNIFIED_OWNER_PAGE_WITH_SECURITY_WATCH
# ================================================================================



# ================================================================================
# PACK134_UNIFIED_OWNER_PAGE_WITH_SECURITY_WATCH_CHECKPOINT
# ================================================================================
# Override renderer to include Security Watch and Security Watch Checkpoint directly
# in the unified Security Command page.
# ================================================================================

def render_unified_owner_security_command_html(status: Dict[str, Any] | None = None) -> str:
    if not isinstance(status, dict):
        status = {
            "human_reason": "Unified Security Command loaded in safe render mode.",
            "readiness_score": 100,
            "route_health": {"coverage_pct": 100, "guarded_needed_count": "ready", "needs_guard_count": "ready"},
            "object_checkpoint": {"helper_wrapped_count": 0},
            "object_visibility": {"event_count": "ready"},
            "navigation": {"link_count": "ready"},
        }

    security_watch_section = ""
    security_watch_checkpoint_section = ""
    quick_actions_section = ""
    preferred_section = ""
    inbox_section = ""
    review_section = ""
    filters_section = ""
    incident_section = ""
    incident_filters_section = ""
    nav_section = ""
    object_section = ""

    try:
        from tower.security_watch_owner_posture import (
            load_security_watch_owner_posture,
            render_security_watch_owner_posture_section,
        )
        security_watch_section = render_security_watch_owner_posture_section(
            load_security_watch_owner_posture()
        )
    except Exception as exc:
        security_watch_section = f"""
        <section class="security-watch-owner-posture" data-pack="134-watch-error">
          <h2>Tower Security Watch Unavailable</h2>
          <p>{_html_escape(type(exc).__name__)}</p>
        </section>
        """

    try:
        from tower.security_watch_checkpoint import (
            load_security_watch_checkpoint,
            render_security_watch_checkpoint_section,
        )
        security_watch_checkpoint_section = render_security_watch_checkpoint_section(
            load_security_watch_checkpoint()
        )
    except Exception as exc:
        security_watch_checkpoint_section = f"""
        <section class="security-watch-checkpoint" data-pack="134-watch-checkpoint-error">
          <h2>Security Watch Checkpoint Unavailable</h2>
          <p>{_html_escape(type(exc).__name__)}</p>
        </section>
        """

    try:
        from tower.security_command_owner_quick_actions import (
            load_owner_quick_actions_status,
            render_owner_quick_actions_section,
        )
        quick_actions_section = render_owner_quick_actions_section(load_owner_quick_actions_status())
    except Exception as exc:
        quick_actions_section = f"""
        <section class="owner-quick-action-rail" data-pack="134-quick-error">
          <h2>Owner Quick Actions Unavailable</h2>
          <p>{_html_escape(type(exc).__name__)}</p>
        </section>
        """

    try:
        from tower.security_command_preferred_destination import (
            load_security_command_preferred_destination_status,
            render_security_command_preferred_destination_section,
        )
        preferred_section = render_security_command_preferred_destination_section(
            load_security_command_preferred_destination_status()
        )
    except Exception as exc:
        preferred_section = f"""
        <section class="preferred-command-destination" data-pack="134-preferred-error">
          <h2>Preferred Security Command Destination Unavailable</h2>
          <p>{_html_escape(type(exc).__name__)}</p>
        </section>
        """

    try:
        from tower.security_inbox_owner_queue import (
            load_security_inbox_owner_queue,
            render_security_inbox_owner_queue_section,
        )
        inbox_section = render_security_inbox_owner_queue_section(load_security_inbox_owner_queue())
    except Exception as exc:
        inbox_section = f"""
        <section class="security-inbox-owner-queue" data-pack="134-inbox-error">
          <h2>Tower Security Inbox Unavailable</h2>
          <p>{_html_escape(type(exc).__name__)}</p>
        </section>
        """

    try:
        from tower.security_inbox_review_actions import (
            load_security_inbox_review_status,
            render_security_inbox_review_section,
        )
        review_section = render_security_inbox_review_section(load_security_inbox_review_status())
    except Exception as exc:
        review_section = f"""
        <section class="security-inbox-review-actions" data-pack="134-review-error">
          <h2>Security Inbox Review Actions Unavailable</h2>
          <p>{_html_escape(type(exc).__name__)}</p>
        </section>
        """

    try:
        from tower.security_inbox_filters_priorities import (
            load_security_inbox_filters_priorities_status,
            render_security_inbox_filters_priorities_section,
        )
        filters_section = render_security_inbox_filters_priorities_section(
            load_security_inbox_filters_priorities_status()
        )
    except Exception as exc:
        filters_section = f"""
        <section class="security-inbox-filters-priorities" data-pack="134-filters-error">
          <h2>Security Inbox Filters & Priorities Unavailable</h2>
          <p>{_html_escape(type(exc).__name__)}</p>
        </section>
        """

    try:
        from tower.security_incident_desk import (
            load_security_incident_desk_status,
            render_security_incident_desk_section,
        )
        incident_section = render_security_incident_desk_section(load_security_incident_desk_status())
    except Exception as exc:
        incident_section = f"""
        <section class="security-incident-desk" data-pack="134-incident-error">
          <h2>Tower Incident Desk Unavailable</h2>
          <p>{_html_escape(type(exc).__name__)}</p>
        </section>
        """

    try:
        from tower.security_incident_filters_escalation import (
            load_security_incident_filters_escalation_status,
            render_security_incident_filters_escalation_section,
        )
        incident_filters_section = render_security_incident_filters_escalation_section(
            load_security_incident_filters_escalation_status()
        )
    except Exception as exc:
        incident_filters_section = f"""
        <section class="security-incident-filters-escalation" data-pack="134-incident-filters-error">
          <h2>Incident Filters & Escalation Unavailable</h2>
          <p>{_html_escape(type(exc).__name__)}</p>
        </section>
        """

    try:
        from tower.security_command_navigation_links import (
            load_security_command_navigation_links_status,
            render_security_command_navigation_links_section,
        )
        nav_section = render_security_command_navigation_links_section(
            load_security_command_navigation_links_status()
        )
    except Exception as exc:
        nav_section = f"""
        <section class="tower-security-command-links" data-pack="134-nav-error">
          <h2>Security Command Links Unavailable</h2>
          <p>{_html_escape(type(exc).__name__)}</p>
        </section>
        """

    try:
        from tower.security_command_object_visibility_integration import (
            load_security_command_object_visibility_status,
            render_security_command_object_visibility_section,
        )
        object_section = render_security_command_object_visibility_section(
            load_security_command_object_visibility_status()
        )
    except Exception:
        try:
            from tower.security_command_page import pack113_security_command_object_visibility_html_section
            object_section = pack113_security_command_object_visibility_html_section()
        except Exception as exc:
            object_section = f"""
            <section class="tower-object-visibility-panel" data-pack="134-object-error">
              <h2>Object Visibility Unavailable</h2>
              <p>{_html_escape(type(exc).__name__)}</p>
            </section>
            """

    route_health = status.get("route_health", {}) if isinstance(status.get("route_health"), dict) else {}
    object_checkpoint = status.get("object_checkpoint", {}) if isinstance(status.get("object_checkpoint"), dict) else {}
    object_visibility = status.get("object_visibility", {}) if isinstance(status.get("object_visibility"), dict) else {}
    navigation = status.get("navigation", {}) if isinstance(status.get("navigation"), dict) else {}

    health_cards = "".join([
        _build_health_card("Route Coverage", f"{route_health.get('coverage_pct', 0)}%", "ROUTE WALL"),
        _build_health_card("Guarded Protected Routes", f"{route_health.get('guarded_needed_count', 0)} / {route_health.get('needs_guard_count', 0)}", "GUARDS"),
        _build_health_card("Helper Wraps", object_checkpoint.get("helper_wrapped_count", 0), "OBJECT CLEANUP"),
        _build_health_card("Object Events", object_visibility.get("event_count", 0), "OBJECT VISIBILITY"),
        _build_health_card("Security Links", navigation.get("link_count", 0), "NAVIGATION"),
        _build_health_card("Readiness", status.get("readiness_score", 0), "OWNER COMMAND"),
    ])

    html = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>The Tower · Unified Owner Security Command</title>
  <style>
    body {{
      margin: 0;
      min-height: 100vh;
      background:
        radial-gradient(circle at top left, rgba(220,183,94,.13), transparent 32%),
        radial-gradient(circle at bottom right, rgba(168,175,255,.10), transparent 35%),
        #080907;
      color: #f5ead2;
      font-family: Inter, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }}
    main {{ max-width: 1220px; margin: 0 auto; padding: 42px 22px 70px; }}
    .tower-owner-hero {{
      border: 1px solid rgba(220,183,94,.38);
      border-radius: 34px;
      padding: 32px;
      background: linear-gradient(135deg, rgba(75,48,18,.76), rgba(8,9,7,.94));
      box-shadow: 0 24px 90px rgba(0,0,0,.44);
      margin-bottom: 22px;
    }}
    .tower-owner-hero__eyebrow {{
      color: rgba(220,183,94,.88);
      text-transform: uppercase;
      letter-spacing: .16em;
      font-size: 11px;
      margin-bottom: 10px;
    }}
    .tower-owner-hero h1 {{ margin: 0 0 10px; font-size: 38px; letter-spacing: -.045em; }}
    .tower-owner-hero p {{ margin: 0; color: rgba(245,234,210,.76); line-height: 1.55; max-width: 880px; }}
    .tower-owner-health-grid {{
      display: grid;
      grid-template-columns: repeat(6, minmax(0, 1fr));
      gap: 12px;
      margin: 18px 0 0;
    }}
    .tower-owner-health-card {{
      border: 1px solid rgba(143,221,158,.26);
      border-radius: 20px;
      padding: 14px;
      background: rgba(255,255,255,.045);
    }}
    .tower-owner-health-card__eyebrow {{
      color: rgba(220,183,94,.8);
      text-transform: uppercase;
      letter-spacing: .12em;
      font-size: 10px;
      margin-bottom: 7px;
    }}
    .tower-owner-health-card h3 {{ margin: 0 0 6px; font-size: 22px; }}
    .tower-owner-health-card p {{ margin: 0; color: rgba(245,234,210,.63); font-size: 12px; }}
    .tower-owner-section {{ margin-top: 22px; }}
    @media (max-width: 1050px) {{ .tower-owner-health-grid {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }} }}
    @media (max-width: 720px) {{ .tower-owner-health-grid {{ grid-template-columns: 1fr; }} .tower-owner-hero h1 {{ font-size: 30px; }} }}
  </style>
</head>
<body>
<main>
  <!-- PACK116_UNIFIED_OWNER_SECURITY_COMMAND_PAGE -->
  <!-- PACK118B_SAFE_NON_RECURSIVE_RENDERER -->
  <!-- PACK119_UNIFIED_OWNER_PAGE_INCLUDES_QUICK_ACTION_RAIL -->
  <!-- PACK123_UNIFIED_OWNER_PAGE_INCLUDES_SECURITY_INBOX_AND_REVIEW -->
  <!-- PACK125_UNIFIED_OWNER_PAGE_INCLUDES_SECURITY_INBOX_FILTERS -->
  <!-- PACK127_UNIFIED_OWNER_PAGE_INCLUDES_INCIDENT_DESK -->
  <!-- PACK129_UNIFIED_OWNER_PAGE_INCLUDES_INCIDENT_FILTERS_ESCALATION -->
  <!-- PACK132_UNIFIED_OWNER_PAGE_INCLUDES_SECURITY_WATCH -->
  <!-- PACK134_UNIFIED_OWNER_PAGE_INCLUDES_SECURITY_WATCH_CHECKPOINT -->
  <section class="tower-owner-hero" data-pack="116-134">
    <div class="tower-owner-hero__eyebrow">PACK 116 + 134 · UNIFIED OWNER COMMAND</div>
    <h1>The Tower Security Command</h1>
    <p>{_html_escape(status.get('human_reason', 'Unified Security Command loaded.'))}</p>
    <div class="tower-owner-health-grid">{health_cards}</div>
  </section>

  <section class="tower-owner-section">{security_watch_section}</section>
  <section class="tower-owner-section">{security_watch_checkpoint_section}</section>
  <section class="tower-owner-section">{quick_actions_section}</section>
  <section class="tower-owner-section">{preferred_section}</section>
  <section class="tower-owner-section">{inbox_section}</section>
  <section class="tower-owner-section">{review_section}</section>
  <section class="tower-owner-section">{filters_section}</section>
  <section class="tower-owner-section">{incident_section}</section>
  <section class="tower-owner-section">{incident_filters_section}</section>
  <section class="tower-owner-section">{nav_section}</section>
  <section class="tower-owner-section">{object_section}</section>
  <!-- END PACK134_UNIFIED_OWNER_PAGE_INCLUDES_SECURITY_WATCH_CHECKPOINT -->
  <!-- END PACK132_UNIFIED_OWNER_PAGE_INCLUDES_SECURITY_WATCH -->
  <!-- END PACK129_UNIFIED_OWNER_PAGE_INCLUDES_INCIDENT_FILTERS_ESCALATION -->
  <!-- END PACK127_UNIFIED_OWNER_PAGE_INCLUDES_INCIDENT_DESK -->
  <!-- END PACK125_UNIFIED_OWNER_PAGE_INCLUDES_SECURITY_INBOX_FILTERS -->
  <!-- END PACK123_UNIFIED_OWNER_PAGE_INCLUDES_SECURITY_INBOX_AND_REVIEW -->
  <!-- END PACK119_UNIFIED_OWNER_PAGE_INCLUDES_QUICK_ACTION_RAIL -->
  <!-- END PACK118B_SAFE_NON_RECURSIVE_RENDERER -->
  <!-- END PACK116_UNIFIED_OWNER_SECURITY_COMMAND_PAGE -->
</main>
</body>
</html>"""
    return html

# ================================================================================
# END PACK134_UNIFIED_OWNER_PAGE_WITH_SECURITY_WATCH_CHECKPOINT
# ================================================================================



# ================================================================================
# PACK136_UNIFIED_OWNER_PAGE_WITH_OWNER_ACTION_CENTER
# ================================================================================
# Override renderer to include Owner Action Center near the top of unified Security
# Command, above Security Watch / checkpoints.
# ================================================================================

def render_unified_owner_security_command_html(status: Dict[str, Any] | None = None) -> str:
    if not isinstance(status, dict):
        status = {
            "human_reason": "Unified Security Command loaded in safe render mode.",
            "readiness_score": 100,
            "route_health": {"coverage_pct": 100, "guarded_needed_count": "ready", "needs_guard_count": "ready"},
            "object_checkpoint": {"helper_wrapped_count": 0},
            "object_visibility": {"event_count": "ready"},
            "navigation": {"link_count": "ready"},
        }

    owner_action_center_section = ""
    security_watch_section = ""
    security_watch_checkpoint_section = ""
    quick_actions_section = ""
    preferred_section = ""
    inbox_section = ""
    review_section = ""
    filters_section = ""
    incident_section = ""
    incident_filters_section = ""
    nav_section = ""
    object_section = ""

    try:
        from tower.owner_action_center import (
            load_owner_action_center_status,
            render_owner_action_center_section,
        )
        owner_action_center_section = render_owner_action_center_section(
            load_owner_action_center_status()
        )
    except Exception as exc:
        owner_action_center_section = f"""
        <section class="owner-action-center" data-pack="136-action-center-error">
          <h2>Owner Action Center Unavailable</h2>
          <p>{_html_escape(type(exc).__name__)}</p>
        </section>
        """

    try:
        from tower.security_watch_owner_posture import (
            load_security_watch_owner_posture,
            render_security_watch_owner_posture_section,
        )
        security_watch_section = render_security_watch_owner_posture_section(
            load_security_watch_owner_posture()
        )
    except Exception as exc:
        security_watch_section = f"""
        <section class="security-watch-owner-posture" data-pack="136-watch-error">
          <h2>Tower Security Watch Unavailable</h2>
          <p>{_html_escape(type(exc).__name__)}</p>
        </section>
        """

    try:
        from tower.security_watch_checkpoint import (
            load_security_watch_checkpoint,
            render_security_watch_checkpoint_section,
        )
        security_watch_checkpoint_section = render_security_watch_checkpoint_section(
            load_security_watch_checkpoint()
        )
    except Exception as exc:
        security_watch_checkpoint_section = f"""
        <section class="security-watch-checkpoint" data-pack="136-watch-checkpoint-error">
          <h2>Security Watch Checkpoint Unavailable</h2>
          <p>{_html_escape(type(exc).__name__)}</p>
        </section>
        """

    try:
        from tower.security_command_owner_quick_actions import (
            load_owner_quick_actions_status,
            render_owner_quick_actions_section,
        )
        quick_actions_section = render_owner_quick_actions_section(load_owner_quick_actions_status())
    except Exception as exc:
        quick_actions_section = f"""
        <section class="owner-quick-action-rail" data-pack="136-quick-error">
          <h2>Owner Quick Actions Unavailable</h2>
          <p>{_html_escape(type(exc).__name__)}</p>
        </section>
        """

    try:
        from tower.security_command_preferred_destination import (
            load_security_command_preferred_destination_status,
            render_security_command_preferred_destination_section,
        )
        preferred_section = render_security_command_preferred_destination_section(
            load_security_command_preferred_destination_status()
        )
    except Exception as exc:
        preferred_section = f"""
        <section class="preferred-command-destination" data-pack="136-preferred-error">
          <h2>Preferred Security Command Destination Unavailable</h2>
          <p>{_html_escape(type(exc).__name__)}</p>
        </section>
        """

    try:
        from tower.security_inbox_owner_queue import (
            load_security_inbox_owner_queue,
            render_security_inbox_owner_queue_section,
        )
        inbox_section = render_security_inbox_owner_queue_section(load_security_inbox_owner_queue())
    except Exception as exc:
        inbox_section = f"""
        <section class="security-inbox-owner-queue" data-pack="136-inbox-error">
          <h2>Tower Security Inbox Unavailable</h2>
          <p>{_html_escape(type(exc).__name__)}</p>
        </section>
        """

    try:
        from tower.security_inbox_review_actions import (
            load_security_inbox_review_status,
            render_security_inbox_review_section,
        )
        review_section = render_security_inbox_review_section(load_security_inbox_review_status())
    except Exception as exc:
        review_section = f"""
        <section class="security-inbox-review-actions" data-pack="136-review-error">
          <h2>Security Inbox Review Actions Unavailable</h2>
          <p>{_html_escape(type(exc).__name__)}</p>
        </section>
        """

    try:
        from tower.security_inbox_filters_priorities import (
            load_security_inbox_filters_priorities_status,
            render_security_inbox_filters_priorities_section,
        )
        filters_section = render_security_inbox_filters_priorities_section(
            load_security_inbox_filters_priorities_status()
        )
    except Exception as exc:
        filters_section = f"""
        <section class="security-inbox-filters-priorities" data-pack="136-filters-error">
          <h2>Security Inbox Filters & Priorities Unavailable</h2>
          <p>{_html_escape(type(exc).__name__)}</p>
        </section>
        """

    try:
        from tower.security_incident_desk import (
            load_security_incident_desk_status,
            render_security_incident_desk_section,
        )
        incident_section = render_security_incident_desk_section(load_security_incident_desk_status())
    except Exception as exc:
        incident_section = f"""
        <section class="security-incident-desk" data-pack="136-incident-error">
          <h2>Tower Incident Desk Unavailable</h2>
          <p>{_html_escape(type(exc).__name__)}</p>
        </section>
        """

    try:
        from tower.security_incident_filters_escalation import (
            load_security_incident_filters_escalation_status,
            render_security_incident_filters_escalation_section,
        )
        incident_filters_section = render_security_incident_filters_escalation_section(
            load_security_incident_filters_escalation_status()
        )
    except Exception as exc:
        incident_filters_section = f"""
        <section class="security-incident-filters-escalation" data-pack="136-incident-filters-error">
          <h2>Incident Filters & Escalation Unavailable</h2>
          <p>{_html_escape(type(exc).__name__)}</p>
        </section>
        """

    try:
        from tower.security_command_navigation_links import (
            load_security_command_navigation_links_status,
            render_security_command_navigation_links_section,
        )
        nav_section = render_security_command_navigation_links_section(
            load_security_command_navigation_links_status()
        )
    except Exception as exc:
        nav_section = f"""
        <section class="tower-security-command-links" data-pack="136-nav-error">
          <h2>Security Command Links Unavailable</h2>
          <p>{_html_escape(type(exc).__name__)}</p>
        </section>
        """

    try:
        from tower.security_command_object_visibility_integration import (
            load_security_command_object_visibility_status,
            render_security_command_object_visibility_section,
        )
        object_section = render_security_command_object_visibility_section(
            load_security_command_object_visibility_status()
        )
    except Exception:
        try:
            from tower.security_command_page import pack113_security_command_object_visibility_html_section
            object_section = pack113_security_command_object_visibility_html_section()
        except Exception as exc:
            object_section = f"""
            <section class="tower-object-visibility-panel" data-pack="136-object-error">
              <h2>Object Visibility Unavailable</h2>
              <p>{_html_escape(type(exc).__name__)}</p>
            </section>
            """

    route_health = status.get("route_health", {}) if isinstance(status.get("route_health"), dict) else {}
    object_checkpoint = status.get("object_checkpoint", {}) if isinstance(status.get("object_checkpoint"), dict) else {}
    object_visibility = status.get("object_visibility", {}) if isinstance(status.get("object_visibility"), dict) else {}
    navigation = status.get("navigation", {}) if isinstance(status.get("navigation"), dict) else {}

    health_cards = "".join([
        _build_health_card("Route Coverage", f"{route_health.get('coverage_pct', 0)}%", "ROUTE WALL"),
        _build_health_card("Guarded Protected Routes", f"{route_health.get('guarded_needed_count', 0)} / {route_health.get('needs_guard_count', 0)}", "GUARDS"),
        _build_health_card("Helper Wraps", object_checkpoint.get("helper_wrapped_count", 0), "OBJECT CLEANUP"),
        _build_health_card("Object Events", object_visibility.get("event_count", 0), "OBJECT VISIBILITY"),
        _build_health_card("Security Links", navigation.get("link_count", 0), "NAVIGATION"),
        _build_health_card("Readiness", status.get("readiness_score", 0), "OWNER COMMAND"),
    ])

    html = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>The Tower · Unified Owner Security Command</title>
  <style>
    body {{
      margin: 0;
      min-height: 100vh;
      background:
        radial-gradient(circle at top left, rgba(220,183,94,.13), transparent 32%),
        radial-gradient(circle at bottom right, rgba(168,175,255,.10), transparent 35%),
        #080907;
      color: #f5ead2;
      font-family: Inter, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }}
    main {{ max-width: 1220px; margin: 0 auto; padding: 42px 22px 70px; }}
    .tower-owner-hero {{
      border: 1px solid rgba(220,183,94,.38);
      border-radius: 34px;
      padding: 32px;
      background: linear-gradient(135deg, rgba(75,48,18,.76), rgba(8,9,7,.94));
      box-shadow: 0 24px 90px rgba(0,0,0,.44);
      margin-bottom: 22px;
    }}
    .tower-owner-hero__eyebrow {{
      color: rgba(220,183,94,.88);
      text-transform: uppercase;
      letter-spacing: .16em;
      font-size: 11px;
      margin-bottom: 10px;
    }}
    .tower-owner-hero h1 {{ margin: 0 0 10px; font-size: 38px; letter-spacing: -.045em; }}
    .tower-owner-hero p {{ margin: 0; color: rgba(245,234,210,.76); line-height: 1.55; max-width: 880px; }}
    .tower-owner-health-grid {{
      display: grid;
      grid-template-columns: repeat(6, minmax(0, 1fr));
      gap: 12px;
      margin: 18px 0 0;
    }}
    .tower-owner-health-card {{
      border: 1px solid rgba(143,221,158,.26);
      border-radius: 20px;
      padding: 14px;
      background: rgba(255,255,255,.045);
    }}
    .tower-owner-health-card__eyebrow {{
      color: rgba(220,183,94,.8);
      text-transform: uppercase;
      letter-spacing: .12em;
      font-size: 10px;
      margin-bottom: 7px;
    }}
    .tower-owner-health-card h3 {{ margin: 0 0 6px; font-size: 22px; }}
    .tower-owner-health-card p {{ margin: 0; color: rgba(245,234,210,.63); font-size: 12px; }}
    .tower-owner-section {{ margin-top: 22px; }}
    @media (max-width: 1050px) {{ .tower-owner-health-grid {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }} }}
    @media (max-width: 720px) {{ .tower-owner-health-grid {{ grid-template-columns: 1fr; }} .tower-owner-hero h1 {{ font-size: 30px; }} }}
  </style>
</head>
<body>
<main>
  <!-- PACK116_UNIFIED_OWNER_SECURITY_COMMAND_PAGE -->
  <!-- PACK118B_SAFE_NON_RECURSIVE_RENDERER -->
  <!-- PACK119_UNIFIED_OWNER_PAGE_INCLUDES_QUICK_ACTION_RAIL -->
  <!-- PACK123_UNIFIED_OWNER_PAGE_INCLUDES_SECURITY_INBOX_AND_REVIEW -->
  <!-- PACK125_UNIFIED_OWNER_PAGE_INCLUDES_SECURITY_INBOX_FILTERS -->
  <!-- PACK127_UNIFIED_OWNER_PAGE_INCLUDES_INCIDENT_DESK -->
  <!-- PACK129_UNIFIED_OWNER_PAGE_INCLUDES_INCIDENT_FILTERS_ESCALATION -->
  <!-- PACK132_UNIFIED_OWNER_PAGE_INCLUDES_SECURITY_WATCH -->
  <!-- PACK134_UNIFIED_OWNER_PAGE_INCLUDES_SECURITY_WATCH_CHECKPOINT -->
  <!-- PACK136_UNIFIED_OWNER_PAGE_INCLUDES_OWNER_ACTION_CENTER -->
  <section class="tower-owner-hero" data-pack="116-136">
    <div class="tower-owner-hero__eyebrow">PACK 116 + 136 · UNIFIED OWNER COMMAND</div>
    <h1>The Tower Security Command</h1>
    <p>{_html_escape(status.get('human_reason', 'Unified Security Command loaded.'))}</p>
    <div class="tower-owner-health-grid">{health_cards}</div>
  </section>

  <section class="tower-owner-section">{owner_action_center_section}</section>
  <section class="tower-owner-section">{security_watch_section}</section>
  <section class="tower-owner-section">{security_watch_checkpoint_section}</section>
  <section class="tower-owner-section">{quick_actions_section}</section>
  <section class="tower-owner-section">{preferred_section}</section>
  <section class="tower-owner-section">{inbox_section}</section>
  <section class="tower-owner-section">{review_section}</section>
  <section class="tower-owner-section">{filters_section}</section>
  <section class="tower-owner-section">{incident_section}</section>
  <section class="tower-owner-section">{incident_filters_section}</section>
  <section class="tower-owner-section">{nav_section}</section>
  <section class="tower-owner-section">{object_section}</section>
  <!-- END PACK136_UNIFIED_OWNER_PAGE_INCLUDES_OWNER_ACTION_CENTER -->
  <!-- END PACK134_UNIFIED_OWNER_PAGE_INCLUDES_SECURITY_WATCH_CHECKPOINT -->
  <!-- END PACK132_UNIFIED_OWNER_PAGE_INCLUDES_SECURITY_WATCH -->
  <!-- END PACK129_UNIFIED_OWNER_PAGE_INCLUDES_INCIDENT_FILTERS_ESCALATION -->
  <!-- END PACK127_UNIFIED_OWNER_PAGE_INCLUDES_INCIDENT_DESK -->
  <!-- END PACK125_UNIFIED_OWNER_PAGE_INCLUDES_SECURITY_INBOX_FILTERS -->
  <!-- END PACK123_UNIFIED_OWNER_PAGE_INCLUDES_SECURITY_INBOX_AND_REVIEW -->
  <!-- END PACK119_UNIFIED_OWNER_PAGE_INCLUDES_QUICK_ACTION_RAIL -->
  <!-- END PACK118B_SAFE_NON_RECURSIVE_RENDERER -->
  <!-- END PACK116_UNIFIED_OWNER_SECURITY_COMMAND_PAGE -->
</main>
</body>
</html>"""
    return html

# ================================================================================
# END PACK136_UNIFIED_OWNER_PAGE_WITH_OWNER_ACTION_CENTER
# ================================================================================



# ================================================================================
# PACK146_UNIFIED_OWNER_PAGE_INCLUDES_OWNER_ACTION_REVIEW_CHECKPOINT
# ================================================================================
# Adds cached Pack 145 Owner Action Review Checkpoint section to unified page.
# This avoids calling any recursive command-room builders.
# ================================================================================

def _pack146_render_owner_action_review_checkpoint_for_unified() -> str:
    try:
        from tower.owner_action_review_checkpoint import (
            build_owner_action_review_checkpoint,
            render_owner_action_review_checkpoint_section,
        )

        status = build_owner_action_review_checkpoint(write_panel=False)
        return render_owner_action_review_checkpoint_section(status)
    except Exception as exc:
        error_type = type(exc).__name__
        return f"""
<!-- PACK146_OWNER_ACTION_REVIEW_CHECKPOINT_FALLBACK_SECTION -->
<section class="owner-action-review-checkpoint" data-pack="146-fallback"
  style="margin:24px 0;border:1px solid rgba(220,183,94,.35);border-radius:24px;padding:20px;background:#14110b;color:#f5ead2;">
  <div style="color:#dcb75e;text-transform:uppercase;letter-spacing:.14em;font-size:11px;">PACK 146 · OWNER ACTION REVIEW CHECKPOINT</div>
  <h2 style="margin:8px 0 0;">Owner Action Review Checkpoint</h2>
  <p style="color:rgba(245,234,210,.72);">Checkpoint section could not render in the unified page.</p>
  <p style="color:rgba(245,234,210,.58);font-size:12px;">Error type: {error_type}</p>
</section>
<!-- END PACK146_OWNER_ACTION_REVIEW_CHECKPOINT_FALLBACK_SECTION -->
"""


try:
    _pack146_original_render_unified_owner_security_command_html = render_unified_owner_security_command_html
except Exception:
    _pack146_original_render_unified_owner_security_command_html = None


def render_unified_owner_security_command_html(*args, **kwargs) -> str:
    base_html = ""
    if _pack146_original_render_unified_owner_security_command_html is not None:
        base_html = _pack146_original_render_unified_owner_security_command_html(*args, **kwargs)
    else:
        base_html = """<!doctype html><html><body><main><h1>Unified Security Command</h1></main></body></html>"""

    marker = "PACK146_UNIFIED_OWNER_PAGE_INCLUDES_OWNER_ACTION_REVIEW_CHECKPOINT"
    if marker in base_html or "PACK145_OWNER_ACTION_REVIEW_CHECKPOINT_SECTION" in base_html:
        return base_html

    section = _pack146_render_owner_action_review_checkpoint_for_unified()
    injection = f"""
<!-- PACK146_UNIFIED_OWNER_PAGE_INCLUDES_OWNER_ACTION_REVIEW_CHECKPOINT -->
{section}
<!-- END PACK146_UNIFIED_OWNER_PAGE_INCLUDES_OWNER_ACTION_REVIEW_CHECKPOINT -->
"""

    if "</main>" in base_html:
        return base_html.replace("</main>", injection + "\n</main>", 1)

    if "</body>" in base_html:
        return base_html.replace("</body>", injection + "\n</body>", 1)

    return base_html + injection


try:
    _pack146_original_write_unified_owner_security_command_html = write_unified_owner_security_command_html
except Exception:
    _pack146_original_write_unified_owner_security_command_html = None


def write_unified_owner_security_command_html(*args, **kwargs) -> Dict[str, Any]:
    html = render_unified_owner_security_command_html()

    try:
        path = DATA_DIR / "security_command_unified_owner_page.html"
    except Exception:
        path = Path(__file__).resolve().parents[1] / "tower" / "data" / "security_command_unified_owner_page.html"

    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(html, encoding="utf-8")
    except Exception:
        pass

    return {
        "ok": True,
        "pack": "146",
        "decision": "unified_owner_security_command_html_written",
        "path": str(path),
        "html_length": len(html),
        "human_reason": "Unified owner Security Command HTML written with Owner Action Review Checkpoint.",
        "soulaana_translation": "Soulaana: Unified command page now includes the Owner Action review checkpoint.",
    }

# ================================================================================
# END PACK146_UNIFIED_OWNER_PAGE_INCLUDES_OWNER_ACTION_REVIEW_CHECKPOINT
# ================================================================================



# ================================================================================
# PACK147_UNIFIED_OWNER_PAGE_INCLUDES_OWNER_ACTION_REVIEW_DASHBOARD_CARDS
# ================================================================================
# Adds cached Pack 147 dashboard cards to unified owner command page.
# ================================================================================

def _pack147_render_owner_action_review_dashboard_cards_for_unified() -> str:
    try:
        from tower.owner_action_review_dashboard_cards import (
            build_owner_action_review_dashboard_cards,
            render_owner_action_review_dashboard_cards_section,
        )

        status = build_owner_action_review_dashboard_cards(write_panel=False)
        return render_owner_action_review_dashboard_cards_section(status)
    except Exception as exc:
        error_type = type(exc).__name__
        return f"""
<!-- PACK147_OWNER_ACTION_REVIEW_DASHBOARD_CARDS_FALLBACK_SECTION -->
<section class="owner-action-dashboard-cards" data-pack="147-fallback"
  style="margin:24px 0;border:1px solid rgba(220,183,94,.35);border-radius:24px;padding:20px;background:#14110b;color:#f5ead2;">
  <div style="color:#dcb75e;text-transform:uppercase;letter-spacing:.14em;font-size:11px;">PACK 147 · OWNER ACTION REVIEW DASHBOARD</div>
  <h2 style="margin:8px 0 0;">Owner Action Review Dashboard Cards</h2>
  <p style="color:rgba(245,234,210,.72);">Dashboard card section could not render in the unified page.</p>
  <p style="color:rgba(245,234,210,.58);font-size:12px;">Error type: {error_type}</p>
</section>
<!-- END PACK147_OWNER_ACTION_REVIEW_DASHBOARD_CARDS_FALLBACK_SECTION -->
"""


try:
    _pack147_previous_render_unified_owner_security_command_html = render_unified_owner_security_command_html
except Exception:
    _pack147_previous_render_unified_owner_security_command_html = None


def render_unified_owner_security_command_html(*args, **kwargs) -> str:
    base_html = ""
    if _pack147_previous_render_unified_owner_security_command_html is not None:
        base_html = _pack147_previous_render_unified_owner_security_command_html(*args, **kwargs)
    else:
        base_html = """<!doctype html><html><body><main><h1>Unified Security Command</h1></main></body></html>"""

    marker = "PACK147_UNIFIED_OWNER_PAGE_INCLUDES_OWNER_ACTION_REVIEW_DASHBOARD_CARDS"
    if marker in base_html or "PACK147_OWNER_ACTION_REVIEW_DASHBOARD_CARDS_SECTION" in base_html:
        return base_html

    section = _pack147_render_owner_action_review_dashboard_cards_for_unified()
    injection = f"""
<!-- PACK147_UNIFIED_OWNER_PAGE_INCLUDES_OWNER_ACTION_REVIEW_DASHBOARD_CARDS -->
{section}
<!-- END PACK147_UNIFIED_OWNER_PAGE_INCLUDES_OWNER_ACTION_REVIEW_DASHBOARD_CARDS -->
"""

    if "PACK145_OWNER_ACTION_REVIEW_CHECKPOINT_SECTION" in base_html:
        # Place dashboard cards before the checkpoint section when possible.
        return base_html.replace("<!-- PACK145_OWNER_ACTION_REVIEW_CHECKPOINT_SECTION -->", injection + "\n<!-- PACK145_OWNER_ACTION_REVIEW_CHECKPOINT_SECTION -->", 1)

    if "</main>" in base_html:
        return base_html.replace("</main>", injection + "\n</main>", 1)

    if "</body>" in base_html:
        return base_html.replace("</body>", injection + "\n</body>", 1)

    return base_html + injection


try:
    _pack147_previous_write_unified_owner_security_command_html = write_unified_owner_security_command_html
except Exception:
    _pack147_previous_write_unified_owner_security_command_html = None


def write_unified_owner_security_command_html(*args, **kwargs) -> Dict[str, Any]:
    html = render_unified_owner_security_command_html()

    try:
        path = DATA_DIR / "security_command_unified_owner_page.html"
    except Exception:
        path = Path(__file__).resolve().parents[1] / "tower" / "data" / "security_command_unified_owner_page.html"

    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(html, encoding="utf-8")
    except Exception:
        pass

    return {
        "ok": True,
        "pack": "147",
        "decision": "unified_owner_security_command_html_written",
        "path": str(path),
        "html_length": len(html),
        "human_reason": "Unified owner Security Command HTML written with Owner Action Review Dashboard Cards.",
        "soulaana_translation": "Soulaana: Unified command page now includes Owner Action review dashboard cards.",
    }

# ================================================================================
# END PACK147_UNIFIED_OWNER_PAGE_INCLUDES_OWNER_ACTION_REVIEW_DASHBOARD_CARDS
# ================================================================================



# ================================================================================
# PACK148_UNIFIED_OWNER_PAGE_INCLUDES_COMPACT_OWNER_ACTION_REVIEW_CARD
# ================================================================================
# Adds cached Pack 148 compact card to unified owner command page.
# ================================================================================

def _pack148_render_compact_owner_action_review_card_for_unified() -> str:
    try:
        from tower.owner_action_review_compact_card import (
            build_owner_action_review_compact_card,
            render_owner_action_review_compact_card_section,
        )

        status = build_owner_action_review_compact_card(write_panel=False)
        return render_owner_action_review_compact_card_section(status)
    except Exception as exc:
        error_type = type(exc).__name__
        return f"""
<!-- PACK148_OWNER_ACTION_REVIEW_COMPACT_CARD_FALLBACK_SECTION -->
<section class="owner-action-compact-card" data-pack="148-fallback"
  style="margin:24px 0;border:1px solid rgba(220,183,94,.35);border-radius:24px;padding:20px;background:#14110b;color:#f5ead2;">
  <div style="color:#dcb75e;text-transform:uppercase;letter-spacing:.14em;font-size:11px;">PACK 148 · COMPACT OWNER ACTION REVIEW</div>
  <h2 style="margin:8px 0 0;">Compact Owner Action Review Card</h2>
  <p style="color:rgba(245,234,210,.72);">Compact card section could not render in the unified page.</p>
  <p style="color:rgba(245,234,210,.58);font-size:12px;">Error type: {error_type}</p>
</section>
<!-- END PACK148_OWNER_ACTION_REVIEW_COMPACT_CARD_FALLBACK_SECTION -->
"""


try:
    _pack148_previous_render_unified_owner_security_command_html = render_unified_owner_security_command_html
except Exception:
    _pack148_previous_render_unified_owner_security_command_html = None


def render_unified_owner_security_command_html(*args, **kwargs) -> str:
    base_html = ""
    if _pack148_previous_render_unified_owner_security_command_html is not None:
        base_html = _pack148_previous_render_unified_owner_security_command_html(*args, **kwargs)
    else:
        base_html = """<!doctype html><html><body><main><h1>Unified Security Command</h1></main></body></html>"""

    marker = "PACK148_UNIFIED_OWNER_PAGE_INCLUDES_COMPACT_OWNER_ACTION_REVIEW_CARD"
    if marker in base_html or "PACK148_OWNER_ACTION_REVIEW_COMPACT_CARD_SECTION" in base_html:
        return base_html

    section = _pack148_render_compact_owner_action_review_card_for_unified()
    injection = f"""
<!-- PACK148_UNIFIED_OWNER_PAGE_INCLUDES_COMPACT_OWNER_ACTION_REVIEW_CARD -->
{section}
<!-- END PACK148_UNIFIED_OWNER_PAGE_INCLUDES_COMPACT_OWNER_ACTION_REVIEW_CARD -->
"""

    if "PACK147_OWNER_ACTION_REVIEW_DASHBOARD_CARDS_SECTION" in base_html:
        return base_html.replace("<!-- PACK147_OWNER_ACTION_REVIEW_DASHBOARD_CARDS_SECTION -->", injection + "\n<!-- PACK147_OWNER_ACTION_REVIEW_DASHBOARD_CARDS_SECTION -->", 1)

    if "</main>" in base_html:
        return base_html.replace("</main>", injection + "\n</main>", 1)

    if "</body>" in base_html:
        return base_html.replace("</body>", injection + "\n</body>", 1)

    return base_html + injection


try:
    _pack148_previous_write_unified_owner_security_command_html = write_unified_owner_security_command_html
except Exception:
    _pack148_previous_write_unified_owner_security_command_html = None


def write_unified_owner_security_command_html(*args, **kwargs) -> Dict[str, Any]:
    html = render_unified_owner_security_command_html()

    try:
        path = DATA_DIR / "security_command_unified_owner_page.html"
    except Exception:
        path = Path(__file__).resolve().parents[1] / "tower" / "data" / "security_command_unified_owner_page.html"

    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(html, encoding="utf-8")
    except Exception:
        pass

    return {
        "ok": True,
        "pack": "148",
        "decision": "unified_owner_security_command_html_written",
        "path": str(path),
        "html_length": len(html),
        "human_reason": "Unified owner Security Command HTML written with Compact Owner Action Review Card.",
        "soulaana_translation": "Soulaana: Unified command page now includes the compact Owner Action review card.",
    }

# ================================================================================
# END PACK148_UNIFIED_OWNER_PAGE_INCLUDES_COMPACT_OWNER_ACTION_REVIEW_CARD
# ================================================================================



# ================================================================================
# PACK149_UNIFIED_OWNER_PAGE_INCLUDES_OWNER_ACTION_REVIEW_FOCUS_LANES
# ================================================================================
# Adds cached Pack 149 focus lanes to unified owner command page.
# ================================================================================

def _pack149_render_owner_action_review_focus_lanes_for_unified() -> str:
    try:
        from tower.owner_action_review_focus_lanes import (
            build_owner_action_review_focus_lanes,
            render_owner_action_review_focus_lanes_section,
        )

        status = build_owner_action_review_focus_lanes(lane="all", write_panel=False)
        return render_owner_action_review_focus_lanes_section(status)
    except Exception as exc:
        error_type = type(exc).__name__
        return f"""
<!-- PACK149_OWNER_ACTION_REVIEW_FOCUS_LANES_FALLBACK_SECTION -->
<section class="owner-action-focus-lanes" data-pack="149-fallback"
  style="margin:24px 0;border:1px solid rgba(220,183,94,.35);border-radius:24px;padding:20px;background:#14110b;color:#f5ead2;">
  <div style="color:#dcb75e;text-transform:uppercase;letter-spacing:.14em;font-size:11px;">PACK 149 · OWNER ACTION REVIEW FOCUS LANES</div>
  <h2 style="margin:8px 0 0;">Owner Action Review Focus Lanes</h2>
  <p style="color:rgba(245,234,210,.72);">Focus lane section could not render in the unified page.</p>
  <p style="color:rgba(245,234,210,.58);font-size:12px;">Error type: {error_type}</p>
</section>
<!-- END PACK149_OWNER_ACTION_REVIEW_FOCUS_LANES_FALLBACK_SECTION -->
"""


try:
    _pack149_previous_render_unified_owner_security_command_html = render_unified_owner_security_command_html
except Exception:
    _pack149_previous_render_unified_owner_security_command_html = None


def render_unified_owner_security_command_html(*args, **kwargs) -> str:
    base_html = ""
    if _pack149_previous_render_unified_owner_security_command_html is not None:
        base_html = _pack149_previous_render_unified_owner_security_command_html(*args, **kwargs)
    else:
        base_html = """<!doctype html><html><body><main><h1>Unified Security Command</h1></main></body></html>"""

    marker = "PACK149_UNIFIED_OWNER_PAGE_INCLUDES_OWNER_ACTION_REVIEW_FOCUS_LANES"
    if marker in base_html or "PACK149_OWNER_ACTION_REVIEW_FOCUS_LANES_SECTION" in base_html:
        return base_html

    section = _pack149_render_owner_action_review_focus_lanes_for_unified()
    injection = f"""
<!-- PACK149_UNIFIED_OWNER_PAGE_INCLUDES_OWNER_ACTION_REVIEW_FOCUS_LANES -->
{section}
<!-- END PACK149_UNIFIED_OWNER_PAGE_INCLUDES_OWNER_ACTION_REVIEW_FOCUS_LANES -->
"""

    if "PACK148_OWNER_ACTION_REVIEW_COMPACT_CARD_SECTION" in base_html:
        return base_html.replace("<!-- PACK148_OWNER_ACTION_REVIEW_COMPACT_CARD_SECTION -->", injection + "\n<!-- PACK148_OWNER_ACTION_REVIEW_COMPACT_CARD_SECTION -->", 1)

    if "</main>" in base_html:
        return base_html.replace("</main>", injection + "\n</main>", 1)

    if "</body>" in base_html:
        return base_html.replace("</body>", injection + "\n</body>", 1)

    return base_html + injection


try:
    _pack149_previous_write_unified_owner_security_command_html = write_unified_owner_security_command_html
except Exception:
    _pack149_previous_write_unified_owner_security_command_html = None


def write_unified_owner_security_command_html(*args, **kwargs) -> Dict[str, Any]:
    html = render_unified_owner_security_command_html()

    try:
        path = DATA_DIR / "security_command_unified_owner_page.html"
    except Exception:
        path = Path(__file__).resolve().parents[1] / "tower" / "data" / "security_command_unified_owner_page.html"

    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(html, encoding="utf-8")
    except Exception:
        pass

    return {
        "ok": True,
        "pack": "149",
        "decision": "unified_owner_security_command_html_written",
        "path": str(path),
        "html_length": len(html),
        "human_reason": "Unified owner Security Command HTML written with Owner Action Review Focus Lanes.",
        "soulaana_translation": "Soulaana: Unified command page now includes Owner Action review focus lanes.",
    }

# ================================================================================
# END PACK149_UNIFIED_OWNER_PAGE_INCLUDES_OWNER_ACTION_REVIEW_FOCUS_LANES
# ================================================================================



# ================================================================================
# PACK150_UNIFIED_OWNER_PAGE_INCLUDES_FINAL_OWNER_ACTION_REVIEW_READINESS
# ================================================================================
# Adds cached Pack 150 final readiness section to unified owner command page.
# ================================================================================

def _pack150_render_owner_action_review_readiness_for_unified() -> str:
    try:
        from tower.owner_action_review_readiness_checkpoint import (
            build_owner_action_review_readiness_checkpoint,
            render_owner_action_review_readiness_section,
        )

        status = build_owner_action_review_readiness_checkpoint(write_panel=False)
        return render_owner_action_review_readiness_section(status)
    except Exception as exc:
        error_type = type(exc).__name__
        return f"""
<!-- PACK150_OWNER_ACTION_REVIEW_READINESS_FALLBACK_SECTION -->
<section class="owner-action-readiness" data-pack="150-fallback"
  style="margin:24px 0;border:1px solid rgba(220,183,94,.35);border-radius:24px;padding:20px;background:#14110b;color:#f5ead2;">
  <div style="color:#dcb75e;text-transform:uppercase;letter-spacing:.14em;font-size:11px;">PACK 150 · FINAL OWNER ACTION REVIEW READINESS</div>
  <h2 style="margin:8px 0 0;">Final Owner Action Review Readiness</h2>
  <p style="color:rgba(245,234,210,.72);">Final readiness section could not render in the unified page.</p>
  <p style="color:rgba(245,234,210,.58);font-size:12px;">Error type: {error_type}</p>
</section>
<!-- END PACK150_OWNER_ACTION_REVIEW_READINESS_FALLBACK_SECTION -->
"""


try:
    _pack150_previous_render_unified_owner_security_command_html = render_unified_owner_security_command_html
except Exception:
    _pack150_previous_render_unified_owner_security_command_html = None


def render_unified_owner_security_command_html(*args, **kwargs) -> str:
    base_html = ""
    if _pack150_previous_render_unified_owner_security_command_html is not None:
        base_html = _pack150_previous_render_unified_owner_security_command_html(*args, **kwargs)
    else:
        base_html = """<!doctype html><html><body><main><h1>Unified Security Command</h1></main></body></html>"""

    marker = "PACK150_UNIFIED_OWNER_PAGE_INCLUDES_FINAL_OWNER_ACTION_REVIEW_READINESS"
    if marker in base_html or "PACK150_OWNER_ACTION_REVIEW_READINESS_CHECKPOINT_SECTION" in base_html:
        return base_html

    section = _pack150_render_owner_action_review_readiness_for_unified()
    injection = f"""
<!-- PACK150_UNIFIED_OWNER_PAGE_INCLUDES_FINAL_OWNER_ACTION_REVIEW_READINESS -->
{section}
<!-- END PACK150_UNIFIED_OWNER_PAGE_INCLUDES_FINAL_OWNER_ACTION_REVIEW_READINESS -->
"""

    if "PACK149_OWNER_ACTION_REVIEW_FOCUS_LANES_SECTION" in base_html:
        return base_html.replace("<!-- PACK149_OWNER_ACTION_REVIEW_FOCUS_LANES_SECTION -->", injection + "\n<!-- PACK149_OWNER_ACTION_REVIEW_FOCUS_LANES_SECTION -->", 1)

    if "</main>" in base_html:
        return base_html.replace("</main>", injection + "\n</main>", 1)

    if "</body>" in base_html:
        return base_html.replace("</body>", injection + "\n</body>", 1)

    return base_html + injection


try:
    _pack150_previous_write_unified_owner_security_command_html = write_unified_owner_security_command_html
except Exception:
    _pack150_previous_write_unified_owner_security_command_html = None


def write_unified_owner_security_command_html(*args, **kwargs) -> Dict[str, Any]:
    html = render_unified_owner_security_command_html()

    try:
        path = DATA_DIR / "security_command_unified_owner_page.html"
    except Exception:
        path = Path(__file__).resolve().parents[1] / "tower" / "data" / "security_command_unified_owner_page.html"

    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(html, encoding="utf-8")
    except Exception:
        pass

    return {
        "ok": True,
        "pack": "150",
        "decision": "unified_owner_security_command_html_written",
        "path": str(path),
        "html_length": len(html),
        "human_reason": "Unified owner Security Command HTML written with final Owner Action review readiness.",
        "soulaana_translation": "Soulaana: Unified command page now includes final Owner Action review readiness.",
    }

# ================================================================================
# END PACK150_UNIFIED_OWNER_PAGE_INCLUDES_FINAL_OWNER_ACTION_REVIEW_READINESS
# ================================================================================



# ================================================================================
# PACK151_UNIFIED_OWNER_PAGE_INCLUDES_POLICY_AS_CODE_ENGINE
# ================================================================================

def _pack151_render_policy_as_code_engine_for_unified() -> str:
    try:
        from tower.policy_as_code_engine import (
            build_policy_as_code_engine_status,
            render_policy_as_code_engine_section,
        )

        status = build_policy_as_code_engine_status(write_panel=False)
        return render_policy_as_code_engine_section(status)
    except Exception as exc:
        error_type = type(exc).__name__
        return f"""
<!-- PACK151_POLICY_AS_CODE_ENGINE_FALLBACK_SECTION -->
<section class="policy-as-code-engine" data-pack="151-fallback"
  style="margin:24px 0;border:1px solid rgba(220,183,94,.35);border-radius:24px;padding:20px;background:#14110b;color:#f5ead2;">
  <div style="color:#dcb75e;text-transform:uppercase;letter-spacing:.14em;font-size:11px;">PACK 151 · POLICY-AS-CODE FOUNDATION</div>
  <h2 style="margin:8px 0 0;">Policy-as-Code Engine</h2>
  <p style="color:rgba(245,234,210,.72);">Policy-as-Code section could not render in the unified page.</p>
  <p style="color:rgba(245,234,210,.58);font-size:12px;">Error type: {error_type}</p>
</section>
<!-- END PACK151_POLICY_AS_CODE_ENGINE_FALLBACK_SECTION -->
"""


try:
    _pack151_previous_render_unified_owner_security_command_html = render_unified_owner_security_command_html
except Exception:
    _pack151_previous_render_unified_owner_security_command_html = None


def render_unified_owner_security_command_html(*args, **kwargs) -> str:
    base_html = ""
    if _pack151_previous_render_unified_owner_security_command_html is not None:
        base_html = _pack151_previous_render_unified_owner_security_command_html(*args, **kwargs)
    else:
        base_html = """<!doctype html><html><body><main><h1>Unified Security Command</h1></main></body></html>"""

    marker = "PACK151_UNIFIED_OWNER_PAGE_INCLUDES_POLICY_AS_CODE_ENGINE"
    if marker in base_html or "PACK151_POLICY_AS_CODE_ENGINE_SECTION" in base_html:
        return base_html

    section = _pack151_render_policy_as_code_engine_for_unified()
    injection = f"""
<!-- PACK151_UNIFIED_OWNER_PAGE_INCLUDES_POLICY_AS_CODE_ENGINE -->
{section}
<!-- END PACK151_UNIFIED_OWNER_PAGE_INCLUDES_POLICY_AS_CODE_ENGINE -->
"""

    if "PACK150_OWNER_ACTION_REVIEW_READINESS_CHECKPOINT_SECTION" in base_html:
        return base_html.replace("<!-- PACK150_OWNER_ACTION_REVIEW_READINESS_CHECKPOINT_SECTION -->", injection + "\n<!-- PACK150_OWNER_ACTION_REVIEW_READINESS_CHECKPOINT_SECTION -->", 1)

    if "</main>" in base_html:
        return base_html.replace("</main>", injection + "\n</main>", 1)

    if "</body>" in base_html:
        return base_html.replace("</body>", injection + "\n</body>", 1)

    return base_html + injection


try:
    _pack151_previous_write_unified_owner_security_command_html = write_unified_owner_security_command_html
except Exception:
    _pack151_previous_write_unified_owner_security_command_html = None


def write_unified_owner_security_command_html(*args, **kwargs) -> Dict[str, Any]:
    html = render_unified_owner_security_command_html()

    try:
        path = DATA_DIR / "security_command_unified_owner_page.html"
    except Exception:
        path = Path(__file__).resolve().parents[1] / "tower" / "data" / "security_command_unified_owner_page.html"

    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(html, encoding="utf-8")
    except Exception:
        pass

    return {
        "ok": True,
        "pack": "151",
        "decision": "unified_owner_security_command_html_written",
        "path": str(path),
        "html_length": len(html),
        "human_reason": "Unified owner Security Command HTML written with Policy-as-Code Engine.",
        "soulaana_translation": "Soulaana: Unified command page now includes Policy-as-Code.",
    }

# ================================================================================
# END PACK151_UNIFIED_OWNER_PAGE_INCLUDES_POLICY_AS_CODE_ENGINE
# ================================================================================



# === PACK 152 POLICY SIMULATION UNIFIED SECTION START ===
def build_pack_152_policy_simulation_unified_section():
    """
    Pack 152 unified owner section.

    Safe/non-recursive:
    - reads only policy_simulation_mode
    - does not call quick actions
    - does not call the full unified page builder
    """
    try:
        from tower.policy_simulation_mode import build_policy_simulation_unified_owner_section
        return build_policy_simulation_unified_owner_section()
    except Exception as exc:
        return {
            "section_id": "policy_simulation_mode",
            "title": "Policy Simulation Mode",
            "subtitle": "Simulation section needs review.",
            "status": "review",
            "href": "/tower/policy-simulation-mode.json",
            "cards": [],
            "simulated_only": True,
            "cached_non_recursive": True,
            "error": str(exc),
        }


def build_pack_152_policy_simulation_html_section():
    try:
        from tower.policy_simulation_mode import build_policy_simulation_mode_html_section
        return build_policy_simulation_mode_html_section()
    except Exception as exc:
        return f"""
        <section class="tower-section policy-simulation-mode-section" id="policy-simulation-mode">
            <div class="tower-section-heading">
                <p class="tower-kicker">Pack 152</p>
                <h2>Policy Simulation Mode</h2>
                <p>Simulation section needs review: {exc}</p>
                <a class="tower-link-pill" href="/tower/policy-simulation-mode.json">Open simulation JSON</a>
            </div>
        </section>
        """


def append_pack_152_policy_simulation_section(sections):
    """
    Append Pack 152 section to list-like unified section payloads.
    Safe if called more than once.
    """
    try:
        if not isinstance(sections, list):
            return sections

        existing_ids = {
            str(item.get("section_id") or item.get("id"))
            for item in sections
            if isinstance(item, dict)
        }

        if "policy_simulation_mode" not in existing_ids:
            sections.append(build_pack_152_policy_simulation_unified_section())

        return sections
    except Exception:
        return sections
# === PACK 152 POLICY SIMULATION UNIFIED SECTION END ===



# === PACK 153 POLICY DECISION TRACE PREVIEW UNIFIED SECTION START ===
def build_pack_153_policy_decision_trace_preview_unified_section():
    """
    Pack 153 unified owner section.

    Safe/non-recursive:
    - reads only policy_decision_trace_receipt_preview
    - does not call quick actions
    - does not call full unified page builder
    """
    try:
        from tower.policy_decision_trace_receipt_preview import build_policy_decision_trace_preview_unified_owner_section
        return build_policy_decision_trace_preview_unified_owner_section()
    except Exception as exc:
        return {
            "section_id": "policy_decision_trace_preview",
            "title": "Policy Decision Trace Preview",
            "subtitle": "Trace preview section needs review.",
            "status": "review",
            "href": "/tower/policy-decision-trace-preview.json",
            "cards": [],
            "simulated_only": True,
            "cached_non_recursive": True,
            "error": str(exc),
        }


def build_pack_153_policy_decision_trace_preview_html_section():
    try:
        from tower.policy_decision_trace_receipt_preview import build_policy_decision_trace_preview_html_section
        return build_policy_decision_trace_preview_html_section()
    except Exception as exc:
        return f"""
        <section class="tower-section policy-decision-trace-preview-section" id="policy-decision-trace-preview">
            <div class="tower-section-heading">
                <p class="tower-kicker">Pack 153</p>
                <h2>Policy Decision Trace Preview</h2>
                <p>Trace preview section needs review: {exc}</p>
                <a class="tower-link-pill" href="/tower/policy-decision-trace-preview.json">Open trace preview JSON</a>
            </div>
        </section>
        """


def append_pack_153_policy_decision_trace_preview_section(sections):
    """
    Append Pack 153 section to list-like unified section payloads.
    Safe if called more than once.
    """
    try:
        if not isinstance(sections, list):
            return sections

        existing_ids = {
            str(item.get("section_id") or item.get("id"))
            for item in sections
            if isinstance(item, dict)
        }

        if "policy_decision_trace_preview" not in existing_ids:
            sections.append(build_pack_153_policy_decision_trace_preview_unified_section())

        return sections
    except Exception:
        return sections
# === PACK 153 POLICY DECISION TRACE PREVIEW UNIFIED SECTION END ===



# === PACK 154 POLICY RECEIPT VAULT PREVIEW UNIFIED SECTION START ===
def build_pack_154_policy_receipt_vault_preview_unified_section():
    """
    Pack 154 unified owner section.

    Safe/non-recursive:
    - reads only policy_receipt_vault_preview
    - does not call quick actions
    - does not call full unified page builder
    """
    try:
        from tower.policy_receipt_vault_preview import build_policy_receipt_vault_preview_unified_owner_section
        return build_policy_receipt_vault_preview_unified_owner_section()
    except Exception as exc:
        return {
            "section_id": "policy_receipt_vault_preview",
            "title": "Policy Receipt Vault Preview",
            "subtitle": "Vault preview section needs review.",
            "status": "review",
            "href": "/tower/policy-receipt-vault-preview.json",
            "cards": [],
            "simulated_only": True,
            "cached_non_recursive": True,
            "error": str(exc),
        }


def build_pack_154_policy_receipt_vault_preview_html_section():
    try:
        from tower.policy_receipt_vault_preview import build_policy_receipt_vault_preview_html_section
        return build_policy_receipt_vault_preview_html_section()
    except Exception as exc:
        return f"""
        <section class="tower-section policy-receipt-vault-preview-section" id="policy-receipt-vault-preview">
            <div class="tower-section-heading">
                <p class="tower-kicker">Pack 154</p>
                <h2>Policy Receipt Vault Preview</h2>
                <p>Vault preview section needs review: {exc}</p>
                <a class="tower-link-pill" href="/tower/policy-receipt-vault-preview.json">Open vault preview JSON</a>
            </div>
        </section>
        """


def append_pack_154_policy_receipt_vault_preview_section(sections):
    """
    Append Pack 154 section to list-like unified section payloads.
    Safe if called more than once.
    """
    try:
        if not isinstance(sections, list):
            return sections

        existing_ids = {
            str(item.get("section_id") or item.get("id"))
            for item in sections
            if isinstance(item, dict)
        }

        if "policy_receipt_vault_preview" not in existing_ids:
            sections.append(build_pack_154_policy_receipt_vault_preview_unified_section())

        return sections
    except Exception:
        return sections
# === PACK 154 POLICY RECEIPT VAULT PREVIEW UNIFIED SECTION END ===



# === PACK 155 POLICY EXPIRATION RULES UNIFIED SECTION START ===
def build_pack_155_policy_expiration_rules_unified_section():
    """
    Pack 155 unified owner section.

    Safe/non-recursive:
    - reads only policy_expiration_rules
    - does not call quick actions
    - does not call full unified page builder
    """
    try:
        from tower.policy_expiration_rules import build_policy_expiration_rules_unified_owner_section
        return build_policy_expiration_rules_unified_owner_section()
    except Exception as exc:
        return {
            "section_id": "policy_expiration_rules",
            "title": "Policy Expiration Rules",
            "subtitle": "Expiration rules section needs review.",
            "status": "review",
            "href": "/tower/policy-expiration-rules.json",
            "cards": [],
            "simulated_only": True,
            "cached_non_recursive": True,
            "error": str(exc),
        }


def build_pack_155_policy_expiration_rules_html_section():
    try:
        from tower.policy_expiration_rules import build_policy_expiration_rules_html_section
        return build_policy_expiration_rules_html_section()
    except Exception as exc:
        return f"""
        <section class="tower-section policy-expiration-rules-section" id="policy-expiration-rules">
            <div class="tower-section-heading">
                <p class="tower-kicker">Pack 155</p>
                <h2>Policy Expiration Rules</h2>
                <p>Expiration rules section needs review: {exc}</p>
                <a class="tower-link-pill" href="/tower/policy-expiration-rules.json">Open expiration rules JSON</a>
            </div>
        </section>
        """


def append_pack_155_policy_expiration_rules_section(sections):
    """
    Append Pack 155 section to list-like unified section payloads.
    Safe if called more than once.
    """
    try:
        if not isinstance(sections, list):
            return sections

        existing_ids = {
            str(item.get("section_id") or item.get("id"))
            for item in sections
            if isinstance(item, dict)
        }

        if "policy_expiration_rules" not in existing_ids:
            sections.append(build_pack_155_policy_expiration_rules_unified_section())

        return sections
    except Exception:
        return sections
# === PACK 155 POLICY EXPIRATION RULES UNIFIED SECTION END ===



# === PACK 156 POLICY RENEWAL RECHECK QUEUE UNIFIED SECTION START ===
def build_pack_156_policy_renewal_recheck_queue_unified_section():
    """
    Pack 156 unified owner section.

    Safe/non-recursive:
    - reads only policy_renewal_recheck_queue
    - does not call quick actions
    - does not call full unified page builder
    """
    try:
        from tower.policy_renewal_recheck_queue import build_policy_renewal_recheck_queue_unified_owner_section
        return build_policy_renewal_recheck_queue_unified_owner_section()
    except Exception as exc:
        return {
            "section_id": "policy_renewal_recheck_queue",
            "title": "Policy Renewal / Recheck Queue",
            "subtitle": "Renewal/recheck queue section needs review.",
            "status": "review",
            "href": "/tower/policy-renewal-recheck-queue.json",
            "cards": [],
            "simulated_only": True,
            "cached_non_recursive": True,
            "error": str(exc),
        }


def build_pack_156_policy_renewal_recheck_queue_html_section():
    try:
        from tower.policy_renewal_recheck_queue import build_policy_renewal_recheck_queue_html_section
        return build_policy_renewal_recheck_queue_html_section()
    except Exception as exc:
        return f"""
        <section class="tower-section policy-renewal-recheck-queue-section" id="policy-renewal-recheck-queue">
            <div class="tower-section-heading">
                <p class="tower-kicker">Pack 156</p>
                <h2>Policy Renewal / Recheck Queue</h2>
                <p>Renewal/recheck queue section needs review: {exc}</p>
                <a class="tower-link-pill" href="/tower/policy-renewal-recheck-queue.json">Open renewal/recheck queue JSON</a>
            </div>
        </section>
        """


def append_pack_156_policy_renewal_recheck_queue_section(sections):
    """
    Append Pack 156 section to list-like unified section payloads.
    Safe if called more than once.
    """
    try:
        if not isinstance(sections, list):
            return sections

        existing_ids = {
            str(item.get("section_id") or item.get("id"))
            for item in sections
            if isinstance(item, dict)
        }

        if "policy_renewal_recheck_queue" not in existing_ids:
            sections.append(build_pack_156_policy_renewal_recheck_queue_unified_section())

        return sections
    except Exception:
        return sections
# === PACK 156 POLICY RENEWAL RECHECK QUEUE UNIFIED SECTION END ===



# === PACK 157 LEAST PRIVILEGE RECOMMENDATION UNIFIED SECTION START ===
def build_pack_157_least_privilege_recommendation_unified_section():
    """
    Pack 157 unified owner section.

    Safe/non-recursive:
    - reads only least_privilege_recommendation_engine
    - does not call quick actions
    - does not call full unified page builder
    """
    try:
        from tower.least_privilege_recommendation_engine import build_least_privilege_recommendation_unified_owner_section
        return build_least_privilege_recommendation_unified_owner_section()
    except Exception as exc:
        return {
            "section_id": "least_privilege_recommendations",
            "title": "Least-Privilege Recommendations",
            "subtitle": "Least-privilege recommendation section needs review.",
            "status": "review",
            "href": "/tower/least-privilege-recommendations.json",
            "cards": [],
            "simulated_only": True,
            "recommendation_only": True,
            "cached_non_recursive": True,
            "error": str(exc),
        }


def build_pack_157_least_privilege_recommendation_html_section():
    try:
        from tower.least_privilege_recommendation_engine import build_least_privilege_recommendation_html_section
        return build_least_privilege_recommendation_html_section()
    except Exception as exc:
        return f"""
        <section class="tower-section least-privilege-recommendation-section" id="least-privilege-recommendations">
            <div class="tower-section-heading">
                <p class="tower-kicker">Pack 157</p>
                <h2>Least-Privilege Recommendations</h2>
                <p>Least-privilege recommendation section needs review: {exc}</p>
                <a class="tower-link-pill" href="/tower/least-privilege-recommendations.json">Open least-privilege recommendations JSON</a>
            </div>
        </section>
        """


def append_pack_157_least_privilege_recommendation_section(sections):
    """
    Append Pack 157 section to list-like unified section payloads.
    Safe if called more than once.
    """
    try:
        if not isinstance(sections, list):
            return sections

        existing_ids = {
            str(item.get("section_id") or item.get("id"))
            for item in sections
            if isinstance(item, dict)
        }

        if "least_privilege_recommendations" not in existing_ids:
            sections.append(build_pack_157_least_privilege_recommendation_unified_section())

        return sections
    except Exception:
        return sections
# === PACK 157 LEAST PRIVILEGE RECOMMENDATION UNIFIED SECTION END ===



# === PACK 158 POLICY CHANGE RISK SCORE UNIFIED SECTION START ===
def build_pack_158_policy_change_risk_score_unified_section():
    """
    Pack 158 unified owner section.

    Safe/non-recursive:
    - reads only policy_change_risk_score
    - does not call quick actions
    - does not call full unified page builder
    """
    try:
        from tower.policy_change_risk_score import build_policy_change_risk_score_unified_owner_section
        return build_policy_change_risk_score_unified_owner_section()
    except Exception as exc:
        return {
            "section_id": "policy_change_risk_score",
            "title": "Policy Change Risk Score",
            "subtitle": "Policy change risk score section needs review.",
            "status": "review",
            "href": "/tower/policy-change-risk-score.json",
            "cards": [],
            "simulated_only": True,
            "scoring_only": True,
            "recommendation_only": True,
            "cached_non_recursive": True,
            "error": str(exc),
        }


def build_pack_158_policy_change_risk_score_html_section():
    try:
        from tower.policy_change_risk_score import build_policy_change_risk_score_html_section
        return build_policy_change_risk_score_html_section()
    except Exception as exc:
        return f"""
        <section class="tower-section policy-change-risk-score-section" id="policy-change-risk-score">
            <div class="tower-section-heading">
                <p class="tower-kicker">Pack 158</p>
                <h2>Policy Change Risk Score</h2>
                <p>Policy change risk score section needs review: {exc}</p>
                <a class="tower-link-pill" href="/tower/policy-change-risk-score.json">Open policy change risk score JSON</a>
            </div>
        </section>
        """


def append_pack_158_policy_change_risk_score_section(sections):
    """
    Append Pack 158 section to list-like unified section payloads.
    Safe if called more than once.
    """
    try:
        if not isinstance(sections, list):
            return sections

        existing_ids = {
            str(item.get("section_id") or item.get("id"))
            for item in sections
            if isinstance(item, dict)
        }

        if "policy_change_risk_score" not in existing_ids:
            sections.append(build_pack_158_policy_change_risk_score_unified_section())

        return sections
    except Exception:
        return sections
# === PACK 158 POLICY CHANGE RISK SCORE UNIFIED SECTION END ===



# === PACK 159 POLICY CHANGE APPROVAL GATE UNIFIED SECTION START ===
def build_pack_159_policy_change_approval_gate_unified_section():
    """
    Pack 159 unified owner section.

    Safe/non-recursive:
    - reads only policy_change_approval_gate
    - does not call quick actions
    - does not call full unified page builder
    """
    try:
        from tower.policy_change_approval_gate import build_policy_change_approval_gate_unified_owner_section
        return build_policy_change_approval_gate_unified_owner_section()
    except Exception as exc:
        return {
            "section_id": "policy_change_approval_gate",
            "title": "Policy Change Approval Gate",
            "subtitle": "Policy change approval gate section needs review.",
            "status": "review",
            "href": "/tower/policy-change-approval-gate.json",
            "cards": [],
            "simulated_only": True,
            "approval_preview_only": True,
            "gate_preview_only": True,
            "cached_non_recursive": True,
            "error": str(exc),
        }


def build_pack_159_policy_change_approval_gate_html_section():
    try:
        from tower.policy_change_approval_gate import build_policy_change_approval_gate_html_section
        return build_policy_change_approval_gate_html_section()
    except Exception as exc:
        return f"""
        <section class="tower-section policy-change-approval-gate-section" id="policy-change-approval-gate">
            <div class="tower-section-heading">
                <p class="tower-kicker">Pack 159</p>
                <h2>Policy Change Approval Gate</h2>
                <p>Policy change approval gate section needs review: {exc}</p>
                <a class="tower-link-pill" href="/tower/policy-change-approval-gate.json">Open policy change approval gate JSON</a>
            </div>
        </section>
        """


def append_pack_159_policy_change_approval_gate_section(sections):
    """
    Append Pack 159 section to list-like unified section payloads.
    Safe if called more than once.
    """
    try:
        if not isinstance(sections, list):
            return sections

        existing_ids = {
            str(item.get("section_id") or item.get("id"))
            for item in sections
            if isinstance(item, dict)
        }

        if "policy_change_approval_gate" not in existing_ids:
            sections.append(build_pack_159_policy_change_approval_gate_unified_section())

        return sections
    except Exception:
        return sections
# === PACK 159 POLICY CHANGE APPROVAL GATE UNIFIED SECTION END ===



# === PACK 160 POLICY CHANGE APPROVAL RECEIPT PREVIEW UNIFIED SECTION START ===
def build_pack_160_policy_change_approval_receipt_preview_unified_section():
    """
    Pack 160 unified owner section.

    Safe/non-recursive:
    - reads only policy_change_approval_receipt_preview
    - does not call quick actions
    - does not call full unified page builder
    """
    try:
        from tower.policy_change_approval_receipt_preview import build_policy_change_approval_receipt_preview_unified_owner_section
        return build_policy_change_approval_receipt_preview_unified_owner_section()
    except Exception as exc:
        return {
            "section_id": "policy_change_approval_receipt_preview",
            "title": "Policy Change Approval Receipts",
            "subtitle": "Policy change approval receipt preview section needs review.",
            "status": "review",
            "href": "/tower/policy-change-approval-receipt-preview.json",
            "cards": [],
            "simulated_only": True,
            "receipt_preview_only": True,
            "approval_preview_only": True,
            "evidence_preview_only": True,
            "cached_non_recursive": True,
            "error": str(exc),
        }


def build_pack_160_policy_change_approval_receipt_preview_html_section():
    try:
        from tower.policy_change_approval_receipt_preview import build_policy_change_approval_receipt_preview_html_section
        return build_policy_change_approval_receipt_preview_html_section()
    except Exception as exc:
        return f"""
        <section class="tower-section policy-change-approval-receipt-section" id="policy-change-approval-receipt-preview">
            <div class="tower-section-heading">
                <p class="tower-kicker">Pack 160</p>
                <h2>Policy Change Approval Receipts</h2>
                <p>Policy change approval receipt preview section needs review: {exc}</p>
                <a class="tower-link-pill" href="/tower/policy-change-approval-receipt-preview.json">Open policy change approval receipt preview JSON</a>
            </div>
        </section>
        """


def append_pack_160_policy_change_approval_receipt_preview_section(sections):
    """
    Append Pack 160 section to list-like unified section payloads.
    Safe if called more than once.
    """
    try:
        if not isinstance(sections, list):
            return sections

        existing_ids = {
            str(item.get("section_id") or item.get("id"))
            for item in sections
            if isinstance(item, dict)
        }

        if "policy_change_approval_receipt_preview" not in existing_ids:
            sections.append(build_pack_160_policy_change_approval_receipt_preview_unified_section())

        return sections
    except Exception:
        return sections
# === PACK 160 POLICY CHANGE APPROVAL RECEIPT PREVIEW UNIFIED SECTION END ===



# === PACK 161 POLICY CHANGE APPROVAL RECEIPT VAULT INDEX UNIFIED SECTION START ===
def build_pack_161_policy_change_approval_receipt_vault_index_unified_section():
    """
    Pack 161 unified owner section.

    Safe/non-recursive:
    - reads only policy_change_approval_receipt_vault_index
    - does not call quick actions
    - does not call full unified page builder
    """
    try:
        from tower.policy_change_approval_receipt_vault_index import build_policy_change_approval_receipt_vault_index_unified_owner_section
        return build_policy_change_approval_receipt_vault_index_unified_owner_section()
    except Exception as exc:
        return {
            "section_id": "policy_change_approval_receipt_vault_index",
            "title": "Approval Receipt Vault Index",
            "subtitle": "Approval receipt vault/index section needs review.",
            "status": "review",
            "href": "/tower/policy-change-approval-receipt-vault-index.json",
            "cards": [],
            "simulated_only": True,
            "vault_preview_only": True,
            "index_preview_only": True,
            "receipt_preview_only": True,
            "approval_preview_only": True,
            "evidence_preview_only": True,
            "cached_non_recursive": True,
            "error": str(exc),
        }


def build_pack_161_policy_change_approval_receipt_vault_index_html_section():
    try:
        from tower.policy_change_approval_receipt_vault_index import build_policy_change_approval_receipt_vault_index_html_section
        return build_policy_change_approval_receipt_vault_index_html_section()
    except Exception as exc:
        return f"""
        <section class="tower-section policy-change-approval-receipt-vault-section" id="policy-change-approval-receipt-vault-index">
            <div class="tower-section-heading">
                <p class="tower-kicker">Pack 161</p>
                <h2>Approval Receipt Vault Index</h2>
                <p>Approval receipt vault/index section needs review: {exc}</p>
                <a class="tower-link-pill" href="/tower/policy-change-approval-receipt-vault-index.json">Open approval receipt vault index JSON</a>
            </div>
        </section>
        """


def append_pack_161_policy_change_approval_receipt_vault_index_section(sections):
    """
    Append Pack 161 section to list-like unified section payloads.
    Safe if called more than once.
    """
    try:
        if not isinstance(sections, list):
            return sections

        existing_ids = {
            str(item.get("section_id") or item.get("id"))
            for item in sections
            if isinstance(item, dict)
        }

        if "policy_change_approval_receipt_vault_index" not in existing_ids:
            sections.append(build_pack_161_policy_change_approval_receipt_vault_index_unified_section())

        return sections
    except Exception:
        return sections
# === PACK 161 POLICY CHANGE APPROVAL RECEIPT VAULT INDEX UNIFIED SECTION END ===



# === PACK 162 POLICY CHANGE APPROVAL RECEIPT EXPIRATION RULES UNIFIED SECTION START ===
def build_pack_162_policy_change_approval_receipt_expiration_rules_unified_section():
    """
    Pack 162 unified owner section.

    Safe/non-recursive:
    - reads only policy_change_approval_receipt_expiration_rules
    - does not call quick actions
    - does not call full unified page builder
    """
    try:
        from tower.policy_change_approval_receipt_expiration_rules import build_policy_change_approval_receipt_expiration_rules_unified_owner_section
        return build_policy_change_approval_receipt_expiration_rules_unified_owner_section()
    except Exception as exc:
        return {
            "section_id": "policy_change_approval_receipt_expiration_rules",
            "title": "Approval Receipt Expiration Rules",
            "subtitle": "Approval receipt expiration rules section needs review.",
            "status": "review",
            "href": "/tower/policy-change-approval-receipt-expiration-rules.json",
            "cards": [],
            "simulated_only": True,
            "expiration_preview_only": True,
            "renewal_preview_only": True,
            "recheck_preview_only": True,
            "vault_preview_only": True,
            "index_preview_only": True,
            "receipt_preview_only": True,
            "approval_preview_only": True,
            "evidence_preview_only": True,
            "cached_non_recursive": True,
            "error": str(exc),
        }


def build_pack_162_policy_change_approval_receipt_expiration_rules_html_section():
    try:
        from tower.policy_change_approval_receipt_expiration_rules import build_policy_change_approval_receipt_expiration_rules_html_section
        return build_policy_change_approval_receipt_expiration_rules_html_section()
    except Exception as exc:
        return f"""
        <section class="tower-section policy-change-approval-receipt-expiration-section" id="policy-change-approval-receipt-expiration-rules">
            <div class="tower-section-heading">
                <p class="tower-kicker">Pack 162</p>
                <h2>Approval Receipt Expiration Rules</h2>
                <p>Approval receipt expiration rules section needs review: {exc}</p>
                <a class="tower-link-pill" href="/tower/policy-change-approval-receipt-expiration-rules.json">Open approval receipt expiration rules JSON</a>
            </div>
        </section>
        """


def append_pack_162_policy_change_approval_receipt_expiration_rules_section(sections):
    """
    Append Pack 162 section to list-like unified section payloads.
    Safe if called more than once.
    """
    try:
        if not isinstance(sections, list):
            return sections

        existing_ids = {
            str(item.get("section_id") or item.get("id"))
            for item in sections
            if isinstance(item, dict)
        }

        if "policy_change_approval_receipt_expiration_rules" not in existing_ids:
            sections.append(build_pack_162_policy_change_approval_receipt_expiration_rules_unified_section())

        return sections
    except Exception:
        return sections
# === PACK 162 POLICY CHANGE APPROVAL RECEIPT EXPIRATION RULES UNIFIED SECTION END ===



# === PACK 163 POLICY CHANGE APPROVAL RECEIPT RENEWAL RECHECK QUEUE UNIFIED SECTION START ===
def build_pack_163_policy_change_approval_receipt_renewal_recheck_queue_unified_section():
    """
    Pack 163 unified owner section.

    Safe/non-recursive:
    - reads only policy_change_approval_receipt_renewal_recheck_queue
    - does not call quick actions
    - does not call full unified page builder
    """
    try:
        from tower.policy_change_approval_receipt_renewal_recheck_queue import build_policy_change_approval_receipt_renewal_recheck_queue_unified_owner_section
        return build_policy_change_approval_receipt_renewal_recheck_queue_unified_owner_section()
    except Exception as exc:
        return {
            "section_id": "policy_change_approval_receipt_renewal_recheck_queue",
            "title": "Approval Receipt Renewal Queue",
            "subtitle": "Approval receipt renewal/recheck queue section needs review.",
            "status": "review",
            "href": "/tower/policy-change-approval-receipt-renewal-recheck-queue.json",
            "cards": [],
            "simulated_only": True,
            "queue_preview_only": True,
            "renewal_preview_only": True,
            "recheck_preview_only": True,
            "expiration_preview_only": True,
            "vault_preview_only": True,
            "index_preview_only": True,
            "receipt_preview_only": True,
            "approval_preview_only": True,
            "evidence_preview_only": True,
            "cached_non_recursive": True,
            "error": str(exc),
        }


def build_pack_163_policy_change_approval_receipt_renewal_recheck_queue_html_section():
    try:
        from tower.policy_change_approval_receipt_renewal_recheck_queue import build_policy_change_approval_receipt_renewal_recheck_queue_html_section
        return build_policy_change_approval_receipt_renewal_recheck_queue_html_section()
    except Exception as exc:
        return f"""
        <section class="tower-section policy-change-approval-receipt-renewal-section" id="policy-change-approval-receipt-renewal-recheck-queue">
            <div class="tower-section-heading">
                <p class="tower-kicker">Pack 163</p>
                <h2>Approval Receipt Renewal Queue</h2>
                <p>Approval receipt renewal/recheck queue section needs review: {exc}</p>
                <a class="tower-link-pill" href="/tower/policy-change-approval-receipt-renewal-recheck-queue.json">Open approval receipt renewal queue JSON</a>
            </div>
        </section>
        """


def append_pack_163_policy_change_approval_receipt_renewal_recheck_queue_section(sections):
    """
    Append Pack 163 section to list-like unified section payloads.
    Safe if called more than once.
    """
    try:
        if not isinstance(sections, list):
            return sections

        existing_ids = {
            str(item.get("section_id") or item.get("id"))
            for item in sections
            if isinstance(item, dict)
        }

        if "policy_change_approval_receipt_renewal_recheck_queue" not in existing_ids:
            sections.append(build_pack_163_policy_change_approval_receipt_renewal_recheck_queue_unified_section())

        return sections
    except Exception:
        return sections
# === PACK 163 POLICY CHANGE APPROVAL RECEIPT RENEWAL RECHECK QUEUE UNIFIED SECTION END ===



# === PACK 164 POLICY CHANGE APPROVAL RECEIPT OWNER REVIEW QUEUE UNIFIED SECTION START ===
def build_pack_164_policy_change_approval_receipt_owner_review_queue_unified_section():
    """
    Pack 164 unified owner section.

    Safe/non-recursive:
    - reads only policy_change_approval_receipt_owner_review_queue
    - does not call quick actions
    - does not call full unified page builder
    """
    try:
        from tower.policy_change_approval_receipt_owner_review_queue import build_policy_change_approval_receipt_owner_review_queue_unified_owner_section
        return build_policy_change_approval_receipt_owner_review_queue_unified_owner_section()
    except Exception as exc:
        return {
            "section_id": "policy_change_approval_receipt_owner_review_queue",
            "title": "Approval Receipt Owner Review",
            "subtitle": "Approval receipt owner review queue section needs review.",
            "status": "review",
            "href": "/tower/policy-change-approval-receipt-owner-review-queue.json",
            "cards": [],
            "simulated_only": True,
            "owner_review_preview_only": True,
            "queue_preview_only": True,
            "renewal_preview_only": True,
            "recheck_preview_only": True,
            "expiration_preview_only": True,
            "vault_preview_only": True,
            "index_preview_only": True,
            "receipt_preview_only": True,
            "approval_preview_only": True,
            "evidence_preview_only": True,
            "cached_non_recursive": True,
            "error": str(exc),
        }


def build_pack_164_policy_change_approval_receipt_owner_review_queue_html_section():
    try:
        from tower.policy_change_approval_receipt_owner_review_queue import build_policy_change_approval_receipt_owner_review_queue_html_section
        return build_policy_change_approval_receipt_owner_review_queue_html_section()
    except Exception as exc:
        return f"""
        <section class="tower-section policy-change-approval-receipt-owner-review-section" id="policy-change-approval-receipt-owner-review-queue">
            <div class="tower-section-heading">
                <p class="tower-kicker">Pack 164</p>
                <h2>Approval Receipt Owner Review</h2>
                <p>Approval receipt owner review queue section needs review: {exc}</p>
                <a class="tower-link-pill" href="/tower/policy-change-approval-receipt-owner-review-queue.json">Open approval receipt owner review JSON</a>
            </div>
        </section>
        """


def append_pack_164_policy_change_approval_receipt_owner_review_queue_section(sections):
    """
    Append Pack 164 section to list-like unified section payloads.
    Safe if called more than once.
    """
    try:
        if not isinstance(sections, list):
            return sections

        existing_ids = {
            str(item.get("section_id") or item.get("id"))
            for item in sections
            if isinstance(item, dict)
        }

        if "policy_change_approval_receipt_owner_review_queue" not in existing_ids:
            sections.append(build_pack_164_policy_change_approval_receipt_owner_review_queue_unified_section())

        return sections
    except Exception:
        return sections
# === PACK 164 POLICY CHANGE APPROVAL RECEIPT OWNER REVIEW QUEUE UNIFIED SECTION END ===



# === PACK 165 POLICY CHANGE APPROVAL RECEIPT DETAIL EVIDENCE DRAWER UNIFIED SECTION START ===
def build_pack_165_policy_change_approval_receipt_detail_evidence_drawer_unified_section():
    """
    Pack 165 unified owner section.

    Safe/non-recursive:
    - reads only policy_change_approval_receipt_detail_evidence_drawer
    - does not call quick actions
    - does not call full unified page builder
    """
    try:
        from tower.policy_change_approval_receipt_detail_evidence_drawer import build_policy_change_approval_receipt_detail_evidence_drawer_unified_owner_section
        return build_policy_change_approval_receipt_detail_evidence_drawer_unified_owner_section()
    except Exception as exc:
        return {
            "section_id": "policy_change_approval_receipt_detail_evidence_drawer",
            "title": "Approval Receipt Evidence Drawer",
            "subtitle": "Approval receipt evidence drawer section needs review.",
            "status": "review",
            "href": "/tower/policy-change-approval-receipt-detail-evidence-drawer.json",
            "cards": [],
            "simulated_only": True,
            "detail_preview_only": True,
            "evidence_drawer_preview_only": True,
            "owner_review_preview_only": True,
            "queue_preview_only": True,
            "renewal_preview_only": True,
            "recheck_preview_only": True,
            "expiration_preview_only": True,
            "vault_preview_only": True,
            "index_preview_only": True,
            "receipt_preview_only": True,
            "approval_preview_only": True,
            "evidence_preview_only": True,
            "cached_non_recursive": True,
            "error": str(exc),
        }


def build_pack_165_policy_change_approval_receipt_detail_evidence_drawer_html_section():
    try:
        from tower.policy_change_approval_receipt_detail_evidence_drawer import build_policy_change_approval_receipt_detail_evidence_drawer_html_section
        return build_policy_change_approval_receipt_detail_evidence_drawer_html_section()
    except Exception as exc:
        return f"""
        <section class="tower-section policy-change-approval-receipt-detail-section" id="policy-change-approval-receipt-detail-evidence-drawer">
            <div class="tower-section-heading">
                <p class="tower-kicker">Pack 165</p>
                <h2>Approval Receipt Evidence Drawer</h2>
                <p>Approval receipt detail/evidence drawer section needs review: {exc}</p>
                <a class="tower-link-pill" href="/tower/policy-change-approval-receipt-detail-evidence-drawer.json">Open approval receipt evidence drawer JSON</a>
            </div>
        </section>
        """


def append_pack_165_policy_change_approval_receipt_detail_evidence_drawer_section(sections):
    """
    Append Pack 165 section to list-like unified section payloads.
    Safe if called more than once.
    """
    try:
        if not isinstance(sections, list):
            return sections

        existing_ids = {
            str(item.get("section_id") or item.get("id"))
            for item in sections
            if isinstance(item, dict)
        }

        if "policy_change_approval_receipt_detail_evidence_drawer" not in existing_ids:
            sections.append(build_pack_165_policy_change_approval_receipt_detail_evidence_drawer_unified_section())

        return sections
    except Exception:
        return sections
# === PACK 165 POLICY CHANGE APPROVAL RECEIPT DETAIL EVIDENCE DRAWER UNIFIED SECTION END ===



# === PACK 166 POLICY CHANGE APPROVAL RECEIPT EVIDENCE DRAWER LOOKUP UNIFIED SECTION START ===
def build_pack_166_policy_change_approval_receipt_evidence_drawer_lookup_unified_section():
    """
    Pack 166 unified owner section.

    Safe/non-recursive:
    - reads only policy_change_approval_receipt_evidence_drawer_lookup
    - does not call quick actions
    - does not call full unified page builder
    """
    try:
        from tower.policy_change_approval_receipt_evidence_drawer_lookup import build_policy_change_approval_receipt_evidence_drawer_lookup_unified_owner_section
        return build_policy_change_approval_receipt_evidence_drawer_lookup_unified_owner_section()
    except Exception as exc:
        return {
            "section_id": "policy_change_approval_receipt_evidence_drawer_lookup",
            "title": "Evidence Drawer Lookup",
            "subtitle": "Approval receipt evidence drawer lookup section needs review.",
            "status": "review",
            "href": "/tower/policy-change-approval-receipt-evidence-drawer-lookup.json",
            "cards": [],
            "simulated_only": True,
            "lookup_preview_only": True,
            "detail_preview_only": True,
            "evidence_drawer_preview_only": True,
            "owner_review_preview_only": True,
            "queue_preview_only": True,
            "renewal_preview_only": True,
            "recheck_preview_only": True,
            "expiration_preview_only": True,
            "vault_preview_only": True,
            "index_preview_only": True,
            "receipt_preview_only": True,
            "approval_preview_only": True,
            "evidence_preview_only": True,
            "cached_non_recursive": True,
            "error": str(exc),
        }


def build_pack_166_policy_change_approval_receipt_evidence_drawer_lookup_html_section():
    try:
        from tower.policy_change_approval_receipt_evidence_drawer_lookup import build_policy_change_approval_receipt_evidence_drawer_lookup_html_section
        return build_policy_change_approval_receipt_evidence_drawer_lookup_html_section()
    except Exception as exc:
        return f"""
        <section class="tower-section policy-change-approval-receipt-lookup-section" id="policy-change-approval-receipt-evidence-drawer-lookup">
            <div class="tower-section-heading">
                <p class="tower-kicker">Pack 166</p>
                <h2>Evidence Drawer Lookup</h2>
                <p>Approval receipt evidence drawer lookup section needs review: {exc}</p>
                <a class="tower-link-pill" href="/tower/policy-change-approval-receipt-evidence-drawer-lookup.json">Open evidence drawer lookup JSON</a>
            </div>
        </section>
        """


def append_pack_166_policy_change_approval_receipt_evidence_drawer_lookup_section(sections):
    """
    Append Pack 166 section to list-like unified section payloads.
    Safe if called more than once.
    """
    try:
        if not isinstance(sections, list):
            return sections

        existing_ids = {
            str(item.get("section_id") or item.get("id"))
            for item in sections
            if isinstance(item, dict)
        }

        if "policy_change_approval_receipt_evidence_drawer_lookup" not in existing_ids:
            sections.append(build_pack_166_policy_change_approval_receipt_evidence_drawer_lookup_unified_section())

        return sections
    except Exception:
        return sections
# === PACK 166 POLICY CHANGE APPROVAL RECEIPT EVIDENCE DRAWER LOOKUP UNIFIED SECTION END ===



# === PACK 167 POLICY CHANGE APPROVAL RECEIPT FILTER LANES SEARCH FACETS UNIFIED SECTION START ===
def build_pack_167_policy_change_approval_receipt_filter_lanes_search_facets_unified_section():
    """
    Pack 167 unified owner section.

    Safe/non-recursive:
    - reads only policy_change_approval_receipt_filter_lanes_search_facets
    - does not call quick actions
    - does not call full unified page builder
    """
    try:
        from tower.policy_change_approval_receipt_filter_lanes_search_facets import build_policy_change_approval_receipt_filter_lanes_search_facets_unified_owner_section
        return build_policy_change_approval_receipt_filter_lanes_search_facets_unified_owner_section()
    except Exception as exc:
        return {
            "section_id": "policy_change_approval_receipt_filter_lanes_search_facets",
            "title": "Evidence Drawer Filters",
            "subtitle": "Evidence drawer filter/search facets section needs review.",
            "status": "review",
            "href": "/tower/policy-change-approval-receipt-filter-lanes-search-facets.json",
            "cards": [],
            "simulated_only": True,
            "filter_preview_only": True,
            "search_facet_preview_only": True,
            "lookup_preview_only": True,
            "detail_preview_only": True,
            "evidence_drawer_preview_only": True,
            "owner_review_preview_only": True,
            "queue_preview_only": True,
            "renewal_preview_only": True,
            "recheck_preview_only": True,
            "expiration_preview_only": True,
            "vault_preview_only": True,
            "index_preview_only": True,
            "receipt_preview_only": True,
            "approval_preview_only": True,
            "evidence_preview_only": True,
            "cached_non_recursive": True,
            "error": str(exc),
        }


def build_pack_167_policy_change_approval_receipt_filter_lanes_search_facets_html_section():
    try:
        from tower.policy_change_approval_receipt_filter_lanes_search_facets import build_policy_change_approval_receipt_filter_lanes_search_facets_html_section
        return build_policy_change_approval_receipt_filter_lanes_search_facets_html_section()
    except Exception as exc:
        return f"""
        <section class="tower-section policy-change-approval-receipt-filter-section" id="policy-change-approval-receipt-filter-lanes-search-facets">
            <div class="tower-section-heading">
                <p class="tower-kicker">Pack 167</p>
                <h2>Evidence Drawer Filters</h2>
                <p>Evidence drawer filter/search facets section needs review: {exc}</p>
                <a class="tower-link-pill" href="/tower/policy-change-approval-receipt-filter-lanes-search-facets.json">Open evidence drawer filters JSON</a>
            </div>
        </section>
        """


def append_pack_167_policy_change_approval_receipt_filter_lanes_search_facets_section(sections):
    """
    Append Pack 167 section to list-like unified section payloads.
    Safe if called more than once.
    """
    try:
        if not isinstance(sections, list):
            return sections

        existing_ids = {
            str(item.get("section_id") or item.get("id"))
            for item in sections
            if isinstance(item, dict)
        }

        if "policy_change_approval_receipt_filter_lanes_search_facets" not in existing_ids:
            sections.append(build_pack_167_policy_change_approval_receipt_filter_lanes_search_facets_unified_section())

        return sections
    except Exception:
        return sections
# === PACK 167 POLICY CHANGE APPROVAL RECEIPT FILTER LANES SEARCH FACETS UNIFIED SECTION END ===



# === PACK 168 POLICY CHANGE APPROVAL RECEIPT SAVED VIEWS FILTER PRESETS UNIFIED SECTION START ===
def build_pack_168_policy_change_approval_receipt_saved_views_filter_presets_unified_section():
    """
    Pack 168 unified owner section.

    Safe/non-recursive:
    - reads only policy_change_approval_receipt_saved_views_filter_presets
    - does not call quick actions
    - does not call full unified page builder
    """
    try:
        from tower.policy_change_approval_receipt_saved_views_filter_presets import build_policy_change_approval_receipt_saved_views_filter_presets_unified_owner_section
        return build_policy_change_approval_receipt_saved_views_filter_presets_unified_owner_section()
    except Exception as exc:
        return {
            "section_id": "policy_change_approval_receipt_saved_views_filter_presets",
            "title": "Evidence Drawer Saved Views",
            "subtitle": "Evidence drawer saved views/filter presets section needs review.",
            "status": "review",
            "href": "/tower/policy-change-approval-receipt-saved-views-filter-presets.json",
            "cards": [],
            "simulated_only": True,
            "saved_view_preview_only": True,
            "filter_preset_preview_only": True,
            "filter_preview_only": True,
            "search_facet_preview_only": True,
            "lookup_preview_only": True,
            "detail_preview_only": True,
            "evidence_drawer_preview_only": True,
            "owner_review_preview_only": True,
            "queue_preview_only": True,
            "renewal_preview_only": True,
            "recheck_preview_only": True,
            "expiration_preview_only": True,
            "vault_preview_only": True,
            "index_preview_only": True,
            "receipt_preview_only": True,
            "approval_preview_only": True,
            "evidence_preview_only": True,
            "cached_non_recursive": True,
            "error": str(exc),
        }


def build_pack_168_policy_change_approval_receipt_saved_views_filter_presets_html_section():
    try:
        from tower.policy_change_approval_receipt_saved_views_filter_presets import build_policy_change_approval_receipt_saved_views_filter_presets_html_section
        return build_policy_change_approval_receipt_saved_views_filter_presets_html_section()
    except Exception as exc:
        return f"""
        <section class="tower-section policy-change-approval-receipt-saved-view-section" id="policy-change-approval-receipt-saved-views-filter-presets">
            <div class="tower-section-heading">
                <p class="tower-kicker">Pack 168</p>
                <h2>Evidence Drawer Saved Views</h2>
                <p>Evidence drawer saved views/filter presets section needs review: {exc}</p>
                <a class="tower-link-pill" href="/tower/policy-change-approval-receipt-saved-views-filter-presets.json">Open evidence drawer saved views JSON</a>
            </div>
        </section>
        """


def append_pack_168_policy_change_approval_receipt_saved_views_filter_presets_section(sections):
    """
    Append Pack 168 section to list-like unified section payloads.
    Safe if called more than once.
    """
    try:
        if not isinstance(sections, list):
            return sections

        existing_ids = {
            str(item.get("section_id") or item.get("id"))
            for item in sections
            if isinstance(item, dict)
        }

        if "policy_change_approval_receipt_saved_views_filter_presets" not in existing_ids:
            sections.append(build_pack_168_policy_change_approval_receipt_saved_views_filter_presets_unified_section())

        return sections
    except Exception:
        return sections
# === PACK 168 POLICY CHANGE APPROVAL RECEIPT SAVED VIEWS FILTER PRESETS UNIFIED SECTION END ===



# === PACK 169 POLICY CHANGE APPROVAL RECEIPT OWNER NOTES REVIEW DRAFTS UNIFIED SECTION START ===
def build_pack_169_policy_change_approval_receipt_owner_notes_review_drafts_unified_section():
    """
    Pack 169 unified owner section.

    Safe/non-recursive:
    - reads only policy_change_approval_receipt_owner_notes_review_drafts
    - does not call quick actions
    - does not call full unified page builder
    """
    try:
        from tower.policy_change_approval_receipt_owner_notes_review_drafts import build_policy_change_approval_receipt_owner_notes_review_drafts_unified_owner_section
        return build_policy_change_approval_receipt_owner_notes_review_drafts_unified_owner_section()
    except Exception as exc:
        return {
            "section_id": "policy_change_approval_receipt_owner_notes_review_drafts",
            "title": "Evidence Drawer Owner Notes",
            "subtitle": "Evidence drawer owner notes/review drafts section needs review.",
            "status": "review",
            "href": "/tower/policy-change-approval-receipt-owner-notes-review-drafts.json",
            "cards": [],
            "simulated_only": True,
            "owner_note_preview_only": True,
            "review_draft_preview_only": True,
            "saved_view_preview_only": True,
            "filter_preset_preview_only": True,
            "filter_preview_only": True,
            "search_facet_preview_only": True,
            "lookup_preview_only": True,
            "detail_preview_only": True,
            "evidence_drawer_preview_only": True,
            "owner_review_preview_only": True,
            "queue_preview_only": True,
            "renewal_preview_only": True,
            "recheck_preview_only": True,
            "expiration_preview_only": True,
            "vault_preview_only": True,
            "index_preview_only": True,
            "receipt_preview_only": True,
            "approval_preview_only": True,
            "evidence_preview_only": True,
            "cached_non_recursive": True,
            "error": str(exc),
        }


def build_pack_169_policy_change_approval_receipt_owner_notes_review_drafts_html_section():
    try:
        from tower.policy_change_approval_receipt_owner_notes_review_drafts import build_policy_change_approval_receipt_owner_notes_review_drafts_html_section
        return build_policy_change_approval_receipt_owner_notes_review_drafts_html_section()
    except Exception as exc:
        return f"""
        <section class="tower-section policy-change-approval-receipt-owner-note-section" id="policy-change-approval-receipt-owner-notes-review-drafts">
            <div class="tower-section-heading">
                <p class="tower-kicker">Pack 169</p>
                <h2>Evidence Drawer Owner Notes</h2>
                <p>Evidence drawer owner notes/review drafts section needs review: {exc}</p>
                <a class="tower-link-pill" href="/tower/policy-change-approval-receipt-owner-notes-review-drafts.json">Open evidence drawer owner notes JSON</a>
            </div>
        </section>
        """


def append_pack_169_policy_change_approval_receipt_owner_notes_review_drafts_section(sections):
    """
    Append Pack 169 section to list-like unified section payloads.
    Safe if called more than once.
    """
    try:
        if not isinstance(sections, list):
            return sections

        existing_ids = {
            str(item.get("section_id") or item.get("id"))
            for item in sections
            if isinstance(item, dict)
        }

        if "policy_change_approval_receipt_owner_notes_review_drafts" not in existing_ids:
            sections.append(build_pack_169_policy_change_approval_receipt_owner_notes_review_drafts_unified_section())

        return sections
    except Exception:
        return sections
# === PACK 169 POLICY CHANGE APPROVAL RECEIPT OWNER NOTES REVIEW DRAFTS UNIFIED SECTION END ===



# === PACK 170 POLICY CHANGE APPROVAL RECEIPT OWNER NOTE DRAFT DETAIL EDIT PREVIEW UNIFIED SECTION START ===
def build_pack_170_policy_change_approval_receipt_owner_note_draft_detail_edit_preview_unified_section():
    """
    Pack 170 unified owner section.

    Safe/non-recursive:
    - reads only policy_change_approval_receipt_owner_note_draft_detail_edit_preview
    - does not call quick actions
    - does not call full unified page builder
    """
    try:
        from tower.policy_change_approval_receipt_owner_note_draft_detail_edit_preview import build_policy_change_approval_receipt_owner_note_draft_detail_edit_preview_unified_owner_section
        return build_policy_change_approval_receipt_owner_note_draft_detail_edit_preview_unified_owner_section()
    except Exception as exc:
        return {
            "section_id": "policy_change_approval_receipt_owner_note_draft_detail_edit_preview",
            "title": "Owner Note Draft Edit Preview",
            "subtitle": "Owner note draft detail/edit preview section needs review.",
            "status": "review",
            "href": "/tower/policy-change-approval-receipt-owner-note-draft-detail-edit-preview.json",
            "cards": [],
            "simulated_only": True,
            "edit_preview_only": True,
            "detail_drawer_preview_only": True,
            "owner_note_preview_only": True,
            "review_draft_preview_only": True,
            "saved_view_preview_only": True,
            "filter_preset_preview_only": True,
            "filter_preview_only": True,
            "search_facet_preview_only": True,
            "lookup_preview_only": True,
            "detail_preview_only": True,
            "evidence_drawer_preview_only": True,
            "owner_review_preview_only": True,
            "queue_preview_only": True,
            "renewal_preview_only": True,
            "recheck_preview_only": True,
            "expiration_preview_only": True,
            "vault_preview_only": True,
            "index_preview_only": True,
            "receipt_preview_only": True,
            "approval_preview_only": True,
            "evidence_preview_only": True,
            "cached_non_recursive": True,
            "error": str(exc),
        }


def build_pack_170_policy_change_approval_receipt_owner_note_draft_detail_edit_preview_html_section():
    try:
        from tower.policy_change_approval_receipt_owner_note_draft_detail_edit_preview import build_policy_change_approval_receipt_owner_note_draft_detail_edit_preview_html_section
        return build_policy_change_approval_receipt_owner_note_draft_detail_edit_preview_html_section()
    except Exception as exc:
        return f"""
        <section class="tower-section policy-change-approval-receipt-owner-note-edit-section" id="policy-change-approval-receipt-owner-note-draft-detail-edit-preview">
            <div class="tower-section-heading">
                <p class="tower-kicker">Pack 170</p>
                <h2>Owner Note Draft Edit Preview</h2>
                <p>Owner note draft detail/edit preview section needs review: {exc}</p>
                <a class="tower-link-pill" href="/tower/policy-change-approval-receipt-owner-note-draft-detail-edit-preview.json">Open owner note draft edit preview JSON</a>
            </div>
        </section>
        """


def append_pack_170_policy_change_approval_receipt_owner_note_draft_detail_edit_preview_section(sections):
    """
    Append Pack 170 section to list-like unified section payloads.
    Safe if called more than once.
    """
    try:
        if not isinstance(sections, list):
            return sections

        existing_ids = {
            str(item.get("section_id") or item.get("id"))
            for item in sections
            if isinstance(item, dict)
        }

        if "policy_change_approval_receipt_owner_note_draft_detail_edit_preview" not in existing_ids:
            sections.append(build_pack_170_policy_change_approval_receipt_owner_note_draft_detail_edit_preview_unified_section())

        return sections
    except Exception:
        return sections
# === PACK 170 POLICY CHANGE APPROVAL RECEIPT OWNER NOTE DRAFT DETAIL EDIT PREVIEW UNIFIED SECTION END ===



# === PACK 171 POLICY CHANGE APPROVAL RECEIPT OWNER NOTE DRAFT EDIT HISTORY VERSION PREVIEW UNIFIED SECTION START ===
def build_pack_171_policy_change_approval_receipt_owner_note_draft_edit_history_version_preview_unified_section():
    """
    Pack 171 unified owner section.

    Safe/non-recursive:
    - reads only policy_change_approval_receipt_owner_note_draft_edit_history_version_preview
    - does not call quick actions
    - does not call full unified page builder
    """
    try:
        from tower.policy_change_approval_receipt_owner_note_draft_edit_history_version_preview import build_policy_change_approval_receipt_owner_note_draft_edit_history_version_preview_unified_owner_section
        return build_policy_change_approval_receipt_owner_note_draft_edit_history_version_preview_unified_owner_section()
    except Exception as exc:
        return {
            "section_id": "policy_change_approval_receipt_owner_note_draft_edit_history_version_preview",
            "title": "Owner Note Version History",
            "subtitle": "Owner note draft edit history/version preview section needs review.",
            "status": "review",
            "href": "/tower/policy-change-approval-receipt-owner-note-draft-edit-history-version-preview.json",
            "cards": [],
            "simulated_only": True,
            "version_preview_only": True,
            "edit_history_preview_only": True,
            "rollback_preview_only": True,
            "compare_preview_only": True,
            "edit_preview_only": True,
            "detail_drawer_preview_only": True,
            "owner_note_preview_only": True,
            "review_draft_preview_only": True,
            "saved_view_preview_only": True,
            "filter_preset_preview_only": True,
            "filter_preview_only": True,
            "search_facet_preview_only": True,
            "lookup_preview_only": True,
            "detail_preview_only": True,
            "evidence_drawer_preview_only": True,
            "owner_review_preview_only": True,
            "queue_preview_only": True,
            "renewal_preview_only": True,
            "recheck_preview_only": True,
            "expiration_preview_only": True,
            "vault_preview_only": True,
            "index_preview_only": True,
            "receipt_preview_only": True,
            "approval_preview_only": True,
            "evidence_preview_only": True,
            "cached_non_recursive": True,
            "error": str(exc),
        }


def build_pack_171_policy_change_approval_receipt_owner_note_draft_edit_history_version_preview_html_section():
    try:
        from tower.policy_change_approval_receipt_owner_note_draft_edit_history_version_preview import build_policy_change_approval_receipt_owner_note_draft_edit_history_version_preview_html_section
        return build_policy_change_approval_receipt_owner_note_draft_edit_history_version_preview_html_section()
    except Exception as exc:
        return f"""
        <section class="tower-section policy-change-approval-receipt-owner-note-history-section" id="policy-change-approval-receipt-owner-note-draft-edit-history-version-preview">
            <div class="tower-section-heading">
                <p class="tower-kicker">Pack 171</p>
                <h2>Owner Note Version History</h2>
                <p>Owner note draft edit history/version preview section needs review: {exc}</p>
                <a class="tower-link-pill" href="/tower/policy-change-approval-receipt-owner-note-draft-edit-history-version-preview.json">Open owner note version history JSON</a>
            </div>
        </section>
        """


def append_pack_171_policy_change_approval_receipt_owner_note_draft_edit_history_version_preview_section(sections):
    """
    Append Pack 171 section to list-like unified section payloads.
    Safe if called more than once.
    """
    try:
        if not isinstance(sections, list):
            return sections

        existing_ids = {
            str(item.get("section_id") or item.get("id"))
            for item in sections
            if isinstance(item, dict)
        }

        if "policy_change_approval_receipt_owner_note_draft_edit_history_version_preview" not in existing_ids:
            sections.append(build_pack_171_policy_change_approval_receipt_owner_note_draft_edit_history_version_preview_unified_section())

        return sections
    except Exception:
        return sections
# === PACK 171 POLICY CHANGE APPROVAL RECEIPT OWNER NOTE DRAFT EDIT HISTORY VERSION PREVIEW UNIFIED SECTION END ===



# === PACK 172 POLICY CHANGE APPROVAL RECEIPT OWNER NOTE DRAFT VERSION DETAIL COMPARE VIEW UNIFIED SECTION START ===
def build_pack_172_policy_change_approval_receipt_owner_note_draft_version_detail_compare_view_unified_section():
    """
    Pack 172 unified owner section.

    Safe/non-recursive:
    - reads only policy_change_approval_receipt_owner_note_draft_version_detail_compare_view
    - does not call quick actions
    - does not call full unified page builder
    """
    try:
        from tower.policy_change_approval_receipt_owner_note_draft_version_detail_compare_view import build_policy_change_approval_receipt_owner_note_draft_version_detail_compare_view_unified_owner_section
        return build_policy_change_approval_receipt_owner_note_draft_version_detail_compare_view_unified_owner_section()
    except Exception as exc:
        return {
            "section_id": "policy_change_approval_receipt_owner_note_draft_version_detail_compare_view",
            "title": "Owner Note Version Compare",
            "subtitle": "Owner note draft version detail/compare view section needs review.",
            "status": "review",
            "href": "/tower/policy-change-approval-receipt-owner-note-draft-version-detail-compare-view.json",
            "cards": [],
            "simulated_only": True,
            "version_detail_preview_only": True,
            "compare_view_preview_only": True,
            "version_preview_only": True,
            "edit_history_preview_only": True,
            "rollback_preview_only": True,
            "compare_preview_only": True,
            "edit_preview_only": True,
            "detail_drawer_preview_only": True,
            "owner_note_preview_only": True,
            "review_draft_preview_only": True,
            "saved_view_preview_only": True,
            "filter_preset_preview_only": True,
            "filter_preview_only": True,
            "search_facet_preview_only": True,
            "lookup_preview_only": True,
            "detail_preview_only": True,
            "evidence_drawer_preview_only": True,
            "owner_review_preview_only": True,
            "queue_preview_only": True,
            "renewal_preview_only": True,
            "recheck_preview_only": True,
            "expiration_preview_only": True,
            "vault_preview_only": True,
            "index_preview_only": True,
            "receipt_preview_only": True,
            "approval_preview_only": True,
            "evidence_preview_only": True,
            "cached_non_recursive": True,
            "error": str(exc),
        }


def build_pack_172_policy_change_approval_receipt_owner_note_draft_version_detail_compare_view_html_section():
    try:
        from tower.policy_change_approval_receipt_owner_note_draft_version_detail_compare_view import build_policy_change_approval_receipt_owner_note_draft_version_detail_compare_view_html_section
        return build_policy_change_approval_receipt_owner_note_draft_version_detail_compare_view_html_section()
    except Exception as exc:
        return f"""
        <section class="tower-section policy-change-approval-receipt-owner-note-version-compare-section" id="policy-change-approval-receipt-owner-note-draft-version-detail-compare-view">
            <div class="tower-section-heading">
                <p class="tower-kicker">Pack 172</p>
                <h2>Owner Note Version Compare</h2>
                <p>Owner note draft version detail/compare view section needs review: {exc}</p>
                <a class="tower-link-pill" href="/tower/policy-change-approval-receipt-owner-note-draft-version-detail-compare-view.json">Open owner note version compare JSON</a>
            </div>
        </section>
        """


def append_pack_172_policy_change_approval_receipt_owner_note_draft_version_detail_compare_view_section(sections):
    """
    Append Pack 172 section to list-like unified section payloads.
    Safe if called more than once.
    """
    try:
        if not isinstance(sections, list):
            return sections

        existing_ids = {
            str(item.get("section_id") or item.get("id"))
            for item in sections
            if isinstance(item, dict)
        }

        if "policy_change_approval_receipt_owner_note_draft_version_detail_compare_view" not in existing_ids:
            sections.append(build_pack_172_policy_change_approval_receipt_owner_note_draft_version_detail_compare_view_unified_section())

        return sections
    except Exception:
        return sections
# === PACK 172 POLICY CHANGE APPROVAL RECEIPT OWNER NOTE DRAFT VERSION DETAIL COMPARE VIEW UNIFIED SECTION END ===



# === PACK 173 POLICY CHANGE APPROVAL RECEIPT OWNER NOTE DRAFT VERSION COMPARE FILTER NAVIGATION UNIFIED SECTION START ===
def build_pack_173_policy_change_approval_receipt_owner_note_draft_version_compare_filter_navigation_unified_section():
    """
    Pack 173 unified owner section.

    Safe/non-recursive:
    - reads only policy_change_approval_receipt_owner_note_draft_version_compare_filter_navigation
    - does not call quick actions
    - does not call full unified page builder
    """
    try:
        from tower.policy_change_approval_receipt_owner_note_draft_version_compare_filter_navigation import build_policy_change_approval_receipt_owner_note_draft_version_compare_filter_navigation_unified_owner_section
        return build_policy_change_approval_receipt_owner_note_draft_version_compare_filter_navigation_unified_owner_section()
    except Exception as exc:
        return {
            "section_id": "policy_change_approval_receipt_owner_note_draft_version_compare_filter_navigation",
            "title": "Owner Note Compare Navigation",
            "subtitle": "Owner note version compare filter/navigation section needs review.",
            "status": "review",
            "href": "/tower/policy-change-approval-receipt-owner-note-draft-version-compare-filter-navigation.json",
            "cards": [],
            "simulated_only": True,
            "navigation_preview_only": True,
            "filter_navigation_preview_only": True,
            "version_detail_preview_only": True,
            "compare_view_preview_only": True,
            "version_preview_only": True,
            "edit_history_preview_only": True,
            "rollback_preview_only": True,
            "compare_preview_only": True,
            "edit_preview_only": True,
            "detail_drawer_preview_only": True,
            "owner_note_preview_only": True,
            "review_draft_preview_only": True,
            "saved_view_preview_only": True,
            "filter_preset_preview_only": True,
            "filter_preview_only": True,
            "search_facet_preview_only": True,
            "lookup_preview_only": True,
            "detail_preview_only": True,
            "evidence_drawer_preview_only": True,
            "owner_review_preview_only": True,
            "queue_preview_only": True,
            "renewal_preview_only": True,
            "recheck_preview_only": True,
            "expiration_preview_only": True,
            "vault_preview_only": True,
            "index_preview_only": True,
            "receipt_preview_only": True,
            "approval_preview_only": True,
            "evidence_preview_only": True,
            "cached_non_recursive": True,
            "error": str(exc),
        }


def build_pack_173_policy_change_approval_receipt_owner_note_draft_version_compare_filter_navigation_html_section():
    try:
        from tower.policy_change_approval_receipt_owner_note_draft_version_compare_filter_navigation import build_policy_change_approval_receipt_owner_note_draft_version_compare_filter_navigation_html_section
        return build_policy_change_approval_receipt_owner_note_draft_version_compare_filter_navigation_html_section()
    except Exception as exc:
        return f"""
        <section class="tower-section policy-change-approval-receipt-owner-note-compare-navigation-section" id="policy-change-approval-receipt-owner-note-draft-version-compare-filter-navigation">
            <div class="tower-section-heading">
                <p class="tower-kicker">Pack 173</p>
                <h2>Owner Note Compare Navigation</h2>
                <p>Owner note version compare filter/navigation section needs review: {exc}</p>
                <a class="tower-link-pill" href="/tower/policy-change-approval-receipt-owner-note-draft-version-compare-filter-navigation.json">Open owner note compare navigation JSON</a>
            </div>
        </section>
        """


def append_pack_173_policy_change_approval_receipt_owner_note_draft_version_compare_filter_navigation_section(sections):
    """
    Append Pack 173 section to list-like unified section payloads.
    Safe if called more than once.
    """
    try:
        if not isinstance(sections, list):
            return sections

        existing_ids = {
            str(item.get("section_id") or item.get("id"))
            for item in sections
            if isinstance(item, dict)
        }

        if "policy_change_approval_receipt_owner_note_draft_version_compare_filter_navigation" not in existing_ids:
            sections.append(build_pack_173_policy_change_approval_receipt_owner_note_draft_version_compare_filter_navigation_unified_section())

        return sections
    except Exception:
        return sections
# === PACK 173 POLICY CHANGE APPROVAL RECEIPT OWNER NOTE DRAFT VERSION COMPARE FILTER NAVIGATION UNIFIED SECTION END ===



# === PACK 174 POLICY CHANGE APPROVAL RECEIPT OWNER NOTE COMPARE NAVIGATION SAVED VIEW FILTER PRESET UNIFIED SECTION START ===
def build_pack_174_policy_change_approval_receipt_owner_note_compare_navigation_saved_view_filter_preset_unified_section():
    """
    Pack 174 unified owner section.

    Safe/non-recursive:
    - reads only policy_change_approval_receipt_owner_note_compare_navigation_saved_view_filter_preset
    - does not call quick actions
    - does not call full unified page builder
    """
    try:
        from tower.policy_change_approval_receipt_owner_note_compare_navigation_saved_view_filter_preset import build_policy_change_approval_receipt_owner_note_compare_navigation_saved_view_filter_preset_unified_owner_section
        return build_policy_change_approval_receipt_owner_note_compare_navigation_saved_view_filter_preset_unified_owner_section()
    except Exception as exc:
        return {
            "section_id": "policy_change_approval_receipt_owner_note_compare_navigation_saved_view_filter_preset",
            "title": "Owner Note Saved Compare Views",
            "subtitle": "Owner note compare navigation saved view/filter preset section needs review.",
            "status": "review",
            "href": "/tower/policy-change-approval-receipt-owner-note-compare-navigation-saved-view-filter-preset.json",
            "cards": [],
            "simulated_only": True,
            "saved_navigation_preview_only": True,
            "saved_filter_preset_preview_only": True,
            "navigation_preview_only": True,
            "filter_navigation_preview_only": True,
            "saved_view_preview_only": True,
            "filter_preset_preview_only": True,
            "cached_non_recursive": True,
            "error": str(exc),
        }


def build_pack_174_policy_change_approval_receipt_owner_note_compare_navigation_saved_view_filter_preset_html_section():
    try:
        from tower.policy_change_approval_receipt_owner_note_compare_navigation_saved_view_filter_preset import build_policy_change_approval_receipt_owner_note_compare_navigation_saved_view_filter_preset_html_section
        return build_policy_change_approval_receipt_owner_note_compare_navigation_saved_view_filter_preset_html_section()
    except Exception as exc:
        return f"""
        <section class="tower-section policy-change-approval-receipt-owner-note-saved-view-section" id="policy-change-approval-receipt-owner-note-compare-navigation-saved-view-filter-preset">
            <div class="tower-section-heading">
                <p class="tower-kicker">Pack 174</p>
                <h2>Owner Note Saved Compare Views</h2>
                <p>Owner note compare navigation saved view/filter preset section needs review: {exc}</p>
                <a class="tower-link-pill" href="/tower/policy-change-approval-receipt-owner-note-compare-navigation-saved-view-filter-preset.json">Open owner note saved compare views JSON</a>
            </div>
        </section>
        """


def append_pack_174_policy_change_approval_receipt_owner_note_compare_navigation_saved_view_filter_preset_section(sections):
    """
    Append Pack 174 section to list-like unified section payloads.
    Safe if called more than once.
    """
    try:
        if not isinstance(sections, list):
            return sections

        existing_ids = {
            str(item.get("section_id") or item.get("id"))
            for item in sections
            if isinstance(item, dict)
        }

        if "policy_change_approval_receipt_owner_note_compare_navigation_saved_view_filter_preset" not in existing_ids:
            sections.append(build_pack_174_policy_change_approval_receipt_owner_note_compare_navigation_saved_view_filter_preset_unified_section())

        return sections
    except Exception:
        return sections
# === PACK 174 POLICY CHANGE APPROVAL RECEIPT OWNER NOTE COMPARE NAVIGATION SAVED VIEW FILTER PRESET UNIFIED SECTION END ===



# === PACK 175 POLICY CHANGE APPROVAL RECEIPT OWNER NOTE SAVED VIEW PRESET DETAIL EDIT PREVIEW UNIFIED SECTION START ===
def build_pack_175_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_preview_unified_section():
    """
    Pack 175 unified owner section.

    Safe/non-recursive:
    - reads only policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_preview
    - does not call quick actions
    - does not call full unified page builder
    """
    try:
        from tower.policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_preview import build_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_preview_unified_owner_section
        return build_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_preview_unified_owner_section()
    except Exception as exc:
        return {
            "section_id": "policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_preview",
            "title": "Owner Note Preset Edit Preview",
            "subtitle": "Owner note saved view preset detail/edit section needs review.",
            "status": "review",
            "href": "/tower/policy-change-approval-receipt-owner-note-saved-view-preset-detail-edit-preview.json",
            "cards": [],
            "simulated_only": True,
            "saved_view_preset_detail_preview_only": True,
            "saved_view_preset_edit_preview_only": True,
            "saved_navigation_preview_only": True,
            "saved_filter_preset_preview_only": True,
            "navigation_preview_only": True,
            "filter_navigation_preview_only": True,
            "saved_view_preview_only": True,
            "filter_preset_preview_only": True,
            "cached_non_recursive": True,
            "error": str(exc),
        }


def build_pack_175_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_preview_html_section():
    try:
        from tower.policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_preview import build_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_preview_html_section
        return build_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_preview_html_section()
    except Exception as exc:
        return f"""
        <section class="tower-section policy-change-approval-receipt-owner-note-preset-edit-section" id="policy-change-approval-receipt-owner-note-saved-view-preset-detail-edit-preview">
            <div class="tower-section-heading">
                <p class="tower-kicker">Pack 175</p>
                <h2>Owner Note Preset Edit Preview</h2>
                <p>Owner note saved view preset detail/edit section needs review: {exc}</p>
                <a class="tower-link-pill" href="/tower/policy-change-approval-receipt-owner-note-saved-view-preset-detail-edit-preview.json">Open owner note preset edit preview JSON</a>
            </div>
        </section>
        """


def append_pack_175_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_preview_section(sections):
    """
    Append Pack 175 section to list-like unified section payloads.
    Safe if called more than once.
    """
    try:
        if not isinstance(sections, list):
            return sections

        existing_ids = {
            str(item.get("section_id") or item.get("id"))
            for item in sections
            if isinstance(item, dict)
        }

        if "policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_preview" not in existing_ids:
            sections.append(build_pack_175_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_preview_unified_section())

        return sections
    except Exception:
        return sections
# === PACK 175 POLICY CHANGE APPROVAL RECEIPT OWNER NOTE SAVED VIEW PRESET DETAIL EDIT PREVIEW UNIFIED SECTION END ===



# === PACK 176 POLICY CHANGE APPROVAL RECEIPT OWNER NOTE SAVED VIEW PRESET EDIT HISTORY VERSION PREVIEW UNIFIED SECTION START ===
def build_pack_176_policy_change_approval_receipt_owner_note_saved_view_preset_edit_history_version_preview_unified_section():
    """
    Pack 176 unified owner section.

    Safe/non-recursive:
    - reads only policy_change_approval_receipt_owner_note_saved_view_preset_edit_history_version_preview
    - does not call quick actions
    - does not call full unified page builder
    """
    try:
        from tower.policy_change_approval_receipt_owner_note_saved_view_preset_edit_history_version_preview import build_policy_change_approval_receipt_owner_note_saved_view_preset_edit_history_version_preview_unified_owner_section
        return build_policy_change_approval_receipt_owner_note_saved_view_preset_edit_history_version_preview_unified_owner_section()
    except Exception as exc:
        return {
            "section_id": "policy_change_approval_receipt_owner_note_saved_view_preset_edit_history_version_preview",
            "title": "Owner Note Preset Edit History",
            "subtitle": "Owner note saved view preset edit history/version section needs review.",
            "status": "review",
            "href": "/tower/policy-change-approval-receipt-owner-note-saved-view-preset-edit-history-version-preview.json",
            "cards": [],
            "simulated_only": True,
            "edit_history_preview_only": True,
            "version_preview_only": True,
            "rollback_preview_only": True,
            "saved_view_preset_detail_preview_only": True,
            "saved_view_preset_edit_preview_only": True,
            "saved_navigation_preview_only": True,
            "saved_filter_preset_preview_only": True,
            "cached_non_recursive": True,
            "error": str(exc),
        }


def build_pack_176_policy_change_approval_receipt_owner_note_saved_view_preset_edit_history_version_preview_html_section():
    try:
        from tower.policy_change_approval_receipt_owner_note_saved_view_preset_edit_history_version_preview import build_policy_change_approval_receipt_owner_note_saved_view_preset_edit_history_version_preview_html_section
        return build_policy_change_approval_receipt_owner_note_saved_view_preset_edit_history_version_preview_html_section()
    except Exception as exc:
        return f"""
        <section class="tower-section policy-change-approval-receipt-owner-note-preset-history-section" id="policy-change-approval-receipt-owner-note-saved-view-preset-edit-history-version-preview">
            <div class="tower-section-heading">
                <p class="tower-kicker">Pack 176</p>
                <h2>Owner Note Preset Edit History</h2>
                <p>Owner note saved view preset edit history/version section needs review: {exc}</p>
                <a class="tower-link-pill" href="/tower/policy-change-approval-receipt-owner-note-saved-view-preset-edit-history-version-preview.json">Open owner note preset edit history JSON</a>
            </div>
        </section>
        """


def append_pack_176_policy_change_approval_receipt_owner_note_saved_view_preset_edit_history_version_preview_section(sections):
    """
    Append Pack 176 section to list-like unified section payloads.
    Safe if called more than once.
    """
    try:
        if not isinstance(sections, list):
            return sections

        existing_ids = {
            str(item.get("section_id") or item.get("id"))
            for item in sections
            if isinstance(item, dict)
        }

        if "policy_change_approval_receipt_owner_note_saved_view_preset_edit_history_version_preview" not in existing_ids:
            sections.append(build_pack_176_policy_change_approval_receipt_owner_note_saved_view_preset_edit_history_version_preview_unified_section())

        return sections
    except Exception:
        return sections
# === PACK 176 POLICY CHANGE APPROVAL RECEIPT OWNER NOTE SAVED VIEW PRESET EDIT HISTORY VERSION PREVIEW UNIFIED SECTION END ===



# === PACK 177 POLICY CHANGE APPROVAL RECEIPT OWNER NOTE SAVED VIEW PRESET VERSION DETAIL COMPARE VIEW UNIFIED SECTION START ===
def build_pack_177_policy_change_approval_receipt_owner_note_saved_view_preset_version_detail_compare_view_unified_section():
    """
    Pack 177 unified owner section.

    Safe/non-recursive:
    - reads only policy_change_approval_receipt_owner_note_saved_view_preset_version_detail_compare_view
    - does not call quick actions
    - does not call full unified page builder
    """
    try:
        from tower.policy_change_approval_receipt_owner_note_saved_view_preset_version_detail_compare_view import build_policy_change_approval_receipt_owner_note_saved_view_preset_version_detail_compare_view_unified_owner_section
        return build_policy_change_approval_receipt_owner_note_saved_view_preset_version_detail_compare_view_unified_owner_section()
    except Exception as exc:
        return {
            "section_id": "policy_change_approval_receipt_owner_note_saved_view_preset_version_detail_compare_view",
            "title": "Owner Note Preset Version Compare",
            "subtitle": "Owner note saved view preset version detail/compare section needs review.",
            "status": "review",
            "href": "/tower/policy-change-approval-receipt-owner-note-saved-view-preset-version-detail-compare-view.json",
            "cards": [],
            "simulated_only": True,
            "version_detail_preview_only": True,
            "compare_view_preview_only": True,
            "edit_history_preview_only": True,
            "version_preview_only": True,
            "rollback_preview_only": True,
            "saved_view_preset_detail_preview_only": True,
            "saved_view_preset_edit_preview_only": True,
            "cached_non_recursive": True,
            "error": str(exc),
        }


def build_pack_177_policy_change_approval_receipt_owner_note_saved_view_preset_version_detail_compare_view_html_section():
    try:
        from tower.policy_change_approval_receipt_owner_note_saved_view_preset_version_detail_compare_view import build_policy_change_approval_receipt_owner_note_saved_view_preset_version_detail_compare_view_html_section
        return build_policy_change_approval_receipt_owner_note_saved_view_preset_version_detail_compare_view_html_section()
    except Exception as exc:
        return f"""
        <section class="tower-section policy-change-approval-receipt-owner-note-preset-version-compare-section" id="policy-change-approval-receipt-owner-note-saved-view-preset-version-detail-compare-view">
            <div class="tower-section-heading">
                <p class="tower-kicker">Pack 177</p>
                <h2>Owner Note Preset Version Compare</h2>
                <p>Owner note saved view preset version detail/compare section needs review: {exc}</p>
                <a class="tower-link-pill" href="/tower/policy-change-approval-receipt-owner-note-saved-view-preset-version-detail-compare-view.json">Open owner note preset version compare JSON</a>
            </div>
        </section>
        """


def append_pack_177_policy_change_approval_receipt_owner_note_saved_view_preset_version_detail_compare_view_section(sections):
    """
    Append Pack 177 section to list-like unified section payloads.
    Safe if called more than once.
    """
    try:
        if not isinstance(sections, list):
            return sections

        existing_ids = {
            str(item.get("section_id") or item.get("id"))
            for item in sections
            if isinstance(item, dict)
        }

        if "policy_change_approval_receipt_owner_note_saved_view_preset_version_detail_compare_view" not in existing_ids:
            sections.append(build_pack_177_policy_change_approval_receipt_owner_note_saved_view_preset_version_detail_compare_view_unified_section())

        return sections
    except Exception:
        return sections
# === PACK 177 POLICY CHANGE APPROVAL RECEIPT OWNER NOTE SAVED VIEW PRESET VERSION DETAIL COMPARE VIEW UNIFIED SECTION END ===


# === PACK 178 UNIFIED SECTION START ===
def build_pack_178_policy_change_approval_receipt_owner_note_saved_view_preset_version_compare_filter_navigation_unified_section():
    try:
        from tower.policy_change_approval_receipt_owner_note_saved_view_preset_version_compare_filter_navigation import build_policy_change_approval_receipt_owner_note_saved_view_preset_version_compare_filter_navigation_unified_owner_section
        return build_policy_change_approval_receipt_owner_note_saved_view_preset_version_compare_filter_navigation_unified_owner_section()
    except Exception as exc:
        return {"section_id":"policy_change_approval_receipt_owner_note_saved_view_preset_version_compare_filter_navigation","title":"Owner Note Preset Compare Navigation","status":"review","href":"/tower/policy-change-approval-receipt-owner-note-saved-view-preset-version-compare-filter-navigation.json","cards":[],"error":str(exc)}
def append_pack_178_policy_change_approval_receipt_owner_note_saved_view_preset_version_compare_filter_navigation_section(sections):
    if isinstance(sections, list) and not any(isinstance(x, dict) and x.get("section_id") == "policy_change_approval_receipt_owner_note_saved_view_preset_version_compare_filter_navigation" for x in sections):
        sections.append(build_pack_178_policy_change_approval_receipt_owner_note_saved_view_preset_version_compare_filter_navigation_unified_section())
    return sections
# === PACK 178 UNIFIED SECTION END ===



# === PACK 179 POLICY CHANGE APPROVAL RECEIPT OWNER NOTE SAVED VIEW PRESET VERSION COMPARE NAVIGATION SAVED VIEW FILTER PRESET UNIFIED SECTION START ===
def build_pack_179_policy_change_approval_receipt_owner_note_saved_view_preset_version_compare_navigation_saved_view_filter_preset_unified_section():
    """
    Pack 179 unified owner section.

    Safe/non-recursive:
    - reads only Pack 179 saved view/filter preset payload
    - does not call quick actions
    - does not call full unified page builder
    """
    try:
        from tower.policy_change_approval_receipt_owner_note_saved_view_preset_version_compare_navigation_saved_view_filter_preset import build_policy_change_approval_receipt_owner_note_saved_view_preset_version_compare_navigation_saved_view_filter_preset_unified_owner_section
        return build_policy_change_approval_receipt_owner_note_saved_view_preset_version_compare_navigation_saved_view_filter_preset_unified_owner_section()
    except Exception as exc:
        return {
            "section_id": "policy_change_approval_receipt_owner_note_saved_view_preset_version_compare_navigation_saved_view_filter_preset",
            "title": "Owner Note Preset Compare Saved Views",
            "subtitle": "Owner note saved view preset version compare navigation saved view/filter preset section needs review.",
            "status": "review",
            "href": "/tower/policy-change-approval-receipt-owner-note-saved-view-preset-version-compare-navigation-saved-view-filter-preset.json",
            "cards": [],
            "simulated_only": True,
            "saved_view_preview_only": True,
            "filter_preset_preview_only": True,
            "navigation_preview_only": True,
            "filter_navigation_preview_only": True,
            "cached_non_recursive": True,
            "error": str(exc),
        }


def append_pack_179_policy_change_approval_receipt_owner_note_saved_view_preset_version_compare_navigation_saved_view_filter_preset_section(sections):
    """
    Append Pack 179 section to list-like unified section payloads.
    Safe if called more than once.
    """
    try:
        if not isinstance(sections, list):
            return sections

        existing_ids = {
            str(item.get("section_id") or item.get("id"))
            for item in sections
            if isinstance(item, dict)
        }

        if "policy_change_approval_receipt_owner_note_saved_view_preset_version_compare_navigation_saved_view_filter_preset" not in existing_ids:
            sections.append(build_pack_179_policy_change_approval_receipt_owner_note_saved_view_preset_version_compare_navigation_saved_view_filter_preset_unified_section())

        return sections
    except Exception:
        return sections
# === PACK 179 POLICY CHANGE APPROVAL RECEIPT OWNER NOTE SAVED VIEW PRESET VERSION COMPARE NAVIGATION SAVED VIEW FILTER PRESET UNIFIED SECTION END ===



# === PACK 180 POLICY CHANGE APPROVAL RECEIPT OWNER NOTE SAVED VIEW PRESET SAVED VIEW FILTER PRESET DETAIL EDIT PREVIEW UNIFIED SECTION START ===
def build_pack_180_policy_change_approval_receipt_owner_note_saved_view_preset_saved_view_filter_preset_detail_edit_preview_unified_section():
    """
    Pack 180 unified owner section.

    Safe/non-recursive:
    - reads only Pack 180 saved view/filter preset detail edit payload
    - does not call quick actions
    - does not call full unified page builder
    """
    try:
        from tower.policy_change_approval_receipt_owner_note_saved_view_preset_saved_view_filter_preset_detail_edit_preview import build_policy_change_approval_receipt_owner_note_saved_view_preset_saved_view_filter_preset_detail_edit_preview_unified_owner_section
        return build_policy_change_approval_receipt_owner_note_saved_view_preset_saved_view_filter_preset_detail_edit_preview_unified_owner_section()
    except Exception as exc:
        return {
            "section_id": "policy_change_approval_receipt_owner_note_saved_view_preset_saved_view_filter_preset_detail_edit_preview",
            "title": "Owner Note Saved View Detail Edit",
            "subtitle": "Owner note saved view/filter preset detail edit section needs review.",
            "status": "review",
            "href": "/tower/policy-change-approval-receipt-owner-note-saved-view-preset-saved-view-filter-preset-detail-edit-preview.json",
            "cards": [],
            "simulated_only": True,
            "detail_edit_preview_only": True,
            "saved_view_preview_only": True,
            "filter_preset_preview_only": True,
            "navigation_preview_only": True,
            "filter_navigation_preview_only": True,
            "cached_non_recursive": True,
            "error": str(exc),
        }


def append_pack_180_policy_change_approval_receipt_owner_note_saved_view_preset_saved_view_filter_preset_detail_edit_preview_section(sections):
    """
    Append Pack 180 section to list-like unified section payloads.
    Safe if called more than once.
    """
    try:
        if not isinstance(sections, list):
            return sections

        existing_ids = {
            str(item.get("section_id") or item.get("id"))
            for item in sections
            if isinstance(item, dict)
        }

        if "policy_change_approval_receipt_owner_note_saved_view_preset_saved_view_filter_preset_detail_edit_preview" not in existing_ids:
            sections.append(build_pack_180_policy_change_approval_receipt_owner_note_saved_view_preset_saved_view_filter_preset_detail_edit_preview_unified_section())

        return sections
    except Exception:
        return sections
# === PACK 180 POLICY CHANGE APPROVAL RECEIPT OWNER NOTE SAVED VIEW PRESET SAVED VIEW FILTER PRESET DETAIL EDIT PREVIEW UNIFIED SECTION END ===



# === PACK 181 POLICY CHANGE APPROVAL RECEIPT OWNER NOTE SAVED VIEW PRESET DETAIL EDIT HISTORY VERSION PREVIEW UNIFIED SECTION START ===
def build_pack_181_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_preview_unified_section():
    """
    Pack 181 unified owner section.

    Safe/non-recursive:
    - reads only Pack 181 edit history/version payload
    - does not call quick actions
    - does not call full unified page builder
    """
    try:
        from tower.policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_preview import build_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_preview_unified_owner_section
        return build_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_preview_unified_owner_section()
    except Exception as exc:
        return {
            "section_id": "policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_preview",
            "title": "Owner Note Saved View History",
            "subtitle": "Owner note saved view preset detail edit history/version section needs review.",
            "status": "review",
            "href": "/tower/policy-change-approval-receipt-owner-note-saved-view-preset-detail-edit-history-version-preview.json",
            "cards": [],
            "simulated_only": True,
            "edit_history_preview_only": True,
            "version_preview_only": True,
            "rollback_preview_only": True,
            "restore_preview_only": True,
            "detail_edit_preview_only": True,
            "cached_non_recursive": True,
            "error": str(exc),
        }


def append_pack_181_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_preview_section(sections):
    """
    Append Pack 181 section to list-like unified section payloads.
    Safe if called more than once.
    """
    try:
        if not isinstance(sections, list):
            return sections

        existing_ids = {
            str(item.get("section_id") or item.get("id"))
            for item in sections
            if isinstance(item, dict)
        }

        if "policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_preview" not in existing_ids:
            sections.append(build_pack_181_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_preview_unified_section())

        return sections
    except Exception:
        return sections
# === PACK 181 POLICY CHANGE APPROVAL RECEIPT OWNER NOTE SAVED VIEW PRESET DETAIL EDIT HISTORY VERSION PREVIEW UNIFIED SECTION END ===



# === PACK 182 POLICY CHANGE APPROVAL RECEIPT OWNER NOTE SAVED VIEW PRESET DETAIL EDIT HISTORY VERSION DETAIL COMPARE VIEW UNIFIED SECTION START ===
def build_pack_182_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_detail_compare_view_unified_section():
    """
    Pack 182 unified owner section.

    Safe/non-recursive:
    - reads only Pack 182 version detail/compare payload
    - does not call quick actions
    - does not call full unified page builder
    """
    try:
        from tower.policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_detail_compare_view import build_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_detail_compare_view_unified_owner_section
        return build_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_detail_compare_view_unified_owner_section()
    except Exception as exc:
        return {
            "section_id": "policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_detail_compare_view",
            "title": "Owner Note Saved View Version Compare",
            "subtitle": "Owner note saved view preset detail edit history version detail/compare section needs review.",
            "status": "review",
            "href": "/tower/policy-change-approval-receipt-owner-note-saved-view-preset-detail-edit-history-version-detail-compare-view.json",
            "cards": [],
            "simulated_only": True,
            "version_detail_preview_only": True,
            "compare_view_preview_only": True,
            "edit_history_preview_only": True,
            "version_preview_only": True,
            "rollback_preview_only": True,
            "restore_preview_only": True,
            "cached_non_recursive": True,
            "error": str(exc),
        }


def append_pack_182_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_detail_compare_view_section(sections):
    """
    Append Pack 182 section to list-like unified section payloads.
    Safe if called more than once.
    """
    try:
        if not isinstance(sections, list):
            return sections

        existing_ids = {
            str(item.get("section_id") or item.get("id"))
            for item in sections
            if isinstance(item, dict)
        }

        if "policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_detail_compare_view" not in existing_ids:
            sections.append(build_pack_182_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_detail_compare_view_unified_section())

        return sections
    except Exception:
        return sections
# === PACK 182 POLICY CHANGE APPROVAL RECEIPT OWNER NOTE SAVED VIEW PRESET DETAIL EDIT HISTORY VERSION DETAIL COMPARE VIEW UNIFIED SECTION END ===



# === PACK 183 POLICY CHANGE APPROVAL RECEIPT OWNER NOTE SAVED VIEW PRESET DETAIL EDIT HISTORY VERSION COMPARE FILTER NAVIGATION UNIFIED SECTION START ===
def build_pack_183_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_filter_navigation_unified_section():
    """
    Pack 183 unified owner section.

    Safe/non-recursive:
    - reads only Pack 183 compare filter/navigation payload
    - does not call quick actions
    - does not call full unified page builder
    """
    try:
        from tower.policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_filter_navigation import build_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_filter_navigation_unified_owner_section
        return build_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_filter_navigation_unified_owner_section()
    except Exception as exc:
        return {
            "section_id": "policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_filter_navigation",
            "title": "Owner Note Version Compare Navigation",
            "subtitle": "Owner note saved view preset version compare navigation section needs review.",
            "status": "review",
            "href": "/tower/policy-change-approval-receipt-owner-note-saved-view-preset-detail-edit-history-version-compare-filter-navigation.json",
            "cards": [],
            "simulated_only": True,
            "navigation_preview_only": True,
            "filter_navigation_preview_only": True,
            "version_detail_preview_only": True,
            "compare_view_preview_only": True,
            "cached_non_recursive": True,
            "error": str(exc),
        }


def append_pack_183_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_filter_navigation_section(sections):
    """
    Append Pack 183 section to list-like unified section payloads.
    Safe if called more than once.
    """
    try:
        if not isinstance(sections, list):
            return sections

        existing_ids = {
            str(item.get("section_id") or item.get("id"))
            for item in sections
            if isinstance(item, dict)
        }

        if "policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_filter_navigation" not in existing_ids:
            sections.append(build_pack_183_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_filter_navigation_unified_section())

        return sections
    except Exception:
        return sections
# === PACK 183 POLICY CHANGE APPROVAL RECEIPT OWNER NOTE SAVED VIEW PRESET DETAIL EDIT HISTORY VERSION COMPARE FILTER NAVIGATION UNIFIED SECTION END ===



# === PACK 184 POLICY CHANGE APPROVAL RECEIPT OWNER NOTE SAVED VIEW PRESET DETAIL EDIT HISTORY VERSION COMPARE NAVIGATION SAVED VIEW FILTER PRESET UNIFIED SECTION START ===
def build_pack_184_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_navigation_saved_view_filter_preset_unified_section():
    """
    Pack 184 unified owner section.

    Safe/non-recursive:
    - reads only Pack 184 saved view/filter preset payload
    - does not call quick actions
    - does not call full unified page builder
    """
    try:
        from tower.policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_navigation_saved_view_filter_preset import build_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_navigation_saved_view_filter_preset_unified_owner_section
        return build_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_navigation_saved_view_filter_preset_unified_owner_section()
    except Exception as exc:
        return {
            "section_id": "policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_navigation_saved_view_filter_preset",
            "title": "Owner Note Version Compare Saved Views",
            "subtitle": "Owner note version compare saved view/filter preset section needs review.",
            "status": "review",
            "href": "/tower/policy-change-approval-receipt-owner-note-saved-view-preset-detail-edit-history-version-compare-navigation-saved-view-filter-preset.json",
            "cards": [],
            "simulated_only": True,
            "saved_view_preview_only": True,
            "filter_preset_preview_only": True,
            "navigation_preview_only": True,
            "filter_navigation_preview_only": True,
            "cached_non_recursive": True,
            "error": str(exc),
        }


def append_pack_184_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_navigation_saved_view_filter_preset_section(sections):
    """
    Append Pack 184 section to list-like unified section payloads.
    Safe if called more than once.
    """
    try:
        if not isinstance(sections, list):
            return sections

        existing_ids = {
            str(item.get("section_id") or item.get("id"))
            for item in sections
            if isinstance(item, dict)
        }

        if "policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_navigation_saved_view_filter_preset" not in existing_ids:
            sections.append(build_pack_184_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_navigation_saved_view_filter_preset_unified_section())

        return sections
    except Exception:
        return sections
# === PACK 184 POLICY CHANGE APPROVAL RECEIPT OWNER NOTE SAVED VIEW PRESET DETAIL EDIT HISTORY VERSION COMPARE NAVIGATION SAVED VIEW FILTER PRESET UNIFIED SECTION END ===



# === PACK 185 POLICY CHANGE APPROVAL RECEIPT OWNER NOTE SAVED VIEW PRESET DETAIL EDIT HISTORY VERSION COMPARE SAVED VIEW FILTER PRESET DETAIL EDIT PREVIEW UNIFIED SECTION START ===
def build_pack_185_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_saved_view_filter_preset_detail_edit_preview_unified_section():
    """
    Pack 185 unified owner section.

    Safe/non-recursive:
    - reads only Pack 185 detail edit payload
    - does not call quick actions
    - does not call full unified page builder
    """
    try:
        from tower.policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_saved_view_filter_preset_detail_edit_preview import build_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_saved_view_filter_preset_detail_edit_preview_unified_owner_section
        return build_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_saved_view_filter_preset_detail_edit_preview_unified_owner_section()
    except Exception as exc:
        return {
            "section_id": "policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_saved_view_filter_preset_detail_edit_preview",
            "title": "Owner Note Version Compare Saved View Detail Edit",
            "subtitle": "Owner note version compare saved view/filter preset detail edit section needs review.",
            "status": "review",
            "href": "/tower/policy-change-approval-receipt-owner-note-saved-view-preset-detail-edit-history-version-compare-saved-view-filter-preset-detail-edit-preview.json",
            "cards": [],
            "simulated_only": True,
            "detail_edit_preview_only": True,
            "saved_view_preview_only": True,
            "filter_preset_preview_only": True,
            "navigation_preview_only": True,
            "filter_navigation_preview_only": True,
            "cached_non_recursive": True,
            "error": str(exc),
        }


def append_pack_185_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_saved_view_filter_preset_detail_edit_preview_section(sections):
    """
    Append Pack 185 section to list-like unified section payloads.
    Safe if called more than once.
    """
    try:
        if not isinstance(sections, list):
            return sections

        existing_ids = {
            str(item.get("section_id") or item.get("id"))
            for item in sections
            if isinstance(item, dict)
        }

        if "policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_saved_view_filter_preset_detail_edit_preview" not in existing_ids:
            sections.append(build_pack_185_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_saved_view_filter_preset_detail_edit_preview_unified_section())

        return sections
    except Exception:
        return sections
# === PACK 185 POLICY CHANGE APPROVAL RECEIPT OWNER NOTE SAVED VIEW PRESET DETAIL EDIT HISTORY VERSION COMPARE SAVED VIEW FILTER PRESET DETAIL EDIT PREVIEW UNIFIED SECTION END ===



# === PACK 186 POLICY CHANGE APPROVAL RECEIPT OWNER NOTE SAVED VIEW PRESET DETAIL EDIT HISTORY VERSION COMPARE SAVED VIEW FILTER PRESET DETAIL EDIT HISTORY VERSION PREVIEW UNIFIED SECTION START ===
def build_pack_186_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_saved_view_filter_preset_detail_edit_history_version_preview_unified_section():
    """
    Pack 186 unified owner section.

    Safe/non-recursive:
    - reads only Pack 186 edit history/version payload
    - does not call quick actions
    - does not call full unified page builder
    """
    try:
        from tower.policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_saved_view_filter_preset_detail_edit_history_version_preview import build_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_saved_view_filter_preset_detail_edit_history_version_preview_unified_owner_section
        return build_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_saved_view_filter_preset_detail_edit_history_version_preview_unified_owner_section()
    except Exception as exc:
        return {
            "section_id": "policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_saved_view_filter_preset_detail_edit_history_version_preview",
            "title": "Owner Note Version Compare Saved View History",
            "subtitle": "Owner note version compare saved view/filter preset detail edit history/version section needs review.",
            "status": "review",
            "href": "/tower/policy-change-approval-receipt-owner-note-saved-view-preset-detail-edit-history-version-compare-saved-view-filter-preset-detail-edit-history-version-preview.json",
            "cards": [],
            "simulated_only": True,
            "edit_history_preview_only": True,
            "version_preview_only": True,
            "rollback_preview_only": True,
            "restore_preview_only": True,
            "detail_edit_preview_only": True,
            "cached_non_recursive": True,
            "error": str(exc),
        }


def append_pack_186_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_saved_view_filter_preset_detail_edit_history_version_preview_section(sections):
    """
    Append Pack 186 section to list-like unified section payloads.
    Safe if called more than once.
    """
    try:
        if not isinstance(sections, list):
            return sections

        existing_ids = {
            str(item.get("section_id") or item.get("id"))
            for item in sections
            if isinstance(item, dict)
        }

        if "policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_saved_view_filter_preset_detail_edit_history_version_preview" not in existing_ids:
            sections.append(build_pack_186_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_saved_view_filter_preset_detail_edit_history_version_preview_unified_section())

        return sections
    except Exception:
        return sections
# === PACK 186 POLICY CHANGE APPROVAL RECEIPT OWNER NOTE SAVED VIEW PRESET DETAIL EDIT HISTORY VERSION COMPARE SAVED VIEW FILTER PRESET DETAIL EDIT HISTORY VERSION PREVIEW UNIFIED SECTION END ===



# === PACK 187 POLICY CHANGE APPROVAL RECEIPT OWNER NOTE SAVED VIEW PRESET DETAIL EDIT HISTORY VERSION COMPARE SAVED VIEW FILTER PRESET DETAIL EDIT HISTORY VERSION DETAIL COMPARE VIEW UNIFIED SECTION START ===
def build_pack_187_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_saved_view_filter_preset_detail_edit_history_version_detail_compare_view_unified_section():
    """
    Pack 187 unified owner section.

    Safe/non-recursive:
    - reads only Pack 187 detail/compare payload
    - does not call quick actions
    - does not call full unified page builder
    """
    try:
        from tower.policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_saved_view_filter_preset_detail_edit_history_version_detail_compare_view import build_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_saved_view_filter_preset_detail_edit_history_version_detail_compare_view_unified_owner_section
        return build_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_saved_view_filter_preset_detail_edit_history_version_detail_compare_view_unified_owner_section()
    except Exception as exc:
        return {
            "section_id": "policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_saved_view_filter_preset_detail_edit_history_version_detail_compare_view",
            "title": "Owner Note Version Compare Detail View",
            "subtitle": "Owner note version compare saved view/filter preset detail edit history version detail/compare section needs review.",
            "status": "review",
            "href": "/tower/policy-change-approval-receipt-owner-note-saved-view-preset-detail-edit-history-version-compare-saved-view-filter-preset-detail-edit-history-version-detail-compare-view.json",
            "cards": [],
            "simulated_only": True,
            "version_detail_preview_only": True,
            "compare_view_preview_only": True,
            "edit_history_preview_only": True,
            "version_preview_only": True,
            "rollback_preview_only": True,
            "restore_preview_only": True,
            "cached_non_recursive": True,
            "error": str(exc),
        }


def append_pack_187_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_saved_view_filter_preset_detail_edit_history_version_detail_compare_view_section(sections):
    """
    Append Pack 187 section to list-like unified section payloads.
    Safe if called more than once.
    """
    try:
        if not isinstance(sections, list):
            return sections

        existing_ids = {
            str(item.get("section_id") or item.get("id"))
            for item in sections
            if isinstance(item, dict)
        }

        if "policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_saved_view_filter_preset_detail_edit_history_version_detail_compare_view" not in existing_ids:
            sections.append(build_pack_187_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_saved_view_filter_preset_detail_edit_history_version_detail_compare_view_unified_section())

        return sections
    except Exception:
        return sections
# === PACK 187 POLICY CHANGE APPROVAL RECEIPT OWNER NOTE SAVED VIEW PRESET DETAIL EDIT HISTORY VERSION COMPARE SAVED VIEW FILTER PRESET DETAIL EDIT HISTORY VERSION DETAIL COMPARE VIEW UNIFIED SECTION END ===



# === PACK 188 POLICY CHANGE APPROVAL RECEIPT OWNER NOTE SAVED VIEW PRESET DETAIL EDIT HISTORY VERSION COMPARE SAVED VIEW FILTER PRESET DETAIL EDIT HISTORY VERSION COMPARE FILTER NAVIGATION UNIFIED SECTION START ===
def build_pack_188_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_saved_view_filter_preset_detail_edit_history_version_compare_filter_navigation_unified_section():
    """
    Pack 188 unified owner section.

    Safe/non-recursive:
    - reads only Pack 188 filter/navigation payload
    - does not call quick actions
    - does not call full unified page builder
    """
    try:
        from tower.policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_saved_view_filter_preset_detail_edit_history_version_compare_filter_navigation import build_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_saved_view_filter_preset_detail_edit_history_version_compare_filter_navigation_unified_owner_section
        return build_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_saved_view_filter_preset_detail_edit_history_version_compare_filter_navigation_unified_owner_section()
    except Exception as exc:
        return {
            "section_id": "policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_saved_view_filter_preset_detail_edit_history_version_compare_filter_navigation",
            "title": "Owner Note Version Compare Filter Navigation",
            "subtitle": "Owner note version compare saved view/filter preset detail history filter/navigation section needs review.",
            "status": "review",
            "href": "/tower/policy-change-approval-receipt-owner-note-saved-view-preset-detail-edit-history-version-compare-saved-view-filter-preset-detail-edit-history-version-compare-filter-navigation.json",
            "cards": [],
            "simulated_only": True,
            "navigation_preview_only": True,
            "filter_navigation_preview_only": True,
            "version_detail_preview_only": True,
            "compare_view_preview_only": True,
            "cached_non_recursive": True,
            "error": str(exc),
        }


def append_pack_188_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_saved_view_filter_preset_detail_edit_history_version_compare_filter_navigation_section(sections):
    """
    Append Pack 188 section to list-like unified section payloads.
    Safe if called more than once.
    """
    try:
        if not isinstance(sections, list):
            return sections

        existing_ids = {
            str(item.get("section_id") or item.get("id"))
            for item in sections
            if isinstance(item, dict)
        }

        if "policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_saved_view_filter_preset_detail_edit_history_version_compare_filter_navigation" not in existing_ids:
            sections.append(build_pack_188_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_saved_view_filter_preset_detail_edit_history_version_compare_filter_navigation_unified_section())

        return sections
    except Exception:
        return sections
# === PACK 188 POLICY CHANGE APPROVAL RECEIPT OWNER NOTE SAVED VIEW PRESET DETAIL EDIT HISTORY VERSION COMPARE SAVED VIEW FILTER PRESET DETAIL EDIT HISTORY VERSION COMPARE FILTER NAVIGATION UNIFIED SECTION END ===



# === PACK 189 POLICY CHANGE APPROVAL RECEIPT OWNER NOTE SAVED VIEW PRESET DETAIL EDIT HISTORY VERSION COMPARE SAVED VIEW FILTER PRESET DETAIL EDIT HISTORY VERSION COMPARE NAVIGATION SAVED VIEW FILTER PRESET UNIFIED SECTION START ===
def build_pack_189_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_saved_view_filter_preset_detail_edit_history_version_compare_navigation_saved_view_filter_preset_unified_section():
    """
    Pack 189 unified owner section.

    Safe/non-recursive:
    - reads only Pack 189 saved view/filter preset payload
    - does not call quick actions
    - does not call full unified page builder
    """
    try:
        from tower.policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_saved_view_filter_preset_detail_edit_history_version_compare_navigation_saved_view_filter_preset import build_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_saved_view_filter_preset_detail_edit_history_version_compare_navigation_saved_view_filter_preset_unified_owner_section
        return build_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_saved_view_filter_preset_detail_edit_history_version_compare_navigation_saved_view_filter_preset_unified_owner_section()
    except Exception as exc:
        return {
            "section_id": "policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_saved_view_filter_preset_detail_edit_history_version_compare_navigation_saved_view_filter_preset",
            "title": "Owner Note Version Compare Saved Views",
            "subtitle": "Owner note version compare navigation saved view/filter preset section needs review.",
            "status": "review",
            "href": "/tower/policy-change-approval-receipt-owner-note-saved-view-preset-detail-edit-history-version-compare-saved-view-filter-preset-detail-edit-history-version-compare-navigation-saved-view-filter-preset.json",
            "cards": [],
            "simulated_only": True,
            "saved_view_preview_only": True,
            "filter_preset_preview_only": True,
            "navigation_preview_only": True,
            "filter_navigation_preview_only": True,
            "cached_non_recursive": True,
            "error": str(exc),
        }


def append_pack_189_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_saved_view_filter_preset_detail_edit_history_version_compare_navigation_saved_view_filter_preset_section(sections):
    """
    Append Pack 189 section to list-like unified section payloads.
    Safe if called more than once.
    """
    try:
        if not isinstance(sections, list):
            return sections

        existing_ids = {
            str(item.get("section_id") or item.get("id"))
            for item in sections
            if isinstance(item, dict)
        }

        if "policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_saved_view_filter_preset_detail_edit_history_version_compare_navigation_saved_view_filter_preset" not in existing_ids:
            sections.append(build_pack_189_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_saved_view_filter_preset_detail_edit_history_version_compare_navigation_saved_view_filter_preset_unified_section())

        return sections
    except Exception:
        return sections
# === PACK 189 POLICY CHANGE APPROVAL RECEIPT OWNER NOTE SAVED VIEW PRESET DETAIL EDIT HISTORY VERSION COMPARE SAVED VIEW FILTER PRESET DETAIL EDIT HISTORY VERSION COMPARE NAVIGATION SAVED VIEW FILTER PRESET UNIFIED SECTION END ===



# === PACK 190 POLICY CHANGE APPROVAL RECEIPT OWNER NOTE SAVED VIEW PRESET DETAIL EDIT HISTORY VERSION COMPARE SAVED VIEW FILTER PRESET DETAIL EDIT HISTORY VERSION COMPARE NAVIGATION SAVED VIEW FILTER PRESET DETAIL EDIT PREVIEW UNIFIED SECTION START ===
def build_pack_190_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_saved_view_filter_preset_detail_edit_history_version_compare_navigation_saved_view_filter_preset_detail_edit_preview_unified_section():
    """
    Pack 190 unified owner section.

    Safe/non-recursive:
    - reads only Pack 190 detail edit payload
    - does not call quick actions
    - does not call full unified page builder
    """
    try:
        from tower.policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_saved_view_filter_preset_detail_edit_history_version_compare_navigation_saved_view_filter_preset_detail_edit_preview import build_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_saved_view_filter_preset_detail_edit_history_version_compare_navigation_saved_view_filter_preset_detail_edit_preview_unified_owner_section
        return build_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_saved_view_filter_preset_detail_edit_history_version_compare_navigation_saved_view_filter_preset_detail_edit_preview_unified_owner_section()
    except Exception as exc:
        return {
            "section_id": "policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_saved_view_filter_preset_detail_edit_history_version_compare_navigation_saved_view_filter_preset_detail_edit_preview",
            "title": "Owner Note Version Compare Saved View Detail Edit",
            "subtitle": "Owner note version compare navigation saved view/filter preset detail edit section needs review.",
            "status": "review",
            "href": "/tower/policy-change-approval-receipt-owner-note-saved-view-preset-detail-edit-history-version-compare-saved-view-filter-preset-detail-edit-history-version-compare-navigation-saved-view-filter-preset-detail-edit-preview.json",
            "cards": [],
            "simulated_only": True,
            "detail_edit_preview_only": True,
            "saved_view_preview_only": True,
            "filter_preset_preview_only": True,
            "navigation_preview_only": True,
            "filter_navigation_preview_only": True,
            "cached_non_recursive": True,
            "error": str(exc),
        }


def append_pack_190_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_saved_view_filter_preset_detail_edit_history_version_compare_navigation_saved_view_filter_preset_detail_edit_preview_section(sections):
    """
    Append Pack 190 section to list-like unified section payloads.
    Safe if called more than once.
    """
    try:
        if not isinstance(sections, list):
            return sections

        existing_ids = {
            str(item.get("section_id") or item.get("id"))
            for item in sections
            if isinstance(item, dict)
        }

        if "policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_saved_view_filter_preset_detail_edit_history_version_compare_navigation_saved_view_filter_preset_detail_edit_preview" not in existing_ids:
            sections.append(build_pack_190_policy_change_approval_receipt_owner_note_saved_view_preset_detail_edit_history_version_compare_saved_view_filter_preset_detail_edit_history_version_compare_navigation_saved_view_filter_preset_detail_edit_preview_unified_section())

        return sections
    except Exception:
        return sections
# === PACK 190 POLICY CHANGE APPROVAL RECEIPT OWNER NOTE SAVED VIEW PRESET DETAIL EDIT HISTORY VERSION COMPARE SAVED VIEW FILTER PRESET DETAIL EDIT HISTORY VERSION COMPARE NAVIGATION SAVED VIEW FILTER PRESET DETAIL EDIT PREVIEW UNIFIED SECTION END ===



# === PACK 191 OWNER NOTE VC NAV DETAIL HISTORY UNIFIED SECTION START ===
def build_pack_191_owner_note_vc_nav_detail_history_v191_unified_section():
    """
    Pack 191 unified owner section.

    Safe/non-recursive:
    - reads only Pack 191 short-module history/version payload
    - does not call quick actions
    - does not call full unified page builder
    """
    try:
        from tower.owner_note_vc_nav_detail_history_v191 import build_owner_note_vc_nav_detail_history_v191_unified_owner_section
        return build_owner_note_vc_nav_detail_history_v191_unified_owner_section()
    except Exception as exc:
        return {
            "section_id": "owner_note_vc_nav_detail_history_v191",
            "title": "Owner Note Version Compare Saved View History",
            "subtitle": "Owner note version compare navigation saved view/filter preset detail edit history section needs review.",
            "status": "review",
            "href": "/tower/policy-change-approval-receipt-owner-note-saved-view-preset-detail-edit-history-version-compare-saved-view-filter-preset-detail-edit-history-version-compare-navigation-saved-view-filter-preset-detail-edit-history-version-preview.json",
            "cards": [],
            "simulated_only": True,
            "edit_history_preview_only": True,
            "version_preview_only": True,
            "rollback_preview_only": True,
            "restore_preview_only": True,
            "detail_edit_preview_only": True,
            "saved_view_preview_only": True,
            "filter_preset_preview_only": True,
            "cached_non_recursive": True,
            "error": str(exc),
        }


def append_pack_191_owner_note_vc_nav_detail_history_v191_section(sections):
    """
    Append Pack 191 section to list-like unified section payloads.
    Safe if called more than once.
    """
    try:
        if not isinstance(sections, list):
            return sections

        existing_ids = {
            str(item.get("section_id") or item.get("id"))
            for item in sections
            if isinstance(item, dict)
        }

        if "owner_note_vc_nav_detail_history_v191" not in existing_ids:
            sections.append(build_pack_191_owner_note_vc_nav_detail_history_v191_unified_section())

        return sections
    except Exception:
        return sections
# === PACK 191 OWNER NOTE VC NAV DETAIL HISTORY UNIFIED SECTION END ===



# === PACK 192 OWNER NOTE VC NAV VERSION COMPARE UNIFIED SECTION START ===
def build_pack_192_owner_note_vc_nav_version_compare_v192_unified_section():
    """
    Pack 192 unified owner section.

    Safe/non-recursive:
    - reads only Pack 192 short-module version compare payload
    - does not call quick actions
    - does not call full unified page builder
    """
    try:
        from tower.owner_note_vc_nav_version_compare_v192 import build_owner_note_vc_nav_version_compare_v192_unified_owner_section
        return build_owner_note_vc_nav_version_compare_v192_unified_owner_section()
    except Exception as exc:
        return {
            "section_id": "owner_note_vc_nav_version_compare_v192",
            "title": "Owner Note Version Compare Detail View",
            "subtitle": "Owner note version compare detail view section needs review.",
            "status": "review",
            "href": "/tower/owner-note-vc-nav-version-compare-v192.json",
            "cards": [],
            "simulated_only": True,
            "version_detail_preview_only": True,
            "compare_view_preview_only": True,
            "version_preview_only": True,
            "edit_history_preview_only": True,
            "cached_non_recursive": True,
            "error": str(exc),
        }


def append_pack_192_owner_note_vc_nav_version_compare_v192_section(sections):
    """
    Append Pack 192 section to list-like unified section payloads.
    Safe if called more than once.
    """
    try:
        if not isinstance(sections, list):
            return sections

        existing_ids = {
            str(item.get("section_id") or item.get("id"))
            for item in sections
            if isinstance(item, dict)
        }

        if "owner_note_vc_nav_version_compare_v192" not in existing_ids:
            sections.append(build_pack_192_owner_note_vc_nav_version_compare_v192_unified_section())

        return sections
    except Exception:
        return sections
# === PACK 192 OWNER NOTE VC NAV VERSION COMPARE UNIFIED SECTION END ===



# === PACK 193 OWNER NOTE VC NAV COMPARE FILTER UNIFIED SECTION START ===
def build_pack_193_owner_note_vc_nav_compare_filter_v193_unified_section():
    """
    Pack 193 unified owner section.

    Safe/non-recursive:
    - reads only Pack 193 short-module compare filter payload
    - does not call quick actions
    - does not call full unified page builder
    """
    try:
        from tower.owner_note_vc_nav_compare_filter_v193 import build_owner_note_vc_nav_compare_filter_v193_unified_owner_section
        return build_owner_note_vc_nav_compare_filter_v193_unified_owner_section()
    except Exception as exc:
        return {
            "section_id": "owner_note_vc_nav_compare_filter_v193",
            "title": "Owner Note Compare Filters",
            "subtitle": "Owner note version compare filter/search section needs review.",
            "status": "review",
            "href": "/tower/owner-note-vc-nav-compare-filter-v193.json",
            "cards": [],
            "simulated_only": True,
            "filter_preview_only": True,
            "search_facet_preview_only": True,
            "filter_navigation_preview_only": True,
            "version_detail_preview_only": True,
            "compare_view_preview_only": True,
            "cached_non_recursive": True,
            "error": str(exc),
        }


def append_pack_193_owner_note_vc_nav_compare_filter_v193_section(sections):
    """
    Append Pack 193 section to list-like unified section payloads.
    Safe if called more than once.
    """
    try:
        if not isinstance(sections, list):
            return sections

        existing_ids = {
            str(item.get("section_id") or item.get("id"))
            for item in sections
            if isinstance(item, dict)
        }

        if "owner_note_vc_nav_compare_filter_v193" not in existing_ids:
            sections.append(build_pack_193_owner_note_vc_nav_compare_filter_v193_unified_section())

        return sections
    except Exception:
        return sections
# === PACK 193 OWNER NOTE VC NAV COMPARE FILTER UNIFIED SECTION END ===



# === PACK 194 OWNER NOTE VC NAV FILTER NAV UNIFIED SECTION START ===
def build_pack_194_owner_note_vc_nav_filter_nav_v194_unified_section():
    """
    Pack 194 unified owner section.

    Safe/non-recursive:
    - reads only Pack 194 short-module filter navigation payload
    - does not call quick actions
    - does not call full unified page builder
    """
    try:
        from tower.owner_note_vc_nav_filter_nav_v194 import build_owner_note_vc_nav_filter_nav_v194_unified_owner_section
        return build_owner_note_vc_nav_filter_nav_v194_unified_owner_section()
    except Exception as exc:
        return {
            "section_id": "owner_note_vc_nav_filter_nav_v194",
            "title": "Owner Note Compare Filter Navigation",
            "subtitle": "Owner note version compare filter navigation section needs review.",
            "status": "review",
            "href": "/tower/owner-note-vc-nav-filter-nav-v194.json",
            "cards": [],
            "simulated_only": True,
            "navigation_preview_only": True,
            "filter_navigation_preview_only": True,
            "drawer_selection_preview_only": True,
            "filter_preview_only": True,
            "search_facet_preview_only": True,
            "cached_non_recursive": True,
            "error": str(exc),
        }


def append_pack_194_owner_note_vc_nav_filter_nav_v194_section(sections):
    """
    Append Pack 194 section to list-like unified section payloads.
    Safe if called more than once.
    """
    try:
        if not isinstance(sections, list):
            return sections

        existing_ids = {
            str(item.get("section_id") or item.get("id"))
            for item in sections
            if isinstance(item, dict)
        }

        if "owner_note_vc_nav_filter_nav_v194" not in existing_ids:
            sections.append(build_pack_194_owner_note_vc_nav_filter_nav_v194_unified_section())

        return sections
    except Exception:
        return sections
# === PACK 194 OWNER NOTE VC NAV FILTER NAV UNIFIED SECTION END ===



# === PACK 195 OWNER NOTE VC NAV DRAWER FOCUS UNIFIED SECTION START ===
def build_pack_195_owner_note_vc_nav_drawer_focus_v195_unified_section():
    """
    Pack 195 unified owner section.

    Safe/non-recursive:
    - reads only Pack 195 short-module selected drawer focus payload
    - does not call quick actions
    - does not call full unified page builder
    """
    try:
        from tower.owner_note_vc_nav_drawer_focus_v195 import build_owner_note_vc_nav_drawer_focus_v195_unified_owner_section
        return build_owner_note_vc_nav_drawer_focus_v195_unified_owner_section()
    except Exception as exc:
        return {
            "section_id": "owner_note_vc_nav_drawer_focus_v195",
            "title": "Owner Note Drawer Focus",
            "subtitle": "Owner note selected drawer focus section needs review.",
            "status": "review",
            "href": "/tower/owner-note-vc-nav-drawer-focus-v195.json",
            "cards": [],
            "simulated_only": True,
            "selected_drawer_preview_only": True,
            "compare_row_focus_preview_only": True,
            "drawer_action_preview_only": True,
            "breadcrumb_preview_only": True,
            "navigation_preview_only": True,
            "filter_navigation_preview_only": True,
            "drawer_selection_preview_only": True,
            "cached_non_recursive": True,
            "error": str(exc),
        }


def append_pack_195_owner_note_vc_nav_drawer_focus_v195_section(sections):
    """
    Append Pack 195 section to list-like unified section payloads.
    Safe if called more than once.
    """
    try:
        if not isinstance(sections, list):
            return sections

        existing_ids = {
            str(item.get("section_id") or item.get("id"))
            for item in sections
            if isinstance(item, dict)
        }

        if "owner_note_vc_nav_drawer_focus_v195" not in existing_ids:
            sections.append(build_pack_195_owner_note_vc_nav_drawer_focus_v195_unified_section())

        return sections
    except Exception:
        return sections
# === PACK 195 OWNER NOTE VC NAV DRAWER FOCUS UNIFIED SECTION END ===



# === PACK 196 OWNER NOTE VC NAV FOCUS ACTION RECEIPTS UNIFIED SECTION START ===
def build_pack_196_owner_note_vc_nav_focus_action_receipts_v196_unified_section():
    """
    Pack 196 unified owner section.

    Safe/non-recursive:
    - reads only Pack 196 short-module focus action receipt payload
    - does not call quick actions
    - does not call full unified page builder
    """
    try:
        from tower.owner_note_vc_nav_focus_action_receipts_v196 import build_owner_note_vc_nav_focus_action_receipts_v196_unified_owner_section
        return build_owner_note_vc_nav_focus_action_receipts_v196_unified_owner_section()
    except Exception as exc:
        return {
            "section_id": "owner_note_vc_nav_focus_action_receipts_v196",
            "title": "Owner Note Focus Action Receipts",
            "subtitle": "Owner note focus action receipts section needs review.",
            "status": "review",
            "href": "/tower/owner-note-vc-nav-focus-action-receipts-v196.json",
            "cards": [],
            "simulated_only": True,
            "action_receipt_preview_only": True,
            "blocked_action_receipt_preview_only": True,
            "preview_action_receipt_preview_only": True,
            "drawer_action_preview_only": True,
            "selected_drawer_preview_only": True,
            "compare_row_focus_preview_only": True,
            "cached_non_recursive": True,
            "error": str(exc),
        }


def append_pack_196_owner_note_vc_nav_focus_action_receipts_v196_section(sections):
    """
    Append Pack 196 section to list-like unified section payloads.
    Safe if called more than once.
    """
    try:
        if not isinstance(sections, list):
            return sections

        existing_ids = {
            str(item.get("section_id") or item.get("id"))
            for item in sections
            if isinstance(item, dict)
        }

        if "owner_note_vc_nav_focus_action_receipts_v196" not in existing_ids:
            sections.append(build_pack_196_owner_note_vc_nav_focus_action_receipts_v196_unified_section())

        return sections
    except Exception:
        return sections
# === PACK 196 OWNER NOTE VC NAV FOCUS ACTION RECEIPTS UNIFIED SECTION END ===



# === PACK 197 OWNER NOTE VC NAV ACTION RECEIPT FILTER UNIFIED SECTION START ===
def build_pack_197_owner_note_vc_nav_action_receipt_filter_v197_unified_section():
    """
    Pack 197 unified owner section.

    Safe/non-recursive:
    - reads only Pack 197 short-module action receipt filter payload
    - does not call quick actions
    - does not call full unified page builder
    """
    try:
        from tower.owner_note_vc_nav_action_receipt_filter_v197 import build_owner_note_vc_nav_action_receipt_filter_v197_unified_owner_section
        return build_owner_note_vc_nav_action_receipt_filter_v197_unified_owner_section()
    except Exception as exc:
        return {
            "section_id": "owner_note_vc_nav_action_receipt_filter_v197",
            "title": "Owner Note Action Receipt Filters",
            "subtitle": "Owner note action receipt filter/search section needs review.",
            "status": "review",
            "href": "/tower/owner-note-vc-nav-action-receipt-filter-v197.json",
            "cards": [],
            "simulated_only": True,
            "action_receipt_filter_preview_only": True,
            "search_facet_preview_only": True,
            "filter_preview_only": True,
            "action_receipt_preview_only": True,
            "cached_non_recursive": True,
            "error": str(exc),
        }


def append_pack_197_owner_note_vc_nav_action_receipt_filter_v197_section(sections):
    """
    Append Pack 197 section to list-like unified section payloads.
    Safe if called more than once.
    """
    try:
        if not isinstance(sections, list):
            return sections

        existing_ids = {
            str(item.get("section_id") or item.get("id"))
            for item in sections
            if isinstance(item, dict)
        }

        if "owner_note_vc_nav_action_receipt_filter_v197" not in existing_ids:
            sections.append(build_pack_197_owner_note_vc_nav_action_receipt_filter_v197_unified_section())

        return sections
    except Exception:
        return sections
# === PACK 197 OWNER NOTE VC NAV ACTION RECEIPT FILTER UNIFIED SECTION END ===



# === PACK 198 OWNER NOTE VC NAV ACTION RECEIPT FILTER NAV UNIFIED SECTION START ===
def build_pack_198_owner_note_vc_nav_action_receipt_filter_nav_v198_unified_section():
    """
    Pack 198 unified owner section.

    Safe/non-recursive:
    - reads only Pack 198 short-module action receipt filter navigation payload
    - does not call quick actions
    - does not call full unified page builder
    """
    try:
        from tower.owner_note_vc_nav_action_receipt_filter_nav_v198 import build_owner_note_vc_nav_action_receipt_filter_nav_v198_unified_owner_section
        return build_owner_note_vc_nav_action_receipt_filter_nav_v198_unified_owner_section()
    except Exception as exc:
        return {
            "section_id": "owner_note_vc_nav_action_receipt_filter_nav_v198",
            "title": "Owner Note Action Receipt Navigation",
            "subtitle": "Owner note action receipt filter navigation section needs review.",
            "status": "review",
            "href": "/tower/owner-note-vc-nav-action-receipt-filter-nav-v198.json",
            "cards": [],
            "simulated_only": True,
            "action_receipt_navigation_preview_only": True,
            "receipt_selection_preview_only": True,
            "action_receipt_filter_preview_only": True,
            "search_facet_preview_only": True,
            "filter_preview_only": True,
            "cached_non_recursive": True,
            "error": str(exc),
        }


def append_pack_198_owner_note_vc_nav_action_receipt_filter_nav_v198_section(sections):
    """
    Append Pack 198 section to list-like unified section payloads.
    Safe if called more than once.
    """
    try:
        if not isinstance(sections, list):
            return sections

        existing_ids = {
            str(item.get("section_id") or item.get("id"))
            for item in sections
            if isinstance(item, dict)
        }

        if "owner_note_vc_nav_action_receipt_filter_nav_v198" not in existing_ids:
            sections.append(build_pack_198_owner_note_vc_nav_action_receipt_filter_nav_v198_unified_section())

        return sections
    except Exception:
        return sections
# === PACK 198 OWNER NOTE VC NAV ACTION RECEIPT FILTER NAV UNIFIED SECTION END ===



# === PACK 199 OWNER NOTE VC NAV RECEIPT DETAIL FOCUS UNIFIED SECTION START ===
def build_pack_199_owner_note_vc_nav_receipt_detail_focus_v199_unified_section():
    """
    Pack 199 unified owner section.

    Safe/non-recursive:
    - reads only Pack 199 short-module receipt detail focus payload
    - does not call quick actions
    - does not call full unified page builder
    """
    try:
        from tower.owner_note_vc_nav_receipt_detail_focus_v199 import build_owner_note_vc_nav_receipt_detail_focus_v199_unified_owner_section
        return build_owner_note_vc_nav_receipt_detail_focus_v199_unified_owner_section()
    except Exception as exc:
        return {
            "section_id": "owner_note_vc_nav_receipt_detail_focus_v199",
            "title": "Owner Note Receipt Detail Focus",
            "subtitle": "Owner note receipt detail focus section needs review.",
            "status": "review",
            "href": "/tower/owner-note-vc-nav-receipt-detail-focus-v199.json",
            "cards": [],
            "simulated_only": True,
            "receipt_detail_focus_preview_only": True,
            "receipt_safety_detail_preview_only": True,
            "receipt_action_panel_preview_only": True,
            "receipt_breadcrumb_preview_only": True,
            "action_receipt_navigation_preview_only": True,
            "receipt_selection_preview_only": True,
            "cached_non_recursive": True,
            "error": str(exc),
        }


def append_pack_199_owner_note_vc_nav_receipt_detail_focus_v199_section(sections):
    """
    Append Pack 199 section to list-like unified section payloads.
    Safe if called more than once.
    """
    try:
        if not isinstance(sections, list):
            return sections

        existing_ids = {
            str(item.get("section_id") or item.get("id"))
            for item in sections
            if isinstance(item, dict)
        }

        if "owner_note_vc_nav_receipt_detail_focus_v199" not in existing_ids:
            sections.append(build_pack_199_owner_note_vc_nav_receipt_detail_focus_v199_unified_section())

        return sections
    except Exception:
        return sections
# === PACK 199 OWNER NOTE VC NAV RECEIPT DETAIL FOCUS UNIFIED SECTION END ===



# === PACK 200 OWNER NOTE VC NAV RECEIPT CHAIN CHECKPOINT UNIFIED SECTION START ===
def build_pack_200_owner_note_vc_nav_receipt_chain_checkpoint_v200_unified_section():
    """
    Pack 200 unified owner section.

    Safe/non-recursive:
    - reads only Pack 200 short-module receipt chain checkpoint payload
    - does not call quick actions
    - does not call full unified page builder
    """
    try:
        from tower.owner_note_vc_nav_receipt_chain_checkpoint_v200 import build_owner_note_vc_nav_receipt_chain_checkpoint_v200_unified_owner_section
        return build_owner_note_vc_nav_receipt_chain_checkpoint_v200_unified_owner_section()
    except Exception as exc:
        return {
            "section_id": "owner_note_vc_nav_receipt_chain_checkpoint_v200",
            "title": "Owner Note Receipt Chain Checkpoint",
            "subtitle": "Owner note receipt chain checkpoint section needs review.",
            "status": "review",
            "href": "/tower/owner-note-vc-nav-receipt-chain-checkpoint-v200.json",
            "cards": [],
            "simulated_only": True,
            "checkpoint_preview_only": True,
            "receipt_chain_checkpoint_preview_only": True,
            "cached_non_recursive": True,
            "error": str(exc),
        }


def append_pack_200_owner_note_vc_nav_receipt_chain_checkpoint_v200_section(sections):
    """
    Append Pack 200 section to list-like unified section payloads.
    Safe if called more than once.
    """
    try:
        if not isinstance(sections, list):
            return sections

        existing_ids = {
            str(item.get("section_id") or item.get("id"))
            for item in sections
            if isinstance(item, dict)
        }

        if "owner_note_vc_nav_receipt_chain_checkpoint_v200" not in existing_ids:
            sections.append(build_pack_200_owner_note_vc_nav_receipt_chain_checkpoint_v200_unified_section())

        return sections
    except Exception:
        return sections
# === PACK 200 OWNER NOTE VC NAV RECEIPT CHAIN CHECKPOINT UNIFIED SECTION END ===



# === PACK 201 RECEIPT CHAIN OPERATIONAL HANDOFF UNIFIED SECTION START ===
def build_pack_201_receipt_chain_operational_handoff_v201_unified_section():
    """
    Pack 201 unified owner section.

    Safe/non-recursive:
    - reads only Pack 201 short-module operational handoff payload
    - does not call quick actions
    - does not call full unified page builder
    """
    try:
        from tower.receipt_chain_operational_handoff_v201 import build_receipt_chain_operational_handoff_v201_unified_owner_section
        return build_receipt_chain_operational_handoff_v201_unified_owner_section()
    except Exception as exc:
        return {
            "section_id": "receipt_chain_operational_handoff_v201",
            "title": "Receipt Chain Operational Handoff",
            "subtitle": "Receipt chain operational handoff section needs review.",
            "status": "review",
            "href": "/tower/receipt-chain-operational-handoff-v201.json",
            "cards": [],
            "simulated_only": True,
            "operational_handoff_preview_only": True,
            "receipt_chain_handoff_preview_only": True,
            "checkpoint_preview_only": True,
            "receipt_chain_checkpoint_preview_only": True,
            "owner_action_menu_preview_only": True,
            "evidence_map_preview_only": True,
            "routing_preview_only": True,
            "cached_non_recursive": True,
            "error": str(exc),
        }


def append_pack_201_receipt_chain_operational_handoff_v201_section(sections):
    """
    Append Pack 201 section to list-like unified section payloads.
    Safe if called more than once.
    """
    try:
        if not isinstance(sections, list):
            return sections

        existing_ids = {
            str(item.get("section_id") or item.get("id"))
            for item in sections
            if isinstance(item, dict)
        }

        if "receipt_chain_operational_handoff_v201" not in existing_ids:
            sections.append(build_pack_201_receipt_chain_operational_handoff_v201_unified_section())

        return sections
    except Exception:
        return sections
# === PACK 201 RECEIPT CHAIN OPERATIONAL HANDOFF UNIFIED SECTION END ===



# === PACK 202 RECEIPT CHAIN HANDOFF SAVED VIEWS UNIFIED SECTION START ===
def build_pack_202_receipt_chain_handoff_saved_views_v202_unified_section():
    """
    Pack 202 unified owner section.

    Safe/non-recursive:
    - reads only Pack 202 short-module saved views/filter presets payload
    - does not call quick actions
    - does not call full unified page builder
    """
    try:
        from tower.receipt_chain_handoff_saved_views_v202 import build_receipt_chain_handoff_saved_views_v202_unified_owner_section
        return build_receipt_chain_handoff_saved_views_v202_unified_owner_section()
    except Exception as exc:
        return {
            "section_id": "receipt_chain_handoff_saved_views_v202",
            "title": "Receipt Chain Handoff Saved Views",
            "subtitle": "Receipt chain handoff saved views/filter presets section needs review.",
            "status": "review",
            "href": "/tower/receipt-chain-handoff-saved-views-v202.json",
            "cards": [],
            "simulated_only": True,
            "saved_view_preview_only": True,
            "filter_preset_preview_only": True,
            "selected_saved_view_preview_only": True,
            "operational_handoff_preview_only": True,
            "receipt_chain_handoff_preview_only": True,
            "cached_non_recursive": True,
            "error": str(exc),
        }


def append_pack_202_receipt_chain_handoff_saved_views_v202_section(sections):
    """
    Append Pack 202 section to list-like unified section payloads.
    Safe if called more than once.
    """
    try:
        if not isinstance(sections, list):
            return sections

        existing_ids = {
            str(item.get("section_id") or item.get("id"))
            for item in sections
            if isinstance(item, dict)
        }

        if "receipt_chain_handoff_saved_views_v202" not in existing_ids:
            sections.append(build_pack_202_receipt_chain_handoff_saved_views_v202_unified_section())

        return sections
    except Exception:
        return sections
# === PACK 202 RECEIPT CHAIN HANDOFF SAVED VIEWS UNIFIED SECTION END ===



# === PACK 203 RECEIPT CHAIN EVIDENCE PACKET UNIFIED SECTION START ===
def build_pack_203_receipt_chain_evidence_packet_v203_unified_section():
    """
    Pack 203 unified owner section.

    Safe/non-recursive:
    - reads only Pack 203 short-module evidence packet payload
    - does not call quick actions
    - does not call full unified page builder
    """
    try:
        from tower.receipt_chain_evidence_packet_v203 import build_receipt_chain_evidence_packet_v203_unified_owner_section
        return build_receipt_chain_evidence_packet_v203_unified_owner_section()
    except Exception as exc:
        return {
            "section_id": "receipt_chain_evidence_packet_v203",
            "title": "Receipt Chain Evidence Packet",
            "subtitle": "Receipt chain evidence packet section needs review.",
            "status": "review",
            "href": "/tower/receipt-chain-evidence-packet-v203.json",
            "cards": [],
            "simulated_only": True,
            "evidence_packet_preview_only": True,
            "evidence_bundle_preview_only": True,
            "packet_section_preview_only": True,
            "export_request_preview_only": True,
            "export_blocked": True,
            "raw_evidence_redacted": True,
            "cached_non_recursive": True,
            "error": str(exc),
        }


def append_pack_203_receipt_chain_evidence_packet_v203_section(sections):
    """
    Append Pack 203 section to list-like unified section payloads.
    Safe if called more than once.
    """
    try:
        if not isinstance(sections, list):
            return sections

        existing_ids = {
            str(item.get("section_id") or item.get("id"))
            for item in sections
            if isinstance(item, dict)
        }

        if "receipt_chain_evidence_packet_v203" not in existing_ids:
            sections.append(build_pack_203_receipt_chain_evidence_packet_v203_unified_section())

        return sections
    except Exception:
        return sections
# === PACK 203 RECEIPT CHAIN EVIDENCE PACKET UNIFIED SECTION END ===



# === PACK 204 RECEIPT CHAIN RECHECK EXPIRATION HANDOFF UNIFIED SECTION START ===
def build_pack_204_receipt_chain_recheck_expiration_handoff_v204_unified_section():
    """
    Pack 204 unified owner section.

    Safe/non-recursive:
    - reads only Pack 204 short-module recheck/expiration handoff payload
    - does not call quick actions
    - does not call full unified page builder
    """
    try:
        from tower.receipt_chain_recheck_expiration_handoff_v204 import build_receipt_chain_recheck_expiration_handoff_v204_unified_owner_section
        return build_receipt_chain_recheck_expiration_handoff_v204_unified_owner_section()
    except Exception as exc:
        return {
            "section_id": "receipt_chain_recheck_expiration_handoff_v204",
            "title": "Receipt Chain Recheck Handoff",
            "subtitle": "Receipt chain recheck/expiration handoff section needs review.",
            "status": "review",
            "href": "/tower/receipt-chain-recheck-expiration-handoff-v204.json",
            "cards": [],
            "simulated_only": True,
            "recheck_expiration_handoff_preview_only": True,
            "recheck_hook_preview_only": True,
            "expiration_trigger_preview_only": True,
            "renewal_trigger_preview_only": True,
            "freshness_lane_preview_only": True,
            "owner_followup_queue_preview_only": True,
            "cached_non_recursive": True,
            "error": str(exc),
        }


def append_pack_204_receipt_chain_recheck_expiration_handoff_v204_section(sections):
    """
    Append Pack 204 section to list-like unified section payloads.
    Safe if called more than once.
    """
    try:
        if not isinstance(sections, list):
            return sections

        existing_ids = {
            str(item.get("section_id") or item.get("id"))
            for item in sections
            if isinstance(item, dict)
        }

        if "receipt_chain_recheck_expiration_handoff_v204" not in existing_ids:
            sections.append(build_pack_204_receipt_chain_recheck_expiration_handoff_v204_unified_section())

        return sections
    except Exception:
        return sections
# === PACK 204 RECEIPT CHAIN RECHECK EXPIRATION HANDOFF UNIFIED SECTION END ===



# === PACK 205 RECEIPT CHAIN OPERATIONAL BATCH CHECKPOINT UNIFIED SECTION START ===
def build_pack_205_receipt_chain_operational_batch_checkpoint_v205_unified_section():
    """
    Pack 205 unified owner section.

    Safe/non-recursive:
    - reads only Pack 205 short-module operational batch checkpoint payload
    - does not call quick actions
    - does not call full unified page builder
    """
    try:
        from tower.receipt_chain_operational_batch_checkpoint_v205 import build_receipt_chain_operational_batch_checkpoint_v205_unified_owner_section
        return build_receipt_chain_operational_batch_checkpoint_v205_unified_owner_section()
    except Exception as exc:
        return {
            "section_id": "receipt_chain_operational_batch_checkpoint_v205",
            "title": "Receipt Chain Batch Checkpoint",
            "subtitle": "Receipt chain operational batch checkpoint section needs review.",
            "status": "review",
            "href": "/tower/receipt-chain-operational-batch-checkpoint-v205.json",
            "cards": [],
            "simulated_only": True,
            "batch_checkpoint_preview_only": True,
            "operational_batch_checkpoint_preview_only": True,
            "cached_non_recursive": True,
            "error": str(exc),
        }


def append_pack_205_receipt_chain_operational_batch_checkpoint_v205_section(sections):
    """
    Append Pack 205 section to list-like unified section payloads.
    Safe if called more than once.
    """
    try:
        if not isinstance(sections, list):
            return sections

        existing_ids = {
            str(item.get("section_id") or item.get("id"))
            for item in sections
            if isinstance(item, dict)
        }

        if "receipt_chain_operational_batch_checkpoint_v205" not in existing_ids:
            sections.append(build_pack_205_receipt_chain_operational_batch_checkpoint_v205_unified_section())

        return sections
    except Exception:
        return sections
# === PACK 205 RECEIPT CHAIN OPERATIONAL BATCH CHECKPOINT UNIFIED SECTION END ===



# === PACK 206 RECEIPT CHAIN POST BATCH OPS UNIFIED SECTION START ===
def build_pack_206_receipt_chain_post_batch_ops_v206_unified_section():
    """
    Pack 206 unified owner section.

    Safe/non-recursive:
    - reads only Pack 206 short-module post-batch ops payload
    - does not call quick actions
    - does not call full unified page builder
    """
    try:
        from tower.receipt_chain_post_batch_ops_v206 import build_receipt_chain_post_batch_ops_v206_unified_owner_section
        return build_receipt_chain_post_batch_ops_v206_unified_owner_section()
    except Exception as exc:
        return {
            "section_id": "receipt_chain_post_batch_ops_v206",
            "title": "Receipt Chain Post-Batch Ops",
            "subtitle": "Receipt chain post-batch ops section needs review.",
            "status": "review",
            "href": "/tower/receipt-chain-post-batch-ops-v206.json",
            "cards": [],
            "simulated_only": True,
            "post_batch_ops_preview_only": True,
            "operational_readiness_preview_only": True,
            "containment_lane_preview_only": True,
            "incident_lane_preview_only": True,
            "archive_lane_preview_only": True,
            "gateway_lane_preview_only": True,
            "owner_next_action_preview_only": True,
            "next_batch_board_preview_only": True,
            "cached_non_recursive": True,
            "error": str(exc),
        }


def append_pack_206_receipt_chain_post_batch_ops_v206_section(sections):
    """
    Append Pack 206 section to list-like unified section payloads.
    Safe if called more than once.
    """
    try:
        if not isinstance(sections, list):
            return sections

        existing_ids = {
            str(item.get("section_id") or item.get("id"))
            for item in sections
            if isinstance(item, dict)
        }

        if "receipt_chain_post_batch_ops_v206" not in existing_ids:
            sections.append(build_pack_206_receipt_chain_post_batch_ops_v206_unified_section())

        return sections
    except Exception:
        return sections
# === PACK 206 RECEIPT CHAIN POST BATCH OPS UNIFIED SECTION END ===

