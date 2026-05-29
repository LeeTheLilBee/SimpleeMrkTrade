
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "tower" / "data"

OBJECT_SECURITY_COMMAND_STATUS_PATH = DATA_DIR / "security_command_object_visibility_status.json"
OBJECT_SECURITY_COMMAND_FRAGMENT_PATH = DATA_DIR / "security_command_object_visibility_fragment.html"
OBJECT_VISIBILITY_STATUS_PATH = DATA_DIR / "ob_object_permission_visibility_status.json"


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


def _redact(value: Any) -> Any:
    secret_keys = {
        "token",
        "raw_token",
        "access_token",
        "refresh_token",
        "api_key",
        "apikey",
        "secret",
        "client_secret",
        "password",
        "passphrase",
        "private_key",
        "encryption_key",
        "broker_key",
        "broker_secret",
        "github_token",
        "stripe_secret",
        "payment_secret",
        "authorization",
        "bearer",
        "credential",
        "credentials",
        "tower_keycard",
        "session_secret",
        "device_secret",
        "raw_value",
    }

    if isinstance(value, dict):
        clean = {}
        redacted_count = 0
        for key, item in value.items():
            key_text = str(key).lower().strip()
            if key_text in secret_keys or key_text.endswith(("_token", "_password", "_api_key", "_secret", "_credential")):
                redacted_count += 1
                continue

            redacted_item = _redact(item)

            if isinstance(redacted_item, dict) and "__redacted_security_command_object_field_count__" in redacted_item:
                try:
                    redacted_count += int(redacted_item.get("__redacted_security_command_object_field_count__", 0))
                except Exception:
                    redacted_count += 1
                redacted_item = dict(redacted_item)
                redacted_item.pop("__redacted_security_command_object_field_count__", None)

            clean[key] = redacted_item

        if redacted_count:
            clean["__redacted_security_command_object_field_count__"] = redacted_count
        return clean

    if isinstance(value, list):
        return [_redact(item) for item in value]

    if isinstance(value, str):
        lowered = value.lower()
        if lowered.startswith("secret_ref_"):
            return value
        if (
            "should_not_survive" in lowered
            or "tower_keycard=" in lowered
            or "bearer " in lowered
            or "ghp_" in lowered
            or "sk_live_" in lowered
            or "-----begin private key-----" in lowered
            or "access_token=" in lowered
            or "refresh_token=" in lowered
        ):
            return "[REDACTED_SECURITY_COMMAND_OBJECT_VALUE]"
        return value

    return value


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


def load_or_build_object_visibility_status() -> Dict[str, Any]:
    try:
        from tower.ob_object_permission_visibility import build_object_permission_visibility_status
        return build_object_permission_visibility_status(limit=120, write_panel=True)
    except Exception:
        status = _load_json(OBJECT_VISIBILITY_STATUS_PATH, {})
        if isinstance(status, dict) and status:
            return status
        return {
            "ok": False,
            "pack": "113",
            "reason_code": "object_visibility_status_unavailable",
            "human_reason": "Object visibility status could not be loaded.",
        }


def build_security_command_object_visibility_status(write_fragment: bool = True) -> Dict[str, Any]:
    visibility = load_or_build_object_visibility_status()

    recent = visibility.get("recent_important_events", [])
    if not isinstance(recent, list):
        recent = []

    cards = []
    for event in recent[-18:]:
        if not isinstance(event, dict):
            continue
        cards.append({
            "decision": event.get("decision", "unknown"),
            "object_type": event.get("object_type", "object"),
            "object_id": event.get("object_id", ""),
            "action": event.get("action", ""),
            "role_family": event.get("role_family", ""),
            "reason_code": event.get("reason_code", ""),
            "requires_step_up": event.get("requires_step_up", False),
            "requires_archive_handoff": event.get("requires_archive_handoff", False),
            "requires_summary_only": event.get("requires_summary_only", False),
            "required_actions": event.get("required_actions", []),
        })

    status = {
        "ok": visibility.get("ok") is True,
        "pack": "113",
        "created_at": _utc_now(),
        "visibility_status_path": str(OBJECT_VISIBILITY_STATUS_PATH),
        "security_command_status_path": str(OBJECT_SECURITY_COMMAND_STATUS_PATH),
        "security_command_fragment_path": str(OBJECT_SECURITY_COMMAND_FRAGMENT_PATH),
        "event_count": visibility.get("event_count", 0),
        "important_event_count": visibility.get("important_event_count", 0),
        "deny_count": visibility.get("deny_count", 0),
        "step_up_required_count": visibility.get("step_up_required_count", 0),
        "summary_only_count": visibility.get("summary_only_count", 0),
        "export_event_count": visibility.get("export_event_count", 0),
        "admin_event_count": visibility.get("admin_event_count", 0),
        "live_mode_event_count": visibility.get("live_mode_event_count", 0),
        "readiness_score": visibility.get("readiness_score", 0),
        "recent_security_command_cards": cards,
        "human_reason": "OB object permission visibility is available inside Security Command.",
        "soulaana_translation": "Soulaana: Security Command can now see object denials, step-ups, exports, and summary-only locks.",
    }

    status = _redact(status)
    scan = _safe_scan(status)
    status["no_secret_leakage"] = scan.get("ok") is True
    status["leakage_scan"] = scan
    status["status_fingerprint"] = _fingerprint(status)

    _write_json(OBJECT_SECURITY_COMMAND_STATUS_PATH, status)

    try:
        from tower.tamper_evident_audit_chain import create_tamper_chain_entry

        create_tamper_chain_entry(
            event_type="tower_security_command_object_visibility_status",
            source_name="security_command_object_visibility_status",
            source_path=str(OBJECT_SECURITY_COMMAND_STATUS_PATH),
            source_hash=_fingerprint(status),
            record_count=int(status.get("event_count", 0) or 0),
            actor_user_id="tower_system",
            reason="Pack 113 Security Command object visibility status generated.",
            metadata={
                "pack": "113",
                "deny_count": status.get("deny_count"),
                "step_up_required_count": status.get("step_up_required_count"),
                "export_event_count": status.get("export_event_count"),
            },
        )
    except Exception:
        pass

    if write_fragment:
        write_security_command_object_visibility_fragment(status)

    return status


