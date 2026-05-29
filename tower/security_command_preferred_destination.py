
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "tower" / "data"

PREFERRED_STATUS_PATH = DATA_DIR / "security_command_preferred_destination_status.json"
PREFERRED_PANEL_PATH = DATA_DIR / "security_command_preferred_destination_panel.html"

PREFERRED_SECURITY_COMMAND_ROUTE = "/tower/security-command-unified"
LEGACY_SECURITY_COMMAND_ROUTE = "/tower/security-command"
SMOKE_SECURITY_COMMAND_ROUTE = "/tower/security-command-smoke"
LINKS_STATUS_ROUTE = "/tower/security-command-links.json"
GUARD_STATUS_ROUTE = "/tower/ob-guard-status.json"


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


def _unified_health() -> Dict[str, Any]:
    try:
        from tower.security_command_unified_owner_page import build_unified_owner_security_command_status
        status = build_unified_owner_security_command_status(write_html=True)
        return {
            "ok": status.get("ok") is True,
            "status": status.get("status"),
            "readiness_score": status.get("readiness_score"),
            "html_path": status.get("html_path"),
            "failed_checks": status.get("failed_checks"),
        }
    except Exception as exc:
        return {"ok": False, "error_type": type(exc).__name__}


def _navigation_health() -> Dict[str, Any]:
    try:
        from tower.security_command_navigation_links import build_security_command_navigation_links_status
        status = build_security_command_navigation_links_status(write_panel=True)
        links = status.get("links", []) if isinstance(status.get("links"), list) else []
        return {
            "ok": status.get("ok") is True,
            "status": status.get("status"),
            "readiness_score": status.get("readiness_score"),
            "link_count": status.get("link_count"),
            "links": links,
            "hrefs": [link.get("href") for link in links if isinstance(link, dict)],
        }
    except Exception as exc:
        return {"ok": False, "error_type": type(exc).__name__}


def preferred_security_command_links() -> list[dict[str, Any]]:
    return [
        {
            "link_id": "tower_security_command_unified_preferred",
            "title": "Unified Security Command",
            "href": PREFERRED_SECURITY_COMMAND_ROUTE,
            "kind": "preferred",
            "pack": "116+117",
            "available": True,
            "readiness_score": 100,
            "human_reason": "Preferred owner Security Command destination. Combines links, object visibility, route health, and checkpoint health.",
        },
        {
            "link_id": "tower_security_command_legacy",
            "title": "Legacy Security Command",
            "href": LEGACY_SECURITY_COMMAND_ROUTE,
            "kind": "legacy",
            "pack": "022E+",
            "available": True,
            "readiness_score": 100,
            "human_reason": "Original Security Command route kept as a fallback.",
        },
        {
            "link_id": "tower_security_command_smoke",
            "title": "Security Command Composition Smoke",
            "href": SMOKE_SECURITY_COMMAND_ROUTE,
            "kind": "smoke",
            "pack": "114",
            "available": True,
            "readiness_score": 100,
            "human_reason": "Pack 114 smoke page proving Security Command composition renders with object visibility attached.",
        },
        {
            "link_id": "tower_security_command_links_json",
            "title": "Security Command Links JSON",
            "href": LINKS_STATUS_ROUTE,
            "kind": "status_json",
            "pack": "115",
            "available": True,
            "readiness_score": 100,
            "human_reason": "Pack 115 guarded JSON endpoint for Security Command navigation/status links.",
        },
        {
            "link_id": "tower_ob_guard_status_json",
            "title": "OB Guard Status JSON",
            "href": GUARD_STATUS_ROUTE,
            "kind": "status_json",
            "pack": "105",
            "available": True,
            "readiness_score": 100,
            "human_reason": "OB route guard coverage status endpoint.",
        },
    ]


