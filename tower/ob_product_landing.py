"""Verify product rendering without granting access or changing Tower guards."""
from __future__ import annotations

from flask import request, make_response

PRODUCT_PATH = "/ob/dashboard"
PRODUCT_ENDPOINT = "ob_dashboard_v16"
PRODUCT_MARKERS = (
    'data-ob-room="dashboard"',
    'data-ob-surface="user-dashboard"',
    'data-ob-dashboard-role="normal"',
    'id="obArrivalRoot"',
    'id="ob-app"',
    '/static/ob/ob_dashboard.js',
    '/static/ob/ob_checkin_entry.js',
)
PROOF_MARKERS = (
    'towerObRealSurfaceGuide',
    'towerObGuidedRoomAction',
    'Observatory protected run-through',
    'towerObWalkthroughEntry',
    'ob_mission_accounts.js',
    'ob_room_data_polish.js',
    'ob_account_experience.js',
    'ob_dashboard_simplification_obux.js',
)


def register_ob_product_landing(app):
    """Require one real dashboard and reject later response substitutions."""
    if app.extensions.get("tower_ob_product_landing"):
        return app
    rules = [r for r in app.url_map.iter_rules() if r.rule == PRODUCT_PATH]
    if len(rules) != 1 or rules[0].endpoint != PRODUCT_ENDPOINT:
        raise RuntimeError("Tower requires the canonical Observatory dashboard route")
    view = app.view_functions.get(PRODUCT_ENDPOINT)
    if not callable(view) or view.__name__ != PRODUCT_ENDPOINT:
        raise RuntimeError("Canonical Observatory dashboard renderer unavailable")
    source, _, _ = app.jinja_loader.get_source(app.jinja_env, "dashboard.html")
    if not all(marker in source for marker in (
        'data-ob-room="dashboard"',
        'data-ob-surface="user-dashboard"',
        'id="obArrivalRoot"',
        'ob_checkin_entry.js',
    )) or any(marker in source for marker in PROOF_MARKERS):
        raise RuntimeError("Canonical Observatory dashboard template unavailable")

    def verify_product_response(response):
        if request.path != PRODUCT_PATH:
            return response
        # Preserve every security denial, login redirect, and failed request.
        if response.status_code == 200:
            body = response.get_data(as_text=True)
            if (response.mimetype != "text/html"
                    or not all(marker in body for marker in PRODUCT_MARKERS)
                    or any(marker in body for marker in PROOF_MARKERS)):
                response = make_response(
                    '<!doctype html><title>Observatory unavailable</title>'
                    '<h1>The Observatory could not open</h1>'
                    '<p><a href="/tower/access-home">Return to Tower</a></p>', 503)
            else:
                response.headers["X-OB-Product-Surface"] = "dashboard"
        response.headers["Cache-Control"] = "no-store"
        return response

    # Flask runs application callbacks in reverse registration order.
    # Insert first to validate the final response after all existing callbacks.
    app.after_request_funcs.setdefault(None, []).insert(0, verify_product_response)
    app.extensions["tower_ob_product_landing"] = True
    return app
