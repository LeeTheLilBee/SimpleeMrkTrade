from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, List

from flask import jsonify, redirect, request

from tower.tower_human_login_ob_launch import owner_session_active


@dataclass(frozen=True)
class TowerPersonProfile:
    person_id: str
    display_name: str
    designation: str
    relationship: str
    status: str
    assigned_scope: str
    access_summary: str
    needs: str
    risk_note: str


DESIGNATION_OPTIONS = (
    "Family",
    "Employee",
    "Manager",
    "Contractor",
    "Advisor",
    "Trustee",
    "Vendor",
    "Beta Tester",
    "Observer",
)


APP_ACCESS_OPTIONS = (
    "No Access",
    "View Only",
    "Limited Workspace",
    "Manager Tools",
    "Owner Review Required",
    "Blocked",
)


APP_MATRIX = (
    "Tower",
    "Observatory",
    "Teller",
    "Vault",
    "Clouds",
    "Grounds",
)


PEOPLE_PROFILE_ROOMS = (
    TowerPersonProfile(
        person_id="future-manager-seat",
        display_name="Future Manager Seat",
        designation="Manager Candidate",
        relationship="Business operations",
        status="staged_profile",
        assigned_scope="Tower only for now",
        access_summary="No real access granted. Manager tools remain draft-only.",
        needs="Role definition, app assignment, paperwork, owner approval.",
        risk_note="Cannot invite others, move money, see Vault records, or touch OB Live.",
    ),
    TowerPersonProfile(
        person_id="future-family-friend-seat",
        display_name="Future Family / Friend Seat",
        designation="Family / Friend Candidate",
        relationship="Personal network",
        status="staged_profile",
        assigned_scope="No app access by default",
        access_summary="Family relationship does not equal platform access.",
        needs="Sliding-scale/payment terms, invite terms, privacy boundaries.",
        risk_note="Cannot access OB, Vault, trust records, payroll, or sensitive admin.",
    ),
    TowerPersonProfile(
        person_id="future-trustee-advisor-seat",
        display_name="Future Trustee / Advisor Seat",
        designation="Trustee / Advisor Candidate",
        relationship="Trust or strategic support",
        status="staged_profile",
        assigned_scope="Owner review required",
        access_summary="Sensitive seat. Everything stays owner-reviewed and blocked by default.",
        needs="Trust role clarity, paperwork, confidentiality, dual-approval rules.",
        risk_note="Cannot change trust/admin permissions or export sensitive proof.",
    ),
    TowerPersonProfile(
        person_id="future-beta-tester-seat",
        display_name="Future Beta Tester Seat",
        designation="Beta Tester Candidate",
        relationship="Platform tester",
        status="staged_profile",
        assigned_scope="Beta surfaces only later",
        access_summary="Survey/Paper access only when beta gates open. Live stays blocked.",
        needs="Beta terms, feedback lane, app scope, NDA if needed.",
        risk_note="Cannot access Live Auto, broker actions, capital, owner rooms, or Vault.",
    ),
)


def people_profile_rooms() -> List[Dict[str, Any]]:
    return [
        asdict(profile)
        for profile in PEOPLE_PROFILE_ROOMS
    ]


def people_profile_by_id(person_id: str) -> Dict[str, Any] | None:
    normalized = str(person_id or "").strip().lower()

    for profile in people_profile_rooms():
        if profile["person_id"] == normalized:
            return profile

    return None


def people_profile_summary() -> Dict[str, Any]:
    return {
        "status": "tower_people_profile_rooms_ready",
        "person_room_count": len(PEOPLE_PROFILE_ROOMS),
        "homepage_clutter_policy": "calm_home_power_behind_names",
        "routes": [
            f"/tower/owner-dashboard/person/{profile.person_id}"
            for profile in PEOPLE_PROFILE_ROOMS
        ],
        "designation_options": list(DESIGNATION_OPTIONS),
        "app_access_options": list(APP_ACCESS_OPTIONS),
        "app_matrix": list(APP_MATRIX),
        "real_account_creation": False,
        "real_invites_sent": False,
        "real_access_granted": False,
        "real_permission_changes": False,
        "live_auto": "LOCKED",
        "broker_execution": False,
        "capital_action": False,
        "meaning": (
            "People + Access Desk stays calm. Person-level designation, access, paperwork, "
            "risk locks, notes, and freezes live behind each person's name as draft-only controls."
        ),
    }


