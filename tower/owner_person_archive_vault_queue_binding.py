from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict

from flask import jsonify, redirect, request

from tower.archive_vault_handoff import (
    build_archive_vault_handoff_record,
    queue_archive_vault_handoff,
)

from tower.owner_person_decision_workflow import (
    latest_decision_for_event,
)

from tower.owner_person_event_ledger import (
    append_person_event,
    build_person_event,
    build_vault_ready_person_packet,
    read_event_by_id,
)

from tower.owner_people_profile_rooms import (
    people_profile_by_id,
)

from tower.tower_human_login_ob_launch import (
    owner_session_active,
)


PERSON_ARCHIVE_VAULT_QUEUE_MARKER = (
    "tower-person-real-archive-vault-queue-binding-twr071-075"
)


VAULT_QUEUE_STATUS = (
    "VAULT_HANDOFF_QUEUED"
)


def person_archive_vault_queue_summary() -> Dict[str, Any]:

    return {
        "status": "tower_person_archive_vault_queue_binding_ready",

        "product_rule": (
            "reuse_real_existing_archive_vault_queue_without_claiming_vault_acceptance"
        ),

        "existing_handoff_module": (
            "tower.archive_vault_handoff"
        ),

        "existing_builder": (
            "build_archive_vault_handoff_record"
        ),

        "existing_queue_callable": (
            "queue_archive_vault_handoff"
        ),

        "tower_queue_status": (
            VAULT_QUEUE_STATUS
        ),

        "vault_accepted": False,

        "vault_sealed": False,

        "archive_vault_app_wired": False,

        "queue_receipt_enabled": True,

        "browser_direct_vault_access": False,

        "creates_parallel_transport": False,

        "real_permission_changes": False,

        "live_auto": "LOCKED",

        "broker_execution": False,

        "capital_action": False,
    }


def approved_person_packet(
    person_id: str,
    event_id: str,
) -> Dict[str, Any]:

    profile = people_profile_by_id(
        person_id
    )

    if not profile:

        return {
            "status": "not_found",
            "person_id": person_id,
        }


    source_event = read_event_by_id(
        event_id
    )


    if (
        not source_event
        or source_event.get(
            "person_id"
        )
        != profile[
            "person_id"
        ]
    ):

        return {
            "status": "source_event_not_found",
            "person_id": profile[
                "person_id"
            ],
            "event_id": event_id,
        }


    decision_event = (
        latest_decision_for_event(
            profile[
                "person_id"
            ],
            event_id,
        )
    )


    if not decision_event:

        return {
            "status": "owner_decision_required",
            "vault_queue_performed": False,
        }


    resulting = (
        decision_event.get(
            "resulting_state"
        )
        or {}
    )


    owner_decision = (
        resulting.get(
            "owner_decision"
        )
    )


    if (
        owner_decision
        != "APPROVED"
    ):

        return {
            "status": "event_not_approved_for_archive",
            "owner_decision": owner_decision,
            "vault_queue_performed": False,
        }


    packet_result = (
        build_vault_ready_person_packet(
            source_event,

            owner_decision=(
                "APPROVED"
            ),

            decision_reason=(
                decision_event.get(
                    "reason",
                    "",
                )
            ),

            decision_receipt_id=(
                resulting.get(
                    "decision_receipt_id"
                )
            ),
        )
    )


    if (
        packet_result.get(
            "status"
        )
        != "vault_person_packet_ready"
    ):

        return {
            "status": "person_packet_not_ready",
            "packet_result": packet_result,
            "vault_queue_performed": False,
        }


    packet = (
        packet_result[
            "packet"
        ]
    )


    if (
        packet.get(
            "archive_ready"
        )
        is not True
        or packet.get(
            "vault_status"
        )
        != "READY_FOR_VAULT"
    ):

        return {
            "status": "ready_for_vault_gate_closed",
            "packet": packet,
            "vault_queue_performed": False,
        }


    return {
        "status": "approved_person_packet_ready",
        "profile": profile,
        "source_event": source_event,
        "decision_event": decision_event,
        "packet": packet,
        "vault_queue_performed": False,
    }


