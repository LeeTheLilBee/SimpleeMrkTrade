# =============================================================================
# THE_TOWER_FOUNDATION_PACK_001_TEST
# FILE: tower/test_tower_foundation.py
# =============================================================================

import json

from tower.clearance import request_clearance
from tower.permissions import (
    APP_OBSERVATORY,
    APP_TOWER_ADMIN,
    MODE_SURVEY,
    MODE_PAPER,
    MODE_LIVE_AUTOMATED,
)
from tower.models import TowerUser
from tower.audit import read_recent_audit_events


def pretty(title, payload):
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)
    print(json.dumps(payload, indent=2, sort_keys=True, default=str))


def run_tests():
    owner = TowerUser(
        user_id="owner_solice",
        email="bowdre.solice@gmail.com",
        display_name="Solice Bowdre",
        role="owner",
        account_type="owner",
        status="active",
        app_access={
            APP_OBSERVATORY: "allowed",
            APP_TOWER_ADMIN: "allowed",
        },
        consents={
            "paper_trading_disclosure": True,
            "live_trading_consent": True,
            "automated_trading_consent": True,
        },
        can_export=True,
    ).to_dict()

    beta_user_missing_paper = TowerUser(
        user_id="beta_001",
        email="beta@example.com",
        display_name="Beta Tester",
        role="user",
        account_type="beta_user",
        status="active",
        app_access={
            APP_OBSERVATORY: "allowed",
        },
        consents={},
        can_export=False,
    ).to_dict()

    locked_user = TowerUser(
        user_id="locked_001",
        email="locked@example.com",
        display_name="Locked User",
        role="user",
        account_type="beta_user",
        status="locked",
        app_access={
            APP_OBSERVATORY: "allowed",
        },
        consents={
            "paper_trading_disclosure": True,
        },
    ).to_dict()

    pretty(
        "OWNER ENTERS OBSERVATORY SURVEY MODE",
        request_clearance(
            user=owner,
            app_name=APP_OBSERVATORY,
            mode_name=MODE_SURVEY,
        ),
    )

    pretty(
        "BETA USER TRIES PAPER MODE WITHOUT DISCLOSURE",
        request_clearance(
            user=beta_user_missing_paper,
            app_name=APP_OBSERVATORY,
            mode_name=MODE_PAPER,
        ),
    )

    pretty(
        "BETA USER TRIES LIVE AUTOMATED",
        request_clearance(
            user=beta_user_missing_paper,
            app_name=APP_OBSERVATORY,
            mode_name=MODE_LIVE_AUTOMATED,
        ),
    )

    pretty(
        "LOCKED USER TRIES OBSERVATORY",
        request_clearance(
            user=locked_user,
            app_name=APP_OBSERVATORY,
            mode_name=MODE_SURVEY,
        ),
    )

    pretty(
        "OWNER TRIES TOWER ADMIN",
        request_clearance(
            user=owner,
            app_name=APP_TOWER_ADMIN,
            action="enter_admin",
        ),
    )

    pretty(
        "RECENT AUDIT RECEIPTS",
        read_recent_audit_events(limit=10),
    )


if __name__ == "__main__":
    run_tests()
