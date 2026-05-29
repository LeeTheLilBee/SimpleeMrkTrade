
from __future__ import annotations

import hashlib
import json
import re
import secrets
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "tower" / "data"

OB_ROUTE_GUARD_EVENTS_PATH = DATA_DIR / "ob_tower_route_guard_events.json"
OB_ROUTE_GUARD_SUMMARY_PATH = DATA_DIR / "ob_tower_route_guard_summary.json"
OB_ROUTE_GUARD_PANEL_PATH = DATA_DIR / "ob_tower_route_guard_panel.html"


PUBLIC_OB_ROUTES = {
    "/signals-spotlight",
    "/public/signals-spotlight",
    "/health",
}

PRIVATE_OB_ENTRY_ROUTES = {
    "/observatory-private",
    "/observatory",
    "/dashboard",
    "/simulation",
    "/paper",
}

MODE_ROUTE_MAP = {
    "/survey": "survey",
    "/paper": "paper",
    "/paper-mode": "paper",
    "/live": "live_manual",
    "/live/manual": "live_manual",
    "/live/hybrid": "live_hybrid",
    "/live/automated": "live_automated",
}

EXPORT_ROUTE_PREFIXES = (
    "/export",
    "/download",
    "/reports/export",
    "/trade-packet",
    "/proof-packet",
)

REVEAL_ROUTE_PREFIXES = (
    "/reveal",
    "/positions/reveal",
    "/trades/reveal",
    "/analysis/reveal",
)

LIVE_ROUTE_PREFIXES = (
    "/live",
    "/broker",
    "/automated",
)

ADMIN_ROUTE_PREFIXES = (
    "/admin",
    "/tower-admin",
    "/observatory-admin",
)

SYMBOL_ROUTE_PATTERNS = (
    r"^/signals/([A-Za-z0-9\.\-_]+)$",
    r"^/symbol/([A-Za-z0-9\.\-_]+)$",
    r"^/symbols/([A-Za-z0-9\.\-_]+)$",
)

POSITION_ROUTE_PATTERNS = (
    r"^/positions/([A-Za-z0-9\.\-_]+)$",
    r"^/my-positions/([A-Za-z0-9\.\-_]+)$",
)

TRADE_ROUTE_PATTERNS = (
    r"^/trades/([A-Za-z0-9\.\-_]+)$",
    r"^/trade/([A-Za-z0-9\.\-_]+)$",
)


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _safe_str(value: Any, default: str = "") -> str:
    if value is None:
        return default
    text = str(value).strip()
    return text if text else default


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


def _event_id(prefix: str = "ob_route_guard") -> str:
    return f"{prefix}_{secrets.token_urlsafe(18)}"


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

    sensitive_keys = {
        "document_text",
        "raw_payload",
        "private_notes",
        "bank_account",
        "routing_number",
        "account_number",
    }

    if isinstance(value, dict):
        clean = {}
        redacted_count = 0

        for key, item in value.items():
            key_text = str(key).lower().strip()

            if key_text in secret_keys or key_text.endswith(("_token", "_password", "_api_key", "_secret", "_credential")):
                redacted_count += 1
                continue

            if key_text in sensitive_keys:
                clean[key] = "[REDACTED_OB_ROUTE_GUARD_SENSITIVE]"
                redacted_count += 1
                continue

            redacted_item = _redact(item)

            if isinstance(redacted_item, dict) and "__redacted_ob_route_guard_field_count__" in redacted_item:
                try:
                    redacted_count += int(redacted_item.get("__redacted_ob_route_guard_field_count__", 0))
                except Exception:
                    redacted_count += 1
                redacted_item = dict(redacted_item)
                redacted_item.pop("__redacted_ob_route_guard_field_count__", None)

            clean[key] = redacted_item

        if redacted_count:
            clean["__redacted_ob_route_guard_field_count__"] = redacted_count

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
            return "[REDACTED_OB_ROUTE_GUARD_VALUE]"
        return value

    return value


