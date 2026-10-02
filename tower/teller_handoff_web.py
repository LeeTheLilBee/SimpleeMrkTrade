"""
TWR189 + TWR196 — Tower -> Teller one-time handoff exchange.

v1:
    Historical access-only exchange. Preserved.

v2:
    Persistence-capable hosted bootstrap for sealed Teller
    TINT061–TINT070.

Both versions use the existing:

    POST /tower/teller/exchange

The persistence bearer appears only in a successful exact-origin
v2 JSON response. It is never placed in a URL, receipt, log, or
persistent browser storage by Tower.
"""

from __future__ import annotations

import hmac
import os

from flask import (
    Flask,
    jsonify,
    request,
)

from tower.owner_teller_handoff import (
    OwnerTellerHandoffError,
    consume_owner_teller_handoff,
)

from tower.teller_persistence_authority import (
    TellerPersistenceAuthorityError,
    resolve_owner_teller_persistence_authority,
)

from tower.teller_persistence_contract import (
    TOWER_TELLER_EXCHANGE_V1,
    TOWER_TELLER_EXCHANGE_V2,
    teller_persistence_contract_status,
)

from tower.teller_persistence_token import (
    TellerPersistenceTokenError,
    issue_teller_persistence_access_token,
)


TOWER_TELLER_EXCHANGE_PATH = (
    "/tower/teller/exchange"
)

TOWER_TELLER_EXCHANGE_ENDPOINT = (
    "tower_teller_handoff_exchange_twr189"
)

# Historical public symbol preserved for TWR189/TWR190 callers.
TOWER_TELLER_EXCHANGE_VERSION = (
    TOWER_TELLER_EXCHANGE_V1
)

TOWER_TELLER_EXCHANGE_VERSION_V2 = (
    TOWER_TELLER_EXCHANGE_V2
)

TOWER_TELLER_CLIENT_ID = (
    "the-teller"
)

TOWER_TELLER_ALLOWED_ORIGIN_ENV = (
    "TOWER_TELLER_ALLOWED_ORIGIN"
)

_SUPPORTED_EXCHANGE_VERSIONS = frozenset({
    TOWER_TELLER_EXCHANGE_V1,
    TOWER_TELLER_EXCHANGE_V2,
})


def _clean(
    value,
):
    return str(
        value
        if value is not None
        else ""
    ).strip()


def _origin():

    return _clean(
        request.headers.get(
            "Origin"
        )
    ).rstrip("/")


def _allowed_origin():

    return _clean(
        os.environ.get(
            TOWER_TELLER_ALLOWED_ORIGIN_ENV
        )
    ).rstrip("/")


def _origin_allowed(
    origin,
):

    if not origin:
        return True

    allowed = _allowed_origin()

    return bool(
        allowed
        and hmac.compare_digest(
            origin,
            allowed,
        )
    )


def _exact_v2_origin_allowed(
    origin,
):

    allowed = _allowed_origin()

    return bool(
        origin
        and allowed
        and hmac.compare_digest(
            origin,
            allowed,
        )
    )


def _respond(
    payload,
    status,
    origin,
):

    response = jsonify(
        payload
    )

    response.status_code = (
        status
    )

    response.headers[
        "Cache-Control"
    ] = "no-store"

    response.headers[
        "Pragma"
    ] = "no-cache"

    response.headers[
        "X-Content-Type-Options"
    ] = "nosniff"

    if (
        origin
        and _origin_allowed(
            origin
        )
    ):
        response.headers[
            "Access-Control-Allow-Origin"
        ] = origin

        response.headers[
            "Access-Control-Allow-Credentials"
        ] = "true"

        response.headers[
            "Access-Control-Allow-Methods"
        ] = "POST, OPTIONS"

        response.headers[
            "Access-Control-Allow-Headers"
        ] = "Accept, Content-Type"

        response.headers[
            "Vary"
        ] = "Origin"

    return response


def _deny(
    reason,
    status,
    origin,
    *,
    exchange_version=(
        TOWER_TELLER_EXCHANGE_V1
    ),
):

    return _respond(
        {
            "exchange_version":
                exchange_version,

            "access_verified":
                False,

            "status":
                "denied",

            "reason":
                reason,
        },
        status,
        origin,
    )


def _v1_response(
    receipt,
    origin,
):

    return _respond(
        {
            "exchange_version":
                TOWER_TELLER_EXCHANGE_V1,

            "access_verified":
                True,

            "app_id":
                receipt[
                    "app_id"
                ],

            "role":
                receipt[
                    "role"
                ],

            "target_path":
                receipt[
                    "target_path"
                ],

            "receipt_id":
                receipt[
                    "receipt_id"
                ],

            "expires_at_epoch":
                receipt[
                    "expires_at_epoch"
                ],

            "navigation_context":
                receipt[
                    "navigation_context"
                ],
        },
        200,
        origin,
    )


