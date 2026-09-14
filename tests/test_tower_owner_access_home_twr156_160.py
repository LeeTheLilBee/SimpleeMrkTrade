from __future__ import annotations

import inspect

from flask import Flask, session

import tower.access_home_owner_launches as owner_launches

from tower.tower_access_home_ui_v2 import (
    APP_CARDS,
    record_ob_return_receipt,
    render_access_home_v2,
    ui_v2_contract,
)


def render_home(
    *,
    step_up: bool = False,
    with_return: bool = False,
) -> str:

    app = Flask(__name__)

    app.secret_key = (
        "tower-owner-access-home-twr156-160"
    )

    with app.test_request_context(
        "/tower/access-home"
    ):

        session[
            "tower_authenticated"
        ] = True

        session[
            "tower_role"
        ] = "owner"

        session[
            "owner_id"
        ] = "owner-test"

        session[
            "tower_username"
        ] = "Owner"

        if with_return:

            record_ob_return_receipt(
                source="observatory",
                last_room="/ob/dashboard",
            )

        return render_access_home_v2(
            step_up_active=step_up,
            username="Owner",
        )


def test_twr156_access_home_is_explicit_owner_front_door():

    body = render_home()

    assert (
        'data-tower-owner-access-home="twr156-160"'
        in body
    )

    assert (
        'data-tower-owner-front-door="true"'
        in body
    )

    assert (
        "One front door. One real product entry."
        in body
    )

    assert (
        "Welcome back, Owner."
        in body
    )


def test_twr157_observatory_remains_only_product_card():

    assert [
        card["id"]
        for card in APP_CARDS
    ] == [
        "observatory",
    ]

    card = APP_CARDS[0]

    assert (
        card["href"]
        == "/tower/launch/observatory"
    )

    assert (
        card["status"]
        == "Protected entry"
    )

    body = render_home()

    assert (
        'data-tower-primary-owner-action="observatory"'
        in body
    )

    assert (
        "The Observatory"
        in body
    )

    assert (
        "/tower/launch/observatory"
        in body
    )


def test_twr157_access_home_does_not_publish_fake_products():

    body = render_home()

    for prohibited in (
        "The Teller",
        "The Grounds",
        "The Clouds",
        "Archive Vault",
        "#vault-preview",
        "#teller-preview",
        "#grounds-preview",
        "#clouds-preview",
    ):

        assert (
            prohibited
            not in body
        )


def test_twr158_owner_headquarters_is_integrated_not_duplicated():

    body = render_home()

    assert (
        'id="tower-owner-launch-dock"'
        in body
    )

    assert (
        'data-tower-owner-control="integrated"'
        in body
    )

    assert (
        "/tower/owner-dashboard"
        in body
    )

    enhanced = (
        owner_launches
        .inject_owner_launch_dock(
            body
        )
    )

    assert (
        enhanced
        == body
    )


def test_twr159_evidence_is_backstage():

    body = render_home()

    assert (
        'data-tower-backstage-evidence="true"'
        in body
    )

    assert (
        "<details"
        in body
    )

    assert (
        "Evidence & audit"
        in body
    )

    assert (
        "/tower/owner/evidence"
        in body
    )

    assert (
        "/tower/owner/release-review/prerequisites"
        not in body
    )

    assert (
        "/tower/observatory-walkthrough"
        not in body
    )


def test_twr159_return_state_is_compact_and_truthful():

    without_return = render_home(
        with_return=False
    )

    assert (
        "No verified return receipt"
        in without_return
    )

    with_return = render_home(
        with_return=True
    )

    assert (
        "Verified return receipt"
        in with_return
    )

    assert (
        'data-tower-return-status="compact"'
        in with_return
    )


def test_twr160_primary_source_has_no_proof_navigation():

    source = inspect.getsource(
        render_access_home_v2
    )

    for prohibited in (
        'href="/tower/owner/release-review/prerequisites"',
        'href="/tower/owner/release-review/walkthrough"',
        'href="/tower/security-map"',
        "/tower/observatory-walkthrough",
        "Simulate return",
        "Evidence drawers",
    ):

        assert (
            prohibited
            not in source
        )


def test_twr160_safety_contract_remains_locked():

    contract = (
        ui_v2_contract()
    )

    assert (
        contract[
            "credentials_committed"
        ]
        is False
    )

    assert (
        contract[
            "broker_submission"
        ]
        is False
    )

    assert (
        contract[
            "capital_movement"
        ]
        is False
    )

    assert (
        contract[
            "production_manual_live_authorization"
        ]
        is False
    )

    assert (
        contract[
            "live_auto_activation"
        ]
        is False
    )

    assert (
        contract[
            "direct_vault_write"
        ]
        is False
    )


def test_twr160_access_home_keeps_default_deny_visible():

    body = render_home(
        step_up=False
    )

    assert (
        "DEFAULT DENY"
        in body
    )

    assert (
        "STEP-UP REQUIRED"
        in body
    )

    assert (
        "Additional verification required"
        in body
    )

    body = render_home(
        step_up=True
    )

    assert (
        "STEP-UP ACTIVE"
        in body
    )

    assert (
        "Verified for protected entry"
        in body
    )
