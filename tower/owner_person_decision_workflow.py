from __future__ import annotations

import uuid
from copy import deepcopy
from typing import Any, Dict, List

from flask import jsonify, redirect, request

from tower.owner_people_profile_rooms import people_profile_by_id

from tower.owner_person_event_ledger import (
    append_person_event,
    build_person_event,
    build_vault_ready_person_packet,
    read_event_by_id,
    read_person_events,
)

from tower.tower_human_login_ob_launch import owner_session_active


PERSON_OWNER_DECISION_MARKER = (
    "tower-person-owner-decision-twr061-065"
)


OWNER_DECISIONS = (
    "APPROVED",
    "REJECTED",
    "HOLD",
    "RETURN_FOR_CHANGES",
)


def person_owner_decision_summary() -> Dict[str, Any]:
    return {
        "status": "tower_person_owner_decision_ready",
        "product_rule": (
            "owner_decision_is_append_only_and_does_not_mutate_source_event"
        ),
        "owner_decisions": list(OWNER_DECISIONS),
        "approved_effective_vault_status": "READY_FOR_VAULT",
        "nonapproved_effective_vault_status": "NOT_READY_FOR_VAULT",
        "decision_receipts": True,
        "source_event_mutation": False,
        "vault_delivery_enabled": False,
        "real_permission_changes": False,
        "live_auto": "LOCKED",
        "broker_execution": False,
        "capital_action": False,
    }


def _decision_events(person_id: str) -> List[Dict[str, Any]]:
    return [
        event
        for event in read_person_events(person_id)
        if event.get("event_type") == "PERSON_OWNER_DECISION"
    ]


def latest_decision_for_event(
    person_id: str,
    source_event_id: str,
) -> Dict[str, Any] | None:

    matches = []

    for event in _decision_events(person_id):
        before = event.get("before_state") or {}

        if before.get("source_event_id") == source_event_id:
            matches.append(event)

    return matches[-1] if matches else None


def effective_vault_status(
    person_id: str,
    source_event_id: str,
) -> str:

    decision_event = latest_decision_for_event(
        person_id,
        source_event_id,
    )

    if not decision_event:
        return "NOT_READY_FOR_VAULT"

    resulting = decision_event.get("resulting_state") or {}

    return (
        resulting.get("effective_vault_status")
        or "NOT_READY_FOR_VAULT"
    )


def pending_owner_decisions(
    person_id: str,
) -> List[Dict[str, Any]]:

    events = read_person_events(person_id)

    result = []

    for event in events:

        if event.get("event_type") != "PERSON_CONTROL_DRAFT":
            continue

        decision = latest_decision_for_event(
            person_id,
            event["event_id"],
        )

        if decision:
            continue

        projected = deepcopy(event)

        projected["effective_vault_status"] = (
            "NOT_READY_FOR_VAULT"
        )

        result.append(projected)

    return result


def build_owner_decision(
    person_id: str,
    source_event_id: str,
    decision: str,
    *,
    reason: str = "",
) -> Dict[str, Any]:

    profile = people_profile_by_id(person_id)

    if not profile:
        return {
            "status": "not_found",
            "person_id": person_id,
        }

    source_event = read_event_by_id(source_event_id)

    if (
        not source_event
        or source_event.get("person_id") != profile["person_id"]
    ):
        return {
            "status": "source_event_not_found",
            "person_id": profile["person_id"],
            "source_event_id": source_event_id,
        }

    normalized = str(decision or "").strip().upper()

    if normalized not in OWNER_DECISIONS:
        return {
            "status": "invalid_owner_decision",
            "allowed_decisions": list(OWNER_DECISIONS),
        }

    existing = latest_decision_for_event(
        profile["person_id"],
        source_event_id,
    )

    if existing:
        return {
            "status": "owner_decision_already_exists",
            "decision_event": existing,
            "source_event_mutated": False,
        }

    decision_id = "per-dec-" + uuid.uuid4().hex
    receipt_id = "per-dec-receipt-" + uuid.uuid4().hex

    effective_status = (
        "READY_FOR_VAULT"
        if normalized == "APPROVED"
        else "NOT_READY_FOR_VAULT"
    )

    built = build_person_event(
        profile["person_id"],
        event_type="PERSON_OWNER_DECISION",
        action="owner_decision",
        before_state={
            "source_event_id": source_event_id,
            "source_event_type": source_event.get("event_type"),
            "source_action": source_event.get("action"),
            "source_owner_review_status": source_event.get(
                "owner_review_status"
            ),
        },
        requested_state={
            "decision": normalized,
            "decision_reason": str(reason or "").strip(),
        },
        resulting_state={
            "decision_id": decision_id,
            "decision_receipt_id": receipt_id,
            "owner_decision": normalized,
            "effective_vault_status": effective_status,
        },
        reason=str(reason or "").strip(),
        owner_review_status=normalized,
        tower_validation={
            "source_event_exists": True,
            "source_event_integrity_hash": source_event.get(
                "integrity_hash"
            ),
            "decision_allowed": True,
        },
        related_receipt_ids=[
            receipt_id,
            source_event_id,
        ],
        source="TOWER_OWNER_DECISION_WORKFLOW",
    )

    if built.get("status") != "person_event_built":
        return built

    append_result = append_person_event(
        built["event"]
    )

    if not append_result.get("appended"):
        return {
            "status": "owner_decision_append_failed",
            "append_result": append_result,
        }

    vault_packet = build_vault_ready_person_packet(
        source_event,
        owner_decision=normalized,
        decision_reason=str(reason or "").strip(),
        decision_receipt_id=receipt_id,
    )

    return {
        "status": "person_owner_decision_recorded",
        "decision": normalized,
        "decision_id": decision_id,
        "decision_receipt": {
            "receipt_id": receipt_id,
            "receipt_type": "tower_person_owner_decision_receipt",
            "person_id": profile["person_id"],
            "source_event_id": source_event_id,
            "decision": normalized,
            "effective_vault_status": effective_status,
            "source_event_mutated": False,
            "vault_delivery_performed": False,
        },
        "decision_event": built["event"],
        "vault_packet_preview": vault_packet,
        "safety": {
            "real_permission_changes": False,
            "vault_delivery_enabled": False,
            "live_auto": "LOCKED",
            "broker_execution": False,
            "capital_action": False,
        },
    }


