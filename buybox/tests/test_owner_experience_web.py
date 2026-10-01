"""BBX136–155 owner experience authenticated web regression."""
from __future__ import annotations
import tempfile,unittest
from pathlib import Path
from cryptography.fernet import Fernet
from werkzeug.security import generate_password_hash

from buybox.app import create_app
from buybox.owner_experience import preferences,latest_triage,acceptance_defects
from buybox.store import connect,load

class OwnerExperienceWebTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); root=Path(self.tmp.name); root.chmod(0o700)
        docs=root/"originals"; docs.mkdir(mode=0o700)
        self.dbpath=str(root/"buybox.sqlite3")
        self.app=create_app({"TESTING":True,"SECRET_KEY":"owner-experience-test",
          "BUYBOX_AUTH_MODE":"local","BUYBOX_PASSWORD_HASH":generate_password_hash("pw"),
          "BUYBOX_DB_PATH":self.dbpath,"BUYBOX_DOCS_DIR":str(docs),
          "BUYBOX_DOCUMENT_KEY":Fernet.generate_key().decode(),"SESSION_COOKIE_SECURE":False})
        self.client=self.app.test_client()
        with self.client.session_transaction() as s:s["csrf"]="initial"
        self.assertEqual(self.client.post("/login",data={"csrf_token":"initial","password":"pw"}).status_code,302)
        with self.client.session_transaction() as s:self.csrf=s["csrf"]
        r=self.post("/opportunities",{"vertical":"atm","name":"Griffin Route","asking_price":"95000","city":"Griffin","region":"GA","source_url":"https://example.com/deal"})
        self.oid=r.location.rsplit("/",1)[-1]

    def tearDown(self): self.tmp.cleanup()

    def post(self,path,data=None):
        return self.client.post(path,data={"csrf_token":self.csrf,**(data or {})})

    def test_shell_command_density_and_bulk_triage(self):
        home=self.client.get("/")
        self.assertIn(b"Acquisition pulse",home.data)
        self.assertIn(b"Search deals, places, evidence, notes",home.data)
        cmd=self.client.get("/command?q=Griffin")
        self.assertEqual(cmd.status_code,200); self.assertIn(b"Griffin Route",cmd.data)
        self.assertEqual(self.post("/owner-density",{"density":"CALM","return_to":"/"}).status_code,303)
        self.assertEqual(self.post("/bulk-triage",{"opportunity_id":self.oid,"state":"FOCUS","note":"Needs owner","return_to":"/"}).status_code,303)
        with connect(self.dbpath) as db:
            self.assertEqual(preferences(db)["density"],"CALM")
            self.assertEqual(latest_triage(db,self.oid)["state"],"FOCUS")

    def test_field_capture_can_become_task_but_not_evidence(self):
        r=self.post(f"/opportunities/{self.oid}/field",{"title":"Machine condition","note":"Owner observation only"})
        self.assertEqual(r.status_code,303)
        page=self.client.get(f"/opportunities/{self.oid}/field")
        self.assertIn(b"Owner observation only",page.data)
        with connect(self.dbpath) as db:
            rec=db.execute("SELECT id FROM buybox_intelligence_records WHERE opportunity_id=? AND kind='QUICK_CAPTURE'",(self.oid,)).fetchone()
        r=self.post(f"/opportunities/{self.oid}/field/{rec['id']}/follow-up",{"due_date":"2026-10-20"})
        self.assertEqual(r.status_code,303)
        with connect(self.dbpath) as db: op=load(db,self.oid)
        self.assertEqual(len(op.get("tasks",[])),1)
        self.assertEqual(len(op.get("evidence",[])),0)

    def test_provenance_cockpit_and_repaired_templates_render(self):
        prov=self.client.get(f"/opportunities/{self.oid}/provenance")
        self.assertEqual(prov.status_code,200); self.assertIn(b"WHY AM I SEEING THIS?",prov.data)
        cockpit=self.client.get("/integration-cockpit")
        self.assertIn(b"Tower protected action",cockpit.data)
        studio=self.client.get("/intelligence")
        self.assertIn(b"OPPORTUNITY INBOX",studio.data)
        dossier=self.client.get(f"/opportunities/{self.oid}")
        self.assertIn(b"SOULAANA CONTEXT RAIL",dossier.data)
        self.assertIn(b"Why am I seeing this?",dossier.data)

    def test_acceptance_defect_flow(self):
        page=self.client.get("/acceptance")
        self.assertIn(b"OWNER ACCEPTANCE MODE",page.data)
        r=self.post("/acceptance/defects",{"area":"Discover","severity":"BLOCKER","title":"Broken thing","detail":"Walkthrough defect"})
        self.assertEqual(r.status_code,303)
        with connect(self.dbpath) as db: defect=acceptance_defects(db)[0]
        self.assertEqual(defect["status"],"OPEN")
        self.assertEqual(self.post(f"/acceptance/defects/{defect['id']}/resolve").status_code,303)
        with connect(self.dbpath) as db: self.assertEqual(acceptance_defects(db)[0]["status"],"RESOLVED")

    def test_owner_surfaces_require_authentication(self):
        anon=self.app.test_client()
        for path in ("/command","/integration-cockpit","/acceptance",f"/opportunities/{self.oid}/field",f"/opportunities/{self.oid}/provenance"):
            with self.subTest(path=path): self.assertEqual(anon.get(path).status_code,302)

if __name__=="__main__": unittest.main()
