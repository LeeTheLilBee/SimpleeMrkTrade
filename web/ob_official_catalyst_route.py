"""Exact owner-only Tower route for reviewed official catalyst research."""
from __future__ import annotations

from flask import Blueprint, abort, jsonify, make_response, request

PATH = "/ob/research/catalysts.json"


def create_official_catalyst_blueprint(*, owner_authorize, catalyst_service):
    if not callable(owner_authorize) or not callable(getattr(catalyst_service, "snapshot", None)):
        raise ValueError("Tower authorization and official source service required")
    bp = Blueprint("ob_official_catalyst_radar", __name__)

    @bp.route(PATH, methods=["GET"])
    def official_catalysts():
        if owner_authorize() is not True:
            abort(403)
        if request.args:
            abort(400)
        try:
            packet = catalyst_service.snapshot()
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
