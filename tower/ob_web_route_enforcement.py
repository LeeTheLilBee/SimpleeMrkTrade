from __future__ import annotations

import re

from flask import abort, redirect, request

from tower.tower_human_login_ob_launch import (
    operational_ob_access_active,
    owner_session_active,
    step_up_active,
)


PROTECTED_EXACT_OB_ROUTES = frozenset(
    {
        "/ob/dashboard",
        "/ob/market-map",
        "/ob/data-desk",
        "/ob/data-desk/public",
        "/ob/research/keyless.json",
        # OBDATA009: exact private, read-only canonical source-status corridor.
        "/ob/engine-feed-snapshot.json",
        "/ob/trade-center",
        "/ob/review-center",
        "/ob/owner-console",
        "/ob/owner-dashboard",
        # OBSIM hosted synthetic owner rehearsal: exact enumerated paths only.
        "/ob/owner-rehearsal",
        "/ob/owner-rehearsal/status.json",
        "/ob/owner-rehearsal/sample.json",
        "/ob/owner-rehearsal/tick.json",
        "/ob/owner-rehearsal/pause.json",
        "/ob/owner-rehearsal/resume.json",
        "/ob/owner-rehearsal/stop.json",
        "/ob/owner-rehearsal/new.json",
        "/ob/owner-rehearsal/evidence.json",
    }
)

PROTECTED_SYMBOL_PREFIX = "/ob/symbol/"

OWNER_ONLY_OB_ROUTES = frozenset(
    {
        "/ob/owner-console",
        "/ob/owner-dashboard",
    }
)


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
        # Match the exact canonical ticker shape; nonempty alone let nested
        # /ob/symbol/XYZ/secret enter the protected-room allowlist.
        symbol = path[len(PROTECTED_SYMBOL_PREFIX):]
        return bool(re.fullmatch(r"[A-Za-z][A-Za-z0-9.-]{0,15}", symbol)
                    and ".." not in symbol)

    return False


def is_owner_only_ob_web_room(path: str) -> bool:
    return normalize_ob_web_path(path) in OWNER_ONLY_OB_ROUTES


def register_ob_protected_route_enforcement(app):
    """
    Attach the real HTTP fail-closed boundary for Observatory rooms.

    Rules:
      - every /ob/* request is private by default
      - unknown/unapproved /ob/* paths return 403
      - approved rooms require an active Tower owner session
      - normal rooms additionally require active Tower owner step-up
      - Owner Console and Owner Dashboard remain owner-session-only rooms
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

        if not is_approved_ob_web_room(path):
            abort(403)

        # Only the canonical feed URL may be read; no mutation or alias.
        if path == "/ob/engine-feed-snapshot.json" and request.method not in {"GET", "HEAD"}:
            abort(405)

        if not owner_session_active():
            return redirect("/tower/login")

        if is_owner_only_ob_web_room(path):
            return None

        if not step_up_active():
            return redirect("/tower/access-home")

        if not operational_ob_access_active():
            return redirect("/tower/launch/observatory")

        return None

    setattr(
        app,
        marker,
        True,
    )

    return app
