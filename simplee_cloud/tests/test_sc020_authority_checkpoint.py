"""SC020 joint storage/replay signed authority checkpoint source tests."""
import json
import os
import sqlite3
from dataclasses import replace

import pytest

from simplee_cloud.authority_checkpoints import (
    SignedAuthorityCheckpoint,
    deliver_source_authority_checkpoint,
    seal_source_authority_checkpoint,
    verify_authority_checkpoint,
    verify_source_authority_checkpoint_sequence,
)
from simplee_cloud.contracts import CloudError, IntegrityError
from simplee_cloud.tests.test_sc004b_bound_port import Harness, PEER
from simplee_cloud.tests.test_sc005_recovery import keys


class FakeAuthoritySink:
    def __init__(self):
        self.items = {}
        self.put_calls = 0

    def put_if_absent(self, reference, checkpoint):
        self.put_calls += 1
        if reference in self.items:
            raise CloudError("authority checkpoint already stored")
        self.items[reference] = checkpoint

    def get(self, reference):
        return self.items[reference]


def prepared(tmp_path):
    h = Harness(tmp_path)
    h.port.write(
        grant=h.grant("write-1", "WRITE_CIPHERTEXT"),
        authenticated_transport_peer=PEER,
        request_id="write-1", envelope=h.data,
    )
    private, pubs = keys()
    return h, private, pubs


def seal(h, private, pubs, previous=None):
    return seal_source_authority_checkpoint(
        journal=h.journal,
        replay_store=h.nonces,
        key_id="synthetic-external-signer",
        external_signer=private.sign,
        pinned_public_keys=pubs,
        previous=previous,
        mode="source_test",
    )


def add_read(h, request_id):
    assert h.port.read_encrypted(
        grant=h.grant(request_id, "READ_CIPHERTEXT"),
        authenticated_transport_peer=PEER,
        request_id=request_id,
    ) == h.data


def verify(signed, h, pubs):
    return verify_authority_checkpoint(
        signed,
        pinned_public_keys=pubs,
        journal=h.journal,
        replay_store=h.nonces,
    )


def sequence(checkpoints, h, pubs):
    return verify_source_authority_checkpoint_sequence(
        checkpoints=checkpoints,
        pinned_public_keys=pubs,
        journal=h.journal,
        replay_store=h.nonces,
        mode="source_test",
    )


def resign(signed, private, **changes):
    doc = json.loads(signed.payload)
    doc.update(changes)
    payload = json.dumps(
        doc, sort_keys=True, separators=(",", ":"), ensure_ascii=True,
    ).encode()
    return SignedAuthorityCheckpoint(payload, private.sign(payload))


def test_joint_checkpoint_commits_storage_and_replay_heads_and_exact_readback(tmp_path):
    h, private, pubs = prepared(tmp_path)
    signed = seal(h, private, pubs)
    doc = verify(signed, h, pubs)
    assert doc["storage_event_count"] == h.journal.verify_chain()["event_count"]
    assert doc["storage_head_sha256"] == h.journal.verify_chain()["head_sha256"]
    assert doc["replay_event_count"] == h.nonces.verify_chain()["event_count"]
    assert doc["replay_head_sha256"] == h.nonces.verify_chain()["head_sha256"]
    sink = FakeAuthoritySink()
    ref = deliver_source_authority_checkpoint(
        signed=signed, sink=sink, pinned_public_keys=pubs,
        journal=h.journal, replay_store=h.nonces, mode="source_test",
    )
    assert sink.get(ref) == signed
    assert sink.put_calls == 1


def test_storage_and_replay_progress_form_one_contiguous_authority_lineage(tmp_path):
    h, private, pubs = prepared(tmp_path)
    first = seal(h, private, pubs)
    add_read(h, "read-1")
    second = seal(h, private, pubs, previous=first)
    add_read(h, "read-2")
    third = seal(h, private, pubs, previous=second)
    report = sequence([first, second, third], h, pubs)
    assert report["checkpoint_count"] == 3
    assert report["latest_storage_event_count"] == h.journal.verify_chain()["event_count"]
    assert report["latest_replay_event_count"] == h.nonces.verify_chain()["event_count"]
    assert report["storage_prefix_matches"] is True
    assert report["replay_prefix_matches"] is True
    assert report["actual_external_latest_attested"] is False
    assert report["production_authorized"] is False


def test_replay_ledger_tamper_invalidates_joint_checkpoint(tmp_path):
    h, private, pubs = prepared(tmp_path)
    signed = seal(h, private, pubs)
    with sqlite3.connect(h.nonces.path) as db:
        db.execute("DROP TRIGGER consumed_block_update")
        db.execute("UPDATE consumed SET expires_at=expires_at+1")
    with pytest.raises(IntegrityError, match="replay prefix unavailable"):
        verify(signed, h, pubs)