def _v2_response(
    receipt,
    origin,
):

    contract = (
        teller_persistence_contract_status()
    )

    if (
        contract.get(
            "signing_secret_configured"
        )
        is not True
    ):
        return _deny(
            "tower_teller_persistence_not_configured",
            503,
            origin,
            exchange_version=(
                TOWER_TELLER_EXCHANGE_V2
            ),
        )

    try:
        authority = (
            resolve_owner_teller_persistence_authority(
                receipt
            )
        )

        issued = (
            issue_teller_persistence_access_token(
                tower_session_id=(
                    authority[
                        "tower_session_id"
                    ]
                ),
                tower_receipt_id=(
                    authority[
                        "tower_receipt_id"
                    ]
                ),
                actor_id=(
                    authority[
                        "actor_id"
                    ]
                ),
                actor_role=(
                    authority[
                        "actor_role"
                    ]
                ),
                business_key=(
                    authority[
                        "business_key"
                    ]
                ),
                not_after_epoch=(
                    receipt[
                        "expires_at_epoch"
                    ]
                ),
            )
        )

    except (
        TellerPersistenceAuthorityError,
        TellerPersistenceTokenError,
    ):
        return _deny(
            "tower_teller_persistence_authority_denied",
            403,
            origin,
            exchange_version=(
                TOWER_TELLER_EXCHANGE_V2
            ),
        )

    # IMPORTANT:
    # Do not persist this token in the Tower receipt or handoff store.
    # It exists only in this response object/runtime call frame.
    persistence_access_token = (
        issued[
            "token"
        ]
    )

    token_claims = (
        issued[
            "claims"
        ]
    )

    return _respond(
        {
            "exchange_version":
                TOWER_TELLER_EXCHANGE_V2,

            "access_verified":
                True,

            "app_id":
                receipt[
                    "app_id"
                ],

            "role":
                authority[
                    "actor_role"
                ],

            "target_path":
                receipt[
                    "target_path"
                ],

            "receipt_id":
                authority[
                    "tower_receipt_id"
                ],

            # Runtime session expires with the shorter
            # persistence token, not the longer receipt.
            "expires_at_epoch":
                issued[
                    "expires_at_epoch"
                ],

            "navigation_context":
                receipt[
                    "navigation_context"
                ],

            "tower_session_id":
                authority[
                    "tower_session_id"
                ],

            "actor_id":
                authority[
                    "actor_id"
                ],

            "business_key":
                authority[
                    "business_key"
                ],

            "persistence_access_token":
                persistence_access_token,
        },
        200,
        origin,
    )


def teller_handoff_exchange_view():

    origin = _origin()

    if (
        origin
        and not _origin_allowed(
            origin
        )
    ):
        return _deny(
            "tower_teller_origin_denied",
            403,
            origin,
        )

    if (
        request.method
        == "OPTIONS"
    ):
        return _respond(
            {
                "exchange_version":
                    TOWER_TELLER_EXCHANGE_V1,

                "status":
                    "preflight_ok",
            },
            204,
            origin,
        )

    body = request.get_json(
        silent=True
    )

    if not isinstance(
        body,
        dict,
    ):
        return _deny(
            "tower_teller_exchange_request_invalid",
            400,
            origin,
        )

    requested_version = _clean(
        body.get(
            "exchange_version"
        )
    )

    if (
        requested_version
        not in
        _SUPPORTED_EXCHANGE_VERSIONS
    ):
        return _deny(
            "tower_teller_exchange_version_invalid",
            400,
            origin,
        )

    if (
        requested_version
        == TOWER_TELLER_EXCHANGE_V2
        and not _exact_v2_origin_allowed(
            origin
        )
    ):
        return _deny(
            "tower_teller_v2_origin_required",
            403,
            origin,
            exchange_version=(
                TOWER_TELLER_EXCHANGE_V2
            ),
        )

    if (
        body.get(
            "client"
        )
        != TOWER_TELLER_CLIENT_ID
    ):
        return _deny(
            "tower_teller_exchange_client_invalid",
            400,
            origin,
            exchange_version=(
                requested_version
            ),
        )

    code = _clean(
        body.get(
            "handoff_code"
        )
    )

    if not code:
        return _deny(
            "tower_teller_handoff_required",
            400,
            origin,
            exchange_version=(
                requested_version
            ),
        )

    # Fail before consuming the one-time handoff when the v2
    # signer itself is not configured.
    if (
        requested_version
        == TOWER_TELLER_EXCHANGE_V2
        and teller_persistence_contract_status()
            .get(
                "signing_secret_configured"
            )
            is not True
    ):
        return _deny(
            "tower_teller_persistence_not_configured",
            503,
            origin,
            exchange_version=(
                TOWER_TELLER_EXCHANGE_V2
            ),
        )

    try:
        receipt = (
            consume_owner_teller_handoff(
                code
            )
        )

    except OwnerTellerHandoffError:
        return _deny(
            "tower_teller_exchange_denied",
            403,
            origin,
            exchange_version=(
                requested_version
            ),
        )

    if (
        requested_version
        == TOWER_TELLER_EXCHANGE_V1
    ):
        return _v1_response(
            receipt,
            origin,
        )

    return _v2_response(
        receipt,
        origin,
    )


def register_teller_handoff_web(
    app: Flask,
):

    if (
        TOWER_TELLER_EXCHANGE_ENDPOINT
        in app.view_functions
    ):
        return

    app.add_url_rule(
        TOWER_TELLER_EXCHANGE_PATH,
        endpoint=(
            TOWER_TELLER_EXCHANGE_ENDPOINT
        ),
        view_func=(
            teller_handoff_exchange_view
        ),
        methods=[
            "POST",
            "OPTIONS",
        ],
    )
