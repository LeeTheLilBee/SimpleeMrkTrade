"""GRD053: urgency ack, explicit entry preference and transactional undelivered outbox."""
import tempfile
import unittest
from pathlib import Path

from grounds.access import AccessDenied
from grounds.maintenance import MaintenanceIntake
from grounds.operations import GroundsConflict, GroundsOperations
from grounds.safety import GroundsSafety
from grounds.storage import GroundsStore
from grounds.test_grounds_operations import fixture_scope


class SafetyTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        store=GroundsStore(Path(self.tmp.name)/"fictitious.sqlite3")
        store.initialize()
        self.ops=GroundsOperations(store)
        self.safety=GroundsSafety(store)
        self.owner=fixture_scope("owner","owner",("p1","p2"))
        self.manager=fixture_scope("manager","property_manager",("p1",))
        self.resident=fixture_scope("resident1","resident",("p1",),("u1",))
        self.other=fixture_scope("resident2","resident",("p1",),("u1",))
        self.outside=fixture_scope("manager2","property_manager",("p2",))
        for prop in ("p1","p2"):
            self.ops.record_closed_property(
                self.owner,property_ref=prop,name="Fiction "+prop,
                close_evidence={"status":"verified_closed","property_ref":prop,
                                "proof_ref":"close-"+prop,"owned_on":"2026-09-26"},
                close_verifier=lambda x:x, # TEST FIXTURE ONLY
            )
        self.ops.add_building(self.manager,property_ref="p1",building_ref="b1",label="A")
        self.ops.add_unit(self.manager,property_ref="p1",building_ref="b1",unit_ref="u1",label="101")
        self.ops.activate_lease(
            self.manager,property_ref="p1",unit_ref="u1",lease_ref="l1",
            resident_ref="resident1",start_on="2026-09-26",end_on="2027-09-25",
        )
        self.ops.submit_maintenance(
            self.resident,work_ref="urgent1",
            intake=MaintenanceIntake("p1","u1","plumbing","Example leak",True,"contact_first"),
        )

    def tearDown(self):
        self.tmp.cleanup()

    def test_urgent_flag_blocks_transition_until_human_acknowledges(self):
        with self.assertRaises(GroundsConflict):
            self.ops.advance_work_order(
                self.manager,work_ref="urgent1",next_state="received",expected_revision=1,
            )
        with self.assertRaises(AccessDenied):
            self.safety.acknowledge_urgency(
                self.resident,work_ref="urgent1",assessed_urgency="priority",
            )
        with self.assertRaises(AccessDenied):
            self.safety.acknowledge_urgency(
                self.outside,work_ref="urgent1",assessed_urgency="priority",
            )
        with self.assertRaises(GroundsConflict):
            self.safety.acknowledge_urgency(
                self.manager,work_ref="urgent1",assessed_urgency="routine",
            )
        reviewed=self.safety.acknowledge_urgency(
            self.manager,work_ref="urgent1",assessed_urgency="priority",
        )
        self.assertTrue(reviewed["human_review_recorded"])
        self.assertFalse(reviewed["emergency_services_contacted"])
        with self.assertRaises(GroundsConflict):
            self.safety.acknowledge_urgency(
                self.manager,work_ref="urgent1",assessed_urgency="priority",
            )
        self.assertTrue(self.safety.triage_status(
            self.resident,work_ref="urgent1",
        )["human_review_recorded"])
        transitioned=self.ops.advance_work_order(
            self.manager,work_ref="urgent1",next_state="received",expected_revision=1,
        )
        self.assertEqual(transitioned["state"],"received")

    def test_entry_preference_has_audit_but_does_not_authorize_entry(self):
        current=self.safety.entry_preference(self.resident,work_ref="urgent1")
        self.assertEqual(current["revision"],0)
        self.assertEqual(current["current_preference"],"contact_first")
        changed=self.safety.record_entry_preference(
            self.resident,work_ref="urgent1",preference="no",expected_revision=0,
        )
        self.assertEqual(changed["revision"],1)
        self.assertFalse(changed["staff_entry_authorized"])
        self.assertEqual(self.safety.entry_preference(
            self.manager,work_ref="urgent1",
        )["current_preference"],"no")
        with self.assertRaises(GroundsConflict):
            self.safety.record_entry_preference(
                self.resident,work_ref="urgent1",preference="yes",expected_revision=0,
            )
        with self.assertRaises(AccessDenied):
            self.safety.record_entry_preference(
                self.other,work_ref="urgent1",preference="yes",expected_revision=0,
            )
        with self.assertRaises(AccessDenied):
            self.safety.record_entry_preference(
                self.manager,work_ref="urgent1",preference="yes",expected_revision=1,
            )
        changed=self.safety.record_entry_preference(
            self.resident,work_ref="urgent1",preference="contact_first",expected_revision=1,
        )
        self.assertFalse(changed["legal_entry_notice_proven"])

    def test_explicit_no_entry_blocks_job_start_and_in_progress_is_not_entry_proof(self):
        self.safety.acknowledge_urgency(
            self.manager,work_ref="urgent1",assessed_urgency="priority",
        )
        revision=1
        for state in ("received","under_review","scheduled"):
            revision=self.ops.advance_work_order(
                self.manager,work_ref="urgent1",next_state=state,expected_revision=revision,
            )["revision"]
        technician=fixture_scope(
            "tech","maintenance_technician",("p1",),assignments=("urgent1",),
        )
        revision=self.ops.assign_work_order(
            self.manager,work_ref="urgent1",technician=technician,
            expected_revision=revision,
        )["revision"]
        self.safety.record_entry_preference(
            self.resident,work_ref="urgent1",preference="no",expected_revision=0,
        )
        with self.assertRaises(GroundsConflict):
            self.ops.advance_work_order(
                technician,work_ref="urgent1",next_state="in_progress",
                expected_revision=revision,
            )
        self.safety.record_entry_preference(
            self.resident,work_ref="urgent1",preference="contact_first",
            expected_revision=1,
        )
        moved=self.ops.advance_work_order(
            technician,work_ref="urgent1",next_state="in_progress",
            expected_revision=revision,
        )
        self.assertEqual(moved["state"],"in_progress")
        self.assertFalse(moved["entry_authorized"])
        self.assertFalse(moved["notification_sent"])

    def test_outbox_is_property_scoped_metadata_pending_not_messages_sent(self):
        pending=self.safety.pending_event_intents(self.manager,property_ref="p1")
        self.assertEqual(set(e["event_kind"] for e in pending),{
            "work_changed","urgent_intake_requires_human_review",
        })
        self.assertTrue(all(e["status"]=="pending" for e in pending))
        self.assertFalse(any("description" in e for e in pending))
        with self.assertRaises(AccessDenied):
            self.safety.pending_event_intents(self.outside,property_ref="p1")
        self.ops.publish_notice(
            self.manager,property_ref="p1",notice_ref="notice1",
            headline="Example",body="Fictional content",
        )
        self.assertEqual(len(self.safety.pending_event_intents(
            self.manager,property_ref="p1",
        )),3)
        before=self.safety.delivery_status(self.owner,property_ref="p1")
        self.assertEqual(before["pending_intent_count"],3)
        self.assertEqual(before["delivered_count"],0)
        self.assertFalse(before["recipient_resolution_enabled"])
        self.safety.acknowledge_urgency(
            self.manager,work_ref="urgent1",assessed_urgency="priority",
        )
        self.ops.advance_work_order(
            self.manager,work_ref="urgent1",next_state="received",expected_revision=1,
        )
        after=self.safety.delivery_status(self.owner,property_ref="p1")
        self.assertEqual(after["pending_intent_count"],4)
        self.assertFalse(after["legal_service_proven"])
        self.assertFalse(after["emergency_dispatch_confirmed"])

    def test_ended_lease_denies_new_entry_preference_and_resident_triage_view(self):
        self.ops.end_lease(
            self.manager,property_ref="p1",lease_ref="l1",expected_revision=1,
        )
        with self.assertRaises(AccessDenied):
            self.safety.record_entry_preference(
                self.resident,work_ref="urgent1",preference="no",expected_revision=0,
            )
        with self.assertRaises(AccessDenied):
            self.safety.triage_status(self.resident,work_ref="urgent1")


    def test_staff_safety_desk_exact_property_and_reviewed_queue(self):
        desk=self.safety.staff_safety_desk(self.manager,property_ref="p1")
        self.assertEqual(desk["source"],"grounds")
        self.assertEqual(desk["unreviewed_urgent_count"],1)
        self.assertEqual(desk["queue"][0]["work_ref"],"urgent1")
        self.assertEqual(desk["queue"][0]["unit_ref"],"u1")
        self.assertEqual(desk["pending_local_event_intents"],2)
        self.assertFalse(desk["provider_connected"])
        self.assertFalse(desk["recipient_delivery_proven"])
        self.assertFalse(desk["human_on_call_escalation_confirmed"])
        self.assertFalse(desk["emergency_services_contacted"])
        self.assertNotIn("description",desk["queue"][0])
        self.assertNotIn("created_by",desk["queue"][0])
        for denied,property_ref in ((self.resident,"p1"),(self.outside,"p1"),
                                    (self.other,"p1"),(self.manager,"p2")):
            with self.subTest(subject=denied.subject_ref,property_ref=property_ref):
                with self.assertRaises(AccessDenied):
                    self.safety.staff_safety_desk(denied,property_ref=property_ref)
        self.safety.acknowledge_urgency(
            self.manager,work_ref="urgent1",assessed_urgency="priority",
        )
        after=self.safety.staff_safety_desk(self.owner,property_ref="p1")
        self.assertEqual(after["unreviewed_urgent_count"],0)
        self.assertEqual(after["queue"],[])
        # Historical local intents are still pending; human review does NOT
        # magically establish delivery/dispatch.
        self.assertEqual(after["pending_local_event_intents"],2)
        self.assertFalse(after["recipient_delivery_proven"])


if __name__=="__main__":
    unittest.main()
