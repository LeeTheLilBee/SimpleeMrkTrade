# =============================================================================
# THE TOWER — SEED USERS
# FILE: tower/tower_seed.py
# =============================================================================

from tower.user_store import upsert_user
from tower.permissions import (
    APP_OBSERVATORY,
    APP_ARCHIVE_VAULT,
    APP_SIMPLEEPAY,
    APP_TOWER_ADMIN,
)


def seed_tower_users():
    """
    Creates starter users for The Tower.

    Baby version:
    This puts the first names in The Tower address book.
    """

    owner = {
        "user_id": "owner_solice",
        "email": "bowdre.solice@gmail.com",
        "display_name": "Solice Bowdre",
        "role": "owner",
        "account_type": "owner",
        "status": "active",
        "app_access": {
            APP_OBSERVATORY: "allowed",
            APP_ARCHIVE_VAULT: "allowed",
            APP_SIMPLEEPAY: "allowed",
            APP_TOWER_ADMIN: "allowed",
        },
        "consents": {
            "paper_trading_disclosure": True,
            "live_trading_consent": True,
            "automated_trading_consent": True,
            "beta_confidentiality_terms": True,
            "terms_of_service": True,
            "privacy_policy": True,
        },
        "can_export": True,
        "trust_score": 95,
        "risk_state": "clear",
    }

    beta_user = {
        "user_id": "beta_001",
        "email": "beta@example.com",
        "display_name": "Beta Tester",
        "role": "user",
        "account_type": "beta_user",
        "status": "active",
        "app_access": {
            APP_OBSERVATORY: "allowed",
            APP_ARCHIVE_VAULT: "denied",
            APP_SIMPLEEPAY: "denied",
            APP_TOWER_ADMIN: "denied",
        },
        "consents": {
            "paper_trading_disclosure": False,
            "beta_confidentiality_terms": False,
            "terms_of_service": False,
            "privacy_policy": False,
        },
        "can_export": False,
        "trust_score": 70,
        "risk_state": "clear",
    }

    locked_user = {
        "user_id": "locked_001",
        "email": "locked@example.com",
        "display_name": "Locked User",
        "role": "user",
        "account_type": "beta_user",
        "status": "locked",
        "app_access": {
            APP_OBSERVATORY: "allowed",
            APP_ARCHIVE_VAULT: "denied",
            APP_SIMPLEEPAY: "denied",
            APP_TOWER_ADMIN: "denied",
        },
        "consents": {
            "paper_trading_disclosure": True,
        },
        "can_export": False,
        "trust_score": 10,
        "risk_state": "locked",
    }

    created = []
    for user in [owner, beta_user, locked_user]:
        created.append(
            upsert_user(
                user=user,
                actor_user_id="system_seed",
                reason="seed_tower_users",
                write_audit=True,
            )
        )

    return created


if __name__ == "__main__":
    users = seed_tower_users()
    print(f"Seeded {len(users)} Tower users.")
    for user in users:
        print(f"- {user.get('user_id')} | {user.get('email')} | {user.get('status')}")
