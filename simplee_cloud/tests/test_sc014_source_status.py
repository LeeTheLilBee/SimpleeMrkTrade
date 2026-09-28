"""SC014 verifies owner-safe source-only aggregation without leaked identifiers."""
import json
import os
import sqlite3

import pytest

from simplee_cloud.contracts import AccessDenied, CloudError, IntegrityError
from simplee_cloud.source_status import (
    owner_safe_source_markdown, owner_safe_source_snapshot,
)
from simplee_cloud.tests.test_sc004b_bound_port import Harness, PEER, AcceptThenTimeout
from simplee_cloud.tests.test_sc005b_backup_operations import AcceptBackupThenTimeout


def write(h):
    return h.port.write(
        grant=h.grant("write-1", "WRITE_CIPHERTEXT"),
        authenticated_transport_peer=PEER,
        request_id="write-1", envelope=h.data,
    )


def source_snapshot(h):
    return owner_safe_source_snapshot(h.journal)


def test_empty_source_snapshot_stays_no_go_and_never_asserts_live_health(tmp_path):
    h = Harness(tmp_path)
    result = source_snapshot(h)
    assert result["status"] == "SOURCE_ONLY_NO_GO"
    assert result["attention"] == "NO_LOCAL_SOURCE_FLAGS"
    assert result["production_authorized"] is False
    assert result["live_provider_health_verified"] is False
    assert result["external_alert_delivery_certified"] is False
    assert result["independent_recovery_certified"] is False
    assert result["primary_write_count"] == 0
    assert result["backend_error_event_count"] == 0
    assert [x["key"] for x in result["work_queue"]] == ["source_only_external_gates"]
    rendered = owner_safe_source_markdown(h.journal)
    assert "NOT A LIVE PROVIDER STATUS" in rendered
    assert "No flags in this local source-test journal" in rendered
    assert "not" in rendered.lower()


def test_approved_write_and_backup_have_no_fabricated_live_certification(tmp_path):
    h = Harness(tmp_path)
    write(h)
    h.port.create_encrypted_backup(
        grant=h.grant("backup-1", "BACKUP_CIPHERTEXT"),
        authenticated_transport_peer=PEER, request_id="backup-1",
    )
    result = source_snapshot(h)
    assert result["primary_write_count"] == 1
    assert result["backup_reservation_count"] == 1
    assert result["total_incident_records"] == 0
    assert result["production_authorized"] is False
    assert result["live_provider_health_verified"] is False


def test_pending_uncertain_primary_and_backup_render_action_first(tmp_path):
    h = Harness(tmp_path / "primary", primary=AcceptThenTimeout())
    with pytest.raises(OSError):
        write(h)
    source = source_snapshot(h)
    assert source["pending_primary_count"] == 1
    assert source["primary_integrity_hold_count"] == 0
    assert source["production_authorized"] is False
    assert source["work_queue"][0]["key"] == "primary_reconciliation"
    assert "ORIGINAL write ID" in source["work_queue"][0]["next_action"]

    b = Harness(tmp_path / "backup")
    write(b)
    b.backup.backup_backend = AcceptBackupThenTimeout()
    with pytest.raises(OSError):
        b.port.create_encrypted_backup(
            grant=b.grant("backup-1", "BACKUP_CIPHERTEXT"),
            authenticated_transport_peer=PEER, request_id="backup-1",
        )
    result = source_snapshot(b)
    assert result["pending_backup_count"] == 1
    assert result["backup_integrity_hold_count"] == 0
    assert result["work_queue"][0]["key"] == "backup_reconciliation"
    assert "generate another backup" in result["work_queue"][0]["next_action"]


def test_corrupt_primary_and_backend_outage_get_distinct_cards(tmp_path):
    h = Harness(tmp_path)
    receipt = write(h)
    # Deliberately corrupt an ACKed primary object, then replay under a fresh
    # source-only grant. The durable journal moves to integrity failure.
    path = h.primary.root / receipt.namespace_digest / h.ref
    path.write_bytes(b"VLT1" + os.urandom(len(h.data) - 4))
    with pytest.raises(IntegrityError):
        write(h)
    health = source_snapshot(h)
    assert health["primary_integrity_hold_count"] == 1
    assert health["backend_error_event_count"] == 0
    assert health["work_queue"][0]["key"] == "primary_integrity"

    # Separate synthetic outage event stays in its own nonterminal category.
    h.journal.record_backend_incident(
        namespace=receipt.namespace_digest, request_id="read-2",
        code="PRIMARY_REPLAY_BACKEND_ERROR",
    )
    after = source_snapshot(h)
    assert after["primary_integrity_hold_count"] == 1
    assert after["backend_error_event_count"] == 1
    assert any(card["key"] == "backend_outages" for card in after["work_queue"])
    assert after["external_alert_delivery_certified"] is False


def test_report_redacts_raw_request_entity_paths_and_exception_text(tmp_path):
    h = Harness(tmp_path)
    write(h)
    h.journal.record_backend_incident(
        namespace="a" * 64, request_id="private-request-identifier",
        code="PRIMARY_REPLAY_BACKEND_ERROR",
    )
    snapshot = source_snapshot(h)
    data = json.dumps(snapshot)
    markdown = owner_safe_source_markdown(h.journal)
    for forbidden in (
        "private-request-identifier", "objects/" + h.ref.split("/")[1],
        str(h.journal.path), h.data.hex(), "synthetic-tower",
    ):
        assert forbidden not in data
        assert forbidden not in markdown
    assert "Backend-error events" in markdown
    assert "NO GO" in markdown


def test_corrupt_local_journal_cannot_be_presented_as_verified_owner_status(tmp_path):
    h = Harness(tmp_path)
    write(h)
    with sqlite3.connect(h.journal.path) as db:
        db.execute("DROP TRIGGER intents_block_update")
        db.execute("UPDATE intents SET ciphertext_sha256=?", ("0" * 64,))
    with pytest.raises(IntegrityError):
        owner_safe_source_snapshot(h.journal)
    with pytest.raises(IntegrityError):
        owner_safe_source_markdown(h.journal)


def test_arbitrary_or_untrusted_health_mapping_cannot_grant_owner_status(tmp_path):
    with pytest.raises(CloudError):
        owner_safe_source_snapshot({
            "status": "LIVE_GO", "production_authorized": True,
        })
    with pytest.raises(CloudError):
        owner_safe_source_snapshot(None)
