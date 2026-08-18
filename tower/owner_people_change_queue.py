from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, List

from flask import jsonify, redirect, request

from tower.tower_human_login_ob_launch import owner_session_active


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


@dataclass(frozen=True)
class PersonDraftPacket:
    draft_id: str
    display_name: str
    relationship: str
    requested_designation: str
    requested_scope: str
    paperwork_needed: str
    owner_notes: str
    status: str = "draft_only_owner_review_required"


@dataclass(frozen=True)
class AccessChangeQueueItem:
    queue_id: str
    person_id: str
    display_name: str
    change_type: str
    requested_change: str
    risk_note: str
    status: str = "queued_for_owner_review"


STAGED_DRAFTS = (
    PersonDraftPacket(
        draft_id="draft-future-manager-seat",
        display_name="Future Manager Seat",
        relationship="Business operations",
        requested_designation="Manager",
        requested_scope="Tower only for now",
        paperwork_needed="Role definition, privacy terms, manager boundaries",
        owner_notes="Manager tools stay draft-only until Tower grants real permission.",
    ),
    PersonDraftPacket(
        draft_id="draft-future-family-friend-seat",
        display_name="Future Family / Friend Seat",
        relationship="Personal network",
        requested_designation="Family",
        requested_scope="No app access by default",
        paperwork_needed="Sliding-scale terms, privacy terms, invite rules",
        owner_notes="Family does not equal access.",
    ),
)

STAGED_CHANGE_QUEUE = (
    AccessChangeQueueItem(
        queue_id="queue-manager-designation-review",
        person_id="future-manager-seat",
        display_name="Future Manager Seat",
        change_type="designation",
        requested_change="Review Manager designation",
        risk_note="Manager access cannot include money movement, invites, Vault, or OB Live.",
    ),
    AccessChangeQueueItem(
        queue_id="queue-beta-ob-paper-only-review",
        person_id="future-beta-tester-seat",
        display_name="Future Beta Tester Seat",
        change_type="app_access",
        requested_change="Review future Observatory Survey/Paper access only",
        risk_note="Live Auto, broker execution, capital action, and owner rooms remain locked.",
    ),
)


def people_change_queue_summary() -> Dict[str, Any]:
    return {
        "status": "tower_people_change_queue_ready",
        "homepage_policy": "calm_search_first_with_small_actions",
        "add_person_draft_available": True,
        "change_queue_available": True,
        "draft_count": len(STAGED_DRAFTS),
        "queue_count": len(STAGED_CHANGE_QUEUE),
        "real_account_creation": False,
        "real_invites_sent": False,
        "real_access_granted": False,
        "real_permission_changes": False,
        "live_auto": "LOCKED",
        "broker_execution": False,
        "capital_action": False,
        "meaning": (
            "Solice can stage people and permission changes as owner-review drafts. "
            "Nothing becomes real access from this queue."
        ),
    }


def staged_person_drafts() -> List[Dict[str, Any]]:
    return [asdict(item) for item in STAGED_DRAFTS]


def staged_change_queue() -> List[Dict[str, Any]]:
    return [asdict(item) for item in STAGED_CHANGE_QUEUE]


def build_add_person_draft(payload: Dict[str, Any]) -> Dict[str, Any]:
    display_name = str(payload.get("display_name", "") or "").strip()
    relationship = str(payload.get("relationship", "") or "").strip()
    requested_designation = str(payload.get("requested_designation", "") or "").strip()
    requested_scope = str(payload.get("requested_scope", "") or "").strip()
    paperwork_needed = str(payload.get("paperwork_needed", "") or "").strip()
    owner_notes = str(payload.get("owner_notes", "") or "").strip()

    if not display_name:
        return {
            "status": "invalid_person_draft",
            "reason": "display_name_required",
            "creates_real_account": False,
            "sends_real_invite": False,
            "grants_real_access": False,
            "changes_real_permissions": False,
        }

    if requested_designation and requested_designation not in DESIGNATION_OPTIONS:
        return {
            "status": "invalid_person_draft",
            "reason": "invalid_requested_designation",
            "allowed_designations": list(DESIGNATION_OPTIONS),
            "creates_real_account": False,
            "sends_real_invite": False,
            "grants_real_access": False,
            "changes_real_permissions": False,
        }

    safe_id = (
        display_name.lower()
        .replace("/", " ")
        .replace("\\", " ")
        .replace("&", " and ")
    )
    safe_id = "-".join(part for part in safe_id.split() if part)

    return {
        "status": "add_person_draft_created",
        "draft_id": f"draft-{safe_id or 'person'}",
        "display_name": display_name,
        "relationship": relationship or "Unspecified",
        "requested_designation": requested_designation or "Observer",
        "requested_scope": requested_scope or "No app access by default",
        "paperwork_needed": paperwork_needed or "Owner review required",
        "owner_notes": owner_notes,
        "requires_owner_review": True,
        "creates_real_account": False,
        "sends_real_invite": False,
        "grants_real_access": False,
        "changes_real_permissions": False,
        "live_auto": "LOCKED",
        "broker_execution": False,
        "capital_action": False,
    }


