from __future__ import annotations

from flask import abort, redirect, request

from tower.tower_human_login_ob_launch import (
    owner_session_active,
    step_up_active,
)


PROTECTED_EXACT_OB_ROUTES = frozenset(
    {
        "/ob/dashboard",
        "/ob/market-map",
        "/ob/trade-center",
        "/ob/review-center",
        "/ob/owner-console",
    }
)

PROTECTED_SYMBOL_PREFIX = "/ob/symbol/"
OWNER_ONLY_OB_ROUTE = "/ob/owner-console"


def normalize_ob_web_path(path: str) -> str:
    value = str(path or "/").strip()

    if not value.startswith("/"):
        value = "/" + value

    if len(value) > 1:
        value = value.rstrip("/")

    return value


def is_approved_ob_web_room(path: str) -> bool:
    path = normalize_ob_web_path(path)

    if path in PROTECTED_EXACT_OB_ROUTES:
        return True

    if path.startswith(PROTECTED_SYMBOL_PREFIX):
        symbol = path[len(PROTECTED_SYMBOL_PREFIX):].strip()
        return bool(symbol)

    return False


def register_ob_protected_route_enforcement(app):
    """
    Attach the real HTTP fail-closed boundary for Observatory rooms.

    This protects the actual Flask request before an OB room handler can render.

    Rules:
      - every /ob/* request is private by default
      - unknown/unapproved /ob/* paths return 403
      - approved rooms require an active Tower owner session
      - normal rooms additionally require active Tower owner step-up
      - Owner Console remains owner-session-only per native-launch doctrine
    """

    marker = "_tower_ob_web_failclosed_registered"

    if getattr(app, marker, False):
        return app

    @app.before_request
    def _tower_ob_web_failclosed_gate():
        path = normalize_ob_web_path(
            request.path
        )

        if not path.startswith("/ob/"):
            return None

        # Default deny first. A valid session does not make an unknown
        # Observatory path permissible.
        if not is_approved_ob_web_room(path):
            abort(403)

        # No anonymous direct room access.
        if not owner_session_active():
            return redirect("/tower/login")

        # Owner Console is already defined by Tower native-launch doctrine
        # as owner-only rather than ordinary room step-up access.
        if path == OWNER_ONLY_OB_ROUTE:
            return None

        # Normal Observatory rooms require the owner session plus the
        # Tower step-up that precedes the protected native handoff.
        if not step_up_active():
            return redirect("/tower/access-home")

        return None

    setattr(
        app,
        marker,
        True,
    )

    return app
