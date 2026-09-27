"""GRD059: fictional, scoped nonfinancial maintenance resource audit tests."""
import tempfile
import unittest
from pathlib import Path

from grounds.access import AccessDenied
from grounds.maintenance import MaintenanceIntake
from grounds.operations import GroundsOperations, GroundsConflict
from grounds.storage import GroundsStore
from grounds.test_grounds_operations import fixture_scope
from grounds.work_resources import GroundsWorkResources


class GroundsResourceTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.store=GroundsStore(Path(self.tmp.name)/"resource-fixture.sqlite3")
        self.store.initialize()
        self.ops=GroundsOperations(self.store)
        self.resources=GroundsWorkResources(self.store)
        self.owner=fixture_scope("owner","owner",("p1","p2"))
        self.manager=fixture_scope("manager","property_manager",("p1",))
        self.resident=fixture_scope("resident","resident",("p1",),("u1",))
        self.tech=fixture_scope("tech","maintenance_technician",("p1",),assignments=("w1",))
        self.unassigned=fixture_scope("tech-other","maintenance_technician",("p1",),assignments=("other-job",))
        self.cross=fixture_scope("cross-manager","property_manager",("p2",))
        self.vendor=fixture_scope("vendor","vendor",("p1",),assignments=("w1",))
        for prop in ("p1","p2"):
            self.ops.record_closed_property(
                self.owner,property_ref=prop,name="Sample "+prop,
                close_evidence={"status":"verified_closed","property_ref":prop,
                                "proof_ref":"closed-"+prop,"owned_on":"2026-09-26"},
                close_verifier=lambda proof:proof, # TEST FIXTURE ONLY
            )
        self.ops.add_building(self.manager,property_ref="p1",building_ref="b1",label="A")
        self.ops.add_unit(self.manager,property_ref="p1",building_ref="b1",unit_ref="u1",label="101")
        self.ops.activate_lease(
            self.manager,property_ref="p1",unit_ref="u1",lease_ref="l1",
            resident_ref="resident",start_on="2026-09-26",end_on="2027-09-25",
        )
        self.ops.submit_maintenance(
            self.resident,work_ref="w1",
            intake=MaintenanceIntake("p1","u1","plumbing","Sample repair",False,"contact_first"),
        )
    def tearDown(self):
        self.tmp.cleanup()

    def _in_progress(self):
        rev=1
        for state in ("received","under_review","scheduled"):
            rev=self.ops.advance_work_order(
                self.manager,work_ref="w1",next_state=state,expected_revision=rev,
            )["revision"]
        rev=self.ops.assign_work_order(
            self.manager,work_ref="w1",technician=self.tech,expected_revision=rev,
        )["revision"]
        rev=self.ops.advance_work_order(
            self.tech,work_ref="w1",next_state="in_progress",expected_revision=rev,
        )["revision"]
        return rev

    def test_assignment_state_and_resident_privacy(self):
        with self.assertRaises(GroundsConflict):
            self.resources.record(self.manager,work_ref="w1",resource_type="material",
                                  label="Pipe",quantity=2)
        self._in_progress()
        with self.assertRaises(AccessDenied):
            self.resources.history(self.resident,work_ref="w1")
        with self.assertRaises(AccessDenied):
            self.resources.record(self.vendor,work_ref="w1",resource_type="material",
                                  label="Pipe",quantity=2)
        with self.assertRaises(AccessDenied):
            self.resources.record(self.unassigned,work_ref="w1",resource_type="material",
                                  label="Pipe",quantity=2)
        with self.assertRaises(AccessDenied):
            self.resources.summary(self.cross,work_ref="w1")
        with self.assertRaises(AccessDenied):
            self.resources.history(self.cross,work_ref="w1")

    def test_material_and_labor_reversal_is_immutable_not_teller_money(self):
        self._in_progress()
        material=self.resources.record(
            self.tech,work_ref="w1",resource_type="material",
            label="Example washer",quantity=3,event_ref="mat1",
        )
        self.assertIsNone(material["financial_amount"])
        self.assertFalse(material["inventory_reservation_created"])
        self.resources.record(
            self.tech,work_ref="w1",resource_type="labor",
            label="Inspection and replacement",quantity=90,event_ref="labor1",
        )
        summary=self.resources.summary(self.manager,work_ref="w1")
        self.assertEqual((summary["net_material_items"],summary["net_labor_minutes"]),(3,90))
        self.assertIsNone(summary["labor_cost"])
        self.assertFalse(summary["teller_connected"])
        with self.assertRaises(AccessDenied):
            self.resources.reverse(self.tech,work_ref="w1",original_event_ref="mat1")
        result=self.resources.reverse(self.manager,work_ref="w1",original_event_ref="mat1",
                                      reversal_ref="mat1-reversal")
        self.assertFalse(result["financial_adjustment_executed"])
        summary=self.resources.summary(self.manager,work_ref="w1")
        self.assertEqual((summary["net_material_items"],summary["net_labor_minutes"]),(0,90))
        self.assertEqual(summary["resource_event_count"],3)
        history=self.resources.history(self.manager,work_ref="w1")
        self.assertIn("record",set(x["action"] for x in history))
        self.assertIn("reverse",set(x["action"] for x in history))
        with self.assertRaises(GroundsConflict):
            self.resources.reverse(self.manager,work_ref="w1",original_event_ref="mat1",
                                   reversal_ref="another-reversal")
        with self.assertRaises(GroundsConflict):
            self.resources.reverse(self.manager,work_ref="w1",
                                   original_event_ref="mat1-reversal")
        with self.assertRaises(GroundsConflict):
            self.resources.record(self.tech,work_ref="w1",resource_type="labor",
                                  label="Duplicate",quantity=10,event_ref="labor1")

    def test_invalid_quantities_and_unrecognized_categories(self):
        self._in_progress()
        for amount in (0,-1,True,1.5,1000001,"5"):
            with self.assertRaises(GroundsConflict):
                self.resources.record(self.manager,work_ref="w1",resource_type="material",
                                      label="Material",quantity=amount)
        with self.assertRaises(GroundsConflict):
            self.resources.record(self.manager,work_ref="w1",resource_type="cost",
                                  label="Money is Teller owned",quantity=1)
        with self.assertRaises(GroundsConflict):
            self.resources.record(self.manager,work_ref="w1",resource_type="labor",
                                  label=" ",quantity=5)

    def test_technician_cannot_log_after_completion_or_reverse_after_close(self):
        revision=self._in_progress()
        self.resources.record(self.tech,work_ref="w1",resource_type="material",
                              label="Part",quantity=1,event_ref="part")
        revision=self.ops.advance_work_order(
            self.tech,work_ref="w1",next_state="completed",expected_revision=revision,
        )["revision"]
        with self.assertRaises(GroundsConflict):
            self.resources.record(self.tech,work_ref="w1",resource_type="material",
                                  label="Late part",quantity=1)
        revision=self.ops.advance_work_order(
            self.manager,work_ref="w1",next_state="confirmation",expected_revision=revision,
        )["revision"]
        revision=self.ops.advance_work_order(
            self.manager,work_ref="w1",next_state="closed",expected_revision=revision,
        )["revision"]
        with self.assertRaises(GroundsConflict):
            self.resources.reverse(self.manager,work_ref="w1",original_event_ref="part")
        with self.assertRaises(GroundsConflict):
            self.resources.record(self.manager,work_ref="w1",resource_type="labor",
                                  label="Late labor",quantity=5)


if __name__=="__main__":
    unittest.main()
