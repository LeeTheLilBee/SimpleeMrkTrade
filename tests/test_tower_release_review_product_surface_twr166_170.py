from __future__ import annotations

import inspect

from flask import (
    Flask,
    session,
)

import tower.hosted_owner_release_readiness as readiness
import tower.hosted_owner_release_review_web as release_web
import tower.hosted_release_prerequisite_certification as prerequisite

from tower.hosted_owner_release_review import (
    APPROVE_RELEASE,
    HOLD_RELEASE,
    REJECT_RELEASE,
)


def install_support_snapshots(
    monkeypatch,
):

    monkeypatch.setattr(
        readiness,
        "owner_hosted_readiness_dashboard_snapshot",
        lambda: {
            "state":
                "HOSTED_AWAITING_OWNER_DECISION",

            "label":
                "Hosted candidate ready for your decision",

            "detail":
                "Review the exact hosted candidate.",
        },
    )

    monkeypatch.setattr(
        prerequisite,
        "owner_prerequisite_certificate_dashboard_snapshot",
        lambda: {
            "state":
                "RELEASE_PREREQUISITES_NOT_CERTIFIED",

            "label":
                "Prerequisites not certified",

            "detail":
                (
                    "Complete verified owner approval first."
                ),
        },
    )


def fake_review():

    return {
        "review_allowed":
            True,

        "packet_integrity_hash":
            "a" * 64,

        "expected_revision":
            "abc123def456",

        "release_recommendation":
            "OWNER_REVIEW_READY",

        "critical_route_count":
            14,

        "allowed_decisions": [
            APPROVE_RELEASE,
            HOLD_RELEASE,
            REJECT_RELEASE,
        ],

        "failures":
            [],
    }


def render_reviewable_room(
    monkeypatch,
) -> str:

    install_support_snapshots(
        monkeypatch
    )

    monkeypatch.setattr(
        release_web,
        "project_owner_release_candidate_state",
        lambda **kwargs: {
            "candidate_state":
                "READY_FOR_OWNER_REVIEW",
        },
    )

    monkeypatch.setattr(
        release_web,
        "owner_release_session_context",
        lambda:
            {},
    )

    monkeypatch.setattr(
        release_web,
        "build_owner_release_review",
        lambda *args, **kwargs:
            fake_review(),
    )

    app = Flask(
        __name__
    )

    app.secret_key = (
        "twr166-170-release-review"
    )

    with app.test_request_context(
        release_web.RELEASE_REVIEW_PATH
    ):

        session[
            "tower_owner_release_review_csrf"
        ] = (
            "release-review-csrf"
        )

        return (
            release_web
            ._review_room_html({
                "reviewable":
                    True,

                "packet": {
                    "expected_revision":
                        "abc123def456",
                },
            })
        )


def test_twr166_release_review_is_explicit_owner_decision_room(
    monkeypatch,
):

    body = (
        render_reviewable_room(
            monkeypatch
        )
    )

    assert (
        'data-tower-release-review-product="twr166-170"'
        in body
    )

    assert (
        "Tower · owner decision room"
        in body
    )

    assert (
        "Release Review"
        in body
    )

    assert (
        "What do you want Tower to record?"
        in body
    )

    assert (
        'data-tower-owner-decision-surface="true"'
        in body
    )


def test_twr166_no_candidate_state_remains_fail_closed(
    monkeypatch,
):

    install_support_snapshots(
        monkeypatch
    )

    app = Flask(
        __name__
    )

    app.secret_key = (
        "twr166-no-candidate"
    )

    with app.test_request_context(
        release_web.RELEASE_REVIEW_PATH
    ):

        body = (
            release_web
            ._review_room_html({
                "reviewable":
                    False,

                "reason":
                    "packet_source_missing",
            })
        )

    assert (
        "NO REVIEWABLE CANDIDATE"
        in body
    )

    assert (
        "Approve candidate"
        not in body
    )

    assert (
        'data-tower-owner-decision-surface="unavailable"'
        in body
    )

    assert (
        "No decision or release action is available."
        in body
    )


