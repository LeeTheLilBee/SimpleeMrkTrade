"""BBX091: local Closing Review stays source-bound and never becomes authority."""
from __future__ import annotations

import unittest
from uuid import uuid4

from buybox.core import add_evidence, new_opportunity
from buybox.evidence import artifact_descriptor
from buybox.financing import record_financing_option
from buybox.insurance import record_insurance_document
from buybox.closing_review import (
    ClosingReviewError, closing_review_snapshot, record_local_closing_review,
)
from buybox.store import connect, save, load


def attach_original(op,kind,name):
    artifact=artifact_descriptor(
        ("%PDF-1.7\n"+name+"\n%%EOF").encode(),
        filename=name+".pdf",mime="application/pdf",
        storage_reference="private-"+str(uuid4()),source_party="Recorded source")
    op.setdefault("artifacts",[]).append(artifact)
    evidence=add_evidence(op,kind,status="RECEIVED",
                          reference=artifact["id"],source="Recorded source")
    evidence["artifact_id"]=artifact["id"]
    return evidence,artifact


def add_financing(op):
    evidence,_=attach_original(op,"financing_terms","financing")
    return record_financing_option(
        op,evidence_id=evidence["id"],lender_name="Documented lender",
        program_name="Written fixed terms",source_locator="Page 2",
        source_date="2026-09-20",expiration_date="2026-10-31",
        purchase_price="100000",principal="80000",apr_percent="6",
        term_months="120",origination_fee="1000",lender_fee="500",
        other_closing_cost="2500",reserve_cash="10000",vault_cash="0",
        actor_ref="local_owner")


def add_insurance(op):
    evidence,_=attach_original(op,"insurance_document","insurance")
    return record_insurance_document(
        op,evidence_id=evidence["id"],document_kind="BINDER",
        carrier_label="Documented carrier",broker_label="Recorded broker",
        source_locator="Page 1",source_date="2026-09-22",
        quote_valid_until="",effective_date="2026-09-25",
        expiration_date="2027-09-25",planned_closing_date="2026-10-15",
        coverage_codes=["GENERAL_LIABILITY"],annual_premium="2400",
        upfront_premium_due="400",limits_note="",deductible_note="",
        exclusion_note="",actor_ref="local_owner",
        upfront_in_financing_costs=False,
        annual_in_operating_expenses=False)


