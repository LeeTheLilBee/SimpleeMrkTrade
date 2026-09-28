"""GRD172–180 — current-authority, lease-bound work conversations and timeline.

Message writes are private Grounds records only; they are never SMS/email, an
external delivery, emergency dispatch, legal notice or permission for entry.
No protected file bytes, image URLs, finance fields or unreviewed AI responses.
"""
from __future__ import annotations

import re
import sqlite3
from datetime import datetime,timezone
from .access import AccessDenied,TowerScope
from .operations import GroundsConflict,GroundsOperations,_now
from .storage import GroundsStoreBase

_REF=re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}$")
_STAFF=frozenset(("owner","property_manager","maintenance_supervisor"))
_ALLOWED=_STAFF|{"resident","maintenance_technician"}


class GroundsWorkThread:
    def __init__(self,store:GroundsStoreBase):
        self.store=store
        self.ops=GroundsOperations(store)

    def _scope(self,actor,db,work_ref):
        actor=self.ops._scope(actor)
        row=self.ops._visible_order(db,actor,work_ref)
        if actor.role not in _ALLOWED:
            raise AccessDenied("work conversation unavailable")
        return actor,row

    def post(self,actor:TowerScope,*,work_ref:str,message_ref:str,
             body:str,audience:str="shared")->dict:
        if not isinstance(message_ref,str) or not _REF.fullmatch(message_ref):
            raise GroundsConflict("invalid conversation reference")
        if not isinstance(body,str) or not body.strip() or len(body)>1200 or "\x00" in body:
            raise GroundsConflict("message must have 1 to 1200 plain-text characters")
        body=body.strip()
        if audience not in ("shared","staff_internal"):
            raise GroundsConflict("invalid conversation audience")
        if not isinstance(work_ref,str) or not _REF.fullmatch(work_ref):
            raise GroundsConflict("invalid work reference")
        timestamp=_now()
        with self.store.transaction(write=True) as db:
            actor,row=self._scope(actor,db,work_ref)
            if audience=="staff_internal" and actor.role not in _STAFF:
                raise AccessDenied("staff-only note unavailable")
            if row["state"]=="closed":
                raise GroundsConflict("closed work does not accept new conversation posts")
            # Read the exact idempotency identity BEFORE attempting an INSERT.
            # A PostgreSQL uniqueness violation aborts its transaction; do
            # not query inside an already-aborted PG transaction on retry.
            prior=db.execute(
                """SELECT work_ref,property_ref,author_ref,author_role,audience,body
                   FROM work_messages WHERE message_ref=?""",(message_ref,),
            ).fetchone()
            if prior is not None:
                if (prior["work_ref"]!=work_ref or prior["property_ref"]!=row["property_ref"]
                    or prior["author_ref"]!=actor.subject_ref or prior["author_role"]!=actor.role
                    or prior["audience"]!=audience or prior["body"]!=body):
                    raise GroundsConflict("conversation retry mismatched")
                return {"message_ref":message_ref,"work_ref":work_ref,
                        "posted_in_grounds":True,"replayed":True,
                        "external_notification_delivered":False,
                        "legal_notice_proven":False}
            try:
                db.execute(
                    """INSERT INTO work_messages
                       (message_ref,work_ref,property_ref,author_ref,author_role,audience,body,created_at)
                       VALUES(?,?,?,?,?,?,?,?)""",
                    (message_ref,work_ref,row["property_ref"],actor.subject_ref,
                     actor.role,audience,body,timestamp),
                )
            except sqlite3.IntegrityError as exc:
                # Competing transaction or constraint: rollback and require an
                # externally replayed idempotent request, never continue on PG.
                raise GroundsConflict("conversation insert conflicted; retry exact key") from exc
        return {"message_ref":message_ref,"work_ref":work_ref,
                "posted_in_grounds":True,"replayed":False,
                "external_notification_delivered":False,
                "legal_notice_proven":False}

    def thread(self,actor:TowerScope,*,work_ref:str)->dict:
        with self.store.transaction() as db:
            actor,row=self._scope(actor,db,work_ref)
            staff=actor.role in _STAFF
            predicate="" if staff else " AND audience='shared'"
            count=db.execute(
                "SELECT COUNT(*) FROM work_messages WHERE work_ref=?"+predicate,
                (work_ref,),
            ).fetchone()[0]
            rows=[dict(r) for r in db.execute(
                """SELECT message_ref,author_role,audience,body,created_at
                   FROM work_messages WHERE work_ref=?"""+predicate+
                " ORDER BY created_at DESC,message_ref DESC LIMIT 100",
                (work_ref,),
            )]
            history_count=db.execute(
                "SELECT COUNT(*) FROM work_events WHERE work_ref=?",(work_ref,),
            ).fetchone()[0]
            history=[dict(r) for r in db.execute(
                """SELECT action,from_state,to_state,revision,occurred_at
                   FROM work_events WHERE work_ref=?
                   ORDER BY revision DESC LIMIT 100""",(work_ref,),
            )]
            receipts=db.execute(
                """SELECT COUNT(DISTINCT r.event_ref) FROM event_delivery_receipts r
                   JOIN event_outbox e ON e.event_ref=r.event_ref
                   WHERE e.property_ref=? AND e.resource_ref=?
                     AND r.receipt_kind='notification_delivery'
                     AND r.delivery_state='delivered'""",
                (row["property_ref"],work_ref),
            ).fetchone()[0]
            completions=[dict(r) for r in db.execute(
                """SELECT outcome,note,resulting_state,recorded_at
                   FROM work_completion_events WHERE work_ref=?
                   ORDER BY to_revision,recorded_at""",(work_ref,),
            )]
        messages=list(reversed(rows))
        # Timeline is a derived read-only projection. Never reveal the internal
        # author's subject ID or protected staff notes to resident/technician.
        timeline=[
            {"kind":"state","state":h["to_state"],"action":h["action"],
             "occurred_at":h["occurred_at"]} for h in history
        ]+[
            {"kind":"message","role":m["author_role"],"body":m["body"],
             "audience":m["audience"],"occurred_at":m["created_at"]} for m in messages
        ]+[
            {"kind":"resident_completion","outcome":x["outcome"],
             "note":x["note"],"state":x["resulting_state"],
             "occurred_at":x["recorded_at"]} for x in completions
        ]
        timeline.sort(key=lambda item:item["occurred_at"])
        return {
            "source":"grounds","work_ref":work_ref,"property_ref":row["property_ref"],
            "unit_ref":row["unit_ref"],"state":row["state"],
            "timeline":timeline,"messages":messages,
            "visible_message_count":count,"shown_message_limit":100,
            "messages_truncated":count>len(messages),
            "state_event_count":history_count,
            "state_events_truncated":history_count>len(history),
            "can_post":row["state"]!="closed",
            "can_post_staff_internal":staff and row["state"]!="closed",
            "in_app_post_is_not_external_delivery":True,
            "verified_historical_delivered_event_count":receipts,
            "resident_completion_response_count":len(completions),
            "latest_resident_completion_response":(
                completions[-1] if completions else None
            ),
            "provider_currently_connected":False,
            "emergency_services_contacted":False,"entry_authorized":False,
        }
