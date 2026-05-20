# =============================================================================
# THE_TOWER_FOUNDATION_PACK_012_TEST
# FILE: tower/test_tower_pack_012.py
# =============================================================================

import json

from tower.export_vault import (
    get_export_summary,
    list_exports,
    request_export,
    revoke_export,
    verify_export,
)
from tower.object_access import CLASS_CONFIDENTIAL, CLASS_USER_PRIVATE
from tower.step_up import approve_step_up_challenge
from tower.tower_seed import seed_tower_users
from tower.tower_status import get_tower_status
from tower.user_store import get_user, set_consent


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
        reason="pack_012_setup",
    )

    record = {
        "object_id": "trade_beta_export_001",
        "object_type": "trade_record",
        "app_name": "observatory",
        "classification": "user_private",
        "owner_user_id": "beta_001",
        "title": "Beta Trade Export",
        "symbol": "AAPL",
        "status": "paper",
        "email": "beta@example.com",
        "strategy_core": "secret internal strategy logic",
        "raw_signal_payload": {
            "internal_score": 91,
            "broker_token": "NOPE",
            "reason": "technical setup",
        },
        "public_summary": "Safe summary.",
    }

    object_payload = {
        "object_type": "trade_record",
        "object_id": "trade_beta_export_001",
        "app_name": "observatory",
        "classification": CLASS_USER_PRIVATE,
        "owner_user_id": "beta_001",
    }

    pretty(
        "BETA EXPORT FIRST TRY SHOULD NEED STEP-UP",
        request_export(
            user_id="beta_001",
            app_name="observatory",
            object_type="trade_record",
            object_id="trade_beta_export_001",
            record=record,
            classification=CLASS_USER_PRIVATE,
            object_payload=object_payload,
            export_reason="pack_012_beta_trade_export_test",
        ),
    )

    # Owner export is allowed because owner has can_export.
    owner_record = {
        "object_id": "owner_confidential_export_001",
        "object_type": "analysis_export",
        "app_name": "observatory",
        "classification": "confidential",
        "title": "Owner Analysis Export",
        "symbol": "TSLA",
        "strategy_core": "owner visible strategy core",
        "broker_token": "OWNER_SECRET_TOKEN",
        "public_summary": "Owner export summary.",
    }

    owner_payload = {
        "object_type": "analysis_export",
        "object_id": "owner_confidential_export_001",
        "app_name": "observatory",
        "classification": CLASS_CONFIDENTIAL,
        "allowed_roles": ["owner"],
    }

    owner_first = request_export(
        user_id="owner_solice",
        app_name="observatory",
        object_type="analysis_export",
        object_id="owner_confidential_export_001",
        record=owner_record,
        classification=CLASS_CONFIDENTIAL,
        object_payload=owner_payload,
        export_reason="pack_012_owner_export_test",
    )

    pretty("OWNER EXPORT FIRST TRY MAY NEED STEP-UP", owner_first)

    challenge_id = owner_first.get("decision", {}).get("metadata", {}).get("challenge_id")

    if challenge_id:
        pretty(
            "APPROVE OWNER EXPORT STEP-UP",
            approve_step_up_challenge(
                challenge_id=challenge_id,
                approved_by="owner_solice",
            ),
        )

        owner_second = request_export(
            user_id="owner_solice",
            app_name="observatory",
            object_type="analysis_export",
            object_id="owner_confidential_export_001",
            record=owner_record,
            classification=CLASS_CONFIDENTIAL,
            object_payload=owner_payload,
            export_reason="pack_012_owner_export_test_after_stepup",
        )

        pretty("OWNER EXPORT AFTER STEP-UP", owner_second)

        export_id = owner_second.get("export_id")
    else:
        export_id = owner_first.get("export_id")

    if export_id:
        pretty("VERIFY OWNER EXPORT", verify_export(export_id))

        pretty(
            "REVOKE OWNER EXPORT",
            revoke_export(
                export_id=export_id,
                revoked_by="owner_solice",
                reason="pack_012_test_revoke_export",
            ),
        )

        pretty("VERIFY OWNER EXPORT AFTER REVOKE", verify_export(export_id))

    pretty("EXPORT SUMMARY", get_export_summary())

    pretty("RECENT EXPORTS", list_exports(limit=5))

    pretty("TOWER STATUS WITH EXPORTS", get_tower_status())


if __name__ == "__main__":
    run_tests()
