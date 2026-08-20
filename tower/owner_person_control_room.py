from __future__ import annotations

from flask import request


PERSON_CONTROL_ROOM_MARKER = "tower-person-control-room-twr046-050"


TOWER_ACCESS_AREAS = [
    "Access Home",
    "People + seats",
    "Security Map",
    "Owner Dashboard",
    "The Teller",
    "The Vault",
    "The Clouds",
]


OBSERVATORY_ACCESS_AREAS = [
    "Dashboard",
    "Market Map",
    "Symbol Page",
    "Trade Center",
    "Review Center",
    "Owner Console",
    "Owner Dashboard",
]


PERSON_ROOM_SECTIONS = [
    "Identity",
    "Designation",
    "Responsibilities",
    "Companies",
    "Access",
    "Paperwork",
    "Activity",
    "Notes",
    "Change Queue",
]


def person_control_room_summary() -> dict:
    return {
        "status": "tower_person_control_room_ready",
        "product_rule": "person_room_is_owner_control_surface",
        "person_room_sections": PERSON_ROOM_SECTIONS,
        "tower_access_areas": TOWER_ACCESS_AREAS,
        "observatory_access_areas": OBSERVATORY_ACCESS_AREAS,
        "designation_change": "draft_only",
        "responsibility_change": "draft_only",
        "access_change": "draft_only",
        "status_change": "draft_only",
        "freeze_change": "draft_only",
        "restore_change": "draft_only",
        "paperwork_review": "owner_review_only",
        "activity_history": True,
        "real_account_creation": False,
        "real_invites_sent": False,
        "real_access_granted": False,
        "real_access_revoked": False,
        "real_person_suspended": False,
        "real_permission_changes": False,
        "live_auto": "LOCKED",
        "broker_execution": False,
        "capital_action": False,
    }


def _control_room_style() -> str:
    return """
    <style id="tower-person-control-room-style-twr046-050">

      .tower-person-control-room {
        margin: 18px 0 0;
        display: grid;
        gap: 14px;
      }

      .tower-person-control-header {
        padding: 18px;
        border-radius: 24px;
        border: 1px solid rgba(248,217,120,0.22);
        background:
          radial-gradient(circle at 0% 0%, rgba(248,217,120,0.15), transparent 36%),
          radial-gradient(circle at 100% 0%, rgba(115,76,255,0.14), transparent 34%),
          rgba(10,8,25,0.72);
      }

      .tower-person-control-kicker {
        color: #f8d978;
        text-transform: uppercase;
        letter-spacing: .13em;
        font-size: 11px;
        font-weight: 950;
        margin: 0 0 6px;
      }

      .tower-person-control-title {
        margin: 0;
        color: #fff8ff;
        font-size: clamp(22px, 4vw, 34px);
        font-weight: 950;
        letter-spacing: -.035em;
      }

      .tower-person-control-subtitle {
        margin: 6px 0 0;
        color: rgba(255,248,255,0.68);
        font-size: 13px;
        line-height: 1.45;
      }

      .tower-person-control-chip-row {
        display: flex;
        flex-wrap: wrap;
        gap: 7px;
        margin-top: 12px;
      }

      .tower-person-control-chip {
        border-radius: 999px;
        border: 1px solid rgba(255,255,255,0.12);
        background: rgba(255,255,255,0.07);
        color: rgba(255,248,255,0.82);
        padding: 7px 10px;
        font-size: 11px;
        font-weight: 900;
      }

      .tower-person-control-chip strong {
        color: #f8d978;
      }

      .tower-person-control-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
        gap: 12px;
      }

      .tower-person-control-card {
        border: 1px solid rgba(255,255,255,0.10);
        border-radius: 20px;
        background: rgba(255,255,255,0.052);
        padding: 14px;
      }

      .tower-person-control-card h3 {
        margin: 0 0 8px;
        color: #fff8ff;
        font-size: 15px;
        font-weight: 950;
      }

      .tower-person-control-card p {
        margin: 5px 0;
        color: rgba(255,248,255,0.70);
        font-size: 12px;
        line-height: 1.4;
      }

      .tower-person-control-card strong {
        color: #f8d978;
      }

      .tower-person-control-button-row {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        margin-top: 10px;
      }

      .tower-person-control-button {
        border: 1px solid rgba(248,217,120,0.30);
        border-radius: 999px;
        background: rgba(248,217,120,0.10);
        color: #f8d978;
        padding: 8px 11px;
        font: inherit;
        font-size: 12px;
        font-weight: 950;
        cursor: pointer;
      }

      .tower-person-control-button.danger {
        border-color: rgba(255,111,139,0.30);
        background: rgba(255,111,139,0.10);
        color: #ff9bb0;
      }

      .tower-person-control-drawer {
        margin-top: 10px;
        border-top: 1px solid rgba(255,255,255,0.08);
        padding-top: 10px;
      }

      .tower-person-control-drawer[hidden] {
        display: none !important;
      }

      .tower-person-control-field {
        margin: 8px 0;
      }

      .tower-person-control-field label {
        display: block;
        color: #f8d978;
        text-transform: uppercase;
        letter-spacing: .09em;
        font-size: 10px;
        font-weight: 950;
        margin-bottom: 5px;
      }

      .tower-person-control-field input,
      .tower-person-control-field select,
      .tower-person-control-field textarea {
        width: 100%;
        box-sizing: border-box;
        border-radius: 13px;
        border: 1px solid rgba(255,255,255,0.12);
        background: rgba(255,255,255,0.065);
        color: #fff8ff;
        padding: 9px 10px;
        font: inherit;
        font-size: 12px;
      }

      .tower-person-control-field textarea {
        min-height: 76px;
        resize: vertical;
      }

      .tower-person-access-table {
        display: grid;
        gap: 6px;
        margin-top: 8px;
      }

      .tower-person-access-row {
        display: grid;
        grid-template-columns: 1fr auto;
        align-items: center;
        gap: 10px;
        padding: 8px 9px;
        border-radius: 12px;
        background: rgba(255,255,255,0.045);
        border: 1px solid rgba(255,255,255,0.08);
        color: rgba(255,248,255,0.78);
        font-size: 12px;
      }

      .tower-person-access-state {
        color: #f8d978;
        font-size: 10px;
        font-weight: 950;
        text-transform: uppercase;
        letter-spacing: .08em;
      }

      .tower-person-activity {
        display: grid;
        gap: 8px;
      }

      .tower-person-activity-item {
        padding-left: 12px;
        border-left: 2px solid rgba(248,217,120,0.24);
      }

      .tower-person-activity-item strong {
        display: block;
        color: #fff8ff;
        font-size: 12px;
      }

      .tower-person-activity-item span {
        color: rgba(255,248,255,0.62);
        font-size: 11px;
      }

      .tower-person-safety-note {
        border-radius: 16px;
        border: 1px solid rgba(248,217,120,0.20);
        background: rgba(248,217,120,0.065);
        color: rgba(255,248,255,0.74);
        padding: 11px;
        font-size: 11px;
        line-height: 1.45;
      }

    </style>
    """


