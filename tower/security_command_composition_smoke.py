
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "tower" / "data"

COMPOSITION_STATUS_PATH = DATA_DIR / "security_command_composition_smoke_status.json"
COMPOSITION_HTML_PATH = DATA_DIR / "security_command_composition_smoke.html"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _load_json(path: Path, default: Any) -> Any:
    try:
        if not path.exists():
            return default
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def _write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, indent=2, sort_keys=True, default=str), encoding="utf-8")
    tmp.replace(path)


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


def _bridge_call_status() -> Dict[str, Any]:
    status = {
        "object_visibility_bridge_ok": False,
        "tower_status_bridge_ok": False,
        "security_command_bridge_ok": False,
        "object_visibility_html_ok": False,
        "errors": [],
        "object_html_length": 0,
    }

    try:
        from tower.security_command_page import pack113_security_command_object_visibility_html_section

        html = pack113_security_command_object_visibility_html_section()
        status["object_visibility_html_ok"] = (
            isinstance(html, str)
            and "PACK113_SECURITY_COMMAND_OBJECT_VISIBILITY_SECTION" in html
            and "Object Permission Visibility" in html
        )
        status["object_html_length"] = len(html) if isinstance(html, str) else 0
    except Exception as exc:
        status["errors"].append({
            "bridge": "pack113_security_command_object_visibility_html_section",
            "error_type": type(exc).__name__,
        })

    try:
        from tower.tower_status import pack112_object_permission_visibility_status_bridge

        card = pack112_object_permission_visibility_status_bridge()
        status["tower_status_bridge_ok"] = (
            isinstance(card, dict)
            and card.get("ok") is True
            and card.get("pack") == "112"
        )
    except Exception as exc:
        status["errors"].append({
            "bridge": "pack112_object_permission_visibility_status_bridge",
            "error_type": type(exc).__name__,
        })

    try:
        from tower.security_command_page import pack112_object_permission_visibility_command_panel

        panel = pack112_object_permission_visibility_command_panel()
        status["security_command_bridge_ok"] = (
            isinstance(panel, dict)
            and panel.get("ok") is True
            and panel.get("pack") == "112"
        )
    except Exception as exc:
        status["errors"].append({
            "bridge": "pack112_object_permission_visibility_command_panel",
            "error_type": type(exc).__name__,
        })

    status["object_visibility_bridge_ok"] = (
        status["object_visibility_html_ok"]
        and status["tower_status_bridge_ok"]
        and status["security_command_bridge_ok"]
    )

    return status


