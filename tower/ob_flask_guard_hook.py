
from __future__ import annotations

import functools
import hashlib
import json
import secrets
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, List, Tuple


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "tower" / "data"

OB_FLASK_GUARD_EVENTS_PATH = DATA_DIR / "ob_flask_guard_events.json"
OB_FLASK_GUARD_SUMMARY_PATH = DATA_DIR / "ob_flask_guard_summary.json"
OB_FLASK_GUARD_PANEL_PATH = DATA_DIR / "ob_flask_guard_panel.html"


DEFAULT_PUBLIC_USER_ID = "anonymous"
DEFAULT_PUBLIC_ROLE = "public"
DEFAULT_AUTHENTICATED_ROLE = "beta"
DEFAULT_OWNER_USER_ID = "owner_solice"


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


def _event_id(prefix: str = "ob_flask_guard") -> str:
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
                clean[key] = "[REDACTED_OB_FLASK_GUARD_SENSITIVE]"
                redacted_count += 1
                continue

            redacted_item = _redact(item)

            if isinstance(redacted_item, dict) and "__redacted_ob_flask_guard_field_count__" in redacted_item:
                try:
                    redacted_count += int(redacted_item.get("__redacted_ob_flask_guard_field_count__", 0))
                except Exception:
                    redacted_count += 1
                redacted_item = dict(redacted_item)
                redacted_item.pop("__redacted_ob_flask_guard_field_count__", None)

            clean[key] = redacted_item

        if redacted_count:
            clean["__redacted_ob_flask_guard_field_count__"] = redacted_count

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
            return "[REDACTED_OB_FLASK_GUARD_VALUE]"
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
    data = _load_json(OB_FLASK_GUARD_EVENTS_PATH, [])
    return data if isinstance(data, list) else []


def _save_events(events: List[Dict[str, Any]]) -> None:
    _write_json(OB_FLASK_GUARD_EVENTS_PATH, events)


def _record_hook_event(event: Dict[str, Any]) -> Dict[str, Any]:
    event = dict(event)
    event.setdefault("event_id", _event_id("ob_flask_guard_evt"))
    event.setdefault("event_type", "tower_ob_flask_guard_event")
    event.setdefault("created_at", _utc_now())
    event.setdefault("pack", "103")

    event = _redact(event)
    event["event_fingerprint"] = _fingerprint(event)

    events = _load_events()
    events.append(event)
    _save_events(events)

    try:
        from tower.tamper_evident_audit_chain import create_tamper_chain_entry

        create_tamper_chain_entry(
            event_type="tower_ob_flask_guard_event_snapshot",
            source_name="ob_flask_guard_events",
            source_path=str(OB_FLASK_GUARD_EVENTS_PATH),
            source_hash=_fingerprint(events),
            record_count=len(events),
            actor_user_id=_safe_str(event.get("user_id"), "tower_system"),
            reason=f"Pack 103 chained OB Flask guard hook event {event.get('decision')}.",
            metadata={
                "pack": "103",
                "event_id": event.get("event_id"),
                "route_path": event.get("route_path"),
                "decision": event.get("decision"),
            },
        )
    except Exception:
        pass

    return event


def _get_flask_request() -> Any:
    try:
        from flask import request
        return request
    except Exception:
        return None


def _get_flask_session() -> Dict[str, Any]:
    try:
        from flask import session
        return session
    except Exception:
        return {}


def _extract_from_obj(obj: Any, names: List[str], default: Any = "") -> Any:
    if obj is None:
        return default

    if isinstance(obj, dict):
        for name in names:
            if name in obj and obj.get(name) not in {None, ""}:
                return obj.get(name)
        return default

    for name in names:
        try:
            value = getattr(obj, name)
            if value not in {None, ""}:
                return value
        except Exception:
            pass

    return default


