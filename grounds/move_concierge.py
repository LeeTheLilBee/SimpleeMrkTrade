"""GRD181–189: lease-scoped resident self-reported move planning, never legal close.

No key custody, inventory certification, deposit decision, lease termination,
utilities account opening, real calendar booking, address collection or Vault
upload is performed by a checklist toggle.
"""
from __future__ import annotations

import re
import sqlite3
from datetime import date,timedelta

from .access import AccessDenied,TowerScope
from .operations import GroundsConflict,GroundsOperations,_now
from .storage import GroundsStoreBase

_TASKS={
    "move_in":(
        ("welcome_reviewed","Review your recorded home and welcome information",
         "Confirm only that you reviewed the information in Grounds."),
        ("utilities_plan_reviewed","Plan utilities and service contacts",
         "Do not enter account numbers or passwords in Grounds."),
        ("key_collection_arranged","Plan how you will collect keys",
         "A checklist mark never proves actual key custody or building access."),
        ("condition_notes_prepared","Prepare initial condition notes",
         "A signed inspection/photo needs independent Tower/Vault evidence."),
    ),
    "move_out":(
        ("departure_plan_reviewed","Review your tentative departure plan",
         "This does not end or amend your lease."),
        ("walkthrough_request_prepared","Plan a walkthrough discussion",
         "An actual appointment requires the separately authorized workflow."),
        ("keys_return_plan","Plan how keys will be returned",
         "A mark is not staff-confirmed key receipt."),
        ("forwarding_details_reserved_for_vault","Plan private forwarding details",
         "Do not type addresses here; any later collection belongs to protected Vault."),
    ),
}
_REF=re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}$")


