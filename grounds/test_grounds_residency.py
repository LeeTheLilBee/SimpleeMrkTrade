"""GRD040: local household authorization and lease-end revocation tests."""
import tempfile
import unittest
from pathlib import Path

from grounds.access import AccessDenied
from grounds.operations import GroundsConflict, GroundsOperations
from grounds.maintenance import MaintenanceIntake
from grounds.residency import GroundsResidency
from grounds.storage import GroundsStore
from grounds.test_grounds_operations import fixture_scope


def grant(kind, *, subject="person2", relationship="co_tenant", proof="proof-grant",
          lease="l1", unit="u1", property_ref="p1"):
    return {
        "status":"verified_sealed","kind":kind,"subject_ref":subject,
        "relationship":relationship,"property_ref":property_ref,"unit_ref":unit,
        "lease_ref":lease,"proof_ref":proof,
    }


class HouseholdTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        store=GroundsStore(Path(self.tmp.name)/"private-fictional.sqlite3")
        store.initialize()
        self.ops=GroundsOperations(store)
        self.household=GroundsResidency(store)
        self.owner=fixture_scope("owner","owner",("p1","p2"))
        self.manager=fixture_scope("manager","property_manager",("p1",))
        self.primary=fixture_scope("person1","resident",("p1",),("u1",))
        self.co=fixture_scope("person2","resident",("p1",),("u1",))
        self.other=fixture_scope("person3","resident",("p1",),("u1",))
        self.other_property=fixture_scope("property2","property_manager",("p2",))
        for prop in ("p1","p2"):
            self.ops.record_closed_property(
                self.owner,property_ref=prop,name="Fiction "+prop,
                close_evidence={"status":"verified_closed","property_ref":prop,
                                "proof_ref":"closed-"+prop,"owned_on":"2026-09-26"},
                close_verifier=lambda x:x, # TEST FIXTURE ONLY
            )
        self.ops.add_building(self.manager,property_ref="p1",building_ref="b1",label="A")
        self.ops.add_unit(self.manager,property_ref="p1",building_ref="b1",unit_ref="u1",label="101")
        self.ops.activate_lease(self.manager,property_ref="p1",unit_ref="u1",
                                lease_ref="l1",resident_ref="person1",
                                start_on="2026-09-26",end_on="2027-09-25")

    def tearDown(self):
        self.tmp.cleanup()

    def _add(self,*,subject="person2",relationship="co_tenant",proof="proof-grant"):
        evidence=grant("lease_member_grant",subject=subject,relationship=relationship,proof=proof)
        return self.household.grant_member(
            self.manager,property_ref="p1",unit_ref="u1",lease_ref="l1",
            subject_ref=subject,relationship=relationship,
            signed_grant=evidence,proof_verifier=lambda x:x, # TEST FIXTURE ONLY
        )

    def test_primary_exists_but_unlisted_occupant_cannot_enter(self):
        self.assertEqual(self.ops.resident_home(self.primary,property_ref="p1",
                                                unit_ref="u1")["lease"]["lease_ref"],"l1")
        with self.assertRaises(AccessDenied):
            self.ops.resident_home(self.co,property_ref="p1",unit_ref="u1")
        with self.assertRaises(AccessDenied):
            self.ops.submit_maintenance(
                self.co,work_ref="w-unlisted",
                intake=MaintenanceIntake("p1","u1","plumbing","Leak under sink",False,"contact_first"),
            )
        members=self.household.active_members(self.manager,property_ref="p1",lease_ref="l1")
        self.assertEqual([m["subject_ref"] for m in members],["person1"])
        with self.assertRaises(AccessDenied):
            self.household.active_members(self.other_property,property_ref="p1",lease_ref="l1")

    def test_verified_co_tenant_can_submit_own_request_not_see_peers(self):
        added=self._add()
        self.assertFalse(added["tower_entitlement_granted"])
        self.assertEqual(self.ops.resident_home(self.co,property_ref="p1",unit_ref="u1")["lease"]["lease_ref"],"l1")
        self.ops.submit_maintenance(
            self.co,work_ref="w-co",
            intake=MaintenanceIntake("p1","u1","plumbing","Test faucet leaks",False,"contact_first"),
        )
        self.assertEqual(len(self.ops.list_work_orders(self.co,property_ref="p1")),1)
        with self.assertRaises(AccessDenied):
            self.ops.get_work_order(self.primary,work_ref="w-co")
        with self.assertRaises(AccessDenied):
            self.ops.resident_home(self.other,property_ref="p1",unit_ref="u1")
        self.assertEqual(self.household.history(self.manager,property_ref="p1",lease_ref="l1")[-1]["action"],"verified_grant")

    def test_wrong_relationship_scope_or_reused_grant_denied(self):
        signed=grant("lease_member_grant",relationship="authorized_occupant")
        with self.assertRaises(AccessDenied):
            self.household.grant_member(
                self.manager,property_ref="p1",unit_ref="u1",lease_ref="l1",
                subject_ref="person2",relationship="co_tenant",
                signed_grant=signed,proof_verifier=lambda x:x,
            )
        with self.assertRaises(AccessDenied):
            self.household.grant_member(
                self.manager,property_ref="p1",unit_ref="u1",lease_ref="l1",
                subject_ref="person2",relationship="co_tenant",
                signed_grant={**signed,"relationship":"co_tenant","property_ref":"p2"},
                proof_verifier=lambda x:x,
            )
        with self.assertRaises(AccessDenied):
            self.household.grant_member(
                self.manager,property_ref="p1",unit_ref="u1",lease_ref="l1",
                subject_ref="person2",relationship="co_tenant",
                signed_grant=signed,proof_verifier=None,
            )
        self._add()
        with self.assertRaises(GroundsConflict):
            self._add(subject="person3",proof="proof-grant") # same proof different subject
        with self.assertRaises(GroundsConflict):
            self._add()
        with self.assertRaises(GroundsConflict):
            self._add(subject="person1",proof="proof-primary")

    def test_grant_revoked_immediately_from_ground_even_if_old_tower_unit_scope_remains(self):
        self._add()
        self.ops.submit_maintenance(
            self.co,work_ref="w-co",
            intake=MaintenanceIntake("p1","u1","plumbing","Test faucet leaks",False,"contact_first"),
        )
        with self.assertRaises(AccessDenied):
            self.household.revoke_member(
                self.manager,lease_ref="l1",property_ref="p1",unit_ref="u1",
                subject_ref="person2",signed_revocation=grant("lease_member_revocation",
                    subject="person2",proof="revoke"),proof_verifier=None,
            )
        revoked=self.household.revoke_member(
            self.manager,lease_ref="l1",property_ref="p1",unit_ref="u1",
            subject_ref="person2",signed_revocation=grant(
                "lease_member_revocation",subject="person2",proof="revoke",
            ),proof_verifier=lambda x:x, # TEST FIXTURE ONLY
        )
        self.assertTrue(revoked["tower_session_revocation_required"])
        with self.assertRaises(AccessDenied):
            self.ops.resident_home(self.co,property_ref="p1",unit_ref="u1")
        with self.assertRaises(AccessDenied):
            self.ops.get_work_order(self.co,work_ref="w-co")
        self.assertEqual(self.ops.list_work_orders(self.co,property_ref="p1"),[])
        self.assertFalse(any(m["subject_ref"]=="person2" for m in
            self.household.active_members(self.manager,property_ref="p1",lease_ref="l1")))
        with self.assertRaises(GroundsConflict):
            self.household.revoke_member(
                self.manager,lease_ref="l1",property_ref="p1",unit_ref="u1",
                subject_ref="person1",signed_revocation=grant(
                    "lease_member_revocation",subject="person1",proof="different",
                ),proof_verifier=lambda x:x,
            )

    def test_resident_list_requires_tower_unit_and_current_lease_membership(self):
        # Same subject is on two separate active leases, but Tower granted only u1.
        self.ops.add_unit(self.manager,property_ref="p1",building_ref="b1",
                          unit_ref="u2",label="102")
        self.ops.activate_lease(
            self.manager,property_ref="p1",unit_ref="u2",lease_ref="l2",
            resident_ref="person1",start_on="2026-09-26",end_on="2027-09-25",
        )
        broader=fixture_scope("person1","resident",("p1",),("u1","u2"))
        self.ops.submit_maintenance(
            broader,work_ref="unit1-request",
            intake=MaintenanceIntake("p1","u1","plumbing","Unit 101 tap",False,"contact_first"),
        )
        self.ops.submit_maintenance(
            broader,work_ref="unit2-request",
            intake=MaintenanceIntake("p1","u2","plumbing","Unit 102 tap",False,"contact_first"),
        )
        scoped=self.ops.list_work_orders(self.primary,property_ref="p1")
        self.assertEqual([x["work_ref"] for x in scoped],["unit1-request"])
        with self.assertRaises(AccessDenied):
            self.ops.get_work_order(self.primary,work_ref="unit2-request")

    def test_new_lease_same_subject_does_not_reopen_private_history_from_old_lease(self):
        self.ops.submit_maintenance(
            self.primary,work_ref="old-lease-job",
            intake=MaintenanceIntake(
                "p1","u1","plumbing","Private old-lease issue",False,"contact_first",
            ),
        )
        self.ops.end_lease(
            self.manager,property_ref="p1",lease_ref="l1",expected_revision=1,
        )
        # TEST FIXTURE ONLY: stand in for completed, certified turnover. Production
        # must use exact proof-gated GroundsStewardship turnover before ready.
        with self.ops.store.transaction(write=True) as db:
            db.execute("UPDATE units SET lifecycle='ready' WHERE unit_ref='u1' AND property_ref='p1'")
        self.ops.activate_lease(
            self.manager,property_ref="p1",unit_ref="u1",lease_ref="l-next",
            resident_ref="person1",start_on="2028-01-01",end_on="2028-12-31",
        )
        self.assertEqual(self.ops.list_work_orders(self.primary,property_ref="p1"),[])
        self.assertEqual(self.ops.resident_home(
            self.primary,property_ref="p1",unit_ref="u1",
        )["maintenance"],[])
        with self.assertRaises(AccessDenied):
            self.ops.get_work_order(self.primary,work_ref="old-lease-job")

    def test_ending_lease_invalidates_every_member(self):
        self._add()
        self.ops.end_lease(self.manager,property_ref="p1",lease_ref="l1",expected_revision=1)
        for actor in (self.primary,self.co):
            with self.assertRaises(AccessDenied):
                self.ops.resident_home(actor,property_ref="p1",unit_ref="u1")
        history=self.household.history(self.manager,property_ref="p1",lease_ref="l1")
        self.assertEqual([x["action"] for x in history].count("lease_ended"),2)
        with self.assertRaises(AccessDenied):
            self._add(subject="person3",proof="different")


if __name__=="__main__":
    unittest.main()
