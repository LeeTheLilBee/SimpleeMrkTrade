"""BBX061: actual-source fixed amortization; no fabricated lender or Teller authority."""
import unittest
from copy import deepcopy
from datetime import date
from decimal import Decimal
from uuid import uuid4

from buybox.core import new_opportunity, add_evidence
from buybox.evidence import artifact_descriptor
from buybox.financing import (
    FinancingError, monthly_payment, record_financing_option,
    option_analysis, current_options, financing_snapshot,
)

def original(op, *, evidence_state="RECEIVED", source="Financing correspondent"):
    a=artifact_descriptor(b"%PDF-1.7\nActual uploaded original\n%%EOF",
                          filename="terms.pdf",mime="application/pdf",
                          storage_reference="local-private-"+str(uuid4()),
                          source_party=source)
    op.setdefault("artifacts",[]).append(a)
    e=add_evidence(op,"financing_terms",status=evidence_state,
                   reference=a["id"],source=source)
    e["artifact_id"]=a["id"]
    return e,a

def terms(evidence_id,**changes):
    d=dict(evidence_id=evidence_id,lender_name="Owner-identified provider",
        program_name="Written fixed-rate terms",source_locator="Page 2, terms",
        source_date="2026-09-20",expiration_date="2026-10-15",
        purchase_price="100000.00",principal="80000.00",
        apr_percent="0",term_months="120",origination_fee="1000",
        lender_fee="500",other_closing_cost="2500",reserve_cash="10000",
        vault_cash="12000",actor_ref="local_owner")
    d.update(changes)
    return d

