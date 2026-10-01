"""End-to-end Deal Integrity owner flows against real saved test-only originals."""
from __future__ import annotations

from io import BytesIO
from pathlib import Path
import tempfile
import unittest

from cryptography.fernet import Fernet
from werkzeug.security import generate_password_hash

from buybox.app import create_app
from buybox.store import connect, load


class DealIntegrityWebTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.root=Path(self.temp.name)
        self.root.chmod(0o700)
        self.docs=self.root/"originals"
        self.docs.mkdir(mode=0o700)
        self.path=str(self.root/"buybox.sqlite3")
        self.app=create_app({
            "TESTING":True, "SECRET_KEY":"only-for-test-suite",
            "BUYBOX_AUTH_MODE":"local",
            "BUYBOX_PASSWORD_HASH":generate_password_hash("private-test-password"),
            "BUYBOX_DB_PATH":self.path,"BUYBOX_DOCS_DIR":str(self.docs),
            "BUYBOX_DOCUMENT_KEY":Fernet.generate_key().decode(),
            "SESSION_COOKIE_SECURE":False,
        })
        self.client=self.app.test_client()
        with self.client.session_transaction() as ses:
            ses["csrf"]="test-csrf"
        self.csrf="test-csrf"
        response=self.client.post("/login",data={
            "csrf_token":self.csrf,"password":"private-test-password"})
        self.assertEqual(response.status_code,302)
        with self.client.session_transaction() as ses:
            self.csrf=ses["csrf"]
        response=self.post("/opportunities",{
            "vertical":"atm","name":"Owner-supplied opportunity",
            "asking_price":"95000","city":"","region":"","source_url":""})
        self.assertEqual(response.status_code,302)
        self.oid=response.location.rsplit("/",1)[-1]

    def tearDown(self):
        self.temp.cleanup()

    def op(self):
        with connect(self.path) as conn:
            return load(conn,self.oid)

    def post(self,path,fields,**kwargs):
        return self.client.post(path,data={**fields,"csrf_token":self.csrf},**kwargs)

    def upload(self,name,content):
        before=self.op()
        response=self.post("/opportunities/"+self.oid+"/upload",{
            "revision":str(before["version"]),"kind":"processor_statements",
            "source_party":"Actual file source in test fixture",
            "document":(BytesIO(content),name,"application/pdf"),
        },content_type="multipart/form-data")
        self.assertEqual(response.status_code,302)
        current=self.op()
        return current["evidence"][-1],current["artifacts"][-1]

    def claim(self,evidence_id,value, *, revision=None, **changes):
        op=self.op()
        fields={
            "revision":str(op["version"] if revision is None else revision),
            "evidence_id":evidence_id,"subject_id":"deal",
            "field":"ANNUAL_REVENUE","value":value,
            "period_key":"2025-01-01 / 2025-12-31",
            "locator":"Page 3, revenue line",
        }
        fields.update(changes)
        return self.post("/opportunities/"+self.oid+"/claims",fields)

    def test_real_document_discrepancies_display_and_block_with_sources(self):
        self.assertEqual(self.client.get("/opportunities/"+self.oid+"/integrity").status_code,200)
        first,artifact_a=self.upload("one.pdf",b"%PDF-1.7\nRevenue: 80000\n%%EOF")
        second,artifact_b=self.upload("two.pdf",b"%PDF-1.7\nRevenue: 92000\n%%EOF")
        self.assertEqual(self.claim(first["id"],"80000").status_code,303)
        self.assertEqual(self.claim(second["id"],"92000").status_code,303)
        op=self.op()
        self.assertEqual(len(op["source_claims"]),2)
        from buybox.core import evaluate
        evaluation=evaluate(op)
        self.assertEqual(evaluation["deal_integrity"]["unresolved_count"],1)
        self.assertFalse(evaluation["purchase_authorized"])
        self.assertEqual(evaluation["judgment"],"REVIEW")
        dossier=self.client.get("/opportunities/"+self.oid)
        self.assertEqual(dossier.status_code,200)
        self.assertIn(b"unresolved document comparison",dossier.data)
        page=self.client.get("/opportunities/"+self.oid+"/integrity")
        self.assertEqual(page.status_code,200)
        self.assertIn(b"80000",page.data)
        self.assertIn(b"92000",page.data)
        self.assertIn(b"one.pdf",page.data)
        self.assertIn(b"two.pdf",page.data)
        self.assertNotIn(artifact_a["storage_reference"].encode(),page.data)
        self.assertNotIn(artifact_b["storage_reference"].encode(),page.data)
        explanation=self.client.get("/opportunities/"+self.oid+"/soulaana?intent=evidence")
        self.assertIn(b"SOURCE DISCREPANCY",explanation.data)
        self.assertIn(b"Neither source has been selected",explanation.data)
        self.assertEqual(op["readiness"]["teller"],None)

    def test_claim_before_document_review_can_follow_exact_successor_evidence(self):
        first,artifact=self.upload("original.pdf",b"%PDF-1.7\nPage 3\n%%EOF")
        self.assertEqual(self.claim(first["id"],"80000").status_code,303)
        old_claim=self.op()["source_claims"][-1]
        before=self.op()
        unready=self.post("/opportunities/"+self.oid+"/claims/"+old_claim["id"]+"/review",{
            "revision":str(before["version"]),"rationale":"Read the exact original."})
        self.assertEqual(unready.status_code,409)
        reviewed=self.post("/opportunities/"+self.oid+"/evidence/"+first["id"]+"/review",{
            "revision":str(before["version"]),"rationale":"I inspected the processor file"})
        self.assertEqual(reviewed.status_code,302)
        current=self.op()
        successor=next(e for e in current["evidence"] if
                       e.get("supersedes")==first["id"] and e["status"]=="DOCUMENT_SUPPORTED")
        page=self.client.get("/opportunities/"+self.oid+"/integrity")
        self.assertIn(b"Record owner documentary review",page.data)
        response=self.post("/opportunities/"+self.oid+"/claims/"+old_claim["id"]+"/review",{
            "revision":str(current["version"]),"rationale":"I checked page 3 against the original"})
        self.assertEqual(response.status_code,303)
        current=self.op()
        new_claim=current["source_claims"][-1]
        self.assertEqual(new_claim["state"],"OWNER_DOCUMENT_REVIEWED")
        self.assertEqual(new_claim["evidence_id"],successor["id"])
        self.assertEqual(new_claim["source_evidence_id"],first["id"])
        self.assertEqual(new_claim["artifact_sha256"],artifact["sha256"])
        self.assertFalse(new_claim["independently_verified"])
        self.assertNotIn("annual_revenue",current["metrics"])
        second=self.post("/opportunities/"+self.oid+"/claims/"+old_claim["id"]+"/review",{
            "revision":str(current["version"]),"rationale":"Retry"})
        self.assertEqual(second.status_code,409)

    def test_stale_revision_cannot_insert_claim_and_invalid_source_is_not_accepted(self):
        e,_=self.upload("first.pdf",b"%PDF-1.7\nFile\n%%EOF")
        current=self.op()
        old_revision=current["version"]
        self.assertEqual(self.claim(e["id"],"80000").status_code,303)
        stale=self.claim(e["id"],"90000",revision=old_revision)
        self.assertEqual(stale.status_code,409)
        self.assertEqual(len(self.op()["source_claims"]),1)
        fake=self.claim("invented-source-id","92000")
        self.assertEqual(fake.status_code,409)
        self.assertEqual(len(self.op()["source_claims"]),1)

    def test_unauthenticated_user_cannot_read_integrity_or_review_claim(self):
        e,_=self.upload("first.pdf",b"%PDF-1.7\nFile\n%%EOF")
        self.assertEqual(self.claim(e["id"],"80000").status_code,303)
        claim_id=self.op()["source_claims"][0]["id"]
        anonymous=self.app.test_client()
        self.assertEqual(anonymous.get("/opportunities/"+self.oid+"/integrity").status_code,302)
        self.assertEqual(anonymous.post("/opportunities/"+self.oid+"/claims/"+claim_id+"/review",
                      data={"rationale":"No","csrf_token":"wrong"}).status_code,400)


if __name__=="__main__":
    unittest.main()
