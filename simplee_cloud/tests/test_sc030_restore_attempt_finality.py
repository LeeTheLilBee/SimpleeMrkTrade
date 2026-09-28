"""SC030: integrity-failed restore requests are final; outages are retryable.

All storage, Tower-shaped grants and Vault receipts are synthetic. This proves
source state-machine behavior only, not real DR, custody or production access.
"""
import sqlite3

import pytest

from simplee_cloud.contracts import CloudError, IntegrityError
from simplee_cloud.journal import _hash_event, _now, _request_tag
from simplee_cloud.tests.test_sc004b_bound_port import Harness, PEER


class CountGet:
    def __init__(self, actual):
        self.actual = actual
        self.calls = 0
    def get(self, namespace, ref):
        self.calls += 1
        return self.actual.get(namespace, ref)
    def put_if_absent(self, namespace, ref, body):
        return self.actual.put_if_absent(namespace, ref, body)


class OfflineGet:
    def __init__(self):
        self.calls = 0
    def get(self, namespace, ref):
        self.calls += 1
        raise OSError("synthetic backup provider unavailable")
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


def backup_path(h, receipt):
    return h.backup_backend.root / receipt.namespace_digest / receipt.backup_ref


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


def test_corrupt_restore_attempt_requires_fresh_request_after_bytes_are_repaired(tmp_path):
    h, receipt = prepared(tmp_path)
    path = backup_path(h, receipt)
    good = path.read_bytes()
    bad = good[:-1] + bytes([good[-1] ^ 1])
    path.write_bytes(bad)

    with pytest.raises(IntegrityError):
        verify(h, receipt, "restore-1")
    assert h.journal.health()["incident_count"] >= 1
    assert h.journal.verify_chain()["valid"] is True

    path.write_bytes(good)
    spy = CountGet(h.backup_backend)
    h.backup.backup_backend = spy
    with pytest.raises(CloudError, match="integrity hold; fresh authorization"):
        verify(h, receipt, "restore-1")
    assert spy.calls == 0

    evidence = verify(h, receipt, "restore-2")
    assert evidence.verified_ciphertext is True
    assert evidence.production_recovery_authorized is False
    assert spy.calls == 1


def test_missing_restore_attempt_also_closes_same_logical_request(tmp_path):
    h, receipt = prepared(tmp_path)
    path = backup_path(h, receipt)
    good = path.read_bytes()
    path.unlink()
    with pytest.raises(Exception):
        verify(h, receipt, "restore-missing")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(good)
    spy = CountGet(h.backup_backend)
    h.backup.backup_backend = spy
    with pytest.raises(CloudError, match="integrity hold; fresh authorization"):
        verify(h, receipt, "restore-missing")
    assert spy.calls == 0
    assert verify(h, receipt, "restore-new").verified_ciphertext is True


def test_provider_outage_does_not_permanently_poison_same_exact_restore_request(tmp_path):
    h, receipt = prepared(tmp_path)
    actual = h.backup_backend
    offline = OfflineGet()
    h.backup.backup_backend = offline
    with pytest.raises(OSError, match="provider unavailable"):
        verify(h, receipt, "restore-outage")
    assert offline.calls == 1
    with sqlite3.connect(h.journal.path) as db:
        codes = [
            row[0] for row in db.execute(
                "SELECT incident_code FROM incidents WHERE incident_code='BACKUP_VERIFY_BACKEND_ERROR'"
            )
        ]
    assert codes == ["BACKUP_VERIFY_BACKEND_ERROR"]

    spy = CountGet(actual)
    h.backup.backup_backend = spy
    evidence = verify(h, receipt, "restore-outage")
    assert evidence.verified_ciphertext is True
    assert spy.calls == 1
    assert h.journal.verify_chain()["valid"] is True


def test_completed_restore_request_cannot_repeat_provider_read(tmp_path):
    h, receipt = prepared(tmp_path)
    assert verify(h, receipt, "restore-once").verified_ciphertext is True
    spy = CountGet(h.backup_backend)
    h.backup.backup_backend = spy
    with pytest.raises(CloudError, match="already completed; new request"):
        verify(h, receipt, "restore-once")
    assert spy.calls == 0


def test_journal_api_refuses_success_after_integrity_incident_even_with_fake_crypto_event(tmp_path):
    h, receipt = prepared(tmp_path)
    h.journal.reserve_restore_verification(
        namespace=receipt.namespace_digest, request_id="restore-held",
        backup_ref=receipt.backup_ref, backup_sha256=receipt.backup_sha256,
        source_object_ref=receipt.source_object_ref,
        source_digest=receipt.source_ciphertext_sha256,
        key_reference=receipt.key_reference,
    )
    h.journal.record_backup_incident(
        namespace=receipt.namespace_digest, request_id="restore-held",
    )
    h.journal.record_safe_event({
        "event": "restore_copy_verified",
        "request_id": "restore-held",
        "tower_decision_ref": "tower-decision-1",
        "namespace_digest": receipt.namespace_digest,
    })
    with pytest.raises(IntegrityError, match="integrity hold forbids"):
        h.journal.record_restore_verified(
            namespace=receipt.namespace_digest, request_id="restore-held",
        )
    assert h.journal.verify_chain()["valid"] is True


def test_historical_integrity_failure_then_forged_success_is_detected(tmp_path):
    h, receipt = prepared(tmp_path)
    h.journal.reserve_restore_verification(
        namespace=receipt.namespace_digest, request_id="restore-history",
        backup_ref=receipt.backup_ref, backup_sha256=receipt.backup_sha256,
        source_object_ref=receipt.source_object_ref,
        source_digest=receipt.source_ciphertext_sha256,
        key_reference=receipt.key_reference,
    )
    h.journal.record_backup_incident(
        namespace=receipt.namespace_digest, request_id="restore-history",
    )
    h.journal.record_safe_event({
        "event": "restore_copy_verified",
        "request_id": "restore-history",
        "tower_decision_ref": "tower-decision-1",
        "namespace_digest": receipt.namespace_digest,
    })
    tag = _request_tag(receipt.namespace_digest, "restore-history")
    with sqlite3.connect(h.journal.path) as db:
        append_event(
            db, event="RESTORE_BOUND_VERIFIED", tag=tag,
            namespace=receipt.namespace_digest,
        )
    with pytest.raises(IntegrityError, match="prior integrity hold"):
        h.journal.verify_chain()


def test_historical_duplicate_bound_success_is_rejected(tmp_path):
    h, receipt = prepared(tmp_path)
    assert verify(h, receipt, "restore-success").verified_ciphertext is True
    tag = _request_tag(receipt.namespace_digest, "restore-success")
    with sqlite3.connect(h.journal.path) as db:
        append_event(
            db, event="RESTORE_BOUND_VERIFIED", tag=tag,
            namespace=receipt.namespace_digest,
        )
    with pytest.raises(IntegrityError, match="duplicate bound success"):
        h.journal.verify_chain()


def test_integrity_failure_for_one_restore_id_does_not_block_separate_restore_id(tmp_path):
    h, receipt = prepared(tmp_path)
    path = backup_path(h, receipt)
    good = path.read_bytes()
    path.write_bytes(good[:-1] + bytes([good[-1] ^ 1]))
    with pytest.raises(IntegrityError):
        verify(h, receipt, "restore-failed")
    path.write_bytes(good)
    assert verify(h, receipt, "restore-separate").verified_ciphertext is True
    assert h.port.health()["production_authorized"] is False
