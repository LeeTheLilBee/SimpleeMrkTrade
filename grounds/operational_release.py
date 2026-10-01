"""GRD136 — independent, fail-closed operational release wrapper for future hosting.

This is NOT a certification verifier, owner approval or live route. It consumes
a trusted server-created authority on every protected request, distinctly from
Tower's per-user identity receiver. The future authority must independently
validate current issuer-backed owner acceptance, provider/on-call readiness,
private recovery, legal/privacy approval and revocation. No env boolean, HTTP
header, uploaded checklist or fixture verifier may create that authority.
"""
from __future__ import annotations

from collections.abc import Callable


_HEADERS=(
    ("Content-Type","application/json; charset=utf-8"),
    ("Cache-Control","no-store, private, max-age=0"),
    ("Pragma","no-cache"),
    ("X-Content-Type-Options","nosniff"),
    ("X-Frame-Options","DENY"),
    ("Referrer-Policy","no-referrer"),
)


class GroundsOperationalReleaseUnavailable(ValueError):
    pass


class GroundsOperationalReleaseGate:
    """Second gate: infrastructure readiness is never tenant release approval."""

    def __init__(self,app:Callable,authority:Callable):
        if not callable(app) or not callable(authority) or not callable(
            getattr(authority,"health_check",None)
        ):
            raise GroundsOperationalReleaseUnavailable(
                "independent certified release authority and health check required"
            )
        self._app=app
        self._authority=authority

    @staticmethod
    def _closed(start_response,*,readiness:bool=False):
        payload=b'{"ready":false}' if readiness else b'{"error":"service_unavailable"}'
        start_response(
            "503 Service Unavailable",
            list(_HEADERS)+[("Content-Length",str(len(payload)))],
        )
        return [payload]

    def __call__(self,environ,start_response):
        path=environ.get("PATH_INFO","")
        method=environ.get("REQUEST_METHOD","")
        # Liveness is metadata only. It is NOT authenticated product access or
        # authority to serve tenants. The underlying app owns this exact route.
        if (method,path)==("GET","/grounds/health/live"):
            return self._app(environ,start_response)
        try:
            healthy=self._authority.health_check() is True
        except Exception:
            healthy=False
        if not healthy:
            return self._closed(
                start_response,readiness=(method,path)==("GET","/grounds/health/ready"),
            )
        if (method,path)==("GET","/grounds/health/ready"):
            # Both independent operational authority and underlying private DB
            # plus certified Tower receiver health must pass.
            return self._app(environ,start_response)
        try:
            admitted=self._authority(environ) is True
        except Exception:
            admitted=False
        if not admitted:
            return self._closed(start_response)
        # Identity/lease/staff/CSRF/resource grants remain the WSGI app's own
        # mandatory independently verified checks on each admitted request.
        return self._app(environ,start_response)
