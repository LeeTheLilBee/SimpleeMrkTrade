"""GRD113–117 — verified post-close multifamily acceptance into Grounds.

BuyBox may prepare an UNSENT source proposal, but it cannot make a property
operational. Grounds accepts an owned-property record only after a separately
authenticated Tower verifier supplies a fresh, audience-bound completed-close
receipt with exact BuyBox source fingerprints and ownership/encumbrance proof
references. A local ACQUIRED label, browser JSON, listing, or fixture callback
is never sufficient production authority.

The verifier is injected by trusted server composition; this module does not
implement Tower signing, title review, money movement, or closing.
"""
from __future__ import annotations

import hashlib
import json
import re
import sqlite3
from datetime import date, datetime, timezone
from time import time
from typing import Callable, Mapping

from .access import AccessDenied, TowerScope
from .operations import GroundsConflict
from .storage import GroundsStoreBase

SCHEMA_VERSION="tower.grounds.multifamily.post_close.v1"
MAX_LIFETIME_SECONDS=300
_REF=re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}$")
_HEX64=re.compile(r"^[0-9a-f]{64}$")
_FIELDS=frozenset({
    "schema_version","source","audience","kind","handoff_ref","owner_ref",
    "property_ref","property_name","owned_on","opportunity_id",
    "opportunity_revision","input_snapshot_digest","proposal_fingerprint",
    "vertical_id","proposed_recipient","closing_status","ownership_status",
    "encumbrance_status","tower_close_receipt_ref","title_proof_ref",
    "encumbrance_review_ref","issued_at","expires_at",
})


def _ref(value: object, label: str) -> str:
    if not isinstance(value,str) or _REF.fullmatch(value) is None:
        raise AccessDenied("post-close handoff rejected: "+label)
    return value


def _text(value: object, label: str, *, max_length: int=256) -> str:
    if (not isinstance(value,str) or not value.strip() or len(value.strip())>max_length
        or "\x00" in value):
        raise AccessDenied("post-close handoff rejected: "+label)
    return value.strip()


def _day(value: object) -> str:
    if not isinstance(value,str):
        raise AccessDenied("post-close handoff rejected: owned_on")
    try:
        parsed=date.fromisoformat(value)
    except ValueError as exc:
        raise AccessDenied("post-close handoff rejected: owned_on") from exc
    if parsed.isoformat()!=value:
        raise AccessDenied("post-close handoff rejected: owned_on")
    return value


