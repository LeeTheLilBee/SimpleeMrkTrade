"""SC043 v2 control checkpoint binds namespace binding-key commitment.

Legacy v1 source checkpoints remain verifiable but explicitly cannot claim the
new key-commitment binding. All signers/keys/sinks here are synthetic.
"""
import json

import pytest

from simplee_cloud.control_checkpoints import (
    SignedControlCheckpoint,
    seal_source_control_checkpoint,
    verify_control_checkpoint,
    verify_source_control_checkpoint_sequence,
)
from simplee_cloud.contracts import CloudError, IntegrityError
from simplee_cloud.namespace_bindings import SQLiteNamespaceBindingLedger
from simplee_cloud.owner_evidence_desk import owner_local_evidence_desk
from simplee_cloud.tests.test_sc004b_bound_port import Harness, PEER
from simplee_cloud.tests.test_sc005_recovery import keys


def prepared(tmp_path):
    h = Harness(tmp_path / "cloud")
    h.port.write(
        grant=h.grant("write-1", "WRITE_CIPHERTEXT"),
        authenticated_transport_peer=PEER,
        request_id="write-1", envelope=h.data,
    )
    bindings = SQLiteNamespaceBindingLedger(
        tmp_path / "namespace" / "bindings.sqlite",
        binding_key=b"m" * 32, mode="source_test",
    )
    bindings.enroll_source_binding(
        entity_id="trust", namespace=h.ref_namespace,
    ) if hasattr(h, "ref_namespace") else bindings.enroll_source_binding(
        entity_id="trust",
        namespace=h.port.health().get("namespace_digest", "a" * 64),
    )
    private, pubs = keys()
    return h, bindings, private, pubs


def prepared_exact(tmp_path):
    """Avoid relying on Harness internals for the namespace under test."""
    h = Harness(tmp_path / "cloud")
    receipt = h.port.write(
        grant=h.grant("write-1", "WRITE_CIPHERTEXT"),
        authenticated_transport_peer=PEER,
        request_id="write-1", envelope=h.data,
    )
    bindings = SQLiteNamespaceBindingLedger(
        tmp_path / "namespace" / "bindings.sqlite",
        binding_key=b"m" * 32, mode="source_test",
    )
    bindings.enroll_source_binding(
        entity_id="trust", namespace=receipt.namespace_digest,
    )
    private, pubs = keys()
    return h, bindings, private, pubs


def seal(h, bindings, private, pubs, previous=None):
    return seal_source_control_checkpoint(
        journal=h.journal, replay_store=h.nonces,
        namespace_bindings=bindings,
        key_id="synthetic-external-signer",
        external_signer=private.sign,
        pinned_public_keys=pubs, previous=previous,
        mode="source_test",
    )


def verify(signed, h, bindings, pubs):
    return verify_control_checkpoint(
        signed, pinned_public_keys=pubs,
        journal=h.journal, replay_store=h.nonces,
        namespace_bindings=bindings,
    )


def legacy_v1(v2, private):
    doc = json.loads(v2.payload)
    doc["schema"] = "simplee.cloud.control-checkpoint.v1"
    doc.pop("namespace_binding_key_commitment_sha256")
    payload = json.dumps(
        doc, sort_keys=True, separators=(",", ":"), ensure_ascii=True,
    ).encode()
    return SignedControlCheckpoint(payload, private.sign(payload))


def test_new_control_checkpoint_signs_exact_registered_binding_key_commitment(tmp_path):
    h, bindings, private, pubs = prepared_exact(tmp_path)
    signed = seal(h, bindings, private, pubs)
    doc = verify(signed, h, bindings, pubs)
    local = bindings.source_binding_key_commitment()
    assert doc["schema"] == "simplee.cloud.control-checkpoint.v2"
    assert doc["namespace_binding_key_commitment_sha256"] == (
        local["binding_key_commitment"]
    )
    assert local["external_anchor_certified"] is False


def test_validly_resigned_wrong_key_commitment_is_rejected_against_ledger(tmp_path):
    h, bindings, private, pubs = prepared_exact(tmp_path)
    signed = seal(h, bindings, private, pubs)
    doc = json.loads(signed.payload)
    doc["namespace_binding_key_commitment_sha256"] = "f" * 64
    payload = json.dumps(
        doc, sort_keys=True, separators=(",", ":"), ensure_ascii=True,
    ).encode()
    forged = SignedControlCheckpoint(payload, private.sign(payload))
    with pytest.raises(
        IntegrityError, match="binding-key commitment mismatch"
    ):
        verify(forged, h, bindings, pubs)


def test_legacy_v1_checkpoint_still_verifies_but_has_no_key_commitment_claim(tmp_path):
    h, bindings, private, pubs = prepared_exact(tmp_path)
    current = seal(h, bindings, private, pubs)
    old = legacy_v1(current, private)
    doc = verify(old, h, bindings, pubs)
    assert doc["schema"] == "simplee.cloud.control-checkpoint.v1"
    assert "namespace_binding_key_commitment_sha256" not in doc


def test_one_same_vector_v1_to_v2_strengthening_is_allowed_and_lineage_verifies(tmp_path):
    h, bindings, private, pubs = prepared_exact(tmp_path)
    initial_v2 = seal(h, bindings, private, pubs)
    old = legacy_v1(initial_v2, private)
    upgraded = seal(h, bindings, private, pubs, previous=old)
    new_doc = verify(upgraded, h, bindings, pubs)
    old_doc = verify(old, h, bindings, pubs)
    assert (
        new_doc["storage_event_count"],
        new_doc["replay_event_count"],
        new_doc["namespace_event_count"],
    ) == (
        old_doc["storage_event_count"],
        old_doc["replay_event_count"],
        old_doc["namespace_event_count"],
    )
    report = verify_source_control_checkpoint_sequence(
        checkpoints=[old, upgraded], pinned_public_keys=pubs,
        journal=h.journal, replay_store=h.nonces,
        namespace_bindings=bindings, mode="source_test",
    )
    assert report["namespace_binding_key_commitment_in_tip"] is True
    assert report["namespace_binding_key_commitment_matches_current"] is True
    assert report["actual_external_latest_attested"] is False
    assert report["production_authorized"] is False


def test_same_vector_second_v2_checkpoint_is_still_replay_and_denied(tmp_path):
    h, bindings, private, pubs = prepared_exact(tmp_path)
    first = seal(h, bindings, private, pubs)
    with pytest.raises(
        CloudError, match="monotonic ledger progress|v1-to-v2"
    ):
        seal(h, bindings, private, pubs, previous=first)


def test_owner_desk_reports_local_signed_key_commitment_without_exposing_digest(tmp_path):
    h, bindings, private, pubs = prepared_exact(tmp_path)
    signed = seal(h, bindings, private, pubs)
    report = owner_local_evidence_desk(
        journal=h.journal, replay_store=h.nonces,
        namespace_bindings=bindings,
        control_checkpoint=signed, pinned_public_keys=pubs,
    )
    checkpoint = report["joint_checkpoint"]
    assert checkpoint["kind"] == "SC043_STORAGE_REPLAY_NAMESPACE_KEY"
    assert checkpoint["local_cross_ledger_checkpoint_verified"] is True
    assert checkpoint["local_namespace_binding_key_commitment_signed"] is True
    assert checkpoint["actual_external_latest_attested"] is False
    assert checkpoint["external_immutability_certified"] is False
    assert report["production_authorized"] is False
    commitment = bindings.source_binding_key_commitment()[
        "binding_key_commitment"
    ]
    assert commitment not in json.dumps(report)
