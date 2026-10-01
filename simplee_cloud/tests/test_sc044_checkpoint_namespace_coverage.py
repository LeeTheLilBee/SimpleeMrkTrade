"""SC044 signed-prefix namespace coverage and historical non-rewrite tests."""
import hashlib
import json
import os

import pytest

from simplee_cloud.control_checkpoints import (
    SignedControlCheckpoint, seal_source_control_checkpoint,
)
from simplee_cloud.contracts import AccessDenied, IntegrityError, StorageContext
from simplee_cloud.journal import SQLiteOperationalJournal
from simplee_cloud.local_backend import LocalPrivateCiphertextBackend
from simplee_cloud.namespace_bindings import SQLiteNamespaceBindingLedger
from simplee_cloud.namespace_coverage import (
    source_control_checkpoint_namespace_coverage,
    source_namespace_binding_coverage,
)
from simplee_cloud.operations import JournaledCiphertextOperations
from simplee_cloud.owner_evidence_desk import owner_local_evidence_desk
from simplee_cloud.service import CiphertextStorageService
from simplee_cloud.tests.test_sc005_recovery import keys
from simplee_cloud.tower_grants import SQLiteNonceReplayStore


KEY = b"c" * 32


class Authority:
    def authorize(self, context, operation):
        if (
            context.caller_service != "archive_vault" or
            context.tower_decision_ref != "synthetic-gate" or
            context.operation != operation
        ):
            raise AccessDenied("synthetic authority denied")


def ctx(operation, request, entity="trust"):
    return StorageContext(
        request_id=request, caller_service="archive_vault",
        tower_decision_ref="synthetic-gate", entity_id=entity,
        purpose="archive", operation=operation,
    )


def bindings(tmp_path):
    return SQLiteNamespaceBindingLedger(
        tmp_path / "namespace" / "bindings.sqlite",
        binding_key=KEY, mode="source_test",
    )


def replay(tmp_path):
    return SQLiteNonceReplayStore(
        tmp_path / "replay" / "consumed.sqlite", mode="source_test",
    )


def journal(tmp_path):
    return SQLiteOperationalJournal(
        tmp_path / "audit" / "operations.sqlite", mode="source_test",
    )


def stack(tmp_path, mapping, ledger):
    j = journal(tmp_path)
    svc = CiphertextStorageService(
        backend=LocalPrivateCiphertextBackend(tmp_path / "objects"),
        namespace_resolver=lambda entity: mapping[entity],
        namespace_binding_ledger=ledger,
        authority=Authority(), audit_event=j.record_safe_event,
        mode="source_test",
    )
    return svc, JournaledCiphertextOperations(source=svc, journal=j), j


def write(ops, svc, request, entity="trust"):
    body = b"VLT1" + os.urandom(48)
    digest = hashlib.sha256(body).hexdigest()
    return ops.put_if_absent(
        context=ctx("WRITE_CIPHERTEXT", request, entity),
        object_ref=svc.new_object_ref(),
        envelope=body, expected_sha256=digest,
    )


def seal(j, r, b):
    private, pubs = keys()
    signed = seal_source_control_checkpoint(
        journal=j, replay_store=r, namespace_bindings=b,
        key_id="synthetic-external-signer",
        external_signer=private.sign, pinned_public_keys=pubs,
        mode="source_test",
    )
    return signed, pubs, private


def signed_coverage(signed, pubs, j, r, b):
    return source_control_checkpoint_namespace_coverage(
        checkpoint=signed, pinned_public_keys=pubs,
        journal=j, replay_store=r, namespace_bindings=b,
    )


def legacy_v1(v2, private):
    doc = json.loads(v2.payload)
    doc["schema"] = "simplee.cloud.control-checkpoint.v1"
    doc.pop("namespace_binding_key_commitment_sha256")
    payload = json.dumps(
        doc, sort_keys=True, separators=(",", ":"), ensure_ascii=True,
    ).encode()
    return SignedControlCheckpoint(payload, private.sign(payload))


