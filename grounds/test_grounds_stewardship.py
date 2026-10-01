"""GRD029–030: fictional local asset, inspection, preventive and turnover checks."""
import tempfile
import unittest
from datetime import date, timedelta
from pathlib import Path

from grounds.access import AccessDenied
from grounds.maintenance import MaintenanceIntake
from grounds.operations import GroundsConflict, GroundsOperations
from grounds.stewardship import GroundsStewardship
from grounds.storage import GroundsStore
from grounds.test_grounds_operations import fixture_scope, intake


class GroundsStewardshipTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.store=GroundsStore(Path(self.temp.name)/"test.sqlite3")
        self.store.initialize()
        self.ops=GroundsOperations(self.store)
        self.st=GroundsStewardship(self.store)
        self.owner=fixture_scope("owner","owner",("p1","p2"))
        self.manager=fixture_scope("manager","property_manager",("p1",))
        self.supervisor=fixture_scope("supervisor","maintenance_supervisor",("p1",))
        self.tech=fixture_scope("tech","maintenance_technician",("p1",),assignments=("w1",))
        self.inspector=fixture_scope("inspector","inspector",("p1",))
        self.outside=fixture_scope("outside","property_manager",("p2",))
        self.resident=fixture_scope("resident","resident",("p1",),("u1",))
        for ref in ("p1","p2"):
            self.ops.record_closed_property(
                self.owner,property_ref=ref,name="Example "+ref,
                close_evidence={"status":"verified_closed","property_ref":ref,
                                "proof_ref":"close-"+ref,"owned_on":"2026-09-26"},
                close_verifier=lambda doc:doc, # isolated test fixture only
            )
        self.ops.add_building(self.manager,property_ref="p1",building_ref="b1",label="A")
        self.ops.add_unit(self.manager,property_ref="p1",building_ref="b1",unit_ref="u1",label="101")
        self.ops.activate_lease(
            self.manager,property_ref="p1",unit_ref="u1",lease_ref="l1",resident_ref="resident",
            start_on="2026-09-26",end_on="2027-09-25",
        )
        self.st.record_asset(
            self.manager,property_ref="p1",unit_ref="u1",asset_ref="a1",
            label="Example fixture",category="plumbing",
        )

    def tearDown(self):
        self.temp.cleanup()

    def _closed_work(self):
        self.ops.submit_maintenance(self.resident,work_ref="w1",intake=intake())
        revision=1
        for state in ("received","under_review","scheduled"):
            revision=self.ops.advance_work_order(
                self.manager,work_ref="w1",next_state=state,expected_revision=revision,
            )["revision"]
        revision=self.ops.assign_work_order(
            self.manager,work_ref="w1",technician=self.tech,expected_revision=revision,
        )["revision"]
        for state in ("in_progress","completed"):
            revision=self.ops.advance_work_order(
                self.tech,work_ref="w1",next_state=state,expected_revision=revision,
            )["revision"]
        for state in ("confirmation","closed"):
            revision=self.ops.advance_work_order(
                self.manager,work_ref="w1",next_state=state,expected_revision=revision,
            )["revision"]

    def test_physical_workboard_minimized_counts_role_scope_and_no_authority(self):
        past=(date.today()-timedelta(days=1)).isoformat()
        self.st.create_preventive_plan(
            self.manager,property_ref="p1",asset_ref="a1",
            plan_ref="due-plan",cadence_days=30,next_due_on=past,
        )
        self.st.plan_inspection(
            self.manager,property_ref="p1",unit_ref="u1",
            inspection_ref="pending-inspection",category="routine",
            planned_on=date.today().isoformat(),
        )
        visible=self.st.physical_workboard(self.manager,property_ref="p1")
        self.assertEqual(visible["counts"]["assets"],1)
        self.assertEqual(visible["counts"]["due_preventive_plans"],1)
        self.assertEqual(visible["counts"]["open_inspections"],1)
        self.assertEqual(visible["due_preventive_plans"][0]["plan_ref"],"due-plan")
        self.assertEqual(visible["open_inspections"][0]["inspection_ref"],"pending-inspection")
        self.assertTrue(visible["turnover_view_authorized"])
        for name in ("provider_dispatch_confirmed","inspection_signoff_automated",
                     "vault_evidence_fetch_connected","capital_approval_enabled",
                     "legal_entry_or_notice_authorized"):
            self.assertFalse(visible[name])
        supervisor=self.st.physical_workboard(self.supervisor,property_ref="p1")
        self.assertFalse(supervisor["turnover_view_authorized"])
        self.assertIsNone(supervisor["counts"]["open_turnovers"])
        self.assertEqual(supervisor["open_turnovers"],[])
        for denied,prop in ((self.resident,"p1"),(self.tech,"p1"),(self.outside,"p1"),
                            (self.manager,"p2")):
            with self.subTest(role=denied.role,property_ref=prop):
                with self.assertRaises(AccessDenied):
                    self.st.physical_workboard(denied,property_ref=prop)
        self.ops.end_lease(self.manager,property_ref="p1",lease_ref="l1",
                           expected_revision=1)
        self.st.begin_turnover(
            self.manager,property_ref="p1",unit_ref="u1",
            lease_ref="l1",turnover_ref="turn-open",
        )
        manager_after=self.st.physical_workboard(self.manager,property_ref="p1")
        self.assertEqual(manager_after["counts"]["open_turnovers"],1)
        self.assertEqual(manager_after["open_turnovers"][0]["turnover_ref"],"turn-open")
        supervisor_after=self.st.physical_workboard(self.supervisor,property_ref="p1")
        self.assertIsNone(supervisor_after["counts"]["open_turnovers"])
        self.assertEqual(supervisor_after["open_turnovers"],[])

    def test_asset_boundary_and_no_inspector_self_grant(self):
        self.assertEqual(self.st.list_assets(self.manager,property_ref="p1")[0]["asset_ref"],"a1")
        with self.assertRaises(AccessDenied):
            self.st.list_assets(self.outside,property_ref="p1")
        with self.assertRaises(AccessDenied):
            self.st.list_assets(self.resident,property_ref="p1")
        with self.assertRaises(AccessDenied):
            self.st.plan_inspection(
                self.inspector,property_ref="p1",inspection_ref="i-denied",
                category="routine",planned_on=date.today().isoformat(),unit_ref="u1",
            )
        with self.assertRaises(GroundsConflict):
            self.st.record_asset(
                self.manager,property_ref="p1",unit_ref="unit-other-property",
                asset_ref="invalid",label="Wrong",category="fixture",
            )

    def test_preventive_plan_due_is_informational(self):
        past=(date.today()-timedelta(days=2)).isoformat()
        self.st.create_preventive_plan(
            self.supervisor,property_ref="p1",asset_ref="a1",plan_ref="plan1",
            cadence_days=30,next_due_on=past,
        )
        due=self.st.due_plans(self.manager,property_ref="p1",as_of=date.today().isoformat())
        self.assertEqual(len(due),1)
        self.assertEqual(due[0]["asset_ref"],"a1")
        with self.assertRaises(AccessDenied):
            self.st.due_plans(self.outside,property_ref="p1",as_of=date.today().isoformat())
        with self.assertRaises(GroundsConflict):
            self.st.create_preventive_plan(
                self.manager,property_ref="p1",asset_ref="a1",plan_ref="bad",
                cadence_days=True,next_due_on=past,
            )

    def test_preventive_completion_requires_closed_matching_work_and_sealed_evidence(self):
        today=date.today().isoformat()
        self.st.create_preventive_plan(
            self.manager,property_ref="p1",asset_ref="a1",plan_ref="plan1",
            cadence_days=30,next_due_on=today,
        )
        proof={"status":"verified_sealed","source":"vault","audience":"grounds","kind":"preventive_completion",
               "property_ref":"p1","plan_ref":"plan1","asset_ref":"a1","work_ref":"w1",
               "completed_on":today,"proof_ref":"test-proof-1"}
        with self.assertRaises(AccessDenied):
            self.st.complete_preventive_plan(
                self.manager,property_ref="p1",plan_ref="plan1",work_ref="w1",
                completed_on=today,expected_revision=1,signed_proof=proof,
                proof_verifier=lambda doc:doc,
            )
        self._closed_work()
        with self.assertRaises(AccessDenied):
            self.st.complete_preventive_plan(
                self.manager,property_ref="p1",plan_ref="plan1",work_ref="w1",
                completed_on=today,expected_revision=1,signed_proof={**proof,"asset_ref":"other"},
                proof_verifier=lambda doc:doc,
            )
        for incorrect in ({"source":"observatory"},{"audience":"buybox"}):
            with self.assertRaises(AccessDenied):
                self.st.complete_preventive_plan(
                    self.manager,property_ref="p1",plan_ref="plan1",work_ref="w1",
                    completed_on=today,expected_revision=1,
                    signed_proof={**proof,**incorrect},proof_verifier=lambda doc:doc,
                )
        with self.assertRaises(AccessDenied):
            self.st.complete_preventive_plan(
                self.manager,property_ref="p1",plan_ref="plan1",work_ref="w1",
                completed_on=today,expected_revision=1,signed_proof=proof,proof_verifier=None,
            )
        outcome=self.st.complete_preventive_plan(
            self.manager,property_ref="p1",plan_ref="plan1",work_ref="w1",
            completed_on=today,expected_revision=1,signed_proof=proof,
            proof_verifier=lambda doc:doc,
        )
        self.assertEqual(outcome["revision"],2)
        self.assertEqual(outcome["next_due_on"],(date.today()+timedelta(days=30)).isoformat())
        self.assertFalse(outcome["external_schedule_created"])
        with self.assertRaises(GroundsConflict):
            self.st.complete_preventive_plan(
                self.manager,property_ref="p1",plan_ref="plan1",work_ref="w1",
                completed_on=today,expected_revision=1,signed_proof=proof,
                proof_verifier=lambda doc:doc,
            )

    def test_inspection_review_rejects_missing_or_severe_findings(self):
        today=date.today().isoformat()
        self.st.plan_inspection(self.manager,property_ref="p1",unit_ref="u1",
                                inspection_ref="i1",category="routine",planned_on=today)
        self.st.advance_inspection(
            self.manager,property_ref="p1",inspection_ref="i1",
            next_state="in_progress",expected_revision=1,
        )
        with self.assertRaises(GroundsConflict):
            self.st.advance_inspection(
                self.manager,property_ref="p1",inspection_ref="i1",
                next_state="closed",expected_revision=2,
            )
        self.st.record_finding(
            self.supervisor,property_ref="p1",inspection_ref="i1",
            finding_ref="f1",severity="major",narrative="Example serious finding",
        )
        self.st.advance_inspection(
            self.manager,property_ref="p1",inspection_ref="i1",
            next_state="review",expected_revision=2,
        )
        with self.assertRaises(GroundsConflict):
            self.st.advance_inspection(
                self.manager,property_ref="p1",inspection_ref="i1",
                next_state="closed",expected_revision=3,
            )
        with self.assertRaises(AccessDenied):
            self.st.record_finding(
                self.inspector,property_ref="p1",inspection_ref="i1",
                finding_ref="f-bad",severity="minor",narrative="No assignment protocol",
            )
        proof={"status":"verified_sealed","source":"vault","audience":"grounds","kind":"inspection_resolution","property_ref":"p1",
               "inspection_ref":"i1","finding_ref":"f1","unit_ref":"u1","proof_ref":"proof-clear-1"}
        with self.assertRaises(AccessDenied):
            self.st.resolve_inspection_finding(
                self.manager,property_ref="p1",inspection_ref="i1",finding_ref="f1",
                signed_proof=proof,proof_verifier=None,
            )
        with self.assertRaises(AccessDenied):
            self.st.resolve_inspection_finding(
                self.manager,property_ref="p1",inspection_ref="i1",finding_ref="f1",
                signed_proof={**proof,"property_ref":"p2"},proof_verifier=lambda doc:doc,
            )
        resolved=self.st.resolve_inspection_finding(
            self.manager,property_ref="p1",inspection_ref="i1",finding_ref="f1",
            signed_proof=proof,proof_verifier=lambda doc:doc, # TEST ONLY
        )
        self.assertEqual(resolved["proof_ref"],"proof-clear-1")
        with self.assertRaises(GroundsConflict):
            self.st.resolve_inspection_finding(
                self.manager,property_ref="p1",inspection_ref="i1",finding_ref="f1",
                signed_proof=proof,proof_verifier=lambda doc:doc,
            )
        reviewed=self.st.advance_inspection(
            self.manager,property_ref="p1",inspection_ref="i1",
            next_state="closed",expected_revision=3,
        )
        self.assertEqual(reviewed["state"],"closed")

    def _begin_turnover(self):
        self.ops.end_lease(self.manager,property_ref="p1",lease_ref="l1",expected_revision=1)
        return self.st.begin_turnover(
            self.manager,property_ref="p1",unit_ref="u1",lease_ref="l1",turnover_ref="t1",
        )

    def _closed_turnover_inspection(self):
        today=date.today().isoformat()
        self.st.plan_inspection(
            self.manager,property_ref="p1",unit_ref="u1",inspection_ref="inspect-turn",
            category="turnover",planned_on=today,turnover_ref="t1",
        )
        self.st.advance_inspection(
            self.manager,property_ref="p1",inspection_ref="inspect-turn",
            next_state="in_progress",expected_revision=1,
        )
        self.st.record_finding(
            self.manager,property_ref="p1",inspection_ref="inspect-turn",
            finding_ref="f-no-defect",severity="observation",narrative="No observed deficiencies",
        )
        self.st.advance_inspection(
            self.manager,property_ref="p1",inspection_ref="inspect-turn",
            next_state="review",expected_revision=2,
        )
        self.st.advance_inspection(
            self.manager,property_ref="p1",inspection_ref="inspect-turn",
            next_state="closed",expected_revision=3,
        )

    def test_unlinked_or_old_same_day_inspection_does_not_satisfy_turnover(self):
        today=date.today().isoformat()
        # A routine inspection of the same unit—even today—cannot be reused.
        self.st.plan_inspection(
            self.manager,property_ref="p1",unit_ref="u1",inspection_ref="old-inspection",
            category="routine",planned_on=today,
        )
        self.st.advance_inspection(self.manager,property_ref="p1",
                                   inspection_ref="old-inspection",next_state="in_progress",
                                   expected_revision=1)
        self.st.record_finding(self.manager,property_ref="p1",inspection_ref="old-inspection",
                               finding_ref="old-observation",severity="observation",
                               narrative="Unrelated routine check")
        self.st.advance_inspection(self.manager,property_ref="p1",
                                   inspection_ref="old-inspection",next_state="review",
                                   expected_revision=2)
        self.st.advance_inspection(self.manager,property_ref="p1",
                                   inspection_ref="old-inspection",next_state="closed",
                                   expected_revision=3)
        self._begin_turnover()
        self.st.advance_turnover(self.manager,property_ref="p1",turnover_ref="t1",
                                 next_state="inspection",expected_revision=1)
        with self.assertRaises(GroundsConflict):
            self.st.advance_turnover(self.manager,property_ref="p1",turnover_ref="t1",
                                     next_state="work",expected_revision=2)
        with self.assertRaises(GroundsConflict):
            self.st.plan_inspection(
                self.manager,property_ref="p1",unit_ref="u1",inspection_ref="unlinked",
                category="turnover",planned_on=today,
            )
        with self.assertRaises(AccessDenied):
            self.st.plan_inspection(
                self.manager,property_ref="p1",unit_ref="u1",inspection_ref="wrong-turn",
                category="turnover",planned_on=today,turnover_ref="unknown",
            )

    def test_no_turnover_before_ended_lease_and_single_active_case(self):
        with self.assertRaises(AccessDenied):
            self.st.begin_turnover(
                self.manager,property_ref="p1",unit_ref="u1",lease_ref="l1",
                turnover_ref="premature",
            )
        created=self._begin_turnover()
        self.assertEqual(created["state"],"planned")
        with self.assertRaises(GroundsConflict):
            self.st.begin_turnover(
                self.manager,property_ref="p1",unit_ref="u1",lease_ref="l1",
                turnover_ref="duplicate",
            )
        with self.assertRaises(AccessDenied):
            self.st.turnover_history(self.outside,property_ref="p1",turnover_ref="t1")

    def test_full_turnover_requires_inspection_no_open_work_and_valid_sealed_proof(self):
        started=self._begin_turnover()
        with self.assertRaises(GroundsConflict):
            self.st.advance_turnover(
                self.manager,property_ref="p1",turnover_ref="t1",
                next_state="work",expected_revision=1,
            )
        self.st.advance_turnover(
            self.manager,property_ref="p1",turnover_ref="t1",
            next_state="inspection",expected_revision=1,
        )
        with self.assertRaises(GroundsConflict):
            self.st.advance_turnover(
                self.manager,property_ref="p1",turnover_ref="t1",
                next_state="work",expected_revision=2,
            )
        self._closed_turnover_inspection()
        self.st.advance_turnover(
            self.manager,property_ref="p1",turnover_ref="t1",
            next_state="work",expected_revision=2,
        )
        # A new *manager* request is still open; review is blocked.
        self.ops.submit_maintenance(
            self.manager,work_ref="open-unit-work",intake=MaintenanceIntake(
                "p1","u1","turnover","Fixture needs attention",False,"contact_first",
            ),
        )
        with self.assertRaises(GroundsConflict):
            self.st.advance_turnover(
                self.manager,property_ref="p1",turnover_ref="t1",
                next_state="final_review",expected_revision=3,
            )
        # Close the review through real reference maintenance transitions.
        revision=1
        for state in ("received","under_review","scheduled"):
            revision=self.ops.advance_work_order(
                self.manager,work_ref="open-unit-work",
                next_state=state,expected_revision=revision,
            )["revision"]
        assigned_tech=fixture_scope(
            "tech","maintenance_technician",("p1",),assignments=("open-unit-work",),
        )
        revision=self.ops.assign_work_order(
            self.manager,work_ref="open-unit-work",
            technician=assigned_tech,expected_revision=revision,
        )["revision"]
        for state in ("in_progress","completed"):
            revision=self.ops.advance_work_order(
                assigned_tech,work_ref="open-unit-work",next_state=state,
                expected_revision=revision,
            )["revision"]
        for state in ("confirmation","closed"):
            revision=self.ops.advance_work_order(
                self.manager,work_ref="open-unit-work",next_state=state,
                expected_revision=revision,
            )["revision"]
        self.st.advance_turnover(
            self.manager,property_ref="p1",turnover_ref="t1",
            next_state="final_review",expected_revision=3,
        )
        proof={"status":"verified_sealed","source":"vault","audience":"grounds","kind":"turnover_final",
               "property_ref":"p1","unit_ref":"u1","turnover_ref":"t1","proof_ref":"final-proof-1"}
        with self.assertRaises(AccessDenied):
            self.st.complete_turnover(
                self.manager,property_ref="p1",turnover_ref="t1",
                expected_revision=4,signed_proof={**proof,"unit_ref":"u2"},
                proof_verifier=lambda doc:doc,
            )
        with self.assertRaises(AccessDenied):
            self.st.complete_turnover(
                self.manager,property_ref="p1",turnover_ref="t1",
                expected_revision=4,signed_proof=proof,proof_verifier=None,
            )
        finished=self.st.complete_turnover(
            self.manager,property_ref="p1",turnover_ref="t1",
            expected_revision=4,signed_proof=proof,
            proof_verifier=lambda doc:doc, # TEST ONLY; certified Vault adapter not connected
        )
        self.assertEqual(finished["state"],"complete")
        self.assertEqual(finished["unit_lifecycle"],"ready")
        self.assertFalse(finished["resident_notification_sent"])
        self.assertEqual(
            [row["to_state"] for row in self.st.turnover_history(
                self.manager,property_ref="p1",turnover_ref="t1",
            )],
            ["planned","inspection","work","final_review","complete"],
        )
        with self.assertRaises(GroundsConflict):
            self.st.complete_turnover(
                self.manager,property_ref="p1",turnover_ref="t1",
                expected_revision=4,signed_proof=proof,
                proof_verifier=lambda doc:doc,
            )


if __name__=="__main__":
    unittest.main()
