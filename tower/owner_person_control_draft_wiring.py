from __future__ import annotations

from typing import Any, Dict, List

from flask import jsonify, redirect, request

from tower.owner_people_change_queue import (
    build_change_queue_item,
    staged_change_queue,
)

from tower.owner_people_profile_rooms import (
    APP_ACCESS_OPTIONS,
    APP_MATRIX,
    DESIGNATION_OPTIONS,
    build_app_access_change_draft,
    build_designation_change_draft,
    build_person_freeze_draft,
    people_profile_by_id,
)

from tower.tower_human_login_ob_launch import (
    owner_session_active,
)


PERSON_CONTROL_DRAFT_WIRING_MARKER = (
    "tower-person-control-draft-wiring-twr051-055"
)


CONTROL_ACTIONS = (
    "designation",
    "app_access",
    "responsibility",
    "status",
    "freeze",
    "restore",
    "paperwork_note",
)


STATUS_OPTIONS = (
    "Planned",
    "Active",
    "Inactive",
    "Owner Review Required",
    "Blocked",
)


def person_control_draft_wiring_summary() -> Dict[str, Any]:
    return {
        "status": "tower_person_control_draft_wiring_ready",
        "product_rule": (
            "person_control_room_actions_create_validated_drafts_not_live_mutations"
        ),
        "control_actions": list(CONTROL_ACTIONS),
        "designation_options": list(DESIGNATION_OPTIONS),
        "app_access_options": list(APP_ACCESS_OPTIONS),
        "app_matrix": list(APP_MATRIX),
        "status_options": list(STATUS_OPTIONS),
        "draft_submission_enabled": True,
        "durable_persistence_enabled": False,
        "activity_projection_enabled": True,
        "draft_receipts_enabled": True,
        "real_account_creation": False,
        "real_invites_sent": False,
        "real_access_granted": False,
        "real_access_revoked": False,
        "real_person_frozen": False,
        "real_person_restored": False,
        "real_permission_changes": False,
        "live_auto": "LOCKED",
        "broker_execution": False,
        "capital_action": False,
    }


def person_queue_projection(
    person_id: str,
) -> List[Dict[str, Any]]:
    normalized = str(
        person_id or ""
    ).strip().lower()

    return [
        item
        for item in staged_change_queue()
        if str(
            item.get(
                "person_id",
                "",
            )
        ).strip().lower()
        == normalized
    ]


def person_control_room_payload(
    person_id: str,
) -> Dict[str, Any]:
    profile = people_profile_by_id(
        person_id
    )

    if not profile:
        return {
            "status": "not_found",
            "person_id": person_id,
            "real_permission_changes": False,
            "real_access_granted": False,
        }

    return {
        "status": "tower_person_control_room_payload_ready",
        "profile": profile,
        "allowed": {
            "actions": list(
                CONTROL_ACTIONS
            ),
            "designations": list(
                DESIGNATION_OPTIONS
            ),
            "apps": list(
                APP_MATRIX
            ),
            "access_levels": list(
                APP_ACCESS_OPTIONS
            ),
            "status_options": list(
                STATUS_OPTIONS
            ),
        },
        "queue": person_queue_projection(
            profile["person_id"]
        ),
        "safety": {
            "durable_persistence_enabled": False,
            "real_account_creation": False,
            "real_invites_sent": False,
            "real_access_granted": False,
            "real_access_revoked": False,
            "real_person_frozen": False,
            "real_person_restored": False,
            "real_permission_changes": False,
            "live_auto": "LOCKED",
            "broker_execution": False,
            "capital_action": False,
        },
    }


def _queue_from_result(
    *,
    profile: Dict[str, Any],
    action: str,
    requested_change: str,
    risk_note: str,
) -> Dict[str, Any]:
    return build_change_queue_item(
        {
            "person_id": profile[
                "person_id"
            ],
            "display_name": profile[
                "display_name"
            ],
            "change_type": action,
            "requested_change": requested_change,
            "risk_note": risk_note,
        }
    )