def build_designation_change_draft(person_id: str, designation: str, notes: str = "") -> Dict[str, Any]:
    profile = people_profile_by_id(person_id)

    if not profile:
        return {
            "status": "not_found",
            "person_id": person_id,
            "real_permission_changes": False,
            "real_access_granted": False,
        }

    clean_designation = str(designation or "").strip()

    if clean_designation not in DESIGNATION_OPTIONS:
        return {
            "status": "invalid_designation",
            "person_id": person_id,
            "allowed_designations": list(DESIGNATION_OPTIONS),
            "real_permission_changes": False,
            "real_access_granted": False,
        }

    return {
        "status": "designation_change_draft_created",
        "person_id": profile["person_id"],
        "display_name": profile["display_name"],
        "current_designation": profile["designation"],
        "requested_designation": clean_designation,
        "notes": str(notes or "").strip(),
        "requires_owner_review": True,
        "creates_real_account": False,
        "sends_real_invite": False,
        "grants_real_access": False,
        "changes_real_permissions": False,
        "live_auto": "LOCKED",
        "broker_execution": False,
        "capital_action": False,
    }


def build_app_access_change_draft(
    person_id: str,
    app_name: str,
    access_level: str,
    notes: str = "",
) -> Dict[str, Any]:
    profile = people_profile_by_id(person_id)

    if not profile:
        return {
            "status": "not_found",
            "person_id": person_id,
            "grants_real_access": False,
            "changes_real_permissions": False,
        }

    clean_app = str(app_name or "").strip()
    clean_access = str(access_level or "").strip()

    if clean_app not in APP_MATRIX:
        return {
            "status": "invalid_app",
            "person_id": person_id,
            "allowed_apps": list(APP_MATRIX),
            "grants_real_access": False,
            "changes_real_permissions": False,
        }

    if clean_access not in APP_ACCESS_OPTIONS:
        return {
            "status": "invalid_access_level",
            "person_id": person_id,
            "allowed_access_levels": list(APP_ACCESS_OPTIONS),
            "grants_real_access": False,
            "changes_real_permissions": False,
        }

    return {
        "status": "app_access_change_draft_created",
        "person_id": profile["person_id"],
        "display_name": profile["display_name"],
        "app_name": clean_app,
        "requested_access_level": clean_access,
        "notes": str(notes or "").strip(),
        "requires_owner_review": True,
        "creates_real_account": False,
        "sends_real_invite": False,
        "grants_real_access": False,
        "changes_real_permissions": False,
        "live_auto": "LOCKED",
        "broker_execution": False,
        "capital_action": False,
    }


def build_person_freeze_draft(person_id: str, reason: str = "") -> Dict[str, Any]:
    profile = people_profile_by_id(person_id)

    if not profile:
        return {
            "status": "not_found",
            "person_id": person_id,
            "freezes_real_access": False,
        }

    return {
        "status": "person_freeze_draft_created",
        "person_id": profile["person_id"],
        "display_name": profile["display_name"],
        "reason": str(reason or "").strip(),
        "requires_owner_review": True,
        "freezes_real_access": False,
        "creates_real_account": False,
        "sends_real_invite": False,
        "grants_real_access": False,
        "changes_real_permissions": False,
        "live_auto": "LOCKED",
        "broker_execution": False,
        "capital_action": False,
    }


def _back_nav_html(active: str) -> str:
    owner_active = "active" if active == "owner" else ""
    security_active = "active" if active == "security" else ""

    return f"""
    <nav id="tower-owner-back-nav" class="tower-owner-back-nav" aria-label="Tower owner room navigation">
      <style>
        .tower-owner-back-nav {{
          width: min(1120px, calc(100% - 32px));
          margin: 18px auto 14px;
          padding: 12px;
          border: 1px solid rgba(248,217,120,0.22);
          border-radius: 999px;
          background: rgba(16, 9, 34, 0.82);
          box-shadow: 0 18px 50px rgba(0,0,0,0.22);
          display: flex;
          gap: 10px;
          flex-wrap: wrap;
          justify-content: center;
          align-items: center;
          font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
          color: #fff8ff;
        }}

        .tower-owner-back-nav a {{
          text-decoration: none;
          color: #fff8ff;
          border: 1px solid rgba(255,255,255,0.12);
          background: rgba(255,255,255,0.07);
          border-radius: 999px;
          padding: 10px 13px;
          font-weight: 900;
          font-size: 13px;
        }}

        .tower-owner-back-nav a.active {{
          color: #f8d978;
          border-color: rgba(248,217,120,0.45);
          background: rgba(248,217,120,0.11);
        }}

        .tower-owner-back-nav span {{
          color: #b8a9d8;
          font-size: 12px;
          font-weight: 800;
        }}
      </style>

      <a href="/tower/access-home">← Back to Access Home</a>
      <a class="{owner_active}" href="/tower/owner-dashboard">People + Access Desk</a>
      <a class="{security_active}" href="/tower/security-map">Security Map</a>
      <span>Draft-only controls · no real access changes</span>
    </nav>
    """


