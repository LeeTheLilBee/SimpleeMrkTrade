from __future__ import annotations

from flask import request


COMBINED_PEOPLE_ROOMS_MARKER = "tower-combine-people-seats-rooms-twr036-040"


def combined_people_rooms_summary() -> dict:
    return {
        "status": "tower_people_seats_rooms_combined_ready",
        "route": "/tower/owner-dashboard",
        "product_rule": "people_seats_is_the_roster_and_room_hub",
        "people_rooms_separate_homepage_block_removed": True,
        "people_seats_roster_preserved": True,
        "inline_room_controls_added": True,
        "full_person_room_routes_preserved": True,
        "search_preserved": True,
        "draft_queue_preserved": True,
        "back_buttons_preserved": True,
        "real_account_creation": False,
        "real_invites_sent": False,
        "real_access_granted": False,
        "real_permission_changes": False,
        "live_auto": "LOCKED",
        "broker_execution": False,
        "capital_action": False,
    }


def _combined_people_rooms_style() -> str:
    return """
    <style id="tower-combine-people-seats-rooms-style-twr036-040">
      [data-tower-hidden-separate-people-rooms="true"] {
        display: none !important;
      }

      .tower-inline-room-panel {
        margin: 12px 0 0;
        border: 1px solid rgba(248,217,120,0.22);
        border-radius: 18px;
        background:
          radial-gradient(circle at 8% 0%, rgba(248,217,120,0.10), transparent 34%),
          rgba(12, 8, 28, 0.68);
        padding: 12px;
        box-shadow: inset 0 1px 0 rgba(255,255,255,0.08);
      }

      .tower-inline-room-panel[hidden] {
        display: none !important;
      }

      .tower-inline-room-title {
        color: #f8d978;
        font-weight: 950;
        letter-spacing: .02em;
        margin: 0 0 8px;
      }

      .tower-inline-room-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
        gap: 8px;
        margin: 8px 0;
      }

      .tower-inline-room-chip {
        border: 1px solid rgba(255,255,255,0.12);
        border-radius: 14px;
        padding: 9px 10px;
        background: rgba(255,255,255,0.06);
        color: rgba(255,248,255,0.86);
        font-size: 12px;
        font-weight: 800;
      }

      .tower-inline-room-chip strong {
        display: block;
        color: #fff8ff;
        font-size: 13px;
      }

      .tower-inline-room-actions {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        margin-top: 10px;
      }

      .tower-inline-room-toggle,
      .tower-inline-room-full-link {
        border: 1px solid rgba(248,217,120,0.28);
        border-radius: 999px;
        padding: 8px 11px;
        background: rgba(248,217,120,0.10);
        color: #f8d978;
        font-weight: 950;
        text-decoration: none;
        cursor: pointer;
        font: inherit;
        font-size: 12px;
      }

      .tower-inline-room-note {
        margin: 8px 0 0;
        color: rgba(255,248,255,0.68);
        font-size: 12px;
        line-height: 1.35;
      }
    </style>
    """


