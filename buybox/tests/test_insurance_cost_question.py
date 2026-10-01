"""BBX082–086: saved financing + insurance costs never become Teller readiness."""
from __future__ import annotations

import json
import sqlite3
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from buybox.core import new_opportunity
from buybox.financing import current_options
from buybox.insurance import current_insurance_records, record_insurance_document
from buybox.insurance_cost_question import (
    CORE_KEYS, PACKET_KEYS, SCHEMA, InsuranceCostSourceError,
    prepare_unsubmitted_insurance_cost_proposal, recheck_unsubmitted_insurance_cost_proposal,
)
from buybox.store import connect, load, save
from buybox.tests.test_insurance import (
    source, details, financing_source, finance,
)

NOW = datetime(2026, 9, 28, 12, 0, tzinfo=timezone.utc)


class SourceOnlyInsuranceCostTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = str(Path(self.tmp.name) / "owner-local.sqlite3")
        self.db = connect(self.path)
        op = new_opportunity("atm", "Synthetic route, no actual seller", "100000")
        fe = financing_source(op)
        op, self.fin = finance(op, fe)
        ie, _ = source(op)
        op, self.ins = record_insurance_document(op, **details(ie["id"]))
        self.op = save(self.db, op, event_type="SyntheticSourceOnly")

    def tearDown(self):
        self.db.close()
        self.tmp.cleanup()

    def prepare(self, **kwargs):
        args = {
            "insurance_record_id": self.ins["id"],
            "financing_option_id": self.fin["id"],
            "now_utc": NOW,
        }
        args.update(kwargs)
        return prepare_unsubmitted_insurance_cost_proposal(
            self.db, self.op["id"], **args
        )

    def test_exact_saved_originals_produce_only_unsubmitted_owner_assumptions(self):
        result = self.prepare()
        packet = result["packet"]
        self.assertEqual(set(packet), PACKET_KEYS)
        self.assertEqual(set(packet) - {"source_fingerprint", "issued_at", "valid_until"}, CORE_KEYS)
        self.assertEqual(packet["schema_version"], SCHEMA)
        self.assertEqual(packet["opportunity_revision"], 1)
        self.assertEqual(packet["financing_original_sha256"], self.fin["source_sha256"])
        self.assertEqual(packet["insurance_original_sha256"], self.ins["source_sha256"])
        self.assertEqual(packet["insurance_document_kind"], "QUOTE")
        self.assertEqual(packet["annual_premium"], "6000.00")
        self.assertEqual(packet["upfront_premium_due"], "2000.00")
        self.assertEqual(packet["illustrative_additional_upfront_premium"], "2000.00")
        self.assertEqual(packet["illustrative_buyer_cash_gap"], "48000.00")
        self.assertIn("QUOTE_IS_NOT_BOUND_POLICY", packet["insurance_source_review_flags"])
        self.assertFalse(result["original_bytes_reverified"])
        self.assertFalse(result["owner_cost_inclusion_assumptions_verified"])
        for key in ("insurer_confirmed", "lender_approved", "authorizes_acquisition",
                    "authorizes_capital_deployment"):
            self.assertFalse(packet[key])
        self.assertEqual(packet["coverage_in_force"], "UNKNOWN")
        self.assertEqual(packet["teller_money_readiness"], "UNKNOWN")
        self.assertEqual(packet["teller_management_capacity_readiness"], "UNKNOWN")
        self.assertFalse(result["teller_request_sent"])
        self.assertFalse(result["tower_authorization"])

    def test_current_recheck_is_local_only_without_fake_teller_receipt(self):
        packet = self.prepare()["packet"]
        r = recheck_unsubmitted_insurance_cost_proposal(self.db, packet, now_utc=NOW)
        self.assertEqual(r["state"], "CURRENT_LOCAL_UNSUBMITTED")
        self.assertEqual(r["reason_codes"], [])
        self.assertFalse(r["teller_request_sent"])
        self.assertFalse(r["teller_receipt_present"])
        self.assertEqual(r["teller_readiness"], "UNKNOWN")
        self.assertFalse(r["authorizes_capital_deployment"])

    def test_changed_opportunity_price_invalidates_prior_packet(self):
        packet = self.prepare()["packet"]
        updated = dict(load(self.db, self.op["id"]), asking_price="101000.00")
        save(self.db, updated, expected_revision=1)
        r = recheck_unsubmitted_insurance_cost_proposal(self.db, packet, now_utc=NOW)
        self.assertEqual(r["state"], "STALE_OR_EXPIRED_LOCAL")
        self.assertIn("CURRENT_SAVED_SOURCE_OR_COST_TERMS_CHANGED", r["reason_codes"])

    def test_missing_or_superseded_selected_financing_is_not_current(self):
        packet = self.prepare()["packet"]
        op = load(self.db, self.op["id"])
        op["financing_options"].append({
            **self.fin, "id": "replacement-option-id", "supersedes": self.fin["id"],
        })
        save(self.db, op, expected_revision=1)
        self.assertIn("CURRENT_SOURCE_OR_ORIGINAL_UNAVAILABLE",
                      recheck_unsubmitted_insurance_cost_proposal(
                          self.db, packet, now_utc=NOW)["reason_codes"])

    def test_tampered_original_reference_is_not_accepted_as_current(self):
        packet = self.prepare()["packet"]
        op = load(self.db, self.op["id"])
        target = next(a for a in op["artifacts"]
                      if a["id"] == self.ins["source_artifact_id"])
        target["sha256"] = "f" * 64
        save(self.db, op, expected_revision=1)
        with self.assertRaisesRegex(InsuranceCostSourceError, "CURRENT_ORIGINAL_REFERENCE_INVALID"):
            self.prepare()
        self.assertIn("CURRENT_SOURCE_OR_ORIGINAL_UNAVAILABLE",
                      recheck_unsubmitted_insurance_cost_proposal(
                          self.db, packet, now_utc=NOW)["reason_codes"])

    def test_unpriced_certificate_does_not_become_zero_cost(self):
        op = load(self.db, self.op["id"])
        record = next(r for r in op["insurance_records"] if r["id"] == self.ins["id"])
        record["document_kind"] = "CERTIFICATE"
        record["annual_premium"] = None
        record["upfront_premium_due"] = None
        save(self.db, op, expected_revision=1)
        with self.assertRaisesRegex(InsuranceCostSourceError, "INSURANCE_PREMIUM_NOT_RECORDED"):
            self.prepare()

    def test_expiry_and_extra_or_forged_fields_cannot_make_ready(self):
        packet = self.prepare()["packet"]
        expired = recheck_unsubmitted_insurance_cost_proposal(
            self.db, packet, now_utc=NOW + timedelta(seconds=121))
        self.assertIn("LOCAL_PROPOSAL_EXPIRED", expired["reason_codes"])
        for bad in [
            {**packet, "teller_receipt": "fake"},
            {**packet, "teller_money_readiness": "READY"},
            {**packet, "authorizes_acquisition": True},
            {**packet, "annual_premium": "0.00"},
        ]:
            with self.subTest(bad=bad):
                with self.assertRaises(InsuranceCostSourceError):
                    recheck_unsubmitted_insurance_cost_proposal(self.db, bad, now_utc=NOW)

    def test_no_clean_false_approval_if_attacker_rehashes_forged_cost_fields(self):
        packet = self.prepare()["packet"]
        from buybox.insurance_cost_question import _sha
        forged = dict(packet, annual_premium="0.00")
        core = {key: forged[key] for key in CORE_KEYS}
        forged["source_fingerprint"] = _sha(core)
        result = recheck_unsubmitted_insurance_cost_proposal(self.db, forged, now_utc=NOW)
        self.assertIn("CURRENT_SAVED_SOURCE_OR_COST_TERMS_CHANGED", result["reason_codes"])
        self.assertFalse(result["authorizes_acquisition"])

    def test_naive_time_dirty_transaction_and_zero_lifetime_fail_closed(self):
        with self.assertRaisesRegex(InsuranceCostSourceError, "TIMEZONE_REQUIRED"):
            self.prepare(now_utc=datetime(2026, 9, 28))
        with self.assertRaisesRegex(InsuranceCostSourceError, "INVALID_PROPOSAL_LIFETIME"):
            self.prepare(lifetime_seconds=0)
        self.db.execute(
            "INSERT INTO events(opportunity_id,revision,event_type,occurred_at,details_json) "
            "VALUES(?,?,?,?,?)",
            (self.op["id"], 1, "SyntheticUncommitted", NOW.isoformat(), "{}"),
        )
        with self.assertRaisesRegex(InsuranceCostSourceError, "FRESH_DATABASE_TRANSACTION_REQUIRED"):
            self.prepare()
        self.db.rollback()

    def test_no_ledger_or_external_call_and_source_remains_unchanged(self):
        before = load(self.db, self.op["id"])
        p = self.prepare()
        self.assertEqual(load(self.db, self.op["id"]), before)
        self.assertEqual(self.db.execute(
            "SELECT COUNT(*) FROM sqlite_master WHERE name='buybox_teller_insurance_receipts'"
        ).fetchone()[0], 0)
        self.assertFalse(p["authorizes_capital_deployment"])
        from buybox import insurance_cost_question as module
        content = Path(module.__file__).read_text(encoding="utf-8")
        for absent in ("requests.post(", "from observatory.", "from vault.",
                       "from teller.", "@app.route("):
            self.assertNotIn(absent, content)


if __name__ == "__main__":
    unittest.main()
