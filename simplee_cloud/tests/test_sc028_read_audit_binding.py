"""SC028: exact read request/ref/hash audit lineage before provider GET.

All authority and provider interactions are synthetic. This hardens source audit
provenance only; it is not a live access-log, SIEM or Tower/Vault certification.
"""
import sqlite3

import pytest

from simplee_cloud.contracts import CloudError, IntegrityError
from simplee_cloud.journal import _hash_event, _now, _reservation_hash, _read_tag
from simplee_cloud.service import namespace_digest
from simplee_cloud.tests.test_sc004b_bound_port import Harness, PEER


class CountGet:
    def __init__(self, actual):
        self.actual = actual
        self.calls = 0
    def get(self, namespace, ref):
        self.calls += 1
        return self.actual.get(namespace, ref)
    def put_if_absent(self, namespace, ref, body):
        return self.actual.put_if_absent(namespace, ref, body)


def write(h):
    return h.port.write(
        grant=h.grant("write-1", "WRITE_CIPHERTEXT"),
        authenticated_transport_peer=PEER,
        request_id="write-1", envelope=h.data,
    )


def read(h, request="read-1", *, ref=None, digest=None, entity="trust"):
    return h.port.read_encrypted(
        grant=h.grant(
            request, "READ_CIPHERTEXT", ref=ref, digest=digest, entity=entity,
        ),
        authenticated_transport_peer=PEER, request_id=request,
    )


def scope(h, entity="trust"):
    return namespace_digest(entity, namespace_key=h.source._namespace_key)


def append_event(db, *, event, tag, namespace, code="-"):
    previous = db.execute(
        "SELECT seq,event_hash FROM events ORDER BY seq DESC LIMIT 1"
    ).fetchone()
    seq = 1 if previous is None else previous[0] + 1
    prior = "0" * 64 if previous is None else previous[1]
    at = _now()
    digest = _hash_event(seq, event, tag, namespace, code, at, prior)
    db.execute(
        "INSERT INTO events VALUES(?,?,?,?,?,?,?,?)",
        (seq, event, tag, namespace, code, at, prior, digest),
    )


def inject_read(h, *, request="old-read", ref=None, digest=None, entity="trust"):
    ns = scope(h, entity)
    tag = _read_tag(ns, request)
    values = (tag, ns, ref or h.ref, digest or h.digest, _now())
    with sqlite3.connect(h.journal.path) as db:
        db.execute("INSERT INTO read_intents VALUES(?,?,?,?,?)", values)
        append_event(
            db, event="READ_RESERVED", tag=tag, namespace=ns,
            code=_reservation_hash("READ_RESERVED", values),
        )
    return values


def test_valid_signed_read_binds_exact_ref_hash_and_audit_events(tmp_path):
    h = Harness(tmp_path)
    write(h)
    spy = CountGet(h.primary)
    h.source._backend = spy
    assert read(h) == h.data
    assert spy.calls == 1
    ns = scope(h)
    tag = _read_tag(ns, "read-1")
    with sqlite3.connect(h.journal.path) as db:
        row = db.execute(
            """SELECT namespace_digest,object_ref,ciphertext_sha256
               FROM read_intents WHERE request_tag=?""", (tag,),
        ).fetchone()
        events = db.execute(
            """SELECT event_type FROM events WHERE request_tag=?
               ORDER BY seq""", (tag,),
        ).fetchall()
    assert row == (ns, h.ref, h.digest)
    assert [x[0] for x in events] == [
        "READ_RESERVED", "read_intent", "read_verified",
    ]
    assert h.journal.verify_chain()["valid"] is True
    assert h.port.health()["production_authorized"] is False


def test_same_read_request_can_retry_same_exact_object_but_not_rebind(tmp_path):
    h = Harness(tmp_path)
    write(h)
    spy = CountGet(h.primary)
    h.source._backend = spy
    assert read(h, "read-1") == h.data
    assert read(h, "read-1") == h.data
    assert spy.calls == 2
    with sqlite3.connect(h.journal.path) as db:
        assert db.execute("SELECT COUNT(*) FROM read_intents").fetchone()[0] == 1
        assert db.execute(
            "SELECT COUNT(*) FROM events WHERE event_type='READ_RESERVED'"
        ).fetchone()[0] == 1
        assert db.execute(
            "SELECT COUNT(*) FROM events WHERE event_type='read_verified'"
        ).fetchone()[0] == 2

    other = h.source.new_object_ref()
    with pytest.raises(CloudError, match="read idempotency conflict"):
        read(h, "read-1", ref=other)
    assert spy.calls == 2


def test_different_read_requests_may_read_same_acknowledged_ciphertext(tmp_path):
    h = Harness(tmp_path)
    write(h)
    assert read(h, "read-1") == h.data
    assert read(h, "read-2") == h.data
    with sqlite3.connect(h.journal.path) as db:
        assert db.execute("SELECT COUNT(*) FROM read_intents").fetchone()[0] == 2
    assert h.journal.verify_chain()["valid"] is True


