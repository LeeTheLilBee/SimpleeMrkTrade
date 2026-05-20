# =============================================================================
# THE_TOWER_FOUNDATION_PACK_017_TEST
# FILE: tower/test_tower_pack_017.py
# =============================================================================

import json

from tower.security_events import create_security_event
from tower.security_inbox import (
    INBOX_ACTION_ADD_NOTE,
    INBOX_ACTION_DISMISS,
    INBOX_ACTION_ESCALATE,
    INBOX_ACTION_REOPEN,
    INBOX_ACTION_REQUIRE_STEP_UP,
    INBOX_ACTION_RESOLVE,
    build_security_review_queue,
    get_security_inbox_action_summary,
    get_security_inbox_summary,
    list_available_inbox_actions,
    perform_inbox_group_action,
    perform_inbox_item_action,
    sync_security_inbox,
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

    # Create fresh events so this test has clean targets.
    create_security_event(
        user_id="beta_001",
        event_type="pack_017_review_action_test",
        severity="medium",
        source_app="tower_admin",
        description="Pack 017 review action test event.",
        recommended_action="review_pack_017_action",
        metadata={"pack": "017", "case": "single_item"},
    )

    create_security_event(
        user_id="beta_001",
        event_type="pack_017_group_action_test",
        severity="high",
        source_app="tower_admin",
        description="Pack 017 group action test event A.",
        recommended_action="review_pack_017_group",
        metadata={"pack": "017", "case": "group_a"},
    )

    create_security_event(
        user_id="beta_001",
        event_type="pack_017_group_action_test",
        severity="high",
        source_app="tower_admin",
        description="Pack 017 group action test event B.",
        recommended_action="review_pack_017_group",
        metadata={"pack": "017", "case": "group_b"},
    )

    pretty("AVAILABLE INBOX ACTIONS", list_available_inbox_actions())

    pretty("SYNC SECURITY INBOX", sync_security_inbox(limit_per_source=150))

    pretty("INBOX SUMMARY BEFORE ACTIONS", get_security_inbox_summary())

    queue = build_security_review_queue(include_resolved=False, limit_groups=50)
    pretty("REVIEW QUEUE BEFORE ACTIONS", queue[:8])

    single_item_id = None
    group_key = None

    for group in queue:
        if group.get("reason_code") == "pack_017_review_action_test":
            ids = group.get("sample_item_ids") or []
            if ids:
                single_item_id = ids[0]

        if group.get("reason_code") == "pack_017_group_action_test":
            group_key = group.get("group_key")

    if single_item_id:
        pretty(
            "ADD NOTE TO SINGLE ITEM",
            perform_inbox_item_action(
                inbox_item_id=single_item_id,
                action=INBOX_ACTION_ADD_NOTE,
                actor_user_id="owner_solice",
                note="Pack 017 note test.",
            ),
        )

        pretty(
            "ESCALATE SINGLE ITEM",
            perform_inbox_item_action(
                inbox_item_id=single_item_id,
                action=INBOX_ACTION_ESCALATE,
                actor_user_id="owner_solice",
                note="Pack 017 escalation test.",
            ),
        )

        pretty(
            "REOPEN SINGLE ITEM",
            perform_inbox_item_action(
                inbox_item_id=single_item_id,
                action=INBOX_ACTION_REOPEN,
                actor_user_id="owner_solice",
                note="Pack 017 reopen test.",
            ),
        )

        pretty(
            "RESOLVE SINGLE ITEM",
            perform_inbox_item_action(
                inbox_item_id=single_item_id,
                action=INBOX_ACTION_RESOLVE,
                actor_user_id="owner_solice",
                note="Pack 017 resolve test.",
            ),
        )

    if group_key:
        pretty(
            "REQUIRE STEP-UP FOR GROUP",
            perform_inbox_group_action(
                group_key=group_key,
                action=INBOX_ACTION_REQUIRE_STEP_UP,
                actor_user_id="owner_solice",
                note="Pack 017 group step-up test.",
            ),
        )

        pretty(
            "DISMISS GROUP AFTER STEP-UP TEST",
            perform_inbox_group_action(
                group_key=group_key,
                action=INBOX_ACTION_DISMISS,
                actor_user_id="owner_solice",
                note="Pack 017 group dismiss cleanup.",
            ),
        )

    pretty("INBOX ACTION SUMMARY", get_security_inbox_action_summary())

    pretty("INBOX SUMMARY AFTER ACTIONS", get_security_inbox_summary())

    pretty("REVIEW QUEUE AFTER ACTIONS", build_security_review_queue(include_resolved=False, limit_groups=10))

    pretty("TOWER STATUS WITH INBOX ACTIONS", get_tower_status())


if __name__ == "__main__":
    run_tests()
