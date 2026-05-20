# =============================================================================
# THE_TOWER_FOUNDATION_PACK_009_TEST
# FILE: tower/test_tower_pack_009.py
# =============================================================================

import json

from tower.policy_engine import evaluate_policy
from tower.permissions import MODE_LIVE_AUTOMATED, MODE_PAPER, MODE_SURVEY
from tower.tower_seed import seed_tower_users
from tower.user_store import get_user, set_consent


def pretty(title, payload):
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)
    print(json.dumps(payload, indent=2, sort_keys=True, default=str))


def run_tests():
    seed_tower_users()

    owner = get_user("owner_solice")
    beta = get_user("beta_001")
    locked = get_user("locked_001")

    pretty(
        "BETA SURVEY POLICY",
        evaluate_policy(
            user=beta,
            app_name="observatory",
            mode_name=MODE_SURVEY,
        ).to_dict(),
    )

    pretty(
        "BETA PAPER POLICY BEFORE DISCLOSURE",
        evaluate_policy(
            user=beta,
            app_name="observatory",
            mode_name=MODE_PAPER,
        ).to_dict(),
    )

    set_consent(
        user_id="beta_001",
        consent_key="paper_trading_disclosure",
        accepted=True,
        actor_user_id="owner_solice",
        reason="pack_009_policy_test_paper_consent",
    )

    beta_after = get_user("beta_001")

    pretty(
        "BETA PAPER POLICY AFTER DISCLOSURE",
        evaluate_policy(
            user=beta_after,
            app_name="observatory",
            mode_name=MODE_PAPER,
        ).to_dict(),
    )

    pretty(
        "BETA LIVE AUTOMATED POLICY",
        evaluate_policy(
            user=beta_after,
            app_name="observatory",
            mode_name=MODE_LIVE_AUTOMATED,
        ).to_dict(),
    )

    pretty(
        "LOCKED USER POLICY",
        evaluate_policy(
            user=locked,
            app_name="observatory",
            mode_name=MODE_SURVEY,
        ).to_dict(),
    )

    pretty(
        "HIGH SESSION RISK POLICY",
        evaluate_policy(
            user=beta_after,
            app_name="observatory",
            mode_name=MODE_PAPER,
            context={
                "session_risk": {
                    "risk_score": 85,
                    "risk_state": "step_up_required",
                    "risk_reasons": ["device_not_trusted", "failed_attempts"],
                }
            },
        ).to_dict(),
    )

    pretty(
        "OWNER EXPORT POLICY",
        evaluate_policy(
            user=owner,
            app_name="observatory",
            action="export",
            object_type="analysis_export",
            object_id="policy_export_001",
        ).to_dict(),
    )


if __name__ == "__main__":
    run_tests()
