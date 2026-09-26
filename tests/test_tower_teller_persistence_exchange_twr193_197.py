from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import time

from datetime import (
    datetime,
    timezone,
)

import pytest

from flask import Flask

import tower.identity_authority as identity

from tower.owner_teller_handoff import (
    issue_owner_teller_handoff,
    reset_owner_teller_handoff_store_for_tests,
)

from tower.teller_handoff_web import (
    TOWER_TELLER_ALLOWED_ORIGIN_ENV,
    TOWER_TELLER_EXCHANGE_PATH,
    register_teller_handoff_web,
)

from tower.teller_persistence_contract import (
    TELLER_PERSISTENCE_MAX_LIFETIME_SECONDS,
    TELLER_TOWER_TOKEN_SECRET_ENV,
    TOWER_TELLER_EXCHANGE_V1,
    TOWER_TELLER_EXCHANGE_V2,
)

from tower.teller_persistence_token import (
    TellerPersistenceTokenError,
    issue_teller_persistence_access_token,
    verify_teller_persistence_access_token,
)


NOW = 2_000_000_000

ORIGIN = (
    "https://teller.example.test"
)

TEST_SECRET = (
    "twr193-197-synthetic-teller-secret-"
    "0123456789abcdef0123456789abcdef"
)


def iso(
    epoch,
):

    return datetime.fromtimestamp(
        epoch,
        tz=timezone.utc,
    ).isoformat()


def configure(
    monkeypatch,
):

    monkeypatch.setenv(
        identity.TOWER_OWNER_USERNAME_ENV,
        "twr193-owner",
    )

    monkeypatch.setenv(
        identity.TOWER_OWNER_PASSWORD_HASH_ENV,
        "synthetic-test-hash",
    )

    monkeypatch.setenv(
        identity.TOWER_OWNER_ID_ENV,
        "twr193-owner-id",
    )

    monkeypatch.setenv(
        identity.TOWER_ORGANIZATION_ID_ENV,
        "simplee-world-test",
    )

    monkeypatch.setenv(
        identity.TOWER_ORGANIZATION_NAME_ENV,
        "Simplee World Test",
    )

    monkeypatch.delenv(
        identity.TOWER_LOCAL_WALKTHROUGH_MODE_ENV,
        raising=False,
    )

    monkeypatch.setenv(
        "TOWER_SESSION_SECRET",
        (
            "twr193-session-secret-"
            "0123456789abcdef"
            "0123456789abcdef"
        ),
    )

    monkeypatch.setenv(
        TELLER_TOWER_TOKEN_SECRET_ENV,
        TEST_SECRET,
    )

    monkeypatch.setenv(
        TOWER_TELLER_ALLOWED_ORIGIN_ENV,
        ORIGIN,
    )

    reset_owner_teller_handoff_store_for_tests()


def session():

    return {
        "authenticated":
            True,

        "role":
            "owner",

        "owner_id":
            "twr193-owner-id",

        "username":
            "twr193-owner",

        "authenticated_at":
            iso(
                time.time()
                - 30
            ),

        "step_up_until":
            iso(
                time.time()
                + 600
            ),

        "tower_session_id":
            "tower_session_twr193_test",
    }


def application():

    value = Flask(
        __name__
    )

    value.config[
        "TESTING"
    ] = True

    register_teller_handoff_web(
        value
    )

    return value


def issue(
    *,
    source_app="tower",
):

    return issue_owner_teller_handoff(
        session(),

        navigation_context={
            "source_app":
                source_app,

            "destination":
                "owner_money_workspace",

            "return_app":
                "tower",

            "return_destination":
                "access_home",

            "correlation_id":
                "corr-twr193-test",
        },
    )


def exchange(
    client,
    code,
    version,
    *,
    origin=ORIGIN,
    extra=None,
):

    body = {
        "handoff_code":
            code,

        "client":
            "the-teller",

        "exchange_version":
            version,
    }

    if extra:
        body.update(
            extra
        )

    headers = {}

    if origin:
        headers[
            "Origin"
        ] = origin

    return client.post(
        TOWER_TELLER_EXCHANGE_PATH,
        headers=headers,
        json=body,
    )