class FinancingTests(unittest.TestCase):
    def test_actual_original_required_and_source_hash_preserved(self):
        op=new_opportunity("atm","Saved real route",100000)
        with self.assertRaisesRegex(FinancingError,"ACTUAL_ACTIVE"):
            record_financing_option(op,**terms("unseen-evidence"))
        e,a=original(op)
        revised,q=record_financing_option(op,**terms(e["id"]))
        self.assertNotIn("financing_options",op)
        self.assertEqual(q["source_artifact_id"],a["id"])
        self.assertEqual(q["source_sha256"],a["sha256"])
        self.assertEqual(q["record_type"],"OWNER_TRANSCRIBED_ORIGINAL")
        self.assertFalse(q["lender_approval_confirmed"])
        self.assertEqual(q["teller_readiness"],"UNKNOWN")
        self.assertFalse(q["authorizes_money"])
        self.assertIsNone(revised["readiness"]["teller"])
        self.assertEqual(revised["analysis_state"],"STALE")

    def test_zero_interest_and_separate_liquidity(self):
        op=new_opportunity("atm","Real source",100000)
        e,a=original(op)
        op,q=record_financing_option(op,**terms(e["id"]))
        result=option_analysis(op,q,today="2026-09-27")
        self.assertEqual(result["modeled_monthly_payment"],"666.67")
        self.assertEqual(result["modeled_annual_debt_service"],"8000.04")
        self.assertEqual(result["modeled_interest"],"0.00")
        self.assertEqual(result["modeled_total_scheduled_payments"],"80000.00")
        self.assertEqual(result["modeled_adjusted_final_payment"],"666.27")
        self.assertEqual(result["recorded_project_cash_needed"],"126000.00")
        self.assertEqual(result["unverified_buyer_cash_gap"],"46000.00")
        self.assertFalse(result["reserve_cash_is_cost"])
        self.assertFalse(result["vault_cash_is_cost"])
        self.assertIsNone(result["illustrative_operating_to_debt_ratio"])
        self.assertEqual(result["status"],"RECORDED_NOT_APPROVED")
        self.assertFalse(result["bank_commitment"])
        self.assertFalse(result["funding_available"])
        self.assertFalse(result["tower_authorization"])
        self.assertEqual(result["money_and_management_readiness"],"UNKNOWN")
        self.assertEqual(monthly_payment("120000","0",120),Decimal("1000.00"))
        self.assertGreater(monthly_payment("120000","10",120),Decimal("1000.00"))

    def test_changed_price_expiry_and_hash_fail_closed(self):
        op=new_opportunity("atm","Price changed",100000)
        e,a=original(op)
        op,q=record_financing_option(op,**terms(e["id"]))
        self.assertEqual(option_analysis(op,q,today="2026-09-27")["review_flags"],[])
        op["asking_price"]="105000.00"
        reasons=option_analysis(op,q,today="2026-10-16")["review_flags"]
        self.assertIn("RECORDED_TERMS_EXPIRED",reasons)
        self.assertIn("OPPORTUNITY_ASKING_PRICE_CHANGED",reasons)
        op["artifacts"][0]["sha256"]="f"*64
        reasons=option_analysis(op,q,today="2026-09-27")["review_flags"]
        self.assertIn("ORIGINAL_DOCUMENT_LINK_OR_HASH_CHANGED",reasons)
        self.assertEqual(option_analysis(op,q,today="2026-09-27")["status"],
                         "RECHECK_SOURCE_OR_PRICE")

    def test_two_real_options_and_append_only_correction(self):
        op=new_opportunity("atm","Compare documents",100000)
        first,_=original(op,source="First provider")
        second,_=original(op,source="Second provider")
        op,a=record_financing_option(op,**terms(first["id"]))
        op,b=record_financing_option(op,**terms(second["id"],
                                     lender_name="Second provider",apr_percent="5"))
        self.assertEqual(financing_snapshot(op,today="2026-09-27")["active_option_count"],2)
        op,c=record_financing_option(op,**terms(second["id"],apr_percent="4",
                                     supersedes=b["id"],
                                     correction_reason="New original provided"))
        self.assertEqual(op["financing_options"][1]["id"],b["id"])
        self.assertEqual(op["financing_options"][1]["apr_percent"],"5")
        self.assertEqual(c["supersedes"],b["id"])
        self.assertEqual(set(q["id"] for q in current_options(op)),{a["id"],c["id"]})
        with self.assertRaisesRegex(FinancingError,"CURRENT_OPTION_CORRECTION_TARGET"):
            record_financing_option(op,**terms(second["id"],supersedes=b["id"],
                                  correction_reason="Invalid old target"))

    def test_reject_unsupported_loan_shapes_bad_ranges_and_non_atm_vault(self):
        op=new_opportunity("atm","Invalid terms",100000)
        e,_=original(op)
        for change,reason in [
            ({"structure":"VARIABLE_OR_BALLOON"},"STRUCTURE_NOT_SUPPORTED"),
            ({"apr_percent":"nan"},"APR_FORMAT_INVALID"),
            ({"apr_percent":"101"},"APR_OUT_OF_RANGE"),
            ({"apr_percent":"12.12345"},"APR_FORMAT_INVALID"),
            ({"term_months":"11"},"ONLY_12_TO_360"),
            ({"term_months":"361"},"ONLY_12_TO_360"),
            ({"term_months":"12.5"},"MONTHS_INVALID"),
            ({"principal":"200000"},"LOAN_EXCEEDS"),
            ({"principal":"-1"},"PRINCIPAL_INVALID"),
            ({"reserve_cash":"1e6"},"RESERVE_INVALID"),
            ({"expiration_date":"2026-08-01"},"EXPIRES_BEFORE"),
        ]:
            with self.subTest(change=change):
                with self.assertRaisesRegex(FinancingError,reason):
                    record_financing_option(op,**terms(e["id"],**change))
        land=new_opportunity("land_farm","Farm",100000)
        e,_=original(land)
        with self.assertRaisesRegex(FinancingError,"ATM_VAULT_CASH_ONLY"):
            record_financing_option(land,**terms(e["id"]))
        land,q=record_financing_option(land,**terms(e["id"],vault_cash="0"))
        self.assertEqual(q["vault_cash"],"0.00")
        self.assertEqual(financing_snapshot(land,today="2026-09-27")["active_option_count"],1)

if __name__=="__main__":
    unittest.main()
