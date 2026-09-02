


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
:root {
    color-scheme: dark;

    --bg:
        #05030a;

    --panel:
        rgba(255,255,255,.058);

    --panel-strong:
        rgba(255,255,255,.092);

    --line:
        rgba(255,255,255,.115);

    --line-gold:
        rgba(241,210,132,.31);

    --text:
        #fffaff;

    --muted:
        #c3b7d1;

    --dim:
        #8f839f;

    --gold:
        #f1d284;

    --violet:
        #9b7af0;

    --green:
        #b8f3cf;

    --red:
        #ffc0c6;

    --amber:
        #ffdda7;
}


* {
    box-sizing:
        border-box;
}


body {
    margin:
        0;

    min-height:
        100vh;

    color:
        var(--text);

    font:
        15px/1.6
        Inter,
        system-ui,
        -apple-system,
        BlinkMacSystemFont,
        "Segoe UI",
        sans-serif;

    background:
        radial-gradient(
            circle at 8% 4%,
            rgba(155,122,240,.26),
            transparent 34rem
        ),
        radial-gradient(
            circle at 91% 6%,
            rgba(241,210,132,.11),
            transparent 27rem
        ),
        linear-gradient(
            145deg,
            #030207,
            #080512 52%,
            #05030a
        );
}


main {
    width:
        min(
            1180px,
            calc(100% - 34px)
        );

    margin:
        0 auto;

    padding:
        34px 0 70px;
}


.back {
    display:
        inline-flex;

    align-items:
        center;

    min-height:
        38px;

    padding:
        0 12px;

    border:
        1px solid var(--line);

    border-radius:
        999px;

    color:
        var(--muted);

    text-decoration:
        none;

    font-weight:
        800;
}


.hero,
.card {
    border:
        1px solid var(--line);

    background:
        var(--panel);

    box-shadow:
        0 18px 65px rgba(0,0,0,.20);
}


.hero {
    margin:
        16px 0 18px;

    padding:
        30px;

    border-color:
        var(--line-gold);

    border-radius:
        28px;

    background:
        radial-gradient(
            circle at 88% 9%,
            rgba(241,210,132,.12),
            transparent 29%
        ),
        linear-gradient(
            135deg,
            rgba(155,122,240,.16),
            rgba(255,255,255,.035)
        );
}


.card {
    padding:
        20px;

    border-radius:
        21px;
}


.eyebrow,
.label {
    font-size:
        11px;

    letter-spacing:
        .14em;

    text-transform:
        uppercase;

    font-weight:
        900;
}


.eyebrow {
    color:
        var(--gold);
}


.label {
    color:
        var(--dim);
}


h1 {
    margin:
        10px 0 10px;

    font-size:
        clamp(
            2.7rem,
            6vw,
            5.7rem
        );

    line-height:
        .92;

    letter-spacing:
        -.052em;
}


h2 {
    margin:
        8px 0 10px;

    font-size:
        1.55rem;
}


.quiet {
    color:
        var(--muted);
}


.value {
    display:
        block;

    margin-top:
        8px;

    color:
        var(--gold);

    font-size:
        18px;

    font-weight:
        850;

    word-break:
        break-word;
}


.grid {
    display:
        grid;

    grid-template-columns:
        repeat(
            3,
            minmax(0,1fr)
        );

    gap:
        12px;

    margin:
        18px 0;
}


.chip {
    display:
        inline-flex;

    align-items:
        center;

    min-height:
        34px;

    padding:
        0 12px;

    border:
        1px solid var(--line-gold);

    border-radius:
        999px;

    color:
        var(--gold);

    font-size:
        .78rem;

    font-weight:
        900;
}


.actions {
    display:
        flex;

    gap:
        10px;

    flex-wrap:
        wrap;

    margin-top:
        17px;
}


button,
.button {
    appearance:
        none;

    min-height:
        44px;

    padding:
        0 16px;

    border:
        1px solid var(--line);

    border-radius:
        14px;

    color:
        var(--text);

    background:
        rgba(155,122,240,.12);

    cursor:
        pointer;

    text-decoration:
        none;

    font-weight:
        850;
}


