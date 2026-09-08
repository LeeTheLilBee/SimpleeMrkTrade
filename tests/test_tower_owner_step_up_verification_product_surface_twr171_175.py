from datetime import datetime, timezone

from flask import Flask

import tower.hosted_owner_release_review_web as release_web

from tower.tower_human_login_ob_launch import (
    SESSION_STEP_UP_UNTIL,
    SESSION_USERNAME,
)


ORIGIN = {
    "Origin": "http://localhost"
}


def build_app(
    monkeypatch,
    *,
    owner=True,
    valid_password=True,
):

    monkeypatch.setattr(
        release_web,
        "owner_session_active",
        lambda: owner,
    )

    monkeypatch.setattr(
        release_web,
        "verify_owner_credentials",
        lambda *,
        username,
        password: (
            valid_password
            and username == "owner"
            and password == "correct-owner-password"
        ),
    )

    monkeypatch.setattr(
        release_web,
        "configured_step_up_minutes",
        lambda: 10,
    )

    monkeypatch.setattr(
        release_web,
        "utc_now",
        lambda: datetime(
            2026,
            9,
            8,
            14,
            0,
            tzinfo=timezone.utc,
        ),
    )

    app = Flask(__name__)

    app.secret_key = (
        "twr171-175-step-up-product-test"
    )

    release_web.register_tower_owner_release_review_routes(
        app
    )

    client = app.test_client()

    if owner:

        with client.session_transaction() as data:

            data[
                SESSION_USERNAME
            ] = "owner"

    return app, client


def csrf_token(client):

    client.get(
        release_web.RELEASE_STEP_UP_PATH
    )

    with client.session_transaction() as data:

        return data[
            release_web.RELEASE_CSRF_SESSION_KEY
        ]


def test_twr171_step_up_is_owner_verification_product_surface(
    monkeypatch,
):

    _, client = build_app(
        monkeypatch
    )

    response = client.get(
        release_web.RELEASE_STEP_UP_PATH
    )

    body = response.get_data(
        as_text=True
    )

    assert response.status_code == 200

    assert (
        'data-tower-step-up-product="twr171-175"'
        in body
    )

    assert (
        "Tower owner verification"
        in body
    )

    assert (
        "Verify your identity"
        in body
    )

    assert (
        "Confirm it is you"
        in body
    )

    assert (
        "Release Review"
        in body
    )


def test_twr172_step_up_explains_why_and_what_it_does_not_authorize(
    monkeypatch,
):

    _, client = build_app(
        monkeypatch
    )

    body = (
        client.get(
            release_web.RELEASE_STEP_UP_PATH
        )
        .get_data(
            as_text=True
        )
    )

    assert (
        'data-tower-step-up-explanation="true"'
        in body
    )

    assert (
        "Why Tower is asking"
        in body
    )

    assert (
        "What verification does"
        in body
    )

    assert (
        "What verification does not do"
        in body
    )

    assert (
        "Verification does not approve a candidate"
        in body
    )

    assert (
        "Execution stays locked"
        in body
    )

    assert (
        'data-tower-step-up-boundary="identity-only"'
        in body
    )


def test_twr173_successful_verification_returns_directly_to_release_review(
    monkeypatch,
):

    _, client = build_app(
        monkeypatch
    )

    token = csrf_token(
        client
    )

    response = client.post(
        release_web.RELEASE_STEP_UP_PATH,

        data={
            "csrf_token":
                token,

            "password":
                "correct-owner-password",
        },

        headers=ORIGIN,

        follow_redirects=False,
    )

    assert response.status_code == 303

    assert (
        response.headers[
            "Location"
        ]
        == release_web.RELEASE_REVIEW_PATH
    )

    assert (
        "observatory"
        not in response.headers[
            "Location"
        ].lower()
    )

    with client.session_transaction() as data:

        assert (
            SESSION_STEP_UP_UNTIL
            in data
        )

        assert (
            "correct-owner-password"
            not in repr(
                dict(data)
            )
        )


def test_twr173_historical_remain_in_tower_wording_is_preserved(
    monkeypatch,
):

    _, client = build_app(
        monkeypatch
    )

    body = (
        client.get(
            release_web.RELEASE_STEP_UP_PATH
        )
        .get_data(
            as_text=True
        )
    )

    assert (
        "remain in Tower"
        in body
    )

    assert (
        "Verify and return to Release Review"
        in body
    )


