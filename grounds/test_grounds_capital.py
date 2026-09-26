"""GRD021: five-lane Teller financial source, floors, terms and expiry tests."""
import time
import unittest

from grounds.access import AccessDenied
from grounds.capital import LANES, verified_apartment_readiness
from grounds.test_grounds_operations import fixture_scope


def fixture_snapshot():
    now = int(time.time())
    lanes = {
        name: {
            "current_cents": 400000, "target_cents": 1000000,
            "hard_bottom_cents": 100000, "protected_cents": 100000,
            "committed_cents": 50000, "available_cents": 250000,
            "status": "watch", "allowed_use": "Teller-authorized use only",
            "next_action": "Review current scope and funding",
        } for name in LANES
    }
    return {
        "source":"teller","audience":"grounds","property_ref":"p1",
        "mission_ref":"apartment-mission","terms_digest":"digest-v1",
        "overall":"review","observed_at":now,"expires_at":now+120,
        "lanes":lanes,
    }


class CapitalReadinessTests(unittest.TestCase):
    def setUp(self):
        self.actor = fixture_scope("owner","owner",("p1",))
        self.snapshot = fixture_snapshot()
        # TEST ONLY: production requires authenticated Teller verifier.
        self.verifier = lambda document: document

    def view(self, snapshot=None, *, terms="digest-v1", actor=None, verifier=None):
        return verified_apartment_readiness(
            self.actor if actor is None else actor,
            self.snapshot if snapshot is None else snapshot,
            property_ref="p1", mission_ref="apartment-mission", terms_digest=terms,
            teller_verifier=self.verifier if verifier is None else verifier,
        )

    def test_exact_five_lanes_not_one_generic_account(self):
        view=self.view()
        self.assertEqual(set(view["lanes"]),set(LANES))
        self.assertFalse(view["money_movement_enabled"])
        self.assertFalse(view["ob_account_query_performed"])
        self.assertEqual(view["lanes"]["repair_capex"]["hard_bottom_cents"],100000)

    def test_change_of_deal_terms_requires_new_teller_snapshot(self):
        with self.assertRaises(AccessDenied):
            self.view(terms="digest-v2")

    def test_protected_floor_not_spendable(self):
        altered=fixture_snapshot()
        altered["lanes"]["repair_capex"]["available_cents"]=250001
        with self.assertRaises(AccessDenied):
            self.view(altered)

    def test_underfunded_lane_valid_but_cannot_claim_ready(self):
        altered=fixture_snapshot()
        lane=altered["lanes"]["operating_emergency"]
        lane.update(current_cents=50000,hard_bottom_cents=100000,
                    protected_cents=50000,committed_cents=0,available_cents=0,
                    status="blocked")
        self.assertEqual(self.view(altered)["lanes"]["operating_emergency"]["status"],"blocked")
        lane["status"]="ready"
        with self.assertRaises(AccessDenied):
            self.view(altered)

    def test_no_fabricated_source_or_outdated_view(self):
        altered=fixture_snapshot();altered["source"]="observatory"
        with self.assertRaises(AccessDenied):
            self.view(altered)
        altered=fixture_snapshot();altered["observed_at"]=int(time.time())-500
        altered["expires_at"]=int(time.time())-200
        with self.assertRaises(AccessDenied):
            self.view(altered)

    def test_scope_and_verifier_fail_closed(self):
        with self.assertRaises(AccessDenied):
            self.view(actor=fixture_scope("resident","resident",("p1",),("u1",)))
        with self.assertRaises(AccessDenied):
            verified_apartment_readiness(
                self.actor,self.snapshot,property_ref="p1",mission_ref="apartment-mission",
                terms_digest="digest-v1",teller_verifier=None,
            )

    def test_all_lanes_required_and_numbers_are_integral(self):
        altered=fixture_snapshot();del altered["lanes"]["closing_costs"]
        with self.assertRaises(AccessDenied):
            self.view(altered)
        altered=fixture_snapshot();altered["lanes"]["down_payment"]["current_cents"]=True
        with self.assertRaises(AccessDenied):
            self.view(altered)


if __name__=="__main__":
    unittest.main()
