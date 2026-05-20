# =============================================================================
# THE_TOWER_FOUNDATION_PACK_003_TEST
# FILE: tower/test_tower_pack_003.py
# =============================================================================

import json

from tower.clearance import request_clearance
from tower.permissions import APP_OBSERVATORY, APP_TOWER_ADMIN, MODE_PAPER, MODE_SURVEY
from tower.tower_seed import seed_tower_users
from tower.tower_status import get_tower_status
from tower.user_store import (
    get_user,
    list_users,
    set_consent,
)


def pretty(title, payload):
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)
    print(json.dumps(payload, indent=2, sort_keys=True, default=str))


def run_tests():
    seeded = seed_tower_users()
    pretty("SEEDED USERS", seeded)

    users = list_users()
    pretty("ALL TOWER USERS", users)

    owner = get_user("owner_solice")
    beta = get_user("beta_001")

    pretty(
        "OWNER ENTERS TOWER ADMIN",
        request_clearance(
            user=owner,
            app_name=APP_TOWER_ADMIN,
            action="enter_admin",
        ),
    )

    pretty(
        "BETA TRIES PAPER BEFORE DISCLOSURE",
        request_clearance(
            user=beta,
            app_name=APP_OBSERVATORY,
            mode_name=MODE_PAPER,
        ),
    )

    set_consent(
        user_id="beta_001",
        consent_key="paper_trading_disclosure",
        accepted=True,
        actor_user_id="owner_solice",
        reason="beta_completed_paper_disclosure_test",
    )

    beta_after = get_user("beta_001")

    pretty(
        "BETA TRIES PAPER AFTER DISCLOSURE",
        request_clearance(
            user=beta_after,
            app_name=APP_OBSERVATORY,
            mode_name=MODE_PAPER,
        ),
    )

    pretty(
        "TOWER STATUS SUMMARY",
        get_tower_status(),
    )


if __name__ == "__main__":
    run_tests()
