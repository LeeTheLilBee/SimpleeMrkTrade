


"""Protected, owner-facing Tower release review room / TWR102-TWR105."""

from __future__ import annotations

import hmac
import secrets
from datetime import timedelta
from html import escape
from typing import Any
from urllib.parse import urlsplit

from flask import current_app, jsonify, redirect, request, session

from tower.hosted_owner_release_review import (
    APPROVE_RELEASE,
    HOLD_RELEASE,
    REJECT_RELEASE,
    build_owner_release_review,
    owner_release_session_context,
    read_owner_release_decision_receipts,
    record_owner_release_decision,
    verify_owner_release_decision_receipt,
)
from tower.hosted_owner_release_candidate_state import (
    DECISION_STATES,
    project_owner_release_candidate_state,
)
from tower.hosted_release_candidate_publication import publish_hosted_release_candidate
from tower.hosted_release_packet_provider import load_canonical_release_packet
from tower.tower_human_login_ob_launch import (
    SESSION_STEP_UP_UNTIL,
    SESSION_USERNAME,
    configured_step_up_minutes,
    owner_session_active,
    step_up_active,
    utc_now,
    verify_owner_credentials,
)


RELEASE_REVIEW_PATH = "/tower/owner/release-review"
RELEASE_REVIEW_JSON_PATH = "/tower/owner/release-review.json"
RELEASE_STEP_UP_PATH = "/tower/owner/release-review/step-up"
RELEASE_DECISION_PATH = "/tower/owner/release-review/decision"
RELEASE_PUBLICATION_PATH = "/tower/owner/release-review/publish"
RELEASE_STATE_PATH = "/tower/owner/release-review/state.json"
RELEASE_RECEIPT_PATH = "/tower/owner/release-review/receipt/<receipt_id>"
RELEASE_CSRF_SESSION_KEY = "tower_owner_release_review_csrf"
RELEASE_ROOM_MARKER = "tower-owner-release-review-room-twr101-105"

_PAGE_STYLE = """
:root{color-scheme:dark;--bg:#080611;--panel:rgba(24,19,40,.86);
--line:rgba(224,190,108,.22);--text:#faf7ff;--muted:#c0b5d4;
--gold:#efd58b;--violet:#a68cff;--green:#a9e7c1;--red:#ffb7be}
*{box-sizing:border-box}body{margin:0;min-height:100vh;font:15px/1.6
Inter,system-ui,sans-serif;color:var(--text);background:radial-gradient(
ellipse at 15% 0%,rgba(124,87,184,.22),transparent 36%),var(--bg)}
main{width:min(1060px,calc(100% - 36px));margin:0 auto;padding:44px 0 70px}
.back{color:var(--muted);text-decoration:none}.hero,.card{border:1px solid
var(--line);background:var(--panel);border-radius:26px;padding:24px}
.hero{margin:18px 0 20px;padding:32px}.eyebrow{font-size:11px;letter-spacing:
.17em;text-transform:uppercase;color:var(--gold);font-weight:800}
h1{font-size:clamp(32px,5vw,54px);line-height:1.08;margin:12px 0}
.quiet{color:var(--muted)}.grid{display:grid;grid-template-columns:
repeat(3,minmax(0,1fr));gap:14px;margin:20px 0}.label{font-size:11px;
letter-spacing:.11em;text-transform:uppercase;color:var(--muted)}
.value{display:block;color:var(--gold);font-size:18px;font-weight:750;
word-break:break-word;margin-top:8px}.chip{display:inline-flex;padding:7px
12px;border:1px solid var(--line);border-radius:999px;color:var(--gold)}
.actions{display:flex;gap:10px;flex-wrap:wrap;margin-top:18px}button,.button{
appearance:none;border:1px solid var(--line);border-radius:14px;padding:11px
16px;background:rgba(166,140,255,.12);color:var(--text);font-weight:700;
cursor:pointer;text-decoration:none}.approve{background:rgba(169,231,193,.14);
color:var(--green)}.reject{background:rgba(255,183,190,.10);color:var(--red)}
textarea,input{width:100%;margin-top:8px;padding:12px;border:1px solid
var(--line);border-radius:14px;color:var(--text);background:rgba(0,0,0,.24)}
details{margin-top:18px;color:var(--muted)}summary{cursor:pointer;color:
var(--gold)}.notice{margin-top:18px;padding:14px;border-radius:14px;
background:rgba(166,140,255,.10)}@media(max-width:720px){.grid{
grid-template-columns:1fr}.hero{padding:23px}}
"""


