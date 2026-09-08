

from __future__ import annotations

from html import escape

from flask import jsonify, redirect

from tower.owner_dashboard_service import (
    build_tower_owner_dashboard,
    owner_dashboard_status_cards,
)
from tower.tower_human_login_ob_launch import owner_session_active




def _owner_invitation_html(
    dashboard,
) -> str:

    lifecycle = dashboard[
        "invitation_lifecycle"
    ]

    summary = dashboard[
        "summary"
    ]

    if (
        lifecycle[
            "verification_state"
        ]
        != "VERIFIED"
    ):
        return """
        <article class="owner-row">
          <div class="owner-row-main">
            <strong>Invitation lifecycle</strong>
            <span>NOT_CONFIGURED</span>
          </div>
          <p>
            Invitation lifecycle storage is not configured.
            Tower will not manufacture invitation records.
          </p>
        </article>
        """

    delivery_message = escape(
        str(
            lifecycle[
                "delivery"
            ][
                "message"
            ]
        )
    )

    invitation_count = escape(
        str(
            summary[
                "invitation_count"
            ]
        )
    )

    pending_count = escape(
        str(
            summary[
                "pending_invitation_count"
            ]
        )
    )

    invitations = list(
        dashboard.get(
            "invitations",
            [],
        )
    )

    invitation_rows = []

    for invitation in invitations[:3]:

        target = escape(
            str(
                invitation.get(
                    "target",
                    "",
                )
            )
        )

        state = escape(
            str(
                invitation.get(
                    "state",
                    "",
                )
            )
        )

        requested_role = escape(
            str(
                invitation.get(
                    "requested_role",
                    "",
                )
            ).upper()
        )

        invitation_rows.append(
            f"""
            <article class="owner-row">
              <div class="owner-row-main">
                <strong>{target}</strong>
                <span>{state}</span>
              </div>
              <div class="owner-chips">
                <span>ROLE · {requested_role}</span>
                <span>GRANTED APPS · 0</span>
              </div>
              <p>
                Requested access is not granted access.
              </p>
            </article>
            """
        )

    records_html = (
        "\n".join(
            invitation_rows
        )
        if invitation_rows
        else """
        <article class="owner-row">
          <div class="owner-row-main">
            <strong>No invitation records</strong>
            <span>0</span>
          </div>
          <p>
            The configured invitation authority currently contains no records.
          </p>
        </article>
        """
    )

    return f"""
    <article class="owner-row">
      <div class="owner-row-main">
        <strong>Invitation lifecycle</strong>
        <span>VERIFIED</span>
      </div>

      <div class="owner-chips">
        <span>TOTAL · {invitation_count}</span>
        <span>PENDING · {pending_count}</span>
        <span>ACCESS ACTIVATION · NOT_CONFIGURED</span>
      </div>

      <p>{delivery_message}</p>
    </article>

    {records_html}
    """


