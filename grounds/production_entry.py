"""GRD102 — opt-in production WSGI composition; intentionally unavailable today.

This module creates NO public server, endpoint, Render service, user account,
schema or credential. It has no `app` global and never uses developer fixture
verifiers. An operator invoking create_wsgi_application MUST first obtain the
separate owner/security approval and supply a privately provisioned PostgreSQL
DSN and independent high-entropy anti-CSRF secret. A trusted Tower module with
the exact certified receiver factory MUST exist in the authoritative branch.
The current Tower source-only reviewer does not satisfy that requirement.

The future Tower adapter must verify original authenticated session, audience,
issuer, expiry, replay, revoke/logout, active tenant/property/unit/lease and
staff job assignment for EVERY request. It returns a TowerScope only after
verification and never consumes claimed role flags supplied by a browser.
"""
from __future__ import annotations

import importlib
import os
from collections.abc import Callable

from .postgres import PostgresGroundsStore
from .web import GroundsWebApp, GroundsWebConfigurationError


class GroundsProductionUnavailable(RuntimeError):
    """Safe summary: never interpolate DSN, secrets or session material."""


def create_wsgi_application():
    """No implicit development fallback: missing any real source stays closed."""
    if str(os.getenv("TOWER_LOCAL_WALKTHROUGH_MODE","")).strip().lower() in {
        "true","yes","on","1",
    }:
        raise GroundsProductionUnavailable("local Tower walkthrough cannot authorize residents")
    dsn=os.getenv("GROUNDS_PRIVATE_POSTGRES_URL","").strip()
    secret_hex=os.getenv("GROUNDS_CSRF_SECRET_HEX","").strip()
    if not dsn or not secret_hex:
        raise GroundsProductionUnavailable("approved private database and CSRF configuration required")
    try:
        secret=bytes.fromhex(secret_hex)
    except ValueError as exc:
        raise GroundsProductionUnavailable("invalid independent CSRF configuration") from exc
    if len(secret)<32 or len(set(secret))<8:
        raise GroundsProductionUnavailable("high-entropy CSRF configuration required")
    try:
        authority=importlib.import_module("tower.grounds_runtime_receiver")
        factory=getattr(authority,"create_certified_grounds_receiver")
    except (ImportError,AttributeError) as exc:
        raise GroundsProductionUnavailable(
            "the real Tower Grounds receiver is not implemented/certified"
        ) from exc
    if not isinstance(factory,Callable):
        raise GroundsProductionUnavailable("certified Tower receiver factory unavailable")
    try:
        receiver=factory()
    except Exception as exc:
        raise GroundsProductionUnavailable("certified Tower receiver failed initialization") from exc
    if not isinstance(receiver,Callable):
        raise GroundsProductionUnavailable("certified Tower receiver unavailable")
    store=PostgresGroundsStore(dsn)
    try:
        return GroundsWebApp(
            store,tower_receiver=receiver,csrf_secret=secret,local_fixture_only=False,
        )
    except (GroundsWebConfigurationError,Exception) as exc:
        # Generic operator error. Real migration/connection details stay private
        # and should be sent only to an independently approved secure log system.
        raise GroundsProductionUnavailable(
            "private Grounds database or authenticated runtime failed startup preflight"
        ) from exc
