"""Soulaana is grounded, read-only and cannot invent external authority."""
import unittest
from buybox.core import new_opportunity,add_evidence
from buybox.soulaana import context

class SoulaanaContextTests(unittest.TestCase):
    def test_new_opportunity_exposes_missing_not_invented(self):
        op=new_opportunity("multifamily","Actual owner-entered property")
        result=context(op,"overview")
        self.assertFalse(result["live_ai_connected"])
        self.assertFalse(result["can_authorize"])
        self.assertEqual(result["readiness"],"UNKNOWN")
        self.assertTrue(any(e["classification"]=="MISSING_OR_UNVERIFIED" for e in result["entries"]))
        self.assertFalse(any("verified net profit" in e["text"].lower() for e in result["entries"]))

    def test_owner_document_has_source_reference_and_truth_label(self):
        op=new_opportunity("atm","Document review")
        evidence=add_evidence(op,"processor_statements","DOCUMENT_SUPPORTED",
                              reference="owner-reviewed-internal-file",source="Seller")
        result=context(op,"evidence")
        lines=[x for x in result["entries"] if "processor statements" in x["text"].lower()]
        self.assertTrue(lines)
        self.assertEqual(lines[0]["classification"],"DOCUMENTARY_SUPPORT")
        self.assertIn("owner-reviewed-internal-file",lines[0]["references"])

    def test_changes_use_recorded_provenance(self):
        op=new_opportunity("land_farm","Parcel")
        op["last_material_change"]={"fields":["asking_price"],"reason":"Owner recorded price revision",
                                   "source_reference":"seller-email-reference"}
        result=context(op,"changes")
        self.assertTrue(any("seller-email-reference" in e["references"] for e in result["entries"]))

    def test_red_team_does_not_invent_stress_results(self):
        op=new_opportunity("atm","Route")
        result=context(op,"red_team")
        self.assertTrue(any(e["classification"]=="MODELING_LIMITATION" for e in result["entries"]))

    def test_local_snapshot_is_not_misrepresented_as_vault_archived(self):
        op=new_opportunity("atm","Original file")
        op["snapshots"]=[{"snapshot_id":"local-snapshot-1","opportunity_revision":2,
                          "archive_state":"NOT_REQUESTED",
                          "evidence_versions":[{"evidence_id":"original-evidence-1"}]}]
        report=context(op,"evidence")
        proof=[x for x in report["entries"] if x["classification"]=="LOCAL_PROOF_SNAPSHOT"]
        self.assertEqual(len(proof),1)
        self.assertEqual(proof[0]["label"],"NOT_ARCHIVED")
        self.assertIn("local-snapshot-1",proof[0]["references"])
        self.assertIn("NOT been requested",proof[0]["text"])
        self.assertFalse(report["can_authorize"])

    def test_reject_unsupported_context(self):
        with self.assertRaises(ValueError):
            context(new_opportunity("atm","Route"),"approve_purchase")

if __name__=="__main__":unittest.main()
