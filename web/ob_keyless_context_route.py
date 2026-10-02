"""Exact Tower-protected GET of non-price, keyless public research context.

All provider traffic occurs on the server only after authoritative owner,
step-up and OB admission. Unknown methods/URLs remain default denied by Tower.
"""
from __future__ import annotations

from flask import Blueprint, abort, jsonify, make_response, request

PATH = "/ob/research/keyless.json"


def create_keyless_context_blueprint(*, owner_authorize, context_service):
    if not callable(owner_authorize) or not callable(getattr(context_service, "snapshot", None)):
        raise ValueError("Independent Tower owner authorization and source service required")
    bp = Blueprint("ob_keyless_public_context", __name__)

    @bp.route(PATH, methods=["GET"])
    def keyless_owner_context():
        if owner_authorize() is not True:
            abort(403)
        if set(request.args) - {"symbol"} or len(request.args.getlist("symbol")) > 1:
            abort(400)
        symbol = request.args.get("symbol")
        if symbol == "":
            abort(400)
        try:
            payload = context_service.snapshot(symbol=symbol)
        except ValueError:
            abort(400)
        except Exception:
            # Provider errors and source-specific access values never flow out.
            abort(503)
        response = make_response(jsonify(payload))
        response.headers["Cache-Control"] = "no-store, private"
        response.headers["Pragma"] = "no-cache"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "same-origin"
        response.headers["Content-Security-Policy"] = "default-src 'none'"
        return response

    return bp
