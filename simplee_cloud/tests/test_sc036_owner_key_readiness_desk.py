"""SC036 owner evidence desk optionally includes redacted key readiness."""
import json
import sqlite3

import pytest

from simplee_cloud.contracts import CloudError, IntegrityError
from simplee_cloud.owner_evidence_desk import owner_local_evidence_desk
from simplee_cloud.tests.test_sc004b_bound_port import Harness, PEER


def write_and_backup(h):
    h.port.write(
        grant=h.grant("write-1", "WRITE_CIPHERTEXT"),
        authenticated_transport_peer=PEER,
        request_id="write-1", envelope=h.data,
    )
    return h.port.create_encrypted_backup(
        grant=h.grant("backup-1", "BACKUP_CIPHERTEXT"),
        authenticated_transport_peer=PEER, request_id="backup-1",
    )


def desk(h, **kwargs):
    return owner_local_evidence_desk(
        journal=h.journal, replay_store=h.nonces, **kwargs,
    )


def test_key_readiness_not_supplied_is_explicitly_not_evaluated(tmp_path):
    h = Harness(tmp_path)
    report = desk(h)
    keys = report["backup_key_readiness"]
    assert keys["supplied"] is False
    assert keys["status"] == "NOT_EVALUATED"
    assert keys["acknowledged_backup_count"] is None
    assert keys["unavailable_key_reference_count"] is None
    assert keys["provider_bytes_read"] is False
    assert keys["external_kms_hsm_custody_certified"] is False
    assert keys["production_authorized"] is False


def test_fixed_acknowledged_backup_key_readiness_is_redacted_in_owner_desk(tmp_path):
    h = Harness(tmp_path)
    receipt = write_and_backup(h)
    report = desk(h, backup_operations=h.journaled_backup)
    keys = report["backup_key_readiness"]
    assert keys["supplied"] is True
    assert keys["status"] == "SOURCE_ONLY_KEY_REFERENCES_RESOLVABLE"
    assert keys["acknowledged_backup_count"] == 1
    assert keys["distinct_key_reference_count"] == 1
    assert keys["resolvable_key_reference_count"] == 1
    assert keys["unavailable_key_reference_count"] == 0
    assert keys["provider_bytes_read"] is False
    assert keys["backup_ciphertext_authenticated_in_this_check"] is False
    assert keys["external_kms_hsm_custody_certified"] is False
    assert report["production_authorized"] is False
    wire = json.dumps(report)
    for forbidden in (
        receipt.key_reference, receipt.backup_ref, receipt.backup_sha256,
        receipt.source_object_ref, receipt.source_ciphertext_sha256,
        receipt.namespace_digest, "trust",
    ):
        assert forbidden not in wire


def test_missing_fixed_historical_key_becomes_owner_hold_not_false_recovery(tmp_path):
    h = Harness(tmp_path)
    write_and_backup(h)
    h.backup._backup_key = None
    report = desk(h, backup_operations=h.journaled_backup)
    keys = report["backup_key_readiness"]
    assert keys["status"] == "SOURCE_ONLY_KEY_REFERENCE_HOLD"
    assert keys["acknowledged_backup_count"] == 1
    assert keys["resolvable_key_reference_count"] == 0
    assert keys["unavailable_key_reference_count"] == 1
    assert keys["acknowledged_backups_depending_on_unavailable_key_count"] == 1
    assert keys["old_key_recovery_drill_certified"] is False
    assert report["local_storage"]["matched_backup_ack_count"] == 1
    # Journal ACK and current key resolvability are deliberately different facts.
    assert report["production_authorized"] is False


def test_owner_desk_rejects_backup_operations_from_different_journal(tmp_path):
    h = Harness(tmp_path / "one")
    other = Harness(tmp_path / "two")
    with pytest.raises(CloudError, match="this verified Cloud journal"):
        desk(h, backup_operations=other.journaled_backup)


def test_owner_desk_rejects_non_backup_object_as_key_preflight(tmp_path):
    h = Harness(tmp_path)
    with pytest.raises(CloudError, match="backup key preflight"):
        desk(h, backup_operations=object())


def test_storage_journal_tamper_still_blocks_desk_before_key_readiness(tmp_path):
    h = Harness(tmp_path)
    write_and_backup(h)
    with sqlite3.connect(h.journal.path) as db:
        db.execute("DROP TRIGGER backup_intents_block_update")
        db.execute("UPDATE backup_intents SET key_reference=?", ("tampered-key",))
    with pytest.raises(IntegrityError):
        desk(h, backup_operations=h.journaled_backup)


def test_replay_ledger_tamper_still_blocks_desk_with_key_readiness(tmp_path):
    h = Harness(tmp_path)
    write_and_backup(h)
    with sqlite3.connect(h.nonces.path) as db:
        db.execute("DROP TRIGGER consumed_block_update")
        db.execute("UPDATE consumed SET expires_at=expires_at+1")
    with pytest.raises(Exception, match="replay rows differ"):
        desk(h, backup_operations=h.journaled_backup)
