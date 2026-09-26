"""GRD019: role-scoped leasing, verified evidence and preview regressions."""
import shutil
import subprocess
import tempfile
import time
import unittest
from html.parser import HTMLParser
from pathlib import Path

from grounds.access import AccessDenied
from grounds.evidence import GroundsWorkProof
from grounds.leasing import GroundsLeasing
from grounds.maintenance import MaintenanceIntake
from grounds.operations import GroundsConflict, GroundsOperations
from grounds.storage import GroundsStore
from grounds.test_grounds_operations import fixture_scope, intake


class LeasingAndProofTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        store = GroundsStore(Path(self.temp.name) / "grounds.sqlite3")
        store.initialize()
        self.ops = GroundsOperations(store)
        self.leasing = GroundsLeasing(store)
        self.proof = GroundsWorkProof(store)
        self.owner = fixture_scope("owner","owner",("p1","p2"))
        self.manager = fixture_scope("manager","property_manager",("p1",))
        self.leaser = fixture_scope("leaser","leasing_agent",("p1",))
        self.resident = fixture_scope("resident1","resident",("p1",),("u1",))
        self.tech = fixture_scope("tech1","maintenance_technician",("p1",),assignments=("w1",))
        self.outside = fixture_scope("outside","leasing_agent",("p2",))
        for prop in ("p1","p2"):
            self.ops.record_closed_property(
                self.owner, property_ref=prop, name="Fictional "+prop,
                close_evidence={"status":"verified_closed","property_ref":prop,
                                "proof_ref":"closed-"+prop,"owned_on":"2026-09-26"},
                close_verifier=lambda fixture: fixture,  # TEST ONLY
            )
        self.ops.add_building(self.manager,property_ref="p1",building_ref="b1",label="A")
        self.ops.add_unit(self.manager,property_ref="p1",building_ref="b1",unit_ref="u1",label="101")
        self.ops.activate_lease(self.manager,property_ref="p1",unit_ref="u1",lease_ref="l1",
                                resident_ref="resident1",start_on="2026-09-26",end_on="2027-09-25")
        self.ops.submit_maintenance(self.resident,work_ref="w1",intake=intake())

    def tearDown(self):
        self.temp.cleanup()

    def test_availability_excludes_resident_and_protected_lease(self):
        available = self.leasing.availability(self.leaser,property_ref="p1")
        self.assertEqual(available[0]["lifecycle"],"occupied")
        self.assertNotIn("resident_ref",available[0])
        self.assertNotIn("vault_proof_ref",available[0])
        with self.assertRaises(AccessDenied):
            self.leasing.availability(self.outside,property_ref="p1")
        with self.assertRaises(AccessDenied):
            self.leasing.availability(self.resident,property_ref="p1")

    def test_prospect_tour_and_version_boundaries(self):
        prospect = self.leasing.register_prospect(
            self.leaser,property_ref="p1",prospect_ref="pr1",
            contact_vault_ref="opaque-private-contact",desired_unit_ref="u1",
        )
        self.assertEqual(prospect["stage"],"new")
        with self.assertRaises(AccessDenied):
            self.leasing.prospect(self.outside,property_ref="p1",prospect_ref="pr1")
        with self.assertRaises(GroundsConflict):
            self.leasing.plan_tour(self.leaser,property_ref="p1",prospect_ref="pr1",
                                   tour_ref="tour1",unit_ref="u1",
                                   starts_at="2026-10-04T13:00:00-04:00",expected_revision=1)
        moved = self.leasing.move_stage(self.leaser,property_ref="p1",prospect_ref="pr1",
                                        next_stage="contacted",expected_revision=1)
        self.assertEqual(moved["revision"],2)
        planned = self.leasing.plan_tour(self.leaser,property_ref="p1",prospect_ref="pr1",
                                         tour_ref="tour1",unit_ref="u1",
                                         starts_at="2026-10-04T13:00:00-04:00",expected_revision=2)
        self.assertFalse(planned["notification_sent"])
        self.assertEqual(self.leasing.list_tours(self.manager,property_ref="p1")[0]["unit_ref"],"u1")
        with self.assertRaises(GroundsConflict):
            self.leasing.move_stage(self.leaser,property_ref="p1",prospect_ref="pr1",
                                    next_stage="application_received",expected_revision=2)
        with self.assertRaises(GroundsConflict):
            self.leasing.register_prospect(self.leaser,property_ref="p1",prospect_ref="pr1",
                                           contact_vault_ref="duplicate")

    def test_sealed_proof_identity_role_uniqueness_and_visibility(self):
        untrusted={"status":"verified_sealed","work_ref":"w1","proof_ref":"vault-proof-1"}
        with self.assertRaises(AccessDenied):
            self.proof.record(self.resident,work_ref="w1",kind="intake",
                              signed_proof=untrusted,proof_verifier=None)
        with self.assertRaises(AccessDenied):
            self.proof.record(self.resident,work_ref="w1",kind="before",
                              signed_proof=untrusted,proof_verifier=lambda x:x)
        with self.assertRaises(AccessDenied):
            self.proof.record(self.resident,work_ref="w1",kind="intake",
                              signed_proof={**untrusted,"work_ref":"other"},proof_verifier=lambda x:x)
        result=self.proof.record(self.resident,work_ref="w1",kind="intake",
                                 signed_proof=untrusted,proof_verifier=lambda x:x)  # TEST ONLY
        self.assertIsNone(result["content_url"])
        self.assertEqual(self.proof.list_refs(self.resident,work_ref="w1")[0]["kind"],"intake")
        with self.assertRaises(GroundsConflict):
            self.proof.record(self.resident,work_ref="w1",kind="intake",
                              signed_proof=untrusted,proof_verifier=lambda x:x)
        with self.assertRaises(AccessDenied):
            self.proof.list_refs(self.outside,work_ref="w1")
        with self.assertRaises(AccessDenied):
            self.proof.record(self.tech,work_ref="w1",kind="before",
                              signed_proof={**untrusted,"proof_ref":"vault-proof-2"},
                              proof_verifier=lambda x:x)  # not assigned yet

    def test_no_real_applicant_data_fields(self):
        keys=self.leasing.register_prospect(
            self.leaser,property_ref="p1",prospect_ref="pr2",
            contact_vault_ref="opaque-ref",
        )
        row=self.leasing.prospect(self.leaser,property_ref="p1",prospect_ref="pr2")
        self.assertNotIn("email",row)
        self.assertNotIn("social_security_number",row)
        self.assertNotIn("phone",row)
        self.assertEqual(row["contact_vault_ref"],"opaque-ref")


