"""
TWR194 — Tower-side issuer for Teller's sealed tpt1 persistence token.

Exact token shape:

    tpt1.<base64url-json-payload>.<HMAC-SHA256-signature>

The payload property order intentionally mirrors the sealed Teller
normalizeClaims() implementation at:

    LeeTheLilBee/The-Teller
    fd430134295167c6ee10e8c2d27a59592fa5d353
    server/teller/transport/tellerPersistenceAccessToken.js
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import secrets
import time

from collections.abc import Mapping

from tower.teller_persistence_contract import (
    TELLER_PERSISTENCE_ALLOWED_ROLES,
    TELLER_PERSISTENCE_DEFAULT_LIFETIME_SECONDS,
    TELLER_PERSISTENCE_MAX_LIFETIME_SECONDS,
    TELLER_PERSISTENCE_MINIMUM_SECRET_LENGTH,
    TELLER_PERSISTENCE_TOKEN_AUDIENCE,
    TELLER_PERSISTENCE_TOKEN_ISSUER,
    TELLER_PERSISTENCE_TOKEN_VERSION,
    TELLER_TOWER_TOKEN_SECRET_ENV,
)


class TellerPersistenceTokenError(
    ValueError
):

    def __init__(
        self,
        code,
    ):
        self.code = str(
            code
            or
            "teller_persistence_token_error"
        )

        super().__init__(
            self.code
        )


def _clean(
    value,
):
    return str(
        value
        if value is not None
        else ""
    ).strip()


def _secret():

    secret = _clean(
        os.environ.get(
            TELLER_TOWER_TOKEN_SECRET_ENV
        )
    )

    if (
        len(secret)
        <
        TELLER_PERSISTENCE_MINIMUM_SECRET_LENGTH
    ):
        raise TellerPersistenceTokenError(
            "teller_persistence_signing_secret_not_configured"
        )

    return secret


def _base64url_encode(
    raw,
):

    return (
        base64
        .urlsafe_b64encode(
            raw
        )
        .decode(
            "ascii"
        )
        .rstrip("=")
    )


def _base64url_decode(
    value,
):

    text = _clean(
        value
    )

    padding = (
        "="
        * (
            (
                4
                - len(text) % 4
            )
            % 4
        )
    )

    try:
        return base64.urlsafe_b64decode(
            (
                text
                + padding
            ).encode(
                "ascii"
            )
        )

    except Exception as exc:
        raise TellerPersistenceTokenError(
            "teller_persistence_token_payload_encoding_invalid"
        ) from exc


def _normalize_claims(
    claims,
):

    if not isinstance(
        claims,
        Mapping,
    ):
        raise TellerPersistenceTokenError(
            "teller_persistence_claims_missing"
        )

    actor_role = _clean(
        claims.get(
            "actor_role"
        )
    ).lower()

    if (
        actor_role
        not in
        TELLER_PERSISTENCE_ALLOWED_ROLES
    ):
        raise TellerPersistenceTokenError(
            "teller_persistence_actor_role_invalid"
        )

    try:
        iat = int(
            claims.get(
                "iat"
            )
        )

        exp = int(
            claims.get(
                "exp"
            )
        )

    except (
        TypeError,
        ValueError,
    ) as exc:
        raise TellerPersistenceTokenError(
            "teller_persistence_timestamp_invalid"
        ) from exc

    # IMPORTANT:
    # Dict insertion order intentionally matches Teller JS.
    normalized = {
        "iss":
            _clean(
                claims.get(
                    "iss"
                )
            ),

        "aud":
            _clean(
                claims.get(
                    "aud"
                )
            ),

        "iat":
            iat,

        "exp":
            exp,

        "jti":
            _clean(
                claims.get(
                    "jti"
                )
            ),

        "tower_session_id":
            _clean(
                claims.get(
                    "tower_session_id"
                )
            ),

        "tower_receipt_id":
            _clean(
                claims.get(
                    "tower_receipt_id"
                )
            ),

        "actor_id":
            _clean(
                claims.get(
                    "actor_id"
                )
            ),

        "actor_role":
            actor_role,

        "business_key":
            _clean(
                claims.get(
                    "business_key"
                )
            ),
    }

    for required in (
        "iss",
        "aud",
        "jti",
        "tower_session_id",
        "tower_receipt_id",
        "actor_id",
        "actor_role",
        "business_key",
    ):
        if not normalized[
            required
        ]:
            raise TellerPersistenceTokenError(
                "teller_persistence_claim_missing_"
                + required
            )

    return normalized


def _payload_bytes(
    claims,
):

    normalized = (
        _normalize_claims(
            claims
        )
    )

    # Mirrors JSON.stringify(normalizedClaims):
    # compact separators,
    # insertion order,
    # UTF-8 JSON.
    return json.dumps(
        normalized,
        separators=(
            ",",
            ":",
        ),
        ensure_ascii=False,
        allow_nan=False,
    ).encode(
        "utf-8"
    )


def _signature(
    signing_input,
    secret,
):

    return _base64url_encode(
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


def issue_teller_persistence_access_token(
    *,
    tower_session_id,
    tower_receipt_id,
    actor_id,
    actor_role,
    business_key,
    now_epoch=None,
    lifetime_seconds=(
        TELLER_PERSISTENCE_DEFAULT_LIFETIME_SECONDS
    ),
    not_after_epoch=None,
):

    secret = _secret()

    now = int(
        time.time()
        if now_epoch is None
        else float(
            now_epoch
        )
    )

    try:
        requested_lifetime = int(
            lifetime_seconds
        )

    except (
        TypeError,
        ValueError,
    ) as exc:
        raise TellerPersistenceTokenError(
            "teller_persistence_token_lifetime_invalid"
        ) from exc

    if (
        requested_lifetime
        <= 0
        or requested_lifetime
        >
        TELLER_PERSISTENCE_MAX_LIFETIME_SECONDS
    ):
        raise TellerPersistenceTokenError(
            "teller_persistence_token_lifetime_invalid"
        )

    expires_at = (
        now
        + requested_lifetime
    )

    if (
        not_after_epoch
        is not None
    ):
        expires_at = min(
            expires_at,
            int(
                float(
                    not_after_epoch
                )
            ),
        )

    if (
        expires_at
        <= now
    ):
        raise TellerPersistenceTokenError(
            "teller_persistence_token_no_valid_lifetime"
        )

    claims = {
        "iss":
            TELLER_PERSISTENCE_TOKEN_ISSUER,

        "aud":
            TELLER_PERSISTENCE_TOKEN_AUDIENCE,

        "iat":
            now,

        "exp":
            expires_at,

        "jti":
            (
                "tpt1_"
                + secrets.token_urlsafe(
                    24
                )
            ),

        "tower_session_id":
            tower_session_id,

        "tower_receipt_id":
            tower_receipt_id,

        "actor_id":
            actor_id,

        "actor_role":
            actor_role,

        "business_key":
            business_key,
    }

    payload = _base64url_encode(
        _payload_bytes(
            claims
        )
    )

    signing_input = (
        TELLER_PERSISTENCE_TOKEN_VERSION
        + "."
        + payload
    )

    signature = _signature(
        signing_input,
        secret,
    )

    token = (
        signing_input
        + "."
        + signature
    )

    return {
        "token":
            token,

        "claims":
            _normalize_claims(
                claims
            ),

        "expires_at_epoch":
            expires_at,

        "secret_exposed":
            False,
    }


def verify_teller_persistence_access_token(
    token,
    *,
    now_epoch=None,
    expected_issuer=(
        TELLER_PERSISTENCE_TOKEN_ISSUER
    ),
    expected_audience=(
        TELLER_PERSISTENCE_TOKEN_AUDIENCE
    ),
    max_lifetime_seconds=(
        TELLER_PERSISTENCE_MAX_LIFETIME_SECONDS
    ),
):

    secret = _secret()

    raw = _clean(
        token
    )

    parts = raw.split(
        "."
    )

    if (
        len(parts)
        != 3
        or parts[0]
        !=
        TELLER_PERSISTENCE_TOKEN_VERSION
    ):
        raise TellerPersistenceTokenError(
            "teller_persistence_token_invalid"
        )

    version, payload, supplied_signature = (
        parts
    )

    signing_input = (
        version
        + "."
        + payload
    )

    expected_signature = (
        _signature(
            signing_input,
            secret,
        )
    )

    if not hmac.compare_digest(
        supplied_signature,
        expected_signature,
    ):
        raise TellerPersistenceTokenError(
            "teller_persistence_token_signature_invalid"
        )

    try:
        parsed = json.loads(
            _base64url_decode(
                payload
            ).decode(
                "utf-8"
            )
        )

    except TellerPersistenceTokenError:
        raise

    except Exception as exc:
        raise TellerPersistenceTokenError(
            "teller_persistence_token_payload_invalid"
        ) from exc

    claims = _normalize_claims(
        parsed
    )

    if (
        claims["iss"]
        != expected_issuer
    ):
        raise TellerPersistenceTokenError(
            "teller_persistence_token_issuer_mismatch"
        )

    if (
        claims["aud"]
        != expected_audience
    ):
        raise TellerPersistenceTokenError(
            "teller_persistence_token_audience_mismatch"
        )

    now = int(
        time.time()
        if now_epoch is None
        else float(
            now_epoch
        )
    )

    if (
        claims["exp"]
        <= now
    ):
        raise TellerPersistenceTokenError(
            "teller_persistence_token_expired"
        )

    if (
        claims["iat"]
        > now + 60
    ):
        raise TellerPersistenceTokenError(
            "teller_persistence_token_iat_invalid"
        )

    lifetime = (
        claims["exp"]
        - claims["iat"]
    )

    if (
        lifetime
        <= 0
        or lifetime
        >
        int(
            max_lifetime_seconds
        )
    ):
        raise TellerPersistenceTokenError(
            "teller_persistence_token_lifetime_invalid"
        )

    return claims
