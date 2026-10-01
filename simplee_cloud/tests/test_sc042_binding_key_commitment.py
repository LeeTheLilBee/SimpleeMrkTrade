"""SC042 durable namespace binding-key source commitment regressions.

The commitment only detects accidental/wrong-key restart and partial metadata
tampering. It is NOT external KMS/HSM custody, key secrecy proof or rotation.
"""
import json
import sqlite3

import pytest

from simplee_cloud.contracts import AccessDenied, IntegrityError
from simplee_cloud.namespace_bindings import SQLiteNamespaceBindingLedger
from simplee_cloud.owner_evidence_desk import owner_local_evidence_desk
from simplee_cloud.tests.test_sc004b_bound_port import Harness


KEY = b"b" * 32
WRONG = b"x" * 32


def ledger(tmp_path, key=KEY):
    return SQLiteNamespaceBindingLedger(
        tmp_path / "namespace" / "bindings.sqlite",
        binding_key=key, mode="source_test",
    )


def test_fresh_ledger_registers_key_commitment_without_exposing_key(tmp_path):
    bindings = ledger(tmp_path)
    report = bindings.verify_chain()
    assert report["binding_key_matches_registered_commitment"] is True
    assert report["binding_key_commitment_external_anchor_certified"] is False
    assert report["binding_key_custody_certified"] is False
    with sqlite3.connect(bindings.path) as db:
        rows = db.execute(
            "SELECT schema_id,binding_key_commitment,created_at FROM ledger_metadata"
        ).fetchall()
    assert len(rows) == 1
    assert rows[0][0] == "simplee.cloud.namespace-binding-key-commitment.v1"
    assert len(rows[0][1]) == 64
    assert rows[0][1] != KEY.hex()
    assert KEY.hex() not in repr(rows)


def test_reopen_with_same_key_succeeds_wrong_key_fails_before_lookup(tmp_path):
    bindings = ledger(tmp_path)
    bindings.enroll_source_binding(entity_id="trust", namespace="a" * 64)
    reopened = ledger(tmp_path, KEY)
    assert reopened.verify_chain()["binding_count"] == 1
    with pytest.raises(AccessDenied, match="binding key commitment mismatch"):
        ledger(tmp_path, WRONG)


def test_wrong_key_cannot_generate_reassuring_owner_namespace_readiness(tmp_path):
    h = Harness(tmp_path / "cloud")
    bindings = ledger(tmp_path)
    bindings.enroll_source_binding(entity_id="trust", namespace="a" * 64)
    with pytest.raises(AccessDenied, match="binding key commitment mismatch"):
        wrong = ledger(tmp_path, WRONG)
        owner_local_evidence_desk(
            journal=h.journal, replay_store=h.nonces,
            namespace_bindings=wrong,
        )


def test_commitment_metadata_update_or_delete_is_fail_closed(tmp_path):
    bindings = ledger(tmp_path)
    bindings.enroll_source_binding(entity_id="trust", namespace="a" * 64)
    with sqlite3.connect(bindings.path) as db:
        db.execute("DROP TRIGGER ledger_metadata_block_update")
        db.execute(
            "UPDATE ledger_metadata SET binding_key_commitment=?",
            ("f" * 64,),
        )
    with pytest.raises(AccessDenied, match="binding key commitment mismatch"):
        bindings.verify_chain()

    other = ledger(tmp_path / "delete")
    other.enroll_source_binding(entity_id="trust", namespace="a" * 64)
    with sqlite3.connect(other.path) as db:
        db.execute("DROP TRIGGER ledger_metadata_block_delete")
        db.execute("DELETE FROM ledger_metadata")
    with pytest.raises(IntegrityError, match="commitment row mismatch"):
        other.verify_chain()


def test_extra_metadata_row_is_not_accepted_as_ambiguous_key_identity(tmp_path):
    bindings = ledger(tmp_path)
    with sqlite3.connect(bindings.path) as db:
        db.execute(
            "INSERT INTO ledger_metadata VALUES(?,?,?)",
            (
                "simplee.cloud.namespace-binding-key-commitment.fake",
                "f" * 64, "2000-01-01T00:00:00Z",
            ),
        )
    with pytest.raises(IntegrityError, match="commitment row mismatch"):
        bindings.verify_chain()


def test_populated_legacy_ledger_missing_commitment_requires_reviewed_migration(tmp_path):
    bindings = ledger(tmp_path)
    bindings.enroll_source_binding(entity_id="trust", namespace="a" * 64)
    with sqlite3.connect(bindings.path) as db:
        db.execute("DROP TRIGGER ledger_metadata_block_delete")
        db.execute("DELETE FROM ledger_metadata")
    with pytest.raises(IntegrityError, match="reviewed migration required"):
        ledger(tmp_path, KEY)


def test_owner_desk_exposes_match_boolean_not_commitment_or_entity(tmp_path):
    h = Harness(tmp_path / "cloud")
    bindings = ledger(tmp_path)
    bindings.enroll_source_binding(entity_id="private-entity", namespace="a" * 64)
    report = owner_local_evidence_desk(
        journal=h.journal, replay_store=h.nonces,
        namespace_bindings=bindings,
    )
    ready = report["namespace_binding_readiness"]
    assert ready["binding_key_matches_registered_commitment"] is True
    assert ready["binding_key_commitment_external_anchor_certified"] is False
    assert ready["binding_key_custody_certified"] is False
    assert report["production_authorized"] is False
    wire = json.dumps(report)
    with sqlite3.connect(bindings.path) as db:
        commitment = db.execute(
            "SELECT binding_key_commitment FROM ledger_metadata"
        ).fetchone()[0]
    assert commitment not in wire
    assert "private-entity" not in wire
    assert "a" * 64 not in wire
    assert KEY.hex() not in wire