def build_security_command_composition_status(write_html: bool = True) -> Dict[str, Any]:
    bridge_status = _bridge_call_status()

    route_coverage = {}
    checkpoint = {}
    object_visibility = {}
    security_object_status = {}

    try:
        from tower.ob_route_coverage_report import build_ob_route_coverage_report

        route_coverage = build_ob_route_coverage_report(write_panel=True)
    except Exception as exc:
        route_coverage = {
            "ok": False,
            "error_type": type(exc).__name__,
        }

    try:
        from tower.ob_object_permission_integration_checkpoint import build_object_permission_integration_checkpoint

        checkpoint = build_object_permission_integration_checkpoint(write_panel=True)
    except Exception as exc:
        checkpoint = {
            "ok": False,
            "status": "failed",
            "error_type": type(exc).__name__,
        }

    try:
        from tower.ob_object_permission_visibility import build_object_permission_visibility_status

        object_visibility = build_object_permission_visibility_status(limit=120, write_panel=True)
    except Exception as exc:
        object_visibility = {
            "ok": False,
            "error_type": type(exc).__name__,
        }

    try:
        from tower.security_command_object_visibility_integration import build_security_command_object_visibility_status

        security_object_status = build_security_command_object_visibility_status(write_fragment=True)
    except Exception as exc:
        security_object_status = {
            "ok": False,
            "error_type": type(exc).__name__,
        }

    checks = {
        "route_coverage_ok": route_coverage.get("ok") is True,
        "route_coverage_100": route_coverage.get("coverage_pct") == 100,
        "unguarded_needed_zero": route_coverage.get("unguarded_needed_count") == 0,
        "unguarded_high_risk_zero": route_coverage.get("unguarded_high_risk_count") == 0,
        "object_checkpoint_ok": checkpoint.get("ok") is True,
        "object_checkpoint_passed": checkpoint.get("status") == "passed",
        "helper_wrapped_zero": checkpoint.get("helper_wrapped_count") == 0,
        "object_visibility_ok": object_visibility.get("ok") is True,
        "object_visibility_ready": object_visibility.get("readiness_score") == 100,
        "security_object_status_ok": security_object_status.get("ok") is True,
        "security_object_status_ready": security_object_status.get("readiness_score") == 100,
        "object_visibility_html_bridge_ok": bridge_status.get("object_visibility_html_ok") is True,
        "tower_status_bridge_ok": bridge_status.get("tower_status_bridge_ok") is True,
        "security_command_bridge_ok": bridge_status.get("security_command_bridge_ok") is True,
    }

    failed_checks = [key for key, value in checks.items() if not value]

    status = {
        "ok": not failed_checks,
        "pack": "114",
        "status": "passed" if not failed_checks else "failed",
        "created_at": _utc_now(),
        "status_path": str(COMPOSITION_STATUS_PATH),
        "html_path": str(COMPOSITION_HTML_PATH),
        "checks": checks,
        "failed_checks": failed_checks,
        "bridge_status": bridge_status,
        "route_coverage_summary": {
            "coverage_pct": route_coverage.get("coverage_pct"),
            "guarded_needed_count": route_coverage.get("guarded_needed_count"),
            "needs_guard_count": route_coverage.get("needs_guard_count"),
            "unguarded_needed_count": route_coverage.get("unguarded_needed_count"),
            "unguarded_high_risk_count": route_coverage.get("unguarded_high_risk_count"),
            "readiness_score": route_coverage.get("readiness_score"),
        },
        "object_checkpoint_summary": {
            "status": checkpoint.get("status"),
            "readiness_score": checkpoint.get("readiness_score"),
            "object_guard_count": checkpoint.get("object_guard_count"),
            "helper_wrapped_count": checkpoint.get("helper_wrapped_count"),
            "warnings": checkpoint.get("warnings"),
        },
        "object_visibility_summary": {
            "event_count": object_visibility.get("event_count"),
            "deny_count": object_visibility.get("deny_count"),
            "step_up_required_count": object_visibility.get("step_up_required_count"),
            "summary_only_count": object_visibility.get("summary_only_count"),
            "export_event_count": object_visibility.get("export_event_count"),
            "readiness_score": object_visibility.get("readiness_score"),
            "no_secret_leakage": object_visibility.get("no_secret_leakage"),
        },
        "security_object_summary": {
            "event_count": security_object_status.get("event_count"),
            "important_event_count": security_object_status.get("important_event_count"),
            "deny_count": security_object_status.get("deny_count"),
            "step_up_required_count": security_object_status.get("step_up_required_count"),
            "summary_only_count": security_object_status.get("summary_only_count"),
            "export_event_count": security_object_status.get("export_event_count"),
            "readiness_score": security_object_status.get("readiness_score"),
            "no_secret_leakage": security_object_status.get("no_secret_leakage"),
        },
        "readiness_score": 100 if not failed_checks else max(0, 100 - (len(failed_checks) * 10)),
        "readiness_label": (
            "Security Command composition smoke passed"
            if not failed_checks
            else "Security Command composition smoke needs review"
        ),
        "human_reason": "Security Command composition can render object visibility while route/object readiness remains healthy.",
        "soulaana_translation": "Soulaana: The Security Command room loads with the object visibility board attached.",
    }

    scan = _safe_scan(status)
    status["no_secret_leakage"] = scan.get("ok") is True
    status["leakage_scan"] = scan
    status["status_fingerprint"] = _fingerprint(status)

    _write_json(COMPOSITION_STATUS_PATH, status)

    try:
        from tower.tamper_evident_audit_chain import create_tamper_chain_entry

        create_tamper_chain_entry(
            event_type="tower_security_command_composition_smoke",
            source_name="security_command_composition_smoke_status",
            source_path=str(COMPOSITION_STATUS_PATH),
            source_hash=_fingerprint(status),
            record_count=1,
            actor_user_id="tower_system",
            reason="Pack 114 Security Command composition smoke status generated.",
            metadata={
                "pack": "114",
                "status": status.get("status"),
                "readiness_score": status.get("readiness_score"),
                "failed_checks": failed_checks,
            },
        )
    except Exception:
        pass

    if write_html:
        write_security_command_composition_html(status)

    return status


