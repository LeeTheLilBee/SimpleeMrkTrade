"""SC013 provider outage incident taxonomy, no false missing/corrupt terminal state.

Everything is synthetic: no network, actual vendor, Tower signer, live scan,
production alert delivery or real records. Opaque incident fields only.
"""
import os
import sqlite3

import pytest

from simplee_cloud.contracts import AccessDenied, CloudError, IntegrityError
from simplee_cloud.tests.test_sc004b_bound_port import Harness, PEER, AcceptThenTimeout
from simplee_cloud.tests.test_sc005b_backup_operations import AcceptBackupThenTimeout


SECRET = "synthetic-do-not-record-provider-exception-secret"


class UnavailableRead:
    def __init__(self, backend):
        self.backend = backend
        self.get_calls = 0
        self.put_calls = 0

    def get(self, namespace, ref):
        self.get_calls += 1
        raise OSError(SECRET)

    def put_if_absent(self, namespace, ref, body):
        self.put_calls += 1
        return self.backend.put_if_absent(namespace, ref, body)


def write(h, request="write-1"):
    return h.port.write(
        grant=h.grant(request, "WRITE_CIPHERTEXT"),
        authenticated_transport_peer=PEER, request_id=request, envelope=h.data,
    )


def backup(h, request="backup-1"):
    return h.port.create_encrypted_backup(
        grant=h.grant(request, "BACKUP_CIPHERTEXT"),
        authenticated_transport_peer=PEER, request_id=request,
    )


def reconcile_write(h, request="write-1"):
    return h.port.reconcile_original_write(
        grant=h.grant(request, "RECONCILE_WRITE"),
        authenticated_transport_peer=PEER, original_request_id=request,
    )


def reconcile_backup(h, request="backup-1"):
    return h.port.reconcile_original_backup(
        grant=h.grant(request, "RECONCILE_BACKUP"),
        authenticated_transport_peer=PEER, original_request_id=request,
    )


def read(h, request="read-1"):
    return h.port.read_encrypted(
        grant=h.grant(request, "READ_CIPHERTEXT"),
        authenticated_transport_peer=PEER, request_id=request,
    )


def redacted(h, expected_code):
    health = h.journal.health()
    assert health["backend_error_events"] >= 1
    assert health["provider_incident_delivery_certified"] is False
    assert health["external_checkpoint_certified"] is False
    assert h.journal.verify_chain()["valid"] is True
    with sqlite3.connect(h.journal.path) as db:
        codes = [row[0] for row in db.execute("SELECT incident_code FROM incidents")]
        assert expected_code in codes
        raw_rows = repr(db.execute("SELECT * FROM incidents").fetchall())
        raw_events = repr(db.execute("SELECT * FROM events").fetchall())
    assert SECRET not in raw_rows and SECRET not in raw_events
    assert "trust" not in raw_rows and "trust" not in raw_events
    assert h.port.health()["production_authorized"] is False


def test_primary_encrypted_read_provider_outage_is_separate_from_corruption(tmp_path):
    h = Harness(tmp_path)
    write(h)
    unavailable = UnavailableRead(h.source._backend)
    h.source._backend = unavailable
    with pytest.raises(OSError, match=SECRET):
        read(h)
    assert unavailable.get_calls == 1
    assert h.journal.health()["missing_or_corrupt"] == 0
    assert h.journal.health()["write_count"] == 1
    redacted(h, "PRIMARY_READ_BACKEND_ERROR")


def test_acknowledged_primary_replay_provider_outage_keeps_durable_ack(tmp_path):
    h = Harness(tmp_path)
    receipt = write(h)
    h.source._backend = UnavailableRead(h.source._backend)
    with pytest.raises(OSError, match=SECRET):
        write(h)
    scope = receipt.namespace_digest
    assert h.journal.intent(namespace=scope, request_id="write-1")["state"] == "WRITE_ACKNOWLEDGED"
    assert h.journal.health()["missing_or_corrupt"] == 0
    assert h.journal.health()["pending_writes"] == 0
    assert h.source._backend.put_calls == 0
    redacted(h, "PRIMARY_REPLAY_BACKEND_ERROR")