def build_person_archive_handoff_record(
    person_id: str,
    event_id: str,
    *,
    owner_note: str = "",
) -> Dict[str, Any]:

    ready = (
        approved_person_packet(
            person_id,
            event_id,
        )
    )


    if (
        ready.get(
            "status"
        )
        != "approved_person_packet_ready"
    ):

        return ready


    profile = (
        ready[
            "profile"
        ]
    )

    source_event = (
        ready[
            "source_event"
        ]
    )

    packet = (
        ready[
            "packet"
        ]
    )


    handoff_record = (
        build_archive_vault_handoff_record(

            source_type=(
                "tower_person_change_proof"
            ),

            source_id=(
                source_event[
                    "event_id"
                ]
            ),

            title=(
                "Tower person change proof: "
                + profile[
                    "display_name"
                ]
            ),

            summary=(
                "Approved Tower person-control event "
                "prepared for Archive Vault handoff queue."
            ),

            severity="medium",

            user_id="owner_solice",

            related_object={
                "person_id": profile[
                    "person_id"
                ],

                "display_name": profile[
                    "display_name"
                ],

                "event_id": source_event[
                    "event_id"
                ],

                "action": source_event.get(
                    "action"
                ),

                "packet_id": packet.get(
                    "packet_id"
                ),

                "packet_type": packet.get(
                    "packet_type"
                ),

                "tower_event_integrity_hash": (
                    source_event.get(
                        "integrity_hash"
                    )
                ),

                "packet_integrity_hash": (
                    packet.get(
                        "packet_integrity_hash"
                    )
                ),
            },

            source_payload={
                "person_change_proof_packet": deepcopy(
                    packet
                ),

                "owner_decision": (
                    ready[
                        "decision_event"
                    ].get(
                        "resulting_state",
                        {},
                    )
                ),
            },

            owner_note=(
                owner_note
            ),
        )
    )


    return {
        "status": "person_archive_handoff_record_ready",

        "handoff_record": handoff_record,

        "packet": packet,

        "source_event": source_event,

        "vault_queue_performed": False,

        "vault_accepted": False,

        "vault_sealed": False,
    }


def queue_person_event_for_archive_vault(
    person_id: str,
    event_id: str,
    *,
    owner_note: str = "",
) -> Dict[str, Any]:

    prepared = (
        build_person_archive_handoff_record(
            person_id,
            event_id,
            owner_note=owner_note,
        )
    )


    if (
        prepared.get(
            "status"
        )
        != "person_archive_handoff_record_ready"
    ):

        return prepared


    record = (
        prepared[
            "handoff_record"
        ]
    )


    queued = (
        queue_archive_vault_handoff(
            record
        )
    )


    if (
        queued.get(
            "ok"
        )
        is not True
        or queued.get(
            "status"
        )
        != "queued"
    ):

        return {
            "status": "person_archive_vault_queue_failed",

            "queue_result": queued,

            "handoff_record": record,

            "vault_queue_performed": False,

            "vault_accepted": False,

            "vault_sealed": False,
        }


    receipt_event_result = (
        build_person_event(

            person_id,

            event_type=(
                "PERSON_ARCHIVE_VAULT_HANDOFF_QUEUED"
            ),

            action=(
                "archive_vault_handoff_queue"
            ),

            before_state={
                "source_event_id": event_id,

                "vault_status": (
                    "READY_FOR_VAULT"
                ),
            },

            requested_state={
                "destination": (
                    "Archive Vault"
                ),

                "handoff_id": (
                    queued.get(
                        "handoff_id"
                    )
                ),

                "packet_id": (
                    prepared[
                        "packet"
                    ].get(
                        "packet_id"
                    )
                ),
            },

            resulting_state={
                "vault_status": (
                    VAULT_QUEUE_STATUS
                ),

                "handoff_status": (
                    "queued"
                ),

                "handoff_id": (
                    queued.get(
                        "handoff_id"
                    )
                ),

                "queue_path": (
                    queued.get(
                        "path"
                    )
                ),

                "vault_accepted": False,

                "vault_sealed": False,
            },

            reason=(
                "Approved person proof queued through "
                "existing Tower Archive Vault handoff."
            ),

            owner_review_status=(
                "APPROVED"
            ),

            tower_validation={
                "owner_approval_verified": True,

                "ready_for_vault_verified": True,

                "existing_archive_vault_handoff_reused": True,

                "existing_handoff_status": (
                    queued.get(
                        "status"
                    )
                ),

                "archive_vault_app_wired": False,

                "vault_acceptance_verified": False,

                "vault_sealing_verified": False,
            },

            related_receipt_ids=[
                str(
                    queued.get(
                        "handoff_id",
                        "",
                    )
                    or ""
                ),

                event_id,
            ],

            source=(
                "TOWER_ARCHIVE_VAULT_HANDOFF_QUEUE"
            ),
        )
    )


    append_result = None


    if (
        receipt_event_result.get(
            "status"
        )
        == "person_event_built"
    ):

        append_result = (
            append_person_event(
                receipt_event_result[
                    "event"
                ]
            )
        )


    return {
        "status": "person_archive_vault_handoff_queued",

        "vault_queue_performed": True,

        "vault_status": VAULT_QUEUE_STATUS,

        "vault_accepted": False,

        "vault_sealed": False,

        "existing_handoff_reused": True,

        "creates_parallel_transport": False,

        "handoff_id": queued.get(
            "handoff_id"
        ),

        "queue_path": queued.get(
            "path"
        ),

        "queue_result": queued,

        "handoff_record": record,

        "packet": prepared[
            "packet"
        ],

        "tower_receipt_event": (
            receipt_event_result.get(
                "event"
            )
        ),

        "append_result": append_result,

        "receipt": {
            "receipt_type": (
                "tower_person_archive_vault_handoff_queue_receipt"
            ),

            "source_event_id": event_id,

            "handoff_id": queued.get(
                "handoff_id"
            ),

            "vault_status": (
                VAULT_QUEUE_STATUS
            ),

            "vault_accepted": False,

            "vault_sealed": False,

            "message": (
                "Tower queued the approved person proof "
                "through the existing Archive Vault handoff. "
                "Archive Vault acceptance/sealing has not occurred."
            ),
        },
    }


