"""SC016 actual merged Vault registry source-read conformance, NOT a live resolver.

The lookup adapter is deliberately defined ONLY in this test. Real private
Vault service identity, Tower issuer/policy, scan/retention and canonical
registry transaction must be implemented by their owning workstreams.
"""
import os
import sqlite3
from dataclasses import replace

import pytest

from simplee_cloud.bound_port import SourceOnlyBoundCloudPort
from simplee_cloud.contracts import AccessDenied, valid_object_ref, valid_sha256
from simplee_cloud.tests.test_sc004b_bound_port import Harness, PEER
from simplee_cloud.tests.test_sc008_vault_finalization import SyntheticVaultAcceptance
from simplee_cloud.tower_grants import TrustedVaultScope


class SyntheticVaultCanonicalArchivedRead:
    """Internal test-only read-only adapter; never use with HTTP or client JSON."""
    def __init__(self, vault_journal, registry):
        self.vault_journal = vault_journal
        self.registry = registry
        self.records = {}

    def assign(self, *, read_request_id, archival_request_id,
               receipt_id, entity_id):
        self.records[read_request_id] = (
            archival_request_id, receipt_id, entity_id,
        )

    def __call__(self, request_id, operation):
        if operation != "READ_CIPHERTEXT":
            raise AccessDenied("read-only synthetic Vault metadata contract")
        original_request, receipt_id, entity_id = self.records[request_id]
        if not self.vault_journal.verify_chain(original_request) or (
            self.vault_journal.status(original_request) != "ARCHIVED"
        ):
            raise AccessDenied("Vault workflow has no verified ARCHIVED state")
        # Deliberately read the ACTUAL merged canonical registry schema, not
        # a fixture dict containing invented object refs/hashes. In production
        # the Vault-owning server must put this behind authenticated transport.
        with sqlite3.connect(
            "file:" + self.registry.path + "?mode=ro", uri=True,
        ) as db:
            row = db.execute(
                """SELECT object_ref,ciphertext_sha256,version_id,
                          retention_policy_id FROM archival_receipts
                   WHERE receipt_id=? AND request_id=? AND entity_id=?""",
                (receipt_id, original_request, entity_id),
            ).fetchone()
        if row is None or not (
            valid_object_ref(row[0]) and valid_sha256(row[1])
        ) or not row[2] or not row[3]:
            raise AccessDenied("no canonical archived ciphertext row")
        return TrustedVaultScope(
            request_id=request_id, entity_id=entity_id, purpose="archive",
            operation=operation, classification="owner_private",
            object_ref=row[0], ciphertext_sha256=row[1],
        )


def prepared(tmp_path, *, archive=True):
    h = Harness(tmp_path / "cloud")
    step = SyntheticVaultAcceptance(tmp_path / "vault", h)
    written = step.write()
    if archive:
        step.finalized_after_independent_source_check(written)
    lookup = SyntheticVaultCanonicalArchivedRead(step.journal, step.registry)
    port = SourceOnlyBoundCloudPort(
        operations=h.operations, tower_verifier=h.verifier,
        canonical_scope_resolver=lookup, mode="source_test",
    )
    return h, step, lookup, port, written


def read(h, port, request_id, *, entity="trust", digest=None, ref=None,
         signed=None):
    grant = signed if signed is not None else h.grant(
        request_id, "READ_CIPHERTEXT", entity=entity,
        digest=digest, ref=ref, canonical=False,
    )
    return port.read_encrypted(
        grant=grant, authenticated_transport_peer=PEER,
        request_id=request_id,
    )


def test_canonical_archived_registry_row_supplies_actual_signed_read_scope(tmp_path):
    h, step, lookup, port, receipt = prepared(tmp_path)
    lookup.assign(
        read_request_id="read-1", archival_request_id="write-1",
        receipt_id="receipt-write-1", entity_id="trust",
    )
    assert read(h, port, "read-1") == step.envelope
    assert receipt.object_ref == h.ref
    assert port.health()["real_vault_canonical_registry_connected"] is False
    assert port.health()["production_authorized"] is False


