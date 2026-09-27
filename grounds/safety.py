"""GRD052 — human urgency acknowledgment, entry preference and event-intent review.

This code DOES NOT place emergency calls, dispatch a worker, send notifications,
certify legal entry consent, or provide a notification transport. Event outbox
records are pending metadata only and contain no resident message content.
"""
from __future__ import annotations

import sqlite3
from uuid import uuid4

from .access import AccessDenied, TowerScope
from .operations import GroundsOperations, GroundsConflict, _now
from .storage import GroundsStore


class GroundsSafety:
    def __init__(self,store:GroundsStore):
        if not isinstance(store,GroundsStore):
            raise TypeError("GroundsStore required")
        self.store=store
        self.ops=GroundsOperations(store)

    def acknowledge_urgency(self,actor:TowerScope,*,work_ref:str,
                            assessed_urgency:str)->dict:
        actor=self.ops._scope(actor)
        actor.require_role("owner","property_manager","maintenance_supervisor")
        if assessed_urgency not in ("routine","priority","emergency"):
            raise GroundsConflict("unknown human triage level")
        with self.store.transaction(write=True) as db:
            row=self.ops._visible_order(db,actor,work_ref)
            if row["state"]!="submitted":
                raise GroundsConflict("intake already progressed; triage record must be created first")
            if row["emergency_flag"] and assessed_urgency=="routine":
                raise GroundsConflict("urgent resident flag cannot be silently downgraded")
            try:
                db.execute(
                    """INSERT INTO emergency_reviews
                       (work_ref,urgency,reviewed_by,reviewed_at)
                       VALUES(?,?,?,?)""",
                    (work_ref,assessed_urgency,actor.subject_ref,_now()),
                )
            except sqlite3.IntegrityError as exc:
                raise GroundsConflict("human triage already recorded") from exc
            return {"work_ref":work_ref,"assessed_urgency":assessed_urgency,
                    "human_review_recorded":True,"external_dispatch_confirmed":False,
                    "emergency_services_contacted":False}

    def triage_status(self,actor:TowerScope,*,work_ref:str)->dict:
        actor=self.ops._scope(actor)
        with self.store.transaction() as db:
            order=self.ops._visible_order(db,actor,work_ref)
            row=db.execute(
                """SELECT urgency,reviewed_at FROM emergency_reviews WHERE work_ref=?""",
                (work_ref,),
            ).fetchone()
            return {"work_ref":work_ref,"resident_urgent_flag":bool(order["emergency_flag"]),
                    "human_review_recorded":row is not None,
                    "assessed_urgency":row["urgency"] if row else None,
                    "external_dispatch_confirmed":False}

    def record_entry_preference(self,actor:TowerScope,*,work_ref:str,preference:str,
                                expected_revision:int)->dict:
        actor=self.ops._scope(actor)
        actor.require_role("resident")
        if preference not in ("yes","no","contact_first"):
            raise GroundsConflict("entry preference invalid")
        if type(expected_revision) is not int or expected_revision<0:
            raise GroundsConflict("entry preference revision invalid")
        with self.store.transaction(write=True) as db:
            order=self.ops._visible_order(db,actor,work_ref)
            if order["state"]=="closed":
                raise GroundsConflict("closed job requires a new request")
            previous=db.execute(
                "SELECT revision FROM work_entry_preferences WHERE work_ref=?",(work_ref,),
            ).fetchone()
            current=previous["revision"] if previous else 0
            if current!=expected_revision:
                raise GroundsConflict("entry preference changed")
            revision=current+1
            db.execute(
                """INSERT INTO work_entry_preferences
                   (work_ref,subject_ref,preference,revision,updated_at)
                   VALUES(?,?,?,?,?)
                   ON CONFLICT(work_ref) DO UPDATE SET
                   subject_ref=excluded.subject_ref,preference=excluded.preference,
                   revision=excluded.revision,updated_at=excluded.updated_at""",
                (work_ref,actor.subject_ref,preference,revision,_now()),
            )
            db.execute(
                """INSERT INTO work_entry_events
                   (event_ref,work_ref,subject_ref,preference,revision,updated_at)
                   VALUES(?,?,?,?,?,?)""",
                (uuid4().hex,work_ref,actor.subject_ref,preference,revision,_now()),
            )
            return {"work_ref":work_ref,"preference":preference,"revision":revision,
                    "legal_entry_notice_proven":False,
                    "staff_entry_authorized":False,"notification_sent":False}

    def entry_preference(self,actor:TowerScope,*,work_ref:str)->dict:
        actor=self.ops._scope(actor)
        with self.store.transaction() as db:
            order=self.ops._visible_order(db,actor,work_ref)
            row=db.execute(
                "SELECT preference,revision FROM work_entry_preferences WHERE work_ref=?",
                (work_ref,),
            ).fetchone()
            return {"work_ref":work_ref,
                    "current_preference":row["preference"] if row else order["entry_permission"],
                    "revision":row["revision"] if row else 0,
                    "staff_entry_authorized":False,
                    "legal_entry_notice_proven":False}

    def pending_event_intents(self,actor:TowerScope,*,property_ref:str)->list[dict]:
        actor=self.ops._scope(actor)
        actor.require_role("owner","property_manager","maintenance_supervisor")
        actor.require_property(property_ref)
        with self.store.transaction() as db:
            return [dict(row) for row in db.execute(
                """SELECT event_ref,event_kind,resource_ref,source_revision,created_at,status
                   FROM event_outbox WHERE property_ref=? AND status='pending'
                   ORDER BY created_at,event_ref""",(property_ref,),
            )]

    def delivery_status(self,actor:TowerScope,*,property_ref:str)->dict:
        pending=self.pending_event_intents(actor,property_ref=property_ref)
        return {
            "property_ref":property_ref,"pending_intent_count":len(pending),
            "provider_connected":False,"recipient_resolution_enabled":False,
            "delivered_count":0,"legal_service_proven":False,
            "emergency_dispatch_confirmed":False,
        }
