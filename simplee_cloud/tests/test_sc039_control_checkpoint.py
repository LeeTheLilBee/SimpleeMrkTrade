"""SC039 joint storage/replay/namespace signed control checkpoint source tests."""
import json
import sqlite3
from dataclasses import replace

import pytest

from simplee_cloud.control_checkpoints import (
    SignedControlCheckpoint,
    deliver_source_control_checkpoint,
    seal_source_control_checkpoint,
    verify_control_checkpoint,
    verify_source_control_checkpoint_sequence,
)
from simplee_cloud.contracts import CloudError, IntegrityError
from simplee_cloud.namespace_bindings import SQLiteNamespaceBindingLedger
from simplee_cloud.tests.test_sc004b_bound_port import Harness, PEER
from simplee_cloud.tests.test_sc005_recovery import keys


class FakeControlSink:
    def __init__(self):
        self.items = {}
        self.put_calls = 0

    def put_if_absent(self, reference, checkpoint):
        self.put_calls += 1
        if reference in self.items:
            raise CloudError("control checkpoint already stored")
        self.items[reference] = checkpoint

    def get(self, reference):
        return self.items[reference]


def prepared(tmp_path):
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
        pinned_public_keys=pubs,
        previous=previous, mode="source_test",
    )


def verify(signed, h, bindings, pubs):
    return verify_control_checkpoint(
        signed, pinned_public_keys=pubs,
        journal=h.journal, replay_store=h.nonces,
        namespace_bindings=bindings,
    )


def sequence(checkpoints, h, bindings, pubs):
    return verify_source_control_checkpoint_sequence(
        checkpoints=checkpoints, pinned_public_keys=pubs,
        journal=h.journal, replay_store=h.nonces,
        namespace_bindings=bindings, mode="source_test",
    )


def add_read(h, request_id):
    assert h.port.read_encrypted(
        grant=h.grant(request_id, "READ_CIPHERTEXT"),
        authenticated_transport_peer=PEER,
        request_id=request_id,
    ) == h.data


def add_namespace(bindings, suffix):
    bindings.enroll_source_binding(
        entity_id=f"synthetic-entity-{suffix}",
        namespace=f"{suffix:064x}",
    )


def resign(signed, private, **changes):
    doc = json.loads(signed.payload)
    doc.update(changes)
    payload = json.dumps(
        doc, sort_keys=True, separators=(",", ":"), ensure_ascii=True,
    ).encode()
    return SignedControlCheckpoint(payload, private.sign(payload))


def test_joint_control_checkpoint_commits_all_three_heads_and_exact_readback(tmp_path):
    h, bindings, private, pubs = prepared(tmp_path)
    signed = seal(h, bindings, private, pubs)
    doc = verify(signed, h, bindings, pubs)
    assert doc["storage_event_count"] == h.journal.verify_chain()["event_count"]
    assert doc["storage_head_sha256"] == h.journal.verify_chain()["head_sha256"]
    assert doc["replay_event_count"] == h.nonces.verify_chain()["event_count"]
    assert doc["replay_head_sha256"] == h.nonces.verify_chain()["head_sha256"]
    assert doc["namespace_event_count"] == bindings.verify_chain()["event_count"]
    assert doc["namespace_head_sha256"] == bindings.verify_chain()["head_sha256"]

    sink = FakeControlSink()
    ref = deliver_source_control_checkpoint(
        signed=signed, sink=sink, pinned_public_keys=pubs,
        journal=h.journal, replay_store=h.nonces,
        namespace_bindings=bindings, mode="source_test",
    )
    assert sink.get(ref) == signed
    assert sink.put_calls == 1


def test_independent_progress_in_each_ledger_forms_one_contiguous_lineage(tmp_path):
    h, bindings, private, pubs = prepared(tmp_path)
    first = seal(h, bindings, private, pubs)

    add_read(h, "read-1")
    second = seal(h, bindings, private, pubs, previous=first)

    add_namespace(bindings, 2)
    third = seal(h, bindings, private, pubs, previous=second)

    report = sequence([first, second, third], h, bindings, pubs)
    assert report["checkpoint_count"] == 3
    assert report["latest_storage_event_count"] == h.journal.verify_chain()["event_count"]
    assert report["latest_replay_event_count"] == h.nonces.verify_chain()["event_count"]
    assert report["latest_namespace_event_count"] == bindings.verify_chain()["event_count"]
    assert report["storage_prefix_matches"] is True
    assert report["replay_prefix_matches"] is True
    assert report["namespace_prefix_matches"] is True
    assert report["actual_external_latest_attested"] is False
    assert report["production_authorized"] is False


def test_namespace_ledger_tamper_invalidates_otherwise_valid_control_checkpoint(tmp_path):
    h, bindings, private, pubs = prepared(tmp_path)
    signed = seal(h, bindings, private, pubs)
    with sqlite3.connect(bindings.path) as db:
        db.execute("DROP TRIGGER bindings_block_update")
        db.execute("UPDATE bindings SET namespace_digest=?", ("f" * 64,))
    with pytest.raises(IntegrityError, match="namespace prefix unavailable"):
        verify(signed, h, bindings, pubs)


