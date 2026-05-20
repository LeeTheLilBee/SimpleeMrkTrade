# =============================================================================
# THE_TOWER_FOUNDATION_PACK_008_TEST
# FILE: tower/test_tower_pack_008.py
# =============================================================================

import json

from tower.clearance_service import check_ob_mode_clearance
from tower.device_risk import (
    create_session,
    evaluate_session_risk,
    list_devices,
    list_sessions,
    update_session_risk,
)
from tower.permissions import MODE_PAPER
from tower.step_up import approve_step_up_challenge
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
        reason="pack_008_setup_paper_consent",
    )

    session = create_session(
        user_id="beta_001",
        user_agent="Pack008 Test Browser",
        ip_address="127.0.0.1",
        device_hint="colab_test_device",
        app_name="observatory",
        actor_user_id="tower_test",
    )

    pretty("CREATED SESSION", session)

    pretty(
        "BETA PAPER WITH NORMAL SESSION RISK",
        check_ob_mode_clearance(
            "beta_001",
            MODE_PAPER,
            context={
                "session_id": session.get("session_id"),
                "session_risk": {
                    "risk_score": session.get("risk_score"),
                    "risk_state": session.get("risk_state"),
                    "risk_reasons": session.get("risk_reasons"),
                },
            },
        ),
    )

    risky_session = update_session_risk(
        session_id=session.get("session_id"),
        failed_attempt_delta=7,
        actor_user_id="tower_test",
    )

    pretty("SESSION AFTER FAILED ATTEMPTS", risky_session)

    risky_decision = check_ob_mode_clearance(
        "beta_001",
        MODE_PAPER,
        context={
            "session_id": session.get("session_id"),
            "session_risk": {
                "risk_score": risky_session.get("risk_score"),
                "risk_state": risky_session.get("risk_state"),
                "risk_reasons": risky_session.get("risk_reasons"),
            },
        },
    )

    pretty("BETA PAPER WITH HIGH SESSION RISK", risky_decision)

    challenge_id = risky_decision.get("metadata", {}).get("challenge_id")

    if challenge_id:
        pretty(
            "APPROVE RISK STEP-UP",
            approve_step_up_challenge(
                challenge_id=challenge_id,
                approved_by="owner_solice",
            ),
        )

        pretty(
            "BETA PAPER AFTER RISK STEP-UP",
            check_ob_mode_clearance(
                "beta_001",
                MODE_PAPER,
                context={
                    "session_id": session.get("session_id"),
                    "session_risk": {
                        "risk_score": risky_session.get("risk_score"),
                        "risk_state": risky_session.get("risk_state"),
                        "risk_reasons": risky_session.get("risk_reasons"),
                    },
                },
            ),
        )

    quarantine_risk = evaluate_session_risk(
        user_id="beta_001",
        device_id=session.get("device_id"),
        device_trusted=False,
        new_device=True,
        failed_attempts=8,
        context={
            "sensitive_action": True,
            "rapid_denials": True,
        },
    )

    pretty("MANUAL QUARANTINE-LEVEL RISK", quarantine_risk)

    pretty(
        "BETA PAPER WITH QUARANTINE RISK",
        check_ob_mode_clearance(
            "beta_001",
            MODE_PAPER,
            context={
                "session_id": session.get("session_id"),
                "session_risk": quarantine_risk,
            },
        ),
    )

    pretty("RECENT DEVICES", list_devices(limit=5))
    pretty("RECENT SESSIONS", list_sessions(limit=5))


if __name__ == "__main__":
    run_tests()
