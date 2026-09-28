"""BBX101 web: integration readiness is protected, read-only, and never authority."""
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from cryptography.fernet import Fernet
from werkzeug.security import generate_password_hash

from buybox.app import create_app
from buybox.store import connect, load

class IntegrationReadinessWebTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        root=Path(self.temp.name); root.chmod(0o700)
        docs=root/"originals"; docs.mkdir(mode=0o700)
        self.dbpath=str(root/"buybox.sqlite3")
        self.app=create_app({
            "TESTING":True,"SECRET_KEY":"integration-test-secret",
            "BUYBOX_AUTH_MODE":"local",
            "BUYBOX_PASSWORD_HASH":generate_password_hash("local-test-password"),
            "BUYBOX_DB_PATH":self.dbpath,"BUYBOX_DOCS_DIR":str(docs),
            "BUYBOX_DOCUMENT_KEY":Fernet.generate_key().decode(),
            "SESSION_COOKIE_SECURE":False,
        })
        self.client=self.app.test_client()
        with self.client.session_transaction() as sess:sess["csrf"]="initial"
        self.client.post("/login",data={"csrf_token":"initial","password":"local-test-password"})
        with self.client.session_transaction() as sess:self.csrf=sess["csrf"]
        response=self.client.post("/opportunities",data={
            "csrf_token":self.csrf,"vertical":"atm","name":"Readiness candidate",
            "asking_price":"95000","city":"","region":"","source_url":""})
        self.oid=response.location.rsplit("/",1)[-1]

    def tearDown(self):self.temp.cleanup()

    def current(self):
        with connect(self.dbpath) as conn:return load(conn,self.oid)

    def test_readiness_page_is_read_only_and_explicitly_pending(self):
        before=self.current()
        page=self.client.get(f"/opportunities/{self.oid}/integration-readiness")
        self.assertEqual(page.status_code,200)
        self.assertIn(b"Protected Integration Readiness",page.data)
        self.assertIn(b"External proof pending",page.data)
        self.assertIn(b"Owner release is still required",page.data)
        after=self.current()
        self.assertEqual(before["version"],after["version"])
        self.assertFalse(after.get("external_proofs"))

    def test_anonymous_is_redirected_and_no_post_route_exists(self):
        anonymous=self.app.test_client()
        self.assertEqual(
            anonymous.get(f"/opportunities/{self.oid}/integration-readiness").status_code,302)
        self.assertEqual(
            self.client.post(f"/opportunities/{self.oid}/integration-readiness",
                             data={"csrf_token":self.csrf,"ready":"true"}).status_code,405)

if __name__=="__main__":
    unittest.main()
