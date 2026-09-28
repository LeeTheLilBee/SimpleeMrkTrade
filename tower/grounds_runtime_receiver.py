"""Certified Tower -> Grounds runtime adapter boundary.

This module intentionally contains no resident identities, property grants, secrets,
provider booleans or fallback fixture authority. It only composes a separately
installed server-owned provider with Grounds' own TowerScope normalizer.

A provider is trusted only because it is reviewed/installed server code. Browser
headers cannot select it, and env flags alone cannot manufacture an identity.
"""
from __future__ import annotations

from importlib import import_module
import os
import re
import time
from collections.abc import Callable, Mapping
from typing import Any

PROVIDER_ENV = "TOWER_GROUNDS_RUNTIME_PROVIDER_MODULE"
ATTESTATION_SCHEMA = "tower.grounds.runtime-provider-attestation.v1"
OPAQUE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.:-]{7,191}$")
ALLOWED_ROLES = frozenset({
    "resident", "maintenance_technician", "maintenance_supervisor",
    "leasing_agent", "property_manager", "regional_manager", "inspector",
    "turnover_crew", "grounds_janitorial", "renovation_coordinator",
    "compliance", "vendor", "owner",
})


class GroundsRuntimeReceiverUnavailable(RuntimeError):
    pass


def _provider():
    module_name = str(os.getenv(PROVIDER_ENV, "") or "").strip()
    if not module_name or module_name.startswith(("tower.", "grounds.")):
        raise GroundsRuntimeReceiverUnavailable(
            "independent Grounds runtime provider module is not configured"
        )
    try:
        provider = import_module(module_name)
    except Exception as exc:
        raise GroundsRuntimeReceiverUnavailable(
            "independent Grounds runtime provider cannot be loaded"
        ) from None
    required = (
        "provider_attestation", "verify_grounds_request", "health_check",
        "list_ground_technicians", "verify_ground_technician_assignment",
    )
    if any(not callable(getattr(provider, name, None)) for name in required):
        raise GroundsRuntimeReceiverUnavailable(
            "independent Grounds runtime provider contract is incomplete"
        )
    _attestation(provider)
    return provider


def _attestation(provider, *, now_epoch: int | None = None) -> dict[str, Any]:
    now = int(time.time()) if now_epoch is None else int(now_epoch)
    try:
        record = provider.provider_attestation()
    except Exception:
        raise GroundsRuntimeReceiverUnavailable(
            "Grounds runtime provider attestation unavailable"
        ) from None
    expected = {
        "schema_version", "issuer", "audience", "provider_id", "status",
        "issued_at_epoch", "expires_at_epoch", "revocation_checked",
        "session_binding_checked", "resource_grants_checked",
    }
    if not isinstance(record, Mapping) or set(record) != expected:
        raise GroundsRuntimeReceiverUnavailable(
            "Grounds runtime provider attestation invalid"
        )
    if (
        record["schema_version"] != ATTESTATION_SCHEMA
        or record["issuer"] != "tower"
        or record["audience"] != "grounds"
        or record["status"] != "VERIFIED"
        or record["revocation_checked"] is not True
        or record["session_binding_checked"] is not True
        or record["resource_grants_checked"] is not True
        or not isinstance(record["provider_id"], str)
        or OPAQUE.fullmatch(record["provider_id"]) is None
        or type(record["issued_at_epoch"]) is not int
        or type(record["expires_at_epoch"]) is not int
        or not record["issued_at_epoch"] <= now < record["expires_at_epoch"]
        or record["expires_at_epoch"] - record["issued_at_epoch"] > 300
    ):
        raise GroundsRuntimeReceiverUnavailable(
            "Grounds runtime provider attestation not current"
        )
    return dict(record)


