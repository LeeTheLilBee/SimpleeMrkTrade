# =============================================================================
# THE_TOWER_FOUNDATION_PACK_002_TEST
# FILE: tower/test_tower_pack_002.py
# =============================================================================

import json

from tower.audit import verify_audit_chain, get_audit_summary
from tower.security_events import (
    create_security_event,
    read_security_events,
    get_security_summary,
)


def pretty(title, payload):
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)
    print(json.dumps(payload, indent=2, sort_keys=True, default=str))


def run_tests():
    pretty("AUDIT CHAIN CHECK", verify_audit_chain())

    pretty("AUDIT SUMMARY", get_audit_summary())

    event = create_security_event(
        user_id="beta_001",
        event_type="manual_test_security_event",
        severity="medium",
        source_app="tower_admin",
        description="Manual test security event from Pack 002.",
        recommended_action="review_event",
        metadata={"pack": "002"},
    )

    pretty("CREATED SECURITY EVENT", event)

    pretty("RECENT SECURITY EVENTS", read_security_events(limit=10))

    pretty("SECURITY SUMMARY", get_security_summary())


if __name__ == "__main__":
    run_tests()
