"""GRD184–186: fiction-only lease/role, revocation and checklist self-report."""
import tempfile
import unittest
from pathlib import Path
from grounds.access import AccessDenied
from grounds.move_concierge import GroundsMoveConcierge
from grounds.operations import GroundsConflict,GroundsOperations
from grounds.storage import GroundsStore
from grounds.test_grounds_operations import fixture_scope


class MoveConciergeTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.store=GroundsStore(Path(self.tmp.name)/"fiction.sqlite3")
        self.store.initialize()
        self.ops=GroundsOperations(self.store)
        self.move=GroundsMoveConcierge(self.store)
        self.owner=fixture_scope("owner","owner",("p1","p2"))
        self.manager=fixture_scope("manager","property_manager",("p1",))
        self.supervisor=fixture_scope("super","maintenance_supervisor",("p1",))
        self.resident=fixture_scope("r1","resident",("p1",),("u1",))
        self.other=fixture_scope("r2","resident",("p1",),("u1",))
        self.outside=fixture_scope("outsider","property_manager",("p2",))
        self.ops.record_closed_property(
            self.owner,property_ref="p1",name="Synthetic home",
            close_evidence={"status":"verified_closed","property_ref":"p1",
                            "proof_ref":"close-p1","owned_on":"2026-09-26"},
            close_verifier=lambda x:x,
        )
        self.ops.add_building(self.manager,property_ref="p1",building_ref="b1",label="A")
        self.ops.add_unit(self.manager,property_ref="p1",building_ref="b1",unit_ref="u1",label="101")
        self.ops.activate_lease(self.manager,property_ref="p1",unit_ref="u1",lease_ref="l1",
                                resident_ref="r1",start_on="2026-09-26",end_on="2027-09-25")

    def tearDown(self):
        self.tmp.cleanup()

    def test_current_lease_self_report_and_exact_retry_no_false_key_custody(self):
        view=self.move.resident_checklist(self.resident,property_ref="p1",unit_ref="u1")
        self.assertEqual(view["lease_ref"],"l1")
        self.assertEqual([p["phase"] for p in view["phases"]],["move_in","move_out"])
        self.assertEqual(view["phases"][0]["tasks"][0]["revision"],0)
        self.assertFalse(view["keys_received_confirmed"])
        kwargs=dict(property_ref="p1",unit_ref="u1",phase="move_in",task_ref="welcome_reviewed",
                    status="self_reported_done",expected_revision=0,event_ref="event1")
        first=self.move.mark_task(self.resident,**kwargs)
        self.assertEqual(first["revision"],1)
        self.assertTrue(first["self_reported_only"])
        self.assertFalse(first["staff_or_legal_verification"])
        self.assertTrue(self.move.mark_task(self.resident,**kwargs)["replayed"])
        with self.assertRaises(GroundsConflict):
            self.move.mark_task(self.resident,**{**kwargs,"status":"planned"})
        with self.assertRaises(GroundsConflict):
            self.move.mark_task(self.resident,**{**kwargs,"event_ref":"new"})
        view=self.move.resident_checklist(self.resident,property_ref="p1",unit_ref="u1")
        task=view["phases"][0]["tasks"][0]
        self.assertEqual(task["status"],"self_reported_done")
        self.assertEqual(task["revision"],1)
        self.assertFalse(task["staff_or_legal_verification"])
        self.assertFalse(view["deposit_return_approved"])

    def test_another_resident_and_ended_lease_have_no_checklist(self):
        with self.assertRaises(AccessDenied):
            self.move.resident_checklist(self.other,property_ref="p1",unit_ref="u1")
        with self.assertRaises(AccessDenied):
            self.move.mark_task(self.other,property_ref="p1",unit_ref="u1",
                phase="move_in",task_ref="welcome_reviewed",status="planned",
                expected_revision=0,event_ref="wrong")
        with self.assertRaises(AccessDenied):
            self.move.resident_checklist(self.manager,property_ref="p1",unit_ref="u1")
        self.ops.end_lease(self.manager,property_ref="p1",lease_ref="l1",expected_revision=1)
        with self.assertRaises(AccessDenied):
            self.move.resident_checklist(self.resident,property_ref="p1",unit_ref="u1")
        with self.assertRaises(AccessDenied):
            self.move.mark_task(self.resident,property_ref="p1",unit_ref="u1",
                phase="move_in",task_ref="welcome_reviewed",status="planned",
                expected_revision=0,event_ref="ended")

    def test_manager_desk_is_aggregate_and_never_terminates_or_returns_deposit(self):
        view=self.move.staff_move_desk(self.manager,property_ref="p1")
        self.assertEqual(view["source"],"grounds")
        self.assertFalse(view["resident_identity_included"])
        self.assertFalse(view["deposit_decision_authorized"])
        self.assertFalse(view["keys_return_verified"])
        self.assertNotIn("r1",str(view))
        self.assertEqual(self.move.staff_move_desk(self.owner,property_ref="p1")["room"],"move_desk")
        for actor in (self.resident,self.supervisor,self.outside):
            with self.assertRaises(AccessDenied):
                self.move.staff_move_desk(actor,property_ref="p1")


if __name__=="__main__":
    unittest.main()
