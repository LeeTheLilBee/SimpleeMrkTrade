"""TWR189 — HTTP exchange for Tower -> Teller one-time handoffs."""

from __future__ import annotations

import hmac
import os

from flask import Flask, jsonify, request

from tower.owner_teller_handoff import (
    OwnerTellerHandoffError,
    consume_owner_teller_handoff,
)


TOWER_TELLER_EXCHANGE_PATH = (
    "/tower/teller/exchange"
)

TOWER_TELLER_EXCHANGE_ENDPOINT = (
    "tower_teller_handoff_exchange_twr189"
)

TOWER_TELLER_EXCHANGE_VERSION = (
    "tower-teller-exchange.v1"
)

TOWER_TELLER_CLIENT_ID = (
    "the-teller"
)

TOWER_TELLER_ALLOWED_ORIGIN_ENV = (
    "TOWER_TELLER_ALLOWED_ORIGIN"
)


def _clean(value):
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


def _origin_allowed(origin):

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


def _respond(
    payload,
    status,
    origin,
):

    response = jsonify(
        payload
    )

    response.status_code = status

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
):

    return _respond(
        {
            "exchange_version":
                TOWER_TELLER_EXCHANGE_VERSION,

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


def teller_handoff_exchange_view():

    origin = _origin()

    if not _origin_allowed(
        origin
    ):
        return _deny(
            "tower_teller_origin_denied",
            403,
            origin,
        )

    if request.method == "OPTIONS":
        return _respond(
            {
                "exchange_version":
                    TOWER_TELLER_EXCHANGE_VERSION,

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

    if (
        body.get("exchange_version")
        != TOWER_TELLER_EXCHANGE_VERSION
    ):
        return _deny(
            "tower_teller_exchange_version_invalid",
            400,
            origin,
        )

    if (
        body.get("client")
        != TOWER_TELLER_CLIENT_ID
    ):
        return _deny(
            "tower_teller_exchange_client_invalid",
            400,
            origin,
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
        )

    try:
        receipt = consume_owner_teller_handoff(
            code
        )

    except OwnerTellerHandoffError:

        return _deny(
            "tower_teller_exchange_denied",
            403,
            origin,
        )

    return _respond(
        {
            "exchange_version":
                TOWER_TELLER_EXCHANGE_VERSION,

            "access_verified":
                True,

            "app_id":
                receipt["app_id"],

            "role":
                receipt["role"],

            "target_path":
                receipt["target_path"],

            "receipt_id":
                receipt["receipt_id"],

            "expires_at_epoch":
                receipt["expires_at_epoch"],

            "navigation_context":
                receipt["navigation_context"],
        },
        200,
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
