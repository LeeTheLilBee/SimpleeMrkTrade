"""BBX066: original-source comparable calculations without appraisals or fake sales."""
import unittest
from uuid import uuid4

from buybox.core import add_evidence,new_opportunity
from buybox.evidence import artifact_descriptor
from buybox.comparables import (
    BASIS_BY_VERTICAL, ComparableError, record_comparable, current_comparables,
    market_evidence_report,
)
from buybox.soulaana import context

BASIS={key:next(iter(reg)) for key,reg in BASIS_BY_VERTICAL.items()}

def source(op, *, label="source"):
    a=artifact_descriptor(b"%PDF-1.7\nRecorded source\n%%EOF",
        filename=label+".pdf",mime="application/pdf",
        storage_reference="private-"+str(uuid4()),source_party="Owner-recorded source")
    op.setdefault("artifacts",[]).append(a)
    e=add_evidence(op,"comparable_original",status="RECEIVED",
                   reference=a["id"],source="Owner-recorded source")
    e["artifact_id"]=a["id"]
    return e,a

def data(vertical,eid,**changes):
    d=dict(evidence_id=eid,subject_id="comparable-subject-1",
           market="Georgia metro",source_kind="DOCUMENTED_LISTING_ASK",
           basis=BASIS[vertical],price="100000",denominator="10",
           event_date="2026-09-26",locator="Page 2, comparison row",
           actor_ref="owner-record")
    d.update(changes)
    return d