def _people_rooms_dock_html() -> str:
    cards = "\n".join(
        f"""
        <a class="tower-person-room-card" href="/tower/owner-dashboard/person/{profile['person_id']}">
          <span>{profile['designation']}</span>
          <strong>{profile['display_name']}</strong>
          <p>{profile['access_summary']}</p>
          <small>{profile['needs']}</small>
        </a>
        """
        for profile in people_profile_rooms()
    )

    return f"""
    <section id="tower-people-room-dock" class="tower-people-room-dock" aria-label="Tower people profile rooms">
      <style>
        .tower-people-room-dock {{
          width: min(1120px, calc(100% - 32px));
          margin: 16px auto 30px;
          padding: 20px;
          border: 1px solid rgba(155,124,255,0.26);
          border-radius: 28px;
          background:
            radial-gradient(circle at 10% 0%, rgba(248,217,120,0.14), transparent 22rem),
            linear-gradient(135deg, rgba(255,255,255,0.085), rgba(255,255,255,0.032));
          color: #fff8ff;
          box-shadow: 0 20px 60px rgba(0,0,0,0.25);
          font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        }}

        .tower-people-room-head {{
          display: flex;
          justify-content: space-between;
          gap: 16px;
          align-items: flex-end;
          margin-bottom: 14px;
        }}

        .tower-people-room-head h2 {{
          margin: 0;
          font-size: clamp(24px, 4vw, 38px);
          line-height: 1;
        }}

        .tower-people-room-head p {{
          margin: 0;
          max-width: 520px;
          color: #cab9ee;
          line-height: 1.45;
        }}

        .tower-people-room-grid {{
          display: grid;
          grid-template-columns: repeat(4, minmax(0, 1fr));
          gap: 12px;
        }}

        .tower-person-room-card {{
          display: block;
          text-decoration: none;
          color: #fff8ff;
          border: 1px solid rgba(255,255,255,0.12);
          border-radius: 20px;
          padding: 15px;
          background: rgba(255,255,255,0.065);
          min-height: 190px;
          transition: transform .16s ease, border-color .16s ease, background .16s ease;
        }}

        .tower-person-room-card:hover {{
          transform: translateY(-2px);
          border-color: rgba(248,217,120,0.45);
          background: rgba(255,255,255,0.095);
        }}

        .tower-person-room-card span {{
          display: block;
          color: #f8d978;
          text-transform: uppercase;
          letter-spacing: .12em;
          font-size: 11px;
          font-weight: 900;
          margin-bottom: 8px;
        }}

        .tower-person-room-card strong {{
          display: block;
          font-size: 21px;
          line-height: 1.05;
          margin-bottom: 10px;
        }}

        .tower-person-room-card p {{
          color: #cab9ee;
          line-height: 1.35;
          margin: 0 0 10px;
          font-size: 13px;
        }}

        .tower-person-room-card small {{
          color: #b8a9d8;
          line-height: 1.35;
          display: block;
        }}

        @media (max-width: 980px) {{
          .tower-people-room-grid {{
            grid-template-columns: repeat(2, minmax(0, 1fr));
          }}
        }}

        @media (max-width: 620px) {{
          .tower-people-room-head {{
            display: block;
          }}

          .tower-people-room-head p {{
            margin-top: 10px;
          }}

          .tower-people-room-grid {{
            grid-template-columns: 1fr;
          }}
        }}
      </style>

      <div class="tower-people-room-head">
        <div>
          <div style="color:#f8d978;text-transform:uppercase;letter-spacing:.14em;font-weight:900;font-size:12px;">
            People rooms
          </div>
          <h2>Click a name to control the room behind it.</h2>
        </div>
        <p>
          The People + Access Desk stays calm here. Designation changes, app access,
          paperwork, notes, risk locks, and freeze drafts live behind each person’s name.
        </p>
      </div>

      <div class="tower-people-room-grid">
        {cards}
      </div>
    </section>
    """