def build_person_control_draft(
    person_id: str,
    payload: Dict[str, Any],
) -> Dict[str, Any]:
    profile = people_profile_by_id(
        person_id
    )

    if not profile:
        return {
            "status": "not_found",
            "person_id": person_id,
            "real_permission_changes": False,
            "real_access_granted": False,
        }

    action = str(
        payload.get(
            "action",
            "",
        )
        or ""
    ).strip()

    if action not in CONTROL_ACTIONS:
        return {
            "status": "invalid_control_action",
            "person_id": profile[
                "person_id"
            ],
            "allowed_actions": list(
                CONTROL_ACTIONS
            ),
            "real_permission_changes": False,
            "real_access_granted": False,
        }

    notes = str(
        payload.get(
            "notes",
            "",
        )
        or ""
    ).strip()

    draft: Dict[str, Any]
    queue_item: Dict[str, Any]


    # ------------------------------------------------------------------------------------------------
    # DESIGNATION
    # ------------------------------------------------------------------------------------------------

    if action == "designation":
        requested_designation = str(
            payload.get(
                "requested_designation",
                "",
            )
            or ""
        ).strip()

        draft = build_designation_change_draft(
            profile["person_id"],
            requested_designation,
            notes,
        )

        if (
            draft.get("status")
            != "designation_change_draft_created"
        ):
            return {
                **draft,
                "control_action": action,
            }

        queue_item = _queue_from_result(
            profile=profile,
            action=action,
            requested_change=(
                f"Change designation from "
                f"{profile['designation']} to "
                f"{requested_designation}"
            ),
            risk_note=(
                notes
                or "Designation changes require explicit owner review."
            ),
        )


    # ------------------------------------------------------------------------------------------------
    # APP ACCESS
    # ------------------------------------------------------------------------------------------------

    elif action == "app_access":
        app_name = str(
            payload.get(
                "app_name",
                "",
            )
            or ""
        ).strip()

        access_level = str(
            payload.get(
                "access_level",
                "",
            )
            or ""
        ).strip()

        draft = build_app_access_change_draft(
            profile["person_id"],
            app_name,
            access_level,
            notes,
        )

        if (
            draft.get("status")
            != "app_access_change_draft_created"
        ):
            return {
                **draft,
                "control_action": action,
            }

        queue_item = _queue_from_result(
            profile=profile,
            action=action,
            requested_change=(
                f"{app_name}: "
                f"{access_level}"
            ),
            risk_note=(
                notes
                or "No app access changes become live from this draft."
            ),
        )


    # ------------------------------------------------------------------------------------------------
    # FREEZE
    # ------------------------------------------------------------------------------------------------

    elif action == "freeze":
        reason = str(
            payload.get(
                "reason",
                "",
            )
            or notes
        ).strip()

        draft = build_person_freeze_draft(
            profile["person_id"],
            reason,
        )

        if (
            draft.get("status")
            != "person_freeze_draft_created"
        ):
            return {
                **draft,
                "control_action": action,
            }

        queue_item = _queue_from_result(
            profile=profile,
            action=action,
            requested_change=(
                "Prepare account/access freeze review"
            ),
            risk_note=(
                reason
                or "Freeze remains a draft. No real access is disabled."
            ),
        )


    # ------------------------------------------------------------------------------------------------
    # RESPONSIBILITY
    # ------------------------------------------------------------------------------------------------

    elif action == "responsibility":
        responsibilities = str(
            payload.get(
                "responsibilities",
                "",
            )
            or ""
        ).strip()

        if not responsibilities:
            return {
                "status": "invalid_responsibility_draft",
                "reason": "responsibilities_required",
                "person_id": profile[
                    "person_id"
                ],
                "real_permission_changes": False,
                "real_access_granted": False,
            }

        draft = {
            "status": "responsibility_change_draft_created",
            "person_id": profile[
                "person_id"
            ],
            "display_name": profile[
                "display_name"
            ],
            "responsibilities": responsibilities,
            "notes": notes,
            "requires_owner_review": True,
            "changes_real_permissions": False,
            "grants_real_access": False,
        }

        queue_item = _queue_from_result(
            profile=profile,
            action=action,
            requested_change=(
                f"Responsibilities: {responsibilities}"
            ),
            risk_note=(
                notes
                or "Responsibilities remain staged until owner review."
            ),
        )


    # ------------------------------------------------------------------------------------------------
    # STATUS
    # ------------------------------------------------------------------------------------------------

    elif action == "status":
        requested_status = str(
            payload.get(
                "requested_status",
                "",
            )
            or ""
        ).strip()

        if requested_status not in STATUS_OPTIONS:
            return {
                "status": "invalid_status_draft",
                "person_id": profile[
                    "person_id"
                ],
                "allowed_statuses": list(
                    STATUS_OPTIONS
                ),
                "real_permission_changes": False,
                "real_access_granted": False,
            }

        draft = {
            "status": "status_change_draft_created",
            "person_id": profile[
                "person_id"
            ],
            "display_name": profile[
                "display_name"
            ],
            "current_status": profile[
                "status"
            ],
            "requested_status": requested_status,
            "notes": notes,
            "requires_owner_review": True,
            "changes_real_permissions": False,
            "grants_real_access": False,
        }

        queue_item = _queue_from_result(
            profile=profile,
            action=action,
            requested_change=(
                f"Status: "
                f"{profile['status']} → "
                f"{requested_status}"
            ),
            risk_note=(
                notes
                or "Status draft does not enable or disable a real account."
            ),
        )


    # ------------------------------------------------------------------------------------------------
    # RESTORE
    # ------------------------------------------------------------------------------------------------

    elif action == "restore":
        reason = str(
            payload.get(
                "reason",
                "",
            )
            or notes
        ).strip()

        draft = {
            "status": "person_restore_draft_created",
            "person_id": profile[
                "person_id"
            ],
            "display_name": profile[
                "display_name"
            ],
            "reason": reason,
            "requires_owner_review": True,
            "restores_real_access": False,
            "changes_real_permissions": False,
            "grants_real_access": False,
        }

        queue_item = _queue_from_result(
            profile=profile,
            action=action,
            requested_change=(
                "Prepare restore-access review"
            ),
            risk_note=(
                reason
                or "Restore draft does not change live permissions."
            ),
        )


    # ------------------------------------------------------------------------------------------------
    # PAPERWORK NOTE
    # ------------------------------------------------------------------------------------------------

    else:
        paperwork_note = str(
            payload.get(
                "paperwork_note",
                "",
            )
            or notes
        ).strip()

        if not paperwork_note:
            return {
                "status": "invalid_paperwork_note_draft",
                "reason": "paperwork_note_required",
                "person_id": profile[
                    "person_id"
                ],
                "real_permission_changes": False,
                "real_access_granted": False,
            }

        draft = {
            "status": "paperwork_note_draft_created",
            "person_id": profile[
                "person_id"
            ],
            "display_name": profile[
                "display_name"
            ],
            "paperwork_note": paperwork_note,
            "requires_owner_review": True,
            "changes_real_permissions": False,
            "grants_real_access": False,
        }

        queue_item = _queue_from_result(
            profile=profile,
            action=action,
            requested_change=(
                f"Paperwork review note: "
                f"{paperwork_note}"
            ),
            risk_note=(
                "Paperwork workflow remains owner-reviewed."
            ),
        )


    if (
        queue_item.get("status")
        != "change_queue_item_created"
    ):
        return {
            "status": "control_draft_queue_build_failed",
            "control_action": action,
            "draft": draft,
            "queue_item": queue_item,
            "real_permission_changes": False,
            "real_access_granted": False,
        }

    return {
        "status": "person_control_draft_created",
        "control_action": action,
        "person_id": profile[
            "person_id"
        ],
        "display_name": profile[
            "display_name"
        ],
        "draft": draft,
        "queue_item": queue_item,
        "receipt": {
            "receipt_type": (
                "tower_person_control_draft_receipt"
            ),
            "owner_review_required": True,
            "durable_persistence": False,
            "message": (
                "Draft validated. "
                "Nothing has been applied to live access."
            ),
        },
        "safety": {
            "creates_real_account": False,
            "sends_real_invite": False,
            "grants_real_access": False,
            "revokes_real_access": False,
            "freezes_real_access": False,
            "restores_real_access": False,
            "changes_real_permissions": False,
            "live_auto": "LOCKED",
            "broker_execution": False,
            "capital_action": False,
        },
    }


