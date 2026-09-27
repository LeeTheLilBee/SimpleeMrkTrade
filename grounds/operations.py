"""GRD008–010 — property, leasing, maintenance and notice operations.

This is a locally testable domain/service layer. The only accepted identity is
a normalized, externally verified TowerScope; real token verification, durable
hosting, communication delivery and payments are not wired. Every operation
rechecks scope and records work-order changes transactionally.
"""
from __future__ import annotations

import sqlite3
from datetime import date, datetime, timezone
from typing import Callable, Mapping
from uuid import uuid4

from .access import AccessDenied, TowerScope
from .maintenance import MaintenanceIntake, WorkOrder, transition_work_order
from .storage import GroundsStore


class GroundsConflict(ValueError):
    """Validation, duplicate, or stale-version conflict."""


def _required(value: str, label: str, *, max_length: int = 256) -> str:
    if not isinstance(value, str) or not value.strip() or len(value) > max_length:
        raise GroundsConflict(f"invalid {label}")
    return value.strip()


def _date(value: str) -> str:
    try:
        result = date.fromisoformat(value)
        if result.isoformat() != value:
            raise ValueError
        return value
    except (TypeError, ValueError) as exc:
        raise GroundsConflict("date must use YYYY-MM-DD") from exc


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _event(db, work_ref: str, actor: TowerScope, action: str,
           before: str | None, after: str, revision: int):
    db.execute(
        """INSERT INTO work_events
           (event_ref,work_ref,actor_ref,action,from_state,to_state,revision,occurred_at)
           VALUES(?,?,?,?,?,?,?,?)""",
        (uuid4().hex, work_ref, actor.subject_ref, action, before, after, revision, _now()),
    )


def _record(row):
    return dict(row) if row is not None else None


def _outbox(db, *, property_ref: str, event_kind: str,
            resource_ref: str, revision: int):
    """Transactional local event intent; NEVER an externally delivered notification."""
    db.execute(
        """INSERT INTO event_outbox
           (event_ref,property_ref,event_kind,resource_ref,source_revision,created_at)
           VALUES(?,?,?,?,?,?)""",
        (uuid4().hex,property_ref,event_kind,resource_ref,revision,_now()),
    )


