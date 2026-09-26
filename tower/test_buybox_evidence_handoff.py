from vault.test_buybox_evidence_handoff_contract import packet
from tower.buybox_evidence_handoff import prepare_buybox_evidence_handoff

def context():
    return dict(identity_verified=True, permission_verified=True, entity_verified=True, purpose_verified=True, classification_verified=True, retention_verified=True, redaction_verified=True, approval_verified=True, principal_ref="tower-principal", entity_id="entity-1")

def test_missing_tower_gate_denied():
    c = context()
    c["approval_verified"] = False
    assert prepare_buybox_evidence_handoff(packet(), tower_context=c)["status"] == "DENIED"

def test_cross_entity_denied():
    c = context()
    c["entity_id"] = "other-entity"
    assert prepare_buybox_evidence_handoff(packet(), tower_context=c)["status"] == "DENIED"

def test_all_tower_gates_only_pending_not_archived():
    r = prepare_buybox_evidence_handoff(packet(), tower_context=context())
    assert r["status"] == "PENDING"
    assert r["reason_code"] == "CONTROLLED_TRANSFER_AND_SCAN_REQUIRED"
    assert "archival_receipt_id" not in r
    assert "vault_path" not in r