def build_change_queue_item(payload: Dict[str, Any]) -> Dict[str, Any]:
    person_id = str(payload.get("person_id", "") or "").strip()
    display_name = str(payload.get("display_name", "") or "").strip()
    change_type = str(payload.get("change_type", "") or "").strip()
    requested_change = str(payload.get("requested_change", "") or "").strip()
    risk_note = str(payload.get("risk_note", "") or "").strip()

    if not person_id or not display_name or not change_type or not requested_change:
        return {
            "status": "invalid_change_queue_item",
            "reason": "person_id_display_name_change_type_requested_change_required",
            "grants_real_access": False,
            "changes_real_permissions": False,
        }

    safe_id = "-".join(
        part
        for part in f"{person_id}-{change_type}".lower().replace("/", " ").split()
        if part
    )

    return {
        "status": "change_queue_item_created",
        "queue_id": f"queue-{safe_id}",
        "person_id": person_id,
        "display_name": display_name,
        "change_type": change_type,
        "requested_change": requested_change,
        "risk_note": risk_note or "Owner review required before anything changes.",
        "requires_owner_review": True,
        "creates_real_account": False,
        "sends_real_invite": False,
        "grants_real_access": False,
        "changes_real_permissions": False,
        "live_auto": "LOCKED",
        "broker_execution": False,
        "capital_action": False,
    }


def _change_queue_controls_html() -> str:
    return """
    <section id="tower-people-change-queue-controls" class="tower-people-change-queue-controls">
      <style>
        .tower-people-change-queue-controls {
          width: min(1120px, calc(100% - 32px));
          margin: 10px auto 22px;
          padding: 14px;
          border-radius: 22px;
          border: 1px solid rgba(248,217,120,0.18);
          background: rgba(255,255,255,0.055);
          color: #fff8ff;
          font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
          display: flex;
          flex-wrap: wrap;
          gap: 10px;
          align-items: center;
          justify-content: space-between;
        }

        .tower-people-change-queue-controls strong {
          color: #f8d978;
        }

        .tower-people-change-queue-actions {
          display: flex;
          flex-wrap: wrap;
          gap: 8px;
        }

        .tower-people-change-queue-actions a {
          text-decoration: none;
          border: 1px solid rgba(248,217,120,0.32);
          background: rgba(248,217,120,0.10);
          color: #f8d978;
          border-radius: 999px;
          padding: 9px 11px;
          font-size: 12px;
          font-weight: 950;
        }

        .tower-people-change-queue-controls span {
          color: #cab9ee;
          font-size: 13px;
        }
      </style>

      <div>
        <strong>Draft queue</strong>
        <span>Stage people and access changes here. Owner review required before anything becomes real.</span>
      </div>

      <div class="tower-people-change-queue-actions">
        <a href="/tower/owner-dashboard/person-drafts.json">View person drafts</a>
        <a href="/tower/owner-dashboard/change-queue.json">View change queue</a>
      </div>
    </section>
    """


def inject_change_queue_controls(html: str) -> str:
    source = str(html or "")

    if "tower-people-change-queue-controls" in source:
        return source

    controls = _change_queue_controls_html()

    if "tower-people-search-note" in source:
        marker_end = source.find("</div>", source.find("tower-people-search-note"))
        if marker_end != -1:
            marker_end += len("</div>")
            return source[:marker_end] + controls + source[marker_end:]

    if "</body>" in source:
        return source.replace("</body>", controls + "\n</body>", 1)

    return source + controls


def register_tower_people_change_queue(app):
    marker = "_tower_people_change_queue_twr026_030_registered"

    if getattr(app, marker, False):
        return app

    @app.after_request
    def tower_people_change_queue_injector(response):
        if request.path != "/tower/owner-dashboard":
            return response

        if response.status_code != 200:
            return response

        if "text/html" not in response.headers.get("Content-Type", ""):
            return response

        html = response.get_data(as_text=True)
        html = inject_change_queue_controls(html)

        response.set_data(html)
        response.headers["Content-Length"] = str(len(response.get_data()))

        return response

    @app.route("/tower/owner-dashboard/person-drafts.json")
    def tower_owner_person_drafts_json():
        if not owner_session_active():
            return redirect("/tower/login")

        return jsonify(
            {
                "summary": people_change_queue_summary(),
                "drafts": staged_person_drafts(),
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

    @app.route("/tower/owner-dashboard/change-queue.json")
    def tower_owner_change_queue_json():
        if not owner_session_active():
            return redirect("/tower/login")

        return jsonify(
            {
                "summary": people_change_queue_summary(),
                "queue": staged_change_queue(),
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

    @app.route("/tower/owner-dashboard/person-draft", methods=["POST"])
    def tower_owner_create_person_draft():
        if not owner_session_active():
            return redirect("/tower/login")

        payload = request.get_json(silent=True) or request.form or {}
        draft = build_add_person_draft(payload)
        status_code = 200 if draft["status"] == "add_person_draft_created" else 400

        return jsonify(draft), status_code

    @app.route("/tower/owner-dashboard/change-queue", methods=["POST"])
    def tower_owner_create_change_queue_item():
        if not owner_session_active():
            return redirect("/tower/login")

        payload = request.get_json(silent=True) or request.form or {}
        item = build_change_queue_item(payload)
        status_code = 200 if item["status"] == "change_queue_item_created" else 400

        return jsonify(item), status_code

    setattr(app, marker, True)

    return app