class InlineScripts(HTMLParser):
    def __init__(self):
        super().__init__()
        self.inside=False
        self.scripts=[]
        self.external=[]
    def handle_starttag(self,tag,attrs):
        if tag=="script":
            self.inside=True
            if dict(attrs).get("src"):
                self.external.append(dict(attrs)["src"])
    def handle_endtag(self,tag):
        if tag=="script":
            self.inside=False
    def handle_data(self,data):
        if self.inside:
            self.scripts.append(data)


class GroundsPreviewTests(unittest.TestCase):
    def test_preview_is_only_in_memory_with_disabled_payment(self):
        page=(Path(__file__).parent/"ui"/"preview.html").read_text(encoding="utf8")
        self.assertIn("LOCAL CONCEPT PREVIEW",page)
        self.assertIn("Pay Rent · not connected",page)
        self.assertIn("button class=\"button\" disabled",page)
        self.assertIn('data-role="resident"',page)
        self.assertIn('data-role="maintenance_technician"',page)
        self.assertIn('data-role="leasing_agent"',page)
        self.assertIn('data-role="property_manager"',page)
        self.assertIn('data-role="owner"',page)
        parser=InlineScripts();parser.feed(page)
        self.assertFalse(parser.external)
        script="\n".join(parser.scripts)
        self.assertNotIn("fetch(",script)
        self.assertNotIn("XMLHttpRequest",script)
        self.assertNotIn("localStorage",script)
        self.assertNotIn("sessionStorage",script)
        self.assertIn("render();",script)
        if not shutil.which("node"):
            self.skipTest("Node unavailable outside CI")
        with tempfile.TemporaryDirectory() as tmp:
            script_path=Path(tmp)/"grounds_preview.js"
            script_path.write_text(script,encoding="utf8")
            result=subprocess.run(["node","--check",str(script_path)],capture_output=True,text=True)
            self.assertEqual(result.returncode,0,result.stderr)


if __name__=="__main__":
    unittest.main()
