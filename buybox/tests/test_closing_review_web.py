"""BBX091 — authenticated owner Closing Review is historical source review only."""
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from cryptography.fernet import Fernet
from werkzeug.security import generate_password_hash

from buybox.app import create_app
from buybox.store import connect, load


class ClosingReviewWebTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.root=Path(self.temp.name)
        self.root.chmod(0o700)
        self.docs=self.root/"originals"
        self.docs.mkdir(mode=0o700)
        self.dbpath=str(self.root/"buybox.sqlite3")
        self.app=create_app({
            "TESTING":True,
            "SECRET_KEY":"closing-test-secret-not-production",
            "BUYBOX_AUTH_MODE":"local",
            "BUYBOX_PASSWORD_HASH":generate_password_hash("local-test-password"),
            "BUYBOX_DB_PATH":self.dbpath,
            "BUYBOX_DOCS_DIR":str(self.docs),
            "BUYBOX_DOCUMENT_KEY":Fernet.generate_key().decode(),
            "SESSION_COOKIE_SECURE":False,
        })
        self.client=self.app.test_client()
        with self.client.session_transaction() as sess:
            sess["csrf"]="initial-csrf"
        logged=self.client.post("/login",data={
            "csrf_token":"initial-csrf","password":"local-test-password"})
        self.assertEqual(logged.status_code,302)
        with self.client.session_transaction() as sess:self.csrf=sess["csrf"]
        created=self.post("/opportunities",{
            "vertical":"commercial","name":"Owner-recorded closing candidate",
            "asking_price":"275000","city":"","region":"","source_url":""})
        self.assertEqual(created.status_code,302)
        self.oid=created.location.rsplit("/",1)[-1]

    def tearDown(self):
        self.temp.cleanup()

    def post(self,path,data):
        return self.client.post(path,data={"csrf_token":self.csrf,**data})

    def current(self):
        with connect(self.dbpath) as conn:return load(conn,self.oid)

    def review(self,revision=None,**changes):
        op=self.current()
        data={
            "revision":str(op["version"] if revision is None else revision),
            "financing_option_id":"","insurance_record_id":"",
            "planned_closing_date":"2026-10-15",
            "rationale":"Reviewing current sources; protected closing authority is still outstanding.",
        }
        data.update(changes)
        return self.post("/opportunities/"+self.oid+"/closing-review",data)

    def test_empty_room_is_visibly_blocked_and_not_green(self):
        page=self.client.get("/opportunities/"+self.oid+"/closing-review")
        self.assertEqual(page.status_code,200)
        self.assertIn(b"Protected closing",page.data)
        self.assertIn(b"Blocked",page.data)
        self.assertIn(b"Tower Closing Authorization Absent",page.data)
        self.assertIn(b"Teller Money Readiness Unknown",page.data)
        self.assertIn(b"No Documented Financing Option",page.data)
        self.assertIn(b"No Documented Insurance Record",page.data)
        self.assertNotIn(b"Approved to close",page.data)
        self.assertFalse(self.current().get("closing_reviews"))

    def test_owner_freezes_review_without_stage_or_external_action(self):
        before=self.current()
        response=self.review()
        self.assertEqual(response.status_code,303)
        current=self.current()
        self.assertEqual(current["version"],before["version"]+1)
        self.assertEqual(current["lifecycle"],before["lifecycle"])
        self.assertEqual(len(current["closing_reviews"]),1)
        record=current["closing_reviews"][0]
        self.assertEqual(record["actor"],"local_owner")
        self.assertFalse(record["authorizes_closing"])
        self.assertFalse(record["authorizes_money"])
        self.assertFalse(record["transmitted_externally"])
        self.assertFalse(record["updates_lifecycle"])
        self.assertIsNone(record["tower_closing_authorization"])
        self.assertEqual(record["teller_money_ready"],"UNKNOWN")
        page=self.client.get("/opportunities/"+self.oid+"/closing-review")
        self.assertIn(b"Current Recorded Review",page.data)
        self.assertIn(record["local_snapshot_sha256"][:16].encode(),page.data)
        soulaana=self.client.get(
            "/opportunities/"+self.oid+"/soulaana?intent=closing")
        self.assertEqual(soulaana.status_code,200)
        self.assertIn(b"CLOSING AUTHORITY BLOCKED",soulaana.data)
        self.assertIn(b"OWNER LOCAL CLOSING REVIEW",soulaana.data)
        self.assertIn(record["id"].encode(),soulaana.data)
        self.assertIn(b"NOT AUTHORIZED TO CLOSE",soulaana.data)

    def test_stale_form_and_foreign_selected_ids_fail_closed(self):
        stale=self.current()["version"]
        self.assertEqual(self.review().status_code,303)
        again=self.review(revision=stale)
        self.assertEqual(again.status_code,409)
        current=self.current()
        self.assertEqual(len(current["closing_reviews"]),1)
        invalid=self.review(financing_option_id="foreign-option")
        self.assertEqual(invalid.status_code,409)
        self.assertEqual(len(self.current()["closing_reviews"]),1)

    def test_later_change_keeps_review_but_marks_it_historical(self):
        self.assertEqual(self.review().status_code,303)
        current=self.current()
        source_version=current["version"]
        changed=self.post("/opportunities/"+self.oid+"/source",{
            "revision":str(source_version),"url":"https://example.org/updated-source"})
        self.assertEqual(changed.status_code,302)
        page=self.client.get("/opportunities/"+self.oid+"/closing-review")
        self.assertIn(b"Historical Opportunity Version",page.data)
        self.assertEqual(len(self.current()["closing_reviews"]),1)

    def test_anonymous_and_bad_csrf_cannot_access_or_write(self):
        anonymous=self.app.test_client()
        self.assertEqual(
            anonymous.get("/opportunities/"+self.oid+"/closing-review").status_code,302)
        self.assertEqual(
            anonymous.post("/opportunities/"+self.oid+"/closing-review",
                           data={"csrf_token":"bad","rationale":"forged"}).status_code,400)
        self.assertFalse(self.current().get("closing_reviews"))


if __name__=="__main__":
    unittest.main()
