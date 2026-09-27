"""Tower source-only Grounds handoff regressions."""
import unittest

from tower.grounds_handoff_requirements_v1 import (
    CONTRACT_ID, DECISION_REQUIRED, ROOM_ROLES,
    get_grounds_requirements, grounds_readiness_review,
)


class TowerGroundsHandoffTests(unittest.TestCase):
    def test_resident_and_staff_not_owner_only(self):
        spec=get_grounds_requirements()
        self.assertEqual(spec["contract_id"],CONTRACT_ID)
        self.assertIn("resident",ROOM_ROLES)
        self.assertIn("vendor",ROOM_ROLES)
        self.assertIn("maintenance_technician",ROOM_ROLES)
        self.assertIn("owner",ROOM_ROLES)
        self.assertEqual(spec["separate_identity_contexts"],["resident","staff","owner"])
        self.assertFalse(spec["wire_protocol_authorized"])

    def test_default_deny_without_evidence(self):
        review=grounds_readiness_review()
        self.assertEqual(review["status"],"BLOCKED")
        self.assertFalse(review["launch_authorized"])
        self.assertEqual(set(review["missing_or_unverified"]),set(DECISION_REQUIRED))

    def test_boolean_truth_not_trust_external_evidence(self):
        review=grounds_readiness_review({
            **{item:False for item in DECISION_REQUIRED},
            "host_and_receiver_proof":"yes",
        })
        self.assertIn("host_and_receiver_proof",review["missing_or_unverified"])

    def test_complete_claim_never_unblocks_automatically(self):
        review=grounds_readiness_review({item:True for item in DECISION_REQUIRED})
        self.assertEqual(review["status"],"OWNER_SECURITY_REVIEW_REQUIRED")
        self.assertFalse(review["launch_authorized"])
        self.assertFalse(review["entitlement_granted"])
        self.assertFalse(review["token_issued"])

    def test_public_registry_remains_nonlaunchable(self):
        from tower.app_registry import TOWER_APP_REGISTRY, TOWER_ROUTE_REGISTRY
        grounds=next(app for app in TOWER_APP_REGISTRY if app.app_id=="grounds")
        self.assertEqual(grounds.app_status,"registered_future_room")
        self.assertEqual(grounds.tower_launch_route,"/tower/app-registry")
        self.assertFalse(any(route.app_id=="grounds" for route in TOWER_ROUTE_REGISTRY))
        self.assertFalse(get_grounds_requirements()["route_registered"])

    def test_checklist_is_copy_safe(self):
        copy=get_grounds_requirements()
        copy["roles"].clear()
        self.assertIn("resident",get_grounds_requirements()["roles"])


if __name__=="__main__":
    unittest.main()
