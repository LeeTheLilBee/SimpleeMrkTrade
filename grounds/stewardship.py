"""GRD025–028: source-only physical-asset stewardship and unit turnovers.

No scheduling daemon, emergency dispatch, real inspection sign-off, tenant
notifications, vendor execution, or Vault network connection is created.
TowerScope is an *externally verified* server-side input; test fixtures supply
it only in tests. Certified evidence callbacks must not be user-controlled.
"""
from __future__ import annotations

import sqlite3
from datetime import date, timedelta
from typing import Callable, Mapping
from uuid import uuid4

from .access import AccessDenied, TowerScope
from .operations import GroundsConflict, GroundsOperations, _date, _now, _required
from .storage import GroundsStoreBase


def _verified_proof(verifier: Callable[[object], Mapping], message: object,
                    *, kind: str, expected: Mapping[str, str]) -> str:
    if not callable(verifier):
        raise AccessDenied("certified proof verifier required")
    try:
        value = verifier(message)
    except Exception as exc:
        raise AccessDenied("proof rejected") from exc
    if (not isinstance(value, Mapping) or value.get("status") != "verified_sealed"
        or value.get("source") != "vault" or value.get("audience") != "grounds"
        or value.get("kind") != kind):
        raise AccessDenied("proof rejected")
    for name, bound in expected.items():
        if value.get(name) != bound:
            raise AccessDenied("proof/scope mismatch")
    return _required(value.get("proof_ref"), "proof_ref", max_length=128)


