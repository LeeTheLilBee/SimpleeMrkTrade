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


# TOWER_HOSTED_RUNTIME_IDENTITY_TWR081_085
#
# Safe hosted-runtime identity contract.
#
# This intentionally exposes only:
#
# - managed WSGI entrypoint name
# - source revision fingerprint
# - revision source
# - booleans for critical route presence
#
# It does NOT expose environment contents, secrets, session data,
# filesystem paths, broker state, or capital state.

import os as _runtime_os
import subprocess as _runtime_subprocess
from pathlib import Path as _RuntimePath


_RUNTIME_CRITICAL_ROUTES = {
    "tower_login": "/tower/login",
    "tower_owner_dashboard": "/tower/owner-dashboard",
    "tower_security_map": "/tower/security-map",
    "archive_vault_acceptance_records": (
        "/tower/archive-vault/acceptance-records.json"
    ),
    "archive_vault_intake": (
        "/tower/archive-vault/intake/<handoff_id>"
    ),
    "person_archive_vault_queue": (
        "/tower/owner-dashboard/person/"
        "<person_id>/event/<event_id>/archive-vault-queue"
    ),
    "ob_dashboard": "/ob/dashboard",
    "ob_market_map": "/ob/market-map",
    "ob_trade_center": "/ob/trade-center",
    "ob_review_center": "/ob/review-center",
    "ob_owner_console": "/ob/owner-console",
}


def _simplee_runtime_revision() -> tuple[str, str]:
    """
    Resolve a safe revision fingerprint.

    Managed-host environment identifiers are preferred.
    A local git fallback is used only when available.
    """

    candidates = (
        "RENDER_GIT_COMMIT",
        "GIT_COMMIT",
        "COMMIT_SHA",
        "SOURCE_VERSION",
    )

    for key in candidates:
        value = str(
            _runtime_os.environ.get(
                key,
                "",
            )
            or ""
        ).strip()

        if value:
            return value, "environment:" + key


    try:
        project_root = (
            _RuntimePath(__file__)
            .resolve()
            .parents[1]
        )

        proc = _runtime_subprocess.run(
            [
                "git",
                "rev-parse",
                "HEAD",
            ],
            cwd=project_root,
            text=True,
            stdout=_runtime_subprocess.PIPE,
            stderr=_runtime_subprocess.PIPE,
            timeout=2,
            check=False,
        )

        value = (
            proc.stdout
            or ""
        ).strip()

        if (
            proc.returncode == 0
            and value
        ):
            return value, "git:HEAD"

    except Exception:
        pass


    return "unknown", "unavailable"


def _simplee_runtime_route_manifest() -> dict[str, bool]:
    rules = {
        rule.rule
        for rule
        in app.url_map.iter_rules()
    }

    return {
        name: path in rules
        for name, path
        in _RUNTIME_CRITICAL_ROUTES.items()
    }


def managed_staging_runtime_manifest() -> dict[str, object]:
    revision, revision_source = (
        _simplee_runtime_revision()
    )

    route_manifest = (
        _simplee_runtime_route_manifest()
    )

    return {
        "status": "tower_managed_staging_runtime_manifest_ready",
        "entrypoint": STAGING_ENTRYPOINT,
        "revision": revision,
        "revision_source": revision_source,
        "critical_routes": route_manifest,
        "critical_routes_present": all(
            route_manifest.values()
        ),
        "production_deployment": PRODUCTION_DEPLOYMENT,
        "broker_submission": BROKER_SUBMISSION,
        "capital_movement": CAPITAL_MOVEMENT,
        "manual_live_authorized": MANUAL_LIVE_AUTHORIZED,
        "live_auto_authorized": LIVE_AUTO_AUTHORIZED,
        "staging_ready": STAGING_READY,
    }


def _simplee_runtime_manifest_view():
    payload = (
        managed_staging_runtime_manifest()
    )

    return payload, 200


if (
    "simplee_managed_staging_runtime_manifest"
    not in app.view_functions
):
    app.add_url_rule(
        "/tower/runtime-manifest.json",
        endpoint=(
            "simplee_managed_staging_runtime_manifest"
        ),
        view_func=(
            _simplee_runtime_manifest_view
        ),
        methods=[
            "GET",
        ],
    )


class _SimpleeRuntimeIdentityHeadersMiddleware:

    def __init__(
        self,
        wrapped,
    ):
        self.wrapped = wrapped


    def __call__(
        self,
        environ,
        start_response,
    ):

        revision, revision_source = (
            _simplee_runtime_revision()
        )


        def _start_response(
            status,
            headers,
            exc_info=None,
        ):
            headers = list(
                headers
            )

            headers.append(
                (
                    "X-Simplee-Entrypoint",
                    STAGING_ENTRYPOINT,
                )
            )

            headers.append(
                (
                    "X-Simplee-Revision",
                    revision,
                )
            )

            headers.append(
                (
                    "X-Simplee-Revision-Source",
                    revision_source,
                )
            )

            return start_response(
                status,
                headers,
                exc_info,
            )


        return self.wrapped(
            environ,
            _start_response,
        )




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


# TOWER_HOSTED_RUNTIME_IDENTITY_OUTERMOST_TWR081_085
#
# Install runtime identity headers LAST so this middleware sits outside the
# managed-staging health middleware and sees every response, including the
# /tower/healthz short-circuit path.
if not getattr(
    app,
    "_simplee_runtime_identity_headers_twr081_085",
    False,
):
    app.wsgi_app = (
        _SimpleeRuntimeIdentityHeadersMiddleware(
            app.wsgi_app
        )
    )

    app._simplee_runtime_identity_headers_twr081_085 = True
