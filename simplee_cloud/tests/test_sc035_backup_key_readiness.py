"""SC035 redacted backup-key readiness from verified acknowledged intents."""
import json
import os
import sqlite3

import pytest

from simplee_cloud.backup import IndependentBackupService
from simplee_cloud.bound_port import SourceOnlyBoundCloudPort
from simplee_cloud.contracts import IntegrityError
from simplee_cloud.journaled_backup import JournaledBackupOperations
from simplee_cloud.key_readiness import source_backup_key_readiness
from simplee_cloud.tests.test_sc004b_bound_port import Harness, PEER
from simplee_cloud.tests.test_sc005b_backup_operations import AcceptBackupThenTimeout


SECRET = "synthetic-kms-secret-exception"


class NoRead:
    def __init__(self, actual):
        self.actual = actual
        self.get_calls = 0
        self.put_calls = 0
    def get(self, namespace, ref):
        self.get_calls += 1
        raise AssertionError("key readiness must not read provider bytes")
    def put_if_absent(self, namespace, ref, body):
        self.put_calls += 1
        return self.actual.put_if_absent(namespace, ref, body)


def rewire(h, active_ref, resolver):
    backup = IndependentBackupService(
        source=h.source, backup_backend=h.backup_backend,
        key_reference=active_ref, backup_key_resolver=resolver,
    )
    ops = JournaledBackupOperations(
        operations=h.operations, backup=backup, mode="source_test",
    )
    port = SourceOnlyBoundCloudPort(
        operations=h.operations, tower_verifier=h.verifier,
        canonical_scope_resolver=lambda request, operation: h.canonical[
            (request, operation)
        ],
        backup=backup, journaled_backup=ops,
        canonical_backup_resolver=lambda request: h.receipts[request],
        mode="source_test",
    )
    return backup, ops, port


def write(h):
    return h.port.write(
        grant=h.grant("write-1", "WRITE_CIPHERTEXT"),
        authenticated_transport_peer=PEER,
        request_id="write-1", envelope=h.data,
    )


def create(port, h, request):
    return port.create_encrypted_backup(
        grant=h.grant(request, "BACKUP_CIPHERTEXT"),
        authenticated_transport_peer=PEER, request_id=request,
    )


def test_empty_inventory_is_not_kms_or_recovery_certification(tmp_path):
    h = Harness(tmp_path)
    report = source_backup_key_readiness(h.journaled_backup)
    assert report["acknowledged_backup_count"] == 0
    assert report["distinct_key_reference_count"] == 0
    assert report["unavailable_key_reference_count"] == 0
    assert report["provider_bytes_read"] is False
    assert report["external_kms_hsm_custody_certified"] is False
    assert report["old_key_recovery_drill_certified"] is False
    assert report["production_authorized"] is False


def test_fixed_key_acknowledged_backup_reference_is_resolvable_source_only(tmp_path):
    h = Harness(tmp_path)
    write(h)
    h.port.create_encrypted_backup(
        grant=h.grant("backup-1", "BACKUP_CIPHERTEXT"),
        authenticated_transport_peer=PEER, request_id="backup-1",
    )
    report = source_backup_key_readiness(h.journaled_backup)
    assert report["acknowledged_backup_count"] == 1
    assert report["distinct_key_reference_count"] == 1
    assert report["resolvable_key_reference_count"] == 1
    assert report["unavailable_key_reference_count"] == 0
    assert report["resolved_key_material_correct_for_ciphertext_certified"] is False


def test_rotated_v1_v2_inventory_counts_both_without_exposing_references(tmp_path):
    h = Harness(tmp_path)
    write(h)
    keys = {
        "backup-key-v1": os.urandom(32),
        "backup-key-v2": os.urandom(32),
    }
    resolver = lambda ref: keys[ref]
    _, _, port1 = rewire(h, "backup-key-v1", resolver)
    first = create(port1, h, "backup-v1")
    _, ops2, port2 = rewire(h, "backup-key-v2", resolver)
    second = create(port2, h, "backup-v2")

    report = source_backup_key_readiness(ops2)
    assert report["acknowledged_backup_count"] == 2
    assert report["distinct_key_reference_count"] == 2
    assert report["resolvable_key_reference_count"] == 2
    assert report["unavailable_key_reference_count"] == 0
    wire = json.dumps(report)
    assert first.key_reference not in wire
    assert second.key_reference not in wire


