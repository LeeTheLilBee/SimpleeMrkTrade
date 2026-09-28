"""GRD146–149 — append-only verified delivery/on-call receipt intake.

Grounds event_outbox rows are intents, not delivery. This module records only
receipts authenticated by a server-owned Tower delivery-gateway verifier and
binds each receipt to the exact existing outbox event/property/resource/revision.

A notification receipt is not legal service. An urgent human-escalation receipt
is not emergency-services dispatch. No transport, recipient discovery, provider
credential, SMS/email send, or webhook endpoint is implemented here.
"""
from __future__ import annotations

import hashlib
import json
import re
import sqlite3
from datetime import datetime, timezone
from time import time
from typing import Callable, Mapping

from .access import AccessDenied, TowerScope
from .operations import GroundsConflict
from .storage import GroundsStoreBase

SCHEMA_VERSION="tower.grounds.delivery.receipt.v1"
MAX_LIFETIME_SECONDS=300
_REF=re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}$")
_FIELDS=frozenset({
    "schema_version","source","audience","kind","receipt_ref","event_ref",
    "property_ref","event_kind","resource_ref","source_revision",
    "provider_receipt_ref","delivery_state","observed_at","expires_at",
})
_STATES={
    "notification_delivery":frozenset(("accepted","delivered","failed")),
    "urgent_human_escalation":frozenset(("queued","human_acknowledged","failed")),
}


def _ref(value:object)->str:
    if not isinstance(value,str) or _REF.fullmatch(value) is None:
        raise AccessDenied("delivery receipt rejected")
    return value


def _digest(item:Mapping)->str:
    return hashlib.sha256(json.dumps(
        {key:item[key] for key in sorted(_FIELDS)},
        sort_keys=True,separators=(",",":"),ensure_ascii=False,allow_nan=False,
    ).encode("utf-8")).hexdigest()


class GroundsDeliveryReceipts:
    def __init__(self,store:GroundsStoreBase):
        if not isinstance(store,GroundsStoreBase):
            raise TypeError("transaction-backed Grounds store required")
        self.store=store

    def record(
        self, signed_receipt:object, *,
        receipt_verifier:Callable[[object],Mapping], now:int|None=None,
    )->dict:
        if not callable(receipt_verifier):
            raise AccessDenied("certified delivery receipt verifier required")
        try:
            item=receipt_verifier(signed_receipt)
        except Exception as exc:
            raise AccessDenied("delivery receipt rejected") from exc
        if not isinstance(item,Mapping) or set(item)!=_FIELDS:
            raise AccessDenied("delivery receipt rejected")
        kind=item["kind"]
        if (item["schema_version"]!=SCHEMA_VERSION
            or item["source"]!="tower_delivery_gateway"
            or item["audience"]!="grounds"
            or kind not in _STATES
            or item["delivery_state"] not in _STATES[kind]):
            raise AccessDenied("delivery receipt rejected")
        receipt_ref=_ref(item["receipt_ref"])
        event_ref=_ref(item["event_ref"])
        property_ref=_ref(item["property_ref"])
        event_kind=_ref(item["event_kind"])
        resource_ref=_ref(item["resource_ref"])
        provider_receipt_ref=_ref(item["provider_receipt_ref"])
        revision=item["source_revision"]
        if type(revision) is not int or not 1<=revision<=2147483647:
            raise AccessDenied("delivery receipt rejected")
        clock=int(time()) if now is None else now
        observed,expires=item["observed_at"],item["expires_at"]
        if any(type(v) is not int for v in (clock,observed,expires)):
            raise AccessDenied("delivery receipt rejected")
        if observed>clock+5 or expires<=clock or not 0<expires-observed<=MAX_LIFETIME_SECONDS:
            raise AccessDenied("delivery receipt rejected")
        digest=_digest(item)
        recorded_at=datetime.now(timezone.utc).isoformat()
        try:
            with self.store.transaction(write=True) as db:
                intent=db.execute(
                    """SELECT property_ref,event_kind,resource_ref,source_revision
                       FROM event_outbox WHERE event_ref=?""",(event_ref,),
                ).fetchone()
                if (intent is None or intent["property_ref"]!=property_ref
                    or intent["event_kind"]!=event_kind
                    or intent["resource_ref"]!=resource_ref
                    or intent["source_revision"]!=revision):
                    raise AccessDenied("delivery receipt event mismatch")
                if kind=="urgent_human_escalation" and event_kind!="urgent_intake_requires_human_review":
                    raise AccessDenied("urgent escalation receipt event mismatch")
                prior=db.execute(
                    """SELECT event_ref,receipt_digest,receipt_kind,delivery_state
                       FROM event_delivery_receipts WHERE receipt_ref=?""",
                    (receipt_ref,),
                ).fetchone()
                if prior is not None:
                    if prior["receipt_digest"]!=digest or prior["event_ref"]!=event_ref:
                        raise GroundsConflict("delivery receipt replay changed")
                    return {
                        "receipt_ref":receipt_ref,"event_ref":event_ref,
                        "kind":prior["receipt_kind"],"delivery_state":prior["delivery_state"],
                        "recorded":True,"replayed":True,
                        "legal_service_proven":False,"emergency_services_contacted":False,
                    }
                db.execute(
                    """INSERT INTO event_delivery_receipts
                       (receipt_ref,event_ref,property_ref,receipt_kind,delivery_state,
                        provider_receipt_ref,receipt_digest,observed_at,recorded_at)
                       VALUES(?,?,?,?,?,?,?,?,?)""",
                    (receipt_ref,event_ref,property_ref,kind,item["delivery_state"],
                     provider_receipt_ref,digest,observed,recorded_at),
                )
        except sqlite3.IntegrityError as exc:
            raise GroundsConflict("duplicate or conflicting delivery receipt") from exc
        return {
            "receipt_ref":receipt_ref,"event_ref":event_ref,
            "kind":kind,"delivery_state":item["delivery_state"],
            "recorded":True,"replayed":False,
            "legal_service_proven":False,"emergency_services_contacted":False,
        }

    def property_status(self,actor:TowerScope,*,property_ref:str)->dict:
        if not isinstance(actor,TowerScope):
            raise AccessDenied("verified Tower scope required")
        actor.require_role("owner","property_manager","maintenance_supervisor")
        actor.require_property(property_ref)
        with self.store.transaction() as db:
            total=db.execute(
                "SELECT COUNT(*) FROM event_delivery_receipts WHERE property_ref=?",
                (property_ref,),
            ).fetchone()[0]
            delivered=db.execute(
                """SELECT COUNT(DISTINCT event_ref) FROM event_delivery_receipts
                   WHERE property_ref=? AND receipt_kind='notification_delivery'
                     AND delivery_state='delivered'""",(property_ref,),
            ).fetchone()[0]
            failed=db.execute(
                """SELECT COUNT(*) FROM event_delivery_receipts
                   WHERE property_ref=? AND delivery_state='failed'""",(property_ref,),
            ).fetchone()[0]
            urgent_ack=db.execute(
                """SELECT COUNT(DISTINCT event_ref) FROM event_delivery_receipts
                   WHERE property_ref=? AND receipt_kind='urgent_human_escalation'
                     AND delivery_state='human_acknowledged'""",(property_ref,),
            ).fetchone()[0]
        return {
            "property_ref":property_ref,"verified_receipt_count":total,
            "delivered_event_count":delivered,"failed_receipt_count":failed,
            "urgent_human_acknowledged_event_count":urgent_ack,
            "provider_connection_currently_verified":False,
            "legal_service_proven":False,"emergency_dispatch_confirmed":False,
        }
