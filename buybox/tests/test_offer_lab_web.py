"""BBX096 web proof: Offer Lab is an authenticated private analysis room only."""
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from cryptography.fernet import Fernet
from werkzeug.security import generate_password_hash

from buybox.app import create_app
from buybox.store import connect, load


class OfferLabWebTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        root=Path(self.temp.name); root.chmod(0o700)
        docs=root/"originals"; docs.mkdir(mode=0o700)
        self.dbpath=str(root/"buybox.sqlite3")
        self.app=create_app({"TESTING":True,"SECRET_KEY":"offer-lab-test-secret","BUYBOX_AUTH_MODE":"local","BUYBOX_PASSWORD_HASH":generate_password_hash("local-test-password"),"BUYBOX_DB_PATH":self.dbpath,"BUYBOX_DOCS_DIR":str(docs),"BUYBOX_DOCUMENT_KEY":Fernet.generate_key().decode(),"SESSION_COOKIE_SECURE":False})
        self.client=self.app.test_client()
        with self.client.session_transaction() as sess:sess["csrf"]="initial-csrf"
        self.assertEqual(self.client.post("/login",data={"csrf_token":"initial-csrf","password":"local-test-password"}).status_code,302)
        with self.client.session_transaction() as sess:self.csrf=sess["csrf"]
        created=self.post("/opportunities",{"vertical":"atm","name":"Private route candidate","asking_price":"100000","city":"","region":"","source_url":""})
        self.assertEqual(created.status_code,302)
        self.oid=created.location.rsplit("/",1)[-1]

    def tearDown(self):
        self.temp.cleanup()

    def post(self,path,data):
        return self.client.post(path,data={"csrf_token":self.csrf,**data})

    def current(self):
        with connect(self.dbpath) as conn:return load(conn,self.oid)

    def test_room_records_private_scenario_without_external_action(self):
        page=self.client.get(f"/opportunities/{self.oid}/offer-lab")
        self.assertEqual(page.status_code,200)
        self.assertIn(b"Offer Lab",page.data)
        before=self.current()
        response=self.post(f"/opportunities/{self.oid}/offer-lab/scenarios",{"revision":str(before["version"]),"name":"Private 90k scenario","proposed_purchase_price":"90000","earnest_money":"2500","requested_seller_credit":"3000","due_diligence_days":"21","financing_contingency":"on","planned_closing_date":"2026-10-30","financing_option_id":"","insurance_record_id":"","rationale":"Internal comparison only.","terms_note":"Do not transmit.","supersedes":"","correction_reason":""})
        self.assertEqual(response.status_code,303)
        current=self.current()
        self.assertEqual(current["lifecycle"],before["lifecycle"])
        self.assertEqual(len(current["offer_scenarios"]),1)
        record=current["offer_scenarios"][0]
        self.assertFalse(record["transmitted_to_seller"])
        self.assertFalse(record["authorizes_offer"])
        self.assertFalse(record["authorizes_purchase"])
        self.assertFalse(record["authorizes_money"])
        self.assertEqual(record["teller_readiness"],"UNKNOWN")
        rendered=self.client.get(f"/opportunities/{self.oid}/offer-lab")
        self.assertIn(b"Private 90k scenario",rendered.data)
        self.assertNotIn(b"Offer sent",rendered.data)

    def test_stale_revision_and_anonymous_access_fail_closed(self):
        revision=self.current()["version"]
        payload={"revision":str(revision),"name":"First","proposed_purchase_price":"90000","earnest_money":"0","requested_seller_credit":"0","due_diligence_days":"10","planned_closing_date":"2026-10-30","rationale":"private","terms_note":"","financing_option_id":"","insurance_record_id":"","supersedes":"","correction_reason":""}
        self.assertEqual(self.post(f"/opportunities/{self.oid}/offer-lab/scenarios",payload).status_code,303)
        stale=dict(payload,name="Stale",proposed_purchase_price="89000")
        self.assertEqual(self.post(f"/opportunities/{self.oid}/offer-lab/scenarios",stale).status_code,409)
        self.assertEqual(len(self.current()["offer_scenarios"]),1)
        anonymous=self.app.test_client()
        self.assertEqual(anonymous.get(f"/opportunities/{self.oid}/offer-lab").status_code,302)


if __name__=="__main__":
    unittest.main()
