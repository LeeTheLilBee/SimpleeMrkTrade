"""BBX037-041: real-source claim integrity, period matching and safe owner review."""
from __future__ import annotations

from copy import deepcopy
from uuid import uuid4
import unittest

from buybox.core import add_evidence, evaluate, new_opportunity
from buybox.evidence import artifact_descriptor
from buybox.claim_register import (
    ClaimRegisterError, active_claims, integrity_report, owner_reviewed_source,
    record_owner_document_review, record_source_claim,
)
from buybox.soulaana import context


def original(op, *, contents, name, kind="processor_statements"):
    descriptor=artifact_descriptor(contents,filename=name,mime="application/pdf",
                                   storage_reference="private-"+str(uuid4()),
                                   source_party="Recorded source")
    op.setdefault("artifacts",[]).append(descriptor)
    item=add_evidence(op,kind,reference=descriptor["id"],source="Recorded source")
    item["artifact_id"]=descriptor["id"]
    return item,descriptor


def statement(op, evidence_id, value, **kwargs):
    params={
        "evidence_id":evidence_id, "subject_id":"deal",
        "field":"ANNUAL_REVENUE", "value":value,
        "period_key":"2025-01-01 / 2025-12-31",
        "locator":"Page 3, operating statement",
    }
    params.update(kwargs)
    return record_source_claim(op,**params)


