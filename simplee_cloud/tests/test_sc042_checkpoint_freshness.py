"""SC042 owner desk checkpoint freshness versus valid historical prefix tests."""
import pytest

from simplee_cloud.authority_checkpoints import seal_source_authority_checkpoint
from simplee_cloud.control_checkpoints import seal_source_control_checkpoint
from simplee_cloud.namespace_bindings import SQLiteNamespaceBindingLedger
from simplee_cloud.owner_evidence_desk import owner_local_evidence_desk
from simplee_cloud.service import namespace_digest
from simplee_cloud.tests.test_sc004b_bound_port import Harness, PEER
from simplee_cloud.tests.test_sc005_recovery import keys


def write(h):
    return h.port.write(
        grant=h.grant("write-1", "WRITE_CIPHERTEXT"),
        authenticated_transport_peer=PEER,
        request_id="write-1", envelope=h.data,
    )


def add_read(h, request="read-later"):
    return h.port.read_encrypted(
        grant=h.grant(request, "READ_CIPHERTEXT"),
        authenticated_transport_peer=PEER,
        request_id=request,
    )


def bindings(h, tmp_path):
    ledger = SQLiteNamespaceBindingLedger(
        tmp_path / "namespace" / "bindings.sqlite",
        binding_key=b"m" * 32, mode="source_test",
    )
    ledger.enroll_source_binding(
        entity_id="trust",
        namespace=namespace_digest("trust", namespace_key=h.source._namespace_key),
    )
    return ledger


def control(h, ledger):
    private, pubs = keys()
    signed = seal_source_control_checkpoint(
        journal=h.journal, replay_store=h.nonces,
        namespace_bindings=ledger,
        key_id="synthetic-external-signer",
        external_signer=private.sign, pinned_public_keys=pubs,
        mode="source_test",
    )
    return signed, pubs


def old_checkpoint(h):
    private, pubs = keys()
    signed = seal_source_authority_checkpoint(
        journal=h.journal, replay_store=h.nonces,
        key_id="synthetic-external-signer",
        external_signer=private.sign, pinned_public_keys=pubs,
        mode="source_test",
    )
    return signed, pubs


def desk(h, **kwargs):
    return owner_local_evidence_desk(
        journal=h.journal, replay_store=h.nonces, **kwargs,
    )


def test_no_checkpoint_has_no_fake_freshness_claim(tmp_path):
    h = Harness(tmp_path)
    report = desk(h)
    checkpoint = report["joint_checkpoint"]
    assert checkpoint["freshness_status"] == "NOT_EVALUATED"
    assert checkpoint["matches_current_local_heads"] is None
    assert checkpoint["storage_events_since_checkpoint"] is None
    assert checkpoint["replay_events_since_checkpoint"] is None
    assert checkpoint["namespace_events_since_checkpoint"] is None


def test_fresh_sc039_checkpoint_matches_current_three_local_heads(tmp_path):
    h = Harness(tmp_path / "cloud")
    write(h)
    ledger = bindings(h, tmp_path)
    signed, pubs = control(h, ledger)
    report = desk(
        h, control_checkpoint=signed,
        namespace_bindings=ledger, pinned_public_keys=pubs,
    )
    checkpoint = report["joint_checkpoint"]
    assert checkpoint["freshness_status"] == "SOURCE_ONLY_LOCAL_CHECKPOINT_CURRENT"
    assert checkpoint["matches_current_local_heads"] is True
    assert checkpoint["storage_events_since_checkpoint"] == 0
    assert checkpoint["replay_events_since_checkpoint"] == 0
    assert checkpoint["namespace_events_since_checkpoint"] == 0
    assert checkpoint["actual_external_latest_attested"] is False
    assert report["production_authorized"] is False