class GroundsOperations:
    def __init__(self, store: GroundsStore):
        if not isinstance(store, GroundsStore):
            raise TypeError("GroundsStore required")
        self.store = store

    @staticmethod
    def _scope(actor: TowerScope) -> TowerScope:
        if not isinstance(actor, TowerScope):
            raise AccessDenied("verified Tower scope required")
        actor.assert_active()
        return actor

    def record_closed_property(
        self, actor: TowerScope, *, property_ref: str, name: str,
        close_evidence: object, close_verifier: Callable[[object], Mapping],
    ) -> dict:
        actor = self._scope(actor)
        actor.require_role("owner")
        actor.require_property(property_ref)
        _required(property_ref, "property_ref", max_length=128)
        name = _required(name, "name")
        if not callable(close_verifier):
            raise AccessDenied("verified close evidence required")
        try:
            verified = close_verifier(close_evidence)
        except Exception as exc:
            raise AccessDenied("close evidence rejected") from exc
        if not isinstance(verified, Mapping) or verified.get("status") != "verified_closed":
            raise AccessDenied("close evidence rejected")
        if verified.get("property_ref") != property_ref:
            raise AccessDenied("close evidence/property mismatch")
        proof_ref = _required(verified.get("proof_ref"), "proof_ref", max_length=128)
        owned_on = _date(verified.get("owned_on"))
        try:
            with self.store.transaction(write=True) as db:
                db.execute(
                    "INSERT INTO properties(property_ref,name,owned_on,close_proof_ref) VALUES (?,?,?,?)",
                    (property_ref, name, owned_on, proof_ref),
                )
        except sqlite3.IntegrityError as exc:
            raise GroundsConflict("property or close proof already recorded") from exc
        return {"property_ref": property_ref, "name": name, "owned_on": owned_on}

    def add_building(self, actor: TowerScope, *, property_ref: str,
                     building_ref: str, label: str):
        actor = self._scope(actor)
        actor.require_role("owner", "property_manager")
        actor.require_property(property_ref)
        _required(building_ref, "building_ref", max_length=128)
        label = _required(label, "building label", max_length=128)
        try:
            with self.store.transaction(write=True) as db:
                db.execute(
                    "INSERT INTO buildings(building_ref,property_ref,label) VALUES (?,?,?)",
                    (building_ref, property_ref, label),
                )
        except sqlite3.IntegrityError as exc:
            raise GroundsConflict("building invalid or already recorded") from exc

    def add_unit(self, actor: TowerScope, *, property_ref: str, building_ref: str,
                 unit_ref: str, label: str):
        actor = self._scope(actor)
        actor.require_role("owner", "property_manager")
        actor.require_property(property_ref)
        _required(unit_ref, "unit_ref", max_length=128)
        label = _required(label, "unit label", max_length=128)
        try:
            with self.store.transaction(write=True) as db:
                db.execute(
                    """INSERT INTO units(unit_ref,property_ref,building_ref,label)
                       VALUES (?,?,?,?)""",
                    (unit_ref, property_ref, building_ref, label),
                )
        except sqlite3.IntegrityError as exc:
            raise GroundsConflict("unit invalid or already recorded") from exc

    def activate_lease(
        self, actor: TowerScope, *, property_ref: str, unit_ref: str,
        lease_ref: str, resident_ref: str, start_on: str, end_on: str,
        vault_proof_ref: str | None = None,
    ):
        actor = self._scope(actor)
        actor.require_role("owner", "property_manager")
        actor.require_property(property_ref)
        _required(lease_ref, "lease_ref", max_length=128)
        _required(resident_ref, "resident_ref", max_length=128)
        start_on, end_on = _date(start_on), _date(end_on)
        if end_on < start_on:
            raise GroundsConflict("lease end precedes start")
        if vault_proof_ref is not None:
            raise GroundsConflict("lease proof attachment requires a certified Tower/Vault handoff")
        try:
            with self.store.transaction(write=True) as db:
                unit=db.execute(
                    "SELECT lifecycle FROM units WHERE unit_ref=? AND property_ref=?",
                    (unit_ref,property_ref),
                ).fetchone()
                if unit is None:
                    raise AccessDenied("unit unavailable")
                if unit["lifecycle"]!="ready":
                    raise GroundsConflict("lease activation requires a ready unit")
                db.execute(
                    """INSERT INTO leases(lease_ref,property_ref,unit_ref,resident_ref,start_on,
                       end_on,status,vault_proof_ref) VALUES (?,?,?,?,?,?,'active',?)""",
                    (lease_ref, property_ref, unit_ref, resident_ref, start_on, end_on, vault_proof_ref),
                )
                db.execute(
                    "UPDATE units SET lifecycle='occupied' WHERE unit_ref=? AND property_ref=?",
                    (unit_ref, property_ref),
                )
                db.execute(
                    """INSERT INTO lease_members
                       (lease_ref,property_ref,unit_ref,subject_ref,relationship,status,joined_at)
                       VALUES(?,?,?,?,?,'active',?)""",
                    (lease_ref,property_ref,unit_ref,resident_ref,"primary",_now()),
                )
                db.execute(
                    """INSERT INTO lease_member_events
                       (event_ref,lease_ref,subject_ref,actor_ref,action,occurred_at)
                       VALUES(?,?,?,?,'primary_registered',?)""",
                    (uuid4().hex,lease_ref,resident_ref,actor.subject_ref,_now()),
                )
        except sqlite3.IntegrityError as exc:
            raise GroundsConflict("lease already active or wrong property/unit") from exc

    def end_lease(self, actor: TowerScope, *, property_ref: str, lease_ref: str,
                  expected_revision: int):
        actor = self._scope(actor)
        actor.require_role("owner", "property_manager")
        actor.require_property(property_ref)
        with self.store.transaction(write=True) as db:
            lease = db.execute(
                "SELECT * FROM leases WHERE lease_ref=? AND property_ref=?",
                (lease_ref, property_ref),
            ).fetchone()
            if lease is None:
                raise AccessDenied("lease unavailable")
            if lease["status"] != "active" or lease["revision"] != expected_revision:
                raise GroundsConflict("lease state changed")
            db.execute(
                "UPDATE leases SET status='ended', revision=revision+1 WHERE lease_ref=?",
                (lease_ref,),
            )
            db.execute(
                "UPDATE units SET lifecycle='make_ready' WHERE unit_ref=? AND property_ref=?",
                (lease["unit_ref"], property_ref),
            )
            members=db.execute(
                "SELECT subject_ref FROM lease_members WHERE lease_ref=? AND status='active'",
                (lease_ref,),
            ).fetchall()
            db.execute(
                """UPDATE lease_members SET status='ended',revoked_at=?
                   WHERE lease_ref=? AND status='active'""",
                (_now(),lease_ref),
            )
            for member in members:
                db.execute(
                    """INSERT INTO lease_member_events
                       (event_ref,lease_ref,subject_ref,actor_ref,action,occurred_at)
                       VALUES(?,?,?,?,'lease_ended',?)""",
                    (uuid4().hex,lease_ref,member["subject_ref"],actor.subject_ref,_now()),
                )

    @staticmethod
    def _resident_lease(db, actor: TowerScope, property_ref: str, unit_ref: str):
        actor.require_role("resident")
        actor.require_unit(property_ref,unit_ref)
        lease=db.execute(
            """SELECT l.lease_ref,l.start_on,l.end_on,l.vault_proof_ref,l.revision
               FROM leases l JOIN lease_members m ON m.lease_ref=l.lease_ref
               AND m.property_ref=l.property_ref AND m.unit_ref=l.unit_ref
               WHERE l.property_ref=? AND l.unit_ref=? AND l.status='active'
                 AND m.subject_ref=? AND m.status='active'""",
            (property_ref,unit_ref,actor.subject_ref),
        ).fetchone()
        if lease is None:
            raise AccessDenied("active authorized resident lease unavailable")
        return lease

    def submit_maintenance(self, actor: TowerScope, *, work_ref: str,
                           intake: MaintenanceIntake):
        actor = self._scope(actor)
        actor.require_role("resident", "owner", "property_manager", "maintenance_supervisor")
        if not isinstance(intake, MaintenanceIntake):
            raise GroundsConflict("valid intake required")
        actor.require_property(intake.property_ref)
        if intake.photo_refs:
            raise GroundsConflict("direct photo intake is not connected; submit verified Vault proof separately")
        if actor.role == "resident":
            actor.require_unit(intake.property_ref, intake.unit_ref)
        _required(work_ref, "work_ref", max_length=128)
        timestamp = _now()
        try:
            with self.store.transaction(write=True) as db:
                lease_ref = None
                if actor.role == "resident":
                    lease = self._resident_lease(
                        db,actor,intake.property_ref,intake.unit_ref,
                    )
                    lease_ref = lease["lease_ref"]
                else:
                    unit = db.execute(
                        "SELECT 1 FROM units WHERE property_ref=? AND unit_ref=?",
                        (intake.property_ref, intake.unit_ref),
                    ).fetchone()
                    if unit is None:
                        raise AccessDenied("unit unavailable")
                db.execute(
                    """INSERT INTO work_orders
                       (work_ref,property_ref,unit_ref,lease_ref,created_by,category,description,
                        emergency_flag,entry_permission,state,created_at,updated_at)
                       VALUES(?,?,?,?,?,?,?,?,?,'submitted',?,?)""",
                    (work_ref,intake.property_ref,intake.unit_ref,lease_ref,actor.subject_ref,
                     intake.category,intake.description,int(intake.emergency_flag),
                     intake.entry_permission,timestamp,timestamp),
                )
                _event(db, work_ref, actor, "created", None, "submitted", 1)
                _outbox(db,property_ref=intake.property_ref,event_kind="work_changed",
                        resource_ref=work_ref,revision=1)
                if intake.emergency_flag:
                    _outbox(db,property_ref=intake.property_ref,
                            event_kind="urgent_intake_requires_human_review",
                            resource_ref=work_ref,revision=1)
        except sqlite3.IntegrityError as exc:
            raise GroundsConflict("duplicate or invalid request") from exc
        return {"work_ref": work_ref, "state": "submitted", "emergency_flag": intake.emergency_flag}

    def _visible_order(self, db, actor: TowerScope, work_ref: str):
        actor.assert_active()
        row = db.execute(
            "SELECT * FROM work_orders WHERE work_ref=?",
            (work_ref,),
        ).fetchone()
        if row is None or row["property_ref"] not in actor.property_refs:
            raise AccessDenied("work order unavailable")
        if actor.role == "resident":
            if (row["created_by"] != actor.subject_ref
                or row["unit_ref"] not in actor.unit_refs):
                raise AccessDenied("work order unavailable")
            self._resident_lease(db,actor,row["property_ref"],row["unit_ref"])
        elif actor.role in ("maintenance_technician", "vendor"):
            if row["assigned_to"] != actor.subject_ref or work_ref not in actor.assigned_work_refs:
                raise AccessDenied("work order unavailable")
        elif actor.role not in ("owner", "property_manager", "maintenance_supervisor"):
            raise AccessDenied("work order unavailable")
        return row

    def get_work_order(self, actor: TowerScope, *, work_ref: str) -> dict:
        actor = self._scope(actor)
        with self.store.transaction() as db:
            return _record(self._visible_order(db, actor, work_ref))

    def list_work_orders(self, actor: TowerScope, *, property_ref: str) -> list[dict]:
        actor = self._scope(actor)
        actor.require_property(property_ref)
        with self.store.transaction() as db:
            if actor.role == "resident":
                rows = db.execute(
                    """SELECT w.* FROM work_orders w
                       WHERE w.property_ref=? AND w.created_by=? AND EXISTS(
                         SELECT 1 FROM leases l JOIN lease_members m ON m.lease_ref=l.lease_ref
                         WHERE l.property_ref=w.property_ref AND l.unit_ref=w.unit_ref
                           AND l.status='active' AND m.subject_ref=?
                           AND m.status='active' AND m.property_ref=w.property_ref
                           AND m.unit_ref=w.unit_ref)
                       ORDER BY created_at DESC""",
                    (property_ref, actor.subject_ref, actor.subject_ref),
                )
            elif actor.role in ("maintenance_technician", "vendor"):
                if not actor.assigned_work_refs:
                    return []
                rows = db.execute(
                    """SELECT * FROM work_orders WHERE property_ref=? AND assigned_to=?
                       ORDER BY created_at DESC""",
                    (property_ref, actor.subject_ref),
                )
                return [_record(row) for row in rows if row["work_ref"] in actor.assigned_work_refs]
            elif actor.role in ("owner", "property_manager", "maintenance_supervisor"):
                rows = db.execute(
                    "SELECT * FROM work_orders WHERE property_ref=? ORDER BY created_at DESC",
                    (property_ref,),
                )
            else:
                raise AccessDenied("work queue unavailable")
            return [_record(row) for row in rows]

    def advance_work_order(self, actor: TowerScope, *, work_ref: str,
                           next_state: str, expected_revision: int):
        actor = self._scope(actor)
        with self.store.transaction(write=True) as db:
            row = self._visible_order(db, actor, work_ref)
            if row["revision"] != expected_revision:
                raise GroundsConflict("stale work order revision")
            if row["emergency_flag"] and row["state"]=="submitted" and next_state=="received":
                triage=db.execute(
                    "SELECT 1 FROM emergency_reviews WHERE work_ref=?",(work_ref,),
                ).fetchone()
                if triage is None:
                    raise GroundsConflict("urgency flag requires human triage acknowledgment")
            if actor.role == "vendor":
                raise AccessDenied("vendor transition not yet authorized")
            after = transition_work_order(
                WorkOrder(work_ref, MaintenanceIntake(
                    row["property_ref"],row["unit_ref"],row["category"],row["description"],
                    bool(row["emergency_flag"]),row["entry_permission"],
                ),state=row["state"]),
                next_state=next_state, actor_role=actor.role,
            )
            revision = expected_revision + 1
            db.execute(
                """UPDATE work_orders SET state=?,revision=?,updated_at=?
                   WHERE work_ref=? AND revision=?""",
                (after.state,revision,_now(),work_ref,expected_revision),
            )
            _event(db, work_ref, actor, "transition", row["state"], after.state, revision)
            _outbox(db,property_ref=row["property_ref"],event_kind="work_changed",
                    resource_ref=work_ref,revision=revision)
            return {"work_ref": work_ref, "state": after.state, "revision": revision}

    def assign_work_order(self, actor: TowerScope, *, work_ref: str,
                          technician: TowerScope, expected_revision: int):
        actor = self._scope(actor)
        actor.require_role("owner", "property_manager", "maintenance_supervisor")
        technician = self._scope(technician)
        technician.require_role("maintenance_technician")
        with self.store.transaction(write=True) as db:
            row = self._visible_order(db, actor, work_ref)
            technician.require_property(row["property_ref"])
            if row["state"] != "scheduled" or row["revision"] != expected_revision:
                raise GroundsConflict("work order not schedulable at current revision")
            revision = expected_revision + 1
            db.execute(
                """UPDATE work_orders SET state='assigned', assigned_to=?,revision=?,updated_at=?
                   WHERE work_ref=? AND revision=?""",
                (technician.subject_ref, revision, _now(), work_ref, expected_revision),
            )
            _event(db, work_ref, actor, "assigned", "scheduled", "assigned", revision)
            _outbox(db,property_ref=row["property_ref"],event_kind="work_changed",
                    resource_ref=work_ref,revision=revision)
            return {"work_ref": work_ref, "state": "assigned", "revision": revision,
                    "assigned_to": technician.subject_ref}

    def work_history(self, actor: TowerScope, *, work_ref: str) -> list[dict]:
        actor = self._scope(actor)
        with self.store.transaction() as db:
            self._visible_order(db, actor, work_ref)
            return [_record(row) for row in db.execute(
                """SELECT action,from_state,to_state,revision,occurred_at
                   FROM work_events WHERE work_ref=? ORDER BY revision""", (work_ref,),
            )]

    def publish_notice(self, actor: TowerScope, *, property_ref: str,
                       notice_ref: str, headline: str, body: str,
                       unit_ref: str | None = None):
        actor = self._scope(actor)
        actor.require_role("owner", "property_manager")
        actor.require_property(property_ref)
        _required(notice_ref, "notice_ref", max_length=128)
        headline, body = _required(headline, "headline"), _required(body, "body", max_length=4000)
        try:
            with self.store.transaction(write=True) as db:
                db.execute(
                    """INSERT INTO property_notices
                       (notice_ref,property_ref,unit_ref,headline,body,published_at)
                       VALUES(?,?,?,?,?,?)""",
                    (notice_ref, property_ref, unit_ref, headline, body, _now()),
                )
                _outbox(db,property_ref=property_ref,event_kind="notice_visible_in_app",
                        resource_ref=notice_ref,revision=1)
        except sqlite3.IntegrityError as exc:
            raise GroundsConflict("notice invalid or already recorded") from exc

    def resident_home(self, actor: TowerScope, *, property_ref: str, unit_ref: str) -> dict:
        actor = self._scope(actor)
        actor.require_role("resident")
        actor.require_unit(property_ref, unit_ref)
        with self.store.transaction() as db:
            lease=self._resident_lease(db,actor,property_ref,unit_ref)
            unit = db.execute(
                "SELECT label,building_ref FROM units WHERE property_ref=? AND unit_ref=?",
                (property_ref,unit_ref),
            ).fetchone()
            notices = db.execute(
                """SELECT n.notice_ref,n.headline,n.body,n.published_at,
                          CASE WHEN r.read_at IS NULL THEN 0 ELSE 1 END AS read_in_app
                   FROM property_notices n
                   LEFT JOIN notice_reads r ON r.notice_ref=n.notice_ref AND r.subject_ref=?
                   WHERE n.property_ref=? AND (n.unit_ref IS NULL OR n.unit_ref=?)
                   ORDER BY n.published_at DESC""",
                (actor.subject_ref,property_ref,unit_ref),
            ).fetchall()
            return {
                "property_ref": property_ref, "unit_ref": unit_ref,
                "unit_label": unit["label"], "building_ref": unit["building_ref"],
                "lease": _record(lease),
                "maintenance": self._orders_for_resident(db, actor, property_ref, unit_ref),
                "notices": [_record(row) for row in notices],
                "rent": {"source": "teller", "status": "awaiting_verified_projection",
                         "amount_due_cents": None, "checkout_url": None,
                         "checkout_execution_enabled": False},
            }

    @staticmethod
    def _orders_for_resident(db, actor, property_ref, unit_ref):
        return [_record(row) for row in db.execute(
            """SELECT work_ref,category,state,emergency_flag,updated_at FROM work_orders
               WHERE property_ref=? AND unit_ref=? AND created_by=?
               ORDER BY created_at DESC""",
            (property_ref, unit_ref, actor.subject_ref),
        )]

    def property_pulse(self, actor: TowerScope, *, property_ref: str) -> dict:
        actor = self._scope(actor)
        actor.require_role("owner", "property_manager", "regional_manager")
        actor.require_property(property_ref)
        with self.store.transaction() as db:
            prop = db.execute(
                "SELECT property_ref,name,owned_on FROM properties WHERE property_ref=?",
                (property_ref,),
            ).fetchone()
            if prop is None:
                raise AccessDenied("property unavailable")
            unit_count = db.execute(
                "SELECT COUNT(*) FROM units WHERE property_ref=?", (property_ref,),
            ).fetchone()[0]
            occupied_count = db.execute(
                "SELECT COUNT(*) FROM units WHERE property_ref=? AND lifecycle='occupied'",
                (property_ref,),
            ).fetchone()[0]
            open_work = db.execute(
                "SELECT COUNT(*) FROM work_orders WHERE property_ref=? AND state!='closed'",
                (property_ref,),
            ).fetchone()[0]
            return {**_record(prop), "units":unit_count, "occupied_units":occupied_count,
                    "open_work_orders":open_work, "financial_source":"teller",
                    "rent_collections":None}
