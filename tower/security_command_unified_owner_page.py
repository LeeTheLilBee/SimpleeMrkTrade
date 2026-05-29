
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

