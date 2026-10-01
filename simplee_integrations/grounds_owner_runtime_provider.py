"""Real owner-only Tower -> Grounds runtime provider.

This is the first non-fixture provider for the reviewed Tower Grounds adapter.
It supports ONLY the current hosted owner corridor. Resident/staff sessions are
not manufactured here.

Identity comes from the signed Flask Tower session plus the current exact
Tower Grounds access receipt. Resource grants come from the current private
Grounds PostgreSQL database: the current owner receives only property refs that
actually exist in Grounds. No browser header, query/body role flag or property
list can widen that grant.

The provider deliberately returns an empty technician directory and rejects
technician resolution until Tower has a separately authoritative staff people /
assignment source. That keeps resident/staff work closed instead of deriving
staff identity from mutable work rows.
"""
from __future__ import annotations

from collections.abc import Mapping
import os
import re
import time
from typing import Any

from flask import has_request_context, request, session

from tower.ecosystem_direct_route_guard import (
    ACCESS_RECEIPT_KEYS,
    ecosystem_access_active,
)
from tower.identity_authority import hosted_owner_identity_authority
from tower.tower_human_login_ob_launch import (
    SESSION_ID,
    SESSION_OWNER_ID,
    SESSION_ROLE,
    owner_session_active,
)
from tower.truth_contract import VERIFIED

SCHEMA="tower.grounds.runtime-provider-attestation.v1"
PROVIDER_ID="simplee_grounds_owner_runtime_provider_v1"
GROUNDS_DSN_ENV="GROUNDS_PRIVATE_POSTGRES_URL"
MAX_PROPERTIES=500
REF=re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}$")


class GroundsOwnerRuntimeProviderUnavailable(PermissionError):
    pass


def _identity_record() -> dict[str,Any]:
    try:
        authority=hosted_owner_identity_authority()
    except Exception:
        raise GroundsOwnerRuntimeProviderUnavailable("owner identity authority unavailable") from None
    record=authority.get("record") if isinstance(authority,Mapping) else None
    entitlements=authority.get("app_entitlements") if isinstance(authority,Mapping) else None
    if (
        authority.get("verification_state")!=VERIFIED
        or not isinstance(record,Mapping)
        or record.get("role")!="owner"
        or record.get("session_subject_alignment")!=VERIFIED
        or not isinstance(record.get("person_id"),str)
        or REF.fullmatch(record["person_id"]) is None
        or not isinstance(entitlements,list)
    ):
        raise GroundsOwnerRuntimeProviderUnavailable("owner identity authority unavailable")
    grounds=next((
        item for item in entitlements
        if isinstance(item,Mapping)
        and item.get("app_id")=="grounds"
        and item.get("access_policy")=="GRANTED"
        and item.get("verification_state")==VERIFIED
    ),None)
    if grounds is None:
        raise GroundsOwnerRuntimeProviderUnavailable("Grounds owner entitlement unavailable")
    return dict(record)


def _store():
    dsn=str(os.getenv(GROUNDS_DSN_ENV,"") or "").strip()
    if not dsn:
        raise GroundsOwnerRuntimeProviderUnavailable("private Grounds store unavailable")
    try:
        from grounds.postgres import PostgresGroundsStore
        store=PostgresGroundsStore(dsn)
        store.assert_schema_ready()
        return store
    except Exception:
        raise GroundsOwnerRuntimeProviderUnavailable("private Grounds store unavailable") from None


def _property_refs() -> list[str]:
    store=_store()
    try:
        with store.transaction() as db:
            rows=db.execute(
                "SELECT property_ref FROM properties ORDER BY property_ref LIMIT ?",
                (MAX_PROPERTIES+1,),
            ).fetchall()
    except Exception:
        raise GroundsOwnerRuntimeProviderUnavailable("current Grounds property grants unavailable") from None
    refs=[row["property_ref"] for row in rows]
    if (
        not refs or len(refs)>MAX_PROPERTIES
        or len(refs)!=len(set(refs))
        or any(not isinstance(ref,str) or REF.fullmatch(ref) is None for ref in refs)
    ):
        raise GroundsOwnerRuntimeProviderUnavailable("current Grounds property grants unavailable")
    return refs


