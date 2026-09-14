"""
TWR190 — real Tower -> Teller owner launch.

A route being registered does not manufacture product availability.

Launch requires:
- current Tower owner session,
- active step-up,
- effective owner Teller entitlement,
- verified Teller publication / environment / health truth,
- configured HTTPS Teller URL,
- exact allowed Teller origin,
- secure one-time Tower handoff.

No employee or manager access is activated here.
No payroll execution, banking, capital movement, broker execution,
Manual Live, or Live Auto authority is created here.
"""

from __future__ import annotations

import hmac
import os

from datetime import timedelta
from html import escape
from urllib.parse import (
    urlencode,
    urlsplit,
)

from flask import (
    Flask,
    redirect,
    request,
    session,
)

from tower.app_truth_projection import (
    app_truth_by_id,
)

from tower.owner_teller_handoff import (
    OwnerTellerHandoffError,
    issue_owner_teller_handoff,
)

from tower.teller_handoff_web import (
    TOWER_TELLER_ALLOWED_ORIGIN_ENV,
)

from tower.teller_owner_entitlement_reservation import (
    teller_owner_entitlement_reservation,
)

from tower.tower_human_login_ob_launch import (
    ACCESS_HOME_PATH,
    SESSION_AUTHENTICATED,
    SESSION_AUTH_TIME,
    SESSION_OWNER_ID,
    SESSION_ROLE,
    SESSION_STEP_UP_UNTIL,
    SESSION_USERNAME,
    configured_step_up_minutes,
    page,
    require_human_owner,
    safe_next_path,
    step_up_active,
    utc_now,
    verify_owner_credentials,
)


TOWER_TELLER_WEB_URL_ENV = (
    "TOWER_TELLER_WEB_URL"
)

TELLER_LAUNCH_PATH = (
    "/tower/launch/teller"
)

TELLER_STEP_UP_PATH = (
    "/tower/step-up/teller"
)

TELLER_LAUNCH_ENDPOINT = (
    "tower_teller_owner_launch_twr190"
)

TELLER_STEP_UP_ENDPOINT = (
    "tower_teller_owner_step_up_twr190"
)


class TellerOwnerLaunchError(
    ValueError
):

    def __init__(
        self,
        code,
    ):

        self.code = str(
            code
            or "tower_teller_launch_blocked"
        )

        super().__init__(
            self.code
        )


def _clean(value):

    return str(
        value
        if value is not None
        else ""
    ).strip()


def _session_context():

    return {
        "authenticated":
            session.get(
                SESSION_AUTHENTICATED
            )
            is True,

        "role":
            session.get(
                SESSION_ROLE
            ),

        "owner_id":
            session.get(
                SESSION_OWNER_ID
            ),

        "username":
            session.get(
                SESSION_USERNAME
            ),

        "authenticated_at":
            session.get(
                SESSION_AUTH_TIME
            ),

        "step_up_until":
            session.get(
                SESSION_STEP_UP_UNTIL
            ),
    }


def _configured_teller_web_url():

    raw = _clean(
        os.environ.get(
            TOWER_TELLER_WEB_URL_ENV
        )
    )

    if not raw:

        raise TellerOwnerLaunchError(
            "tower_teller_web_url_not_configured"
        )

    parsed = urlsplit(
        raw
    )

    if (
        parsed.scheme
        != "https"
        or not parsed.netloc
        or parsed.username
        or parsed.password
        or parsed.query
        or parsed.fragment
    ):
        raise TellerOwnerLaunchError(
            "tower_teller_web_url_invalid"
        )

    origin = (
        f"{parsed.scheme}://"
        f"{parsed.netloc}"
    )

    allowed_origin = (
        _clean(
            os.environ.get(
                TOWER_TELLER_ALLOWED_ORIGIN_ENV
            )
        )
        .rstrip("/")
    )

    if not allowed_origin:

        raise TellerOwnerLaunchError(
            "tower_teller_allowed_origin_not_configured"
        )

    if not hmac.compare_digest(
        origin,
        allowed_origin,
    ):
        raise TellerOwnerLaunchError(
            "tower_teller_origin_configuration_mismatch"
        )

    return raw.rstrip("/")


def _verify_activation():

    activation = (
        teller_owner_entitlement_reservation()
    )

    if (
        activation.get(
            "policy_contract_verified"
        )
        is not True
        or activation.get(
            "reservation_state"
        )
        != "ACTIVATED"
        or activation.get(
            "effective_entitlement"
        )
        is not True
    ):
        raise TellerOwnerLaunchError(
            "tower_teller_owner_entitlement_not_active"
        )

    return activation


