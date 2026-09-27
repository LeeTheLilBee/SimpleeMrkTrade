"""GRD047: context-grounded Soulaana explanations, privacy and no action claims."""
import tempfile
import time
import unittest
from datetime import datetime,timezone,timedelta
from pathlib import Path

from grounds.access import AccessDenied
from grounds.capital import LANES
from grounds.communications import GroundsCommunications
from grounds.leasing import GroundsLeasing
from grounds.maintenance import MaintenanceIntake
from grounds.operations import GroundsOperations
from grounds.soulaana import (
    explain_resident_lease,explain_verified_resident_rent,
    explain_verified_apartment_readiness,explain_appointment,
    explain_inspection,explain_turnover,explain_leasing_unit,
    explain_property_pulse,
)
from grounds.stewardship import GroundsStewardship
from grounds.storage import GroundsStore
from grounds.test_grounds_capital import fixture_snapshot
from grounds.test_grounds_operations import fixture_scope


class SoulaanaContextTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        store=GroundsStore(Path(self.tmp.name)/"grounds.sqlite3")
        store.initialize()
        self.ops=GroundsOperations(store)
        self.comms=GroundsCommunications(store)
        self.st=GroundsStewardship(store)
        self.leasing=GroundsLeasing(store)
        self.owner=fixture_scope("owner","owner",("p1","p2"))
        self.manager=fixture_scope("manager","property_manager",("p1",))
        self.resident=fixture_scope("resident1","resident",("p1",),("u1",))
        self.other=fixture_scope("resident2","resident",("p1",),("u1",))
        self.outside=fixture_scope("manager2","property_manager",("p2",))
        self.agent=fixture_scope("leasing","leasing_agent",("p1",))
        for p in ("p1","p2"):
            self.ops.record_closed_property(
                self.owner,property_ref=p,name="Fictional "+p,
                close_evidence={"status":"verified_closed","property_ref":p,
                                "proof_ref":"closed-"+p,"owned_on":"2026-09-26"},
                close_verifier=lambda d:d, # TEST ONLY
            )
        self.ops.add_building(self.manager,property_ref="p1",building_ref="b1",label="Building A")
        self.ops.add_unit(self.manager,property_ref="p1",building_ref="b1",unit_ref="u1",label="101")
        self.ops.activate_lease(
            self.manager,property_ref="p1",unit_ref="u1",
            lease_ref="l1",resident_ref="resident1",
            start_on="2026-09-26",end_on="2027-09-25",
        )
        self.ops.submit_maintenance(
            self.resident,work_ref="w1",
            intake=MaintenanceIntake("p1","u1","plumbing",
                                     "Example kitchen faucet leak",True,"contact_first"),
        )

    def tearDown(self):
        self.tmp.cleanup()

    def _rent(self):
        now=int(time.time())
        return {
            "source":"teller","audience":"grounds","resident_ref":"resident1",
            "property_ref":"p1","unit_ref":"u1","lease_ref":"l1",
            "observed_at":now,"expires_at":now+120,
            "amount_due_cents":50000,"currency":"USD","invoice_status":"partial",
            "due_on":"2026-10-01","teller_handoff_ref":"opaque-intent",
        }

    def test_resident_lease_and_rent_recheck_own_current_membership_and_teller(self):
        lease=explain_resident_lease(self.resident,self.ops,property_ref="p1",unit_ref="u1")
        self.assertEqual(lease["lease_ref"],"l1")
        self.assertFalse(lease["actual_lease_document_loaded"])
        rent=explain_verified_resident_rent(
            self.resident,self.ops,self._rent(),property_ref="p1",unit_ref="u1",
            teller_verifier=lambda signed:signed, # TEST ONLY
        )
        self.assertEqual(rent["invoice_status"],"partial")
        self.assertEqual(rent["amount_due_cents"],50000)
        self.assertFalse(rent["checkout_executed"])
        self.assertIsNone(rent["checkout_url"])
        with self.assertRaises(AccessDenied):
            explain_resident_lease(self.other,self.ops,property_ref="p1",unit_ref="u1")
        with self.assertRaises(AccessDenied):
            explain_verified_resident_rent(
                self.other,self.ops,self._rent(),property_ref="p1",unit_ref="u1",
                teller_verifier=lambda d:d,
            )
        with self.assertRaises(AccessDenied):
            explain_verified_resident_rent(
                self.resident,self.ops,{**self._rent(),"lease_ref":"other"},
                property_ref="p1",unit_ref="u1",teller_verifier=lambda d:d,
            )
        with self.assertRaises(AccessDenied):
            explain_verified_resident_rent(
                self.resident,self.ops,self._rent(),property_ref="p1",
                unit_ref="u1",teller_verifier=None,
            )

    def test_teller_readiness_requires_exact_terms_and_no_spendable_assumption(self):
        snap=fixture_snapshot()
        output=explain_verified_apartment_readiness(
            self.owner,snap,property_ref="p1",mission_ref="apartment-mission",
            terms_digest="digest-v1",teller_verifier=lambda d:d, # TEST ONLY
        )
        self.assertFalse(output["ob_queried"])
        self.assertFalse(output["money_moved"])
        self.assertEqual(output["source_terms_digest"],"digest-v1")
        with self.assertRaises(AccessDenied):
            explain_verified_apartment_readiness(
                self.owner,snap,property_ref="p1",mission_ref="apartment-mission",
                terms_digest="changed-terms",teller_verifier=lambda d:d,
            )
        with self.assertRaises(AccessDenied):
            explain_verified_apartment_readiness(
                self.outside,snap,property_ref="p1",mission_ref="apartment-mission",
                terms_digest="digest-v1",teller_verifier=lambda d:d,
            )

    def test_appointment_explanation_cannot_imply_entry_or_notice(self):
        start=datetime.now(timezone.utc)+timedelta(days=2)
        end=start+timedelta(hours=2)
        self.comms.request_appointment(
            self.resident,work_ref="w1",appointment_ref="ap1",
            start_at=start.isoformat(),end_at=end.isoformat(),
        )
        output=explain_appointment(self.resident,self.comms,appointment_ref="ap1")
        self.assertEqual(output["source_state"],"requested")
        self.assertFalse(output["entry_consent_granted"])
        self.assertFalse(output["notice_delivered"])
        with self.assertRaises(AccessDenied):
            explain_appointment(self.other,self.comms,appointment_ref="ap1")

    def test_inspection_severe_findings_explained_only_to_authorized_staff(self):
        self.st.plan_inspection(
            self.manager,property_ref="p1",unit_ref="u1",inspection_ref="i1",
            category="routine",planned_on="2026-10-03",
        )
        self.st.advance_inspection(
            self.manager,property_ref="p1",inspection_ref="i1",
            next_state="in_progress",expected_revision=1,
        )
        self.st.record_finding(
            self.manager,property_ref="p1",inspection_ref="i1",
            finding_ref="f1",severity="urgent",narrative="Fictional serious finding",
        )
        info=explain_inspection(self.manager,self.st,property_ref="p1",inspection_ref="i1")
        self.assertEqual(info["unresolved_major_or_urgent"],1)
        self.assertIn("Certified",info["message"])
        self.assertFalse(info["inspection_closed_by_assistant"])
        with self.assertRaises(AccessDenied):
            explain_inspection(self.outside,self.st,property_ref="p1",inspection_ref="i1")
        with self.assertRaises(AccessDenied):
            explain_inspection(self.resident,self.st,property_ref="p1",inspection_ref="i1")

    def test_turnover_explains_missing_exact_inspection_no_auto_approval(self):
        self.ops.end_lease(self.manager,property_ref="p1",lease_ref="l1",expected_revision=1)
        self.st.begin_turnover(
            self.manager,property_ref="p1",unit_ref="u1",lease_ref="l1",turnover_ref="t1",
        )
        item=explain_turnover(self.manager,self.st,property_ref="p1",turnover_ref="t1")
        self.assertIn("linked inspection",item["message"])
        self.assertFalse(item["leasing_advertised"])
        with self.assertRaises(AccessDenied):
            explain_turnover(self.outside,self.st,property_ref="p1",turnover_ref="t1")

    def test_leasing_and_owner_status_no_hidden_finance_or_applicant_claims(self):
        item=explain_leasing_unit(self.agent,self.leasing,property_ref="p1",unit_ref="u1")
        self.assertEqual(item["lifecycle"],"occupied")
        self.assertFalse(item["applicant_screened"])
        with self.assertRaises(AccessDenied):
            explain_leasing_unit(self.resident,self.leasing,property_ref="p1",unit_ref="u1")
        pulse=explain_property_pulse(self.owner,self.ops,property_ref="p1")
        self.assertEqual((pulse["units"],pulse["occupied_units"],pulse["open_work_orders"]),(1,1,1))
        self.assertIsNone(pulse["rent_collections"])
        self.assertFalse(pulse["ob_queried"])
        with self.assertRaises(AccessDenied):
            explain_property_pulse(self.outside,self.ops,property_ref="p1")


if __name__=="__main__":
    unittest.main()
