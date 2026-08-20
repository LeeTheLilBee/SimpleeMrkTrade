from __future__ import annotations

import hashlib
import json
import os
import threading
import uuid

from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List

from flask import jsonify, redirect, request

from tower.owner_people_profile_rooms import (
    people_profile_by_id,
)

from tower.owner_person_control_draft_wiring import (
    build_person_control_draft,
)

from tower.tower_human_login_ob_launch import (
    owner_session_active,
)


PERSON_EVENT_LEDGER_MARKER = (
    "tower-person-event-ledger-vault-ready-twr056-060"
)


PERSON_EVENT_SCHEMA_VERSION = (
    "tower.person.event.v1"
)


VAULT_PACKET_SCHEMA_VERSION = (
    "tower.vault.person-change-proof.v1"
)


VAULT_PACKET_TYPE = (
    "TOWER_PERSON_CHANGE_PROOF"
)


VAULT_STATUSES = (
    "NOT_READY_FOR_VAULT",
    "READY_FOR_VAULT",
    "VAULT_DELIVERY_FAILED",
    "VAULT_SEALED",
)


LEDGER_LOCK = threading.Lock()


def _utc_now() -> str:
    return datetime.now(
        timezone.utc
    ).isoformat()


def _runtime_ledger_path() -> Path:
    configured = str(
        os.environ.get(
            "TOWER_PERSON_EVENT_LEDGER_PATH",
            "",
        )
        or ""
    ).strip()

    if configured:
        return Path(
            configured
        )

    repo_root = Path(
        __file__
    ).resolve().parents[1]

    return (
        repo_root
        / "runtime"
        / "tower"
        / "person_event_ledger.jsonl"
    )


def person_event_ledger_summary() -> Dict[str, Any]:
    return {
        "status": "tower_person_event_ledger_ready",
        "product_rule": (
            "tower_keeps_operational_person_history_vault_remains_sealed_archive"
        ),
        "event_schema_version": PERSON_EVENT_SCHEMA_VERSION,
        "vault_packet_schema_version": VAULT_PACKET_SCHEMA_VERSION,
        "vault_packet_type": VAULT_PACKET_TYPE,
        "vault_statuses": list(
            VAULT_STATUSES
        ),
        "append_only_store": True,
        "local_file_backing": True,
        "production_archival_durability": False,
        "vault_required_for_sealed_archive": True,
        "vault_delivery_enabled": False,
        "browser_direct_vault_access": False,
        "real_permission_changes": False,
        "real_access_granted": False,
        "real_access_revoked": False,
        "real_person_frozen": False,
        "real_person_restored": False,
        "live_auto": "LOCKED",
        "broker_execution": False,
        "capital_action": False,
    }


def _canonical_json(
    value: Any,
) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )


def _sha256(
    value: Any,
) -> str:
    return hashlib.sha256(
        _canonical_json(
            value
        ).encode(
            "utf-8"
        )
    ).hexdigest()


def _safe_dict(
    value: Any,
) -> Dict[str, Any]:
    if isinstance(
        value,
        dict,
    ):
        return deepcopy(
            value
        )

    return {}


