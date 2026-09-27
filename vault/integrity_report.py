"""Internal entity-scoped integrity report; never a public route.

The canonical registry is authoritative for archived evidence. Journal state
alone is not archival proof. Tower must authorize the caller before presentation.
"""
from __future__ import annotations
import sqlite3
from vault.archival_transaction_journal import valid_id

def integrity_report(*,entity_id,journal,registry):
    valid_id(entity_id)
    with journal.db() as db:
        workflows=db.execute("SELECT request_id,evidence_id,version_id,state,registry_digest FROM workflows WHERE entity_id=? ORDER BY request_id",(entity_id,)).fetchall()
    with registry._db() as db:
        receipts=db.execute("SELECT request_id,evidence_id,version_id,receipt_id FROM archival_receipts WHERE entity_id=?",(entity_id,)).fetchall()
    canonical={r[0]:r for r in receipts}
    issues=[]
    for request,evidence,version,state,digest in workflows:
        actual=canonical.get(request)
        if not journal.verify_chain(request):
            issues.append({"request_id":request,"issue":"JOURNAL_INTEGRITY_FAILURE"})
        if state=="ARCHIVED":
            if not actual or actual[1:3]!=(evidence,version):
                issues.append({"request_id":request,"issue":"CANONICAL_RECEIPT_MISMATCH"})
            elif __import__("hashlib").sha256(actual[3].encode()).hexdigest()!=digest:
                issues.append({"request_id":request,"issue":"REGISTRY_DIGEST_MISMATCH"})
        elif actual:
            issues.append({"request_id":request,"issue":"REGISTRY_COMMITTED_JOURNAL_UNRESOLVED"})
        elif state=="RECONCILE_REQUIRED":
            issues.append({"request_id":request,"issue":"RECONCILIATION_REQUIRED"})
    journal_ids={r[0] for r in workflows}
    for request in canonical:
        if request not in journal_ids:issues.append({"request_id":request,"issue":"CANONICAL_RECEIPT_WITHOUT_JOURNAL"})
    return {"entity_id":entity_id,"workflow_counts":journal.owner_summary(entity_id),
            "canonical_receipt_count":len(receipts),"issues":issues,
            "integrity_ok":not issues}
