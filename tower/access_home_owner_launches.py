
"""Owner shortcut injection for Tower Access Home / TWR128."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, List

from flask import jsonify, redirect, request

from tower.owner_people_registry import (
    owner_people_authority_snapshot,
)
from tower.tower_human_login_ob_launch import (
    owner_session_active,
)


@dataclass(frozen=True)
class TowerAccessHomeLaunch:
    launch_id: str
    title: str
    eyebrow: str
    href: str
    status: str
    owner_only: bool
    danger_action: bool
    explanation: str
    button_label: str


ACCESS_HOME_OWNER_LAUNCHES = (
    TowerAccessHomeLaunch(
        launch_id="tower-owner-headquarters",
        title="Owner Headquarters",
        eyebrow="Owner Control",
        href="/tower/owner-dashboard",
        status="owner_only_route",
        owner_only=True,
        danger_action=False,
        explanation=(
            "Open Tower Owner Headquarters. "
            "Unavailable people/access authority is shown explicitly "
            "rather than replaced with invented records."
        ),
        button_label="Open Owner Headquarters",
    ),
)


def access_home_owner_launches() -> List[Dict[str, Any]]:
    return [
        asdict(launch)
        for launch in ACCESS_HOME_OWNER_LAUNCHES
    ]


def access_home_owner_launch_summary() -> Dict[str, Any]:
    launches = access_home_owner_launches()
    people_authority = owner_people_authority_snapshot()

    return {
        "status":
            "tower_access_home_owner_launches_truthful",

        "launch_count":
            len(launches),

        "routes":
            [
                launch["href"]
                for launch in launches
            ],

        "all_owner_only":
            all(
                launch["owner_only"]
                for launch in launches
            ),

        "danger_actions_enabled":
            any(
                launch["danger_action"]
                for launch in launches
            ),

        "people_authority_state":
            people_authority["verification_state"],

        "live_auto":
            "LOCKED",

        "broker_execution":
            False,

        "capital_action":
            False,

        "meaning": (
            "Access Home exposes Owner Headquarters as the "
            "owner control destination. Security architecture "
            "and technical proof remain outside the primary shortcut dock."
        ),
    }


def _launch_card_html() -> str:
    launch_cards = "\n".join(
        f"""
        <a class="tower-owner-launch-card" href="{launch['href']}">
          <span class="tower-owner-launch-eyebrow">
            {launch['eyebrow']}
          </span>
          <strong>{launch['title']}</strong>
          <p>{launch['explanation']}</p>
          <span class="tower-owner-launch-button">
            {launch['button_label']}
          </span>
          <small>
            Owner-only · No execution authority
          </small>
        </a>
        """
        for launch in access_home_owner_launches()
    )

    return f"""
    <section
      id="tower-owner-launch-dock"
      class="tower-owner-launch-dock"
      aria-label="Tower owner shortcut"
    >
      <style>
        .tower-owner-launch-dock {{
          width: min(1120px, calc(100% - 32px));
          margin: 24px auto 36px;
          padding: 22px;
          border: 1px solid rgba(225,194,128,.28);
          border-radius: 24px;
          background:
            linear-gradient(
              135deg,
              rgba(255,255,255,.075),
              rgba(255,255,255,.025)
            );
          box-shadow: 0 22px 70px rgba(0,0,0,.30);
          color: #f5f0e6;
          font-family:
            Inter, ui-sans-serif, system-ui,
            -apple-system, BlinkMacSystemFont,
            "Segoe UI", sans-serif;
        }}

        .tower-owner-launch-head {{
          display: flex;
          justify-content: space-between;
          gap: 18px;
          align-items: flex-end;
          margin-bottom: 16px;
        }}

        .tower-owner-launch-kicker,
        .tower-owner-launch-eyebrow {{
          color: #dfc181;
          text-transform: uppercase;
          letter-spacing: .14em;
          font-weight: 900;
          font-size: 12px;
        }}

        .tower-owner-launch-head h2 {{
          margin: 6px 0 0;
          font-size: clamp(24px, 4vw, 40px);
          line-height: 1;
        }}

        .tower-owner-launch-head p,
        .tower-owner-launch-card p {{
          color: #b9b0a3;
          line-height: 1.45;
        }}

        .tower-owner-launch-card {{
          display: block;
          text-decoration: none;
          color: #f5f0e6;
          border: 1px solid rgba(255,255,255,.11);
          border-radius: 20px;
          background: rgba(255,255,255,.05);
          padding: 18px;
        }}

        .tower-owner-launch-card strong {{
          display: block;
          font-size: 26px;
          margin: 10px 0;
        }}

        .tower-owner-launch-button {{
          display: inline-flex;
          border: 1px solid rgba(225,194,128,.36);
          background: rgba(225,194,128,.10);
          color: #dfc181;
          border-radius: 999px;
          padding: 9px 12px;
          font-size: 13px;
          font-weight: 900;
        }}

        .tower-owner-launch-card small {{
          display: block;
          color: #968d80;
          margin-top: 14px;
          font-size: 12px;
        }}
      </style>

      <div class="tower-owner-launch-head">
        <div>
          <div class="tower-owner-launch-kicker">
            Tower owner
          </div>
          <h2>Owner Headquarters</h2>
        </div>
        <p>
          One owner destination. Technical security maps and
          audit proof stay outside the normal Access Home.
        </p>
      </div>

      {launch_cards}
    </section>
    """


def inject_owner_launch_dock(
    html: str,
) -> str:
    source = str(html or "")

    if "tower-owner-launch-dock" in source:
        return source

    dock = _launch_card_html()

    if "</body>" in source:
        return source.replace(
            "</body>",
            dock + "\n</body>",
            1,
        )

    if "</html>" in source:
        return source.replace(
            "</html>",
            dock + "\n</html>",
            1,
        )

    return source + dock


def register_tower_access_home_owner_launches(app):
    marker = (
        "_tower_access_home_owner_launches_registered"
    )

    if getattr(app, marker, False):
        return app

    @app.after_request
    def tower_access_home_owner_launch_injector(response):
        if request.path != "/tower/access-home":
            return response

        if response.status_code != 200:
            return response

        content_type = response.headers.get(
            "Content-Type",
            "",
        )

        if "text/html" not in content_type:
            return response

        html = response.get_data(
            as_text=True
        )

        enhanced = inject_owner_launch_dock(
            html
        )

        response.set_data(
            enhanced
        )

        if "Content-Length" in response.headers:
            response.headers["Content-Length"] = str(
                len(response.get_data())
            )

        return response

    @app.route(
        "/tower/access-home-launches.json"
    )
    def tower_access_home_owner_launches_json():
        if not owner_session_active():
            return redirect(
                "/tower/login"
            )

        return jsonify({
            "summary":
                access_home_owner_launch_summary(),

            "launches":
                access_home_owner_launches(),
        })

    setattr(
        app,
        marker,
        True,
    )

    return app