def _person_control_wiring_script() -> str:
    return """
    <script id="tower-person-control-draft-wiring-twr051-055">
    (function () {

      function personIdFromPath() {
        var match = window.location.pathname.match(
          /^\\/tower\\/owner-dashboard\\/person\\/([^/]+)$/
        );

        return match
          ? decodeURIComponent(match[1])
          : "";
      }


      function createReceiptHost(room) {
        var existing = room.querySelector(
          "[data-tower-control-receipt-host='true']"
        );

        if (existing) return existing;

        var host = document.createElement("section");

        host.setAttribute(
          "data-tower-control-receipt-host",
          "true"
        );

        host.style.marginTop = "12px";
        host.style.padding = "12px";
        host.style.borderRadius = "16px";
        host.style.border =
          "1px solid rgba(248,217,120,.22)";
        host.style.background =
          "rgba(248,217,120,.06)";
        host.style.color =
          "rgba(255,248,255,.82)";
        host.style.fontSize = "12px";

        host.innerHTML =
          "<strong style='color:#f8d978'>Draft receipts</strong>"
          + "<p style='margin:5px 0 0'>"
          + "Validated owner drafts will appear here."
          + "</p>";

        room.appendChild(host);

        return host;
      }


      function showReceipt(host, payload, ok) {
        host.innerHTML = "";

        var title = document.createElement("strong");

        title.style.color = ok
          ? "#f8d978"
          : "#ff9bb0";

        title.textContent = ok
          ? "Draft validated"
          : "Draft not created";

        var pre = document.createElement("pre");

        pre.style.whiteSpace = "pre-wrap";
        pre.style.wordBreak = "break-word";
        pre.style.margin = "8px 0 0";
        pre.style.fontSize = "11px";
        pre.style.color =
          "rgba(255,248,255,.78)";

        pre.textContent = JSON.stringify(
          payload,
          null,
          2
        );

        host.appendChild(title);
        host.appendChild(pre);
      }


      async function submitDraft(
        personId,
        payload,
        receiptHost
      ) {
        receiptHost.innerHTML =
          "<strong style='color:#f8d978'>Validating draft…</strong>";

        try {
          var response = await fetch(
            "/tower/owner-dashboard/person/"
              + encodeURIComponent(personId)
              + "/control-draft",
            {
              method: "POST",
              headers: {
                "Content-Type": "application/json"
              },
              body: JSON.stringify(payload)
            }
          );

          var data = await response.json();

          showReceipt(
            receiptHost,
            data,
            response.ok
          );

          return data;

        } catch (error) {
          showReceipt(
            receiptHost,
            {
              status: "draft_submission_error",
              error: String(error)
            },
            false
          );
        }
      }


      function fieldValue(drawer, selector) {
        var element = drawer.querySelector(
          selector
        );

        return element
          ? String(element.value || "").trim()
          : "";
      }


      function addSubmitButton(
        drawer,
        action,
        personId,
        receiptHost
      ) {
        if (
          drawer.querySelector(
            "[data-tower-control-submit='"
              + action
              + "']"
          )
        ) {
          return;
        }

        var button = document.createElement(
          "button"
        );

        button.type = "button";

        button.className =
          "tower-person-control-button";

        button.setAttribute(
          "data-tower-control-submit",
          action
        );

        button.textContent =
          "Submit draft for owner review";


        button.addEventListener(
          "click",
          function () {

            var payload = {
              action: action
            };


            if (action === "designation") {
              payload.requested_designation =
                fieldValue(
                  drawer,
                  "input"
                );

              payload.notes =
                fieldValue(
                  drawer,
                  "textarea"
                );
            }


            else if (action === "responsibility") {
              payload.responsibilities =
                fieldValue(
                  drawer,
                  "textarea"
                );
            }


            else if (action === "access") {
              payload.action = "app_access";

              var inputs =
                drawer.querySelectorAll(
                  "input, select, textarea"
                );

              payload.app_name =
                inputs[0]
                  ? String(
                      inputs[0].value || ""
                    ).trim()
                  : "";

              payload.access_level =
                inputs[1]
                  ? String(
                      inputs[1].value || ""
                    ).trim()
                  : "";

              payload.notes =
                inputs[2]
                  ? String(
                      inputs[2].value || ""
                    ).trim()
                  : "";
            }


            else if (action === "freeze") {
              payload.reason =
                fieldValue(
                  drawer,
                  "textarea"
                )
                || "Owner requested freeze review";
            }


            else if (action === "restore") {
              payload.reason =
                fieldValue(
                  drawer,
                  "textarea"
                )
                || "Owner requested restore review";
            }


            submitDraft(
              personId,
              payload,
              receiptHost
            );

          }
        );


        var row = document.createElement(
          "div"
        );

        row.className =
          "tower-person-control-button-row";

        row.appendChild(button);

        drawer.appendChild(row);
      }


      async function loadProfile(
        personId,
        room
      ) {
        try {
          var response = await fetch(
            "/tower/owner-dashboard/person/"
              + encodeURIComponent(personId)
              + "/control-room.json"
          );

          if (!response.ok) {
            return;
          }

          var data = await response.json();

          var profile = data.profile || {};

          var header = room.querySelector(
            ".tower-person-control-header"
          );

          if (header) {
            var title = header.querySelector(
              ".tower-person-control-title"
            );

            if (
              title
              && profile.display_name
            ) {
              title.textContent =
                profile.display_name;
            }

            var chips = header.querySelector(
              ".tower-person-control-chip-row"
            );

            if (chips) {
              chips.innerHTML = [
                "<span class='tower-person-control-chip'><strong>Designation</strong> "
                  + (profile.designation || "Unknown")
                  + "</span>",

                "<span class='tower-person-control-chip'><strong>Status</strong> "
                  + (profile.status || "Unknown")
                  + "</span>",

                "<span class='tower-person-control-chip'><strong>Scope</strong> "
                  + (profile.assigned_scope || "Owner review")
                  + "</span>"
              ].join("");
            }
          }


          var queue = data.queue || [];

          if (queue.length) {
            var receiptHost = createReceiptHost(
              room
            );

            var summary =
              document.createElement("div");

            summary.style.marginTop = "8px";

            summary.innerHTML =
              "<strong style='color:#f8d978'>"
              + queue.length
              + " staged queue item(s) already relate to this person."
              + "</strong>";

            receiptHost.appendChild(
              summary
            );
          }


          document.documentElement.setAttribute(
            "data-tower-person-control-profile-status",
            "loaded"
          );

        } catch (error) {
          document.documentElement.setAttribute(
            "data-tower-person-control-profile-status",
            "load-error"
          );
        }
      }


      function installWiring() {
        var personId = personIdFromPath();

        if (!personId) return;

        var room = document.querySelector(
          "[data-tower-person-control-room='true']"
        );

        if (!room) {
          window.setTimeout(
            installWiring,
            50
          );

          return;
        }


        if (
          room.getAttribute(
            "data-tower-control-draft-wiring"
          )
          === "true"
        ) {
          return;
        }


        room.setAttribute(
          "data-tower-control-draft-wiring",
          "true"
        );


        var receiptHost =
          createReceiptHost(room);


        [
          "designation",
          "responsibility",
          "access",
          "freeze",
          "restore"
        ].forEach(function (action) {

          var drawers =
            room.querySelectorAll(
              '[data-tower-drawer="'
              + action
              + '"]'
            );

          Array.prototype.forEach.call(
            drawers,
            function (drawer) {
              addSubmitButton(
                drawer,
                action,
                personId,
                receiptHost
              );
            }
          );

        });


        loadProfile(
          personId,
          room
        );


        document.documentElement.setAttribute(
          "data-tower-person-control-draft-wiring-status",
          "ready"
        );
      }


      if (
        document.readyState === "loading"
      ) {
        document.addEventListener(
          "DOMContentLoaded",
          installWiring
        );
      } else {
        installWiring();
      }

    })();
    </script>
    """


