"""BBX081 — actual encrypted insurance originals and protected owner web workflow."""
from __future__ import annotations

from io import BytesIO
from pathlib import Path
import tempfile
import unittest

from cryptography.fernet import Fernet
from werkzeug.security import generate_password_hash

from buybox.app import create_app
from buybox.insurance import insurance_snapshot
from buybox.store import connect, load


class InsuranceWebTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.root=Path(self.tmp.name)
        self.root.chmod(0o700)
        self.docs=self.root/"originals"
        self.docs.mkdir(mode=0o700)
        self.db_path=str(self.root/"buybox.sqlite3")
        self.app=create_app({
            "TESTING":True,"SECRET_KEY":"test-only-local-secret",
            "BUYBOX_AUTH_MODE":"local",
            "BUYBOX_PASSWORD_HASH":generate_password_hash("local-test-password"),
            "BUYBOX_DB_PATH":self.db_path,"BUYBOX_DOCS_DIR":str(self.docs),
            "BUYBOX_DOCUMENT_KEY":Fernet.generate_key().decode(),
            "SESSION_COOKIE_SECURE":False,
        })
        self.client=self.app.test_client()
        with self.client.session_transaction() as session:session["csrf"]="test-csrf"
        logged=self.client.post("/login",data={
            "csrf_token":"test-csrf","password":"local-test-password"})
        self.assertEqual(logged.status_code,302)
        with self.client.session_transaction() as session:self.csrf=session["csrf"]
        result=self.post("/opportunities",{
            "vertical":"atm","name":"Actual owner record","asking_price":"100000",
            "city":"","region":"","source_url":""})
        self.assertEqual(result.status_code,302)
        self.oid=result.location.rsplit("/",1)[-1]

    def tearDown(self):
        self.tmp.cleanup()

    def post(self,path,payload,**kwargs):
        return self.client.post(path,data={"csrf_token":self.csrf,**payload},**kwargs)

    def op(self):
        with connect(self.db_path) as conn:return load(conn,self.oid)

    def original(self,kind="insurance_document",filename="insurance.pdf"):
        before=self.op()
        response=self.post("/opportunities/"+self.oid+"/upload",{
            "revision":str(before["version"]),"kind":kind,
            "source_party":"Owner received actual document",
            "document":(BytesIO(b"%PDF-1.7\nInsurance source fixture\n%%EOF"),
                        filename,"application/pdf"),
        },content_type="multipart/form-data")
        self.assertEqual(response.status_code,302)
        current=self.op()
        return current["evidence"][-1],current["artifacts"][-1]

    def record(self,evidence_id, *, revision=None, **changes):
        op=self.op()
        payload={
            "revision":str(op["version"] if revision is None else revision),
            "evidence_id":evidence_id,
            "document_kind":"QUOTE","carrier_label":"Written source insurer",
            "broker_label":"Source broker",
            "source_locator":"Page 2 - quoted coverages",
            "source_date":"2026-09-20","quote_valid_until":"2026-10-15",
            "effective_date":"2026-10-01","expiration_date":"2027-10-01",
            "planned_closing_date":"2026-10-05",
            "coverage_codes":["PROPERTY","GENERAL_LIABILITY"],
            "annual_premium":"6000","upfront_premium_due":"2000",
            "limits_note":"From source original",
            "deductible_note":"See page 3",
            "exclusion_note":"Check actual exclusions",
            "supersedes":"","correction_reason":"",
        }
        payload.update(changes)
        return self.post("/opportunities/"+self.oid+"/insurance/records",payload)

    def test_empty_room_and_original_sourced_workflow(self):
        room=self.client.get("/opportunities/"+self.oid+"/insurance")
        self.assertEqual(room.status_code,200)
        self.assertIn(b"No insurance originals recorded yet",room.data)
        self.assertEqual(self.op().get("insurance_records",[]),[])
        invalid=self.record("fake-document-id")
        self.assertEqual(invalid.status_code,409)
        e,a=self.original()
        self.assertEqual(e["artifact_id"],a["id"])
        saved=self.record(e["id"])
        self.assertEqual(saved.status_code,303)
        op=self.op()
        self.assertEqual(len(op["insurance_records"]),1)
        rec=op["insurance_records"][0]
        self.assertEqual(rec["source_artifact_id"],a["id"])
        self.assertEqual(rec["source_sha256"],a["sha256"])
        self.assertFalse(rec["insurer_confirmation_verified"])
        self.assertEqual(rec["coverage_in_force"],"UNKNOWN")
        self.assertEqual(op["readiness"]["teller"],None)
        page=self.client.get("/opportunities/"+self.oid+"/insurance")
        self.assertEqual(page.status_code,200)
        self.assertIn(b"Written source insurer",page.data)
        self.assertIn(b"6000.00",page.data)
        self.assertIn(b"Quote Is Not Bound Policy",page.data)
        self.assertNotIn(a["storage_reference"].encode(),page.data)
        explaining=self.client.get("/opportunities/"+self.oid+"/soulaana?intent=insurance")
        self.assertEqual(explaining.status_code,200)
        self.assertIn(b"SOURCE LINKED INSURANCE",explaining.data)
        self.assertIn(rec["id"].encode(),explaining.data)
        self.assertFalse(insurance_snapshot(op)["authorizes_acquisition"])

    def test_actual_encrypted_source_must_be_untampered(self):
        e,a=self.original()
        (self.docs/a["storage_reference"]).write_bytes(b"tampered")
        response=self.record(e["id"])
        self.assertEqual(response.status_code,409)
        self.assertFalse(self.op().get("insurance_records"))

    def test_certificate_no_price_no_free_premium(self):
        e,a=self.original(filename="certificate.pdf")
        result=self.record(e["id"],document_kind="CERTIFICATE",
                           quote_valid_until="",effective_date="",expiration_date="",
                           annual_premium="",upfront_premium_due="")
        self.assertEqual(result.status_code,303)
        current=self.op()["insurance_records"][0]
        self.assertIsNone(current["annual_premium"])
        page=self.client.get("/opportunities/"+self.oid+"/insurance")
        self.assertIn(b"Not stated",page.data)
        self.assertIn(b"Certificate Alone Does Not Verify Current Coverage",page.data)
        self.assertNotIn(b"$0.00",page.data)

    def test_csrf_anonymous_stale_revision_and_scope(self):
        e,_=self.original()
        anonymous=self.app.test_client()
        self.assertEqual(anonymous.get("/opportunities/"+self.oid+"/insurance").status_code,302)
        self.assertEqual(anonymous.post("/opportunities/"+self.oid+"/insurance/records",
                         data={"csrf_token":"bad"}).status_code,400)
        stale=self.op()["version"]
        self.assertEqual(self.record(e["id"]).status_code,303)
        self.assertEqual(self.record(e["id"],revision=stale).status_code,409)
        self.assertEqual(len(self.op()["insurance_records"]),1)
        invalid=self.record(e["id"],coverage_codes=["UNKNOWN_FICTIONAL"])
        self.assertEqual(invalid.status_code,409)
        self.assertEqual(len(self.op()["insurance_records"]),1)

    def test_existing_property_insurance_quote_original_allowed(self):
        # Create separate multifamily opportunity with real uploaded original.
        response=self.post("/opportunities",{
            "vertical":"multifamily","name":"Actual owner property",
            "asking_price":"100000","city":"","region":"","source_url":""})
        self.assertEqual(response.status_code,302)
        self.oid=response.location.rsplit("/",1)[-1]
        e,a=self.original(kind="insurance_quote",filename="property-insurance.pdf")
        recorded=self.record(e["id"])
        self.assertEqual(recorded.status_code,303)
        self.assertEqual(self.op()["insurance_records"][0]["source_artifact_id"],a["id"])
        self.assertEqual(insurance_snapshot(self.op())["coverage_in_force"],"UNKNOWN")


if __name__=="__main__":
    unittest.main()
