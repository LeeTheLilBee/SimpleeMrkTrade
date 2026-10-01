"""BBX131–135: Tower browser bootstrap preserves the strict owner exchange."""
from __future__ import annotations
import base64,hashlib,hmac,json,tempfile,time,unittest
from pathlib import Path

from cryptography.fernet import Fernet

from buybox.app import create_app

BUYBOX="https://buybox.example.test"
TOWER="https://tower.example.test"
SECRET="test-only-separate-handshake-key-1234567890-ABCDEF"
WORKSPACE="tea-dag3rfu1egvs73a6s72g"

def claims(now,**changes):
    value={
      "schema_version":"tower.buybox.owner.handoff.v1","issuer":"tower",
      "audience":"buybox-owner","purpose":"owner_entry",
      "handoff_id":"tower_buybox_"+"a"*32,
      "tower_session_ref":"tower_session_"+"b"*32,
      "actor_ref":"actor_"+"c"*32,"entity_ref":"entity_"+"d"*32,
      "owner_entitlement_ref":"entitlement_"+"e"*32,
      "issued_at_epoch":now,"expires_at_epoch":now+60,
      "target_path":"/","return_path":"/tower/access-home",
    }
    value.update(changes); return value

def signed(packet):
    raw=json.dumps(packet,sort_keys=True,separators=(",",":")).encode()
    body=base64.urlsafe_b64encode(raw).decode().rstrip("=")
    prefix="tbh1."+body
    mac=hmac.new(SECRET.encode(),prefix.encode(),hashlib.sha256).digest()
    return prefix+"."+base64.urlsafe_b64encode(mac).decode().rstrip("=")

class TowerBrowserBootstrapTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); root=Path(self.tmp.name); root.chmod(0o700)
        mount=root/"durable"; mount.mkdir(mode=0o700)
        dbdir=mount/"db"; dbdir.mkdir(mode=0o700)
        docs=mount/"originals"; docs.mkdir(mode=0o700)
        self.now=int(time.time())
        def verifier(**kwargs):
            return {"issuer":"tower","status":"ACTIVE","app_id":"buybox",**kwargs,
                    "step_up_active":True,"entitlement_active":True,
                    "expires_at_epoch":int(time.time())+600}
        self.app=create_app({
          "TESTING":True,"SECRET_KEY":"bootstrap-test-secret-1234567890",
          "BUYBOX_SECRET_KEY":"bootstrap-test-secret-1234567890",
          "BUYBOX_AUTH_MODE":"tower","BUYBOX_PASSWORD_HASH":None,
          "BUYBOX_DB_PATH":str(dbdir/"buybox.sqlite3"),"BUYBOX_DOCS_DIR":str(docs),
          "BUYBOX_DOCUMENT_KEY":Fernet.generate_key().decode(),
          "BUYBOX_PUBLIC_ORIGIN":BUYBOX,"TOWER_PUBLIC_ORIGIN":TOWER,
          "TOWER_BUYBOX_HANDOFF_SECRET":SECRET,"BUYBOX_DURABLE_MOUNT":str(mount),
          "BUYBOX_SECURE_COOKIE":"1","SESSION_COOKIE_SECURE":True,
          "BUYBOX_TEST_MOUNT_CHECK":lambda _:True,
          "TOWER_SESSION_VERIFIER":verifier,
          "BUYBOX_STORAGE_ATTESTOR":lambda:{
            "status":"VERIFIED","workspace_id":WORKSPACE,"mount":str(mount),
            "backup_restore_proven":True,"evidence_reference":"test-only"},
        })
        self.client=self.app.test_client()
        self.packet=claims(self.now); self.token=signed(self.packet)

    def tearDown(self): self.tmp.cleanup()

    def bootstrap(self,**kwargs):
        origin=kwargs.pop("origin",TOWER)
        data=kwargs.pop("data",{"handoff":self.token})
        return self.client.post("/tower/bootstrap",base_url=BUYBOX,
            headers={"Origin":origin},data=data,**kwargs)

    def test_exact_tower_post_yields_no_store_buybox_origin_bridge(self):
        r=self.bootstrap()
        self.assertEqual(r.status_code,200)
        self.assertIn(b'tower-buybox-bootstrap',r.data)
        self.assertIn(b'/tower/owner-exchange',r.data)
        self.assertIn(self.token.encode(),r.data)
        self.assertIn(b'tower_bootstrap.js',r.data)
        self.assertIn("no-store",r.headers.get("Cache-Control",""))
        self.assertNotIn("Set-Cookie",r.headers)
        self.assertIsNone(r.location)
        js=self.client.get("/buybox/static/tower_bootstrap.js",base_url=BUYBOX)
        self.assertNotIn(b"localStorage",js.data)
        self.assertNotIn(b"sessionStorage",js.data)
        self.assertNotIn(b"location",js.data)

    def test_bridge_preserves_original_same_origin_exchange(self):
        self.assertEqual(self.bootstrap().status_code,200)
        exchanged=self.client.post("/tower/owner-exchange",base_url=BUYBOX,
            headers={"Origin":BUYBOX},data={"handoff":self.token})
        self.assertEqual(exchanged.status_code,303)
        self.assertEqual(exchanged.location,"/")
        self.assertEqual(self.client.get("/",base_url=BUYBOX).status_code,200)

    def test_wrong_origin_query_duplicate_and_get_fail_closed(self):
        self.assertEqual(self.bootstrap(origin=BUYBOX).status_code,403)
        self.assertEqual(self.bootstrap(origin="https://evil.example").status_code,403)
        self.assertEqual(self.client.get("/tower/bootstrap",base_url=BUYBOX).status_code,405)
        q=self.client.post("/tower/bootstrap?handoff=x",base_url=BUYBOX,
            headers={"Origin":TOWER},data={"handoff":self.token})
        self.assertEqual(q.status_code,403)
        dup=self.bootstrap(data={"handoff":[self.token,self.token]})
        self.assertEqual(dup.status_code,403)

    def test_bad_signature_and_expired_token_fail_before_page_render(self):
        bad=self.token[:-1]+("A" if self.token[-1]!="A" else "B")
        self.assertEqual(self.bootstrap(data={"handoff":bad}).status_code,403)
        expired=signed(claims(self.now-120,expires_at_epoch=self.now-60))
        self.assertEqual(self.bootstrap(data={"handoff":expired}).status_code,403)

    def test_bootstrap_does_not_weaken_exchange_origin_rule(self):
        self.assertEqual(self.client.post("/tower/owner-exchange",base_url=BUYBOX,
            headers={"Origin":TOWER},data={"handoff":self.token}).status_code,403)

if __name__=="__main__": unittest.main()