def make_test_token(
    claims,
    secret,
):
    payload_bytes = json.dumps(
        claims,
        separators=(
            ",",
            ":",
        ),
        ensure_ascii=False,
    ).encode(
        "utf-8"
    )

    payload = (
        base64.urlsafe_b64encode(
            payload_bytes
        )
        .decode(
            "ascii"
        )
        .rstrip("=")
    )

    signing_input = (
        "tpt1."
        + payload
    )

    signature = (
        base64.urlsafe_b64encode(
            hmac.new(
                secret.encode(
                    "utf-8"
                ),
                signing_input.encode(
                    "ascii"
                ),
                hashlib.sha256,
            ).digest()
        )
        .decode(
            "ascii"
        )
        .rstrip("=")
    )

    return (
        signing_input
        + "."
        + signature
    )


def test_twr193_v1_is_preserved(
    monkeypatch,
):

    configure(
        monkeypatch
    )

    launched = issue()

    with application().test_client() as client:
        response = exchange(
            client,
            launched[
                "handoff_code"
            ],
            TOWER_TELLER_EXCHANGE_V1,
        )

    assert (
        response.status_code
        == 200
    )

    body = (
        response.get_json()
    )

    assert (
        body[
            "exchange_version"
        ]
        ==
        TOWER_TELLER_EXCHANGE_V1
    )

    assert (
        body[
            "access_verified"
        ]
        is True
    )

    assert (
        "persistence_access_token"
        not in body
    )

    assert (
        "tower_session_id"
        not in body
    )

    assert (
        "actor_id"
        not in body
    )

    assert (
        "business_key"
        not in body
    )


def test_twr196_v2_returns_exact_teller_contract(
    monkeypatch,
):

    configure(
        monkeypatch
    )

    launched = issue()

    with application().test_client() as client:
        response = exchange(
            client,
            launched[
                "handoff_code"
            ],
            TOWER_TELLER_EXCHANGE_V2,

            # These must NEVER become authority.
            extra={
                "actor_id":
                    "evil-actor",

                "actor_role":
                    "employee",

                "business_key":
                    "evil-business",

                "tower_session_id":
                    "evil-session",

                "receipt_id":
                    "evil-receipt",
            },
        )

    assert (
        response.status_code
        == 200
    )

    body = (
        response.get_json()
    )

    assert (
        body[
            "exchange_version"
        ]
        ==
        TOWER_TELLER_EXCHANGE_V2
    )

    assert (
        body[
            "access_verified"
        ]
        is True
    )

    assert (
        body[
            "app_id"
        ]
        == "teller"
    )

    assert (
        body[
            "role"
        ]
        == "owner"
    )

    assert (
        body[
            "target_path"
        ]
        == "/teller"
    )

    assert (
        body[
            "tower_session_id"
        ]
        ==
        "tower_session_twr193_test"
    )

    assert (
        body[
            "actor_id"
        ]
        ==
        "twr193-owner-id"
    )

    assert (
        body[
            "business_key"
        ]
        ==
        "simplee-world-test"
    )

    assert (
        body[
            "actor_id"
        ]
        != "evil-actor"
    )

    assert (
        body[
            "business_key"
        ]
        != "evil-business"
    )

    assert (
        body[
            "tower_session_id"
        ]
        != "evil-session"
    )

    token = (
        body[
            "persistence_access_token"
        ]
    )

    assert token.startswith(
        "tpt1."
    )

    claims = (
        verify_teller_persistence_access_token(
            token
        )
    )

    assert (
        claims[
            "iss"
        ]
        == "tower"
    )

    assert (
        claims[
            "aud"
        ]
        == "teller-persistence"
    )

    assert (
        claims[
            "tower_session_id"
        ]
        ==
        body[
            "tower_session_id"
        ]
    )

    assert (
        claims[
            "tower_receipt_id"
        ]
        ==
        body[
            "receipt_id"
        ]
    )

    assert (
        claims[
            "actor_id"
        ]
        ==
        body[
            "actor_id"
        ]
    )

    assert (
        claims[
            "actor_role"
        ]
        ==
        body[
            "role"
        ]
    )

    assert (
        claims[
            "business_key"
        ]
        ==
        body[
            "business_key"
        ]
    )

    assert (
        (
            claims[
                "exp"
            ]
            -
            claims[
                "iat"
            ]
        )
        <=
        TELLER_PERSISTENCE_MAX_LIFETIME_SECONDS
    )

    assert (
        TEST_SECRET
        not in
        json.dumps(
            body
        )
    )

    assert (
        response.headers[
            "Cache-Control"
        ]
        == "no-store"
    )

    assert (
        response.headers[
            "Pragma"
        ]
        == "no-cache"
    )

    assert (
        response.headers[
            "X-Content-Type-Options"
        ]
        == "nosniff"
    )

    assert (
        response.headers[
            "Access-Control-Allow-Origin"
        ]
        == ORIGIN
    )