def infer_user_role(user: Any = None, session_data: Dict[str, Any] | None = None) -> Dict[str, Any]:
    session_data = session_data if isinstance(session_data, dict) else {}

    user_id = _extract_from_obj(
        user,
        ["id", "user_id", "username", "email"],
        default="",
    )

    if not user_id:
        user_id = _extract_from_obj(
            session_data,
            ["user_id", "username", "email"],
            default=DEFAULT_PUBLIC_USER_ID,
        )

    role = _extract_from_obj(
        user,
        ["role", "designation", "tier", "access_role"],
        default="",
    )

    if not role:
        role = _extract_from_obj(
            session_data,
            ["role", "designation", "tier", "access_role"],
            default="",
        )

    user_id = _safe_str(user_id, DEFAULT_PUBLIC_USER_ID)
    role = _safe_str(role, "")

    lowered_user = user_id.lower()
    lowered_role = role.lower()

    if lowered_user in {"owner_solice", "solice", "solice_bowdre", "bowdre.solice@gmail.com"}:
        role = "owner"
        user_id = "owner_solice"
    elif lowered_role in {"owner", "admin_owner", "master"}:
        role = "owner"
    elif lowered_role in {"admin", "manager"}:
        role = lowered_role
    elif lowered_role in {"elite", "pro", "starter", "free", "beta", "tester", "member", "user"}:
        # For Tower bridge purposes, subscription/tier labels map to beta/user access
        # unless explicitly owner/admin.
        role = "beta"
    elif user_id != DEFAULT_PUBLIC_USER_ID:
        role = DEFAULT_AUTHENTICATED_ROLE
    else:
        role = DEFAULT_PUBLIC_ROLE

    return {
        "ok": True,
        "user_id": user_id,
        "role": role,
        "human_reason": "User/role inferred for OB Tower Flask guard.",
    }


