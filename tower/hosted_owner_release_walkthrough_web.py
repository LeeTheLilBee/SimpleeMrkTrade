
"""Protected owner-facing hosted release-readiness walkthrough / TWR112-TWR115."""

from __future__ import annotations

from html import escape
from typing import Any

from flask import jsonify

from tower.hosted_owner_release_readiness import (
    HOSTED_AWAITING_CANDIDATE,
    HOSTED_AWAITING_OWNER_DECISION,
    HOSTED_OWNER_APPROVED_CERTIFIED,
    HOSTED_OWNER_HOLD_RECORDED,
    HOSTED_OWNER_REJECTION_RECORDED,
    certify_hosted_owner_release_walkthrough,
    project_hosted_owner_release_readiness,
)
from tower.hosted_owner_release_review import owner_release_session_context
from tower.hosted_owner_release_review_web import (
    RELEASE_REVIEW_PATH,
    _page,
    _publication_form,
    _step_up_required,
)


HOSTED_WALKTHROUGH_PATH = "/tower/owner/release-review/walkthrough"
HOSTED_READINESS_JSON_PATH = "/tower/owner/release-review/readiness.json"
HOSTED_CERTIFICATION_JSON_PATH = "/tower/owner/release-review/walkthrough/certification.json"
HOSTED_WALKTHROUGH_MARKER = "tower-hosted-owner-release-walkthrough-twr111-115"


def _walkthrough_action(readiness: dict[str, Any]) -> str:
    state = readiness.get("readiness_state")
    if state == HOSTED_AWAITING_CANDIDATE:
        return _publication_form(label="Run genuine hosted candidate check")
    if state == HOSTED_AWAITING_OWNER_DECISION:
        return f'<a class="button" href="{RELEASE_REVIEW_PATH}">Review hosted candidate</a>'
    if state in {
        HOSTED_OWNER_APPROVED_CERTIFIED,
        HOSTED_OWNER_HOLD_RECORDED,
        HOSTED_OWNER_REJECTION_RECORDED,
    }:
        receipt_id = escape(str(readiness.get("receipt_id") or ""))
        return (
            f'<a class="button" href="{RELEASE_REVIEW_PATH}/receipt/{receipt_id}">'
            "View verified owner receipt</a>"
        )
    return '<span class="chip">Owner action required</span>'


def hosted_owner_walkthrough_html(
    readiness: dict[str, Any],
    certification: dict[str, Any],
) -> str:
    host = escape(str(readiness.get("hosted_host") or "Not configured"))
    revision = escape(str(readiness.get("expected_revision") or "Not verified"))
    configuration = "Ready" if readiness.get("hosted_configuration_ready") else "Needs attention"
    owner_state = escape(str(readiness.get("readiness_state") or "UNAVAILABLE").replace("_", " "))
    next_action = escape(str(readiness.get("owner_next_action") or "Inspect hosted owner readiness."))
    result = "Verified" if certification.get("certified") else "Not complete"

    blockers = readiness.get("blockers", [])
    blocker_detail = "".join(
        f'<p><strong>{escape(str(item.get("code") or ""))}</strong><br>'
        f'{escape(str(item.get("owner_action") or ""))}</p>'
        for item in blockers
    )
    if not blocker_detail:
        blocker_detail = "<p>All hosted configuration and protected route checks are passing.</p>"

    body = (
        f'<section class="hero" data-tower-hosted-owner-walkthrough="{HOSTED_WALKTHROUGH_MARKER}">'
        '<span class="eyebrow">Tower hosted owner walkthrough</span>'
        '<h1>Hosted Release Readiness</h1><p class="quiet">See what is actually '
        'ready, resolve the next real blocker, and keep every execution boundary closed.</p>'
        f'<span class="chip">{owner_state}</span></section>'
        '<section class="grid">'
        f'<article class="card"><span class="label">Hosted identity</span>'
        f'<strong class="value">{host}</strong><p class="quiet">{revision[:12]}</p></article>'
        f'<article class="card"><span class="label">Durable owner storage</span>'
        f'<strong class="value">{configuration}</strong></article>'
        f'<article class="card"><span class="label">Owner walkthrough</span>'
        f'<strong class="value">{result}</strong></article></section>'
        '<section class="card"><span class="eyebrow">Your next move</span>'
        f'<p>{next_action}</p><div class="actions">{_walkthrough_action(readiness)}</div>'
        f'<details><summary>Hosted readiness details</summary>{blocker_detail}</details>'
        '<p class="notice">Deployment, staging promotion, broker execution, capital '
        'movement, Manual Live, and Live Auto remain locked.</p></section>'
    )
    return _page("Tower · Hosted Release Readiness", body, back=RELEASE_REVIEW_PATH)


def register_tower_hosted_owner_walkthrough_routes(app):
    marker = "_tower_hosted_owner_walkthrough_routes_twr111_115"
    if getattr(app, marker, False):
        return app

    @app.get(HOSTED_WALKTHROUGH_PATH)
    def tower_hosted_owner_release_walkthrough_page():
        denied = _step_up_required()
        if denied is not None:
            return denied
        context = owner_release_session_context()
        return hosted_owner_walkthrough_html(
            project_hosted_owner_release_readiness(owner_context=context),
            certify_hosted_owner_release_walkthrough(owner_context=context),
        )

    @app.get(HOSTED_READINESS_JSON_PATH)
    def tower_hosted_owner_release_readiness_json():
        denied = _step_up_required()
        if denied is not None:
            return denied
        return jsonify(
            project_hosted_owner_release_readiness(
                owner_context=owner_release_session_context()
            )
        )

    @app.get(HOSTED_CERTIFICATION_JSON_PATH)
    def tower_hosted_owner_release_walkthrough_certification_json():
        denied = _step_up_required()
        if denied is not None:
            return denied
        return jsonify(
            certify_hosted_owner_release_walkthrough(
                owner_context=owner_release_session_context()
            )
        )

    setattr(app, marker, True)
    return app
