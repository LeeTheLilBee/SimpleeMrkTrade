
# ============================================================
# THE TOWER WEB BRIDGE
# Pack 026 — Private Front Door Gate
# ============================================================

from __future__ import annotations

import importlib.util
import json
import os
import sys
import types
from pathlib import Path
from typing import Any, Dict, Optional


SECURITY_COMMAND_HTML = Path(__file__).resolve().parent / "data" / "security_command_dashboard.html"


def _project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _tower_root() -> Path:
    return Path(__file__).resolve().parent


def _ensure_project_import_path() -> None:
    root = _project_root()
    tower_root = _tower_root()

    root_text = str(root)
    tower_text = str(tower_root)

    if root_text not in sys.path:
        sys.path.insert(0, root_text)

    try:
        os.chdir(root_text)
    except Exception:
        pass

    existing = sys.modules.get("tower")
    if existing is None or not hasattr(existing, "__path__"):
        package = types.ModuleType("tower")
        package.__file__ = str(tower_root / "__init__.py")
        package.__path__ = [tower_text]
        package.__package__ = "tower"
        try:
            package.__spec__ = importlib.util.spec_from_file_location(
                "tower",
                str(tower_root / "__init__.py"),
                submodule_search_locations=[tower_text],
            )
        except Exception:
            package.__spec__ = None
        sys.modules["tower"] = package
    else:
        paths = list(getattr(existing, "__path__", []))
        if tower_text not in paths:
            paths.insert(0, tower_text)
            existing.__path__ = paths


def _load_tower_package_module(module_basename: str, file_path: Path):
    _ensure_project_import_path()

    module_name = f"tower.{module_basename}"
    existing = sys.modules.get(module_name)
    if existing is not None:
        return existing

    spec = importlib.util.spec_from_file_location(module_name, str(file_path))
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load module spec for {file_path}")

    module = importlib.util.module_from_spec(spec)
    module.__package__ = "tower"
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def _safe_tower_status() -> Dict[str, Any]:
    _ensure_project_import_path()

    try:
        from tower.tower_status import get_tower_status
        payload = get_tower_status()
        if isinstance(payload, dict):
            payload.setdefault("ok", True)
            return payload
    except Exception as normal_error:
        try:
            module = _load_tower_package_module("tower_status", _tower_root() / "tower_status.py")
            payload = module.get_tower_status()
            if isinstance(payload, dict):
                payload.setdefault("ok", True)
                return payload
        except Exception as file_error:
            return {
                "ok": False,
                "tower_name": "The Tower",
                "reason_code": "tower_status_unavailable",
                "human_reason": "Tower status could not be loaded.",
                "normal_import_error": f"{type(normal_error).__name__}: {normal_error}",
                "file_path_error": f"{type(file_error).__name__}: {file_error}",
            }

    return {
        "ok": False,
        "tower_name": "The Tower",
        "reason_code": "tower_status_bad_payload",
        "human_reason": "Tower status returned an invalid payload.",
    }


def _safe_security_command_html(tower_user_id: str = "owner_solice") -> str:
    _ensure_project_import_path()

    try:
        from tower.security_command_page import save_security_command_dashboard_html
        result = save_security_command_dashboard_html(tower_user_id=tower_user_id)
        saved_path = result.get("path") if isinstance(result, dict) else None
        if saved_path and Path(saved_path).exists():
            return Path(saved_path).read_text(encoding="utf-8")
    except Exception:
        pass

    if SECURITY_COMMAND_HTML.exists():
        return SECURITY_COMMAND_HTML.read_text(encoding="utf-8")

    return """
    <!doctype html>
    <html><head><meta charset="utf-8"><title>Restricted</title></head>
    <body style="background:#050505;color:#f8fafc;font-family:Arial;padding:32px;">
      <h1>Restricted area</h1>
      <p>Clearance required.</p>
    </body></html>
    """