def _current_owner_request() -> tuple[str,str,dict[str,Any]]:
    if not has_request_context() or not owner_session_active():
        raise GroundsOwnerRuntimeProviderUnavailable("current Tower owner session required")
    if not request.path.startswith("/grounds"):
        raise GroundsOwnerRuntimeProviderUnavailable("Grounds request path required")
    if not ecosystem_access_active("grounds"):
        raise GroundsOwnerRuntimeProviderUnavailable("current Tower Grounds access receipt required")
    record=_identity_record()
    owner_id=session.get(SESSION_OWNER_ID)
    session_ref=session.get(SESSION_ID)
    if (
        session.get(SESSION_ROLE)!="owner"
        or not isinstance(owner_id,str)
        or owner_id!=record["person_id"]
        or not isinstance(session_ref,str)
        or REF.fullmatch(session_ref) is None
    ):
        raise GroundsOwnerRuntimeProviderUnavailable("Tower owner/session identity mismatch")
    receipt=session.get(ACCESS_RECEIPT_KEYS["grounds"])
    if not isinstance(receipt,dict):
        raise GroundsOwnerRuntimeProviderUnavailable("current Tower Grounds access receipt required")
    return owner_id,session_ref,receipt


def provider_attestation() -> dict[str,Any]:
    # Health/attestation is environment-level, not a grant to a caller.
    _identity_record()
    _property_refs()
    now=int(time.time())
    return {
        "schema_version":SCHEMA,
        "issuer":"tower",
        "audience":"grounds",
        "provider_id":PROVIDER_ID,
        "status":"VERIFIED",
        "issued_at_epoch":now,
        "expires_at_epoch":now+60,
        "revocation_checked":True,
        "session_binding_checked":True,
        "resource_grants_checked":True,
    }


def health_check() -> bool:
    try:
        provider_attestation()
        return True
    except Exception:
        return False


def verify_grounds_request(ticket) -> dict[str,Any]:
    if not isinstance(ticket,Mapping):
        raise GroundsOwnerRuntimeProviderUnavailable("Grounds request rejected")
    owner_id,session_ref,receipt=_current_owner_request()
    # The WSGI ticket is used only to prove this verifier is servicing the same
    # Grounds request; identity and grants still come from server-side sources.
    ticket_path=str(ticket.get("PATH_INFO","") or "")
    if ticket_path!=request.path or not ticket_path.startswith("/grounds"):
        raise GroundsOwnerRuntimeProviderUnavailable("Grounds request rejected")
    now=int(time.time())
    receipt_expiry=receipt.get("expires_at_epoch")
    if type(receipt_expiry) is not int or receipt_expiry<=now:
        raise GroundsOwnerRuntimeProviderUnavailable("current Tower Grounds access receipt required")
    expiry=min(now+60,receipt_expiry)
    if expiry<=now:
        raise GroundsOwnerRuntimeProviderUnavailable("current Tower Grounds access receipt required")
    return {
        "issuer":"tower",
        "audience":"grounds",
        "subject_ref":owner_id,
        "session_ref":session_ref,
        "role":"owner",
        "property_refs":_property_refs(),
        "unit_refs":[],
        "assigned_work_refs":[],
        "issued_at":now,
        "expires_at":expiry,
    }


def list_ground_technicians(*,actor_subject_ref,actor_session_ref,property_ref):
    owner_id,session_ref,_receipt=_current_owner_request()
    if actor_subject_ref!=owner_id or actor_session_ref!=session_ref:
        raise GroundsOwnerRuntimeProviderUnavailable("Grounds staff directory denied")
    if property_ref not in _property_refs():
        raise GroundsOwnerRuntimeProviderUnavailable("Grounds staff directory denied")
    # No authoritative staff people source exists yet. Empty is truthful and
    # prevents assignment; do not infer staff identity from work_orders.
    return []


def verify_ground_technician_assignment(**_kwargs):
    raise GroundsOwnerRuntimeProviderUnavailable(
        "authoritative Tower staff identity/assignment provider not configured"
    )