def test_twr167_candidate_decision_surface_preserves_all_three_decisions(
    monkeypatch,
):

    body = (
        render_reviewable_room(
            monkeypatch
        )
    )

    assert (
        "Approve candidate"
        in body
    )

    assert (
        "Place on hold"
        in body
    )

    assert (
        "Reject candidate"
        in body
    )

    assert (
        f'value="{APPROVE_RELEASE}"'
        in body
    )

    assert (
        f'value="{HOLD_RELEASE}"'
        in body
    )

    assert (
        f'value="{REJECT_RELEASE}"'
        in body
    )

    assert (
        f'action="{release_web.RELEASE_DECISION_PATH}"'
        in body
    )


def test_twr167_candidate_identity_is_visible_without_evidence_dump(
    monkeypatch,
):

    body = (
        render_reviewable_room(
            monkeypatch
        )
    )

    assert (
        'data-tower-current-candidate="abc123def456"'
        in body
    )

    assert (
        "abc123def456"
        in body
    )

    assert (
        "Candidate evidence"
        in body
    )

    assert (
        'data-tower-candidate-evidence="backstage-detail"'
        in body
    )

    assert (
        "<details"
        in body
    )


def test_twr168_readiness_and_prerequisite_meaning_is_upstairs(
    monkeypatch,
):

    body = (
        render_reviewable_room(
            monkeypatch
        )
    )

    assert (
        'data-tower-release-readiness-summary="true"'
        in body
    )

    assert (
        'data-tower-hosted-readiness="HOSTED_AWAITING_OWNER_DECISION"'
        in body
    )

    assert (
        "Hosted candidate ready for your decision"
        in body
    )

    assert (
        'data-tower-prerequisite-summary="RELEASE_PREREQUISITES_NOT_CERTIFIED"'
        in body
    )

    assert (
        "Prerequisites not certified"
        in body
    )


def test_twr168_detailed_evidence_remains_in_evidence_basement(
    monkeypatch,
):

    body = (
        render_reviewable_room(
            monkeypatch
        )
    )

    assert (
        "Evidence & readiness details"
        in body
    )

    assert (
        'data-tower-release-evidence-backstage="true"'
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


def test_twr169_owner_decision_is_record_only(
    monkeypatch,
):

    body = (
        render_reviewable_room(
            monkeypatch
        )
    )

    assert (
        'data-tower-release-decision-boundary="record-only"'
        in body
    )

    assert (
        "Approval records your owner decision only."
        in body
    )

    assert (
        "Decision recording is not release execution."
        in body
    )

    assert (
        'data-tower-release-execution="locked"'
        in body
    )

    assert (
        'data-tower-release-execution-boundary="closed"'
        in body
    )

    assert (
        "Execution"
        in body
    )

    assert (
        "Still locked"
        in body
    )


def test_twr169_route_and_decision_constants_are_unchanged():

    assert (
        release_web.RELEASE_REVIEW_PATH
        == "/tower/owner/release-review"
    )

    assert (
        release_web.RELEASE_DECISION_PATH
        == "/tower/owner/release-review/decision"
    )

    assert (
        release_web.RELEASE_PUBLICATION_PATH
        == "/tower/owner/release-review/publish"
    )

    assert (
        release_web.RELEASE_STEP_UP_PATH
        == "/tower/owner/release-review/step-up"
    )

    assert (
        release_web.RELEASE_ROOM_MARKER
        == "tower-owner-release-review-room-twr101-105"
    )


def test_twr170_primary_review_source_keeps_proof_and_execution_backstage():

    source = inspect.getsource(
        release_web
        ._review_room_html
    )

    assert (
        "Evidence & readiness details"
        in source
    )

    assert (
        'href="/tower/owner/evidence"'
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

    for prohibited in (
        "Execute release",
        "Promote release",
        "Deploy candidate",
        "Submit to broker",
        "Move capital now",
        "Activate Live Auto",
        "Enable Manual Live",
    ):

        assert (
            prohibited
            not in source
        )


def test_twr170_historical_focused_room_contract_remains_present(
    monkeypatch,
):

    body = (
        render_reviewable_room(
            monkeypatch
        )
    )

    for required in (
        "Release Review",
        "Approve candidate",
        "Candidate evidence",
        "Execution",
        "Still locked",
    ):

        assert (
            required
            in body
        )
