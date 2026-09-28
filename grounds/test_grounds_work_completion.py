"""GRD212–216: resident work-completion response boundaries."""
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from grounds.access import AccessDenied
from grounds.maintenance import MaintenanceIntake
from grounds.operations import GroundsConflict, GroundsOperations
from grounds.storage import GroundsStore
from grounds.test_grounds_operations import fixture_scope
from grounds.work_completion import GroundsWorkCompletion


class GroundsWorkCompletionTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.store=GroundsStore(Path(self.tmp.name)/"fiction.sqlite3")
        self.store.initialize()
        self.ops=GroundsOperations(self.store)
        self.completion=GroundsWorkCompletion(self.store)
        self.owner=fixture_scope("owner","owner",("p1",))
        self.manager=fixture_scope("manager","property_manager",("p1",))
        self.resident=fixture_scope("resident","resident",("p1",),("u1",))
        self.other=fixture_scope("other","resident",("p1",),("u1",))
        self.tech=fixture_scope("tech","maintenance_technician",("p1",),(),("w1",))
        self.ops.record_closed_property(
            self.owner,property_ref="p1",name="Fictional Home",
            close_evidence={"status":"verified_closed","property_ref":"p1",
                            "proof_ref":"fiction-close","owned_on":"2026-09-28"},
            close_verifier=lambda x:x,
        )
        self.ops.add_building(self.manager,property_ref="p1",building_ref="b1",label="A")
        self.ops.add_unit(self.manager,property_ref="p1",building_ref="b1",
                          unit_ref="u1",label="101")
        self.ops.activate_lease(
            self.manager,property_ref="p1",unit_ref="u1",lease_ref="l1",
            resident_ref="resident",start_on="2026-09-28",end_on="2027-09-27",
        )
        self.ops.submit_maintenance(
            self.resident,work_ref="w1",
            intake=MaintenanceIntake("p1","u1","plumbing","Synthetic completion test",
                                     False,"contact_first"),
        )
        revision=1
        for state in ("received","under_review","scheduled"):
            item=self.ops.advance_work_order(
                self.manager,work_ref="w1",next_state=state,expected_revision=revision,
            );revision=item["revision"]
        item=self.ops.assign_work_order(
            self.manager,work_ref="w1",technician=self.tech,expected_revision=revision,
        );revision=item["revision"]
        item=self.ops.advance_work_order(
            self.tech,work_ref="w1",next_state="in_progress",expected_revision=revision,
        );revision=item["revision"]
        item=self.ops.advance_work_order(
            self.tech,work_ref="w1",next_state="completed",expected_revision=revision,
        );revision=item["revision"]
        item=self.ops.advance_work_order(
            self.manager,work_ref="w1",next_state="confirmation",expected_revision=revision,
        )
        self.confirmation_revision=item["revision"]

    def tearDown(self):
        self.tmp.cleanup()

    def test_resident_can_confirm_resolved_without_creating_waiver(self):
        result=self.completion.respond(
            self.resident,work_ref="w1",outcome="resolved",
            expected_revision=self.confirmation_revision,event_ref="completion-1",
            note="Looks fixed now.",
        )
        self.assertEqual(result["state"],"closed")
        self.assertFalse(result["legal_waiver_created"])
        self.assertFalse(result["inspection_certified"])
        self.assertFalse(result["provider_delivery_proven"])
        status=self.completion.status(self.resident,work_ref="w1")
        self.assertEqual(status["latest_resident_response"]["outcome"],"resolved")
        self.assertEqual(status["latest_resident_response"]["note"],"Looks fixed now.")
        with self.store.transaction() as db:
            self.assertEqual(db.execute(
                "SELECT COUNT(*) FROM work_completion_events WHERE work_ref='w1'"
            ).fetchone()[0],1)
            self.assertEqual(db.execute(
                "SELECT state FROM work_orders WHERE work_ref='w1'"
            ).fetchone()[0],"closed")

    def test_resident_can_reopen_from_confirmation_and_manager_reviews_again(self):
        result=self.completion.respond(
            self.resident,work_ref="w1",outcome="still_needs_attention",
            expected_revision=self.confirmation_revision,event_ref="completion-2",
            note="The leak started again.",
        )
        self.assertEqual(result["state"],"reopened")
        moved=self.ops.advance_work_order(
            self.manager,work_ref="w1",next_state="under_review",
            expected_revision=result["revision"],
        )
        self.assertEqual(moved["state"],"under_review")

    def test_exact_retry_is_idempotent_but_changed_retry_and_stale_state_fail(self):
        first=self.completion.respond(
            self.resident,work_ref="w1",outcome="resolved",
            expected_revision=self.confirmation_revision,event_ref="completion-3",
        )
        repeat=self.completion.respond(
            self.resident,work_ref="w1",outcome="resolved",
            expected_revision=self.confirmation_revision,event_ref="completion-3",
        )
        self.assertTrue(repeat["replayed"])
        self.assertEqual(first["revision"],repeat["revision"])
        with self.assertRaises(GroundsConflict):
            self.completion.respond(
                self.resident,work_ref="w1",outcome="resolved",
                expected_revision=self.confirmation_revision,event_ref="completion-3",
                note="changed",
            )
        with self.assertRaises(GroundsConflict):
            self.completion.respond(
                self.resident,work_ref="w1",outcome="resolved",
                expected_revision=first["revision"],event_ref="completion-4",
            )

    def test_only_current_original_resident_can_answer_and_note_is_bounded(self):
        with self.assertRaises(AccessDenied):
            self.completion.respond(
                self.other,work_ref="w1",outcome="resolved",
                expected_revision=self.confirmation_revision,event_ref="other-1",
            )
        with self.assertRaises(AccessDenied):
            self.completion.respond(
                self.manager,work_ref="w1",outcome="resolved",
                expected_revision=self.confirmation_revision,event_ref="manager-1",
            )
        with self.assertRaises(GroundsConflict):
            self.completion.respond(
                self.resident,work_ref="w1",outcome="resolved",
                expected_revision=self.confirmation_revision,event_ref="long-note",
                note="x"*801,
            )


if __name__=="__main__":
    unittest.main()