def _verify_product_launchability():

    truth = app_truth_by_id(
        "teller"
    )

    if not truth:

        raise TellerOwnerLaunchError(
            "tower_teller_app_truth_missing"
        )

    if (
        truth.get(
            "launchable"
        )
        is not True
    ):
        raise TellerOwnerLaunchError(
            "tower_teller_publication_truth_not_launchable"
        )

    return truth


def _launch_blocked(
    code,
    *,
    status_code=503,
):

    safe = escape(
        _clean(
            code
        )
        or "tower_teller_launch_blocked"
    )

    content = f"""
    <section class="hero">
        <h1>Teller launch is blocked</h1>

        <p>
            Tower did not verify every fact required
            for the protected Teller crossing.
        </p>
    </section>

    <section class="card">
        <div class="notice danger">
            {safe}
        </div>

        <div class="actions">
            <a
                class="button secondary"
                href="{ACCESS_HOME_PATH}"
            >
                Return to Tower
            </a>
        </div>
    </section>
    """

    return (
        page(
            title="Teller launch blocked",
            content=content,
        ),
        status_code,
    )


def _redirect_target(
    web_url,
    handoff_code,
):

    return (
        web_url
        + "#"
        + urlencode({
            "tower_handoff":
                handoff_code,
        })
    )


def teller_owner_launch_view():

    if not step_up_active():

        return redirect(
            TELLER_STEP_UP_PATH
            + "?"
            + urlencode({
                "next":
                    TELLER_LAUNCH_PATH,
            })
        )

    try:

        _verify_activation()

        _verify_product_launchability()

        web_url = (
            _configured_teller_web_url()
        )

        issued = (
            issue_owner_teller_handoff(
                _session_context(),

                navigation_context={
                    "source_app":
                        "tower",

                    "destination":
                        "owner_money_workspace",

                    "return_app":
                        "tower",

                    "return_destination":
                        "access_home",
                },
            )
        )

    except (
        TellerOwnerLaunchError,
        OwnerTellerHandoffError,
    ) as exc:

        code = getattr(
            exc,
            "code",
            "tower_teller_launch_blocked",
        )

        return _launch_blocked(
            code
        )

    return redirect(
        _redirect_target(
            web_url,
            issued[
                "handoff_code"
            ],
        )
    )


def teller_owner_step_up_view():

    next_path = safe_next_path(
        request.values.get(
            "next"
        ),
        TELLER_LAUNCH_PATH,
    )

    error = ""

    if request.method == "POST":

        password = (
            request.form.get(
                "password",
                "",
            )
        )

        username = _clean(
            session.get(
                SESSION_USERNAME
            )
        )

        if verify_owner_credentials(
            username=username,
            password=password,
        ):

            expires_at = (
                utc_now()
                + timedelta(
                    minutes=(
                        configured_step_up_minutes()
                    )
                )
            )

            session[
                SESSION_STEP_UP_UNTIL
            ] = (
                expires_at
                .isoformat()
            )

            return redirect(
                next_path
            )

        error = (
            "Tower could not verify the "
            "step-up password."
        )

    error_html = (
        '<div class="notice danger">'
        + escape(error)
        + "</div>"
        if error
        else ""
    )

    content = f"""
    <section class="hero">
        <h1>Confirm It Is You</h1>

        <p>
            Re-enter your Tower password before
            opening The Teller.
        </p>
    </section>

    <section class="card">
        {error_html}

        <form method="post">

            <input
                type="hidden"
                name="next"
                value="{escape(next_path)}"
            >

            <label for="password">
                Owner password
            </label>

            <input
                id="password"
                name="password"
                type="password"
                autocomplete="current-password"
                required
            >

            <button type="submit">
                Verify and open Teller
            </button>

        </form>
    </section>
    """

    return page(
        title="Tower Teller Step-Up",
        content=content,
    )


def register_teller_owner_launch_web(
    app: Flask,
):

    if (
        TELLER_LAUNCH_ENDPOINT
        not in app.view_functions
    ):
        app.add_url_rule(
            TELLER_LAUNCH_PATH,
            endpoint=(
                TELLER_LAUNCH_ENDPOINT
            ),
            view_func=(
                require_human_owner(
                    teller_owner_launch_view
                )
            ),
            methods=[
                "GET",
            ],
        )

    if (
        TELLER_STEP_UP_ENDPOINT
        not in app.view_functions
    ):
        app.add_url_rule(
            TELLER_STEP_UP_PATH,
            endpoint=(
                TELLER_STEP_UP_ENDPOINT
            ),
            view_func=(
                require_human_owner(
                    teller_owner_step_up_view
                )
            ),
            methods=[
                "GET",
                "POST",
            ],
        )

    return app
