"""Canonical hosted WSGI entrypoint for Simplee World.

The active application identity is environment-neutral. Historical pre-release
evidence can remain in Git history, but current hosting should use web.runtime:app.
"""

from __future__ import annotations

import os

from web.app import app as app


RUNTIME_ENTRYPOINT = "web.runtime:app"
RUNTIME_CLASS = "canonical_hosted_runtime"

BROKER_SUBMISSION = False
CAPITAL_MOVEMENT = False
MANUAL_LIVE_AUTHORIZED = False
LIVE_AUTO_AUTHORIZED = False


_secret = os.environ.get(
    "SIMPLEE_FLASK_SECRET_KEY",
    "",
).strip()

if _secret:
    app.secret_key = _secret


def canonical_runtime_status() -> dict[str, object]:
    return {
        "entrypoint": RUNTIME_ENTRYPOINT,
        "runtime_class": RUNTIME_CLASS,
        "app_imported": app is not None,
        "flask_secret_override_configured": bool(_secret),
        "broker_submission": BROKER_SUBMISSION,
        "capital_movement": CAPITAL_MOVEMENT,
        "manual_live_authorized": MANUAL_LIVE_AUTHORIZED,
        "live_auto_authorized": LIVE_AUTO_AUTHORIZED,
    }


def _runtime_health_payload():
    return {
        "ok": True,
        "runtime": "simplee-world",
    }


if "/tower/healthz" not in {
    rule.rule
    for rule
    in app.url_map.iter_rules()
}:
    app.add_url_rule(
        "/tower/healthz",
        endpoint="simplee_runtime_healthz",
        view_func=lambda: _runtime_health_payload(),
        methods=["GET"],
    )


class _SimpleeRuntimeHealthMiddleware:
    def __init__(self, wrapped):
        self.wrapped = wrapped

    def __call__(self, environ, start_response):
        path = environ.get(
            "PATH_INFO",
            "",
        )
        method = environ.get(
            "REQUEST_METHOD",
            "GET",
        ).upper()

        if (
            path == "/tower/healthz"
            and method in {"GET", "HEAD"}
        ):
            body = (
                b'{"ok":true,"runtime":"simplee-world"}\n'
            )

            headers = [
                (
                    "Content-Type",
                    "application/json; charset=utf-8",
                ),
                (
                    "Content-Length",
                    str(len(body)),
                ),
                (
                    "Cache-Control",
                    "no-store",
                ),
            ]

            start_response(
                "200 OK",
                headers,
            )

            if method == "HEAD":
                return [b""]

            return [body]

        return self.wrapped(
            environ,
            start_response,
        )


if not getattr(
    app,
    "_simplee_runtime_health_middleware_v1",
    False,
):
    app.wsgi_app = (
        _SimpleeRuntimeHealthMiddleware(
            app.wsgi_app
        )
    )

    app._simplee_runtime_health_middleware_v1 = (
        True
    )
