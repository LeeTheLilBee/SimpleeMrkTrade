# =============================================================================
# THE_TOWER_FOUNDATION_PACK_005_TEST
# FILE: tower/test_tower_pack_005.py
# =============================================================================

import json

from tower.clearance_service import (
    check_export_clearance,
    check_ob_mode_clearance,
)
from tower.permissions import MODE_PAPER, MODE_SURVEY
from tower.security_state import (
    get_security_state,
    set_app_lockdown,
    set_global_lockdown,
    set_mode_lockdown,
)
from tower.step_up import approve_step_up_challenge
from tower.tower_seed import seed_tower_users
from tower.user_store import set_consent


def pretty(title, payload):
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)
    print(json.dumps(payload, indent=2, sort_keys=True, default=str))


def run_tests():
    seed_tower_users()

    # Make sure beta can pass normal paper rules for this test.
    set_consent(
        user_id="beta_001",
        consent_key="paper_trading_disclosure",
        accepted=True,
        actor_user_id="owner_solice",
        reason="pack_005_setup_paper_disclosure",
    )

    pretty("SECURITY STATE", get_security_state())

    pretty(
        "BETA PAPER MODE BEFORE LOCKDOWN",
        check_ob_mode_clearance("beta_001", MODE_PAPER),
    )

    set_mode_lockdown(
        mode_name=MODE_PAPER,
        enabled=True,
        actor_user_id="owner_solice",
        reason="pack_005_test_lock_paper_mode",
    )

    pretty(
        "BETA PAPER MODE DURING MODE LOCKDOWN",
        check_ob_mode_clearance("beta_001", MODE_PAPER),
    )

    set_mode_lockdown(
        mode_name=MODE_PAPER,
        enabled=False,
        actor_user_id="owner_solice",
        reason="pack_005_test_unlock_paper_mode",
    )

    pretty(
        "BETA PAPER MODE AFTER MODE UNLOCK",
        check_ob_mode_clearance("beta_001", MODE_PAPER),
    )

    set_app_lockdown(
        app_name="observatory",
        enabled=True,
        actor_user_id="owner_solice",
        reason="pack_005_test_lock_observatory",
    )

    pretty(
        "BETA SURVEY MODE DURING APP LOCKDOWN",
        check_ob_mode_clearance("beta_001", MODE_SURVEY),
    )

    set_app_lockdown(
        app_name="observatory",
        enabled=False,
        actor_user_id="owner_solice",
        reason="pack_005_test_unlock_observatory",
    )

    export_first = check_export_clearance(
        user_id="owner_solice",
        app_name="observatory",
        object_type="analysis_export",
        object_id="owner_export_001",
    )

    pretty("OWNER EXPORT FIRST TRY NEEDS STEP-UP", export_first)

    challenge_id = export_first.get("metadata", {}).get("challenge_id")

    if challenge_id:
        pretty(
            "APPROVE STEP-UP CHALLENGE",
            approve_step_up_challenge(
                challenge_id=challenge_id,
                approved_by="owner_solice",
            ),
        )

    pretty(
        "OWNER EXPORT AFTER STEP-UP APPROVED",
        check_export_clearance(
            user_id="owner_solice",
            app_name="observatory",
            object_type="analysis_export",
            object_id="owner_export_001",
        ),
    )

    set_global_lockdown(
        enabled=True,
        actor_user_id="owner_solice",
        reason="pack_005_test_global_lockdown",
    )

    pretty(
        "OWNER SURVEY DURING GLOBAL LOCKDOWN",
        check_ob_mode_clearance("owner_solice", MODE_SURVEY),
    )

    set_global_lockdown(
        enabled=False,
        actor_user_id="owner_solice",
        reason="pack_005_test_global_unlock",
    )

    pretty("SECURITY STATE AFTER TESTS", get_security_state())


if __name__ == "__main__":
    run_tests()
