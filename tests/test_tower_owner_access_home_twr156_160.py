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
        "Everything you built, one place."
        in body
    )

    assert (
        "Welcome home, Owner."
        in body
    )


def test_twr157_access_home_shows_full_world_without_fake_launches():

    ids = [
        card["id"]
        for card in APP_CARDS
    ]

    for expected in (
        "observatory",
        "teller",
        "grounds",
        "buybox",
        "vault",
        "clouds",
        "simplee_on_the_go",
        "crown_calendar",
        "beauty",
        "sunday_table",
        "our_oral_traditions",
        "cookout_ready",
        "sunday_best",
        "the_village",
        "simplee_fitness",
        "simplee_skincare",
    ):
        assert expected in ids

    live = [
        card for card in APP_CARDS
        if card["href"]
    ]

    assert {
        card["id"]
        for card in live
    } == {
        "observatory",
        "teller",
    }

    body = render_home()

    assert (
        'data-tower-primary-owner-action="protected-products"'
        in body
    )

    for visible in (
        "The Observatory",
        "The Teller",
        "The Grounds",
        "BuyBox",
        "Archive Vault",
        "Simplee Cloud",
        "SimpleeOnTheGo",
        "Crown Calendar",
        "Simplee Beauty",
        "Sunday Table",
        "Our Oral Traditions",
        "Cookout Ready",
        "Sunday Best",
        "The Village",
        "Simplee Fitness",
        "Simplee Skincare",
    ):
        assert visible in body

    assert "/tower/launch/observatory" in body
    assert "/tower/launch/teller" in body

    assert 'href="/apps/crown-calendar"' not in body
    assert 'href="/grounds"' not in body
    assert 'href="/buybox"' not in body


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
        "Protected doors need verification"
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
        "Protected doors ready"
        in body
    )
