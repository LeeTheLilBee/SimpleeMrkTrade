"""GRD097 — production-oriented PostgreSQL transaction adapter for Grounds.

This is a *real PostgreSQL* backend implementation, not a simulation or a
SQLite file in a hosted container. Connections use psycopg 3 when installed.
DDL is NOT auto-applied: the separate SQL migration needs approved private
database provisioning, backups, review and operator execution. A source-code
adapter alone does not certify tenant data protection, infrastructure or
authentication. No credentials or hosts are committed to the repository.

Existing domain SQL uses the DB-API '?'/sqlite-style positional parameter; this
adapter translates placeholders ONLY on trusted internal SQL statements, never
user-provided SQL. It maps PostgreSQL integrity errors to the legacy domain's
sqlite3.IntegrityError catch sites for consistent application conflicts.
Write transactions use SERIALIZABLE with no unsafe automatic retries.
"""
from __future__ import annotations

import sqlite3
from collections.abc import Mapping
from contextlib import contextmanager
from typing import Iterator

from .storage import GroundsStoreBase

MIGRATION_ID="grounds-postgres-baseline-0001"
_REQUIRED_COLUMNS={
    "properties":("property_ref","owned_on","close_proof_ref"),
    "property_acquisition_receipts":("handoff_ref","property_ref","opportunity_id","opportunity_revision","proposal_fingerprint","tower_close_receipt_ref","receipt_digest"),
    "buildings":("building_ref","property_ref"),
    "units":("unit_ref","property_ref","building_ref","lifecycle"),
    "leases":("lease_ref","property_ref","unit_ref","resident_ref","status","revision"),
    "lease_members":("lease_ref","property_ref","unit_ref","subject_ref","status"),
    "work_orders":("work_ref","property_ref","unit_ref","lease_ref","revision","state"),
    "work_messages":("message_ref","work_ref","property_ref","author_ref","audience","body"),
    "work_completion_events":("event_ref","work_ref","property_ref","unit_ref","lease_ref","resident_ref","outcome","from_revision","to_revision","resulting_state"),
    "move_task_events":("event_ref","lease_ref","property_ref","unit_ref","subject_ref","phase","task_ref","status","revision"),
    "resident_access_events":("access_ref","lease_ref","property_ref","unit_ref","actor_ref","resource_kind","resource_ref"),
    "property_notices":("notice_ref","property_ref","unit_ref","lease_ref"),
    "notice_reads":("notice_ref","subject_ref","property_ref","unit_ref","lease_ref"),
    "work_appointments":("appointment_ref","work_ref","requested_by","state","revision"),
    "event_outbox":("event_ref","property_ref","event_kind","source_revision"),
    "event_delivery_receipts":("receipt_ref","event_ref","property_ref","receipt_kind","delivery_state","provider_receipt_ref","receipt_digest"),
    "work_resource_events":("event_ref","work_ref","action","resource_type"),
    "grounds_schema_migrations":("version","migration_id"),
}
_REQUIRED_INDEXES=frozenset((
    "lease_scope_identity","one_active_lease_per_unit",
    "one_active_appointment_per_work","one_unfinished_turnover_per_unit",
    "resource_event_one_reversal","acquisition_receipt_opportunity",
    "delivery_receipts_property","delivery_receipts_event","work_messages_scope_idx",
    "move_task_lease_subject_idx","resident_access_lease_subject_idx",
    "work_completion_work_idx",
))

class PostgresGroundsConfigurationError(ValueError):
    pass

class PgRow(Mapping):
    """Supports the existing SQLite row access by name or zero-based position."""
    __slots__=("_fields","_values","_named")
    def __init__(self,fields,values):
        self._fields=tuple(fields)
        self._values=tuple(values)
        self._named=dict(zip(self._fields,self._values))
    def __getitem__(self,key):
        if type(key) is int:
            return self._values[key]
        return self._named[key]
    def __iter__(self)->Iterator[str]:
        return iter(self._named)
    def __len__(self):
        return len(self._fields)