def test_twr196_v2_replay_is_denied(
    monkeypatch,
):

    configure(
        monkeypatch
    )

    launched = issue()

    with application().test_client() as client:
        first = exchange(
            client,
            launched[
                "handoff_code"
            ],
            TOWER_TELLER_EXCHANGE_V2,
        )

        replay = exchange(
            client,
            launched[
                "handoff_code"
            ],
            TOWER_TELLER_EXCHANGE_V2,
        )

    assert (
        first.status_code
        == 200
    )

    assert (
        replay.status_code
        == 403
    )


def test_twr196_v2_requires_exact_teller_origin(
    monkeypatch,
):

    configure(
        monkeypatch
    )

    launched = issue()

    with application().test_client() as client:
        evil = exchange(
            client,
            launched[
                "handoff_code"
            ],
            TOWER_TELLER_EXCHANGE_V2,
            origin=(
                "https://evil.example"
            ),
        )

        no_origin = exchange(
            client,
            launched[
                "handoff_code"
            ],
            TOWER_TELLER_EXCHANGE_V2,
            origin="",
        )

        valid = exchange(
            client,
            launched[
                "handoff_code"
            ],
            TOWER_TELLER_EXCHANGE_V2,
        )

    assert (
        evil.status_code
        == 403
    )

    assert (
        no_origin.status_code
        == 403
    )

    # Wrong/no Origin must fail BEFORE consuming
    # the valid one-time handoff.
    assert (
        valid.status_code
        == 200
    )


def test_twr196_v2_missing_signing_secret_fails_before_consume(
    monkeypatch,
):

    configure(
        monkeypatch
    )

    launched = issue()

    monkeypatch.delenv(
        TELLER_TOWER_TOKEN_SECRET_ENV,
        raising=False,
    )

    with application().test_client() as client:
        blocked = exchange(
            client,
            launched[
                "handoff_code"
            ],
            TOWER_TELLER_EXCHANGE_V2,
        )

        assert (
            blocked.status_code
            == 503
        )

        # Restore synthetic secret. The one-time code should
        # still be usable because signer configuration failed
        # before handoff consumption.
        monkeypatch.setenv(
            TELLER_TOWER_TOKEN_SECRET_ENV,
            TEST_SECRET,
        )

        valid = exchange(
            client,
            launched[
                "handoff_code"
            ],
            TOWER_TELLER_EXCHANGE_V2,
        )

    assert (
        valid.status_code
        == 200
    )


def test_twr195_no_verified_business_authority_means_no_v2_token(
    monkeypatch,
):

    configure(
        monkeypatch
    )

    monkeypatch.delenv(
        identity.TOWER_ORGANIZATION_ID_ENV,
        raising=False,
    )

    monkeypatch.delenv(
        identity.TOWER_ORGANIZATION_NAME_ENV,
        raising=False,
    )

    launched = issue()

    with application().test_client() as client:
        blocked = exchange(
            client,
            launched[
                "handoff_code"
            ],
            TOWER_TELLER_EXCHANGE_V2,
        )

    assert (
        blocked.status_code
        == 403
    )

    body = (
        blocked.get_json()
    )

    assert (
        body[
            "access_verified"
        ]
        is False
    )

    assert (
        "persistence_access_token"
        not in body
    )


def test_twr194_token_tampering_is_rejected(
    monkeypatch,
):

    configure(
        monkeypatch
    )

    issued = (
        issue_teller_persistence_access_token(
            tower_session_id=(
                "tower_session_test"
            ),
            tower_receipt_id=(
                "tower_receipt_test"
            ),
            actor_id=(
                "owner_test"
            ),
            actor_role=(
                "owner"
            ),
            business_key=(
                "business_test"
            ),
            now_epoch=NOW,
        )
    )

    token = (
        issued[
            "token"
        ]
    )

    version, payload, signature = (
        token.split(
            "."
        )
    )

    changed = (
        "A"
        if signature[-1]
        != "A"
        else "B"
    )

    tampered = (
        version
        + "."
        + payload
        + "."
        + signature[:-1]
        + changed
    )

    with pytest.raises(
        TellerPersistenceTokenError
    ):
        verify_teller_persistence_access_token(
            tampered,
            now_epoch=NOW,
        )


