"""Fail-closed same-origin mount for The Grounds inside hosted Tower.

The Tower launch gate requires an actual /grounds runtime. This adapter never
creates one from source presence or an env Boolean alone. Registration occurs
only when the operator explicitly opts in AND Grounds' own production factory
successfully initializes its private PostgreSQL store, certified Tower runtime
receiver/staff adapters, independent operational release guard and CSRF secret.

The mounted child receives the original /grounds PATH_INFO unchanged because
Grounds' WSGI router owns that prefix. The generic Tower direct-route guard is
registered separately by hosted_tower and remains authoritative for the initial
owner crossing. No resident/staff Tower doorway is created here.
"""
from __future__ import annotations

from importlib import import_module
import os

from flask import Flask, request
from werkzeug.wrappers import Response as WerkzeugResponse

ENABLE_ENV = "TOWER_GROUNDS_SAME_ORIGIN_MOUNT"
EXTENSION_KEY = "tower_grounds_same_origin_mount_v1"
ROOT_PATH = "/grounds"
ENDPOINT_ROOT = "tower_mounted_grounds_root"
ENDPOINT_CHILD = "tower_mounted_grounds_child"


def _enabled() -> bool:
    return str(os.getenv(ENABLE_ENV, "") or "").strip() == "1"


def _status(app: Flask, *, configured: bool, mounted: bool, reason_code: str) -> Flask:
    app.extensions[EXTENSION_KEY] = {
        "configured": configured,
        "mounted": mounted,
        "same_origin": True,
        "root_path": ROOT_PATH if mounted else None,
        "reason_code": reason_code,
        "owner_crossing_only": True,
        "resident_staff_launch_created": False,
        "new_entitlement_granted": False,
        "payment_execution_authorized": False,
        "capital_movement_authorized": False,
        "legal_entry_authorized": False,
    }
    return app


def register_configured_grounds_same_origin_runtime(app: Flask) -> Flask:
    """Mount the real Grounds production WSGI app only after all its own gates pass.

    Failure is intentionally non-fatal to Tower startup: Tower remains usable
    while /grounds simply stays unregistered and the owner launch preflight
    reports GROUNDS_SAME_ORIGIN_RUNTIME_NOT_MOUNTED.
    """
    if not isinstance(app, Flask):
        raise TypeError("Flask application required")
    if ENDPOINT_ROOT in app.view_functions or ENDPOINT_CHILD in app.view_functions:
        return app
    if not _enabled():
        return _status(
            app, configured=False, mounted=False,
            reason_code="GROUNDS_SAME_ORIGIN_MOUNT_NOT_CONFIGURED",
        )

    try:
        production = import_module("grounds.production_entry")
        factory = getattr(production, "create_wsgi_application")
        if not callable(factory):
            raise TypeError("Grounds production factory unavailable")
    except Exception:
        return _status(
            app, configured=True, mounted=False,
            reason_code="GROUNDS_PRODUCTION_FACTORY_UNAVAILABLE",
        )

    try:
        grounds_app = factory()
    except Exception:
        return _status(
            app, configured=True, mounted=False,
            reason_code="GROUNDS_PRODUCTION_PREFLIGHT_BLOCKED",
        )
    if not callable(grounds_app):
        return _status(
            app, configured=True, mounted=False,
            reason_code="GROUNDS_PRODUCTION_RUNTIME_INVALID",
        )

    def dispatch_grounds(**_kwargs):
        # Response.from_app uses the current request environ and preserves the
        # exact /grounds prefix expected by Grounds' own router.
        return WerkzeugResponse.from_app(grounds_app, request.environ)

    app.add_url_rule(
        ROOT_PATH,
        endpoint=ENDPOINT_ROOT,
        view_func=dispatch_grounds,
        methods=["GET", "POST"],
    )
    app.add_url_rule(
        ROOT_PATH + "/<path:grounds_path>",
        endpoint=ENDPOINT_CHILD,
        view_func=dispatch_grounds,
        methods=["GET", "POST"],
    )
    return _status(
        app, configured=True, mounted=True,
        reason_code="GROUNDS_SAME_ORIGIN_RUNTIME_MOUNTED",
    )
