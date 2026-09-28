"""GRD175: fictional maintenance thread permission, replay and timeline regressions."""
import tempfile
import unittest
from pathlib import Path

from grounds.access import AccessDenied
from grounds.maintenance import MaintenanceIntake
from grounds.operations import GroundsConflict,GroundsOperations
from grounds.storage import GroundsStore
from grounds.test_grounds_operations import fixture_scope
from grounds.work_thread import GroundsWorkThread


class WorkThreadTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.store=GroundsStore(Path(self.temp.name)/"test.sqlite3")
        self.store.initialize()
        self.ops=GroundsOperations(self.store)
        self.thread=GroundsWorkThread(self.store)
        self.owner=fixture_scope("owner","owner",("p1","p2"))
        self.manager=fixture_scope("manager","property_manager",("p1",))
        self.supervisor=fixture_scope("super","maintenance_supervisor",("p1",))
        self.resident=fixture_scope("r1","resident",("p1",),("u1",))
        self.other=fixture_scope("r2","resident",("p1",),("u1",))
        self.tech=fixture_scope("tech","maintenance_technician",("p1",),assignments=("w1",))
        self.outside=fixture_scope("outside","property_manager",("p2",))
        self.ops.record_closed_property(
            self.owner,property_ref="p1",name="Fictional home",
            close_evidence={"status":"verified_closed","property_ref":"p1",
                            "proof_ref":"closed-p1","owned_on":"2026-09-26"},
            close_verifier=lambda x:x,
        )
        self.ops.add_building(self.manager,property_ref="p1",building_ref="b1",label="A")
        self.ops.add_unit(self.manager,property_ref="p1",building_ref="b1",unit_ref="u1",label="101")
        self.ops.activate_lease(self.manager,property_ref="p1",unit_ref="u1",
                                lease_ref="l1",resident_ref="r1",
                                start_on="2026-09-26",end_on="2027-09-25")
        self.ops.submit_maintenance(self.resident,work_ref="w1",intake=MaintenanceIntake(
            "p1","u1","plumbing","Synthetic blocked fixture",False,"contact_first",
        ))

    def tearDown(self):
        self.temp.cleanup()

    def test_resident_shared_staff_internal_redaction_and_replay(self):
        saved=self.thread.post(self.resident,work_ref="w1",message_ref="m1",
                               body="Could someone share the current update?")
        self.assertFalse(saved["external_notification_delivered"])
        self.assertFalse(saved["replayed"])
        repeated=self.thread.post(self.resident,work_ref="w1",message_ref="m1",
                                  body="Could someone share the current update?")
        self.assertTrue(repeated["replayed"])
        with self.assertRaises(GroundsConflict):
            self.thread.post(self.resident,work_ref="w1",message_ref="m1",body="Changed content")
        self.thread.post(self.manager,work_ref="w1",message_ref="internal",
                         body="Internal operational only",audience="staff_internal")
        visible=self.thread.thread(self.resident,work_ref="w1")
        self.assertEqual(visible["visible_message_count"],1)
        self.assertNotIn("Internal operational only",str(visible))
        self.assertNotIn("author_ref",str(visible))
        self.assertFalse(visible["provider_currently_connected"])
        staff=self.thread.thread(self.manager,work_ref="w1")
        self.assertEqual(staff["visible_message_count"],2)
        self.assertIn("Internal operational only",str(staff))
        self.assertTrue(staff["can_post_staff_internal"])
        with self.assertRaises(AccessDenied):
            self.thread.post(self.resident,work_ref="w1",message_ref="bad",
                             body="private",audience="staff_internal")
        with self.assertRaises(AccessDenied):
            self.thread.thread(self.other,work_ref="w1")
        with self.assertRaises(AccessDenied):
            self.thread.thread(self.outside,work_ref="w1")

    def test_assignment_is_not_self_granted_and_closed_or_ended_lease_denied(self):
        with self.assertRaises(AccessDenied):
            self.thread.thread(self.tech,work_ref="w1")
        with self.assertRaises(AccessDenied):
            self.thread.post(self.tech,work_ref="w1",message_ref="t1",body="Unassigned")
        self.ops.end_lease(self.manager,property_ref="p1",lease_ref="l1",expected_revision=1)
        with self.assertRaises(AccessDenied):
            self.thread.thread(self.resident,work_ref="w1")
        with self.assertRaises(AccessDenied):
            self.thread.post(self.resident,work_ref="w1",message_ref="new",
                             body="Old lease cannot post")
        with self.assertRaises(GroundsConflict):
            self.thread.post(self.manager,work_ref="w1",message_ref="badtext",body="  ")

    def test_no_external_delivery_or_injected_markup(self):
        self.thread.post(self.resident,work_ref="w1",message_ref="m2",
                         body="<script>this is shown only as plain text</script>")
        data=self.thread.thread(self.resident,work_ref="w1")
        self.assertTrue(data["in_app_post_is_not_external_delivery"])
        self.assertFalse(data["emergency_services_contacted"])
        self.assertFalse(data["entry_authorized"])
        self.assertEqual(data["visible_message_count"],1)
        self.assertEqual(data["timeline"][-1]["kind"],"message")
        self.assertEqual(data["messages"][0]["audience"],"shared")


if __name__=="__main__":
    unittest.main()
