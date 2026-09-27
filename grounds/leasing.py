"""GRD017 — property-scoped leasing inventory, opaque prospects and tour planning.

Does not conduct screening, approve applications, receive applicant PII, send
communications, collect fees, or make legal housing decisions. All contacts
are Tower-mediated private evidence references; a real issuer/notification
service is an independent future integration.
"""
from __future__ import annotations

import sqlite3
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from .access import AccessDenied, TowerScope
from .operations import GroundsConflict, _required, _now
from .storage import GroundsStoreBase

LEASING_ROLES = ("owner", "property_manager", "leasing_agent")
STAGE_EDGES = {
    "new": ("contacted", "closed"),
    "contacted": ("tour_scheduled", "application_received", "closed"),
    "tour_scheduled": ("application_received", "closed"),
    "application_received": ("manual_review", "closed"),
    "manual_review": ("closed",),
}


class GroundsLeasing:
    def __init__(self, store: GroundsStoreBase):
        if not isinstance(store, GroundsStoreBase):
            raise TypeError("transaction-backed Grounds store required")
        self.store = store

    @staticmethod
    def _access(actor: TowerScope, property_ref: str):
        if not isinstance(actor, TowerScope):
            raise AccessDenied("verified Tower scope required")
        actor.require_role(*LEASING_ROLES)
        actor.require_property(property_ref)

    def availability(self, actor: TowerScope, *, property_ref: str) -> list[dict]:
        self._access(actor, property_ref)
        with self.store.transaction() as db:
            rows = db.execute(
                """SELECT u.unit_ref,u.building_ref,b.label AS building_label,
                          u.label AS unit_label,u.lifecycle
                   FROM units u JOIN buildings b ON b.building_ref=u.building_ref
                   WHERE u.property_ref=? ORDER BY b.label,u.label""", (property_ref,),
            )
            # Deliberately do not return resident IDs, lease documents or financial info.
            return [dict(x) for x in rows]

    def register_prospect(
        self, actor: TowerScope, *, property_ref: str, prospect_ref: str,
        contact_vault_ref: str, desired_unit_ref: str | None = None,
    ) -> dict:
        self._access(actor, property_ref)
        _required(prospect_ref, "prospect_ref", max_length=128)
        _required(contact_vault_ref, "contact_vault_ref", max_length=128)
        timestamp = _now()
        try:
            with self.store.transaction(write=True) as db:
                db.execute(
                    """INSERT INTO leasing_prospects
                       (prospect_ref,property_ref,contact_vault_ref,desired_unit_ref,
                        created_at,updated_at) VALUES(?,?,?,?,?,?)""",
                    (prospect_ref,property_ref,contact_vault_ref,desired_unit_ref,timestamp,timestamp),
                )
        except sqlite3.IntegrityError as exc:
            raise GroundsConflict("prospect invalid, duplicated or outside property") from exc
        return {"prospect_ref":prospect_ref,"stage":"new","revision":1}

    def _prospect(self, db, property_ref, prospect_ref):
        row = db.execute(
            "SELECT * FROM leasing_prospects WHERE property_ref=? AND prospect_ref=?",
            (property_ref,prospect_ref),
        ).fetchone()
        if row is None:
            raise AccessDenied("prospect unavailable")
        return row

    def prospect(self, actor: TowerScope, *, property_ref: str, prospect_ref: str) -> dict:
        self._access(actor, property_ref)
        with self.store.transaction() as db:
            return dict(self._prospect(db,property_ref,prospect_ref))

    def move_stage(self, actor: TowerScope, *, property_ref: str,
                   prospect_ref: str, next_stage: str, expected_revision: int) -> dict:
        self._access(actor, property_ref)
        with self.store.transaction(write=True) as db:
            row = self._prospect(db,property_ref,prospect_ref)
            if row["revision"] != expected_revision or next_stage not in STAGE_EDGES.get(row["stage"], ()):
                raise GroundsConflict("invalid or stale prospect transition")
            revision = expected_revision + 1
            db.execute(
                "UPDATE leasing_prospects SET stage=?,revision=?,updated_at=? WHERE prospect_ref=?",
                (next_stage,revision,_now(),prospect_ref),
            )
            return {"prospect_ref": prospect_ref,"stage":next_stage,"revision":revision}

    def plan_tour(self, actor: TowerScope, *, property_ref: str,
                  prospect_ref: str, tour_ref: str, unit_ref: str, starts_at: str,
                  expected_revision: int) -> dict:
        self._access(actor, property_ref)
        _required(tour_ref, "tour_ref", max_length=128)
        try:
            starts = datetime.fromisoformat(starts_at)
            if starts.tzinfo is None or starts.utcoffset() is None:
                raise ValueError
            now=datetime.now(timezone.utc)
            utc_start=starts.astimezone(timezone.utc)
            if not now < utc_start <= now+timedelta(days=366):
                raise ValueError
        except (ValueError,TypeError,OverflowError) as exc:
            raise GroundsConflict("tour requires a future timezone-aware time within 366 days") from exc
        with self.store.transaction(write=True) as db:
            row = self._prospect(db,property_ref,prospect_ref)
            if row["revision"] != expected_revision or row["stage"] != "contacted":
                raise GroundsConflict("prospect not ready to schedule at current revision")
            unit = db.execute(
                "SELECT 1 FROM units WHERE unit_ref=? AND property_ref=?",
                (unit_ref,property_ref),
            ).fetchone()
            if unit is None:
                raise AccessDenied("unit unavailable")
            try:
                db.execute(
                    """INSERT INTO leasing_tours
                       (tour_ref,property_ref,prospect_ref,unit_ref,starts_at,created_by)
                       VALUES(?,?,?,?,?,?)""",
                    (tour_ref,property_ref,prospect_ref,unit_ref,starts.isoformat(),actor.subject_ref),
                )
            except sqlite3.IntegrityError as exc:
                raise GroundsConflict("tour duplicated or invalid") from exc
            revision = expected_revision+1
            db.execute(
                """UPDATE leasing_prospects SET stage='tour_scheduled',revision=?,updated_at=?
                   WHERE prospect_ref=?""",
                (revision,_now(),prospect_ref),
            )
            return {"tour_ref":tour_ref,"prospect_ref":prospect_ref,
                    "stage":"tour_scheduled","revision":revision,"notification_sent":False}

    def list_tours(self, actor: TowerScope, *, property_ref: str) -> list[dict]:
        self._access(actor,property_ref)
        with self.store.transaction() as db:
            return [dict(x) for x in db.execute(
                """SELECT tour_ref,prospect_ref,unit_ref,starts_at
                   FROM leasing_tours WHERE property_ref=? ORDER BY starts_at""",
                (property_ref,),
            )]
