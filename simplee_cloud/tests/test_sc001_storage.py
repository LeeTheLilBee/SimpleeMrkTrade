import hashlib
import os
from dataclasses import replace

import pytest

from simplee_cloud.contracts import (
    AccessDenied, AlreadyExists, CloudError, IntegrityError, StorageContext,
)
from simplee_cloud.local_backend import LocalPrivateCiphertextBackend
from simplee_cloud.service import CiphertextStorageService


class TestOnlyAuthority:
    # Synthetic ONLY. Not a signer, credential, expiry/revocation verifier or
    # production authorization implementation.
    __test__ = False
    def authorize(self, context, operation):
        if context.tower_decision_ref != "trusted-test-decision":
            raise AccessDenied("test gate denied")
        if context.operation != operation:
            raise AccessDenied("test operation denied")


def ctx(operation="WRITE_CIPHERTEXT", entity="trust"):
    return StorageContext(
        request_id="request-1", caller_service="archive_vault",
        tower_decision_ref="trusted-test-decision",
        entity_id=entity, purpose="archival", operation=operation,
    )


def service(tmp_path, **overrides):
    audit = []
    data = dict(
        backend=LocalPrivateCiphertextBackend(tmp_path / "primary"),
        namespace_key=os.urandom(32), authority=TestOnlyAuthority(),
        audit_event=audit.append, mode="source_test",
    )
    data.update(overrides)
    return CiphertextStorageService(**data), audit


def test_ciphertext_round_trip_and_immutable_write(tmp_path):
    cloud, audit = service(tmp_path)
    original = b"VLT1" + os.urandom(48)
    ref = cloud.new_object_ref()
    digest = hashlib.sha256(original).hexdigest()
    receipt = cloud.put_if_absent(
        context=ctx(), object_ref=ref, envelope=original, expected_sha256=digest,
    )
    assert receipt.ciphertext_sha256 == digest
    assert receipt.ciphertext_size == len(original)
    assert cloud.get(
        context=ctx("READ_CIPHERTEXT"), object_ref=ref, expected_sha256=digest
    ) == original
    with pytest.raises(AlreadyExists):
        cloud.put_if_absent(
            context=ctx(), object_ref=ref, envelope=original, expected_sha256=digest,
        )
    assert [row["event"] for row in audit] == [
        "write_intent", "write_acknowledged", "read_intent",
        "read_verified", "write_intent",
    ]
    assert all("body" not in row and "entity_id" not in row for row in audit)


def test_denied_by_default_and_disabled_in_any_live_mode(tmp_path):
    backend = LocalPrivateCiphertextBackend(tmp_path / "primary")
    key = os.urandom(32)
    data = b"VLT1" + os.urandom(48)
    ref = CiphertextStorageService.new_object_ref()
    digest = hashlib.sha256(data).hexdigest()
    denied = CiphertextStorageService(
        backend=backend, namespace_key=key, audit_event=lambda event: None,
        mode="source_test",
    )
    with pytest.raises(AccessDenied):
        denied.put_if_absent(
            context=ctx(), object_ref=ref, envelope=data, expected_sha256=digest,
        )
    disabled = CiphertextStorageService(
        backend=backend, namespace_key=key, authority=TestOnlyAuthority(),
        audit_event=lambda event: None,
    )
    with pytest.raises(AccessDenied):
        disabled.put_if_absent(
            context=ctx(), object_ref=ref, envelope=data, expected_sha256=digest,
        )
    assert disabled.health()["production_authorized"] is False
    with pytest.raises(CloudError):
        CiphertextStorageService(backend=backend, namespace_key=key, mode="production")


def test_scope_auth_and_content_fail_closed(tmp_path):
    cloud, _ = service(tmp_path)
    data = b"VLT1" + os.urandom(48)
    digest = hashlib.sha256(data).hexdigest()
    ref = cloud.new_object_ref()
    with pytest.raises(AccessDenied):
        cloud.put_if_absent(
            context=replace(ctx(), caller_service="buybox"),
            object_ref=ref, envelope=data, expected_sha256=digest,
        )
    with pytest.raises(AccessDenied):
        cloud.put_if_absent(
            context=replace(ctx(), tower_decision_ref="self-attested"),
            object_ref=ref, envelope=data, expected_sha256=digest,
        )
    with pytest.raises(IntegrityError):
        cloud.put_if_absent(
            context=ctx(), object_ref=ref, envelope=data, expected_sha256="0" * 64,
        )
    with pytest.raises(CloudError):
        cloud.put_if_absent(
            context=ctx(), object_ref=ref, envelope=b"PDF plaintext",
            expected_sha256=hashlib.sha256(b"PDF plaintext").hexdigest(),
        )
    with pytest.raises(CloudError):
        cloud.put_if_absent(
            context=ctx(), object_ref="../escape", envelope=data,
            expected_sha256=digest,
        )
    cloud.put_if_absent(
        context=ctx(), object_ref=ref, envelope=data, expected_sha256=digest,
    )
    with pytest.raises(Exception):
        cloud.get(
            context=ctx("READ_CIPHERTEXT", entity="business-other"),
            object_ref=ref, expected_sha256=digest,
        )
    with pytest.raises(IntegrityError):
        cloud.get(
            context=ctx("READ_CIPHERTEXT"), object_ref=ref, expected_sha256="0" * 64,
        )
    assert not (tmp_path / "escape").exists()


def test_tamper_and_symlink_root_rejected(tmp_path):
    cloud, _ = service(tmp_path)
    data = b"VLT1" + os.urandom(48)
    digest = hashlib.sha256(data).hexdigest()
    ref = cloud.new_object_ref()
    receipt = cloud.put_if_absent(
        context=ctx(), object_ref=ref, envelope=data, expected_sha256=digest,
    )
    target = tmp_path / "primary" / receipt.namespace_digest / "objects" / ref.split("/")[1]
    target.write_bytes(b"VLT1" + os.urandom(48))
    with pytest.raises(IntegrityError):
        cloud.get(context=ctx("READ_CIPHERTEXT"), object_ref=ref, expected_sha256=digest)
    (tmp_path / "link").symlink_to(tmp_path / "primary", target_is_directory=True)
    with pytest.raises(CloudError):
        LocalPrivateCiphertextBackend(tmp_path / "link")
