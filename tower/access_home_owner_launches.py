from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, List

from flask import jsonify, redirect, request

from tower.tower_human_login_ob_launch import owner_session_active


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
        launch_id="tower-owner-dashboard-people-access-desk",
        title="Owner Dashboard",
        eyebrow="People + Access Desk",
        href="/tower/owner-dashboard",
        status="owner_only_live_route",
        owner_only=True,
        danger_action=False,
        explanation=(
            "Open the Tower owner desk for people, staged seats, invite drafts, "
            "access requests, owner review, and danger locks."
        ),
        button_label="Open Owner Dashboard",
    ),
    TowerAccessHomeLaunch(
        launch_id="tower-security-map",
        title="Security Map",
        eyebrow="Locks + Route Coverage",
        href="/tower/security-map",
        status="owner_only_live_route",
        owner_only=True,
        danger_action=False,
        explanation=(
            "Review what Tower protects: app registry, OB route coverage, owner-only rooms, "
            "default-deny behavior, and safety boundaries."
        ),
        button_label="Open Security Map",
    ),
)


def access_home_owner_launches() -> List[Dict[str, Any]]:
    return [
        asdict(launch)
        for launch in ACCESS_HOME_OWNER_LAUNCHES
    ]


def access_home_owner_launch_summary() -> Dict[str, Any]:
    launches = access_home_owner_launches()

    return {
        "status": "tower_access_home_owner_launches_ready",
        "launch_count": len(launches),
        "routes": [
            launch["href"]
            for launch in launches
        ],
        "all_owner_only": all(
            launch["owner_only"]
            for launch in launches
        ),
        "danger_actions_enabled": any(
            launch["danger_action"]
            for launch in launches
        ),
        "real_account_creation": False,
        "real_invites_sent": False,
        "real_access_granted": False,
        "live_auto": "LOCKED",
        "broker_execution": False,
        "capital_action": False,
        "meaning": (
            "Access Home now surfaces the Tower Owner Dashboard and Security Map "
            "as owner-only launch destinations without creating accounts, sending invites, "
            "granting access, or unlocking trading actions."
        ),
    }


def _launch_card_html() -> str:
    launch_cards = "\n".join(
        f"""
        <a class="tower-owner-launch-card" href="{launch['href']}">
          <span class="tower-owner-launch-eyebrow">{launch['eyebrow']}</span>
          <strong>{launch['title']}</strong>
          <p>{launch['explanation']}</p>
          <span class="tower-owner-launch-button">{launch['button_label']}</span>
          <small>{'Owner-only' if launch['owner_only'] else 'Protected'} · No dangerous action</small>
        </a>
        """
        for launch in access_home_owner_launches()
    )

    return f"""
    <section id="tower-owner-launch-dock" class="tower-owner-launch-dock" aria-label="Tower owner launch dock">
      <style>
        .tower-owner-launch-dock {{
          width: min(1120px, calc(100% - 32px));
          margin: 24px auto 36px;
          padding: 22px;
          border: 1px solid rgba(248,217,120,0.28);
          border-radius: 28px;
          background:
            radial-gradient(circle at 12% 0%, rgba(155,124,255,0.22), transparent 24rem),
            linear-gradient(135deg, rgba(255,255,255,0.105), rgba(255,255,255,0.035));
          box-shadow: 0 22px 70px rgba(0,0,0,0.30);
          color: #fff8ff;
          font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        }}

        .tower-owner-launch-head {{
          display: flex;
          justify-content: space-between;
          gap: 18px;
          align-items: flex-end;
          margin-bottom: 16px;
        }}

        .tower-owner-launch-kicker {{
          color: #f8d978;
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

        .tower-owner-launch-head p {{
          margin: 0;
          max-width: 520px;
          color: #cab9ee;
          line-height: 1.45;
        }}

        .tower-owner-launch-grid {{
          display: grid;
          grid-template-columns: repeat(2, minmax(0, 1fr));
          gap: 14px;
        }}

        .tower-owner-launch-card {{
          display: block;
          text-decoration: none;
          color: #fff8ff;
          border: 1px solid rgba(255,255,255,0.12);
          border-radius: 22px;
          background: rgba(255,255,255,0.075);
          padding: 18px;
          min-height: 210px;
          transition: transform .16s ease, background .16s ease, border-color .16s ease;
        }}

        .tower-owner-launch-card:hover {{
          transform: translateY(-2px);
          border-color: rgba(248,217,120,0.48);
          background: rgba(255,255,255,0.105);
        }}

        .tower-owner-launch-eyebrow {{
          display: block;
          color: #f8d978;
          text-transform: uppercase;
          letter-spacing: .12em;
          font-size: 12px;
          font-weight: 900;
          margin-bottom: 10px;
        }}

        .tower-owner-launch-card strong {{
          display: block;
          font-size: 26px;
          margin-bottom: 10px;
        }}

        .tower-owner-launch-card p {{
          color: #cab9ee;
          line-height: 1.45;
          margin: 0 0 16px;
        }}

        .tower-owner-launch-button {{
          display: inline-flex;
          align-items: center;
          justify-content: center;
          border: 1px solid rgba(248,217,120,0.40);
          background: rgba(248,217,120,0.12);
          color: #f8d978;
          border-radius: 999px;
          padding: 9px 12px;
          font-size: 13px;
          font-weight: 900;
        }}

        .tower-owner-launch-card small {{
          display: block;
          color: #b8a9d8;
          margin-top: 14px;
          font-size: 12px;
        }}

        @media (max-width: 820px) {{
          .tower-owner-launch-head {{
            display: block;
          }}

          .tower-owner-launch-head p {{
            margin-top: 10px;
          }}

          .tower-owner-launch-grid {{
            grid-template-columns: 1fr;
          }}
        }}
      </style>

      <div class="tower-owner-launch-head">
        <div>
          <div class="tower-owner-launch-kicker">Tower owner shortcuts</div>
          <h2>Your owner rooms are ready.</h2>
        </div>
        <p>
          Access Home now points to the people/access desk and the lock map.
          These are view/control rooms only — no real accounts, invites, or access grants happen here yet.
        </p>
      </div>

      <div class="tower-owner-launch-grid">
        {launch_cards}
      </div>
    </section>
    """


def inject_owner_launch_dock(html: str) -> str:
    source = str(html or "")

    if "tower-owner-launch-dock" in source:
        return source

    dock = _launch_card_html()

    if "</body>" in source:
        return source.replace("</body>", dock + "\n</body>", 1)

    if "</html>" in source:
        return source.replace("</html>", dock + "\n</html>", 1)

    return source + dock


def register_tower_access_home_owner_launches(app):
    marker = "_tower_access_home_owner_launches_registered"

    if getattr(app, marker, False):
        return app

    @app.after_request
    def tower_access_home_owner_launch_injector(response):
        if request.path != "/tower/access-home":
            return response

        if response.status_code != 200:
            return response

        content_type = response.headers.get("Content-Type", "")

        if "text/html" not in content_type:
            return response

        html = response.get_data(as_text=True)
        enhanced = inject_owner_launch_dock(html)

        response.set_data(enhanced)

        if "Content-Length" in response.headers:
            response.headers["Content-Length"] = str(len(response.get_data()))

        return response

    @app.route("/tower/access-home-launches.json")
    def tower_access_home_owner_launches_json():
        if not owner_session_active():
            return redirect("/tower/login")

        return jsonify(
            {
                "summary": access_home_owner_launch_summary(),
                "launches": access_home_owner_launches(),
            }
        )

    setattr(app, marker, True)

    return app