def _control_room_script() -> str:
    return """
    <script id="tower-person-control-room-twr046-050">
      (function () {

        function routePersonId() {
          var match = window.location.pathname.match(
            /^\\/tower\\/owner-dashboard\\/person\\/([^/]+)$/
          );

          return match ? decodeURIComponent(match[1]) : "";
        }

        function titleFromPage(personId) {
          var candidates = Array.prototype.slice.call(
            document.querySelectorAll("h1, h2, h3")
          );

          for (var i = 0; i < candidates.length; i++) {
            var text = (candidates[i].innerText || "").trim();

            if (text && text.length < 100) {
              return text;
            }
          }

          return personId
            .replace(/-/g, " ")
            .replace(/\\b\\w/g, function (m) { return m.toUpperCase(); });
        }

        function towerAccessRows() {
          var areas = [
            "Access Home",
            "People + seats",
            "Security Map",
            "Owner Dashboard",
            "The Teller",
            "The Vault",
            "The Clouds"
          ];

          return areas.map(function (area) {
            return [
              '<div class="tower-person-access-row">',
                '<span>' + area + '</span>',
                '<span class="tower-person-access-state">Review</span>',
              '</div>'
            ].join("");
          }).join("");
        }

        function obAccessRows() {
          var areas = [
            "Dashboard",
            "Market Map",
            "Symbol Page",
            "Trade Center",
            "Review Center",
            "Owner Console",
            "Owner Dashboard"
          ];

          return areas.map(function (area) {
            return [
              '<div class="tower-person-access-row">',
                '<span>' + area + '</span>',
                '<span class="tower-person-access-state">Review</span>',
              '</div>'
            ].join("");
          }).join("");
        }

        function buildControlRoom(personId, title) {
          var room = document.createElement("section");

          room.className = "tower-person-control-room";
          room.setAttribute("data-tower-person-control-room", "true");
          room.setAttribute("data-person-id", personId);

          room.innerHTML = [
            '<section class="tower-person-control-header">',
              '<p class="tower-person-control-kicker">Person Control Room</p>',
              '<h2 class="tower-person-control-title">' + title + '</h2>',
              '<p class="tower-person-control-subtitle">',
                'Identity, designation, responsibilities, access, paperwork, history, notes, and owner-review actions.',
              '</p>',
              '<div class="tower-person-control-chip-row">',
                '<span class="tower-person-control-chip"><strong>Status</strong> Planned / controlled</span>',
                '<span class="tower-person-control-chip"><strong>Access</strong> Owner review required</span>',
                '<span class="tower-person-control-chip"><strong>Changes</strong> Draft-only</span>',
              '</div>',
            '</section>',

            '<section class="tower-person-control-grid">',

              '<article class="tower-person-control-card">',
                '<h3>Identity + designation</h3>',
                '<p><strong>Person ID</strong> ' + personId + '</p>',
                '<p><strong>Current designation</strong> Existing Tower profile</p>',
                '<p><strong>Organizational lane</strong> Owner-defined</p>',
                '<div class="tower-person-control-button-row">',
                  '<button class="tower-person-control-button" type="button" data-tower-drawer-toggle="designation">Change designation</button>',
                  '<button class="tower-person-control-button" type="button" data-tower-drawer-toggle="responsibility">Responsibilities</button>',
                '</div>',

                '<div class="tower-person-control-drawer" data-tower-drawer="designation" hidden>',
                  '<div class="tower-person-control-field">',
                    '<label>Requested designation</label>',
                    '<input placeholder="Example: Operations Manager">',
                  '</div>',
                  '<div class="tower-person-control-field">',
                    '<label>Organizational lane</label>',
                    '<input placeholder="Example: Operations / Payroll / Advisory">',
                  '</div>',
                  '<div class="tower-person-control-field">',
                    '<label>Reason</label>',
                    '<textarea placeholder="Why the designation should change"></textarea>',
                  '</div>',
                  '<p class="tower-person-safety-note">Draft only. This prepares an owner change request; it does not change the live designation.</p>',
                '</div>',

                '<div class="tower-person-control-drawer" data-tower-drawer="responsibility" hidden>',
                  '<div class="tower-person-control-field">',
                    '<label>Responsibilities</label>',
                    '<textarea placeholder="Describe this person\\'s responsibilities"></textarea>',
                  '</div>',
                  '<p class="tower-person-safety-note">Responsibility edits remain staged for owner review.</p>',
                '</div>',
              '</article>',

              '<article class="tower-person-control-card">',
                '<h3>Access</h3>',
                '<p>Review intended Tower and Observatory access before preparing a change request.</p>',

                '<p><strong>Tower</strong></p>',
                '<div class="tower-person-access-table">' + towerAccessRows() + '</div>',

                '<p style="margin-top:12px;"><strong>The Observatory</strong></p>',
                '<div class="tower-person-access-table">' + obAccessRows() + '</div>',

                '<div class="tower-person-control-button-row">',
                  '<button class="tower-person-control-button" type="button" data-tower-drawer-toggle="access">Change access draft</button>',
                '</div>',

                '<div class="tower-person-control-drawer" data-tower-drawer="access" hidden>',
                  '<div class="tower-person-control-field">',
                    '<label>Requested access change</label>',
                    '<textarea placeholder="Describe apps/rooms to add, remove, or review"></textarea>',
                  '</div>',
                  '<div class="tower-person-control-field">',
                    '<label>Reason</label>',
                    '<textarea placeholder="Why this access change is needed"></textarea>',
                  '</div>',
                  '<p class="tower-person-safety-note">Draft only. No permission is granted or revoked by this room.</p>',
                '</div>',
              '</article>',

              '<article class="tower-person-control-card">',
                '<h3>Paperwork + notes</h3>',
                '<p><strong>Paperwork status</strong> Owner review</p>',
                '<p><strong>Examples</strong> NDA, agreement, employee documents, vendor documents, trustee/advisor documents.</p>',

                '<div class="tower-person-control-field">',
                  '<label>Owner notes</label>',
                  '<textarea placeholder="Notes about this person, seat, responsibilities, or future changes"></textarea>',
                '</div>',

                '<div class="tower-person-control-button-row">',
                  '<button class="tower-person-control-button" type="button">Review paperwork</button>',
                '</div>',

                '<p class="tower-person-safety-note">Future paperwork handoffs must remain Tower-controlled and permission-checked.</p>',
              '</article>',

              '<article class="tower-person-control-card">',
                '<h3>Activity + history</h3>',

                '<div class="tower-person-activity">',
                  '<div class="tower-person-activity-item">',
                    '<strong>Person room reviewed</strong>',
                    '<span>Current owner session</span>',
                  '</div>',
                  '<div class="tower-person-activity-item">',
                    '<strong>Profile available</strong>',
                    '<span>Existing Tower person-room layer</span>',
                  '</div>',
                  '<div class="tower-person-activity-item">',
                    '<strong>Changes remain draft-only</strong>',
                    '<span>No live access mutation performed</span>',
                  '</div>',
                '</div>',

                '<p class="tower-person-safety-note">Future activity entries should become append-only Tower audit records.</p>',
              '</article>',

              '<article class="tower-person-control-card">',
                '<h3>Owner actions</h3>',
                '<p>High-impact actions stay explicit, reviewed, and fail-closed.</p>',

                '<div class="tower-person-control-button-row">',
                  '<button class="tower-person-control-button" type="button" data-tower-drawer-toggle="designation">Change designation</button>',
                  '<button class="tower-person-control-button" type="button" data-tower-drawer-toggle="access">Change access</button>',
                  '<button class="tower-person-control-button" type="button" data-tower-drawer-toggle="responsibility">Change responsibilities</button>',
                  '<button class="tower-person-control-button danger" type="button" data-tower-drawer-toggle="freeze">Suspend / freeze draft</button>',
                  '<button class="tower-person-control-button" type="button" data-tower-drawer-toggle="restore">Restore draft</button>',
                '</div>',

                '<div class="tower-person-control-drawer" data-tower-drawer="freeze" hidden>',
                  '<p class="tower-person-safety-note">Creates a freeze/suspension draft only. It does not disable a real account.</p>',
                '</div>',

                '<div class="tower-person-control-drawer" data-tower-drawer="restore" hidden>',
                  '<p class="tower-person-safety-note">Creates a restore draft only. It does not restore or change live permissions.</p>',
                '</div>',
              '</article>',

              '<article class="tower-person-control-card">',
                '<h3>Owner review chain</h3>',
                '<p><strong>1.</strong> Prepare change</p>',
                '<p><strong>2.</strong> Tower validates scope</p>',
                '<p><strong>3.</strong> Change enters owner queue</p>',
                '<p><strong>4.</strong> Owner explicitly reviews</p>',
                '<p><strong>5.</strong> Future authorized apply layer handles real changes</p>',
                '<p class="tower-person-safety-note">Nothing in TWR046–TWR050 applies real access or identity changes.</p>',
              '</article>',

            '</section>',
          ].join("");

          return room;
        }

        function wireDrawers(room) {
          var toggles = Array.prototype.slice.call(
            room.querySelectorAll("[data-tower-drawer-toggle]")
          );

          toggles.forEach(function (toggle) {
            toggle.addEventListener("click", function () {
              var key = toggle.getAttribute("data-tower-drawer-toggle");

              var drawers = Array.prototype.slice.call(
                room.querySelectorAll('[data-tower-drawer="' + key + '"]')
              );

              drawers.forEach(function (drawer) {
                if (drawer.hasAttribute("hidden")) {
                  drawer.removeAttribute("hidden");
                } else {
                  drawer.setAttribute("hidden", "");
                }
              });
            });
          });
        }

        function installPersonControlRoom() {
          var personId = routePersonId();

          if (!personId) {
            return;
          }

          if (document.querySelector("[data-tower-person-control-room='true']")) {
            return;
          }

          var title = titleFromPage(personId);

          var room = buildControlRoom(
            personId,
            title
          );

          var anchor =
            document.querySelector("main") ||
            document.body;

          anchor.appendChild(room);

          wireDrawers(room);

          document.documentElement.setAttribute(
            "data-tower-person-control-room-status",
            "ready"
          );
        }

        if (document.readyState === "loading") {
          document.addEventListener(
            "DOMContentLoaded",
            installPersonControlRoom
          );
        } else {
          installPersonControlRoom();
        }

      })();
    </script>
    """


