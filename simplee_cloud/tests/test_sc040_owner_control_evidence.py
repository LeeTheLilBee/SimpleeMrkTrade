"""SC040 owner evidence desk: namespace readiness + SC039 control checkpoint."""
import json
import sqlite3

import pytest

from simplee_cloud.authority_checkpoints import seal_source_authority_checkpoint
from simplee_cloud.control_checkpoints import seal_source_control_checkpoint
from simplee_cloud.contracts import CloudError, IntegrityError
from simplee_cloud.namespace_bindings import SQLiteNamespaceBindingLedger
from simplee_cloud.owner_evidence_desk import owner_local_evidence_desk
from simplee_cloud.provider_review import ProviderCandidate, required_provider_checks
from simplee_cloud.readiness import GATE_IDS
from simplee_cloud.service import namespace_digest
from simplee_cloud.tests.test_sc004b_bound_port import Harness, PEER
from simplee_cloud.tests.test_sc005_recovery import keys


def view(h, **kwargs):
    return owner_local_evidence_desk(
        journal=h.journal, replay_store=h.nonces, **kwargs,
    )


def bindings(h, tmp_path, *, entity="trust"):
    ledger = SQLiteNamespaceBindingLedger(
        tmp_path / "namespace" / "bindings.sqlite",
        binding_key=b"m" * 32, mode="source_test",
    )
    ledger.enroll_source_binding(
        entity_id=entity,
        namespace=namespace_digest(entity, namespace_key=h.source._namespace_key),
    )
    return ledger


def write(h, request="write-1"):
    return h.port.write(
        grant=h.grant(request, "WRITE_CIPHERTEXT"),
        authenticated_transport_peer=PEER,
        request_id=request, envelope=h.data,
    )


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


def candidate():
    return ProviderCandidate(
        provider_label="Synthetic vendor review only",
        software_operator="Unverified operator",
        physical_server_owner="Unverified hardware owner",
        storage_jurisdiction="Unverified jurisdiction",
        external_dependencies=("Unverified dependency",),
    )


def test_namespace_readiness_not_supplied_is_explicitly_not_evaluated(tmp_path):
    h = Harness(tmp_path)
    report = view(h)
    namespace = report["namespace_binding_readiness"]
    assert namespace["supplied"] is False
    assert namespace["status"] == "NOT_EVALUATED"
    assert namespace["binding_count"] is None
    assert namespace["external_registry_certified"] is False
    assert namespace["binding_key_custody_certified"] is False
    assert report["production_authorized"] is False


def test_verified_local_namespace_ledger_is_redacted_without_external_claim(tmp_path):
    h = Harness(tmp_path / "cloud")
    ledger = bindings(h, tmp_path)
    report = view(h, namespace_bindings=ledger)
    namespace = report["namespace_binding_readiness"]
    assert namespace["supplied"] is True
    assert namespace["status"] == "SOURCE_ONLY_NAMESPACE_BINDING_COVERAGE_VERIFIED"
    assert namespace["binding_count"] == 1
    assert namespace["resolver_namespace_count"] == 0
    assert namespace["missing_resolver_namespace_count"] == 0
    assert namespace["unused_enrolled_namespace_count"] == 1
    assert namespace["event_count"] == 1
    assert namespace["raw_entity_ids_persisted"] is False
    assert namespace["external_registry_certified"] is False
    assert namespace["production_authorized"] is False
    wire = json.dumps(report)
    assert "trust" not in wire
    assert namespace_digest("trust", namespace_key=h.source._namespace_key) not in wire


def test_sc039_control_checkpoint_verifies_all_three_local_prefixes_but_not_external_latest(tmp_path):
    h = Harness(tmp_path / "cloud")
    write(h)
    ledger = bindings(h, tmp_path)
    signed, pubs = control(h, ledger)
    report = view(
        h, control_checkpoint=signed, namespace_bindings=ledger,
        pinned_public_keys=pubs,
    )
    checkpoint = report["joint_checkpoint"]
    assert checkpoint["supplied"] is True
    assert checkpoint["kind"] == "SC039_STORAGE_REPLAY_NAMESPACE"
    assert checkpoint["local_storage_and_replay_prefix_verified"] is True
    assert checkpoint["local_namespace_prefix_verified"] is True
    assert checkpoint["local_cross_ledger_checkpoint_verified"] is True
    assert checkpoint["storage_event_count"] == h.journal.verify_chain()["event_count"]
    assert checkpoint["replay_event_count"] == h.nonces.verify_chain()["event_count"]
    assert checkpoint["namespace_event_count"] == ledger.verify_chain()["event_count"]
    assert checkpoint["actual_external_latest_attested"] is False
    assert checkpoint["external_immutability_certified"] is False
    assert report["cross_ledger_point_in_time_certified"] is False
    assert report["production_authorized"] is False


