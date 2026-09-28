"""Fail-closed guard for ecosystem product routes that are not yet launched.

Source code or Flask route registration never equals Tower authorization. Apps
listed here may only serve direct product paths after a future Tower launch has
placed an app-specific access receipt in the current authenticated session.

This guard never covers /tower/* integration/receipt endpoints.
"""
from __future__ import annotations

from html import escape

from flask import Flask, jsonify, redirect, request, session

from tower.app_registry import registered_apps
from tower.tower_human_login_ob_launch import (
    ACCESS_HOME_PATH, LOGIN_PATH, owner_session_active, page,
)

APP_PATHS = {
    "grounds": ("/grounds",),
    "buybox": ("/buybox",),
    "vault": ("/vault", "/archive-vault"),
    "clouds": ("/clouds", "/the-clouds"),
}
ACCESS_RECEIPT_KEYS = {
    app_id: f"tower_{app_id}_access_receipt"
    for app_id in APP_PATHS
}


def _matches(path: str, prefixes: tuple[str, ...]) -> bool:
    return any(path == prefix or path.startswith(prefix + "/") for prefix in prefixes)


def _app_registration(app_id: str) -> dict | None:
    for app in registered_apps():
        if app.get("app_id") == app_id:
            return app
    return None


def _jsonish() -> bool:
    return (
        request.path.endswith(".json")
        or "/api/" in request.path
        or request.accept_mimetypes.best == "application/json"
    )


def _blocked(app_id: str, reason: str):
    if _jsonish():
        response = jsonify({
            "allowed": False,
            "app_id": app_id,
            "state": "BLOCKED",
            "reason": reason,
            "tower_front_door_required": True,
            "direct_route_authorized": False,
        })
        response.status_code = 503
        response.headers["Cache-Control"] = "no-store"
        return response

    safe = escape(app_id)
    body = f"""
    <section class="hero">
      <h1>{safe} is not open through Tower yet.</h1>
      <p>The application source exists, but Tower has not verified a current
      launch receipt for this browser session.</p>
    </section>
    <section class="card">
      <div class="notice danger">{escape(reason)}</div>
      <div class="actions">
        <a class="button secondary" href="{ACCESS_HOME_PATH}">Return to Tower</a>
      </div>
    </section>
    """
    response = page(title="Tower application launch blocked", content=body)
    return response, 503, {"Cache-Control": "no-store"}


def ecosystem_direct_route_guard():
    path = request.path
    for app_id, prefixes in APP_PATHS.items():
        if not _matches(path, prefixes):
            continue

        if not owner_session_active():
            return redirect(LOGIN_PATH + "?next=" + ACCESS_HOME_PATH)

        registration = _app_registration(app_id)
        if not registration:
            return _blocked(app_id, "tower_app_not_registered")

        # Even after a future registry promotion, direct product paths remain
        # closed until that app's launch flow writes a server-side receipt.
        receipt = session.get(ACCESS_RECEIPT_KEYS[app_id])
        if not isinstance(receipt, dict):
            return _blocked(app_id, "tower_app_access_receipt_required")
        if (
            receipt.get("app_id") != app_id
            or receipt.get("allowed") is not True
            or receipt.get("owner_session_preserved") is not True
        ):
            session.pop(ACCESS_RECEIPT_KEYS[app_id], None)
            return _blocked(app_id, "tower_app_access_receipt_invalid")

        return None
    return None


def register_ecosystem_direct_route_guard(app: Flask):
    if app.extensions.get("tower_ecosystem_direct_route_guard_v1"):
        return app
    app.before_request(ecosystem_direct_route_guard)
    app.extensions["tower_ecosystem_direct_route_guard_v1"] = {
        "apps": sorted(APP_PATHS),
        "default_deny": True,
        "registry_presence_grants_access": False,
        "browser_claim_grants_access": False,
    }
    return app