def inject_person_control_room(html: str) -> str:
    source = str(html or "")

    if PERSON_CONTROL_ROOM_MARKER in source:
        return source

    style = _control_room_style()
    script = _control_room_script()

    if "</head>" in source:
        source = source.replace(
            "</head>",
            style + "\n</head>",
            1,
        )
    else:
        source = style + source

    if "</body>" in source:
        source = source.replace(
            "</body>",
            script + "\n</body>",
            1,
        )
    else:
        source = source + script

    return source


def is_person_room_path(path: str) -> bool:
    prefix = "/tower/owner-dashboard/person/"

    if not path.startswith(prefix):
        return False

    remainder = path[len(prefix):]

    if not remainder:
        return False

    if "/" in remainder:
        return False

    if remainder.endswith(".json"):
        return False

    return True


def register_tower_person_control_room(app):
    marker = "_tower_person_control_room_twr046_050_registered"

    if getattr(app, marker, False):
        return app

    @app.after_request
    def tower_person_control_room_injector(response):

        if not is_person_room_path(
            request.path
        ):
            return response

        if response.status_code != 200:
            return response

        if "text/html" not in response.headers.get(
            "Content-Type",
            "",
        ):
            return response

        html = response.get_data(
            as_text=True
        )

        html = inject_person_control_room(
            html
        )

        response.set_data(
            html
        )

        response.headers["Content-Length"] = str(
            len(response.get_data())
        )

        return response

    setattr(
        app,
        marker,
        True,
    )

    return app
