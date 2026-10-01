"""SC032 Vault retention/disposition source wall: review never equals Cloud delete."""
import inspect
import json
import sqlite3

import pytest

from simplee_cloud.bound_port import SourceOnlyBoundCloudPort
from simplee_cloud.contracts import CiphertextBackend, CloudError
from simplee_cloud.local_backend import LocalPrivateCiphertextBackend
from simplee_cloud.owner_evidence_desk import owner_local_evidence_desk
from simplee_cloud.retention_boundary import (
    TrustedVaultRetentionScope, source_retention_disposition_status,
)
from simplee_cloud.s3_backend import S3CompatibleCiphertextBackend
from simplee_cloud.service import CiphertextStorageService
from simplee_cloud.tests.test_sc004b_bound_port import Harness, PEER
from vault.canonical_evidence_registry import CanonicalEvidenceRegistry
from vault.retention_governance import GovernanceError, RetentionGovernance


def scope(*, hold=False, blocked=False, reviewed=False,
          archive_policy="retain-7", governance_policy="retain-7"):
    return TrustedVaultRetentionScope(
        version_id="version-1",
        object_ref="objects/" + "a" * 48,
        ciphertext_sha256="b" * 64,
        archival_retention_policy_id=archive_policy,
        governance_policy_id=governance_policy,
        legal_hold=hold,
        disposition_blocked=blocked,
        disposition_reviewed=reviewed,
    )


def test_retention_policy_match_or_hold_never_exposes_delete():
    report = source_retention_disposition_status(scope(blocked=True))
    assert report["status"] == "SOURCE_ONLY_RETENTION_HOLD"
    assert report["retention_policy_match"] is True
    assert report["cloud_delete_capability_exposed"] is False
    assert report["provider_delete_authorized"] is False
    assert report["backup_delete_authorized"] is False
    assert report["production_authorized"] is False


def test_completed_disposition_review_still_requires_separate_future_protocol():
    report = source_retention_disposition_status(
        scope(blocked=False, reviewed=True)
    )
    assert report["status"] == "SOURCE_ONLY_DISPOSITION_REVIEWED_NO_DELETE"
    assert report["disposition_reviewed"] is True
    assert report["future_separate_tower_vault_deletion_protocol_required"] is True
    assert report["owner_release_required"] is True
    assert report["cloud_delete_capability_exposed"] is False
    assert report["provider_delete_authorized"] is False
    assert report["vault_canonical_receipt_deleted"] is False


@pytest.mark.parametrize("bad", [
    scope(archive_policy="retain-7", governance_policy="retain-8"),
    scope(hold=True, blocked=False),
    scope(hold=True, blocked=True, reviewed=True),
    scope(blocked=True, reviewed=True),
])
def test_inconsistent_or_policy_mismatched_retention_scope_fails_closed(bad):
    with pytest.raises(CloudError):
        source_retention_disposition_status(bad)


def test_raw_mapping_or_invalid_object_binding_is_not_trusted():
    with pytest.raises(CloudError, match="trusted Vault retention scope"):
        source_retention_disposition_status({
            "disposition_reviewed": True,
            "provider_delete_authorized": True,
        })
    with pytest.raises(CloudError, match="object retention binding"):
        source_retention_disposition_status(
            TrustedVaultRetentionScope(
                version_id="version-1", object_ref="objects/not-valid",
                ciphertext_sha256="b" * 64,
                archival_retention_policy_id="retain-7",
                governance_policy_id="retain-7",
                legal_hold=False, disposition_blocked=False,
                disposition_reviewed=True,
            )
        )


