"""SC025: every historical backup reservation must follow an ACKed exact primary."""
import hashlib
import os
import sqlite3

import pytest

from simplee_cloud.contracts import IntegrityError
from simplee_cloud.journal import (
    _backup_tag, _hash_event, _now, _reservation_hash,
)
from simplee_cloud.service import namespace_digest
from simplee_cloud.source_status import owner_safe_source_snapshot
from simplee_cloud.tests.test_sc004b_bound_port import Harness, PEER


def write(h, *, entity="trust"):
    return h.port.write(
        grant=h.grant("write-1", "WRITE_CIPHERTEXT", entity=entity),
        authenticated_transport_peer=PEER,
        request_id="write-1", envelope=h.data,
    )


def scope(h, entity="trust"):
    return namespace_digest(entity, namespace_key=h.source._namespace_key)


def append_event(db, *, event, tag, namespace, code="-"):
    previous = db.execute(
        "SELECT seq,event_hash FROM events ORDER BY seq DESC LIMIT 1"
    ).fetchone()
    seq = 1 if previous is None else previous[0] + 1
    prior_hash = "0" * 64 if previous is None else previous[1]
    at = _now()
    digest = _hash_event(seq, event, tag, namespace, code, at, prior_hash)
    db.execute(
        "INSERT INTO events VALUES(?,?,?,?,?,?,?,?)",
        (seq, event, tag, namespace, code, at, prior_hash, digest),
    )


def inject_fully_chain_committed_backup(
    h, *, entity="trust", source_ref=None, source_sha=None, backup_request="back-1",
):
    """Simulate an old accepted source-test journal row, not new API bypass."""
    ns = scope(h, entity)
    tag = _backup_tag(ns, backup_request)
    values = (
        tag, ns, source_ref or h.ref, source_sha or h.digest,
        "backups/" + os.urandom(24).hex(),
        hashlib.sha256(b"SCB1" + os.urandom(64)).hexdigest(),
        68, "synthetic-key", _now(),
    )
    with sqlite3.connect(h.journal.path) as db:
        db.execute("INSERT INTO backup_intents VALUES(?,?,?,?,?,?,?,?,?)", values)
        append_event(
            db, event="BACKUP_RESERVED", tag=tag, namespace=ns,
            code=_reservation_hash("BACKUP_RESERVED", values),
        )
    return values


def test_valid_journaled_backup_from_acknowledged_primary_passes_historical_check(tmp_path):
    h = Harness(tmp_path)
    primary = write(h)
    receipt = h.port.create_encrypted_backup(
        grant=h.grant("backup-1", "BACKUP_CIPHERTEXT"),
        authenticated_transport_peer=PEER, request_id="backup-1",
    )
    assert h.journal.verify_chain()["valid"] is True
    assert h.journal.health()["backup_count"] == 1
    h.journal.transition(
        namespace=primary.namespace_digest, request_id="write-1",
        next_state="REPLAY_INTEGRITY_FAILURE",
    )
    # A later damaged primary must not rewrite the truth of an earlier
    # properly acknowledged source or invalidate its independent copy.
    assert h.journal.verify_chain()["valid"] is True
    assert h.journal.health()["backup_count"] == 1
    assert receipt.source_ciphertext_sha256 == h.digest


def test_old_self_consistent_orphan_backup_event_no_primary_fails_all_owner_paths(tmp_path):
    h = Harness(tmp_path)
    inject_fully_chain_committed_backup(h)
    with pytest.raises(IntegrityError, match="exact primary journal source"):
        h.journal.verify_chain()
    with pytest.raises(IntegrityError):
        h.journal.health()
    with pytest.raises(IntegrityError):
        owner_safe_source_snapshot(h.journal)
    with pytest.raises(IntegrityError):
        h.journal.checkpoint_head(1)


def test_reservation_followed_by_backup_before_primary_ack_never_retroactively_valid(tmp_path):
    h = Harness(tmp_path)
    ns = scope(h)
    h.journal.reserve_write(
        namespace=ns, request_id="write-1",
        object_ref=h.ref, digest=h.digest, size=len(h.data),
    )
    inject_fully_chain_committed_backup(h)
    with sqlite3.connect(h.journal.path) as db:
        from simplee_cloud.journal import _request_tag
        append_event(
            db, event="WRITE_ACKNOWLEDGED",
            tag=_request_tag(ns, "write-1"), namespace=ns,
        )
    with pytest.raises(IntegrityError, match="earlier acknowledged"):
        h.journal.verify_chain()


def test_primary_hold_at_time_of_backup_reservation_is_detected_even_after_prior_ack(tmp_path):
    h = Harness(tmp_path)
    original = write(h)
    h.journal.transition(
        namespace=original.namespace_digest, request_id="write-1",
        next_state="REPLAY_INTEGRITY_FAILURE",
    )
    inject_fully_chain_committed_backup(h)
    with pytest.raises(IntegrityError, match="earlier acknowledged"):
        h.journal.verify_chain()


@pytest.mark.parametrize("fault", ["ref", "sha", "entity"])
def test_backup_cannot_borrow_another_primary_identity_in_historical_chain(tmp_path, fault):
    h = Harness(tmp_path)
    write(h)
    options = {}
    if fault == "ref":
        options["source_ref"] = h.source.new_object_ref()
    elif fault == "sha":
        options["source_sha"] = "f" * 64
    else:
        options["entity"] = "different-entity"
    inject_fully_chain_committed_backup(h, **options)
    with pytest.raises(IntegrityError, match="exact primary"):
        h.journal.verify_chain()


def test_multiple_distinct_backup_destinations_can_share_one_properly_acked_source(tmp_path):
    h = Harness(tmp_path)
    write(h)
    for request in ("backup-1", "backup-2"):
        receipt = h.port.create_encrypted_backup(
            grant=h.grant(request, "BACKUP_CIPHERTEXT"),
            authenticated_transport_peer=PEER, request_id=request,
        )
        assert receipt.source_object_ref == h.ref
    assert h.journal.verify_chain()["valid"] is True
    assert h.journal.health()["backup_count"] == 2
    coverage = h.journal.source_backup_coverage()
    assert coverage["acknowledged_primary_object_count"] == 1
    assert coverage["matched_backup_ack_count"] == 1
    assert coverage["independent_failure_domain_certified"] is False