def build_person_event(
    person_id: str,
    *,
    event_type: str,
    action: str,
    before_state: Dict[str, Any] | None = None,
    requested_state: Dict[str, Any] | None = None,
    resulting_state: Dict[str, Any] | None = None,
    reason: str = "",
    owner_review_status: str = "PENDING_OWNER_REVIEW",
    tower_validation: Dict[str, Any] | None = None,
    related_receipt_ids: Iterable[str] | None = None,
    source: str = "TOWER_PERSON_CONTROL_ROOM",
) -> Dict[str, Any]:

    profile = people_profile_by_id(
        person_id
    )

    if not profile:
        return {
            "status": "not_found",
            "person_id": person_id,
            "real_permission_changes": False,
        }

    event_id = (
        "per-evt-"
        + uuid.uuid4().hex
    )

    event = {
        "schema_version": PERSON_EVENT_SCHEMA_VERSION,
        "event_id": event_id,
        "person_id": profile[
            "person_id"
        ],
        "display_name": profile[
            "display_name"
        ],
        "event_type": str(
            event_type or ""
        ).strip(),
        "action": str(
            action or ""
        ).strip(),
        "before_state": _safe_dict(
            before_state
        ),
        "requested_state": _safe_dict(
            requested_state
        ),
        "resulting_state": _safe_dict(
            resulting_state
        ),
        "reason": str(
            reason or ""
        ).strip(),
        "source": str(
            source or "TOWER_PERSON_CONTROL_ROOM"
        ).strip(),
        "created_at_utc": _utc_now(),
        "owner_review_status": str(
            owner_review_status
            or "PENDING_OWNER_REVIEW"
        ).strip(),
        "tower_validation": _safe_dict(
            tower_validation
        ),
        "related_receipt_ids": [
            str(item)
            for item in (
                related_receipt_ids
                or []
            )
            if str(item).strip()
        ],
        "vault_status": "NOT_READY_FOR_VAULT",
        "vault_packet_id": None,
        "vault_record_reference": None,
        "real_permission_changes": False,
        "real_access_granted": False,
        "real_access_revoked": False,
        "real_person_frozen": False,
        "real_person_restored": False,
    }

    event["integrity_hash"] = _sha256(
        {
            key: value
            for key, value in event.items()
            if key != "integrity_hash"
        }
    )

    return {
        "status": "person_event_built",
        "event": event,
    }


def append_person_event(
    event: Dict[str, Any],
    *,
    ledger_path: Path | None = None,
) -> Dict[str, Any]:

    record = deepcopy(
        event
    )

    if (
        record.get(
            "schema_version"
        )
        != PERSON_EVENT_SCHEMA_VERSION
    ):
        return {
            "status": "invalid_person_event",
            "reason": "schema_version_mismatch",
            "appended": False,
        }

    required = (
        "event_id",
        "person_id",
        "display_name",
        "event_type",
        "action",
        "created_at_utc",
        "integrity_hash",
    )

    missing = [
        field
        for field in required
        if not record.get(
            field
        )
    ]

    if missing:
        return {
            "status": "invalid_person_event",
            "reason": "missing_required_fields",
            "missing_fields": missing,
            "appended": False,
        }

    path = (
        ledger_path
        or _runtime_ledger_path()
    )

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    serialized = (
        _canonical_json(
            record
        )
        + "\n"
    )

    with LEDGER_LOCK:
        with path.open(
            "a",
            encoding="utf-8",
        ) as handle:
            handle.write(
                serialized
            )
            handle.flush()

            try:
                os.fsync(
                    handle.fileno()
                )
            except OSError:
                pass

    return {
        "status": "person_event_appended",
        "event_id": record[
            "event_id"
        ],
        "person_id": record[
            "person_id"
        ],
        "ledger_path": str(
            path
        ),
        "append_only": True,
        "production_archival_durability": False,
        "vault_required_for_sealed_archive": True,
        "appended": True,
    }


def read_person_events(
    person_id: str,
    *,
    ledger_path: Path | None = None,
) -> List[Dict[str, Any]]:

    normalized = str(
        person_id or ""
    ).strip().lower()

    path = (
        ledger_path
        or _runtime_ledger_path()
    )

    if not path.exists():
        return []

    records: List[
        Dict[str, Any]
    ] = []

    with LEDGER_LOCK:
        with path.open(
            "r",
            encoding="utf-8",
        ) as handle:
            for raw_line in handle:
                line = raw_line.strip()

                if not line:
                    continue

                try:
                    item = json.loads(
                        line
                    )
                except json.JSONDecodeError:
                    continue

                if str(
                    item.get(
                        "person_id",
                        "",
                    )
                ).strip().lower() == normalized:
                    records.append(
                        item
                    )

    records.sort(
        key=lambda item: str(
            item.get(
                "created_at_utc",
                "",
            )
        )
    )

    return records


