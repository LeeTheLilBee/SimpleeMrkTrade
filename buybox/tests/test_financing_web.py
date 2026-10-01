"""BBX061: actual encrypted financing original -> protected owner comparison."""
import tempfile
import unittest
from io import BytesIO
from pathlib import Path

from cryptography.fernet import Fernet
from werkzeug.security import generate_password_hash

from buybox.app import create_app
from buybox.store import connect, load
from buybox.financing import financing_snapshot

class FinancingWebTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.root=Path(self.tmp.name)
        self.root.chmod(0o700)
        self.docs=self.root/"docs"
        self.docs.mkdir(mode=0o700)
        self.db_path=str(self.root/"buybox.sqlite3")
        self.app=create_app({
            "TESTING":True,"SECRET_KEY":"test-only-not-a-real-secret",
            "BUYBOX_AUTH_MODE":"local",
            "BUYBOX_PASSWORD_HASH":generate_password_hash("test-only-local-password"),
            "BUYBOX_DB_PATH":self.db_path,
            "BUYBOX_DOCS_DIR":str(self.docs),
            "BUYBOX_DOCUMENT_KEY":Fernet.generate_key().decode(),
            "SESSION_COOKIE_SECURE":False,
        })
        self.client=self.app.test_client()
        with self.client.session_transaction() as s:s["csrf"]="test-csrf"
        login=self.client.post("/login",data={"csrf_token":"test-csrf",
                                           "password":"test-only-local-password"})
        self.assertEqual(login.status_code,302)
        with self.client.session_transaction() as s:self.csrf=s["csrf"]
        result=self.post("/opportunities",{
            "vertical":"atm","name":"Owner-entered opportunity",
            "asking_price":"100000","city":"","region":"","source_url":""})
        self.assertEqual(result.status_code,302)
        self.oid=result.location.rsplit("/",1)[-1]

    def tearDown(self):
        self.tmp.cleanup()

    def post(self,path,data,**kwargs):
        return self.client.post(path,data={"csrf_token":self.csrf,**data},**kwargs)

    def current(self):
        with connect(self.db_path) as conn:return load(conn,self.oid)

    def original(self):
        op=self.current()
        response=self.post("/opportunities/"+self.oid+"/upload",{
            "revision":str(op["version"]),"kind":"financing_terms",
            "source_party":"Term sheet received from actual source",
            "document":(BytesIO(b"%PDF-1.7\nActual written terms in test-only original\n%%EOF"),
                        "terms.pdf","application/pdf"),
        },content_type="multipart/form-data")
        self.assertEqual(response.status_code,302)
        now=self.current()
        return next(e for e in now["evidence"] if e["kind"]=="financing_terms"),now["artifacts"][-1]

    def terms(self,eid,revision=None,**changes):
        op=self.current()
        fields={
            "revision":str(op["version"] if revision is None else revision),
            "evidence_id":eid,"lender_name":"Owner-entered provider label",
            "program_name":"Owner-transcribed full amortization",
            "source_locator":"Page 2 - pricing table","source_date":"2026-09-20",
            "expiration_date":"2026-10-15","purchase_price":"100000",
            "principal":"80000","apr_percent":"0","term_months":"120",
            "origination_fee":"1000","lender_fee":"500",
            "other_closing_cost":"2500","reserve_cash":"10000",
            "vault_cash":"12000","supersedes":"","correction_reason":"",
        }
        fields.update(changes)
        return self.post("/opportunities/"+self.oid+"/financing/options",fields)

    def test_empty_app_has_no_fabricated_lender(self):
        page=self.client.get("/opportunities/"+self.oid+"/financing")
        self.assertEqual(page.status_code,200)
        self.assertIn(b"No documented financing options yet",page.data)
        self.assertIn(b"Unknown",page.data)
        self.assertEqual(self.current().get("financing_options",[]),[])
        result=self.terms("made-up-evidence-id")
        self.assertEqual(result.status_code,409)
        self.assertFalse(self.current().get("financing_options"))

    def test_original_upload_and_owner_recorded_terms_are_persisted(self):
        e,art=self.original()
        self.assertEqual(e["status"],"RECEIVED")
        self.assertEqual(e["artifact_id"],art["id"])
        self.assertEqual(self.terms(e["id"]).status_code,303)
        op=self.current()
        self.assertEqual(len(op["financing_options"]),1)
        q=op["financing_options"][0]
        self.assertEqual(q["source_artifact_id"],art["id"])
        self.assertEqual(q["source_sha256"],art["sha256"])
        self.assertFalse(q["lender_approval_confirmed"])
        self.assertEqual(op["readiness"]["teller"],None)
        self.assertFalse(financing_snapshot(op)["authorizes_acquisition"])
        page=self.client.get("/opportunities/"+self.oid+"/financing")
        self.assertEqual(page.status_code,200)
        self.assertIn(b"Owner-entered provider label",page.data)
        self.assertIn(b"666.67",page.data)
        self.assertIn(b"46000.00",page.data)
        self.assertIn(b"Physical vault cash",page.data)
        self.assertNotIn(art["storage_reference"].encode(),page.data)
        context=self.client.get("/opportunities/"+self.oid+"/soulaana?intent=financing")
        self.assertEqual(context.status_code,200)
        self.assertIn(b"SOURCE LINKED FINANCING",context.data)
        self.assertIn(q["id"].encode(),context.data)
        self.assertIn(b"NOT APPROVED",context.data)

    def test_stale_form_and_changed_asking_price_need_recheck(self):
        e,_=self.original()
        old_revision=self.current()["version"]
        self.assertEqual(self.terms(e["id"]).status_code,303)
        self.assertEqual(self.terms(e["id"],revision=old_revision).status_code,409)
        self.assertEqual(len(self.current()["financing_options"]),1)
        with connect(self.db_path) as conn:
            op=load(conn,self.oid)
            op["asking_price"]="104000.00"
            from buybox.store import save
            save(conn,op,"SellerAskingChanged",expected_revision=op["version"])
        page=self.client.get("/opportunities/"+self.oid+"/financing")
        self.assertIn(b"Opportunity Asking Price Changed",page.data)
        self.assertEqual(financing_snapshot(self.current())["options"][0]["analysis"]["teller_readiness"],
                         "UNKNOWN")

    def test_tampered_encrypted_original_cannot_support_lender_terms(self):
        evidence,artifact=self.original()
        (self.docs/artifact["storage_reference"]).write_bytes(b"tampered-ciphertext")
        response=self.terms(evidence["id"])
        self.assertEqual(response.status_code,409)
        self.assertFalse(self.current().get("financing_options"))

    def test_anonymous_cannot_access_documents_or_finance(self):
        e,a=self.original()
        anon=self.app.test_client()
        self.assertEqual(anon.get("/opportunities/"+self.oid+"/financing").status_code,302)
        self.assertEqual(anon.get("/opportunities/"+self.oid+"/documents/"+a["id"]).status_code,302)
        self.assertEqual(anon.post("/opportunities/"+self.oid+"/financing/options",
                                   data={"csrf_token":"bad"}).status_code,400)

if __name__=="__main__":
    unittest.main()