def build_security_command_preferred_destination_status(write_panel: bool = True) -> Dict[str, Any]:
    route_health = _route_health()
    unified_health = _unified_health()
    navigation_health = _navigation_health()

    links = preferred_security_command_links()
    hrefs = [link.get("href") for link in links]

    checks = {
        "preferred_route_set": PREFERRED_SECURITY_COMMAND_ROUTE == "/tower/security-command-unified",
        "preferred_route_in_links": PREFERRED_SECURITY_COMMAND_ROUTE in hrefs,
        "legacy_route_kept": LEGACY_SECURITY_COMMAND_ROUTE in hrefs,
        "smoke_route_kept": SMOKE_SECURITY_COMMAND_ROUTE in hrefs,
        "links_json_kept": LINKS_STATUS_ROUTE in hrefs,
        "guard_status_kept": GUARD_STATUS_ROUTE in hrefs,

        "route_health_ok": route_health.get("ok") is True,
        "route_coverage_100": route_health.get("coverage_pct") == 100,
        "unguarded_needed_zero": route_health.get("unguarded_needed_count") == 0,
        "unguarded_high_risk_zero": route_health.get("unguarded_high_risk_count") == 0,

        "unified_health_ok": unified_health.get("ok") is True,
        "unified_status_passed": unified_health.get("status") == "passed",
        "unified_ready": unified_health.get("readiness_score") == 100,

        "navigation_health_ok": navigation_health.get("ok") is True,
        "navigation_status_passed": navigation_health.get("status") == "passed",
        "navigation_ready": navigation_health.get("readiness_score") == 100,
    }

    failed_checks = [key for key, ok in checks.items() if not ok]

    status = {
        "ok": not failed_checks,
        "pack": "117",
        "status": "passed" if not failed_checks else "failed",
        "created_at": _utc_now(),
        "status_path": str(PREFERRED_STATUS_PATH),
        "panel_path": str(PREFERRED_PANEL_PATH),
        "preferred_route": PREFERRED_SECURITY_COMMAND_ROUTE,
        "legacy_route": LEGACY_SECURITY_COMMAND_ROUTE,
        "links": links,
        "link_count": len(links),
        "hrefs": hrefs,
        "checks": checks,
        "failed_checks": failed_checks,
        "route_health": route_health,
        "unified_health": unified_health,
        "navigation_health": navigation_health,
        "readiness_score": 100 if not failed_checks else max(0, 100 - (len(failed_checks) * 8)),
        "readiness_label": (
            "Unified Security Command is the preferred destination"
            if not failed_checks
            else "Preferred Security Command destination needs review"
        ),
        "human_reason": "Unified Security Command is now the preferred Tower Security Command destination while legacy and smoke routes remain available.",
        "soulaana_translation": "Soulaana: The main sign now points to the real command room.",
    }

    scan = _safe_scan(status)
    status["no_secret_leakage"] = scan.get("ok") is True
    status["leakage_scan"] = scan
    status["status_fingerprint"] = _fingerprint(status)

    _write_json(PREFERRED_STATUS_PATH, status)

    try:
        from tower.tamper_evident_audit_chain import create_tamper_chain_entry
        create_tamper_chain_entry(
            event_type="tower_security_command_preferred_destination_status",
            source_name="security_command_preferred_destination_status",
            source_path=str(PREFERRED_STATUS_PATH),
            source_hash=_fingerprint(status),
            record_count=len(links),
            actor_user_id="tower_system",
            reason="Pack 117 preferred Security Command destination status generated.",
            metadata={
                "pack": "117",
                "status": status.get("status"),
                "preferred_route": PREFERRED_SECURITY_COMMAND_ROUTE,
                "readiness_score": status.get("readiness_score"),
            },
        )
    except Exception:
        pass

    if write_panel:
        write_security_command_preferred_destination_panel(status)

    return status


