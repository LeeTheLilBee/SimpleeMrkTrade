# =============================================================================
# THE_TOWER_FOUNDATION_PACK_013_TEST
# FILE: tower/test_tower_pack_013.py
# =============================================================================

import json

from tower.admin_action_gate import (
    list_admin_actions,
    mark_admin_action_executed,
    request_admin_action,
    revoke_admin_action,
    verify_admin_action,
    get_admin_action_summary,
)
from tower.step_up import approve_step_up_challenge
from tower.tower_seed import seed_tower_users
from tower.tower_status import get_tower_status


def pretty(title, payload):
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)
    print(json.dumps(payload, indent=2, sort_keys=True, default=str))


def run_tests():
    seed_tower_users()

    pretty(
        "BETA USER TRIES ADMIN ACTION",
        request_admin_action(
            actor_user_id="beta_001",
            admin_action="change_permissions",
            target_user_id="locked_001",
            target_app="tower_admin",
            object_type="tower_user",
            object_id="locked_001",
            requested_changes={"app_access.observatory": "allowed"},
            reason="pack_013_beta_should_not_admin",
        ),
    )

    first = request_admin_action(
        actor_user_id="owner_solice",
        admin_action="change_permissions",
        target_user_id="beta_001",
        target_app="tower_admin",
        object_type="tower_user",
        object_id="beta_001",
        requested_changes={"can_export": True},
        reason="pack_013_owner_change_permissions_test",
    )

    pretty("OWNER CHANGE PERMISSIONS FIRST TRY SHOULD STEP-UP", first)

    challenge_id = first.get("decision", {}).get("metadata", {}).get("challenge_id")

    if challenge_id:
        pretty(
            "APPROVE ADMIN STEP-UP",
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
        object_id="beta_001",
        requested_changes={"can_export": True},
        reason="pack_013_owner_change_permissions_after_stepup",
    )

    pretty("OWNER CHANGE PERMISSIONS AFTER STEP-UP", second)

    action_id = second.get("admin_action_id")

    if action_id:
        pretty("VERIFY ADMIN ACTION", verify_admin_action(action_id))

        pretty(
            "MARK ADMIN ACTION EXECUTED",
            mark_admin_action_executed(
                admin_action_id=action_id,
                executed_by="owner_solice",
                execution_result={
                    "applied": True,
                    "note": "Pack 013 test only; no real user mutation applied here.",
                },
            ),
        )

        pretty("VERIFY EXECUTED ADMIN ACTION", verify_admin_action(action_id))

    critical = request_admin_action(
        actor_user_id="owner_solice",
        admin_action="approve_automated_mode",
        target_user_id="beta_001",
        target_app="observatory",
        object_type="mode_permission",
        object_id="live_automated",
        requested_changes={"live_automated": "requested"},
        reason="pack_013_critical_action_test",
    )

    pretty("OWNER CRITICAL ADMIN ACTION", critical)

    if critical.get("admin_action_id"):
        pretty(
            "REVOKE CRITICAL ADMIN ACTION PACKAGE",
            revoke_admin_action(
                admin_action_id=critical.get("admin_action_id"),
                revoked_by="owner_solice",
                reason="pack_013_test_revoke_critical_action",
            ),
        )

    pretty("ADMIN ACTION SUMMARY", get_admin_action_summary())

    pretty("RECENT ADMIN ACTIONS", list_admin_actions(limit=5))

    pretty("TOWER STATUS WITH ADMIN ACTIONS", get_tower_status())


if __name__ == "__main__":
    run_tests()