def _scope_from_verified(provider, ticket):
    try:
        from grounds.access import TowerScope, verified_scope
    except Exception:
        raise GroundsRuntimeReceiverUnavailable(
            "Grounds TowerScope implementation is unavailable"
        ) from None

    try:
        scope = verified_scope(ticket, verifier=provider.verify_grounds_request)
    except Exception:
        raise GroundsRuntimeReceiverUnavailable("Grounds request rejected") from None

    if not isinstance(scope, TowerScope) or scope.role not in ALLOWED_ROLES:
        raise GroundsRuntimeReceiverUnavailable("Grounds request rejected")
    return scope


def create_certified_grounds_receiver():
    provider = _provider()

    def receive(environ):
        _attestation(provider)
        return _scope_from_verified(provider, environ)

    def health_check():
        try:
            _attestation(provider)
            return provider.health_check() is True
        except Exception:
            return False

    receive.health_check = health_check
    receive.provider_id = _attestation(provider)["provider_id"]
    return receive


def create_certified_grounds_staff_directory():
    provider = _provider()

    def directory(actor, property_ref):
        _attestation(provider)
        if getattr(actor, "role", None) not in {
            "owner", "property_manager", "maintenance_supervisor",
        }:
            raise GroundsRuntimeReceiverUnavailable("Grounds staff directory denied")
        if property_ref not in getattr(actor, "property_refs", frozenset()):
            raise GroundsRuntimeReceiverUnavailable("Grounds staff directory denied")
        try:
            rows = provider.list_ground_technicians(
                actor_subject_ref=actor.subject_ref,
                actor_session_ref=actor.session_ref,
                property_ref=property_ref,
            )
        except Exception:
            raise GroundsRuntimeReceiverUnavailable(
                "Grounds staff directory unavailable"
            ) from None
        if not isinstance(rows, list) or len(rows) > 100:
            raise GroundsRuntimeReceiverUnavailable(
                "Grounds staff directory response invalid"
            )
        safe = []
        seen = set()
        for row in rows:
            if not isinstance(row, Mapping) or set(row) != {"staff_ref", "label"}:
                raise GroundsRuntimeReceiverUnavailable(
                    "Grounds staff directory response invalid"
                )
            staff_ref, label = row["staff_ref"], row["label"]
            if (
                not isinstance(staff_ref, str) or OPAQUE.fullmatch(staff_ref) is None
                or staff_ref in seen or not isinstance(label, str)
                or not 1 <= len(label.strip()) <= 100
            ):
                raise GroundsRuntimeReceiverUnavailable(
                    "Grounds staff directory response invalid"
                )
            seen.add(staff_ref)
            safe.append({"staff_ref": staff_ref, "label": label.strip()})
        return safe

    return directory


def create_certified_grounds_staff_resolver():
    provider = _provider()

    def resolve(actor, property_ref, work_ref, technician_ref):
        _attestation(provider)
        if getattr(actor, "role", None) not in {
            "owner", "property_manager", "maintenance_supervisor",
        }:
            raise GroundsRuntimeReceiverUnavailable("Grounds technician resolution denied")
        if property_ref not in getattr(actor, "property_refs", frozenset()):
            raise GroundsRuntimeReceiverUnavailable("Grounds technician resolution denied")
        try:
            ticket = provider.verify_ground_technician_assignment(
                actor_subject_ref=actor.subject_ref,
                actor_session_ref=actor.session_ref,
                property_ref=property_ref,
                work_ref=work_ref,
                technician_ref=technician_ref,
            )
        except Exception:
            raise GroundsRuntimeReceiverUnavailable(
                "Grounds technician resolution unavailable"
            ) from None
        scope = _scope_from_verified(provider, ticket)
        if (
            scope.role != "maintenance_technician"
            or scope.subject_ref != technician_ref
            or property_ref not in scope.property_refs
            or work_ref not in scope.assigned_work_refs
        ):
            raise GroundsRuntimeReceiverUnavailable(
                "Grounds technician assignment not verified"
            )
        return scope

    return resolve
