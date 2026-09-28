"""SC011: synthetic complete offsite checkpoint ancestry and rollback checks.

The source caller supplies a claimed complete ordered history. This cannot
prove an untrusted sink disclosed its REAL latest checkpoint or is WORM.
"""
import json
from dataclasses import replace

import pytest

from simplee_cloud.checkpoints import (
    SignedCheckpoint, deliver_source_checkpoint, verify_checkpoint,
    verify_source_checkpoint_sequence,
)
from simplee_cloud.contracts import CloudError, IntegrityError
from simplee_cloud.tests.test_sc005_recovery import (
    FakeImmutableAnchor, event, journal, keys, seal,
)


def history(tmp_path):
    j = journal(tmp_path)
    private, pubs = keys()
    event(j, "source-event-1")
    first = seal(j, private, pubs)
    event(j, "source-event-2")
    second = seal(j, private, pubs, previous=first)
    event(j, "source-event-3")
    third = seal(j, private, pubs, previous=second)
    sink = FakeImmutableAnchor()
    refs = [
        deliver_source_checkpoint(
            signed=cp, sink=sink, pinned_public_keys=pubs,
            journal=j, mode="source_test",
        )
        for cp in (first, second, third)
    ]
    return j, private, pubs, sink, refs, (first, second, third)


def verified(chain, j, pubs):
    return verify_source_checkpoint_sequence(
        checkpoints=chain, pinned_public_keys=pubs,
        journal=j, mode="source_test",
    )


def resign(signed, private, **changes):
    claims = json.loads(signed.payload)
    claims.update(changes)
    payload = json.dumps(
        claims, sort_keys=True, separators=(",", ":"), ensure_ascii=True,
    ).encode()
    return SignedCheckpoint(payload=payload, signature=private.sign(payload))


def test_exact_readback_and_complete_three_checkpoint_lineage(tmp_path):
    j, private, pubs, sink, refs, chain = history(tmp_path)
    recovered = tuple(sink.get(ref) for ref in refs)
    assert recovered == chain
    report = verified(recovered, j, pubs)
    assert report["status"] == "SOURCE_ONLY_SIGNED_LINEAGE_CHECKED"
    assert report["checkpoint_count"] == 3
    assert report["latest_event_count"] == 3
    assert report["latest_checkpoint_ref"] == json.loads(chain[-1].payload)["checkpoint_ref"]
    assert report["local_prefix_matches"] is True
    assert report["actual_external_latest_attested"] is False
    assert report["independent_offsite_immutability_certified"] is False
    assert report["production_authorized"] is False


@pytest.mark.parametrize("fault", ["skip_middle", "reverse", "duplicate", "only_tip"])
def test_incomplete_out_of_order_or_replayed_history_denied(tmp_path, fault):
    j, _, pubs, _, _, (first, second, third) = history(tmp_path)
    bad = {
        "skip_middle": [first, third],
        "reverse": [second, first],
        "duplicate": [first, second, second],
        "only_tip": [third],
    }[fault]
    with pytest.raises(IntegrityError, match="lineage|nonmonotonic"):
        verified(bad, j, pubs)


def test_validly_signed_but_forked_external_parent_is_denied(tmp_path):
    j, private, pubs, _, _, (first, second, third) = history(tmp_path)
    fork = resign(second, private, previous_checkpoint_sha256="f" * 64)
    assert verify_checkpoint(fork, pinned_public_keys=pubs, journal=j)["event_count"] == 2
    with pytest.raises(IntegrityError, match="lineage gap or fork"):
        verified([first, fork], j, pubs)


def test_validly_signed_nonmonotonic_checkpoint_is_denied(tmp_path):
    j, private, pubs, _, _, (first, second, third) = history(tmp_path)
    old_head = verify_checkpoint(first, pinned_public_keys=pubs, journal=j)["head_sha256"]
    duplicate_count = resign(
        second, private, event_count=1,
        head_sha256=old_head, previous_checkpoint_sha256=first.sha256,
    )
    assert verify_checkpoint(duplicate_count, pinned_public_keys=pubs, journal=j)["event_count"] == 1
    with pytest.raises(IntegrityError, match="nonmonotonic"):
        verified([first, duplicate_count], j, pubs)


def test_bad_signature_and_wrong_trust_root_denied(tmp_path):
    j, _, pubs, _, _, (first, second, third) = history(tmp_path)
    tampered = replace(second, signature=second.signature[:-1] +
                       bytes([second.signature[-1] ^ 1]))
    with pytest.raises(IntegrityError):
        verified([first, tampered], j, pubs)
    other_private, other_public = keys()
    with pytest.raises(IntegrityError):
        verified([first, second, third], j, other_public)


def test_local_journal_prefix_rollback_denied(tmp_path):
    j, _, pubs, _, _, chain = history(tmp_path)
    from simplee_cloud.journal import SQLiteOperationalJournal
    empty = SQLiteOperationalJournal(
        tmp_path / "independent-empty-journal" / "operations.sqlite",
        mode="source_test",
    )
    with pytest.raises(IntegrityError):
        verified(chain, empty, pubs)


def test_source_can_not_claim_the_input_was_actual_latest_checkpoint(tmp_path):
    j, private, pubs, _, _, (first, second, third) = history(tmp_path)
    earlier_valid_prefix = verified([first, second], j, pubs)
    assert earlier_valid_prefix["latest_event_count"] == 2
    assert earlier_valid_prefix["actual_external_latest_attested"] is False
    assert earlier_valid_prefix["production_authorized"] is False


def test_missing_or_excessive_history_and_default_live_mode_denied(tmp_path):
    j, _, pubs, _, _, chain = history(tmp_path)
    with pytest.raises(CloudError):
        verified([], j, pubs)
    with pytest.raises(CloudError):
        verified([chain[0]] * 257, j, pubs)
    with pytest.raises(CloudError, match="runtime disabled"):
        verify_source_checkpoint_sequence(
            checkpoints=chain, pinned_public_keys=pubs, journal=j,
        )