def _ui_script() -> str:

    return """
<script id="tower-person-real-archive-vault-queue-binding-twr071-075">
(function () {

  function personId() {
    var match = window.location.pathname.match(
      /^\\/tower\\/owner-dashboard\\/person\\/([^/]+)$/
    );

    return match
      ? decodeURIComponent(match[1])
      : "";
  }


  function install() {

    var pid = personId();

    if (!pid) return;


    var room = document.querySelector(
      "[data-tower-person-control-room='true']"
    );


    if (!room) {

      window.setTimeout(
        install,
        50
      );

      return;
    }


    if (
      room.getAttribute(
        "data-real-archive-vault-queue-binding"
      )
      === "true"
    ) {
      return;
    }


    room.setAttribute(
      "data-real-archive-vault-queue-binding",
      "true"
    );


    var card = document.createElement(
      "section"
    );

    card.className = (
      "tower-person-control-card"
    );


    card.innerHTML = [

      "<h3>Archive Vault handoff queue</h3>",

      "<p>",
      "Approved person changes can be queued through ",
      "Tower's existing Archive Vault handoff.",
      "</p>",

      "<p class='tower-person-safety-note'>",
      "Queued does not mean Vault accepted or sealed. ",
      "The current Archive Vault handoff is a safe Tower-side queue.",
      "</p>",

      "<input ",
      "data-archive-vault-event-id='true' ",
      "placeholder='Approved event ID' ",
      "style='width:100%'>",

      "<textarea ",
      "data-archive-vault-owner-note='true' ",
      "placeholder='Optional archive note' ",
      "style='width:100%;margin-top:7px'></textarea>",

      "<button ",
      "type='button' ",
      "class='tower-person-control-button' ",
      "data-queue-archive-vault='true' ",
      "style='margin-top:8px'>",
      "Queue approved proof for Archive Vault",
      "</button>",

      "<div ",
      "data-archive-vault-result='true' ",
      "style='margin-top:10px'>",
      "</div>"

    ].join("");


    room.appendChild(
      card
    );


    card.querySelector(
      "[data-queue-archive-vault='true']"
    ).addEventListener(
      "click",
      async function () {

        var eventId = (
          card.querySelector(
            "[data-archive-vault-event-id='true']"
          ).value.trim()
        );


        var ownerNote = (
          card.querySelector(
            "[data-archive-vault-owner-note='true']"
          ).value.trim()
        );


        var result = (
          card.querySelector(
            "[data-archive-vault-result='true']"
          )
        );


        if (!eventId) {

          result.textContent = (
            "Enter an approved event ID."
          );

          return;
        }


        result.textContent = (
          "Queueing through Tower's existing Archive Vault handoff…"
        );


        var response = await fetch(

          "/tower/owner-dashboard/person/"
          + encodeURIComponent(pid)
          + "/event/"
          + encodeURIComponent(eventId)
          + "/archive-vault-queue",

          {
            method: "POST",

            headers: {
              "Content-Type": "application/json"
            },

            body: JSON.stringify({
              owner_note: ownerNote
            })
          }
        );


        var payload = await response.json();


        result.innerHTML = (
          "<pre style='white-space:pre-wrap;font-size:11px'>"
          + JSON.stringify(
              payload,
              null,
              2
            )
          + "</pre>"
        );
      }
    );


    document.documentElement.setAttribute(
      "data-tower-person-archive-vault-queue-status",
      "ready"
    );
  }


  if (
    document.readyState
    === "loading"
  ) {

    document.addEventListener(
      "DOMContentLoaded",
      install
    );

  } else {

    install();

  }

})();
</script>
"""


