"""BBX027-031: proposed financing terms remain UNKNOWN and unsent."""
from __future__ import annotations

import copy
import json
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from buybox.core import new_opportunity
from buybox.store import connect, save
from buybox.teller_readiness_question import (
    SCHEMA_VERSION,
    TellerReadinessQuestionError,
    prepare_unsubmitted_teller_readiness_question,
    recheck_unsubmitted_teller_readiness_question,
)

NOW = datetime(2026, 9, 26, 22, 0, tzinfo=timezone.utc)


def terms(**changes):
    item = {
        "proposed_purchase_price": "95000.00",
        "proposed_debt_amount": "75000.00",
        "proposed_equity_amount": "20000.00",
        "estimated_closing_costs": "5000.00",
        "proposed_reserve": "12000.00",
        "funding_lane": "ATM_SET_1_ACQUISITION",
        "terms_reference": "proposal-1",
    }
    item.update(changes)
    return item


class SourceTellerQuestionTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.db = connect(str(Path(self.tmp.name) / "fake.sqlite3"))
        self.op = save(self.db, new_opportunity("atm", "Fictional eight-machine route", "95000"))
    def tearDown(self):
        self.db.close()
        self.tmp.cleanup()

    def ask(self, **overrides):
        args = dict(proposed_terms=terms(), now_utc=NOW)
        args.update(overrides)
        return prepare_unsubmitted_teller_readiness_question(self.db, self.op["id"], **args)

    def test_exact_saved_opportunity_and_canonical_terms_without_authority(self):
        result = self.ask()
        packet = result["packet"]
        self.assertEqual(packet["schema_version"], SCHEMA_VERSION)
        self.assertEqual(packet["source_app"], "buybox")
        self.assertEqual(packet["route_via"], "tower")
        self.assertEqual(packet["destination"], "teller")
        self.assertEqual(packet["requested_action"], "REQUEST_TELLER_READINESS")
        self.assertEqual(packet["opportunity_revision"], 1)
        self.assertEqual(packet["stored_asking_price"], "95000.00")
        self.assertEqual(packet["terms"]["proposed_debt_amount"], "75000.00")
        self.assertEqual(len(packet["terms_fingerprint"]), 64)
        self.assertEqual(result["state"], "LOCAL_TERMS_QUESTION_UNSUBMITTED")
        for key in (
            "atm_protected_floors_checked", "tower_identity_verified",
            "teller_issuer_verified", "external_request_sent",
            "teller_receipt_present", "authorizes_capital_deployment",
            "authorizes_acquisition",
        ):
            self.assertIs(result[key], False)
        for key in ("buyer_money_ready", "management_capacity_ready", "teller_readiness"):
            self.assertEqual(result[key], "UNKNOWN")
        self.assertNotIn("broker_balance", json.dumps(result))
        self.assertNotIn("payment_instructions", json.dumps(result))
        self.assertEqual(
            recheck_unsubmitted_teller_readiness_question(
                self.db, packet, now_utc=NOW
            )["state"], "CURRENT_LOCAL_UNSUBMITTED"
        )

    def test_distinct_atm_set_sleeves_never_pool_or_become_money_readiness(self):
        first = self.ask()["packet"]
        second = self.ask(proposed_terms=terms(
            funding_lane="ATM_SET_2_ACQUISITION",
        ))["packet"]
        self.assertNotEqual(first["terms_fingerprint"], second["terms_fingerprint"])
        self.assertEqual(
            recheck_unsubmitted_teller_readiness_question(
                self.db, second, now_utc=NOW
            )["buyer_money_ready"], "UNKNOWN"
        )
        with self.assertRaisesRegex(
            TellerReadinessQuestionError, "UNVERIFIED_FUNDING_LANE_NOT_ALLOWED"
        ):
            self.ask(proposed_terms=terms(funding_lane="ATM_SET_1_PLUS_SET_2"))

    def test_material_saved_terms_change_invalidates_old_question(self):
        old = self.ask()["packet"]
        self.op = save(
            self.db,
            {**self.op, "asking_price": "89000.00"},
            expected_revision=1,
        )
        state = recheck_unsubmitted_teller_readiness_question(
            self.db, old, now_utc=NOW
        )
        self.assertEqual(state["state"], "STALE_OR_EXPIRED_LOCAL")
        self.assertIn("CURRENT_SAVED_OPPORTUNITY_CHANGED", state["reason_codes"])
        fresh = self.ask()["packet"]
        self.assertEqual(fresh["opportunity_revision"], 2)
        self.assertNotEqual(fresh["terms_fingerprint"], old["terms_fingerprint"])
        self.assertEqual(fresh["stored_asking_price"], "89000.00")

    def test_altering_any_deal_terms_or_source_digest_breaks_fingerprint(self):
        original = self.ask()["packet"]
        modified = copy.deepcopy(original)
        modified["terms"]["proposed_debt_amount"] = "70000.00"
        with self.assertRaisesRegex(TellerReadinessQuestionError, "QUESTION_FINGERPRINT_MISMATCH"):
            recheck_unsubmitted_teller_readiness_question(
                self.db, modified, now_utc=NOW
            )
        modified = copy.deepcopy(original)
        modified["input_snapshot_digest"] = "0" * 64
        with self.assertRaisesRegex(TellerReadinessQuestionError, "QUESTION_FINGERPRINT_MISMATCH"):
            recheck_unsubmitted_teller_readiness_question(
                self.db, modified, now_utc=NOW
            )

    def test_missing_or_corrupted_source_never_claims_ready(self):
        question = self.ask()["packet"]
        self.db.execute(
            "UPDATE revisions SET digest=? WHERE opportunity_id=? AND revision=1",
            ("0" * 64, self.op["id"]),
        )
        self.db.commit()
        result = recheck_unsubmitted_teller_readiness_question(
            self.db, question, now_utc=NOW
        )
        self.assertEqual(result["state"], "STALE_OR_EXPIRED_LOCAL")
        self.assertIn("CURRENT_SAVED_OPPORTUNITY_UNAVAILABLE", result["reason_codes"])
        self.assertEqual(result["teller_readiness"], "UNKNOWN")

    def test_expiry_does_not_renew_a_question(self):
        question = self.ask()["packet"]
        future = NOW + timedelta(seconds=121)
        result = recheck_unsubmitted_teller_readiness_question(
            self.db, question, now_utc=future
        )
        self.assertEqual(result["state"], "STALE_OR_EXPIRED_LOCAL")
        self.assertIn("LOCAL_TERMS_QUESTION_EXPIRED", result["reason_codes"])
        self.assertFalse(result["authorizes_capital_deployment"])

    def test_price_and_term_validation_fail_closed(self):
        for changes in (
            {"proposed_purchase_price": "0.00"},
            {"proposed_debt_amount": "-1"},
            {"proposed_reserve": "NaN"},
            {"proposed_equity_amount": 100.0},
            {"estimated_closing_costs": "1.999"},
            {"proposed_debt_amount": "1e9"},
            {"proposed_purchase_price": "1000000000000.01"},
            {"terms_reference": "../fake"},
            {"fake_teller_ready": True},
        ):
            with self.subTest(changes=changes), self.assertRaises(TellerReadinessQuestionError):
                self.ask(proposed_terms=terms(**changes))
        for duration in (0, 301, True, -1):
            with self.subTest(lifetime=duration), self.assertRaises(TellerReadinessQuestionError):
                self.ask(lifetime_seconds=duration)
        with self.assertRaises(TellerReadinessQuestionError):
            self.ask(now_utc=datetime(2026, 9, 26, 22))

    def test_multifamily_and_other_vertical_have_no_atm_sleeve_leak(self):
        mf = save(self.db, new_opportunity("multifamily", "Fictional flats", "150000"))
        packet = prepare_unsubmitted_teller_readiness_question(
            self.db, mf["id"], proposed_terms=terms(
                funding_lane="GROUNDS_ACQUISITION_UNVERIFIED",
            ), now_utc=NOW,
        )["packet"]
        self.assertEqual(packet["vertical_id"], "multifamily")
        self.assertEqual(packet["terms"]["funding_lane"], "GROUNDS_ACQUISITION_UNVERIFIED")
        with self.assertRaises(TellerReadinessQuestionError):
            prepare_unsubmitted_teller_readiness_question(
                self.db, mf["id"], proposed_terms=terms(
                    funding_lane="ATM_SET_1_ACQUISITION",
                ), now_utc=NOW,
            )
        land = save(self.db, new_opportunity("land_farm", "Fictional parcel"))
        packet = prepare_unsubmitted_teller_readiness_question(
            self.db, land["id"], proposed_terms=terms(
                funding_lane="MISSION_ACCOUNT_UNASSIGNED",
            ), now_utc=NOW,
        )["packet"]
        self.assertIsNone(packet["stored_asking_price"])
        self.assertEqual(packet["terms"]["funding_lane"], "MISSION_ACCOUNT_UNASSIGNED")

    def test_response_shaped_payload_cannot_be_substituted_for_request(self):
        question = self.ask()["packet"]
        for extra in (
            {"teller_readiness": "READY"}, {"approved": True},
            {"broker_balance": "90000"}, {"issuer": "teller"},
            {"teller_receipt": "unverified"},
        ):
            with self.subTest(extra=extra):
                modified = {**question, **extra}
                with self.assertRaisesRegex(TellerReadinessQuestionError, "QUESTION_FIELDS_INVALID"):
                    recheck_unsubmitted_teller_readiness_question(
                        self.db, modified, now_utc=NOW
                    )

    def test_no_direct_ob_teller_or_payment_transport(self):
        from buybox import teller_readiness_question as module
        content = Path(module.__file__).read_text(encoding="utf-8")
        for forbidden in ("requests.post(", "from observatory.", "from teller.",
                          "from vault.", "broker_balance", "TELLER_TOWER_TOKEN_SECRET"):
            self.assertNotIn(forbidden, content)


if __name__ == "__main__":
    unittest.main()
