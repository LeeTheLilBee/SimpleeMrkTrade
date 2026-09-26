import copy
import pytest
from vault.buybox_evidence_handoff_contract import ContractError, validate_buybox_evidence_request, validate_tower_safe_response, request_fingerprint

def packet():
    return {
        "schema_version": "buybox.vault.evidence.v1", "request_id": "request-1", "idempotency_key": "request-1-v1",
        "source_app": "BUYBOX", "destination": "TOWER", "workflow_type": "acquisition_evidence_archive",
        "requested_operation": "PREPARE_ARCHIVAL",
        "requester": {"principal_ref": "tower-principal", "role": "owner", "entity_id": "entity-1", "purpose": "acquisition_due_diligence"},
        "acquisition": {"deal_id": "deal-1", "asset_type": "ATM_ROUTE", "evidence_id": "evidence-1", "decision_snapshot_id": "snapshot-1"},
        "document": {"source_document_id": "document-1", "source_version_id": "version-1", "original_document_ref": "opaque-1", "sha256": "a"*64, "byte_size": 10, "declared_mime_type": "application/pdf", "classification": "CONFIDENTIAL", "parent_version_id": None, "correction_of_version_id": None},
        "controls": {"malware_scan_required": True, "retention_policy_id": "retention-1", "redaction_profile_id": "redaction-1", "owner_approval_required": True, "requested_output": "ARCHIVAL_RECEIPT"},
        "transport": {"metadata_only": True, "raw_bytes_in_json": False, "public_url_requested": False, "direct_vault_access": False}
    }

def test_valid_metadata_only_and_stable_fingerprint():
    p = packet()
    assert validate_buybox_evidence_request(p) == p
    assert request_fingerprint(p) == request_fingerprint(copy.deepcopy(p))

@pytest.mark.parametrize("mutation", [
    lambda p: p.update(destination="VAULT"),
    lambda p: p["transport"].update(direct_vault_access=True),
    lambda p: p["transport"].update(raw_bytes_in_json=True),
    lambda p: p["controls"].update(malware_scan_required=False),
    lambda p: p["controls"].update(owner_approval_required=False),
    lambda p: p["document"].update(sha256="wrong"),
    lambda p: p["document"].update(original_document_ref="/data/vault/file"),
    lambda p: p["document"].update(byte_size=-1),
    lambda p: p["document"].update(correction_of_version_id="version-1"),
    lambda p: p.update(vault_path="/secret"),
    lambda p: p["requester"].update(purpose="unrelated"),
])
def test_fail_closed(mutation):
    p = packet()
    mutation(p)
    with pytest.raises(ContractError):
        validate_buybox_evidence_request(p)

def test_correction_preserves_version_reference():
    p = packet()
    p["document"].update(source_version_id="version-2", parent_version_id="version-1", correction_of_version_id="version-1", sha256="b"*64)
    assert validate_buybox_evidence_request(p)["document"]["correction_of_version_id"] == "version-1"

def test_archival_receipt_requires_verified_fields():
    r = {"schema_version": "buybox.vault.evidence.v1", "request_id": "request-1", "status": "ARCHIVED"}
    with pytest.raises(ContractError):
        validate_tower_safe_response(r)
    r.update(archival_receipt_id="receipt-1", vault_document_ref="document-1", vault_version_ref="version-1", verified_sha256="a"*64)
    assert validate_tower_safe_response(r)["status"] == "ARCHIVED"

def test_response_never_exposes_raw_location():
    r = {"schema_version": "buybox.vault.evidence.v1", "request_id": "request-1", "status": "PENDING", "vault_path": "/private"}
    with pytest.raises(ContractError):
        validate_tower_safe_response(r)
