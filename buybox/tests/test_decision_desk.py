"""BBX071 — owner research notes bound to exact persistent source digest."""
import unittest
from copy import deepcopy

from buybox.core import new_opportunity,add_evidence
from buybox.store import connect,load,save
from buybox.decision_desk import (
    CHOICES,DecisionDeskError,decision_dossier,record_owner_research_disposition,
)
from buybox.soulaana import context
from buybox.registry import VERTICALS

class DecisionDeskTests(unittest.TestCase):
    def setUp(self):
        self.db=connect()
        self.op=save(self.db,new_opportunity("atm","Actual owner-entered route",95000),
                     event_type="OpportunityCreated")
    def tearDown(self):
        self.db.close()

    def test_all_verticals_default_to_unknown_external_authority(self):
        for vertical in VERTICALS:
            with self.subTest(vertical=vertical):
                d=decision_dossier(new_opportunity(vertical,"Owner-recorded property"))
                self.assertFalse(d["acquisition_authorized"])
                self.assertFalse(d["tower_protected_action_authorized"])
                self.assertEqual(d["teller_money_ready"],"UNKNOWN")
                self.assertEqual(d["teller_management_ready"],"UNKNOWN")
                self.assertEqual(d["historical_notes"],[])

    def test_stored_source_digest_required_and_no_approval(self):
        before=deepcopy(self.op)
        revised,note=record_owner_research_disposition(
            self.db,self.op,choice="WATCH",rationale="Await actual machine ownership proof",
            actor_ref="local_owner")
        self.assertEqual(self.op,before)
        self.assertEqual(len(revised["research_decisions"]),1)
        self.assertEqual(len(note["source_snapshot_digest"]),64)
        self.assertEqual(len(note["local_snapshot_sha256"]),64)
        self.assertEqual(note["recorded_opportunity_revision"],self.op["version"]+1)
        for key in ("authorizes_purchase","authorizes_offer_or_loi","authorizes_closing",
                    "transmitted_externally","updates_lifecycle"):
            self.assertFalse(note[key])
        self.assertEqual(note["teller_money_ready"],"UNKNOWN")
        self.assertIsNone(note["tower_authorization"])
        stored=save(self.db,revised,"OwnerResearchDispositionRecorded",
                    expected_revision=self.op["version"])
        self.assertEqual(stored["lifecycle"],before["lifecycle"])
        self.assertEqual(decision_dossier(stored)["historical_notes"][0]["display_state"],
                         "LATEST_RECORDED_ANALYTICAL_NOTE")
        self.assertFalse(decision_dossier(stored)["acquisition_authorized"])
        result=context(stored,"decision")
        self.assertTrue(any(x["classification"]=="OWNER_RESEARCH_DISPOSITION"
                            and note["id"] in x["references"] for x in result["entries"]))
        self.assertFalse(result["can_authorize"])

    def test_later_revision_preserves_historical_snapshot(self):
        revised,note=record_owner_research_disposition(
            self.db,self.op,choice="REQUEST_EVIDENCE",
            rationale="Obtain the dated processor source first",actor_ref="local_owner")
        stored=save(self.db,revised,expected_revision=self.op["version"])
        stored["name"]="Owner later changed deal label"
        later=save(self.db,stored,expected_revision=stored["version"])
        view=decision_dossier(later)["historical_notes"][0]
        self.assertEqual(view["display_state"],"HISTORICAL_OPPORTUNITY_VERSION")
        self.assertEqual(view["source_snapshot_digest"],note["source_snapshot_digest"])
        self.assertEqual(view["rationale"],note["rationale"])
        self.assertFalse(view["authorizes_purchase"])

    def test_unrelated_claims_and_forged_actor_source_fail(self):
        original=deepcopy(self.op)
        changed=deepcopy(self.op)
        changed["name"]="Changed without saving"
        with self.assertRaisesRegex(DecisionDeskError,"SOURCE_SNAPSHOT_CHANGED"):
            record_owner_research_disposition(
                self.db,changed,choice="WATCH",rationale="Needs actual proof",
                actor_ref="local_owner")
        with self.assertRaisesRegex(DecisionDeskError,"UNAUTHORIZED_OR_UNKNOWN"):
            record_owner_research_disposition(
                self.db,self.op,choice="APPROVE_ACQUISITION",
                rationale="Should never be allowed",actor_ref="local_owner")
        with self.assertRaisesRegex(DecisionDeskError,"EVIDENCE_REFERENCE_NOT_IN_OPPORTUNITY"):
            record_owner_research_disposition(
                self.db,self.op,choice="WATCH",rationale="Need more documentation",
                actor_ref="local_owner",cited_evidence_ids=["other-opportunity-file"])
        with self.assertRaisesRegex(DecisionDeskError,"OWNER_ACTOR_REQUIRED"):
            record_owner_research_disposition(
                self.db,self.op,choice="WATCH",rationale="Need source",
                actor_ref="")
        self.assertEqual(load(self.db,self.op["id"]),original)

    def test_only_exact_local_evidence_ids_can_be_cited(self):
        e=add_evidence(self.op,"processor_statements",reference="source-1",source="Seller")
        self.op=save(self.db,self.op,event_type="EvidenceReceived",
                     expected_revision=1)
        revised,note=record_owner_research_disposition(
            self.db,self.op,choice="DEFER",rationale="Waiting on complete monthly statements",
            actor_ref="local_owner",
            cited_evidence_ids=[e["id"],e["id"]])
        self.assertEqual(note["cited_evidence_ids"],[e["id"]])
        self.assertFalse(note["transmitted_externally"])
        self.assertEqual(decision_dossier(revised)["teller_money_ready"],"UNKNOWN")

    def test_stored_digest_tamper_rejected(self):
        self.db.execute("UPDATE revisions SET digest=? WHERE opportunity_id=?",
                        ("f"*64,self.op["id"]))
        self.db.commit()
        with self.assertRaisesRegex(DecisionDeskError,"PERSISTED_SOURCE_UNAVAILABLE"):
            record_owner_research_disposition(self.db,self.op,choice="DECLINE",
                 rationale="Source record cannot be trusted",actor_ref="local_owner")

if __name__=="__main__":
    unittest.main()