def _page(title: str, body: str, *, back: str = "/tower/owner-dashboard") -> str:
    return (
        '<!doctype html><html lang="en"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        f"<title>{escape(title)}</title><style>{_PAGE_STYLE}</style></head>"
        f'<body><main data-tower-release-room="{RELEASE_ROOM_MARKER}">'
        f'<a class="back" href="{escape(back)}">← Back to Tower</a>'
        f"{body}</main></body></html>"
    )


def _csrf_token() -> str:
    token = str(session.get(RELEASE_CSRF_SESSION_KEY) or "")
    if not token:
        token = secrets.token_urlsafe(32)
        session[RELEASE_CSRF_SESSION_KEY] = token
    return token


def _request_value(name: str) -> str:
    payload = request.get_json(silent=True) if request.is_json else request.form
    return str((payload or {}).get(name) or "").strip()


def _same_origin() -> bool:
    claimed = request.headers.get("Origin") or request.headers.get("Referer")
    if not claimed:
        return False
    origin = urlsplit(claimed)
    expected = urlsplit(request.host_url)
    return (
        origin.scheme.lower() == expected.scheme.lower()
        and origin.netloc.lower() == expected.netloc.lower()
    )


def _csrf_valid() -> bool:
    provided = _request_value("csrf_token") or request.headers.get("X-CSRF-Token", "")
    expected = str(session.get(RELEASE_CSRF_SESSION_KEY) or "")
    return bool(provided and expected and hmac.compare_digest(provided, expected))


def _deny(status: str, code: int):
    return jsonify({"status": status, "recorded": False}), code


def _owner_required():
    if not owner_session_active():
        return redirect("/tower/login")
    return None


def _step_up_required():
    denied = _owner_required()
    if denied is not None:
        return denied
    if not step_up_active():
        return redirect(RELEASE_STEP_UP_PATH)
    return None


def _publication_form(*, label: str = "Check hosted candidate") -> str:
    token = escape(_csrf_token())
    return (
        f'<form method="post" action="{RELEASE_PUBLICATION_PATH}">'
        f'<input type="hidden" name="csrf_token" value="{token}">'
        f'<div class="actions"><button type="submit">{escape(label)}</button></div>'
        "</form>"
    )


def _decided_candidate_html(state: dict[str, Any]) -> str:
    _csrf_token()
    decision = escape(str(state.get("owner_decision") or ""))
    revision = escape(str(state.get("expected_revision") or ""))
    receipt_id = escape(str(state.get("receipt_id") or ""))
    receipt_path = f"{RELEASE_REVIEW_PATH}/receipt/{receipt_id}"
    body = (
        '<section class="hero"><span class="eyebrow">Tower owner release state</span>'
        '<h1>Decision recorded</h1><p class="quiet">Your exact hosted candidate '
        f'decision is recorded and verified.</p><span class="chip">{decision}'
        '</span></section><section class="grid">'
        f'<article class="card"><span class="label">Candidate</span>'
        f'<strong class="value">{revision[:12]}</strong></article>'
        '<article class="card"><span class="label">Receipt integrity</span>'
        '<strong class="value">Verified</strong></article>'
        '<article class="card"><span class="label">Execution</span>'
        '<strong class="value">Still locked</strong></article></section>'
        '<section class="card"><span class="eyebrow">Owner decision</span>'
        '<p class="quiet">This candidate already has an owner decision. A second '
        'decision is not available.</p>'
        f'<a class="button" href="{receipt_path}">View verified receipt</a>'
        f'{_publication_form(label="Check for a newly deployed candidate")}'
        '<p class="notice">Deployment, promotion, broker execution, capital movement, '
        'and live trading remain locked.</p></section>'
    )
    return _page("Tower · Owner Release Decision State", body)