button:hover,
.button:hover {
    border-color:
        var(--line-gold);
}


.approve {
    border-color:
        rgba(184,243,207,.30);

    color:
        var(--green);

    background:
        rgba(184,243,207,.09);
}


.reject {
    border-color:
        rgba(255,192,198,.26);

    color:
        var(--red);

    background:
        rgba(255,192,198,.075);
}


textarea,
input {
    width:
        100%;

    margin-top:
        8px;

    padding:
        12px;

    border:
        1px solid var(--line);

    border-radius:
        14px;

    color:
        var(--text);

    background:
        rgba(0,0,0,.26);
}


textarea:focus,
input:focus {
    outline:
        1px solid var(--line-gold);

    border-color:
        var(--line-gold);
}


.notice {
    margin-top:
        17px;

    padding:
        14px;

    border:
        1px solid var(--line);

    border-radius:
        14px;

    color:
        var(--muted);

    background:
        rgba(155,122,240,.08);
}


details {
    margin-top:
        15px;

    overflow:
        hidden;

    border:
        1px solid var(--line);

    border-radius:
        17px;

    color:
        var(--muted);

    background:
        rgba(255,255,255,.025);
}


summary {
    cursor:
        pointer;

    list-style:
        none;

    padding:
        15px 17px;

    color:
        var(--gold);

    font-weight:
        850;
}


summary::-webkit-details-marker {
    display:
        none;
}


summary:after {
    content:
        "+";

    float:
        right;
}


details[open] summary:after {
    content:
        "–";
}


.release-product-hero {
    display:
        grid;

    grid-template-columns:
        minmax(0,1.5fr)
        minmax(250px,.5fr);

    gap:
        22px;

    align-items:
        end;
}


.release-product-hero-copy {
    max-width:
        760px;

    margin:
        0;

    color:
        var(--muted);
}


.release-hero-state {
    padding:
        18px;

    border:
        1px solid var(--line);

    border-radius:
        19px;

    background:
        rgba(255,255,255,.045);
}


.release-hero-state span {
    display:
        block;

    color:
        var(--dim);

    text-transform:
        uppercase;

    letter-spacing:
        .11em;

    font-size:
        .7rem;

    font-weight:
        900;
}


.release-hero-state strong {
    display:
        block;

    margin-top:
        8px;

    color:
        var(--gold);

    font-size:
        1.05rem;
}


.release-summary-grid {
    display:
        grid;

    grid-template-columns:
        repeat(
            4,
            minmax(0,1fr)
        );

    gap:
        12px;

    margin:
        16px 0;
}


.release-summary-card {
    min-height:
        142px;

    padding:
        17px;

    border:
        1px solid var(--line);

    border-radius:
        19px;

    background:
        linear-gradient(
            180deg,
            rgba(255,255,255,.058),
            rgba(255,255,255,.025)
        );
}


.release-summary-card span {
    display:
        block;

    color:
        var(--dim);

    text-transform:
        uppercase;

    letter-spacing:
        .10em;

    font-size:
        .68rem;

    font-weight:
        900;
}


.release-summary-card strong {
    display:
        block;

    margin:
        8px 0 7px;

    color:
        var(--gold);

    font-size:
        1rem;
}


.release-summary-card p {
    margin:
        0;

    color:
        var(--muted);

    line-height:
        1.42;

    font-size:
        .84rem;
}


.release-decision-panel {
    padding:
        24px;

    border:
        1px solid var(--line-gold);

    border-radius:
        24px;

    background:
        radial-gradient(
            circle at 91% 9%,
            rgba(241,210,132,.08),
            transparent 30%
        ),
        rgba(255,255,255,.035);
}


.release-decision-panel > p {
    max-width:
        820px;
}


.release-boundary {
    display:
        grid;

    grid-template-columns:
        repeat(
            3,
            minmax(0,1fr)
        );

    gap:
        9px;

    margin:
        16px 0;
}


