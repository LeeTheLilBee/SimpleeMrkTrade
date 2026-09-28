"""SC029: bound restore verification requires exact durable backup provenance."""
import hashlib
import os
import sqlite3
from dataclasses import replace

import pytest

from simplee_cloud.contracts import (
    BackupReceipt, CloudError, IntegrityError, StorageContext,
)
from simplee_cloud.journal import _hash_event, _now, _request_tag, _reservation_hash
from simplee_cloud.tests.test_sc004b_bound_port import Harness, PEER


class CountBackupGet:
    def __init__(self, actual):
        self.actual = actual
        self.get_calls = 0
        self.put_calls = 0
    def get(self, namespace, ref):
        self.get_calls += 1
        return self.actual.get(namespace, ref)
    def put_if_absent(self, namespace, ref, body):
        self.put_calls += 1
        return self.actual.put_if_absent(namespace, ref, body)


def write(h):
    return h.port.write(
        grant=h.grant("write-1", "WRITE_CIPHERTEXT"),
        authenticated_transport_peer=PEER,
        request_id="write-1", envelope=h.data,
    )


def backup(h, request="backup-1"):
    return h.port.create_encrypted_backup(
        grant=h.grant(request, "BACKUP_CIPHERTEXT"),
        authenticated_transport_peer=PEER, request_id=request,
    )


def verify(h, receipt, request="verify-1"):
    h.receipts[request] = receipt
    return h.port.verify_backup_copy(
        grant=h.grant(
            request, "VERIFY_BACKUP",
            ref=receipt.backup_ref, digest=receipt.backup_sha256,
        ),
        authenticated_transport_peer=PEER, request_id=request,
    )


def legacy_backup_context():
    return StorageContext(
        request_id="legacy-backup", caller_service="archive_vault",
        tower_decision_ref="tower-decision-1", entity_id="trust",
        purpose="archive", operation="BACKUP_CIPHERTEXT",
    )


def append_event(db, *, event, tag, namespace, code="-"):
    prior = db.execute(
        "SELECT seq,event_hash FROM events ORDER BY seq DESC LIMIT 1"
    ).fetchone()
    seq = 1 if prior is None else prior[0] + 1
    previous = "0" * 64 if prior is None else prior[1]
    at = _now()
    digest = _hash_event(seq, event, tag, namespace, code, at, previous)
    db.execute(
        "INSERT INTO events VALUES(?,?,?,?,?,?,?,?)",
        (seq, event, tag, namespace, code, at, previous, digest),
    )


def inject_restore(h, receipt, *, request="restore-old"):
    tag = _request_tag(receipt.namespace_digest, request)
    values = (
        tag, receipt.namespace_digest, receipt.backup_ref,
        receipt.backup_sha256, receipt.source_object_ref,
        receipt.source_ciphertext_sha256, receipt.key_reference, _now(),
    )
    with sqlite3.connect(h.journal.path) as db:
        db.execute("INSERT INTO restore_intents VALUES(?,?,?,?,?,?,?,?)", values)
        append_event(
            db, event="RESTORE_RESERVED", tag=tag,
            namespace=receipt.namespace_digest,
            code=_reservation_hash("RESTORE_RESERVED", values),
        )
    return tag


def test_canonical_physical_backup_without_cloud_backup_ack_denied_before_get(tmp_path):
    h = Harness(tmp_path)
    write(h)
    # Low-level primitive can create a physical backup for isolated crypto
    # testing, but it creates NO durable JournaledBackupOperations reservation.
    receipt = h.backup.create(
        context=legacy_backup_context(),
        source_object_ref=h.ref, source_ciphertext_sha256=h.digest,
    )
    spy = CountBackupGet(h.backup_backend)
    h.backup.backup_backend = spy
    h.receipts["verify-raw"] = receipt
    with pytest.raises(CloudError, match="acknowledged exact backup"):
        h.port.verify_backup_copy(
            grant=h.grant(
                "verify-raw", "VERIFY_BACKUP",
                ref=receipt.backup_ref, digest=receipt.backup_sha256,
            ),
            authenticated_transport_peer=PEER, request_id="verify-raw",
        )
    assert spy.get_calls == 0
    with sqlite3.connect(h.journal.path) as db:
        assert db.execute("SELECT COUNT(*) FROM restore_intents").fetchone()[0] == 0