def test_retired_historical_key_counts_affected_acknowledged_backups_without_provider_get(tmp_path):
    h = Harness(tmp_path)
    write(h)
    keys = {
        "backup-key-v1": os.urandom(32),
        "backup-key-v2": os.urandom(32),
    }
    resolver = lambda ref: keys[ref]
    _, _, port1 = rewire(h, "backup-key-v1", resolver)
    create(port1, h, "backup-v1")
    backup2, ops2, port2 = rewire(h, "backup-key-v2", resolver)
    create(port2, h, "backup-v2")
    del keys["backup-key-v1"]

    no_backup_read = NoRead(backup2.backup_backend)
    no_primary_read = NoRead(h.source._backend)
    backup2.backup_backend = no_backup_read
    h.source._backend = no_primary_read
    report = source_backup_key_readiness(ops2)
    assert report["acknowledged_backup_count"] == 2
    assert report["resolvable_key_reference_count"] == 1
    assert report["unavailable_key_reference_count"] == 1
    assert report["acknowledged_backups_depending_on_unavailable_key_count"] == 1
    assert no_backup_read.get_calls == 0
    assert no_primary_read.get_calls == 0
    assert report["provider_bytes_read"] is False


def test_wrong_but_32_byte_key_is_only_resolvable_not_cryptographically_certified(tmp_path):
    h = Harness(tmp_path)
    write(h)
    keys = {"backup-key-v1": os.urandom(32)}
    resolver = lambda ref: keys[ref]
    _, ops, port = rewire(h, "backup-key-v1", resolver)
    create(port, h, "backup-v1")
    keys["backup-key-v1"] = os.urandom(32)
    report = source_backup_key_readiness(ops)
    assert report["resolvable_key_reference_count"] == 1
    assert report["unavailable_key_reference_count"] == 0
    assert report["backup_ciphertext_authenticated_in_this_check"] is False
    assert report["resolved_key_material_correct_for_ciphertext_certified"] is False


def test_resolver_exception_is_redacted_to_counts_only(tmp_path):
    h = Harness(tmp_path)
    write(h)
    key = os.urandom(32)
    state = {"fail": False}
    def resolver(ref):
        if state["fail"]:
            raise OSError(SECRET)
        return key

    _, ops, port = rewire(h, "backup-key-v1", resolver)
    create(port, h, "backup-v1")
    state["fail"] = True
    report = source_backup_key_readiness(ops)
    assert report["unavailable_key_reference_count"] == 1
    assert report["acknowledged_backups_depending_on_unavailable_key_count"] == 1
    assert SECRET not in json.dumps(report)


def test_pending_ack_lost_backup_is_not_counted_as_recovery_key_dependency(tmp_path):
    h = Harness(tmp_path)
    write(h)
    provider = AcceptBackupThenTimeout()
    h.backup.backup_backend = provider
    with pytest.raises(OSError):
        h.port.create_encrypted_backup(
            grant=h.grant("backup-pending", "BACKUP_CIPHERTEXT"),
            authenticated_transport_peer=PEER, request_id="backup-pending",
        )
    report = source_backup_key_readiness(h.journaled_backup)
    assert report["acknowledged_backup_count"] == 0
    assert report["distinct_key_reference_count"] == 0
    assert report["pending_backup_count"] == 1
    assert report["integrity_hold_backup_count"] == 0


def test_backup_integrity_hold_is_not_counted_as_acknowledged_key_ready(tmp_path):
    h = Harness(tmp_path)
    write(h)
    receipt = h.port.create_encrypted_backup(
        grant=h.grant("backup-1", "BACKUP_CIPHERTEXT"),
        authenticated_transport_peer=PEER, request_id="backup-1",
    )
    assert source_backup_key_readiness(h.journaled_backup)["acknowledged_backup_count"] == 1
    h.journal.backup_transition(
        namespace=receipt.namespace_digest, request_id="backup-1",
        next_state="BACKUP_REPLAY_INTEGRITY_FAILURE",
    )
    report = source_backup_key_readiness(h.journaled_backup)
    assert report["acknowledged_backup_count"] == 0
    assert report["integrity_hold_backup_count"] == 1


def test_tampered_key_reference_journal_fails_before_resolver_preflight(tmp_path):
    h = Harness(tmp_path)
    write(h)
    h.port.create_encrypted_backup(
        grant=h.grant("backup-1", "BACKUP_CIPHERTEXT"),
        authenticated_transport_peer=PEER, request_id="backup-1",
    )
    with sqlite3.connect(h.journal.path) as db:
        db.execute("DROP TRIGGER backup_intents_block_update")
        db.execute(
            "UPDATE backup_intents SET key_reference=?",
            ("tampered-key-reference",),
        )
    with pytest.raises(IntegrityError):
        source_backup_key_readiness(h.journaled_backup)
