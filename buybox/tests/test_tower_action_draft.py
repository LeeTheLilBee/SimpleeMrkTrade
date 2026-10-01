"""Exact Tower TWR202–206 action-draft compatibility; no live permissions."""
from __future__ import annotations
from datetime import datetime, timezone
from hashlib import sha256
import importlib.util
import os
from pathlib import Path
import unittest

from buybox.core import new_opportunity
from buybox.store import connect,save
from buybox.tower_action_draft import (
    ACTION_PURPOSES, CLASSIFICATIONS, SCHEMA_VERSION,
    BuyBoxTowerActionPreparationError, prepare_untrusted_tower_action_draft,
    stored_source_snapshot, draft_still_matches_store,
)

NOW = datetime(2026,9,26,23,30,tzinfo=timezone.utc)

def draft(db, oid, **overrides):
    values = dict(requested_action="AUTHORIZE_CLOSING",
                  claimed_identity_ref="claimed-identity-1",
                  claimed_entity_ref="claimed-entity-1",
                  classification="CONFIDENTIAL",now_utc=NOW)
    values.update(overrides)
    return prepare_untrusted_tower_action_draft(db,oid,**values)

class TowerActionDraftTests(unittest.TestCase):
    def setUp(self):
        self.db=connect()
        self.op=save(self.db,new_opportunity("atm","Real source-bound deal",95000),
                     event_type="OpportunityCreated")

    def tearDown(self):
        self.db.close()

    def test_exact_persisted_revision_and_digest_not_user_supplied(self):
        result=draft(self.db,self.op["id"])
        packet=result["packet"]
        row=self.db.execute("SELECT current_json FROM opportunities WHERE id=?",
                            (self.op["id"],)).fetchone()
        self.assertEqual(packet["input_snapshot_digest"],
                         sha256(row["current_json"].encode()).hexdigest())
        self.assertEqual(packet["opportunity_revision"],1)
        self.assertEqual(packet["opportunity_id"],self.op["id"])
        self.assertEqual(packet["vertical_id"],"atm")
        self.assertEqual(packet["purpose"],"acquisition_closing")
        self.assertEqual(packet["schema_version"],SCHEMA_VERSION)
        self.assertFalse(result["authorizes_action"])
        self.assertFalse(result["requester_authenticated_by_tower"])
        self.assertFalse(result["external_call_made"])
        self.assertFalse(result["issuer_receipt_present"])
        self.assertEqual(result["teller_readiness"],"UNKNOWN")
        self.assertTrue(draft_still_matches_store(self.db,packet))
        self.assertNotIn("asking_price",packet)
        self.assertNotIn("storage_reference",packet)

    def test_material_revision_change_invalidates_draft(self):
        packet=draft(self.db,self.op["id"])["packet"]
        revised=dict(self.op,name="Seller updated asking terms",asking_price="89000.00")
        revised=save(self.db,revised,expected_revision=1)
        self.assertEqual(revised["version"],2)
        self.assertFalse(draft_still_matches_store(self.db,packet))
        new_packet=draft(self.db,self.op["id"])["packet"]
        self.assertEqual(new_packet["opportunity_revision"],2)
        self.assertNotEqual(packet["input_snapshot_digest"],new_packet["input_snapshot_digest"])

    def test_corrupt_or_absent_persisted_source_fails_closed(self):
        self.db.execute("UPDATE revisions SET digest=? WHERE opportunity_id=?",
                        ("a"*64,self.op["id"]))
        self.db.commit()
        with self.assertRaisesRegex(BuyBoxTowerActionPreparationError,"DIGEST_CONFLICT"):
            draft(self.db,self.op["id"])
        with self.assertRaisesRegex(BuyBoxTowerActionPreparationError,"NOT_FOUND"):
            draft(self.db,"missing-opportunity-id")

    def test_action_identity_classification_and_ttl_fail_closed(self):
        for field,value in [
            ("requested_action","APPROVE_ALL"),
            ("claimed_identity_ref","../path"),
            ("claimed_entity_ref",""),
            ("classification","PUBLIC"),
            ("lifetime_seconds",0),
            ("lifetime_seconds",301),
            ("lifetime_seconds",True),
            ("now_utc",datetime(2026,9,26,23,30)),
        ]:
            with self.subTest(field=field):
                with self.assertRaises(BuyBoxTowerActionPreparationError):
                    draft(self.db,self.op["id"],**{field:value})

    def test_all_action_purposes_are_exact_and_only_untrusted(self):
        for action,purpose in ACTION_PURPOSES.items():
            with self.subTest(action=action):
                result=draft(self.db,self.op["id"],requested_action=action)
                self.assertEqual(result["packet"]["purpose"],purpose)
                self.assertEqual(result["state"],"UNTRUSTED_DRAFT")
                self.assertFalse(result["authorizes_action"])

    def test_canonical_merged_tower_contract(self):
        path=os.environ.get("BUYBOX_TOWER_ACTION_CONTRACT_PATH")
        if not path:
            self.skipTest("Pinned merged TWR202–206 validator supplied by CI")
        full=Path(path)
        self.assertTrue(full.is_file(),"Exact Tower source checkout required")
        spec=importlib.util.spec_from_file_location("merged_twr202_buybox_contract",full)
        module=importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        for vertical in sorted(module.VERTICAL_IDS):
            opp=save(self.db,new_opportunity(vertical,vertical+" actual input"),
                     event_type="OpportunityCreated")
            for action in sorted(module.ACTION_PURPOSES):
                result=draft(self.db,opp["id"],requested_action=action)
                packet=result["packet"]
                valid=module.validate_buybox_action_draft(packet,now_utc=NOW)
                self.assertEqual(valid,packet)
                outcome=module.prepare_buybox_action_review(packet,now_utc=NOW)
                self.assertEqual(outcome["state"],"UNTRUSTED_DRAFT")
                self.assertFalse(outcome["authorizes_action"])
                self.assertTrue(module.draft_matches_current_opportunity(
                    packet,current_opportunity_id=opp["id"],
                    current_revision=opp["version"],
                    current_snapshot_digest=packet["input_snapshot_digest"],
                    now_utc=NOW,
                ))
                self.assertFalse(module.draft_matches_current_opportunity(
                    packet,current_opportunity_id=opp["id"],
                    current_revision=opp["version"]+1,
                    current_snapshot_digest=packet["input_snapshot_digest"],
                    now_utc=NOW,
                ))

if __name__=="__main__":
    unittest.main()
