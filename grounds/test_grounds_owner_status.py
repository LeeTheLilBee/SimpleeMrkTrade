"""GRD068: source-only, sanitized owner/Clouds readiness and count tests."""
import tempfile
import unittest
from pathlib import Path

from grounds.access import AccessDenied
from grounds.maintenance import MaintenanceIntake
from grounds.operations import GroundsOperations
from grounds.owner_status import owner_operating_snapshot
from grounds.safety import GroundsSafety
from grounds.stewardship import GroundsStewardship
from grounds.storage import GroundsStore
from grounds.test_grounds_operations import fixture_scope


class OwnerAggregateTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        store=GroundsStore(Path(self.tmp.name)/"fixture.sqlite3")
        store.initialize()
        self.ops=GroundsOperations(store)
        self.st=GroundsStewardship(store)
        self.safety=GroundsSafety(store)
        self.owner=fixture_scope("owner","owner",("p1","p2"))
        self.manager=fixture_scope("manager","property_manager",("p1",))
        self.regional=fixture_scope("regional","regional_manager",("p1",))
        self.resident=fixture_scope("resident-secret","resident",("p1",),("u1",))
        self.outside=fixture_scope("outside","owner",("p2",))
        for ref in ("p1","p2"):
            self.ops.record_closed_property(
                self.owner,property_ref=ref,name="Fictional "+ref,
                close_evidence={"status":"verified_closed","property_ref":ref,
                                "proof_ref":"close-"+ref,"owned_on":"2026-09-26"},
                close_verifier=lambda doc:doc, # TEST ONLY
            )
        self.ops.add_building(self.manager,property_ref="p1",building_ref="b1",label="A")
        self.ops.add_unit(self.manager,property_ref="p1",building_ref="b1",unit_ref="u1",label="101")
        self.ops.activate_lease(
            self.manager,property_ref="p1",unit_ref="u1",lease_ref="lease-secret",
            resident_ref="resident-secret",start_on="2026-09-26",end_on="2027-09-25",
        )
        self.ops.submit_maintenance(
            self.resident,work_ref="work-secret",
            intake=MaintenanceIntake(
                "p1","u1","plumbing","Private complaint description",True,"contact_first",
            ),
        )

    def tearDown(self):
        self.tmp.cleanup()

    def test_owner_counts_only_and_no_payment_or_private_document(self):
        pulse=owner_operating_snapshot(self.owner,self.ops,property_ref="p1")
        self.assertEqual(pulse["source"],"grounds")
        self.assertEqual(pulse["intended_audience"],"clouds")
        self.assertEqual((pulse["counts"]["units"],pulse["counts"]["occupied_units"]),(1,1))
        self.assertEqual(pulse["counts"]["untriaged_urgent_work"],1)
        self.assertIsNone(pulse["rent_collections"])
        self.assertIsNone(pulse["available_capital"])
        self.assertFalse(pulse["publisher_enabled"])
        self.assertFalse(pulse["identity_receiver_certified"])
        for secret in ("resident-secret","lease-secret","work-secret","Private complaint description"):
            self.assertNotIn(secret,str(pulse))
        with self.assertRaises(AccessDenied):
            owner_operating_snapshot(self.resident,self.ops,property_ref="p1")
        with self.assertRaises(AccessDenied):
            owner_operating_snapshot(self.regional,self.ops,property_ref="p1")
        with self.assertRaises(AccessDenied):
            owner_operating_snapshot(self.outside,self.ops,property_ref="p1")

    def test_human_triage_and_urgent_findings_change_source_counts(self):
        self.safety.acknowledge_urgency(
            self.manager,work_ref="work-secret",assessed_urgency="priority",
        )
        self.st.plan_inspection(
            self.manager,property_ref="p1",unit_ref="u1",inspection_ref="inspection1",
            category="routine",planned_on="2026-10-01",
        )
        self.st.advance_inspection(
            self.manager,property_ref="p1",inspection_ref="inspection1",
            next_state="in_progress",expected_revision=1,
        )
        self.st.record_finding(
            self.manager,property_ref="p1",inspection_ref="inspection1",
            finding_ref="finding-secret",severity="major",
            narrative="Synthetic issue",
        )
        pulse=owner_operating_snapshot(self.owner,self.ops,property_ref="p1")
        self.assertEqual(pulse["counts"]["untriaged_urgent_work"],0)
        self.assertEqual(pulse["counts"]["unresolved_serious_inspection_findings"],1)
        self.assertNotIn("finding-secret",str(pulse))

    def test_turnover_count_tracks_source_and_does_not_publish(self):
        self.ops.end_lease(
            self.manager,property_ref="p1",lease_ref="lease-secret",expected_revision=1,
        )
        self.st.begin_turnover(
            self.manager,property_ref="p1",unit_ref="u1",
            lease_ref="lease-secret",turnover_ref="turn-secret",
        )
        pulse=owner_operating_snapshot(self.owner,self.ops,property_ref="p1")
        self.assertEqual(pulse["counts"]["occupied_units"],0)
        self.assertEqual(pulse["counts"]["open_turnovers"],1)
        self.assertFalse(pulse["publisher_enabled"])


if __name__=="__main__":
    unittest.main()