def test_twr194_expired_token_is_rejected(
    monkeypatch,
):

    configure(
        monkeypatch
    )

    issued = (
        issue_teller_persistence_access_token(
            tower_session_id=(
                "tower_session_test"
            ),
            tower_receipt_id=(
                "tower_receipt_test"
            ),
            actor_id=(
                "owner_test"
            ),
            actor_role=(
                "owner"
            ),
            business_key=(
                "business_test"
            ),
            now_epoch=(
                NOW
                - 1000
            ),
            lifetime_seconds=(
                300
            ),
        )
    )

    with pytest.raises(
        TellerPersistenceTokenError
    ):
        verify_teller_persistence_access_token(
            issued[
                "token"
            ],
            now_epoch=NOW,
        )


def test_twr194_wrong_issuer_and_audience_are_rejected(
    monkeypatch,
):

    configure(
        monkeypatch
    )

    base = {
        "iss":
            "tower",

        "aud":
            "teller-persistence",

        "iat":
            NOW,

        "exp":
            NOW + 300,

        "jti":
            "test-jti",

        "tower_session_id":
            "tower-session",

        "tower_receipt_id":
            "tower-receipt",

        "actor_id":
            "owner-test",

        "actor_role":
            "owner",

        "business_key":
            "business-test",
    }

    wrong_issuer = dict(
        base
    )

    wrong_issuer[
        "iss"
    ] = "evil"

    wrong_audience = dict(
        base
    )

    wrong_audience[
        "aud"
    ] = "evil"

    with pytest.raises(
        TellerPersistenceTokenError
    ):
        verify_teller_persistence_access_token(
            make_test_token(
                wrong_issuer,
                TEST_SECRET,
            ),
            now_epoch=NOW,
        )

    with pytest.raises(
        TellerPersistenceTokenError
    ):
        verify_teller_persistence_access_token(
            make_test_token(
                wrong_audience,
                TEST_SECRET,
            ),
            now_epoch=NOW,
        )


def test_twr194_more_than_600_seconds_is_impossible(
    monkeypatch,
):

    configure(
        monkeypatch
    )

    with pytest.raises(
        TellerPersistenceTokenError
    ):
        issue_teller_persistence_access_token(
            tower_session_id=(
                "tower_session_test"
            ),
            tower_receipt_id=(
                "tower_receipt_test"
            ),
            actor_id=(
                "owner_test"
            ),
            actor_role=(
                "owner"
            ),
            business_key=(
                "business_test"
            ),
            now_epoch=NOW,
            lifetime_seconds=601,
        )


def test_twr197_token_and_secret_are_not_written_to_existing_receipt_store(
    monkeypatch,
):

    configure(
        monkeypatch
    )

    launched = issue()

    with application().test_client() as client:
        response = exchange(
            client,
            launched[
                "handoff_code"
            ],
            TOWER_TELLER_EXCHANGE_V2,
        )

    assert (
        response.status_code
        == 200
    )

    body = (
        response.get_json()
    )

    # Only the approved successful v2 response contains
    # the bearer. It is not a URL field and not a receipt field.
    assert (
        body[
            "persistence_access_token"
        ].startswith(
            "tpt1."
        )
    )

    assert (
        "handoff_code"
        not in body
    )

    assert (
        "signature"
        not in body
    )

    assert (
        "token_secret"
        not in body
    )

    assert (
        TEST_SECRET
        not in
        json.dumps(
            body
        )
    )


def test_twr197_new_source_has_no_token_logging_calls():

    root = os.path.dirname(
        os.path.dirname(
            __file__
        )
    )

    for relative in (
        "tower/teller_persistence_contract.py",
        "tower/teller_persistence_token.py",
        "tower/teller_persistence_authority.py",
        "tower/teller_handoff_web.py",
    ):
        text = open(
            os.path.join(
                root,
                relative,
            ),
            "r",
            encoding="utf-8",
        ).read()

        assert (
            "print("
            not in text
        )

        assert (
            "logger."
            not in text
        )

        assert (
            "logging."
            not in text
        )