def _combined_people_rooms_script() -> str:
    return """
    <script id="tower-combine-people-seats-rooms-twr036-040">
      (function () {
        function textOf(node) {
          return (node && node.innerText ? node.innerText : "").replace(/\\s+/g, " ").trim();
        }

        function lowerText(node) {
          return textOf(node).toLowerCase();
        }

        function closestCard(link) {
          return link.closest("article, li, .card, .seat, .person, [data-person-id], [data-seat-id]") || link.parentElement;
        }

        function slugFromHref(href) {
          var match = String(href || "").match(/\\/tower\\/owner-dashboard\\/person\\/([^?#]+)/);
          return match ? decodeURIComponent(match[1]) : "";
        }

        function titleFromCard(card, fallback) {
          if (!card) return fallback || "Person room";

          var preferred =
            card.querySelector(".tower-people-name-room-link") ||
            card.querySelector("h2, h3, h4, strong, a");

          var title = textOf(preferred || card).split("\\n")[0].trim();

          return title || fallback || "Person room";
        }

        function hideSeparatePeopleRoomsBlocks() {
          var nodes = Array.prototype.slice.call(document.querySelectorAll("section, article, aside, div"));

          nodes.forEach(function (node) {
            if (!node || !node.querySelector) return;

            var text = lowerText(node);
            var isPeopleRoomsBlock =
              (
                text.indexOf("people rooms") !== -1 ||
                text.indexOf("person rooms") !== -1 ||
                text.indexOf("room dock") !== -1
              ) &&
              text.indexOf("people + seats") === -1 &&
              text.indexOf("draft queue") === -1;

            if (!isPeopleRoomsBlock) return;

            if (node.closest("#tower-owner-back-nav") || node.closest("#tower-people-change-queue-controls")) return;

            node.setAttribute("data-tower-hidden-separate-people-rooms", "true");
            node.setAttribute("aria-hidden", "true");
          });
        }

        function roomPanelHtml(title, href, personId) {
          var safeTitle = title || "Person room";
          var safeHref = href || "#";
          var safePersonId = personId || "unknown-person";

          return [
            '<div class="tower-inline-room-panel" hidden data-tower-inline-room-panel="true" data-person-id="' + safePersonId + '">',
              '<p class="tower-inline-room-title">' + safeTitle + ' room</p>',
              '<div class="tower-inline-room-grid">',
                '<div class="tower-inline-room-chip"><strong>Status</strong> Planned / draft-only</div>',
                '<div class="tower-inline-room-chip"><strong>Access</strong> Owner review required</div>',
                '<div class="tower-inline-room-chip"><strong>Controls</strong> Designation, app access, freeze drafts</div>',
              '</div>',
              '<p class="tower-inline-room-note">This is the combined quick room inside People + seats. Nothing here creates accounts, sends invites, grants access, or changes real permissions.</p>',
              '<div class="tower-inline-room-actions">',
                '<a class="tower-inline-room-full-link" href="' + safeHref + '">Open full room</a>',
              '</div>',
            '</div>'
          ].join("");
        }

        function combineRoomsIntoPeopleSeats() {
          var personLinks = Array.prototype.slice.call(
            document.querySelectorAll("a[href*='/tower/owner-dashboard/person/']")
          );

          if (!personLinks.length) {
            document.documentElement.setAttribute("data-tower-combined-people-rooms-status", "no-person-links-found");
            return;
          }

          var seen = {};

          personLinks.forEach(function (link) {
            var href = link.getAttribute("href") || "";
            var personId = slugFromHref(href);

            if (!personId || seen[personId]) return;
            seen[personId] = true;

            var card = closestCard(link);
            if (!card) return;

            card.setAttribute("data-tower-combined-person-card", "true");

            var title = titleFromCard(card, link.textContent || personId);
            var existingPanel = card.querySelector("[data-tower-inline-room-panel='true']");

            var toggle = document.createElement("button");
            toggle.type = "button";
            toggle.className = "tower-inline-room-toggle";
            toggle.setAttribute("data-tower-inline-room-toggle", "true");
            toggle.setAttribute("aria-expanded", "false");
            toggle.textContent = "Room details";

            if (!existingPanel) {
              card.insertAdjacentHTML("beforeend", roomPanelHtml(title, href, personId));
            }

            var panel = card.querySelector("[data-tower-inline-room-panel='true']");

            if (!card.querySelector("[data-tower-inline-room-toggle='true']")) {
              var actionWrap = document.createElement("div");
              actionWrap.className = "tower-inline-room-actions";
              actionWrap.setAttribute("data-tower-inline-room-actions", "true");
              actionWrap.appendChild(toggle);

              card.insertBefore(actionWrap, panel);
            }

            var activeToggle = card.querySelector("[data-tower-inline-room-toggle='true']");

            if (activeToggle && panel) {
              activeToggle.addEventListener("click", function () {
                var isHidden = panel.hasAttribute("hidden");

                if (isHidden) {
                  panel.removeAttribute("hidden");
                  activeToggle.setAttribute("aria-expanded", "true");
                  activeToggle.textContent = "Hide room details";
                } else {
                  panel.setAttribute("hidden", "");
                  activeToggle.setAttribute("aria-expanded", "false");
                  activeToggle.textContent = "Room details";
                }
              });
            }
          });

          hideSeparatePeopleRoomsBlocks();

          document.documentElement.setAttribute(
            "data-tower-combined-people-rooms-status",
            "people-seats-roster-is-room-hub"
          );
        }

        if (document.readyState === "loading") {
          document.addEventListener("DOMContentLoaded", combineRoomsIntoPeopleSeats);
        } else {
          combineRoomsIntoPeopleSeats();
        }
      })();
    </script>
    """


def inject_combined_people_rooms(html: str) -> str:
    source = str(html or "")

    if COMBINED_PEOPLE_ROOMS_MARKER in source:
        return source

    style = _combined_people_rooms_style()
    script = _combined_people_rooms_script()

    if "</head>" in source:
        source = source.replace("</head>", style + "\n</head>", 1)
    else:
        source = style + source

    if "</body>" in source:
        source = source.replace("</body>", script + "\n</body>", 1)
    else:
        source = source + script

    return source


def register_tower_people_combined_rooms(app):
    marker = "_tower_people_combined_rooms_twr036_040_registered"

    if getattr(app, marker, False):
        return app

    @app.after_request
    def tower_people_combined_rooms_injector(response):
        if request.path != "/tower/owner-dashboard":
            return response

        if response.status_code != 200:
            return response

        if "text/html" not in response.headers.get("Content-Type", ""):
            return response

        html = response.get_data(as_text=True)
        html = inject_combined_people_rooms(html)

        response.set_data(html)
        response.headers["Content-Length"] = str(len(response.get_data()))

        return response

    setattr(app, marker, True)

    return app