def test_acknowledged_backup_restore_binds_exact_receipt_before_provider_and_success(tmp_path):
    h = Harness(tmp_path)
    write(h)
    receipt = backup(h)
    spy = CountBackupGet(h.backup_backend)
    h.backup.backup_backend = spy
    evidence = verify(h, receipt)
    assert evidence.verified_ciphertext is True
    assert evidence.production_recovery_authorized is False
    assert spy.get_calls == 1
    tag = _request_tag(receipt.namespace_digest, "verify-1")
    with sqlite3.connect(h.journal.path) as db:
        row = db.execute(
            """SELECT namespace_digest,backup_ref,backup_sha256,
                      source_object_ref,source_ciphertext_sha256,key_reference
               FROM restore_intents WHERE request_tag=?""", (tag,),
        ).fetchone()
        events = db.execute(
            "SELECT event_type FROM events WHERE request_tag=? ORDER BY seq",
            (tag,),
        ).fetchall()
    assert row == (
        receipt.namespace_digest, receipt.backup_ref, receipt.backup_sha256,
        receipt.source_object_ref, receipt.source_ciphertext_sha256,
        receipt.key_reference,
    )
    assert [x[0] for x in events][-4:] == [
        "RESTORE_RESERVED", "restore_verification_intent",
        "restore_copy_verified", "RESTORE_BOUND_VERIFIED",
    ]
    assert h.journal.verify_chain()["valid"] is True


def test_pending_backup_reservation_cannot_be_restored_even_with_forged_canonical_receipt(tmp_path):
    h = Harness(tmp_path)
    primary = write(h)
    backup_ref = "backups/" + "a" * 48
    backup_body = b"SCB1" + os.urandom(64)
    backup_sha = hashlib.sha256(backup_body).hexdigest()
    h.journal.reserve_backup(
        namespace=primary.namespace_digest, request_id="pending-backup",
        source_object_ref=h.ref, source_digest=h.digest,
        backup_ref=backup_ref, backup_digest=backup_sha,
        backup_size=len(backup_body), key_reference=h.backup.key_reference,
    )
    receipt = BackupReceipt(
        backup_ref, backup_sha, h.ref, h.digest,
        primary.namespace_digest, h.backup.key_reference,
    )
    spy = CountBackupGet(h.backup_backend)
    h.backup.backup_backend = spy
    with pytest.raises(CloudError, match="acknowledged exact backup"):
        verify(h, receipt, "verify-pending")
    assert spy.get_calls == 0


@pytest.mark.parametrize("field", ["source_sha", "source_ref", "key_reference"])
def test_canonical_receipt_cannot_borrow_different_backup_lineage(tmp_path, field):
    h = Harness(tmp_path)
    write(h)
    receipt = backup(h)
    changes = {}
    if field == "source_sha":
        changes["source_ciphertext_sha256"] = "f" * 64
    elif field == "source_ref":
        changes["source_object_ref"] = h.source.new_object_ref()
    else:
        changes["key_reference"] = "different-key-reference"
    forged = replace(receipt, **changes)
    spy = CountBackupGet(h.backup_backend)
    h.backup.backup_backend = spy
    with pytest.raises(CloudError, match="acknowledged exact backup"):
        verify(h, forged, "verify-forged")
    assert spy.get_calls == 0


def test_backup_integrity_hold_blocks_new_bound_restore_before_provider(tmp_path):
    h = Harness(tmp_path)
    write(h)
    receipt = backup(h)
    h.journal.backup_transition(
        namespace=receipt.namespace_digest, request_id="backup-1",
        next_state="BACKUP_REPLAY_INTEGRITY_FAILURE",
    )
    spy = CountBackupGet(h.backup_backend)
    h.backup.backup_backend = spy
    with pytest.raises(CloudError, match="acknowledged exact backup"):
        verify(h, receipt, "verify-after-hold")
    assert spy.get_calls == 0


def test_primary_later_enters_hold_but_prior_acknowledged_backup_remains_verifiable(tmp_path):
    h = Harness(tmp_path)
    primary = write(h)
    receipt = backup(h)
    h.journal.transition(
        namespace=primary.namespace_digest, request_id="write-1",
        next_state="REPLAY_INTEGRITY_FAILURE",
    )
    evidence = verify(h, receipt, "verify-after-primary-hold")
    assert evidence.verified_ciphertext is True
    assert evidence.primary_rewritten is False
    assert h.journal.health()["missing_or_corrupt"] == 1


