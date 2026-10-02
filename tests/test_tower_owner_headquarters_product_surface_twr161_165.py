from __future__ import annotations

import inspect

import tower.hosted_owner_release_candidate_state as candidate_state
import tower.hosted_owner_release_readiness as readiness
import tower.hosted_release_prerequisite_certification as prerequisites
import tower.owner_dashboard_web as dashboard_web


LEGACY_PREREQUISITE_HREF = (
    'href="/tower/owner/release-review/prerequisites"'
)


def install_deterministic_headquarters(
    monkeypatch,
):

    fake_dashboard = {
        "summary": {
            "people_authority_state":
                "NOT_CONFIGURED",

            "invitation_authority_state":
                "NOT_CONFIGURED",

            "invitation_delivery_state":
                "NOT_CONFIGURED",

            "access_lifecycle_state":
                "NOT_CONFIGURED",

            "access_authority_state":
                "NOT_CONFIGURED",

            "entitlement_authority_state":
                "NOT_CONFIGURED",

            "organization_authority_state":
                "NOT_CONFIGURED",

            "people_count":
                None,

            "invitation_count":
                None,

            "pending_invitation_count":
                None,

            "pending_access_count":
                None,

            "tower_meaning":
                (
                    "Tower shows only supported owner truth."
                ),

            "owner_next_action":
                (
                    "Configure real authority before creating records."
                ),
        },

        "people":
            [],

        "invitations":
            [],

        "invitation_lifecycle": {
            "verification_state":
                "NOT_CONFIGURED",
        },

        "danger_locks": {
            "live_auto":
                "LOCKED",

            "broker_execution":
                False,

            "capital_action":
                False,

            "release_execution":
                False,
        },
    }

    fake_cards = [
        {
            "card_id":
                "owner-card-people",

            "title":
                "People",

            "value":
                "NOT_CONFIGURED",

            "status":
                "not-configured",

            "meaning":
                "Hosted owner identity authority is not configured.",
        },

        {
            "card_id":
                "owner-card-danger-locks",

            "title":
                "Execution safety",

            "value":
                "LOCKED",

            "status":
                "locked",

            "meaning":
                "Broker, capital, release execution, and Live Auto remain closed.",
        },
    ]

    monkeypatch.setattr(
        dashboard_web,
        "build_tower_owner_dashboard",
        lambda:
            fake_dashboard,
    )

    monkeypatch.setattr(
        dashboard_web,
        "owner_dashboard_status_cards",
        lambda:
            fake_cards,
    )

    monkeypatch.setattr(
        candidate_state,
        "owner_release_dashboard_snapshot",
        lambda: {
            "state":
                "RELEASE_REVIEW_REQUIRED",

            "label":
                "Review required",

            "detail":
                "Owner review is required before any later release gate.",
        },
    )

    monkeypatch.setattr(
        readiness,
        "owner_hosted_readiness_dashboard_snapshot",
        lambda: {
            "state":
                "READINESS_REVIEW_REQUIRED",

            "label":
                "Readiness review required",
        },
    )

    monkeypatch.setattr(
        prerequisites,
        "owner_prerequisite_certificate_dashboard_snapshot",
        lambda: {
            "state":
                "PREREQUISITES_NOT_CERTIFIED",

            "label":
                "Not certified",
        },
    )

    return fake_dashboard


def test_twr161_headquarters_is_owner_workspace(
    monkeypatch,
):

    install_deterministic_headquarters(
        monkeypatch
    )

    body = (
        dashboard_web
        ._tower_owner_dashboard_html()
    )

    assert (
        'data-tower-owner-headquarters="twr161-165"'
        in body
    )

    assert (
        'data-tower-headquarters-hierarchy="owner-workspace"'
        in body
    )

    assert (
        "Owner Headquarters"
        in body
    )

    assert (
        "Tower Owner Dashboard"
        in body
    )

    assert (
        'href="/tower/access-home"'
        in body
    )

    assert (
        'href="/tower/owner-dashboard"'
        in body
    )


def test_twr162_missing_authority_is_not_fake_zero(
    monkeypatch,
):

    install_deterministic_headquarters(
        monkeypatch
    )

    body = (
        dashboard_web
        ._tower_owner_dashboard_html()
    )

    assert (
        'data-tower-people-count="unavailable"'
        in body
    )

    assert (
        'data-tower-invitation-count="unavailable"'
        in body
    )

    assert (
        'data-tower-pending-access="unavailable"'
        in body
    )

    assert (
        "NOT_CONFIGURED"
        in body
    )

    assert (
        "PEOPLE · —"
        in body
    )

    assert (
        "INVITATIONS · —"
        in body
    )

    assert (
        "PENDING ACCESS · —"
        in body
    )


