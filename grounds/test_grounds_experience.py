"""GRD163–167: fictional exact-lease, daily and owner portfolio projections."""
from __future__ import annotations

import tempfile
import unittest
from datetime import datetime,timedelta,timezone
from pathlib import Path

from grounds.access import AccessDenied
from grounds.experience import GroundsExperience
from grounds.maintenance import MaintenanceIntake
from grounds.operations import GroundsOperations
from grounds.storage import GroundsStore
from grounds.test_grounds_operations import fixture_scope


class ExperienceTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.store=GroundsStore(Path(self.tmp.name)/"fiction.sqlite3")
        self.store.initialize()
        self.ops=GroundsOperations(self.store)
        self.experience=GroundsExperience(self.store)
        self.owner=fixture_scope("owner","owner",("p1","p2"))
        self.manager=fixture_scope("manager","property_manager",("p1",))
        self.supervisor=fixture_scope("supervisor","maintenance_supervisor",("p1",))
        self.regional=fixture_scope("regional","regional_manager",("p1",))
        self.resident=fixture_scope("r1","resident",("p1",),("u1",))
        self.other=fixture_scope("r2","resident",("p1",),("u1",))
        for ref in ("p1","p2"):
            self.ops.record_closed_property(
                self.owner,property_ref=ref,name="Fictional "+ref,
                close_evidence={"status":"verified_closed","property_ref":ref,
                                "proof_ref":"proof-"+ref,"owned_on":"2026-09-26"},
                close_verifier=lambda x:x,
            )
        self.ops.add_building(self.manager,property_ref="p1",building_ref="b1",label="A")
        self.ops.add_unit(self.manager,property_ref="p1",building_ref="b1",unit_ref="u1",label="101")
        self.ops.activate_lease(self.manager,property_ref="p1",unit_ref="u1",
                                lease_ref="l1",resident_ref="r1",
                                start_on="2026-09-26",end_on="2027-09-25")
        self.ops.publish_notice(
            self.manager,property_ref="p1",notice_ref="n1",
            headline="Fictional update",body="Fixture-only notice",
        )

    def tearDown(self):
        self.tmp.cleanup()

    def test_my_home_is_current_lease_only_and_cannot_infer_money(self):
        home=self.experience.my_home(self.resident,property_ref="p1",unit_ref="u1")
        self.assertEqual(home["property_name"],"Fictional p1")
        self.assertEqual(home["lease"]["lease_ref"],"l1")
        self.assertEqual(home["visible_notice_count"],1)
        self.assertEqual(home["unread_in_app_count"],1)
        self.assertIsNone(home["rent"]["amount_due_cents"])
        self.assertFalse(home["rent"]["payment_enabled"])
        self.assertFalse(home["documents"]["private_retrieval_connected"])
        with self.assertRaises(AccessDenied):
            self.experience.my_home(self.other,property_ref="p1",unit_ref="u1")
        with self.assertRaises(AccessDenied):
            self.experience.my_home(self.resident,property_ref="p2",unit_ref="u1")
        with self.assertRaises(AccessDenied):
            self.experience.my_home(self.manager,property_ref="p1",unit_ref="u1")
        self.ops.end_lease(self.manager,property_ref="p1",lease_ref="l1",expected_revision=1)
        with self.assertRaises(AccessDenied):
            self.experience.my_home(self.resident,property_ref="p1",unit_ref="u1")

    def test_daily_priority_queue_and_supervisor_turnover_redaction(self):
        self.ops.submit_maintenance(
            self.resident,work_ref="urgent1",
            intake=MaintenanceIntake("p1","u1","safety","Synthetic leak",True,"contact_first"),
        )
        d=self.experience.daily(self.manager,property_ref="p1")
        self.assertEqual(d["counts"]["unreviewed_urgent"],1)
        self.assertEqual(d["urgent_work"][0]["work_ref"],"urgent1")
        self.assertNotIn("description",str(d))
        self.assertFalse(d["delivery_confirmed_by_this_view"])
        self.assertFalse(d["emergency_dispatch_confirmed"])
        sup=self.experience.daily(self.supervisor,property_ref="p1")
        self.assertIsNone(sup["counts"]["open_turnovers"])
        self.assertFalse(sup["turnovers_authorized"])
        for actor in (self.resident,self.regional):
            with self.assertRaises(AccessDenied):
                self.experience.daily(actor,property_ref="p1")
        with self.assertRaises(AccessDenied):
            self.experience.daily(self.manager,property_ref="p2")

    def test_property_health_is_bounded_operational_only_and_owner_portfolio(self):
        self.ops.submit_maintenance(
            self.resident,work_ref="repeat1",
            intake=MaintenanceIntake("p1","u1","plumbing","Synthetic A",False,"contact_first"),
        )
        self.ops.submit_maintenance(
            self.resident,work_ref="repeat2",
            intake=MaintenanceIntake("p1","u1","plumbing","Synthetic B",False,"contact_first"),
        )
        h=self.experience.property_health(self.regional,property_ref="p1")
        self.assertEqual(h["counts"]["repeat_unit_category_groups_last_30_days"],1)
        self.assertEqual(h["counts"]["new_requests_last_30_days"],2)
        self.assertIsNone(h["rent_collections"])
        self.assertIsNone(h["available_capital"])
        self.assertFalse(h["resident_identity_included"])
        self.assertFalse(h["sla_attested"])
        with self.assertRaises(AccessDenied):
            self.experience.property_health(self.regional,property_ref="p2")
        with self.assertRaises(AccessDenied):
            self.experience.property_health(self.resident,property_ref="p1")
        portfolio=self.experience.owner_portfolio(self.owner)
        self.assertEqual(portfolio["total_scope_count"],2)
        self.assertEqual(len(portfolio["properties"]),2)
        self.assertFalse(portfolio["money_fields_included"])
        with self.assertRaises(AccessDenied):
            self.experience.owner_portfolio(self.manager)


if __name__=="__main__":
    unittest.main()