def extract_flask_guard_context(
    *,
    route_path: str = "",
    method: str = "",
    user: Any = None,
    session_data: Dict[str, Any] | None = None,
    request_obj: Any = None,
    metadata: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    request_obj = request_obj if request_obj is not None else _get_flask_request()
    session_data = session_data if isinstance(session_data, dict) else dict(_get_flask_session() or {})
    metadata = metadata if isinstance(metadata, dict) else {}

    inferred = infer_user_role(user=user, session_data=session_data)

    if not route_path:
        route_path = _extract_from_obj(request_obj, ["path", "full_path"], default="/")

    if not method:
        method = _extract_from_obj(request_obj, ["method"], default="GET")

    headers = {}
    try:
        headers = dict(getattr(request_obj, "headers", {}) or {})
    except Exception:
        headers = {}

    remote_addr = _extract_from_obj(request_obj, ["remote_addr"], default="")
    ip_address = (
        headers.get("X-Forwarded-For", "").split(",")[0].strip()
        or headers.get("X-Real-IP", "").strip()
        or remote_addr
    )

    session_id = (
        _extract_from_obj(session_data, ["session_id", "_id"], default="")
        or headers.get("X-Session-ID", "")
    )

    device_id = (
        _extract_from_obj(session_data, ["device_id"], default="")
        or headers.get("X-Device-ID", "")
    )

    context = {
        "ok": True,
        "pack": "103",
        "created_at": _utc_now(),
        "user_id": inferred.get("user_id"),
        "role": inferred.get("role"),
        "route_path": _safe_str(route_path, "/"),
        "method": _safe_str(method, "GET").upper(),
        "session_id": _safe_str(session_id),
        "device_id": _safe_str(device_id),
        "ip_address": _safe_str(ip_address),
        "metadata": _redact({
            "source": "flask_guard_hook",
            "headers_seen": sorted([key for key in headers.keys() if key.lower().startswith("x-")])[:12],
            **metadata,
        }),
    }

    context["context_fingerprint"] = _fingerprint(context)
    return _redact(context)


def guard_current_ob_flask_route(
    *,
    route_path: str = "",
    method: str = "",
    user: Any = None,
    session_data: Dict[str, Any] | None = None,
    request_obj: Any = None,
    metadata: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    context = extract_flask_guard_context(
        route_path=route_path,
        method=method,
        user=user,
        session_data=session_data,
        request_obj=request_obj,
        metadata=metadata,
    )

    from tower.ob_tower_route_guard import guard_ob_route

    guard = guard_ob_route(
        user_id=context.get("user_id", DEFAULT_PUBLIC_USER_ID),
        role=context.get("role", DEFAULT_PUBLIC_ROLE),
        route_path=context.get("route_path", "/"),
        method=context.get("method", "GET"),
        session_id=context.get("session_id", ""),
        device_id=context.get("device_id", ""),
        ip_address=context.get("ip_address", ""),
        metadata=context.get("metadata", {}),
    )

    result = {
        "ok": guard.get("ok") is True,
        "pack": "103",
        "hook_id": _event_id("ob_flask_hook"),
        "created_at": _utc_now(),
        "context": context,
        "guard": guard,
        "decision": guard.get("decision"),
        "allowed": guard.get("allowed") is True,
        "should_render_route": guard.get("should_render_route") is True,
        "should_render_locked_page": guard.get("should_render_locked_page") is True,
        "locked_page_kind": guard.get("locked_page_kind"),
        "required_actions": guard.get("required_actions", []),
        "human_reason": (
            "Flask guard hook allowed this OB route."
            if guard.get("allowed") is True
            else "Flask guard hook blocked or gated this OB route."
        ),
        "soulaana_translation": (
            "Soulaana: Flask asked Tower. This route can render."
            if guard.get("allowed") is True
            else "Soulaana: Flask asked Tower. The hallway is locked or gated."
        ),
    }

    result = _redact(result)
    scan = _safe_scan(result)
    result["no_secret_leakage"] = scan.get("ok") is True
    result["leakage_scan"] = scan
    result["hook_fingerprint"] = _fingerprint(result)

    event = _record_hook_event({
        "user_id": context.get("user_id"),
        "role": context.get("role"),
        "route_path": context.get("route_path"),
        "method": context.get("method"),
        "decision": result.get("decision"),
        "allowed": result.get("allowed"),
        "locked_page_kind": result.get("locked_page_kind"),
        "hook": result,
    })
    result["event"] = event

    return result


def render_locked_response_from_hook(hook_result: Dict[str, Any]) -> Tuple[str, int]:
    hook_result = hook_result if isinstance(hook_result, dict) else {}
    guard = hook_result.get("guard", {}) if isinstance(hook_result.get("guard"), dict) else hook_result

    from tower.ob_tower_route_guard import render_ob_locked_page

    html = render_ob_locked_page(guard)
    decision = _safe_str(hook_result.get("decision") or guard.get("decision"), "deny")

    status_code = 403
    if decision == "step_up_required":
        status_code = 428
    elif decision == "quarantine":
        status_code = 423
    elif decision == "lockdown":
        status_code = 503
    elif decision in {"summary_only", "redacted_summary"}:
        status_code = 200

    return html, status_code


def require_ob_tower_guard(
    *,
    route_path: str = "",
    user_getter: Callable[[], Any] | None = None,
    session_getter: Callable[[], Dict[str, Any]] | None = None,
    metadata: Dict[str, Any] | None = None,
) -> Callable:
    """Decorator factory for future Flask route wiring.

    Usage later:
        @app.route("/paper")
        @require_ob_tower_guard(route_path="/paper")
        def paper_dashboard():
            ...

    If allowed: original route runs.
    If blocked/gated: locked Tower page returns.
    """
    def decorator(fn: Callable) -> Callable:
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            user = user_getter() if callable(user_getter) else None
            session_data = session_getter() if callable(session_getter) else None

            hook = guard_current_ob_flask_route(
                route_path=route_path,
                user=user,
                session_data=session_data,
                metadata=metadata or {},
            )

            if hook.get("allowed") is True:
                return fn(*args, **kwargs)

            html, status_code = render_locked_response_from_hook(hook)
            return html, status_code

        return wrapper

    return decorator


def guard_then_call(
    *,
    view_func: Callable[[], Any],
    route_path: str,
    user: Any = None,
    session_data: Dict[str, Any] | None = None,
    method: str = "GET",
    metadata: Dict[str, Any] | None = None,
) -> Any:
    """Testable non-Flask helper: guard first, then run view if allowed."""
    hook = guard_current_ob_flask_route(
        route_path=route_path,
        method=method,
        user=user,
        session_data=session_data,
        metadata=metadata or {},
    )

    if hook.get("allowed") is True:
        return {
            "ok": True,
            "decision": "route_rendered",
            "hook": hook,
            "view_result": view_func(),
        }

    html, status_code = render_locked_response_from_hook(hook)

    return {
        "ok": True,
        "decision": "locked_response_returned",
        "hook": hook,
        "status_code": status_code,
        "html": html,
    }


def summarize_ob_flask_guard_hook(limit: int = 60) -> Dict[str, Any]:
    events = _load_events()

    try:
        limit = int(limit)
    except Exception:
        limit = 60
    limit = max(1, min(limit, 200))

    by_decision: Dict[str, int] = {}
    by_role: Dict[str, int] = {}
    by_locked_kind: Dict[str, int] = {}

    for event in events:
        decision = event.get("decision", "unknown")
        role = event.get("role", "unknown")
        locked_kind = event.get("locked_page_kind", "none")

        by_decision[decision] = by_decision.get(decision, 0) + 1
        by_role[role] = by_role.get(role, 0) + 1
        by_locked_kind[locked_kind] = by_locked_kind.get(locked_kind, 0) + 1

    summary = {
        "ok": True,
        "pack": "103",
        "events_path": str(OB_FLASK_GUARD_EVENTS_PATH),
        "summary_path": str(OB_FLASK_GUARD_SUMMARY_PATH),
        "panel_path": str(OB_FLASK_GUARD_PANEL_PATH),
        "event_count": len(events),
        "by_decision": by_decision,
        "by_role": by_role,
        "by_locked_kind": by_locked_kind,
        "recent_events": events[-limit:],
        "readiness_score": 100,
        "readiness_label": "OB Flask guard hook ready",
        "human_reason": "OB Flask guard hook summary loaded.",
        "soulaana_translation": "Soulaana: Flask has a clean Tower knock now.",
    }

    summary = _redact(summary)
    scan = _safe_scan(summary)
    summary["no_secret_leakage"] = scan.get("ok") is True
    summary["leakage_scan"] = scan

    _write_json(OB_FLASK_GUARD_SUMMARY_PATH, summary)
    write_ob_flask_guard_panel(summary)
    return summary


def write_ob_flask_guard_panel(summary: Dict[str, Any] | None = None) -> Dict[str, Any]:
    summary = summary if isinstance(summary, dict) else _load_json(OB_FLASK_GUARD_SUMMARY_PATH, {})
    events = summary.get("recent_events", []) if isinstance(summary.get("recent_events"), list) else []

    cards = []
    for event in events[-24:]:
        decision = event.get("decision", "unknown")
        cards.append(f"""
        <article class="card {'pass' if event.get('allowed') else 'locked'}">
          <div class="eyebrow">{decision} · {event.get('locked_page_kind', 'none')}</div>
          <h2>{event.get('route_path', '/')}</h2>
          <p>{event.get('role', 'role')} · {event.get('method', 'GET')}</p>
        </article>
        """)

    html = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>The Tower · OB Flask Guard Hook</title>
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
    <h1>The Tower · OB Flask Guard Hook</h1>
    <p>{summary.get('human_reason', 'OB Flask guard hook summary loaded.')}</p>
  </section>
  <section class="stats">
    <div class="stat"><b>{summary.get('event_count', 0)}</b><span>Hook Events</span></div>
    <div class="stat"><b>{summary.get('by_decision', {}).get('allow', 0) if isinstance(summary.get('by_decision'), dict) else 0}</b><span>Allowed</span></div>
    <div class="stat"><b>{summary.get('by_decision', {}).get('step_up_required', 0) if isinstance(summary.get('by_decision'), dict) else 0}</b><span>Step-up</span></div>
    <div class="stat"><b>{summary.get('readiness_score', 0)}</b><span>Readiness</span></div>
  </section>
  <section class="grid">{''.join(cards)}</section>
</main>
</body>
</html>
"""
    OB_FLASK_GUARD_PANEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    OB_FLASK_GUARD_PANEL_PATH.write_text(html, encoding="utf-8")

    return {
        "ok": True,
        "decision": "ob_flask_guard_panel_written",
        "path": str(OB_FLASK_GUARD_PANEL_PATH),
        "human_reason": "OB Flask guard hook HTML panel written.",
        "soulaana_translation": "Soulaana: Flask guard hook board posted.",
    }


def reset_ob_flask_guard_hook_for_test() -> Dict[str, Any]:
    _save_events([])
    _write_json(OB_FLASK_GUARD_SUMMARY_PATH, {
        "ok": True,
        "pack": "103",
        "event_count": 0,
        "human_reason": "OB Flask guard hook reset for test.",
        "soulaana_translation": "Soulaana: Flask guard hook reset for a clean test lane.",
    })

    if OB_FLASK_GUARD_PANEL_PATH.exists():
        try:
            OB_FLASK_GUARD_PANEL_PATH.unlink()
        except Exception:
            pass

    return {
        "ok": True,
        "decision": "ob_flask_guard_hook_reset_for_test",
        "events_reset": True,
        "summary_reset": True,
        "soulaana_translation": "Soulaana: OB Flask guard hook reset for a clean test lane.",
    }