class PgResults:
    def __init__(self,cursor):
        self.cursor=cursor
        self._fields=tuple(column.name for column in (cursor.description or ()))
    def fetchone(self):
        row=self.cursor.fetchone()
        return PgRow(self._fields,row) if row is not None else None
    def fetchall(self):
        return [PgRow(self._fields,row) for row in self.cursor.fetchall()]
    def __iter__(self):
        for row in self.cursor:
            yield PgRow(self._fields,row)
    @property
    def rowcount(self):
        return self.cursor.rowcount

class PgSession:
    def __init__(self,connection,integrity_error):
        self.connection=connection
        self.integrity_error=integrity_error
    def execute(self,sql,params=()):
        if not isinstance(sql,str):
            raise TypeError("trusted internal SQL string required")
        if not isinstance(params,(tuple,list)):
            raise TypeError("positional SQL parameters required")
        # Domain SQL is static and uses '?' solely for positional parameters.
        # Guard accidental placeholder mismatch and prohibit raw user queries
        # at the WSGI service layer; this is NOT a general SQL parser.
        if sql.count("?") != len(params):
            raise ValueError("internal SQL parameter mismatch")
        cursor=self.connection.cursor()
        try:
            cursor.execute(sql.replace("?","%s"),tuple(params))
        except self.integrity_error as exc:
            cursor.close()
            raise sqlite3.IntegrityError("Grounds persistence constraint") from exc
        return PgResults(cursor)

class PostgresGroundsStore(GroundsStoreBase):
    """Privately provisioned DB. Does not create users, schema or resources."""
    def __init__(self,dsn:str):
        if not isinstance(dsn,str) or not dsn.strip():
            raise PostgresGroundsConfigurationError("private PostgreSQL DSN is required")
        # psycopg understands URI and keyword DSNs. Nothing is logged or echoed.
        self._dsn=dsn.strip()

    @contextmanager
    def transaction(self,*,write:bool=False):
        try:
            import psycopg
            from psycopg import IsolationLevel
        except ImportError as exc:
            raise PostgresGroundsConfigurationError(
                "psycopg 3 runtime dependency is not installed"
            ) from exc
        # Connection context closes on success/failure and commits/rolls back
        # a transaction. SERIALIZABLE writes prevent concurrent lease/state
        # checks from silently both succeeding; serialization errors are left
        # failed/rolled back, never retried around external proof callbacks.
        with psycopg.connect(self._dsn,connect_timeout=5) as db:
            db.isolation_level=(IsolationLevel.SERIALIZABLE if write
                                else IsolationLevel.READ_COMMITTED)
            yield PgSession(db,psycopg.IntegrityError)

    def initialize(self):
        raise PostgresGroundsConfigurationError(
            "never auto-initialize or migrate a live tenant database; "
            "review and apply grounds/sql/0001_initial_postgres.sql separately"
        )

    def assert_schema_ready(self)->dict:
        """Read-only compatibility check; doesn't claim backup/security approval."""
        with self.transaction() as db:
            marker=db.execute(
                "SELECT migration_id FROM grounds_schema_migrations WHERE version=?",
                (1,),
            ).fetchone()
            if marker is None or marker["migration_id"]!=MIGRATION_ID:
                raise PostgresGroundsConfigurationError("PostgreSQL baseline migration unverified")
            rows=db.execute(
                """SELECT table_name,column_name FROM information_schema.columns
                   WHERE table_schema=current_schema()""",
            )
            present={}
            for row in rows:
                present.setdefault(row["table_name"],set()).add(row["column_name"])
            missing={
                table:sorted(set(fields)-present.get(table,set()))
                for table,fields in _REQUIRED_COLUMNS.items()
                if set(fields)-present.get(table,set())
            }
            indexes={row[0] for row in db.execute(
                """SELECT indexname FROM pg_indexes WHERE schemaname=current_schema()"""
            )}
            missing_indexes=sorted(_REQUIRED_INDEXES-indexes)
            if missing or missing_indexes:
                raise PostgresGroundsConfigurationError(
                    "private Grounds database baseline is incomplete"
                )
            return {
                "backend":"postgresql","baseline_version":1,
                "schema_compatible":True,"source_only_adapter":False,
                "backup_restore_certified":False,
                "tower_receiver_certified":False,
                "payment_or_notification_connected":False,
            }
