

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

    dashboard = build_tower_owner_dashboard()
    summary = dashboard["summary"]
    cards = owner_dashboard_status_cards()
    release_snapshot = owner_release_dashboard_snapshot()
    release_label = escape(release_snapshot["label"])
    release_detail = escape(release_snapshot["detail"])
    release_state = escape(release_snapshot["state"])
    hosted_snapshot = owner_hosted_readiness_dashboard_snapshot()
    hosted_readiness_label = escape(hosted_snapshot["label"])
    hosted_readiness_state = escape(hosted_snapshot["state"])
    prerequisite_snapshot = owner_prerequisite_certificate_dashboard_snapshot()
    prerequisite_label = escape(prerequisite_snapshot["label"])
    prerequisite_state = escape(prerequisite_snapshot["state"])

    card_html = "\n".join(
        f"""
        <article class="owner-card owner-card-{card['status']}">
          <div class="owner-card-label">{card['title']}</div>
          <div class="owner-card-value">{card['value']}</div>
          <p>{card['meaning']}</p>
        </article>
        """
        for card in cards
    )

    people_html = (
        _owner_people_html(
            dashboard
        )
    )

    return f"""
    <!doctype html>
    <html>
      <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>Tower · Owner Dashboard</title>
        <style>
          :root {{
            --bg: #070411;
            --panel: rgba(255,255,255,0.075);
            --panel-strong: rgba(255,255,255,0.13);
            --text: #fff8ff;
            --muted: #cab9ee;
            --gold: #f8d978;
            --violet: #9b7cff;
            --pink: #ffb8e6;
            --border: rgba(248,217,120,0.28);
            --good: #b8f8cf;
            --warn: #ffd6a0;
          }}

          * {{
            box-sizing: border-box;
          }}

          body {{
            margin: 0;
            min-height: 100vh;
            background:
              radial-gradient(circle at 8% 4%, rgba(155,124,255,0.34), transparent 34rem),
              radial-gradient(circle at 88% 10%, rgba(255,184,230,0.16), transparent 28rem),
              radial-gradient(circle at 50% 88%, rgba(248,217,120,0.10), transparent 30rem),
              var(--bg);
            color: var(--text);
            font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
          }}

          main {{
            width: min(1180px, calc(100% - 32px));
            margin: 0 auto;
            padding: 36px 0 58px;
          }}

          .owner-hero {{
            border: 1px solid var(--border);
            background: linear-gradient(135deg, rgba(255,255,255,0.11), rgba(255,255,255,0.035));
            box-shadow: 0 24px 80px rgba(0,0,0,0.40);
            border-radius: 30px;
            padding: 32px;
            margin-bottom: 22px;
          }}

          .eyebrow {{
            color: var(--gold);
            text-transform: uppercase;
            letter-spacing: .16em;
            font-size: 12px;
            font-weight: 900;
          }}

          h1 {{
            margin: 10px 0 12px;
            font-size: clamp(34px, 5vw, 64px);
            line-height: .95;
          }}

          .hero-copy {{
            color: var(--muted);
            font-size: 18px;
            max-width: 900px;
            line-height: 1.55;
          }}

          .summary-grid {{
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 14px;
            margin: 22px 0;
          }}

          .owner-card {{
            border: 1px solid rgba(255,255,255,0.12);
            background: var(--panel);
            border-radius: 22px;
            padding: 18px;
            min-height: 150px;
          }}

          .owner-card-label {{
            color: var(--muted);
            font-size: 13px;
            font-weight: 900;
            text-transform: uppercase;
            letter-spacing: .12em;
          }}

          .owner-card-value {{
            color: var(--gold);
            font-size: 34px;
            font-weight: 950;
            margin: 10px 0;
          }}

          .owner-card p,
          .owner-row p {{
            color: var(--muted);
            line-height: 1.45;
            margin-bottom: 0;
          }}

          .owner-release-card {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 18px;
            margin: 20px 0 24px;
            padding: 22px;
            border: 1px solid rgba(248,217,120,0.30);
            border-radius: 24px;
            background: linear-gradient(135deg, rgba(155,124,255,0.12), rgba(248,217,120,0.05));
          }}

          .owner-release-card p {{
            margin: 7px 0 0;
            color: var(--muted);
          }}

          .owner-release-state {{
            display: inline-flex;
            margin-top: 10px;
            padding: 6px 11px;
            border: 1px solid rgba(248,217,120,0.28);
            border-radius: 999px;
            color: var(--gold);
            font-size: 12px;
            font-weight: 850;
          }}

          .owner-release-link {{
            color: var(--gold);
            text-decoration: none;
            white-space: nowrap;
            border: 1px solid rgba(248,217,120,0.32);
            border-radius: 999px;
            padding: 10px 15px;
            font-weight: 850;
          }}

          .owner-hosted-readiness {{
            display: inline-flex;
            margin-top: 9px;
            color: var(--gold);
            text-decoration: none;
            font-size: 12px;
            font-weight: 750;
          }}

          .owner-section {{
            margin-top: 24px;
            border: 1px solid rgba(255,255,255,0.10);
            background: rgba(0,0,0,0.18);
            border-radius: 26px;
            padding: 22px;
          }}

          .owner-section h2 {{
            margin: 0 0 14px;
            font-size: 24px;
          }}

          .owner-row {{
            border: 1px solid rgba(255,255,255,0.10);
            background: var(--panel);
            border-radius: 18px;
            padding: 16px;
            margin-top: 12px;
          }}

          .owner-row-main {{
            display: flex;
            justify-content: space-between;
            gap: 12px;
            align-items: center;
          }}

          .owner-row-main span {{
            color: var(--gold);
            font-size: 13px;
            font-weight: 900;
            text-transform: uppercase;
            letter-spacing: .10em;
          }}

          .owner-chips {{
            display: flex;
            gap: 8px;
            flex-wrap: wrap;
            margin-top: 12px;
          }}

          .owner-chips span {{
            border: 1px solid rgba(248,217,120,0.25);
            background: rgba(248,217,120,0.08);
            color: var(--gold);
            border-radius: 999px;
            padding: 6px 10px;
            font-size: 12px;
            font-weight: 850;
          }}

          .owner-warning {{
            margin-top: 22px;
            border: 1px solid rgba(255,214,160,0.30);
            background: rgba(255,214,160,0.09);
            border-radius: 22px;
            padding: 18px;
            color: var(--warn);
          }}

          .owner-next {{
            margin-top: 14px;
            border: 1px solid rgba(184,248,207,0.28);
            background: rgba(184,248,207,0.08);
            border-radius: 22px;
            padding: 18px;
          }}

          .owner-next strong {{
            color: var(--good);
          }}

          @media (max-width: 820px) {{
            .summary-grid {{
              grid-template-columns: 1fr;
            }}

            .owner-row-main {{
              align-items: flex-start;
              flex-direction: column;
            }}
          }}
        </style>
      </head>
      <body>
        <main>
          <section class="owner-hero">
            <div class="eyebrow">Tower Owner Dashboard</div>
            <h1>Owner Headquarters.</h1>
            <p class="hero-copy">{summary['tower_meaning']}</p>
          </section>

          <section class="summary-grid">
            {card_html}
          </section>

          <section class="owner-release-card" data-tower-release-review-entry="true">
            <div>
              <div class="eyebrow">Owner release review</div>
              <span class="owner-release-state" data-tower-release-state="{release_state}">
                {release_label}
              </span>
              <p>{release_detail}</p>
              <a class="owner-hosted-readiness"
                 data-tower-hosted-readiness="{hosted_readiness_state}"
                 href="/tower/owner/release-review">
                Hosted readiness · {hosted_readiness_label}
              </a>
              <br>
              <a class="owner-hosted-readiness"
                 data-tower-prerequisite-certificate="{prerequisite_state}"
                 href="/tower/owner/release-review/prerequisites">
                Release prerequisite certificate · {prerequisite_label}
              </a>
            </div>
            <a class="owner-release-link" href="/tower/owner/release-review">
              Open release review
            </a>
          </section>

          <section class="owner-section">
            <h2>People & access</h2>

            {people_html}
          </section>

          <section class="owner-next">
            <strong>Owner next move:</strong>
            {summary['owner_next_action']}
          </section>
        </main>
      </body>
    </html>
    """


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

    register_tower_owner_release_review_routes(app)

    setattr(
        app,
        marker,
        True,
    )

    return app