def test_cloud_ack_before_vault_registry_and_archived_state_cannot_read(tmp_path):
    h, step, lookup, port, receipt = prepared(tmp_path, archive=False)
    lookup.assign(
        read_request_id="read-1", archival_request_id="write-1",
        receipt_id="receipt-write-1", entity_id="trust",
    )
    class MustNeverRead:
        get_calls = 0
        def get(self, namespace, object_ref):
            self.get_calls += 1
            raise AssertionError("provider must not be accessed before Vault finality")
    fail_backend = MustNeverRead()
    h.source._backend = fail_backend
    with pytest.raises(AccessDenied, match="canonical Vault scope unavailable"):
        read(h, port, "read-1")
    assert fail_backend.get_calls == 0
    assert step.journal.status("write-1") == "ENCRYPTED"


def test_even_inserted_canonical_row_cannot_replace_vault_final_workflow_state(tmp_path):
    h, step, lookup, port, receipt = prepared(tmp_path, archive=False)
    step.registry.record_archival(
        receipt_id="receipt-write-1", request_id="write-1",
        entity_id="trust", evidence_id=step.evidence_id,
        version_id=step.version_id,
        original_sha256=step.meta["original_sha256"],
        ciphertext_sha256=step.meta["ciphertext_sha256"],
        object_ref=h.ref, scan_receipt_ref="synthetic-scan",
        tower_receipt_ref="synthetic-tower", retention_policy_id="synthetic-policy",
    )
    lookup.assign(
        read_request_id="read-1", archival_request_id="write-1",
        receipt_id="receipt-write-1", entity_id="trust",
    )
    with pytest.raises(AccessDenied, match="canonical Vault scope unavailable"):
        read(h, port, "read-1")
    assert step.journal.status("write-1") == "ENCRYPTED"


@pytest.mark.parametrize("wrong", ["entity", "receipt", "archival_request"])
def test_wrong_entity_receipt_or_original_request_never_reveals_object(tmp_path, wrong):
    h, step, lookup, port, receipt = prepared(tmp_path)
    values = {
        "read_request_id": "read-wrong",
        "archival_request_id": "write-1",
        "receipt_id": "receipt-write-1", "entity_id": "trust",
    }
    if wrong == "entity":
        values["entity_id"] = "foreign-entity"
    if wrong == "receipt":
        values["receipt_id"] = "not-a-receipt"
    if wrong == "archival_request":
        values["archival_request_id"] = "foreign-write"
    lookup.assign(**values)
    with pytest.raises(AccessDenied):
        read(h, port, "read-wrong", entity=values["entity_id"])
    assert port.health()["production_authorized"] is False


def test_signed_wrong_hash_and_wrong_object_denied_against_actual_registry(tmp_path):
    h, step, lookup, port, receipt = prepared(tmp_path)
    lookup.assign(
        read_request_id="read-wrong", archival_request_id="write-1",
        receipt_id="receipt-write-1", entity_id="trust",
    )
    with pytest.raises(AccessDenied, match="trusted Vault scope"):
        read(h, port, "read-wrong", digest="0" * 64)
    with pytest.raises(AccessDenied, match="trusted Vault scope"):
        read(h, port, "read-wrong", ref=h.source.new_object_ref())


def test_expired_or_revoked_source_policy_denies_even_valid_canonical_metadata(tmp_path):
    h, step, lookup, port, receipt = prepared(tmp_path)
    lookup.assign(
        read_request_id="read-1", archival_request_id="write-1",
        receipt_id="receipt-write-1", entity_id="trust",
    )
    valid_signed = h.grant("read-1", "READ_CIPHERTEXT", canonical=False)
    original_policy = h.verifier._active
    h.verifier._active = lambda policy: False
    with pytest.raises(AccessDenied, match="revoked"):
        read(h, port, "read-1", signed=valid_signed)
    h.verifier._active = original_policy
    assert read(h, port, "read-1", signed=valid_signed) == step.envelope
    with pytest.raises(AccessDenied, match="already consumed"):
        read(h, port, "read-1", signed=valid_signed)


def test_vault_journal_tampering_blocks_canonical_read_before_physical_lookup(tmp_path):
    h, step, lookup, port, receipt = prepared(tmp_path)
    lookup.assign(
        read_request_id="read-1", archival_request_id="write-1",
        receipt_id="receipt-write-1", entity_id="trust",
    )
    with sqlite3.connect(step.journal.path) as db:
        db.execute("DROP TRIGGER events_no_update")
        db.execute(
            "UPDATE workflow_events SET to_state='REJECTED' "
            "WHERE request_id='write-1' AND step=1"
        )
    with pytest.raises(AccessDenied, match="canonical Vault scope unavailable"):
        read(h, port, "read-1")
    assert port.health()["production_authorized"] is False
