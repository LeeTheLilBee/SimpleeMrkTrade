# =============================================================================
# THE_TOWER_FOUNDATION_PACK_006_TEST
# FILE: tower/test_tower_pack_006.py
# =============================================================================

import json

from tower.clearance_service import check_user_clearance
from tower.object_access import (
    CLASS_ADMIN_ONLY,
    CLASS_PUBLIC,
    CLASS_RESTRICTED,
    CLASS_TRUST_INTERNAL,
    CLASS_USER_PRIVATE,
    OBJECT_ARCHIVE_FILE,
    OBJECT_TRADE_RECORD,
    evaluate_object_access,
)
from tower.tower_seed import seed_tower_users
from tower.user_store import get_user


def pretty(title, payload):
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)
    print(json.dumps(payload, indent=2, sort_keys=True, default=str))


def run_tests():
    seed_tower_users()

    owner = get_user("owner_solice")
    beta = get_user("beta_001")
    locked = get_user("locked_001")

    public_obj = {
        "object_type": OBJECT_ARCHIVE_FILE,
        "object_id": "public_file_001",
        "app_name": "archive_vault",
        "classification": CLASS_PUBLIC,
        "owner_user_id": None,
    }

    beta_private_trade = {
        "object_type": OBJECT_TRADE_RECORD,
        "object_id": "trade_beta_001",
        "app_name": "observatory",
        "classification": CLASS_USER_PRIVATE,
        "owner_user_id": "beta_001",
    }

    other_private_trade = {
        "object_type": OBJECT_TRADE_RECORD,
        "object_id": "trade_other_001",
        "app_name": "observatory",
        "classification": CLASS_USER_PRIVATE,
        "owner_user_id": "someone_else",
    }

    admin_obj = {
        "object_type": "security_event",
        "object_id": "security_event_001",
        "app_name": "tower_admin",
        "classification": CLASS_ADMIN_ONLY,
        "allowed_roles": ["owner", "admin"],
    }

    trust_obj = {
        "object_type": "trust_record",
        "object_id": "trust_record_001",
        "app_name": "archive_vault",
        "classification": CLASS_TRUST_INTERNAL,
        "allowed_account_types": ["owner", "trust", "internal"],
    }

    restricted_obj = {
        "object_type": OBJECT_ARCHIVE_FILE,
        "object_id": "restricted_file_001",
        "app_name": "archive_vault",
        "classification": CLASS_RESTRICTED,
    }

    pretty(
        "BETA VIEWS PUBLIC OBJECT",
        evaluate_object_access(beta, public_obj, action="view").to_dict(),
    )

    pretty(
        "BETA VIEWS OWN PRIVATE TRADE",
        evaluate_object_access(beta, beta_private_trade, action="view").to_dict(),
    )

    pretty(
        "BETA VIEWS SOMEONE ELSE PRIVATE TRADE",
        evaluate_object_access(beta, other_private_trade, action="view").to_dict(),
    )

    pretty(
        "OWNER VIEWS ADMIN OBJECT",
        evaluate_object_access(owner, admin_obj, action="view").to_dict(),
    )

    pretty(
        "BETA VIEWS ADMIN OBJECT",
        evaluate_object_access(beta, admin_obj, action="view").to_dict(),
    )

    pretty(
        "OWNER VIEWS TRUST OBJECT",
        evaluate_object_access(owner, trust_obj, action="view").to_dict(),
    )

    pretty(
        "BETA VIEWS TRUST OBJECT",
        evaluate_object_access(beta, trust_obj, action="view").to_dict(),
    )

    pretty(
        "LOCKED USER VIEWS PUBLIC OBJECT",
        evaluate_object_access(locked, public_obj, action="view").to_dict(),
    )

    pretty(
        "BETA VIEWS RESTRICTED OBJECT DEFAULT DENY",
        evaluate_object_access(beta, restricted_obj, action="view").to_dict(),
    )

    pretty(
        "CLEARANCE SERVICE WITH OBJECT PAYLOAD DENIES WRONG PRIVATE TRADE",
        check_user_clearance(
            user_id="beta_001",
            app_name="observatory",
            action="view",
            object_type=OBJECT_TRADE_RECORD,
            object_id="trade_other_001",
            object_payload=other_private_trade,
        ),
    )


if __name__ == "__main__":
    run_tests()
