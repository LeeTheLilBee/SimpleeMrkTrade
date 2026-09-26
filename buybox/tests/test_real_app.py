"""Real Flask endpoints; temporary file DB only, no fabricated product listings."""
import os
import tempfile
import unittest
from pathlib import Path
from werkzeug.security import generate_password_hash
from cryptography.fernet import Fernet
from io import BytesIO
from buybox.app import create_app
from buybox.store import connect, list_opportunities

class OwnerAppTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.db=str(Path(self.tmp.name)/"opportunities.sqlite3")
        self.docs=str(Path(self.tmp.name)/"documents")
        Path(self.docs).mkdir(mode=0o700)
        self.app=create_app({
            "TESTING":True, "SECRET_KEY":"test-secret-not-for-production",
            "BUYBOX_PASSWORD_HASH":generate_password_hash("test-local-only-password"),
            "BUYBOX_DB_PATH":self.db,"BUYBOX_DOCS_DIR":self.docs,
            "BUYBOX_DOCUMENT_KEY":Fernet.generate_key().decode(),
            "SESSION_COOKIE_SECURE":False,
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

    def test_owner_review_then_source_linked_financials(self):
        oid=self.create()
        with connect(self.db) as conn: op=list_opportunities(conn)[0]
        for kind,ref in (("processor_statements","processor-private-01"),("expense_records","expense-private-01")):
            result=self.post("/opportunities/"+oid+"/evidence",{
                "revision":str(op["version"]),"kind":kind,
                "reference":ref,"source_party":"Document source"})
            self.assertEqual(result.status_code,302)
            with connect(self.db) as conn: op=list_opportunities(conn)[0]
            eid=next(e["id"] for e in op["evidence"] if e["kind"]==kind and e["status"]=="RECEIVED")
            result=self.post("/opportunities/"+oid+"/evidence/"+eid+"/review",{
                "revision":str(op["version"]),"rationale":"Manually reviewed supporting document"})
            self.assertEqual(result.status_code,302)
            with connect(self.db) as conn: op=list_opportunities(conn)[0]
            reviewed=next(e for e in op["evidence"] if e["kind"]==kind and e["status"]=="DOCUMENT_SUPPORTED")
            self.assertEqual(reviewed["verification"]["verification_scope"],"DOCUMENT_SUPPORT_ONLY")
        for metric,value,kind in (("annual_revenue","80000","processor_statements"),
                                  ("annual_expenses","30000","expense_records")):
            evidence_id=next(e["id"] for e in op["evidence"] if e["kind"]==kind and e["status"]=="DOCUMENT_SUPPORTED")
            result=self.post("/opportunities/"+oid+"/metric",{
                "revision":str(op["version"]),"metric_name":metric,"value":value,
                "period":"2025-01-01 / 2025-12-31","evidence_id":evidence_id})
            self.assertEqual(result.status_code,302)
            with connect(self.db) as conn: op=list_opportunities(conn)[0]
        self.assertEqual(op["metrics"]["annual_revenue"]["value"],"80000")
        self.assertEqual(op["metrics"]["annual_expenses"]["value"],"30000")
        self.assertIsNone(op["readiness"]["teller"])
        self.assertIn(b"50000.00",self.client.get("/opportunities/"+oid).data)

    def test_wrong_evidence_category_cannot_support_expenses(self):
        oid=self.create()
        with connect(self.db) as conn: op=list_opportunities(conn)[0]
        self.post("/opportunities/"+oid+"/evidence",{
            "revision":str(op["version"]),"kind":"processor_statements",
            "reference":"processor-source","source_party":"Seller"})
        with connect(self.db) as conn: op=list_opportunities(conn)[0]
        eid=op["evidence"][-1]["id"]
        self.post("/opportunities/"+oid+"/evidence/"+eid+"/review",{
            "revision":str(op["version"]),"rationale":"Reviewed processor document"})
        with connect(self.db) as conn: op=list_opportunities(conn)[0]
        eid=next(e["id"] for e in op["evidence"] if e["status"]=="DOCUMENT_SUPPORTED")
        result=self.post("/opportunities/"+oid+"/metric",{
            "revision":str(op["version"]),"metric_name":"annual_expenses",
            "value":"100","period":"2025","evidence_id":eid})
        self.assertEqual(result.status_code,400)

    def test_upload_encrypts_real_original_and_authenticated_downloads(self):
        oid=self.create()
        with connect(self.db) as conn: op=list_opportunities(conn)[0]
        contents=b"%PDF-1.7\\nDocument supplied to owner\\n%%EOF"
        response=self.client.post("/opportunities/"+oid+"/upload",data={
            "revision":str(op["version"]),"csrf_token":self.csrf,
            "kind":"processor_statements","source_party":"Seller",
            "document":(BytesIO(contents),"seller_statement.pdf","application/pdf"),
        },content_type="multipart/form-data")
        self.assertEqual(response.status_code,302)
        with connect(self.db) as conn: op=list_opportunities(conn)[0]
        self.assertEqual(op["evidence"][-1]["status"],"RECEIVED")
        artifact=op["artifacts"][-1]
        encrypted=(Path(self.docs)/artifact["storage_reference"]).read_bytes()
        self.assertNotEqual(encrypted,contents)
        self.assertNotIn(b"Document supplied to owner",encrypted)
        download=self.client.get("/opportunities/"+oid+"/documents/"+artifact["id"])
        self.assertEqual(download.status_code,200)
        self.assertEqual(download.data,contents)
        self.assertIn("attachment",download.headers["Content-Disposition"])
        self.post("/logout",{})
        self.assertEqual(self.client.get("/opportunities/"+oid+"/documents/"+artifact["id"]).status_code,302)

    def test_invalid_upload_rejected_without_product_evidence(self):
        oid=self.create()
        with connect(self.db) as conn: op=list_opportunities(conn)[0]
        response=self.client.post("/opportunities/"+oid+"/upload",data={
            "revision":str(op["version"]),"csrf_token":self.csrf,
            "kind":"processor_statements","source_party":"Seller",
            "document":(BytesIO(b"not a real pdf"),"fake.pdf","application/pdf"),
        },content_type="multipart/form-data")
        self.assertEqual(response.status_code,400)
        with connect(self.db) as conn: op=list_opportunities(conn)[0]
        self.assertFalse(op.get("artifacts"))

    def test_compare_requires_real_saved_records(self):
        first=self.create()
        with connect(self.db) as conn: op=list_opportunities(conn)[0]
        second=self.post("/opportunities",{
            "vertical":"multifamily","name":"Another owner-entered opportunity",
            "asking_price":"","city":"","region":"","source_url":""}).location.rsplit("/",1)[-1]
        response=self.post("/compare",{"opportunity_id":[first,second]})
        self.assertEqual(response.status_code,200)
        self.assertIn(b"Owner-entered route",response.data)
        self.assertIn(b"Another owner-entered opportunity",response.data)
        self.assertEqual(self.post("/compare",{"opportunity_id":[first]}).status_code,400)

    def test_scenario_uses_recorded_figures_only(self):
        oid=self.create()
        page=self.client.get("/opportunities/"+oid+"/scenario?revenue_factor=0.75&expense_factor=2")
        self.assertEqual(page.status_code,200)
        self.assertIn(b"Unavailable",page.data)
        self.assertEqual(self.client.get("/opportunities/"+oid+"/scenario?revenue_factor=-1").status_code,400)

    def test_actual_deal_room_tasks_and_price_event(self):
        oid=self.create()
        page=self.client.get("/opportunities/"+oid+"/deal-room")
        self.assertEqual(page.status_code,200)
        self.assertIn(b"No tasks recorded yet",page.data)
        with connect(self.db) as conn: op=list_opportunities(conn)[0]
        result=self.post("/opportunities/"+oid+"/tasks",{
            "revision":str(op["version"]),"title":"Request serial-numbered inventory",
            "due_date":"2026-10-15","notes":"Waiting for seller"})
        self.assertEqual(result.status_code,302)
        with connect(self.db) as conn: op=list_opportunities(conn)[0]
        self.assertEqual(len(op["tasks"]),1)
        original_task=op["tasks"][0]["id"]
        result=self.post("/opportunities/"+oid+"/tasks/"+original_task+"/status",{
            "revision":str(op["version"]),"status":"COMPLETE","notes":"Received"})
        self.assertEqual(result.status_code,302)
        with connect(self.db) as conn: op=list_opportunities(conn)[0]
        self.assertEqual(len(op["tasks"]),2)
        self.assertEqual(op["tasks"][-1]["status"],"COMPLETE")
        result=self.post("/opportunities/"+oid+"/negotiations",{
            "revision":str(op["version"]),"kind":"ASKING_PRICE_CHANGED",
            "description":"Seller provided revised price in email",
            "source_reference":"owner-email-reference","amount":"90000",
            "occurred_on":"2026-09-26"})
        self.assertEqual(result.status_code,302)
        with connect(self.db) as conn: op=list_opportunities(conn)[0]
        self.assertEqual(op["asking_price"],"90000.00")
        self.assertEqual(op["analysis_state"],"STALE")
        self.assertFalse(op["negotiations"][-1]["transmitted_by_buybox"])
        result=self.post("/opportunities/"+oid+"/decision-note",{
            "revision":str(op["version"]),"reason":"Ownership verification remains pending."})
        self.assertEqual(result.status_code,302)
        with connect(self.db) as conn: op=list_opportunities(conn)[0]
        self.assertFalse(op["decisions"][-1]["authorizes_purchase"])

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