def _review_room_html(candidate: dict[str, Any]) -> str:
    if not candidate.get("reviewable"):
        reason = escape(str(candidate.get("reason") or "packet_source_missing"))
        return _page(
            "Tower · Owner Release Review",
            '<section class="hero"><span class="eyebrow">Tower owner review</span>'
            '<h1>Release Review</h1><p class="quiet">There is no sealed, current '
            'release candidate available for owner review.</p><span class="chip">'
            'NO REVIEWABLE CANDIDATE</span></section><section class="card">'
            f'<span class="label">Why the room is waiting</span><p>{reason}</p>'
            "<p class=\"quiet\">No decision or release action is available.</p>"
            f"{_publication_form()}"
            '<p><a class="back" href="/tower/owner/release-review/walkthrough">'
            'View hosted readiness and your next move</a></p></section>',
        )

    state = project_owner_release_candidate_state(
        owner_context=owner_release_session_context()
    )
    if state.get("candidate_state") in DECISION_STATES.values():
        return _decided_candidate_html(state)
    if state.get("candidate_state") == "DECISION_STATE_UNAVAILABLE":
        return _page(
            "Tower · Owner Release Decision State",
            '<section class="hero"><span class="eyebrow">Tower owner review</span>'
            '<h1>Decision state unavailable</h1><p class="quiet">Tower could not '
            'verify the existing owner decision ledger. All decisions remain locked.'
            '</p></section>',
        )

    review = build_owner_release_review(
        candidate["packet"],
        owner_context=owner_release_session_context(),
    )
    if not review.get("review_allowed"):
        return _page(
            "Tower · Owner Release Review",
            '<section class="hero"><span class="eyebrow">Tower owner review</span>'
            '<h1>Review unavailable</h1><p class="quiet">Owner clearance or packet '
            'integrity could not be verified.</p></section>',
        )

    csrf = escape(_csrf_token())
    packet_hash = escape(str(review["packet_integrity_hash"]))
    revision = escape(str(review["expected_revision"]))
    recommendation = escape(str(review["release_recommendation"]))
    route_count = escape(str(review.get("critical_route_count") or 0))
    buttons = []
    for decision in review["allowed_decisions"]:
        css = "approve" if decision == APPROVE_RELEASE else "reject" if decision == REJECT_RELEASE else ""
        label = {
            APPROVE_RELEASE: "Approve candidate",
            HOLD_RELEASE: "Place on hold",
            REJECT_RELEASE: "Reject candidate",
        }[decision]
        buttons.append(
            f'<button class="{css}" type="submit" name="decision" '
            f'value="{escape(decision)}">{escape(label)}</button>'
        )

    failures = review.get("failures") or review.get("validation_errors") or []
    detail = "".join(f"<p>{escape(str(item))}</p>" for item in failures)
    if not detail:
        detail = "<p>All required hosted candidate checks are passing.</p>"

    body = (
        '<section class="hero"><span class="eyebrow">Tower owner review</span>'
        '<h1>Release Review</h1><p class="quiet">Review the exact hosted '
        'candidate, record your decision, and keep every execution gate closed.</p>'
        f'<span class="chip">{recommendation}</span></section>'
        '<section class="grid">'
        f'<article class="card"><span class="label">Candidate</span>'
        f'<strong class="value">{revision[:12]}</strong></article>'
        f'<article class="card"><span class="label">Critical routes</span>'
        f'<strong class="value">{route_count} verified</strong></article>'
        '<article class="card"><span class="label">Execution</span>'
        '<strong class="value">Still locked</strong></article></section>'
        '<section class="card"><span class="eyebrow">Your decision</span>'
        '<p class="quiet">Approval records your owner decision only. It does '
        'not deploy, move capital, place a trade, or change a live mode.</p>'
        f'<form method="post" action="{RELEASE_DECISION_PATH}">'
        f'<input type="hidden" name="csrf_token" value="{csrf}">'
        f'<input type="hidden" name="packet_integrity_hash" value="{packet_hash}">'
        f'<input type="hidden" name="expected_revision" value="{revision}">'
        '<label for="release-reason">Decision reason</label>'
        '<textarea id="release-reason" name="reason" maxlength="1000" '
        'rows="3" required placeholder="Why are you making this decision?"></textarea>'
        f'<div class="actions">{"".join(buttons)}</div></form>'
        f'<details><summary>Candidate evidence</summary>{detail}</details>'
        f'{_publication_form(label="Refresh hosted candidate")}</section>'
    )
    return _page("Tower · Owner Release Review", body)