def _canonical_json(value: Any) -> str:
    return json.dumps(_redact(value), sort_keys=True, separators=(",", ":"), default=str)


def _fingerprint(value: Any) -> str:
    return hashlib.sha256(_canonical_json(value).encode("utf-8")).hexdigest()


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


def _load_events() -> List[Dict[str, Any]]:
    data = _load_json(OB_ROUTE_GUARD_EVENTS_PATH, [])
    return data if isinstance(data, list) else []


def _save_events(events: List[Dict[str, Any]]) -> None:
    _write_json(OB_ROUTE_GUARD_EVENTS_PATH, events)


def _normalize_route_path(route_path: str) -> str:
    route_path = _safe_str(route_path, "/")
    if not route_path.startswith("/"):
        route_path = "/" + route_path
    if len(route_path) > 1:
        route_path = route_path.rstrip("/")
    return route_path


def _match_first(patterns: tuple[str, ...], route_path: str) -> str:
    for pattern in patterns:
        match = re.match(pattern, route_path)
        if match:
            return match.group(1)
    return ""


def classify_ob_route(route_path: str, method: str = "GET") -> Dict[str, Any]:
    route_path = _normalize_route_path(route_path)
    method = _safe_str(method, "GET").upper()

    if route_path in PUBLIC_OB_ROUTES or route_path.startswith("/public/"):
        return {
            "request_type": "route_access",
            "object_type": "route",
            "object_id": route_path,
            "action": "",
            "mode": "",
            "classification": "public_route",
        }

    if route_path in PRIVATE_OB_ENTRY_ROUTES:
        return {
            "request_type": "app_entry",
            "object_type": "route",
            "object_id": route_path,
            "action": "",
            "mode": "",
            "classification": "private_ob_entry",
        }

    if route_path in MODE_ROUTE_MAP:
        mode = MODE_ROUTE_MAP[route_path]
        return {
            "request_type": "mode_access",
            "object_type": "mode",
            "object_id": mode,
            "action": "",
            "mode": mode,
            "classification": "mode_route",
        }

    symbol = _match_first(SYMBOL_ROUTE_PATTERNS, route_path)
    if symbol:
        return {
            "request_type": "object_access",
            "object_type": "symbol",
            "object_id": symbol.upper(),
            "action": "",
            "mode": "",
            "classification": "symbol_object_route",
        }

    position_id = _match_first(POSITION_ROUTE_PATTERNS, route_path)
    if position_id:
        return {
            "request_type": "object_access",
            "object_type": "position",
            "object_id": position_id,
            "action": "",
            "mode": "",
            "classification": "position_object_route",
        }

    trade_id = _match_first(TRADE_ROUTE_PATTERNS, route_path)
    if trade_id:
        return {
            "request_type": "object_access",
            "object_type": "trade",
            "object_id": trade_id,
            "action": "",
            "mode": "",
            "classification": "trade_object_route",
        }

    if route_path.startswith(EXPORT_ROUTE_PREFIXES):
        return {
            "request_type": "export_access",
            "object_type": "export",
            "object_id": route_path,
            "action": "export" if method == "GET" else "download",
            "mode": "",
            "classification": "export_route",
        }

    if route_path.startswith(REVEAL_ROUTE_PREFIXES):
        return {
            "request_type": "reveal_access",
            "object_type": "analysis",
            "object_id": route_path,
            "action": "reveal_sensitive",
            "mode": "",
            "classification": "reveal_route",
        }

    if route_path.startswith(LIVE_ROUTE_PREFIXES):
        mode = "live_manual"
        if "/hybrid" in route_path:
            mode = "live_hybrid"
        if "/automated" in route_path:
            mode = "live_automated"
        return {
            "request_type": "live_action_access",
            "object_type": "mode",
            "object_id": mode,
            "action": "live_mode_enable",
            "mode": mode,
            "classification": "live_route",
        }

    if route_path.startswith(ADMIN_ROUTE_PREFIXES):
        return {
            "request_type": "action_access",
            "object_type": "admin_panel",
            "object_id": route_path,
            "action": "admin_override",
            "mode": "",
            "classification": "admin_route",
        }

    return {
        "request_type": "route_access",
        "object_type": "route",
        "object_id": route_path,
        "action": "",
        "mode": "",
        "classification": "unknown_route",
    }


