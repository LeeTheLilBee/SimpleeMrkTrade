# =============================================================================
# THE_TOWER_FOUNDATION_PACK_016_TEST
# FILE: tower/test_tower_pack_016.py
# =============================================================================

import json

from tower.security_events import create_security_event
from tower.security_inbox import (
    archive_test_noise,
    build_security_review_queue,
    bulk_update_group,
    get_security_inbox_summary,
    get_security_review_queue_summary,
    rebuild_security_inbox_dedupe,
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

    # Create repeated events so grouping has something obvious to group.
    for i in range(3):
        create_security_event(
            user_id="beta_001",
            event_type="pack_016_repeated_test_event",
            severity="high",
            source_app="tower_admin",
            description=f"Pack 016 repeated test event #{i + 1}.",
            recommended_action="review_pack_016_group",
            metadata={"pack": "016", "repeat": i + 1},
        )

    pretty("SYNC SECURITY INBOX", sync_security_inbox(limit_per_source=100))

    pretty("INBOX SUMMARY BEFORE CLEANUP", get_security_inbox_summary())

    pretty("REVIEW QUEUE SUMMARY BEFORE CLEANUP", get_security_review_queue_summary())

    queue = build_security_review_queue(include_resolved=False, limit_groups=10)
    pretty("TOP REVIEW GROUPS", queue)

    repeated_group = None
    for group in queue:
        if group.get("reason_code") == "pack_016_repeated_test_event":
            repeated_group = group
            break

    if repeated_group:
        pretty(
            "BULK RESOLVE REPEATED TEST GROUP",
            bulk_update_group(
                group_key=repeated_group.get("group_key"),
                status="resolved",
                actor_user_id="owner_solice",
                resolution_note="Pack 016 group resolution test.",
            ),
        )

    pretty("REBUILD INBOX DEDUPE", rebuild_security_inbox_dedupe())

    pretty("ARCHIVE TEST NOISE", archive_test_noise(actor_user_id="owner_solice"))

    pretty("INBOX SUMMARY AFTER CLEANUP", get_security_inbox_summary())

    pretty("REVIEW QUEUE SUMMARY AFTER CLEANUP", get_security_review_queue_summary())

    pretty("TOP REVIEW GROUPS AFTER CLEANUP", build_security_review_queue(include_resolved=False, limit_groups=10))

    pretty("TOWER STATUS WITH REVIEW QUEUE", get_tower_status())


if __name__ == "__main__":
    run_tests()
