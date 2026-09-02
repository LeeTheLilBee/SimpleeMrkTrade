from __future__ import annotations

import inspect

from flask import Flask

import tower.hosted_owner_release_review_web as release_web
import tower.hosted_owner_release_walkthrough_web as walkthrough_web
import tower.hosted_release_prerequisite_certification_web as prerequisite_web
import tower.owner_dashboard_web as dashboard_web
import tower.owner_evidence_basement_web as basement


def test_twr151_manifest_marks_every_resource_backstage():

    manifest = (
        basement.evidence_basement_manifest()
    )

    assert (
        manifest[
            "backstage"
        ]
        is True
    )

    assert (
        manifest[
            "primary_owner_surface"
        ]
        is False
    )

    assert (
        manifest[
            "read_only"
        ]
        is True
    )

    assert (
        manifest[
            "execution_authority"
        ]
        is False
    )

    assert (
        manifest[
            "resource_count"
        ]
        == 6
    )

    assert all(
        item[
            "backstage"
        ]
        is True
        for item in manifest[
            "resources"
        ]
    )

    assert all(
        item[
            "primary_navigation"
        ]
        is False
        for item in manifest[
            "resources"
        ]
    )

    assert all(
        item[
            "read_only"
        ]
        is True
        for item in manifest[
            "resources"
        ]
    )

    assert all(
        item[
            "execution_authority"
        ]
        is False
        for item in manifest[
            "resources"
        ]
    )


def test_twr151_historical_routes_are_preserved():

    paths = {
        item[
            "path"
        ]
        for item in (
            basement
            .evidence_basement_manifest()[
                "resources"
            ]
        )
    }

    assert (
        walkthrough_web.HOSTED_WALKTHROUGH_PATH
        in paths
    )

    assert (
        walkthrough_web.HOSTED_READINESS_JSON_PATH
        in paths
    )

    assert (
        walkthrough_web.HOSTED_CERTIFICATION_JSON_PATH
        in paths
    )

    assert (
        prerequisite_web.PREREQUISITE_PAGE_PATH
        in paths
    )

    assert (
        prerequisite_web.PREREQUISITE_VERIFICATION_JSON_PATH
        in paths
    )

    assert (
        prerequisite_web.PREREQUISITE_CERTIFICATION_JSON_PATH
        in paths
    )


def test_twr152_basement_is_explicitly_backstage():

    html = (
        basement.owner_evidence_basement_html()
    )

    assert (
        "Evidence Basement"
        in html
    )

    assert (
        "BACKSTAGE · READ ONLY"
        in html
    )

    assert (
        "data-tower-evidence-basement"
        in html
    )

    assert (
        "does not execute"
        in html
    )


def test_twr152_basement_requires_step_up(
    monkeypatch,
):

    monkeypatch.setattr(
        basement,
        "_step_up_required",
        lambda:
            (
                "STEP UP REQUIRED",
                403,
            ),
    )

    app = Flask(
        __name__
    )

    app.secret_key = (
        "twr151-basement-test-secret"
    )

    basement.register_tower_owner_evidence_basement_routes(
        app
    )

    response = (
        app.test_client().get(
            basement.EVIDENCE_BASEMENT_PATH
        )
    )

    assert (
        response.status_code
        == 403
    )


def test_twr152_verified_step_up_can_open_basement(
    monkeypatch,
):

    monkeypatch.setattr(
        basement,
        "_step_up_required",
        lambda:
            None,
    )

    app = Flask(
        __name__
    )

    app.secret_key = (
        "twr151-basement-open-test"
    )

    basement.register_tower_owner_evidence_basement_routes(
        app
    )

    response = (
        app.test_client().get(
            basement.EVIDENCE_BASEMENT_PATH
        )
    )

    assert (
        response.status_code
        == 200
    )

    assert (
        b"Evidence Basement"
        in response.data
    )


def test_twr153_primary_dashboard_has_basement_not_direct_prerequisite_navigation():

    source = inspect.getsource(
        dashboard_web
        ._tower_owner_dashboard_html
    )

    assert (
        'href="/tower/owner/evidence"'
        in source
    )

    assert (
        'href="/tower/owner/release-review"'
        in source
    )

    assert (
        'href="/tower/owner/release-review/walkthrough"'
        not in source
    )

    assert (
        'href="/tower/owner/release-review/prerequisites"'
        not in source
    )

    assert (
        "Release prerequisite certificate"
        in source
    )

    assert (
        "data-tower-prerequisite-certificate"
        in source
    )


def test_twr153_historical_prerequisite_contract_is_inert_module_metadata():

    whole_source = inspect.getsource(
        dashboard_web
    )

    primary_source = inspect.getsource(
        dashboard_web
        ._tower_owner_dashboard_html
    )

    legacy = (
        'href="/tower/owner/release-review/prerequisites"'
    )

    assert (
        legacy
        in whole_source
    )

    assert (
        legacy
        not in primary_source
    )

    assert (
        "LEGACY_PREREQUISITE_CONTRACT_HREF"
        in whole_source
    )


def test_twr154_release_review_routes_evidence_backstage():

    source = inspect.getsource(
        release_web
        ._review_room_html
    )

    assert (
        'href="/tower/owner/release-review/walkthrough"'
        not in source
    )

    assert (
        'href="/tower/owner/evidence"'
        in source
    )

    assert (
        "Evidence & readiness details"
        in source
    )


def test_twr155_historical_walkthrough_and_prerequisite_routes_still_exist():

    assert (
        walkthrough_web.HOSTED_WALKTHROUGH_PATH
        == "/tower/owner/release-review/walkthrough"
    )

    assert (
        prerequisite_web.PREREQUISITE_PAGE_PATH
        == "/tower/owner/release-review/prerequisites"
    )


def test_twr155_basement_never_claims_execution_authority():

    manifest = (
        basement.evidence_basement_manifest()
    )

    assert (
        manifest[
            "execution_authority"
        ]
        is False
    )

    assert (
        manifest[
            "read_only"
        ]
        is True
    )

    assert (
        manifest[
            "step_up_required"
        ]
        is True
    )
