
"""Protected owner-facing hosted release-prerequisite certificate / TWR118-TWR120."""

from __future__ import annotations

from html import escape
from typing import Any

from flask import jsonify

from tower.hosted_owner_release_review import (
    owner_release_session_context,
)

from tower.hosted_owner_release_review_web import (
    RELEASE_REVIEW_PATH,
    _page,
    _step_up_required,
)

from tower.hosted_release_prerequisite_certification import (
    build_release_prerequisite_certificate,
    project_hosted_owner_verification,
)


PREREQUISITE_PAGE_PATH = (
    "/tower/owner/release-review/prerequisites"
)

PREREQUISITE_VERIFICATION_JSON_PATH = (
    "/tower/owner/release-review/prerequisites/verification.json"
)

PREREQUISITE_CERTIFICATION_JSON_PATH = (
    "/tower/owner/release-review/prerequisites/certification.json"
)

PREREQUISITE_PAGE_MARKER = (
    "tower-hosted-owner-verification-prerequisite-certification-twr116-120"
)


def hosted_release_prerequisite_html(
    verification: dict[str, Any],
    certificate_result: dict[str, Any],
) -> str:

    state = escape(
        str(
            verification.get("verification_state")
            or "UNAVAILABLE"
        ).replace("_", " ")
    )

    owner_verified = (
        "Verified"
        if verification.get("owner_verified_for_release")
        else "Not complete"
    )

    prereqs = (
        "Certified"
        if verification.get(
            "release_prerequisites_certified"
        )
        else "Not certified"
    )

    revision = escape(
        str(
            verification.get("expected_revision")
            or "Not verified"
        )
    )

    receipt_id = escape(
        str(
            verification.get("receipt_id")
            or "Not verified"
        )
    )

    certificate = (
        certificate_result.get("certificate")
        or {}
    )

    certificate_id = escape(
        str(
            certificate.get("certificate_id")
            or "Not issued"
        )
    )

    integrity = (
        "Integrity sealed"
        if certificate_result.get(
            "certificate_issued"
        )
        else "Waiting for verified approval"
    )

    detail = (
        "The exact hosted owner approval, candidate revision, packet integrity, "
        "and durable receipt chain are verified."
        if verification.get(
            "release_prerequisites_certified"
        )
        else
        "Tower will not issue a prerequisite certificate until the complete hosted owner chain verifies."
    )

    receipt_action = ""

    if (
        verification.get(
            "release_prerequisites_certified"
        )
        and verification.get("receipt_id")
    ):
        receipt_action = (
            f'<a class="button" '
            f'href="{RELEASE_REVIEW_PATH}/receipt/{receipt_id}">'
            "View source owner receipt</a>"
        )

    body = (
        f'<section class="hero" '
        f'data-tower-prerequisite-certification="{PREREQUISITE_PAGE_MARKER}">'

        '<span class="eyebrow">Tower owner verification</span>'

        '<h1>Release Prerequisite Certificate</h1>'

        '<p class="quiet">'
        'Verify the owner, exact hosted candidate, and decision receipt '
        'before release execution is even considered.'
        '</p>'

        f'<span class="chip">{state}</span>'
        '</section>'

        '<section class="grid">'

        '<article class="card">'
        '<span class="label">Owner verification</span>'
        f'<strong class="value">{owner_verified}</strong>'
        '</article>'

        '<article class="card">'
        '<span class="label">Release prerequisites</span>'
        f'<strong class="value">{prereqs}</strong>'
        '</article>'

        '<article class="card">'
        '<span class="label">Execution authority</span>'
        '<strong class="value">Locked</strong>'
        '</article>'

        '</section>'

        '<section class="card">'
        '<span class="eyebrow">Certified chain</span>'

        f'<p>{escape(detail)}</p>'

        f'<p>'
        f'<span class="label">Hosted revision</span><br>'
        f'<strong>{revision[:12]}</strong>'
        f'</p>'

        f'<p>'
        f'<span class="label">Owner receipt</span><br>'
        f'<strong>{receipt_id}</strong>'
        f'</p>'

        f'<p>'
        f'<span class="label">Certificate</span><br>'
        f'<strong>{certificate_id}</strong>'
        f'</p>'

        f'<span class="chip">{integrity}</span>'

        f'<div class="actions">'
        f'{receipt_action}'
        f'<a class="button" href="{RELEASE_REVIEW_PATH}/walkthrough">'
        'Back to hosted walkthrough'
        '</a>'
        '</div>'

        '<p class="notice">'
        'This certificate proves prerequisites only. '
        'It does not set STAGING_READY, deploy code, promote a release, '
        'submit broker orders, move capital, unlock Manual Live, '
        'or unlock Live Auto.'
        '</p>'

        '</section>'
    )

    return _page(
        "Tower · Release Prerequisite Certificate",
        body,
        back="/tower/owner-dashboard",
    )


def register_tower_release_prerequisite_certification_routes(app):

    marker = (
        "_tower_release_prerequisite_certification_routes_twr116_120"
    )

    if getattr(app, marker, False):
        return app

    @app.get(PREREQUISITE_PAGE_PATH)
    def tower_release_prerequisite_certificate_page():

        denied = _step_up_required()

        if denied is not None:
            return denied

        context = owner_release_session_context()

        verification = (
            project_hosted_owner_verification(
                owner_context=context
            )
        )

        certificate = (
            build_release_prerequisite_certificate(
                owner_context=context
            )
        )

        return hosted_release_prerequisite_html(
            verification,
            certificate,
        )

    @app.get(PREREQUISITE_VERIFICATION_JSON_PATH)
    def tower_release_prerequisite_verification_json():

        denied = _step_up_required()

        if denied is not None:
            return denied

        return jsonify(
            project_hosted_owner_verification(
                owner_context=owner_release_session_context()
            )
        )

    @app.get(PREREQUISITE_CERTIFICATION_JSON_PATH)
    def tower_release_prerequisite_certification_json():

        denied = _step_up_required()

        if denied is not None:
            return denied

        return jsonify(
            build_release_prerequisite_certificate(
                owner_context=owner_release_session_context()
            )
        )

    setattr(app, marker, True)

    return app
