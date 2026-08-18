from __future__ import annotations

from flask import request


BOTTOM_SECTION_PREFERENCE_MARKER = "tower-keep-bottom-people-seats-search-twr031-035"


def bottom_section_preference_summary() -> dict:
    return {
        "status": "tower_bottom_people_seats_search_ready",
        "route": "/tower/owner-dashboard",
        "visual_rule": "remove_top_people_seats_keep_bottom_people_seats",
        "top_people_seats_removed": True,
        "bottom_people_seats_preserved": True,
        "bottom_people_seats_search_required": True,
        "person_room_links_preserved": True,
        "open_room_chips_preserved": True,
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


def _bottom_section_style() -> str:
    return """
    <style id="tower-bottom-people-seats-search-style-twr031-035">
      [data-tower-removed-top-people-seats="true"] {
        display: none !important;
      }

      .tower-bottom-people-search-wrap {
        width: 100%;
        margin: 0 0 14px 0;
      }

      .tower-bottom-people-search-label {
        display: block;
        color: #f8d978;
        text-transform: uppercase;
        letter-spacing: .12em;
        font-size: 11px;
        font-weight: 950;
        margin-bottom: 7px;
      }

      .tower-bottom-people-search-input {
        width: 100%;
        box-sizing: border-box;
        border: 1px solid rgba(248,217,120,0.30);
        background: rgba(255,255,255,0.075);
        color: #fff8ff;
        border-radius: 999px;
        padding: 12px 15px;
        outline: none;
        font-weight: 800;
      }

      .tower-bottom-people-search-input::placeholder {
        color: rgba(255,248,255,0.55);
      }

      [data-tower-people-filter-hidden="true"] {
        display: none !important;
      }
    </style>
    """


def _bottom_section_script() -> str:
    return """
    <script id="tower-keep-bottom-people-seats-search-twr031-035">
      (function () {
        function textOf(node) {
          return (node && node.innerText ? node.innerText : "").replace(/\\s+/g, " ").trim().toLowerCase();
        }

        function hasPeopleSeatsTitle(node) {
          var text = textOf(node);
          return (
            text.indexOf("people + seats") !== -1 ||
            text.indexOf("people and seats") !== -1 ||
            text.indexOf("people seats") !== -1
          );
        }

        function isProtectedControl(node) {
          if (!node || !node.closest) return false;

          return Boolean(
            node.closest("#tower-owner-back-nav") ||
            node.closest("#tower-people-change-queue-controls") ||
            node.closest("#tower-people-search-note") ||
            node.closest("[data-tower-person-room='true']")
          );
        }

        function candidateScore(node) {
          var text = textOf(node);
          var score = 0;

          if (text.indexOf("people + seats") !== -1) score += 6;
          if (text.indexOf("people and seats") !== -1) score += 6;
          if (text.indexOf("people seats") !== -1) score += 5;
          if (text.indexOf("search") !== -1) score += 2;
          if (text.indexOf("future manager seat") !== -1) score += 2;
          if (text.indexOf("future family") !== -1) score += 2;
          if (text.indexOf("future trustee") !== -1) score += 2;
          if (text.indexOf("future beta") !== -1) score += 2;
          if (text.indexOf("draft queue") !== -1) score -= 6;
          if (text.indexOf("back to access home") !== -1) score -= 6;
          if (text.length > 2500) score -= 2;

          return score;
        }

        function visibleCandidateSections() {
          var nodes = Array.prototype.slice.call(
            document.querySelectorAll("section, article, aside, div")
          );

          var candidates = nodes.filter(function (node) {
            if (isProtectedControl(node)) return false;
            if (!hasPeopleSeatsTitle(node)) return false;
            if (candidateScore(node) < 6) return false;

            var rect = node.getBoundingClientRect();
            if (rect.width <= 0 || rect.height <= 0) return false;

            return true;
          });

          return candidates.filter(function (node) {
            return !candidates.some(function (other) {
              return other !== node && other.contains(node);
            });
          });
        }

        function ensureSearchBar(keptSection) {
          if (!keptSection) return;

          keptSection.setAttribute("data-tower-keep-bottom-people-seats", "true");

          var existingSearch = keptSection.querySelector(
            "input[type='search'], input[placeholder*='Search'], input[placeholder*='search'], [data-tower-people-search='true']"
          );

          if (existingSearch) {
            existingSearch.setAttribute("data-tower-people-search", "true");
            document.documentElement.setAttribute("data-tower-bottom-people-search-status", "existing-search-kept");
            return;
          }

          var wrap = document.createElement("div");
          wrap.className = "tower-bottom-people-search-wrap";
          wrap.setAttribute("data-tower-people-search-wrap", "true");

          var label = document.createElement("label");
          label.className = "tower-bottom-people-search-label";
          label.textContent = "Search people + seats";

          var input = document.createElement("input");
          input.className = "tower-bottom-people-search-input";
          input.type = "search";
          input.placeholder = "Search people, seats, roles, access notes...";
          input.setAttribute("aria-label", "Search people and seats");
          input.setAttribute("data-tower-people-search", "true");

          wrap.appendChild(label);
          wrap.appendChild(input);
          keptSection.insertBefore(wrap, keptSection.firstChild);

          document.documentElement.setAttribute("data-tower-bottom-people-search-status", "search-added");
        }

        function wireSearch(keptSection) {
          if (!keptSection) return;

          var input = keptSection.querySelector("[data-tower-people-search='true']");

          if (!input) return;

          input.addEventListener("input", function () {
            var query = String(input.value || "").trim().toLowerCase();
            var items = Array.prototype.slice.call(
              keptSection.querySelectorAll("article, li, .card, .seat, .person, [data-person-id], [data-seat-id]")
            );

            if (!items.length) {
              items = Array.prototype.slice.call(keptSection.children).filter(function (child) {
                return !child.matches("[data-tower-people-search-wrap='true']");
              });
            }

            items.forEach(function (item) {
              var itemText = textOf(item);
              var shouldHide = Boolean(query) && itemText.indexOf(query) === -1;
              item.setAttribute("data-tower-people-filter-hidden", shouldHide ? "true" : "false");
            });
          });
        }

        function applyBottomPreference() {
          var candidates = visibleCandidateSections();

          if (!candidates.length) {
            document.documentElement.setAttribute("data-tower-people-bottom-preference-status", "no-people-seats-candidate-found");
            return;
          }

          candidates.sort(function (a, b) {
            return a.getBoundingClientRect().top - b.getBoundingClientRect().top;
          });

          var keptSection = candidates[candidates.length - 1];

          candidates.slice(0, -1).forEach(function (node) {
            node.setAttribute("data-tower-removed-top-people-seats", "true");
            node.style.display = "none";
            node.setAttribute("aria-hidden", "true");
          });

          keptSection.setAttribute("data-tower-keep-bottom-people-seats", "true");
          ensureSearchBar(keptSection);
          wireSearch(keptSection);

          document.documentElement.setAttribute(
            "data-tower-people-bottom-preference-status",
            candidates.length > 1 ? "top-hidden-bottom-kept-search-ready" : "single-bottom-search-ready"
          );
        }

        if (document.readyState === "loading") {
          document.addEventListener("DOMContentLoaded", applyBottomPreference);
        } else {
          applyBottomPreference();
        }
      })();
    </script>
    """


def inject_bottom_people_seats_preference(html: str) -> str:
    source = str(html or "")

    if BOTTOM_SECTION_PREFERENCE_MARKER in source:
        return source

    style = _bottom_section_style()
    script = _bottom_section_script()

    if "</head>" in source:
        source = source.replace("</head>", style + "\n</head>", 1)
    else:
        source = style + source

    if "</body>" in source:
        source = source.replace("</body>", script + "\n</body>", 1)
    else:
        source = source + script

    return source


def register_tower_bottom_people_seats_preference(app):
    marker = "_tower_bottom_people_seats_preference_twr031_035_registered"

    if getattr(app, marker, False):
        return app

    @app.after_request
    def tower_bottom_people_seats_preference_injector(response):
        if request.path != "/tower/owner-dashboard":
            return response

        if response.status_code != 200:
            return response

        if "text/html" not in response.headers.get("Content-Type", ""):
            return response

        html = response.get_data(as_text=True)
        html = inject_bottom_people_seats_preference(html)

        response.set_data(html)
        response.headers["Content-Length"] = str(len(response.get_data()))

        return response

    setattr(app, marker, True)

    return app
