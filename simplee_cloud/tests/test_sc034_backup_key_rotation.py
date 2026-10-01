"""SC034 source-only backup-key rotation/history resolver contract.

Resolver callbacks are synthetic. This is NOT a real KMS/HSM, custody policy,
key escrow, provider secret store or production rotation ceremony.
"""
import os
from dataclasses import replace

import pytest

from simplee_cloud.backup import IndependentBackupService
from simplee_cloud.bound_port import SourceOnlyBoundCloudPort
from simplee_cloud.contracts import AccessDenied, CloudError, IntegrityError
from simplee_cloud.journaled_backup import JournaledBackupOperations
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


class CountPrimaryGet:
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


def rewire(h, *, active_ref, resolver, backup_backend=None):
    service = IndependentBackupService(
        source=h.source,
        backup_backend=backup_backend or h.backup_backend,
        key_reference=active_ref,
        backup_key_resolver=resolver,
    )
    journaled = JournaledBackupOperations(
        operations=h.operations, backup=service, mode="source_test",
    )
    port = SourceOnlyBoundCloudPort(
        operations=h.operations, tower_verifier=h.verifier,
        canonical_scope_resolver=lambda request, operation: h.canonical[
            (request, operation)
        ],
        backup=service, journaled_backup=journaled,
        canonical_backup_resolver=lambda request: h.receipts[request],
        mode="source_test",
    )
    return service, journaled, port


def write_primary(h):
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


def restore(port, h, receipt, request):
    h.receipts[request] = receipt
    return port.verify_backup_copy(
        grant=h.grant(
            request, "VERIFY_BACKUP",
            ref=receipt.backup_ref, digest=receipt.backup_sha256,
        ),
        authenticated_transport_peer=PEER, request_id=request,
    )


def test_new_active_key_can_create_new_backup_while_historical_key_restores_old_copy(tmp_path):
    h = Harness(tmp_path)
    write_primary(h)
    keys = {
        "backup-key-v1": os.urandom(32),
        "backup-key-v2": os.urandom(32),
    }
    resolver = lambda ref: keys[ref]

    v1, _, port1 = rewire(h, active_ref="backup-key-v1", resolver=resolver)
    old = create(port1, h, "backup-v1")
    assert old.key_reference == "backup-key-v1"

    v2, _, port2 = rewire(h, active_ref="backup-key-v2", resolver=resolver)
    new = create(port2, h, "backup-v2")
    assert new.key_reference == "backup-key-v2"
    assert new.backup_ref != old.backup_ref
    assert new.backup_sha256 != old.backup_sha256

    old_evidence = restore(port2, h, old, "restore-old-after-rotation")
    new_evidence = restore(port2, h, new, "restore-new")
    assert old_evidence.verified_ciphertext is True
    assert new_evidence.verified_ciphertext is True
    assert old_evidence.production_recovery_authorized is False
    assert new_evidence.production_recovery_authorized is False


def test_retired_historical_key_reference_denies_before_backup_provider_get(tmp_path):
    h = Harness(tmp_path)
    write_primary(h)
    keys = {
        "backup-key-v1": os.urandom(32),
        "backup-key-v2": os.urandom(32),
    }
    resolver = lambda ref: keys[ref]
    _, _, port1 = rewire(h, active_ref="backup-key-v1", resolver=resolver)
    old = create(port1, h, "backup-v1")

    spy = CountBackupGet(h.backup_backend)
    service2, _, port2 = rewire(
        h, active_ref="backup-key-v2", resolver=resolver,
        backup_backend=spy,
    )
    del keys["backup-key-v1"]
    with pytest.raises(AccessDenied, match="backup key unavailable"):
        restore(port2, h, old, "restore-retired-key")
    assert spy.get_calls == 0
    assert service2.key_reference == "backup-key-v2"


def test_resolver_wrong_key_material_authentication_fails_not_silent_relabel(tmp_path):
    h = Harness(tmp_path)
    write_primary(h)
    keys = {
        "backup-key-v1": os.urandom(32),
        "backup-key-v2": os.urandom(32),
    }
    resolver = lambda ref: keys[ref]
    _, _, port1 = rewire(h, active_ref="backup-key-v1", resolver=resolver)
    old = create(port1, h, "backup-v1")
    keys["backup-key-v1"] = os.urandom(32)

    _, _, port2 = rewire(h, active_ref="backup-key-v2", resolver=resolver)
    with pytest.raises(IntegrityError, match="backup authentication failed"):
        restore(port2, h, old, "restore-wrong-key-material")
    assert h.port.health()["production_authorized"] is False


