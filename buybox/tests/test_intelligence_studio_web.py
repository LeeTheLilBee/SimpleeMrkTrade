"""BBX107-130 authenticated Intelligence Studio owner-flow regression."""
from __future__ import annotations
import tempfile,unittest
from pathlib import Path
from cryptography.fernet import Fernet
from werkzeug.security import generate_password_hash

from buybox.app import create_app
from buybox.expansion_store import load_thesis,records
from buybox.store import connect,load

class IntelligenceStudioWebTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); root=Path(self.tmp.name); root.chmod(0o700)
        docs=root/"originals"; docs.mkdir(mode=0o700)
        self.dbpath=str(root/"buybox.sqlite3")
        self.app=create_app({"TESTING":True,"SECRET_KEY":"intelligence-test",
            "BUYBOX_AUTH_MODE":"local","BUYBOX_PASSWORD_HASH":generate_password_hash("pw"),
            "BUYBOX_DB_PATH":self.dbpath,"BUYBOX_DOCS_DIR":str(docs),
            "BUYBOX_DOCUMENT_KEY":Fernet.generate_key().decode(),"SESSION_COOKIE_SECURE":False})
        self.client=self.app.test_client()
        with self.client.session_transaction() as s:s["csrf"]="initial"
        self.assertEqual(self.client.post("/login",data={"csrf_token":"initial","password":"pw"}).status_code,302)
        with self.client.session_transaction() as s:self.csrf=s["csrf"]
        r=self.post("/opportunities",{"vertical":"atm","name":"Route One","asking_price":"95000","city":"Griffin","region":"GA","source_url":""})
        self.assertEqual(r.status_code,302); self.oid=r.location.rsplit("/",1)[-1]

    def tearDown(self): self.tmp.cleanup()

    def post(self,path,data):
        return self.client.post(path,data={"csrf_token":self.csrf,**data})

    def test_portfolio_studio_renders_and_thesis_saves(self):
        page=self.client.get("/intelligence")
        self.assertEqual(page.status_code,200)
        self.assertIn(b"BUYBOX INTELLIGENCE STUDIO",page.data)
        r=self.post("/intelligence/thesis",{"priorities":"atm\nmultifamily","preferred_regions":"GA","avoid":"partner equity","sequence":"ATM first","notes":"Owner strategy"})
        self.assertEqual(r.status_code,303)
        with connect(self.dbpath) as db:
            thesis=load_thesis(db)
        self.assertEqual(thesis["priorities"],["atm","multifamily"])
        self.assertEqual(thesis["preferred_regions"],["GA"])

    def test_deal_studio_records_capex_capture_impact_team_and_actuals(self):
        for kind,data in [
          ("CAPEX_ITEM",{"title":"Replace cassette","severity":"MEDIUM","estimated_cost":"700","date":"2026-10-30","note":"Inspection note"}),
          ("QUICK_CAPTURE",{"title":"Site visit","note":"Observed owner-entered condition"}),
          ("COMMUNITY_IMPACT",{"dimension":"local jobs","note":"Potential hiring impact"}),
          ("TEAM_LANE",{"role":"Attorney","task":"Review assignment clause","status":"OPEN"}),
          ("PERFORMANCE_ACTUAL",{"period":"2027-Q1","actual_net":"12000","note":"Owner-entered operating actual"}),
          ("COUNTERPARTY",{"name":"Seller LLC","role":"seller","note":"Broker-introduced"}),
          ("MARKET_OBSERVATION",{"title":"Nearby vacancy note","source":"Owner field note","observed_on":"2026-09-28","note":"Not externally verified"}),
          ("AUTOPSY",{"outcome":"Still active","reason":"Testing learning record"}),
        ]:
            r=self.post(f"/opportunities/{self.oid}/intelligence/{kind}",data)
            self.assertEqual(r.status_code,303,kind)
        page=self.client.get(f"/opportunities/{self.oid}/intelligence")
        self.assertEqual(page.status_code,200)
        for text in (b"Replace cassette",b"Site visit",b"local jobs",b"Attorney",b"Seller LLC",b"Nearby vacancy note",b"Still active"):
            self.assertIn(text,page.data)
        with connect(self.dbpath) as db:
            rs=records(db,opportunity_id=self.oid)
        self.assertEqual(len(rs),8)

    def test_inbox_creates_provisional_owner_entered_opportunity(self):
        r=self.post("/intelligence/inbox",{"vertical":"business","title":"Inbox candidate","source_url":"https://example.com/listing","note":"Raw broker note only"})
        self.assertEqual(r.status_code,303)
        oid=r.location.rstrip("/").split("/")[-2]
        with connect(self.dbpath) as db: op=load(db,oid)
        self.assertEqual(op["lifecycle"],"DISCOVERED")
        self.assertEqual(op["sources"][0]["type"],"OWNER_INBOX")
        self.assertEqual(op["owner_notes"][0]["type"],"OPPORTUNITY_INBOX")

    def test_what_if_uses_saved_opportunities_without_claiming_capital(self):
        r=self.post("/opportunities",{"vertical":"multifamily","name":"Flats","asking_price":"250000","city":"Griffin","region":"GA","source_url":""})
        other=r.location.rsplit("/",1)[-1]
        result=self.post("/intelligence/what-if",{"opportunity_id":[self.oid,other]})
        self.assertEqual(result.status_code,200)
        self.assertIn(b"$345000.00",result.data)
        self.assertIn(b"Not assumed",result.data)

    def test_studio_is_authenticated_and_unknown_kind_denied(self):
        anon=self.app.test_client()
        self.assertEqual(anon.get("/intelligence").status_code,302)
        self.assertEqual(anon.get(f"/opportunities/{self.oid}/intelligence").status_code,302)
        self.assertEqual(self.post(f"/opportunities/{self.oid}/intelligence/FAKE",{"note":"x"}).status_code,400)

if __name__=="__main__":
    unittest.main()
