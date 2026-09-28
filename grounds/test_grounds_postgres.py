"""GRD098 — real PostgreSQL behavior tests using a disposable GitHub Actions DB.

These tests run only when CI supplies a private synthetic test PostgreSQL DSN.
Never point GROUNDS_TEST_POSTGRES_URL at live or shared customer data.
"""
from __future__ import annotations

import io
import json
import os
import re
import sqlite3
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from uuid import uuid4

from grounds.access import AccessDenied
from grounds.acquisition_handoff import GroundsAcquisitionHandoff, SCHEMA_VERSION as CLOSE_SCHEMA
from grounds.communications import GroundsCommunications
from grounds.delivery import GroundsDeliveryReceipts, SCHEMA_VERSION as DELIVERY_SCHEMA
from grounds.maintenance import MaintenanceIntake
from grounds.operations import GroundsConflict, GroundsOperations
from grounds.postgres import (
    MIGRATION_ID, PgRow, PostgresGroundsConfigurationError, PostgresGroundsStore,
)
from grounds.safety import GroundsSafety
from grounds.test_grounds_operations import fixture_scope
from grounds.work_resources import GroundsWorkResources
from grounds.web import GroundsWebApp

URL=os.environ.get("GROUNDS_TEST_POSTGRES_URL")

@unittest.skipUnless(URL and os.environ.get("GROUNDS_POSTGRES_TEST_ONLY")=="true",
                     "synthetic CI PostgreSQL service required")
class PostgresGroundsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import psycopg
        cls.conn_string=URL
        cls.store=PostgresGroundsStore(URL)
        sql=(Path(__file__).parent/"sql"/"0001_initial_postgres.sql").read_text(encoding="utf-8")
        if "DROP TABLE" in sql.upper() or "PRAGMA" in sql:
            raise AssertionError("PostgreSQL baseline cannot drop schema or contain SQLite PRAGMA")
        # Only a disposable CI database. The migration script itself is static,
        # contains no user records and is not executed by production app startup.
        stripped=re.sub(r"(?m)^--[^\n]*(?:\n|$)","",sql)
        with psycopg.connect(URL,autocommit=True) as db:
            for statement in stripped.split(";"):
                if statement.strip():
                    db.execute(statement)
            db.execute(
                """INSERT INTO grounds_schema_migrations(version,migration_id)
                   VALUES (%s,%s) ON CONFLICT (version) DO NOTHING""",
                (1,MIGRATION_ID),
            )

    def setUp(self):
        self.id="p"+uuid4().hex[:16]
        self.b="b"+uuid4().hex[:16]
        self.u="u"+uuid4().hex[:16]
        self.l="l"+uuid4().hex[:16]
        self.w="w"+uuid4().hex[:16]
        self.ops=GroundsOperations(self.store)
        self.comms=GroundsCommunications(self.store)
        self.safety=GroundsSafety(self.store)
        self.resources=GroundsWorkResources(self.store)
        self.owner=fixture_scope("owner","owner",(self.id,))
        self.manager=fixture_scope("manager","property_manager",(self.id,))
        self.resident=fixture_scope("resident","resident",(self.id,),(self.u,))
        self.ops.record_closed_property(
            self.owner,property_ref=self.id,name="Synthetic PostgreSQL Property",
            close_evidence={"status":"verified_closed","property_ref":self.id,
                            "proof_ref":"proof-"+self.id,"owned_on":"2026-09-26"},
            close_verifier=lambda doc:doc, # FIXTURE ONLY
        )
        self.ops.add_building(self.manager,property_ref=self.id,building_ref=self.b,label="A")
        self.ops.add_unit(self.manager,property_ref=self.id,building_ref=self.b,
                          unit_ref=self.u,label="101")
        self.ops.activate_lease(
            self.manager,property_ref=self.id,unit_ref=self.u,lease_ref=self.l,
            resident_ref="resident",start_on="2026-09-26",end_on="2027-09-25",
        )

    def test_real_postgres_wsgi_browser_command_to_durable_rows(self):
        # This remains an in-process synthetic Tower receiver, NEVER a public
        # authentication route. The HTTP layer and persistence are REAL code/PG.
        app=GroundsWebApp(
            self.store,tower_receiver=lambda environ:environ["test.fixture.actor"],
            csrf_secret=bytes(range(32)),local_fixture_only=False,
        )
        def call(path,actor,*,method="GET",payload=None,key=None):
            raw=json.dumps(payload).encode("utf-8") if payload is not None else b""
            query=""
            if "?" in path:
                path,query=path.split("?",1)
            env={
                "REQUEST_METHOD":method,"PATH_INFO":path,"QUERY_STRING":query,
                "CONTENT_TYPE":"application/json","CONTENT_LENGTH":str(len(raw)),
                "wsgi.input":io.BytesIO(raw),"test.fixture.actor":actor,
            }
            if method=="POST":
                env["HTTP_X_GROUNDS_CSRF"]=app.csrf.token(actor)
                if key:
                    env["HTTP_X_GROUNDS_IDEMPOTENCY_KEY"]=key
            response={}
            def start(status,headers):
                response["status"]=status
                response["headers"]=dict(headers)
            data=b"".join(app(env,start))
            response["json"]=json.loads(data)
            return response
        payload={
            "property_ref":self.id,"unit_ref":self.u,"category":"plumbing",
            "description":"Actual Postgres-backed WSGI synthetic check",
            "emergency_flag":False,"entry_permission":"contact_first",
        }
        key=str(uuid4())
        first=call("/grounds/api/work",self.resident,method="POST",payload=payload,key=key)
        self.assertEqual(first["status"],"201 Created")
        repeat=call("/grounds/api/work",self.resident,method="POST",payload=payload,key=key)
        self.assertTrue(repeat["json"]["replayed"])
        self.assertEqual(first["json"]["work_ref"],repeat["json"]["work_ref"])
        work=first["json"]["work_ref"]
        listing=call(
            "/grounds/api/workspace?property_ref="+self.id+"&unit_ref="+self.u,
            self.resident,
        )
        self.assertEqual(listing["json"]["work_orders"][0]["work_ref"],work)
        self.assertIsNone(listing["json"]["rent"]["amount_due_cents"])
        start=datetime.now(timezone.utc)+timedelta(days=3)
        ap_payload={"work_ref":work,"start_at":start.isoformat(),
                    "end_at":(start+timedelta(hours=2)).isoformat()}
        ap_key=str(uuid4())
        ap=call("/grounds/api/appointment/request",self.resident,method="POST",
                payload=ap_payload,key=ap_key)
        self.assertEqual(ap["status"],"201 Created")
        ap_retry=call("/grounds/api/appointment/request",self.resident,method="POST",
                      payload=ap_payload,key=ap_key)
        self.assertTrue(ap_retry["json"]["replayed"])
        self.assertEqual(ap_retry["json"]["appointment_ref"],ap["json"]["appointment_ref"])
        with self.store.transaction() as db:
            self.assertEqual(db.execute(
                "SELECT COUNT(*) FROM work_orders WHERE property_ref=?",(self.id,),
            ).fetchone()[0],1)
            self.assertEqual(db.execute(
                "SELECT COUNT(*) FROM work_events WHERE work_ref=?",(work,),
            ).fetchone()[0],1)
            self.assertEqual(db.execute(
                "SELECT COUNT(*) FROM work_appointments WHERE work_ref=?",(work,),
            ).fetchone()[0],1)
        outsider=fixture_scope("wrong","resident",(self.id,),(self.u,))
        self.assertEqual(call("/grounds/api/work?work_ref="+work,outsider)["status"],
                         "404 Not Found")
        self.ops.end_lease(self.manager,property_ref=self.id,lease_ref=self.l,
                           expected_revision=1)
        with self.store.transaction(write=True) as db:
            # CI-only stand-in for independent proof-gated turnover; not API.
            db.execute("UPDATE units SET lifecycle='ready' WHERE unit_ref=?",(self.u,))
        self.ops.activate_lease(self.manager,property_ref=self.id,unit_ref=self.u,
                                lease_ref="next-"+self.l,resident_ref="resident",
                                start_on="2028-01-01",end_on="2028-12-31")
        self.assertEqual(call("/grounds/api/work?work_ref="+work,self.resident)["status"],
                         "404 Not Found")
        self.assertEqual(call("/grounds/api/appointments?work_ref="+work,self.resident)["status"],
                         "404 Not Found")

    def test_post_close_and_delivery_receipt_ledgers_execute_on_real_postgres(self):
        close_property="pc"+uuid4().hex[:16]
        close_owner=fixture_scope("owner","owner",(close_property,))
        close=GroundsAcquisitionHandoff(self.store)
        payload={
            "schema_version":CLOSE_SCHEMA,"source":"tower","audience":"grounds",
            "kind":"multifamily_post_close","handoff_ref":"h-"+uuid4().hex,
            "owner_ref":"owner","property_ref":close_property,
            "property_name":"Synthetic Closed Property","owned_on":"2026-09-28",
            "opportunity_id":"opp-"+uuid4().hex[:12],"opportunity_revision":3,
            "input_snapshot_digest":"a"*64,"proposal_fingerprint":"b"*64,
            "vertical_id":"multifamily","proposed_recipient":"grounds",
            "closing_status":"completed","ownership_status":"verified_owner",
            "encumbrance_status":"verified_recorded",
            "tower_close_receipt_ref":"close-"+uuid4().hex,
            "title_proof_ref":"title-"+uuid4().hex,
            "encumbrance_review_ref":"enc-"+uuid4().hex,
            "issued_at":990,"expires_at":1100,
        }
        accepted=close.accept_multifamily_close(
            close_owner,signed_handoff=payload,tower_verifier=lambda doc:doc,now=1000,
        )
        self.assertTrue(accepted["accepted"])
        self.assertTrue(close.accept_multifamily_close(
            close_owner,signed_handoff=payload,tower_verifier=lambda doc:doc,now=1000,
        )["replayed"])

        work="delivery-"+uuid4().hex
        self.ops.submit_maintenance(
            self.resident,work_ref=work,
            intake=MaintenanceIntake(
                self.id,self.u,"plumbing","PG delivery receipt check",False,"contact_first",
            ),
        )
        event=next(
            item for item in self.safety.pending_event_intents(
                self.manager,property_ref=self.id,
            )
            if item["resource_ref"]==work and item["event_kind"]=="work_changed"
        )
        delivery=GroundsDeliveryReceipts(self.store)
        receipt={
            "schema_version":DELIVERY_SCHEMA,"source":"tower_delivery_gateway",
            "audience":"grounds","kind":"notification_delivery",
            "receipt_ref":"receipt-"+uuid4().hex,
            "event_ref":event["event_ref"],"property_ref":self.id,
            "event_kind":event["event_kind"],"resource_ref":work,
            "source_revision":event["source_revision"],
            "provider_receipt_ref":"provider-"+uuid4().hex,
            "delivery_state":"delivered","observed_at":990,"expires_at":1100,
        }
        saved=delivery.record(
            receipt,receipt_verifier=lambda doc:doc,now=1000,
        )
        self.assertEqual(saved["delivery_state"],"delivered")
        self.assertEqual(
            delivery.property_status(self.manager,property_ref=self.id)["delivered_event_count"],1,
        )

    def test_readiness_checks_actual_postgres_and_explicit_receiver_health(self):
        class SyntheticTowerReceiver:
            def __call__(self,environ):
                return environ["test.fixture.actor"]
            def health_check(self):
                return True  # CI fixture ONLY; no real Tower signature here.
        app=GroundsWebApp(
            self.store,tower_receiver=SyntheticTowerReceiver(),
            csrf_secret=bytes(range(32)),local_fixture_only=False,
        )
        def probe(path):
            result={}
            def start(status,headers):
                result["status"]=status
                result["headers"]=dict(headers)
            payload=b"".join(app({
                "REQUEST_METHOD":"GET","PATH_INFO":path,
                "QUERY_STRING":"","wsgi.input":io.BytesIO(),
            },start))
            result["json"]=json.loads(payload)
            return result
        self.assertEqual(probe("/grounds/health/live")["status"],"200 OK")
        self.assertEqual(probe("/grounds/health/ready")["json"],{"ready":True})
        self.assertEqual(probe("/grounds/api/me")["status"],"401 Unauthorized")

    def test_schema_does_not_auto_migrate_and_row_shape(self):
        ready=self.store.assert_schema_ready()
        self.assertEqual(ready["backend"],"postgresql")
        self.assertTrue(ready["schema_compatible"])
        self.assertFalse(ready["backup_restore_certified"])
        self.assertFalse(ready["tower_receiver_certified"])
        with self.assertRaises(PostgresGroundsConfigurationError):
            self.store.initialize()
        with self.store.transaction() as db:
            row=db.execute(
                "SELECT property_ref,name FROM properties WHERE property_ref=?",(self.id,),
            ).fetchone()
            self.assertIsInstance(row,PgRow)
            self.assertEqual(row[0],row["property_ref"])
            self.assertEqual(dict(row)["name"],"Synthetic PostgreSQL Property")

    def test_real_postgres_lease_work_notice_appointment_and_scope(self):
        created=self.ops.submit_maintenance(
            self.resident,work_ref=self.w,
            intake=MaintenanceIntake(
                self.id,self.u,"plumbing","Pg synthetic leak",True,"contact_first",
            ),
        )
        self.assertEqual(created["state"],"submitted")
        with self.assertRaises(GroundsConflict):
            self.ops.advance_work_order(
                self.manager,work_ref=self.w,next_state="received",expected_revision=1,
            )
        self.safety.acknowledge_urgency(
            self.manager,work_ref=self.w,assessed_urgency="priority",
        )
        moved=self.ops.advance_work_order(
            self.manager,work_ref=self.w,next_state="received",expected_revision=1,
        )
        self.assertEqual(moved["revision"],2)
        with self.assertRaises(GroundsConflict):
            self.ops.advance_work_order(
                self.manager,work_ref=self.w,next_state="under_review",expected_revision=1,
            )
        notice="notice-"+self.id
        self.ops.publish_notice(self.manager,property_ref=self.id,unit_ref=self.u,
                                notice_ref=notice,headline="Synthetic unit notice",body="Test")
        self.assertEqual(self.ops.resident_home(
            self.resident,property_ref=self.id,unit_ref=self.u)["notices"][0]["read_in_app"],0)
        self.comms.mark_notice_read(
            self.resident,property_ref=self.id,unit_ref=self.u,notice_ref=notice,
        )
        self.assertEqual(self.ops.resident_home(
            self.resident,property_ref=self.id,unit_ref=self.u)["notices"][0]["read_in_app"],1)
        start=datetime.now(timezone.utc)+timedelta(days=2)
        appointment="appointment-"+self.id
        requested=self.comms.request_appointment(
            self.resident,work_ref=self.w,appointment_ref=appointment,
            start_at=start.isoformat(),end_at=(start+timedelta(hours=1)).isoformat(),
        )
        self.assertEqual(requested["state"],"requested")
        outside=fixture_scope("out","resident",(self.id,),(self.u,))
        with self.assertRaises(AccessDenied):
            self.comms.appointment(outside,appointment_ref=appointment)
        with self.store.transaction() as db:
            self.assertEqual(db.execute(
                "SELECT COUNT(*) FROM event_outbox WHERE property_ref=?",(self.id,),
            ).fetchone()[0],4)  # creation, urgent metadata, work move, notice

    def test_real_transaction_integrity_and_no_old_lease_visibility(self):
        with self.assertRaises(GroundsConflict):
            self.ops.activate_lease(
                self.manager,property_ref=self.id,unit_ref=self.u,
                lease_ref="other-"+self.l,resident_ref="wrong",
                start_on="2026-09-26",end_on="2027-09-25",
            )
        with self.store.transaction() as db:
            self.assertEqual(db.execute(
                "SELECT COUNT(*) FROM leases WHERE property_ref=?",(self.id,),
            ).fetchone()[0],1)
        self.ops.submit_maintenance(
            self.resident,work_ref=self.w,
            intake=MaintenanceIntake(self.id,self.u,"plumbing","Private old lease",False,"contact_first"),
        )
        self.ops.end_lease(self.manager,property_ref=self.id,lease_ref=self.l,expected_revision=1)
        with self.store.transaction(write=True) as db:
            # Disposable CI fixture only; certified real turnover is required
            # for any actual release of a unit back to ready.
            db.execute("UPDATE units SET lifecycle='ready' WHERE unit_ref=?",(self.u,))
        self.ops.activate_lease(
            self.manager,property_ref=self.id,unit_ref=self.u,
            lease_ref="new-"+self.l,resident_ref="resident",
            start_on="2028-01-01",end_on="2028-12-31",
        )
        self.assertEqual(self.ops.list_work_orders(self.resident,property_ref=self.id),[])
        with self.assertRaises(AccessDenied):
            self.ops.get_work_order(self.resident,work_ref=self.w)

    def test_postgres_integrity_error_maps_to_domain_conflict(self):
        with self.store.transaction(write=True) as db:
            with self.assertRaises(sqlite3.IntegrityError):
                db.execute(
                    """INSERT INTO units(unit_ref,property_ref,building_ref,label)
                       VALUES(?,?,?,?)""",
                    ("bad-"+self.u,self.id,"wrong-building","Unsafe"),
                )


if __name__=="__main__":
    unittest.main()
