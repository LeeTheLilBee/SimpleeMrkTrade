"""SC006 actual Vault VLT1 envelope ↔ source-only Cloud contract regression.

All Tower signing keys, identities, Vault originals and backend bytes below
are random/synthetic. This proves only source compatibility, NOT a real
Tower/Vault/Cloud authenticated transport or production archival lifecycle.
"""
import hashlib
import os

import pytest

from simplee_cloud.contracts import (
    AccessDenied, CloudError, ObjectMissing, StorageContext,
)
from simplee_cloud.readiness import GATE_IDS, source_preflight
from simplee_cloud.service import CiphertextStorageService
from simplee_cloud.tests.test_sc004b_bound_port import Harness, PEER
from vault.real_operations_encrypted_storage import (
    MAX_ORIGINAL_BYTES, StorageError, decrypt_original, encrypt_original,
)


def vault_envelope(*, original=None, key=None, version="synthetic-version-1", entity="trust"):
    original = os.urandom(1536) if original is None else original
    key = os.urandom(32) if key is None else key
    result = encrypt_original(
        original, key=key, entity_id=entity,
        evidence_id="synthetic-evidence-1", version_id=version,
    )
    envelope, metadata = result
    return original, key, envelope, metadata


def configure(h, envelope, metadata):
    h.data = envelope
    h.digest = metadata["ciphertext_sha256"]
    assert hashlib.sha256(envelope).hexdigest() == h.digest


def write(h):
    return h.port.write(
        grant=h.grant("write-1", "WRITE_CIPHERTEXT"),
        authenticated_transport_peer=PEER,
        request_id="write-1", envelope=h.data,
    )


def read(h, req="read-1", entity="trust"):
    return h.port.read_encrypted(
        grant=h.grant(req, "READ_CIPHERTEXT", entity=entity),
        authenticated_transport_peer=PEER, request_id=req,
    )


def test_actual_vault_envelope_roundtrip_through_bound_cloud_and_backup(tmp_path):
    h = Harness(tmp_path)
    original, key, envelope, metadata = vault_envelope()
    configure(h, envelope, metadata)
    receipt = write(h)
    assert receipt.ciphertext_sha256 == metadata["ciphertext_sha256"]
    assert receipt.ciphertext_size == len(envelope)
    assert receipt.object_ref.startswith("objects/")
    assert read(h) == envelope

    # Decryption/authenticity of original is Vault-owned, NOT Cloud's job.
    assert decrypt_original(
        read(h, req="read-2"), key=key, entity_id="trust",
        evidence_id="synthetic-evidence-1",
        version_id="synthetic-version-1",
        expected_sha256=metadata["original_sha256"],
    ) == original

    backup = h.port.create_encrypted_backup(
        grant=h.grant("backup-1", "BACKUP_CIPHERTEXT"),
        authenticated_transport_peer=PEER, request_id="backup-1",
    )
    assert backup.source_ciphertext_sha256 == metadata["ciphertext_sha256"]
    h.receipts["verify-1"] = backup
    evidence = h.port.verify_backup_copy(
        grant=h.grant(
            "verify-1", "VERIFY_BACKUP",
            ref=backup.backup_ref, digest=backup.backup_sha256,
        ),
        authenticated_transport_peer=PEER, request_id="verify-1",
    )
    assert evidence.verified_ciphertext is True
    assert evidence.primary_rewritten is False
    assert evidence.vault_original_authenticated is False
    assert evidence.production_recovery_authorized is False
    # A separate Vault-side caller explicitly authenticates the encrypted copy.
    restored_vlt1 = h.backup.verify_restore_copy(
        context=StorageContext(
            request_id="isolated-verify", caller_service="archive_vault",
            tower_decision_ref="tower-decision-1", entity_id="trust",
            purpose="archive", operation="VERIFY_BACKUP",
        ),
        receipt=backup,
    )
    assert decrypt_original(
        restored_vlt1, key=key, entity_id="trust",
        evidence_id="synthetic-evidence-1",
        version_id="synthetic-version-1",
        expected_sha256=metadata["original_sha256"],
    ) == original
    assert h.port.health()["production_authorized"] is False


