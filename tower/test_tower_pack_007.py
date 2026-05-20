# =============================================================================
# THE_TOWER_FOUNDATION_PACK_007_TEST
# FILE: tower/test_tower_pack_007.py
# =============================================================================

import json

from tower.clearance_service import check_ob_mode_clearance
from tower.clearance_tokens import (
    list_clearance_tokens,
    revoke_clearance_token,
    validate_clearance_token,
)
from tower.permissions import MODE_PAPER
from tower.tower_seed import seed_tower_users
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
        reason="pack_007_setup_paper_consent",
    )

    decision = check_ob_mode_clearance("beta_001", MODE_PAPER)

    pretty("BETA PAPER CLEARANCE WITH TOKEN", decision)

    token_id = decision.get("clearance_token", {}).get("token_id")

    pretty(
        "VALIDATE TOKEN CORRECTLY",
        validate_clearance_token(
            token_id=token_id,
            user_id="beta_001",
            app_name="observatory",
            action="enter_app",
            mode_name=MODE_PAPER,
        ),
    )

    pretty(
        "VALIDATE TOKEN AGAINST WRONG MODE",
        validate_clearance_token(
            token_id=token_id,
            user_id="beta_001",
            app_name="observatory",
            action="enter_app",
            mode_name="survey",
        ),
    )

    pretty(
        "REVOKE TOKEN",
        revoke_clearance_token(
            token_id=token_id,
            revoked_by="owner_solice",
            reason="pack_007_test_revoke_token",
        ),
    )

    pretty(
        "VALIDATE TOKEN AFTER REVOKE",
        validate_clearance_token(
            token_id=token_id,
            user_id="beta_001",
            app_name="observatory",
            action="enter_app",
            mode_name=MODE_PAPER,
        ),
    )

    pretty(
        "RECENT CLEARANCE TOKENS",
        list_clearance_tokens(limit=5),
    )


if __name__ == "__main__":
    run_tests()
