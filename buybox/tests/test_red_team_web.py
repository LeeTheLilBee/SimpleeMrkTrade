"""End-to-end Red Team owner flow with encrypted real-original test fixtures."""
import tempfile
import unittest
from pathlib import Path
from io import BytesIO

from cryptography.fernet import Fernet
from werkzeug.security import generate_password_hash

from buybox.app import create_app
from buybox.store import connect,load

class RedTeamWebTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        root=Path(self.tmp.name)
        self.docs=root/"originals"
        self.docs.mkdir(mode=0o700)
        self.db=str(root/"real-owner-test.sqlite3")
        self.app=create_app({
            "TESTING":True,"SECRET_KEY":"only-tests-never-host",
            "BUYBOX_AUTH_MODE":"local",
            "BUYBOX_PASSWORD_HASH":generate_password_hash("test-only-password"),
            "BUYBOX_DB_PATH":self.db,"BUYBOX_DOCS_DIR":str(self.docs),
            "BUYBOX_DOCUMENT_KEY":Fernet.generate_key().decode(),
            "SESSION_COOKIE_SECURE":False,
        })
        self.client=self.app.test_client()
        with self.client.session_transaction() as sess:sess["csrf"]="unit-csrf"
        self.csrf="unit-csrf"
        response=self.post("/login",{"password":"test-only-password"})
        self.assertEqual(response.status_code,302)
        with self.client.session_transaction() as sess:self.csrf=sess["csrf"]
        response=self.post("/opportunities",{
            "vertical":"atm","name":"Real-input test opportunity",
            "asking_price":"100000","city":"","region":"","source_url":""})
        self.assertEqual(response.status_code,302)
        self.oid=response.location.rsplit("/",1)[-1]

    def tearDown(self): self.tmp.cleanup()

    def post(self,path,fields,**kwargs):
        return self.client.post(path,data={**fields,"csrf_token":self.csrf},**kwargs)

    def load(self):
        with connect(self.db) as db:return load(db,self.oid)

    def originals_and_metrics(self):
        for kind,metric,amount in (
            ("processor_statements","annual_revenue","80000"),
            ("expense_records","annual_expenses","30000"),
        ):
            op=self.load()
            response=self.post("/opportunities/"+self.oid+"/upload",{
                "revision":str(op["version"]),"kind":kind,
                "source_party":"Test-only document source",
                "document":(BytesIO(("%PDF-1.7\n"+metric+"\n%%EOF").encode()),
                            metric+".pdf","application/pdf"),
            },content_type="multipart/form-data")
            self.assertEqual(response.status_code,302)
            op=self.load()
            evidence=next(e for e in op["evidence"] if e["kind"]==kind and e["status"]=="RECEIVED")
            response=self.post("/opportunities/"+self.oid+"/evidence/"+evidence["id"]+"/review",{
                "revision":str(op["version"]),"rationale":"Personally examined source file in test"})
            self.assertEqual(response.status_code,302)
            op=self.load()
            reviewed=next(e for e in op["evidence"] if e["kind"]==kind and e["status"]=="DOCUMENT_SUPPORTED")
            response=self.post("/opportunities/"+self.oid+"/metric",{
                "revision":str(op["version"]),"metric_name":metric,
                "value":amount,"period":"2025-01-01 / 2025-12-31",
                "evidence_id":reviewed["id"]})
            self.assertEqual(response.status_code,302)

    def stress(self,revision=None,**updates):
        op=self.load()
        params={"revision":str(op["version"] if revision is None else revision),
                "name":"Owner volume/cost hypothesis",
                "rationale":"Assess financial sensitivity without claiming a real event.",
                "revenue_factor":"0.75","expense_factor":"1.20"}
        params.update(updates)
        return self.post("/opportunities/"+self.oid+"/red-team",params)

    def test_no_source_no_model_no_auto_generated_scenario(self):
        page=self.client.get("/opportunities/"+self.oid+"/red-team")
        self.assertEqual(page.status_code,200)
        self.assertIn(b"Unavailable",page.data)
        self.assertIn(b"No owner stress scenarios recorded",page.data)
        self.assertEqual(self.stress().status_code,409)
        self.assertNotIn("owner_stress_records",self.load())

    def test_encrypted_original_to_actual_persisted_stress_and_soulaana(self):
        self.originals_and_metrics()
        page=self.client.get("/opportunities/"+self.oid+"/red-team")
        self.assertIn(b"50000.00",page.data)
        r=self.stress()
        self.assertEqual(r.status_code,303)
        op=self.load()
        rec=op["owner_stress_records"][0]
        self.assertEqual(rec["recorded_operating_difference"],"50000.00")
        self.assertEqual(rec["modeled_operating_difference"],"24000.00")
        self.assertFalse(rec["authorizes_purchase"])
        self.assertEqual(rec["recorded_opportunity_revision"],op["version"])
        self.assertEqual(len(rec["source_metrics"]),2)
        page=self.client.get("/opportunities/"+self.oid+"/red-team")
        self.assertIn(b"24000.00",page.data)
        self.assertIn(b"CURRENT SOURCE VERSION",page.data)
        self.assertIn(b"Owner volume/cost hypothesis",page.data)
        soulaana=self.client.get("/opportunities/"+self.oid+"/soulaana?intent=red_team")
        self.assertEqual(soulaana.status_code,200)
        self.assertIn(b"OWNER RECORDED STRESS",soulaana.data)
        self.assertIn(rec["id"].encode(),soulaana.data)
        self.assertEqual(self.stress(revision=rec["source_opportunity_revision"]).status_code,409)
        self.assertEqual(len(self.load()["owner_stress_records"]),1)

    def test_tampered_encrypted_original_cannot_appear_available_or_be_saved(self):
        self.originals_and_metrics()
        op=self.load()
        artifact=op["artifacts"][0]
        (self.docs/artifact["storage_reference"]).write_bytes(b"tampered ciphertext")
        page=self.client.get("/opportunities/"+self.oid+"/red-team")
        self.assertIn(b"Unavailable",page.data)
        self.assertEqual(self.stress().status_code,409)
        self.assertNotIn("owner_stress_records",self.load())

    def test_anonymous_cannot_read_or_submit_owner_stress(self):
        self.originals_and_metrics()
        outsider=self.app.test_client()
        self.assertEqual(outsider.get("/opportunities/"+self.oid+"/red-team").status_code,302)
        self.assertEqual(outsider.post("/opportunities/"+self.oid+"/red-team",
                         data={"csrf_token":"bad"}).status_code,400)

if __name__=="__main__":unittest.main()
