from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Dict, List

from flask import request


@dataclass(frozen=True)
class PreferredPeopleRoomLink:
    label: str
    person_id: str
    route: str
    designation_hint: str


PREFERRED_PEOPLE_ROOM_LINKS: tuple[PreferredPeopleRoomLink, ...] = (
    PreferredPeopleRoomLink(
        label="Future Manager Seat",
        person_id="future-manager-seat",
        route="/tower/owner-dashboard/person/future-manager-seat",
        designation_hint="Manager Candidate",
    ),
    PreferredPeopleRoomLink(
        label="Future Family / Friend Seat",
        person_id="future-family-friend-seat",
        route="/tower/owner-dashboard/person/future-family-friend-seat",
        designation_hint="Family / Friend Candidate",
    ),
    PreferredPeopleRoomLink(
        label="Future Trustee / Advisor Seat",
        person_id="future-trustee-advisor-seat",
        route="/tower/owner-dashboard/person/future-trustee-advisor-seat",
        designation_hint="Trustee / Advisor Candidate",
    ),
    PreferredPeopleRoomLink(
        label="Future Beta Tester Seat",
        person_id="future-beta-tester-seat",
        route="/tower/owner-dashboard/person/future-beta-tester-seat",
        designation_hint="Beta Tester Candidate",
    ),
)


def people_search_consolidation_summary() -> Dict[str, object]:
    return {
        "status": "tower_people_desk_search_consolidation_ready",
        "homepage_policy": "one_people_section_search_first",
        "preferred_home_surface": "existing_people_and_seats_search_section",
        "duplicate_people_rooms_dock_removed": True,
        "person_names_clickable": True,
        "open_room_chips_added": True,
        "person_room_count": len(PREFERRED_PEOPLE_ROOM_LINKS),
        "routes": [
            link.route
            for link in PREFERRED_PEOPLE_ROOM_LINKS
        ],
        "real_account_creation": False,
        "real_invites_sent": False,
        "real_access_granted": False,
        "real_permission_changes": False,
        "live_auto": "LOCKED",
        "broker_execution": False,
        "capital_action": False,
        "meaning": (
            "The People + Access Desk homepage keeps one searchable people/seats surface. "
            "Power stays behind each person name through owner-only person rooms."
        ),
    }


def preferred_people_room_links() -> List[Dict[str, str]]:
    return [
        {
            "label": link.label,
            "person_id": link.person_id,
            "route": link.route,
            "designation_hint": link.designation_hint,
        }
        for link in PREFERRED_PEOPLE_ROOM_LINKS
    ]


def remove_duplicate_people_rooms_dock(html: str) -> str:
    source = str(html or "")

    if "tower-people-room-dock" not in source:
        return source

    # Remove the entire duplicate dock section from TWR016 if present.
    section_pattern = re.compile(
        r"\s*<section\b[^>]*id=[\"']tower-people-room-dock[\"'][\s\S]*?</section>\s*",
        re.IGNORECASE,
    )

    cleaned = section_pattern.sub("\n", source)

    # Fallback: if malformed HTML somehow leaves markers, hide/remove visible residue.
    cleaned = cleaned.replace("tower-people-room-dock", "tower-people-room-dock-removed")

    return cleaned


def _room_chip_html(route: str) -> str:
    return (
        f'<a class="tower-people-open-room-chip" href="{route}" '
        f'aria-label="Open person room">Open room</a>'
    )


def _link_label_once(html: str, label: str, route: str) -> str:
    source = str(html or "")

    if route in source:
        return source

    replacement = (
        f'<a class="tower-people-name-room-link" href="{route}">{label}</a>'
        f'{_room_chip_html(route)}'
    )

    # Split HTML into tags and text nodes so we only replace visible text.
    # This safely catches cases like:
    #   <div>Future Manager Seat</div>
    # without mutating tag attributes.
    parts = re.split(r"(<[^>]+>)", source)

    changed = False
    linked_parts = []

    for part in parts:
        if changed:
            linked_parts.append(part)
            continue

        if not part:
            linked_parts.append(part)
            continue

        if part.startswith("<") and part.endswith(">"):
            linked_parts.append(part)
            continue

        if label not in part:
            linked_parts.append(part)
            continue

        linked_parts.append(part.replace(label, replacement, 1))
        changed = True

    return "".join(linked_parts)


def add_people_search_room_styles(html: str) -> str:
    source = str(html or "")

    if "tower-people-search-consolidation-style" in source:
        return source

    style = """
    <style id="tower-people-search-consolidation-style">
      .tower-people-name-room-link {
        color: #f8d978 !important;
        text-decoration: none !important;
        font-weight: 950 !important;
      }

      .tower-people-name-room-link:hover {
        text-decoration: underline !important;
      }

      .tower-people-open-room-chip {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        margin-left: 8px;
        padding: 5px 9px;
        border-radius: 999px;
        border: 1px solid rgba(248,217,120,0.38);
        background: rgba(248,217,120,0.10);
        color: #f8d978 !important;
        font-size: 11px;
        line-height: 1;
        font-weight: 950;
        letter-spacing: .02em;
        text-decoration: none !important;
        vertical-align: middle;
        white-space: nowrap;
      }

      .tower-people-search-note {
        width: min(1120px, calc(100% - 32px));
        margin: 10px auto 22px;
        padding: 12px 15px;
        border-radius: 18px;
        border: 1px solid rgba(248,217,120,0.20);
        background: rgba(248,217,120,0.075);
        color: #cab9ee;
        font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        font-size: 13px;
        line-height: 1.35;
      }

      .tower-people-search-note strong {
        color: #f8d978;
      }
    </style>
    """

    if "</head>" in source:
        return source.replace("</head>", style + "\n</head>", 1)

    return style + source


def add_people_search_note(html: str) -> str:
    source = str(html or "")

    if "tower-people-search-note" in source:
        return source

    note = """
    <div id="tower-people-search-note" class="tower-people-search-note">
      <strong>People + seats stays search-first.</strong>
      Click a person or seat name to open the control room behind it. Designation,
      app access, and freeze controls remain draft-only.
    </div>
    """

    # Place note after nav if available, otherwise before body end.
    if "tower-owner-back-nav" in source:
        nav_end = source.find("</nav>", source.find("tower-owner-back-nav"))

        if nav_end != -1:
            nav_end += len("</nav>")
            return source[:nav_end] + note + source[nav_end:]

    if "</body>" in source:
        return source.replace("</body>", note + "\n</body>", 1)

    return source + note


def enhance_preferred_people_search_section(html: str) -> str:
    source = str(html or "")

    source = remove_duplicate_people_rooms_dock(source)
    source = add_people_search_room_styles(source)

    for link in PREFERRED_PEOPLE_ROOM_LINKS:
        source = _link_label_once(
            source,
            label=link.label,
            route=link.route,
        )

    source = add_people_search_note(source)

    return source


def register_tower_people_search_consolidation(app):
    marker = "_tower_people_search_consolidation_twr021_025_registered"

    if getattr(app, marker, False):
        return app

    @app.after_request
    def tower_people_search_consolidation_injector(response):
        if request.path != "/tower/owner-dashboard":
            return response

        if response.status_code != 200:
            return response

        content_type = response.headers.get("Content-Type", "")

        if "text/html" not in content_type:
            return response

        html = response.get_data(as_text=True)
        html = enhance_preferred_people_search_section(html)

        response.set_data(html)
        response.headers["Content-Length"] = str(len(response.get_data()))

        return response

    setattr(app, marker, True)

    return app
