"""GRD203–205: synthetic minimal personal access ledger and same-unit denial."""
import tempfile
import unittest
from pathlib import Path

from grounds.access import AccessDenied
from grounds.operations import GroundsOperations
from grounds.privacy_log import GroundsResidentPrivacyLog
from grounds.storage import GroundsStore
from grounds.test_grounds_operations import fixture_scope


class PrivacyLogTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.store=GroundsStore(Path(self.tmp.name)/"fixture.sqlite3")
        self.store.initialize()
        self.ops=GroundsOperations(self.store)
        self.audit=GroundsResidentPrivacyLog(self.store)
        self.owner=fixture_scope("owner","owner",("p1",))
        self.manager=fixture_scope("manager","property_manager",("p1",))
        self.resident=fixture_scope("resident","resident",("p1",),("u1",))
        self.same_unit=fixture_scope("other","resident",("p1",),("u1",))
        self.ops.record_closed_property(
            self.owner,property_ref="p1",name="Synthetic",
            close_evidence={"status":"verified_closed","property_ref":"p1",
                            "proof_ref":"closed-p1","owned_on":"2026-09-26"},
            close_verifier=lambda x:x,
        )
        self.ops.add_building(self.manager,property_ref="p1",building_ref="b1",label="A")
        self.ops.add_unit(self.manager,property_ref="p1",building_ref="b1",unit_ref="u1",label="101")
        self.ops.activate_lease(self.manager,property_ref="p1",unit_ref="u1",
                                lease_ref="l1",resident_ref="resident",
                                start_on="2026-09-26",end_on="2027-09-25")

    def tearDown(self):
        self.tmp.cleanup()

    def test_same_current_lease_self_only_no_secrets_or_content(self):
        self.audit.record_read(
            self.resident,property_ref="p1",unit_ref="u1",
            resource_kind="my_home",resource_ref="u1",
        )
        history=self.audit.my_history(self.resident,property_ref="p1",unit_ref="u1")
        self.assertEqual(history["total_events_before_current_response"],1)
        self.assertEqual(history["events"][0]["resource_kind"],"my_home")
        self.assertNotIn("actor_ref",str(history))
        self.assertNotIn("session_ref",str(history))
        self.assertFalse(history["session_tokens_included"])
        self.assertFalse(history["ip_addresses_included"])
        self.assertFalse(history["document_or_message_contents_included"])
        self.assertFalse(history["staff_access_log_complete"])
        with self.assertRaises(AccessDenied):
            self.audit.my_history(self.same_unit,property_ref="p1",unit_ref="u1")
        with self.assertRaises(AccessDenied):
            self.audit.my_history(self.manager,property_ref="p1",unit_ref="u1")
        with self.assertRaises(AccessDenied):
            self.audit.record_read(
                self.same_unit,property_ref="p1",unit_ref="u1",
                resource_kind="rent",resource_ref="u1",
            )
        self.ops.end_lease(self.manager,property_ref="p1",lease_ref="l1",expected_revision=1)
        with self.assertRaises(AccessDenied):
            self.audit.my_history(self.resident,property_ref="p1",unit_ref="u1")
        with self.assertRaises(AccessDenied):
            self.audit.record_read(
                self.resident,property_ref="p1",unit_ref="u1",
                resource_kind="my_home",resource_ref="u1",
            )

    def test_unrecognized_audit_kind_is_not_client_controllable(self):
        with self.assertRaises(Exception):
            self.audit.record_read(
                self.resident,property_ref="p1",unit_ref="u1",
                resource_kind="payment_amount",resource_ref="secret",
            )


if __name__=="__main__":
    unittest.main()
