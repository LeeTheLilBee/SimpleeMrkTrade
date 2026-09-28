"""BBX101: external authority enters BuyBox only through trusted adapters."""
import unittest
from datetime import datetime, timezone

from buybox.core import new_opportunity
from buybox.external_proof_gate import ExternalProofError, integration_readiness, record_verified_external_proof
from buybox.store import connect, save

NOW=datetime(2026,9,28,15,0,tzinfo=timezone.utc)

class ExternalProofGateTests(unittest.TestCase):
    def setUp(self):
        self.db=connect()
        self.op=save(self.db,new_opportunity("atm","Source-bound route",95000),event_type="OpportunityCreated")

    def tearDown(self):
        self.db.close()

    def claims(self,kind):
        from buybox.tower_action_draft import stored_source_snapshot
        src=stored_source_snapshot(self.db,self.op["id"])
        return {
            "authenticated":True,
            "issuer":"trusted-"+kind.lower().replace("_","-"),
            "receipt_ref":"receipt-"+kind.lower().replace("_","-"),
            "opportunity_id":src["opportunity_id"],
            "opportunity_revision":src["opportunity_revision"],
            "input_snapshot_digest":src["input_snapshot_digest"],
            "purpose":"acquisition-readiness",
        }

    def add(self,kind):
        raw={"untrusted":"body"}
        verifier=lambda _: self.claims(kind)
        revised,record=record_verified_external_proof(self.db,self.op,kind=kind,raw_proof=raw,verifier=verifier,now_utc=NOW)
        self.op=save(self.db,revised,event_type="ExternalProofRecorded",expected_revision=self.op["version"])
        return record

    def test_no_verifier_or_browser_shaped_ready_is_rejected(self):
        with self.assertRaisesRegex(ExternalProofError,"TRUSTED_VERIFIER_REQUIRED"):
            record_verified_external_proof(self.db,self.op,kind="TELLER_MONEY_AND_MANAGEMENT",raw_proof={"ready":True},verifier=None)
        with self.assertRaisesRegex(ExternalProofError,"NOT_AUTHENTICATED"):
            record_verified_external_proof(self.db,self.op,kind="TELLER_MONEY_AND_MANAGEMENT",raw_proof={"ready":True},verifier=lambda _:{"authenticated":False})

    def test_verified_claims_are_exactly_source_bound_and_nonexecuting(self):
        record=self.add("TOWER_PROTECTED_ACTION")
        self.assertFalse(record["browser_supplied_authority"])
        self.assertFalse(record["authorizes_purchase"])
        self.assertFalse(record["authorizes_money"])
        report=integration_readiness(self.op)
        self.assertIn("TELLER_MONEY_AND_MANAGEMENT",report["missing"])
        self.assertFalse(report["authorizes_purchase"])

    def test_source_mismatch_is_rejected(self):
        bad=self.claims("VAULT_CANONICAL_ARCHIVAL")
        bad["opportunity_revision"] += 1
        with self.assertRaisesRegex(ExternalProofError,"SOURCE_MISMATCH"):
            record_verified_external_proof(self.db,self.op,kind="VAULT_CANONICAL_ARCHIVAL",raw_proof={},verifier=lambda _:bad)

    def test_all_external_proofs_still_require_owner_release(self):
        for kind in ("TOWER_PROTECTED_ACTION","TELLER_MONEY_AND_MANAGEMENT","VAULT_CANONICAL_ARCHIVAL","OPERATIONS_RECEIVER_ACCEPTANCE"):
            self.add(kind)
        report=integration_readiness(self.op)
        self.assertTrue(report["external_proofs_complete"])
        self.assertEqual(report["missing"],[])
        self.assertTrue(report["owner_release_required"])
        self.assertFalse(report["hosted_runtime_certified"])
        self.assertFalse(report["authorizes_closing"])
        self.assertFalse(report["can_mark_operational"])

    def test_later_revision_makes_old_proofs_noncurrent(self):
        self.add("TOWER_PROTECTED_ACTION")
        self.op=save(self.db,{**self.op,"asking_price":"90000.00"},event_type="OpportunityUpdated",expected_revision=self.op["version"])
        report=integration_readiness(self.op)
        self.assertIn("TOWER_PROTECTED_ACTION",report["missing"])

    def test_other_vertical_does_not_invent_receiver_requirement(self):
        op=save(self.db,new_opportunity("land_farm","Parcel",50000),event_type="OpportunityCreated")
        report=integration_readiness(op)
        self.assertNotIn("OPERATIONS_RECEIVER_ACCEPTANCE",[r["kind"] for r in report["requirements"]])

if __name__=="__main__":
    unittest.main()
