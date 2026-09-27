"""Authenticated owner Saved Search / Radar route tests on a private actual DB."""
from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from cryptography.fernet import Fernet
from werkzeug.security import generate_password_hash

from buybox.app import create_app
from buybox.store import connect, load
from buybox.saved_search import saved_searches, latest_check


class SavedSearchWebTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        root=Path(self.temp.name)
        root.chmod(0o700)
        docs=root/"originals"
        docs.mkdir(mode=0o700)
        self.path=str(root/"workspace.sqlite3")
        self.app=create_app({
            "TESTING":True,"SECRET_KEY":"test-secret-only",
            "BUYBOX_AUTH_MODE":"local",
            "BUYBOX_PASSWORD_HASH":generate_password_hash("test-private-owner"),
            "BUYBOX_DB_PATH":self.path,"BUYBOX_DOCS_DIR":str(docs),
            "BUYBOX_DOCUMENT_KEY":Fernet.generate_key().decode(),
            "SESSION_COOKIE_SECURE":False,
        })
        self.client=self.app.test_client()
        with self.client.session_transaction() as session:
            session["csrf"]="test-token"
        response=self.client.post("/login",data={
            "csrf_token":"test-token","password":"test-private-owner"})
        self.assertEqual(response.status_code,302)
        with self.client.session_transaction() as session:
            self.csrf=session["csrf"]

    def tearDown(self):
        self.temp.cleanup()

    def post(self,path,fields):
        return self.client.post(path,data={**fields,"csrf_token":self.csrf})

    def create_opportunity(self,name,price="95000"):
        response=self.post("/opportunities",{
            "vertical":"atm","name":name,"asking_price":price,
            "city":"Griffin","region":"GA","source_url":""})
        self.assertEqual(response.status_code,302)
        return response.location.rsplit("/",1)[-1]

    def create_saved(self):
        response=self.post("/saved-searches",{
            "name":"Actual Georgia route search","vertical":"atm",
            "query":"Griffin","max_price":"100000"})
        self.assertEqual(response.status_code,303)
        return response.location.rsplit("/",1)[-1]

    def test_owner_check_baselines_then_recognizes_real_saved_changes(self):
        first_id=self.create_opportunity("Owner's first actual route")
        search_id=self.create_saved()
        page=self.client.get("/saved-searches/"+search_id)
        self.assertEqual(page.status_code,200)
        self.assertIn(b"No Radar result exists yet",page.data)
        self.assertNotIn(b"Newly matches this filter",page.data)
        baseline=self.post("/saved-searches/"+search_id+"/check",{})
        self.assertEqual(baseline.status_code,303)
        with connect(self.path) as conn:
            first=latest_check(conn,search_id)
        self.assertTrue(first["result"]["delta"]["first_baseline"])
        self.assertEqual(first["result"]["delta"]["newly_matching"],[])
        self.assertEqual(first["result"]["match_ids"],[first_id])
        other_id=self.create_opportunity("Another actual owner route","89000")
        changed=self.post("/saved-searches/"+search_id+"/check",{})
        self.assertEqual(changed.status_code,303)
        with connect(self.path) as conn:
            later=latest_check(conn,search_id)
        self.assertFalse(later["result"]["delta"]["first_baseline"])
        self.assertEqual(later["result"]["delta"]["newly_matching"],[other_id])
        self.assertFalse(later["result"]["automated_notification_sent"])
        page=self.client.get("/saved-searches/"+search_id)
        self.assertIn(other_id.encode(),page.data)
        self.assertIn(b"Newly matches this filter",page.data)
        self.assertIn(b"persisted BuyBox",page.data)

    def test_record_revision_reported_then_price_change_no_longer_matching(self):
        oid=self.create_opportunity("Actual route")
        sid=self.create_saved()
        self.post("/saved-searches/"+sid+"/check",{})
        with connect(self.path) as conn:
            op=load(conn,oid)
        response=self.post("/opportunities/"+oid+"/source",{
            "revision":str(op["version"]),"url":"https://example.org/real-file-reference"})
        self.assertEqual(response.status_code,302)
        self.post("/saved-searches/"+sid+"/check",{})
        with connect(self.path) as conn:
            result=latest_check(conn,sid)["result"]
        self.assertEqual(len(result["delta"]["revised"]),1)
        self.assertEqual(result["delta"]["revised"][0]["id"],oid)
        self.assertEqual(result["delta"]["revised"][0]["previous_revision"],1)
        self.assertEqual(result["delta"]["revised"][0]["current_revision"],2)

    def test_archived_search_is_audited_not_deleted_and_blocked(self):
        self.create_opportunity("Owner route")
        sid=self.create_saved()
        self.post("/saved-searches/"+sid+"/check",{})
        response=self.post("/saved-searches/"+sid+"/archive",{})
        self.assertEqual(response.status_code,303)
        with connect(self.path) as conn:
            definition=next(x for x in saved_searches(conn) if x["id"]==sid)
            previous=latest_check(conn,sid)
        self.assertIsNotNone(definition["archived_at"])
        self.assertEqual(definition["archived_by"],"local_owner")
        self.assertIsNotNone(previous)
        self.assertEqual(self.post("/saved-searches/"+sid+"/check",{}).status_code,409)
        self.assertIn(b"Archived owner view",self.client.get("/saved-searches/"+sid).data)

    def test_invalid_filters_no_source_observation_or_search_written(self):
        self.assertEqual(self.post("/saved-searches",{
            "name":"Invalid","vertical":"unregistered","query":"",
            "max_price":"1e5"}).status_code,409)
        with connect(self.path) as conn:
            self.assertEqual(saved_searches(conn),[])

    def test_cannot_read_owner_saved_search_without_login(self):
        sid=self.create_saved()
        anonymous=self.app.test_client()
        self.assertEqual(anonymous.get("/saved-searches").status_code,302)
        self.assertEqual(anonymous.get("/saved-searches/"+sid).status_code,302)
        self.assertEqual(anonymous.post("/saved-searches/"+sid+"/check",
                  data={"csrf_token":"fake"}).status_code,400)


if __name__=="__main__":
    unittest.main()