def _receipt_html(receipt: dict[str, Any]) -> str:
    decision = escape(str(receipt.get("decision") or ""))
    revision = escape(str(receipt.get("expected_revision") or ""))
    receipt_id = escape(str(receipt.get("receipt_id") or ""))
    timestamp = escape(str(receipt.get("decided_at_utc") or ""))
    reason = escape(str(receipt.get("decision_reason") or ""))
    verified = verify_owner_release_decision_receipt(receipt)
    integrity = "Verified" if verified.get("valid") else "INVALID — REVIEW REQUIRED"
    body = (
        '<section class="hero"><span class="eyebrow">Tower owner receipt</span>'
        '<h1>Decision recorded</h1><p class="quiet">Your decision has been '
        f'recorded for the exact hosted candidate.</p><span class="chip">{decision}'
        '</span></section><section class="grid">'
        f'<article class="card"><span class="label">Candidate</span><strong '
        f'class="value">{revision[:12]}</strong></article>'
        f'<article class="card"><span class="label">Receipt integrity</span>'
        f'<strong class="value">{integrity}</strong></article>'
        '<article class="card"><span class="label">Execution</span>'
        '<strong class="value">Still locked</strong></article></section>'
        '<section class="card"><span class="label">Owner reason</span>'
        f'<p>{reason}</p><details><summary>Receipt details</summary>'
        f'<p>Reference: {receipt_id}</p><p>Recorded: {timestamp}</p></details>'
        '<p class="notice">A separate Tower release-execution gate is still '
        'required. No deployment or trading action was performed.</p></section>'
    )
    return _page("Tower · Owner Decision Receipt", body, back=RELEASE_REVIEW_PATH)


