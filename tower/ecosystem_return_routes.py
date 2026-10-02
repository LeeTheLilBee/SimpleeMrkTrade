"""Reciprocal product -> Tower owner return routes.

These routes preserve an already-authenticated owner session and record only a
navigation receipt. They do not create app access, entitlement, step-up,
financial authority, storage authority, tenant authority, or execution rights.
"""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from html import escape

from flask import Flask, jsonify, redirect, request, session

from tower.tower_human_login_ob_launch import ACCESS_HOME_PATH, require_human_owner

RETURN_APPS = {
    "teller": {
        "path": "/tower/return/teller",
        "rooms": frozenset({"Owner Money Workspace", "Payroll", "Payments", "Records"}),
    },
    "grounds": {
        "path": "/tower/return/grounds",
        "rooms": frozenset({"My Home", "Daily Grounds", "Property Health", "Owner Portfolio"}),
    },
    "buybox": {
        "path": "/tower/return/buybox",
        "rooms": frozenset({"Browse", "Opportunity", "Deal Room", "Decision Desk", "Intelligence Studio"}),
    },
    "vault": {
        "path": "/tower/return/vault",
        "rooms": frozenset({"Vault Home", "Command Center", "Search Tracker", "Receipt Control"}),
    },
    "clouds": {
        "path": "/tower/return/clouds",
        "rooms": frozenset({"Clouds Home", "Owner Focus", "App Registry", "Today"}),
    },
}


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _hash(payload: dict) -> str:
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def record_ecosystem_return(app_id: str, last_room: str | None) -> dict:
    spec = RETURN_APPS[app_id]
    safe_room = last_room if isinstance(last_room, str) and last_room in spec["rooms"] else "unknown"
    receipt = {
        "schema_version": "tower.ecosystem.return.v1",
        "app_id": app_id,
        "source": app_id,
        "destination": ACCESS_HOME_PATH,
        "last_room": safe_room,
        "owner_id": session.get("owner_id"),
        "role": session.get("tower_role"),
        "tower_session_id": session.get("tower_session_id"),
        "owner_session_preserved": bool(
            session.get("tower_authenticated") is True
            and session.get("tower_role") == "owner"
            and session.get("owner_id")
        ),
        "returned_at": _now_iso(),
        "new_entitlement_granted": False,
        "dangerous_action_unlocked": False,
        "broker_submission": False,
        "capital_movement": False,
        "payroll_execution": False,
        "tenant_access_granted": False,
        "vault_storage_access_granted": False,
        "closing_authorized": False,
    }
    receipt["receipt_hash"] = _hash(receipt)
    session[f"tower_{app_id}_return_receipt"] = receipt
    return dict(receipt)


def _return_view(app_id: str):
    receipt = record_ecosystem_return(app_id, request.args.get("last_room"))
    if request.path.endswith(".json"):
        response = jsonify({
            "allowed": True,
            "return_receipt": receipt,
            "owner_session_preserved": receipt["owner_session_preserved"],
            "new_entitlement_granted": False,
            "dangerous_action_unlocked": False,
        })
        response.headers["Cache-Control"] = "no-store"
        return response
    return redirect(ACCESS_HOME_PATH)


def register_ecosystem_return_routes(app: Flask):
    # An app may already own a separately reviewed reciprocal Tower return
    # (Clouds does). Never register a competing rule for the same URL.
    existing_paths = {rule.rule for rule in app.url_map.iter_rules()}
    for app_id, spec in RETURN_APPS.items():
        endpoint = f"tower_return_{app_id}_v1"
        json_endpoint = f"tower_return_{app_id}_json_v1"
        if spec["path"] not in existing_paths and endpoint not in app.view_functions:
            app.add_url_rule(
                spec["path"],
                endpoint=endpoint,
                view_func=require_human_owner(lambda app_id=app_id: _return_view(app_id)),
                methods=["GET"],
            )
            existing_paths.add(spec["path"])
        json_path = spec["path"] + ".json"
        if json_path not in existing_paths and json_endpoint not in app.view_functions:
            app.add_url_rule(
                json_path,
                endpoint=json_endpoint,
                view_func=require_human_owner(lambda app_id=app_id: _return_view(app_id)),
                methods=["GET"],
            )
            existing_paths.add(json_path)
    return app
