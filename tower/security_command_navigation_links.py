
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "tower" / "data"

NAV_STATUS_PATH = DATA_DIR / "security_command_navigation_links_status.json"
NAV_PANEL_PATH = DATA_DIR / "security_command_navigation_links_panel.html"


CORE_SECURITY_COMMAND_LINKS = [
    {
        "link_id": "tower_security_command_main",
        "title": "Security Command",
        "href": "/tower/security-command",
        "kind": "primary",
        "pack": "022E+",
        "human_reason": "Main Tower Security Command page.",
    },
    {
        "link_id": "tower_security_command_smoke",
        "title": "Security Command Composition Smoke",
        "href": "/tower/security-command-smoke",
        "kind": "smoke",
        "pack": "114",
        "human_reason": "Pack 114 smoke page proving Security Command composition renders with object visibility attached.",
    },
    {
        "link_id": "tower_ob_guard_status_json",
        "title": "OB Guard Status JSON",
        "href": "/tower/ob-guard-status.json",
        "kind": "status_json",
        "pack": "105",
        "human_reason": "OB route guard coverage status endpoint.",
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


def _composition_health() -> Dict[str, Any]:
    try:
        from tower.security_command_composition_smoke import build_security_command_composition_status
        status = build_security_command_composition_status(write_html=True)
        return {
            "ok": status.get("ok") is True,
            "status": status.get("status"),
            "readiness_score": status.get("readiness_score"),
            "failed_checks": status.get("failed_checks"),
            "html_path": status.get("html_path"),
        }
    except Exception as exc:
        return {"ok": False, "error_type": type(exc).__name__}


def _object_checkpoint_health() -> Dict[str, Any]:
    try:
        from tower.ob_object_permission_integration_checkpoint import build_object_permission_integration_checkpoint
        checkpoint = build_object_permission_integration_checkpoint(write_panel=True)
        return {
            "ok": checkpoint.get("ok") is True,
            "status": checkpoint.get("status"),
            "readiness_score": checkpoint.get("readiness_score"),
            "helper_wrapped_count": checkpoint.get("helper_wrapped_count"),
            "warnings": checkpoint.get("warnings"),
        }
    except Exception as exc:
        return {"ok": False, "error_type": type(exc).__name__}


def build_security_command_navigation_links_status(write_panel: bool = True) -> Dict[str, Any]:
    route_health = _route_health()
    composition_health = _composition_health()
    object_health = _object_checkpoint_health()

    links: List[Dict[str, Any]] = []
    for link in CORE_SECURITY_COMMAND_LINKS:
        item = dict(link)
        item["available"] = True

        if item.get("link_id") == "tower_security_command_smoke":
            item["available"] = composition_health.get("ok") is True
            item["readiness_score"] = composition_health.get("readiness_score", 0)
        elif item.get("link_id") == "tower_ob_guard_status_json":
            item["available"] = route_health.get("ok") is True
            item["readiness_score"] = route_health.get("readiness_score", 0)
        else:
            item["readiness_score"] = 100 if route_health.get("ok") else 0

        links.append(item)

    checks = {
        "route_coverage_ok": route_health.get("ok") is True,
        "route_coverage_100": route_health.get("coverage_pct") == 100,
        "unguarded_needed_zero": route_health.get("unguarded_needed_count") == 0,
        "unguarded_high_risk_zero": route_health.get("unguarded_high_risk_count") == 0,
        "composition_smoke_ok": composition_health.get("ok") is True,
        "composition_smoke_passed": composition_health.get("status") == "passed",
        "object_checkpoint_ok": object_health.get("ok") is True,
        "object_checkpoint_passed": object_health.get("status") == "passed",
        "helper_wrapped_zero": object_health.get("helper_wrapped_count") == 0,
        "all_links_available": all(link.get("available") is True for link in links),
    }

    failed_checks = [key for key, value in checks.items() if not value]

    status = {
        "ok": not failed_checks,
        "pack": "115",
        "status": "passed" if not failed_checks else "failed",
        "created_at": _utc_now(),
        "status_path": str(NAV_STATUS_PATH),
        "panel_path": str(NAV_PANEL_PATH),
        "links": links,
        "link_count": len(links),
        "checks": checks,
        "failed_checks": failed_checks,
        "route_health": route_health,
        "composition_health": composition_health,
        "object_checkpoint_health": object_health,
        "readiness_score": 100 if not failed_checks else max(0, 100 - (len(failed_checks) * 10)),
        "readiness_label": (
            "Security Command navigation/status links ready"
            if not failed_checks
            else "Security Command navigation/status links need review"
        ),
        "human_reason": "Security Command smoke and status routes are discoverable through Tower navigation/status links.",
        "soulaana_translation": "Soulaana: The door is no longer hidden. Security Command has its route signs.",
    }

    scan = _safe_scan(status)
    status["no_secret_leakage"] = scan.get("ok") is True
    status["leakage_scan"] = scan
    status["status_fingerprint"] = _fingerprint(status)

    _write_json(NAV_STATUS_PATH, status)

    try:
        from tower.tamper_evident_audit_chain import create_tamper_chain_entry
        create_tamper_chain_entry(
            event_type="tower_security_command_navigation_links_status",
            source_name="security_command_navigation_links_status",
            source_path=str(NAV_STATUS_PATH),
            source_hash=_fingerprint(status),
            record_count=len(links),
            actor_user_id="tower_system",
            reason="Pack 115 Security Command navigation/status links generated.",
            metadata={
                "pack": "115",
                "status": status.get("status"),
                "link_count": len(links),
                "readiness_score": status.get("readiness_score"),
            },
        )
    except Exception:
        pass

    if write_panel:
        write_security_command_navigation_links_panel(status)

    return status


def render_security_command_navigation_links_section(status: Dict[str, Any] | None = None) -> str:
    status = status if isinstance(status, dict) else build_security_command_navigation_links_status(write_panel=False)
    links = status.get("links", [])
    if not isinstance(links, list):
        links = []

    cards = []
    for link in links:
        title = _html_escape(link.get("title", "Tower Link"))
        href = _html_escape(link.get("href", "#"))
        kind = _html_escape(link.get("kind", "link"))
        pack = _html_escape(link.get("pack", ""))
        reason = _html_escape(link.get("human_reason", ""))
        readiness = _html_escape(link.get("readiness_score", 0))
        available = "AVAILABLE" if link.get("available") else "REVIEW"

        css = "tower-nav-card--ready" if link.get("available") else "tower-nav-card--review"

        cards.append(f"""
        <a class="tower-nav-card {css}" href="{href}">
          <div class="tower-nav-card__eyebrow">{available} · {kind} · {pack}</div>
          <h3>{title}</h3>
          <p>{reason}</p>
          <small>Readiness: {readiness}</small>
        </a>
        """)

    html = f"""
<!-- PACK115_SECURITY_COMMAND_NAVIGATION_LINKS_SECTION -->
<section class="tower-security-command-links" data-pack="115">
  <style>
    .tower-security-command-links {{
      margin: 24px 0;
      border: 1px solid rgba(220,183,94,.34);
      border-radius: 28px;
      padding: 22px;
      background:
        radial-gradient(circle at top right, rgba(168,175,255,.13), transparent 34%),
        linear-gradient(135deg, rgba(13,17,27,.78), rgba(8,9,7,.94));
      color: #f5ead2;
      box-shadow: 0 18px 70px rgba(0,0,0,.32);
    }}
    .tower-security-command-links__eyebrow {{
      color: rgba(220,183,94,.86);
      text-transform: uppercase;
      letter-spacing: .14em;
      font-size: 11px;
      margin-bottom: 8px;
    }}
    .tower-security-command-links h2 {{
      margin: 0;
      font-size: 24px;
      letter-spacing: -.03em;
    }}
    .tower-security-command-links p {{
      color: rgba(245,234,210,.72);
      line-height: 1.45;
    }}
    .tower-security-command-links__stats {{
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 10px;
      margin: 16px 0;
    }}
    .tower-nav-stat {{
      border: 1px solid rgba(245,234,210,.13);
      border-radius: 18px;
      padding: 12px;
      background: rgba(255,255,255,.04);
    }}
    .tower-nav-stat b {{
      display: block;
      font-size: 22px;
    }}
    .tower-nav-stat span {{
      color: rgba(245,234,210,.62);
      font-size: 12px;
    }}
    .tower-security-command-links__grid {{
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 12px;
      margin-top: 14px;
    }}
    .tower-nav-card {{
      display: block;
      color: inherit;
      text-decoration: none;
      border: 1px solid rgba(245,234,210,.13);
      border-radius: 20px;
      padding: 14px;
      background: rgba(255,255,255,.04);
      transition: transform .18s ease, border-color .18s ease;
    }}
    .tower-nav-card:hover {{
      transform: translateY(-2px);
      border-color: rgba(220,183,94,.7);
    }}
    .tower-nav-card--ready {{
      border-color: rgba(143,221,158,.34);
    }}
    .tower-nav-card--review {{
      border-color: rgba(255,128,128,.55);
    }}
    .tower-nav-card__eyebrow {{
      color: rgba(220,183,94,.84);
      text-transform: uppercase;
      letter-spacing: .12em;
      font-size: 10px;
      margin-bottom: 7px;
    }}
    .tower-nav-card h3 {{
      margin: 0 0 7px;
      font-size: 16px;
    }}
    .tower-nav-card p {{
      margin: 0 0 8px;
      color: rgba(245,234,210,.72);
    }}
    .tower-nav-card small {{
      color: rgba(245,234,210,.55);
    }}
    @media (max-width: 900px) {{
      .tower-security-command-links__stats,
      .tower-security-command-links__grid {{
        grid-template-columns: 1fr;
      }}
    }}
  </style>

  <div class="tower-security-command-links__eyebrow">PACK 115 · TOWER NAVIGATION</div>
  <h2>Security Command Links</h2>
  <p>{_html_escape(status.get('human_reason', 'Security Command links are available.'))}</p>

  <div class="tower-security-command-links__stats">
    <div class="tower-nav-stat"><b>{_html_escape(status.get('link_count', 0))}</b><span>Links</span></div>
    <div class="tower-nav-stat"><b>{_html_escape(status.get('route_health', {}).get('coverage_pct', 0) if isinstance(status.get('route_health'), dict) else 0)}%</b><span>Route Coverage</span></div>
    <div class="tower-nav-stat"><b>{_html_escape(status.get('readiness_score', 0))}</b><span>Readiness</span></div>
  </div>

  <div class="tower-security-command-links__grid">
    {''.join(cards)}
  </div>
</section>
<!-- END PACK115_SECURITY_COMMAND_NAVIGATION_LINKS_SECTION -->
"""
    return html


def write_security_command_navigation_links_panel(status: Dict[str, Any] | None = None) -> Dict[str, Any]:
    status = status if isinstance(status, dict) else build_security_command_navigation_links_status(write_panel=False)
    html = f"""<!doctype html>
<html lang="en">
<head><meta charset="utf-8"><title>The Tower · Security Command Links</title></head>
<body style="margin:0;background:#080907;color:#f5ead2;font-family:system-ui;padding:32px;">
<main style="max-width:1180px;margin:auto;">
{render_security_command_navigation_links_section(status)}
</main>
</body>
</html>
"""
    _write_text(NAV_PANEL_PATH, html)
    return {
        "ok": True,
        "pack": "115",
        "decision": "security_command_navigation_links_panel_written",
        "path": str(NAV_PANEL_PATH),
        "human_reason": "Security Command navigation links panel written.",
        "soulaana_translation": "Soulaana: Security Command links panel posted.",
    }


def load_security_command_navigation_links_status() -> Dict[str, Any]:
    status = _load_json(NAV_STATUS_PATH, {})
    if not status:
        status = build_security_command_navigation_links_status(write_panel=True)
    return status


def security_command_navigation_links_status_card() -> Dict[str, Any]:
    status = load_security_command_navigation_links_status()
    return {
        "ok": status.get("ok") is True,
        "pack": "115",
        "title": "Security Command Links",
        "link_count": status.get("link_count", 0),
        "readiness_score": status.get("readiness_score", 0),
        "route_coverage_pct": status.get("route_health", {}).get("coverage_pct", 0) if isinstance(status.get("route_health"), dict) else 0,
        "links": status.get("links", []),
        "panel_path": status.get("panel_path", str(NAV_PANEL_PATH)),
        "status_path": status.get("status_path", str(NAV_STATUS_PATH)),
        "human_reason": "Security Command links status card loaded.",
        "soulaana_translation": "Soulaana: Security Command links are visible.",
    }


def reset_security_command_navigation_links_for_test() -> Dict[str, Any]:
    _write_json(NAV_STATUS_PATH, {
        "ok": True,
        "pack": "115",
        "reset_at": _utc_now(),
        "human_reason": "Security Command navigation links reset for test.",
    })
    if NAV_PANEL_PATH.exists():
        try:
            NAV_PANEL_PATH.unlink()
        except Exception:
            pass
    return {
        "ok": True,
        "decision": "security_command_navigation_links_reset_for_test",
        "soulaana_translation": "Soulaana: Security Command links reset for a clean test lane.",
    }



# ================================================================================
# PACK117_PREFERRED_SECURITY_COMMAND_LINKS_OVERRIDE
# ================================================================================
# Make the unified owner command page the preferred/main Security Command destination.
try:
    from tower.security_command_preferred_destination import preferred_security_command_links
    CORE_SECURITY_COMMAND_LINKS = preferred_security_command_links()
except Exception:
    pass

# ================================================================================
# END PACK117_PREFERRED_SECURITY_COMMAND_LINKS_OVERRIDE
# ================================================================================