def test_storage_or_replay_tamper_still_invalidates_control_checkpoint(tmp_path):
    h, bindings, private, pubs = prepared(tmp_path)
    signed = seal(h, bindings, private, pubs)

    with sqlite3.connect(h.journal.path) as db:
        db.execute("DROP TRIGGER events_block_update")
        db.execute("UPDATE events SET event_type='altered' WHERE seq=1")
    with pytest.raises(IntegrityError):
        verify(signed, h, bindings, pubs)

    # Build a fresh fixture for replay tamper so the prior journal corruption
    # does not mask the independent failure.
    h2, bindings2, private2, pubs2 = prepared(tmp_path / "other")
    signed2 = seal(h2, bindings2, private2, pubs2)
    with sqlite3.connect(h2.nonces.path) as db:
        db.execute("DROP TRIGGER consumed_block_update")
        db.execute("UPDATE consumed SET expires_at=expires_at+1")
    with pytest.raises(IntegrityError, match="replay prefix unavailable"):
        verify(signed2, h2, bindings2, pubs2)


@pytest.mark.parametrize("fault", ["drop", "payload", "signature", "wrong_type"])
def test_external_sink_ack_without_exact_control_readback_denies(tmp_path, fault):
    h, bindings, private, pubs = prepared(tmp_path)
    signed = seal(h, bindings, private, pubs)

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
                    payload=self.item.payload[:-1] +
                    bytes([self.item.payload[-1] ^ 1]),
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
        deliver_source_control_checkpoint(
            signed=signed, sink=sink, pinned_public_keys=pubs,
            journal=h.journal, replay_store=h.nonces,
            namespace_bindings=bindings, mode="source_test",
        )
    assert sink.put_calls == 1


def test_missing_middle_fork_or_duplicate_vector_denied(tmp_path):
    h, bindings, private, pubs = prepared(tmp_path)
    first = seal(h, bindings, private, pubs)
    add_read(h, "read-1")
    second = seal(h, bindings, private, pubs, previous=first)
    add_namespace(bindings, 2)
    third = seal(h, bindings, private, pubs, previous=second)

    with pytest.raises(IntegrityError, match="lineage gap or fork"):
        sequence([first, third], h, bindings, pubs)

    fork = resign(
        second, private, previous_checkpoint_sha256="f" * 64,
    )
    assert verify(fork, h, bindings, pubs)["namespace_event_count"] == json.loads(
        second.payload
    )["namespace_event_count"]
    with pytest.raises(IntegrityError, match="lineage gap or fork"):
        sequence([first, fork], h, bindings, pubs)

    with pytest.raises(IntegrityError, match="lineage gap|duplicate|nonmonotonic"):
        sequence([first, first], h, bindings, pubs)


def test_same_three_ledger_vector_cannot_be_sealed_again_without_progress(tmp_path):
    h, bindings, private, pubs = prepared(tmp_path)
    first = seal(h, bindings, private, pubs)
    with pytest.raises(CloudError, match="monotonic ledger progress"):
        seal(h, bindings, private, pubs, previous=first)


def test_historical_namespace_prefix_remains_verifiable_after_later_enrollment(tmp_path):
    h, bindings, private, pubs = prepared(tmp_path)
    first = seal(h, bindings, private, pubs)
    first_doc = json.loads(first.payload)
    add_namespace(bindings, 2)
    assert bindings.verify_chain()["event_count"] > first_doc["namespace_event_count"]
    assert bindings.checkpoint_head(
        first_doc["namespace_event_count"]
    ) == first_doc["namespace_head_sha256"]
    assert verify(first, h, bindings, pubs)["namespace_head_sha256"] == (
        first_doc["namespace_head_sha256"]
    )


def test_valid_older_control_prefix_never_claims_true_external_latest(tmp_path):
    h, bindings, private, pubs = prepared(tmp_path)
    first = seal(h, bindings, private, pubs)
    add_read(h, "read-1")
    second = seal(h, bindings, private, pubs, previous=first)
    add_namespace(bindings, 2)
    third = seal(h, bindings, private, pubs, previous=second)

    older = sequence([first, second], h, bindings, pubs)
    assert older["actual_external_latest_attested"] is False
    assert older["independent_offsite_immutability_certified"] is False
    assert older["production_authorized"] is False
    assert verify(third, h, bindings, pubs)["previous_checkpoint_sha256"] == second.sha256


def test_wrong_signer_and_live_modes_are_disabled(tmp_path):
    h, bindings, private, pubs = prepared(tmp_path)
    signed = seal(h, bindings, private, pubs)
    _, other_pubs = keys()
    with pytest.raises(IntegrityError):
        verify_control_checkpoint(
            signed, pinned_public_keys=other_pubs,
            journal=h.journal, replay_store=h.nonces,
            namespace_bindings=bindings,
        )

    with pytest.raises(CloudError, match="signing disabled"):
        seal_source_control_checkpoint(
            journal=h.journal, replay_store=h.nonces,
            namespace_bindings=bindings,
            key_id="synthetic-external-signer",
            external_signer=private.sign, pinned_public_keys=pubs,
        )
    with pytest.raises(CloudError, match="lineage runtime disabled"):
        verify_source_control_checkpoint_sequence(
            checkpoints=[signed], pinned_public_keys=pubs,
            journal=h.journal, replay_store=h.nonces,
            namespace_bindings=bindings,
        )
