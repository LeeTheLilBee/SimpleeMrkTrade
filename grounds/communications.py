"""GRD042 — resident notices/read state and in-app maintenance appointments.

This is NOT notification delivery, lease-entry authorization or legal service.
No email, SMS, push, worker dispatch, calendar, keys or payment API is called.
A resident request and later slot acceptance do NOT imply permission to enter;
notice-read marks only a local UI action and cannot prove receipt/legal service.
"""
from __future__ import annotations

import sqlite3
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from .access import AccessDenied, TowerScope
from .operations import GroundsOperations, GroundsConflict, _now, _required
from .storage import GroundsStore


def _slot(start_at: str, end_at: str) -> tuple[str,str]:
    try:
        start=datetime.fromisoformat(start_at)
        end=datetime.fromisoformat(end_at)
        if (start.tzinfo is None or start.utcoffset() is None
            or end.tzinfo is None or end.utcoffset() is None):
            raise ValueError
        utc_start=start.astimezone(timezone.utc)
        utc_end=end.astimezone(timezone.utc)
        seconds=(utc_end-utc_start).total_seconds()
        now=datetime.now(timezone.utc)
        if (utc_start<=now or utc_start>now+timedelta(days=366)
            or not 0<seconds<=8*3600):
            raise ValueError
        return utc_start.isoformat(),utc_end.isoformat()
    except (ValueError,TypeError,OverflowError) as exc:
        raise GroundsConflict("appointment requires a timezone-aware window within 366 days, lasting at most 8 hours") from exc


