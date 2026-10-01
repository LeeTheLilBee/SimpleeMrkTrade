"""BBX136–155 owner experience deterministic regression."""
from __future__ import annotations
import unittest
from copy import deepcopy

from buybox.core import new_opportunity,evaluate
from buybox.owner_experience import (
    ensure_ux_schema,preferences,set_density,record_triage,triage_map,
    universal_search,paged_opportunities,pulse_snapshot,integration_cockpit,
    revision_diff,provenance,record_acceptance_defect,acceptance_defects,
    resolve_acceptance_defect,
)
from buybox.store import connect,save

class OwnerExperienceUnitTests(unittest.TestCase):
    def setUp(self):
        self.db=connect(); ensure_ux_schema(self.db)

    def tearDown(self): self.db.close()

    def make(self,i,vertical="atm"):
        op=new_opportunity(vertical,f"Route {i}",10000+i,
            source={"url":f"https://example.com/{i}","type":"OWNER_ENTERED"},
            location={"city":"Griffin" if i%2==0 else "Atlanta","region":"GA"})
        return save(self.db,op,"OpportunityCreated")

    def test_pagination_and_search_are_bounded(self):
        for i in range(65): self.make(i)
        p1=paged_opportunities(self.db,page=1,page_size=24)
        p3=paged_opportunities(self.db,page=3,page_size=24)
        self.assertEqual(p1["total"],65); self.assertEqual(len(p1["items"]),24)
        self.assertEqual(len(p3["items"]),17); self.assertEqual(p1["pages"],3)
        results=universal_search(self.db,"Griffin",limit=7)
        self.assertEqual(len(results),7)
        self.assertTrue(all("location" in r["matched_in"] for r in results))

    def test_density_triage_and_pulse_are_owner_workflow_only(self):
        op=self.make(1)
        self.assertEqual(preferences(self.db)["density"],"STANDARD")
        self.assertEqual(set_density(self.db,"CALM")["density"],"CALM")
        record_triage(self.db,op["id"],"FOCUS","Review this","local_owner")
        self.assertEqual(triage_map(self.db,[op["id"]])[op["id"]]["state"],"FOCUS")
        pulse=pulse_snapshot(self.db)
        self.assertEqual(pulse["active_opportunities"],1)
        self.assertEqual(pulse["needs_owner"],1)
        self.assertEqual(pulse["external_blockers"],1)

    def test_revision_diff_and_provenance_are_descriptive(self):
        op=self.make(2)
        newer=deepcopy(op); newer["asking_price"]="12345.00"
        newer=save(self.db,newer,"AskingChanged",expected_revision=op["version"])
        diff=revision_diff(self.db,op["id"])
        self.assertEqual(diff["from_revision"],1); self.assertEqual(diff["to_revision"],2)
        self.assertTrue(any(x["field"]=="asking_price" for x in diff["changes"]))
        rows=provenance(newer,evaluate(newer))
        self.assertTrue(any(x["kind"]=="RULE_FINDING" for x in rows))

    def test_integration_cockpit_never_invents_external_proof(self):
        a=self.make(3,"atm"); b=self.make(4,"business")
        rows={x["kind"]:x for x in integration_cockpit([a,b])}
        self.assertEqual(rows["TOWER_PROTECTED_ACTION"]["present"],0)
        self.assertEqual(rows["TOWER_PROTECTED_ACTION"]["state"],"AWAITING_EXTERNAL_PROOF")
        self.assertEqual(rows["OPERATIONS_RECEIVER_ACCEPTANCE"]["required"],1)

    def test_acceptance_defects_are_separate_release_records(self):
        d=record_acceptance_defect(self.db,area="Discover",severity="HIGH",
            title="Card clipped",detail="Owner walkthrough observation",actor_ref="local_owner")
        self.assertEqual(acceptance_defects(self.db)[0]["status"],"OPEN")
        self.assertTrue(resolve_acceptance_defect(self.db,d["id"],actor_ref="local_owner"))
        self.assertEqual(acceptance_defects(self.db)[0]["status"],"RESOLVED")

if __name__=="__main__": unittest.main()