def test_twr162_authority_snapshot_is_compact(
    monkeypatch,
):

    install_deterministic_headquarters(
        monkeypatch
    )

    body = (
        dashboard_web
        ._tower_owner_dashboard_html()
    )

    assert (
        'data-tower-authority-snapshot="true"'
        in body
    )

    assert (
        "People authority"
        in body
    )

    assert (
        "Invitation authority"
        in body
    )

    assert (
        "Access authority"
        in body
    )

    assert (
        'data-tower-authority-details="true"'
        in body
    )

    assert (
        "<details"
        in body
    )


def test_twr163_release_review_is_primary_operation(
    monkeypatch,
):

    install_deterministic_headquarters(
        monkeypatch
    )

    body = (
        dashboard_web
        ._tower_owner_dashboard_html()
    )

    # Historical TWR103 operational-entry contract.
    assert (
        'data-tower-release-review-entry="true"'
        in body
    )

    # TWR163 product hierarchy contract.
    assert (
        'data-tower-release-review-primary="true"'
        in body
    )

    assert (
        'href="/tower/owner/release-review"'
        in body
    )

    assert (
        "Open release review"
        in body
    )

    assert (
        "Primary operational next move"
        in body
    )


def test_twr163_no_execution_action_is_added_to_headquarters():

    source = inspect.getsource(
        dashboard_web
        ._tower_owner_dashboard_html
    )

    for prohibited in (
        'href="/tower/owner/release-review/walkthrough"',
        'href="/tower/owner/release-review/prerequisites"',
        'href="/tower/security-map"',
        "/tower/observatory-walkthrough",
        "Execute release",
        "Execute trade",
        "Submit order",
        "Move capital",
        "Activate Live Auto",
        "Enable Manual Live",
    ):

        assert (
            prohibited
            not in source
        )


def test_twr164_evidence_is_backstage(
    monkeypatch,
):

    install_deterministic_headquarters(
        monkeypatch
    )

    body = (
        dashboard_web
        ._tower_owner_dashboard_html()
    )

    assert (
        'data-tower-backstage-evidence="true"'
        in body
    )

    assert (
        "Evidence & certification"
        in body
    )

    assert (
        'href="/tower/owner/evidence"'
        in body
    )

    assert (
        "Open evidence basement"
        in body
    )

    assert (
        "Release prerequisite certificate"
        in body
    )

    assert (
        'data-tower-prerequisite-certificate="PREREQUISITES_NOT_CERTIFIED"'
        in body
    )


def test_twr164_historical_prerequisite_contract_remains_inert(
    monkeypatch,
):

    install_deterministic_headquarters(
        monkeypatch
    )

    whole_source = inspect.getsource(
        dashboard_web
    )

    primary_source = inspect.getsource(
        dashboard_web
        ._tower_owner_dashboard_html
    )

    body = (
        dashboard_web
        ._tower_owner_dashboard_html()
    )

    assert (
        LEGACY_PREREQUISITE_HREF
        in whole_source
    )

    assert (
        LEGACY_PREREQUISITE_HREF
        not in primary_source
    )

    # Historical TWR119 runtime contract remains discoverable,
    # but only through inert rendered comment metadata.
    assert (
        LEGACY_PREREQUISITE_HREF
        in body
    )

    assert (
        '<a href="/tower/owner/release-review/prerequisites"'
        not in body
    )


def test_twr164_walkthrough_never_returns_to_owner_dashboard_source():

    whole_source = inspect.getsource(
        dashboard_web
    )

    assert (
        'href="/tower/owner/release-review/walkthrough"'
        not in whole_source
    )

    assert (
        "/tower/observatory-walkthrough"
        not in whole_source
    )


def test_twr165_danger_locks_remain_visible_and_closed(
    monkeypatch,
):

    install_deterministic_headquarters(
        monkeypatch
    )

    body = (
        dashboard_web
        ._tower_owner_dashboard_html()
    )

    assert (
        'data-tower-danger-boundary="locked"'
        in body
    )

    for label in (
        "Live Auto",
        "Broker execution",
        "Capital movement",
        "Release execution",
    ):

        assert (
            label
            in body
        )

    assert (
        body.count(
            ">LOCKED<"
        )
        >= 4
        or body.count(
            "LOCKED"
        )
        >= 4
    )


def test_twr165_existing_service_danger_contract_remains_closed():

    dashboard = (
        dashboard_web
        .build_tower_owner_dashboard()
    )

    locks = dashboard[
        "danger_locks"
    ]

    assert (
        locks[
            "live_auto"
        ]
        == "LOCKED"
    )

    assert (
        locks[
            "broker_execution"
        ]
        is False
    )

    assert (
        locks[
            "capital_action"
        ]
        is False
    )

    assert (
        locks[
            "release_execution"
        ]
        is False
    )
