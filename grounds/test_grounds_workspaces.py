"""GRD075: role-specific workspace read models are scoped and never grant access."""
import tempfile
import unittest
from pathlib import Path

from grounds.access import AccessDenied
from grounds.contract import ROOMS
from grounds.maintenance import MaintenanceIntake
from grounds.operations import GroundsOperations
from grounds.storage import GroundsStore
from grounds.test_grounds_operations import fixture_scope
from grounds.workspaces import build_workspace


class WorkspacesTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        store=GroundsStore(Path(self.tmp.name)/"fake.sqlite3")
        store.initialize()
        self.ops=GroundsOperations(store)
        self.owner=fixture_scope("owner","owner",("p1","p2"))
        self.manager=fixture_scope("manager","property_manager",("p1",))
        self.resident=fixture_scope("resident1","resident",("p1",),("u1",))
        self.other=fixture_scope("resident2","resident",("p1",),("u1",))
        self.tech=fixture_scope("tech1","maintenance_technician",("p1",),assignments=("w1",))
        self.unassigned=fixture_scope("tech2","maintenance_technician",("p1",))
        for p in ("p1","p2"):
            self.ops.record_closed_property(
                self.owner,property_ref=p,name="Fictional "+p,
                close_evidence={"status":"verified_closed","property_ref":p,
                                "proof_ref":"closed-"+p,"owned_on":"2026-09-26"},
                close_verifier=lambda x:x, # TEST FICTION ONLY
            )
        self.ops.add_building(self.manager,property_ref="p1",building_ref="b1",label="A")
        self.ops.add_unit(self.manager,property_ref="p1",building_ref="b1",unit_ref="u1",label="101")
        self.ops.activate_lease(
            self.manager,property_ref="p1",unit_ref="u1",lease_ref="l1",
            resident_ref="resident1",start_on="2026-09-26",end_on="2027-09-25",
        )
        self.ops.publish_notice(
            self.manager,property_ref="p1",notice_ref="n1",
            headline="Example announcement",body="No resident information",
        )
        self.ops.submit_maintenance(
            self.resident,work_ref="w1",
            intake=MaintenanceIntake("p1","u1","plumbing","Private description",False,"contact_first"),
        )

    def tearDown(self):
        self.tmp.cleanup()

    def test_resident_own_home_and_other_denied(self):
        view=build_workspace(
            self.resident,self.ops,property_ref="p1",unit_ref="u1",
        )
        self.assertEqual(view["room"],"resident_home")
        self.assertEqual(view["lease"]["lease_ref"],"l1")
        self.assertEqual([w["work_ref"] for w in view["work_orders"]],["w1"])
        self.assertEqual(view["notices"][0]["read_in_app"],0)
        self.assertIsNone(view["rent"]["amount_due_cents"])
        self.assertIsNone(view["rent"]["checkout_url"])
        self.assertFalse(view["payment_execution_enabled"])
        self.assertFalse(view["authenticated_by_tower_receiver"])
        self.assertNotIn("resident_ref",str(view))
        with self.assertRaises(AccessDenied):
            build_workspace(self.other,self.ops,property_ref="p1",unit_ref="u1")
        with self.assertRaises(AccessDenied):
            build_workspace(self.resident,self.ops,property_ref="p1",unit_ref="u2")
        with self.assertRaises(AccessDenied):
            build_workspace(self.resident,self.ops,property_ref="p1")

    def test_staff_only_real_assignment_and_minimal_queue(self):
        pre=build_workspace(self.unassigned,self.ops,property_ref="p1")
        self.assertEqual(pre["work_orders"],[])
        rev=1
        for state in ("received","under_review","scheduled"):
            rev=self.ops.advance_work_order(
                self.manager,work_ref="w1",next_state=state,expected_revision=rev,
            )["revision"]
        self.ops.assign_work_order(
            self.manager,work_ref="w1",technician=self.tech,expected_revision=rev,
        )
        tech=build_workspace(self.tech,self.ops,property_ref="p1")
        self.assertEqual([x["work_ref"] for x in tech["work_orders"]],["w1"])
        self.assertNotIn("Private description",str(tech))
        self.assertNotIn("resident1",str(tech))
        self.assertIsNotNone(tech["soulaana"])
        manager=build_workspace(self.manager,self.ops,property_ref="p1")
        self.assertEqual(manager["room"],"property_service_desk")
        self.assertEqual(manager["property_pulse"]["open_work_orders"],1)

    def test_leasing_regional_owner_use_scoped_source_without_money_fiction(self):
        agent=fixture_scope("agent","leasing_agent",("p1",))
        availability=build_workspace(agent,self.ops,property_ref="p1")
        self.assertEqual(availability["units"][0]["lifecycle"],"occupied")
        self.assertNotIn("resident1",str(availability))
        self.assertIsNone(availability["actual_advertised_rent"])
        regional=fixture_scope("regional","regional_manager",("p1",))
        regview=build_workspace(regional,self.ops,property_ref="p1")
        self.assertEqual(regview["room"],"regional_property_summary")
        self.assertNotIn("resident1",str(regview))
        owner=build_workspace(self.owner,self.ops,property_ref="p1")
        self.assertIsNone(owner["operating_snapshot"]["rent_collections"])
        self.assertFalse(owner["operating_snapshot"]["publisher_enabled"])
        self.assertIn("Soulaana" if "Soulaana" in str(owner) else "source",str(owner))
        outsider=fixture_scope("outsider","owner",("p2",))
        with self.assertRaises(AccessDenied):
            build_workspace(outsider,self.ops,property_ref="p1")

    def test_remaining_roles_are_locked_not_fake_authorized_workspaces(self):
        implemented={
            "resident","maintenance_technician","maintenance_supervisor",
            "property_manager","leasing_agent","regional_manager","owner",
        }
        self.assertEqual(len(ROOMS),13)
        for role in set(ROOMS)-implemented:
            actor=fixture_scope("sample-"+role,role,("p1",))
            view=build_workspace(actor,self.ops,property_ref="p1")
            self.assertEqual(view["room"],"assignment_certification_required")
            self.assertTrue(view["locked"])
            self.assertIsNone(view["record_count"])
            self.assertNotIn("Private description",str(view))
            self.assertFalse(view["authenticated_by_tower_receiver"])


if __name__=="__main__":
    unittest.main()