def test_valid_sc039_prefix_becomes_explicitly_stale_after_storage_and_replay_progress(tmp_path):
    h = Harness(tmp_path / "cloud")
    write(h)
    ledger = bindings(h, tmp_path)
    signed, pubs = control(h, ledger)
    add_read(h)
    report = desk(
        h, control_checkpoint=signed,
        namespace_bindings=ledger, pinned_public_keys=pubs,
    )
    checkpoint = report["joint_checkpoint"]
    assert checkpoint["local_cross_ledger_checkpoint_verified"] is True
    assert checkpoint["freshness_status"] == "SOURCE_ONLY_LOCAL_CHECKPOINT_STALE"
    assert checkpoint["matches_current_local_heads"] is False
    assert checkpoint["storage_events_since_checkpoint"] > 0
    assert checkpoint["replay_events_since_checkpoint"] > 0
    assert checkpoint["namespace_events_since_checkpoint"] == 0
    assert checkpoint["external_immutability_certified"] is False


def test_valid_sc039_prefix_becomes_stale_when_only_namespace_registry_progresses(tmp_path):
    h = Harness(tmp_path / "cloud")
    write(h)
    ledger = bindings(h, tmp_path)
    signed, pubs = control(h, ledger)
    ledger.enroll_source_binding(
        entity_id="future-entity", namespace="f" * 64,
    )
    report = desk(
        h, control_checkpoint=signed,
        namespace_bindings=ledger, pinned_public_keys=pubs,
    )
    checkpoint = report["joint_checkpoint"]
    assert checkpoint["freshness_status"] == "SOURCE_ONLY_LOCAL_CHECKPOINT_STALE"
    assert checkpoint["matches_current_local_heads"] is False
    assert checkpoint["storage_events_since_checkpoint"] == 0
    assert checkpoint["replay_events_since_checkpoint"] == 0
    assert checkpoint["namespace_events_since_checkpoint"] == 1
    assert report["namespace_binding_readiness"]["unused_enrolled_namespace_count"] >= 1


def test_legacy_sc020_checkpoint_reports_storage_replay_freshness_only(tmp_path):
    h = Harness(tmp_path)
    write(h)
    signed, pubs = old_checkpoint(h)
    current = desk(h, checkpoint=signed, pinned_public_keys=pubs)
    summary = current["joint_checkpoint"]
    assert summary["kind"] == "SC020_STORAGE_REPLAY"
    assert summary["freshness_status"] == "SOURCE_ONLY_LOCAL_CHECKPOINT_CURRENT"
    assert summary["matches_current_local_heads"] is True
    assert summary["namespace_events_since_checkpoint"] is None

    add_read(h)
    stale = desk(h, checkpoint=signed, pinned_public_keys=pubs)["joint_checkpoint"]
    assert stale["local_storage_and_replay_prefix_verified"] is True
    assert stale["freshness_status"] == "SOURCE_ONLY_LOCAL_CHECKPOINT_STALE"
    assert stale["matches_current_local_heads"] is False
    assert stale["storage_events_since_checkpoint"] > 0
    assert stale["replay_events_since_checkpoint"] > 0
    assert stale["namespace_events_since_checkpoint"] is None


def test_historical_prefix_validity_never_turns_freshness_into_external_latest(tmp_path):
    h = Harness(tmp_path / "cloud")
    write(h)
    ledger = bindings(h, tmp_path)
    signed, pubs = control(h, ledger)
    add_read(h)
    ledger.enroll_source_binding(entity_id="later", namespace="e" * 64)
    report = desk(
        h, control_checkpoint=signed,
        namespace_bindings=ledger, pinned_public_keys=pubs,
    )
    checkpoint = report["joint_checkpoint"]
    assert checkpoint["local_storage_and_replay_prefix_verified"] is True
    assert checkpoint["local_namespace_prefix_verified"] is True
    assert checkpoint["matches_current_local_heads"] is False
    assert checkpoint["actual_external_latest_attested"] is False
    assert checkpoint["external_immutability_certified"] is False
    assert report["cross_ledger_point_in_time_certified"] is False
    assert report["production_authorized"] is False