def inject_person_archive_vault_queue_ui(
    html: str,
) -> str:

    source = str(
        html
        or ""
    )


    if (
        PERSON_ARCHIVE_VAULT_QUEUE_MARKER
        in source
    ):

        return source


    script = (
        _ui_script()
    )


    if "</body>" in source:

        return source.replace(
            "</body>",
            script
            + "\n</body>",
            1,
        )


    return (
        source
        + script
    )


def _is_person_html_room(
    path: str,
) -> bool:

    prefix = (
        "/tower/owner-dashboard/person/"
    )


    if not path.startswith(
        prefix
    ):

        return False


    remainder = (
        path[
            len(
                prefix
            ):
        ]
    )


    return (
        bool(
            remainder
        )
        and "/" not in remainder
        and not remainder.endswith(
            ".json"
        )
    )


def register_tower_person_archive_vault_queue_binding(
    app,
):

    marker = (
        "_tower_person_archive_vault_queue_binding_"
        "twr071_075_registered"
    )


    if getattr(
        app,
        marker,
        False,
    ):

        return app


    @app.after_request
    def archive_vault_queue_ui(
        response,
    ):

        if not _is_person_html_room(
            request.path
        ):

            return response


        if (
            response.status_code
            != 200
        ):

            return response


        if (
            "text/html"
            not in response.headers.get(
                "Content-Type",
                "",
            )
        ):

            return response


        html = (
            inject_person_archive_vault_queue_ui(
                response.get_data(
                    as_text=True
                )
            )
        )


        response.set_data(
            html
        )


        response.headers[
            "Content-Length"
        ] = str(
            len(
                response.get_data()
            )
        )


        return response


    @app.route(
        "/tower/owner-dashboard/person/"
        "<person_id>/event/<event_id>/archive-vault-queue",
        methods=[
            "POST",
        ],
    )
    def tower_person_archive_vault_queue_post(
        person_id,
        event_id,
    ):

        if not owner_session_active():

            return redirect(
                "/tower/login"
            )


        incoming = (
            request.get_json(
                silent=True
            )
            or request.form
            or {}
        )


        result = (
            queue_person_event_for_archive_vault(
                person_id,
                event_id,

                owner_note=str(
                    incoming.get(
                        "owner_note",
                        "",
                    )
                    or ""
                ),
            )
        )


        status = (
            result.get(
                "status"
            )
        )


        if (
            status
            == "person_archive_vault_handoff_queued"
        ):

            code = 200


        elif status in {
            "not_found",
            "source_event_not_found",
        }:

            code = 404


        else:

            code = 400


        return jsonify(
            result
        ), code


    setattr(
        app,
        marker,
        True,
    )


    return app
