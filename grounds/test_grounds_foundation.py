"""Source-only contract regressions; no real tenant data, payments or network."""
import unittest

from grounds.contract import (
    SYSTEM_BOUNDARIES, foundation_status, resident_home_contract, room_contract,
)
from grounds.maintenance import (
    MaintenanceIntake, WorkOrder, transition_work_order,
)


def sample_intake(**overrides):
    payload = dict(
        property_ref="property-example", unit_ref="unit-example",
        category="plumbing", description="Example fixture leak",
        emergency_flag=False, entry_permission="contact_first",
        photo_refs=("opaque-proof-reference",),
    )
    payload.update(overrides)
    return MaintenanceIntake(**payload)


class GroundsFoundationTests(unittest.TestCase):
    def test_truth_stays_source_only(self):
        truth = foundation_status()
        self.assertEqual(truth["mode"], "source_only")
        self.assertFalse(truth["real_tenant_data_connected"])
        self.assertFalse(truth["tenant_login_enabled"])
        self.assertFalse(truth["teller_connected"])
        self.assertFalse(truth["resident_rent_checkout_enabled"])
        self.assertFalse(truth["paid_infrastructure_provisioned"])
        self.assertTrue(truth["real_data_browser_ui_source_available"])
        self.assertTrue(truth["server_injected_tower_wsgi_api_source_available"])
        self.assertTrue(truth["postgresql_baseline_schema_source_available"])
        self.assertTrue(truth["postgresql_transaction_adapter_source_available"])
        self.assertFalse(truth["postgresql_hosted_connection_certified"])
        self.assertFalse(truth["real_tower_http_receiver_connected"])
        self.assertTrue(truth["verified_post_close_property_receiver_source_available"])
        self.assertTrue(truth["verified_teller_rent_runtime_source_available"])
        self.assertTrue(truth["verified_delivery_receipt_ledger_source_available"])
        self.assertTrue(truth["verified_urgent_human_escalation_receipt_source_available"])

    def test_resident_home_includes_rent_and_maintenance(self):
        home = resident_home_contract()
        self.assertIn("maintenance", home["sections"])
        self.assertIn("pay_rent_handoff", home["sections"])
        self.assertEqual(home["amount_due_and_invoice_source"], "teller")
        self.assertIsNone(home["actual_amount_due"])
        self.assertIsNone(home["checkout_url"])
        self.assertFalse(home["payment_execution_enabled"])

    def test_no_cross_domain_payment_claim(self):
        self.assertIn("ACH/card checkout", SYSTEM_BOUNDARIES["teller"])
        self.assertIn("unit", SYSTEM_BOUNDARIES["grounds"])
        self.assertIn("verified close", SYSTEM_BOUNDARIES["buybox"])

    def test_room_manifest_is_not_permission(self):
        role = room_contract("resident")
        self.assertFalse(role["permission_grant"])
        self.assertTrue(role["tower_authorization_required"])
        self.assertIn("rent_display", role["rooms"])
        with self.assertRaises(ValueError):
            room_contract("anyone")

    def test_intake_is_explicit_about_entry(self):
        self.assertEqual(sample_intake().entry_permission, "contact_first")
        with self.assertRaises(ValueError):
            sample_intake(entry_permission="always")
        with self.assertRaises(ValueError):
            sample_intake(unit_ref="")
        with self.assertRaises(ValueError):
            sample_intake(emergency_flag="yes")

    def test_maintenance_intake_bounded_and_bad_shapes_fail_closed(self):
        for bad in (
            {"property_ref":"p"*129},
            {"unit_ref":"u"*129},
            {"category":"c"*81},
            {"description":"d"*2001},
            {"description":"\u0000hidden"},
            {"entry_permission":[]},
            {"photo_refs":tuple("ref"+str(i) for i in range(9))},
            {"photo_refs":("x"*129,)},
            {"photo_refs":("okay",1)},
        ):
            with self.subTest(bad=str(bad)[:70]):
                with self.assertRaises(ValueError):
                    sample_intake(**bad)
        # Bounded multiline descriptions remain supported.
        self.assertEqual(sample_intake(description="Water dripping\\nNeed assistance").category,"plumbing")

    def test_work_order_begins_submitted(self):
        order = WorkOrder("wo-example", sample_intake())
        self.assertEqual(order.state, "submitted")

    def test_manager_triage_then_technician_work(self):
        order = WorkOrder("wo-example", sample_intake())
        for state in ("received", "under_review", "scheduled", "assigned"):
            order = transition_work_order(order, next_state=state, actor_role="property_manager")
        order = transition_work_order(order, next_state="in_progress", actor_role="maintenance_technician")
        order = transition_work_order(order, next_state="completed", actor_role="maintenance_technician")
        order = transition_work_order(order, next_state="confirmation", actor_role="property_manager")
        order = transition_work_order(order, next_state="closed", actor_role="property_manager")
        self.assertEqual(order.state, "closed")

    def test_resident_cannot_assign_or_complete(self):
        order = WorkOrder("wo-example", sample_intake())
        with self.assertRaises(ValueError):
            transition_work_order(order, next_state="received", actor_role="resident")
        with self.assertRaises(ValueError):
            transition_work_order(order, next_state="closed", actor_role="resident")

    def test_technician_cannot_close_without_review(self):
        order = WorkOrder("wo-example", sample_intake(), state="completed")
        with self.assertRaises(ValueError):
            transition_work_order(order, next_state="closed", actor_role="maintenance_technician")

    def test_reopen_routes_back_to_review(self):
        order = WorkOrder("wo-example", sample_intake(), state="closed")
        order = transition_work_order(order, next_state="reopened", actor_role="resident")
        order = transition_work_order(order, next_state="under_review", actor_role="maintenance_supervisor")
        self.assertEqual(order.state, "under_review")

    def test_reference_transition_does_not_mutate_original(self):
        before = WorkOrder("wo-example", sample_intake())
        after = transition_work_order(before, next_state="received", actor_role="property_manager")
        self.assertEqual(before.state, "submitted")
        self.assertEqual(after.state, "received")


if __name__ == "__main__":
    unittest.main()