.release-boundary div {
    padding:
        12px;

    border:
        1px solid var(--line);

    border-radius:
        14px;

    color:
        var(--muted);

    background:
        rgba(0,0,0,.15);

    font-size:
        .8rem;
}


.release-boundary strong {
    display:
        block;

    color:
        var(--gold);

    margin-bottom:
        3px;
}


.release-evidence-body,
.release-backstage-body {
    padding:
        0 17px 17px;
}


.release-evidence-list {
    margin:
        4px 0 0;

    padding-left:
        20px;
}


.release-evidence-list li {
    margin:
        6px 0;
}


.release-backstage {
    border-color:
        rgba(255,255,255,.08);
}


.release-backstage a {
    display:
        inline-flex;

    align-items:
        center;

    min-height:
        38px;

    padding:
        0 13px;

    border:
        1px solid var(--line);

    border-radius:
        999px;

    color:
        var(--muted);

    text-decoration:
        none;

    font-weight:
        850;
}


.release-waiting-panel {
    padding:
        22px;

    border:
        1px solid var(--line);

    border-radius:
        22px;

    background:
        rgba(255,255,255,.035);
}


.release-waiting-panel p {
    color:
        var(--muted);
}


@media (
    max-width: 900px
) {

    .release-summary-grid {
        grid-template-columns:
            repeat(
                2,
                minmax(0,1fr)
            );
    }


    .release-product-hero {
        grid-template-columns:
            1fr;
    }
}


@media (
    max-width: 720px
) {

    main {
        width:
            min(
                100% - 24px,
                1180px
            );
    }


    .grid,
    .release-summary-grid,
    .release-boundary {
        grid-template-columns:
            1fr;
    }


    .hero {
        padding:
            22px;
    }
}
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