def test_pending_primary_reconciliation_outage_remains_pending_no_put(tmp_path):
    provider = AcceptThenTimeout()
    h = Harness(tmp_path, primary=provider)
    with pytest.raises(OSError, match="ack lost"):
        write(h)
    assert provider.put_calls == 1

    def offline(namespace, ref):
        raise OSError(SECRET)
    provider.get = offline
    with pytest.raises(OSError, match=SECRET):
        reconcile_write(h)
    assert provider.put_calls == 1
    assert h.journal.health()["pending_writes"] == 1
    assert h.journal.health()["missing_or_corrupt"] == 0
    redacted(h, "PRIMARY_RECONCILE_BACKEND_ERROR")


def test_first_backup_source_read_outage_creates_no_backup_intent(tmp_path):
    h = Harness(tmp_path)
    write(h)
    h.source._backend = UnavailableRead(h.source._backend)
    with pytest.raises(OSError, match=SECRET):
        backup(h)
    assert h.journal.health()["backup_count"] == 0
    assert h.journal.health()["missing_or_corrupt"] == 0
    redacted(h, "BACKUP_SOURCE_BACKEND_ERROR")


def test_acknowledged_backup_replay_outage_never_marks_backup_corrupt(tmp_path):
    h = Harness(tmp_path)
    write(h)
    receipt = backup(h)
    unavailable = UnavailableRead(h.backup.backup_backend)
    h.backup.backup_backend = unavailable
    with pytest.raises(OSError, match=SECRET):
        backup(h)
    assert unavailable.get_calls == 1
    assert unavailable.put_calls == 0
    saved = h.journal.backup_intent(
        namespace=receipt.namespace_digest, request_id="backup-1",
    )
    assert saved["state"] == "BACKUP_ACKNOWLEDGED"
    assert h.journal.health()["backup_missing_or_corrupt"] == 0
    redacted(h, "BACKUP_REPLAY_BACKEND_ERROR")


def test_pending_backup_reconcile_outage_never_misclassified_as_missing(tmp_path):
    h = Harness(tmp_path)
    write(h)
    provider = AcceptBackupThenTimeout()
    h.backup.backup_backend = provider
    with pytest.raises(OSError, match="lost ACK"):
        backup(h)
    assert provider.calls == 1

    def offline(namespace, ref):
        raise OSError(SECRET)
    provider.get = offline
    with pytest.raises(OSError, match=SECRET):
        reconcile_backup(h)
    assert provider.calls == 1
    assert h.journal.health()["pending_backups"] == 1
    assert h.journal.health()["backup_missing_or_corrupt"] == 0
    redacted(h, "BACKUP_RECONCILE_BACKEND_ERROR")


def test_isolated_backup_verification_outage_records_safe_incident_not_success(tmp_path):
    h = Harness(tmp_path)
    write(h)
    receipt = backup(h)
    h.receipts["verify-1"] = receipt
    h.backup.backup_backend = UnavailableRead(h.backup.backup_backend)
    with pytest.raises(OSError, match=SECRET):
        h.port.verify_backup_copy(
            grant=h.grant(
                "verify-1", "VERIFY_BACKUP",
                ref=receipt.backup_ref, digest=receipt.backup_sha256,
            ),
            authenticated_transport_peer=PEER, request_id="verify-1",
        )
    assert h.journal.health()["backup_missing_or_corrupt"] == 0
    redacted(h, "BACKUP_VERIFY_BACKEND_ERROR")


def test_bad_grant_does_not_get_classified_as_provider_outage(tmp_path):
    h = Harness(tmp_path)
    write(h)
    with pytest.raises(AccessDenied):
        h.port.read_encrypted(
            grant=h.grant("read-1", "READ_CIPHERTEXT"),
            authenticated_transport_peer=object(), request_id="read-1",
        )
    assert h.journal.health()["backend_error_events"] == 0
    assert h.journal.health()["incident_count"] == 0
    assert h.journal.verify_chain()["valid"] is True


def test_cannot_forge_unrecognized_provider_incident_code(tmp_path):
    h = Harness(tmp_path)
    with pytest.raises(CloudError, match="classification"):
        h.journal.record_backend_incident(
            namespace="a" * 64, request_id="some-request",
            code="PRODUCTION_APPROVED",
        )
    assert h.journal.health()["backend_error_events"] == 0
