"""SC031 owner-safe restore lifecycle metrics from one verified local snapshot."""
import json

import pytest

from simplee_cloud.contracts import IntegrityError
from simplee_cloud.owner_evidence_desk import owner_local_evidence_desk
from simplee_cloud.source_status import (
    owner_safe_source_markdown, owner_safe_source_snapshot,
)
from simplee_cloud.tests.test_sc004b_bound_port import Harness, PEER


class OfflineGet:
    def get(self, namespace, ref):
        raise OSError("synthetic provider unavailable")
    def put_if_absent(self, namespace, ref, body):
        raise AssertionError("restore must never PUT")


def prepared(tmp_path):
    h = Harness(tmp_path)
    h.port.write(
        grant=h.grant("write-1", "WRITE_CIPHERTEXT"),
        authenticated_transport_peer=PEER,
        request_id="write-1", envelope=h.data,
    )
    receipt = h.port.create_encrypted_backup(
        grant=h.grant("backup-1", "BACKUP_CIPHERTEXT"),
        authenticated_transport_peer=PEER, request_id="backup-1",
    )
    return h, receipt


def verify(h, receipt, request):
    h.receipts[request] = receipt
    return h.port.verify_backup_copy(
        grant=h.grant(
            request, "VERIFY_BACKUP",
            ref=receipt.backup_ref, digest=receipt.backup_sha256,
        ),
        authenticated_transport_peer=PEER, request_id=request,
    )


def path_for(h, receipt):
    return h.backup_backend.root / receipt.namespace_digest / receipt.backup_ref


def test_empty_snapshot_has_zero_restore_activity_and_never_claims_recovery(tmp_path):
    h = Harness(tmp_path)
    health = h.journal.health()
    assert health["restore_request_count"] == 0
    assert health["restore_completed_count"] == 0
    assert health["restore_integrity_hold_count"] == 0
    assert health["restore_pending_count"] == 0
    assert health["restore_retryable_outage_count"] == 0
    assert health["restore_physical_recovery_certified"] is False
    assert health["restore_vault_original_authenticated"] is False

    snapshot = owner_safe_source_snapshot(h.journal)
    assert snapshot["restore_request_count"] == 0
    assert snapshot["independent_recovery_certified"] is False
    assert snapshot["production_authorized"] is False


def test_successful_bound_restore_is_completed_not_pending(tmp_path):
    h, receipt = prepared(tmp_path)
    evidence = verify(h, receipt, "restore-ok")
    assert evidence.verified_ciphertext is True

    health = h.journal.health()
    assert health["restore_request_count"] == 1
    assert health["restore_completed_count"] == 1
    assert health["restore_pending_count"] == 0
    assert health["restore_integrity_hold_count"] == 0
    assert health["restore_retryable_outage_count"] == 0

    snapshot = owner_safe_source_snapshot(h.journal)
    assert snapshot["restore_completed_count"] == 1
    assert snapshot["restore_physical_recovery_certified"] is False
    assert snapshot["restore_vault_original_authenticated"] is False


def test_provider_outage_is_pending_and_retryable_then_clears_after_success(tmp_path):
    h, receipt = prepared(tmp_path)
    actual = h.backup_backend
    h.backup.backup_backend = OfflineGet()
    with pytest.raises(OSError, match="provider unavailable"):
        verify(h, receipt, "restore-outage")

    during = h.journal.health()
    assert during["restore_request_count"] == 1
    assert during["restore_completed_count"] == 0
    assert during["restore_pending_count"] == 1
    assert during["restore_pending_without_outage_count"] == 0
    assert during["restore_retryable_outage_count"] == 1
    assert during["restore_integrity_hold_count"] == 0
    assert during["restore_outage_incident_events"] == 1

    h.backup.backup_backend = actual
    assert verify(h, receipt, "restore-outage").verified_ciphertext is True
    after = h.journal.health()
    assert after["restore_completed_count"] == 1
    assert after["restore_pending_count"] == 0
    assert after["restore_retryable_outage_count"] == 0
    assert after["restore_outage_incident_events"] == 1


def test_corrupt_restore_is_owner_integrity_hold_not_generic_incident_double_count(tmp_path):
    h, receipt = prepared(tmp_path)
    path = path_for(h, receipt)
    body = path.read_bytes()
    path.write_bytes(body[:-1] + bytes([body[-1] ^ 1]))
    with pytest.raises(IntegrityError):
        verify(h, receipt, "restore-bad")

    health = h.journal.health()
    assert health["restore_request_count"] == 1
    assert health["restore_completed_count"] == 0
    assert health["restore_pending_count"] == 0
    assert health["restore_integrity_hold_count"] == 1
    assert health["restore_integrity_incident_events"] == 1

    snapshot = owner_safe_source_snapshot(h.journal)
    cards = snapshot["work_queue"]
    assert cards[0]["key"] == "restore_integrity"
    assert cards[0]["count"] == 1
    assert "fresh Tower/Vault restore authorization" in cards[0]["next_action"]
    assert not any(
        card["key"] == "other_incidents" and card["count"] == 1
        for card in cards
    )


def test_failed_restore_and_fresh_success_remain_two_distinct_owner_records(tmp_path):
    h, receipt = prepared(tmp_path)
    path = path_for(h, receipt)
    good = path.read_bytes()
    path.write_bytes(good[:-1] + bytes([good[-1] ^ 1]))
    with pytest.raises(IntegrityError):
        verify(h, receipt, "restore-failed")
    path.write_bytes(good)
    assert verify(h, receipt, "restore-new").verified_ciphertext is True

    health = h.journal.health()
    assert health["restore_request_count"] == 2
    assert health["restore_completed_count"] == 1
    assert health["restore_integrity_hold_count"] == 1
    assert health["restore_pending_count"] == 0


def test_owner_evidence_desk_includes_only_redacted_restore_counts(tmp_path):
    h, receipt = prepared(tmp_path)
    assert verify(h, receipt, "restore-ok").verified_ciphertext is True
    desk = owner_local_evidence_desk(
        journal=h.journal, replay_store=h.nonces,
    )
    local = desk["local_storage"]
    assert local["restore_request_count"] == 1
    assert local["restore_completed_count"] == 1
    assert local["restore_integrity_hold_count"] == 0
    assert local["restore_physical_recovery_certified"] is False
    assert local["restore_vault_original_authenticated"] is False
    wire = json.dumps(desk)
    for secret in (
        receipt.backup_ref, receipt.backup_sha256, receipt.source_object_ref,
        receipt.source_ciphertext_sha256, receipt.namespace_digest,
        receipt.key_reference, "trust",
    ):
        assert secret not in wire
    assert desk["production_authorized"] is False


def test_markdown_calls_restore_counts_source_verification_not_dr_certification(tmp_path):
    h, receipt = prepared(tmp_path)
    verify(h, receipt, "restore-ok")
    text = owner_safe_source_markdown(h.journal)
    assert "| Bound restore requests | 1 |" in text
    assert "| Completed source restore verifications | 1 |" in text
    assert "| Restore integrity holds | 0 |" in text
    assert "physical site-loss recovery are NOT certified" in text
    assert receipt.backup_ref not in text
