# =============================================================================
# THE_TOWER_FOUNDATION_PACK_004_TEST
# FILE: tower/test_tower_pack_004.py
# =============================================================================

import json

from tower.clearance_service import (
    check_export_clearance,
    check_ob_mode_clearance,
    check_tower_admin_clearance,
    check_user_clearance,
)
from tower.permissions import (
    MODE_LIVE_AUTOMATED,
    MODE_PAPER,
    MODE_SURVEY,
)
from tower.security_events import get_security_summary, read_security_events
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

    pretty(
        "OWNER ENTERS TOWER ADMIN THROUGH CLEARANCE SERVICE",
        check_tower_admin_clearance("owner_solice"),
    )

    pretty(
        "BETA ENTERS SURVEY MODE THROUGH CLEARANCE SERVICE",
        check_ob_mode_clearance("beta_001", MODE_SURVEY),
    )

    pretty(
        "BETA TRIES PAPER MODE BEFORE DISCLOSURE THROUGH CLEARANCE SERVICE",
        check_ob_mode_clearance("beta_001", MODE_PAPER),
    )

    set_consent(
        user_id="beta_001",
        consent_key="paper_trading_disclosure",
        accepted=True,
        actor_user_id="owner_solice",
        reason="pack_004_beta_paper_disclosure_test",
    )

    pretty(
        "BETA TRIES PAPER MODE AFTER DISCLOSURE THROUGH CLEARANCE SERVICE",
        check_ob_mode_clearance("beta_001", MODE_PAPER),
    )

    pretty(
        "BETA TRIES LIVE AUTOMATED THROUGH CLEARANCE SERVICE",
        check_ob_mode_clearance("beta_001", MODE_LIVE_AUTOMATED),
    )

    pretty(
        "MISSING USER TRIES OBSERVATORY",
        check_user_clearance(
            user_id="ghost_user_404",
            app_name="observatory",
            mode_name=MODE_SURVEY,
        ),
    )

    pretty(
        "BETA TRIES EXPORT",
        check_export_clearance(
            user_id="beta_001",
            app_name="observatory",
            object_type="analysis_export",
            object_id="export_test_001",
        ),
    )

    pretty(
        "SECURITY SUMMARY AFTER CLEARANCE SERVICE TESTS",
        get_security_summary(),
    )

    pretty(
        "RECENT SECURITY EVENTS",
        read_security_events(limit=15),
    )

    pretty(
        "TOWER STATUS SUMMARY",
        get_tower_status(),
    )


if __name__ == "__main__":
    run_tests()