def test_storage_journal_tamper_invalidates_joint_checkpoint(tmp_path):
    h, private, pubs = prepared(tmp_path)
    signed = seal(h, private, pubs)
    with sqlite3.connect(h.journal.path) as db:
        db.execute("DROP TRIGGER events_block_update")
        db.execute("UPDATE events SET event_type='altered' WHERE seq=1")
    with pytest.raises(IntegrityError):
        verify(signed, h, pubs)


@pytest.mark.parametrize("fault", ["drop", "payload", "signature", "wrong_type"])
def test_external_sink_ack_without_exact_authority_checkpoint_readback_denies(
    tmp_path, fault,
):
    h, private, pubs = prepared(tmp_path)
    signed = seal(h, private, pubs)

    class BadSink:
        def __init__(self):
            self.item = None
            self.put_calls = 0
        def put_if_absent(self, reference, checkpoint):
            self.put_calls += 1
            self.item = checkpoint
        def get(self, reference):
            if fault == "drop":
                raise KeyError("not found")
            if fault == "payload":
                return replace(
                    self.item,
                    payload=self.item.payload[:-1] + bytes([self.item.payload[-1] ^ 1]),
                )
            if fault == "signature":
                return replace(
                    self.item,
                    signature=self.item.signature[:-1] +
                    bytes([self.item.signature[-1] ^ 1]),
                )
            return {"payload": self.item.payload, "signature": self.item.signature}

    sink = BadSink()
    with pytest.raises(IntegrityError):
        deliver_source_authority_checkpoint(
            signed=signed, sink=sink, pinned_public_keys=pubs,
            journal=h.journal, replay_store=h.nonces, mode="source_test",
        )
    assert sink.put_calls == 1


def test_missing_middle_or_forked_checkpoint_denied(tmp_path):
    h, private, pubs = prepared(tmp_path)
    first = seal(h, private, pubs)
    add_read(h, "read-1")
    second = seal(h, private, pubs, previous=first)
    add_read(h, "read-2")
    third = seal(h, private, pubs, previous=second)

    with pytest.raises(IntegrityError, match="lineage gap or fork"):
        sequence([first, third], h, pubs)

    fork = resign(
        second, private, previous_checkpoint_sha256="f" * 64,
    )
    assert verify(fork, h, pubs)["replay_event_count"] == json.loads(
        second.payload
    )["replay_event_count"]
    with pytest.raises(IntegrityError, match="lineage gap or fork"):
        sequence([first, fork], h, pubs)


def test_same_vector_cannot_be_sealed_again_without_ledger_progress(tmp_path):
    h, private, pubs = prepared(tmp_path)
    first = seal(h, private, pubs)
    with pytest.raises(CloudError, match="monotonic ledger progress"):
        seal(h, private, pubs, previous=first)


def test_valid_older_joint_prefix_never_claims_true_external_latest(tmp_path):
    h, private, pubs = prepared(tmp_path)
    first = seal(h, private, pubs)
    add_read(h, "read-1")
    second = seal(h, private, pubs, previous=first)
    add_read(h, "read-2")
    third = seal(h, private, pubs, previous=second)
    older = sequence([first, second], h, pubs)
    assert older["actual_external_latest_attested"] is False
    assert older["independent_offsite_immutability_certified"] is False
    assert older["production_authorized"] is False
    assert verify(third, h, pubs)["previous_checkpoint_sha256"] == second.sha256


def test_wrong_signer_and_default_live_mode_are_denied(tmp_path):
    h, private, pubs = prepared(tmp_path)
    signed = seal(h, private, pubs)
    other_private, other_pubs = keys()
    with pytest.raises(IntegrityError):
        verify_authority_checkpoint(
            signed,
            pinned_public_keys=other_pubs,
            journal=h.journal,
            replay_store=h.nonces,
        )
    with pytest.raises(CloudError, match="signing disabled"):
        seal_source_authority_checkpoint(
            journal=h.journal, replay_store=h.nonces,
            key_id="synthetic-external-signer",
            external_signer=private.sign, pinned_public_keys=pubs,
        )
    with pytest.raises(CloudError, match="lineage runtime disabled"):
        verify_source_authority_checkpoint_sequence(
            checkpoints=[signed], pinned_public_keys=pubs,
            journal=h.journal, replay_store=h.nonces,
        )


def test_replay_prefix_head_supports_historical_joint_checkpoint(tmp_path):
    h, private, pubs = prepared(tmp_path)
    first = seal(h, private, pubs)
    first_doc = json.loads(first.payload)
    add_read(h, "read-later")
    assert h.nonces.verify_chain()["event_count"] > first_doc["replay_event_count"]
    assert h.nonces.checkpoint_head(
        first_doc["replay_event_count"]
    ) == first_doc["replay_head_sha256"]
    assert verify(first, h, pubs)["replay_head_sha256"] == first_doc["replay_head_sha256"]
