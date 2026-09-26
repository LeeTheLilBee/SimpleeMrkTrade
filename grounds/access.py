"""GRD006 — service-side scope from an externally verified Tower handoff.

No signature protocol or Tower receiver is implemented here. The caller must
supply a certified verifier that authenticates the full token (including
signature, issuer, audience, session, replay, revocation and role grants).
This local envelope is an internal normalized form, NOT an existing Tower wire
contract. Do not expose the verifier as a user-controllable callback.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from time import time
from typing import Callable, Mapping

from .contract import ROOMS

_ISSUED = object()


class AccessDenied(PermissionError):
    """Fail closed without leaking another property's existence."""


def _refs(value, label: str) -> frozenset[str]:
    if not isinstance(value, list) or len(value) > 500:
        raise AccessDenied("invalid Tower scope")
    if any(not isinstance(x, str) or not x.strip() or len(x) > 128 for x in value):
        raise AccessDenied("invalid Tower scope")
    if len(set(value)) != len(value):
        raise AccessDenied("invalid Tower scope")
    return frozenset(value)


@dataclass(frozen=True)
class TowerScope:
    subject_ref: str
    role: str
    property_refs: frozenset[str]
    unit_refs: frozenset[str]
    assigned_work_refs: frozenset[str]
    expires_at: int
    session_ref: str
    _proof: object = field(repr=False, compare=False)

    def __post_init__(self):
        if self._proof is not _ISSUED:
            raise AccessDenied("scope must be verified by Tower adapter")

    def assert_active(self) -> None:
        if self.expires_at <= int(time()):
            raise AccessDenied("Tower handoff expired")

    def require_role(self, *roles: str) -> None:
        self.assert_active()
        if self.role not in roles:
            raise AccessDenied("role not authorized")

    def require_property(self, property_ref: str) -> None:
        self.assert_active()
        if property_ref not in self.property_refs:
            raise AccessDenied("property access denied")

    def require_unit(self, property_ref: str, unit_ref: str) -> None:
        self.require_property(property_ref)
        if unit_ref not in self.unit_refs:
            raise AccessDenied("unit access denied")


def verified_scope(ticket: object, *, verifier: Callable[[object], Mapping], now: int | None = None) -> TowerScope:
    """Normalize a *previously authenticated* Tower handoff; deny missing verifier.

    A local unit test may use an explicit fixture verifier. This is not a
    general-purpose login/session API, and creates no endpoint or entitlement.
    """
    if not callable(verifier):
        raise AccessDenied("certified Tower verifier required")
    try:
        claims = verifier(ticket)
    except Exception as exc:
        raise AccessDenied("Tower handoff rejected") from exc
    if not isinstance(claims, Mapping):
        raise AccessDenied("Tower handoff rejected")
    clock = int(time()) if now is None else now
    if type(clock) is not int:
        raise AccessDenied("invalid verification clock")
    if claims.get("issuer") != "tower" or claims.get("audience") != "grounds":
        raise AccessDenied("wrong handoff destination")
    role = claims.get("role")
    subject = claims.get("subject_ref")
    session = claims.get("session_ref")
    issued = claims.get("issued_at")
    expiry = claims.get("expires_at")
    if role not in ROOMS or not isinstance(subject, str) or not subject.strip() or len(subject) > 128:
        raise AccessDenied("invalid identity")
    if not isinstance(session, str) or not session.strip() or len(session) > 128:
        raise AccessDenied("missing authenticated session")
    if type(issued) is not int or type(expiry) is not int or issued > clock or expiry <= clock or expiry - issued > 300:
        raise AccessDenied("expired or invalid handoff")
    properties = _refs(claims.get("property_refs"), "properties")
    units = _refs(claims.get("unit_refs"), "units")
    work = _refs(claims.get("assigned_work_refs"), "assignments")
    if not properties:
        raise AccessDenied("missing property grants")
    if role == "resident" and not units:
        raise AccessDenied("missing resident unit grant")
    return TowerScope(subject, role, properties, units, work, expiry, session, _ISSUED)