def _record_guard_event(event: Dict[str, Any]) -> Dict[str, Any]:
    event = dict(event)
    event.setdefault("event_id", _event_id("ob_route_guard_evt"))
    event.setdefault("event_type", "tower_ob_route_guard_event")
    event.setdefault("created_at", _utc_now())
    event.setdefault("pack", "102")

    event = _redact(event)
    event["event_fingerprint"] = _fingerprint(event)

    events = _load_events()
    events.append(event)
    _save_events(events)

    try:
        from tower.tamper_evident_audit_chain import create_tamper_chain_entry

        create_tamper_chain_entry(
            event_type="tower_ob_route_guard_event_snapshot",
            source_name="ob_tower_route_guard_events",
            source_path=str(OB_ROUTE_GUARD_EVENTS_PATH),
            source_hash=_fingerprint(events),
            record_count=len(events),
            actor_user_id=_safe_str(event.get("user_id"), "tower_system"),
            reason=f"Pack 102 chained OB route guard event {event.get('decision')}.",
            metadata={
                "pack": "102",
                "event_id": event.get("event_id"),
                "route_path": event.get("route_path"),
                "decision": event.get("decision"),
            },
        )
    except Exception:
        pass

    return event


def guard_ob_route(
    *,
    user_id: str,
    role: str,
    route_path: str,
    method: str = "GET",
    session_id: str = "",
    device_id: str = "",
    ip_address: str = "",
    metadata: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    route_path = _normalize_route_path(route_path)
    method = _safe_str(method, "GET").upper()
    metadata = metadata if isinstance(metadata, dict) else {}

    classification = classify_ob_route(route_path, method=method)

    from tower.ob_tower_bridge_adapter import make_ob_bridge_request, evaluate_ob_tower_bridge_request

    request = make_ob_bridge_request(
        user_id=user_id,
        role=role,
        request_type=classification.get("request_type", "route_access"),
        route_path=route_path,
        mode=classification.get("mode", ""),
        object_type=classification.get("object_type", ""),
        object_id=classification.get("object_id", ""),
        action=classification.get("action", ""),
        session_id=session_id,
        device_id=device_id,
        ip_address=ip_address,
        metadata={
            "method": method,
            "route_classification": classification.get("classification"),
            **metadata,
        },
    )

    bridge_response = evaluate_ob_tower_bridge_request(request)

    decision = bridge_response.get("decision", "deny")
    allowed = bridge_response.get("allowed") is True

    guard = {
        "ok": allowed or decision in {"step_up_required", "summary_only", "redacted_summary"},
        "pack": "102",
        "guard_id": _event_id("ob_guard"),
        "created_at": _utc_now(),
        "user_id": _safe_str(user_id, "anonymous"),
        "role": _safe_str(role, "beta"),
        "route_path": route_path,
        "method": method,
        "classification": classification,
        "decision": decision,
        "allowed": allowed,
        "should_render_route": allowed,
        "should_render_locked_page": not allowed,
        "locked_page_kind": _locked_page_kind(decision),
        "bridge_response": bridge_response,
        "required_actions": bridge_response.get("required_actions", []),
        "requires_step_up": bridge_response.get("requires_step_up") is True,
        "requires_receipt": bridge_response.get("requires_receipt") is True,
        "requires_archive_handoff": bridge_response.get("requires_archive_handoff") is True,
        "human_reason": _guard_human_reason(decision, bridge_response),
        "soulaana_translation": _guard_soulaana(decision),
    }

    guard = _redact(guard)
    scan = _safe_scan(guard)
    guard["no_secret_leakage"] = scan.get("ok") is True
    guard["leakage_scan"] = scan
    guard["guard_fingerprint"] = _fingerprint(guard)

    event = _record_guard_event({
        "user_id": user_id,
        "role": role,
        "route_path": route_path,
        "method": method,
        "classification": classification,
        "decision": decision,
        "allowed": allowed,
        "guard": guard,
    })
    guard["event"] = event

    return guard


def _locked_page_kind(decision: str) -> str:
    decision = _safe_str(decision)
    if decision == "step_up_required":
        return "step_up"
    if decision == "quarantine":
        return "quarantine"
    if decision == "lockdown":
        return "lockdown"
    if decision in {"summary_only", "redacted_summary"}:
        return "redacted_summary"
    if decision == "deny":
        return "denied"
    return "none"


def _guard_human_reason(decision: str, bridge_response: Dict[str, Any]) -> str:
    if decision == "allow":
        return "Tower route guard allowed this OB route to render."
    if decision == "step_up_required":
        return "Tower route guard requires step-up before this OB route/action can continue."
    if decision == "quarantine":
        return "Tower route guard placed this subject in a holding-room state."
    if decision == "lockdown":
        return "Tower route guard blocked this OB route because emergency lockdown is active."
    if decision in {"summary_only", "redacted_summary"}:
        return "Tower route guard allows only a redacted summary for this request."
    return bridge_response.get("human_reason") or "Tower route guard denied this OB route."


def _guard_soulaana(decision: str) -> str:
    if decision == "allow":
        return "Soulaana: Tower opened this OB door."
    if decision == "step_up_required":
        return "Soulaana: This OB door has a second lock. Verify first."
    if decision == "quarantine":
        return "Soulaana: Holding room. No OB hallway right now."
    if decision == "lockdown":
        return "Soulaana: Fortress sealed. OB waits outside."
    if decision in {"summary_only", "redacted_summary"}:
        return "Soulaana: Summary glass only. Details stay protected."
    return "Soulaana: No Tower clearance. No Observatory hallway."


def render_ob_locked_page(guard: Dict[str, Any]) -> str:
    guard = guard if isinstance(guard, dict) else {}
    kind = _safe_str(guard.get("locked_page_kind"), "denied")
    title_map = {
        "step_up": "Tower Step-Up Required",
        "quarantine": "Tower Holding Room",
        "lockdown": "Tower Lockdown Active",
        "redacted_summary": "Tower Summary-Only View",
        "denied": "Tower Access Denied",
        "none": "Tower Guard",
    }
    title = title_map.get(kind, "Tower Access Guard")
    reason = _safe_str(guard.get("human_reason"), "Tower guard blocked this route.")
    soulaana = _safe_str(guard.get("soulaana_translation"), "Soulaana: The Tower is guarding this hallway.")
    route_path = _safe_str(guard.get("route_path"), "/")

    safe = _redact({
        "title": title,
        "reason": reason,
        "soulaana": soulaana,
        "route_path": route_path,
        "decision": guard.get("decision"),
        "required_actions": guard.get("required_actions", []),
    })

    required_actions = safe.get("required_actions", [])
    if not isinstance(required_actions, list):
        required_actions = []

    chips = "".join(f"<span>{item}</span>" for item in required_actions[:6])

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>{safe.get('title')}</title>
  <style>
    body {{
      margin: 0;
      min-height: 100vh;
      background: #090907;
      color: #f5ead2;
      font-family: Inter, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      display: grid;
      place-items: center;
      padding: 24px;
    }}
    .card {{
      width: min(760px, 100%);
      border: 1px solid rgba(220,183,94,.36);
      border-radius: 30px;
      padding: 30px;
      background: linear-gradient(135deg, rgba(75,48,18,.74), rgba(12,13,10,.96));
      box-shadow: 0 22px 90px rgba(0,0,0,.42);
    }}
    .eyebrow {{
      color: rgba(220,183,94,.84);
      text-transform: uppercase;
      letter-spacing: .12em;
      font-size: 11px;
      margin-bottom: 10px;
    }}
    h1 {{
      margin: 0 0 12px;
      font-size: 32px;
      letter-spacing: -.04em;
    }}
    p {{
      color: rgba(245,234,210,.78);
      line-height: 1.55;
    }}
    .chips {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      margin-top: 18px;
    }}
    .chips span {{
      border: 1px solid rgba(245,234,210,.16);
      border-radius: 999px;
      padding: 8px 10px;
      background: rgba(255,255,255,.05);
      color: rgba(245,234,210,.82);
      font-size: 13px;
    }}
  </style>