def read_event_by_id(
    event_id: str,
    *,
    ledger_path: Path | None = None,
) -> Dict[str, Any] | None:

    target = str(
        event_id or ""
    ).strip()

    path = (
        ledger_path
        or _runtime_ledger_path()
    )

    if not target or not path.exists():
        return None

    with LEDGER_LOCK:
        with path.open(
            "r",
            encoding="utf-8",
        ) as handle:
            for raw_line in handle:
                line = raw_line.strip()

                if not line:
                    continue

                try:
                    item = json.loads(
                        line
                    )
                except json.JSONDecodeError:
                    continue

                if item.get(
                    "event_id"
                ) == target:
                    return item

    return None


def _requested_state_from_control_result(
    control_result: Dict[str, Any],
) -> Dict[str, Any]:

    action = control_result.get(
        "control_action"
    )

    draft = _safe_dict(
        control_result.get(
            "draft"
        )
    )

    if action == "designation":
        return {
            "designation": draft.get(
                "requested_designation"
            )
        }

    if action == "app_access":
        return {
            "app_name": draft.get(
                "app_name"
            ),
            "access_level": draft.get(
                "requested_access_level"
            ),
        }

    if action == "responsibility":
        return {
            "responsibilities": draft.get(
                "responsibilities"
            )
        }

    if action == "status":
        return {
            "status": draft.get(
                "requested_status"
            )
        }

    if action == "freeze":
        return {
            "freeze_requested": True,
            "reason": draft.get(
                "reason"
            ),
        }

    if action == "restore":
        return {
            "restore_requested": True,
            "reason": draft.get(
                "reason"
            ),
        }

    if action == "paperwork_note":
        return {
            "paperwork_note": draft.get(
                "paperwork_note"
            )
        }

    return {}


def build_event_from_control_draft(
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
        }

    control_result = build_person_control_draft(
        person_id,
        payload,
    )

    if (
        control_result.get(
            "status"
        )
        != "person_control_draft_created"
    ):
        return {
            "status": "person_control_event_not_created",
            "control_result": control_result,
            "real_permission_changes": False,
        }

    action = control_result[
        "control_action"
    ]

    receipt = _safe_dict(
        control_result.get(
            "receipt"
        )
    )

    queue_item = _safe_dict(
        control_result.get(
            "queue_item"
        )
    )

    receipt_id = (
        "draft-receipt-"
        + uuid.uuid4().hex
    )

    before_state = {
        "designation": profile.get(
            "designation"
        ),
        "status": profile.get(
            "status"
        ),
        "assigned_scope": profile.get(
            "assigned_scope"
        ),
        "access_summary": profile.get(
            "access_summary"
        ),
    }

    requested_state = (
        _requested_state_from_control_result(
            control_result
        )
    )

    reason = str(
        payload.get(
            "notes",
            "",
        )
        or payload.get(
            "reason",
            "",
        )
        or ""
    ).strip()

    built = build_person_event(
        person_id,
        event_type="PERSON_CONTROL_DRAFT",
        action=action,
        before_state=before_state,
        requested_state=requested_state,
        resulting_state={},
        reason=reason,
        owner_review_status="PENDING_OWNER_REVIEW",
        tower_validation={
            "control_result_status": control_result.get(
                "status"
            ),
            "draft_status": _safe_dict(
                control_result.get(
                    "draft"
                )
            ).get(
                "status"
            ),
            "queue_item_status": queue_item.get(
                "status"
            ),
            "draft_receipt": receipt,
        },
        related_receipt_ids=[
            receipt_id,
            str(
                queue_item.get(
                    "queue_id",
                    "",
                )
                or ""
            ),
        ],
    )

    if (
        built.get(
            "status"
        )
        != "person_event_built"
    ):
        return built

    append_result = append_person_event(
        built[
            "event"
        ]
    )

    if not append_result.get(
        "appended"
    ):
        return {
            "status": "person_control_event_append_failed",
            "control_result": control_result,
            "append_result": append_result,
            "real_permission_changes": False,
        }

    return {
        "status": "person_control_event_recorded",
        "control_result": control_result,
        "event": built[
            "event"
        ],
        "append_result": append_result,
        "receipt": {
            "receipt_id": receipt_id,
            "receipt_type": "tower_person_event_recorded",
            "event_id": built[
                "event"
            ][
                "event_id"
            ],
            "person_id": profile[
                "person_id"
            ],
            "vault_status": "NOT_READY_FOR_VAULT",
            "production_archival_durability": False,
            "message": (
                "Tower recorded the event locally. "
                "Vault sealing is still required for permanent archive."
            ),
        },
        "safety": {
            "real_permission_changes": False,
            "real_access_granted": False,
            "real_access_revoked": False,
            "real_person_frozen": False,
            "real_person_restored": False,
            "live_auto": "LOCKED",
            "broker_execution": False,
            "capital_action": False,
        },
    }


