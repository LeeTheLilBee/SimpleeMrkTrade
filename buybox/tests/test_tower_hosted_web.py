"""BBX017–021: hosted owner exchange is source-tested, not publicly deployed.

Fixtures impersonate a Tower signer/introspection and storage attestor ONLY in
these tests. None is a real provider, owner entitlement, hosted launch or
backup/restore certification. No secret or fake listing enters product data.
"""
from __future__ import annotations
import base64
import hashlib
import hmac
import json
import tempfile
import time
import unittest
from pathlib import Path

from cryptography.fernet import Fernet
from flask import session

from buybox.app import create_app
from buybox.tower_session_store import (
    create_owner_session, read_owner_session, revoke_owner_session,
)
from buybox.store import connect

ORIGIN="https://buybox.example.test"
TOWER_ORIGIN="https://tower.example.test"
WORKSPACE_ID="tea-dag3rfu1egvs73a6s72g"
SECRET="test-only-separate-handshake-key-1234567890-ABCDEF"

def claims(now,**changes):
    packet={
        "schema_version":"tower.buybox.owner.handoff.v1",
        "issuer":"tower","audience":"buybox-owner","purpose":"owner_entry",
        "handoff_id":"handoff_"+"a"*32,
        "tower_session_ref":"tower_session_"+"b"*32,
        "actor_ref":"actor_"+"c"*32,
        "entity_ref":"entity_"+"d"*32,
        "owner_entitlement_ref":"entitlement_"+"e"*32,
        "issued_at_epoch":now,"expires_at_epoch":now+60,
        "target_path":"/","return_path":"/tower/access-home",
    }
    packet.update(changes)
    return packet

def token(packet):
    body=base64.urlsafe_b64encode(
        json.dumps(packet,sort_keys=True,separators=(",",":")).encode()
    ).decode().rstrip("=")
    prefix="tbh1."+body
    sig=hmac.new(SECRET.encode(),prefix.encode(),hashlib.sha256).digest()
    return prefix+"."+base64.urlsafe_b64encode(sig).decode().rstrip("=")

class HostedWebTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.root=Path(self.temp.name)
        self.mount=self.root/"durable"
        self.mount.mkdir(mode=0o700)
        self.dbdir=self.mount/"db"
        self.dbdir.mkdir(mode=0o700)
        self.docs=self.mount/"originals"
        self.docs.mkdir(mode=0o700)
        self.dbpath=str(self.dbdir/"buybox.sqlite3")
        self.active=True
        self.now=int(time.time())
        self.data=claims(self.now)
        def verifier(**kwargs):
            if not self.active:
                return {"issuer":"tower","status":"REVOKED"}
            return {
                "issuer":"tower","status":"ACTIVE","app_id":"buybox",
                **kwargs,"step_up_active":True,"entitlement_active":True,
                "expires_at_epoch":int(time.time())+600,
            }
        self.config={
            "TESTING":True, "SECRET_KEY":"test-flask-key-1234567890-abcdefgh",
            "BUYBOX_SECRET_KEY":"test-flask-key-1234567890-abcdefgh",
            "BUYBOX_AUTH_MODE":"tower", "BUYBOX_PASSWORD_HASH":None,
            "BUYBOX_DB_PATH":self.dbpath,"BUYBOX_DOCS_DIR":str(self.docs),
            "BUYBOX_DOCUMENT_KEY":Fernet.generate_key().decode(),
            "BUYBOX_PUBLIC_ORIGIN":ORIGIN,"TOWER_PUBLIC_ORIGIN":TOWER_ORIGIN,
            "TOWER_BUYBOX_HANDOFF_SECRET":SECRET,
            "BUYBOX_DURABLE_MOUNT":str(self.mount),
            "BUYBOX_SECURE_COOKIE":"1","SESSION_COOKIE_SECURE":True,
            "BUYBOX_TEST_MOUNT_CHECK":lambda _path:True,
            "TOWER_SESSION_VERIFIER":verifier,
            "BUYBOX_STORAGE_ATTESTOR":lambda:{
                "status":"VERIFIED","workspace_id":WORKSPACE_ID,
                "mount":str(self.mount),"backup_restore_proven":True,
                "evidence_reference":"synthetic-test-only-not-provider-proof",
            },
        }
        self.app=create_app(self.config)
        self.client=self.app.test_client()

    def tearDown(self):
        self.temp.cleanup()

    def exchange(self,client=None, *, packet=None, origin=ORIGIN, content_type=None):
        client=client or self.client
        args={"base_url":ORIGIN,"headers":{"Origin":origin}}
        if content_type is not None: args["content_type"]=content_type
        return client.post("/tower/owner-exchange",
            data={"handoff":token(packet or self.data)},**args)

    def test_hosted_mode_blocks_direct_password_and_unverified_records(self):
        self.assertEqual(self.client.get("/",base_url=ORIGIN).status_code,403)
        self.assertEqual(self.client.get("/login",base_url=ORIGIN).status_code,404)
        self.assertEqual(self.client.get("/opportunities/unknown",base_url=ORIGIN).status_code,403)

    def test_hosted_boot_requires_real_adapter_injection(self):
        for key in ("TOWER_SESSION_VERIFIER","BUYBOX_STORAGE_ATTESTOR"):
            bad={**self.config,key:None}
            with self.subTest(missing=key):
                with self.assertRaises(RuntimeError):
                    create_app(bad)
        with self.assertRaises(RuntimeError):
            create_app({**self.config,"BUYBOX_PASSWORD_HASH":"not-permitted"})
        with self.assertRaises(RuntimeError):
            create_app({**self.config,"SESSION_COOKIE_SECURE":False})
        with self.assertRaises(RuntimeError):
            create_app({**self.config,"BUYBOX_TEST_MOUNT_CHECK":lambda _:False})
        with self.assertRaises(RuntimeError):
            create_app({**self.config,"BUYBOX_STORAGE_ATTESTOR":lambda:{
                "status":"PENDING","workspace_id":WORKSPACE_ID,
                "mount":str(self.mount),"backup_restore_proven":False,
                "evidence_reference":"test",
            }})

    def test_exact_origin_post_and_one_time_exchange(self):
        response=self.exchange()
        self.assertEqual(response.status_code,303)
        self.assertEqual(response.location,"/")
        cookie=response.headers.get("Set-Cookie","")
        self.assertIn("Secure",cookie)
        self.assertIn("HttpOnly",cookie)
        for key in ("tower_session_","actor_","entity_","entitlement_",token(self.data)):
            self.assertNotIn(key,cookie)
        self.assertEqual(self.client.get("/",base_url=ORIGIN).status_code,200)
        other=self.app.test_client()
        self.assertEqual(self.exchange(other).status_code,403)
        self.assertEqual(other.get("/",base_url=ORIGIN).status_code,403)
        with connect(self.dbpath) as conn:
            self.assertEqual(conn.execute(
                "SELECT count(*) FROM buybox_tower_consumed_handoffs").fetchone()[0],1)
            self.assertEqual(conn.execute(
                "SELECT count(*) FROM buybox_tower_owner_sessions").fetchone()[0],1)

    def test_origin_host_query_and_duplicate_fields_fail_closed(self):
        for origin in ("",TOWER_ORIGIN,"https://evil.example.test",ORIGIN+"/"):
            with self.subTest(origin=origin):
                self.assertEqual(self.exchange(origin=origin).status_code,403)
        response=self.client.post("/tower/owner-exchange?handoff=fake",
            base_url=ORIGIN,headers={"Origin":ORIGIN},
            data={"handoff":token(self.data)})
        self.assertEqual(response.status_code,403)
        response=self.client.post("/tower/owner-exchange",
            base_url=ORIGIN,headers={"Origin":ORIGIN},
            data={"handoff":[token(self.data),token(self.data)]})
        self.assertEqual(response.status_code,403)
        response=self.client.post("/tower/owner-exchange",
            base_url="http://buybox.example.test",headers={"Origin":ORIGIN},
            data={"handoff":token(self.data)})
        self.assertEqual(response.status_code,403)
        self.assertEqual(self.client.get("/",base_url=ORIGIN).status_code,403)

    def test_wrong_signature_expiry_and_live_revocation(self):
        wrong=self.exchange(packet=claims(self.now,audience="evil"))
        self.assertEqual(wrong.status_code,403)
        stale=self.exchange(packet=claims(self.now-120,expires_at_epoch=self.now-60))
        self.assertEqual(stale.status_code,403)
        self.assertEqual(self.exchange().status_code,303)
        self.active=False
        self.assertEqual(self.client.get("/",base_url=ORIGIN).status_code,403)
        with connect(self.dbpath) as conn:
            self.assertEqual(conn.execute(
                "SELECT COUNT(*) FROM buybox_tower_owner_sessions "
                "WHERE revoked_at_epoch IS NOT NULL").fetchone()[0],1)
        self.active=True
        self.assertEqual(self.client.get("/",base_url=ORIGIN).status_code,403)

    def test_signout_revokes_private_session_and_returns_to_tower(self):
        self.assertEqual(self.exchange().status_code,303)
        with self.client.session_transaction(base_url=ORIGIN) as sess:
            csrf=sess["csrf"]
        out=self.client.post("/logout",base_url=ORIGIN,
                             data={"csrf_token":csrf})
        self.assertEqual(out.status_code,303)
        self.assertEqual(out.location,TOWER_ORIGIN+"/tower/access-home")
        self.assertEqual(self.client.get("/",base_url=ORIGIN).status_code,403)
        with connect(self.dbpath) as conn:
            self.assertEqual(conn.execute(
                "SELECT COUNT(*) FROM buybox_tower_owner_sessions "
                "WHERE revoked_at_epoch IS NOT NULL").fetchone()[0],1)

    def test_private_handle_ledger_expiry_and_revocation(self):
        with connect(self.dbpath) as conn:
            c={"tower_session_ref":"tower-session-1","actor_ref":"actor-1",
                "entity_ref":"entity-1","owner_entitlement_ref":"entitlement-1"}
            handle=create_owner_session(conn,c,now_epoch=100,expires_at_epoch=200)
            self.assertEqual(read_owner_session(conn,handle,now_epoch=150),c)
            self.assertIsNone(read_owner_session(conn,handle,now_epoch=200))
            self.assertIsNone(read_owner_session(conn,"bad",now_epoch=101))
            self.assertTrue(revoke_owner_session(conn,handle,now_epoch=160))
            self.assertFalse(revoke_owner_session(conn,handle,now_epoch=161))
            self.assertIsNone(read_owner_session(conn,handle,now_epoch=170))

if __name__=="__main__": unittest.main()