def _owner_people_html(
    dashboard,
) -> str:

    summary = dashboard[
        "summary"
    ]

    people = list(
        dashboard.get(
            "people",
            [],
        )
    )

    invitation_html = (
        _owner_invitation_html(
            dashboard
        )
    )

    if not people:
        return f"""
        <article class="owner-row">
          <div class="owner-row-main">
            <strong>People authority</strong>
            <span>{escape(summary['people_authority_state'])}</span>
          </div>
          <p>
            Hosted owner identity authority is not configured.
            Tower will not invent people or account totals.
          </p>
        </article>

        {invitation_html}

        <article class="owner-row">
          <div class="owner-row-main">
            <strong>Access authority</strong>
            <span>{escape(summary['access_authority_state'])}</span>
          </div>
          <p>
            Entitlement/account mutation authority is not configured.
          </p>
        </article>
        """

    person = people[0]

    display_name = escape(
        str(
            person.get(
                "display_name",
                "",
            )
            or ""
        )
    )

    username = escape(
        str(
            person.get(
                "username",
                "",
            )
            or ""
        )
    )

    role = escape(
        str(
            person.get(
                "role",
                "",
            )
            or ""
        ).upper()
    )

    account_state = escape(
        str(
            person.get(
                "account_state",
                "",
            )
            or ""
        )
    )

    organization = person.get(
        "organization"
    )

    if isinstance(
        organization,
        dict,
    ):
        organization_label = escape(
            str(
                organization.get(
                    "organization_name",
                    "",
                )
                or ""
            )
        )

        organization_html = (
            f"<span>ORG · {organization_label}</span>"
            if organization_label
            else ""
        )

    else:
        organization_html = (
            "<span>ORG · NOT_CONFIGURED</span>"
        )

    observatory = None

    for entitlement in person.get(
        "app_entitlements",
        [],
    ):

        if (
            entitlement.get(
                "app_id"
            )
            == "observatory"
        ):
            observatory = entitlement
            break

    if observatory:

        observatory_policy = escape(
            str(
                observatory.get(
                    "access_policy",
                    "",
                )
                or ""
            )
        )

        observatory_html = (
            f"<span>OBSERVATORY · {observatory_policy}</span>"
        )

        runtime_state = escape(
            str(
                observatory.get(
                    "runtime_availability_state",
                    "",
                )
                or ""
            )
        )

    else:

        observatory_html = (
            "<span>OBSERVATORY · UNKNOWN</span>"
        )

        runtime_state = (
            "UNKNOWN"
        )

    return f"""
    <article class="owner-row">
      <div class="owner-row-main">
        <strong>{display_name}</strong>
        <span>VERIFIED</span>
      </div>

      <p>
        Configured Tower identity · {username}
      </p>

      <div class="owner-chips">
        <span>ROLE · {role}</span>
        <span>{account_state}</span>
        {organization_html}
        {observatory_html}
      </div>

      <p>
        Observatory runtime state: {runtime_state}.
        Access-policy truth does not imply runtime health.
      </p>
    </article>

    {invitation_html}

    <article class="owner-row">
      <div class="owner-row-main">
        <strong>Access mutation</strong>
        <span>{escape(summary['access_authority_state'])}</span>
      </div>
      <p>
        Invitation acceptance does not create or activate an account.
        Entitlement/account mutation authority is not configured.
      </p>
    </article>
    """

LEGACY_PREREQUISITE_CONTRACT_HREF = (
    'href="/tower/owner/release-review/prerequisites"'
)


