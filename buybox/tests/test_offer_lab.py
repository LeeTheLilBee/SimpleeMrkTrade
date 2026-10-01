"""BBX096: private Offer Lab scenarios are source-bound analysis, never offers."""
from __future__ import annotations

import unittest

from buybox.core import new_opportunity
from buybox.offer_lab import OfferLabError, analyze_offer_scenario, current_offer_scenarios, offer_lab_snapshot, record_offer_scenario
from buybox.store import connect, save


class OfferLabTests(unittest.TestCase):
    def setUp(self):
        self.db=connect()
        self.op=save(self.db,new_opportunity("atm","Owner-recorded route",100000),event_type="OpportunityCreated")

    def tearDown(self):
        self.db.close()

    def record(self, **changes):
        data=dict(name="Conservative private scenario",proposed_purchase_price="90000",earnest_money="2500",requested_seller_credit="3000",due_diligence_days="21",financing_contingency=True,planned_closing_date="2026-10-30",rationale="Compare a lower private price without contacting the seller.",terms_note="Internal analysis only.",actor_ref="local_owner",today="2026-09-28")
        data.update(changes)
        return record_offer_scenario(self.db,self.op,**data)

    def test_private_scenario_never_becomes_offer_or_authority(self):
        revised,record=self.record()
        self.assertEqual(revised["lifecycle"],self.op["lifecycle"])
        self.assertFalse(record["transmitted_to_seller"])
        self.assertFalse(record["is_loi"])
        self.assertFalse(record["is_contract"])
        self.assertIsNone(record["tower_authorization"])
        self.assertEqual(record["teller_readiness"],"UNKNOWN")
        self.assertFalse(record["authorizes_offer"])
        self.assertFalse(record["authorizes_purchase"])
        self.assertFalse(record["authorizes_money"])
        analysis=analyze_offer_scenario(revised,record,today="2026-09-28")
        self.assertEqual(analysis["status"],"PRIVATE_SCENARIO_CURRENT")
        self.assertEqual(analysis["price_delta_from_current_asking"],"-10000.00")
        self.assertEqual(analysis["net_price_before_other_costs"],"87000.00")
        self.assertFalse(analysis["recommended_option"])
        self.assertFalse(analysis["authorizes_offer"])

    def test_stale_source_and_bad_terms_fail_closed(self):
        forged=dict(self.op,asking_price="99000.00")
        with self.assertRaisesRegex(OfferLabError,"SOURCE_CHANGED"):
            record_offer_scenario(self.db,forged,name="Stale",proposed_purchase_price="90000",earnest_money="0",requested_seller_credit="0",due_diligence_days="10",financing_contingency=False,planned_closing_date="2026-10-30",rationale="stale",actor_ref="local_owner",today="2026-09-28")
        for change,reason in [
            ({"proposed_purchase_price":"0"},"PROPOSED_PRICE_INVALID"),
            ({"earnest_money":"100001"},"EARNEST_MONEY_EXCEEDS"),
            ({"requested_seller_credit":"100001"},"SELLER_CREDIT_EXCEEDS"),
            ({"due_diligence_days":"366"},"DUE_DILIGENCE_DAYS_OUT_OF_RANGE"),
            ({"planned_closing_date":"2026-09-27"},"PLANNED_CLOSING_DATE_IN_PAST"),
        ]:
            with self.subTest(change=change):
                with self.assertRaisesRegex(OfferLabError,reason):
                    self.record(**change)

    def test_append_only_correction_preserves_history(self):
        revised,first=self.record()
        self.op=save(self.db,revised,event_type="OwnerOfferScenarioRecorded",expected_revision=self.op["version"])
        revised,second=record_offer_scenario(self.db,self.op,name="Corrected private scenario",proposed_purchase_price="88000",earnest_money="2500",requested_seller_credit="3000",due_diligence_days="21",financing_contingency=True,planned_closing_date="2026-10-30",rationale="Correct the private analysis only.",terms_note="",actor_ref="local_owner",supersedes=first["id"],correction_reason="Owner changed proposed analysis price.",today="2026-09-28")
        current=current_offer_scenarios(revised)
        self.assertEqual([x["id"] for x in current],[second["id"]])
        report=offer_lab_snapshot(revised,today="2026-09-28")
        states={x["id"]:x["display_state"] for x in report["scenarios"]}
        self.assertEqual(states[first["id"]],"SUPERSEDED_PRIVATE_SCENARIO")
        self.assertEqual(states[second["id"]],"CURRENT_PRIVATE_SCENARIO")
        self.assertIsNone(report["recommended_scenario_id"])
        self.assertFalse(report["seller_contact_sent"])
        self.assertFalse(report["authorizes_purchase"])

    def test_all_verticals_remain_nonexecuting(self):
        for vertical in ("atm","multifamily","commercial","laundromat","land_farm","business","equipment"):
            with self.subTest(vertical=vertical):
                op=new_opportunity(vertical,"Private scenario")
                report=offer_lab_snapshot(op,today="2026-09-28")
                self.assertFalse(report["seller_contact_sent"])
                self.assertFalse(report["tower_authorized"])
                self.assertEqual(report["teller_readiness"],"UNKNOWN")
                self.assertFalse(report["authorizes_offer"])
                self.assertFalse(report["authorizes_purchase"])
                self.assertFalse(report["authorizes_money"])


if __name__=="__main__":
    unittest.main()
