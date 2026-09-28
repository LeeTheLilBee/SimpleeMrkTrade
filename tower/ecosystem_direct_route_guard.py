"""Fail-closed guard for ecosystem product routes that are not yet launched.

Source code or Flask route registration never equals Tower authorization. Apps
listed here may only serve direct product paths after a future Tower launch has
placed an app-specific access receipt in the current authenticated session.

This guard never covers /tower/* integration/receipt endpoints.
"""
from __future__ import annotations

from html import escape
import time

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

ACCESS_RECEIPT_SCHEMA = "tower.ecosystem.access-receipt.v1"
ACCESS_RECEIPT_MAX_SECONDS = 300


def build_ecosystem_access_receipt(app_id: str, *, now_epoch: int | None = None) -> dict:
    """Build a short-lived receipt for a future separately verified launch.

    This helper deliberately does NOT decide whether an app may launch. A future
    app-specific launch corridor may call it only after its own entitlement,
    step-up, publication, provider and receiver checks have succeeded.
    """
    if app_id not in APP_PATHS or not owner_session_active():
        raise ValueError("verified Tower owner session and known app required")
    now = int(time.time()) if now_epoch is None else now_epoch
    if type(now) is not int:
        raise ValueError("valid issuance time required")
    owner_id = session.get("owner_id")
    tower_session_id = session.get("tower_session_id")
    if not isinstance(owner_id, str) or not owner_id:
        raise ValueError("current owner binding required")
    if not isinstance(tower_session_id, str) or not tower_session_id:
        raise ValueError("current Tower session binding required")
    return {
        "schema_version": ACCESS_RECEIPT_SCHEMA,
        "app_id": app_id,
        "allowed": True,
        "owner_id": owner_id,
        "tower_session_id": tower_session_id,
        "issued_at_epoch": now,
        "expires_at_epoch": now + ACCESS_RECEIPT_MAX_SECONDS,
        "owner_session_preserved": True,
        "new_entitlement_granted": False,
        "dangerous_action_unlocked": False,
    }


def _valid_access_receipt(app_id: str, receipt, *, now_epoch: int | None = None) -> bool:
    if not isinstance(receipt, dict):
        return False
    now = int(time.time()) if now_epoch is None else now_epoch
    expected = {
        "schema_version", "app_id", "allowed", "owner_id", "tower_session_id",
        "issued_at_epoch", "expires_at_epoch", "owner_session_preserved",
        "new_entitlement_granted", "dangerous_action_unlocked",
    }
    return bool(
        set(receipt) == expected
        and receipt.get("schema_version") == ACCESS_RECEIPT_SCHEMA
        and receipt.get("app_id") == app_id
        and receipt.get("allowed") is True
        and receipt.get("owner_session_preserved") is True
        and receipt.get("new_entitlement_granted") is False
        and receipt.get("dangerous_action_unlocked") is False
        and receipt.get("owner_id") == session.get("owner_id")
        and receipt.get("tower_session_id") == session.get("tower_session_id")
        and type(receipt.get("issued_at_epoch")) is int
        and type(receipt.get("expires_at_epoch")) is int
        and receipt["issued_at_epoch"] <= now < receipt["expires_at_epoch"]
        and receipt["expires_at_epoch"] - receipt["issued_at_epoch"]
            <= ACCESS_RECEIPT_MAX_SECONDS
    )


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
        if not _valid_access_receipt(app_id, receipt):
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
