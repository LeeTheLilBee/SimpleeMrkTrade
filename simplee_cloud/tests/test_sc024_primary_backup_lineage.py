"""SC024: first backup requires exact durably ACKed primary source lineage.

All identities, data and providers are local synthetic tests. This does not
prove a Vault canonical archive or a physically independent recovery domain.
"""
import hashlib
import os

import pytest

from simplee_cloud.contracts import CloudError
from simplee_cloud.service import namespace_digest
from simplee_cloud.tests.test_sc004b_bound_port import Harness, PEER, AcceptThenTimeout


class CountReads:
    def __init__(self, original):
        self.original = original
        self.get_calls = 0
        self.put_calls = 0

    def get(self, namespace, ref):
        self.get_calls += 1
        return self.original.get(namespace, ref)

    def put_if_absent(self, namespace, ref, body):
        self.put_calls += 1
        return self.original.put_if_absent(namespace, ref, body)


def backup(h, request="backup-1", *, entity="trust", ref=None, digest=None):
    return h.port.create_encrypted_backup(
        grant=h.grant(
            request, "BACKUP_CIPHERTEXT", entity=entity,
            ref=ref, digest=digest,
        ),
        authenticated_transport_peer=PEER, request_id=request,
    )


def write(h, request="write-1", *, entity="trust"):
    return h.port.write(
        grant=h.grant(request, "WRITE_CIPHERTEXT", entity=entity),
        authenticated_transport_peer=PEER, request_id=request,
        envelope=h.data,
    )


def test_raw_physically_present_object_without_journal_primary_cannot_start_backup(tmp_path):
    h = Harness(tmp_path)
    scope = namespace_digest("trust", namespace_key=h.source._namespace_key)
    # Model provider data added outside the Cloud journal. A raw GET alone
    # used to be sufficient to start a fresh backup.
    h.primary.put_if_absent(scope, h.ref, h.data)
    spy = CountReads(h.primary)
    h.source._backend = spy
    with pytest.raises(CloudError, match="acknowledged matching primary"):
        backup(h)
    assert spy.get_calls == 0
    assert h.journal.health()["backup_count"] == 0
    assert h.journal.health()["write_count"] == 0
    assert h.journal.source_backup_coverage()["production_authorized"] is False


def test_durable_reservation_itself_refuses_unacknowledged_source(tmp_path):
    h = Harness(tmp_path)
    scope = namespace_digest("trust", namespace_key=h.source._namespace_key)
    with pytest.raises(CloudError, match="acknowledged matching primary"):
        h.journal.reserve_backup(
            namespace=scope, request_id="manual-backup",
            source_object_ref=h.ref, source_digest=h.digest,
            backup_ref="backups/" + "a" * 48,
            backup_digest=hashlib.sha256(b"SCB1" + os.urandom(64)).hexdigest(),
            backup_size=68, key_reference="synthetic-key",
        )
    assert h.journal.health()["backup_count"] == 0


def test_primary_accepted_but_ack_lost_must_reconcile_original_before_backup(tmp_path):
    backend = AcceptThenTimeout()
    h = Harness(tmp_path, primary=backend)
    with pytest.raises(OSError, match="ack lost"):
        write(h)
    assert backend.put_calls == 1
    original_get = backend.get

    def forbidden_read(namespace, ref):
        raise AssertionError("unacknowledged primary must never be read to create backup")

    backend.get = forbidden_read
    with pytest.raises(CloudError, match="acknowledged matching primary"):
        backup(h)
    backend.get = original_get
    assert h.journal.health()["pending_writes"] == 1
    assert h.journal.health()["backup_count"] == 0
    assert backend.put_calls == 1
    reconciled = h.port.reconcile_original_write(
        grant=h.grant("write-1", "RECONCILE_WRITE"),
        authenticated_transport_peer=PEER,
        original_request_id="write-1",
    )
    assert reconciled["status"] == "PRESENT_INTERNAL_STORAGE_ONLY"
    assert reconciled["vault_archive_committed"] is False
    receipt = backup(h)
    assert receipt.source_ciphertext_sha256 == h.digest
    assert h.journal.health()["backup_count"] == 1
    assert backend.put_calls == 1


def test_canonical_grant_with_different_source_hash_cannot_backup_acked_primary(tmp_path):
    h = Harness(tmp_path)
    write(h)
    spy = CountReads(h.primary)
    h.source._backend = spy
    with pytest.raises(CloudError, match="acknowledged matching primary"):
        backup(h, digest="f" * 64)
    assert spy.get_calls == 0
    assert h.journal.health()["backup_count"] == 0


def test_other_namespace_raw_bytes_do_not_borrow_trust_primary_ack(tmp_path):
    h = Harness(tmp_path)
    write(h, entity="trust")
    foreign = namespace_digest(
        "different-entity", namespace_key=h.source._namespace_key,
    )
    h.primary.put_if_absent(foreign, h.ref, h.data)
    spy = CountReads(h.primary)
    h.source._backend = spy
    with pytest.raises(CloudError, match="acknowledged matching primary"):
        backup(h, entity="different-entity")
    assert spy.get_calls == 0
    assert h.journal.health()["backup_count"] == 0


def test_primary_integrity_hold_refuses_first_backup_even_if_physical_bytes_remain(tmp_path):
    h = Harness(tmp_path)
    first = write(h)
    h.journal.transition(
        namespace=first.namespace_digest, request_id="write-1",
        next_state="REPLAY_INTEGRITY_FAILURE",
    )
    spy = CountReads(h.primary)
    h.source._backend = spy
    with pytest.raises(CloudError, match="acknowledged matching primary"):
        backup(h)
    assert spy.get_calls == 0
    assert h.journal.health()["backup_count"] == 0
    assert h.journal.health()["missing_or_corrupt"] == 1


def test_reservation_rechecks_if_primary_enters_hold_between_preflight_and_put(tmp_path):
    h = Harness(tmp_path)
    first = write(h)
    original_read = h.source._read_verified

    def race_source_read(scope, ref, digest):
        data = original_read(scope, ref, digest)
        h.journal.transition(
            namespace=first.namespace_digest, request_id="write-1",
            next_state="REPLAY_INTEGRITY_FAILURE",
        )
        return data

    h.source._read_verified = race_source_read
    with pytest.raises(CloudError, match="acknowledged matching primary"):
        backup(h)
    assert h.journal.health()["backup_count"] == 0
    assert h.journal.health()["missing_or_corrupt"] == 1
    assert h.journal.verify_chain()["valid"] is True


def test_existing_acknowledged_backup_still_available_after_primary_later_enters_hold(tmp_path):
    h = Harness(tmp_path)
    first = write(h)
    receipt = backup(h)
    h.journal.transition(
        namespace=first.namespace_digest, request_id="write-1",
        next_state="REPLAY_INTEGRITY_FAILURE",
    )
    # Don't abandon an independently stored backup merely because the primary
    # was subsequently found bad; this is exact-ID idempotent backup replay.
    assert backup(h) == receipt
    assert h.journal.health()["backup_count"] == 1
    assert h.journal.verify_chain()["valid"] is True
