# =============================================================================
# THE_TOWER_FOUNDATION_PACK_010_TEST
# FILE: tower/test_tower_pack_010.py
# =============================================================================

import json

from tower.evidence_capsules import (
    close_evidence_capsule,
    create_evidence_capsule,
    get_evidence_summary,
    list_evidence_capsules,
    verify_evidence_capsule,
)
from tower.policy_engine import evaluate_policy
from tower.permissions import MODE_LIVE_AUTOMATED, MODE_PAPER
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

    beta = get_user("beta_001")

    policy_report = evaluate_policy(
        user=beta,
        app_name="observatory",
        mode_name=MODE_LIVE_AUTOMATED,
    ).to_dict()

    capsule = create_evidence_capsule(
        user=beta,
        app_name="observatory",
        action="enter_app",
        mode_name=MODE_LIVE_AUTOMATED,
        decision=policy_report,
        policy_report=policy_report,
        session_context={
            "session_id": "test_session_010",
            "risk_score": 15,
            "risk_state": "clear",
        },
        trigger="live_automated_denial_test",
        created_by="tower_test",
        notes="Pack 010 test capsule for blocked Live Automated.",
    )

    pretty("CREATED LIVE AUTOMATED DENIAL CAPSULE", capsule)

    pretty(
        "VERIFY CAPSULE",
        verify_evidence_capsule(capsule.get("capsule_id")),
    )

    pretty(
        "CLOSE CAPSULE",
        close_evidence_capsule(
            capsule_id=capsule.get("capsule_id"),
            closed_by="owner_solice",
            resolution="reviewed_test_capsule",
            notes="Reviewed during Pack 010 test.",
        ),
    )

    set_consent(
        user_id="beta_001",
        consent_key="paper_trading_disclosure",
        accepted=True,
        actor_user_id="owner_solice",
        reason="pack_010_setup_paper_consent",
    )

    beta_after = get_user("beta_001")

    allow_policy = evaluate_policy(
        user=beta_after,
        app_name="observatory",
        mode_name=MODE_PAPER,
    ).to_dict()

    allow_capsule = create_evidence_capsule(
        user=beta_after,
        app_name="observatory",
        action="enter_app",
        mode_name=MODE_PAPER,
        decision=allow_policy,
        policy_report=allow_policy,
        trigger="paper_mode_allow_test",
        created_by="tower_test",
        notes="Pack 010 test capsule for allowed Paper Mode.",
    )

    pretty("CREATED PAPER ALLOW CAPSULE", allow_capsule)

    pretty("EVIDENCE SUMMARY", get_evidence_summary())

    pretty("RECENT CAPSULES", list_evidence_capsules(limit=3))

    pretty("TOWER STATUS WITH EVIDENCE", get_tower_status())


if __name__ == "__main__":
    run_tests()
