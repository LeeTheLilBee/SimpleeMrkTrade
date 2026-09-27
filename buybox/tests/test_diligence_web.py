"""Authenticated real owner checklist browser flow, isolated temp database only."""
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from cryptography.fernet import Fernet
from werkzeug.security import generate_password_hash

from buybox.app import create_app
from buybox.store import connect, load, activity


class DiligenceWebTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.root=Path(self.temp.name)
        self.root.chmod(0o700)
        self.docs=self.root/"docs"
        self.docs.mkdir(mode=0o700)
        self.db=str(self.root/"data.sqlite3")
        self.app=create_app({
            "TESTING":True,"SECRET_KEY":"local-test-only-secret",
            "BUYBOX_AUTH_MODE":"local",
            "BUYBOX_PASSWORD_HASH":generate_password_hash("test-only-owner-password"),
            "BUYBOX_DB_PATH":self.db,"BUYBOX_DOCS_DIR":str(self.docs),
            "BUYBOX_DOCUMENT_KEY":Fernet.generate_key().decode(),
            "SESSION_COOKIE_SECURE":False,
        })
        self.client=self.app.test_client()
        with self.client.session_transaction() as ses:
            ses["csrf"]="initial-csrf"
        result=self.client.post("/login",data={
            "csrf_token":"initial-csrf","password":"test-only-owner-password"})
        self.assertEqual(result.status_code,302)
        with self.client.session_transaction() as ses:
            self.csrf=ses["csrf"]
        response=self.post("/opportunities",{
            "vertical":"multifamily","name":"Owner entered building",
            "asking_price":"","city":"","region":"","source_url":""})
        self.assertEqual(response.status_code,302)
        self.oid=response.location.rsplit("/",1)[-1]

    def tearDown(self):
        self.temp.cleanup()

    def post(self,path,data):
        return self.client.post(path,data={**data,"csrf_token":self.csrf})

    def op(self):
        with connect(self.db) as conn:
            return load(conn,self.oid)

    def test_real_registry_checklist_and_persisted_owner_task(self):
        page=self.client.get("/opportunities/"+self.oid+"/diligence")
        self.assertEqual(page.status_code,200)
        self.assertIn(b"Rent Roll",page.data)
        self.assertIn(b"Condition Report",page.data)
        self.assertIn(b"Critical still outstanding",page.data)
        self.assertIn(b"No active evidence record",page.data)
        before=self.op()
        result=self.post("/opportunities/"+self.oid+"/diligence/tasks",{
            "revision":str(before["version"]),"evidence_kind":"rent_roll",
            "due_date":"2026-10-05","notes":"Request seller's current rent roll"})
        self.assertEqual(result.status_code,303)
        after=self.op()
        self.assertEqual(after["version"],before["version"]+1)
        self.assertEqual(len(after["tasks"]),1)
        task=after["tasks"][0]
        self.assertEqual(task["evidence_kind"],"rent_roll")
        self.assertEqual(task["owner"],"local_owner")
        self.assertEqual(task["status"],"OPEN")
        self.assertTrue(task["does_not_contact_seller"])
        self.assertNotIn("rent_roll",after.get("metrics",{}))
        self.assertIsNone(after["readiness"]["teller"])
        self.assertFalse(after["tower_authorizations"])
        with connect(self.db) as conn:
            self.assertTrue(any(x["event_type"]=="DiligenceEvidenceTaskCreated"
                                for x in activity(conn,self.oid)))
        reopened=self.client.get("/opportunities/"+self.oid+"/diligence")
        self.assertIn(b"2026-10-05",reopened.data)
        self.assertIn(b"Open Deal Integrity",reopened.data)
        self.assertIn(b"does not contact",reopened.data.lower())

    def test_duplicate_stale_unknown_and_invalid_deadline_fail_closed(self):
        before=self.op()
        route="/opportunities/"+self.oid+"/diligence/tasks"
        fields={"revision":str(before["version"]),"evidence_kind":"rent_roll",
                "due_date":"2026-10-05","notes":""}
        self.assertEqual(self.post(route,fields).status_code,303)
        self.assertEqual(self.post(route,fields).status_code,409)
        revised=self.op()
        self.assertEqual(self.post(route,{
            **fields,"revision":str(revised["version"])}).status_code,409)
        self.assertEqual(self.post(route,{
            **fields,"revision":str(revised["version"]),
            "evidence_kind":"made_up_document"}).status_code,409)
        self.assertEqual(self.post(route,{
            **fields,"revision":str(revised["version"]),
            "evidence_kind":"leases","due_date":"not-a-date"}).status_code,409)
        self.assertEqual(len(self.op()["tasks"]),1)

    def test_unauthenticated_and_csrf_fail_closed(self):
        anonymous=self.app.test_client()
        path="/opportunities/"+self.oid+"/diligence"
        self.assertEqual(anonymous.get(path).status_code,302)
        self.assertEqual(anonymous.post(path+"/tasks",data={
            "revision":str(self.op()["version"]),"evidence_kind":"rent_roll",
            "due_date":"2026-10-05","csrf_token":"forged",
        }).status_code,400)
        self.assertEqual(len(self.op().get("tasks",[])),0)

    def test_soulaana_diligence_displays_actual_source_and_task_not_approval(self):
        before=self.op()
        self.assertEqual(self.post("/opportunities/"+self.oid+"/diligence/tasks",{
            "revision":str(before["version"]),"evidence_kind":"rent_roll",
            "due_date":"2026-10-06","notes":""}).status_code,303)
        page=self.client.get("/opportunities/"+self.oid+"/soulaana?intent=diligence")
        self.assertEqual(page.status_code,200)
        self.assertIn(b"Rent Roll",page.data)
        self.assertIn(b"2026-10-06",page.data)
        self.assertIn(b"ACTUAL RECORDS NOT CERTIFICATION",page.data)
        self.assertIn(b"not connected yet",page.data)

if __name__=="__main__":
    unittest.main()
