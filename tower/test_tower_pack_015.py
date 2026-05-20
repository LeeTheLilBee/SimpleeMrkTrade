# =============================================================================
# THE_TOWER_FOUNDATION_PACK_015_TEST
# FILE: tower/test_tower_pack_015.py
# =============================================================================

import json

from tower.admin_action_gate import request_admin_action
from tower.export_vault import request_export
from tower.object_access import CLASS_USER_PRIVATE
from tower.security_events import create_security_event
from tower.security_inbox import (
    get_security_inbox_summary,
    list_inbox_items,
    sync_security_inbox,
    update_inbox_item_status,
    verify_inbox_item,
)
from tower.tower_seed import seed_tower_users
from tower.tower_status import get_tower_status
from tower.user_store import set_consent


def pretty(title, payload):
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)
    print(json.dumps(payload, indent=2, sort_keys=True, default=str))


def run_tests():
    seed_tower_users()

    set_consent(
        user_id="beta_001",
        consent_key="paper_trading_disclosure",
        accepted=True,
        actor_user_id="owner_solice",
        reason="pack_015_setup",
    )

    pretty(
        "CREATE MANUAL SECURITY EVENT",
        create_security_event(
            user_id="beta_001",
            event_type="pack_015_manual_review_event",
            severity="high",
            source_app="tower_admin",
            description="Pack 015 test security event needs review.",
            recommended_action="review_pack_015_event",
            metadata={"pack": "015"},
        ),
    )

    beta_record = {
        "object_id": "trade_beta_pack_015",
        "object_type": "trade_record",
        "app_name": "observatory",
        "classification": "user_private",
        "owner_user_id": "beta_001",
        "title": "Beta Export Test",
        "strategy_core": "secret",
    }

    beta_payload = {
        "object_type": "trade_record",
        "object_id": "trade_beta_pack_015",
        "app_name": "observatory",
        "classification": CLASS_USER_PRIVATE,
        "owner_user_id": "beta_001",
    }

    pretty(
        "CREATE DENIED EXPORT FOR INBOX",
        request_export(
            user_id="beta_001",
            app_name="observatory",
            object_type="trade_record",
            object_id="trade_beta_pack_015",
            record=beta_record,
            classification=CLASS_USER_PRIVATE,
            object_payload=beta_payload,
            export_reason="pack_015_denied_export_for_inbox",
        ),
    )

    pretty(
        "CREATE ADMIN ACTION STEP-UP FOR INBOX",
        request_admin_action(
            actor_user_id="owner_solice",
            admin_action="approve_automated_mode",
            target_user_id="beta_001",
            target_app="observatory",
            object_type="mode_permission",
            object_id="live_automated_pack_015",
            requested_changes={"live_automated": "requested"},
            reason="pack_015_admin_stepup_for_inbox",
        ),
    )

    pretty("SYNC SECURITY INBOX", sync_security_inbox(limit_per_source=80))

    summary = get_security_inbox_summary()
    pretty("SECURITY INBOX SUMMARY", summary)

    open_items = list_inbox_items(status="open", limit=10)
    pretty("OPEN SECURITY INBOX ITEMS", open_items)

    if open_items:
        first = open_items[0]
        inbox_item_id = first.get("inbox_item_id")

        pretty("VERIFY FIRST INBOX ITEM", verify_inbox_item(inbox_item_id))

        pretty(
            "MARK FIRST ITEM REVIEWING",
            update_inbox_item_status(
                inbox_item_id=inbox_item_id,
                status="reviewing",
                actor_user_id="owner_solice",
                resolution_note="Pack 015 test started review.",
            ),
        )

        pretty(
            "MARK FIRST ITEM RESOLVED",
            update_inbox_item_status(
                inbox_item_id=inbox_item_id,
                status="resolved",
                actor_user_id="owner_solice",
                resolution_note="Pack 015 test resolved this inbox item.",
            ),
        )

        pretty("VERIFY FIRST ITEM AFTER RESOLVE", verify_inbox_item(inbox_item_id))

    pretty("SECURITY INBOX SUMMARY AFTER REVIEW", get_security_inbox_summary())

    pretty("TOWER STATUS WITH SECURITY INBOX", get_tower_status())


if __name__ == "__main__":
    run_tests()