def build_vault_ready_person_packet(
    event: Dict[str, Any],
    *,
    owner_decision: str | None = None,
    decision_reason: str = "",
    decision_receipt_id: str | None = None,
) -> Dict[str, Any]:

    if (
        event.get(
            "schema_version"
        )
        != PERSON_EVENT_SCHEMA_VERSION
    ):
        return {
            "status": "invalid_event_for_vault_packet",
            "vault_delivery_performed": False,
        }

    decision = str(
        owner_decision or ""
    ).strip().upper()

    archive_ready = (
        decision == "APPROVED"
    )

    packet_id = (
        "vlt-pkt-person-"
        + uuid.uuid4().hex
    )

    packet = {
        "schema_version": VAULT_PACKET_SCHEMA_VERSION,
        "packet_id": packet_id,
        "packet_type": VAULT_PACKET_TYPE,
        "source_system": "TOWER",
        "destination_system": "VAULT",
        "person_id": event[
            "person_id"
        ],
        "display_name": event[
            "display_name"
        ],
        "event_id": event[
            "event_id"
        ],
        "event_type": event[
            "event_type"
        ],
        "action": event[
            "action"
        ],
        "before_state": deepcopy(
            event.get(
                "before_state",
                {},
            )
        ),
        "requested_state": deepcopy(
            event.get(
                "requested_state",
                {},
            )
        ),
        "resulting_state": deepcopy(
            event.get(
                "resulting_state",
                {},
            )
        ),
        "reason": event.get(
            "reason",
            "",
        ),
        "owner_decision": decision or None,
        "decision_reason": str(
            decision_reason or ""
        ).strip(),
        "decision_receipt_id": (
            decision_receipt_id
        ),
        "tower_event_integrity_hash": event.get(
            "integrity_hash"
        ),
        "tower_validation": deepcopy(
            event.get(
                "tower_validation",
                {},
            )
        ),
        "related_receipt_ids": list(
            event.get(
                "related_receipt_ids",
                [],
            )
        ),
        "created_at_utc": event.get(
            "created_at_utc"
        ),
        "packet_created_at_utc": _utc_now(),
        "archive_ready": archive_ready,
        "vault_status": (
            "READY_FOR_VAULT"
            if archive_ready
            else "NOT_READY_FOR_VAULT"
        ),
        "vault_delivery_performed": False,
        "vault_acceptance_receipt": None,
    }

    packet[
        "packet_integrity_hash"
    ] = _sha256(
        {
            key: value
            for key, value in packet.items()
            if key != "packet_integrity_hash"
        }
    )

    return {
        "status": (
            "vault_person_packet_ready"
            if archive_ready
            else "vault_person_packet_not_ready"
        ),
        "packet": packet,
        "vault_delivery_performed": False,
        "browser_direct_vault_access": False,
    }


def person_history_payload(
    person_id: str,
) -> Dict[str, Any]:

    profile = people_profile_by_id(
        person_id
    )

    if not profile:
        return {
            "status": "not_found",
            "person_id": person_id,
        }

    events = read_person_events(
        profile[
            "person_id"
        ]
    )

    return {
        "status": "tower_person_history_ready",
        "profile": profile,
        "events": events,
        "event_count": len(
            events
        ),
        "vault_summary": {
            "not_ready": len(
                [
                    item
                    for item in events
                    if item.get(
                        "vault_status"
                    )
                    == "NOT_READY_FOR_VAULT"
                ]
            ),
            "ready": len(
                [
                    item
                    for item in events
                    if item.get(
                        "vault_status"
                    )
                    == "READY_FOR_VAULT"
                ]
            ),
            "sealed": len(
                [
                    item
                    for item in events
                    if item.get(
                        "vault_status"
                    )
                    == "VAULT_SEALED"
                ]
            ),
        },
        "storage_boundary": {
            "tower_local_append_only": True,
            "production_archival_durability": False,
            "vault_required_for_sealed_archive": True,
            "vault_delivery_enabled": False,
        },
    }