def _canonical_digest(item: Mapping) -> str:
    canonical=json.dumps(
        {key:item[key] for key in sorted(_FIELDS)},
        sort_keys=True,separators=(",",":"),ensure_ascii=False,allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


class GroundsAcquisitionHandoff:
    """Server-side receiver half; it consumes only independently verified Tower truth."""

    def __init__(self,store:GroundsStoreBase):
        if not isinstance(store,GroundsStoreBase):
            raise TypeError("transaction-backed Grounds store required")
        self.store=store

    def accept_multifamily_close(
        self, actor:TowerScope, *, signed_handoff:object,
        tower_verifier:Callable[[object],Mapping], now:int|None=None,
    )->dict:
        if not isinstance(actor,TowerScope):
            raise AccessDenied("verified Tower scope required")
        actor.require_role("owner")
        if not callable(tower_verifier):
            raise AccessDenied("certified Tower close verifier required")
        try:
            verified=tower_verifier(signed_handoff)
        except Exception as exc:
            raise AccessDenied("post-close handoff rejected") from exc
        if not isinstance(verified,Mapping) or set(verified)!=_FIELDS:
            raise AccessDenied("post-close handoff rejected")
        if (verified["schema_version"]!=SCHEMA_VERSION
            or verified["source"]!="tower" or verified["audience"]!="grounds"
            or verified["kind"]!="multifamily_post_close"
            or verified["vertical_id"]!="multifamily"
            or verified["proposed_recipient"]!="grounds"
            or verified["closing_status"]!="completed"
            or verified["ownership_status"]!="verified_owner"
            or verified["encumbrance_status"]!="verified_recorded"):
            raise AccessDenied("post-close handoff rejected")
        if verified["owner_ref"]!=actor.subject_ref:
            raise AccessDenied("post-close owner mismatch")
        property_ref=_ref(verified["property_ref"],"property_ref")
        actor.require_property(property_ref)
        handoff_ref=_ref(verified["handoff_ref"],"handoff_ref")
        opportunity_id=_ref(verified["opportunity_id"],"opportunity_id")
        close_ref=_ref(verified["tower_close_receipt_ref"],"tower_close_receipt_ref")
        title_ref=_ref(verified["title_proof_ref"],"title_proof_ref")
        encumbrance_ref=_ref(verified["encumbrance_review_ref"],"encumbrance_review_ref")
        property_name=_text(verified["property_name"],"property_name")
        owned_on=_day(verified["owned_on"])
        revision=verified["opportunity_revision"]
        if type(revision) is not int or not 1<=revision<=2147483647:
            raise AccessDenied("post-close handoff rejected")
        for key in ("input_snapshot_digest","proposal_fingerprint"):
            if not isinstance(verified[key],str) or _HEX64.fullmatch(verified[key]) is None:
                raise AccessDenied("post-close handoff rejected")
        clock=int(time()) if now is None else now
        issued,expires=verified["issued_at"],verified["expires_at"]
        if any(type(value) is not int for value in (clock,issued,expires)):
            raise AccessDenied("post-close handoff rejected")
        if (issued>clock+5 or expires<=clock or not 0<expires-issued<=MAX_LIFETIME_SECONDS):
            raise AccessDenied("post-close handoff rejected")
        digest=_canonical_digest(verified)
        accepted_at=datetime.now(timezone.utc).isoformat()
        try:
            with self.store.transaction(write=True) as db:
                prior=db.execute(
                    """SELECT property_ref,receipt_digest,tower_close_receipt_ref,
                              opportunity_id,opportunity_revision
                       FROM property_acquisition_receipts WHERE handoff_ref=?""",
                    (handoff_ref,),
                ).fetchone()
                if prior is not None:
                    if prior["receipt_digest"]!=digest or prior["property_ref"]!=property_ref:
                        raise GroundsConflict("post-close handoff replay changed")
                    # Recheck current actor/property scope before disclosing accepted state.
                    actor.require_property(prior["property_ref"])
                    return {
                        "handoff_ref":handoff_ref,"property_ref":prior["property_ref"],
                        "opportunity_id":prior["opportunity_id"],
                        "opportunity_revision":prior["opportunity_revision"],
                        "tower_close_receipt_ref":prior["tower_close_receipt_ref"],
                        "accepted":True,"replayed":True,
                        "money_moved":False,"payment_authorized":False,
                    }
                db.execute(
                    """INSERT INTO properties
                       (property_ref,name,owned_on,close_proof_ref)
                       VALUES(?,?,?,?)""",
                    (property_ref,property_name,owned_on,close_ref),
                )
                db.execute(
                    """INSERT INTO property_acquisition_receipts
                       (handoff_ref,property_ref,opportunity_id,opportunity_revision,
                        input_snapshot_digest,proposal_fingerprint,
                        tower_close_receipt_ref,title_proof_ref,encumbrance_review_ref,
                        receipt_digest,accepted_by,accepted_at)
                       VALUES(?,?,?,?,?,?,?,?,?,?,?,?)""",
                    (handoff_ref,property_ref,opportunity_id,revision,
                     verified["input_snapshot_digest"],verified["proposal_fingerprint"],
                     close_ref,title_ref,encumbrance_ref,digest,actor.subject_ref,accepted_at),
                )
        except sqlite3.IntegrityError as exc:
            raise GroundsConflict("property close receipt already accepted or conflicts") from exc
        return {
            "handoff_ref":handoff_ref,"property_ref":property_ref,
            "opportunity_id":opportunity_id,"opportunity_revision":revision,
            "tower_close_receipt_ref":close_ref,"accepted":True,"replayed":False,
            "money_moved":False,"payment_authorized":False,
        }

    def accepted_receipt(self,actor:TowerScope,*,property_ref:str)->dict:
        if not isinstance(actor,TowerScope):
            raise AccessDenied("verified Tower scope required")
        actor.require_role("owner","property_manager","regional_manager")
        actor.require_property(property_ref)
        with self.store.transaction() as db:
            row=db.execute(
                """SELECT handoff_ref,property_ref,opportunity_id,opportunity_revision,
                          input_snapshot_digest,proposal_fingerprint,
                          tower_close_receipt_ref,title_proof_ref,encumbrance_review_ref,
                          accepted_at
                   FROM property_acquisition_receipts WHERE property_ref=?""",
                (property_ref,),
            ).fetchone()
            if row is None:
                raise AccessDenied("verified acquisition receipt unavailable")
            result=dict(row)
            result.update({
                "source":"grounds","status":"accepted_verified_close",
                "raw_close_document_included":False,"money_moved":False,
            })
            return result