def inject_back_nav(html: str, *, active: str) -> str:
    source = str(html or "")

    if "tower-owner-back-nav" in source:
        return source

    nav = _back_nav_html(active)

    if "<body" in source:
        marker_end = source.find(">", source.find("<body"))
        if marker_end != -1:
            return source[: marker_end + 1] + nav + source[marker_end + 1 :]

    return nav + source


def inject_people_room_dock(html: str) -> str:
    source = str(html or "")

    if "tower-people-room-dock" in source:
        return source

    dock = _people_rooms_dock_html()

    if "tower-owner-launch-dock" in source:
        return source.replace("tower-owner-launch-dock", "tower-owner-launch-dock", 1) + dock

    if "</body>" in source:
        return source.replace("</body>", dock + "\n</body>", 1)

    return source + dock


def _person_profile_room_html(profile: Dict[str, Any]) -> str:
    designation_buttons = "\n".join(
        f"""
        <button type="button" data-draft-designation="{designation}">
          {designation}
        </button>
        """
        for designation in DESIGNATION_OPTIONS
    )

    app_rows = "\n".join(
        f"""
        <div class="tower-person-app-row">
          <strong>{app_name}</strong>
          <span>Default: Blocked / owner review required</span>
          <a href="/tower/owner-dashboard/person/{profile['person_id']}.json?draft_app={app_name}">
            Preview {app_name} draft
          </a>
        </div>
        """
        for app_name in APP_MATRIX
    )

    return f"""
    <!doctype html>
    <html lang="en">
    <head>
      <meta charset="utf-8">
      <meta name="viewport" content="width=device-width,initial-scale=1">
      <title>Tower Person Room · {profile['display_name']}</title>
      <style>
        :root {{
          color-scheme: dark;
        }}

        body {{
          margin: 0;
          min-height: 100vh;
          background:
            radial-gradient(circle at 18% 0%, rgba(155,124,255,0.24), transparent 30rem),
            radial-gradient(circle at 90% 12%, rgba(248,217,120,0.16), transparent 26rem),
            linear-gradient(135deg, #090615, #150d2f 48%, #05040c);
          color: #fff8ff;
          font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        }}

        .tower-person-shell {{
          width: min(1120px, calc(100% - 32px));
          margin: 0 auto;
          padding: 28px 0 44px;
        }}

        .tower-person-hero {{
          border: 1px solid rgba(248,217,120,0.28);
          border-radius: 34px;
          padding: 26px;
          background: rgba(255,255,255,0.075);
          box-shadow: 0 24px 76px rgba(0,0,0,0.34);
        }}

        .tower-person-kicker {{
          color: #f8d978;
          text-transform: uppercase;
          letter-spacing: .14em;
          font-size: 12px;
          font-weight: 900;
        }}

        h1 {{
          font-size: clamp(38px, 8vw, 76px);
          line-height: .9;
          margin: 10px 0 12px;
        }}

        .tower-person-summary {{
          color: #cab9ee;
          font-size: 18px;
          max-width: 760px;
          line-height: 1.45;
        }}

        .tower-person-grid {{
          display: grid;
          grid-template-columns: minmax(0, 1.1fr) minmax(320px, .9fr);
          gap: 16px;
          margin-top: 16px;
        }}

        .tower-person-panel {{
          border: 1px solid rgba(255,255,255,0.12);
          border-radius: 26px;
          background: rgba(255,255,255,0.064);
          padding: 18px;
        }}

        .tower-person-panel h2 {{
          margin: 0 0 12px;
          font-size: 24px;
        }}

        .tower-person-field {{
          display: grid;
          grid-template-columns: 170px minmax(0, 1fr);
          gap: 12px;
          padding: 10px 0;
          border-bottom: 1px solid rgba(255,255,255,0.08);
        }}

        .tower-person-field span {{
          color: #b8a9d8;
          font-weight: 900;
        }}

        .tower-person-field strong {{
          color: #fff8ff;
        }}

        .tower-designation-buttons {{
          display: flex;
          flex-wrap: wrap;
          gap: 8px;
        }}

        .tower-designation-buttons button,
        .tower-person-action {{
          border: 1px solid rgba(248,217,120,0.32);
          background: rgba(248,217,120,0.10);
          color: #f8d978;
          border-radius: 999px;
          padding: 10px 12px;
          font-weight: 900;
          cursor: default;
        }}

        .tower-person-app-row {{
          border: 1px solid rgba(255,255,255,0.10);
          border-radius: 18px;
          padding: 12px;
          margin-bottom: 10px;
          display: grid;
          gap: 6px;
        }}

        .tower-person-app-row span {{
          color: #cab9ee;
        }}

        .tower-person-app-row a {{
          color: #f8d978;
          font-weight: 900;
          text-decoration: none;
        }}

        .tower-lock-list {{
          display: grid;
          gap: 9px;
          color: #cab9ee;
        }}

        .tower-lock-list div {{
          border: 1px solid rgba(255,255,255,0.10);
          border-radius: 16px;
          padding: 10px;
          background: rgba(0,0,0,0.12);
        }}

        @media (max-width: 880px) {{
          .tower-person-grid {{
            grid-template-columns: 1fr;
          }}

          .tower-person-field {{
            grid-template-columns: 1fr;
          }}
        }}
      </style>
    </head>

    <body>
      {_back_nav_html(active="owner")}

      <main class="tower-person-shell">
        <section class="tower-person-hero">
          <div class="tower-person-kicker">Person room · draft-only controls</div>
          <h1>{profile['display_name']}</h1>
          <p class="tower-person-summary">
            {profile['access_summary']} This room gives Solice the control surface behind the name,
            without creating accounts, sending invites, granting access, or changing live permissions yet.
          </p>
        </section>

        <section class="tower-person-grid">
          <article class="tower-person-panel">
            <h2>Identity snapshot</h2>
            <div class="tower-person-field"><span>Designation</span><strong>{profile['designation']}</strong></div>
            <div class="tower-person-field"><span>Relationship</span><strong>{profile['relationship']}</strong></div>
            <div class="tower-person-field"><span>Status</span><strong>{profile['status']}</strong></div>
            <div class="tower-person-field"><span>Assigned scope</span><strong>{profile['assigned_scope']}</strong></div>
            <div class="tower-person-field"><span>Needs</span><strong>{profile['needs']}</strong></div>
            <div class="tower-person-field"><span>Risk note</span><strong>{profile['risk_note']}</strong></div>
          </article>

          <aside class="tower-person-panel">
            <h2>Designation controls</h2>
            <p style="color:#cab9ee;line-height:1.45;">
              These buttons are draft-only. They preview what Solice may choose later; they do not change real permissions.
            </p>
            <div class="tower-designation-buttons">
              {designation_buttons}
            </div>
            <p style="color:#b8a9d8;font-size:13px;">
              API draft endpoint: /tower/owner-dashboard/person/{profile['person_id']}/designation-draft
            </p>
          </aside>

          <article class="tower-person-panel">
            <h2>App access matrix</h2>
            <p style="color:#cab9ee;line-height:1.45;">
              Designation is who they are. App access is what they can do. These stay separate.
            </p>
            {app_rows}
          </article>

          <aside class="tower-person-panel">
            <h2>Danger locks</h2>
            <div class="tower-lock-list">
              <div>Live Auto: LOCKED</div>
              <div>Broker execution: false</div>
              <div>Capital action: false</div>
              <div>Real account creation: false</div>
              <div>Real invite sending: false</div>
              <div>Real access grants: false</div>
              <div>Vault direct access: blocked</div>
              <div>Permission changes: draft-only</div>
            </div>

            <p style="margin-top:16px;">
              <a class="tower-person-action" href="/tower/owner-dashboard/person/{profile['person_id']}.json">
                Open JSON profile
              </a>
            </p>
          </aside>
        </section>
      </main>
    </body>
    </html>
    """


