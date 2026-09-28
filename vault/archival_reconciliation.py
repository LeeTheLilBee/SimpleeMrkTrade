"""Explicit internal reconciliation of post-Cloud failures, not a scheduled service.

Only a trusted caller holding independently verified Cloud receipt and matching
canonical registry metadata may invoke this. No client-provided success flag.
"""
import hashlib
from vault.archival_transaction_journal import JournalError

class ReconciliationError(ValueError):pass

def reconcile_archival(*,journal,registry,store,verifier,request_id,entity_id):
    with journal.db() as db:
        row=db.execute("SELECT entity_id,evidence_id,version_id,state FROM workflows WHERE request_id=?",(request_id,)).fetchone()
    if not row or row[0]!=entity_id or row[3]!="RECONCILE_REQUIRED":
        raise ReconciliationError("not an entity-scoped reconciliation candidate")
    _,evidence,version,_=row
    with registry._db() as db:
        receipt=db.execute("""SELECT receipt_id,object_ref,ciphertext_sha256 FROM archival_receipts
            WHERE request_id=? AND entity_id=? AND evidence_id=? AND version_id=?""",
            (request_id,entity_id,evidence,version)).fetchone()
    if not receipt:raise ReconciliationError("canonical receipt absent; owner review required")
    receipt_id,ref,cipher_sha=receipt
    try:blob=store.get(ref)
    except (KeyError,FileNotFoundError) as exc:raise ReconciliationError("Cloud object absent") from exc
    if hashlib.sha256(blob).hexdigest()!=cipher_sha:
        raise ReconciliationError("Cloud ciphertext integrity failure")
    cloud_digest=verifier.verify_cloud(request_id=request_id,object_ref=ref,ciphertext_sha256=cipher_sha)
    if not isinstance(cloud_digest,str) or len(cloud_digest)!=64:
        raise ReconciliationError("invalid verified Cloud receipt")
    registry_digest=hashlib.sha256(receipt_id.encode()).hexdigest()
    if cloud_digest==registry_digest:raise ReconciliationError("non-distinct receipt evidence")
    journal.advance(request_id=request_id,expected_state="RECONCILE_REQUIRED",
        to_state="CLOUD_COMMITTED",receipt_digest=cloud_digest)
    journal.advance(request_id=request_id,expected_state="CLOUD_COMMITTED",
        to_state="ARCHIVED",receipt_digest=registry_digest)
    return receipt_id
