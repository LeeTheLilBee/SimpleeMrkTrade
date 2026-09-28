"""BBX107-130 Intelligence Studio unit regression."""
from __future__ import annotations
import unittest

from buybox.core import new_opportunity
from buybox.expansion_store import ensure_schema,load_thesis,save_thesis,add_record,records
from buybox.intelligence_studio import (
    command_map,portfolio_fit,deal_dna,predicted_vs_actual,impact_summary,
    knowledge_graph,geo_expansion,capital_board,what_if,playbook,build_portfolio_studio,
)
from buybox.store import connect,save

class IntelligenceStudioUnitTests(unittest.TestCase):
    def setUp(self):
        self.db=connect(); ensure_schema(self.db)
        self.atm=save(self.db,new_opportunity("atm","Georgia route",95000,location={"city":"Griffin","region":"GA"}),event_type="OpportunityCreated")
        self.mf=save(self.db,new_opportunity("multifamily","Georgia flats",250000,location={"city":"Griffin","region":"GA"}),event_type="OpportunityCreated")

    def tearDown(self): self.db.close()

    def test_owner_thesis_persists_without_becoming_policy(self):
        saved=save_thesis(self.db,priorities=["ATM","multifamily"],preferred_regions=["GA"],avoid=["partners"],sequence=["ATM first"],notes="Owner strategy")
        self.assertEqual(saved["priorities"],["ATM","multifamily"])
        loaded=load_thesis(self.db)
        self.assertEqual(loaded["preferred_regions"],["GA"])
        fit=portfolio_fit(self.atm,[self.atm,self.mf],loaded)
        self.assertEqual(fit["thesis"]["alignment"],"ALIGNED")
        self.assertEqual(fit["portfolio_authority"],"ANALYTICAL_ONLY")

    def test_expansion_records_are_separate_owner_research(self):
        rec=add_record(self.db,self.atm["id"],"CAPEX_ITEM",{"title":"Replace cassette","estimated_cost":"700","severity":"MEDIUM"})
        self.assertEqual(rec["kind"],"CAPEX_ITEM")
        rows=records(self.db,opportunity_id=self.atm["id"])
        self.assertEqual(rows[0]["payload"]["title"],"Replace cassette")
        self.assertNotIn("CAPEX_ITEM",self.atm.get("evidence",[]))

    def test_command_map_and_geo_expansion_use_only_saved_location(self):
        cmap=command_map([self.atm,self.mf])
        self.assertEqual(cmap[0]["city"],"Griffin")
        self.assertEqual(cmap[0]["count"],2)
        geo=geo_expansion([self.atm,self.mf])
        self.assertEqual(geo[0]["vertical_diversity"],2)

    def test_deal_dna_is_descriptive_not_recommendation(self):
        matches=deal_dna(self.atm,[self.atm,self.mf])
        self.assertEqual(matches[0]["id"],self.mf["id"])
        self.assertIn("same region",matches[0]["reasons"])

    def test_predicted_actual_and_impact_do_not_change_financial_truth(self):
        add_record(self.db,self.atm["id"],"PERFORMANCE_ACTUAL",{"period":"2027-Q1","actual_net":"12000","note":"Owner-entered actual"})
        add_record(self.db,self.atm["id"],"COMMUNITY_IMPACT",{"dimension":"local jobs","note":"Potential hiring"})
        rs=records(self.db,opportunity_id=self.atm["id"])
        pa=predicted_vs_actual(self.atm,rs)
        self.assertEqual(pa["learning_state"],"ACTUAL_AVAILABLE")
        impact=impact_summary(rs)
        self.assertFalse(impact["financial_score_affected"])

    def test_knowledge_graph_uses_recorded_counterparties_and_lenders_only(self):
        add_record(self.db,self.atm["id"],"COUNTERPARTY",{"name":"Seller LLC","role":"seller","note":"owner-entered"})
        graph=knowledge_graph(self.atm,records(self.db,opportunity_id=self.atm["id"]))
        self.assertTrue(any(n["label"]=="Seller LLC" for n in graph["nodes"]))
        self.assertTrue(any(e["relationship"]=="seller" for e in graph["edges"]))

    def test_capital_board_never_reports_balance_or_direct_ob_access(self):
        row=capital_board([self.atm])[0]
        self.assertIsNone(row["deployable_amount"])
        self.assertFalse(row["direct_ob_access"])
        self.assertFalse(row["teller_proof_present"])

    def test_what_if_combines_requirements_without_readiness(self):
        report=what_if([self.atm,self.mf])
        self.assertEqual(report["asking_total"],"345000.00")
        self.assertEqual(report["count"],2)
        self.assertFalse(report["capital_readiness_assumed"])

    def test_vertical_playbooks_cover_every_registered_expansion_vertical(self):
        for vertical in ("atm","multifamily","commercial","laundromat","land_farm","business","equipment"):
            op=new_opportunity(vertical,"Candidate")
            pb=playbook(op)
            self.assertTrue(pb["steps"])
            self.assertFalse(pb["legal_requirements_claimed"])

    def test_portfolio_studio_is_source_projection_only(self):
        thesis=load_thesis(self.db)
        studio=build_portfolio_studio([self.atm,self.mf],thesis,lambda oid:records(self.db,opportunity_id=oid))
        self.assertEqual(len(studio["command_map"]),1)
        self.assertEqual(len(studio["capital_board"]),2)

if __name__=="__main__":
    unittest.main()
