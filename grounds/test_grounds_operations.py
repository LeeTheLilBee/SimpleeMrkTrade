"""GRD012–014: isolated, fake-data integration tests for scoped local operations."""
import sqlite3
import tempfile
import time
import unittest
from pathlib import Path

from grounds.access import AccessDenied, TowerScope, verified_scope
from grounds.maintenance import MaintenanceIntake
from grounds.operations import GroundsConflict, GroundsOperations
from grounds.storage import GroundsStore
from grounds.teller import resident_rent_projection
from grounds.soulaana import explain_work_order


def fixture_scope(subject, role, properties=("p1",), units=(), assignments=(), *, expires=None):
    now = int(time.time())
    ticket = {
        "issuer": "tower", "audience": "grounds",
        "subject_ref": subject, "role": role,
        "property_refs": list(properties), "unit_refs": list(units),
        "assigned_work_refs": list(assignments), "session_ref": "fixture-session",
        "issued_at": now - 1, "expires_at": now + 180 if expires is None else expires,
    }
    # TEST ONLY. Real app must inject an authenticated Tower verifier, never lambda identity.
    return verified_scope(ticket, verifier=lambda signed: signed)


def intake(property_ref="p1", unit_ref="u1", *, emergency=False):
    return MaintenanceIntake(
        property_ref, unit_ref, "plumbing", "Faucet is leaking",
        emergency, "contact_first", (),
    )


class GroundsOperationsTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.store = GroundsStore(Path(self.temp.name) / "grounds.sqlite3")
        self.store.initialize()
        self.ops = GroundsOperations(self.store)
        self.owner = fixture_scope("owner", "owner", ("p1","p2"))
        self.manager = fixture_scope("manager", "property_manager")
        self.resident = fixture_scope("resident1", "resident", units=("u1",))
        self.outsider = fixture_scope("resident2", "resident", ("p2",), ("u2",))
        self.technician = fixture_scope("tech1", "maintenance_technician", assignments=("w1",))
        self.other_technician = fixture_scope("tech2", "maintenance_technician", ("p2",), assignments=("w1",))
        self.ops.record_closed_property(
            self.owner, property_ref="p1", name="Test property",
            close_evidence={"status":"verified_closed","property_ref":"p1",
                            "proof_ref":"vault-proof-test-1","owned_on":"2026-09-26"},
            close_verifier=lambda signed: signed,  # TEST FIXTURE ONLY
        )
        self.ops.record_closed_property(
            self.owner, property_ref="p2", name="Other test property",
            close_evidence={"status":"verified_closed","property_ref":"p2",
                            "proof_ref":"vault-proof-test-2","owned_on":"2026-09-26"},
            close_verifier=lambda signed: signed,
        )
        self.ops.add_building(self.manager, property_ref="p1", building_ref="b1", label="Building One")
        self.ops.add_unit(self.manager, property_ref="p1", building_ref="b1", unit_ref="u1", label="101")
        self.ops.activate_lease(self.manager, property_ref="p1", unit_ref="u1", lease_ref="l1",
                                resident_ref="resident1", start_on="2026-09-26", end_on="2027-09-25",
                                vault_proof_ref=None)

    def tearDown(self):
        self.temp.cleanup()

    def test_tower_scope_requires_verifier_and_valid_properties(self):
        with self.assertRaises(AccessDenied):
            verified_scope({}, verifier=None)
        with self.assertRaises(AccessDenied):
            verified_scope({"foo":"bar"}, verifier=lambda item: item)
        with self.assertRaises(AccessDenied):
            TowerScope("forged","resident",frozenset(("p1",)),frozenset(("u1",)),
                       frozenset(),int(time.time())+100,"fake",object())
        with self.assertRaises(AccessDenied):
            fixture_scope("old", "owner", expires=int(time.time())-1)

    def test_close_evidence_required_and_duplicate_blocked(self):
        with self.assertRaises(AccessDenied):
            self.ops.record_closed_property(
                self.owner, property_ref="p2", name="Unverified",
                close_evidence={"status":"pending","property_ref":"p2"},
                close_verifier=lambda signed: signed,
            )
        with self.assertRaises(GroundsConflict):
            self.ops.record_closed_property(
                self.owner, property_ref="p1", name="Duplicate",
                close_evidence={"status":"verified_closed","property_ref":"p1",
                                "proof_ref":"another","owned_on":"2026-09-26"},
                close_verifier=lambda signed: signed,
            )

    def test_property_and_unit_foreign_keys_reject_mismatch(self):
        with self.assertRaises(GroundsConflict):
            self.ops.add_unit(self.manager, property_ref="p1", building_ref="b-outside",
                              unit_ref="u-wrong", label="999")
        with self.assertRaises(AccessDenied):
            self.ops.add_building(self.outsider, property_ref="p1", building_ref="bad", label="No")
        with self.assertRaises(AccessDenied):
            self.ops.add_building(fixture_scope("mgr2","property_manager",("p2",)),
                                  property_ref="p1", building_ref="bad", label="No")

    def test_lease_proof_cannot_claim_sealed_without_certified_vault(self):
        with self.assertRaises(GroundsConflict):
            self.ops.activate_lease(self.manager,property_ref="p1",unit_ref="u1",lease_ref="unverified",
                                    resident_ref="resident2",start_on="2026-09-26",end_on="2027-09-25",
                                    vault_proof_ref="unverified-ref")

    def test_active_lease_uniqueness_dates_and_turnover(self):
        with self.assertRaises(GroundsConflict):
            self.ops.activate_lease(self.manager,property_ref="p1",unit_ref="u1",lease_ref="l2",
                                    resident_ref="resident2",start_on="2026-09-26",end_on="2027-09-25")
        with self.assertRaises(GroundsConflict):
            self.ops.activate_lease(self.manager,property_ref="p1",unit_ref="u1",lease_ref="bad",
                                    resident_ref="r",start_on="2027-01-01",end_on="2026-01-01")
        self.ops.end_lease(self.manager,property_ref="p1",lease_ref="l1",expected_revision=1)
        with self.assertRaises(GroundsConflict):
            self.ops.activate_lease(
                self.manager,property_ref="p1",unit_ref="u1",lease_ref="l3",
                resident_ref="new-resident",start_on="2027-09-26",end_on="2028-09-25",
            )  # make_ready must be certified ready before another lease
        with self.assertRaises(GroundsConflict):
            self.ops.end_lease(self.manager,property_ref="p1",lease_ref="l1",expected_revision=1)
        with self.assertRaises(AccessDenied):
            self.ops.resident_home(self.resident,property_ref="p1",unit_ref="u1")
        with self.store.transaction() as db:
            self.assertEqual(db.execute("SELECT lifecycle FROM units WHERE unit_ref='u1'").fetchone()[0],"make_ready")

    def test_resident_home_notices_and_no_synthetic_rent(self):
        self.ops.publish_notice(self.manager,property_ref="p1",notice_ref="n1",
                                headline="Building notice",body="Example notice")
        self.ops.publish_notice(self.manager,property_ref="p1",notice_ref="n2",
                                headline="Unit notice",body="Example unit notice",unit_ref="u1")
        home = self.ops.resident_home(self.resident,property_ref="p1",unit_ref="u1")
        self.assertEqual(len(home["notices"]),2)
        self.assertEqual(home["lease"]["lease_ref"],"l1")
        self.assertIsNone(home["rent"]["amount_due_cents"])
        self.assertIsNone(home["rent"]["checkout_url"])
        with self.assertRaises(AccessDenied):
            self.ops.resident_home(self.outsider,property_ref="p1",unit_ref="u1")
        with self.assertRaises(GroundsConflict):
            self.ops.publish_notice(self.manager,property_ref="p1",notice_ref="no",
                                    headline="Wrong",body="Wrong property",unit_ref="u-from-p2")

    def test_unconnected_photo_intake_fails_instead_of_silently_dropping_proof(self):
        with self.assertRaises(GroundsConflict):
            self.ops.submit_maintenance(
                self.resident, work_ref="with-photo",
                intake=MaintenanceIntake("p1","u1","plumbing","Example",
                                         False,"contact_first",("opaque-unverified-ref",)),
            )

    def test_resident_submission_visibility_and_staff_controls(self):
        self.ops.submit_maintenance(self.resident,work_ref="w1",intake=intake(emergency=True))
        self.assertEqual(self.ops.get_work_order(self.resident,work_ref="w1")["emergency_flag"],1)
        self.assertEqual(len(self.ops.list_work_orders(self.resident,property_ref="p1")),1)
        with self.assertRaises(AccessDenied):
            self.ops.get_work_order(self.outsider,work_ref="w1")
        with self.assertRaises(AccessDenied):
            self.ops.get_work_order(self.technician,work_ref="w1")  # unassigned
        with self.assertRaises(AccessDenied):
            self.ops.submit_maintenance(self.outsider,work_ref="w2",intake=intake())

    def test_full_tenant_to_maintenance_workflow_and_audit(self):
        self.ops.submit_maintenance(self.resident,work_ref="w1",intake=intake())
        rev = 1
        for state in ("received","under_review","scheduled"):
            result = self.ops.advance_work_order(self.manager,work_ref="w1",
                                                  next_state=state,expected_revision=rev)
            rev = result["revision"]
        with self.assertRaises(AccessDenied):
            self.ops.assign_work_order(self.manager,work_ref="w1",technician=self.other_technician,
                                       expected_revision=rev)
        result = self.ops.assign_work_order(self.manager,work_ref="w1",
                                            technician=self.technician,expected_revision=rev)
        rev = result["revision"]
        self.assertEqual(self.ops.get_work_order(self.technician,work_ref="w1")["state"],"assigned")
        for state in ("in_progress","waiting","in_progress","completed"):
            result = self.ops.advance_work_order(self.technician,work_ref="w1",
                                                  next_state=state,expected_revision=rev)
            rev = result["revision"]
        with self.assertRaises(GroundsConflict):
            self.ops.advance_work_order(self.manager,work_ref="w1",
                                        next_state="confirmation",expected_revision=rev-1)
        result = self.ops.advance_work_order(self.manager,work_ref="w1",
                                             next_state="confirmation",expected_revision=rev)
        rev = result["revision"]
        result = self.ops.advance_work_order(self.resident,work_ref="w1",
                                              next_state="reopened",expected_revision=rev)
        rev = result["revision"]
        result = self.ops.advance_work_order(self.manager,work_ref="w1",
                                              next_state="under_review",expected_revision=rev)
        history = self.ops.work_history(self.resident,work_ref="w1")
        self.assertEqual(history[0]["action"],"created")
        self.assertEqual(history[-1]["to_state"],"under_review")
        self.assertEqual(len(history),result["revision"])

    def test_fail_closed_technician_and_nonauthorized_transition(self):
        self.ops.submit_maintenance(self.resident,work_ref="w1",intake=intake())
        with self.assertRaises(AccessDenied):
            self.ops.advance_work_order(self.technician,work_ref="w1",
                                        next_state="in_progress",expected_revision=1)
        with self.assertRaises(ValueError):
            self.ops.advance_work_order(self.manager,work_ref="w1",
                                        next_state="closed",expected_revision=1)

    def test_owner_pulse_property_scoped_and_no_rent_fiction(self):
        self.ops.submit_maintenance(self.resident,work_ref="w1",intake=intake())
        pulse = self.ops.property_pulse(self.owner,property_ref="p1")
        self.assertEqual((pulse["units"],pulse["occupied_units"],pulse["open_work_orders"]),(1,1,1))
        self.assertIsNone(pulse["rent_collections"])
        with self.assertRaises(AccessDenied):
            self.ops.property_pulse(self.outsider,property_ref="p1")

    def test_soulaana_explanation_keeps_source_revision_and_no_actions(self):
        self.ops.submit_maintenance(self.resident,work_ref="w1",intake=intake(emergency=True))
        explanation=explain_work_order(self.resident,self.ops,work_ref="w1")
        self.assertEqual(explanation["source"],"grounds")
        self.assertEqual(explanation["source_revision"],1)
        self.assertIn("urgency flag",explanation["message"])
        self.assertFalse(explanation["action_executed"])
        with self.assertRaises(AccessDenied):
            explain_work_order(self.outsider,self.ops,work_ref="w1")

    def test_teller_rent_snapshot_binds_exact_lease_and_freshness(self):
        home = self.ops.resident_home(self.resident,property_ref="p1",unit_ref="u1")
        now = int(time.time())
        signed = {
            "source":"teller","audience":"grounds","resident_ref":"resident1",
            "property_ref":"p1","unit_ref":"u1","lease_ref":"l1",
            "observed_at":now,"expires_at":now+120,
            "amount_due_cents":95000,"currency":"USD","invoice_status":"due",
            "due_on":"2026-10-01","teller_handoff_ref":"opaque-teller-intent",
        }
        # TEST ONLY, actual trusted Teller verifier must validate signature and replay.
        verify = lambda document: document
        rent = resident_rent_projection(self.resident,home,signed,teller_verifier=verify)
        self.assertEqual(rent["amount_due_cents"],95000)
        self.assertEqual(rent["pay_rent_action"],"request_tower_mediated_teller_handoff")
        self.assertIsNone(rent["checkout_url"])
        for change in (
            {"resident_ref":"resident2"}, {"lease_ref":"l2"}, {"source":"observatory"},
            {"amount_due_cents":-100}, {"amount_due_cents":True},
            {"observed_at":now-400,"expires_at":now-200},
        ):
            altered = {**signed,**change}
            with self.assertRaises(AccessDenied):
                resident_rent_projection(self.resident,home,altered,teller_verifier=verify)
        with self.assertRaises(AccessDenied):
            resident_rent_projection(self.resident,home,signed,teller_verifier=None)


if __name__ == "__main__":
    unittest.main()
