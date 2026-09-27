import sqlite3
import pytest
from vault.archival_transaction_journal import ArchivalJournal,JournalError

H=lambda c:c*64
def start(tmp_path):
    journal=ArchivalJournal(tmp_path/"journal.db")
    assert journal.begin(request_id="req-1",entity_id="entity-1",evidence_id="ev-1",version_id="v-1")=="RECEIVED"
    return journal

def test_full_path_and_replay(tmp_path):
    j=start(tmp_path)
    assert j.begin(request_id="req-1",entity_id="entity-1",evidence_id="ev-1",version_id="v-1")=="RECEIVED"
    j.advance(request_id="req-1",expected_state="RECEIVED",to_state="QUARANTINED")
    j.advance(request_id="req-1",expected_state="QUARANTINED",to_state="VERIFIED",receipt_digest=H("a"))
    j.advance(request_id="req-1",expected_state="VERIFIED",to_state="ENCRYPTED",receipt_digest=H("b"))
    j.advance(request_id="req-1",expected_state="ENCRYPTED",to_state="CLOUD_COMMITTED",receipt_digest=H("c"))
    with pytest.raises(JournalError,match="distinct"):
        j.advance(request_id="req-1",expected_state="CLOUD_COMMITTED",to_state="ARCHIVED",receipt_digest=H("c"))
    assert j.status("req-1")=="CLOUD_COMMITTED"
    j.advance(request_id="req-1",expected_state="CLOUD_COMMITTED",to_state="ARCHIVED",receipt_digest=H("d"))
    assert j.verify_chain("req-1")
    assert j.owner_summary("entity-1")=={"ARCHIVED":1}
    with pytest.raises(JournalError,match="stale"):
        j.advance(request_id="req-1",expected_state="CLOUD_COMMITTED",to_state="ARCHIVED",receipt_digest=H("d"))

def test_no_false_archive_and_reconciliation(tmp_path):
    j=start(tmp_path)
    with pytest.raises(JournalError,match="invalid state"):
        j.advance(request_id="req-1",expected_state="RECEIVED",to_state="ARCHIVED",receipt_digest=H("a"))
    j.advance(request_id="req-1",expected_state="RECEIVED",to_state="QUARANTINED")
    with pytest.raises(JournalError,match="requires receipt"):
        j.advance(request_id="req-1",expected_state="QUARANTINED",to_state="VERIFIED")
    j.advance(request_id="req-1",expected_state="QUARANTINED",to_state="VERIFIED",receipt_digest=H("a"))
    j.advance(request_id="req-1",expected_state="VERIFIED",to_state="ENCRYPTED",receipt_digest=H("b"))
    j.advance(request_id="req-1",expected_state="ENCRYPTED",to_state="RECONCILE_REQUIRED")
    assert j.status("req-1")=="RECONCILE_REQUIRED"
    with pytest.raises(JournalError,match="invalid state transition"):
        j.advance(request_id="req-1",expected_state="RECONCILE_REQUIRED",to_state="ARCHIVED",receipt_digest=H("d"))
    j.advance(request_id="req-1",expected_state="RECONCILE_REQUIRED",to_state="CLOUD_COMMITTED",receipt_digest=H("c"))
    j.advance(request_id="req-1",expected_state="CLOUD_COMMITTED",to_state="ARCHIVED",receipt_digest=H("d"))
    assert j.verify_chain("req-1")

def test_entity_and_event_immutability(tmp_path):
    j=start(tmp_path)
    assert j.owner_summary("other")=={}
    with pytest.raises(JournalError,match="conflicting"):
        j.begin(request_id="req-1",entity_id="other",evidence_id="ev-1",version_id="v-1")
    with sqlite3.connect(j.path) as db:
        with pytest.raises(sqlite3.IntegrityError):
            db.execute("DELETE FROM workflow_events")

def test_reconciliation_must_reverify_cloud(tmp_path):
    j=start(tmp_path)
    j.advance(request_id="req-1",expected_state="RECEIVED",to_state="QUARANTINED")
    j.advance(request_id="req-1",expected_state="QUARANTINED",to_state="VERIFIED",receipt_digest=H("a"))
    j.advance(request_id="req-1",expected_state="VERIFIED",to_state="ENCRYPTED",receipt_digest=H("b"))
    j.advance(request_id="req-1",expected_state="ENCRYPTED",to_state="CLOUD_COMMITTED",receipt_digest=H("c"))
    j.advance(request_id="req-1",expected_state="CLOUD_COMMITTED",to_state="RECONCILE_REQUIRED")
    with pytest.raises(JournalError,match="invalid state"):
        j.advance(request_id="req-1",expected_state="RECONCILE_REQUIRED",to_state="ARCHIVED",receipt_digest=H("d"))
    j.advance(request_id="req-1",expected_state="RECONCILE_REQUIRED",to_state="CLOUD_COMMITTED",receipt_digest=H("c"))
    j.advance(request_id="req-1",expected_state="CLOUD_COMMITTED",to_state="ARCHIVED",receipt_digest=H("d"))
    assert j.verify_chain("req-1")

def test_chain_detects_mutated_workflow_digest(tmp_path):
    j=start(tmp_path)
    j.advance(request_id="req-1",expected_state="RECEIVED",to_state="QUARANTINED")
    j.advance(request_id="req-1",expected_state="QUARANTINED",to_state="VERIFIED",receipt_digest=H("a"))
    j.advance(request_id="req-1",expected_state="VERIFIED",to_state="ENCRYPTED",receipt_digest=H("b"))
    j.advance(request_id="req-1",expected_state="ENCRYPTED",to_state="CLOUD_COMMITTED",receipt_digest=H("c"))
    j.advance(request_id="req-1",expected_state="CLOUD_COMMITTED",to_state="ARCHIVED",receipt_digest=H("d"))
    assert j.verify_chain("req-1")
    with sqlite3.connect(j.path) as db:
        db.execute("UPDATE workflows SET cloud_digest=? WHERE request_id=?",(H("e"),"req-1"))
    assert not j.verify_chain("req-1")