class ComparableTests(unittest.TestCase):
    def test_all_seven_verticals_start_empty_and_restrict_bases(self):
        for v in BASIS:
            with self.subTest(v=v):
                op=new_opportunity(v,"Actual opportunity")
                empty=market_evidence_report(op)
                self.assertEqual(empty["active_count"],0)
                self.assertEqual(empty["cohorts"],[])
                self.assertFalse(empty["target_value_calculated"])
                self.assertFalse(empty["external_data_retrieved"])
                e,_=source(op)
                op,one=record_comparable(op,**data(v,e["id"]))
                report=market_evidence_report(op)
                self.assertEqual(report["active_count"],1)
                self.assertEqual(report["cohorts"][0]["status"],"INSUFFICIENT_DISTINCT_SUBJECTS")
                self.assertIsNone(report["cohorts"][0]["observed_median"])
                self.assertFalse(one["independent_appraisal"])
                self.assertFalse(one["purchase_authorized"])

    def test_apples_to_apples_two_subjects_descriptive_only(self):
        op=new_opportunity("atm","Actual recorded route")
        e1,_=source(op,label="first")
        e2,_=source(op,label="second")
        op,a=record_comparable(op,**data("atm",e1["id"]))
        op,b=record_comparable(op,**data("atm",e2["id"],subject_id="lot-2",
                                      market="georgia METRO",price="120000"))
        cohort=market_evidence_report(op)["cohorts"][0]
        self.assertEqual(cohort["status"],"DESCRIPTIVE_COHORT_ONLY")
        self.assertEqual(cohort["observed_min"],"10000.00")
        self.assertEqual(cohort["observed_median"],"11000.00")
        self.assertEqual(cohort["observed_max"],"12000.00")
        self.assertEqual(set(cohort["source_artifact_ids"]),
                         {a["source_artifact_id"],b["source_artifact_id"]})
        self.assertIsNone(cohort["appraised_value"])
        self.assertIsNone(cohort["recommended_purchase_price"])
        report=context(op,"valuation")
        self.assertTrue(any(e["classification"]=="DESCRIPTIVE_COMPARABLE_COHORT" for e in report["entries"]))
        self.assertTrue(any(a["id"] in e["references"] for e in report["entries"]))
        self.assertFalse(report["can_authorize"])

    def test_asking_and_reported_sale_never_mix_as_verified_transactions(self):
        op=new_opportunity("multifamily","Source research")
        e,_=source(op)
        op,asked=record_comparable(op,**data("multifamily",e["id"]))
        op,sale=record_comparable(op,**data("multifamily",e["id"],
            subject_id="property-2",source_kind="OWNER_RECORDED_REPORTED_SALE",
            price="80000"))
        report=market_evidence_report(op)
        self.assertEqual(report["cohort_count"],2)
        self.assertTrue(all(c["observed_median"] is None for c in report["cohorts"]))
        self.assertFalse(sale["independent_sale_verified"])
        self.assertTrue(all(c["asking_and_reported_sales_separated"] for c in report["cohorts"]))

    def test_duplicate_guard_and_append_only_corrected_source(self):
        op=new_opportunity("land_farm","Parcel study")
        e,_=source(op)
        op,first=record_comparable(op,**data("land_farm",e["id"]))
        with self.assertRaisesRegex(ComparableError,"DUPLICATE_SUBJECT"):
            record_comparable(op,**data("land_farm",e["id"],price="105000"))
        with self.assertRaisesRegex(ComparableError,"CORRECTION_SCOPE_MISMATCH"):
            record_comparable(op,**data("land_farm",e["id"],subject_id="different",
                                      supersedes=first["id"],correction_reason="Correct original"))
        op,corrected=record_comparable(op,**data("land_farm",e["id"],price="105000",
                                      supersedes=first["id"],correction_reason="Corrected source row"))
        self.assertEqual(len(op["comparable_observations"]),2)
        self.assertEqual(op["comparable_observations"][0]["documented_price"],"100000.00")
        self.assertEqual(current_comparables(op)[0]["id"],corrected["id"])
        self.assertEqual(market_evidence_report(op)["active_count"],1)
        with self.assertRaisesRegex(ComparableError,"ACTIVE_COMPARABLE_CORRECTION_REQUIRED"):
            record_comparable(op,**data("land_farm",e["id"],supersedes=first["id"],
                                      correction_reason="Cannot revise inactive record"))

    def test_missing_real_original_bad_basis_future_and_amount_fail_closed(self):
        op=new_opportunity("equipment","Record check")
        with self.assertRaisesRegex(ComparableError,"ACTIVE_COMPARABLE_ORIGINAL_REQUIRED"):
            record_comparable(op,**data("equipment","invented-id"))
        e,_=source(op)
        for change,reason in [
            ({"basis":"PRICE_PER_USABLE_ACRE"},"UNSUPPORTED_BASIS"),
            ({"source_kind":"INDEPENDENTLY_VERIFIED_SALE"},"INVALID_SOURCE_KIND"),
            ({"price":"-2"},"SOURCE_PRICE_INVALID"),
            ({"price":"1e6"},"SOURCE_PRICE_INVALID"),
            ({"denominator":"0"},"DENOMINATOR_INVALID"),
            ({"event_date":"2099-01-01"},"INVALID_OR_FUTURE"),
            ({"subject_id":""},"COMPARABLE_SUBJECT_REQUIRED"),
            ({"market":""},"MARKET_REQUIRED"),
        ]:
            with self.subTest(change=change):
                with self.assertRaisesRegex(ComparableError,reason):
                    record_comparable(op,**data("equipment",e["id"],**change))
        self.assertFalse(op.get("comparable_observations"))

    def test_source_event_change_invalidates_stale_external_readiness_without_promoting_truth(self):
        op=new_opportunity("business","Business")
        e,_=source(op)
        op["readiness"]["teller"]={"status":"READY","source":"unverified"}
        op["tower_authorizations"]=["unverified-approval"]
        op,item=record_comparable(op,**data("business",e["id"]))
        self.assertEqual(op["analysis_state"],"STALE")
        self.assertIsNone(op["readiness"]["teller"])
        self.assertEqual(op["tower_authorizations"],[])
        self.assertEqual(item["record_type"],"OWNER_TRANSCRIPTION_FROM_ORIGINAL")
        self.assertEqual(item["basis_unit"],"OBSERVED_PRICE_TO_EARNINGS_RATIO")
        self.assertFalse(item["selected_property_valuation"])

if __name__=="__main__":
    unittest.main()
