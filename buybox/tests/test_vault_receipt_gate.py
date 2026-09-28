"""BBX106: authenticated Vault receipt acceptance remains exact-source and nonexecuting."""
import unittest
from datetime import datetime, timezone

from buybox.core import add_evidence,new_opportunity
from buybox.evidence import artifact_descriptor
from buybox.store import connect,save
from buybox.tower_evidence import freeze_local_evidence_snapshot,make_tower_metadata_draft
from buybox.vault_receipt_gate import VaultReceiptError,record_authenticated_archival_receipt
from buybox.external_proof_gate import integration_readiness

NOW=datetime(2026,9,28,15,30,tzinfo=timezone.utc)

class VaultReceiptGateTests(unittest.TestCase):
    def setUp(self):
        self.db=connect()
        op=new_opportunity("atm","Archive candidate",95000)
        artifact=artifact_descriptor(b"%PDF-1.7\\nEvidence\\n%%EOF",filename="source.pdf",mime="application/pdf",storage_reference="private-local",source_party="Seller")
        op["artifacts"]=[artifact]
        evidence=add_evidence(op,"ownership_documents","RECEIVED",reference=artifact["id"],source="Seller")
        evidence["artifact_id"]=artifact["id"]
        self.op=save(self.db,op,event_type="OpportunityCreated")
        revised,snap=freeze_local_evidence_snapshot(self.op,evidence_id=evidence["id"],artifact_id=artifact["id"],actor_reference="local_owner")
        self.op=save(self.db,revised,event_type="LocalEvidenceSnapshotFrozen",expected_revision=self.op["version"])
        self.artifact=artifact; self.evidence=evidence; self.snap=snap
        self.packet=make_tower_metadata_draft(self.op,evidence_id=evidence["id"],artifact_id=artifact["id"],snapshot_id=snap["snapshot_id"],principal_ref="tower-principal",role="owner",entity_id="owner-entity",classification="CONFIDENTIAL",retention_policy_id="retention-1",redaction_profile_id="redaction-1",request_id="archive-request-1",idempotency_key="archive-request-1")
        self.response={"schema_version":"buybox.vault.evidence.v1","request_id":"archive-request-1","status":"ARCHIVED","reason_code":"ARCHIVED","evidence_id":evidence["id"],"vault_document_ref":"vault-document-1","vault_version_ref":"vault-version-1","archival_receipt_id":"vault-receipt-1","verified_sha256":artifact["sha256"],"decision_snapshot_id":snap["snapshot_id"]}

    def tearDown(self):self.db.close()

    def test_untrusted_response_cannot_be_recorded_without_trusted_verifier(self):
        with self.assertRaisesRegex(VaultReceiptError,"TRUSTED_VAULT"):
            record_authenticated_archival_receipt(self.db,self.op,packet=self.packet,raw_response=self.response,trusted_response_verifier=None,now_utc=NOW)

    def test_authenticated_exact_receipt_records_minimized_nonexecuting_proof(self):
        revised,record=record_authenticated_archival_receipt(self.db,self.op,packet=self.packet,raw_response=self.response,trusted_response_verifier=lambda raw:dict(raw),now_utc=NOW)
        self.assertEqual(record["receipt_ref"],"vault-receipt-1")
        self.assertEqual(record["verified_sha256"],self.artifact["sha256"])
        self.assertFalse(record["browser_supplied_authority"])
        self.assertFalse(record["authorizes_purchase"])
        self.assertFalse(record["authorizes_money"])
        report=integration_readiness(revised)
        self.assertNotIn("VAULT_CANONICAL_ARCHIVAL",report["missing"])
        self.assertIn("TELLER_MONEY_AND_MANAGEMENT",report["missing"])

    def test_digest_request_evidence_and_snapshot_mismatch_fail_closed(self):
        for changed in [
            {**self.response,"verified_sha256":"a"*64},
            {**self.response,"request_id":"other-request"},
            {**self.response,"evidence_id":"other-evidence"},
        ]:
            with self.subTest(changed=changed),self.assertRaises(VaultReceiptError):
                record_authenticated_archival_receipt(self.db,self.op,packet=self.packet,raw_response=changed,trusted_response_verifier=lambda raw:dict(raw),now_utc=NOW)
        no_snapshot={**self.op,"snapshots":[]}
        with self.assertRaisesRegex(VaultReceiptError,"FROZEN"):
            record_authenticated_archival_receipt(self.db,no_snapshot,packet=self.packet,raw_response=self.response,trusted_response_verifier=lambda raw:dict(raw),now_utc=NOW)

    def test_non_archived_status_never_counts(self):
        pending={"schema_version":"buybox.vault.evidence.v1","request_id":"archive-request-1","status":"PENDING","reason_code":"PENDING","evidence_id":self.evidence["id"],"decision_snapshot_id":self.snap["snapshot_id"]}
        with self.assertRaisesRegex(VaultReceiptError,"ARCHIVED"):
            record_authenticated_archival_receipt(self.db,self.op,packet=self.packet,raw_response=pending,trusted_response_verifier=lambda raw:dict(raw),now_utc=NOW)

if __name__=="__main__":
    unittest.main()
