"""GRD058 — append-only maintenance materials/time, not a financial ledger.

All reads/writes recheck the verified TowerScope AND actual work assignment.
This is a developer-only physical work record, never Teller invoice/payroll
truth, actual inventory procurement, a vendor payment, or proof of a repair.
Reversals preserve the original entry and require a scoped human manager.
"""
from __future__ import annotations

import sqlite3
from uuid import uuid4

from .access import AccessDenied, TowerScope
from .operations import GroundsConflict, GroundsOperations, _now, _required
from .storage import GroundsStoreBase


STAFF = frozenset(("owner","property_manager","maintenance_supervisor","maintenance_technician"))


class GroundsWorkResources:
    def __init__(self,store:GroundsStoreBase):
        if not isinstance(store,GroundsStoreBase):
            raise TypeError("transaction-backed Grounds store required")
        self.store=store
        self.ops=GroundsOperations(store)

    def _work(self,db,actor:TowerScope,work_ref:str):
        actor.require_role(*sorted(STAFF))
        return self.ops._visible_order(db,actor,work_ref)

    def record(self,actor:TowerScope,*,work_ref:str,resource_type:str,
               label:str,quantity:int,event_ref:str|None=None)->dict:
        actor=self.ops._scope(actor)
        if resource_type not in ("material","labor"):
            raise GroundsConflict("resource type invalid")
        label=_required(label,"resource label",max_length=160)
        if type(quantity) is not int or not 1 <= quantity <= 1000000:
            raise GroundsConflict("resource quantity invalid")
        ref=_required(event_ref or uuid4().hex,"event_ref",max_length=128)
        unit="items" if resource_type=="material" else "minutes"
        with self.store.transaction(write=True) as db:
            work=self._work(db,actor,work_ref)
            if work["state"] in ("closed","confirmation","submitted","received","under_review","scheduled","assigned","reopened"):
                raise GroundsConflict("resource log not open at this work stage")
            if actor.role=="maintenance_technician" and work["state"] not in ("in_progress","waiting"):
                raise GroundsConflict("technician work log requires active or waiting job")
            try:
                db.execute(
                    """INSERT INTO work_resource_events
                       (event_ref,work_ref,property_ref,unit_ref,action,resource_type,label,
                        quantity,quantity_unit,recorded_by,recorded_at)
                       VALUES(?,?,?,?,'record',?,?,?,?,?,?)""",
                    (ref,work_ref,work["property_ref"],work["unit_ref"],
                     resource_type,label,quantity,unit,actor.subject_ref,_now()),
                )
            except sqlite3.IntegrityError as exc:
                raise GroundsConflict("resource event duplicate or invalid") from exc
            return {"event_ref":ref,"work_ref":work_ref,"resource_type":resource_type,
                    "quantity":quantity,"unit":unit,"financial_amount":None,
                    "inventory_reservation_created":False,"payroll_entry_created":False}

    def reverse(self,actor:TowerScope,*,work_ref:str,original_event_ref:str,
                reversal_ref:str|None=None)->dict:
        actor=self.ops._scope(actor)
        actor.require_role("owner","property_manager","maintenance_supervisor")
        ref=_required(reversal_ref or uuid4().hex,"reversal_ref",max_length=128)
        with self.store.transaction(write=True) as db:
            work=self._work(db,actor,work_ref)
            if work["state"] in ("closed","confirmation"):
                raise GroundsConflict("closed/confirming work must be reopened before correction")
            original=db.execute(
                """SELECT * FROM work_resource_events
                   WHERE event_ref=? AND work_ref=? AND property_ref=? AND unit_ref=?""",
                (original_event_ref,work_ref,work["property_ref"],work["unit_ref"]),
            ).fetchone()
            if original is None:
                raise AccessDenied("original resource event unavailable")
            if original["action"]!="record":
                raise GroundsConflict("cannot reverse a reversal")
            try:
                db.execute(
                    """INSERT INTO work_resource_events
                       (event_ref,work_ref,property_ref,unit_ref,action,resource_type,label,
                        quantity,quantity_unit,reverses_event_ref,recorded_by,recorded_at)
                       VALUES(?,?,?,?,'reverse',?,?,?,?,?,?,?)""",
                    (ref,work_ref,work["property_ref"],work["unit_ref"],
                     original["resource_type"],original["label"],original["quantity"],
                     original["quantity_unit"],original_event_ref,actor.subject_ref,_now()),
                )
            except sqlite3.IntegrityError as exc:
                raise GroundsConflict("resource reversal duplicate or invalid") from exc
            return {"event_ref":ref,"reversed_event_ref":original_event_ref,
                    "work_ref":work_ref,"financial_adjustment_executed":False}

    def history(self,actor:TowerScope,*,work_ref:str)->list[dict]:
        actor=self.ops._scope(actor)
        with self.store.transaction() as db:
            self._work(db,actor,work_ref)
            return [dict(row) for row in db.execute(
                """SELECT event_ref,resource_type,label,quantity,quantity_unit,
                          action,reverses_event_ref,recorded_by,recorded_at
                   FROM work_resource_events WHERE work_ref=?
                   ORDER BY recorded_at,event_ref""",(work_ref,),
            )]

    def summary(self,actor:TowerScope,*,work_ref:str)->dict:
        actor=self.ops._scope(actor)
        with self.store.transaction() as db:
            work=self._work(db,actor,work_ref)
            row=db.execute(
                """SELECT COUNT(*) AS events,
                     COALESCE(SUM(CASE WHEN resource_type='material'
                       THEN CASE WHEN action='record' THEN quantity ELSE -quantity END
                       ELSE 0 END),0) AS material_items,
                     COALESCE(SUM(CASE WHEN resource_type='labor'
                       THEN CASE WHEN action='record' THEN quantity ELSE -quantity END
                       ELSE 0 END),0) AS labor_minutes
                   FROM work_resource_events WHERE work_ref=?""",(work_ref,),
            ).fetchone()
            return {"source":"grounds","work_ref":work_ref,
                    "source_work_revision":work["revision"],
                    "resource_event_count":row["events"],
                    "net_material_items":row["material_items"],
                    "net_labor_minutes":row["labor_minutes"],
                    "inventory_balance":None,"labor_cost":None,"invoice_total":None,
                    "teller_connected":False}