def test_actual_vault_hold_release_and_disposition_review_do_not_delete_cloud_bytes(tmp_path):
    h = Harness(tmp_path / "cloud")
    receipt = h.port.write(
        grant=h.grant("write-1", "WRITE_CIPHERTEXT"),
        authenticated_transport_peer=PEER,
        request_id="write-1", envelope=h.data,
    )
    provider_path = h.primary.root / receipt.namespace_digest / receipt.object_ref
    before = provider_path.read_bytes()

    registry = CanonicalEvidenceRegistry(tmp_path / "vault" / "registry.sqlite")
    registry.record_archival(
        receipt_id="receipt-1", request_id="archive-1",
        entity_id="trust", evidence_id="evidence-1", version_id="version-1",
        original_sha256="c" * 64,
        ciphertext_sha256=receipt.ciphertext_sha256,
        object_ref=receipt.object_ref,
        scan_receipt_ref="scan-1", tower_receipt_ref="tower-1",
        retention_policy_id="retain-7",
    )
    governance = RetentionGovernance(tmp_path / "vault" / "retention.sqlite")
    governance.record(
        event_id="policy-1", entity_id="trust", version_id="version-1",
        action="POLICY_SET", policy_id="retain-7", reason="synthetic retention",
    )
    governance.record(
        event_id="hold-1", entity_id="trust", version_id="version-1",
        action="HOLD_PLACED", reason="synthetic preservation hold",
    )
    with pytest.raises(GovernanceError, match="blocks"):
        governance.record(
            event_id="review-held", entity_id="trust", version_id="version-1",
            action="DISPOSITION_REVIEWED", reason="must remain blocked",
        )
    held = governance.status(entity_id="trust", version_id="version-1")
    held_report = source_retention_disposition_status(
        TrustedVaultRetentionScope(
            version_id="version-1", object_ref=receipt.object_ref,
            ciphertext_sha256=receipt.ciphertext_sha256,
            archival_retention_policy_id="retain-7",
            governance_policy_id=held["policy_id"],
            legal_hold=held["legal_hold"],
            disposition_blocked=held["disposition_blocked"],
            disposition_reviewed=False,
        )
    )
    assert held_report["provider_delete_authorized"] is False
    assert provider_path.read_bytes() == before

    governance.record(
        event_id="release-1", entity_id="trust", version_id="version-1",
        action="HOLD_RELEASED", reason="synthetic hold released",
    )
    governance.record(
        event_id="review-1", entity_id="trust", version_id="version-1",
        action="DISPOSITION_REVIEWED", reason="synthetic review complete",
    )
    ready = governance.status(entity_id="trust", version_id="version-1")
    report = source_retention_disposition_status(
        TrustedVaultRetentionScope(
            version_id="version-1", object_ref=receipt.object_ref,
            ciphertext_sha256=receipt.ciphertext_sha256,
            archival_retention_policy_id="retain-7",
            governance_policy_id=ready["policy_id"],
            legal_hold=ready["legal_hold"],
            disposition_blocked=ready["disposition_blocked"],
            disposition_reviewed=True,
        )
    )
    assert report["status"] == "SOURCE_ONLY_DISPOSITION_REVIEWED_NO_DELETE"
    assert report["provider_delete_authorized"] is False
    assert provider_path.exists()
    assert provider_path.read_bytes() == before
    assert registry.redacted_receipt("receipt-1", "trust") is not None


def test_cloud_runtime_interfaces_expose_no_delete_operation():
    for cls in (
        CiphertextBackend, LocalPrivateCiphertextBackend,
        S3CompatibleCiphertextBackend, CiphertextStorageService,
        SourceOnlyBoundCloudPort,
    ):
        for name in ("delete", "delete_object", "remove", "unlink", "purge"):
            assert not hasattr(cls, name), (cls.__name__, name)
    assert "delete_object(" not in inspect.getsource(S3CompatibleCiphertextBackend)
    assert "delete" not in {
        name for name in dir(CiphertextStorageService)
        if not name.startswith("__")
    }


def test_owner_evidence_desk_never_implies_retention_delete_is_connected(tmp_path):
    h = Harness(tmp_path)
    desk = owner_local_evidence_desk(
        journal=h.journal, replay_store=h.nonces,
    )
    assert desk["retention_deletion_protocol_connected"] is False
    assert desk["cloud_delete_capability_exposed"] is False
    assert desk["provider_delete_authorized"] is False
    assert desk["production_authorized"] is False


def test_retention_report_is_redacted_of_canonical_identifiers():
    original = scope(blocked=False, reviewed=True)
    wire = json.dumps(source_retention_disposition_status(original))
    for secret in (
        original.version_id, original.object_ref, original.ciphertext_sha256,
        original.archival_retention_policy_id, original.governance_policy_id,
    ):
        assert secret not in wire


def test_vault_retention_event_history_remains_append_only(tmp_path):
    g = RetentionGovernance(tmp_path / "retention.sqlite")
    g.record(
        event_id="policy-1", entity_id="trust", version_id="version-1",
        action="POLICY_SET", policy_id="retain-7", reason="policy",
    )
    with sqlite3.connect(g.path) as db:
        with pytest.raises(sqlite3.IntegrityError):
            db.execute("DELETE FROM governance_events")
