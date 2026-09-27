"""VAJ002–006: internal journal sequencing is not independently verified archival."""
from pathlib import Path
import sqlite3
import pytest
from vault.archival_transaction_journal import ArchivalJournal, JournalError

HASH = lambda c: c * 64

def seed(tmp_path, entity="entity-A", request="request-A", version="version-A"):
    journal = ArchivalJournal(tmp_path / "journal.sqlite")
    assert journal.begin(
        request_id=request, entity_id=entity, evidence_id="evidence-A",
        version_id=version,
    ) == "RECEIVED"
    return journal

def test_stale_writes_cannot_mutate_event_history(tmp_path):
    j = seed(tmp_path)
    with pytest.raises(JournalError, match="stale"):
        j.advance(request_id="request-A", expected_state="QUARANTINED", to_state="VERIFIED", receipt_digest=HASH("a"))
    assert j.status("request-A") == "RECEIVED"
    assert j.verify_chain("request-A")
    with sqlite3.connect(j.path) as db:
        assert db.execute("SELECT COUNT(*) FROM workflow_events").fetchone()[0] == 1

def test_ambiguous_cloud_write_remains_reconcile_required_not_archived(tmp_path):
    j = seed(tmp_path)
    j.advance(request_id="request-A", expected_state="RECEIVED", to_state="QUARANTINED")
    j.advance(request_id="request-A", expected_state="QUARANTINED", to_state="VERIFIED", receipt_digest=HASH("a"))
    j.advance(request_id="request-A", expected_state="VERIFIED", to_state="ENCRYPTED", receipt_digest=HASH("b"))
    j.advance(request_id="request-A", expected_state="ENCRYPTED", to_state="RECONCILE_REQUIRED")
    assert j.status("request-A") == "RECONCILE_REQUIRED"
    with pytest.raises(JournalError, match="cloud commit missing"):
        j.advance(request_id="request-A", expected_state="RECONCILE_REQUIRED", to_state="ARCHIVED", receipt_digest=HASH("d"))
    assert j.status("request-A") == "RECONCILE_REQUIRED"
    assert j.verify_chain("request-A")

def test_entity_scoped_internal_summary_does_not_leak_other_workflow(tmp_path):
    j = seed(tmp_path)
    assert j.owner_summary("entity-A") == {"RECEIVED": 1}
    assert j.owner_summary("entity-B") == {}
    assert j.status("request-A") == "RECEIVED"  # internal-only, never expose this API unauthenticated

def test_tamper_with_sqlite_history_is_detected_but_not_administrator_proof(tmp_path):
    j = seed(tmp_path)
    with sqlite3.connect(j.path) as db:
        db.execute("DROP TRIGGER events_no_update")
        db.execute("UPDATE workflow_events SET to_state='ARCHIVED' WHERE request_id='request-A'")
    assert not j.verify_chain("request-A")
    # This test uses local administrator access deliberately. The chain needs
    # independently anchored checkpoints before a real retention claim.

def test_no_external_receipt_authentication_or_live_endpoint_is_claimed():
    source = Path(__file__).with_name("archival_transaction_journal.py").read_text(encoding="utf-8")
    for forbidden in (
        "from simplee_cloud.", "from buybox.", "requests.post(",
        "verify_tower_attestation(", "@app.route(", "boto3.client(",
    ):
        assert forbidden not in source
