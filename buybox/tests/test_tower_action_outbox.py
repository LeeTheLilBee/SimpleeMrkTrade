"""BBX022-026: local unsent outbox regression, synthetic data only."""
from __future__ import annotations

import importlib.util
import json
import os
import sqlite3
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from buybox.core import new_opportunity
from buybox.store import connect, save
from buybox.tower_action_outbox import (
    BuyBoxActionOutboxError, EXPIRED, PENDING, STALE,
    prepare_local_tower_action_draft, reconcile_local_tower_action_drafts,
    read_local_tower_action_draft,
)

NOW = datetime(2026, 9, 27, 10, 0, tzinfo=timezone.utc)
KEY = "request-atm-00000001"


class LocalTowerActionOutboxTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.path = Path(self.directory.name) / "synthetic.sqlite3"
        self.db = connect(str(self.path))
        self.op = save(
            self.db,
            new_opportunity("atm", "Synthetic, not a seller listing", "95000"),
            event_type="OpportunityCreated",
        )

    def tearDown(self):
        self.db.close()
        self.directory.cleanup()

    def prepare(self, **overrides):
        args = {
            "requested_action": "REQUEST_TELLER_READINESS",
            "claimed_identity_ref": "claimed-owner-ref",
            "claimed_entity_ref": "claimed-entity-ref",
            "classification": "CONFIDENTIAL",
            "idempotency_key": KEY,
            "now_utc": NOW,
        }
        args.update(overrides)
        return prepare_local_tower_action_draft(self.db, self.op["id"], **args)

    def row(self, key=KEY):
        return self.db.execute(
            "SELECT * FROM buybox_tower_action_drafts WHERE idempotency_key=?",
            (key,),
        ).fetchone()

    def test_exact_saved_snapshot_is_persisted_unsent_not_approved(self):
        result = self.prepare()
        self.assertEqual(result["state"], PENDING)
        for key in ("authorizes_action", "submitted_to_tower", "tower_receipt_present"):
            self.assertFalse(result[key])
        self.assertEqual(result["teller_readiness"], "UNKNOWN")
        self.assertEqual(result["opportunity_revision"], 1)
        stored = self.row()
        packet = json.loads(stored["packet_json"])
        self.assertEqual(packet["input_snapshot_digest"], result["input_snapshot_digest"])
        self.assertEqual(packet["opportunity_revision"], 1)
        self.assertEqual(packet["request_id"], result["request_id"])
        self.assertEqual(packet["idempotency_key"] != KEY, True)  # server-produced draft key
        self.assertNotIn("asking_price", stored["packet_json"])
        self.assertNotIn("broker_balance", stored["packet_json"])
        self.assertNotIn("document_bytes", stored["packet_json"])
        self.assertTrue(len(result["packet_sha256"]) == 64)

    def test_same_retry_key_keeps_one_row_and_unmodified_request(self):
        first = self.prepare()
        again = self.prepare()
        self.assertEqual(first, again)
        self.assertEqual(
            self.db.execute("SELECT COUNT(*) FROM buybox_tower_action_drafts").fetchone()[0],
            1,
        )
        self.assertEqual(self.row()["state"], PENDING)

    def test_same_key_different_intent_conflicts_without_mutation(self):
        self.prepare()
        old = dict(self.row())
        with self.assertRaisesRegex(BuyBoxActionOutboxError, "IDEMPOTENCY_KEY_CONFLICT"):
            self.prepare(requested_action="DRAFT_LOI")
        self.assertEqual(dict(self.row()), old)

    def test_change_in_deal_revision_marks_draft_stale_and_immutable(self):
        first = self.prepare()
        old = self.row()["packet_json"]
        edited = dict(self.op, asking_price="89000.00")
        updated = save(self.db, edited, expected_revision=1)
        result = read_local_tower_action_draft(self.db, KEY, now_utc=NOW)
        self.assertEqual(result["state"], STALE)
        self.assertEqual(result["terminal_reason"], "CURRENT_SOURCE_CHANGED_OR_UNAVAILABLE")
        self.assertEqual(self.row()["packet_json"], old)
        self.assertEqual(first["opportunity_revision"], 1)
        self.assertEqual(updated["version"], 2)
        retry = self.prepare()
        self.assertEqual(retry["state"], STALE)
        self.assertEqual(retry["request_id"], first["request_id"])
        newer = self.prepare(idempotency_key="request-atm-00000002")
        self.assertEqual(newer["state"], PENDING)
        self.assertEqual(newer["opportunity_revision"], 2)
        self.assertNotEqual(newer["input_snapshot_digest"], first["input_snapshot_digest"])

    def test_draft_expiry_is_terminal_and_never_renewed_by_retry(self):
        first = self.prepare()
        future = NOW + timedelta(seconds=121)
        result = read_local_tower_action_draft(self.db, KEY, now_utc=future)
        self.assertEqual(result["state"], EXPIRED)
        self.assertEqual(result["terminal_reason"], "LOCAL_DRAFT_EXPIRED")
        retry = self.prepare(now_utc=future)
        self.assertEqual(retry["state"], EXPIRED)
        self.assertEqual(retry["request_id"], first["request_id"])

    def test_corrupted_persisted_source_never_stays_pending(self):
        self.prepare()
        self.db.execute(
            "UPDATE revisions SET digest=? WHERE opportunity_id=?",
            ("0" * 64, self.op["id"]),
        )
        self.db.commit()
        statuses = reconcile_local_tower_action_drafts(
            self.db, self.op["id"], now_utc=NOW,
        )
        self.assertEqual(len(statuses), 1)
        self.assertEqual(statuses[0]["state"], STALE)
        self.assertFalse(statuses[0]["authorizes_action"])

    def test_status_survives_reopen_and_is_not_process_local(self):
        first = self.prepare()
        with connect(str(self.path)) as second:
            status = read_local_tower_action_draft(second, KEY, now_utc=NOW)
        self.assertEqual(status["request_id"], first["request_id"])
        self.assertEqual(status["state"], PENDING)

    def test_duplicate_retry_uses_unique_key_across_separate_connections(self):
        first = self.prepare()
        second = connect(str(self.path))
        try:
            response = prepare_local_tower_action_draft(
                second, self.op["id"],
                requested_action="REQUEST_TELLER_READINESS",
                claimed_identity_ref="claimed-owner-ref",
                claimed_entity_ref="claimed-entity-ref",
                classification="CONFIDENTIAL",
                idempotency_key=KEY,
                now_utc=NOW,
            )
            self.assertEqual(response["request_id"], first["request_id"])
        finally:
            second.close()
        self.assertEqual(
            self.db.execute("SELECT COUNT(*) FROM buybox_tower_action_drafts").fetchone()[0],
            1,
        )

    def test_invalid_inputs_no_approved_or_sent_row(self):
        for key in ("bad/key", "", "few", "x" * 129):
            with self.subTest(key=key):
                with self.assertRaises(BuyBoxActionOutboxError):
                    self.prepare(idempotency_key=key)
        with self.assertRaisesRegex(Exception, "UNSUPPORTED_ACTION"):
            self.prepare(requested_action="APPROVE_ALL")
        with self.assertRaisesRegex(BuyBoxActionOutboxError, "UTC_TIME_REQUIRED"):
            self.prepare(now_utc=datetime(2026, 9, 27))
        self.assertEqual(
            self.db.execute(
                "SELECT COUNT(*) FROM sqlite_master "
                "WHERE type='table' AND name='buybox_tower_action_drafts'"
            ).fetchone()[0], 0,
        )

    def test_fails_with_dirty_transaction_instead_of_committing_other_changes(self):
        self.db.execute(
            "INSERT INTO events(opportunity_id,revision,event_type,occurred_at,details_json) "
            "VALUES(?,?,?,?,?)",
            (self.op["id"], 1, "TestUncommitted", NOW.isoformat(), "{}"),
        )
        with self.assertRaisesRegex(
            BuyBoxActionOutboxError, "FRESH_DATABASE_TRANSACTION_REQUIRED"
        ):
            self.prepare()
        self.db.rollback()
        self.assertEqual(
            self.db.execute(
                "SELECT COUNT(*) FROM events WHERE event_type='TestUncommitted'"
            ).fetchone()[0], 0,
        )

    def test_database_constraint_refuses_forged_authorized_states(self):
        self.prepare()
        with self.assertRaises(sqlite3.IntegrityError):
            self.db.execute(
                "UPDATE buybox_tower_action_drafts SET state='APPROVED' "
                "WHERE idempotency_key=?",
                (KEY,),
            )
        self.db.rollback()
        self.assertEqual(self.row()["state"], PENDING)

    def test_unknown_key_safe_and_no_external_call(self):
        self.assertIsNone(
            read_local_tower_action_draft(
                self.db, "request-nonexistent-000001", now_utc=NOW,
            )
        )
        from buybox import tower_action_outbox as module
        source = Path(module.__file__).read_text(encoding="utf-8")
        self.assertNotIn("requests.post(", source)
        self.assertNotIn("from observatory.", source)
        self.assertNotIn("from vault.", source)
        self.assertNotIn("TELLER_TOWER_TOKEN_SECRET", source)

    def test_persisted_packet_validates_against_pinned_canonical_tower(self):
        filename = os.environ.get("BUYBOX_TOWER_ACTION_CONTRACT_PATH")
        if not filename:
            self.skipTest("Exact Tower validator is provided by CI")
        spec = importlib.util.spec_from_file_location("pinned_tower_action", filename)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        self.prepare()
        packet = json.loads(self.row()["packet_json"])
        valid = module.validate_buybox_action_draft(packet, now_utc=NOW)
        self.assertEqual(valid, packet)
        status = module.prepare_buybox_action_review(valid, now_utc=NOW)
        self.assertEqual(status["state"], "UNTRUSTED_DRAFT")
        self.assertFalse(status["authorizes_action"])


if __name__ == "__main__":
    unittest.main()