def render_security_command_composition_html(status: Dict[str, Any] | None = None) -> str:
    status = status if isinstance(status, dict) else build_security_command_composition_status(write_html=False)

    object_section = ""
    try:
        from tower.security_command_page import pack113_security_command_object_visibility_html_section

        object_section = pack113_security_command_object_visibility_html_section()
    except Exception as exc:
        object_section = f"""
        <section class="tower-object-visibility-panel">
          <h2>Object Visibility Bridge Failed</h2>
          <p>{_html_escape(type(exc).__name__)}</p>
        </section>
        """

    html = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>The Tower · Security Command Composition Smoke</title>
  <style>
    body {{
      margin: 0;
      min-height: 100vh;
      background: #080907;
      color: #f5ead2;
      font-family: Inter, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }}
    main {{
      max-width: 1180px;
      margin: 0 auto;
      padding: 42px 22px;
    }}
    .tower-composition-hero {{
      border: 1px solid rgba(220,183,94,.36);
      border-radius: 30px;
      padding: 30px;
      background: linear-gradient(135deg, rgba(75,48,18,.74), rgba(12,13,10,.96));
      box-shadow: 0 22px 90px rgba(0,0,0,.42);
      margin-bottom: 20px;
    }}
    .tower-composition-hero__eyebrow {{
      color: rgba(220,183,94,.86);
      text-transform: uppercase;
      letter-spacing: .14em;
      font-size: 11px;
      margin-bottom: 8px;
    }}
    h1 {{
      margin: 0 0 10px;
      font-size: 34px;
      letter-spacing: -.04em;
    }}
    .tower-composition-hero p {{
      margin: 0;
      color: rgba(245,234,210,.76);
      line-height: 1.55;
    }}
    .tower-composition-stats {{
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 14px;
      margin-top: 18px;
    }}
    .tower-composition-stat {{
      border: 1px solid rgba(245,234,210,.14);
      border-radius: 20px;
      padding: 16px;
      background: rgba(255,255,255,.045);
    }}
    .tower-composition-stat b {{
      display: block;
      font-size: 24px;
    }}
    .tower-composition-stat span {{
      color: rgba(245,234,210,.62);
      font-size: 12px;
    }}
    @media (max-width: 900px) {{
      .tower-composition-stats {{
        grid-template-columns: 1fr;
      }}
    }}
  </style>
</head>
<body>
<main>
  <!-- PACK114_SECURITY_COMMAND_COMPOSITION_SMOKE_PAGE -->
  <section class="tower-composition-hero" data-pack="114">
    <div class="tower-composition-hero__eyebrow">PACK 114 · SECURITY COMMAND COMPOSITION SMOKE</div>
    <h1>The Tower Security Command</h1>
    <p>{_html_escape(status.get('human_reason', 'Security Command composition smoke loaded.'))}</p>
    <div class="tower-composition-stats">
      <div class="tower-composition-stat">
        <b>{_html_escape(status.get('readiness_score', 0))}</b>
        <span>Readiness</span>
      </div>
      <div class="tower-composition-stat">
        <b>{_html_escape(status.get('route_coverage_summary', {}).get('coverage_pct', 0) if isinstance(status.get('route_coverage_summary'), dict) else 0)}%</b>
        <span>Route Coverage</span>
      </div>
      <div class="tower-composition-stat">
        <b>{_html_escape(status.get('object_checkpoint_summary', {}).get('helper_wrapped_count', 0) if isinstance(status.get('object_checkpoint_summary'), dict) else 0)}</b>
        <span>Helper Wraps</span>
      </div>
      <div class="tower-composition-stat">
        <b>{_html_escape(status.get('security_object_summary', {}).get('event_count', 0) if isinstance(status.get('security_object_summary'), dict) else 0)}</b>
        <span>Object Events</span>
      </div>
    </div>
  </section>

  {object_section}
  <!-- END PACK114_SECURITY_COMMAND_COMPOSITION_SMOKE_PAGE -->
</main>
</body>
</html>
"""
    return html


def write_security_command_composition_html(status: Dict[str, Any] | None = None) -> Dict[str, Any]:
    status = status if isinstance(status, dict) else build_security_command_composition_status(write_html=False)
    html = render_security_command_composition_html(status)
    _write_text(COMPOSITION_HTML_PATH, html)

    return {
        "ok": True,
        "pack": "114",
        "decision": "security_command_composition_html_written",
        "path": str(COMPOSITION_HTML_PATH),
        "html_length": len(html),
        "human_reason": "Security Command composition smoke HTML written.",
        "soulaana_translation": "Soulaana: Security Command smoke page written.",
    }


def load_security_command_composition_status() -> Dict[str, Any]:
    status = _load_json(COMPOSITION_STATUS_PATH, {})
    if not status:
        status = build_security_command_composition_status(write_html=True)
    return status


def reset_security_command_composition_smoke_for_test() -> Dict[str, Any]:
    _write_json(COMPOSITION_STATUS_PATH, {
        "ok": True,
        "pack": "114",
        "reset_at": _utc_now(),
        "human_reason": "Security Command composition smoke reset for test.",
    })
    if COMPOSITION_HTML_PATH.exists():
        try:
            COMPOSITION_HTML_PATH.unlink()
        except Exception:
            pass
    return {
        "ok": True,
        "decision": "security_command_composition_smoke_reset_for_test",
        "soulaana_translation": "Soulaana: Security Command composition smoke reset for a clean test lane.",
    }
