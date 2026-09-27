"""Authenticated owner Decision Desk: persisted real research only, never approval."""
import tempfile
import unittest
from pathlib import Path

from cryptography.fernet import Fernet
from werkzeug.security import generate_password_hash

from buybox.app import create_app
from buybox.store import connect, load


class OwnerDecisionWebTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.root=Path(self.temp.name)
        self.root.chmod(0o700)
        self.docs=self.root/"originals"
        self.docs.mkdir(mode=0o700)
        self.dbpath=str(self.root/"buybox.sqlite3")
        self.app=create_app({
            "TESTING":True,
            "SECRET_KEY":"unit-test-secret-not-production",
            "BUYBOX_AUTH_MODE":"local",
            "BUYBOX_PASSWORD_HASH":generate_password_hash("local-test-password"),
            "BUYBOX_DB_PATH":self.dbpath,
            "BUYBOX_DOCS_DIR":str(self.docs),
            "BUYBOX_DOCUMENT_KEY":Fernet.generate_key().decode(),
            "SESSION_COOKIE_SECURE":False,
        })
        self.client=self.app.test_client()
        with self.client.session_transaction() as sess:
            sess["csrf"]="unit-test-csrf"
        login=self.client.post("/login",data={
            "csrf_token":"unit-test-csrf",
            "password":"local-test-password",
        })
        self.assertEqual(login.status_code,302)
        with self.client.session_transaction() as sess:
            self.csrf=sess["csrf"]
        created=self.post("/opportunities",{
            "vertical":"multifamily",
            "name":"Owner-entered actual acquisition",
            "asking_price":"100000",
            "city":"","region":"","source_url":"",
        })
        self.assertEqual(created.status_code,302)
        self.oid=created.location.rsplit("/",1)[-1]

    def tearDown(self):
        self.temp.cleanup()

    def post(self,path,data):
        return self.client.post(path,data={"csrf_token":self.csrf,**data})

    def current(self):
        with connect(self.dbpath) as conn:
            return load(conn,self.oid)

    def note(self,choice="WATCH",revision=None,**changes):
        source=self.current()
        data={
            "revision":str(source["version"] if revision is None else revision),
            "choice":choice,
            "rationale":"Waiting for a documented rent roll and verified contracts",
        }
        data.update(changes)
        return self.post("/opportunities/"+self.oid+"/decision-desk/notes",data)

    def test_empty_room_does_not_create_fake_decision_or_authority(self):
        page=self.client.get("/opportunities/"+self.oid+"/decision-desk")
        self.assertEqual(page.status_code,200)
        self.assertIn(b"No source-bound research dispositions recorded yet",page.data)
        self.assertIn(b"Unknown / Unknown",page.data)
        self.assertNotIn(b'value="APPROVE_ACQUISITION"',page.data)
        self.assertFalse(self.current().get("research_decisions"))

    def test_owner_action_persists_with_exact_saved_source_and_soulaana(self):
        before=self.current()
        outcome=self.note(choice="REQUEST_EVIDENCE")
        self.assertEqual(outcome.status_code,303)
        source=self.current()
        self.assertEqual(source["version"],before["version"]+1)
        self.assertEqual(len(source["research_decisions"]),1)
        decision=source["research_decisions"][0]
        self.assertEqual(decision["choice"],"REQUEST_EVIDENCE")
        self.assertEqual(decision["source_opportunity_revision"],before["version"])
        self.assertEqual(decision["recorded_opportunity_revision"],source["version"])
        self.assertEqual(decision["actor"],"local_owner")
        self.assertEqual(len(decision["source_snapshot_digest"]),64)
        self.assertFalse(decision["authorizes_purchase"])
        self.assertFalse(decision["authorizes_offer_or_loi"])
        self.assertFalse(decision["transmitted_externally"])
        self.assertEqual(source["lifecycle"],before["lifecycle"])
        page=self.client.get("/opportunities/"+self.oid+"/decision-desk")
        self.assertEqual(page.status_code,200)
        self.assertIn(b"Waiting for a documented rent roll",page.data)
        soulaana=self.client.get("/opportunities/"+self.oid+"/soulaana?intent=decision")
        self.assertEqual(soulaana.status_code,200)
        self.assertIn(b"OWNER RESEARCH DISPOSITION",soulaana.data)
        self.assertIn(decision["id"].encode(),soulaana.data)
        self.assertIn(b"NOT A TRANSACTION AUTHORIZATION",soulaana.data)

    def test_reject_forged_purchase_choice_and_cross_opportunity_citations(self):
        self.assertEqual(self.note(choice="APPROVE_ACQUISITION").status_code,409)
        response=self.note(evidence_id=["not-the-opportunity-evidence"])
        self.assertEqual(response.status_code,409)
        self.assertFalse(self.current().get("research_decisions"))

    def test_stale_source_form_cannot_append_a_second_owner_note(self):
        old_version=self.current()["version"]
        self.assertEqual(self.note().status_code,303)
        self.assertEqual(self.note(choice="DEFER",revision=old_version).status_code,409)
        self.assertEqual(len(self.current()["research_decisions"]),1)

    def test_anonymous_user_cannot_view_or_submit_and_csrf_required(self):
        anonymous=self.app.test_client()
        self.assertEqual(anonymous.get("/opportunities/"+self.oid+"/decision-desk").status_code,302)
        self.assertEqual(anonymous.post("/opportunities/"+self.oid+"/decision-desk/notes",
            data={"choice":"WATCH","rationale":"Forged","csrf_token":"wrong"}).status_code,400)
        self.assertFalse(self.current().get("research_decisions"))


if __name__=="__main__":
    unittest.main()