def _generic_locked_html() -> str:
    return """
    <!doctype html>
    <html>
    <head>
      <meta charset="utf-8">
      <meta name="viewport" content="width=device-width, initial-scale=1">
      <title>Restricted</title>
      <style>
        :root { color-scheme: dark; }
        body {
          margin: 0;
          min-height: 100vh;
          display: grid;
          place-items: center;
          background:
            radial-gradient(circle at 25% 10%, rgba(120,120,120,.12), transparent 32%),
            linear-gradient(135deg, #050505, #0b0b0b 50%, #050505);
          color: #f5f5f4;
          font-family: Arial, sans-serif;
        }
        .panel {
          width: min(520px, calc(100vw - 36px));
          border: 1px solid rgba(255,255,255,.12);
          background: rgba(255,255,255,.045);
          border-radius: 24px;
          padding: 28px;
          box-shadow: 0 30px 80px rgba(0,0,0,.45);
        }
        .kicker {
          color: #a8a29e;
          font-size: .72rem;
          letter-spacing: .22em;
          text-transform: uppercase;
          font-weight: 800;
        }
        h1 { margin: 10px 0; font-size: 2rem; letter-spacing: -.03em; }
        p { margin: 0; color: #a8a29e; line-height: 1.7; }
      </style>
    </head>
    <body>
      <main class="panel">
        <div class="kicker">Restricted</div>
        <h1>Clearance required.</h1>
        <p>This area is not available from this session.</p>
      </main>
    </body>
    </html>
    """


def _locked_json(reason_code: str = "clearance_required") -> Dict[str, Any]:
    return {
        "ok": False,
        "reason_code": reason_code,
        "human_reason": "Clearance required.",
    }


def _extract_keycard_token(request_obj) -> Optional[str]:
    token = None

    try:
        token = request_obj.args.get("tower_keycard")
    except Exception:
        token = None

    if not token:
        try:
            token = request_obj.headers.get("X-Tower-Keycard")
        except Exception:
            token = None

    if not token:
        try:
            token = request_obj.cookies.get("tower_keycard_pass")
        except Exception:
            token = None

    token = str(token or "").strip()
    return token or None


def _tower_user_id_from_request(request_obj) -> str:
    try:
        user_id = request_obj.args.get("tower_user_id")
    except Exception:
        user_id = None
    return str(user_id or "anonymous").strip() or "anonymous"


def _session_id_from_request(request_obj) -> Optional[str]:
    for key in ("tower_session_id", "session_id"):
        try:
            value = request_obj.args.get(key)
            if value:
                return str(value).strip()
        except Exception:
            pass

    try:
        value = request_obj.headers.get("X-Tower-Session")
        if value:
            return str(value).strip()
    except Exception:
        pass

    return None


def _device_id_from_request(request_obj) -> Optional[str]:
    for key in ("tower_device_id", "device_id"):
        try:
            value = request_obj.args.get(key)
            if value:
                return str(value).strip()
        except Exception:
            pass

    try:
        value = request_obj.headers.get("X-Tower-Device")
        if value:
            return str(value).strip()
    except Exception:
        pass

    return None


def _validate_front_door(
    *,
    request_obj,
    door_id: str,
    action: str = "view",
    classification: str = "restricted",
    max_allowed_risk_score: int = 85,
) -> Dict[str, Any]:
    _ensure_project_import_path()

    user_id = _tower_user_id_from_request(request_obj)
    token = _extract_keycard_token(request_obj)
    session_id = _session_id_from_request(request_obj)
    device_id = _device_id_from_request(request_obj)

    if not token:
        return {
            "allowed": False,
            "decision": "deny",
            "reason_code": "tower_keycard_required",
            "human_reason": "Clearance required.",
            "risk_state": "restricted",
            "risk_score": 60,
            "required_actions": ["present_valid_keycard_pass"],
            "metadata": {"door_id": door_id, "action": action, "user_id": user_id},
        }

    try:
        from tower.keycard_passes import validate_keycard_pass

        return validate_keycard_pass(
            token=token,
            app_name="tower",
            door_type="route",
            door_id=door_id,
            action=action,
            user_id=user_id if user_id != "anonymous" else None,
            session_id=session_id,
            device_id=device_id,
            required_clearance_level=classification,
            current_risk_score=0,
            max_allowed_risk_score=max_allowed_risk_score,
        )
    except Exception:
        return {
            "allowed": False,
            "decision": "deny",
            "reason_code": "tower_keycard_validation_failed",
            "human_reason": "Clearance required.",
            "risk_state": "restricted",
            "risk_score": 75,
            "required_actions": ["security_review_required"],
            "metadata": {"door_id": door_id, "action": action, "user_id": user_id},
        }


