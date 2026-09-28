"""BBX081: documented insurance risk and financing overlay never become coverage truth."""
from __future__ import annotations
from datetime import date
from decimal import Decimal
from uuid import uuid4
import unittest

from buybox.core import add_evidence, new_opportunity
from buybox.evidence import artifact_descriptor
from buybox.insurance import (
    InsuranceError, INSURANCE_EVIDENCE_KIND, VERTICAL_PROMPTS,
    record_insurance_document, insurance_snapshot, inspect_insurance_record,
    current_insurance_records, project_financing_with_insurance,
)
from buybox.financing import record_financing_option
from buybox.soulaana import context
from buybox.registry import VERTICALS


def source(op, *, kind=INSURANCE_EVIDENCE_KIND):
    a=artifact_descriptor(b"%PDF-1.7\nInsurance source fixture\n%%EOF",
        filename="insurance.pdf",mime="application/pdf",
        storage_reference="private-"+str(uuid4()),
        source_party="Test-only insurance correspondent")
    op.setdefault("artifacts",[]).append(a)
    e=add_evidence(op,kind,status="RECEIVED",
                   reference=a["id"],source="Test-only source")
    e["artifact_id"]=a["id"]
    return e,a

def details(evidence_id,**changes):
    fields={
        "evidence_id":evidence_id,"document_kind":"QUOTE",
        "carrier_label":"Owner-transcribed carrier","broker_label":"",
        "source_locator":"Page 2, coverage table",
        "source_date":"2026-09-20","quote_valid_until":"2026-10-15",
        "effective_date":"2026-10-01","expiration_date":"2027-10-01",
        "planned_closing_date":"2026-10-05",
        "coverage_codes":["PROPERTY","GENERAL_LIABILITY"],
        "annual_premium":"6000","upfront_premium_due":"2000",
        "limits_note":"As stated in original","deductible_note":"See page 3",
        "exclusion_note":"Subject to original exclusions",
        "upfront_in_financing_costs":False,"annual_in_operating_expenses":False,
        "actor_ref":"local_owner","supersedes":None,"correction_reason":None,
    }
    fields.update(changes)
    return fields

def financing_source(op):
    a=artifact_descriptor(b"%PDF-1.7\nLender terms in test fixture\n%%EOF",
       filename="finance.pdf",mime="application/pdf",
       storage_reference="private-"+str(uuid4()),source_party="Fixture")
    op.setdefault("artifacts",[]).append(a)
    e=add_evidence(op,"financing_terms",status="RECEIVED",
                   reference=a["id"],source="Fixture")
    e["artifact_id"]=a["id"]
    return e

def finance(op,e):
    return record_financing_option(op,
        evidence_id=e["id"],lender_name="Recorded lender",
        program_name="Recorded program",source_locator="Page 1",
        source_date="2026-09-20",expiration_date="2026-10-15",
        purchase_price="100000",principal="80000",apr_percent="0",
        term_months="120",origination_fee="1000",lender_fee="500",
        other_closing_cost="2500",reserve_cash="10000",vault_cash="12000",
        actor_ref="local_owner")


