"""Private, durable Tower-owner session references.

Flask's signed cookie is NOT encrypted. It holds only a random opaque handle,
never Tower session, principal or entity references. Each protected request
loads the server-side binding and rechecks authenticated Tower truth.
"""
from __future__ import annotations
from hashlib import sha256
import json
import re
import secrets

HANDLE = re.compile(r"^[0-9a-f]{64}$")
CLAIMS = frozenset({"tower_session_ref","actor_ref","entity_ref","owner_entitlement_ref"})
MAX_SESSION_SECONDS = 15*60

def _digest(handle):
    if not isinstance(handle,str) or not HANDLE.fullmatch(handle):
        return None
    return sha256(handle.encode("ascii")).hexdigest()

def create_owner_session(db, claims, *, now_epoch, expires_at_epoch):
    if (not isinstance(claims,dict) or set(claims)!=CLAIMS
            or any(not isinstance(x,str) or not x for x in claims.values())
            or type(now_epoch) is not int or type(expires_at_epoch) is not int
            or not now_epoch<expires_at_epoch<=now_epoch+MAX_SESSION_SECONDS):
        raise ValueError("INVALID_TOWER_SESSION_BINDING")
    handle=secrets.token_hex(32)
    db.execute("""CREATE TABLE IF NOT EXISTS buybox_tower_owner_sessions (
        session_digest TEXT PRIMARY KEY,
        claims_json TEXT NOT NULL,
        issued_at_epoch INTEGER NOT NULL,
        expires_at_epoch INTEGER NOT NULL,
        revoked_at_epoch INTEGER
    )""")
    db.execute("INSERT INTO buybox_tower_owner_sessions VALUES (?,?,?,?,NULL)",
               (_digest(handle),json.dumps(claims,sort_keys=True,separators=(",",":")),
                now_epoch,expires_at_epoch))
    return handle

def read_owner_session(db, handle, *, now_epoch):
    digest=_digest(handle)
    if digest is None or type(now_epoch) is not int:
        return None
    row=db.execute("""SELECT claims_json,expires_at_epoch,revoked_at_epoch
        FROM buybox_tower_owner_sessions WHERE session_digest=?""",(digest,)).fetchone()
    if not row or row["revoked_at_epoch"] is not None or row["expires_at_epoch"]<=now_epoch:
        return None
    try:
        claims=json.loads(row["claims_json"])
    except (ValueError,TypeError):
        return None
    if not isinstance(claims,dict) or set(claims)!=CLAIMS:
        return None
    if any(not isinstance(v,str) or not v for v in claims.values()):
        return None
    return claims

def revoke_owner_session(db, handle, *, now_epoch):
    digest=_digest(handle)
    if digest is None or type(now_epoch) is not int:
        return False
    result=db.execute("""UPDATE buybox_tower_owner_sessions
        SET revoked_at_epoch=? WHERE session_digest=? AND revoked_at_epoch IS NULL""",
        (now_epoch,digest))
    return result.rowcount==1