</head>
<body>
  <main class="card">
    <div class="eyebrow">The Tower · OB route guard · {safe.get('decision')}</div>
    <h1>{safe.get('title')}</h1>
    <p><strong>Route:</strong> {safe.get('route_path')}</p>
    <p>{safe.get('reason')}</p>
    <p>{safe.get('soulaana')}</p>
    <div class="chips">{chips}</div>
  </main>
</body>
</html>
"""


def summarize_ob_route_guard(limit: int = 60) -> Dict[str, Any]:
    events = _load_events()

    try:
        limit = int(limit)
    except Exception:
        limit = 60
    limit = max(1, min(limit, 200))

    by_decision: Dict[str, int] = {}
    by_classification: Dict[str, int] = {}
    by_role: Dict[str, int] = {}

    for event in events:
        decision = event.get("decision", "unknown")
        role = event.get("role", "unknown")
        classification = event.get("classification", {})
        class_name = classification.get("classification", "unknown") if isinstance(classification, dict) else "unknown"

        by_decision[decision] = by_decision.get(decision, 0) + 1
        by_classification[class_name] = by_classification.get(class_name, 0) + 1
        by_role[role] = by_role.get(role, 0) + 1

    summary = {
        "ok": True,
        "pack": "102",
        "events_path": str(OB_ROUTE_GUARD_EVENTS_PATH),
        "summary_path": str(OB_ROUTE_GUARD_SUMMARY_PATH),
        "panel_path": str(OB_ROUTE_GUARD_PANEL_PATH),
        "event_count": len(events),
        "by_decision": by_decision,
        "by_classification": by_classification,
        "by_role": by_role,
        "recent_events": events[-limit:],
        "readiness_score": 100,
        "readiness_label": "OB Tower route guard ready",
        "human_reason": "OB route guard summary loaded.",
        "soulaana_translation": "Soulaana: OB has a route bouncer now. The Tower checks the hallway before render.",
    }

    summary = _redact(summary)
    scan = _safe_scan(summary)
    summary["no_secret_leakage"] = scan.get("ok") is True
    summary["leakage_scan"] = scan

    _write_json(OB_ROUTE_GUARD_SUMMARY_PATH, summary)
    write_ob_route_guard_panel(summary)
    return summary


def write_ob_route_guard_panel(summary: Dict[str, Any] | None = None) -> Dict[str, Any]:
    summary = summary if isinstance(summary, dict) else _load_json(OB_ROUTE_GUARD_SUMMARY_PATH, {})
    events = summary.get("recent_events", []) if isinstance(summary.get("recent_events"), list) else []

    cards = []
    for event in events[-24:]:
        decision = event.get("decision", "unknown")
        classification = event.get("classification", {}) if isinstance(event.get("classification"), dict) else {}
        cards.append(f"""
        <article class="card {'pass' if event.get('allowed') else 'locked'}">
          <div class="eyebrow">{decision} · {classification.get('classification', 'route')}</div>
          <h2>{event.get('route_path', '/')}</h2>
          <p>{event.get('role', 'role')} · {event.get('method', 'GET')}</p>
        </article>
        """)

    html = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>The Tower · OB Route Guard</title>
  <style>
    body {{
      margin: 0;
      min-height: 100vh;
      background: #080907;
      color: #f5ead2;
      font-family: Inter, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }}
    main {{
      max-width: 1140px;
      margin: 0 auto;
      padding: 42px 22px;
    }}
    .hero {{
      border: 1px solid rgba(220,183,94,.36);
      border-radius: 30px;
      padding: 30px;
      background: linear-gradient(135deg, rgba(75,48,18,.74), rgba(12,13,10,.96));
      box-shadow: 0 22px 90px rgba(0,0,0,.42);
    }}
    h1 {{
      margin: 0 0 10px;
      font-size: 34px;
      letter-spacing: -.04em;
    }}
    .hero p {{
      margin: 0;
      color: rgba(245,234,210,.76);
      line-height: 1.55;
    }}
    .stats {{
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 14px;
      margin: 20px 0;
    }}
    .stat {{
      border: 1px solid rgba(245,234,210,.14);
      border-radius: 20px;
      padding: 16px;
      background: rgba(255,255,255,.045);
    }}
    .stat b {{
      display: block;
      font-size: 24px;
    }}
    .grid {{
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 16px;
      margin-top: 18px;
    }}
    .card {{
      border: 1px solid rgba(245,234,210,.14);
      border-radius: 24px;
      padding: 18px;
      background: rgba(255,255,255,.045);
    }}
    .card.pass {{
      border-color: rgba(143,221,158,.34);
    }}
    .card.locked {{
      border-color: rgba(220,183,94,.34);
    }}
    .eyebrow {{
      color: rgba(220,183,94,.84);
      text-transform: uppercase;
      letter-spacing: .12em;
      font-size: 11px;
      margin-bottom: 8px;
    }}
    h2 {{
      margin: 0 0 8px;
      font-size: 18px;
    }}
    .card p {{
      color: rgba(245,234,210,.72);
      line-height: 1.45;
    }}
  </style>
</head>
<body>
<main>
  <section class="hero">
    <h1>The Tower · OB Route Guard</h1>
    <p>{summary.get('human_reason', 'OB route guard summary loaded.')}</p>
  </section>
  <section class="stats">
    <div class="stat"><b>{summary.get('event_count', 0)}</b><span>Guard Events</span></div>
    <div class="stat"><b>{summary.get('by_decision', {}).get('allow', 0) if isinstance(summary.get('by_decision'), dict) else 0}</b><span>Allowed</span></div>
    <div class="stat"><b>{summary.get('by_decision', {}).get('step_up_required', 0) if isinstance(summary.get('by_decision'), dict) else 0}</b><span>Step-up</span></div>
    <div class="stat"><b>{summary.get('readiness_score', 0)}</b><span>Readiness</span></div>
  </section>
  <section class="grid">{''.join(cards)}</section>
</main>
</body>
</html>
"""
    OB_ROUTE_GUARD_PANEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    OB_ROUTE_GUARD_PANEL_PATH.write_text(html, encoding="utf-8")

    return {
        "ok": True,
        "decision": "ob_route_guard_panel_written",
        "path": str(OB_ROUTE_GUARD_PANEL_PATH),
        "human_reason": "OB route guard HTML panel written.",
        "soulaana_translation": "Soulaana: OB route guard board posted.",
    }


