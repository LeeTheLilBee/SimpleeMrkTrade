# =============================================================================
# THE_TOWER_FOUNDATION_PACK_014_TEST
# FILE: tower/test_tower_pack_014.py
# =============================================================================

import json

from tower.admin_action_gate import request_admin_action
from tower.step_up import (
    approve_step_up_challenge,
    cleanup_step_up_challenges,
    get_step_up_summary,
    list_step_up_challenges,
)
from tower.tower_seed import seed_tower_users
from tower.tower_status import get_tower_status


def pretty(title, payload):
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)
    print(json.dumps(payload, indent=2, sort_keys=True, default=str))


def run_tests():
    seed_tower_users()

    first = request_admin_action(
        actor_user_id="owner_solice",
        admin_action="change_permissions",
        target_user_id="beta_001",
        target_app="tower_admin",
        object_type="tower_user",
        object_id="beta_pack_014",
        requested_changes={"can_export": True},
        reason="pack_014_first_try_should_stepup",
    )

    pretty("FIRST TRY SHOULD STEP-UP", first)

    challenge_id = first.get("decision", {}).get("metadata", {}).get("challenge_id")

    if challenge_id:
        pretty(
            "APPROVE STEP-UP",
            approve_step_up_challenge(
                challenge_id=challenge_id,
                approved_by="owner_solice",
            ),
        )

    second = request_admin_action(
        actor_user_id="owner_solice",
        admin_action="change_permissions",
        target_user_id="beta_001",
        target_app="tower_admin",
        object_type="tower_user",
        object_id="beta_pack_014",
        requested_changes={"can_export": True},
        reason="pack_014_second_try_should_consume",
    )

    pretty("SECOND TRY SHOULD APPROVE AND CONSUME", second)

    third = request_admin_action(
        actor_user_id="owner_solice",
        admin_action="change_permissions",
        target_user_id="beta_001",
        target_app="tower_admin",
        object_type="tower_user",
        object_id="beta_pack_014",
        requested_changes={"can_export": True},
        reason="pack_014_third_try_should_need_new_stepup",
    )

    pretty("THIRD TRY SHOULD NEED NEW STEP-UP", third)

    pretty("STEP-UP SUMMARY", get_step_up_summary())

    pretty("RECENT STEP-UP CHALLENGES", list_step_up_challenges(limit=6))

    pretty("CLEANUP STEP-UP CHALLENGES", cleanup_step_up_challenges())

    pretty("TOWER STATUS WITH STEP-UP SUMMARY", get_tower_status())


if __name__ == "__main__":
    run_tests()
