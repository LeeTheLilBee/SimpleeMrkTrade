"""GRD099 — driver-free static compatibility checks; no fake claim of PG runtime.

Actual PostgreSQL execution lives in test_grounds_postgres.py and is SKIPPED
unless a dedicated, disposable test PostgreSQL service/DSN is supplied.
"""
from __future__ import annotations

import sqlite3
import unittest
from pathlib import Path
from types import SimpleNamespace

from grounds.postgres import (
    MIGRATION_ID, PgResults, PgRow, PgSession,
    PostgresGroundsConfigurationError, PostgresGroundsStore,
)
from grounds.storage import GroundsStoreBase


class FakeIntegrityError(Exception):
    pass

class StubCursor:
    description=(SimpleNamespace(name="work_ref"),SimpleNamespace(name="revision"))
    rowcount=1
    def __init__(self):
        self.sql=None
        self.parameters=None
        self.remaining=[("work-fake",2)]
    def execute(self,sql,params):
        self.sql=sql;self.parameters=params
        if "RAISE" in sql:
            raise FakeIntegrityError("mock only")
    def fetchone(self):
        return self.remaining.pop(0) if self.remaining else None
    def fetchall(self):
        rows=self.remaining[:];self.remaining.clear();return rows
    def __iter__(self):
        yield from self.remaining
    def close(self):
        pass

class StubConnection:
    def __init__(self):self.cursors=[]
    def cursor(self):
        cursor=StubCursor();self.cursors.append(cursor);return cursor


class PostgresStaticTests(unittest.TestCase):
    def test_baseline_constraints_and_fk_order(self):
        schema=(Path(__file__).parent/"sql"/"0001_initial_postgres.sql").read_text()
        self.assertNotIn("PRAGMA foreign_keys",schema)
        self.assertNotIn("DROP TABLE",schema)
        self.assertLess(
            schema.index("CREATE UNIQUE INDEX IF NOT EXISTS lease_scope_identity"),
            schema.index("CREATE TABLE IF NOT EXISTS lease_members"),
        )
        for term in (
            "FOREIGN KEY(lease_ref,unit_ref,property_ref)",
            "one_active_lease_per_unit",
            "one_active_appointment_per_work",
            "one_unfinished_turnover_per_unit",
            "resource_event_one_reversal",
            "lease_ref TEXT",
            "grounds_schema_migrations",
        ):
            self.assertIn(term,schema)

    def test_row_is_both_mapping_and_ordinal(self):
        row=PgRow(("item","quantity"),("washer",3))
        self.assertEqual(row["item"],row[0])
        self.assertEqual(row["quantity"],row[1])
        self.assertEqual(dict(row),{"item":"washer","quantity":3})
        cursor=StubCursor()
        self.assertEqual(PgResults(cursor).fetchone()["work_ref"],"work-fake")
        self.assertIsNone(PgResults(cursor).fetchone())

    def test_placeholder_translation_never_interpolates_user_text(self):
        conn=StubConnection()
        session=PgSession(conn,FakeIntegrityError)
        result=session.execute(
            "SELECT work_ref,revision FROM work_orders WHERE work_ref=?",
            ("x'; DROP TABLE leases; --",),
        )
        self.assertIn("%s",conn.cursors[0].sql)
        self.assertNotIn("DROP TABLE",conn.cursors[0].sql)
        self.assertEqual(conn.cursors[0].parameters,("x'; DROP TABLE leases; --",))
        self.assertEqual(result.fetchone()["revision"],2)
        with self.assertRaises(ValueError):
            session.execute("SELECT ? + ?",(1,))
        with self.assertRaises(sqlite3.IntegrityError):
            session.execute("RAISE ?",("test",))

    def test_constructor_does_not_provision_database(self):
        with self.assertRaises(PostgresGroundsConfigurationError):
            PostgresGroundsStore("")
        store=PostgresGroundsStore("postgresql://unused.example/grounds")
        self.assertIsInstance(store,GroundsStoreBase)
        self.assertEqual(MIGRATION_ID,"grounds-postgres-baseline-0001")
        with self.assertRaises(PostgresGroundsConfigurationError):
            store.initialize()


if __name__=="__main__":
    unittest.main()