def inject_person_control_draft_wiring(
    html: str,
) -> str:
    source = str(
        html or ""
    )

    if (
        PERSON_CONTROL_DRAFT_WIRING_MARKER
        in source
    ):
        return source

    script = _person_control_wiring_script()

    if "</body>" in source:
        return source.replace(
            "</body>",
            script + "\n</body>",
            1,
        )

    return source + script


def _is_person_html_room(
    path: str,
) -> bool:
    prefix = (
        "/tower/owner-dashboard/person/"
    )

    if not path.startswith(prefix):
        return False

    remainder = path[
        len(prefix):
    ]

    return (
        bool(remainder)
        and "/" not in remainder
        and not remainder.endswith(
            ".json"
        )
    )


def register_tower_person_control_draft_wiring(
    app,
):
    marker = (
        "_tower_person_control_draft_wiring_"
        "twr051_055_registered"
    )

    if getattr(
        app,
        marker,
        False,
    ):
        return app


    # ------------------------------------------------------------------------------------------------
    # HTML enhancement
    # ------------------------------------------------------------------------------------------------

    @app.after_request
    def tower_person_control_draft_wiring_injector(
        response,
    ):
        if not _is_person_html_room(
            request.path
        ):
            return response

        if response.status_code != 200:
            return response

        if (
            "text/html"
            not in response.headers.get(
                "Content-Type",
                "",
            )
        ):
            return response

        html = response.get_data(
            as_text=True
        )

        html = inject_person_control_draft_wiring(
            html
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


    # ------------------------------------------------------------------------------------------------
    # TWR052 — PERSON CONTROL ROOM PAYLOAD
    # ------------------------------------------------------------------------------------------------

    @app.route(
        "/tower/owner-dashboard/person/<person_id>/control-room.json"
    )
    def tower_owner_person_control_room_json(
        person_id,
    ):
        if not owner_session_active():
            return redirect(
                "/tower/login"
            )

        payload = person_control_room_payload(
            person_id
        )

        status_code = (
            200
            if payload.get("status")
            == "tower_person_control_room_payload_ready"
            else 404
        )

        return jsonify(
            payload
        ), status_code


    # ------------------------------------------------------------------------------------------------
    # TWR053 — PERSON CONTROL DRAFT
    # ------------------------------------------------------------------------------------------------

    @app.route(
        "/tower/owner-dashboard/person/<person_id>/control-draft",
        methods=["POST"],
    )
    def tower_owner_person_control_draft(
        person_id,
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

        result = build_person_control_draft(
            person_id,
            incoming,
        )

        success = (
            result.get("status")
            == "person_control_draft_created"
        )

        if success:
            status_code = 200

        elif result.get("status") == "not_found":
            status_code = 404

        else:
            status_code = 400

        return jsonify(
            result
        ), status_code


    setattr(
        app,
        marker,
        True,
    )

    return app