class GroundsMoveConcierge:
    def __init__(self,store:GroundsStoreBase):
        self.store=store
        self.ops=GroundsOperations(store)

    def resident_checklist(self,actor:TowerScope,*,property_ref:str,unit_ref:str)->dict:
        actor=self.ops._scope(actor)
        home=self.ops.resident_home(actor,property_ref=property_ref,unit_ref=unit_ref)
        lease_ref=home["lease"]["lease_ref"]
        with self.store.transaction() as db:
            events=[dict(r) for r in db.execute(
                """SELECT phase,task_ref,status,revision,recorded_at FROM move_task_events
                   WHERE lease_ref=? AND property_ref=? AND unit_ref=? AND subject_ref=?
                   ORDER BY revision DESC,recorded_at DESC""",
                (lease_ref,property_ref,unit_ref,actor.subject_ref),
            )]
        latest={}
        for event in events:
            key=(event["phase"],event["task_ref"])
            if key not in latest:latest[key]=event
        phases=[]
        for phase,definitions in _TASKS.items():
            tasks=[]
            for ref,label,hint in definitions:
                row=latest.get((phase,ref))
                tasks.append({
                    "task_ref":ref,"label":label,"hint":hint,
                    "status":row["status"] if row else "not_started",
                    "revision":row["revision"] if row else 0,
                    "last_self_reported_at":row["recorded_at"] if row else None,
                    "staff_or_legal_verification":False,
                })
            phases.append({
                "phase":phase,"tasks":tasks,
                "self_reported_done_count":sum(t["status"]=="self_reported_done" for t in tasks),
                "task_count":len(tasks),
                "completion_is_not_legal_move_authorization":True,
            })
        return {
            "source":"grounds","room":"move_concierge",
            "property_ref":property_ref,"unit_ref":unit_ref,"lease_ref":lease_ref,
            "lease_end_on":home["lease"]["end_on"],"phases":phases,
            "amount_due_cents":None,"deposit_return_approved":False,
            "lease_end_recorded":False,"keys_received_confirmed":False,
            "vault_condition_evidence_connected":False,"notifications_delivered":False,
            "staff_inspection_signed_off":False,
        }

    def mark_task(self,actor:TowerScope,*,property_ref:str,unit_ref:str,
                  phase:str,task_ref:str,status:str,expected_revision:int,
                  event_ref:str)->dict:
        if phase not in _TASKS or task_ref not in {t[0] for t in _TASKS[phase]}:
            raise GroundsConflict("unrecognized move planning task")
        if status not in ("planned","self_reported_done"):
            raise GroundsConflict("invalid self-reported planning status")
        if type(expected_revision) is not int or not 0<=expected_revision<=2147483647:
            raise GroundsConflict("invalid planning revision")
        if not isinstance(event_ref,str) or _REF.fullmatch(event_ref) is None:
            raise GroundsConflict("invalid planning event")
        actor=self.ops._scope(actor)
        with self.store.transaction(write=True) as db:
            lease=self.ops._resident_lease(db,actor,property_ref,unit_ref)
            lease_ref=lease["lease_ref"]
            prior=db.execute(
                """SELECT lease_ref,property_ref,unit_ref,subject_ref,phase,task_ref,status,revision
                   FROM move_task_events WHERE event_ref=?""",(event_ref,),
            ).fetchone()
            if prior is not None:
                if (prior["lease_ref"]!=lease_ref or prior["property_ref"]!=property_ref
                    or prior["unit_ref"]!=unit_ref or prior["subject_ref"]!=actor.subject_ref
                    or prior["phase"]!=phase or prior["task_ref"]!=task_ref
                    or prior["status"]!=status or prior["revision"]!=expected_revision+1):
                    raise GroundsConflict("changed move planning replay")
                return {"event_ref":event_ref,"revision":prior["revision"],
                        "status":status,"replayed":True,
                        "self_reported_only":True,"staff_or_legal_verification":False}
            latest=db.execute(
                """SELECT status,revision FROM move_task_events
                   WHERE lease_ref=? AND subject_ref=? AND phase=? AND task_ref=?
                   ORDER BY revision DESC LIMIT 1""",
                (lease_ref,actor.subject_ref,phase,task_ref),
            ).fetchone()
            current=latest["revision"] if latest else 0
            current_status=latest["status"] if latest else "not_started"
            if current!=expected_revision or current_status==status:
                raise GroundsConflict("stale or unchanged move planning update")
            try:
                db.execute(
                    """INSERT INTO move_task_events
                       (event_ref,lease_ref,property_ref,unit_ref,subject_ref,
                        phase,task_ref,status,revision,recorded_at)
                       VALUES(?,?,?,?,?,?,?,?,?,?)""",
                    (event_ref,lease_ref,property_ref,unit_ref,actor.subject_ref,
                     phase,task_ref,status,current+1,_now()),
                )
            except sqlite3.IntegrityError as exc:
                raise GroundsConflict("move planning update conflicted; retry exact event") from exc
        return {"event_ref":event_ref,"revision":current+1,
                "status":status,"replayed":False,
                "self_reported_only":True,"staff_or_legal_verification":False}

    def staff_move_desk(self,actor:TowerScope,*,property_ref:str)->dict:
        actor=self.ops._scope(actor)
        actor.require_role("owner","property_manager")
        actor.require_property(property_ref)
        today=date.today()
        horizon=(today+timedelta(days=60)).isoformat()
        with self.store.transaction() as db:
            prop=db.execute(
                "SELECT name FROM properties WHERE property_ref=?",(property_ref,),
            ).fetchone()
            if prop is None:raise AccessDenied("property unavailable")
            count=db.execute(
                """SELECT COUNT(*) FROM leases WHERE property_ref=? AND status='active'
                   AND end_on>=? AND end_on<=?""",(property_ref,today.isoformat(),horizon),
            ).fetchone()[0]
            ready=db.execute(
                """SELECT COUNT(*) FROM units WHERE property_ref=? AND lifecycle='make_ready'""",
                (property_ref,),
            ).fetchone()[0]
            turnovers=db.execute(
                """SELECT COUNT(*) FROM turnovers WHERE property_ref=? AND state!='complete'""",
                (property_ref,),
            ).fetchone()[0]
            inspections=db.execute(
                """SELECT COUNT(*) FROM inspections WHERE property_ref=?
                   AND category='turnover' AND state!='closed'""",(property_ref,),
            ).fetchone()[0]
        return {
            "source":"grounds","room":"move_desk","property_ref":property_ref,
            "property_name":prop["name"],
            "active_leases_with_recorded_end_within_60_days":count,
            "units_in_make_ready":ready,"unfinished_turnovers":turnovers,
            "open_recorded_turnover_inspections":inspections,
            "resident_identity_included":False,"future_renewal_or_termination_assumed":False,
            "deposit_decision_authorized":False,"keys_return_verified":False,
            "notification_delivery_proven":False,
        }
