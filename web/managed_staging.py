"""
Managed staging WSGI entrypoint for Render.

This module intentionally imports the canonical Flask app from web.app.
It exists so managed hosts configured for web.managed_staging:app can
boot the same Tower-fronted application without duplicating app logic.

Safety:
- no production deployment authorization
- no broker submission
- no capital movement
- no Manual Live authorization
- no Live Auto authorization
- no STAGING_READY change
"""

from __future__ import annotations

from web.app import app as app


STAGING_ENTRYPOINT = "web.managed_staging:app"
PRODUCTION_DEPLOYMENT = False
BROKER_SUBMISSION = False
CAPITAL_MOVEMENT = False
MANUAL_LIVE_AUTHORIZED = False
LIVE_AUTO_AUTHORIZED = False
STAGING_READY = False


def managed_staging_status() -> dict[str, object]:
    """Return a tiny import-safe status contract for tests and deploy checks."""
    return {
        "entrypoint": STAGING_ENTRYPOINT,
        "app_imported": app is not None,
        "production_deployment": PRODUCTION_DEPLOYMENT,
        "broker_submission": BROKER_SUBMISSION,
        "capital_movement": CAPITAL_MOVEMENT,
        "manual_live_authorized": MANUAL_LIVE_AUTHORIZED,
        "live_auto_authorized": LIVE_AUTO_AUTHORIZED,
        "staging_ready": STAGING_READY,
    }


# SIMPLEE_MANAGED_STAGING_HEALTH_ENDPOINT_V1
# Minimal exact-path Render staging liveness endpoint.
def _simplee_managed_staging_health_view():
    return {"ok": True}, 200


if "simplee_managed_staging_healthz" not in app.view_functions:
    app.add_url_rule(
        "/tower/healthz",
        endpoint="simplee_managed_staging_healthz",
        view_func=_simplee_managed_staging_health_view,
        methods=["GET"],
    )


class _SimpleeManagedStagingHealthMiddleware:
    def __init__(self, wrapped):
        self.wrapped = wrapped

    def __call__(self, environ, start_response):
        path = environ.get("PATH_INFO", "")
        method = environ.get("REQUEST_METHOD", "GET").upper()

        if path == "/tower/healthz" and method in {"GET", "HEAD"}:
            body = b'{"ok":true}\n'
            headers = [
                ("Content-Type", "application/json; charset=utf-8"),
                ("Content-Length", str(len(body))),
                ("Cache-Control", "no-store"),
            ]
            start_response("200 OK", headers)

            if method == "HEAD":
                return [b""]

            return [body]

        return self.wrapped(environ, start_response)


if not getattr(app, "_simplee_health_middleware_v1", False):
    app.wsgi_app = _SimpleeManagedStagingHealthMiddleware(app.wsgi_app)
    app._simplee_health_middleware_v1 = True