def test_restore_request_id_cannot_rebind_to_second_backup(tmp_path):
    h = Harness(tmp_path)
    write(h)
    first = backup(h, "backup-1")
    second = backup(h, "backup-2")
    assert verify(h, first, "same-restore").verified_ciphertext is True
    h.receipts["same-restore"] = second
    with pytest.raises(CloudError, match="restore idempotency conflict"):
        h.port.verify_backup_copy(
            grant=h.grant(
                "same-restore", "VERIFY_BACKUP",
                ref=second.backup_ref, digest=second.backup_sha256,
            ),
            authenticated_transport_peer=PEER, request_id="same-restore",
        )


def test_historically_committed_restore_before_backup_ack_never_retroactively_valid(tmp_path):
    h = Harness(tmp_path)
    primary = write(h)
    backup_ref = "backups/" + "b" * 48
    backup_sha = hashlib.sha256(b"SCB1" + os.urandom(64)).hexdigest()
    h.journal.reserve_backup(
        namespace=primary.namespace_digest, request_id="backup-pending",
        source_object_ref=h.ref, source_digest=h.digest,
        backup_ref=backup_ref, backup_digest=backup_sha,
        backup_size=68, key_reference=h.backup.key_reference,
    )
    receipt = BackupReceipt(
        backup_ref, backup_sha, h.ref, h.digest,
        primary.namespace_digest, h.backup.key_reference,
    )
    inject_restore(h, receipt)
    # Model a legacy/self-consistent history that appended backup ACK AFTER
    # the invalid restore reservation. Current API correctly refuses to mutate
    # once verification detects the bad history, so inject only in this test.
    from simplee_cloud.journal import _backup_tag
    with sqlite3.connect(h.journal.path) as db:
        append_event(
            db, event="BACKUP_ACKNOWLEDGED",
            tag=_backup_tag(primary.namespace_digest, "backup-pending"),
            namespace=primary.namespace_digest,
        )
    with pytest.raises(IntegrityError, match="earlier acknowledged backup"):
        h.journal.verify_chain()


def test_forged_bound_restore_success_without_crypto_verification_event_fails_chain(tmp_path):
    h = Harness(tmp_path)
    write(h)
    receipt = backup(h)
    tag = inject_restore(h, receipt, request="forged-success")
    with sqlite3.connect(h.journal.path) as db:
        append_event(
            db, event="RESTORE_BOUND_VERIFIED", tag=tag,
            namespace=receipt.namespace_digest,
        )
    with pytest.raises(IntegrityError, match="encrypted-copy verification"):
        h.journal.verify_chain()


def test_tampered_restore_receipt_binding_denies_all_verified_journal_reads(tmp_path):
    h = Harness(tmp_path)
    write(h)
    receipt = backup(h)
    verify(h, receipt)
    with sqlite3.connect(h.journal.path) as db:
        db.execute("DROP TRIGGER restore_intents_block_update")
        db.execute("UPDATE restore_intents SET backup_sha256=?", ("f" * 64,))
    with pytest.raises(IntegrityError):
        h.journal.verify_chain()
    with pytest.raises(IntegrityError):
        h.journal.source_owner_metrics()


def test_low_level_crypto_restore_primitive_remains_available_for_isolated_tests(tmp_path):
    h = Harness(tmp_path)
    write(h)
    receipt = h.backup.create(
        context=legacy_backup_context(),
        source_object_ref=h.ref, source_ciphertext_sha256=h.digest,
    )
    isolated = StorageContext(
        request_id="isolated-low-level", caller_service="archive_vault",
        tower_decision_ref="tower-decision-1", entity_id="trust",
        purpose="archive", operation="VERIFY_BACKUP",
    )
    assert h.backup.verify_restore_copy(
        context=isolated, receipt=receipt,
    ) == h.data
    with sqlite3.connect(h.journal.path) as db:
        assert db.execute("SELECT COUNT(*) FROM restore_intents").fetchone()[0] == 0
    assert h.port.health()["production_authorized"] is False