@pytest.mark.parametrize("changed", ["entity", "evidence", "version", "sha", "key"])
def test_vault_original_authentication_rejects_wrong_binding(tmp_path, changed):
    h = Harness(tmp_path)
    original, key, envelope, metadata = vault_envelope()
    configure(h, envelope, metadata)
    write(h)
    options = {
        "key": key, "entity_id": "trust",
        "evidence_id": "synthetic-evidence-1",
        "version_id": "synthetic-version-1",
        "expected_sha256": metadata["original_sha256"],
    }
    mutations = {
        "entity": ("entity_id", "another-entity"),
        "evidence": ("evidence_id", "synthetic-evidence-2"),
        "version": ("version_id", "synthetic-version-2"),
        "sha": ("expected_sha256", "0" * 64),
        "key": ("key", os.urandom(32)),
    }
    name, value = mutations[changed]
    options[name] = value
    with pytest.raises(StorageError):
        decrypt_original(read(h), **options)


def test_entity_separation_and_forged_canonical_vault_scope_fail_closed(tmp_path):
    h = Harness(tmp_path)
    original, key, envelope, metadata = vault_envelope()
    configure(h, envelope, metadata)
    write(h)
    with pytest.raises(CloudError, match="acknowledged matching primary"):
        read(h, req="foreign-read", entity="another-entity")
    grant = h.grant("wrong-scope-write", "WRITE_CIPHERTEXT")
    h.canonical[("wrong-scope-write", "WRITE_CIPHERTEXT")] = None
    with pytest.raises(AccessDenied):
        h.port.write(
            grant=grant, authenticated_transport_peer=PEER,
            request_id="wrong-scope-write", envelope=h.data,
        )
    assert h.journal.health()["write_count"] == 1


def test_vault_format_size_cap_and_ciphertext_hash_contract():
    original, key, envelope, metadata = vault_envelope()
    assert envelope.startswith(b"VLT1")
    assert len(envelope) == len(original) + 4 + 12 + 16
    assert len(envelope) <= 25 * 1024 * 1024 + 64
    assert hashlib.sha256(original).hexdigest() == metadata["original_sha256"]
    assert hashlib.sha256(envelope).hexdigest() == metadata["ciphertext_sha256"]
    with pytest.raises(StorageError):
        encrypt_original(
            b"", key=key, entity_id="trust", evidence_id="synthetic-evidence-1",
            version_id="synthetic-version-1",
        )
    with pytest.raises(StorageError):
        encrypt_original(
            b"x" * (MAX_ORIGINAL_BYTES + 1), key=key,
            entity_id="trust", evidence_id="synthetic-evidence-1",
            version_id="synthetic-version-1",
        )


def test_preflight_is_owner_readable_and_never_self_certifies():
    report = source_preflight()
    assert report["status"] == "SOURCE_ONLY_NO_GO"
    assert report["production_authorized"] is False
    assert report["release_decision_recorded"] is False
    assert report["independent_certifications"] == 0
    assert report["gate_count"] == len(GATE_IDS)
    assert "tower_real_issuer" in GATE_IDS
    assert "vault_canonical_registry" in GATE_IDS
    assert "owner_release" in GATE_IDS
    assert all(not x["independently_certified"] for x in report["gates"])
    pointers = {key: "review/reference-1" for key in GATE_IDS}
    report_with_pointers = source_preflight(pointers)
    assert report_with_pointers["review_references_present"] == len(GATE_IDS)
    assert report_with_pointers["independent_certifications"] == 0
    assert report_with_pointers["production_authorized"] is False
    assert report_with_pointers["hosted_receiver_enabled"] is False
    with pytest.raises(CloudError):
        source_preflight({"production_authorized": "true"})
    with pytest.raises(CloudError):
        source_preflight({"owner_release": "real-token\nsecret"})


def test_no_live_storage_unlocked_by_vault_compatibility(tmp_path):
    from simplee_cloud.local_backend import LocalPrivateCiphertextBackend
    with pytest.raises(CloudError, match="production storage not authorized"):
        CiphertextStorageService(
            backend=LocalPrivateCiphertextBackend(tmp_path / "private"),
            namespace_key=os.urandom(32), mode="production",
        )
