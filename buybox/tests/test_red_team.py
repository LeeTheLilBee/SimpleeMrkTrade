"""Owner financial stresses always derive from current persisted original-backed data."""
import tempfile
import unittest
from copy import deepcopy
from uuid import uuid4
from pathlib import Path

from buybox.core import new_opportunity, add_evidence
from buybox.evidence import artifact_descriptor
from buybox.store import connect,save,load
from buybox.red_team import (
    RedTeamError, model_financial_stress, record_owner_financial_stress,
    red_team_report,
)
from buybox.soulaana import context

PERIOD="2025-01-01 / 2025-12-31"

def backed_op(vertical="atm"):
    op=new_opportunity(vertical,"Actual-source test fixture",100000)
    for kind,amount,category in (
        ("annual_revenue","80000","processor_statements" if vertical=="atm" else "financial_statements"),
        ("annual_expenses","30000","expense_records"),
    ):
        a=artifact_descriptor(("%PDF-1.7\n"+kind+"\n%%EOF").encode(),
            filename=kind+".pdf",mime="application/pdf",
            storage_reference="private-test-"+str(uuid4()),source_party="Test-only source")
        op.setdefault("artifacts",[]).append(a)
        e=add_evidence(op,category,status="DOCUMENT_SUPPORTED",
                       reference=a["id"],source="Test-only reviewed original")
        e["artifact_id"]=a["id"]
        op["metrics"][kind]={"value":amount,"state":"DOCUMENT_SUPPORTED",
                             "evidence_id":e["id"],"period":PERIOD}
    return op

class RedTeamTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.db=connect(str(Path(self.tmp.name)/"redteam.sqlite3"))
        self.op=save(self.db,backed_op(),event_type="TestOpportunityCreated")
    def tearDown(self):
        self.db.close()
        self.tmp.cleanup()

    def test_current_real_source_and_calculation_frozen_as_owner_assumption(self):
        out=model_financial_stress(self.op,revenue_factor="0.75",expense_factor="1.20")
        self.assertEqual(out["recorded_operating_difference"],"50000.00")
        self.assertEqual(out["modeled_operating_difference"],"24000.00")
        self.assertEqual(out["modeled_difference_from_base"],"-26000.00")
        self.assertEqual(out["reporting_period"],PERIOD)
        self.assertEqual(len(out["source_metrics"]),2)
        self.assertFalse(out["funds_spendable"])
        revised,rec=record_owner_financial_stress(
            self.db,self.op,name="Owner-run stress",
            rationale="Owner asks what lower receipts and higher cost would do.",
            revenue_factor="0.75",expense_factor="1.20",
            actor_ref="local_owner")
        self.assertNotIn("owner_stress_records",self.op)
        self.assertEqual(rec["record_type"],"OWNER_ASSUMPTION_NOT_HISTORICAL_FACT")
        self.assertFalse(rec["executed"])
        self.assertFalse(rec["authorizes_purchase"])
        current=save(self.db,revised,expected_revision=self.op["version"],
                     event_type="OwnerFinancialStressRecorded")
        self.assertEqual(red_team_report(current)["records"][0]["freshness"],
                         "CURRENT_SOURCE_VERSION")
        self.assertEqual(load(self.db,current["id"])["owner_stress_records"][0]["id"],rec["id"])
        message=context(current,"red_team")
        self.assertTrue(any(e["classification"]=="OWNER_RECORDED_STRESS"
                            and rec["id"] in e["references"] for e in message["entries"]))
        self.assertFalse(message["can_authorize"])

    def test_scenario_recheck_is_historical_after_a_new_saved_revision(self):
        revised,record=record_owner_financial_stress(
            self.db,self.op,name="Volume uncertainty",rationale="Owner hypothetical.",
            revenue_factor="0.90",expense_factor="1",actor_ref="local_owner")
        current=save(self.db,revised,expected_revision=self.op["version"])
        changed=deepcopy(current)
        changed["asking_price"]="120000.00"
        changed=save(self.db,changed,expected_revision=current["version"])
        old=red_team_report(changed)["records"][0]
        self.assertEqual(old["freshness"],"HISTORICAL_RECHECK_REQUIRED")
        self.assertEqual(old["recorded_operating_difference"],"50000.00")
        self.assertFalse(red_team_report(changed)["has_current"])

    def test_no_document_or_wrong_period_fails_not_invented(self):
        op=new_opportunity("atm","Empty test fixture")
        with self.assertRaisesRegex(RedTeamError,"DOCUMENT_SUPPORTED_ANNUAL_METRICS_REQUIRED"):
            model_financial_stress(op,revenue_factor="1",expense_factor="1")
        altered=deepcopy(self.op)
        altered["metrics"]["annual_expenses"]["period"]="2024-01-01 / 2024-12-31"
        with self.assertRaisesRegex(RedTeamError,"MATCHING_SOURCE_PERIODS_REQUIRED"):
            model_financial_stress(altered,revenue_factor="1",expense_factor="1")
        altered=deepcopy(self.op)
        altered["artifacts"]=[]
        with self.assertRaisesRegex(RedTeamError,"ORIGINAL_SOURCE_DIGEST_REQUIRED"):
            model_financial_stress(altered,revenue_factor="1",expense_factor="1")

    def test_no_unsigned_factors_nan_or_overreach(self):
        for value in ("-0.1","NaN","1e10","3.0001","4","", "1.12345"):
            with self.subTest(value=value), self.assertRaises(RedTeamError):
                model_financial_stress(self.op,revenue_factor=value,expense_factor="1")
        with self.assertRaises(RedTeamError):
            model_financial_stress(self.op,revenue_factor=1.0,expense_factor="1")
        zero=model_financial_stress(self.op,revenue_factor="0",expense_factor="1")
        self.assertEqual(zero["modeled_operating_difference"],"-30000.00")
        self.assertFalse(zero["automatically_favorable"])

    def test_persisted_revision_mismatch_prevents_replay(self):
        changed=deepcopy(self.op)
        changed["asking_price"]="99000.00"
        with self.assertRaisesRegex(RedTeamError,"SOURCE_CHANGED_BEFORE_STRESS_RECORDED"):
            record_owner_financial_stress(
                self.db,changed,name="Unstored edit",rationale="Not allowed.",
                revenue_factor="1",expense_factor="1",actor_ref="local_owner")
        self.db.execute("UPDATE revisions SET digest=? WHERE opportunity_id=?",
                        ("a"*64,self.op["id"]))
        self.db.commit()
        with self.assertRaisesRegex(RedTeamError,"CURRENT_PERSISTED_SOURCE_UNAVAILABLE"):
            record_owner_financial_stress(
                self.db,self.op,name="Corrupt source",rationale="Fail closed.",
                revenue_factor="1",expense_factor="1",actor_ref="local_owner")

if __name__=="__main__":unittest.main()