class ClaimIntegrityTests(unittest.TestCase):
    def test_two_originals_different_same_period_are_unresolved_and_block(self):
        op=new_opportunity("atm","Real seller file intake",95000)
        a,_=original(op,contents=b"%PDF-1.7\nSeller statement 1\n%%EOF",name="one.pdf")
        b,_=original(op,contents=b"%PDF-1.7\nSeller statement 2\n%%EOF",name="two.pdf")
        op,first=statement(op,a["id"],"80000")
        op,second=statement(op,b["id"],"92000.00")
        report=integrity_report(op)
        self.assertEqual(report["unresolved_count"],1)
        c=report["discrepancies"][0]
        self.assertEqual(c["kind"],"CROSS_SOURCE_DISCREPANCY")
        self.assertEqual(set(c["claim_ids"]),{first["id"],second["id"]})
        self.assertFalse(c["automatically_accepted"])
        evaluation=evaluate(op)
        self.assertEqual(evaluation["judgment"],"REVIEW")
        self.assertFalse(evaluation["purchase_authorized"])
        self.assertTrue(any(f["rule_id"]=="CORE-CLAIM-CONFLICT" and
                            f["level"]=="BLOCK" for f in evaluation["findings"]))
        self.assertIsNone(op.get("metrics",{}).get("annual_revenue"))
        soulaana=context(op,"evidence")
        discrepancies=[e for e in soulaana["entries"]
                       if e["classification"]=="SOURCE_DISCREPANCY"]
        self.assertEqual(len(discrepancies),1)
        self.assertEqual(set(discrepancies[0]["references"]),
                         {first["id"],second["id"]})
        self.assertFalse(soulaana["can_authorize"])

    def test_equivalent_normalized_values_and_different_period_not_conflicts(self):
        op=new_opportunity("business","Business source")
        a,_=original(op,contents=b"%PDF-1.7\nOne\n%%EOF",name="a.pdf")
        b,_=original(op,contents=b"%PDF-1.7\nTwo\n%%EOF",name="b.pdf")
        op,_=statement(op,a["id"],"80000")
        op,_=statement(op,b["id"],"80000.00")
        self.assertEqual(integrity_report(op)["unresolved_count"],0)
        op,_=statement(op,b["id"],"92000.00",
                       period_key="2024-01-01 / 2024-12-31")
        self.assertEqual(integrity_report(op)["unresolved_count"],0)
        op,_=statement(op,b["id"],"88000",
                       field="ANNUAL_EXPENSES")
        self.assertEqual(integrity_report(op)["unresolved_count"],0)

    def test_owner_document_review_uses_exact_original_revision_lineage(self):
        op=new_opportunity("atm","Original review")
        e,a=original(op,contents=b"%PDF-1.7\nReal original\n%%EOF",name="file.pdf")
        op,claim=statement(op,e["id"],"50000")
        self.assertIsNone(owner_reviewed_source(op,claim))
        with self.assertRaisesRegex(ClaimRegisterError,"MATCHING_OWNER_REVIEWED"):
            record_owner_document_review(op,claim_id=claim["id"],rationale="Looked at page 3")
        old_evidence=next(x for x in op["evidence"] if x["id"]==e["id"])
        old_evidence["status"]="SUPERSEDED"
        reviewed={**deepcopy(old_evidence),"id":str(uuid4()),"status":"DOCUMENT_SUPPORTED",
                  "supersedes":e["id"]}
        op["evidence"].append(reviewed)
        op,revision=record_owner_document_review(op,claim_id=claim["id"],
                                                 rationale="Reviewed document page 3")
        self.assertEqual(revision["state"],"OWNER_DOCUMENT_REVIEWED")
        self.assertEqual(revision["evidence_id"],reviewed["id"])
        self.assertEqual(revision["source_evidence_id"],e["id"])
        self.assertEqual(revision["artifact_sha256"],a["sha256"])
        self.assertEqual(revision["review"]["scope"],"DOCUMENT_SUPPORT_ONLY")
        self.assertFalse(revision["independently_verified"])
        self.assertFalse(revision["promoted_to_metric"])
        self.assertEqual(op["source_claims"][0]["state"],"SOURCE_RECORDED")
        self.assertEqual(len(active_claims(op)),1)
        with self.assertRaisesRegex(ClaimRegisterError,"ACTIVE_UNREVIEWED"):
            record_owner_document_review(op,claim_id=revision["id"],rationale="Again")

    def test_correction_is_append_only_and_must_match_scope(self):
        op=new_opportunity("multifamily","Rent roll claim")
        a,_=original(op,contents=b"%PDF-1.7\nA\n%%EOF",name="a.pdf")
        b,_=original(op,contents=b"%PDF-1.7\nB\n%%EOF",name="b.pdf")
        op,first=statement(op,a["id"],"90000")
        with self.assertRaisesRegex(ClaimRegisterError,"CORRECTION_SCOPE_MISMATCH"):
            statement(op,b["id"],"95000",supersedes_claim_id=first["id"],
                      correction_reason="Seller sent corrected document",
                      subject_id="another property")
        op,corrected=statement(op,b["id"],"95000",
            supersedes_claim_id=first["id"],
            correction_reason="Seller sent a corrected source document")
        self.assertEqual(corrected["supersedes"],first["id"])
        self.assertEqual(op["source_claims"][0]["id"],first["id"])
        self.assertEqual(op["source_claims"][0]["raw_value"],"90000")
        self.assertEqual(active_claims(op)[0]["id"],corrected["id"])
        self.assertEqual(integrity_report(op)["unresolved_count"],0)
        with self.assertRaisesRegex(ClaimRegisterError,"ACTIVE_CORRECTION_TARGET"):
            statement(op,b["id"],"96000",supersedes_claim_id=first["id"],
                      correction_reason="Late correction")
        
    def test_source_boundaries_strict_and_invalidation(self):
        op=new_opportunity("land_farm","Farm")
        e,_=original(op,contents=b"%PDF-1.7\nA\n%%EOF",name="source.pdf")
        op["readiness"]["teller"]={"source":"teller","status":"READY"}
        op["tower_authorizations"]=["old-approval"]
        with self.assertRaisesRegex(ClaimRegisterError,"LINKED_ORIGINAL_REQUIRED"):
            statement(op,"invented-id","80000")
        with self.assertRaisesRegex(ClaimRegisterError,"FULL_YEAR_PERIOD_REQUIRED"):
            statement(op,e["id"],"80000",period_key="2025")
        with self.assertRaisesRegex(ClaimRegisterError,"MONEY_FORMAT_INVALID"):
            statement(op,e["id"],"80,000")
        with self.assertRaisesRegex(ClaimRegisterError,"UNREGISTERED_CLAIM_FIELD"):
            statement(op,e["id"],"80000",field="APPROVE_PURCHASE")
        op,claim=statement(op,e["id"],"80000")
        self.assertIsNone(op["readiness"]["teller"])
        self.assertEqual(op["tower_authorizations"],[])
        self.assertEqual(op["analysis_state"],"STALE")
        self.assertEqual(claim["state"],"SOURCE_RECORDED")
        self.assertFalse(claim["promoted_to_metric"])
        self.assertFalse(claim["independently_verified"])

    def test_casefold_text_counts_as_same_and_price_dates_distinct(self):
        op=new_opportunity("commercial","Seller documentation")
        a,_=original(op,contents=b"%PDF-1.7\nA\n%%EOF",name="a.pdf")
        b,_=original(op,contents=b"%PDF-1.7\nB\n%%EOF",name="b.pdf")
        op,_=statement(op,a["id"],"Seller Owned",field="OWNERSHIP",
                       period_key="2026-09-25")
        op,_=statement(op,b["id"]," seller   owned ",field="OWNERSHIP",
                       period_key="2026-09-25")
        self.assertEqual(integrity_report(op)["unresolved_count"],0)
        op,_=statement(op,a["id"],"100000",field="ASKING_PRICE",
                       period_key="2026-09-25")
        op,_=statement(op,b["id"],"90000",field="ASKING_PRICE",
                       period_key="2026-09-26")
        self.assertEqual(integrity_report(op)["unresolved_count"],0)

if __name__=="__main__":
    unittest.main()