def test_current_and_historical_inventory_prefixes_are_distinct(tmp_path):
    b = bindings(tmp_path)
    mapping = {"trust": "a" * 64, "other": "b" * 64}
    b.enroll_source_binding(entity_id="trust", namespace=mapping["trust"])
    svc, ops, j = stack(tmp_path, mapping, b)
    write(ops, svc, "write-1")
    first_storage_count = j.verify_chain()["event_count"]
    first_namespace_count = b.verify_chain()["event_count"]

    b.enroll_source_binding(entity_id="other", namespace=mapping["other"])
    write(ops, svc, "write-2", "other")

    historical = source_namespace_binding_coverage(
        j, b,
        storage_event_count=first_storage_count,
        namespace_event_count=first_namespace_count,
    )
    current = source_namespace_binding_coverage(j, b)
    assert historical["historical_prefix_comparison"] is True
    assert historical["resolver_namespace_count"] == 1
    assert historical["enrolled_namespace_count"] == 1
    assert historical["matched_namespace_count"] == 1
    assert historical["storage_state_advanced_after_prefix"] is True
    assert historical["namespace_state_advanced_after_prefix"] is True
    assert current["resolver_namespace_count"] == 2
    assert current["matched_namespace_count"] == 2


def test_signed_control_vector_verifies_exact_historical_namespace_coverage(tmp_path):
    b = bindings(tmp_path)
    mapping = {"trust": "a" * 64}
    b.enroll_source_binding(entity_id="trust", namespace=mapping["trust"])
    svc, ops, j = stack(tmp_path, mapping, b)
    write(ops, svc, "write-1")
    r = replay(tmp_path)
    signed, pubs, _ = seal(j, r, b)

    result = signed_coverage(signed, pubs, j, r, b)
    assert result["signed_control_vector_verified"] is True
    assert result["exact_signed_prefix_coverage_verified"] is True
    assert result["resolver_namespace_count"] == 1
    assert result["enrolled_namespace_count"] == 1
    assert result["missing_resolver_namespace_count"] == 0
    assert result["namespace_binding_key_commitment_signed"] is True
    assert result["cross_ledger_point_in_time_certified"] is False
    assert result["actual_external_latest_attested"] is False
    assert result["production_authorized"] is False


def test_later_repair_does_not_rewrite_signed_checkpoint_missing_coverage(tmp_path):
    b = bindings(tmp_path)
    j = journal(tmp_path)
    r = replay(tmp_path)
    namespace = "a" * 64

    # Source-adversarial marker: a resolver-backed namespace was recorded while
    # its registry had no binding. A signed vector must preserve that fact.
    j.record_safe_event({
        "event": "namespace_binding_verified",
        "request_id": "synthetic-gap",
        "tower_decision_ref": "synthetic-gate",
        "namespace_digest": namespace,
    })
    signed, pubs, _ = seal(j, r, b)
    before = signed_coverage(signed, pubs, j, r, b)
    assert before["status"] == "SOURCE_ONLY_NAMESPACE_BINDING_HOLD"
    assert before["missing_resolver_namespace_count"] == 1
    assert before["exact_signed_prefix_coverage_verified"] is False

    # Repair current registry later. Current readiness is now clean, but the
    # older signed vector remains historically incomplete.
    b.enroll_source_binding(entity_id="trust", namespace=namespace)
    current = source_namespace_binding_coverage(j, b)
    assert current["missing_resolver_namespace_count"] == 0
    after = signed_coverage(signed, pubs, j, r, b)
    assert after["missing_resolver_namespace_count"] == 1
    assert after["exact_signed_prefix_coverage_verified"] is False
    assert after["namespace_state_advanced_after_prefix"] is True

    desk = owner_local_evidence_desk(
        journal=j, replay_store=r, namespace_bindings=b,
        control_checkpoint=signed, pinned_public_keys=pubs,
    )
    assert desk["namespace_binding_readiness"][
        "missing_resolver_namespace_count"
    ] == 0
    historical = desk["checkpoint_namespace_coverage"]
    assert historical["status"] == "SOURCE_ONLY_NAMESPACE_BINDING_HOLD"
    assert historical["missing_resolver_namespace_count"] == 1
    assert historical["exact_signed_prefix_coverage_verified"] is False
    assert desk["production_authorized"] is False


