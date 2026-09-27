"""BBX052–056: post-close proposal is never Tower or receiving-system acceptance."""
from __future__ import annotations

import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from buybox.core import new_opportunity
from buybox.store import connect, save
from buybox.post_close_handoff_proposal import (
    VERSION, PostCloseProposalError, prepare_untrusted_post_close_handoff,
)

NOW = datetime(2026, 9, 27, 13, tzinfo=timezone.utc)


class SourceOnlyPostCloseTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.db = connect(str(Path(self.tmp.name) / "synthetic.sqlite3"))
        self.atm = save(self.db, new_opportunity("atm", "Fictional route", "95000"))

    def tearDown(self):
        self.db.close()
        self.tmp.cleanup()

    def propose(self, op=None, now=NOW):
        return prepare_untrusted_post_close_handoff(
            self.db, (op or self.atm)["id"], now_utc=now,
        )

    def assert_hold(self, proposal):
        self.assertEqual(proposal["schema_version"], VERSION)
        self.assertEqual(proposal["state"], "SOURCE_ONLY_UNSENT")
        for field in (
            "local_stage_is_external_proof", "tower_close_receipt_verified",
            "title_or_contract_verified", "recipient_independent_acceptance",
            "idempotency_and_replay_verified", "owned_asset_record_created",
            "money_movement_authorized", "tower_handoff_issued",
            "external_call_made", "can_mark_operational",
        ):
            self.assertIs(proposal[field], False)

    def test_atm_listing_is_not_an_owned_route_or_receiver_ack(self):
        before = self.db.execute(
            "SELECT COUNT(*) FROM events WHERE opportunity_id=?", (self.atm["id"],)
        ).fetchone()[0]
        result = self.propose()
        self.assert_hold(result)
        self.assertEqual(result["proposed_recipient"], "simplee_on_the_go")
        self.assertIn("LOCAL_STAGE_NOT_ACQUIRED", result["reason_codes"])
        self.assertIn("NO_INCLUDED_SERIAL_NUMBERED_ATM_RECORDS", result["reason_codes"])
        self.assertEqual(result["included_atm_count_from_local_records"], 0)
        self.assertEqual(
            before, self.db.execute(
                "SELECT COUNT(*) FROM events WHERE opportunity_id=?", (self.atm["id"],)
            ).fetchone()[0]
        )

    def test_even_a_locally_recorded_acquired_label_is_not_proof(self):
        self.atm = save(
            self.db,
            {**self.atm, "lifecycle": "ACQUIRED", "vertical_data": {
                "machine_inventory": [{
                    "serial_number": "SYNTHETIC", "included": True,
                    "ownership": "SELLER_OWNED", "title_and_lien_clearance": "UNVERIFIED",
                }]
            }},
            expected_revision=1,
        )
        result = self.propose()
        self.assert_hold(result)
        self.assertEqual(result["included_atm_count_from_local_records"], 1)
        self.assertNotIn("LOCAL_STAGE_NOT_ACQUIRED", result["reason_codes"])
        self.assertIn(
            "TITLE_CONTRACT_AND_LIEN_PROOF_NOT_INDEPENDENTLY_VERIFIED",
            result["reason_codes"],
        )
        self.assertFalse(result["owned_asset_record_created"])

    def test_multifamily_target_is_grounds_only_and_no_property_is_created(self):
        op = save(self.db, new_opportunity("multifamily", "Fictional flats", "200000"))
        result = self.propose(op)
        self.assert_hold(result)
        self.assertEqual(result["proposed_recipient"], "grounds")
        self.assertIsNone(result["included_atm_count_from_local_records"])
        self.assertFalse(result["recipient_independent_acceptance"])

    def test_other_vertical_has_no_invented_operational_receiver(self):
        op = save(self.db, new_opportunity("land_farm", "Fictional farmland"))
        result = self.propose(op)
        self.assert_hold(result)
        self.assertIsNone(result["proposed_recipient"])
        self.assertIn(
            "NO_OPERATIONAL_RECEIVER_CONTRACT_FOR_VERTICAL", result["reason_codes"],
        )

    def test_revision_and_original_digest_are_bound_to_actual_saved_source(self):
        first = self.propose()
        self.atm = save(
            self.db, {**self.atm, "asking_price": "89000.00"}, expected_revision=1,
        )
        next_one = self.propose()
        self.assertEqual(next_one["opportunity_revision"], 2)
        self.assertNotEqual(next_one["input_snapshot_digest"], first["input_snapshot_digest"])
        self.assertNotEqual(next_one["proposal_fingerprint"], first["proposal_fingerprint"])
        self.assert_hold(next_one)

    def test_corrupted_saved_source_or_naive_time_fail_closed(self):
        self.db.execute(
            "UPDATE revisions SET digest=? WHERE opportunity_id=? AND revision=1",
            ("0" * 64, self.atm["id"]),
        )
        self.db.commit()
        with self.assertRaises(PostCloseProposalError):
            self.propose()
        with self.assertRaisesRegex(PostCloseProposalError, "AWARE_TIME_REQUIRED"):
            self.propose(now=datetime(2026, 9, 27))

    def test_no_runtime_receiver_or_money_or_vault_transport(self):
        import buybox.post_close_handoff_proposal as source
        content = Path(source.__file__).read_text(encoding="utf-8")
        for forbidden in (
            "requests.post(", "from observatory.", "from vault.",
            "from teller.", "from grounds.", "broker.place_order(",
            "os.environ[", "mark_as_acquired(",
        ):
            self.assertNotIn(forbidden, content)


if __name__ == "__main__":
    unittest.main()