def _history_ui_script() -> str:
    return """
    <script id="tower-person-event-ledger-vault-ready-twr056-060">
    (function () {

      function personIdFromPath() {
        var match = window.location.pathname.match(
          /^\\/tower\\/owner-dashboard\\/person\\/([^/]+)$/
        );

        return match
          ? decodeURIComponent(match[1])
          : "";
      }


      function escapeHtml(value) {
        return String(value == null ? "" : value)
          .replace(/&/g, "&amp;")
          .replace(/</g, "&lt;")
          .replace(/>/g, "&gt;")
          .replace(/"/g, "&quot;")
          .replace(/'/g, "&#039;");
      }


      function ensureHistoryPanel(room) {
        var existing = room.querySelector(
          "[data-tower-person-history-panel='true']"
        );

        if (existing) {
          return existing;
        }

        var panel = document.createElement(
          "section"
        );

        panel.setAttribute(
          "data-tower-person-history-panel",
          "true"
        );

        panel.className =
          "tower-person-control-card";

        panel.innerHTML = [
          "<h3>Person history + Vault archive</h3>",
          "<p>Loading Tower person-event history…</p>"
        ].join("");

        room.appendChild(
          panel
        );

        return panel;
      }


      function renderHistory(
        panel,
        payload
      ) {
        var events = payload.events || [];

        var html = [
          "<h3>Person history + Vault archive</h3>",
          "<p><strong>"
            + events.length
            + "</strong> Tower event(s) recorded.</p>"
        ];


        if (!events.length) {
          html.push(
            "<p>No person-control events have been recorded yet.</p>"
          );
        }


        events
          .slice()
          .reverse()
          .forEach(function (event) {

            var status =
              event.vault_status
              || "NOT_READY_FOR_VAULT";

            html.push(
              [
                "<div style='margin-top:10px;padding:10px;border-radius:14px;",
                "border:1px solid rgba(255,255,255,.10);",
                "background:rgba(255,255,255,.045)'>",

                "<strong style='color:#f8d978'>",
                escapeHtml(event.action),
                "</strong>",

                "<p style='margin:5px 0'>",
                escapeHtml(event.event_type),
                " · ",
                escapeHtml(event.created_at_utc),
                "</p>",

                "<p style='margin:5px 0'>Owner review: ",
                escapeHtml(event.owner_review_status),
                "</p>",

                "<p style='margin:5px 0'>Vault: <strong>",
                escapeHtml(status),
                "</strong></p>",

                "<small>",
                escapeHtml(event.event_id),
                "</small>",

                "</div>"
              ].join("")
            );
          });


        html.push(
          [
            "<p class='tower-person-safety-note' style='margin-top:10px'>",
            "Tower keeps operational event history here. ",
            "Vault remains the permanent sealed archive. ",
            "No browser-to-Vault delivery occurs from this room.",
            "</p>"
          ].join("")
        );


        panel.innerHTML =
          html.join("");
      }


      async function loadHistory(
        personId,
        panel
      ) {
        try {
          var response = await fetch(
            "/tower/owner-dashboard/person/"
              + encodeURIComponent(personId)
              + "/history.json"
          );

          var payload = await response.json();

          if (!response.ok) {
            panel.innerHTML =
              "<h3>Person history + Vault archive</h3>"
              + "<p>History unavailable.</p>";

            return;
          }

          renderHistory(
            panel,
            payload
          );

          document.documentElement.setAttribute(
            "data-tower-person-history-status",
            "loaded"
          );

        } catch (error) {
          panel.innerHTML =
            "<h3>Person history + Vault archive</h3>"
            + "<p>History load failed.</p>";

          document.documentElement.setAttribute(
            "data-tower-person-history-status",
            "load-error"
          );
        }
      }


      function installHistory() {
        var personId = personIdFromPath();

        if (!personId) {
          return;
        }

        var room = document.querySelector(
          "[data-tower-person-control-room='true']"
        );

        if (!room) {
          window.setTimeout(
            installHistory,
            50
          );

          return;
        }

        if (
          room.getAttribute(
            "data-tower-person-event-ledger"
          )
          === "true"
        ) {
          return;
        }

        room.setAttribute(
          "data-tower-person-event-ledger",
          "true"
        );

        var panel = ensureHistoryPanel(
          room
        );

        loadHistory(
          personId,
          panel
        );

        document.documentElement.setAttribute(
          "data-tower-person-event-ledger-status",
          "ready"
        );
      }


      if (
        document.readyState === "loading"
      ) {
        document.addEventListener(
          "DOMContentLoaded",
          installHistory
        );
      } else {
        installHistory();
      }

    })();
    </script>
    """


