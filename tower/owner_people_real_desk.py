from __future__ import annotations

from flask import request


REAL_DESK_MARKER = "tower-people-seats-real-desk-twr041-045"


PERSON_CATEGORIES = [
    "All",
    "Family/Friends",
    "Managers",
    "Employees",
    "Vendors",
    "Advisors",
    "Trustees/Admin",
    "Beta testers",
    "Future seats",
]


def people_real_desk_summary() -> dict:
    return {
        "status": "tower_people_seats_real_desk_ready",
        "route": "/tower/owner-dashboard",
        "product_rule": "people_seats_is_the_single_people_desk",
        "better_cards_added": True,
        "add_person_workspace_added": True,
        "category_filters_added": True,
        "inline_room_details_polished": True,
        "draft_queue_polished": True,
        "person_categories": PERSON_CATEGORIES,
        "real_account_creation": False,
        "real_invites_sent": False,
        "real_access_granted": False,
        "real_permission_changes": False,
        "live_auto": "LOCKED",
        "broker_execution": False,
        "capital_action": False,
    }


def _real_desk_style() -> str:
    return """
    <style id="tower-people-seats-real-desk-style-twr041-045">
      .tower-real-people-toolbar {
        margin: 14px 0;
        padding: 14px;
        border-radius: 22px;
        border: 1px solid rgba(248,217,120,0.22);
        background:
          radial-gradient(circle at 0% 0%, rgba(248,217,120,0.12), transparent 38%),
          rgba(255,255,255,0.055);
      }

      .tower-real-people-toolbar-top {
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
        align-items: center;
        justify-content: space-between;
      }

      .tower-real-people-title {
        margin: 0;
        color: #fff8ff;
        font-weight: 950;
        letter-spacing: -.02em;
      }

      .tower-real-people-subtitle {
        margin: 4px 0 0;
        color: rgba(255,248,255,0.68);
        font-size: 13px;
        line-height: 1.35;
      }

      .tower-add-person-button,
      .tower-real-filter-chip,
      .tower-real-action-chip {
        border: 1px solid rgba(248,217,120,0.30);
        border-radius: 999px;
        background: rgba(248,217,120,0.10);
        color: #f8d978;
        font: inherit;
        font-size: 12px;
        font-weight: 950;
        padding: 9px 12px;
        cursor: pointer;
        text-decoration: none;
      }

      .tower-real-filter-chip[aria-pressed="true"] {
        background: rgba(248,217,120,0.24);
        color: #fff8ff;
        box-shadow: 0 0 0 1px rgba(248,217,120,0.26) inset;
      }

      .tower-real-filter-row {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        margin-top: 12px;
      }

      .tower-add-person-workspace {
        margin-top: 12px;
        border: 1px solid rgba(255,255,255,0.12);
        border-radius: 20px;
        background: rgba(8,8,22,0.62);
        padding: 14px;
      }

      .tower-add-person-workspace[hidden] {
        display: none !important;
      }

      .tower-add-person-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
        gap: 10px;
        margin-top: 10px;
      }

      .tower-add-person-field label {
        display: block;
        color: #f8d978;
        font-size: 11px;
        font-weight: 950;
        letter-spacing: .10em;
        text-transform: uppercase;
        margin-bottom: 6px;
      }

      .tower-add-person-field input,
      .tower-add-person-field select,
      .tower-add-person-field textarea {
        width: 100%;
        box-sizing: border-box;
        border: 1px solid rgba(255,255,255,0.12);
        border-radius: 14px;
        background: rgba(255,255,255,0.07);
        color: #fff8ff;
        padding: 10px;
        font: inherit;
        font-size: 13px;
      }

      .tower-add-person-field textarea {
        min-height: 78px;
        resize: vertical;
      }

      .tower-add-person-safety {
        margin: 10px 0 0;
        color: rgba(255,248,255,0.70);
        font-size: 12px;
        line-height: 1.35;
      }

      [data-tower-real-person-card="true"] {
        border-color: rgba(248,217,120,0.22) !important;
        background:
          radial-gradient(circle at 0% 0%, rgba(248,217,120,0.10), transparent 34%),
          rgba(255,255,255,0.055) !important;
        box-shadow: 0 16px 44px rgba(0,0,0,0.20);
      }

      .tower-real-person-chip-row {
        display: flex;
        flex-wrap: wrap;
        gap: 7px;
        margin: 10px 0;
      }

      .tower-real-person-chip {
        display: inline-flex;
        align-items: center;
        gap: 5px;
        border: 1px solid rgba(255,255,255,0.12);
        border-radius: 999px;
        background: rgba(255,255,255,0.07);
        color: rgba(255,248,255,0.82);
        padding: 7px 9px;
        font-size: 11px;
        font-weight: 900;
        white-space: nowrap;
      }

      .tower-real-person-chip strong {
        color: #f8d978;
      }

      .tower-real-room-summary {
        margin-top: 8px;
        border-radius: 16px;
        background: rgba(255,255,255,0.045);
        border: 1px solid rgba(255,255,255,0.10);
        padding: 10px;
        color: rgba(255,248,255,0.78);
        font-size: 12px;
        line-height: 1.35;
      }

      .tower-real-queue-pill {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        border-radius: 999px;
        background: rgba(248,217,120,0.10);
        border: 1px solid rgba(248,217,120,0.26);
        color: #f8d978;
        padding: 7px 9px;
        font-size: 11px;
        font-weight: 950;
        margin: 4px 4px 0 0;
      }

      [data-tower-real-filter-hidden="true"] {
        display: none !important;
      }
    </style>
    """