class GroundsStewardship:
    def __init__(self, store: GroundsStoreBase):
        if not isinstance(store, GroundsStoreBase):
            raise TypeError("transaction-backed Grounds store required")
        self.store = store
        self.ops = GroundsOperations(store)

    def _access(self, actor: TowerScope, property_ref: str, *roles: str) -> TowerScope:
        actor = self.ops._scope(actor)
        actor.require_role(*roles)
        actor.require_property(property_ref)
        return actor

    def record_asset(self, actor: TowerScope, *, property_ref: str, asset_ref: str,
                     label: str, category: str, unit_ref: str | None = None) -> dict:
        self._access(actor,property_ref,"owner","property_manager")
        asset_ref = _required(asset_ref,"asset_ref",max_length=128)
        label = _required(label,"label")
        category = _required(category,"category",max_length=80)
        try:
            with self.store.transaction(write=True) as db:
                db.execute(
                    """INSERT INTO physical_assets
                       (asset_ref,property_ref,unit_ref,label,category,recorded_at)
                       VALUES(?,?,?,?,?,?)""",
                    (asset_ref,property_ref,unit_ref,label,category,_now()),
                )
        except sqlite3.IntegrityError as exc:
            raise GroundsConflict("asset duplicated or unit/property mismatch") from exc
        return {"asset_ref":asset_ref,"property_ref":property_ref,
                "unit_ref":unit_ref,"lifecycle":"active"}

    def physical_workboard(self,actor:TowerScope,*,property_ref:str)->dict:
        """Bounded role-scoped physical backlog, not dispatch or legal sign-off."""
        actor=self._access(
            actor,property_ref,"owner","property_manager","maintenance_supervisor",
        )
        today=date.today().isoformat()
        owner_manager=actor.role in ("owner","property_manager")
        with self.store.transaction() as db:
            asset_count=db.execute(
                "SELECT COUNT(*) FROM physical_assets WHERE property_ref=?",
                (property_ref,),
            ).fetchone()[0]
            assets=[dict(row) for row in db.execute(
                """SELECT asset_ref,unit_ref,label,category,lifecycle
                   FROM physical_assets WHERE property_ref=?
                   ORDER BY label,asset_ref LIMIT 100""",(property_ref,),
            )]
            due_count=db.execute(
                """SELECT COUNT(*) FROM preventive_plans
                   WHERE property_ref=? AND enabled=1 AND next_due_on<=?""",
                (property_ref,today),
            ).fetchone()[0]
            due=[dict(row) for row in db.execute(
                """SELECT plan_ref,asset_ref,next_due_on,cadence_days,revision
                   FROM preventive_plans WHERE property_ref=? AND enabled=1
                     AND next_due_on<=? ORDER BY next_due_on,plan_ref LIMIT 100""",
                (property_ref,today),
            )]
            inspection_count=db.execute(
                """SELECT COUNT(*) FROM inspections WHERE property_ref=? AND state!='closed'""",
                (property_ref,),
            ).fetchone()[0]
            inspections=[dict(row) for row in db.execute(
                """SELECT inspection_ref,unit_ref,category,state,planned_on,revision
                   FROM inspections WHERE property_ref=? AND state!='closed'
                   ORDER BY planned_on,inspection_ref LIMIT 100""",
                (property_ref,),
            )]
            if owner_manager:
                turnover_count=db.execute(
                    """SELECT COUNT(*) FROM turnovers
                       WHERE property_ref=? AND state!='complete'""",
                    (property_ref,),
                ).fetchone()[0]
                turnovers=[dict(row) for row in db.execute(
                    """SELECT turnover_ref,unit_ref,state,revision
                       FROM turnovers WHERE property_ref=? AND state!='complete'
                       ORDER BY turnover_ref LIMIT 100""",
                    (property_ref,),
                )]
            else:
                turnover_count=None
                turnovers=[]
        return {
            "source":"grounds","property_ref":property_ref,"as_of":today,
            "index_limit_per_collection":100,"assets":assets,
            "due_preventive_plans":due,"open_inspections":inspections,
            "open_turnovers":turnovers,
            "counts":{
                "assets":asset_count,"due_preventive_plans":due_count,
                "open_inspections":inspection_count,"open_turnovers":turnover_count,
            },
            "turnover_view_authorized":owner_manager,
            "provider_dispatch_confirmed":False,"inspection_signoff_automated":False,
            "vault_evidence_fetch_connected":False,
            "legal_entry_or_notice_authorized":False,
            "capital_approval_enabled":False,
        }

    def list_assets(self, actor: TowerScope, *, property_ref: str) -> list[dict]:
        self._access(actor,property_ref,"owner","property_manager","maintenance_supervisor")
        with self.store.transaction() as db:
            return [dict(row) for row in db.execute(
                """SELECT asset_ref,unit_ref,label,category,lifecycle
                   FROM physical_assets WHERE property_ref=? ORDER BY label""", (property_ref,),
            )]

    def create_preventive_plan(self, actor: TowerScope, *, property_ref: str,
                               asset_ref: str, plan_ref: str, cadence_days: int,
                               next_due_on: str) -> dict:
        self._access(actor,property_ref,"owner","property_manager","maintenance_supervisor")
        _required(plan_ref,"plan_ref",max_length=128)
        if type(cadence_days) is not int or not 1 <= cadence_days <= 3650:
            raise GroundsConflict("invalid preventive cadence")
        _date(next_due_on)
        try:
            with self.store.transaction(write=True) as db:
                asset = db.execute(
                    "SELECT lifecycle FROM physical_assets WHERE asset_ref=? AND property_ref=?",
                    (asset_ref,property_ref),
                ).fetchone()
                if asset is None or asset["lifecycle"]!="active":
                    raise AccessDenied("active asset unavailable")
                db.execute(
                    """INSERT INTO preventive_plans
                       (plan_ref,property_ref,asset_ref,cadence_days,next_due_on)
                       VALUES(?,?,?,?,?)""",
                    (plan_ref,property_ref,asset_ref,cadence_days,next_due_on),
                )
        except sqlite3.IntegrityError as exc:
            raise GroundsConflict("plan duplicated or invalid") from exc
        return {"plan_ref":plan_ref,"next_due_on":next_due_on,"revision":1,"scheduled":False}

    def due_plans(self, actor: TowerScope, *, property_ref: str, as_of: str) -> list[dict]:
        self._access(actor,property_ref,"owner","property_manager","maintenance_supervisor")
        _date(as_of)
        with self.store.transaction() as db:
            return [dict(row) for row in db.execute(
                """SELECT plan_ref,asset_ref,next_due_on,cadence_days,revision
                   FROM preventive_plans WHERE property_ref=? AND enabled=1
                   AND next_due_on<=? ORDER BY next_due_on""",
                (property_ref,as_of),
            )]

    def complete_preventive_plan(
        self, actor: TowerScope, *, property_ref: str, plan_ref: str, work_ref: str,
        completed_on: str, expected_revision: int, signed_proof: object,
        proof_verifier: Callable[[object], Mapping],
    ) -> dict:
        actor=self._access(actor,property_ref,"owner","property_manager","maintenance_supervisor")
        _date(completed_on)
        if completed_on>date.today().isoformat():
            raise GroundsConflict("future completion not allowed")
        with self.store.transaction(write=True) as db:
            plan=db.execute(
                """SELECT p.*,a.unit_ref AS asset_unit FROM preventive_plans p
                   JOIN physical_assets a ON a.asset_ref=p.asset_ref AND a.property_ref=p.property_ref
                   WHERE p.property_ref=? AND p.plan_ref=?""",
                (property_ref,plan_ref),
            ).fetchone()
            if plan is None:
                raise AccessDenied("plan unavailable")
            if plan["enabled"]!=1 or plan["revision"]!=expected_revision:
                raise GroundsConflict("plan disabled or revision stale")
            if plan["last_completed_on"] and completed_on<plan["last_completed_on"]:
                raise GroundsConflict("completion chronology invalid")
            work=db.execute(
                "SELECT property_ref,unit_ref,state FROM work_orders WHERE work_ref=?",
                (work_ref,),
            ).fetchone()
            if (work is None or work["property_ref"]!=property_ref or work["state"]!="closed"
                or (plan["asset_unit"] is not None and plan["asset_unit"]!=work["unit_ref"])):
                raise AccessDenied("matching completed work unavailable")
            proof_ref=_verified_proof(
                proof_verifier,signed_proof,kind="preventive_completion",
                expected={"property_ref":property_ref,"plan_ref":plan_ref,
                          "asset_ref":plan["asset_ref"],"work_ref":work_ref,
                          "completed_on":completed_on},
            )
            next_on=(date.fromisoformat(completed_on)+timedelta(days=plan["cadence_days"])).isoformat()
            revision=expected_revision+1
            try:
                db.execute(
                    """INSERT INTO preventive_completion_events
                       (completion_ref,plan_ref,work_ref,proof_ref,completed_on,
                        actor_ref,plan_revision,recorded_at)
                       VALUES(?,?,?,?,?,?,?,?)""",
                    (uuid4().hex,plan_ref,work_ref,proof_ref,completed_on,
                     actor.subject_ref,revision,_now()),
                )
            except sqlite3.IntegrityError as exc:
                raise GroundsConflict("duplicate or invalid preventive proof") from exc
            db.execute(
                """UPDATE preventive_plans SET last_completed_on=?,next_due_on=?,revision=?
                   WHERE plan_ref=?""",
                (completed_on,next_on,revision,plan_ref),
            )
            return {"plan_ref":plan_ref,"revision":revision,"next_due_on":next_on,
                    "completion_proof_ref":proof_ref,"external_schedule_created":False}

    def plan_inspection(self, actor: TowerScope, *, property_ref: str,
                        inspection_ref: str, category: str, planned_on: str,
                        unit_ref: str | None = None,
                        turnover_ref: str | None = None) -> dict:
        actor=self._access(actor,property_ref,"owner","property_manager","maintenance_supervisor")
        _required(inspection_ref,"inspection_ref",max_length=128)
        _required(category,"category",max_length=80)
        _date(planned_on)
        if (category=="turnover") != (turnover_ref is not None):
            raise GroundsConflict("turnover inspections require exact turnover link; other types forbid it")
        if turnover_ref is not None and unit_ref is None:
            raise GroundsConflict("turnover inspection requires unit")
        try:
            with self.store.transaction(write=True) as db:
                if turnover_ref is not None:
                    turn=db.execute(
                        """SELECT state FROM turnovers
                           WHERE turnover_ref=? AND property_ref=? AND unit_ref=?""",
                        (turnover_ref,property_ref,unit_ref),
                    ).fetchone()
                    if turn is None or turn["state"]!="inspection":
                        raise AccessDenied("active matching turnover inspection stage required")
                db.execute(
                    """INSERT INTO inspections
                       (inspection_ref,property_ref,unit_ref,category,state,planned_on,created_by,updated_at)
                       VALUES(?,?,?,?,'planned',?,?,?)""",
                    (inspection_ref,property_ref,unit_ref,category,planned_on,actor.subject_ref,_now()),
                )
                if turnover_ref is not None:
                    db.execute(
                        "INSERT INTO turnover_inspections(turnover_ref,inspection_ref) VALUES(?,?)",
                        (turnover_ref,inspection_ref),
                    )
        except sqlite3.IntegrityError as exc:
            raise GroundsConflict("inspection duplicated, already linked, or unit/property mismatch") from exc
        return {"inspection_ref":inspection_ref,"state":"planned","revision":1,
                "turnover_ref":turnover_ref,"inspector_self_service_enabled":False}

    def advance_inspection(self, actor: TowerScope, *, property_ref: str,
                           inspection_ref: str, next_state: str,
                           expected_revision: int) -> dict:
        actor=self._access(actor,property_ref,"owner","property_manager","maintenance_supervisor")
        edges={"planned":"in_progress","in_progress":"review","review":"closed"}
        with self.store.transaction(write=True) as db:
            item=db.execute(
                "SELECT * FROM inspections WHERE property_ref=? AND inspection_ref=?",
                (property_ref,inspection_ref),
            ).fetchone()
            if item is None:
                raise AccessDenied("inspection unavailable")
            if item["revision"]!=expected_revision or edges.get(item["state"])!=next_state:
                raise GroundsConflict("invalid or stale inspection transition")
            if next_state=="closed":
                count=db.execute(
                    "SELECT COUNT(*) FROM inspection_findings WHERE inspection_ref=?",
                    (inspection_ref,),
                ).fetchone()[0]
                unresolved=db.execute(
                    """SELECT COUNT(*) FROM inspection_findings f
                       LEFT JOIN inspection_resolutions r ON r.finding_ref=f.finding_ref
                       WHERE f.inspection_ref=? AND f.severity IN ('major','urgent')
                       AND r.finding_ref IS NULL""",
                    (inspection_ref,),
                ).fetchone()[0]
                if count==0 or unresolved:
                    raise GroundsConflict("explicit findings and verified severe-item resolutions required before closure")
            revision=expected_revision+1
            db.execute(
                "UPDATE inspections SET state=?,revision=?,updated_at=? WHERE inspection_ref=?",
                (next_state,revision,_now(),inspection_ref),
            )
            return {"inspection_ref":inspection_ref,"state":next_state,"revision":revision}

    def record_finding(self, actor: TowerScope, *, property_ref: str,
                       inspection_ref: str, finding_ref: str, severity: str,
                       narrative: str) -> dict:
        actor=self._access(actor,property_ref,"owner","property_manager","maintenance_supervisor")
        _required(finding_ref,"finding_ref",max_length=128)
        narrative=_required(narrative,"narrative",max_length=1000)
        if severity not in ("observation","minor","major","urgent"):
            raise GroundsConflict("unknown finding severity")
        with self.store.transaction(write=True) as db:
            item=db.execute(
                "SELECT state FROM inspections WHERE property_ref=? AND inspection_ref=?",
                (property_ref,inspection_ref),
            ).fetchone()
            if item is None:
                raise AccessDenied("inspection unavailable")
            if item["state"]!="in_progress":
                raise GroundsConflict("findings require active inspection")
            try:
                db.execute(
                    """INSERT INTO inspection_findings
                       (finding_ref,inspection_ref,severity,narrative,recorded_by,recorded_at)
                       VALUES(?,?,?,?,?,?)""",
                    (finding_ref,inspection_ref,severity,narrative,actor.subject_ref,_now()),
                )
            except sqlite3.IntegrityError as exc:
                raise GroundsConflict("finding duplicated or invalid") from exc
            return {"finding_ref":finding_ref,"severity":severity,"notification_sent":False}

    def resolve_inspection_finding(
        self, actor: TowerScope, *, property_ref: str, inspection_ref: str,
        finding_ref: str, signed_proof: object,
        proof_verifier: Callable[[object], Mapping],
    ) -> dict:
        actor=self._access(actor,property_ref,"owner","property_manager","maintenance_supervisor")
        with self.store.transaction(write=True) as db:
            item=db.execute(
                """SELECT i.unit_ref,i.state,f.severity FROM inspection_findings f
                   JOIN inspections i ON i.inspection_ref=f.inspection_ref
                   WHERE i.property_ref=? AND i.inspection_ref=? AND f.finding_ref=?""",
                (property_ref,inspection_ref,finding_ref),
            ).fetchone()
            if item is None:
                raise AccessDenied("inspection finding unavailable")
            if item["state"] not in ("in_progress","review"):
                raise GroundsConflict("inspection is not open for remediation")
            if item["severity"] not in ("major","urgent"):
                raise GroundsConflict("minor observation needs no severe-item clearance")
            proof_ref=_verified_proof(
                proof_verifier,signed_proof,kind="inspection_resolution",
                expected={"property_ref":property_ref,"inspection_ref":inspection_ref,
                          "finding_ref":finding_ref,"unit_ref":item["unit_ref"]},
            )
            resolution_ref=uuid4().hex
            try:
                db.execute(
                    """INSERT INTO inspection_resolutions
                       (resolution_ref,finding_ref,proof_ref,verified_by,recorded_at)
                       VALUES(?,?,?,?,?)""",
                    (resolution_ref,finding_ref,proof_ref,actor.subject_ref,_now()),
                )
            except sqlite3.IntegrityError as exc:
                raise GroundsConflict("finding already resolved or proof reference reused") from exc
            return {"resolution_ref":resolution_ref,"finding_ref":finding_ref,
                    "proof_ref":proof_ref,"external_notification_sent":False}

    def begin_turnover(self, actor: TowerScope, *, property_ref: str,
                       unit_ref: str, lease_ref: str, turnover_ref: str) -> dict:
        actor=self._access(actor,property_ref,"owner","property_manager")
        _required(turnover_ref,"turnover_ref",max_length=128)
        with self.store.transaction(write=True) as db:
            lease=db.execute(
                """SELECT status FROM leases WHERE lease_ref=? AND property_ref=? AND unit_ref=?""",
                (lease_ref,property_ref,unit_ref),
            ).fetchone()
            unit=db.execute(
                "SELECT lifecycle FROM units WHERE unit_ref=? AND property_ref=?",
                (unit_ref,property_ref),
            ).fetchone()
            if lease is None or lease["status"]!="ended" or unit is None or unit["lifecycle"]!="make_ready":
                raise AccessDenied("ended lease and make-ready unit required")
            timestamp=_now()
            try:
                db.execute(
                    """INSERT INTO turnovers
                       (turnover_ref,property_ref,unit_ref,lease_ref,state,created_by,created_at,updated_at)
                       VALUES(?,?,?,?,'planned',?,?,?)""",
                    (turnover_ref,property_ref,unit_ref,lease_ref,actor.subject_ref,timestamp,timestamp),
                )
            except sqlite3.IntegrityError as exc:
                raise GroundsConflict("turnover already exists or mismatched") from exc
            self._turnover_event(db,turnover_ref,actor,None,"planned",1)
            return {"turnover_ref":turnover_ref,"state":"planned","revision":1}

    @staticmethod
    def _turnover_event(db,ref,actor,before,after,revision):
        db.execute(
            """INSERT INTO turnover_events
               (event_ref,turnover_ref,actor_ref,from_state,to_state,revision,occurred_at)
               VALUES(?,?,?,?,?,?,?)""",
            (uuid4().hex,ref,actor.subject_ref,before,after,revision,_now()),
        )

    def _turnover(self,db,property_ref,turnover_ref):
        item=db.execute(
            "SELECT * FROM turnovers WHERE property_ref=? AND turnover_ref=?",
            (property_ref,turnover_ref),
        ).fetchone()
        if item is None:
            raise AccessDenied("turnover unavailable")
        return item

    @staticmethod
    def _closed_turnover_inspection(db,item) -> bool:
        return db.execute(
            """SELECT 1 FROM turnover_inspections ti
               JOIN inspections i ON i.inspection_ref=ti.inspection_ref
               WHERE ti.turnover_ref=? AND i.property_ref=? AND i.unit_ref=?
                 AND i.category='turnover' AND i.state='closed' LIMIT 1""",
            (item["turnover_ref"],item["property_ref"],item["unit_ref"]),
        ).fetchone() is not None

    @staticmethod
    def _open_work_exists(db,item) -> bool:
        return db.execute(
            """SELECT 1 FROM work_orders WHERE property_ref=? AND unit_ref=?
               AND state!='closed' LIMIT 1""",
            (item["property_ref"],item["unit_ref"]),
        ).fetchone() is not None

    def advance_turnover(self, actor: TowerScope, *, property_ref: str,
                         turnover_ref: str, next_state: str,
                         expected_revision: int) -> dict:
        actor=self._access(actor,property_ref,"owner","property_manager")
        edges={"planned":"inspection","inspection":"work","work":"final_review"}
        with self.store.transaction(write=True) as db:
            item=self._turnover(db,property_ref,turnover_ref)
            if item["revision"]!=expected_revision or edges.get(item["state"])!=next_state:
                raise GroundsConflict("invalid or stale turnover transition")
            if next_state=="work" and not self._closed_turnover_inspection(db,item):
                raise GroundsConflict("reviewed and closed unit inspection required")
            if next_state=="final_review" and self._open_work_exists(db,item):
                raise GroundsConflict("outstanding unit work blocks final review")
            revision=expected_revision+1
            db.execute(
                "UPDATE turnovers SET state=?,revision=?,updated_at=? WHERE turnover_ref=?",
                (next_state,revision,_now(),turnover_ref),
            )
            self._turnover_event(db,turnover_ref,actor,item["state"],next_state,revision)
            return {"turnover_ref":turnover_ref,"state":next_state,"revision":revision,
                    "unit_readiness_changed":False}

    def complete_turnover(
        self, actor: TowerScope, *, property_ref: str, turnover_ref: str,
        expected_revision: int, signed_proof: object,
        proof_verifier: Callable[[object], Mapping],
    ) -> dict:
        actor=self._access(actor,property_ref,"owner","property_manager")
        with self.store.transaction(write=True) as db:
            item=self._turnover(db,property_ref,turnover_ref)
            if item["state"]!="final_review" or item["revision"]!=expected_revision:
                raise GroundsConflict("turnover not ready for completion")
            if not self._closed_turnover_inspection(db,item) or self._open_work_exists(db,item):
                raise GroundsConflict("inspection or unit work blocks completion")
            unit=db.execute(
                "SELECT lifecycle FROM units WHERE unit_ref=? AND property_ref=?",
                (item["unit_ref"],property_ref),
            ).fetchone()
            if unit is None or unit["lifecycle"]!="make_ready":
                raise GroundsConflict("unit is no longer in make-ready")
            proof_ref=_verified_proof(
                proof_verifier,signed_proof,kind="turnover_final",
                expected={"property_ref":property_ref,
                          "unit_ref":item["unit_ref"],"turnover_ref":turnover_ref},
            )
            revision=expected_revision+1
            try:
                db.execute(
                    """UPDATE turnovers SET state='complete',revision=?,final_vault_proof_ref=?,
                       updated_at=? WHERE turnover_ref=?""",
                    (revision,proof_ref,_now(),turnover_ref),
                )
            except sqlite3.IntegrityError as exc:
                raise GroundsConflict("turnover proof reused") from exc
            db.execute(
                "UPDATE units SET lifecycle='ready' WHERE unit_ref=? AND property_ref=?",
                (item["unit_ref"],property_ref),
            )
            self._turnover_event(db,turnover_ref,actor,"final_review","complete",revision)
            return {"turnover_ref":turnover_ref,"state":"complete","revision":revision,
                    "unit_lifecycle":"ready","proof_ref":proof_ref,
                    "resident_notification_sent":False}

    def inspection_summary(self,actor:TowerScope,*,property_ref:str,inspection_ref:str)->dict:
        self._access(actor,property_ref,"owner","property_manager","maintenance_supervisor")
        with self.store.transaction() as db:
            item=db.execute(
                """SELECT inspection_ref,property_ref,unit_ref,category,state,planned_on,revision
                   FROM inspections WHERE property_ref=? AND inspection_ref=?""",
                (property_ref,inspection_ref),
            ).fetchone()
            if item is None:
                raise AccessDenied("inspection unavailable")
            unresolved=db.execute(
                """SELECT COUNT(*) FROM inspection_findings f
                   LEFT JOIN inspection_resolutions r ON r.finding_ref=f.finding_ref
                   WHERE f.inspection_ref=? AND f.severity IN ('major','urgent')
                     AND r.finding_ref IS NULL""",
                (inspection_ref,),
            ).fetchone()[0]
            findings=db.execute(
                "SELECT COUNT(*) FROM inspection_findings WHERE inspection_ref=?",
                (inspection_ref,),
            ).fetchone()[0]
            return {**dict(item),"findings_count":findings,
                    "unresolved_major_or_urgent":unresolved,
                    "external_notification_sent":False}

    def turnover_summary(self,actor:TowerScope,*,property_ref:str,turnover_ref:str)->dict:
        self._access(actor,property_ref,"owner","property_manager")
        with self.store.transaction() as db:
            item=self._turnover(db,property_ref,turnover_ref)
            linked=db.execute(
                """SELECT i.inspection_ref,i.state FROM turnover_inspections t
                   JOIN inspections i ON i.inspection_ref=t.inspection_ref
                   WHERE t.turnover_ref=?""",(turnover_ref,),
            ).fetchone()
            blocking=db.execute(
                """SELECT COUNT(*) FROM work_orders WHERE property_ref=? AND unit_ref=?
                   AND state!='closed'""",
                (property_ref,item["unit_ref"]),
            ).fetchone()[0]
            return {
                "turnover_ref":turnover_ref,"property_ref":property_ref,
                "unit_ref":item["unit_ref"],"state":item["state"],
                "revision":item["revision"],
                "inspection_ref":linked["inspection_ref"] if linked else None,
                "inspection_state":linked["state"] if linked else None,
                "open_unit_work_orders":blocking,
                "final_sealed_proof_present":bool(item["final_vault_proof_ref"]),
                "notification_sent":False,
            }

    def turnover_history(self,actor:TowerScope,*,property_ref:str,turnover_ref:str) -> list[dict]:
        self._access(actor,property_ref,"owner","property_manager")
        with self.store.transaction() as db:
            self._turnover(db,property_ref,turnover_ref)
            return [dict(row) for row in db.execute(
                """SELECT actor_ref,from_state,to_state,revision,occurred_at FROM turnover_events
                   WHERE turnover_ref=? ORDER BY revision""",(turnover_ref,),
            )]