def inject_person_event_ledger_ui(
    html: str,
) -> str:

    source = str(
        html or ""
    )

    if (
        PERSON_EVENT_LEDGER_MARKER
        in source
    ):
        return source

    script = _history_ui_script()

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

    if not path.startswith(
        prefix
    ):
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


def register_tower_person_event_ledger(
    app,
):
    marker = (
        "_tower_person_event_ledger_"
        "twr056_060_registered"
    )

    if getattr(
        app,
        marker,
        False,
    ):
        return app


    @app.after_request
    def tower_person_event_ledger_ui_injector(
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

        html = inject_person_event_ledger_ui(
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
    # TWR058 — HISTORY
    # ------------------------------------------------------------------------------------------------

    @app.route(
        "/tower/owner-dashboard/person/<person_id>/history.json"
    )
    def tower_owner_person_history_json(
        person_id,
    ):
        if not owner_session_active():
            return redirect(
                "/tower/login"
            )

        payload = person_history_payload(
            person_id
        )

        status_code = (
            200
            if payload.get(
                "status"
            )
            == "tower_person_history_ready"
            else 404
        )

        return jsonify(
            payload
        ), status_code


    # ------------------------------------------------------------------------------------------------
    # TWR058 — APPEND PERSON EVENT FROM CONTROL DRAFT
    # ------------------------------------------------------------------------------------------------

    @app.route(
        "/tower/owner-dashboard/person/<person_id>/event",
        methods=["POST"],
    )
    def tower_owner_person_event_post(
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

        result = build_event_from_control_draft(
            person_id,
            incoming,
        )

        success = (
            result.get(
                "status"
            )
            == "person_control_event_recorded"
        )

        if success:
            status_code = 200

        elif result.get(
            "status"
        ) == "not_found":
            status_code = 404

        else:
            status_code = 400

        return jsonify(
            result
        ), status_code


    # ------------------------------------------------------------------------------------------------
    # TWR059 — VAULT-READY PACKET PREVIEW
    #
    # NO DELIVERY.
    # ------------------------------------------------------------------------------------------------

    @app.route(
        "/tower/owner-dashboard/person/<person_id>/event/<event_id>/vault-packet.json",
        methods=["POST"],
    )
    def tower_owner_person_vault_packet_preview(
        person_id,
        event_id,
    ):
        if not owner_session_active():
            return redirect(
                "/tower/login"
            )

        event = read_event_by_id(
            event_id
        )

        if (
            not event
            or event.get(
                "person_id"
            )
            != person_id
        ):
            return jsonify(
                {
                    "status": "not_found",
                    "person_id": person_id,
                    "event_id": event_id,
                    "vault_delivery_performed": False,
                }
            ), 404

        incoming = (
            request.get_json(
                silent=True
            )
            or request.form
            or {}
        )

        result = build_vault_ready_person_packet(
            event,
            owner_decision=incoming.get(
                "owner_decision"
            ),
            decision_reason=str(
                incoming.get(
                    "decision_reason",
                    "",
                )
                or ""
            ),
            decision_receipt_id=incoming.get(
                "decision_receipt_id"
            ),
        )

        return jsonify(
            result
        ), 200


    setattr(
        app,
        marker,
        True,
    )

    return app
