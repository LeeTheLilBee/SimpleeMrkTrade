"""SC021 owner evidence desk: references cannot self-certify a live service."""
import json
import os
import sqlite3

import pytest

from simplee_cloud.authority_checkpoints import seal_source_authority_checkpoint
from simplee_cloud.contracts import CloudError, IntegrityError
from simplee_cloud.owner_evidence_desk import owner_local_evidence_desk
from simplee_cloud.provider_review import ProviderCandidate, required_provider_checks
from simplee_cloud.readiness import GATE_IDS
from simplee_cloud.tests.test_sc004b_bound_port import Harness, PEER
from simplee_cloud.tests.test_sc005_recovery import keys


def harness(tmp_path):
    return Harness(tmp_path / "cloud")


def view(h, **kwargs):
    return owner_local_evidence_desk(
        journal=h.journal, replay_store=h.nonces, **kwargs,
    )


def candidate():
    return ProviderCandidate(
        provider_label="Synthetic vendor for review only",
        software_operator="Unverified operator",
        physical_server_owner="Unverified physical owner",
        storage_jurisdiction="Unverified jurisdiction",
        external_dependencies=("Unverified network operator",),
    )


def signed(h):
    private, pubs = keys()
    sealed = seal_source_authority_checkpoint(
        journal=h.journal, replay_store=h.nonces,
        key_id="synthetic-external-signer", external_signer=private.sign,
        pinned_public_keys=pubs, mode="source_test",
    )
    return sealed, pubs


def write(h):
    return h.port.write(
        grant=h.grant("write-1", "WRITE_CIPHERTEXT"),
        authenticated_transport_peer=PEER, request_id="write-1",
        envelope=h.data,
    )


def test_empty_healthy_local_ledgers_still_production_hold(tmp_path):
    h = harness(tmp_path)
    result = view(h)
    assert result["status"] == "SOURCE_ONLY_NO_GO"
    assert result["production_authorized"] is False
    assert result["hosted_receiver_enabled"] is False
    assert result["local_storage"]["attention"] == "NO_LOCAL_SOURCE_FLAGS"
    assert result["local_replay"]["verified"] is True
    assert result["local_replay"]["consumed_count"] == 0
    assert result["joint_checkpoint"]["supplied"] is False
    assert result["provider_review"]["supplied"] is False
    assert result["provider_review"]["review_references_present"] == 0
    assert result["release_gates"]["independent_certifications"] == 0
    assert "GO" in result["next_action"]


def test_valid_signed_local_joint_prefix_is_not_external_latest_attestation(tmp_path):
    h = harness(tmp_path)
    write(h)
    checkpoint, pubs = signed(h)
    report = view(h, checkpoint=checkpoint, pinned_public_keys=pubs)
    assert report["joint_checkpoint"]["supplied"] is True
    assert report["joint_checkpoint"]["local_storage_and_replay_prefix_verified"] is True
    assert report["joint_checkpoint"]["storage_event_count"] == h.journal.verify_chain()["event_count"]
    assert report["joint_checkpoint"]["replay_event_count"] == h.nonces.verify_chain()["event_count"]
    assert report["joint_checkpoint"]["actual_external_latest_attested"] is False
    assert report["joint_checkpoint"]["external_immutability_certified"] is False
    assert report["production_authorized"] is False


def test_all_user_supplied_review_references_cannot_turn_on_production(tmp_path):
    h = harness(tmp_path)
    pointers = {key: "synthetic-review-pointer-1" for key in required_provider_checks()}
    release = {key: "synthetic-review-pointer-1" for key in GATE_IDS}
    checkpoint, pubs = signed(h)
    report = view(
        h, candidate=candidate(), provider_references=pointers,
        release_references=release, checkpoint=checkpoint,
        pinned_public_keys=pubs,
    )
    assert report["provider_review"]["missing_check_ids"] == []
    assert report["provider_review"]["review_references_present"] == len(pointers)
    assert report["provider_review"]["independently_verified"] is False
    assert report["provider_review"]["owner_approved"] is False
    assert report["provider_review"]["storage_runtime_authorized"] is False
    assert report["release_gates"]["review_references_present"] == len(GATE_IDS)
    assert report["release_gates"]["independent_certifications"] == 0
    assert report["real_tower_issuer_verified"] is False
    assert report["real_vault_registry_verified"] is False
    assert report["owner_release_recorded"] is False
    assert report["production_authorized"] is False
    wire = json.dumps(report)
    assert candidate().provider_label not in wire
    assert "synthetic-review-pointer-1" not in wire


def test_bad_or_incomplete_inputs_are_fail_closed(tmp_path):
    h = harness(tmp_path)
    with pytest.raises(CloudError, match="together"):
        view(h, candidate=candidate())
    with pytest.raises(CloudError, match="together"):
        view(h, provider_references={})
    with pytest.raises(CloudError, match="together"):
        view(h, checkpoint=signed(h)[0])
    with pytest.raises(CloudError, match="together"):
        view(h, pinned_public_keys={})
    with pytest.raises(CloudError, match="unexpected provider evidence"):
        view(h, candidate=candidate(), provider_references={"production_go": "true"})
    with pytest.raises(CloudError, match="unexpected release-gate"):
        view(h, release_references={"production_authorized": "true"})


def test_storage_chain_tamper_is_not_masked_by_safe_cards(tmp_path):
    h = harness(tmp_path)
    write(h)
    with sqlite3.connect(h.journal.path) as conn:
        conn.execute("DROP TRIGGER intents_block_update")
        conn.execute("UPDATE intents SET ciphertext_sha256=?", ("f" * 64,))
    with pytest.raises(IntegrityError):
        view(h)


def test_replay_ledger_tamper_blocks_owner_report(tmp_path):
    h = harness(tmp_path)
    write(h)
    with sqlite3.connect(h.nonces.path) as conn:
        conn.execute("DROP TRIGGER consumed_block_update")
        conn.execute("UPDATE consumed SET expires_at=expires_at+1")
    with pytest.raises(Exception, match="replay rows differ"):
        view(h)


def test_wrong_signer_or_other_journal_checkpoint_is_rejected(tmp_path):
    h = harness(tmp_path)
    write(h)
    signed_checkpoint, pubs = signed(h)
    other_private, other_pubs = keys()
    with pytest.raises(IntegrityError):
        view(h, checkpoint=signed_checkpoint, pinned_public_keys=other_pubs)
    other = harness(tmp_path / "unrelated")
    with pytest.raises(IntegrityError):
        view(other, checkpoint=signed_checkpoint, pinned_public_keys=pubs)
