"""SC027 signed Cloud reads require exact acknowledged journal primary provenance.

This guards the journaled/source bound port. Direct SC001 storage helpers are
legacy source-test primitives and NOT an approved production bypass.
"""
import sqlite3

import pytest

from simplee_cloud.contracts import CloudError, IntegrityError
from simplee_cloud.service import namespace_digest
from simplee_cloud.tests.test_sc004b_bound_port import Harness, PEER, AcceptThenTimeout


class CountOrForbidGet:
    def __init__(self, actual):
        self.actual = actual
        self.calls = 0

    def get(self, namespace, ref):
        self.calls += 1
        raise AssertionError("unacknowledged ciphertext must not reach provider GET")

    def put_if_absent(self, namespace, ref, body):
        return self.actual.put_if_absent(namespace, ref, body)


def write(h):
    return h.port.write(
        grant=h.grant("write-1", "WRITE_CIPHERTEXT"),
        authenticated_transport_peer=PEER, request_id="write-1", envelope=h.data,
    )


def read(h, request="read-1", *, entity="trust", ref=None, digest=None):
    return h.port.read_encrypted(
        grant=h.grant(
            request, "READ_CIPHERTEXT", entity=entity, ref=ref, digest=digest,
        ),
        authenticated_transport_peer=PEER, request_id=request,
    )


def test_physical_bytes_without_primary_journal_ack_do_not_enable_signed_read(tmp_path):
    h = Harness(tmp_path)
    scope = namespace_digest("trust", namespace_key=h.source._namespace_key)
    h.primary.put_if_absent(scope, h.ref, h.data)
    guard = CountOrForbidGet(h.primary)
    h.source._backend = guard
    with pytest.raises(CloudError, match="acknowledged matching primary"):
        read(h)
    assert guard.calls == 0
    assert h.journal.health()["write_count"] == 0
    assert h.journal.health()["incident_count"] == 0


def test_provider_accepted_primary_but_lost_ack_read_denied_until_original_reconciliation(
    tmp_path,
):
    backend = AcceptThenTimeout()
    h = Harness(tmp_path, primary=backend)
    with pytest.raises(OSError, match="ack lost"):
        write(h)
    assert backend.put_calls == 1
    original_get = backend.get
    backend.get = lambda namespace, ref: (_ for _ in ()).throw(
        AssertionError("read must not touch unresolved physical source")
    )
    with pytest.raises(CloudError, match="acknowledged matching primary"):
        read(h)
    backend.get = original_get
    result = h.port.reconcile_original_write(
        grant=h.grant("write-1", "RECONCILE_WRITE"),
        authenticated_transport_peer=PEER, original_request_id="write-1",
    )
    assert result["status"] == "PRESENT_INTERNAL_STORAGE_ONLY"
    assert result["vault_archive_committed"] is False
    assert read(h, "read-after-reconcile") == h.data
    assert backend.put_calls == 1


def test_wrong_signed_digest_and_cross_entity_raw_bytes_fail_before_provider_get(tmp_path):
    h = Harness(tmp_path)
    write(h)
    foreign_scope = namespace_digest(
        "different-entity", namespace_key=h.source._namespace_key,
    )
    h.primary.put_if_absent(foreign_scope, h.ref, h.data)
    guard = CountOrForbidGet(h.primary)
    h.source._backend = guard
    with pytest.raises(CloudError, match="acknowledged matching primary"):
        read(h, "wrong-digest", digest="f" * 64)
    with pytest.raises(CloudError, match="acknowledged matching primary"):
        read(h, "wrong-entity", entity="different-entity")
    with pytest.raises(CloudError, match="acknowledged matching primary"):
        read(h, "wrong-ref", ref=h.source.new_object_ref())
    assert guard.calls == 0
    assert h.journal.health()["incident_count"] == 0


def test_primary_integrity_hold_blocks_new_read_but_existing_backup_remains_recoverable(
    tmp_path,
):
    h = Harness(tmp_path)
    stored = write(h)
    receipt = h.port.create_encrypted_backup(
        grant=h.grant("backup-1", "BACKUP_CIPHERTEXT"),
        authenticated_transport_peer=PEER, request_id="backup-1",
    )
    h.journal.transition(
        namespace=stored.namespace_digest, request_id="write-1",
        next_state="REPLAY_INTEGRITY_FAILURE",
    )
    guard = CountOrForbidGet(h.primary)
    h.source._backend = guard
    with pytest.raises(CloudError, match="acknowledged matching primary"):
        read(h, "read-after-hold")
    assert guard.calls == 0
    h.receipts["verify-1"] = receipt
    recovery = h.port.verify_backup_copy(
        grant=h.grant(
            "verify-1", "VERIFY_BACKUP", ref=receipt.backup_ref,
            digest=receipt.backup_sha256,
        ),
        authenticated_transport_peer=PEER, request_id="verify-1",
    )
    assert recovery.verified_ciphertext is True
    assert recovery.primary_rewritten is False
    assert recovery.production_recovery_authorized is False


def test_tampered_journal_never_serves_even_matching_physical_ciphertext(tmp_path):
    h = Harness(tmp_path)
    write(h)
    with sqlite3.connect(h.journal.path) as db:
        db.execute("DROP TRIGGER intents_block_update")
        db.execute("UPDATE intents SET ciphertext_sha256=?", ("f" * 64,))
    guard = CountOrForbidGet(h.primary)
    h.source._backend = guard
    with pytest.raises(IntegrityError):
        read(h, "read-corrupt-journal")
    assert guard.calls == 0


def test_valid_acknowledged_source_read_still_works_and_no_live_release(tmp_path):
    h = Harness(tmp_path)
    write(h)
    assert read(h) == h.data
    assert h.journal.health()["write_count"] == 1
    assert h.port.health()["production_authorized"] is False
    assert h.port.health()["hosted_receiver_enabled"] is False
