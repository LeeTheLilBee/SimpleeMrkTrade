"""SC005B synthetic durable backup ambiguity and signed reconcile regressions.

No real provider, hardware, key, Tower signer, Vault registry or document.
"""
import hashlib
import os
import sqlite3

import pytest

from simplee_cloud.contracts import AccessDenied, CloudError, IntegrityError, ObjectMissing
from simplee_cloud.tests.test_sc004b_bound_port import Harness, PEER


class AcceptBackupThenTimeout:
    def __init__(self, *, store_before_error=True):
        self.rows = {}
        self.calls = 0
        self.store_before_error = store_before_error

    def put_if_absent(self, namespace, ref, body):
        self.calls += 1
        if self.store_before_error:
            self.rows[(namespace, ref)] = body
        raise OSError("backup provider lost ACK")

    def get(self, namespace, ref):
        try:
            return self.rows[(namespace, ref)]
        except KeyError as exc:
            raise ObjectMissing("physical backup not found") from exc


def primary(h):
    return h.port.write(
        grant=h.grant("write-1", "WRITE_CIPHERTEXT"),
        authenticated_transport_peer=PEER,
        request_id="write-1", envelope=h.data,
    )


def create(h):
    return h.port.create_encrypted_backup(
        grant=h.grant("backup-1", "BACKUP_CIPHERTEXT"),
        authenticated_transport_peer=PEER, request_id="backup-1",
    )


def reconcile(h, **changes):
    return h.port.reconcile_original_backup(
        grant=h.grant("backup-1", "RECONCILE_BACKUP", **changes),
        authenticated_transport_peer=PEER, original_request_id="backup-1",
    )


def backup_intent(h):
    scope = h.source._gate(
        h.port._invocation(
            grant=h.grant("probe-1", "BACKUP_CIPHERTEXT"),
            authenticated_transport_peer=PEER, request_id="probe-1",
            operation="BACKUP_CIPHERTEXT",
        ).context,
        "BACKUP_CIPHERTEXT",
    )
    return h.journal.backup_intent(namespace=scope, request_id="backup-1")


def test_successful_backup_one_object_idempotent_and_verified(tmp_path):
    h = Harness(tmp_path)
    primary(h)
    first = create(h)
    assert create(h) == first
    assert h.journal.health()["backup_count"] == 1
    assert h.journal.health()["pending_backups"] == 0
    assert h.journal.verify_chain()["valid"] is True
    assert h.journaled_backup.health()["production_authorized"] is False
    h.receipts["verify-1"] = first
    evidence = h.port.verify_backup_copy(
        grant=h.grant("verify-1", "VERIFY_BACKUP",
                      ref=first.backup_ref, digest=first.backup_sha256),
        authenticated_transport_peer=PEER, request_id="verify-1",
    )
    assert evidence.verified_ciphertext
    assert evidence.vault_original_authenticated is False


def test_provider_accepts_backup_but_ack_lost_reconcile_never_reput(tmp_path):
    h = Harness(tmp_path)
    primary(h)
    provider = AcceptBackupThenTimeout()
    h.backup.backup_backend = provider
    with pytest.raises(OSError, match="lost ACK"):
        create(h)
    intent = backup_intent(h)
    assert intent["state"] == "BACKUP_UNCERTAIN"
    assert len(intent["backup_ref"]) == len("backups/") + 48
    assert h.journal.health()["pending_backups"] == 1
    with pytest.raises(CloudError, match="unresolved"):
        create(h)
    assert provider.calls == 1
    result = reconcile(h)
    assert result["status"] == "PRESENT_INTERNAL_BACKUP_ONLY"
    assert result["vault_backup_committed"] is False
    assert result["backup_receipt"].backup_ref == intent["backup_ref"]
    assert h.journal.health()["pending_backups"] == 0
    assert create(h) == result["backup_receipt"]
    assert provider.calls == 1


def test_provider_missing_and_corrupt_are_terminal_holds(tmp_path):
    for fault in ("missing", "corrupt"):
        h = Harness(tmp_path / fault)
        primary(h)
        provider = AcceptBackupThenTimeout(store_before_error=fault == "corrupt")
        h.backup.backup_backend = provider
        with pytest.raises(OSError):
            create(h)
        intent = backup_intent(h)
        if fault == "corrupt":
            provider.rows[(intent["namespace_digest"], intent["backup_ref"])] = (
                b"SCB1" + os.urandom(intent["backup_size"] - 4)
            )
        result = reconcile(h)
        assert result["status"] == (
            "BACKUP_MISSING_HOLD" if fault == "missing" else "BACKUP_CORRUPT_HOLD"
        )
        assert result["backup_receipt"] is None
        assert result["vault_backup_committed"] is False
        assert h.journal.health()["backup_missing_or_corrupt"] == 1
        with pytest.raises(CloudError, match="unresolved"):
            create(h)
        assert provider.calls == 1


def test_acknowledged_backup_tampering_is_durable_incident(tmp_path):
    h = Harness(tmp_path)
    primary(h)
    receipt = create(h)
    target = h.backup_backend.root / receipt.namespace_digest / "backups" / (
        receipt.backup_ref.split("/")[1]
    )
    target.write_bytes(b"SCB1" + os.urandom(target.stat().st_size - 4))
    with pytest.raises(IntegrityError, match="missing or corrupted"):
        create(h)
    assert h.journal.health()["backup_missing_or_corrupt"] == 1
    assert h.journal.health()["incident_count"] == 1
    assert h.journal.verify_chain()["valid"] is True


def test_ack_journal_outage_preserves_reserved_intent_then_recovers(tmp_path):
    h = Harness(tmp_path)
    primary(h)
    original = h.journal.backup_transition

    def fail_ack(*, namespace, request_id, next_state):
        if next_state == "BACKUP_ACKNOWLEDGED":
            raise OSError("journal sync unavailable")
        return original(namespace=namespace, request_id=request_id,
                        next_state=next_state)

    h.journal.backup_transition = fail_ack
    with pytest.raises(OSError, match="journal sync"):
        create(h)
    h.journal.backup_transition = original
    assert backup_intent(h)["state"] == "BACKUP_RESERVED"
    result = reconcile(h)
    assert result["status"] == "PRESENT_INTERNAL_BACKUP_ONLY"


def test_signed_backup_reconciliation_cannot_redirect_source(tmp_path):
    h = Harness(tmp_path)
    primary(h)
    provider = AcceptBackupThenTimeout()
    h.backup.backup_backend = provider
    with pytest.raises(OSError):
        create(h)
    alternative = h.source.new_object_ref()
    with pytest.raises(AccessDenied, match="durable backup intent"):
        reconcile(h, ref=alternative)
    assert h.journal.health()["pending_backups"] == 1
    assert provider.calls == 1


def test_backup_intents_append_only_and_no_production_default(tmp_path):
    h = Harness(tmp_path)
    primary(h)
    receipt = create(h)
    with sqlite3.connect(h.journal.path) as conn:
        with pytest.raises(sqlite3.IntegrityError, match="append-only"):
            conn.execute("UPDATE backup_intents SET backup_sha256=?", ("0" * 64,))
        with pytest.raises(sqlite3.IntegrityError, match="append-only"):
            conn.execute("DELETE FROM backup_intents")
    status = str(h.journaled_backup.health())
    assert receipt.backup_ref not in status
    assert "trust" not in status
    assert h.journaled_backup.health()["status"] == "SOURCE_ONLY_NO_GO"
