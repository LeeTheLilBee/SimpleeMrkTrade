"""Proof contract compatibility with PR #35; no live Tower/Vault access."""
from __future__ import annotations
import copy
import importlib.util
import os
from pathlib import Path
import unittest

from buybox.core import add_evidence,new_opportunity
from buybox.evidence import artifact_descriptor
from buybox.tower_evidence import (
    freeze_local_evidence_snapshot,make_tower_metadata_draft,
    inspect_untrusted_response,HandoffPreparationError,SCHEMA_VERSION,
)

def opportunity_with_actual_original():
    op=new_opportunity("atm","Source-linked asset file")
    artifact=artifact_descriptor(b"%PDF-1.7\nEvidence\n%%EOF",
        filename="source.pdf",mime="application/pdf",
        storage_reference="private-encrypted-local-blob",source_party="Seller")
    op["artifacts"]=[artifact]
    evidence=add_evidence(op,"ownership_documents","RECEIVED",
                          reference=artifact["id"],source="Seller")
    evidence["artifact_id"]=artifact["id"]
    return op,artifact,evidence

def draft():
    op,artifact,evidence=opportunity_with_actual_original()
    op,snapshot=freeze_local_evidence_snapshot(op,evidence_id=evidence["id"],
        artifact_id=artifact["id"],actor_reference="local_owner")
    packet=make_tower_metadata_draft(op,evidence_id=evidence["id"],
        artifact_id=artifact["id"],snapshot_id=snapshot["snapshot_id"],
        principal_ref="tower-principal",role="owner",entity_id="owner-entity",
        classification="CONFIDENTIAL",retention_policy_id="pending-retention-policy",
        redaction_profile_id="pending-redaction-policy",
        request_id="buybox-evidence-request-1",idempotency_key="buybox-evidence-request-1")
    return op,artifact,evidence,snapshot,packet

class BuyBoxTowerEvidenceTests(unittest.TestCase):
    def test_draft_contains_no_original_bytes_or_storage_reference(self):
        op,artifact,evidence,snapshot,packet=draft()
        self.assertEqual(packet["source_app"],"BUYBOX")
        self.assertEqual(packet["destination"],"TOWER")
        self.assertEqual(packet["schema_version"],SCHEMA_VERSION)
        self.assertEqual(packet["document"]["sha256"],artifact["sha256"])
        self.assertEqual(packet["document"]["original_document_ref"],artifact["id"])
        self.assertEqual(packet["acquisition"]["decision_snapshot_id"],snapshot["snapshot_id"])
        self.assertTrue(packet["transport"]["metadata_only"])
        self.assertNotIn("storage_reference",str(packet))
        self.assertNotIn(artifact["storage_reference"],str(packet))
        self.assertFalse(snapshot["authorizes_action"])
        self.assertEqual(snapshot["archive_state"],"NOT_REQUESTED")

    def test_source_binding_required(self):
        op,artifact,evidence,snapshot,packet=draft()
        with self.assertRaisesRegex(HandoffPreparationError,"ARTIFACT_EVIDENCE_LINK_REQUIRED"):
            make_tower_metadata_draft(op,evidence_id=evidence["id"],
                artifact_id="another-file",snapshot_id=snapshot["snapshot_id"],
                principal_ref="tower-principal",role="owner",entity_id="owner-entity",
                classification="CONFIDENTIAL",retention_policy_id="retention-1",
                redaction_profile_id="redaction-1")
        altered=copy.deepcopy(op)
        altered["artifacts"][0]["sha256"]="f"*64
        with self.assertRaisesRegex(HandoffPreparationError,"SNAPSHOT_SOURCE_MISMATCH"):
            make_tower_metadata_draft(altered,evidence_id=evidence["id"],
                artifact_id=artifact["id"],snapshot_id=snapshot["snapshot_id"],
                principal_ref="tower-principal",role="owner",entity_id="owner-entity",
                classification="CONFIDENTIAL",retention_policy_id="retention-1",
                redaction_profile_id="redaction-1")

    def test_contract_excludes_csv_in_v1(self):
        op=new_opportunity("atm","CSV source")
        artifact=artifact_descriptor(b"month,value\n2026-01,1\n",filename="source.csv",
            mime="text/csv",storage_reference="private-opaque",source_party="Seller")
        op["artifacts"]=[artifact]
        evidence=add_evidence(op,"processor_statements",reference=artifact["id"],source="Seller")
        evidence["artifact_id"]=artifact["id"]
        with self.assertRaisesRegex(HandoffPreparationError,"MIME_NOT_IN_CANONICAL_CONTRACT"):
            freeze_local_evidence_snapshot(op,evidence_id=evidence["id"],
                artifact_id=artifact["id"],actor_reference="local_owner")

    def test_untrusted_archived_claim_cannot_activate_vault_status(self):
        _,artifact,evidence,snapshot,packet=draft()
        response={"schema_version":SCHEMA_VERSION,"request_id":packet["request_id"],
            "status":"ARCHIVED","archival_receipt_id":"receipt-1",
            "vault_document_ref":"vault-doc-1","vault_version_ref":"vault-version-1",
            "verified_sha256":artifact["sha256"],"evidence_id":evidence["id"]}
        checked=inspect_untrusted_response(packet,response)
        self.assertTrue(checked["correlated"])
        self.assertFalse(checked["authoritative"])
        self.assertFalse(checked["archived"])
        with self.assertRaisesRegex(HandoffPreparationError,"ARCHIVAL_DIGEST_MISMATCH"):
            inspect_untrusted_response(packet,{**response,"verified_sha256":"a"*64})
        with self.assertRaisesRegex(HandoffPreparationError,"RESPONSE_REQUEST_MISMATCH"):
            inspect_untrusted_response(packet,{**response,"request_id":"another-request"})
        with self.assertRaisesRegex(HandoffPreparationError,"UNSAFE_RESPONSE_FIELDS"):
            inspect_untrusted_response(packet,{**response,"vault_path":"/secret"})

    def test_upstream_pr35_exact_schema_compatibility(self):
        path=os.environ.get("BUYBOX_CANONICAL_CONTRACT_PATH")
        if not path:
            self.skipTest("Pinned PR #35 canonical validator is supplied by CI only")
        full=Path(path)
        self.assertTrue(full.is_file(),"Canonical contract checkout required in CI")
        spec=importlib.util.spec_from_file_location("canonical_pr35_buybox_evidence",full)
        module=importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        _,artifact,_,_,packet=draft()
        self.assertEqual(module.validate_buybox_evidence_request(packet),packet)
        self.assertEqual(module.request_fingerprint(packet),
                         module.request_fingerprint(copy.deepcopy(packet)))
        with self.assertRaises(module.ContractError):
            module.validate_buybox_evidence_request({
                **packet,"transport":{**packet["transport"],"direct_vault_access":True}})
        self.assertEqual(packet["document"]["sha256"],artifact["sha256"])

if __name__=="__main__":
    unittest.main()
