"""SC010: source signed checkpoint delivery must prove exact read-back.

All sinks and Ed25519 signers are local synthetic fakes. An exact read-back
is necessary, not sufficient, for externally certified immutability/WORM.
"""
from dataclasses import replace

import pytest

from simplee_cloud.checkpoints import (
    SignedCheckpoint, deliver_source_checkpoint,
)
from simplee_cloud.contracts import CloudError, IntegrityError
from simplee_cloud.tests.test_sc005_recovery import (
    FakeImmutableAnchor, event, journal, keys, seal,
)


def fixture(tmp_path):
    j = journal(tmp_path)
    event(j, "source-request-1")
    private, pubs = keys()
    signed = seal(j, private, pubs)
    return j, pubs, signed


def deliver(j, pubs, signed, sink):
    return deliver_source_checkpoint(
        signed=signed, sink=sink, pinned_public_keys=pubs,
        journal=j, mode="source_test",
    )


def test_valid_source_create_only_sink_returns_only_after_exact_signed_readback(tmp_path):
    j, pubs, signed = fixture(tmp_path)
    sink = FakeImmutableAnchor()
    ref = deliver(j, pubs, signed, sink)
    assert sink.get(ref) == signed
    assert j.verify_chain()["valid"] is True
    with pytest.raises(CloudError, match="already externally anchored"):
        deliver(j, pubs, signed, sink)


def test_sink_ack_that_drops_checkpoint_does_not_get_success(tmp_path):
    j, pubs, signed = fixture(tmp_path)

    class AckButDrop:
        put_calls = 0
        def put_if_absent(self, reference, checkpoint):
            self.put_calls += 1
        def get(self, reference):
            raise KeyError("object not present")

    sink = AckButDrop()
    with pytest.raises(IntegrityError, match="read-back unavailable"):
        deliver(j, pubs, signed, sink)
    assert sink.put_calls == 1  # never automatically retry provider uncertainty


@pytest.mark.parametrize("fault", ["signature", "payload", "not_checkpoint", "different_valid"])
def test_sink_ack_then_substitutes_object_is_rejected(tmp_path, fault):
    j, pubs, signed = fixture(tmp_path)

    class Substitute:
        def __init__(self):
            self.items = {}
            self.put_calls = 0
        def put_if_absent(self, reference, checkpoint):
            self.put_calls += 1
            self.items[reference] = checkpoint
        def get(self, reference):
            original = self.items[reference]
            if fault == "signature":
                return replace(original, signature=original.signature[:-1] + bytes([original.signature[-1] ^ 1]))
            if fault == "payload":
                return replace(original, payload=original.payload[:-1] + b"x")
            if fault == "not_checkpoint":
                return {"payload": original.payload, "signature": original.signature}
            return SignedCheckpoint(
                payload=original.payload, signature=b"x" * 64,
            )
    sink = Substitute()
    with pytest.raises(IntegrityError, match="differs"):
        deliver(j, pubs, signed, sink)
    assert sink.put_calls == 1
    assert j.verify_chain()["valid"] is True


def test_missing_read_interface_fails_before_put(tmp_path):
    j, pubs, signed = fixture(tmp_path)

    class OneWay:
        called = False
        def put_if_absent(self, reference, checkpoint):
            self.called = True

    sink = OneWay()
    with pytest.raises(CloudError, match="read-back required"):
        deliver(j, pubs, signed, sink)
    assert sink.called is False


def test_readback_provider_unavailable_keeps_uncertain_hold_without_duplicate_put(tmp_path):
    j, pubs, signed = fixture(tmp_path)

    class AckThenOffline:
        def __init__(self):
            self.items = {}
            self.put_calls = 0
        def put_if_absent(self, reference, checkpoint):
            self.put_calls += 1
            self.items[reference] = checkpoint
        def get(self, reference):
            raise OSError("synthetic offsite access unavailable")

    sink = AckThenOffline()
    with pytest.raises(IntegrityError, match="reconcile independently"):
        deliver(j, pubs, signed, sink)
    assert len(sink.items) == 1  # physical write may be present
    assert sink.put_calls == 1
    assert j.verify_chain()["valid"] is True


def test_source_checkpointer_remains_default_disabled_even_with_readback(tmp_path):
    j, pubs, signed = fixture(tmp_path)
    with pytest.raises(CloudError, match="not authorized"):
        deliver_source_checkpoint(
            signed=signed, sink=FakeImmutableAnchor(),
            pinned_public_keys=pubs, journal=j,
        )