def test_legacy_sc020_checkpoint_remains_supported_but_does_not_claim_namespace_prefix(tmp_path):
    h = Harness(tmp_path)
    write(h)
    signed, pubs = old_checkpoint(h)
    report = view(h, checkpoint=signed, pinned_public_keys=pubs)
    checkpoint = report["joint_checkpoint"]
    assert checkpoint["kind"] == "SC020_STORAGE_REPLAY"
    assert checkpoint["local_storage_and_replay_prefix_verified"] is True
    assert checkpoint["local_namespace_prefix_verified"] is False
    assert checkpoint["local_cross_ledger_checkpoint_verified"] is False
    assert report["namespace_binding_readiness"]["status"] == "NOT_EVALUATED"
    assert report["production_authorized"] is False


def test_control_checkpoint_requires_exact_namespace_ledger_and_pinned_keys(tmp_path):
    h = Harness(tmp_path / "cloud")
    write(h)
    ledger = bindings(h, tmp_path / "one")
    signed, pubs = control(h, ledger)

    with pytest.raises(CloudError, match="requires verified namespace"):
        view(h, control_checkpoint=signed, pinned_public_keys=pubs)
    with pytest.raises(CloudError, match="pinned public keys"):
        view(h, control_checkpoint=signed, namespace_bindings=ledger)

    other = bindings(h, tmp_path / "other", entity="different-entity")
    with pytest.raises(IntegrityError, match="namespace prefix"):
        view(
            h, control_checkpoint=signed, namespace_bindings=other,
            pinned_public_keys=pubs,
        )


def test_both_checkpoint_generations_cannot_be_mixed(tmp_path):
    h = Harness(tmp_path / "cloud")
    write(h)
    ledger = bindings(h, tmp_path)
    new, pubs = control(h, ledger)
    old, _ = old_checkpoint(h)
    with pytest.raises(CloudError, match="never both"):
        view(
            h, checkpoint=old, control_checkpoint=new,
            namespace_bindings=ledger, pinned_public_keys=pubs,
        )


def test_namespace_ledger_tamper_blocks_desk_even_without_control_checkpoint(tmp_path):
    h = Harness(tmp_path / "cloud")
    ledger = bindings(h, tmp_path)
    with sqlite3.connect(ledger.path) as db:
        db.execute("DROP TRIGGER bindings_block_update")
        db.execute("UPDATE bindings SET namespace_digest=?", ("f" * 64,))
    with pytest.raises(IntegrityError):
        view(h, namespace_bindings=ledger)


def test_filled_review_references_plus_three_ledger_checkpoint_still_cannot_go(tmp_path):
    h = Harness(tmp_path / "cloud")
    write(h)
    ledger = bindings(h, tmp_path)
    signed, pubs = control(h, ledger)
    provider_refs = {
        key: "synthetic-review-pointer-1" for key in required_provider_checks()
    }
    release_refs = {
        key: "synthetic-review-pointer-1" for key in GATE_IDS
    }
    report = view(
        h,
        candidate=candidate(), provider_references=provider_refs,
        release_references=release_refs,
        control_checkpoint=signed, namespace_bindings=ledger,
        pinned_public_keys=pubs,
    )
    assert report["provider_review"]["missing_check_ids"] == []
    assert report["release_gates"]["review_references_present"] == len(GATE_IDS)
    assert report["joint_checkpoint"]["local_cross_ledger_checkpoint_verified"] is True
    assert report["namespace_binding_readiness"]["binding_count"] == 1
    assert report["actual_provider_contacted"] is False
    assert report["real_tower_issuer_verified"] is False
    assert report["real_vault_registry_verified"] is False
    assert report["owner_release_recorded"] is False
    assert report["cross_ledger_point_in_time_certified"] is False
    assert report["production_authorized"] is False

    wire = json.dumps(report)
    assert candidate().provider_label not in wire
    assert "synthetic-review-pointer-1" not in wire
    assert "trust" not in wire