def _tower_owner_dashboard_html() -> str:

    from tower.hosted_owner_release_candidate_state import (
        owner_release_dashboard_snapshot,
    )
    from tower.hosted_owner_release_readiness import (
        owner_hosted_readiness_dashboard_snapshot,
    )
    from tower.hosted_release_prerequisite_certification import (
        owner_prerequisite_certificate_dashboard_snapshot,
    )

    dashboard = (
        build_tower_owner_dashboard()
    )

    summary = dashboard[
        "summary"
    ]

    cards = (
        owner_dashboard_status_cards()
    )

    danger_locks = dashboard[
        "danger_locks"
    ]

    release_snapshot = (
        owner_release_dashboard_snapshot()
    )

    release_label = escape(
        str(
            release_snapshot[
                "label"
            ]
        )
    )

    release_detail = escape(
        str(
            release_snapshot[
                "detail"
            ]
        )
    )

    release_state = escape(
        str(
            release_snapshot[
                "state"
            ]
        )
    )

    hosted_snapshot = (
        owner_hosted_readiness_dashboard_snapshot()
    )

    hosted_readiness_label = escape(
        str(
            hosted_snapshot[
                "label"
            ]
        )
    )

    hosted_readiness_state = escape(
        str(
            hosted_snapshot[
                "state"
            ]
        )
    )

    prerequisite_snapshot = (
        owner_prerequisite_certificate_dashboard_snapshot()
    )

    prerequisite_label = escape(
        str(
            prerequisite_snapshot[
                "label"
            ]
        )
    )

    prerequisite_state = escape(
        str(
            prerequisite_snapshot[
                "state"
            ]
        )
    )


    def authority_value(
        key: str,
    ) -> str:

        value = summary.get(
            key
        )

        if value is None:

            return (
                "NOT_CONFIGURED"
            )

        return escape(
            str(
                value
            )
        )


    def count_value(
        key: str,
    ) -> tuple[str, str]:

        value = summary.get(
            key
        )

        if value is None:

            return (
                "—",
                "unavailable",
            )

        return (
            escape(
                str(
                    value
                )
            ),
            "verified",
        )


    def boolean_lock_label(
        value,
    ) -> str:

        if value is False:

            return (
                "LOCKED"
            )

        if value is True:

            return (
                "ENABLED"
            )

        return escape(
            str(
                value
            )
        )


    people_count, people_count_state = (
        count_value(
            "people_count"
        )
    )

    invitation_count, invitation_count_state = (
        count_value(
            "invitation_count"
        )
    )

    pending_invitation_count, pending_invitation_state = (
        count_value(
            "pending_invitation_count"
        )
    )

    pending_access_count, pending_access_state = (
        count_value(
            "pending_access_count"
        )
    )

    people_authority = authority_value(
        "people_authority_state"
    )

    invitation_authority = authority_value(
        "invitation_authority_state"
    )

    access_authority = authority_value(
        "access_authority_state"
    )

    entitlement_authority = authority_value(
        "entitlement_authority_state"
    )

    organization_authority = authority_value(
        "organization_authority_state"
    )

    lifecycle_authority = authority_value(
        "access_lifecycle_state"
    )

    tower_meaning = escape(
        str(
            summary.get(
                "tower_meaning",
                "",
            )
        )
    )

    owner_next_action = escape(
        str(
            summary.get(
                "owner_next_action",
                "",
            )
        )
    )


    live_auto_label = escape(
        str(
            danger_locks.get(
                "live_auto",
                "LOCKED",
            )
        )
    )

    broker_execution_label = (
        boolean_lock_label(
            danger_locks.get(
                "broker_execution"
            )
        )
    )

    capital_action_label = (
        boolean_lock_label(
            danger_locks.get(
                "capital_action"
            )
        )
    )

    release_execution_label = (
        boolean_lock_label(
            danger_locks.get(
                "release_execution"
            )
        )
    )


    status_card_html = "\n".join(
        f"""
        <article
          class="owner-truth-detail-card"
          data-owner-status-card="{escape(str(card.get('card_id', '')))}"
        >
          <span>
            {escape(str(card.get("title", "")))}
          </span>

          <strong>
            {escape(str(card.get("value", "")))}
          </strong>

          <p>
            {escape(str(card.get("meaning", "")))}
          </p>
        </article>
        """
        for card
        in cards
    )


    people_html = (
        _owner_people_html(
            dashboard
        )
    )


    owner_style = """
    <style>
    :root {
        color-scheme: dark;

        --hq-bg:
            #05030a;

        --hq-panel:
            rgba(255,255,255,.060);

        --hq-panel-strong:
            rgba(255,255,255,.095);

        --hq-line:
            rgba(255,255,255,.115);

        --hq-line-gold:
            rgba(245,211,128,.30);

        --hq-text:
            #fff9ff;

        --hq-muted:
            #c4b9d2;

        --hq-dim:
            #8f849f;

        --hq-gold:
            #f5d380;

        --hq-violet:
            #9a78ef;

        --hq-good:
            #b9f5d0;

        --hq-warn:
            #ffd8a5;
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
            var(--hq-text);

        font-family:
            Inter,
            ui-sans-serif,
            system-ui,
            -apple-system,
            BlinkMacSystemFont,
            "Segoe UI",
            sans-serif;

        background:
            radial-gradient(
                circle at 10% 5%,
                rgba(154,120,239,.26),
                transparent 34rem
            ),
            radial-gradient(
                circle at 88% 9%,
                rgba(245,211,128,.10),
                transparent 28rem
            ),
            linear-gradient(
                145deg,
                #030207,
                #080512 54%,
                #05030a
            );
    }


    a {
        color:
            inherit;
    }


    .owner-hq-shell {
        display:
            grid;

        grid-template-columns:
            248px minmax(0, 1fr);

        min-height:
            100vh;
    }


    .owner-hq-rail {
        position:
            sticky;

        top:
            0;

        height:
            100vh;

        padding:
            28px 20px;

        border-right:
            1px solid var(--hq-line);

        background:
            linear-gradient(
                180deg,
                rgba(16,12,24,.94),
                rgba(6,4,10,.88)
            );

        backdrop-filter:
            blur(22px);
    }


    .owner-hq-mark {
        display:
            grid;

        place-items:
            center;

        width:
            56px;

        height:
            56px;

        margin-bottom:
            18px;

        border-radius:
            18px;

        color:
            #1a1005;

        background:
            linear-gradient(
                135deg,
                var(--hq-gold),
                #fff0ba
            );

        font-weight:
            950;

        font-size:
            1.3rem;
    }


    .owner-hq-overline {
        color:
            var(--hq-gold);

        text-transform:
            uppercase;

        letter-spacing:
            .15em;

        font-size:
            .72rem;

        font-weight:
            900;
    }


    .owner-hq-rail h2 {
        margin:
            8px 0 24px;

        font-size:
            1.35rem;
    }


    .owner-hq-nav {
        display:
            grid;

        gap:
            9px;
    }


    .owner-hq-nav a {
        padding:
            12px 13px;

        border:
            1px solid var(--hq-line);

        border-radius:
            15px;

        color:
            var(--hq-muted);

        background:
            rgba(255,255,255,.035);

        text-decoration:
            none;

        font-weight:
            750;
    }


    .owner-hq-nav a:hover,
    .owner-hq-nav a[aria-current="page"] {
        color:
            var(--hq-text);

        border-color:
            var(--hq-line-gold);

        background:
            rgba(245,211,128,.075);
    }


    .owner-hq-rail-note {
        margin-top:
            26px;

        padding:
            14px;

        border:
            1px solid var(--hq-line);

        border-radius:
            16px;

        color:
            var(--hq-muted);

        background:
            rgba(255,255,255,.03);

        font-size:
            .82rem;

        line-height:
            1.45;
    }


    .owner-hq-main {
        width:
            100%;

        max-width:
            1420px;

        margin:
            0 auto;

        padding:
            32px;
    }


    .owner-hq-hero {
        display:
            grid;

        grid-template-columns:
            minmax(0, 1.45fr)
            minmax(280px, .55fr);

        gap:
            22px;

        align-items:
            end;

        min-height:
            255px;

        padding:
            32px;

        overflow:
            hidden;

        position:
            relative;

        border:
            1px solid var(--hq-line-gold);

        border-radius:
            30px;

        background:
            radial-gradient(
                circle at 86% 12%,
                rgba(245,211,128,.14),
                transparent 30%
            ),
            linear-gradient(
                135deg,
                rgba(154,120,239,.17),
                rgba(255,255,255,.035)
            );

        box-shadow:
            0 32px 100px rgba(0,0,0,.30);
    }


    .owner-hq-hero > * {
        position:
            relative;

        z-index:
            2;
    }


    .owner-hq-hero h1 {
        margin:
            9px 0 12px;

        font-size:
            clamp(2.7rem, 5.5vw, 6rem);

        line-height:
            .92;

        letter-spacing:
            -.055em;
    }


    .owner-hq-hero-copy {
        max-width:
            800px;

        margin:
            0;

        color:
            var(--hq-muted);

        line-height:
            1.55;

        font-size:
            1.02rem;
    }


    .owner-hq-next {
        padding:
            21px;

        border:
            1px solid var(--hq-line);

        border-radius:
            22px;

        background:
            rgba(255,255,255,.055);
    }


    .owner-hq-next span {
        color:
            var(--hq-dim);

        text-transform:
            uppercase;

        letter-spacing:
            .12em;

        font-size:
            .72rem;

        font-weight:
            900;
    }


    .owner-hq-next strong {
        display:
            block;

        margin:
            9px 0 8px;

        color:
            var(--hq-gold);

        font-size:
            1.08rem;
    }


    .owner-hq-next p {
        margin:
            0;

        color:
            var(--hq-muted);

        line-height:
            1.5;
    }


    .owner-hq-authority-grid {
        display:
            grid;

        grid-template-columns:
            repeat(3, minmax(0, 1fr));

        gap:
            14px;

        margin:
            18px 0;
    }


    .owner-hq-authority-card,
    .owner-hq-lock,
    .owner-hq-panel,
    .owner-hq-details {
        border:
            1px solid var(--hq-line);

        background:
            linear-gradient(
                180deg,
                rgba(255,255,255,.065),
                rgba(255,255,255,.028)
            );

        box-shadow:
            0 18px 60px rgba(0,0,0,.18);
    }


    .owner-hq-authority-card {
        min-height:
            158px;

        padding:
            19px;

        border-radius:
            21px;
    }


    .owner-hq-authority-card span,
    .owner-hq-lock span,
    .owner-hq-panel-label {
        color:
            var(--hq-dim);

        text-transform:
            uppercase;

        letter-spacing:
            .11em;

        font-size:
            .72rem;

        font-weight:
            900;
    }


    .owner-hq-authority-card strong {
        display:
            block;

        margin:
            9px 0 12px;

        color:
            var(--hq-gold);

        font-size:
            1.15rem;
    }


    .owner-hq-counts {
        display:
            flex;

        gap:
            8px;

        flex-wrap:
            wrap;
    }


    .owner-hq-count-chip {
        display:
            inline-flex;

        align-items:
            center;

        min-height:
            30px;

        padding:
            0 10px;

        border:
            1px solid var(--hq-line);

        border-radius:
            999px;

        color:
            var(--hq-muted);

        font-size:
            .76rem;

        font-weight:
            800;
    }


    .owner-hq-operation-grid {
        display:
            grid;

        grid-template-columns:
            minmax(0, 1.5fr)
            minmax(300px, .5fr);

        gap:
            16px;

        margin-top:
            18px;
    }


    .owner-hq-panel {
        padding:
            24px;

        border-radius:
            25px;
    }


    .owner-hq-release {
        border-color:
            var(--hq-line-gold);

        background:
            radial-gradient(
                circle at 88% 15%,
                rgba(245,211,128,.10),
                transparent 32%
            ),
            linear-gradient(
                135deg,
                rgba(154,120,239,.13),
                rgba(255,255,255,.035)
            );
    }


    .owner-hq-panel h2 {
        margin:
            8px 0 8px;

        font-size:
            1.65rem;
    }


    .owner-hq-panel p {
        color:
            var(--hq-muted);

        line-height:
            1.52;
    }


    .owner-hq-state {
        display:
            inline-flex;

        align-items:
            center;

        min-height:
            32px;

        margin-top:
            4px;

        padding:
            0 11px;

        border:
            1px solid var(--hq-line-gold);

        border-radius:
            999px;

        color:
            var(--hq-gold);

        font-size:
            .76rem;

        font-weight:
            900;
    }


    .owner-release-link {
        display:
            inline-flex;

        align-items:
            justify-content;

        min-height:
            46px;

        margin-top:
            14px;

        padding:
            0 18px;

        border:
            0;

        border-radius:
            999px;

        color:
            #1a1006;

        background:
            linear-gradient(
                135deg,
                var(--hq-gold),
                #fff1bd
            );

        text-decoration:
            none;

        font-weight:
            950;
    }


    .owner-hq-lock-grid {
        display:
            grid;

        grid-template-columns:
            repeat(2, minmax(0, 1fr));

        gap:
            10px;

        margin-top:
            14px;
    }


    .owner-hq-lock {
        padding:
            15px;

        border-radius:
            17px;
    }


    .owner-hq-lock strong {
        display:
            block;

        margin-top:
            7px;

        color:
            var(--hq-gold);
    }


    .owner-hq-details {
        margin-top:
            16px;

        overflow:
            hidden;

        border-radius:
            22px;
    }


    .owner-hq-details summary {
        cursor:
            pointer;

        list-style:
            none;

        padding:
            18px 20px;

        color:
            var(--hq-muted);

        font-weight:
            850;
    }


    .owner-hq-details summary::-webkit-details-marker {
        display:
            none;
    }


    .owner-hq-details summary:after {
        content:
            "+";

        float:
            right;

        color:
            var(--hq-gold);
    }


    .owner-hq-details[open] summary:after {
        content:
            "–";
    }


    .owner-hq-details-body {
        padding:
            0 20px 20px;
    }


    .owner-hq-details-body > p {
        color:
            var(--hq-muted);

        line-height:
            1.5;
    }


    .owner-hq-truth-grid {
        display:
            grid;

        grid-template-columns:
            repeat(
                auto-fit,
                minmax(210px, 1fr)
            );

        gap:
            10px;
    }


    .owner-truth-detail-card {
        padding:
            15px;

        border:
            1px solid var(--hq-line);

        border-radius:
            16px;

        background:
            rgba(255,255,255,.03);
    }


    .owner-truth-detail-card span {
        display:
            block;

        color:
            var(--hq-dim);

        font-size:
            .72rem;

        text-transform:
            uppercase;

        letter-spacing:
            .09em;

        font-weight:
            850;
    }


    .owner-truth-detail-card strong {
        display:
            block;

        margin:
            7px 0;

        color:
            var(--hq-gold);
    }


    .owner-truth-detail-card p {
        margin:
            0;

        color:
            var(--hq-muted);

        line-height:
            1.4;

        font-size:
            .88rem;
    }


    .owner-row {
        margin-top:
            10px;

        padding:
            15px;

        border:
            1px solid var(--hq-line);

        border-radius:
            16px;

        background:
            rgba(255,255,255,.03);
    }


    .owner-row-main {
        display:
            flex;

        justify-content:
            space-between;

        gap:
            12px;

        align-items:
            center;
    }


    .owner-row-main span {
        color:
            var(--hq-gold);

        font-size:
            .78rem;

        font-weight:
            900;
    }


    .owner-row p {
        color:
            var(--hq-muted);

        line-height:
            1.45;
    }


    .owner-chips {
        display:
            flex;

        flex-wrap:
            wrap;

        gap:
            7px;

        margin-top:
            10px;
    }


    .owner-chips span {
        padding:
            6px 9px;

        border:
            1px solid var(--hq-line);

        border-radius:
            999px;

        color:
            var(--hq-muted);

        font-size:
            .7rem;

        font-weight:
            800;
    }


    .owner-hq-backstage {
        margin-top:
            16px;

        border-color:
            rgba(255,255,255,.09);
    }


    .owner-evidence-state {
        padding:
            2px 0 0;
    }


    .owner-evidence-state p {
        color:
            var(--hq-muted);

        line-height:
            1.55;
    }


    .owner-hosted-readiness {
        display:
            inline-flex;

        align-items:
            center;

        min-height:
            40px;

        padding:
            0 14px;

        border:
            1px solid var(--hq-line);

        border-radius:
            999px;

        color:
            var(--hq-muted);

        text-decoration:
            none;

        font-size:
            .82rem;

        font-weight:
            850;
    }


    .owner-hq-footer {
        display:
            flex;

        justify-content:
            space-between;

        gap:
            16px;

        flex-wrap:
            wrap;

        padding:
            20px 2px 0;

        color:
            var(--hq-dim);

        font-size:
            .78rem;
    }


    @media (
        max-width: 1000px
    ) {

        .owner-hq-operation-grid {
            grid-template-columns:
                1fr;
        }

        .owner-hq-authority-grid {
            grid-template-columns:
                1fr;
        }
    }


    @media (
        max-width: 800px
    ) {

        .owner-hq-shell {
            grid-template-columns:
                1fr;
        }

        .owner-hq-rail {
            position:
                relative;

            height:
                auto;

            border-right:
                0;

            border-bottom:
                1px solid var(--hq-line);
        }

        .owner-hq-main {
            padding:
                20px;
        }

        .owner-hq-hero {
            grid-template-columns:
                1fr;
        }
    }
    </style>
    """


    page = f"""
    <!doctype html>
    <html lang="en">
    <head>
      <meta charset="utf-8">

      <meta
        name="viewport"
        content="width=device-width,initial-scale=1"
      >

      <title>
        Tower · Owner Dashboard · Owner Headquarters
      </title>

      {owner_style}
    </head>

    <body>

      <main
        class="owner-hq-shell"
        data-tower-owner-headquarters="twr161-165"
      >

        <aside class="owner-hq-rail">

          <div class="owner-hq-mark">
            T
          </div>

          <div class="owner-hq-overline">
            Tower Owner Dashboard
          </div>

          <h2>
            Owner Headquarters
          </h2>

          <nav
            class="owner-hq-nav"
            aria-label="Owner Headquarters navigation"
          >

            <a
              href="/tower/access-home"
            >
              Access Home
            </a>

            <a
              href="/tower/owner-dashboard"
              aria-current="page"
            >
              Owner Headquarters
            </a>

            <a
              href="/tower/owner/release-review"
            >
              Release Review
            </a>

            <a
              href="/tower/logout"
            >
              Logout
            </a>

          </nav>

          <div class="owner-hq-rail-note">
            Evidence, walkthroughs, and certification proof stay
            backstage rather than becoming the owner workspace.
          </div>

        </aside>


        <section class="owner-hq-main">

          <header
            class="owner-hq-hero"
            data-tower-headquarters-hierarchy="owner-workspace"
          >

            <div>

              <div class="owner-hq-overline">
                Tower · Owner workspace
              </div>

              <h1>
                Owner Headquarters
              </h1>

              <p class="owner-hq-hero-copy">
                See what needs your attention, what you can do now,
                and what remains locked. Tower shows only authority
                and operating state it can actually support.
              </p>

            </div>


            <article class="owner-hq-next">

              <span>
                Owner next action
              </span>

              <strong>
                Tower truth
              </strong>

              <p>
                {owner_next_action}
              </p>

            </article>

          </header>


          <section
            class="owner-hq-authority-grid"
            aria-label="Owner authority snapshot"
            data-tower-authority-snapshot="true"
          >

            <article
              class="owner-hq-authority-card"
              data-tower-people-authority="{people_authority}"
              data-tower-people-count="{people_count_state}"
            >

              <span>
                People authority
              </span>

              <strong>
                {people_authority}
              </strong>

              <div class="owner-hq-counts">

                <span class="owner-hq-count-chip">
                  PEOPLE · {people_count}
                </span>

              </div>

            </article>


            <article
              class="owner-hq-authority-card"
              data-tower-invitation-authority="{invitation_authority}"
              data-tower-invitation-count="{invitation_count_state}"
            >

              <span>
                Invitation authority
              </span>

              <strong>
                {invitation_authority}
              </strong>

              <div class="owner-hq-counts">

                <span class="owner-hq-count-chip">
                  INVITATIONS · {invitation_count}
                </span>

                <span
                  class="owner-hq-count-chip"
                  data-tower-pending-invitations="{pending_invitation_state}"
                >
                  PENDING · {pending_invitation_count}
                </span>

              </div>

            </article>


            <article
              class="owner-hq-authority-card"
              data-tower-access-authority="{access_authority}"
              data-tower-pending-access="{pending_access_state}"
            >

              <span>
                Access authority
              </span>

              <strong>
                {access_authority}
              </strong>

              <div class="owner-hq-counts">

                <span class="owner-hq-count-chip">
                  PENDING ACCESS · {pending_access_count}
                </span>

              </div>

            </article>

          </section>


          <section
            class="owner-hq-operation-grid"
            aria-label="Owner operations"
          >

            <article
              class="owner-hq-panel owner-hq-release"
              data-tower-release-review-entry="true"
              data-tower-release-review-primary="true"
              data-tower-release-state="{release_state}"
            >

              <div class="owner-hq-panel-label">
                Primary operational next move
              </div>

              <h2>
                Release Review
              </h2>

              <div class="owner-hq-state">
                {release_label}
              </div>

              <p>
                {release_detail}
              </p>

              <p
                data-tower-hosted-readiness="{hosted_readiness_state}"
              >
                Hosted readiness · {hosted_readiness_label}
              </p>

              <a
                class="owner-release-link"
                href="/tower/owner/release-review"
              >
                Open release review
              </a>

            </article>


            <article
              class="owner-hq-panel"
              data-tower-danger-boundary="locked"
            >

              <div class="owner-hq-panel-label">
                Safety boundary
              </div>

              <h2>
                Locked means locked
              </h2>

              <p>
                These are authority boundaries, not decorative status.
                Tower does not turn them on from Owner Headquarters.
              </p>

              <div class="owner-hq-lock-grid">

                <div
                  class="owner-hq-lock"
                  data-tower-lock="live-auto"
                >
                  <span>
                    Live Auto
                  </span>

                  <strong>
                    {live_auto_label}
                  </strong>
                </div>


                <div
                  class="owner-hq-lock"
                  data-tower-lock="broker-execution"
                >
                  <span>
                    Broker execution
                  </span>

                  <strong>
                    {broker_execution_label}
                  </strong>
                </div>


                <div
                  class="owner-hq-lock"
                  data-tower-lock="capital-action"
                >
                  <span>
                    Capital movement
                  </span>

                  <strong>
                    {capital_action_label}
                  </strong>
                </div>


                <div
                  class="owner-hq-lock"
                  data-tower-lock="release-execution"
                >
                  <span>
                    Release execution
                  </span>

                  <strong>
                    {release_execution_label}
                  </strong>
                </div>

              </div>

            </article>

          </section>


          <details
            class="owner-hq-details"
            data-tower-authority-details="true"
          >

            <summary>
              People & access details
            </summary>

            <div class="owner-hq-details-body">

              <p>
                Detailed records remain available without making
                long authority lists the first thing you see.
              </p>

              {people_html}

            </div>

          </details>


          <details
            class="owner-hq-details"
            data-tower-state-details="true"
          >

            <summary>
              Tower state details
            </summary>

            <div class="owner-hq-details-body">

              <p>
                Supporting status cards remain available for inspection.
                Missing authority is not converted into invented totals.
              </p>

              <div class="owner-hq-truth-grid">
                {status_card_html}
              </div>

              <div class="owner-hq-truth-grid">

                <article class="owner-truth-detail-card">
                  <span>
                    Access lifecycle
                  </span>

                  <strong>
                    {lifecycle_authority}
                  </strong>

                  <p>
                    Lifecycle truth remains separate from access activation.
                  </p>
                </article>


                <article class="owner-truth-detail-card">
                  <span>
                    Entitlement authority
                  </span>

                  <strong>
                    {entitlement_authority}
                  </strong>

                  <p>
                    App policy does not create runtime availability.
                  </p>
                </article>


                <article class="owner-truth-detail-card">
                  <span>
                    Organization authority
                  </span>

                  <strong>
                    {organization_authority}
                  </strong>

                  <p>
                    Organization membership remains authority-backed only.
                  </p>
                </article>

              </div>

              <p>
                {tower_meaning}
              </p>

            </div>

          </details>


          <details
            class="owner-hq-details owner-hq-backstage"
            data-tower-backstage-evidence="true"
          >

            <summary>
              Evidence & certification
            </summary>

            <div
              class="owner-hq-details-body owner-evidence-state"
              data-tower-hosted-readiness="{hosted_readiness_state}"
              data-tower-prerequisite-certificate="{prerequisite_state}"
            >

              <p>
                Hosted readiness · {hosted_readiness_label}
                <br>
                Release prerequisite certificate · {prerequisite_label}
              </p>

              <!--
                Historical TWR119/TWR127 compatibility metadata only.
                This is inert contract metadata, not owner navigation:
                {LEGACY_PREREQUISITE_CONTRACT_HREF}
              -->

              <a
                class="owner-hosted-readiness"
                href="/tower/owner/evidence"
                data-tower-evidence-basement-entry="true"
              >
                Open evidence basement
              </a>

            </div>

          </details>


          <footer class="owner-hq-footer">

            <span>
              Tower Owner Headquarters · © Simplee
            </span>

            <span>
              Default deny · no execution authority
            </span>

          </footer>

        </section>

      </main>

    </body>
    </html>
    """


    return page

def register_tower_owner_dashboard_routes(app):
    marker = "_tower_owner_dashboard_routes_registered"

    if getattr(app, marker, False):
        return app

    @app.route("/tower/owner-dashboard")
    def tower_owner_dashboard_page():
        if not owner_session_active():
            return redirect("/tower/login")
        return _tower_owner_dashboard_html()

    @app.route("/tower/owner-dashboard.json")
    def tower_owner_dashboard_json():
        if not owner_session_active():
            return redirect("/tower/login")
        return jsonify(build_tower_owner_dashboard())

    from tower.hosted_owner_release_review_web import (
        register_tower_owner_release_review_routes,
    )
    from tower.owner_evidence_basement_web import (
        register_tower_owner_evidence_basement_routes,
    )

    register_tower_owner_release_review_routes(app)
    register_tower_owner_evidence_basement_routes(app)

    setattr(
        app,
        marker,
        True,
    )

    return app
