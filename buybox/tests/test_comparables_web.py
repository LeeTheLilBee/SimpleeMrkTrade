"""BBX066: real encrypted comparable original -> authenticated owner market research."""
import tempfile
import unittest
from io import BytesIO
from pathlib import Path
from cryptography.fernet import Fernet
from werkzeug.security import generate_password_hash
from buybox.app import create_app
from buybox.store import connect,load
from buybox.comparables import market_evidence_report

class ComparableWebTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.root=Path(self.temp.name);self.root.chmod(0o700)
        self.docs=self.root/"docs";self.docs.mkdir(mode=0o700)
        self.dbpath=str(self.root/"buybox.sqlite3")
        self.app=create_app({
            "TESTING":True,"SECRET_KEY":"only-tests-no-production-secret",
            "BUYBOX_AUTH_MODE":"local",
            "BUYBOX_PASSWORD_HASH":generate_password_hash("only-tests-local-pass"),
            "BUYBOX_DB_PATH":self.dbpath,"BUYBOX_DOCS_DIR":str(self.docs),
            "BUYBOX_DOCUMENT_KEY":Fernet.generate_key().decode(),
            "SESSION_COOKIE_SECURE":False,
        })
        self.client=self.app.test_client()
        with self.client.session_transaction() as sess:sess["csrf"]="test-csrf"
        result=self.client.post("/login",data={"csrf_token":"test-csrf",
            "password":"only-tests-local-pass"})
        self.assertEqual(result.status_code,302)
        with self.client.session_transaction() as sess:self.csrf=sess["csrf"]
        created=self.post("/opportunities",{
            "vertical":"atm","name":"Actual owner-entered acquisition",
            "asking_price":"95000","city":"","region":"","source_url":""})
        self.assertEqual(created.status_code,302)
        self.oid=created.location.rsplit("/",1)[-1]

    def tearDown(self):
        self.temp.cleanup()

    def post(self,path,values,**kwargs):
        return self.client.post(path,data={"csrf_token":self.csrf,**values},**kwargs)

    def current(self):
        with connect(self.dbpath) as conn:return load(conn,self.oid)

    def original(self,name):
        op=self.current()
        r=self.post("/opportunities/"+self.oid+"/upload",{
            "revision":str(op["version"]),"kind":"comparable_original",
            "source_party":"Owner-recorded original provider",
            "document":(BytesIO(b"%PDF-1.7\nComparable documented listing\n%%EOF"),
                        name,"application/pdf"),
        },content_type="multipart/form-data")
        self.assertEqual(r.status_code,302)
        op=self.current()
        return op["evidence"][-1],op["artifacts"][-1]

    def claim(self,evidence_id,**kwargs):
        op=self.current()
        v=dict(revision=str(op["version"]),evidence_id=evidence_id,
               subject_id="property-1",market="Georgia metro",
               source_kind="DOCUMENTED_LISTING_ASK",basis="PRICE_PER_INCLUDED_MACHINE",
               price="100000",denominator="10",event_date="2026-09-26",
               locator="Page 3, listing price",supersedes="",correction_reason="")
        v.update(kwargs)
        return self.post("/opportunities/"+self.oid+"/valuation/comparables",v)

    def test_empty_room_has_no_fabricated_market_sales(self):
        page=self.client.get("/opportunities/"+self.oid+"/valuation")
        self.assertEqual(page.status_code,200)
        self.assertIn(b"No comparable observations recorded",page.data)
        self.assertEqual(self.current().get("comparable_observations",[]),[])
        self.assertEqual(self.claim("invented-id").status_code,409)

    def test_two_protected_originals_produce_only_descriptive_cohort(self):
        first,a=self.original("one.pdf")
        second,b=self.original("two.pdf")
        self.assertEqual(self.claim(first["id"]).status_code,303)
        self.assertEqual(self.claim(second["id"],subject_id="property-2",
                                    price="120000",market="georgia METRO").status_code,303)
        op=self.current()
        report=market_evidence_report(op)
        cohort=report["cohorts"][0]
        self.assertEqual(cohort["observed_median"],"11000.00")
        self.assertIsNone(cohort["appraised_value"])
        self.assertFalse(report["target_value_calculated"])
        page=self.client.get("/opportunities/"+self.oid+"/valuation")
        self.assertEqual(page.status_code,200)
        self.assertIn(b"11000.00",page.data)
        self.assertIn(b"one.pdf",page.data)
        self.assertIn(b"two.pdf",page.data)
        self.assertNotIn(a["storage_reference"].encode(),page.data)
        self.assertNotIn(b["storage_reference"].encode(),page.data)
        explanation=self.client.get("/opportunities/"+self.oid+"/soulaana?intent=valuation")
        self.assertEqual(explanation.status_code,200)
        self.assertIn(b"DESCRIPTIVE COMPARABLE COHORT",explanation.data)
        self.assertIn(op["comparable_observations"][0]["id"].encode(),explanation.data)
        self.assertIn(b"NO TARGET VALUATION",explanation.data)
        self.assertIsNone(op["readiness"]["teller"])

    def test_duplicate_same_subject_event_does_not_inflate_market(self):
        e,_=self.original("one.pdf")
        self.assertEqual(self.claim(e["id"]).status_code,303)
        self.assertEqual(self.claim(e["id"],price="130000").status_code,409)
        self.assertEqual(market_evidence_report(self.current())["active_count"],1)

    def test_tampered_original_cannot_support_comparable_and_anonymous_denied(self):
        e,a=self.original("one.pdf")
        (self.docs/a["storage_reference"]).write_bytes(b"tampered-original")
        self.assertEqual(self.claim(e["id"]).status_code,409)
        self.assertFalse(self.current().get("comparable_observations"))
        anonymous=self.app.test_client()
        self.assertEqual(anonymous.get("/opportunities/"+self.oid+"/valuation").status_code,302)
        self.assertEqual(anonymous.get("/opportunities/"+self.oid+"/documents/"+a["id"]).status_code,302)
        self.assertEqual(anonymous.post("/opportunities/"+self.oid+"/valuation/comparables",
                                        data={"csrf_token":"bad"}).status_code,400)

if __name__=="__main__":
    unittest.main()