def reset_ob_route_guard_for_test() -> Dict[str, Any]:
    _save_events([])
    _write_json(OB_ROUTE_GUARD_SUMMARY_PATH, {
        "ok": True,
        "pack": "102",
        "event_count": 0,
        "human_reason": "OB route guard reset for test.",
        "soulaana_translation": "Soulaana: OB route guard reset for a clean test lane.",
    })

    if OB_ROUTE_GUARD_PANEL_PATH.exists():
        try:
            OB_ROUTE_GUARD_PANEL_PATH.unlink()
        except Exception:
            pass

    return {
        "ok": True,
        "decision": "ob_route_guard_reset_for_test",
        "events_reset": True,
        "summary_reset": True,
        "soulaana_translation": "Soulaana: OB route guard reset for a clean test lane.",
    }



# ================================================================================
# PACK102B_MODE_ROUTE_CLASSIFICATION_ORDER
# ================================================================================
# Mode routes must be classified before generic/private app-entry routes.
# Example: /paper should be mode_route, not private_ob_entry.
# ================================================================================

try:
    _pack102b_original_classify_ob_route
except NameError:
    _pack102b_original_classify_ob_route = classify_ob_route


def classify_ob_route(route_path: str, method: str = "GET") -> Dict[str, Any]:
    route_path = _normalize_route_path(route_path)
    method = _safe_str(method, "GET").upper()

    if route_path in PUBLIC_OB_ROUTES or route_path.startswith("/public/"):
        return {
            "request_type": "route_access",
            "object_type": "route",
            "object_id": route_path,
            "action": "",
            "mode": "",
            "classification": "public_route",
        }

    # Important: mode routes must come before private app-entry routes.
    # /paper, /live/manual, etc. are not just app entry; they carry mode intent.
    if route_path in MODE_ROUTE_MAP:
        mode = MODE_ROUTE_MAP[route_path]
        return {
            "request_type": "mode_access",
            "object_type": "mode",
            "object_id": mode,
            "action": "",
            "mode": mode,
            "classification": "mode_route",
        }

    if route_path in PRIVATE_OB_ENTRY_ROUTES:
        return {
            "request_type": "app_entry",
            "object_type": "route",
            "object_id": route_path,
            "action": "",
            "mode": "",
            "classification": "private_ob_entry",
        }

    symbol = _match_first(SYMBOL_ROUTE_PATTERNS, route_path)
    if symbol:
        return {
            "request_type": "object_access",
            "object_type": "symbol",
            "object_id": symbol.upper(),
            "action": "",
            "mode": "",
            "classification": "symbol_object_route",
        }

    position_id = _match_first(POSITION_ROUTE_PATTERNS, route_path)
    if position_id:
        return {
            "request_type": "object_access",
            "object_type": "position",
            "object_id": position_id,
            "action": "",
            "mode": "",
            "classification": "position_object_route",
        }

    trade_id = _match_first(TRADE_ROUTE_PATTERNS, route_path)
    if trade_id:
        return {
            "request_type": "object_access",
            "object_type": "trade",
            "object_id": trade_id,
            "action": "",
            "mode": "",
            "classification": "trade_object_route",
        }

    if route_path.startswith(EXPORT_ROUTE_PREFIXES):
        return {
            "request_type": "export_access",
            "object_type": "export",
            "object_id": route_path,
            "action": "export" if method == "GET" else "download",
            "mode": "",
            "classification": "export_route",
        }

    if route_path.startswith(REVEAL_ROUTE_PREFIXES):
        return {
            "request_type": "reveal_access",
            "object_type": "analysis",
            "object_id": route_path,
            "action": "reveal_sensitive",
            "mode": "",
            "classification": "reveal_route",
        }

    if route_path.startswith(LIVE_ROUTE_PREFIXES):
        mode = "live_manual"
        if "/hybrid" in route_path:
            mode = "live_hybrid"
        if "/automated" in route_path:
            mode = "live_automated"
        return {
            "request_type": "live_action_access",
            "object_type": "mode",
            "object_id": mode,
            "action": "live_mode_enable",
            "mode": mode,
            "classification": "live_route",
        }

    if route_path.startswith(ADMIN_ROUTE_PREFIXES):
        return {
            "request_type": "action_access",
            "object_type": "admin_panel",
            "object_id": route_path,
            "action": "admin_override",
            "mode": "",
            "classification": "admin_route",
        }

    return {
        "request_type": "route_access",
        "object_type": "route",
        "object_id": route_path,
        "action": "",
        "mode": "",
        "classification": "unknown_route",
    }

