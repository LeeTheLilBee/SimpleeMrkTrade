"""GRD094 — HTTP boundary regression tests (all actors/properties fictional).

The WSGI receiver in these tests is an IN-PROCESS fixture-only injection.
There is NO credential/identity verification, public server, tenant storage
or suggestion that this stub is a Tower production implementation.
"""
from __future__ import annotations

import io
import json
import shutil
import subprocess
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import patch
from urllib.parse import urlsplit
from uuid import uuid4

from grounds.access import AccessDenied
from grounds.maintenance import MaintenanceIntake
from grounds.operations import GroundsOperations
from grounds.postgres import PostgresGroundsStore
from grounds.storage import GroundsStore
from grounds.test_grounds_operations import fixture_scope
from grounds.web import GroundsWebApp, GroundsWebConfigurationError, SessionCSRF


class GroundsWebTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.store=GroundsStore(Path(self.tmp.name)/"synthetic.sqlite3")
        self.store.initialize()
        self.ops=GroundsOperations(self.store)
        self.owner=fixture_scope("owner","owner",("p1","p2"))
        self.manager=fixture_scope("manager","property_manager",("p1",))
        self.resident=fixture_scope("resident","resident",("p1",),("u1",))
        self.other=fixture_scope("unlisted","resident",("p1",),("u1",))
        self.outsider=fixture_scope("outsider","property_manager",("p2",))
        for ref in ("p1","p2"):
            self.ops.record_closed_property(
                self.owner,property_ref=ref,name="Fictional "+ref,
                close_evidence={"status":"verified_closed","property_ref":ref,
                    "proof_ref":"fictional-close-"+ref,"owned_on":"2026-09-26"},
                close_verifier=lambda doc:doc, # TEST FIXTURE ONLY
            )
        self.ops.add_building(self.manager,property_ref="p1",building_ref="b1",label="A")
        self.ops.add_unit(self.manager,property_ref="p1",building_ref="b1",unit_ref="u1",label="101")
        self.ops.activate_lease(
            self.manager,property_ref="p1",unit_ref="u1",lease_ref="l1",
            resident_ref="resident",start_on="2026-09-26",end_on="2027-09-25",
        )
        self.ops.publish_notice(self.manager,property_ref="p1",notice_ref="n1",
                                headline="Fictional public notice",body="Public example")
        self.secret=bytes(range(32))
        self.app=GroundsWebApp(
            self.store,tower_receiver=lambda environ:environ["test.fixture.actor"],
            csrf_secret=self.secret,local_fixture_only=True,
        )

    def tearDown(self):
        self.tmp.cleanup()

    def invoke(self,path="/grounds",*,actor=None,method="GET",data=None,
               json_raw=None,csrf=None,content_type="application/json",idempotency="auto"):
        url=urlsplit(path)
        if json_raw is not None:
            raw=json_raw
        elif data is None:
            raw=b""
        else:
            raw=json.dumps(data).encode("utf-8")
        environ={
            "REQUEST_METHOD":method,"PATH_INFO":url.path,"QUERY_STRING":url.query,
            "CONTENT_LENGTH":str(len(raw)),"CONTENT_TYPE":content_type,
            "wsgi.input":io.BytesIO(raw),
        }
        if actor is not None:
            environ["test.fixture.actor"]=actor
        if csrf is not None:
            environ["HTTP_X_GROUNDS_CSRF"]=csrf
        if method=="POST" and url.path in (
            "/grounds/api/work","/grounds/api/appointment/request",
        ):
            key=str(uuid4()) if idempotency=="auto" else idempotency
            if key is not None:
                environ["HTTP_X_GROUNDS_IDEMPOTENCY_KEY"]=key
        result={}
        def start(status,headers):
            result["status"]=status
            result["headers"]=dict(headers)
        response=b"".join(self.app(environ,start))
        result["body"]=response
        if result["headers"]["Content-Type"].startswith("application/json"):
            result["json"]=json.loads(response)
        return result

    def post(self,path,actor,data,*,csrf=None,idempotency="auto"):
        return self.invoke(path,actor=actor,method="POST",data=data,
                           csrf=csrf if csrf is not None else self.app.csrf.token(actor),
                           idempotency=idempotency)

    def test_cannot_configure_public_app_or_weak_csrf(self):
        with self.assertRaises(GroundsWebConfigurationError):
            GroundsWebApp(self.store,tower_receiver=lambda e:self.resident,
                          csrf_secret=self.secret)
        with self.assertRaises(GroundsWebConfigurationError):
            GroundsWebApp(self.store,tower_receiver=lambda e:self.resident,
                          csrf_secret=b"changeme",local_fixture_only=True)
        with self.assertRaises(GroundsWebConfigurationError):
            SessionCSRF(b"x"*32)
        with self.assertRaises(GroundsWebConfigurationError):
            GroundsWebApp(
                self.store,tower_receiver=lambda e:self.resident,
                csrf_secret=self.secret,local_fixture_only=True,
                teller_rent_source=lambda actor,home:{},
            )

    def test_postgres_web_composition_demands_actual_schema_preflight(self):
        pg=PostgresGroundsStore("postgresql://not-an-actual-db.example/grounds")
        with patch.object(pg,"assert_schema_ready",return_value={
            "backend":"postgresql","schema_compatible":True,
        }) as ready:
            app=GroundsWebApp(
                pg,tower_receiver=lambda env:env["test.fixture.actor"],
                csrf_secret=self.secret,local_fixture_only=False,
            )
            self.assertIs(app.store,pg)
            ready.assert_called_once_with()
        with self.assertRaises(GroundsWebConfigurationError):
            GroundsWebApp(
                pg,tower_receiver=lambda env:self.resident,
                csrf_secret=self.secret,local_fixture_only=True,
            )
        with patch.object(pg,"assert_schema_ready",
                          side_effect=ValueError("schema not ready")):
            with self.assertRaises(ValueError):
                GroundsWebApp(
                    pg,tower_receiver=lambda env:self.resident,
                    csrf_secret=self.secret,local_fixture_only=False,
                )

    def test_health_liveness_is_nonprivate_and_readiness_stays_closed_for_fixtures(self):
        live=self.invoke("/grounds/health/live")
        self.assertEqual(live["status"],"200 OK")
        self.assertEqual(live["json"],{"service":"grounds","live":True})
        self.assertNotIn("resident",str(live["json"]))
        self.assertEqual(live["headers"]["Cache-Control"],"no-store, private, max-age=0")
        ready=self.invoke("/grounds/health/ready")
        self.assertEqual(ready["status"],"503 Service Unavailable")
        self.assertEqual(ready["json"],{"ready":False})
        for path in ("/grounds","/grounds/app.js","/grounds/api/me"):
            self.assertEqual(self.invoke(path)["status"],"401 Unauthorized")

    def test_every_get_and_static_page_requires_server_owned_scope(self):
        for url in ("/grounds","/grounds/app.js","/grounds/app.css",
                    "/grounds/api/me","/grounds/api/workspace?property_ref=p1&unit_ref=u1"):
            self.assertTrue(self.invoke(url)["status"].startswith("401"),url)
        html=self.invoke("/grounds",actor=self.resident)
        self.assertEqual(html["status"],"200 OK")
        self.assertIn("text/html",html["headers"]["Content-Type"])
        self.assertIn("Content-Security-Policy",html["headers"])
        self.assertEqual(html["headers"]["Cache-Control"],"no-store, private, max-age=0")
        self.assertIn(self.app.csrf.token(self.resident).encode(),html["body"])
        self.assertNotIn(b"__GROUNDS_CSRF__",html["body"])
        self.assertNotIn(b"Fictional resident",html["body"])
        self.assertNotIn(b"Local demo mode",html["body"])
        me=self.invoke("/grounds/api/me",actor=self.resident)["json"]
        self.assertEqual(me["role"],"resident")
        self.assertEqual(me["unit_refs"],["u1"])
        self.assertNotIn("session_ref",me)

    def test_browser_assets_are_real_and_js_syntax_valid(self):
        js=self.invoke("/grounds/app.js",actor=self.resident)
        css=self.invoke("/grounds/app.css",actor=self.resident)
        self.assertEqual(js["status"],"200 OK")
        self.assertIn(b"fetch(",js["body"])
        self.assertIn(b"prefers-reduced-motion",css["body"])
        self.assertNotIn(b"FICTITIOUS_RESIDENT",js["body"])
        node=shutil.which("node")
        if node:
            result=subprocess.run([node,"--check",str(Path(__file__).parent/"ui"/"app.js")],
                                  check=False,capture_output=True,text=True,timeout=8)
            self.assertEqual(result.returncode,0,result.stderr)

    def test_csrf_is_session_bound_and_unknown_body_fields_fail_closed(self):
        payload={"property_ref":"p1","unit_ref":"u1","category":"plumbing",
                 "description":"Fixture leak","emergency_flag":False,"entry_permission":"contact_first"}
        self.assertEqual(self.invoke(
            "/grounds/api/work",actor=self.resident,method="POST",
            data=payload,
        )["status"],"403 Forbidden")
        self.assertEqual(self.invoke(
            "/grounds/api/work",actor=self.resident,method="POST",
            data=payload,csrf=self.app.csrf.token(self.manager),
        )["status"],"403 Forbidden")
        self.assertFalse(self.app.csrf.verify(self.resident,"000"))
        poisoned={**payload,"role":"owner"}
        self.assertEqual(self.post("/grounds/api/work",self.resident,poisoned)["status"],"400 Bad Request")
        duplicated=b'{"property_ref":"p1","property_ref":"p2"}'
        duplicate=self.invoke("/grounds/api/work",actor=self.resident,method="POST",
                              json_raw=duplicated,csrf=self.app.csrf.token(self.resident))
        self.assertEqual(duplicate["status"],"400 Bad Request")
        too_large=self.invoke("/grounds/api/work",actor=self.resident,method="POST",
                              json_raw=b"x"*8193,csrf=self.app.csrf.token(self.resident))
        self.assertEqual(too_large["status"],"400 Bad Request")

    def test_create_commands_require_valid_idempotency_key_and_retry_exactly_once(self):
        payload={"property_ref":"p1","unit_ref":"u1","category":"plumbing",
                 "description":"Same network request","emergency_flag":False,
                 "entry_permission":"contact_first"}
        for bad in ("",None,"not-a-uuid","00000000-0000-0000-0000-000000000000"):
            with self.subTest(key=bad):
                denied=self.post("/grounds/api/work",self.resident,payload,idempotency=bad)
                self.assertEqual(denied["status"],"400 Bad Request")
        key=str(uuid4())
        first=self.post("/grounds/api/work",self.resident,payload,idempotency=key)
        self.assertEqual(first["status"],"201 Created")
        retry=self.post("/grounds/api/work",self.resident,payload,idempotency=key)
        self.assertEqual(retry["status"],"201 Created")
        self.assertTrue(retry["json"]["replayed"])
        self.assertEqual(first["json"]["work_ref"],retry["json"]["work_ref"])
        with self.store.transaction() as db:
            self.assertEqual(db.execute("SELECT COUNT(*) FROM work_orders").fetchone()[0],1)
            self.assertEqual(db.execute("SELECT COUNT(*) FROM work_events").fetchone()[0],1)
        altered=self.post("/grounds/api/work",self.resident,
                          {**payload,"description":"different issue"},idempotency=key)
        self.assertEqual(altered["status"],"409 Conflict")
        other=self.post("/grounds/api/work",self.other,payload,idempotency=key)
        self.assertEqual(other["status"],"404 Not Found")
        new_key=self.post("/grounds/api/work",self.resident,payload,idempotency=str(uuid4()))
        self.assertNotEqual(new_key["json"]["work_ref"],first["json"]["work_ref"])

    def test_idempotent_appointment_retry_preserves_single_event(self):
        import datetime
        created=self.post("/grounds/api/work",self.resident,{
            "property_ref":"p1","unit_ref":"u1","category":"plumbing",
            "description":"Appointment retry job","emergency_flag":False,
            "entry_permission":"contact_first",
        })["json"]
        now=datetime.datetime.now(datetime.timezone.utc)
        start=(now+datetime.timedelta(days=2)).isoformat()
        end=(now+datetime.timedelta(days=2,hours=1)).isoformat()
        body={"work_ref":created["work_ref"],"start_at":start,"end_at":end}
        key=str(uuid4())
        first=self.post("/grounds/api/appointment/request",self.resident,
                        body,idempotency=key)
        second=self.post("/grounds/api/appointment/request",self.resident,
                         body,idempotency=key)
        self.assertEqual(first["json"]["appointment_ref"],second["json"]["appointment_ref"])
        self.assertTrue(second["json"]["replayed"])
        with self.store.transaction() as db:
            self.assertEqual(db.execute("SELECT COUNT(*) FROM work_appointments").fetchone()[0],1)
            self.assertEqual(db.execute("SELECT COUNT(*) FROM appointment_events").fetchone()[0],1)
        different=self.post("/grounds/api/appointment/request",self.resident,
                            {**body,"end_at":(now+datetime.timedelta(days=2,hours=2)).isoformat()},
                            idempotency=key)
        self.assertEqual(different["status"],"409 Conflict")

    def test_csrf_survives_short_ticket_refresh_for_same_tower_session(self):
        from time import time
        first=fixture_scope("resident","resident",("p1",),("u1",),expires=int(time())+180)
        second=fixture_scope("resident","resident",("p1",),("u1",),expires=int(time())+240)
        self.assertEqual(first.session_ref,second.session_ref)
        token=self.app.csrf.token(first)
        self.assertTrue(self.app.csrf.verify(second,token))
        other=fixture_scope("someone_else","resident",("p1",),("u1",))
        self.assertFalse(self.app.csrf.verify(other,token))

    def test_staff_assignment_requires_server_owned_current_roster_and_exact_technician(self):
        created=self.post("/grounds/api/work",self.resident,{
            "property_ref":"p1","unit_ref":"u1","category":"plumbing",
            "description":"Staff assignment test","emergency_flag":False,
            "entry_permission":"contact_first",
        })["json"]
        work=created["work_ref"]
        revision=1
        for state in ("received","under_review","scheduled"):
            moved=self.post("/grounds/api/work/transition",self.manager,{
                "work_ref":work,"next_state":state,"expected_revision":revision,
            })
            self.assertEqual(moved["status"],"201 Created")
            revision=moved["json"]["revision"]
        empty=self.invoke("/grounds/api/technicians?property_ref=p1",actor=self.manager)
        self.assertEqual(empty["json"],{"connected":False,"technicians":[]})
        self.assertEqual(self.invoke(
            "/grounds/api/technicians?property_ref=p1",actor=self.resident,
        )["status"],"404 Not Found")
        unconnected=self.post("/grounds/api/work/assign",self.manager,{
            "work_ref":work,"technician_ref":"tech","expected_revision":revision,
        })
        self.assertEqual(unconnected["status"],"409 Conflict")
        tech=fixture_scope("tech","maintenance_technician",("p1",),assignments=(work,))
        roster=lambda actor,property_ref:(
            [{"staff_ref":"tech","label":"Available maintenance technician"}]
            if actor.role=="property_manager" and property_ref=="p1" else []
        )
        correct_resolver=lambda actor,property_ref,work_ref,technician_ref:(
            tech if (actor.role=="property_manager" and property_ref=="p1"
                     and work_ref==work and technician_ref=="tech") else None
        )
        app=GroundsWebApp(
            self.store,tower_receiver=self.app.receiver,csrf_secret=self.secret,
            local_fixture_only=True,staff_directory=roster,staff_resolver=correct_resolver,
        )
        self.app=app
        directory=self.invoke("/grounds/api/technicians?property_ref=p1",actor=self.manager)
        self.assertEqual(directory["status"],"200 OK")
        self.assertEqual(directory["json"]["technicians"][0]["staff_ref"],"tech")
        self.assertEqual(self.post("/grounds/api/work/assign",self.manager,{
            "work_ref":work,"technician_ref":"unknown","expected_revision":revision,
        })["status"],"404 Not Found")
        assignment=self.post("/grounds/api/work/assign",self.manager,{
            "work_ref":work,"technician_ref":"tech","expected_revision":revision,
        })
        self.assertEqual(assignment["status"],"201 Created")
        self.assertEqual(assignment["json"]["assigned_to"],"tech")
        self.assertEqual(self.invoke(
            "/grounds/api/work?work_ref="+work,actor=tech,
        )["status"],"200 OK")
        self.assertEqual(self.post("/grounds/api/work/assign",self.resident,{
            "work_ref":work,"technician_ref":"tech","expected_revision":revision+1,
        })["status"],"404 Not Found")
        with self.assertRaises(GroundsWebConfigurationError):
            GroundsWebApp(
                self.store,tower_receiver=self.app.receiver,csrf_secret=self.secret,
                local_fixture_only=True,staff_directory=roster,
            )

    def test_real_domain_resident_submission_notice_and_staff_triage(self):
        payload={"property_ref":"p1","unit_ref":"u1","category":"plumbing",
                 "description":"Fixture leak reported by real-data API test",
                 "emergency_flag":True,"entry_permission":"contact_first"}
        denied=self.post("/grounds/api/work",self.other,payload)
        self.assertEqual(denied["status"],"404 Not Found")
        created=self.post("/grounds/api/work",self.resident,payload)
        self.assertEqual(created["status"],"201 Created")
        work=created["json"]["work_ref"]
        self.assertEqual(created["json"]["state"],"submitted")
        self.assertFalse(created["json"]["emergency_dispatch_confirmed"])
        staff=self.invoke("/grounds/api/workspace?property_ref=p1",actor=self.manager)
        self.assertEqual(staff["json"]["work_orders"][0]["work_ref"],work)
        self.assertEqual(self.post(
            "/grounds/api/work/transition",self.manager,
            {"work_ref":work,"next_state":"received","expected_revision":1},
        )["status"],"409 Conflict")
        accepted=self.post("/grounds/api/urgency/review",self.manager,
                           {"work_ref":work,"assessed_urgency":"priority"})
        self.assertTrue(accepted["json"]["human_review_recorded"])
        self.assertFalse(accepted["json"]["emergency_services_contacted"])
        moved=self.post(
            "/grounds/api/work/transition",self.manager,
            {"work_ref":work,"next_state":"received","expected_revision":1},
        )
        self.assertEqual(moved["json"]["state"],"received")
        self.assertEqual(self.invoke("/grounds/api/work?work_ref="+work,
                                     actor=self.other)["status"],"404 Not Found")
        self.assertEqual(self.invoke("/grounds/api/work?work_ref="+work,
                                     actor=self.resident)["json"]["description"],payload["description"])
        self.assertEqual(self.invoke("/grounds/api/workspace?property_ref=p2&unit_ref=u1",
                                     actor=self.resident)["status"],"404 Not Found")
        notice=self.post("/grounds/api/notice-read",self.resident,
                         {"property_ref":"p1","unit_ref":"u1","notice_ref":"n1"})
        self.assertTrue(notice["json"]["read_in_app"])
        self.assertFalse(notice["json"]["legal_service_proven"])
        home=self.invoke("/grounds/api/workspace?property_ref=p1&unit_ref=u1",
                         actor=self.resident)["json"]
        self.assertEqual(home["notices"][0]["read_in_app"],1)
        self.assertEqual(home["work_orders"][0]["work_ref"],work)
        self.assertIsNone(home["rent"]["amount_due_cents"])

    def test_verified_teller_rent_projection_is_exact_lease_bound_and_optional(self):
        disconnected=self.invoke(
            "/grounds/api/rent?property_ref=p1&unit_ref=u1",actor=self.resident,
        )
        self.assertEqual(disconnected["status"],"200 OK")
        self.assertFalse(disconnected["json"]["connected"])
        self.assertIsNone(disconnected["json"]["amount_due_cents"])

        now=int(time.time())
        signed={
            "source":"teller","audience":"grounds","resident_ref":"resident",
            "property_ref":"p1","unit_ref":"u1","lease_ref":"l1",
            "observed_at":now,"expires_at":now+120,
            "amount_due_cents":125050,"currency":"USD","invoice_status":"partial",
            "due_on":"2026-10-01","teller_handoff_ref":"rent-handoff-1",
        }
        app=GroundsWebApp(
            self.store,tower_receiver=lambda env:env["test.fixture.actor"],
            csrf_secret=self.secret,local_fixture_only=True,
            teller_rent_source=lambda actor,home:signed,
            teller_verifier=lambda message:message, # TEST FIXTURE ONLY
        )
        self.app=app
        verified=self.invoke(
            "/grounds/api/rent?property_ref=p1&unit_ref=u1",actor=self.resident,
        )
        self.assertEqual(verified["status"],"200 OK")
        self.assertTrue(verified["json"]["connected"])
        self.assertEqual(verified["json"]["amount_due_cents"],125050)
        self.assertEqual(verified["json"]["invoice_status"],"partial")
        self.assertEqual(verified["json"]["teller_handoff_ref"],"rent-handoff-1")
        self.assertFalse(verified["json"]["checkout_execution_enabled"])
        self.assertEqual(self.invoke(
            "/grounds/api/rent?property_ref=p1&unit_ref=u1",actor=self.other,
        )["status"],"404 Not Found")

        stale=dict(signed);stale["observed_at"]=now-500;stale["expires_at"]=now-200
        self.app=GroundsWebApp(
            self.store,tower_receiver=lambda env:env["test.fixture.actor"],
            csrf_secret=self.secret,local_fixture_only=True,
            teller_rent_source=lambda actor,home:stale,
            teller_verifier=lambda message:message, # TEST FIXTURE ONLY
        )
        self.assertEqual(self.invoke(
            "/grounds/api/rent?property_ref=p1&unit_ref=u1",actor=self.resident,
        )["status"],"503 Service Unavailable")

    def test_appointment_access_current_lease_and_entry_preference(self):
        import datetime
        created=self.post("/grounds/api/work",self.resident,
            {"property_ref":"p1","unit_ref":"u1","category":"plumbing",
             "description":"Work needing appointment","emergency_flag":False,
             "entry_permission":"contact_first"})["json"]
        work=created["work_ref"]
        start=datetime.datetime.now(datetime.timezone.utc)+datetime.timedelta(days=3)
        end=start+datetime.timedelta(hours=2)
        requested=self.post("/grounds/api/appointment/request",self.resident,
                            {"work_ref":work,"start_at":start.isoformat(),
                             "end_at":end.isoformat()})["json"]
        appointment=requested["appointment_ref"]
        found=self.invoke("/grounds/api/appointments?work_ref="+work,
                          actor=self.resident)["json"]
        self.assertEqual(found["appointments"][0]["state"],"requested")
        self.assertFalse(found["entry_consent_granted"])
        self.assertEqual(self.invoke("/grounds/api/appointments?work_ref="+work,
                                     actor=self.other)["status"],"404 Not Found")
        proposal=self.post("/grounds/api/appointment/propose",self.manager,
                           {"appointment_ref":appointment,"start_at":start.isoformat(),
                            "end_at":end.isoformat(),"expected_revision":1})
        self.assertEqual(proposal["json"]["state"],"proposed")
        accepted=self.post("/grounds/api/appointment/accept",self.resident,
                           {"appointment_ref":appointment,"expected_revision":2})
        self.assertFalse(accepted["json"]["entry_consent_granted"])
        pref=self.invoke("/grounds/api/entry-preference?work_ref="+work,
                         actor=self.resident)["json"]
        self.assertEqual(pref["revision"],0)
        changed=self.post("/grounds/api/work/entry-preference",self.resident,
                          {"work_ref":work,"preference":"no","expected_revision":0})
        self.assertEqual(changed["json"]["preference"],"no")
        self.assertFalse(changed["json"]["staff_entry_authorized"])
        self.ops.end_lease(self.manager,property_ref="p1",lease_ref="l1",
                           expected_revision=1)
        with self.store.transaction(write=True) as db:
            db.execute("UPDATE units SET lifecycle='ready' WHERE unit_ref='u1'")
        self.ops.activate_lease(self.manager,property_ref="p1",unit_ref="u1",
                                lease_ref="l2",resident_ref="resident",
                                start_on="2028-01-01",end_on="2028-12-31")
        self.assertEqual(self.invoke("/grounds/api/appointments?work_ref="+work,
                                     actor=self.resident)["status"],"404 Not Found")
        self.assertEqual(self.invoke("/grounds/api/appointment?appointment_ref="+appointment,
                                     actor=self.resident)["status"],"404 Not Found")

    def test_malformed_query_or_unknown_resource_never_leaks_path(self):
        for path in ("/grounds/api/work?work_ref=x&work_ref=y",
                     "/grounds/api/work?work_ref=private%00ref",
                     "/grounds/api/work?work_ref="):
            response=self.invoke(path,actor=self.resident)
            self.assertEqual(response["status"],"400 Bad Request")
            self.assertNotIn("sqlite",str(response))
        self.assertEqual(self.invoke("/grounds/api/unknown",actor=self.resident)["status"],"404 Not Found")


if __name__=="__main__":
    unittest.main()
