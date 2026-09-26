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
  headline TEXT NOT NULL,
  body TEXT NOT NULL,
  published_at TEXT NOT NULL,
  FOREIGN KEY(unit_ref,property_ref) REFERENCES units(unit_ref,property_ref)
);
CREATE INDEX IF NOT EXISTS notices_property ON property_notices(property_ref,unit_ref);
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


class GroundsStore:
    """Owned by the future certified application composition root only."""

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
        with self.transaction() as db:
            db.executescript(SCHEMA)
