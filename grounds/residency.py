"""GRD039: lease household membership with certified Tower/Vault grant boundary.

A signed proof verifier is an injected *server-owned* dependency. It must
authenticate a valid lease/co-tenant or authorized-occupant grant and any
revocation decision; the source-only local fixtures do not do that.
A Grounds membership cannot mint Tower access, override housing law or
bypass consent. No raw identity documents or minors' personal data stored.
"""
from __future__ import annotations

import sqlite3
from typing import Callable, Mapping
from uuid import uuid4

from .access import AccessDenied, TowerScope
from .operations import GroundsOperations, GroundsConflict, _now, _required
from .storage import GroundsStoreBase


def _proof(verifier: Callable[[object], Mapping], document: object,
           *, kind: str, lease_ref: str, property_ref: str,
           unit_ref: str, subject_ref: str, relationship: str | None = None) -> str:
    if not callable(verifier):
        raise AccessDenied("certified Tower/Vault membership verifier required")
    try:
        result=verifier(document)
    except Exception as exc:
        raise AccessDenied("membership evidence rejected") from exc
    if not isinstance(result,Mapping) or result.get("status")!="verified_sealed" or result.get("kind")!=kind:
        raise AccessDenied("membership evidence rejected")
    for key,expected in (
        ("lease_ref",lease_ref),("property_ref",property_ref),
        ("unit_ref",unit_ref),("subject_ref",subject_ref),
    ):
        if result.get(key)!=expected:
            raise AccessDenied("membership proof/scope mismatch")
    if relationship is not None and result.get("relationship")!=relationship:
        raise AccessDenied("membership relationship mismatch")
    return _required(result.get("proof_ref"),"proof_ref",max_length=128)