def owner_decision_payload(
    person_id: str,
) -> Dict[str, Any]:

    profile = people_profile_by_id(person_id)

    if not profile:
        return {
            "status": "not_found",
            "person_id": person_id,
        }

    pending = pending_owner_decisions(person_id)

    decisions = _decision_events(person_id)

    return {
        "status": "tower_person_owner_decision_payload_ready",
        "profile": profile,
        "pending": pending,
        "pending_count": len(pending),
        "decision_events": decisions,
        "decision_count": len(decisions),
        "allowed_decisions": list(OWNER_DECISIONS),
        "vault_delivery_enabled": False,
    }


def _decision_ui_script() -> str:
    return """
<script id="tower-person-owner-decision-twr061-065">
(function () {

  function personId() {
    var match = location.pathname.match(
      /^\\/tower\\/owner-dashboard\\/person\\/([^/]+)$/
    );
    return match ? decodeURIComponent(match[1]) : "";
  }

  function ensurePanel(room) {
    var existing = room.querySelector(
      "[data-tower-owner-decision-panel='true']"
    );

    if (existing) return existing;

    var panel = document.createElement("section");
    panel.className = "tower-person-control-card";
    panel.setAttribute(
      "data-tower-owner-decision-panel",
      "true"
    );

    panel.innerHTML = [
      "<h3>Owner Decision Queue</h3>",
      "<p>Loading pending person changes…</p>"
    ].join("");

    room.appendChild(panel);

    return panel;
  }

  function escapeHtml(value) {
    return String(value == null ? "" : value)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  async function loadQueue(pid, panel) {

    var response = await fetch(
      "/tower/owner-dashboard/person/"
      + encodeURIComponent(pid)
      + "/decisions.json"
    );

    var data = await response.json();

    if (!response.ok) {
      panel.innerHTML =
        "<h3>Owner Decision Queue</h3><p>Queue unavailable.</p>";
      return;
    }

    var pending = data.pending || [];

    var html = [
      "<h3>Owner Decision Queue</h3>",
      "<p><strong>",
      pending.length,
      "</strong> pending change(s).</p>"
    ];

    if (!pending.length) {
      html.push("<p>Nothing currently needs an owner decision.</p>");
    }

    pending.forEach(function (event) {

      html.push([
        "<article style='margin-top:10px;padding:12px;border:1px solid rgba(255,255,255,.1);border-radius:14px'>",

        "<strong style='color:#f8d978'>",
        escapeHtml(event.action),
        "</strong>",

        "<p>Event: ",
        escapeHtml(event.event_id),
        "</p>",

        "<pre style='white-space:pre-wrap;font-size:11px'>",
        escapeHtml(JSON.stringify(event.requested_state || {}, null, 2)),
        "</pre>",

        "<select data-decision-select='",
        escapeHtml(event.event_id),
        "'>",
          "<option value='APPROVED'>Approve</option>",
          "<option value='REJECTED'>Reject</option>",
          "<option value='HOLD'>Hold</option>",
          "<option value='RETURN_FOR_CHANGES'>Return for changes</option>",
        "</select>",

        "<textarea data-decision-reason='",
        escapeHtml(event.event_id),
        "' placeholder='Decision reason' style='width:100%;margin-top:7px'></textarea>",

        "<button type='button' class='tower-person-control-button' ",
        "data-decision-submit='",
        escapeHtml(event.event_id),
        "' style='margin-top:7px'>Record owner decision</button>",

        "</article>"
      ].join(""));
    });

    html.push(
      "<div data-owner-decision-receipt='true' style='margin-top:12px'></div>"
    );

    panel.innerHTML = html.join("");

    panel.querySelectorAll(
      "[data-decision-submit]"
    ).forEach(function (button) {

      button.addEventListener("click", async function () {

        var eventId = button.getAttribute(
          "data-decision-submit"
        );

        var decision = panel.querySelector(
          "[data-decision-select='" + eventId + "']"
        ).value;

        var reason = panel.querySelector(
          "[data-decision-reason='" + eventId + "']"
        ).value;

        var result = await fetch(
          "/tower/owner-dashboard/person/"
          + encodeURIComponent(pid)
          + "/event/"
          + encodeURIComponent(eventId)
          + "/decision",
          {
            method: "POST",
            headers: {
              "Content-Type": "application/json"
            },
            body: JSON.stringify({
              decision: decision,
              reason: reason
            })
          }
        );

        var payload = await result.json();

        var receipt = panel.querySelector(
          "[data-owner-decision-receipt='true']"
        );

        receipt.innerHTML =
          "<pre style='white-space:pre-wrap;font-size:11px'>"
          + escapeHtml(JSON.stringify(payload, null, 2))
          + "</pre>";

        if (result.ok) {
          await loadQueue(pid, panel);
        }
      });
    });
  }

  function install() {
    var pid = personId();
    if (!pid) return;

    var room = document.querySelector(
      "[data-tower-person-control-room='true']"
    );

    if (!room) {
      setTimeout(install, 50);
      return;
    }

    if (
      room.getAttribute("data-owner-decision-workflow") === "true"
    ) {
      return;
    }

    room.setAttribute(
      "data-owner-decision-workflow",
      "true"
    );

    var panel = ensurePanel(room);

    loadQueue(pid, panel);

    document.documentElement.setAttribute(
      "data-tower-owner-decision-status",
      "ready"
    );
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", install);
  } else {
    install();
  }

})();
</script>
"""