def test_forged_unknown_key_reference_denied_before_provider_read(tmp_path):
    h = Harness(tmp_path)
    write_primary(h)
    keys = {"backup-key-v1": os.urandom(32)}
    resolver = lambda ref: keys[ref]
    service, _, port = rewire(h, active_ref="backup-key-v1", resolver=resolver)
    original = create(port, h, "backup-v1")
    forged = replace(original, key_reference="backup-key-does-not-exist")
    spy = CountBackupGet(service.backup_backend)
    service.backup_backend = spy

    # Durable SC029 restore provenance rejects the forged key reference even
    # before key resolution because it no longer matches the ACKed backup intent.
    with pytest.raises(CloudError, match="acknowledged exact backup"):
        restore(port, h, forged, "restore-forged-key-ref")
    assert spy.get_calls == 0


def test_active_key_resolver_outage_denies_new_backup_before_primary_provider_read(tmp_path):
    h = Harness(tmp_path)
    write_primary(h)
    state = {"up": True}
    key = os.urandom(32)
    def resolver(ref):
        if not state["up"]:
            raise OSError("synthetic KMS unavailable")
        if ref != "backup-key-v2":
            raise KeyError(ref)
        return key

    spy_primary = CountPrimaryGet(h.primary)
    h.source._backend = spy_primary
    service, _, port = rewire(h, active_ref="backup-key-v2", resolver=resolver)
    state["up"] = False
    with pytest.raises(AccessDenied, match="backup key unavailable"):
        create(port, h, "backup-kms-outage")
    assert spy_primary.get_calls == 0
    assert service.key_reference == "backup-key-v2"
    assert h.journal.health()["backup_count"] == 0


def test_invalid_resolver_output_and_ambiguous_fixed_plus_resolver_rejected(tmp_path):
    h = Harness(tmp_path)
    with pytest.raises(AccessDenied, match="backup key unavailable"):
        IndependentBackupService(
            source=h.source, backup_backend=h.backup_backend,
            key_reference="backup-key-v2",
            backup_key_resolver=lambda ref: b"too-short",
        )
    with pytest.raises(CloudError, match="either fixed backup key or resolver"):
        IndependentBackupService(
            source=h.source, backup_backend=h.backup_backend,
            backup_key=os.urandom(32), key_reference="backup-key-v2",
            backup_key_resolver=lambda ref: os.urandom(32),
        )


def test_fixed_key_legacy_mode_still_rejects_different_receipt_key_reference(tmp_path):
    h = Harness(tmp_path)
    write_primary(h)
    receipt = h.port.create_encrypted_backup(
        grant=h.grant("backup-fixed", "BACKUP_CIPHERTEXT"),
        authenticated_transport_peer=PEER, request_id="backup-fixed",
    )
    forged = replace(receipt, key_reference="different-key")
    h.receipts["restore-fixed-forged"] = forged
    # Fixed-key mode is also protected first by exact durable backup provenance.
    with pytest.raises(CloudError, match="acknowledged exact backup"):
        h.port.verify_backup_copy(
            grant=h.grant(
                "restore-fixed-forged", "VERIFY_BACKUP",
                ref=forged.backup_ref, digest=forged.backup_sha256,
            ),
            authenticated_transport_peer=PEER,
            request_id="restore-fixed-forged",
        )


def test_same_logical_backup_request_cannot_be_rebound_to_new_active_key(tmp_path):
    h = Harness(tmp_path)
    write_primary(h)
    keys = {
        "backup-key-v1": os.urandom(32),
        "backup-key-v2": os.urandom(32),
    }
    resolver = lambda ref: keys[ref]
    _, _, port1 = rewire(h, active_ref="backup-key-v1", resolver=resolver)
    first = create(port1, h, "same-backup")
    assert first.key_reference == "backup-key-v1"

    _, _, port2 = rewire(h, active_ref="backup-key-v2", resolver=resolver)
    with pytest.raises(CloudError, match="conflicting backup idempotency reservation"):
        create(port2, h, "same-backup")
    intent = h.journal.backup_intent(
        namespace=first.namespace_digest, request_id="same-backup",
    )
    assert intent["key_reference"] == "backup-key-v1"
    assert h.journal.health()["backup_count"] == 1
