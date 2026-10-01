"""GRD073: opt-in disposable Grounds scenario exercises real local domain wiring."""
import unittest

from grounds.dev_demo import main,run_fictional_demo


class DemoReadinessTests(unittest.TestCase):
    def test_full_fictional_workflow_passes_its_safety_gates(self):
        result=run_fictional_demo()
        self.assertEqual(result["mode"],"FICTIONAL_OFFLINE_DEVELOPER_DEMO_ONLY")
        self.assertTrue(all(result["checks"].values()),result["checks"])
        self.assertEqual(result["staff_status"]["resource_summary"]["net_material_items"],2)
        self.assertEqual(result["staff_status"]["resource_summary"]["net_labor_minutes"],25)
        self.assertEqual(result["owner_status"]["physical_counts"]["untriaged_urgent_work"],0)
        self.assertEqual(result["resident_status"]["appointment"],"accepted")
        self.assertFalse(result["checkout_enabled"])
        self.assertFalse(result["external_services_connected"])
        self.assertFalse(result["network_requests_sent"])
        self.assertFalse(result["file_persisted_after_exit"])
        self.assertFalse(result["production_identity_verification_performed"])
        self.assertFalse(result["emergency_dispatch_enabled"])
        self.assertFalse(result["notification_delivery_enabled"])

    def test_explicit_local_fictional_ack_required(self):
        with self.assertRaises(SystemExit) as error:
            main([])
        self.assertNotEqual(error.exception.code,0)


if __name__=="__main__":
    unittest.main()
