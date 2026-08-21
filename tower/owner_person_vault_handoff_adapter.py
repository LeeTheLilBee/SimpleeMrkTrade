from __future__ import annotations

import importlib
import inspect
import os
import uuid
from copy import deepcopy
from typing import Any, Callable, Dict

from flask import jsonify, redirect, request

from tower.owner_people_profile_rooms import people_profile_by_id

from tower.owner_person_event_ledger import (
    append_person_event,
    build_person_event,
    build_vault_ready_person_packet,
    read_event_by_id,
)

from tower.owner_person_decision_workflow import (
    latest_decision_for_event,
)

from tower.tower_human_login_ob_launch import owner_session_active


PERSON_VAULT_HANDOFF_ADAPTER_MARKER = (
    "tower-person-existing-vault-handoff-adapter-twr066-070"
)


EXPLICIT_ACCEPTED_STATUSES = {
    "accepted",
    "vault_accepted",
    "sealed",
    "vault_sealed",
    "handoff_accepted",
    "delivery_accepted",
}


def person_vault_handoff_adapter_summary() -> Dict[str, Any]:
    return {
        "status": "tower_person_existing_vault_handoff_adapter_ready",
        "product_rule": "reuse_existing_vault_handoff_do_not_create_parallel_transport",
        "requires_owner_approval": True,
        "requires_ready_for_vault": True,
        "browser_direct_vault_access": False,
        "creates_new_vault_transport": False,
        "fail_closed_when_handoff_unresolved": True,
        "explicit_acceptance_required_for_vault_sealed": True,
        "real_permission_changes": False,
        "live_auto": "LOCKED",
        "broker_execution": False,
        "capital_action": False,
    }


def _configured_callable_spec() -> str:
    return str(
        os.environ.get(
            "TOWER_VAULT_HANDOFF_CALLABLE",
            "",
        )
        or ""
    ).strip()


def resolve_existing_vault_handoff() -> Dict[str, Any]:

    spec = _configured_callable_spec()

    if not spec:
        return {
            "status": "existing_vault_handoff_not_resolved",
            "callable": None,
            "configured_spec": None,
        }

    if ":" not in spec:
        return {
            "status": "invalid_existing_vault_handoff_spec",
            "callable": None,
            "configured_spec": spec,
        }

    module_name, function_name = spec.split(
        ":",
        1,
    )

    try:
        module = importlib.import_module(
            module_name
        )

        fn = getattr(
            module,
            function_name,
        )

    except Exception as exc:
        return {
            "status": "existing_vault_handoff_import_failed",
            "callable": None,
            "configured_spec": spec,
            "error": repr(exc),
        }

    if not callable(fn):
        return {
            "status": "existing_vault_handoff_not_callable",
            "callable": None,
            "configured_spec": spec,
        }

    return {
        "status": "existing_vault_handoff_resolved",
        "callable": fn,
        "configured_spec": spec,
    }


def _invoke_existing_handoff(
    fn: Callable[..., Any],
    packet: Dict[str, Any],
) -> Any:

    signature = inspect.signature(fn)

    parameters = list(
        signature.parameters.values()
    )

    if any(
        p.kind == inspect.Parameter.VAR_KEYWORD
        for p in parameters
    ):
        return fn(
            packet=packet
        )

    if "packet" in signature.parameters:
        return fn(
            packet=packet
        )

    if "payload" in signature.parameters:
        return fn(
            payload=packet
        )

    required_positional = [
        p
        for p in parameters
        if p.kind in {
            inspect.Parameter.POSITIONAL_ONLY,
            inspect.Parameter.POSITIONAL_OR_KEYWORD,
        }
        and p.default is inspect.Parameter.empty
    ]

    if len(required_positional) == 1:
        return fn(
            packet
        )

    raise TypeError(
        "Existing Vault handoff callable does not expose a supported packet/payload signature."
    )


def normalize_vault_handoff_result(
    result: Any,
) -> Dict[str, Any]:

    if isinstance(result, dict):
        payload = deepcopy(result)
    else:
        payload = {
            "raw_result": repr(result),
        }

    status = str(
        payload.get(
            "status",
            "",
        )
        or ""
    ).strip().lower()

    explicitly_accepted = (
        payload.get("accepted") is True
        or payload.get("sealed") is True
        or status in EXPLICIT_ACCEPTED_STATUSES
    )

    record_reference = (
        payload.get("vault_record_reference")
        or payload.get("record_reference")
        or payload.get("record_id")
        or payload.get("receipt_id")
    )

    return {
        "explicitly_accepted": explicitly_accepted,
        "vault_status": (
            "VAULT_SEALED"
            if explicitly_accepted
            else "VAULT_DELIVERY_FAILED"
        ),
        "vault_record_reference": record_reference,
        "raw_result": payload,
    }


