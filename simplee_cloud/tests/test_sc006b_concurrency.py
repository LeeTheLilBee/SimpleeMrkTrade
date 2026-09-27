"""SC006B synthetic concurrent source authorization, primary and backup races.

Uses small local encrypted envelopes and a counting wrapper; never connects
Tower, Vault canonical runtime, a provider, hardware or production secrets.
"""
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier, Lock

import pytest

from simplee_cloud.contracts import AccessDenied, CloudError
from simplee_cloud.local_backend import LocalPrivateCiphertextBackend
from simplee_cloud.tests.test_sc004b_bound_port import Harness, PEER
from simplee_cloud.tests.test_sc005b_backup_operations import AcceptBackupThenTimeout


class CountingBackend:
    def __init__(self, backend):
        self.backend = backend
        self.put_calls = 0
        self._lock = Lock()

    def put_if_absent(self, namespace, ref, body):
        with self._lock:
            self.put_calls += 1
        return self.backend.put_if_absent(namespace, ref, body)

    def get(self, namespace, ref):
        return self.backend.get(namespace, ref)


def concurrent(workers, action):
    barrier = Barrier(workers)
    def run(index):
        barrier.wait()
        try:
            return ("ok", action(index))
        except Exception as exc:
            return ("blocked", exc)
    with ThreadPoolExecutor(max_workers=workers) as pool:
        return list(pool.map(run, range(workers)))


def test_same_signed_grant_concurrent_replay_consumes_only_once(tmp_path):
    h = Harness(tmp_path)
    signed = h.grant("one-write", "WRITE_CIPHERTEXT")
    records = concurrent(6, lambda _: h.port.write(
        grant=signed, authenticated_transport_peer=PEER,
        request_id="one-write", envelope=h.data,
    ))
    successes = [value for status, value in records if status == "ok"]
    errors = [value for status, value in records if status == "blocked"]
    assert len(successes) == 1
    assert len(errors) == 5
    assert all(isinstance(value, AccessDenied) for value in errors)
    assert h.nonces.count() == 1
    assert h.journal.health()["write_count"] == 1


def test_fresh_signed_grants_for_one_write_never_duplicate_physical_put(tmp_path):
    backend = CountingBackend(LocalPrivateCiphertextBackend(tmp_path / "objects"))
    h = Harness(tmp_path, primary=backend)
    grants = [h.grant("same-write", "WRITE_CIPHERTEXT") for _ in range(6)]
    records = concurrent(6, lambda i: h.port.write(
        grant=grants[i], authenticated_transport_peer=PEER,
        request_id="same-write", envelope=h.data,
    ))
    successes = [v for status, v in records if status == "ok"]
    failures = [v for status, v in records if status == "blocked"]
    assert successes
    assert all(isinstance(v, CloudError) for v in failures)
    assert len({v.object_ref for v in successes}) == 1
    assert backend.put_calls == 1
    assert h.journal.health()["write_count"] == 1
    assert h.journal.verify_chain()["valid"] is True


def test_fresh_signed_backup_grants_for_one_request_never_fork_backup(tmp_path):
    h = Harness(tmp_path)
    h.port.write(
        grant=h.grant("write-1", "WRITE_CIPHERTEXT"),
        authenticated_transport_peer=PEER,
        request_id="write-1", envelope=h.data,
    )
    backup_backend = CountingBackend(h.backup_backend)
    h.backup.backup_backend = backup_backend
    grants = [h.grant("backup-1", "BACKUP_CIPHERTEXT") for _ in range(6)]
    records = concurrent(6, lambda i: h.port.create_encrypted_backup(
        grant=grants[i], authenticated_transport_peer=PEER,
        request_id="backup-1",
    ))
    receipts = [v for status, v in records if status == "ok"]
    failures = [v for status, v in records if status == "blocked"]
    assert receipts
    assert all(isinstance(v, CloudError) for v in failures)
    assert len({v.backup_ref for v in receipts}) == 1
    assert backup_backend.put_calls == 1
    assert h.journal.health()["backup_count"] == 1
    assert h.journal.verify_chain()["valid"] is True


def test_ack_lost_during_competing_backup_requests_is_unresolved_not_retried(tmp_path):
    h = Harness(tmp_path)
    h.port.write(
        grant=h.grant("write-1", "WRITE_CIPHERTEXT"),
        authenticated_transport_peer=PEER,
        request_id="write-1", envelope=h.data,
    )
    unreliable = AcceptBackupThenTimeout()
    h.backup.backup_backend = unreliable
    grants = [h.grant("backup-1", "BACKUP_CIPHERTEXT") for _ in range(5)]
    records = concurrent(5, lambda i: h.port.create_encrypted_backup(
        grant=grants[i], authenticated_transport_peer=PEER,
        request_id="backup-1",
    ))
    assert not [value for status, value in records if status == "ok"]
    assert unreliable.calls == 1
    assert h.journal.health()["backup_count"] == 1
    assert h.journal.health()["pending_backups"] == 1
    assert h.journal.verify_chain()["valid"] is True


def test_competing_fresh_backup_reconciliations_cannot_mutate_twice(tmp_path):
    h = Harness(tmp_path)
    h.port.write(
        grant=h.grant("write-1", "WRITE_CIPHERTEXT"),
        authenticated_transport_peer=PEER,
        request_id="write-1", envelope=h.data,
    )
    unreliable = AcceptBackupThenTimeout()
    h.backup.backup_backend = unreliable
    with pytest.raises(OSError):
        h.port.create_encrypted_backup(
            grant=h.grant("backup-1", "BACKUP_CIPHERTEXT"),
            authenticated_transport_peer=PEER, request_id="backup-1",
        )
    grants = [h.grant("backup-1", "RECONCILE_BACKUP") for _ in range(3)]
    records = concurrent(3, lambda i: h.port.reconcile_original_backup(
        grant=grants[i], authenticated_transport_peer=PEER,
        original_request_id="backup-1",
    ))
    successes = [v for status, v in records if status == "ok"]
    failures = [v for status, v in records if status == "blocked"]
    assert len(successes) == 1
    assert successes[0]["status"] == "PRESENT_INTERNAL_BACKUP_ONLY"
    assert successes[0]["vault_backup_committed"] is False
    assert all(isinstance(v, CloudError) for v in failures)
    assert unreliable.calls == 1
    assert h.journal.health()["pending_backups"] == 0