def render_security_command_preferred_destination_section(status: Dict[str, Any] | None = None) -> str:
    status = status if isinstance(status, dict) else build_security_command_preferred_destination_status(write_panel=False)
    links = status.get("links", []) if isinstance(status.get("links"), list) else []

    cards = []
    for link in links:
        title = _html_escape(link.get("title", "Tower Link"))
        href = _html_escape(link.get("href", "#"))
        kind = _html_escape(link.get("kind", "link"))
        pack = _html_escape(link.get("pack", ""))
        reason = _html_escape(link.get("human_reason", ""))
        readiness = _html_escape(link.get("readiness_score", 0))

        css = "preferred" if link.get("href") == PREFERRED_SECURITY_COMMAND_ROUTE else "normal"

        cards.append(f"""
        <a class="preferred-command-card preferred-command-card--{css}" href="{href}">
          <div class="preferred-command-card__eyebrow">{kind} · {pack}</div>
          <h3>{title}</h3>
          <p>{reason}</p>
          <small>Readiness: {readiness}</small>
        </a>
        """)

    html = f"""
<!-- PACK117_SECURITY_COMMAND_PREFERRED_DESTINATION_SECTION -->
<section class="preferred-command-destination" data-pack="117">
  <style>
    .preferred-command-destination {{
      margin: 24px 0;
      border: 1px solid rgba(220,183,94,.34);
      border-radius: 28px;
      padding: 22px;
      background:
        radial-gradient(circle at top left, rgba(220,183,94,.16), transparent 34%),
        linear-gradient(135deg, rgba(75,48,18,.58), rgba(8,9,7,.94));
      color: #f5ead2;
      box-shadow: 0 18px 70px rgba(0,0,0,.32);
    }}
    .preferred-command-destination__eyebrow {{
      color: rgba(220,183,94,.86);
      text-transform: uppercase;
      letter-spacing: .14em;
      font-size: 11px;
      margin-bottom: 8px;
    }}
    .preferred-command-destination h2 {{
      margin: 0;
      font-size: 24px;
      letter-spacing: -.03em;
    }}
    .preferred-command-destination p {{
      color: rgba(245,234,210,.72);
      line-height: 1.45;
    }}
    .preferred-command-grid {{
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 12px;
      margin-top: 14px;
    }}
    .preferred-command-card {{
      display: block;
      color: inherit;
      text-decoration: none;
      border: 1px solid rgba(245,234,210,.13);
      border-radius: 20px;
      padding: 14px;
      background: rgba(255,255,255,.04);
      transition: transform .18s ease, border-color .18s ease;
    }}
    .preferred-command-card:hover {{
      transform: translateY(-2px);
      border-color: rgba(220,183,94,.7);
    }}
    .preferred-command-card--preferred {{
      border-color: rgba(143,221,158,.45);
      background: rgba(143,221,158,.06);
    }}
    .preferred-command-card__eyebrow {{
      color: rgba(220,183,94,.84);
      text-transform: uppercase;
      letter-spacing: .12em;
      font-size: 10px;
      margin-bottom: 7px;
    }}
    .preferred-command-card h3 {{
      margin: 0 0 7px;
      font-size: 16px;
    }}
    .preferred-command-card p {{
      margin: 0 0 8px;
      color: rgba(245,234,210,.72);
    }}
    .preferred-command-card small {{
      color: rgba(245,234,210,.55);
    }}
    @media (max-width: 900px) {{
      .preferred-command-grid {{
        grid-template-columns: 1fr;
      }}
    }}
  </style>

  <div class="preferred-command-destination__eyebrow">PACK 117 · PREFERRED DESTINATION</div>
  <h2>Preferred Security Command Destination</h2>
  <p>{_html_escape(status.get('human_reason', 'Unified Security Command is preferred.'))}</p>

  <div class="preferred-command-grid">
    {''.join(cards)}
  </div>
</section>
<!-- END PACK117_SECURITY_COMMAND_PREFERRED_DESTINATION_SECTION -->
"""
    return html


def write_security_command_preferred_destination_panel(status: Dict[str, Any] | None = None) -> Dict[str, Any]:
    status = status if isinstance(status, dict) else build_security_command_preferred_destination_status(write_panel=False)
    html = f"""<!doctype html>
<html lang="en">
<head><meta charset="utf-8"><title>The Tower · Preferred Security Command</title></head>
<body style="margin:0;background:#080907;color:#f5ead2;font-family:system-ui;padding:32px;">
<main style="max-width:1180px;margin:auto;">
{render_security_command_preferred_destination_section(status)}
</main>
</body>
</html>
"""
    _write_text(PREFERRED_PANEL_PATH, html)
    return {
        "ok": True,
        "pack": "117",
        "decision": "preferred_security_command_destination_panel_written",
        "path": str(PREFERRED_PANEL_PATH),
        "human_reason": "Preferred Security Command destination panel written.",
        "soulaana_translation": "Soulaana: Preferred command destination panel posted.",
    }


def load_security_command_preferred_destination_status() -> Dict[str, Any]:
    status = _load_json(PREFERRED_STATUS_PATH, {})
    if not status:
        status = build_security_command_preferred_destination_status(write_panel=True)
    return status


def security_command_preferred_destination_status_card() -> Dict[str, Any]:
    status = load_security_command_preferred_destination_status()
    return {
        "ok": status.get("ok") is True,
        "pack": "117",
        "title": "Preferred Security Command",
        "preferred_route": status.get("preferred_route"),
        "legacy_route": status.get("legacy_route"),
        "link_count": status.get("link_count", 0),
        "readiness_score": status.get("readiness_score", 0),
        "panel_path": status.get("panel_path", str(PREFERRED_PANEL_PATH)),
        "status_path": status.get("status_path", str(PREFERRED_STATUS_PATH)),
        "human_reason": "Preferred Security Command destination status card loaded.",
        "soulaana_translation": "Soulaana: Preferred command room route is visible.",
    }


def reset_security_command_preferred_destination_for_test() -> Dict[str, Any]:
    _write_json(PREFERRED_STATUS_PATH, {
        "ok": True,
        "pack": "117",
        "reset_at": _utc_now(),
        "human_reason": "Preferred Security Command destination reset for test.",
    })
    if PREFERRED_PANEL_PATH.exists():
        try:
            PREFERRED_PANEL_PATH.unlink()
        except Exception:
            pass
    return {
        "ok": True,
        "decision": "preferred_security_command_destination_reset_for_test",
        "soulaana_translation": "Soulaana: Preferred command destination reset for a clean test lane.",
    }
