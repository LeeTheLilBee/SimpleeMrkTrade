"""GRD190–198: property-scoped historic delivery exceptions from authenticated receipts.

The existing event_outbox status is an INTERNAL pending intent, not an actual
provider queue or a legally delivered message. This module is read-only and
cannot re-send, resolve recipients, mark delivered or dispatch urgent support.
"""
from __future__ import annotations

from .access import AccessDenied,TowerScope
from .operations import GroundsOperations
from .storage import GroundsStoreBase


class GroundsDeliveryDesk:
    def __init__(self,store:GroundsStoreBase):
        self.ops=GroundsOperations(store)
        self.store=store

    def staff_status(self,actor:TowerScope,*,property_ref:str)->dict:
        actor=self.ops._scope(actor)
        actor.require_role("owner","property_manager","maintenance_supervisor")
        actor.require_property(property_ref)
        with self.store.transaction() as db:
            prop=db.execute(
                "SELECT 1 FROM properties WHERE property_ref=?",(property_ref,),
            ).fetchone()
            if prop is None:
                raise AccessDenied("property unavailable")
            total=db.execute(
                "SELECT COUNT(*) FROM event_outbox WHERE property_ref=?",
                (property_ref,),
            ).fetchone()[0]
            unverified=db.execute(
                """SELECT COUNT(*) FROM event_outbox e
                   WHERE e.property_ref=? AND NOT EXISTS (
                     SELECT 1 FROM event_delivery_receipts r
                     WHERE r.event_ref=e.event_ref
                       AND r.receipt_kind='notification_delivery'
                       AND r.delivery_state='delivered'
                   )""",(property_ref,),
            ).fetchone()[0]
            rows=[dict(r) for r in db.execute(
                """SELECT event_ref,event_kind,resource_ref,source_revision,created_at
                   FROM event_outbox WHERE property_ref=?
                   ORDER BY created_at DESC,event_ref DESC LIMIT 50""",
                (property_ref,),
            )]
            items=[]
            for row in rows:
                records=[dict(r) for r in db.execute(
                    """SELECT receipt_kind,delivery_state,observed_at,recorded_at
                       FROM event_delivery_receipts WHERE event_ref=?
                       ORDER BY observed_at DESC,recorded_at DESC,receipt_ref DESC""",
                    (row["event_ref"],),
                )]
                latest={}
                for receipt in records:
                    if receipt["receipt_kind"] not in latest:
                        latest[receipt["receipt_kind"]]=receipt
                notification=latest.get("notification_delivery")
                human=latest.get("urgent_human_escalation")
                is_urgent=row["event_kind"]=="urgent_intake_requires_human_review"
                notification_state=(notification["delivery_state"] if notification
                                    else "no_verified_receipt")
                human_state=(human["delivery_state"] if human else "no_verified_receipt")
                items.append({
                    "event_ref":row["event_ref"],"event_kind":row["event_kind"],
                    "resource_ref":row["resource_ref"],
                    "source_revision":row["source_revision"],"created_at":row["created_at"],
                    "local_intent_recorded":True,
                    "latest_verified_historical_notification_state":notification_state,
                    "latest_verified_historical_human_escalation_state":
                        human_state if is_urgent else "not_applicable",
                    "requires_provider_review":
                        notification_state!="delivered"
                        or (is_urgent and human_state!="human_acknowledged"),
                    "urgent_human_source_intent":is_urgent,
                    "retry_available":False,"current_external_delivery_confirmed":False,
                })
        return {
            "source":"grounds","room":"delivery_desk","property_ref":property_ref,
            "total_local_intents":total,"not_historically_proven_delivered":unverified,
            "visible_limit":50,"visible_count":len(items),"truncated":total>len(items),
            "visible_items":items,
            "visible_provider_review_count":sum(x["requires_provider_review"] for x in items),
            "provider_currently_connected":False,"retry_dispatch_connected":False,
            "recipient_resolution_connected":False,
            "legal_service_proven":False,"emergency_dispatch_confirmed":False,
        }