class GroundsResidency:
    def __init__(self,store:GroundsStoreBase):
        if not isinstance(store,GroundsStoreBase):
            raise TypeError("transaction-backed Grounds store required")
        self.store=store
        self.ops=GroundsOperations(store)

    def grant_member(
        self,actor:TowerScope,*,lease_ref:str,property_ref:str,unit_ref:str,
        subject_ref:str,relationship:str,signed_grant:object,
        proof_verifier:Callable[[object],Mapping],
    ) -> dict:
        actor=self.ops._scope(actor)
        actor.require_role("owner","property_manager")
        actor.require_property(property_ref)
        _required(subject_ref,"subject_ref",max_length=128)
        if relationship not in ("co_tenant","authorized_occupant"):
            raise GroundsConflict("additional member relationship invalid")
        proof_ref=_proof(
            proof_verifier,signed_grant,kind="lease_member_grant",
            lease_ref=lease_ref,property_ref=property_ref,unit_ref=unit_ref,
            subject_ref=subject_ref,relationship=relationship,
        )
        # Proof of co-tenancy is not a new Tower session, rent obligation,
        # lease signing authority, or independent permission to access peers.
        with self.store.transaction(write=True) as db:
            lease=db.execute(
                """SELECT status,resident_ref FROM leases
                   WHERE lease_ref=? AND property_ref=? AND unit_ref=?""",
                (lease_ref,property_ref,unit_ref),
            ).fetchone()
            if lease is None or lease["status"]!="active":
                raise AccessDenied("active lease unavailable")
            if subject_ref==lease["resident_ref"]:
                raise GroundsConflict("primary occupant is already registered")
            try:
                db.execute(
                    """INSERT INTO lease_members
                       (lease_ref,property_ref,unit_ref,subject_ref,relationship,status,grant_proof_ref,joined_at)
                       VALUES(?,?,?,?,?,'active',?,?)""",
                    (lease_ref,property_ref,unit_ref,subject_ref,relationship,proof_ref,_now()),
                )
                db.execute(
                    """INSERT INTO lease_member_events
                       (event_ref,lease_ref,subject_ref,actor_ref,action,proof_ref,occurred_at)
                       VALUES(?,?,?,?,'verified_grant',?,?)""",
                    (uuid4().hex,lease_ref,subject_ref,actor.subject_ref,proof_ref,_now()),
                )
            except sqlite3.IntegrityError as exc:
                raise GroundsConflict("membership already registered or evidence reused") from exc
            return {"lease_ref":lease_ref,"subject_ref":subject_ref,
                    "relationship":relationship,"status":"active",
                    "tower_entitlement_granted":False}

    def revoke_member(
        self,actor:TowerScope,*,lease_ref:str,property_ref:str,unit_ref:str,
        subject_ref:str,signed_revocation:object,
        proof_verifier:Callable[[object],Mapping],
    ) -> dict:
        actor=self.ops._scope(actor)
        actor.require_role("owner","property_manager")
        actor.require_property(property_ref)
        proof_ref=_proof(
            proof_verifier,signed_revocation,kind="lease_member_revocation",
            lease_ref=lease_ref,property_ref=property_ref,unit_ref=unit_ref,
            subject_ref=subject_ref,
        )
        with self.store.transaction(write=True) as db:
            member=db.execute(
                """SELECT m.relationship,m.status,l.status AS lease_status
                   FROM lease_members m JOIN leases l ON l.lease_ref=m.lease_ref
                   WHERE m.lease_ref=? AND m.property_ref=? AND m.unit_ref=? AND m.subject_ref=?""",
                (lease_ref,property_ref,unit_ref,subject_ref),
            ).fetchone()
            if member is None or member["status"]!="active" or member["lease_status"]!="active":
                raise AccessDenied("active membership unavailable")
            if member["relationship"]=="primary":
                raise GroundsConflict("primary lease member requires certified lease transition")
            try:
                db.execute(
                    """INSERT INTO lease_member_events
                       (event_ref,lease_ref,subject_ref,actor_ref,action,proof_ref,occurred_at)
                       VALUES(?,?,?,?,'revoked',?,?)""",
                    (uuid4().hex,lease_ref,subject_ref,actor.subject_ref,proof_ref,_now()),
                )
                db.execute(
                    """UPDATE lease_members SET status='revoked',revoked_at=?
                       WHERE lease_ref=? AND subject_ref=?""",
                    (_now(),lease_ref,subject_ref),
                )
            except sqlite3.IntegrityError as exc:
                raise GroundsConflict("membership revocation proof already used") from exc
            return {"lease_ref":lease_ref,"subject_ref":subject_ref,
                    "status":"revoked","grounds_access_denied_immediately":True,
                    "tower_session_revocation_required":True,"notifications_sent":False}

    def active_members(self,actor:TowerScope,*,lease_ref:str,property_ref:str) -> list[dict]:
        actor=self.ops._scope(actor)
        actor.require_role("owner","property_manager")
        actor.require_property(property_ref)
        with self.store.transaction() as db:
            lease=db.execute(
                "SELECT status FROM leases WHERE lease_ref=? AND property_ref=?",
                (lease_ref,property_ref),
            ).fetchone()
            if lease is None:
                raise AccessDenied("lease unavailable")
            return [dict(row) for row in db.execute(
                """SELECT subject_ref,relationship,status FROM lease_members
                   WHERE lease_ref=? AND property_ref=? AND status='active'
                   ORDER BY relationship,subject_ref""",
                (lease_ref,property_ref),
            )]

    def history(self,actor:TowerScope,*,lease_ref:str,property_ref:str) -> list[dict]:
        actor=self.ops._scope(actor)
        actor.require_role("owner","property_manager")
        actor.require_property(property_ref)
        with self.store.transaction() as db:
            lease=db.execute(
                "SELECT 1 FROM leases WHERE lease_ref=? AND property_ref=?",
                (lease_ref,property_ref),
            ).fetchone()
            if lease is None:
                raise AccessDenied("lease unavailable")
            return [dict(row) for row in db.execute(
                """SELECT e.subject_ref,e.actor_ref,e.action,e.occurred_at
                   FROM lease_member_events e WHERE e.lease_ref=?
                   ORDER BY e.occurred_at,e.event_ref""",
                (lease_ref,),
            )]
