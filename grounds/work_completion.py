"""GRD212–216: current-lease resident maintenance completion response.

Residents may explicitly acknowledge that work in the `confirmation` state
looks resolved, or say it still needs attention. This is a Grounds workflow
record only: it is not a waiver, release of legal rights, inspection approval,
payment authorization, provider certification or proof of external notice.

Only the current original requester on the active lease may respond. The
response and work-state change are transactional and idempotent.
"""
from __future__ import annotations

import re
import sqlite3

from .access import AccessDenied, TowerScope
from .operations import GroundsConflict, GroundsOperations, _event, _outbox, _now
from .storage import GroundsStoreBase

_REF=re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}$")
_OUTCOMES=frozenset(("resolved","still_needs_attention"))


class GroundsWorkCompletion:
    def __init__(self,store:GroundsStoreBase):
        if not isinstance(store,GroundsStoreBase):
            raise TypeError("transaction-backed Grounds store required")
        self.store=store
        self.ops=GroundsOperations(store)

    def respond(self,actor:TowerScope,*,work_ref:str,outcome:str,
                expected_revision:int,event_ref:str,note:str="")->dict:
        actor=self.ops._scope(actor)
        actor.require_role("resident")
        if not isinstance(work_ref,str) or _REF.fullmatch(work_ref) is None:
            raise GroundsConflict("invalid work reference")
        if outcome not in _OUTCOMES:
            raise GroundsConflict("invalid resident completion outcome")
        if type(expected_revision) is not int or expected_revision<1:
            raise GroundsConflict("invalid work revision")
        if not isinstance(event_ref,str) or _REF.fullmatch(event_ref) is None:
            raise GroundsConflict("invalid completion response reference")
        if not isinstance(note,str) or len(note)>800 or "\x00" in note:
            raise GroundsConflict("completion note must be at most 800 plain-text characters")
        note=note.strip()
        target="closed" if outcome=="resolved" else "reopened"
        now=_now()
        with self.store.transaction(write=True) as db:
            row=self.ops._visible_order(db,actor,work_ref)
            prior=db.execute(
                """SELECT work_ref,property_ref,unit_ref,lease_ref,resident_ref,
                          outcome,note,from_revision,to_revision,resulting_state
                   FROM work_completion_events WHERE event_ref=?""",(event_ref,),
            ).fetchone()
            if prior is not None:
                if (prior["work_ref"]!=work_ref or prior["resident_ref"]!=actor.subject_ref
                    or prior["outcome"]!=outcome or prior["note"]!=note
                    or prior["from_revision"]!=expected_revision
                    or prior["resulting_state"]!=target):
                    raise GroundsConflict("changed resident completion retry")
                return {
                    "event_ref":event_ref,"work_ref":work_ref,
                    "outcome":outcome,"state":prior["resulting_state"],
                    "revision":prior["to_revision"],"replayed":True,
                    "resident_feedback_recorded":True,
                    "legal_waiver_created":False,"inspection_certified":False,
                    "provider_delivery_proven":False,
                }
            if row["state"]!="confirmation":
                raise GroundsConflict("work is not awaiting resident confirmation")
            if row["revision"]!=expected_revision:
                raise GroundsConflict("stale work completion revision")
            revision=expected_revision+1
            try:
                db.execute(
                    """INSERT INTO work_completion_events
                       (event_ref,work_ref,property_ref,unit_ref,lease_ref,resident_ref,
                        outcome,note,from_revision,to_revision,resulting_state,recorded_at)
                       VALUES(?,?,?,?,?,?,?,?,?,?,?,?)""",
                    (event_ref,work_ref,row["property_ref"],row["unit_ref"],row["lease_ref"],
                     actor.subject_ref,outcome,note,expected_revision,revision,target,now),
                )
                result=db.execute(
                    """UPDATE work_orders SET state=?,revision=?,updated_at=?
                       WHERE work_ref=? AND revision=? AND state='confirmation'""",
                    (target,revision,now,work_ref,expected_revision),
                )
                if getattr(result,"rowcount",0)!=1:
                    raise GroundsConflict("work completion state changed; refresh")
                _event(db,work_ref,actor,"resident_completion",row["state"],target,revision)
                _outbox(db,property_ref=row["property_ref"],
                        event_kind="work_changed",resource_ref=work_ref,revision=revision)
            except sqlite3.IntegrityError as exc:
                raise GroundsConflict("resident completion response conflicted; retry exact event") from exc
        return {
            "event_ref":event_ref,"work_ref":work_ref,"outcome":outcome,
            "state":target,"revision":revision,"replayed":False,
            "resident_feedback_recorded":True,
            "legal_waiver_created":False,"inspection_certified":False,
            "provider_delivery_proven":False,
        }

    def status(self,actor:TowerScope,*,work_ref:str)->dict:
        actor=self.ops._scope(actor)
        with self.store.transaction() as db:
            row=self.ops._visible_order(db,actor,work_ref)
            latest=db.execute(
                """SELECT outcome,note,resulting_state,recorded_at
                   FROM work_completion_events WHERE work_ref=?
                   ORDER BY to_revision DESC,recorded_at DESC LIMIT 1""",
                (work_ref,),
            ).fetchone()
        return {
            "source":"grounds","work_ref":work_ref,
            "state":row["state"],"awaiting_resident_confirmation":row["state"]=="confirmation",
            "latest_resident_response":(
                {"outcome":latest["outcome"],"note":latest["note"],
                 "resulting_state":latest["resulting_state"],"recorded_at":latest["recorded_at"]}
                if latest is not None else None
            ),
            "legal_waiver_created":False,"inspection_certified":False,
            "payment_or_deposit_effect":False,
        }
