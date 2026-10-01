"""GRD219 — opt-in production WSGI composition; still fail-closed for live use.

Tower's development lane now implements the exact adapter module/factory names
this composition imports, and Tower CI cross-tests them against the current
Grounds branch. Source presence is not provider certification. A deployed
revision must actually contain those reviewed Tower modules, and the separately
installed server-owned runtime provider must currently attest identity/session,
revocation and exact property/unit/job grants. A second independent operational
release provider must currently approve the exact environment/revision with
owner, recovery, privacy/housing and operations evidence.

This module creates NO public server, endpoint, Render service, user account,
schema or credential. It has no `app` global and never uses developer fixture
verifiers. An operator invoking create_wsgi_application must also supply the
approved private PostgreSQL DSN and independent high-entropy anti-CSRF secret.

The runtime provider behind Tower must verify the original authenticated
request, audience, issuer, expiry, replay, revoke/logout, active
tenant/property/unit/lease and staff job assignment for EVERY request. Grounds
returns no access merely because Tower adapter source or a launch route exists.
"""
from __future__ import annotations

from importlib import import_module
import os
from collections.abc import Callable

from .postgres import PostgresGroundsStore
from .operational_release import GroundsOperationalReleaseGate
from .web import GroundsWebApp


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
        authority=import_module("tower.grounds_runtime_receiver")
        factory=getattr(authority,"create_certified_grounds_receiver")
        directory_factory=getattr(authority,"create_certified_grounds_staff_directory")
        resolver_factory=getattr(authority,"create_certified_grounds_staff_resolver")
    except (ImportError,AttributeError) as exc:
        raise GroundsProductionUnavailable(
            "required Tower Grounds adapter modules are absent from this deployed revision"
        ) from exc
    if not all(isinstance(item,Callable) for item in (
        factory,directory_factory,resolver_factory,
    )):
        raise GroundsProductionUnavailable("certified Tower factories unavailable")
    try:
        receiver=factory()
        staff_directory=directory_factory()
        staff_resolver=resolver_factory()
    except Exception as exc:
        raise GroundsProductionUnavailable("independent Tower Grounds runtime provider failed certification") from None
    if not all(isinstance(item,Callable) for item in (
        receiver,staff_directory,staff_resolver,
    )):
        raise GroundsProductionUnavailable("certified Tower adapters unavailable")
    try:
        # Release is independent of Tower login and of DB readiness. It is
        # authored by an independently approved Tower-owned certification
        # receiver, never self-reported configuration or this app's checklist.
        release_module=import_module("tower.grounds_operational_release")
        release_factory=getattr(
            release_module,"create_certified_grounds_operational_release_guard",
        )
        if not isinstance(release_factory,Callable):
            raise TypeError("independent release authority unavailable")
        release_authority=release_factory()
        if (not isinstance(release_authority,Callable)
            or not isinstance(getattr(release_authority,"health_check",None),Callable)):
            raise TypeError("independent release authority unavailable")
    except Exception:
        raise GroundsProductionUnavailable(
            "independent Grounds operational release provider is unavailable or uncertified"
        ) from None
    try:
        # Construct inside the sanitized failure boundary as well: adapter
        # preflight may reject malformed private connection configuration.
        store=PostgresGroundsStore(dsn)
        app=GroundsWebApp(
            store,tower_receiver=receiver,staff_directory=staff_directory,
            staff_resolver=staff_resolver,csrf_secret=secret,local_fixture_only=False,
        )
        return GroundsOperationalReleaseGate(app,release_authority)
    except Exception as exc:
        # Generic operator error. Real migration/connection details stay private
        # and should be sent only to an independently approved secure log system.
        raise GroundsProductionUnavailable(
            "private Grounds database or authenticated runtime failed startup preflight"
        ) from None