def test_twr174_wrong_password_fails_closed_without_step_up(
    monkeypatch,
):

    _, client = build_app(
        monkeypatch,
        valid_password=False,
    )

    token = csrf_token(
        client
    )

    response = client.post(
        release_web.RELEASE_STEP_UP_PATH,

        data={
            "csrf_token":
                token,

            "password":
                "wrong-password",
        },

        headers=ORIGIN,

        follow_redirects=False,
    )

    assert response.status_code == 403

    with client.session_transaction() as data:

        assert (
            SESSION_STEP_UP_UNTIL
            not in data
        )

        assert (
            "wrong-password"
            not in repr(
                dict(data)
            )
        )


def test_twr174_missing_csrf_and_bad_origin_fail_closed(
    monkeypatch,
):

    _, client = build_app(
        monkeypatch
    )

    missing_csrf = client.post(
        release_web.RELEASE_STEP_UP_PATH,

        data={
            "password":
                "correct-owner-password"
        },

        headers=ORIGIN,

        follow_redirects=False,
    )

    assert missing_csrf.status_code == 403

    token = csrf_token(
        client
    )

    bad_origin = client.post(
        release_web.RELEASE_STEP_UP_PATH,

        data={
            "csrf_token":
                token,

            "password":
                "correct-owner-password",
        },

        headers={
            "Origin":
                "https://example.invalid"
        },

        follow_redirects=False,
    )

    assert bad_origin.status_code == 403


def test_twr174_nonowner_and_expired_step_up_remain_fail_closed(
    monkeypatch,
):

    _, nonowner_client = build_app(
        monkeypatch,
        owner=False,
    )

    response = nonowner_client.get(
        release_web.RELEASE_STEP_UP_PATH,
        follow_redirects=False,
    )

    assert response.status_code == 302

    assert (
        response.headers[
            "Location"
        ]
        == "/tower/login"
    )

    monkeypatch.setattr(
        release_web,
        "owner_session_active",
        lambda: True,
    )

    monkeypatch.setattr(
        release_web,
        "step_up_active",
        lambda: False,
    )

    app = Flask(
        __name__
    )

    app.secret_key = (
        "twr174-expired-step-up"
    )

    with app.test_request_context(
        release_web.RELEASE_REVIEW_PATH
    ):

        denied = (
            release_web
            ._step_up_required()
        )

        assert denied is not None

        assert denied.status_code == 302

        assert (
            denied.headers[
                "Location"
            ]
            == release_web.RELEASE_STEP_UP_PATH
        )


def test_twr175_password_field_never_renders_a_password_value(
    monkeypatch,
):

    _, client = build_app(
        monkeypatch
    )

    body = (
        client.get(
            release_web.RELEASE_STEP_UP_PATH
        )
        .get_data(
            as_text=True
        )
    )

    start = body.index(
        'id="release-password"'
    )

    end = body.index(
        ">",
        start,
    )

    password_tag = body[
        start:end
    ]

    assert (
        'name="password"'
        in password_tag
    )

    assert (
        'type="password"'
        in password_tag
    )

    assert (
        'autocomplete="current-password"'
        in password_tag
    )

    assert (
        "value="
        not in password_tag
    )


def test_twr175_post_security_mechanics_remain_intact():

    source = open(
        "tower/hosted_owner_release_review_web.py",
        encoding="utf-8",
    ).read()

    post_start = source.index(
        "    @app.post(RELEASE_STEP_UP_PATH)"
    )

    review_start = source.index(
        "    @app.get(RELEASE_REVIEW_PATH)",
        post_start,
    )

    post_source = source[
        post_start:
        review_start
    ]

    assert (
        "_owner_required()"
        in post_source
    )

    assert (
        "_same_origin()"
        in post_source
    )

    assert (
        "_csrf_valid()"
        in post_source
    )

    assert (
        "verify_owner_credentials("
        in post_source
    )

    assert (
        "SESSION_STEP_UP_UNTIL"
        in post_source
    )

    assert (
        "configured_step_up_minutes()"
        in post_source
    )

    assert (
        "redirect(RELEASE_REVIEW_PATH, code=303)"
        in post_source
    )

    for forbidden in (
        "release_execution_authorized = True",
        "deployment_authorized = True",
        "promotion_authorized = True",
        "broker_submission_authorized = True",
        "capital_movement_authorized = True",
        "manual_live_authorized = True",
        "live_auto_authorized = True",
    ):

        assert forbidden not in post_source