def approved_packet_for_event(
    person_id: str,
    event_id: str,
) -> Dict[str, Any]:

    profile = people_profile_by_id(
        person_id
    )

    if not profile:
        return {
            "status": "not_found",
        }

    event = read_event_by_id(
        event_id
    )

    if (
        not event
        or event.get("person_id")
        != profile["person_id"]
    ):
        return {
            "status": "source_event_not_found",
        }

    decision_event = latest_decision_for_event(
        profile["person_id"],
        event_id,
    )

    if not decision_event:
        return {
            "status": "owner_decision_required",
            "vault_delivery_performed": False,
        }

    resulting = (
        decision_event.get(
            "resulting_state"
        )
        or {}
    )

    decision = resulting.get(
        "owner_decision"
    )

    if decision != "APPROVED":
        return {
            "status": "event_not_approved_for_vault",
            "owner_decision": decision,
            "vault_delivery_performed": False,
        }

    receipt_id = resulting.get(
        "decision_receipt_id"
    )

    packet_result = build_vault_ready_person_packet(
        event,
        owner_decision="APPROVED",
        decision_reason=decision_event.get(
            "reason",
            "",
        ),
        decision_receipt_id=receipt_id,
    )

    if (
        packet_result.get("status")
        != "vault_person_packet_ready"
    ):
        return {
            "status": "vault_packet_not_ready",
            "packet_result": packet_result,
            "vault_delivery_performed": False,
        }

    return {
        "status": "approved_vault_packet_ready",
        "packet": packet_result["packet"],
        "decision_event": decision_event,
        "vault_delivery_performed": False,
    }


def deliver_person_event_to_existing_vault_handoff(
    person_id: str,
    event_id: str,
    *,
    handoff_callable: Callable[..., Any] | None = None,
) -> Dict[str, Any]:

    packet_result = approved_packet_for_event(
        person_id,
        event_id,
    )

    if (
        packet_result.get("status")
        != "approved_vault_packet_ready"
    ):
        return packet_result

    packet = packet_result["packet"]

    if (
        packet.get("archive_ready") is not True
        or packet.get("vault_status")
        != "READY_FOR_VAULT"
    ):
        return {
            "status": "vault_delivery_gate_closed",
            "vault_delivery_performed": False,
        }

    resolved_spec = None

    if handoff_callable is None:

        resolved = resolve_existing_vault_handoff()

        if (
            resolved.get("status")
            != "existing_vault_handoff_resolved"
        ):
            return {
                **resolved,
                "vault_delivery_performed": False,
                "packet_id": packet.get("packet_id"),
            }

        handoff_callable = resolved["callable"]
        resolved_spec = resolved.get(
            "configured_spec"
        )

    try:
        raw_result = _invoke_existing_handoff(
            handoff_callable,
            packet,
        )

    except Exception as exc:
        normalized = {
            "explicitly_accepted": False,
            "vault_status": "VAULT_DELIVERY_FAILED",
            "vault_record_reference": None,
            "raw_result": {
                "error": repr(exc),
            },
        }

    else:
        normalized = normalize_vault_handoff_result(
            raw_result
        )

    receipt_id = (
        "vault-handoff-receipt-"
        + uuid.uuid4().hex
    )

    built = build_person_event(
        person_id,
        event_type="PERSON_VAULT_HANDOFF_RESULT",
        action="vault_handoff",
        before_state={
            "source_event_id": event_id,
            "packet_id": packet.get("packet_id"),
            "vault_status": "READY_FOR_VAULT",
        },
        requested_state={
            "destination_system": "VAULT",
            "packet_type": packet.get("packet_type"),
        },
        resulting_state={
            "vault_status": normalized[
                "vault_status"
            ],
            "vault_record_reference": normalized[
                "vault_record_reference"
            ],
            "receipt_id": receipt_id,
        },
        reason=(
            "Existing Tower-to-Vault handoff adapter result"
        ),
        owner_review_status="APPROVED",
        tower_validation={
            "owner_approved": True,
            "packet_archive_ready": True,
            "existing_handoff_reused": True,
            "configured_callable": resolved_spec,
            "explicit_acceptance": normalized[
                "explicitly_accepted"
            ],
        },
        related_receipt_ids=[
            receipt_id,
            event_id,
        ],
        source="TOWER_EXISTING_VAULT_HANDOFF_ADAPTER",
    )

    append_result = None

    if built.get("status") == "person_event_built":
        append_result = append_person_event(
            built["event"]
        )

    return {
        "status": (
            "person_vault_handoff_sealed"
            if normalized["vault_status"]
            == "VAULT_SEALED"
            else "person_vault_handoff_failed"
        ),
        "vault_delivery_performed": True,
        "existing_handoff_reused": True,
        "creates_new_vault_transport": False,
        "packet_id": packet.get("packet_id"),
        "vault_status": normalized["vault_status"],
        "vault_record_reference": normalized[
            "vault_record_reference"
        ],
        "vault_handoff_receipt": {
            "receipt_id": receipt_id,
            "receipt_type": "tower_existing_vault_handoff_receipt",
            "source_event_id": event_id,
            "packet_id": packet.get("packet_id"),
            "vault_status": normalized["vault_status"],
            "explicit_acceptance": normalized[
                "explicitly_accepted"
            ],
        },
        "append_result": append_result,
        "handoff_result": normalized["raw_result"],
    }


