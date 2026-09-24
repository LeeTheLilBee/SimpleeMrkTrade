"""
TWR193 — Tower-owned Teller hosted persistence crossing contract.

This module contains configuration and protocol constants only.

It does not:
- authenticate a user,
- manufacture actor/business authority,
- expose signing secrets,
- execute payroll,
- move money,
- access Vault,
- authorize broker execution,
- authorize Manual Live or Live Auto.
"""

from __future__ import annotations

import os


TOWER_TELLER_EXCHANGE_V1 = (
    "tower-teller-exchange.v1"
)

TOWER_TELLER_EXCHANGE_V2 = (
    "tower-teller-exchange.v2"
)

TELLER_PERSISTENCE_TOKEN_VERSION = (
    "tpt1"
)

TELLER_PERSISTENCE_TOKEN_ISSUER = (
    "tower"
)

TELLER_PERSISTENCE_TOKEN_AUDIENCE = (
    "teller-persistence"
)

TELLER_TOWER_TOKEN_SECRET_ENV = (
    "TELLER_TOWER_TOKEN_SECRET"
)

TELLER_PERSISTENCE_MAX_LIFETIME_SECONDS = (
    600
)

TELLER_PERSISTENCE_DEFAULT_LIFETIME_SECONDS = (
    300
)

TELLER_PERSISTENCE_MINIMUM_SECRET_LENGTH = (
    32
)

TELLER_PERSISTENCE_ALLOWED_ROLES = frozenset({
    "employee",
    "manager",
    "owner",
})


def teller_persistence_contract_status():

    secret = str(
        os.environ.get(
            TELLER_TOWER_TOKEN_SECRET_ENV,
            "",
        )
        or ""
    )

    return {
        "contract_id":
            "teller-persistence-token-v1",

        "exchange_v1":
            TOWER_TELLER_EXCHANGE_V1,

        "exchange_v2":
            TOWER_TELLER_EXCHANGE_V2,

        "token_version":
            TELLER_PERSISTENCE_TOKEN_VERSION,

        "issuer":
            TELLER_PERSISTENCE_TOKEN_ISSUER,

        "audience":
            TELLER_PERSISTENCE_TOKEN_AUDIENCE,

        "max_lifetime_seconds":
            TELLER_PERSISTENCE_MAX_LIFETIME_SECONDS,

        "default_lifetime_seconds":
            TELLER_PERSISTENCE_DEFAULT_LIFETIME_SECONDS,

        "allowed_roles":
            sorted(
                TELLER_PERSISTENCE_ALLOWED_ROLES
            ),

        "signing_secret_configured":
            bool(
                len(secret)
                >=
                TELLER_PERSISTENCE_MINIMUM_SECRET_LENGTH
            ),

        "signing_secret_exposed":
            False,

        "database_credentials_exposed":
            False,

        "direct_vault_authority":
            False,

        "payroll_execution_authority":
            False,

        "payment_execution_authority":
            False,

        "broker_execution_authority":
            False,

        "manual_live_authority":
            False,

        "live_auto_authority":
            False,
    }