class GroundsCommunications:
    def __init__(self,store:GroundsStore):
        if not isinstance(store,GroundsStore):
            raise TypeError("GroundsStore required")
        self.store=store
        self.ops=GroundsOperations(store)

    def mark_notice_read(self,actor:TowerScope,*,property_ref:str,
                         unit_ref:str,notice_ref:str)->dict:
        actor=self.ops._scope(actor)
        actor.require_role("resident")
        actor.require_unit(property_ref,unit_ref)
        _required(notice_ref,"notice_ref",max_length=128)
        with self.store.transaction(write=True) as db:
            lease=self.ops._resident_lease(db,actor,property_ref,unit_ref)
            notice=db.execute(
                """SELECT 1 FROM property_notices WHERE notice_ref=? AND property_ref=?
                   AND (unit_ref IS NULL OR (unit_ref=? AND lease_ref=?))""",
                (notice_ref,property_ref,unit_ref,lease["lease_ref"]),
            ).fetchone()
            if notice is None:
                raise AccessDenied("notice unavailable")
            db.execute(
                """INSERT INTO notice_reads
                   (notice_ref,subject_ref,lease_ref,property_ref,unit_ref,read_at)
                   VALUES(?,?,?,?,?,?)
                   ON CONFLICT(notice_ref,lease_ref,subject_ref) DO NOTHING""",
                (notice_ref,actor.subject_ref,lease["lease_ref"],property_ref,unit_ref,_now()),
            )
            return {"notice_ref":notice_ref,"read_in_app":True,
                    "delivery_confirmed":False,"legal_service_proven":False}

    def request_appointment(self,actor:TowerScope,*,work_ref:str,
                            appointment_ref:str,start_at:str,end_at:str)->dict:
        actor=self.ops._scope(actor)
        actor.require_role("resident")
        _required(appointment_ref,"appointment_ref",max_length=128)
        start,end=_slot(start_at,end_at)
        with self.store.transaction(write=True) as db:
            order=self.ops._visible_order(db,actor,work_ref)
            if order["state"]=="closed":
                raise GroundsConflict("closed work order cannot be scheduled")
            if db.execute(
                """SELECT 1 FROM work_appointments
                   WHERE work_ref=? AND state!='cancelled' LIMIT 1""",(work_ref,),
            ).fetchone():
                raise GroundsConflict("an open appointment already exists")
            try:
                db.execute(
                    """INSERT INTO work_appointments
                       (appointment_ref,work_ref,property_ref,unit_ref,requested_by,
                        start_at,end_at,state,updated_at)
                       VALUES(?,?,?,?,?,?,?,'requested',?)""",
                    (appointment_ref,work_ref,order["property_ref"],order["unit_ref"],
                     actor.subject_ref,start,end,_now()),
                )
            except sqlite3.IntegrityError as exc:
                raise GroundsConflict("appointment duplicate or invalid") from exc
            self._event(db,appointment_ref,actor,"requested",1)
            return {"appointment_ref":appointment_ref,"state":"requested","revision":1,
                    "dispatch_confirmed":False,"entry_consent_granted":False}

    @staticmethod
    def _event(db,ref,actor,state,revision):
        db.execute(
            """INSERT INTO appointment_events
               (event_ref,appointment_ref,actor_ref,action,revision,recorded_at)
               VALUES(?,?,?,?,?,?)""",
            (uuid4().hex,ref,actor.subject_ref,state,revision,_now()),
        )

    def _visible(self,db,actor,appointment_ref):
        item=db.execute(
            """SELECT a.*,w.created_by,w.assigned_to,w.lease_ref AS work_lease_ref,
                      w.state AS work_state
               FROM work_appointments a JOIN work_orders w ON w.work_ref=a.work_ref
               WHERE a.appointment_ref=?""",(appointment_ref,),
        ).fetchone()
        if item is None or item["property_ref"] not in actor.property_refs:
            raise AccessDenied("appointment unavailable")
        if actor.role=="resident":
            if item["requested_by"]!=actor.subject_ref or item["created_by"]!=actor.subject_ref:
                raise AccessDenied("appointment unavailable")
            # Recheck the *exact work lease*, not only current occupancy of the unit.
            self.ops._visible_order(db,actor,item["work_ref"])
        elif actor.role=="maintenance_technician":
            if item["assigned_to"]!=actor.subject_ref or item["work_ref"] not in actor.assigned_work_refs:
                raise AccessDenied("appointment unavailable")
        elif actor.role not in ("owner","property_manager","maintenance_supervisor"):
            raise AccessDenied("appointment unavailable")
        return item

    def appointment(self,actor:TowerScope,*,appointment_ref:str)->dict:
        actor=self.ops._scope(actor)
        with self.store.transaction() as db:
            item=self._visible(db,actor,appointment_ref)
            return {
                key:item[key] for key in (
                    "appointment_ref","work_ref","property_ref","unit_ref",
                    "start_at","end_at","state","revision"
                )
            } | {"entry_consent_granted":False,"calendar_synced":False}

    def propose_appointment(self,actor:TowerScope,*,appointment_ref:str,
                            start_at:str,end_at:str,expected_revision:int)->dict:
        actor=self.ops._scope(actor)
        actor.require_role("owner","property_manager","maintenance_supervisor")
        start,end=_slot(start_at,end_at)
        with self.store.transaction(write=True) as db:
            item=self._visible(db,actor,appointment_ref)
            if item["state"]!="requested" or item["revision"]!=expected_revision:
                raise GroundsConflict("appointment state or revision changed")
            if item["work_state"]=="closed":
                raise GroundsConflict("closed work order cannot be scheduled")
            # A different active lease for the same person/unit cannot revive an
            # old lease's request or appointment.
            member=db.execute(
                """SELECT 1 FROM lease_members m JOIN leases l ON l.lease_ref=m.lease_ref
                   WHERE m.subject_ref=? AND m.property_ref=? AND m.unit_ref=?
                     AND m.lease_ref=? AND m.status='active' AND l.status='active'""",
                (item["requested_by"],item["property_ref"],item["unit_ref"],
                 item["work_lease_ref"]),
            ).fetchone()
            if member is None:
                raise AccessDenied("resident membership no longer active")
            revision=expected_revision+1
            db.execute(
                """UPDATE work_appointments
                   SET state='proposed',start_at=?,end_at=?,revision=?,updated_at=?
                   WHERE appointment_ref=?""",
                (start,end,revision,_now(),appointment_ref),
            )
            self._event(db,appointment_ref,actor,"proposed",revision)
            return {"appointment_ref":appointment_ref,"state":"proposed","revision":revision,
                    "notification_sent":False,"entry_consent_granted":False}

    def accept_appointment(self,actor:TowerScope,*,appointment_ref:str,
                           expected_revision:int)->dict:
        actor=self.ops._scope(actor)
        actor.require_role("resident")
        with self.store.transaction(write=True) as db:
            item=self._visible(db,actor,appointment_ref)
            if item["state"]!="proposed" or item["revision"]!=expected_revision:
                raise GroundsConflict("appointment state or revision changed")
            if item["work_state"]=="closed":
                raise GroundsConflict("closed work order cannot be scheduled")
            if datetime.fromisoformat(item["start_at"])<=datetime.now(timezone.utc):
                raise GroundsConflict("appointment window elapsed")
            revision=expected_revision+1
            db.execute(
                """UPDATE work_appointments SET state='accepted',revision=?,updated_at=?
                   WHERE appointment_ref=?""",
                (revision,_now(),appointment_ref),
            )
            self._event(db,appointment_ref,actor,"accepted",revision)
            return {"appointment_ref":appointment_ref,"state":"accepted","revision":revision,
                    "entry_consent_granted":False,"dispatch_confirmed":False,
                    "legal_entry_notice_proven":False}

    def cancel_appointment(self,actor:TowerScope,*,appointment_ref:str,
                           expected_revision:int)->dict:
        actor=self.ops._scope(actor)
        with self.store.transaction(write=True) as db:
            item=self._visible(db,actor,appointment_ref)
            if actor.role not in ("resident","owner","property_manager","maintenance_supervisor"):
                raise AccessDenied("appointment cancellation not authorized")
            if item["state"]=="cancelled" or item["revision"]!=expected_revision:
                raise GroundsConflict("appointment cancellation stale or already recorded")
            revision=expected_revision+1
            db.execute(
                """UPDATE work_appointments SET state='cancelled',revision=?,updated_at=?
                   WHERE appointment_ref=?""",
                (revision,_now(),appointment_ref),
            )
            self._event(db,appointment_ref,actor,"cancelled",revision)
            return {"appointment_ref":appointment_ref,"state":"cancelled","revision":revision,
                    "notification_sent":False}

    def appointments_for_work(self,actor:TowerScope,*,work_ref:str)->list[dict]:
        """Read-only, exact-current-work/lease- or staff-assignment-scoped history.

        Cancelled appointment history remains visible only to the requester
        while that *same original lease* is active, or authorized scoped staff.
        Never returns resident identity or legal entry authorization.
        """
        actor=self.ops._scope(actor)
        with self.store.transaction() as db:
            self.ops._visible_order(db,actor,work_ref)
            if actor.role=="resident":
                rows=db.execute(
                    """SELECT appointment_ref,work_ref,start_at,end_at,state,revision
                       FROM work_appointments
                       WHERE work_ref=? AND requested_by=?
                       ORDER BY updated_at DESC,appointment_ref DESC LIMIT 50""",
                    (work_ref,actor.subject_ref),
                )
            else:
                rows=db.execute(
                    """SELECT appointment_ref,work_ref,start_at,end_at,state,revision
                       FROM work_appointments WHERE work_ref=?
                       ORDER BY updated_at DESC,appointment_ref DESC LIMIT 50""",
                    (work_ref,),
                )
            return [dict(row) for row in rows]

    def history(self,actor:TowerScope,*,appointment_ref:str)->list[dict]:
        actor=self.ops._scope(actor)
        with self.store.transaction() as db:
            self._visible(db,actor,appointment_ref)
            return [dict(row) for row in db.execute(
                """SELECT action,revision,recorded_at FROM appointment_events
                   WHERE appointment_ref=? ORDER BY revision""",(appointment_ref,),
            )]
