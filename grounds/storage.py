"""GRD007 — local transactional property/work-order persistence primitives.

SQLite is an inexpensive local development backend, not the hosted PostgreSQL
architecture or real tenant-data authorization. Runtime access is mediated
through GroundsOperations and a Tower-verified scope, not raw SQL/HTTP.
Do not place live personal records into a disposable preview database.
"""
from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path


SCHEMA = """
PRAGMA foreign_keys = ON;
CREATE TABLE IF NOT EXISTS properties (
  property_ref TEXT PRIMARY KEY,
  name TEXT NOT NULL CHECK (length(trim(name)) > 0),
  owned_on TEXT NOT NULL,
  close_proof_ref TEXT NOT NULL UNIQUE
);
CREATE TABLE IF NOT EXISTS property_acquisition_receipts (
  handoff_ref TEXT PRIMARY KEY,
  property_ref TEXT NOT NULL UNIQUE REFERENCES properties(property_ref),
  opportunity_id TEXT NOT NULL,
  opportunity_revision INTEGER NOT NULL CHECK(opportunity_revision > 0),
  input_snapshot_digest TEXT NOT NULL CHECK(length(input_snapshot_digest)=64),
  proposal_fingerprint TEXT NOT NULL CHECK(length(proposal_fingerprint)=64),
  tower_close_receipt_ref TEXT NOT NULL UNIQUE,
  title_proof_ref TEXT NOT NULL UNIQUE,
  encumbrance_review_ref TEXT NOT NULL UNIQUE,
  receipt_digest TEXT NOT NULL UNIQUE CHECK(length(receipt_digest)=64),
  accepted_by TEXT NOT NULL,
  accepted_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS acquisition_receipt_opportunity
  ON property_acquisition_receipts(opportunity_id,opportunity_revision);
CREATE TABLE IF NOT EXISTS buildings (
  building_ref TEXT PRIMARY KEY,
  property_ref TEXT NOT NULL REFERENCES properties(property_ref),
  label TEXT NOT NULL,
  UNIQUE (property_ref, label),
  UNIQUE (building_ref, property_ref)
);
CREATE TABLE IF NOT EXISTS units (
  unit_ref TEXT PRIMARY KEY,
  property_ref TEXT NOT NULL,
  building_ref TEXT NOT NULL,
  label TEXT NOT NULL,
  lifecycle TEXT NOT NULL DEFAULT 'ready'
    CHECK (lifecycle IN ('ready','occupied','make_ready','unavailable')),
  FOREIGN KEY(building_ref,property_ref) REFERENCES buildings(building_ref,property_ref),
  UNIQUE(building_ref,label),
  UNIQUE(unit_ref,property_ref)
);
CREATE TABLE IF NOT EXISTS leases (
  lease_ref TEXT PRIMARY KEY,
  property_ref TEXT NOT NULL,
  unit_ref TEXT NOT NULL,
  resident_ref TEXT NOT NULL,
  start_on TEXT NOT NULL,
  end_on TEXT NOT NULL,
  status TEXT NOT NULL CHECK(status IN ('active','ended')),
  vault_proof_ref TEXT,
  revision INTEGER NOT NULL DEFAULT 1 CHECK (revision > 0),
  FOREIGN KEY(unit_ref,property_ref) REFERENCES units(unit_ref,property_ref)
);
CREATE UNIQUE INDEX IF NOT EXISTS one_active_lease_per_unit
  ON leases(unit_ref) WHERE status = 'active';
CREATE INDEX IF NOT EXISTS leases_resident ON leases(resident_ref,property_ref,unit_ref);
CREATE TABLE IF NOT EXISTS lease_members (
  lease_ref TEXT NOT NULL,
  property_ref TEXT NOT NULL,
  unit_ref TEXT NOT NULL,
  subject_ref TEXT NOT NULL,
  relationship TEXT NOT NULL CHECK(relationship IN ('primary','co_tenant','authorized_occupant')),
  status TEXT NOT NULL DEFAULT 'active' CHECK(status IN ('active','revoked','ended')),
  grant_proof_ref TEXT,
  joined_at TEXT NOT NULL,
  revoked_at TEXT,
  PRIMARY KEY(lease_ref,subject_ref),
  FOREIGN KEY(lease_ref,unit_ref,property_ref) REFERENCES leases(lease_ref,unit_ref,property_ref)
);
CREATE INDEX IF NOT EXISTS active_lease_members ON lease_members(subject_ref,property_ref,unit_ref,status);
CREATE UNIQUE INDEX IF NOT EXISTS unique_member_grant_proof ON lease_members(grant_proof_ref) WHERE grant_proof_ref IS NOT NULL;
CREATE TABLE IF NOT EXISTS lease_member_events (
  event_ref TEXT PRIMARY KEY,
  lease_ref TEXT NOT NULL,
  subject_ref TEXT NOT NULL,
  actor_ref TEXT NOT NULL,
  action TEXT NOT NULL CHECK(action IN ('primary_registered','verified_grant','revoked','lease_ended')),
  proof_ref TEXT,
  occurred_at TEXT NOT NULL,
  FOREIGN KEY(lease_ref,subject_ref) REFERENCES lease_members(lease_ref,subject_ref)
);
CREATE INDEX IF NOT EXISTS lease_member_history ON lease_member_events(lease_ref,subject_ref,occurred_at);
CREATE UNIQUE INDEX IF NOT EXISTS unique_member_event_proof ON lease_member_events(proof_ref) WHERE proof_ref IS NOT NULL;
CREATE TABLE IF NOT EXISTS work_orders (
  work_ref TEXT PRIMARY KEY,
  property_ref TEXT NOT NULL,
  unit_ref TEXT NOT NULL,
  lease_ref TEXT,
  created_by TEXT NOT NULL,
  assigned_to TEXT,
  category TEXT NOT NULL,
  description TEXT NOT NULL,
  emergency_flag INTEGER NOT NULL CHECK (emergency_flag IN (0,1)),
  entry_permission TEXT NOT NULL CHECK (entry_permission IN ('yes','no','contact_first')),
  state TEXT NOT NULL DEFAULT 'submitted',
  revision INTEGER NOT NULL DEFAULT 1 CHECK (revision > 0),
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  FOREIGN KEY(unit_ref,property_ref) REFERENCES units(unit_ref,property_ref),
  FOREIGN KEY(lease_ref) REFERENCES leases(lease_ref)
);
CREATE INDEX IF NOT EXISTS work_property ON work_orders(property_ref,state);
CREATE INDEX IF NOT EXISTS work_assignee ON work_orders(assigned_to,state);
CREATE UNIQUE INDEX IF NOT EXISTS work_scope_identity
  ON work_orders(work_ref,property_ref,unit_ref);
CREATE TABLE IF NOT EXISTS work_resource_events (
  event_ref TEXT PRIMARY KEY,
  work_ref TEXT NOT NULL,
  property_ref TEXT NOT NULL,
  unit_ref TEXT NOT NULL,
  action TEXT NOT NULL CHECK(action IN ('record','reverse')),
  resource_type TEXT NOT NULL CHECK(resource_type IN ('material','labor')),
  label TEXT NOT NULL CHECK(length(trim(label)) BETWEEN 1 AND 160),
  quantity INTEGER NOT NULL CHECK(quantity BETWEEN 1 AND 1000000),
  quantity_unit TEXT NOT NULL CHECK(quantity_unit IN ('items','minutes')),
  reverses_event_ref TEXT REFERENCES work_resource_events(event_ref),
  recorded_by TEXT NOT NULL,
  recorded_at TEXT NOT NULL,
  FOREIGN KEY(work_ref,property_ref,unit_ref)
    REFERENCES work_orders(work_ref,property_ref,unit_ref),
  CHECK((action='record' AND reverses_event_ref IS NULL) OR
        (action='reverse' AND reverses_event_ref IS NOT NULL)),
  CHECK((resource_type='material' AND quantity_unit='items') OR
        (resource_type='labor' AND quantity_unit='minutes'))
);
CREATE UNIQUE INDEX IF NOT EXISTS resource_event_one_reversal
  ON work_resource_events(reverses_event_ref)
  WHERE reverses_event_ref IS NOT NULL;
CREATE INDEX IF NOT EXISTS work_resource_history ON work_resource_events(work_ref,recorded_at,event_ref);
CREATE TABLE IF NOT EXISTS work_events (
  event_ref TEXT PRIMARY KEY,
  work_ref TEXT NOT NULL REFERENCES work_orders(work_ref),
  actor_ref TEXT NOT NULL,
  action TEXT NOT NULL,
  from_state TEXT,
  to_state TEXT NOT NULL,
  revision INTEGER NOT NULL,
  occurred_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS work_events_order ON work_events(work_ref,revision);
CREATE TABLE IF NOT EXISTS emergency_reviews (
  work_ref TEXT PRIMARY KEY REFERENCES work_orders(work_ref),
  urgency TEXT NOT NULL CHECK(urgency IN ('routine','priority','emergency')),
  reviewed_by TEXT NOT NULL,
  reviewed_at TEXT NOT NULL,
  external_dispatch_confirmed INTEGER NOT NULL DEFAULT 0 CHECK(external_dispatch_confirmed=0)
);
CREATE TABLE IF NOT EXISTS work_entry_preferences (
  work_ref TEXT PRIMARY KEY REFERENCES work_orders(work_ref),
  subject_ref TEXT NOT NULL,
  preference TEXT NOT NULL CHECK(preference IN ('yes','no','contact_first')),
  revision INTEGER NOT NULL CHECK(revision>0),
  updated_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS work_entry_events (
  event_ref TEXT PRIMARY KEY,
  work_ref TEXT NOT NULL REFERENCES work_orders(work_ref),
  subject_ref TEXT NOT NULL,
  preference TEXT NOT NULL,
  revision INTEGER NOT NULL,
  updated_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS entry_events_by_work ON work_entry_events(work_ref,revision);
CREATE TABLE IF NOT EXISTS event_outbox (
  event_ref TEXT PRIMARY KEY,
  property_ref TEXT NOT NULL REFERENCES properties(property_ref),
  event_kind TEXT NOT NULL CHECK(event_kind IN (
    'work_changed','urgent_intake_requires_human_review','notice_visible_in_app'
  )),
  resource_ref TEXT NOT NULL,
  source_revision INTEGER NOT NULL CHECK(source_revision>0),
  status TEXT NOT NULL DEFAULT 'pending' CHECK(status='pending'),
  created_at TEXT NOT NULL,
  UNIQUE(event_kind,resource_ref,source_revision)
);
CREATE INDEX IF NOT EXISTS outbox_property_pending ON event_outbox(property_ref,status,created_at);
CREATE TABLE IF NOT EXISTS work_evidence_refs (
  evidence_ref TEXT PRIMARY KEY,
  work_ref TEXT NOT NULL REFERENCES work_orders(work_ref),
  kind TEXT NOT NULL CHECK(kind IN ('intake','before','after','completion','inspection')),
  vault_proof_ref TEXT NOT NULL UNIQUE,
  actor_ref TEXT NOT NULL,
  recorded_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS evidence_per_work ON work_evidence_refs(work_ref);
CREATE TABLE IF NOT EXISTS property_notices (
  notice_ref TEXT PRIMARY KEY,
  property_ref TEXT NOT NULL REFERENCES properties(property_ref),
  unit_ref TEXT,
  lease_ref TEXT,
  headline TEXT NOT NULL,
  body TEXT NOT NULL,
  published_at TEXT NOT NULL,
  FOREIGN KEY(unit_ref,property_ref) REFERENCES units(unit_ref,property_ref),
  FOREIGN KEY(lease_ref,unit_ref,property_ref) REFERENCES leases(lease_ref,unit_ref,property_ref),
  CHECK((unit_ref IS NULL AND lease_ref IS NULL)
     OR (unit_ref IS NOT NULL AND lease_ref IS NOT NULL))
);
CREATE INDEX IF NOT EXISTS notices_property ON property_notices(property_ref,unit_ref,lease_ref);
CREATE TABLE IF NOT EXISTS notice_reads (
  notice_ref TEXT NOT NULL REFERENCES property_notices(notice_ref),
  subject_ref TEXT NOT NULL,
  lease_ref TEXT NOT NULL REFERENCES leases(lease_ref),
  property_ref TEXT NOT NULL REFERENCES properties(property_ref),
  unit_ref TEXT NOT NULL,
  read_at TEXT NOT NULL,
  PRIMARY KEY(notice_ref,lease_ref,subject_ref),
  FOREIGN KEY(lease_ref,unit_ref,property_ref) REFERENCES leases(lease_ref,unit_ref,property_ref)
);
CREATE TABLE IF NOT EXISTS work_appointments (
  appointment_ref TEXT PRIMARY KEY,
  work_ref TEXT NOT NULL REFERENCES work_orders(work_ref),
  property_ref TEXT NOT NULL REFERENCES properties(property_ref),
  unit_ref TEXT NOT NULL,
  requested_by TEXT NOT NULL,
  start_at TEXT NOT NULL,
  end_at TEXT NOT NULL,
  state TEXT NOT NULL DEFAULT 'requested'
    CHECK(state IN ('requested','proposed','accepted','cancelled')),
  revision INTEGER NOT NULL DEFAULT 1 CHECK(revision>0),
  updated_at TEXT NOT NULL,
  FOREIGN KEY(unit_ref,property_ref) REFERENCES units(unit_ref,property_ref)
);
CREATE INDEX IF NOT EXISTS appointments_per_work ON work_appointments(work_ref,state);
CREATE UNIQUE INDEX IF NOT EXISTS one_active_appointment_per_work
  ON work_appointments(work_ref) WHERE state!='cancelled';
CREATE TABLE IF NOT EXISTS appointment_events (
  event_ref TEXT PRIMARY KEY,
  appointment_ref TEXT NOT NULL REFERENCES work_appointments(appointment_ref),
  actor_ref TEXT NOT NULL,
  action TEXT NOT NULL CHECK(action IN ('requested','proposed','accepted','cancelled')),
  revision INTEGER NOT NULL,
  recorded_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS appointment_event_history ON appointment_events(appointment_ref,revision);
CREATE UNIQUE INDEX IF NOT EXISTS lease_scope_identity ON leases(lease_ref,unit_ref,property_ref);
CREATE TABLE IF NOT EXISTS physical_assets (
  asset_ref TEXT PRIMARY KEY,
  property_ref TEXT NOT NULL REFERENCES properties(property_ref),
  unit_ref TEXT,
  label TEXT NOT NULL,
  category TEXT NOT NULL,
  lifecycle TEXT NOT NULL DEFAULT 'active' CHECK(lifecycle IN ('active','retired')),
  recorded_at TEXT NOT NULL,
  FOREIGN KEY(unit_ref,property_ref) REFERENCES units(unit_ref,property_ref),
  UNIQUE(asset_ref,property_ref)
);
CREATE INDEX IF NOT EXISTS assets_per_property ON physical_assets(property_ref,unit_ref);
CREATE TABLE IF NOT EXISTS preventive_plans (
  plan_ref TEXT PRIMARY KEY,
  property_ref TEXT NOT NULL,
  asset_ref TEXT NOT NULL,
  cadence_days INTEGER NOT NULL CHECK(cadence_days BETWEEN 1 AND 3650),
  next_due_on TEXT NOT NULL,
  last_completed_on TEXT,
  revision INTEGER NOT NULL DEFAULT 1,
  enabled INTEGER NOT NULL DEFAULT 1 CHECK(enabled IN (0,1)),
  FOREIGN KEY(asset_ref,property_ref) REFERENCES physical_assets(asset_ref,property_ref)
);
CREATE INDEX IF NOT EXISTS preventive_due ON preventive_plans(property_ref,enabled,next_due_on);
CREATE TABLE IF NOT EXISTS preventive_completion_events (
  completion_ref TEXT PRIMARY KEY,
  plan_ref TEXT NOT NULL REFERENCES preventive_plans(plan_ref),
  work_ref TEXT NOT NULL REFERENCES work_orders(work_ref),
  proof_ref TEXT NOT NULL UNIQUE,
  completed_on TEXT NOT NULL,
  actor_ref TEXT NOT NULL,
  plan_revision INTEGER NOT NULL,
  recorded_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS plan_completion_history ON preventive_completion_events(plan_ref,plan_revision);
CREATE TABLE IF NOT EXISTS inspections (
  inspection_ref TEXT PRIMARY KEY,
  property_ref TEXT NOT NULL REFERENCES properties(property_ref),
  unit_ref TEXT,
  category TEXT NOT NULL,
  state TEXT NOT NULL CHECK(state IN ('planned','in_progress','review','closed')),
  planned_on TEXT NOT NULL,
  revision INTEGER NOT NULL DEFAULT 1,
  created_by TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  FOREIGN KEY(unit_ref,property_ref) REFERENCES units(unit_ref,property_ref),
  UNIQUE(inspection_ref,unit_ref,property_ref)
);
CREATE INDEX IF NOT EXISTS inspections_per_property ON inspections(property_ref,unit_ref,state);
CREATE TABLE IF NOT EXISTS inspection_findings (
  finding_ref TEXT PRIMARY KEY,
  inspection_ref TEXT NOT NULL REFERENCES inspections(inspection_ref),
  severity TEXT NOT NULL CHECK(severity IN ('observation','minor','major','urgent')),
  narrative TEXT NOT NULL,
  recorded_by TEXT NOT NULL,
  recorded_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS inspection_resolutions (
  resolution_ref TEXT PRIMARY KEY,
  finding_ref TEXT NOT NULL UNIQUE REFERENCES inspection_findings(finding_ref),
  proof_ref TEXT NOT NULL UNIQUE,
  verified_by TEXT NOT NULL,
  recorded_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS turnovers (
  turnover_ref TEXT PRIMARY KEY,
  property_ref TEXT NOT NULL,
  unit_ref TEXT NOT NULL,
  lease_ref TEXT NOT NULL,
  state TEXT NOT NULL CHECK(state IN ('planned','inspection','work','final_review','complete')),
  revision INTEGER NOT NULL DEFAULT 1,
  final_vault_proof_ref TEXT UNIQUE,
  created_by TEXT NOT NULL,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  FOREIGN KEY(unit_ref,property_ref) REFERENCES units(unit_ref,property_ref),
  FOREIGN KEY(lease_ref,unit_ref,property_ref) REFERENCES leases(lease_ref,unit_ref,property_ref)
);
CREATE UNIQUE INDEX IF NOT EXISTS one_unfinished_turnover_per_unit
 ON turnovers(unit_ref) WHERE state!='complete';
CREATE INDEX IF NOT EXISTS turnovers_property ON turnovers(property_ref,state);
CREATE TABLE IF NOT EXISTS turnover_events (
  event_ref TEXT PRIMARY KEY,
  turnover_ref TEXT NOT NULL REFERENCES turnovers(turnover_ref),
  actor_ref TEXT NOT NULL,
  from_state TEXT,
  to_state TEXT NOT NULL,
  revision INTEGER NOT NULL,
  occurred_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS turnover_history ON turnover_events(turnover_ref,revision);
CREATE TABLE IF NOT EXISTS turnover_inspections (
  turnover_ref TEXT PRIMARY KEY REFERENCES turnovers(turnover_ref),
  inspection_ref TEXT NOT NULL UNIQUE REFERENCES inspections(inspection_ref)
);
CREATE TABLE IF NOT EXISTS leasing_prospects (
  prospect_ref TEXT PRIMARY KEY,
  property_ref TEXT NOT NULL REFERENCES properties(property_ref),
  contact_vault_ref TEXT NOT NULL,
  desired_unit_ref TEXT,
  stage TEXT NOT NULL DEFAULT 'new'
    CHECK(stage IN ('new','contacted','tour_scheduled','application_received','manual_review','closed')),
  revision INTEGER NOT NULL DEFAULT 1,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  FOREIGN KEY(desired_unit_ref,property_ref) REFERENCES units(unit_ref,property_ref),
  UNIQUE(prospect_ref,property_ref)
);
CREATE INDEX IF NOT EXISTS prospects_by_property ON leasing_prospects(property_ref,stage);
CREATE TABLE IF NOT EXISTS leasing_tours (
  tour_ref TEXT PRIMARY KEY,
  property_ref TEXT NOT NULL,
  prospect_ref TEXT NOT NULL,
  unit_ref TEXT NOT NULL,
  starts_at TEXT NOT NULL,
  created_by TEXT NOT NULL,
  FOREIGN KEY(prospect_ref,property_ref) REFERENCES leasing_prospects(prospect_ref,property_ref),
  FOREIGN KEY(unit_ref,property_ref) REFERENCES units(unit_ref,property_ref)
);
CREATE INDEX IF NOT EXISTS tours_by_property ON leasing_tours(property_ref,starts_at);
"""