class ClosingReviewTests(unittest.TestCase):
    def setUp(self):
        self.db=connect()
        self.op=save(self.db,new_opportunity("business","Actual saved target",100000),
                     event_type="OpportunityCreated")

    def tearDown(self):
        self.db.close()

    def reload(self):
        return load(self.db,self.op["id"])

    def test_empty_review_is_explicitly_blocked_not_green(self):
        report=closing_review_snapshot(self.op,today="2026-09-28")
        self.assertEqual(report["local_source_state"],"SOURCE_GAPS_OR_RECHECKS")
        self.assertIn("CRITICAL_DILIGENCE_OUTSTANDING",report["source_blockers"])
        self.assertIn("NO_DOCUMENTED_FINANCING_OPTION",report["source_blockers"])
        self.assertIn("NO_DOCUMENTED_INSURANCE_RECORD",report["source_blockers"])
        self.assertIn("TOWER_CLOSING_AUTHORIZATION_ABSENT",report["external_blockers"])
        self.assertEqual(report["teller_money_ready"],"UNKNOWN")
        self.assertEqual(report["insurance_in_force"],"UNKNOWN")
        self.assertFalse(report["authorizes_closing"])
        self.assertFalse(report["authorizes_money"])
        self.assertFalse(report["updates_lifecycle"])

    def test_owner_can_freeze_local_review_without_advancing_or_sending(self):
        revised,record=record_local_closing_review(
            self.db,self.op,actor_ref="local_owner",
            rationale="Reviewed the current package; outside authority is still pending.",
            planned_closing_date="2026-10-15",today="2026-09-28")
        self.assertEqual(revised["lifecycle"],self.op["lifecycle"])
        self.assertFalse(record["authorizes_closing"])
        self.assertFalse(record["authorizes_money"])
        self.assertFalse(record["transmitted_externally"])
        self.assertFalse(record["updates_lifecycle"])
        self.assertIsNone(record["tower_closing_authorization"])
        self.assertEqual(record["teller_money_ready"],"UNKNOWN")
        saved=save(self.db,revised,event_type="ClosingReviewRecorded",
                   expected_revision=self.op["version"])
        report=closing_review_snapshot(saved,today="2026-09-28")
        self.assertEqual(len(report["historical_reviews"]),1)
        self.assertEqual(report["historical_reviews"][0]["display_state"],
                         "CURRENT_RECORDED_REVIEW")
        self.assertEqual(report["historical_reviews"][0]["local_snapshot_sha256"],
                         record["local_snapshot_sha256"])

    def test_real_financing_and_insurance_can_be_cited_without_becoming_approval(self):
        revised,fin=add_financing(self.op)
        self.op=save(self.db,revised,event_type="FinancingOptionRecorded",
                     expected_revision=self.op["version"])
        revised,ins=add_insurance(self.op)
        self.op=save(self.db,revised,event_type="InsuranceDocumentRecorded",
                     expected_revision=self.op["version"])
        report=closing_review_snapshot(self.op,today="2026-09-28")
        self.assertEqual(len(report["financing_options"]),1)
        self.assertEqual(len(report["insurance_records"]),1)
        self.assertNotIn("NO_DOCUMENTED_FINANCING_OPTION",report["source_blockers"])
        self.assertNotIn("NO_DOCUMENTED_INSURANCE_RECORD",report["source_blockers"])
        revised,record=record_local_closing_review(
            self.db,self.op,actor_ref="local_owner",
            rationale="Comparing the current documented alternatives only.",
            financing_option_id=fin["id"],insurance_record_id=ins["id"],
            planned_closing_date="2026-10-15",today="2026-09-28")
        self.assertEqual(record["selected_financing_option_id"],fin["id"])
        self.assertEqual(record["selected_insurance_record_id"],ins["id"])
        self.assertEqual(record["selected_financing_review_flags"],[])
        self.assertEqual(record["selected_insurance_review_flags"],[])
        self.assertFalse(record["bank_commitment_verified"])
        self.assertEqual(record["insurance_in_force"],"UNKNOWN")
        self.assertFalse(record["title_transfer_verified"])
        self.assertFalse(record["settlement_completed"])

    def test_stale_or_foreign_source_selection_fails_closed(self):
        forged=dict(self.op,asking_price="99000.00")
        with self.assertRaisesRegex(ClosingReviewError,"SOURCE_CHANGED"):
            record_local_closing_review(
                self.db,forged,actor_ref="local_owner",rationale="Not current",
                today="2026-09-28")
        with self.assertRaisesRegex(ClosingReviewError,"CURRENT_FINANCING_OPTION_REQUIRED"):
            record_local_closing_review(
                self.db,self.op,actor_ref="local_owner",rationale="Bad selection",
                financing_option_id="foreign-option",today="2026-09-28")
        with self.assertRaisesRegex(ClosingReviewError,"CURRENT_INSURANCE_RECORD_REQUIRED"):
            record_local_closing_review(
                self.db,self.op,actor_ref="local_owner",rationale="Bad selection",
                insurance_record_id="foreign-insurance",today="2026-09-28")

    def test_review_becomes_historical_after_any_later_saved_revision(self):
        revised,_=record_local_closing_review(
            self.db,self.op,actor_ref="local_owner",rationale="Freeze current state",
            today="2026-09-28")
        self.op=save(self.db,revised,event_type="ClosingReviewRecorded",
                     expected_revision=self.op["version"])
        later=dict(self.op,name="Actual saved target — revised")
        self.op=save(self.db,later,event_type="OpportunityUpdated",
                     expected_revision=self.op["version"])
        report=closing_review_snapshot(self.op,today="2026-09-28")
        self.assertEqual(report["historical_reviews"][0]["display_state"],
                         "HISTORICAL_OPPORTUNITY_VERSION")
        self.assertFalse(report["historical_reviews"][0]["authorizes_closing"])

    def test_all_verticals_remain_external_authority_blocked(self):
        for vertical in ("atm","multifamily","commercial","laundromat",
                         "land_farm","business","equipment"):
            with self.subTest(vertical=vertical):
                op=new_opportunity(vertical,"Universal close review")
                report=closing_review_snapshot(op,today="2026-09-28")
                self.assertFalse(report["tower_closing_authorized"])
                self.assertFalse(report["title_transfer_verified"])
                self.assertFalse(report["bank_commitment_verified"])
                self.assertEqual(report["teller_management_ready"],"UNKNOWN")
                self.assertFalse(report["authorizes_closing"])


if __name__=="__main__":
    unittest.main()