def _review_room_html(
    candidate: dict[str, Any],
) -> str:

    from tower.hosted_owner_release_readiness import (
        owner_hosted_readiness_dashboard_snapshot,
    )

    from tower.hosted_release_prerequisite_certification import (
        owner_prerequisite_certificate_dashboard_snapshot,
    )


    readiness = (
        owner_hosted_readiness_dashboard_snapshot()
    )

    prerequisite = (
        owner_prerequisite_certificate_dashboard_snapshot()
    )


    readiness_state = escape(
        str(
            readiness.get(
                "state"
            )
            or "READINESS_UNAVAILABLE"
        )
    )

    readiness_label = escape(
        str(
            readiness.get(
                "label"
            )
            or "Hosted readiness unavailable"
        )
    )

    readiness_detail = escape(
        str(
            readiness.get(
                "detail"
            )
            or "Review hosted Tower readiness."
        )
    )


    prerequisite_state = escape(
        str(
            prerequisite.get(
                "state"
            )
            or "PREREQUISITE_STATE_UNAVAILABLE"
        )
    )

    prerequisite_label = escape(
        str(
            prerequisite.get(
                "label"
            )
            or "Prerequisite certificate unavailable"
        )
    )

    prerequisite_detail = escape(
        str(
            prerequisite.get(
                "detail"
            )
            or "Tower could not verify the prerequisite chain."
        )
    )


    evidence_backstage = f"""
    <details
      class="release-backstage"
      data-tower-release-evidence-backstage="true"
    >
      <summary>
        Evidence & readiness details
      </summary>

      <div class="release-backstage-body">

        <p>
          Detailed walkthrough proof, readiness evidence,
          certification records, and verification material
          stay backstage.
        </p>

        <p>
          Readiness · {readiness_label}
          <br>
          Prerequisite certificate · {prerequisite_label}
        </p>

        <a
          href="/tower/owner/evidence"
          data-tower-release-evidence-basement-entry="true"
        >
          Open evidence basement
        </a>

      </div>

    </details>
    """


    # ----------------------------------------------------------------------------------------------------------
    # NO REVIEWABLE CANDIDATE
    # ----------------------------------------------------------------------------------------------------------

    if not candidate.get(
        "reviewable"
    ):

        reason = escape(
            str(
                candidate.get(
                    "reason"
                )
                or "packet_source_missing"
            )
        )


        body = f"""
        <section
          class="hero release-product-hero"
          data-tower-release-review-product="twr166-170"
          data-tower-release-candidate-state="unavailable"
          data-tower-owner-decision-surface="unavailable"
        >

          <div>

            <span class="eyebrow">
              Tower · owner decision room
            </span>

            <h1>
              Release Review
            </h1>

            <p class="release-product-hero-copy">
              There is no sealed, current release candidate
              available for owner review.
            </p>

          </div>


          <div class="release-hero-state">

            <span>
              Candidate
            </span>

            <strong>
              NO REVIEWABLE CANDIDATE
            </strong>

          </div>

        </section>


        <section
          class="release-summary-grid"
          data-tower-release-readiness-summary="true"
        >

          <article class="release-summary-card">

            <span>
              Candidate availability
            </span>

            <strong>
              Waiting
            </strong>

            <p>
              {reason}
            </p>

          </article>


          <article
            class="release-summary-card"
            data-tower-hosted-readiness="{readiness_state}"
          >

            <span>
              Hosted readiness
            </span>

            <strong>
              {readiness_label}
            </strong>

            <p>
              {readiness_detail}
            </p>

          </article>


          <article
            class="release-summary-card"
            data-tower-prerequisite-summary="{prerequisite_state}"
          >

            <span>
              Prerequisite state
            </span>

            <strong>
              {prerequisite_label}
            </strong>

            <p>
              {prerequisite_detail}
            </p>

          </article>


          <article
            class="release-summary-card"
            data-tower-release-execution="locked"
          >

            <span>
              Execution
            </span>

            <strong>
              Still locked
            </strong>

            <p>
              No release execution authority exists here.
            </p>

          </article>

        </section>


        <section
          class="release-waiting-panel"
          data-tower-release-next-move="check-candidate"
        >

          <span class="eyebrow">
            What you can do now
          </span>

          <h2>
            Check for a hosted candidate
          </h2>

          <p>
            Tower will not manufacture a candidate,
            decision state, or release-ready claim.
          </p>

          {_publication_form()}

          <p class="notice">
            No decision or release action is available.
            Deployment, promotion, broker submission,
            capital movement, Manual Live, and Live Auto
            remain locked.
          </p>

        </section>


        {evidence_backstage}
        """


        return _page(
            "Tower · Owner Release Review",
            body,
        )


    # ----------------------------------------------------------------------------------------------------------
    # PROJECT EXACT OWNER CANDIDATE STATE
    # ----------------------------------------------------------------------------------------------------------

    state = (
        project_owner_release_candidate_state(
            owner_context=
                owner_release_session_context()
        )
    )


    candidate_state = escape(
        str(
            state.get(
                "candidate_state"
            )
            or "CANDIDATE_STATE_UNAVAILABLE"
        )
    )


    # Existing decided-state projection remains authoritative.
    if (
        state.get(
            "candidate_state"
        )
        in DECISION_STATES.values()
    ):

        return (
            _decided_candidate_html(
                state
            )
        )


    # Fail closed when the decision ledger cannot be verified.
    if (
        state.get(
            "candidate_state"
        )
        == "DECISION_STATE_UNAVAILABLE"
    ):

        body = f"""
        <section
          class="hero release-product-hero"
          data-tower-release-review-product="twr166-170"
          data-tower-release-candidate-state="DECISION_STATE_UNAVAILABLE"
          data-tower-owner-decision-surface="locked"
        >

          <div>

            <span class="eyebrow">
              Tower · owner decision room
            </span>

            <h1>
              Decision state unavailable
            </h1>

            <p class="release-product-hero-copy">
              Tower could not verify the existing owner
              decision ledger. All decisions remain locked.
            </p>

          </div>


          <div class="release-hero-state">

            <span>
              Execution
            </span>

            <strong>
              Still locked
            </strong>

          </div>

        </section>


        {evidence_backstage}
        """


        return _page(
            "Tower · Owner Release Decision State",
            body,
        )


    # ----------------------------------------------------------------------------------------------------------
    # BUILD EXISTING AUTHORITATIVE REVIEW CONTRACT
    # ----------------------------------------------------------------------------------------------------------

    review = (
        build_owner_release_review(
            candidate[
                "packet"
            ],
            owner_context=
                owner_release_session_context(),
        )
    )


    if not review.get(
        "review_allowed"
    ):

        body = f"""
        <section
          class="hero release-product-hero"
          data-tower-release-review-product="twr166-170"
          data-tower-release-candidate-state="{candidate_state}"
          data-tower-owner-decision-surface="locked"
        >

          <div>

            <span class="eyebrow">
              Tower · owner decision room
            </span>

            <h1>
              Review unavailable
            </h1>

            <p class="release-product-hero-copy">
              Owner clearance or packet integrity could
              not be verified.
            </p>

          </div>


          <div class="release-hero-state">

            <span>
              Execution
            </span>

            <strong>
              Still locked
            </strong>

          </div>

        </section>


        {evidence_backstage}
        """


        return _page(
            "Tower · Owner Release Review",
            body,
        )


    # ----------------------------------------------------------------------------------------------------------
    # CURRENT REVIEWABLE CANDIDATE
    # ----------------------------------------------------------------------------------------------------------

    csrf = escape(
        _csrf_token()
    )


    packet_hash = escape(
        str(
            review[
                "packet_integrity_hash"
            ]
        )
    )


    revision = escape(
        str(
            review[
                "expected_revision"
            ]
        )
    )


    recommendation = escape(
        str(
            review[
                "release_recommendation"
            ]
        )
    )


    route_value = review.get(
        "critical_route_count"
    )


    route_count = (
        "—"
        if route_value is None
        else escape(
            str(
                route_value
            )
        )
    )


    # ----------------------------------------------------------------------------------------------------------
    # EXISTING DECISION SEMANTICS — UNCHANGED
    # ----------------------------------------------------------------------------------------------------------

    buttons = []


    for decision in review[
        "allowed_decisions"
    ]:

        css = (
            "approve"
            if decision
            == APPROVE_RELEASE
            else (
                "reject"
                if decision
                == REJECT_RELEASE
                else ""
            )
        )


        label = {
            APPROVE_RELEASE:
                "Approve candidate",

            HOLD_RELEASE:
                "Place on hold",

            REJECT_RELEASE:
                "Reject candidate",
        }[
            decision
        ]


        buttons.append(
            f"""
            <button
              class="{css}"
              type="submit"
              name="decision"
              value="{escape(decision)}"
            >
              {escape(label)}
            </button>
            """
        )


    # ----------------------------------------------------------------------------------------------------------
    # CANDIDATE EVIDENCE — DETAIL, NOT THE PRIMARY EXPERIENCE
    # ----------------------------------------------------------------------------------------------------------

    failures = (
        review.get(
            "failures"
        )
        or review.get(
            "validation_errors"
        )
        or []
    )


    if failures:

        evidence_items = "".join(
            f"""
            <li>
              {escape(str(item))}
            </li>
            """
            for item
            in failures
        )

    else:

        evidence_items = """
        <li>
          All required hosted candidate checks are passing.
        </li>
        """


    # ----------------------------------------------------------------------------------------------------------
    # PRODUCT SURFACE
    # ----------------------------------------------------------------------------------------------------------

    body = f"""
    <section
      class="hero release-product-hero"
      data-tower-release-review-product="twr166-170"
      data-tower-release-candidate-state="{candidate_state}"
    >

      <div>

        <span class="eyebrow">
          Tower · owner decision room
        </span>

        <h1>
          Release Review
        </h1>

        <p class="release-product-hero-copy">
          Review the exact hosted candidate,
          understand what Tower currently knows,
          and record your owner decision.
          Every execution gate remains closed.
        </p>

      </div>


      <div class="release-hero-state">

        <span>
          Tower recommendation
        </span>

        <strong>
          {recommendation}
        </strong>

      </div>

    </section>


    <section
      class="release-summary-grid"
      data-tower-release-readiness-summary="true"
    >

      <article
        class="release-summary-card"
        data-tower-current-candidate="{revision}"
      >

        <span>
          Candidate
        </span>

        <strong>
          {revision[:12]}
        </strong>

        <p>
          Exact hosted candidate currently under owner review.
        </p>

      </article>


      <article
        class="release-summary-card"
        data-tower-hosted-readiness="{readiness_state}"
      >

        <span>
          Hosted readiness
        </span>

        <strong>
          {readiness_label}
        </strong>

        <p>
          {readiness_detail}
        </p>

      </article>


      <article
        class="release-summary-card"
        data-tower-prerequisite-summary="{prerequisite_state}"
      >

        <span>
          Prerequisite state
        </span>

        <strong>
          {prerequisite_label}
        </strong>

        <p>
          {prerequisite_detail}
        </p>

      </article>


      <article
        class="release-summary-card"
        data-tower-release-execution="locked"
      >

        <span>
          Execution
        </span>

        <strong>
          Still locked
        </strong>

        <p>
          This room records an owner decision only.
        </p>

      </article>

    </section>


    <section
      class="release-decision-panel"
      data-tower-owner-decision-surface="true"
    >

      <span class="eyebrow">
        Your decision
      </span>

      <h2>
        What do you want Tower to record?
      </h2>

      <p class="quiet">
        Approval records your owner decision only.
        It does not deploy, promote, move capital,
        place a trade, submit to a broker,
        authorize Manual Live, or activate Live Auto.
      </p>


      <div
        class="release-boundary"
        data-tower-release-decision-boundary="record-only"
      >

        <div>
          <strong>
            APPROVE
          </strong>
          Records approval for this exact candidate.
        </div>

        <div>
          <strong>
            HOLD
          </strong>
          Records that this exact candidate should wait.
        </div>

        <div>
          <strong>
            REJECT
          </strong>
          Records rejection of this exact candidate.
        </div>

      </div>


      <form
        method="post"
        action="{RELEASE_DECISION_PATH}"
        data-tower-release-decision-form="true"
      >

        <input
          type="hidden"
          name="csrf_token"
          value="{csrf}"
        >

        <input
          type="hidden"
          name="packet_integrity_hash"
          value="{packet_hash}"
        >

        <input
          type="hidden"
          name="expected_revision"
          value="{revision}"
        >


        <label for="release-reason">
          Decision reason
        </label>

        <textarea
          id="release-reason"
          name="reason"
          maxlength="1000"
          rows="3"
          required
          placeholder="Why are you making this decision?"
        ></textarea>


        <div class="actions">
          {"".join(buttons)}
        </div>

      </form>


      <p
        class="notice"
        data-tower-release-execution-boundary="closed"
      >
        Decision recording is not release execution.
        A separate Tower release-execution gate remains required.
      </p>

    </section>


    <details
      class="release-evidence"
      data-tower-candidate-evidence="backstage-detail"
    >

      <summary>
        Candidate evidence
      </summary>

      <div class="release-evidence-body">

        <p>
          Candidate revision:
          <strong>
            {revision}
          </strong>
        </p>

        <p>
          Critical routes:
          <strong>
            {route_count} verified
          </strong>
        </p>

        <p>
          Packet integrity reference:
          <strong>
            {packet_hash[:16]}…
          </strong>
        </p>

        <ul class="release-evidence-list">
          {evidence_items}
        </ul>

        {_publication_form(
            label="Refresh hosted candidate"
        )}

      </div>

    </details>


    {evidence_backstage}
    """


    return _page(
        "Tower · Owner Release Review",
        body,
    )

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
