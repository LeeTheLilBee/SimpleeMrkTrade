"""VCR002–006: canonical Vault registry is compatible with Cloud internal refs only."""
from __future__ import annotations
import importlib.util
import sqlite3
import sys
from pathlib import Path
import pytest
from vault.canonical_evidence_registry import CanonicalEvidenceRegistry, RegistryError

CLOUD_CONTRACT = Path(__file__).resolve().parents[1] / "cloud-source" / "simplee_cloud" / "contracts.py"

def _values(**changes):
    row = {
        "receipt_id": "receipt-one", "request_id": "request-one",
        "entity_id": "entity-one", "evidence_id": "evidence-one",
        "version_id": "version-one", "original_sha256": "a" * 64,
        "ciphertext_sha256": "b" * 64, "object_ref": "objects/" + "1" * 48,
        "scan_receipt_ref": "scan-one", "tower_receipt_ref": "tower-one",
        "retention_policy_id": "retention-one",
    }
    row.update(changes)
    return row

def _pinned_cloud():
    assert CLOUD_CONTRACT.is_file(), "Independent Cloud SC001 checkout required"
    spec = importlib.util.spec_from_file_location("pinned_cloud_contract", CLOUD_CONTRACT)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module

def test_exact_cloud_and_vault_ref_interoperability(tmp_path):
    cloud = _pinned_cloud()
    ref = "objects/" + "f" * 48
    assert cloud.valid_object_ref(ref)
    reg = CanonicalEvidenceRegistry(tmp_path / "evidence.sqlite")
    assert reg.record_archival(**_values(object_ref=ref)) == "receipt-one"
    assert reg.redacted_receipt("receipt-one", "entity-one")["receipt_id"] == "receipt-one"
    assert reg.redacted_receipt("receipt-one", "entity-two") is None

@pytest.mark.parametrize("ref", [
    "object-one", "objects/not-hex", "objects/" + "A" * 48,
    "objects/" + "f" * 47, "objects/" + "f" * 49,
    "../objects/" + "1" * 48, "https://host/objects/" + "1" * 48,
    "file:///private", "backups/" + "1" * 48, "objects/" + "1" * 48 + "?token=1",
    True, None,
])
def test_invalid_internal_refs_fail_without_archival_row(tmp_path, ref):
    cloud = _pinned_cloud()
    assert not cloud.valid_object_ref(ref)
    reg = CanonicalEvidenceRegistry(tmp_path / "evidence.sqlite")
    with pytest.raises(RegistryError, match="internal ciphertext object reference"):
        reg.record_archival(**_values(object_ref=ref))
    with sqlite3.connect(reg.path) as db:
        assert db.execute("SELECT COUNT(*) FROM archival_receipts").fetchone()[0] == 0

def test_same_request_replay_is_exact_and_different_physical_ref_conflicts(tmp_path):
    reg = CanonicalEvidenceRegistry(tmp_path / "evidence.sqlite")
    packet = _values()
    assert reg.record_archival(**packet) == "receipt-one"
    assert reg.record_archival(**packet) == "receipt-one"
    with pytest.raises(RegistryError, match="conflicting request"):
        reg.record_archival(**_values(object_ref="objects/" + "2" * 48))
    with sqlite3.connect(reg.path) as db:
        assert db.execute("SELECT COUNT(*) FROM archival_receipts").fetchone()[0] == 1

def test_registry_is_not_storage_authorization_or_canonical_live_proof():
    source = Path(__file__).with_name("canonical_evidence_registry.py").read_text(encoding="utf-8")
    for forbidden in (
        "from simplee_cloud.", "from buybox.", "requests.post(",
        "verify_tower_token(", "put_if_absent(", "@app.route(",
    ):
        assert forbidden not in source