def register_tower_people_profile_rooms(app):
    marker = "_tower_people_profile_rooms_twr016_020_registered"

    if getattr(app, marker, False):
        return app

    @app.after_request
    def tower_people_profile_rooms_injector(response):
        if response.status_code != 200:
            return response

        content_type = response.headers.get("Content-Type", "")

        if "text/html" not in content_type:
            return response

        if request.path == "/tower/owner-dashboard":
            html = response.get_data(as_text=True)
            html = inject_back_nav(html, active="owner")
            html = inject_people_room_dock(html)
            response.set_data(html)
            response.headers["Content-Length"] = str(len(response.get_data()))
            return response

        if request.path == "/tower/security-map":
            html = response.get_data(as_text=True)
            html = inject_back_nav(html, active="security")
            response.set_data(html)
            response.headers["Content-Length"] = str(len(response.get_data()))
            return response

        return response

    @app.route("/tower/owner-dashboard/people.json")
    def tower_owner_dashboard_people_rooms_json():
        if not owner_session_active():
            return redirect("/tower/login")

        return jsonify(
            {
                "summary": people_profile_summary(),
                "people": people_profile_rooms(),
            }
        )

    @app.route("/tower/owner-dashboard/person/<person_id>")
    def tower_owner_dashboard_person_room(person_id: str):
        if not owner_session_active():
            return redirect("/tower/login")

        profile = people_profile_by_id(person_id)

        if not profile:
            return (
                _person_profile_room_html(
                    {
                        "person_id": "not-found",
                        "display_name": "Person Room Not Found",
                        "designation": "Unknown",
                        "relationship": "Unknown",
                        "status": "not_found",
                        "assigned_scope": "No access",
                        "access_summary": "Tower could not find this staged person room.",
                        "needs": "Return to People + Access Desk.",
                        "risk_note": "No real access changed.",
                    }
                ),
                404,
            )

        return _person_profile_room_html(profile)

    @app.route("/tower/owner-dashboard/person/<person_id>.json")
    def tower_owner_dashboard_person_room_json(person_id: str):
        if not owner_session_active():
            return redirect("/tower/login")

        profile = people_profile_by_id(person_id)

        if not profile:
            return jsonify(
                {
                    "status": "not_found",
                    "person_id": person_id,
                    "real_access_granted": False,
                    "real_permission_changes": False,
                }
            ), 404

        return jsonify(
            {
                "status": "person_profile_room_ready",
                "profile": profile,
                "designation_options": list(DESIGNATION_OPTIONS),
                "app_matrix": list(APP_MATRIX),
                "app_access_options": list(APP_ACCESS_OPTIONS),
                "safety": {
                    "real_account_creation": False,
                    "real_invites_sent": False,
                    "real_access_granted": False,
                    "real_permission_changes": False,
                    "live_auto": "LOCKED",
                    "broker_execution": False,
                    "capital_action": False,
                },
            }
        )

    @app.route("/tower/owner-dashboard/person/<person_id>/designation-draft", methods=["POST"])
    def tower_owner_dashboard_person_designation_draft(person_id: str):
        if not owner_session_active():
            return redirect("/tower/login")

        payload = request.get_json(silent=True) or request.form or {}

        draft = build_designation_change_draft(
            person_id=person_id,
            designation=payload.get("designation", ""),
            notes=payload.get("notes", ""),
        )

        status_code = 200 if draft["status"] == "designation_change_draft_created" else 400

        return jsonify(draft), status_code

    @app.route("/tower/owner-dashboard/person/<person_id>/app-access-draft", methods=["POST"])
    def tower_owner_dashboard_person_app_access_draft(person_id: str):
        if not owner_session_active():
            return redirect("/tower/login")

        payload = request.get_json(silent=True) or request.form or {}

        draft = build_app_access_change_draft(
            person_id=person_id,
            app_name=payload.get("app_name", ""),
            access_level=payload.get("access_level", ""),
            notes=payload.get("notes", ""),
        )

        status_code = 200 if draft["status"] == "app_access_change_draft_created" else 400

        return jsonify(draft), status_code

    @app.route("/tower/owner-dashboard/person/<person_id>/freeze-draft", methods=["POST"])
    def tower_owner_dashboard_person_freeze_draft(person_id: str):
        if not owner_session_active():
            return redirect("/tower/login")

        payload = request.get_json(silent=True) or request.form or {}

        draft = build_person_freeze_draft(
            person_id=person_id,
            reason=payload.get("reason", ""),
        )

        status_code = 200 if draft["status"] == "person_freeze_draft_created" else 400

        return jsonify(draft), status_code

    setattr(app, marker, True)

    return app
