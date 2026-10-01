"""Owner-only lifecycle proof for Observatory internal events.

This endpoint exposes status metadata only. It never serializes provider values,
credentials, positions, orders, capital instructions, or broker authority.
"""
from __future__ import annotations

from flask import Blueprint, abort, jsonify, make_response

PATH = "/ob/data-desk/event-traces.json"


def create_event_trace_blueprint(*, owner_authorize, event_hub):
    if not callable(owner_authorize) or event_hub is None:
        raise ValueError("Tower owner authorization and event hub required")

    bp = Blueprint("ob_event_trace", __name__)

    @bp.route(PATH, methods=["GET"])
    def event_traces():
        if owner_authorize() is not True:
            abort(403)
        try:
            payload = event_hub.trace_snapshot(limit=24)
        except Exception:
            abort(503)

        response = make_response(jsonify(payload))
        response.headers["Cache-Control"] = "private, no-store"
        response.headers["Pragma"] = "no-cache"
        response.headers["Vary"] = "Cookie"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Content-Security-Policy"] = "default-src 'none'"
        response.headers["X-Content-Type-Options"] = "nosniff"
        return response

    return bp