def _real_desk_script() -> str:
    categories_json = str(PERSON_CATEGORIES).replace("'", '"')

    return f"""
    <script id="tower-people-seats-real-desk-twr041-045">
      (function () {{
        var CATEGORIES = {categories_json};

        function textOf(node) {{
          return (node && node.innerText ? node.innerText : "").replace(/\\s+/g, " ").trim();
        }}

        function lowerText(node) {{
          return textOf(node).toLowerCase();
        }}

        function getPeopleHub() {{
          var kept = document.querySelector("[data-tower-keep-bottom-people-seats='true']");
          if (kept) return kept;

          var sections = Array.prototype.slice.call(document.querySelectorAll("section, article, aside, div"));

          return sections.filter(function (node) {{
            var text = lowerText(node);
            return text.indexOf("people + seats") !== -1;
          }}).pop() || null;
        }}

        function inferCategory(card) {{
          var text = lowerText(card);

          if (text.indexOf("manager") !== -1) return "Managers";
          if (text.indexOf("employee") !== -1) return "Employees";
          if (text.indexOf("vendor") !== -1) return "Vendors";
          if (text.indexOf("advisor") !== -1) return "Advisors";
          if (text.indexOf("trustee") !== -1 || text.indexOf("trust admin") !== -1) return "Trustees/Admin";
          if (text.indexOf("beta") !== -1) return "Beta testers";
          if (text.indexOf("family") !== -1 || text.indexOf("friend") !== -1) return "Family/Friends";
          if (text.indexOf("future") !== -1 || text.indexOf("seat") !== -1) return "Future seats";

          return "Future seats";
        }}

        function getCards(hub) {{
          if (!hub) return [];

          var links = Array.prototype.slice.call(
            hub.querySelectorAll("a[href*='/tower/owner-dashboard/person/']")
          );

          var cards = [];

          links.forEach(function (link) {{
            var card =
              link.closest("article, li, .card, .seat, .person, [data-person-id], [data-seat-id]") ||
              link.parentElement;

            if (card && cards.indexOf(card) === -1) {{
              cards.push(card);
            }}
          }});

          return cards;
        }}

        function ensureToolbar(hub) {{
          if (!hub || hub.querySelector("[data-tower-real-people-toolbar='true']")) return;

          var toolbar = document.createElement("div");
          toolbar.className = "tower-real-people-toolbar";
          toolbar.setAttribute("data-tower-real-people-toolbar", "true");

          toolbar.innerHTML = [
            '<div class="tower-real-people-toolbar-top">',
              '<div>',
                '<p class="tower-real-people-title">People + seats</p>',
                '<p class="tower-real-people-subtitle">Roster, future seats, quick room details, drafts, and owner-review work in one place.</p>',
              '</div>',
              '<button type="button" class="tower-add-person-button" data-tower-add-person-toggle="true" aria-expanded="false">Add person draft</button>',
            '</div>',
            '<div class="tower-real-filter-row" data-tower-real-filter-row="true"></div>',
            '<div class="tower-add-person-workspace" data-tower-add-person-workspace="true" hidden>',
              '<strong>Add Person Draft</strong>',
              '<div class="tower-add-person-grid">',
                '<div class="tower-add-person-field"><label>Name</label><input data-tower-add-person-name="true" placeholder="Future person or seat name"></div>',
                '<div class="tower-add-person-field"><label>Category</label><select data-tower-add-person-category="true"><option>Family/Friends</option><option>Managers</option><option>Employees</option><option>Vendors</option><option>Advisors</option><option>Trustees/Admin</option><option>Beta testers</option><option>Future seats</option></select></div>',
                '<div class="tower-add-person-field"><label>Seat purpose</label><input data-tower-add-person-purpose="true" placeholder="What this person/seat is for"></div>',
                '<div class="tower-add-person-field"><label>Paperwork needed</label><input data-tower-add-person-paperwork="true" placeholder="NDA, agreement, proof, review..."></div>',
              '</div>',
              '<div class="tower-add-person-field" style="margin-top:10px;"><label>Owner notes</label><textarea data-tower-add-person-notes="true" placeholder="Notes before this becomes a real person/access request"></textarea></div>',
              '<p class="tower-add-person-safety">Draft only. This does not create an account, send an invite, grant access, or change permissions.</p>',
            '</div>'
          ].join("");

          var firstChild = hub.firstChild;
          hub.insertBefore(toolbar, firstChild);

          var row = toolbar.querySelector("[data-tower-real-filter-row='true']");

          CATEGORIES.forEach(function (category, index) {{
            var button = document.createElement("button");
            button.type = "button";
            button.className = "tower-real-filter-chip";
            button.textContent = category;
            button.setAttribute("data-tower-real-filter", category);
            button.setAttribute("aria-pressed", index === 0 ? "true" : "false");
            row.appendChild(button);
          }});

          var addToggle = toolbar.querySelector("[data-tower-add-person-toggle='true']");
          var workspace = toolbar.querySelector("[data-tower-add-person-workspace='true']");

          addToggle.addEventListener("click", function () {{
            var isHidden = workspace.hasAttribute("hidden");

            if (isHidden) {{
              workspace.removeAttribute("hidden");
              addToggle.setAttribute("aria-expanded", "true");
              addToggle.textContent = "Hide add person";
            }} else {{
              workspace.setAttribute("hidden", "");
              addToggle.setAttribute("aria-expanded", "false");
              addToggle.textContent = "Add person draft";
            }}
          }});
        }}

        function polishCards(hub) {{
          var cards = getCards(hub);

          cards.forEach(function (card) {{
            if (card.getAttribute("data-tower-real-person-card") === "true") return;

            var category = inferCategory(card);
            card.setAttribute("data-tower-real-person-card", "true");
            card.setAttribute("data-tower-real-category", category);

            var chipRow = document.createElement("div");
            chipRow.className = "tower-real-person-chip-row";
            chipRow.setAttribute("data-tower-real-person-chip-row", "true");

            chipRow.innerHTML = [
              '<span class="tower-real-person-chip"><strong>Type</strong> ' + category + '</span>',
              '<span class="tower-real-person-chip"><strong>Access</strong> Draft-only</span>',
              '<span class="tower-real-person-chip"><strong>Paperwork</strong> Owner review</span>',
              '<span class="tower-real-person-chip"><strong>Status</strong> Planned</span>'
            ].join("");

            var summary = document.createElement("div");
            summary.className = "tower-real-room-summary";
            summary.setAttribute("data-tower-real-room-summary", "true");
            summary.textContent = "Quick room: review role, intended access, paperwork, notes, and queue items here before opening the full person room.";

            var queuePill = document.createElement("span");
            queuePill.className = "tower-real-queue-pill";
            queuePill.setAttribute("data-tower-real-queue-pill", "true");
            queuePill.textContent = "Owner review required";

            card.insertBefore(chipRow, card.firstChild);
            card.appendChild(summary);
            card.appendChild(queuePill);
          }});

          document.documentElement.setAttribute("data-tower-real-people-card-count", String(cards.length));
        }}

        function wireFilters(hub) {{
          var buttons = Array.prototype.slice.call(hub.querySelectorAll("[data-tower-real-filter]"));
          var cards = getCards(hub);

          buttons.forEach(function (button) {{
            button.addEventListener("click", function () {{
              var category = button.getAttribute("data-tower-real-filter") || "All";

              buttons.forEach(function (other) {{
                other.setAttribute("aria-pressed", other === button ? "true" : "false");
              }});

              cards.forEach(function (card) {{
                var cardCategory = card.getAttribute("data-tower-real-category") || inferCategory(card);
                var hidden = category !== "All" && cardCategory !== category;
                card.setAttribute("data-tower-real-filter-hidden", hidden ? "true" : "false");
              }});

              document.documentElement.setAttribute("data-tower-real-people-active-filter", category);
            }});
          }});
        }}

        function polishDraftQueue() {{
          var queue = document.querySelector("#tower-people-change-queue-controls");

          if (!queue) return;

          if (queue.querySelector("[data-tower-real-queue-polish='true']")) return;

          var note = document.createElement("p");
          note.className = "tower-add-person-safety";
          note.setAttribute("data-tower-real-queue-polish", "true");
          note.textContent = "Queue polish: drafts stay staged for owner review. Nothing here changes live permissions.";

          queue.appendChild(note);
        }}

        function applyRealPeopleDesk() {{
          var hub = getPeopleHub();

          if (!hub) {{
            document.documentElement.setAttribute("data-tower-real-people-desk-status", "no-people-hub-found");
            return;
          }}

          hub.setAttribute("data-tower-real-people-desk", "true");

          ensureToolbar(hub);
          polishCards(hub);
          wireFilters(hub);
          polishDraftQueue();

          document.documentElement.setAttribute("data-tower-real-people-desk-status", "people-seats-real-desk-ready");
        }}

        if (document.readyState === "loading") {{
          document.addEventListener("DOMContentLoaded", applyRealPeopleDesk);
        }} else {{
          applyRealPeopleDesk();
        }}
      }})();
    </script>
    """


def inject_people_real_desk(html: str) -> str:
    source = str(html or "")

    if REAL_DESK_MARKER in source:
        return source

    style = _real_desk_style()
    script = _real_desk_script()

    if "</head>" in source:
        source = source.replace("</head>", style + "\n</head>", 1)
    else:
        source = style + source

    if "</body>" in source:
        source = source.replace("</body>", script + "\n</body>", 1)
    else:
        source = source + script

    return source


def register_tower_people_real_desk(app):
    marker = "_tower_people_real_desk_twr041_045_registered"

    if getattr(app, marker, False):
        return app

    @app.after_request
    def tower_people_real_desk_injector(response):
        if request.path != "/tower/owner-dashboard":
            return response

        if response.status_code != 200:
            return response

        if "text/html" not in response.headers.get("Content-Type", ""):
            return response

        html = response.get_data(as_text=True)
        html = inject_people_real_desk(html)

        response.set_data(html)
        response.headers["Content-Length"] = str(len(response.get_data()))

        return response

    setattr(app, marker, True)

    return app