def render_security_command_object_visibility_section(status: Dict[str, Any] | None = None) -> str:
    status = status if isinstance(status, dict) else build_security_command_object_visibility_status(write_fragment=False)
    cards = status.get("recent_security_command_cards", [])
    if not isinstance(cards, list):
        cards = []

    card_html = []
    for event in cards[-18:]:
        if not isinstance(event, dict):
            continue

        decision = _html_escape(event.get("decision", "unknown"))
        object_type = _html_escape(event.get("object_type", "object"))
        object_id = _html_escape(event.get("object_id", ""))
        reason = _html_escape(event.get("reason_code", ""))
        role_family = _html_escape(event.get("role_family", ""))
        actions = event.get("required_actions", [])
        if isinstance(actions, list):
            action_text = _html_escape(", ".join([str(a) for a in actions[:3]]))
        else:
            action_text = ""

        css = "tower-object-card--neutral"
        if decision == "deny":
            css = "tower-object-card--deny"
        elif decision == "step_up_required":
            css = "tower-object-card--step"
        elif decision == "summary_only":
            css = "tower-object-card--summary"
        elif decision == "allow":
            css = "tower-object-card--allow"

        card_html.append(f"""
        <article class="tower-object-card {css}">
          <div class="tower-object-card__eyebrow">{decision} · {object_type} · {role_family}</div>
          <h3>{object_id}</h3>
          <p>{reason}</p>
          <small>{action_text}</small>
        </article>
        """)

    if not card_html:
        card_html.append("""
        <article class="tower-object-card tower-object-card--neutral">
          <div class="tower-object-card__eyebrow">NO RECENT OBJECT EVENTS</div>
          <h3>Object visibility is ready</h3>
          <p>No recent deny, step-up, export, live-mode, or summary-only object events are available yet.</p>
        </article>
        """)

    html = f"""
<!-- PACK113_SECURITY_COMMAND_OBJECT_VISIBILITY_SECTION -->
<section class="tower-object-visibility-panel" data-pack="113">
  <style>
    .tower-object-visibility-panel {{
      margin: 24px 0;
      border: 1px solid rgba(220,183,94,.34);
      border-radius: 28px;
      padding: 22px;
      background:
        radial-gradient(circle at top left, rgba(220,183,94,.15), transparent 34%),
        linear-gradient(135deg, rgba(75,48,18,.58), rgba(8,9,7,.92));
      color: #f5ead2;
      box-shadow: 0 18px 70px rgba(0,0,0,.32);
    }}
    .tower-object-visibility-panel__head {{
      display: flex;
      justify-content: space-between;
      gap: 18px;
      align-items: flex-start;
      margin-bottom: 16px;
    }}
    .tower-object-visibility-panel__eyebrow {{
      color: rgba(220,183,94,.86);
      text-transform: uppercase;
      letter-spacing: .14em;
      font-size: 11px;
      margin-bottom: 8px;
    }}
    .tower-object-visibility-panel h2 {{
      margin: 0;
      font-size: 24px;
      letter-spacing: -.03em;
    }}
    .tower-object-visibility-panel p {{
      color: rgba(245,234,210,.72);
      line-height: 1.45;
    }}
    .tower-object-visibility-panel__stats {{
      display: grid;
      grid-template-columns: repeat(5, minmax(0, 1fr));
      gap: 10px;
      margin: 16px 0;
    }}
    .tower-object-stat {{
      border: 1px solid rgba(245,234,210,.13);
      border-radius: 18px;
      padding: 12px;
      background: rgba(255,255,255,.04);
    }}
    .tower-object-stat b {{
      display: block;
      font-size: 22px;
    }}
    .tower-object-stat span {{
      color: rgba(245,234,210,.62);
      font-size: 12px;
    }}
    .tower-object-visibility-panel__grid {{
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 12px;
      margin-top: 14px;
    }}
    .tower-object-card {{
      border: 1px solid rgba(245,234,210,.13);
      border-radius: 20px;
      padding: 14px;
      background: rgba(255,255,255,.04);
    }}
    .tower-object-card--allow {{
      border-color: rgba(143,221,158,.34);
    }}
    .tower-object-card--deny {{
      border-color: rgba(255,128,128,.55);
    }}
    .tower-object-card--step {{
      border-color: rgba(220,183,94,.58);
    }}
    .tower-object-card--summary {{
      border-color: rgba(168,175,255,.46);
    }}
    .tower-object-card__eyebrow {{
      color: rgba(220,183,94,.84);
      text-transform: uppercase;
      letter-spacing: .12em;
      font-size: 10px;
      margin-bottom: 7px;
    }}
    .tower-object-card h3 {{
      margin: 0 0 7px;
      font-size: 16px;
    }}
    .tower-object-card p {{
      margin: 0 0 8px;
      color: rgba(245,234,210,.72);
    }}
    .tower-object-card small {{
      color: rgba(245,234,210,.55);
    }}
    @media (max-width: 900px) {{
      .tower-object-visibility-panel__stats,
      .tower-object-visibility-panel__grid {{
        grid-template-columns: 1fr;
      }}
      .tower-object-visibility-panel__head {{
        display: block;
      }}
    }}
  </style>

  <div class="tower-object-visibility-panel__head">
    <div>
      <div class="tower-object-visibility-panel__eyebrow">PACK 112 + 113 · OB OBJECT PERMISSIONS</div>
      <h2>Object Permission Visibility</h2>
      <p>{_html_escape(status.get('human_reason', 'Object visibility is available inside Security Command.'))}</p>
    </div>
    <div class="tower-object-stat">
      <b>{_html_escape(status.get('readiness_score', 0))}</b>
      <span>Readiness</span>
    </div>
  </div>

  <div class="tower-object-visibility-panel__stats">
    <div class="tower-object-stat"><b>{_html_escape(status.get('event_count', 0))}</b><span>Events</span></div>
    <div class="tower-object-stat"><b>{_html_escape(status.get('deny_count', 0))}</b><span>Denied</span></div>
    <div class="tower-object-stat"><b>{_html_escape(status.get('step_up_required_count', 0))}</b><span>Step-up</span></div>
    <div class="tower-object-stat"><b>{_html_escape(status.get('export_event_count', 0))}</b><span>Exports</span></div>
    <div class="tower-object-stat"><b>{_html_escape(status.get('summary_only_count', 0))}</b><span>Summary-only</span></div>
  </div>

  <div class="tower-object-visibility-panel__grid">
    {''.join(card_html)}
  </div>
</section>
<!-- END PACK113_SECURITY_COMMAND_OBJECT_VISIBILITY_SECTION -->
"""
    return html