def register_tower_owner_release_review_routes(app):
    marker = "_tower_owner_release_review_routes_twr101_105"
    if getattr(app, marker, False):
        return app

    @app.get(RELEASE_STEP_UP_PATH)
    def tower_owner_release_step_up_page():
        denied = _owner_required()
        if denied is not None:
            return denied
        token = escape(_csrf_token())
        body = (
            '<section class="hero"><span class="eyebrow">Tower owner verification</span>'
            '<h1>Confirm it is you</h1><p class="quiet">Verify your Tower password '
            'before reviewing a hosted release candidate. You will remain in Tower.'
            '</p></section><section class="card">'
            f'<form method="post" action="{RELEASE_STEP_UP_PATH}">'
            f'<input type="hidden" name="csrf_token" value="{token}">'
            '<label for="release-password">Tower owner password</label>'
            '<input id="release-password" name="password" type="password" '
            'autocomplete="current-password" required>'
            '<div class="actions"><button type="submit">Verify and return to '
            'release review</button></div></form></section>'
        )
        return _page("Tower · Release Review Verification", body)

    @app.post(RELEASE_STEP_UP_PATH)
    def tower_owner_release_step_up_submit():
        denied = _owner_required()
        if denied is not None:
            return denied
        if not _same_origin() or not _csrf_valid():
            return _deny("tower_owner_release_step_up_request_rejected", 403)
        if not verify_owner_credentials(
            username=str(session.get(SESSION_USERNAME) or ""),
            password=_request_value("password"),
        ):
            return _deny("tower_owner_release_step_up_denied", 403)
        session[SESSION_STEP_UP_UNTIL] = (
            utc_now() + timedelta(minutes=configured_step_up_minutes())
        ).isoformat()
        return redirect(RELEASE_REVIEW_PATH, code=303)

    @app.get(RELEASE_REVIEW_PATH)
    def tower_owner_release_review_page():
        denied = _step_up_required()
        if denied is not None:
            return denied
        return _review_room_html(load_canonical_release_packet())

    @app.get(RELEASE_REVIEW_JSON_PATH)
    def tower_owner_release_review_json():
        denied = _step_up_required()
        if denied is not None:
            return denied
        candidate = load_canonical_release_packet()
        if not candidate.get("reviewable"):
            safe = dict(candidate)
            safe.pop("packet", None)
            return jsonify(safe), 409
        return jsonify(
            {
                "candidate_state": candidate["candidate_state"],
                "owner_decision_state": project_owner_release_candidate_state(
                    owner_context=owner_release_session_context()
                ),
                "review": build_owner_release_review(
                    candidate["packet"],
                    owner_context=owner_release_session_context(),
                ),
                "csrf_token": _csrf_token(),
            }
        )

    @app.get(RELEASE_STATE_PATH)
    def tower_owner_release_candidate_state_json():
        denied = _step_up_required()
        if denied is not None:
            return denied
        return jsonify(
            project_owner_release_candidate_state(
                owner_context=owner_release_session_context()
            )
        )

    @app.post(RELEASE_PUBLICATION_PATH)
    def tower_owner_release_candidate_publish():
        denied = _step_up_required()
        if denied is not None:
            return denied
        if not _same_origin() or not _csrf_valid():
            return _deny("tower_owner_release_publication_request_rejected", 403)
        result = publish_hosted_release_candidate()
        if not result.get("published"):
            if request.is_json:
                return jsonify(result), 422
            reason = escape(str(result.get("reason") or "hosted_candidate_unavailable"))
            body = (
                '<section class="hero"><span class="eyebrow">Tower owner review</span>'
                '<h1>Candidate check unavailable</h1><p class="quiet">Tower could '
                'not publish a genuine verified hosted candidate.</p>'
                f'<span class="chip">{reason}</span></section>'
                '<section class="card"><p class="quiet">No candidate was fabricated '
                'and no release or trading boundary was opened.</p></section>'
            )
            return _page("Tower · Hosted Candidate Check", body), 422
        if request.is_json:
            return jsonify(result), 201
        return redirect(RELEASE_REVIEW_PATH, code=303)

    @app.post(RELEASE_DECISION_PATH)
    def tower_owner_release_decision_submit():
        denied = _step_up_required()
        if denied is not None:
            return denied
        if not _same_origin() or not _csrf_valid():
            return _deny("tower_owner_release_decision_request_rejected", 403)

        candidate = load_canonical_release_packet()
        if not candidate.get("reviewable"):
            return _deny("tower_owner_release_candidate_unavailable", 409)

        packet = candidate["packet"]
        supplied_hash = _request_value("packet_integrity_hash")
        supplied_revision = _request_value("expected_revision").lower()
        expected_hash = str(packet.get("packet_integrity_hash") or "")
        expected_revision = str(packet.get("expected_revision") or "").lower()

        if (
            not supplied_hash
            or not hmac.compare_digest(supplied_hash, expected_hash)
            or supplied_revision != expected_revision
        ):
            return _deny("tower_owner_release_candidate_stale", 409)

        result = record_owner_release_decision(
            packet,
            owner_context=owner_release_session_context(),
            decision=_request_value("decision"),
            reason=_request_value("reason"),
        )
        if not result.get("recorded"):
            code = 409 if result.get("duplicate") else 422
            if result.get("status") == "tower_owner_release_receipt_persistence_failed":
                code = 503
            return jsonify(result), code

        session.pop(RELEASE_CSRF_SESSION_KEY, None)
        if request.is_json:
            return jsonify(result), 201
        return redirect(
            RELEASE_REVIEW_PATH + "/receipt/" + result["receipt"]["receipt_id"],
            code=303,
        )

    @app.get(RELEASE_RECEIPT_PATH)
    def tower_owner_release_receipt_page(receipt_id: str):
        denied = _step_up_required()
        if denied is not None:
            return denied
        result = read_owner_release_decision_receipts(
            owner_context=owner_release_session_context()
        )
        if result.get("status") != "tower_owner_release_receipts_ready":
            return _deny("tower_owner_release_receipts_unavailable", 503)
        for receipt in result["receipts"]:
            if receipt.get("receipt_id") == receipt_id:
                verification = verify_owner_release_decision_receipt(receipt)
                if not verification.get("valid"):
                    return _deny("tower_owner_release_receipt_integrity_invalid", 409)
                return _receipt_html(receipt)
        return _deny("tower_owner_release_receipt_not_found", 404)

    setattr(app, marker, True)

    from tower.hosted_owner_release_walkthrough_web import (
        register_tower_hosted_owner_walkthrough_routes,
    )

    register_tower_hosted_owner_walkthrough_routes(app)
    return app
