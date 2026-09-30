"""Exact owner-only Tower route for reviewed official catalyst research."""
from __future__ import annotations

import os

from flask import Blueprint, abort, jsonify, make_response, request

from engine.market_intake.official_catalyst_fingerprint import (
    official_catalyst_fingerprint,
)

PATH = "/ob/research/catalysts.json"


def create_official_catalyst_blueprint(
    *,
    owner_authorize,
    catalyst_service,
    observatory_event_hub=None,
):
    if not callable(owner_authorize) or not callable(
        getattr(catalyst_service, "snapshot", None)
    ):
        raise ValueError("Tower authorization and official source service required")
    if observatory_event_hub is not None and not callable(
        getattr(observatory_event_hub, "observe_digest", None)
    ):
        raise ValueError("Exact Observatory event hub required")

    bp = Blueprint("ob_official_catalyst_radar", __name__)

    @bp.route(PATH, methods=["GET"])
    def official_catalysts():
        if owner_authorize() is not True:
            abort(403)

        if observatory_event_hub is not None:
            from flask import session
            from tower.tower_human_login_ob_launch import SESSION_ID

            old_id = session.get(SESSION_ID)
            if old_id and observatory_event_hub.session_revoked(old_id):
                abort(403)

        if request.args:
            abort(400)

        stream_available = (
            observatory_event_hub is not None
            and os.environ.get("OB_EVENT_WS_ASGI_ENABLED") == "1"
        )

        try:
            packet = catalyst_service.snapshot()
            if observatory_event_hub is not None:
                digest = official_catalyst_fingerprint(packet)
                try:
                    observatory_event_hub.observe_digest(
                        observation_key="official_catalyst_radar:snapshot",
                        digest=digest,
                        event_type="research_context_changed",
                        source="official_catalyst_radar",
                        snapshot_path=PATH,
                    )
                except Exception:
                    # Optional delivery can fail without suppressing the
                    # authoritative protected snapshot.
                    stream_available = False
                packet["event_stream"] = observatory_event_hub.hint(
                    available=stream_available
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