def test_cross_entity_or_wrong_hash_creates_no_read_reservation_or_provider_get(tmp_path):
    h = Harness(tmp_path)
    write(h)
    spy = CountGet(h.primary)
    h.source._backend = spy
    with pytest.raises(CloudError, match="acknowledged matching primary"):
        read(h, "foreign", entity="different-entity")
    with pytest.raises(CloudError, match="acknowledged matching primary"):
        read(h, "wrong-sha", digest="f" * 64)
    assert spy.calls == 0
    with sqlite3.connect(h.journal.path) as db:
        assert db.execute("SELECT COUNT(*) FROM read_intents").fetchone()[0] == 0


def test_primary_hold_before_read_reservation_denies_without_provider_or_read_audit(tmp_path):
    h = Harness(tmp_path)
    stored = write(h)
    h.journal.transition(
        namespace=stored.namespace_digest, request_id="write-1",
        next_state="REPLAY_INTEGRITY_FAILURE",
    )
    spy = CountGet(h.primary)
    h.source._backend = spy
    with pytest.raises(CloudError, match="acknowledged matching primary"):
        read(h, "read-after-hold")
    assert spy.calls == 0
    with sqlite3.connect(h.journal.path) as db:
        assert db.execute("SELECT COUNT(*) FROM read_intents").fetchone()[0] == 0
        assert db.execute(
            "SELECT COUNT(*) FROM events WHERE event_type LIKE 'read_%'"
        ).fetchone()[0] == 0


def test_historically_injected_read_without_exact_primary_is_rejected(tmp_path):
    h = Harness(tmp_path)
    inject_read(h)
    with pytest.raises(IntegrityError, match="exact primary"):
        h.journal.verify_chain()


def test_read_reserved_before_primary_ack_never_becomes_valid_retroactively(tmp_path):
    h = Harness(tmp_path)
    ns = scope(h)
    h.journal.reserve_write(
        namespace=ns, request_id="write-1",
        object_ref=h.ref, digest=h.digest, size=len(h.data),
    )
    inject_read(h)
    with sqlite3.connect(h.journal.path) as db:
        from simplee_cloud.journal import _request_tag
        append_event(
            db, event="WRITE_ACKNOWLEDGED",
            tag=_request_tag(ns, "write-1"), namespace=ns,
        )
    with pytest.raises(IntegrityError, match="earlier acknowledged"):
        h.journal.verify_chain()


def test_forged_read_verified_event_without_read_reservation_fails_chain(tmp_path):
    h = Harness(tmp_path)
    write(h)
    ns = scope(h)
    tag = _read_tag(ns, "forged-read")
    with sqlite3.connect(h.journal.path) as db:
        append_event(db, event="read_intent", tag=tag, namespace=ns)
        append_event(db, event="read_verified", tag=tag, namespace=ns)
    with pytest.raises(IntegrityError, match="reserved read scope"):
        h.journal.verify_chain()


def test_public_safe_audit_api_cannot_create_read_success_without_reservation(tmp_path):
    h = Harness(tmp_path)
    ns = scope(h)
    base = {
        "request_id": "read-no-reservation",
        "tower_decision_ref": "synthetic-tower-decision",
        "namespace_digest": ns,
    }
    with pytest.raises(CloudError, match="reserved exact read scope"):
        h.journal.record_safe_event({**base, "event": "read_intent"})
    with pytest.raises(CloudError, match="reserved exact read scope"):
        h.journal.record_safe_event({**base, "event": "read_verified"})


def test_tampered_read_binding_denies_chain_owner_and_later_read(tmp_path):
    h = Harness(tmp_path)
    write(h)
    assert read(h, "read-1") == h.data
    with sqlite3.connect(h.journal.path) as db:
        db.execute("DROP TRIGGER read_intents_block_update")
        db.execute("UPDATE read_intents SET ciphertext_sha256=?", ("f" * 64,))
    with pytest.raises(IntegrityError):
        h.journal.verify_chain()
    with pytest.raises(IntegrityError):
        h.journal.source_owner_metrics()
    with pytest.raises(IntegrityError):
        read(h, "read-2")


def test_existing_old_read_audit_without_bound_row_fails_closed_on_reopen(tmp_path):
    h = Harness(tmp_path)
    write(h)
    ns = scope(h)
    tag = _read_tag(ns, "legacy-read")
    with sqlite3.connect(h.journal.path) as db:
        append_event(db, event="read_intent", tag=tag, namespace=ns)
    with pytest.raises(IntegrityError, match="reserved read scope"):
        h.journal.verify_chain()
    # Constructor is schema-only and does not claim historical data is valid;
    # any actual operational method must run full verification and deny.
    from simplee_cloud.journal import SQLiteOperationalJournal
    reopened = SQLiteOperationalJournal(h.journal.path, mode="source_test")
    with pytest.raises(IntegrityError):
        reopened.health()
