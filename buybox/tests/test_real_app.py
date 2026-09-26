"""Real Flask endpoints; temporary file DB only, no fabricated product listings."""
import os
import tempfile
import unittest
from pathlib import Path
from werkzeug.security import generate_password_hash
from buybox.app import create_app
from buybox.store import connect, list_opportunities

class OwnerAppTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.db=str(Path(self.tmp.name)/"opportunities.sqlite3")
        self.app=create_app({
            "TESTING":True, "SECRET_KEY":"test-secret-not-for-production",
            "BUYBOX_PASSWORD_HASH":generate_password_hash("test-local-only-password"),
            "BUYBOX_DB_PATH":self.db,"SESSION_COOKIE_SECURE":False,
        })
        self.client=self.app.test_client()
        with self.client.session_transaction() as sess:
            sess["csrf"]="unit-csrf"
        self.csrf="unit-csrf"

    def tearDown(self):
        self.tmp.cleanup()

    def login(self):
        response=self.client.post("/login",data={"csrf_token":self.csrf,
              "password":"test-local-only-password"},follow_redirects=False)
        self.assertEqual(response.status_code,302)
        with self.client.session_transaction() as sess:
            self.csrf=sess["csrf"]

    def post(self,path,payload,follow_redirects=False):
        return self.client.post(path,data={**payload,"csrf_token":self.csrf},
                                follow_redirects=follow_redirects)

    def create(self):
        self.login()
        response=self.post("/opportunities",{
            "vertical":"atm","name":"Owner-entered route","asking_price":"95000.00",
            "city":"An actual entered city","region":"GA","source_url":"https://example.org/listing"})
        self.assertEqual(response.status_code,302)
        return response.location.rsplit("/",1)[-1]

    def test_requires_owner_login(self):
        self.assertEqual(self.client.get("/").status_code,302)
        self.assertEqual(self.client.get("/opportunities/unknown").status_code,302)

    def test_bad_csrf_is_rejected(self):
        self.assertEqual(self.client.post("/login",data={"password":"wrong"}).status_code,400)

    def test_intake_is_persisted_and_not_qualified(self):
        oid=self.create()
        with connect(self.db) as conn:
            op=list_opportunities(conn)[0]
        self.assertEqual(op["id"],oid)
        self.assertEqual(op["asking_price"],"95000.00")
        page=self.client.get("/opportunities/"+oid)
        self.assertEqual(page.status_code,200)
        self.assertIn(b"Owner-entered route",page.data)
        self.assertIn(b"UNKNOWN",page.data)

    def test_no_fake_homepage_opportunities(self):
        self.login()
        body=self.client.get("/").data
        self.assertIn(b"No opportunities found",body)
        self.assertNotIn(b"Southeast ATM Route",body)

    def test_receipt_does_not_auto_verify(self):
        oid=self.create()
        with connect(self.db) as conn: op=list_opportunities(conn)[0]
        result=self.post("/opportunities/"+oid+"/evidence",{
            "revision":str(op["version"]),"kind":"processor_statements",
            "reference":"private-reference-001","source_party":"Seller"})
        self.assertEqual(result.status_code,302)
        with connect(self.db) as conn: op=list_opportunities(conn)[0]
        self.assertEqual(op["evidence"][0]["status"],"RECEIVED")
        self.assertIsNone(op["readiness"]["teller"])
        self.assertEqual(op["attention"],"ACTION_NEEDED")

    def test_protected_deal_stage_not_available(self):
        oid=self.create()
        with connect(self.db) as conn: op=list_opportunities(conn)[0]
        result=self.post("/opportunities/"+oid+"/stage",{
            "revision":str(op["version"]),"target":"ACQUIRED","reason":"Trying to bypass authorization"})
        self.assertEqual(result.status_code,409)
        with connect(self.db) as conn: op=list_opportunities(conn)[0]
        self.assertEqual(op["lifecycle"],"DISCOVERED")

    def test_source_changes_invalidate_and_track_history(self):
        oid=self.create()
        with connect(self.db) as conn: op=list_opportunities(conn)[0]
        result=self.post("/opportunities/"+oid+"/source",{
            "revision":str(op["version"]),"url":"https://example.org/second"})
        self.assertEqual(result.status_code,302)
        with connect(self.db) as conn: op=list_opportunities(conn)[0]
        self.assertEqual(op["analysis_state"],"STALE")
        self.assertEqual(len(op["sources"]),2)

if __name__=="__main__":unittest.main()
