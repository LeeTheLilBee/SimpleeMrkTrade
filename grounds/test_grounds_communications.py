"""GRD044 — local notice and appointment privacy/temporal regressions."""
import tempfile
import unittest
from datetime import datetime,timezone,timedelta
from pathlib import Path

from grounds.access import AccessDenied
from grounds.communications import GroundsCommunications
from grounds.maintenance import MaintenanceIntake
from grounds.operations import GroundsConflict, GroundsOperations
from grounds.residency import GroundsResidency
from grounds.storage import GroundsStore
from grounds.test_grounds_operations import fixture_scope
from grounds.test_grounds_residency import grant


def times(days=5,hours=2):
    start=datetime.now(timezone.utc)+timedelta(days=days)
    end=start+timedelta(hours=hours)
    return start.isoformat(),end.isoformat()


class CommunicationsTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        store=GroundsStore(Path(self.tmp.name)/"local.sqlite3")
        store.initialize()
        self.ops=GroundsOperations(store)
        self.comms=GroundsCommunications(store)
        self.res=GroundsResidency(store)
        self.owner=fixture_scope("owner","owner",("p1","p2"))
        self.manager=fixture_scope("manager","property_manager",("p1",))
        self.primary=fixture_scope("resident1","resident",("p1",),("u1",))
        self.co=fixture_scope("resident2","resident",("p1",),("u1",))
        self.other=fixture_scope("resident3","resident",("p1",),("u1",))
        self.outside=fixture_scope("manager2","property_manager",("p2",))
        for prop in ("p1","p2"):
            self.ops.record_closed_property(
                self.owner,property_ref=prop,name="Fiction "+prop,
                close_evidence={"status":"verified_closed","property_ref":prop,
                                "proof_ref":"close-"+prop,"owned_on":"2026-09-26"},
                close_verifier=lambda doc:doc,
            )
        self.ops.add_building(self.manager,property_ref="p1",building_ref="b1",label="A")
        self.ops.add_unit(self.manager,property_ref="p1",building_ref="b1",unit_ref="u1",label="101")
        self.ops.activate_lease(
            self.manager,property_ref="p1",unit_ref="u1",lease_ref="l1",
            resident_ref="resident1",start_on="2026-09-26",end_on="2027-09-25",
        )
        self.res.grant_member(
            self.manager,property_ref="p1",unit_ref="u1",lease_ref="l1",
            subject_ref="resident2",relationship="co_tenant",
            signed_grant=grant("lease_member_grant",subject="resident2",
                               proof="membership2"),
            proof_verifier=lambda doc:doc,
        )
        self.ops.submit_maintenance(
            self.primary,work_ref="w1",
            intake=MaintenanceIntake("p1","u1","plumbing","Sample leak in kitchen",
                                     False,"contact_first"),
        )

    def tearDown(self):
        self.tmp.cleanup()

    def test_notices_are_per_member_local_read_not_delivery(self):
        self.ops.publish_notice(self.manager,property_ref="p1",notice_ref="n1",
                                headline="Water notice",body="Example only")
        home=self.ops.resident_home(self.primary,property_ref="p1",unit_ref="u1")
        self.assertEqual(home["notices"][0]["read_in_app"],0)
        receipt=self.comms.mark_notice_read(
            self.primary,property_ref="p1",unit_ref="u1",notice_ref="n1",
        )
        self.assertFalse(receipt["delivery_confirmed"])
        self.assertFalse(receipt["legal_service_proven"])
        self.assertEqual(self.ops.resident_home(
            self.primary,property_ref="p1",unit_ref="u1",
        )["notices"][0]["read_in_app"],1)
        self.assertEqual(self.ops.resident_home(
            self.co,property_ref="p1",unit_ref="u1",
        )["notices"][0]["read_in_app"],0)
        with self.assertRaises(AccessDenied):
            self.comms.mark_notice_read(
                self.other,property_ref="p1",unit_ref="u1",notice_ref="n1",
            )
        with self.assertRaises(AccessDenied):
            self.comms.mark_notice_read(
                self.primary,property_ref="p1",unit_ref="u1",notice_ref="nonexistent",
            )

    def test_unit_notice_needs_current_lease_and_read_is_per_lease(self):
        self.ops.publish_notice(
            self.manager,property_ref="p1",notice_ref="public1",
            headline="General notice",body="Property wide example",
        )
        self.ops.publish_notice(
            self.manager,property_ref="p1",unit_ref="u1",notice_ref="unit-l1",
            headline="Previous lease confidential notice",body="Old lease only",
        )
        for ref in ("public1","unit-l1"):
            self.comms.mark_notice_read(
                self.primary,property_ref="p1",unit_ref="u1",notice_ref=ref,
            )
        self.assertEqual(
            {x["notice_ref"]:x["read_in_app"] for x in self.ops.resident_home(
                self.primary,property_ref="p1",unit_ref="u1",
            )["notices"]},
            {"public1":1,"unit-l1":1},
        )
        self.ops.end_lease(
            self.manager,property_ref="p1",lease_ref="l1",expected_revision=1,
        )
        with self.assertRaises(GroundsConflict):
            self.ops.publish_notice(
                self.manager,property_ref="p1",unit_ref="u1",notice_ref="vacant",
                headline="Vacant",body="Cannot address a nonexistent current lease",
            )
        # Fixture-only representation of independently verified turnover.
        # No production caller is permitted to change readiness with raw SQL.
        with self.ops.store.transaction(write=True) as db:
            db.execute(
                "UPDATE units SET lifecycle='ready' WHERE property_ref='p1' AND unit_ref='u1'",
            )
        self.ops.activate_lease(
            self.manager,property_ref="p1",unit_ref="u1",lease_ref="l2",
            resident_ref="resident1",start_on="2028-01-01",end_on="2028-12-31",
        )
        home=self.ops.resident_home(self.primary,property_ref="p1",unit_ref="u1")
        self.assertEqual(
            [x["notice_ref"] for x in home["notices"]],["public1"],
        )
        self.assertEqual(home["notices"][0]["read_in_app"],0)
        with self.assertRaises(AccessDenied):
            self.comms.mark_notice_read(
                self.primary,property_ref="p1",unit_ref="u1",notice_ref="unit-l1",
            )
        self.comms.mark_notice_read(
            self.primary,property_ref="p1",unit_ref="u1",notice_ref="public1",
        )
        with self.ops.store.transaction() as db:
            prior=db.execute(
                """SELECT read_at FROM notice_reads
                   WHERE notice_ref='public1' AND lease_ref='l1' AND subject_ref='resident1'""",
            ).fetchone()
            current=db.execute(
                """SELECT read_at FROM notice_reads
                   WHERE notice_ref='public1' AND lease_ref='l2' AND subject_ref='resident1'""",
            ).fetchone()
            self.assertIsNotNone(prior)
            self.assertIsNotNone(current)

    def test_old_lease_appointment_cannot_be_viewed_or_reproposed_after_releasing_unit(self):
        start,end=times()
        self.comms.request_appointment(
            self.primary,work_ref="w1",appointment_ref="old-ap",
            start_at=start,end_at=end,
        )
        self.ops.end_lease(
            self.manager,property_ref="p1",lease_ref="l1",expected_revision=1,
        )
        with self.ops.store.transaction(write=True) as db:
            db.execute(
                "UPDATE units SET lifecycle='ready' WHERE property_ref='p1' AND unit_ref='u1'",
            )
        self.ops.activate_lease(
            self.manager,property_ref="p1",unit_ref="u1",lease_ref="l2",
            resident_ref="resident1",start_on="2028-01-01",end_on="2028-12-31",
        )
        with self.assertRaises(AccessDenied):
            self.comms.appointment(self.primary,appointment_ref="old-ap")
        with self.assertRaises(AccessDenied):
            self.comms.history(self.primary,appointment_ref="old-ap")
        with self.assertRaises(AccessDenied):
            self.comms.accept_appointment(
                self.primary,appointment_ref="old-ap",expected_revision=1,
            )
        with self.assertRaises(AccessDenied):
            self.comms.cancel_appointment(
                self.primary,appointment_ref="old-ap",expected_revision=1,
            )
        with self.assertRaises(AccessDenied):
            self.comms.propose_appointment(
                self.manager,appointment_ref="old-ap",start_at=start,
                end_at=end,expected_revision=1,
            )
        self.ops.submit_maintenance(
            self.primary,work_ref="new-job",
            intake=MaintenanceIntake(
                "p1","u1","plumbing","Current lease request",False,"contact_first",
            ),
        )
        valid=self.comms.request_appointment(
            self.primary,work_ref="new-job",appointment_ref="new-ap",
            start_at=start,end_at=end,
        )
        self.assertEqual(valid["state"],"requested")

    def test_appointment_request_proposal_acceptance_without_entry_authorization(self):
        start,end=times()
        created=self.comms.request_appointment(
            self.primary,work_ref="w1",appointment_ref="ap1",start_at=start,end_at=end,
        )
        self.assertEqual(created["state"],"requested")
        self.assertFalse(created["entry_consent_granted"])
        with self.assertRaises(AccessDenied):
            self.comms.appointment(self.co,appointment_ref="ap1")
        with self.assertRaises(AccessDenied):
            self.comms.appointment(self.outside,appointment_ref="ap1")
        with self.assertRaises(GroundsConflict):
            self.comms.request_appointment(
                self.primary,work_ref="w1",appointment_ref="ap2",start_at=start,end_at=end,
            )
        proposed=self.comms.propose_appointment(
            self.manager,appointment_ref="ap1",start_at=start,end_at=end,expected_revision=1,
        )
        self.assertFalse(proposed["notification_sent"])
        with self.assertRaises(GroundsConflict):
            self.comms.accept_appointment(
                self.primary,appointment_ref="ap1",expected_revision=1,
            )
        with self.assertRaises(AccessDenied):
            self.comms.accept_appointment(
                self.co,appointment_ref="ap1",expected_revision=2,
            )
        accepted=self.comms.accept_appointment(
            self.primary,appointment_ref="ap1",expected_revision=2,
        )
        self.assertEqual(accepted["state"],"accepted")
        self.assertFalse(accepted["entry_consent_granted"])
        self.assertFalse(accepted["dispatch_confirmed"])
        self.assertFalse(accepted["legal_entry_notice_proven"])
        self.assertEqual(
            [e["action"] for e in self.comms.history(self.primary,appointment_ref="ap1")],
            ["requested","proposed","accepted"],
        )
        self.comms.cancel_appointment(self.primary,appointment_ref="ap1",expected_revision=3)
        with self.assertRaises(GroundsConflict):
            self.comms.cancel_appointment(self.primary,appointment_ref="ap1",expected_revision=3)
        self.comms.request_appointment(
            self.primary,work_ref="w1",appointment_ref="ap2",start_at=start,end_at=end,
        )

    def test_invalid_windows_and_unlisted_resident_denied(self):
        start,end=times()
        with self.assertRaises(GroundsConflict):
            self.comms.request_appointment(
                self.primary,work_ref="w1",appointment_ref="no-tz",
                start_at="2030-01-01T10:00:00",end_at="2030-01-01T11:00:00",
            )
        with self.assertRaises(GroundsConflict):
            self.comms.request_appointment(
                self.primary,work_ref="w1",appointment_ref="backwards",
                start_at=end,end_at=start,
            )
        with self.assertRaises(GroundsConflict):
            self.comms.request_appointment(
                self.primary,work_ref="w1",appointment_ref="too-long",
                start_at=start,end_at=(datetime.fromisoformat(start)+timedelta(hours=9)).isoformat(),
            )
        with self.assertRaises(AccessDenied):
            self.comms.request_appointment(
                self.other,work_ref="w1",appointment_ref="other",start_at=start,end_at=end,
            )
        with self.assertRaises(AccessDenied):
            self.comms.request_appointment(
                self.co,work_ref="w1",appointment_ref="co-cannot-see-peer-job",start_at=start,end_at=end,
            )

    def test_revoked_member_and_ended_lease_no_notice_or_appointment_access(self):
        start,end=times()
        self.comms.request_appointment(
            self.primary,work_ref="w1",appointment_ref="ap1",start_at=start,end_at=end,
        )
        self.ops.publish_notice(self.manager,property_ref="p1",notice_ref="n1",
                                headline="Example",body="Test")
        self.ops.end_lease(self.manager,property_ref="p1",lease_ref="l1",expected_revision=1)
        with self.assertRaises(AccessDenied):
            self.comms.appointment(self.primary,appointment_ref="ap1")
        with self.assertRaises(AccessDenied):
            self.comms.mark_notice_read(
                self.co,property_ref="p1",unit_ref="u1",notice_ref="n1",
            )
        with self.assertRaises(AccessDenied):
            self.comms.propose_appointment(
                self.outside,appointment_ref="ap1",start_at=start,end_at=end,
                expected_revision=1,
            )


if __name__=="__main__":
    unittest.main()
