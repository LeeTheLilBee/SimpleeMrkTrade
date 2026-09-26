"""Synthetic, offline tests: no production accounts, approvals or listing feeds."""
import unittest
from datetime import datetime, timedelta, timezone
from buybox.registry import VERTICALS, validate_registry
from buybox.core import (new_opportunity, add_evidence, evaluate, scenario_calculation,
                         compare_opportunities, soulaana_brief, evidence_summary)
from buybox.store import connect, save, load, history, activity
from buybox.contracts import validate_teller, validate_tower, prepare_handoff

def proof(op):
    for requirement in VERTICALS[op["vertical"]]["evidence"]:
        add_evidence(op, requirement["kind"], "DOCUMENT_SUPPORTED", "synthetic-test-record")

def metric(op, key, value):
    op["metrics"][key] = {"value": str(value), "state": "DOCUMENT_SUPPORTED",
                          "source": "synthetic-test-record", "period": "2025-01/2025-12"}

def ready(op):
    op["readiness"]["teller"] = {"source": "teller", "status": "READY",
        "money_status": "READY", "management_status": "READY",
        "authority_reference": "synthetic-not-real",
        "valid_until": (datetime.now(timezone.utc)+timedelta(days=1)).isoformat()}

class BuyBoxFoundationTests(unittest.TestCase):
    def test_registry_is_universal(self):
        self.assertTrue(validate_registry())
        self.assertEqual(len(VERTICALS), 7)
        self.assertEqual(VERTICALS["multifamily"]["handoff"], "grounds")
        self.assertEqual(VERTICALS["atm"]["money_and_capacity_source"], "teller")

    def test_unknown_vertical_rejected(self):
        with self.assertRaises(ValueError):
            new_opportunity("fake", "Example")

    def test_missing_is_not_zero(self):
        op = new_opportunity("atm", "Missing expenses", 95000)
        metric(op, "annual_revenue", 100000)
        self.assertEqual(scenario_calculation(op)["status"], "INSUFFICIENT_DATA")
        self.assertEqual(evidence_summary(op)["confidence_percent"], 0)

    def test_zero_earnings_no_invalid_multiple(self):
        op = new_opportunity("atm", "Zero", 95000)
        metric(op, "annual_revenue", 50000)
        metric(op, "annual_expenses", 50000)
        calc = scenario_calculation(op)
        self.assertEqual(calc["net"], "0.00")
        self.assertIsNone(calc["purchase_multiple"])

    def test_mixed_ownership_is_rejected(self):
        op = new_opportunity("atm", "Mixed machines", 95000)
        proof(op)
        metric(op, "annual_revenue", 80000)
        metric(op, "annual_expenses", 30000)
        ready(op)
        op["vertical_data"]["machine_inventory"] = [
            {"id": str(n), "ownership": "SELLER_OWNED"} for n in range(6)
        ] + [{"id": "6", "ownership": "THIRD_PARTY"}, {"id": "7", "ownership": "THIRD_PARTY"}]
        result = evaluate(op)
        self.assertEqual(result["judgment"], "REJECTED")
        self.assertFalse(result["purchase_authorized"])
        self.assertTrue(any(f["rule_id"] == "ATM-R001" for f in result["findings"]))

    def test_complete_atm_screening_not_closing(self):
        op = new_opportunity("atm", "Complete", 95000)
        proof(op)
        metric(op, "annual_revenue", 80000)
        metric(op, "annual_expenses", 30000)
        ready(op)
        op["vertical_data"]["machine_inventory"] = [
            {"id": str(n), "ownership": "SELLER_OWNED"} for n in range(8)]
        result = evaluate(op)
        self.assertEqual(result["judgment"], "REVIEW")
        self.assertEqual(result["teller_readiness"], "UNKNOWN")
        self.assertFalse(result["closing_authorized"])
        self.assertFalse(result["purchase_authorized"])

    def test_readiness_without_authority_not_ready(self):
        op = new_opportunity("atm", "Claimed ready", 95000)
        proof(op)
        metric(op, "annual_revenue", 80000)
        metric(op, "annual_expenses", 30000)
        op["readiness"]["teller"] = {"status": "READY"}
        self.assertEqual(evaluate(op)["teller_readiness"], "UNKNOWN")

    def test_claimed_evidence_not_verified(self):
        op = new_opportunity("atm", "Claims", 95000)
        add_evidence(op, "processor_statements", "CLAIMED")
        self.assertIn("processor_statements", evidence_summary(op)["missing_critical"])

    def test_stress_preserves_original_case(self):
        op = new_opportunity("atm", "Stress", 95000)
        metric(op, "annual_revenue", 80000)
        metric(op, "annual_expenses", 30000)
        self.assertEqual(scenario_calculation(op)["net"], "50000.00")
        self.assertEqual(scenario_calculation(op, "0.75", "2")["net"], "0.00")
        self.assertEqual(scenario_calculation(op)["net"], "50000.00")

    def test_exact_decimal(self):
        op = new_opportunity("atm", "Decimals", "95.00")
        metric(op, "annual_revenue", "0.30")
        metric(op, "annual_expenses", "0.20")
        self.assertEqual(scenario_calculation(op)["net"], "0.10")

    def test_revision_history_and_conflict(self):
        db = connect()
        op = save(db, new_opportunity("land_farm", "Acreage"), "OpportunityCreated")
        self.assertEqual(op["version"], 1)
        op["name"] = "Revised"
        op = save(db, op, expected_revision=1)
        self.assertEqual(load(db, op["id"])["name"], "Revised")
        self.assertEqual(len(history(db, op["id"])), 2)
        self.assertEqual(len(activity(db, op["id"])), 2)
        with self.assertRaisesRegex(ValueError, "REVISION_CONFLICT"):
            save(db, op, expected_revision=1)

    def test_comparison_limits(self):
        ops = [new_opportunity("atm", str(i)) for i in range(5)]
        with self.assertRaises(ValueError):
            compare_opportunities(ops)
        self.assertEqual(len(compare_opportunities(ops[:2])), 2)

    def test_soulaana_cannot_approve(self):
        op = new_opportunity("atm", "Explain")
        brief = soulaana_brief(op)
        self.assertFalse(brief["can_approve"])
        self.assertFalse(brief["can_change_evidence"])
        self.assertEqual(brief["grounding"]["opportunity_id"], op["id"])

    def test_teller_and_tower_shape_validation(self):
        self.assertFalse(validate_teller({"source": "teller", "status": "READY"}))
        self.assertFalse(validate_tower({"source": "tower", "decision": "APPROVED"}, "CLOSING", "id"))

    def test_handoff_requires_authority(self):
        op = new_opportunity("multifamily", "Property")
        op["lifecycle"] = "ACQUIRED"
        with self.assertRaises(ValueError):
            prepare_handoff(op, {}, None)
        with self.assertRaisesRegex(ValueError, "AUTHENTICATED_TOWER_ADAPTER_UNAVAILABLE"):
            prepare_handoff(op, {}, "receipt-shaped-string-is-not-authority")

if __name__ == "__main__":
    unittest.main()