def inject_owner_decision_ui(html: str) -> str:
    source = str(html or "")

    if PERSON_OWNER_DECISION_MARKER in source:
        return source

    script = _decision_ui_script()

    if "</body>" in source:
        return source.replace(
            "</body>",
            script + "\n</body>",
            1,
        )

    return source + script


def _is_person_html(path: str) -> bool:
    prefix = "/tower/owner-dashboard/person/"

    if not path.startswith(prefix):
        return False

    remainder = path[len(prefix):]

    return (
        bool(remainder)
        and "/" not in remainder
        and not remainder.endswith(".json")
    )


def register_tower_person_owner_decision(app):

    marker = "_tower_person_owner_decision_twr061_065_registered"

    if getattr(app, marker, False):
        return app


    @app.after_request
    def tower_person_owner_decision_ui(response):

        if not _is_person_html(request.path):
            return response

        if response.status_code != 200:
            return response

        if "text/html" not in response.headers.get(
            "Content-Type", ""
        ):
            return response

        html = inject_owner_decision_ui(
            response.get_data(as_text=True)
        )

        response.set_data(html)
        response.headers["Content-Length"] = str(
            len(response.get_data())
        )

        return response


    @app.route(
        "/tower/owner-dashboard/person/<person_id>/decisions.json"
    )
    def tower_person_decisions_json(person_id):

        if not owner_session_active():
            return redirect("/tower/login")

        payload = owner_decision_payload(person_id)

        return jsonify(payload), (
            200
            if payload.get("status")
            == "tower_person_owner_decision_payload_ready"
            else 404
        )


    @app.route(
        "/tower/owner-dashboard/person/<person_id>/event/<event_id>/decision",
        methods=["POST"],
    )
    def tower_person_decision_post(person_id, event_id):

        if not owner_session_active():
            return redirect("/tower/login")

        incoming = (
            request.get_json(silent=True)
            or request.form
            or {}
        )

        result = build_owner_decision(
            person_id,
            event_id,
            incoming.get("decision"),
            reason=str(
                incoming.get("reason", "") or ""
            ),
        )

        if result.get("status") == "person_owner_decision_recorded":
            code = 200

        elif result.get("status") in {
            "not_found",
            "source_event_not_found",
        }:
            code = 404

        else:
            code = 400

        return jsonify(result), code


    setattr(app, marker, True)

    return app