class InsuranceTests(unittest.TestCase):
    def test_seven_verticals_zero_synthetic_records_and_nonmandatory_prompts(self):
        for key in VERTICALS:
            with self.subTest(vertical=key):
                op=new_opportunity(key,"Actual record only")
                snapshot=insurance_snapshot(op,today="2026-09-28")
                self.assertEqual(snapshot["current_document_count"],0)
                self.assertEqual(snapshot["records"],[])
                self.assertEqual(tuple(snapshot["review_prompts"]),VERTICAL_PROMPTS[key])
                self.assertFalse(snapshot["review_prompts_are_requirements"])
                self.assertEqual(snapshot["coverage_in_force"],"UNKNOWN")
                self.assertFalse(snapshot["insurer_verified"])
                self.assertFalse(snapshot["coverage_purchased_by_buybox"])

    def test_uploaded_original_is_required_and_quote_still_not_bound(self):
        op=new_opportunity("atm","Real route",100000)
        with self.assertRaisesRegex(InsuranceError,"ACTIVE_INSURANCE_ORIGINAL_REQUIRED"):
            record_insurance_document(op,**details("fake-original"))
        e,a=source(op)
        revised,rec=record_insurance_document(op,**details(e["id"]))
        self.assertEqual(op.get("insurance_records",[]),[])
        self.assertEqual(rec["source_sha256"],a["sha256"])
        self.assertEqual(rec["source_artifact_id"],a["id"])
        self.assertFalse(rec["insurer_confirmation_verified"])
        self.assertFalse(rec["premium_paid_verified"])
        self.assertEqual(rec["coverage_in_force"],"UNKNOWN")
        self.assertFalse(rec["authorizes_acquisition"])
        self.assertEqual(revised["analysis_state"],"STALE")
        self.assertIsNone(revised["readiness"]["teller"])
        assessment=inspect_insurance_record(revised,rec,today="2026-09-28")
        self.assertIn("QUOTE_IS_NOT_BOUND_POLICY",assessment["review_flags"])
        self.assertFalse(assessment["bound_coverage_verified"])
        self.assertEqual(assessment["illustrative_monthly_premium"],"500.00")
        soulaana=context(revised,"insurance")
        self.assertFalse(soulaana["can_authorize"])
        sourced=[x for x in soulaana["entries"] if x["classification"]=="SOURCE_LINKED_INSURANCE"]
        self.assertEqual(len(sourced),1)
        self.assertIn(rec["id"],sourced[0]["references"])
        self.assertIn(a["id"],sourced[0]["references"])

    def test_quote_expiry_coverage_gap_and_tampered_digest_are_reported(self):
        op=new_opportunity("multifamily","Property",100000)
        e,a=source(op,kind="insurance_quote")
        op,rec=record_insurance_document(op,**details(e["id"],
            quote_valid_until="2026-09-26",effective_date="2026-10-20",
            expiration_date="2027-10-20"))
        flags=inspect_insurance_record(op,rec,today="2026-09-28")["review_flags"]
        self.assertIn("QUOTE_RECORD_EXPIRED",flags)
        self.assertIn("QUOTE_VALIDITY_BEFORE_PROPOSED_CLOSING",flags)
        self.assertIn("COVERAGE_DATES_DO_NOT_INCLUDE_PROPOSED_CLOSING",flags)
        op["artifacts"][0]["sha256"]="f"*64
        checked=inspect_insurance_record(op,rec,today="2026-09-28")
        self.assertFalse(checked["source_link_intact"])
        self.assertIn("ORIGINAL_LINK_OR_DIGEST_CHANGED",checked["review_flags"])

    def test_certificate_without_premium_stays_unknown_and_no_cash_model(self):
        op=new_opportunity("equipment","Equipment",100000)
        e,_=source(op)
        op,rec=record_insurance_document(op,**details(e["id"],
            document_kind="CERTIFICATE",quote_valid_until="",
            annual_premium="",upfront_premium_due="",
            effective_date="",expiration_date=""))
        result=inspect_insurance_record(op,rec,today="2026-09-28")
        self.assertIsNone(rec["annual_premium"])
        self.assertIsNone(result["illustrative_monthly_premium"])
        self.assertIn("CERTIFICATE_ALONE_DOES_NOT_VERIFY_CURRENT_COVERAGE",
                      result["review_flags"])
        self.assertFalse(result["bound_coverage_verified"])
        # Cannot model unknown as free.
        loan_e=financing_source(op)
        # non-ATM financed record cannot include ATM vault cash
        financed,q=record_financing_option(op,
            evidence_id=loan_e["id"],lender_name="Recorded lender",
            program_name="Recorded program",source_locator="Page 1",
            source_date="2026-09-20",expiration_date="2026-10-15",
            purchase_price="100000",principal="80000",apr_percent="0",
            term_months="120",origination_fee="1000",lender_fee="500",
            other_closing_cost="2500",reserve_cash="10000",vault_cash="0",
            actor_ref="local_owner")
        with self.assertRaisesRegex(InsuranceError,"NO_RECORDED_PREMIUM"):
            project_financing_with_insurance(financed,rec,q,today="2026-09-28")

    def test_cash_overlay_adds_only_unincluded_upfront_and_annual_premium(self):
        op=new_opportunity("atm","Cash comparison",100000)
        e,_=source(op)
        op,rec=record_insurance_document(op,**details(e["id"]))
        loan_e=financing_source(op)
        op,q=finance(op,loan_e)
        op["metrics"]={
            "annual_revenue":{"value":"90000","state":"DOCUMENT_SUPPORTED","period":"2025-01-01 / 2025-12-31"},
            "annual_expenses":{"value":"50000","state":"DOCUMENT_SUPPORTED","period":"2025-01-01 / 2025-12-31"},
        }
        overlay=project_financing_with_insurance(op,rec,q,today="2026-09-28")
        self.assertEqual(overlay["illustrative_buyer_cash_gap_with_premium"],"48000.00")
        self.assertEqual(overlay["additional_upfront_premium_if_not_already_counted"],"2000.00")
        self.assertEqual(overlay["illustrative_annual_operating_after_premium"],"34000.00")
        self.assertFalse(overlay["authorizes_purchase_or_spend"])
        included={**rec,"upfront_in_financing_costs":True,
                  "annual_in_operating_expenses":True}
        overlay=project_financing_with_insurance(op,included,q,today="2026-09-28")
        self.assertEqual(overlay["illustrative_buyer_cash_gap_with_premium"],"46000.00")
        self.assertEqual(overlay["illustrative_annual_operating_after_premium"],"40000.00")
        self.assertTrue(overlay["premium_inclusion_is_owner_assumption"])

    def test_append_only_same_carrier_correction_and_cross_carrier_refusal(self):
        op=new_opportunity("commercial","Actual property",100000)
        e,_=source(op)
        op,first=record_insurance_document(op,**details(e["id"]))
        with self.assertRaisesRegex(InsuranceError,"CORRECTION_SOURCE_SCOPE_MISMATCH"):
            record_insurance_document(op,**details(e["id"],carrier_label="Different carrier",
                supersedes=first["id"],correction_reason="Not same source"))
        op,corrected=record_insurance_document(op,**details(e["id"],annual_premium="6400",
             supersedes=first["id"],correction_reason="Corrected source"))
        self.assertEqual(op["insurance_records"][0]["annual_premium"],"6000.00")
        self.assertEqual(corrected["supersedes"],first["id"])
        self.assertEqual(current_insurance_records(op)[0]["id"],corrected["id"])
        with self.assertRaisesRegex(InsuranceError,"ACTIVE_CORRECTION_TARGET_REQUIRED"):
            record_insurance_document(op,**details(e["id"],supersedes=first["id"],
                correction_reason="Old superseded target"))

    def test_bad_coverage_dates_values_and_missing_priced_policy(self):
        op=new_opportunity("business","Owner actual source",100000)
        e,_=source(op)
        for change,code in [
            ({"coverage_codes":[]},"COVERAGE_CODES_REQUIRED"),
            ({"coverage_codes":["PROPERTY","PROPERTY"]},"INVALID_OR_DUPLICATED"),
            ({"coverage_codes":["FAKE"]},"INVALID_OR_DUPLICATED"),
            ({"annual_premium":"0"},"ANNUAL_PREMIUM_INVALID"),
            ({"annual_premium":"nan"},"ANNUAL_PREMIUM_INVALID"),
            ({"quote_valid_until":""},"WRITTEN_QUOTE_VALIDITY_REQUIRED"),
            ({"quote_valid_until":"2026-09-10"},"QUOTE_EXPIRES_BEFORE_SOURCE"),
            ({"effective_date":"2026-10-01","expiration_date":""},"BOTH_COVERAGE_DATES"),
            ({"effective_date":"2026-10-01","expiration_date":"2026-10-01"},"COVERAGE_END_MUST_FOLLOW"),
            ({"upfront_in_financing_costs":"true"},"CLOSING_COST_TREATMENT_REQUIRED"),
            ({"document_kind":"POLICY","quote_valid_until":"2026-10-15"},"QUOTE_VALIDITY_ONLY_FOR_QUOTE"),
        ]:
            with self.subTest(change=change):
                with self.assertRaisesRegex(InsuranceError,code):
                    record_insurance_document(op,**details(e["id"],**change))
        self.assertEqual(op.get("insurance_records",[]),[])


if __name__=="__main__":
    unittest.main()
