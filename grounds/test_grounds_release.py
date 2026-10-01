"""GRD078: no self-reported source checklist can open the tenant release gate."""
import unittest

from grounds.release import (
    RELEASE_REQUIREMENTS, review_live_requirements, source_completion_status,
)


class ReleaseBoundaryTests(unittest.TestCase):
    def test_truthful_fictional_walkthrough_status(self):
        report=source_completion_status()
        self.assertEqual(report["role_contract_count"],13)
        self.assertTrue(report["fictional_browser_preview"])
        self.assertTrue(report["real_data_web_source_available"])
        self.assertTrue(report["tower_guarded_wsgi_source_available"])
        self.assertTrue(report["postgres_schema_and_adapter_source_available"])
        self.assertTrue(report["real_postgres_ci_workflow_available"])
        self.assertTrue(report["real_postgres_ci_result_must_be_checked_externally"])
        self.assertTrue(report["retry_safe_work_and_appointment_source_available"])
        self.assertTrue(report["combined_real_postgres_operational_and_tower_gate_regression_source_available"])
        self.assertFalse(report["external_owner_walkthrough_signed_off"])
        self.assertTrue(report["verified_post_close_property_receiver_source_available"])
        self.assertTrue(report["verified_delivery_receipt_ledger_source_available"])
        self.assertFalse(report["certified_external_post_close_or_delivery_provider_connected"])
        self.assertFalse(report["tower_staff_directory_and_assignment_receiver_certified"])
        self.assertIn("--fictional-only",report["developer_demo_command"])
        self.assertFalse(report["live_tenant_release_authorized"])
        self.assertFalse(report["actual_resident_sessions_enabled"])
        self.assertFalse(report["tower_receiver_certified"])
        self.assertFalse(report["checkout_enabled"])
        self.assertFalse(report["notifications_delivered"])
        self.assertTrue(report["latest_github_ci_must_be_confirmed_externally"])

    def test_even_every_self_reported_gate_cannot_auto_authorize(self):
        empty=review_live_requirements()
        self.assertEqual(len(empty["missing_or_unverified"]),len(RELEASE_REQUIREMENTS))
        all_claimed=review_live_requirements({
            name:True for name in RELEASE_REQUIREMENTS
        })
        self.assertEqual(all_claimed["missing_or_unverified"],[])
        self.assertEqual(len(all_claimed["self_reported_items"]),len(RELEASE_REQUIREMENTS))
        self.assertFalse(all_claimed["trusts_self_reported_evidence"])
        for field in (
            "runtime_unlocked","tenant_session_accepted",
            "real_money_movement_enabled","live_release_authorized",
            "provider_resources_created",
        ):
            self.assertFalse(all_claimed[field])

    def test_unknown_keys_and_falsey_claims_do_not_count(self):
        claims={"tower_identity_and_scopes":"yes",
                "private_storage_and_recovery":False,
                "fake_auto_approve":True}
        result=review_live_requirements(claims)
        self.assertEqual(result["self_reported_items"],[])
        self.assertIn("tower_identity_and_scopes",result["missing_or_unverified"])
        self.assertNotIn("fake_auto_approve",result["requirement_details"])
        cloned=review_live_requirements({x:True for x in RELEASE_REQUIREMENTS})
        cloned["requirement_details"].clear()
        self.assertEqual(len(RELEASE_REQUIREMENTS),8)


if __name__=="__main__":
    unittest.main()