class GroundsStoreBase:
    """Nominal boundary for transaction-backed Grounds stores.

    Domain code needs only transaction(write=...) yielding a SQL cursor-like
    executor. It must never infer live readiness from this base class alone.
    """
    def transaction(self, *, write: bool = False):
        raise NotImplementedError


class GroundsStore(GroundsStoreBase):
    """SQLite is for disposable fictional local fixtures only."""

    def __init__(self, path: str | Path):
        if not isinstance(path, (str, Path)) or not str(path).strip() or str(path) == ":memory:":
            raise ValueError("durable local test DB path required")
        self.path = Path(path)

    @contextmanager
    def transaction(self, *, write: bool = False):
        connection = sqlite3.connect(str(self.path), timeout=5)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        try:
            if write:
                connection.execute("BEGIN IMMEDIATE")
            yield connection
            if write:
                connection.commit()
        except Exception:
            if write:
                connection.rollback()
            raise
        finally:
            connection.close()

    def initialize(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if self.path.is_symlink():
            raise ValueError("local Grounds fixture may not be a symlink")
        if self.path.is_file():
            # CREATE TABLE IF NOT EXISTS is NOT a schema migration. Refuse known
            # old disposable layouts before any schema DDL could partly modify
            # them. Real private database migrations must be designed separately.
            with self.transaction() as check:
                for table in ("property_notices","notice_reads"):
                    exists=check.execute(
                        "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?",
                        (table,),
                    ).fetchone()
                    if exists:
                        columns={item["name"] for item in check.execute(
                            'PRAGMA table_info("'+table+'")',
                        )}
                        if "lease_ref" not in columns:
                            raise ValueError(
                                "legacy local Grounds schema: no automatic notice migration; "
                                "recreate disposable fictional fixture only"
                            )
        with self.transaction() as db:
            db.executescript(SCHEMA)