def _vault_ui_script() -> str:
    return """
<script id="tower-person-existing-vault-handoff-adapter-twr066-070">
(function () {

  function pid() {
    var m = location.pathname.match(
      /^\\/tower\\/owner-dashboard\\/person\\/([^/]+)$/
    );
    return m ? decodeURIComponent(m[1]) : "";
  }

  function install() {

    var personId = pid();
    if (!personId) return;

    var room = document.querySelector(
      "[data-tower-person-control-room='true']"
    );

    if (!room) {
      setTimeout(install, 50);
      return;
    }

    if (
      room.getAttribute("data-vault-handoff-adapter") === "true"
    ) {
      return;
    }

    room.setAttribute(
      "data-vault-handoff-adapter",
      "true"
    );

    var card = document.createElement("section");
    card.className = "tower-person-control-card";

    card.innerHTML = [
      "<h3>Vault archive handoff</h3>",
      "<p>Approved person events can be sent through Tower's existing authorized Vault handoff.</p>",
      "<input data-vault-event-id='true' placeholder='Approved event ID' style='width:100%'>",
      "<button class='tower-person-control-button' type='button' data-send-vault='true' style='margin-top:8px'>Send approved event to Vault</button>",
      "<div data-vault-result='true' style='margin-top:10px'></div>",
      "<p class='tower-person-safety-note'>Tower performs the handoff. The browser does not call Vault directly.</p>"
    ].join("");

    room.appendChild(card);

    card.querySelector(
      "[data-send-vault='true']"
    ).addEventListener("click", async function () {

      var eventId = card.querySelector(
        "[data-vault-event-id='true']"
      ).value.trim();

      var result = card.querySelector(
        "[data-vault-result='true']"
      );

      if (!eventId) {
        result.textContent =
          "Choose or enter an approved event ID.";
        return;
      }

      result.textContent =
        "Sending through existing Tower → Vault handoff…";

      var response = await fetch(
        "/tower/owner-dashboard/person/"
        + encodeURIComponent(personId)
        + "/event/"
        + encodeURIComponent(eventId)
        + "/vault-handoff",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json"
          },
          body: "{}"
        }
      );

      var data = await response.json();

      result.innerHTML =
        "<pre style='white-space:pre-wrap;font-size:11px'>"
        + JSON.stringify(data, null, 2)
        + "</pre>";
    });

    document.documentElement.setAttribute(
      "data-tower-person-vault-handoff-status",
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


def inject_vault_handoff_ui(html: str) -> str:

    source = str(html or "")

    if PERSON_VAULT_HANDOFF_ADAPTER_MARKER in source:
        return source

    script = _vault_ui_script()

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


def register_tower_person_vault_handoff_adapter(app):

    marker = (
        "_tower_person_existing_vault_handoff_adapter_"
        "twr066_070_registered"
    )

    if getattr(app, marker, False):
        return app


    @app.after_request
    def vault_adapter_ui(response):

        if not _is_person_html(
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

        html = inject_vault_handoff_ui(
            response.get_data(as_text=True)
        )

        response.set_data(html)
        response.headers["Content-Length"] = str(
            len(response.get_data())
        )

        return response


    @app.route(
        "/tower/owner-dashboard/person/<person_id>/event/<event_id>/vault-handoff",
        methods=["POST"],
    )
    def tower_person_existing_vault_handoff(
        person_id,
        event_id,
    ):

        if not owner_session_active():
            return redirect("/tower/login")

        result = deliver_person_event_to_existing_vault_handoff(
            person_id,
            event_id,
        )

        status = result.get("status")

        if status == "person_vault_handoff_sealed":
            code = 200

        elif status in {
            "not_found",
            "source_event_not_found",
        }:
            code = 404

        elif status in {
            "existing_vault_handoff_not_resolved",
            "existing_vault_handoff_import_failed",
            "existing_vault_handoff_not_callable",
            "invalid_existing_vault_handoff_spec",
        }:
            code = 503

        else:
            code = 400

        return jsonify(result), code


    setattr(app, marker, True)

    return app
