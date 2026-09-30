"""Exact owner-only Tower route for reviewed official catalyst research."""
from __future__ import annotations

import os

from flask import Blueprint, abort, jsonify, make_response, request

PATH = "/ob/research/catalysts.json"


def create_official_catalyst_blueprint(
    *,
    owner_authorize,
    catalyst_service,
    event_hub=None,
    market_event_hub=None,
):
    if not callable(owner_authorize) or not callable(getattr(catalyst_service, "snapshot", None)):
        raise ValueError("Tower authorization and official source service required")
    if event_hub is not None and not callable(getattr(event_hub, "observe", None)):
        raise ValueError("Exact bounded source notification hub required")
    if market_event_hub is not None and not callable(
        getattr(market_event_hub, "publish_invalidation", None)
    ):
        raise ValueError("Exact normalized market notification hub required")
    bp = Blueprint("ob_official_catalyst_radar", __name__)

    @bp.route(PATH, methods=["GET"])
    def official_catalysts():
        if owner_authorize() is not True:
            abort(403)
        # A signed cookie copied before Tower logout must not keep reading
        # this research corridor after that process revoked its session id.
        if event_hub is not None:
            from flask import session
            from tower.tower_human_login_ob_launch import SESSION_ID
            old_id = session.get(SESSION_ID)
            if old_id and event_hub.session_revoked(old_id):
                abort(403)
        if request.args:
            abort(400)

        market_stream_available = (
            market_event_hub is not None
            and os.environ.get("OB_MARKET_WS_ASGI_ENABLED") == "1"
        )
        try:
            packet = catalyst_service.snapshot()
            changed = False
            if event_hub is not None:
                before = event_hub.hint()["cursor"]
                after = event_hub.observe(packet)
                changed = after["cursor"] != before
                packet["stream"] = event_hub.hint(
                    available=os.environ.get("OB_CATALYST_WS_ASGI_ENABLED") == "1"
                )
            if market_event_hub is not None and changed:
                try:
                    market_event_hub.publish_invalidation(
                        event_type="research_context_changed",
                        source="official_catalyst_radar",
                        snapshot_path=PATH,
                    )
                except Exception:
                    # The authoritative protected snapshot remains usable even
                    # if the optional delivery bus cannot announce its change.
                    market_stream_available = False
            if market_event_hub is not None:
                packet["market_stream"] = market_event_hub.hint(
                    available=market_stream_available
                )
        except Exception:
            abort(503)

        response = make_response(jsonify(packet))
        response.headers["Cache-Control"] = "private, no-store"
        response.headers["Pragma"] = "no-cache"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "same-origin"
        response.headers["Content-Security-Policy"] = "default-src 'none'"
        return response

    return bp
