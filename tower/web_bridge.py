
# ============================================================
# THE TOWER WEB BRIDGE
# Clean Pack 024D version
# ============================================================

from __future__ import annotations

import importlib.util
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict


def _project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _tower_root() -> Path:
    return Path(__file__).resolve().parent


def _ensure_project_import_path() -> None:
    root = str(_project_root())
    if root not in sys.path:
        sys.path.insert(0, root)


def _load_module_from_file(module_name: str, file_path: Path):
    spec = importlib.util.spec_from_file_location(module_name, str(file_path))
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load module spec for {file_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _safe_tower_status() -> Dict[str, Any]:
    """
    Loads Tower status in a way that survives weird Flask import paths.
    Normal import first. File-path import second.
    """
    _ensure_project_import_path()

    try:
        from tower.tower_status import get_tower_status
        payload = get_tower_status()
        if isinstance(payload, dict):
            payload.setdefault("ok", True)
            return payload
        return {
            "ok": False,
            "tower_name": "The Tower",
            "reason_code": "tower_status_bad_payload",
            "human_reason": "Tower status returned a non-dict payload.",
            "payload_type": str(type(payload)),
        }
    except Exception as normal_error:
        try:
            tower_status_path = _tower_root() / "tower_status.py"
            module = _load_module_from_file("_tower_status_pack024d", tower_status_path)
            payload = module.get_tower_status()
            if isinstance(payload, dict):
                payload.setdefault("ok", True)
                return payload
            return {
                "ok": False,
                "tower_name": "The Tower",
                "reason_code": "tower_status_bad_payload",
                "human_reason": "Tower status returned a non-dict payload by file path.",
                "payload_type": str(type(payload)),
            }
        except Exception as file_error:
            return {
                "ok": False,
                "tower_name": "The Tower",
                "reason_code": "tower_status_unavailable",
                "human_reason": "Tower status could not be loaded.",
                "normal_import_error": f"{type(normal_error).__name__}: {normal_error}",
                "file_path_error": f"{type(file_error).__name__}: {file_error}",
            }


def _safe_security_command_html(tower_user_id: str = "owner_solice") -> str:
    """
    Returns the standalone Security Command Dashboard HTML.
    Regenerates if the page builder is available, otherwise reads the saved HTML.
    """
    _ensure_project_import_path()

    html_path = _tower_root() / "data" / "security_command_dashboard.html"

    try:
        from tower.security_command_page import save_security_command_dashboard_html
        result = save_security_command_dashboard_html(tower_user_id=tower_user_id)
        saved_path = result.get("path") if isinstance(result, dict) else None
        if saved_path and Path(saved_path).exists():
            return Path(saved_path).read_text(encoding="utf-8")
    except Exception:
        pass

    if html_path.exists():
        return html_path.read_text(encoding="utf-8")

    return """
    <!doctype html>
    <html>
    <head>
      <meta charset="utf-8">
      <title>The Tower - Security Command Dashboard</title>
    </head>
    <body style="background:#070914;color:#f8fafc;font-family:Arial;padding:32px;">
      <h1>The Tower</h1>
      <p>Security Command Dashboard HTML has not been generated yet.</p>
      <p>Run Pack 020 again to regenerate the dashboard file.</p>
    </body>
    </html>
    """


def _tower_entry_html(tower_user_id: str = "owner_solice") -> str:
    return f"""
    <!doctype html>
    <html>
    <head>
      <meta charset="utf-8">
      <title>The Tower - Command Entry</title>
      <style>
        body {{
          margin: 0;
          min-height: 100vh;
          background:
            radial-gradient(circle at 20% 10%, rgba(59,130,246,.16), transparent 28%),
            radial-gradient(circle at 80% 0%, rgba(14,165,233,.12), transparent 32%),
            linear-gradient(135deg, #050711 0%, #0b1020 55%, #111827 100%);
          color: #f8fafc;
          font-family: Arial, Helvetica, sans-serif;
          display: flex;
          align-items: center;
          justify-content: center;
          padding: 28px;
        }}
        .panel {{
          width: min(900px, 92vw);
          border: 1px solid rgba(148,163,184,.24);
          background: rgba(15,23,42,.72);
          box-shadow: 0 24px 80px rgba(0,0,0,.45);
          border-radius: 28px;
          padding: 34px;
        }}
        .kicker {{
          color: #93c5fd;
          letter-spacing: .18em;
          text-transform: uppercase;
          font-size: 12px;
          margin-bottom: 10px;
        }}
        h1 {{
          margin: 0 0 12px;
          font-size: 44px;
          line-height: 1.02;
        }}
        p {{
          color: #cbd5e1;
          font-size: 16px;
          line-height: 1.65;
          max-width: 760px;
        }}
        .actions {{
          display: flex;
          flex-wrap: wrap;
          gap: 14px;
          margin-top: 26px;
        }}
        a {{
          color: #eff6ff;
          text-decoration: none;
          border: 1px solid rgba(147,197,253,.35);
          background: rgba(37,99,235,.18);
          padding: 13px 16px;
          border-radius: 16px;
          font-weight: 700;
        }}
        a.secondary {{
          background: rgba(15,23,42,.45);
        }}
      </style>
    </head>
    <body>
      <main class="panel">
        <div class="kicker">Control Tower Security Command Center</div>
        <h1>The Tower</h1>
        <p>
          Clearance, security review, audit health, inbox pressure, step-up authorization,
          evidence capsules, export controls, and lockdown visibility live here.
        </p>
        <div class="actions">
          <a href="/tower/security-command?tower_user_id={tower_user_id}">Open Security Command</a>
          <a class="secondary" href="/tower/status.json?tower_user_id={tower_user_id}">View Status JSON</a>
        </div>
      </main>
    </body>
    </html>
    """


def register_tower_web_routes(app):
    """
    Registers Tower routes on the Flask app.

    This function is intentionally idempotent:
    - If routes already exist, it does not add duplicates.
    - If the function is called twice, the second call exits cleanly.
    """
    from flask import Response, jsonify, redirect, request

    existing_tower_routes = sorted(
        str(rule.rule)
        for rule in app.url_map.iter_rules()
        if str(rule.rule).startswith("/tower")
    )

    if existing_tower_routes or getattr(app, "_tower_web_routes_registered", False):
        app._tower_web_routes_registered = True
        return {
            "ok": True,
            "status": "already_registered",
            "human_reason": "The Tower web routes already exist on this Flask app.",
            "routes": existing_tower_routes,
        }

    @app.route("/tower", endpoint="tower_command_entry")
    @app.route("/tower/", endpoint="tower_command_entry_slash")
    def tower_command_entry():
        tower_user_id = request.args.get("tower_user_id", "owner_solice")
        return Response(_tower_entry_html(tower_user_id=tower_user_id), mimetype="text/html")

    @app.route("/tower/security-command", endpoint="tower_security_command")
    def tower_security_command():
        tower_user_id = request.args.get("tower_user_id", "owner_solice")
        html = _safe_security_command_html(tower_user_id=tower_user_id)
        return Response(html, mimetype="text/html")

    @app.route("/tower/security-command/regenerate", endpoint="tower_security_command_regenerate")
    def tower_security_command_regenerate():
        tower_user_id = request.args.get("tower_user_id", "owner_solice")
        html = _safe_security_command_html(tower_user_id=tower_user_id)
        return Response(html, mimetype="text/html")

    @app.route("/tower/status.json", endpoint="tower_status_json")
    def tower_status_json():
        payload = _safe_tower_status()
        return jsonify(payload)

    app._tower_web_routes_registered = True

    final_routes = sorted(
        str(rule.rule)
        for rule in app.url_map.iter_rules()
        if str(rule.rule).startswith("/tower")
    )

    return {
        "ok": True,
        "status": "registered",
        "human_reason": "The Tower web routes were registered.",
        "routes": final_routes,
    }