def test_later_new_namespace_does_not_expand_old_signed_vector_inventory(tmp_path):
    b = bindings(tmp_path)
    mapping = {"trust": "a" * 64, "other": "b" * 64}
    b.enroll_source_binding(entity_id="trust", namespace=mapping["trust"])
    svc, ops, j = stack(tmp_path, mapping, b)
    write(ops, svc, "write-1")
    r = replay(tmp_path)
    signed, pubs, _ = seal(j, r, b)

    b.enroll_source_binding(entity_id="other", namespace=mapping["other"])
    write(ops, svc, "write-2", "other")
    historical = signed_coverage(signed, pubs, j, r, b)
    current = source_namespace_binding_coverage(j, b)
    assert historical["resolver_namespace_count"] == 1
    assert historical["matched_namespace_count"] == 1
    assert historical["storage_state_advanced_after_prefix"] is True
    assert historical["namespace_state_advanced_after_prefix"] is True
    assert current["resolver_namespace_count"] == 2
    assert current["matched_namespace_count"] == 2


def test_legacy_v1_checkpoint_can_anchor_historical_coverage_but_not_key_commitment(tmp_path):
    b = bindings(tmp_path)
    mapping = {"trust": "a" * 64}
    b.enroll_source_binding(entity_id="trust", namespace=mapping["trust"])
    svc, ops, j = stack(tmp_path, mapping, b)
    write(ops, svc, "write-1")
    r = replay(tmp_path)
    v2, pubs, private = seal(j, r, b)
    v1 = legacy_v1(v2, private)

    result = signed_coverage(v1, pubs, j, r, b)
    assert result["exact_signed_prefix_coverage_verified"] is True
    assert result["namespace_binding_key_commitment_signed"] is False
    assert result["control_checkpoint_schema"] == (
        "simplee.cloud.control-checkpoint.v1"
    )
    assert result["production_authorized"] is False


def test_bad_prefix_arguments_fail_closed_not_clamped_to_current(tmp_path):
    b = bindings(tmp_path)
    j = journal(tmp_path)
    with pytest.raises(IntegrityError, match="prefix unavailable"):
        j.source_resolver_namespace_inventory(1)
    with pytest.raises(IntegrityError, match="prefix unavailable"):
        b.source_namespace_inventory(1)
    with pytest.raises(Exception):
        source_namespace_binding_coverage(
            j, b, storage_event_count=0, namespace_event_count=None,
        )


def test_owner_signed_prefix_coverage_is_redacted(tmp_path):
    b = bindings(tmp_path)
    namespace = "a" * 64
    b.enroll_source_binding(entity_id="private-entity", namespace=namespace)
    mapping = {"private-entity": namespace}
    svc, ops, j = stack(tmp_path, mapping, b)
    write(ops, svc, "private-request", "private-entity")
    r = replay(tmp_path)
    signed, pubs, _ = seal(j, r, b)

    desk = owner_local_evidence_desk(
        journal=j, replay_store=r, namespace_bindings=b,
        control_checkpoint=signed, pinned_public_keys=pubs,
    )
    wire = json.dumps(desk)
    assert "private-entity" not in wire
    assert "private-request" not in wire
    assert namespace not in wire
    assert desk["checkpoint_namespace_coverage"][
        "exact_signed_prefix_coverage_verified"
    ] is True
    assert desk["cross_ledger_point_in_time_certified"] is False
