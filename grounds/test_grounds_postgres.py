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
from grounds.delivery import GroundsDeliveryReceipts, SCHEMA_VERSION as DELIVERY_SCHEMA
from grounds.delivery_desk import GroundsDeliveryDesk
from grounds.communications import GroundsCommunications
from grounds.maintenance import MaintenanceIntake
from grounds.operations import GroundsConflict, GroundsOperations
from grounds.operational_release import GroundsOperationalReleaseGate
from grounds.postgres import (
    MIGRATION_ID, PgRow, PostgresGroundsConfigurationError, PostgresGroundsStore,
)
from grounds.safety import GroundsSafety
from grounds.test_grounds_operations import fixture_scope
from grounds.work_resources import GroundsWorkResources
from grounds.work_completion import GroundsWorkCompletion
from grounds.work_thread import GroundsWorkThread
from grounds.move_concierge import GroundsMoveConcierge
from grounds.privacy_log import GroundsResidentPrivacyLog
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


    def test_real_postgres_scoped_leasing_board_hides_contact(self):
        from grounds.leasing import GroundsLeasing
        leasing=GroundsLeasing(self.store)
        ref="prospect-"+self.id
        leasing.register_prospect(
            self.manager,property_ref=self.id,prospect_ref=ref,
            contact_vault_ref="private-contact-"+self.id,desired_unit_ref=self.u,
        )
        rows=leasing.list_prospects(self.manager,property_ref=self.id)
        self.assertEqual(rows[0]["prospect_ref"],ref)
        self.assertNotIn("contact_vault_ref",rows[0])
        app=GroundsWebApp(
            self.store,tower_receiver=lambda environ:environ["test.fixture.actor"],
            csrf_secret=bytes(range(32)),local_fixture_only=False,
        )
        def get(actor):
            result={}
            def start(status,headers):
                result["status"]=status
            raw=b"".join(app({
                "REQUEST_METHOD":"GET","PATH_INFO":"/grounds/api/leasing",
                "QUERY_STRING":"property_ref="+self.id,
                "test.fixture.actor":actor,"wsgi.input":io.BytesIO(b""),
            },start))
            result["json"]=json.loads(raw)
            return result
        visible=get(self.manager)
        self.assertEqual(visible["status"],"200 OK")
        self.assertEqual(visible["json"]["prospects"][0]["prospect_ref"],ref)
        self.assertNotIn("private-contact-"+self.id,str(visible["json"]))
        self.assertEqual(get(self.resident)["status"],"404 Not Found")


    def test_real_postgres_physical_workboard_role_and_backlog(self):
        from datetime import date
        from grounds.stewardship import GroundsStewardship
        stewardship=GroundsStewardship(self.store)
        asset="asset-"+self.id
        plan="plan-"+self.id
        stewardship.record_asset(
            self.manager,property_ref=self.id,unit_ref=self.u,
            asset_ref=asset,label="Synthetic equipment",category="heating",
        )
        stewardship.create_preventive_plan(
            self.manager,property_ref=self.id,asset_ref=asset,
            plan_ref=plan,cadence_days=30,
            next_due_on=(date.today()-timedelta(days=1)).isoformat(),
        )
        item=stewardship.physical_workboard(self.manager,property_ref=self.id)
        self.assertEqual(item["counts"]["assets"],1)
        self.assertEqual(item["counts"]["due_preventive_plans"],1)
        self.assertEqual(item["due_preventive_plans"][0]["plan_ref"],plan)
        self.assertFalse(item["provider_dispatch_confirmed"])
        supervisor=fixture_scope("supervisor","maintenance_supervisor",(self.id,))
        view=stewardship.physical_workboard(supervisor,property_ref=self.id)
        self.assertIsNone(view["counts"]["open_turnovers"])
        with self.assertRaises(AccessDenied):
            stewardship.physical_workboard(self.resident,property_ref=self.id)
        app=GroundsWebApp(
            self.store,tower_receiver=lambda environ:environ["test.fixture.actor"],
            csrf_secret=bytes(range(32)),local_fixture_only=False,
        )
        result={}
        def start(status,headers):
            result["status"]=status
        raw=b"".join(app({
            "REQUEST_METHOD":"GET","PATH_INFO":"/grounds/api/physical-desk",
            "QUERY_STRING":"property_ref="+self.id,
            "test.fixture.actor":self.manager,"wsgi.input":io.BytesIO(b""),
        },start))
        self.assertEqual(result["status"],"200 OK")
        self.assertEqual(json.loads(raw)["due_preventive_plans"][0]["plan_ref"],plan)


    def test_full_private_postgres_wsgi_operational_and_tower_gate_integration(self):
        """Real disposable PG and full actual WSGI stack; auth/issuer are FICTION ONLY."""
        class SyntheticReceiver:
            enabled=True
            def health_check(self):
                return self.enabled
            def __call__(self,environ):
                if not self.enabled:
                    raise AccessDenied("fiction-only synthetic Tower receiver revoked")
                return environ["test.fixture.actor"]

        class SyntheticOwnerRelease:
            healthy=False
            admitted=False
            def health_check(self):
                return self.healthy
            def __call__(self,environ):
                return self.admitted

        receiver=SyntheticReceiver()
        authority=SyntheticOwnerRelease()
        private_app=GroundsWebApp(
            self.store,tower_receiver=receiver,
            csrf_secret=bytes(range(32)),local_fixture_only=False,
        )
        app=GroundsOperationalReleaseGate(private_app,authority)

        def call(path,actor=None,*,method="GET",payload=None,csrf=None,key=None):
            raw=json.dumps(payload).encode("utf-8") if payload is not None else b""
            route,_,query=path.partition("?")
            env={
                "REQUEST_METHOD":method,"PATH_INFO":route,"QUERY_STRING":query,
                "CONTENT_TYPE":"application/json","CONTENT_LENGTH":str(len(raw)),
                "wsgi.input":io.BytesIO(raw),
            }
            if actor is not None:
                env["test.fixture.actor"]=actor
            if csrf is not None:
                env["HTTP_X_GROUNDS_CSRF"]=csrf
            if key is not None:
                env["HTTP_X_GROUNDS_IDEMPOTENCY_KEY"]=key
            result={}
            def start(status,headers):
                result["status"]=status
                result["headers"]=dict(headers)
            result["body"]=b"".join(app(env,start))
            if result["headers"]["Content-Type"].startswith("application/json"):
                result["json"]=json.loads(result["body"])
            return result

        workspace=("/grounds/api/workspace?property_ref="+self.id+
                   "&unit_ref="+self.u)
        rent="/grounds/api/rent?property_ref="+self.id+"&unit_ref="+self.u
        # DB/schema + resident fixture alone cannot unlock the protected app.
        self.assertEqual(call(workspace,self.resident)["status"],"503 Service Unavailable")
        self.assertEqual(call("/grounds/health/ready")["json"],{"ready":False})
        self.assertEqual(call("/grounds/health/live")["status"],"200 OK")
        authority.healthy=True
        self.assertEqual(call("/grounds/health/ready")["json"],{"ready":True})
        self.assertEqual(call(workspace,self.resident)["status"],"503 Service Unavailable")
        self.assertEqual(call("/grounds/app.js",self.resident)["status"],"503 Service Unavailable")

        authority.admitted=True
        self.assertEqual(call(workspace)["status"],"401 Unauthorized")
        outsider=fixture_scope("unlisted","resident",(self.id,),(self.u,))
        self.assertEqual(call(workspace,outsider)["status"],"404 Not Found")
        current=call(workspace,self.resident)
        self.assertEqual(current["status"],"200 OK")
        self.assertEqual(current["json"]["property_ref"],self.id)
        self.assertEqual(current["json"]["unit_ref"],self.u)
        self.assertEqual(current["json"]["lease"]["lease_ref"],self.l)
        unknown=call(rent,self.resident)
        self.assertEqual(unknown["json"]["status"],"not_connected")
        self.assertIsNone(unknown["json"]["amount_due_cents"])
        self.assertFalse(unknown["json"]["checkout_execution_enabled"])

        payload={
            "property_ref":self.id,"unit_ref":self.u,"category":"plumbing",
            "description":"Synthetic WSGI revocation test","emergency_flag":False,
            "entry_permission":"contact_first",
        }
        csrf=private_app.csrf.token(self.resident)
        key=str(uuid4())
        authority.admitted=False
        denied=call("/grounds/api/work",self.resident,method="POST",
                    payload=payload,csrf=csrf,key=key)
        self.assertEqual(denied["status"],"503 Service Unavailable")
        with self.store.transaction() as db:
            self.assertEqual(db.execute(
                "SELECT COUNT(*) FROM work_orders WHERE property_ref=?",
                (self.id,),
            ).fetchone()[0],0)

        authority.admitted=True
        receiver.enabled=False
        self.assertEqual(call(workspace,self.resident)["status"],"401 Unauthorized")
        self.assertEqual(call("/grounds/health/ready")["json"],{"ready":False})
        receiver.enabled=True
        saved=call("/grounds/api/work",self.resident,method="POST",
                   payload=payload,csrf=csrf,key=key)
        self.assertEqual(saved["status"],"201 Created")
        self.assertEqual(saved["json"]["state"],"submitted")
        self.assertFalse(saved["json"]["emergency_dispatch_confirmed"])
        with self.store.transaction() as db:
            self.assertEqual(db.execute(
                "SELECT COUNT(*) FROM work_orders WHERE property_ref=?",
                (self.id,),
            ).fetchone()[0],1)
        authority.healthy=False  # revoked overall current operating acceptance
        self.assertEqual(call(workspace,self.resident)["status"],"503 Service Unavailable")
        self.assertEqual(call("/grounds/health/ready")["json"],{"ready":False})



    def test_real_postgres_my_home_daily_and_property_health_wsgi(self):
        app=GroundsWebApp(
            self.store,tower_receiver=lambda environ:environ["test.fixture.actor"],
            csrf_secret=bytes(range(32)),local_fixture_only=False,
        )
        def get(path,actor):
            route,_,query=path.partition("?")
            out={}
            def start(status,headers):
                out["status"]=status
                out["headers"]=dict(headers)
            raw=b"".join(app({
                "REQUEST_METHOD":"GET","PATH_INFO":route,"QUERY_STRING":query,
                "wsgi.input":io.BytesIO(b""),"test.fixture.actor":actor,
            },start))
            out["json"]=json.loads(raw)
            return out
        home=get("/grounds/api/my-home?property_ref="+self.id+
                 "&unit_ref="+self.u,self.resident)
        self.assertEqual(home["status"],"200 OK")
        self.assertEqual(home["json"]["lease"]["lease_ref"],self.l)
        self.assertIsNone(home["json"]["rent"]["amount_due_cents"])
        daily=get("/grounds/api/daily?property_ref="+self.id,self.manager)
        self.assertEqual(daily["status"],"200 OK")
        self.assertEqual(daily["json"]["counts"]["unreviewed_urgent"],0)
        self.assertEqual(get("/grounds/api/daily?property_ref="+self.id,
                             self.resident)["status"],"404 Not Found")
        health=get("/grounds/api/property-health?property_ref="+self.id,self.owner)
        self.assertEqual(health["status"],"200 OK")
        self.assertIsNone(health["json"]["available_capital"])
        portfolio=get("/grounds/api/owner-portfolio",self.owner)
        self.assertEqual(portfolio["status"],"200 OK")
        self.assertEqual(portfolio["json"]["total_scope_count"],1)
        self.assertFalse(portfolio["json"]["money_fields_included"])


    def test_real_postgres_private_work_thread_and_revoked_lease(self):
        work="thread-"+uuid4().hex
        self.ops.submit_maintenance(
            self.resident,work_ref=work,
            intake=MaintenanceIntake(
                self.id,self.u,"plumbing","Synthetic thread original",
                False,"contact_first",
            ),
        )
        thread=GroundsWorkThread(self.store)
        key="m-"+uuid4().hex
        first=thread.post(self.resident,work_ref=work,message_ref=key,
                          body="Please share an update")
        self.assertFalse(first["external_notification_delivered"])
        self.assertTrue(thread.post(
            self.resident,work_ref=work,message_ref=key,
            body="Please share an update",
        )["replayed"])
        thread.post(self.manager,work_ref=work,
                    message_ref="staff-"+uuid4().hex,
                    body="Private operational note",audience="staff_internal")
        reader=thread.thread(self.resident,work_ref=work)
        self.assertEqual(reader["visible_message_count"],1)
        self.assertNotIn("Private operational note",str(reader))
        self.assertEqual(thread.thread(self.manager,work_ref=work)["visible_message_count"],2)
        self.assertFalse(reader["provider_currently_connected"])
        app=GroundsWebApp(
            self.store,tower_receiver=lambda env:env["test.fixture.actor"],
            csrf_secret=bytes(range(32)),local_fixture_only=False,
        )
        status={}
        def start(value,headers):
            status["value"]=value
        body=b"".join(app({
            "REQUEST_METHOD":"GET","PATH_INFO":"/grounds/api/work-thread",
            "QUERY_STRING":"work_ref="+work,"wsgi.input":io.BytesIO(b""),
            "test.fixture.actor":self.resident,
        },start))
        self.assertEqual(status["value"],"200 OK")
        self.assertEqual(json.loads(body)["visible_message_count"],1)
        self.ops.end_lease(
            self.manager,property_ref=self.id,lease_ref=self.l,
            expected_revision=1,
        )
        with self.assertRaises(AccessDenied):
            thread.thread(self.resident,work_ref=work)


    def test_real_postgres_current_lease_move_concierge_and_self_report(self):
        concierge=GroundsMoveConcierge(self.store)
        view=concierge.resident_checklist(
            self.resident,property_ref=self.id,unit_ref=self.u,
        )
        self.assertEqual(view["lease_ref"],self.l)
        event="move-"+uuid4().hex
        kwargs=dict(property_ref=self.id,unit_ref=self.u,
                    phase="move_in",task_ref="welcome_reviewed",
                    status="planned",expected_revision=0,event_ref=event)
        saved=concierge.mark_task(self.resident,**kwargs)
        self.assertEqual(saved["revision"],1)
        self.assertTrue(concierge.mark_task(self.resident,**kwargs)["replayed"])
        self.assertFalse(saved["staff_or_legal_verification"])
        view=concierge.resident_checklist(
            self.resident,property_ref=self.id,unit_ref=self.u,
        )
        self.assertEqual(view["phases"][0]["tasks"][0]["status"],"planned")
        self.assertFalse(view["keys_received_confirmed"])
        desk=concierge.staff_move_desk(self.manager,property_ref=self.id)
        self.assertFalse(desk["deposit_decision_authorized"])
        app=GroundsWebApp(
            self.store,tower_receiver=lambda env:env["test.fixture.actor"],
            csrf_secret=bytes(range(32)),local_fixture_only=False,
        )
        result={}
        def start(status,headers):
            result["status"]=status
        raw=b"".join(app({
            "REQUEST_METHOD":"GET","PATH_INFO":"/grounds/api/move-concierge",
            "QUERY_STRING":"property_ref="+self.id+"&unit_ref="+self.u,
            "wsgi.input":io.BytesIO(b""),"test.fixture.actor":self.resident,
        },start))
        self.assertEqual(result["status"],"200 OK")
        self.assertEqual(json.loads(raw)["lease_ref"],self.l)
        self.ops.end_lease(
            self.manager,property_ref=self.id,lease_ref=self.l,expected_revision=1,
        )
        with self.assertRaises(AccessDenied):
            concierge.resident_checklist(
                self.resident,property_ref=self.id,unit_ref=self.u,
            )


    def test_real_postgres_staff_delivery_desk_requires_exact_grant(self):
        desk=GroundsDeliveryDesk(self.store)
        item=desk.staff_status(self.manager,property_ref=self.id)
        self.assertEqual(item["total_local_intents"],0)
        self.assertFalse(item["provider_currently_connected"])
        self.assertFalse(item["retry_dispatch_connected"])
        self.assertFalse(item["emergency_dispatch_confirmed"])
        self.assertEqual(item["visible_items"],[])
        with self.assertRaises(AccessDenied):
            desk.staff_status(self.resident,property_ref=self.id)
        app=GroundsWebApp(
            self.store,tower_receiver=lambda env:env["test.fixture.actor"],
            csrf_secret=bytes(range(32)),local_fixture_only=False,
        )
        result={}
        def start(status,headers):
            result["status"]=status
        raw=b"".join(app({
            "REQUEST_METHOD":"GET","PATH_INFO":"/grounds/api/delivery-desk",
            "QUERY_STRING":"property_ref="+self.id,
            "wsgi.input":io.BytesIO(b""),"test.fixture.actor":self.manager,
        },start))
        self.assertEqual(result["status"],"200 OK")
        self.assertFalse(json.loads(raw)["provider_currently_connected"])


    def test_real_postgres_resident_personal_access_history_after_wsgi_read(self):
        app=GroundsWebApp(
            self.store,tower_receiver=lambda env:env["test.fixture.actor"],
            csrf_secret=bytes(range(32)),local_fixture_only=False,
        )
        def get(path,actor):
            route,_,query=path.partition("?")
            res={}
            def start(status,headers):
                res["status"]=status
            raw=b"".join(app({
                "REQUEST_METHOD":"GET","PATH_INFO":route,"QUERY_STRING":query,
                "wsgi.input":io.BytesIO(b""),"test.fixture.actor":actor,
            },start))
            res["json"]=json.loads(raw)
            return res
        self.assertEqual(get(
            "/grounds/api/my-home?property_ref="+self.id+"&unit_ref="+self.u,
            self.resident,
        )["status"],"200 OK")
        path="/grounds/api/privacy-history?property_ref="+self.id+"&unit_ref="+self.u
        result=get(path,self.resident)
        self.assertEqual(result["status"],"200 OK")
        self.assertEqual(result["json"]["total_events_before_current_response"],1)
        self.assertEqual(result["json"]["events"][0]["resource_kind"],"my_home")
        self.assertFalse(result["json"]["session_tokens_included"])
        self.assertEqual(get(path,self.manager)["status"],"404 Not Found")
        audit=GroundsResidentPrivacyLog(self.store)
        self.assertEqual(audit.my_history(
            self.resident,property_ref=self.id,unit_ref=self.u,
        )["total_events_before_current_response"],2)
        with self.store.transaction() as db:
            row=db.execute(
                "SELECT COUNT(*) FROM resident_access_events WHERE lease_ref=? AND actor_ref=?",
                (self.l,"resident"),
            ).fetchone()
            self.assertEqual(row[0],2)


    def test_resident_completion_ledger_executes_on_real_postgres(self):
        work="confirm-"+uuid4().hex
        tech=fixture_scope(
            "confirm-tech","maintenance_technician",(self.id,),(),(work,),
        )
        created=self.ops.submit_maintenance(
            self.resident,work_ref=work,
            intake=MaintenanceIntake(
                self.id,self.u,"plumbing","PG resident completion check",
                False,"contact_first",
            ),
        )
        revision=created["revision"]
        for state in ("received","under_review","scheduled"):
            revision=self.ops.advance_work_order(
                self.manager,work_ref=work,next_state=state,
                expected_revision=revision,
            )["revision"]
        revision=self.ops.assign_work_order(
            self.manager,work_ref=work,technician=tech,
            expected_revision=revision,
        )["revision"]
        revision=self.ops.advance_work_order(
            tech,work_ref=work,next_state="in_progress",
            expected_revision=revision,
        )["revision"]
        revision=self.ops.advance_work_order(
            tech,work_ref=work,next_state="completed",
            expected_revision=revision,
        )["revision"]
        revision=self.ops.advance_work_order(
            self.manager,work_ref=work,next_state="confirmation",
            expected_revision=revision,
        )["revision"]
        completion=GroundsWorkCompletion(self.store)
        result=completion.respond(
            self.resident,work_ref=work,outcome="still_needs_attention",
            expected_revision=revision,event_ref="completion-"+uuid4().hex,
            note="Synthetic PostgreSQL reopen",
        )
        self.assertEqual(result["state"],"reopened")
        status=completion.status(self.resident,work_ref=work)
        self.assertEqual(
            status["latest_resident_response"]["outcome"],
            "still_needs_attention",
        )
        with self.store.transaction() as db:
            self.assertEqual(db.execute(
                "SELECT COUNT(*) FROM work_completion_events WHERE work_ref=?",
                (work,),
            ).fetchone()[0],1)



if __name__=="__main__":
    unittest.main()