def _mark_response_private(response_obj):
    try:
        response_obj.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, private, max-age=0"
        response_obj.headers["Pragma"] = "no-cache"
        response_obj.headers["Expires"] = "0"
        response_obj.headers["X-Robots-Tag"] = "noindex, nofollow, noarchive"
    except Exception:
        pass
    return response_obj


def register_tower_web_routes(app):
    _ensure_project_import_path()

    from flask import Response, jsonify, redirect, request

    existing_routes = {str(rule.rule) for rule in app.url_map.iter_rules()}
    expected_routes = [
        "/tower",
        "/tower/",
        "/tower/security-command",
        "/tower/security-command/regenerate",
        "/tower/status.json",
    ]

    if all(route in existing_routes for route in expected_routes):
        return {
            "ok": True,
            "status": "already_registered",
            "human_reason": "The Tower web routes already exist on this Flask app.",
            "routes": expected_routes,
        }

    def _locked_html_response(reason_code: str = "clearance_required"):
        response = Response(_generic_locked_html(), status=403, mimetype="text/html")
        response.headers["X-Tower-Gate"] = reason_code
        return _mark_response_private(response)

    def _locked_json_response(reason_code: str = "clearance_required"):
        response = jsonify(_locked_json(reason_code))
        response.status_code = 403
        response.headers["X-Tower-Gate"] = reason_code
        return _mark_response_private(response)

    def _allowed_or_locked_html(door_id: str, action: str = "view", classification: str = "restricted"):
        decision = _validate_front_door(
            request_obj=request,
            door_id=door_id,
            action=action,
            classification=classification,
        )
        if not decision.get("allowed"):
            return None, _locked_html_response(str(decision.get("reason_code") or "clearance_required"))
        return decision, None

    def _allowed_or_locked_json(door_id: str, action: str = "view", classification: str = "restricted"):
        decision = _validate_front_door(
            request_obj=request,
            door_id=door_id,
            action=action,
            classification=classification,
        )
        if not decision.get("allowed"):
            return None, _locked_json_response(str(decision.get("reason_code") or "clearance_required"))
        return decision, None

    if "/tower" not in existing_routes:
        @app.route("/tower", endpoint="tower_command_entry_no_slash")
        def tower_command_entry_no_slash():
            decision, locked = _allowed_or_locked_html("/tower", action="view", classification="restricted")
            if locked is not None:
                return locked
            return tower_command_entry()

    if "/tower/" not in existing_routes:
        @app.route("/tower/", endpoint="tower_command_entry")
        def tower_command_entry():
            decision, locked = _allowed_or_locked_html("/tower", action="view", classification="restricted")
            if locked is not None:
                return locked

            user_id = _tower_user_id_from_request(request)
            token = _extract_keycard_token(request) or ""
            session_id = _session_id_from_request(request) or ""
            device_id = _device_id_from_request(request) or ""

            query_parts = [f"tower_user_id={user_id}", f"tower_keycard={token}"]
            if session_id:
                query_parts.append(f"tower_session_id={session_id}")
            if device_id:
                query_parts.append(f"tower_device_id={device_id}")

            command_url = "/tower/security-command?" + "&".join(query_parts)
            status_url = "/tower/status.json?" + "&".join(query_parts)

            html = f"""
            <!doctype html>
            <html>
            <head>
              <meta charset="utf-8">
              <meta name="viewport" content="width=device-width, initial-scale=1">
              <title>The Tower - Command Entry</title>
              <style>
                body {{
                  margin: 0;
                  min-height: 100vh;
                  background:
                    radial-gradient(circle at 20% 10%, rgba(95,120,76,.22), transparent 34%),
                    linear-gradient(135deg, #050806, #101510 50%, #050806);
                  color: #f5f5f4;
                  font-family: Arial, sans-serif;
                  display: grid;
                  place-items: center;
                }}
                .panel {{
                  width: min(760px, calc(100vw - 40px));
                  border: 1px solid rgba(217,249,157,.20);
                  background: rgba(5,8,6,.86);
                  border-radius: 32px;
                  padding: 34px;
                  box-shadow: 0 30px 100px rgba(0,0,0,.55);
                }}
                .kicker {{
                  color: rgba(217,249,157,.7);
                  font-size: .72rem;
                  letter-spacing: .28em;
                  text-transform: uppercase;
                  font-weight: 900;
                }}
                h1 {{
                  margin: 10px 0 14px;
                  font-size: clamp(2.4rem, 8vw, 5.5rem);
                  line-height: .95;
                  letter-spacing: -.06em;
                }}
                p {{
                  color: #a8a29e;
                  line-height: 1.75;
                  font-size: 1rem;
                  max-width: 58ch;
                }}
                .actions {{
                  margin-top: 28px;
                  display: flex;
                  flex-wrap: wrap;
                  gap: 12px;
                }}
                a {{
                  display: inline-flex;
                  text-decoration: none;
                  color: #ecfccb;
                  border: 1px solid rgba(217,249,157,.24);
                  background: rgba(217,249,157,.08);
                  border-radius: 999px;
                  padding: 12px 16px;
                  font-weight: 800;
                }}
                a.secondary {{
                  color: #d6d3d1;
                  border-color: rgba(255,255,255,.12);
                  background: rgba(255,255,255,.055);
                }}
              </style>
            </head>
            <body>
              <main class="panel">
                <div class="kicker">Private command access</div>
                <h1>The Tower</h1>
                <p>Clearance accepted. Choose the command view you want to open.</p>
                <div class="actions">
                  <a href="{command_url}">Open Security Command</a>
                  <a class="secondary" href="{status_url}">View Status JSON</a>
                </div>
              </main>
            </body>
            </html>
            """
            return _mark_response_private(Response(html, mimetype="text/html"))

    if "/tower/security-command" not in existing_routes:
        @app.route("/tower/security-command", endpoint="tower_security_command")
        def tower_security_command():
            decision, locked = _allowed_or_locked_html(
                "/tower/security-command",
                action="view",
                classification="restricted",
            )
            if locked is not None:
                return locked

            user_id = _tower_user_id_from_request(request)
            html = _safe_security_command_html(tower_user_id=user_id)
            return _mark_response_private(Response(html, mimetype="text/html"))

    if "/tower/security-command/regenerate" not in existing_routes:
        @app.route("/tower/security-command/regenerate", methods=["POST", "GET"], endpoint="tower_security_command_regenerate")
        def tower_security_command_regenerate():
            decision, locked = _allowed_or_locked_html(
                "/tower/security-command/regenerate",
                action="regenerate",
                classification="critical",
            )
            if locked is not None:
                return locked

            user_id = _tower_user_id_from_request(request)
            try:
                from tower.security_command_page import save_security_command_dashboard_html
                result = save_security_command_dashboard_html(tower_user_id=user_id)
                payload = {
                    "ok": True,
                    "status": "regenerated",
                    "human_reason": "Security Command Dashboard regenerated.",
                    "result": result,
                }
            except Exception as exc:
                payload = {
                    "ok": False,
                    "reason_code": "tower_dashboard_regenerate_failed",
                    "human_reason": "Security Command Dashboard could not be regenerated.",
                    "error": f"{type(exc).__name__}: {exc}",
                }

            if request.method == "POST":
                response = jsonify(payload)
                response.status_code = 200 if payload.get("ok") else 500
                return _mark_response_private(response)

            token = _extract_keycard_token(request) or ""
            session_id = _session_id_from_request(request) or ""
            device_id = _device_id_from_request(request) or ""
            query_parts = [f"tower_user_id={user_id}", f"tower_keycard={token}"]
            if session_id:
                query_parts.append(f"tower_session_id={session_id}")
            if device_id:
                query_parts.append(f"tower_device_id={device_id}")
            return redirect("/tower/security-command?" + "&".join(query_parts))

    if "/tower/status.json" not in existing_routes:
        @app.route("/tower/status.json", endpoint="tower_status_json")
        def tower_status_json():
            decision, locked = _allowed_or_locked_json(
                "/tower/status.json",
                action="view",
                classification="restricted",
            )
            if locked is not None:
                return locked

            payload = _safe_tower_status()
            payload.setdefault("ok", True)
            response = jsonify(payload)
            return _mark_response_private(response)

    registered_routes = sorted(str(rule.rule) for rule in app.url_map.iter_rules() if str(rule.rule).startswith("/tower"))
    return {
        "ok": True,
        "status": "registered",
        "human_reason": "The Tower web routes were registered with private front door gates.",
        "routes": registered_routes,
    }