def write_security_command_object_visibility_fragment(status: Dict[str, Any] | None = None) -> Dict[str, Any]:
    status = status if isinstance(status, dict) else build_security_command_object_visibility_status(write_fragment=False)
    html = render_security_command_object_visibility_section(status)
    _write_text(OBJECT_SECURITY_COMMAND_FRAGMENT_PATH, html)

    return {
        "ok": True,
        "pack": "113",
        "decision": "security_command_object_visibility_fragment_written",
        "path": str(OBJECT_SECURITY_COMMAND_FRAGMENT_PATH),
        "human_reason": "Security Command object visibility HTML fragment written.",
        "soulaana_translation": "Soulaana: Object visibility panel is ready for Security Command.",
    }


def load_security_command_object_visibility_status() -> Dict[str, Any]:
    status = _load_json(OBJECT_SECURITY_COMMAND_STATUS_PATH, {})
    if not status:
        status = build_security_command_object_visibility_status(write_fragment=True)
    return status


def reset_security_command_object_visibility_for_test() -> Dict[str, Any]:
    _write_json(OBJECT_SECURITY_COMMAND_STATUS_PATH, {
        "ok": True,
        "pack": "113",
        "event_count": 0,
        "reset_at": _utc_now(),
        "human_reason": "Security Command object visibility reset for test.",
    })
    if OBJECT_SECURITY_COMMAND_FRAGMENT_PATH.exists():
        try:
            OBJECT_SECURITY_COMMAND_FRAGMENT_PATH.unlink()
        except Exception:
            pass
    return {
        "ok": True,
        "decision": "security_command_object_visibility_reset_for_test",
        "soulaana_translation": "Soulaana: Security Command object visibility reset for a clean test lane.",
    }
