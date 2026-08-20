from __future__ import annotations

import hashlib
import json
import os
import secrets
import threading

from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from flask import jsonify, redirect, request

from tower.archive_vault_handoff import (
    ARCHIVE_HANDOFF_PATH,
)

from tower.owner_person_event_ledger import (
    append_person_event,
    build_person_event,
)

from tower.tower_human_login_ob_launch import (
    owner_session_active,
)


ARCHIVE_VAULT_INTAKE_MARKER = (
    "tower-archive-vault-intake-acceptance-twr076-080"
)


PROJECT_ROOT = (
    Path(__file__)
    .resolve()
    .parents[1]
)


ARCHIVE_VAULT_ACCEPTANCE_PATH = (
    PROJECT_ROOT
    / "tower"
    / "data"
    / "archive_vault_acceptance_records.jsonl"
)


ACCEPTANCE_LOCK = (
    threading.Lock()
)


EXPECTED_PACKET_TYPE = (
    "TOWER_PERSON_CHANGE_PROOF"
)


EXPECTED_PACKET_SCHEMA = (
    "tower.vault.person-change-proof.v1"
)


def _utc_now() -> str:

    return (
        datetime.now(
            timezone.utc
        )
        .isoformat()
        .replace(
            "+00:00",
            "Z",
        )
    )


def _canonical_json(
    value: Any,
) -> str:

    return json.dumps(
        value,
        sort_keys=True,
        separators=(
            ",",
            ":",
        ),
        ensure_ascii=False,
        default=str,
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


def _load_queue(
    path: Path | None = None,
) -> List[Dict[str, Any]]:

    target = (
        path
        or ARCHIVE_HANDOFF_PATH
    )


    if not target.exists():

        return []


    try:

        data = json.loads(
            target.read_text(
                encoding="utf-8"
            )
        )

    except Exception:

        return []


    if isinstance(
        data,
        list,
    ):

        return [
            item
            for item in data
            if isinstance(
                item,
                dict,
            )
        ]


    if (
        isinstance(
            data,
            dict,
        )
        and isinstance(
            data.get(
                "items"
            ),
            list,
        )
    ):

        return [
            item
            for item
            in data.get(
                "items",
                [],
            )
            if isinstance(
                item,
                dict,
            )
        ]


    return []


def archive_vault_intake_summary() -> Dict[str, Any]:

    return {

        "status": (
            "archive_vault_intake_acceptance_ready"
        ),

        "product_rule": (
            "queued_handoff_requires_vault_validation_before_acceptance_and_sealing"
        ),

        "accepted_packet_type": (
            EXPECTED_PACKET_TYPE
        ),

        "accepted_packet_schema": (
            EXPECTED_PACKET_SCHEMA
        ),

        "queue_state": (
            "VAULT_HANDOFF_QUEUED"
        ),

        "accepted_state": (
            "VAULT_ACCEPTED"
        ),

        "sealed_state": (
            "VAULT_SEALED"
        ),

        "duplicate_acceptance_blocked": True,

        "packet_integrity_validation": True,

        "tower_event_integrity_link_validation": True,

        "application_level_sealed_record": True,

        "external_hardened_archive_storage": False,

        "browser_direct_vault_access": False,

        "real_permission_changes": False,

        "live_auto": "LOCKED",

        "broker_execution": False,

        "capital_action": False,
    }


def find_queued_handoff(
    handoff_id: str,
    *,
    queue_path: Path | None = None,
) -> Dict[str, Any] | None:

    target_id = str(
        handoff_id
        or ""
    ).strip()


    if not target_id:

        return None


    for record in _load_queue(
        queue_path
    ):

        if (
            str(
                record.get(
                    "handoff_id",
                    "",
                )
            ).strip()
            == target_id
        ):

            return deepcopy(
                record
            )


    return None


def _acceptance_records(
    *,
    acceptance_path: Path | None = None,
) -> List[Dict[str, Any]]:

    target = (
        acceptance_path
        or ARCHIVE_VAULT_ACCEPTANCE_PATH
    )


    if not target.exists():

        return []


    records = []


    with target.open(
        "r",
        encoding="utf-8",
    ) as handle:

        for raw in handle:

            line = (
                raw.strip()
            )


            if not line:

                continue


            try:

                item = json.loads(
                    line
                )

            except Exception:

                continue


            if isinstance(
                item,
                dict,
            ):

                records.append(
                    item
                )


    return records


def acceptance_for_handoff(
    handoff_id: str,
    *,
    acceptance_path: Path | None = None,
) -> Dict[str, Any] | None:

    target = str(
        handoff_id
        or ""
    ).strip()


    for record in _acceptance_records(
        acceptance_path=(
            acceptance_path
        )
    ):

        if (
            record.get(
                "handoff_id"
            )
            == target
        ):

            return record


    return None


def _packet_from_handoff(
    handoff: Dict[str, Any],
) -> Dict[str, Any] | None:

    source_payload = (
        handoff.get(
            "source_payload"
        )
        or {}
    )


    if not isinstance(
        source_payload,
        dict,
    ):

        return None


    packet = (
        source_payload.get(
            "person_change_proof_packet"
        )
    )


    if not isinstance(
        packet,
        dict,
    ):

        return None


    return deepcopy(
        packet
    )


def validate_archive_vault_intake(
    handoff: Dict[str, Any],
) -> Dict[str, Any]:

    errors = []


    if not isinstance(
        handoff,
        dict,
    ):

        return {
            "status": (
                "archive_vault_intake_invalid"
            ),

            "accepted": False,

            "sealed": False,

            "errors": [
                "handoff_not_dictionary"
            ],
        }


    if (
        handoff.get(
            "status"
        )
        != "queued"
    ):

        errors.append(
            "handoff_not_queued"
        )


    if (
        handoff.get(
            "destination"
        )
        != "Archive Vault"
    ):

        errors.append(
            "destination_mismatch"
        )


    if (
        handoff.get(
            "source_type"
        )
        != "tower_person_change_proof"
    ):

        errors.append(
            "source_type_mismatch"
        )


    packet = (
        _packet_from_handoff(
            handoff
        )
    )


    if not packet:

        errors.append(
            "person_change_proof_packet_missing"
        )

        return {
            "status": (
                "archive_vault_intake_invalid"
            ),

            "accepted": False,

            "sealed": False,

            "errors": errors,

            "handoff_id": (
                handoff.get(
                    "handoff_id"
                )
            ),
        }


    if (
        packet.get(
            "packet_type"
        )
        != EXPECTED_PACKET_TYPE
    ):

        errors.append(
            "packet_type_mismatch"
        )


    if (
        packet.get(
            "schema_version"
        )
        != EXPECTED_PACKET_SCHEMA
    ):

        errors.append(
            "packet_schema_mismatch"
        )


    if (
        packet.get(
            "source_system"
        )
        != "TOWER"
    ):

        errors.append(
            "source_system_mismatch"
        )


    if (
        packet.get(
            "destination_system"
        )
        != "VAULT"
    ):

        errors.append(
            "destination_system_mismatch"
        )


    if (
        packet.get(
            "owner_decision"
        )
        != "APPROVED"
    ):

        errors.append(
            "owner_decision_not_approved"
        )


    if (
        packet.get(
            "archive_ready"
        )
        is not True
    ):

        errors.append(
            "archive_ready_false"
        )


    if (
        packet.get(
            "vault_status"
        )
        != "READY_FOR_VAULT"
    ):

        errors.append(
            "packet_not_ready_for_vault"
        )


    supplied_packet_hash = (
        packet.get(
            "packet_integrity_hash"
        )
    )


    packet_without_hash = {

        key: value

        for key, value
        in packet.items()

        if key
        != "packet_integrity_hash"
    }


    computed_packet_hash = (
        _sha256(
            packet_without_hash
        )
    )


    if (
        not supplied_packet_hash
        or supplied_packet_hash
        != computed_packet_hash
    ):

        errors.append(
            "packet_integrity_hash_mismatch"
        )


    related = (
        handoff.get(
            "related_object"
        )
        or {}
    )


    if isinstance(
        related,
        dict,
    ):

        related_packet_id = (
            related.get(
                "packet_id"
            )
        )


        if (
            related_packet_id
            and related_packet_id
            != packet.get(
                "packet_id"
            )
        ):

            errors.append(
                "related_packet_id_mismatch"
            )


        related_event_hash = (
            related.get(
                "tower_event_integrity_hash"
            )
        )


        packet_event_hash = (
            packet.get(
                "tower_event_integrity_hash"
            )
        )


        if (
            related_event_hash
            and packet_event_hash
            and related_event_hash
            != packet_event_hash
        ):

            errors.append(
                "tower_event_integrity_link_mismatch"
            )


    valid = (
        len(
            errors
        )
        == 0
    )


    return {

        "status": (
            "archive_vault_intake_valid"
            if valid
            else "archive_vault_intake_invalid"
        ),

        "accepted": False,

        "sealed": False,

        "handoff_id": (
            handoff.get(
                "handoff_id"
            )
        ),

        "packet_id": (
            packet.get(
                "packet_id"
            )
        ),

        "event_id": (
            packet.get(
                "event_id"
            )
        ),

        "person_id": (
            packet.get(
                "person_id"
            )
        ),

        "packet": packet,

        "computed_packet_integrity_hash": (
            computed_packet_hash
        ),

        "errors": errors,
    }


def _append_acceptance_record(
    record: Dict[str, Any],
    *,
    acceptance_path: Path | None = None,
) -> Dict[str, Any]:

    target = (
        acceptance_path
        or ARCHIVE_VAULT_ACCEPTANCE_PATH
    )


    target.parent.mkdir(
        parents=True,
        exist_ok=True,
    )


    serialized = (
        json.dumps(
            record,
            sort_keys=True,
            separators=(
                ",",
                ":",
            ),
            ensure_ascii=False,
            default=str,
        )
        + "\n"
    )


    with ACCEPTANCE_LOCK:

        with target.open(
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

        "status": (
            "archive_vault_acceptance_record_appended"
        ),

        "path": str(
            target
        ),

        "record_reference": (
            "archive-vault-record:"
            + record[
                "vault_acceptance_id"
            ]
        ),

        "appended": True,
    }


def accept_archive_vault_handoff(
    handoff_id: str,
    *,
    queue_path: Path | None = None,
    acceptance_path: Path | None = None,
) -> Dict[str, Any]:

    handoff = (
        find_queued_handoff(
            handoff_id,
            queue_path=(
                queue_path
            ),
        )
    )


    if not handoff:

        return {

            "status": (
                "archive_vault_handoff_not_found"
            ),

            "handoff_id": (
                handoff_id
            ),

            "accepted": False,

            "sealed": False,
        }


    existing = (
        acceptance_for_handoff(
            handoff_id,
            acceptance_path=(
                acceptance_path
            ),
        )
    )


    if existing:

        return {

            "status": (
                "archive_vault_handoff_already_accepted"
            ),

            "accepted": True,

            "sealed": True,

            "duplicate_acceptance_blocked": True,

            "acceptance_record": existing,

            "vault_receipt_id": (
                existing.get(
                    "vault_receipt_id"
                )
            ),

            "vault_record_reference": (
                existing.get(
                    "vault_record_reference"
                )
            ),
        }


    validation = (
        validate_archive_vault_intake(
            handoff
        )
    )


    if (
        validation.get(
            "status"
        )
        != "archive_vault_intake_valid"
    ):

        return {

            "status": (
                "archive_vault_handoff_rejected"
            ),

            "accepted": False,

            "sealed": False,

            "validation": (
                validation
            ),
        }


    packet = (
        validation[
            "packet"
        ]
    )


    acceptance_id = (
        "vaultaccept_"
        + secrets.token_urlsafe(
            18
        )
    )


    receipt_id = (
        "vaultreceipt_"
        + secrets.token_urlsafe(
            18
        )
    )


    accepted_at = (
        _utc_now()
    )


    acceptance_record = {

        "schema_version": (
            "archive.vault.acceptance.v1"
        ),

        "vault_acceptance_id": (
            acceptance_id
        ),

        "vault_receipt_id": (
            receipt_id
        ),

        "vault_record_reference": (
            "archive-vault-record:"
            + acceptance_id
        ),

        "handoff_id": (
            handoff[
                "handoff_id"
            ]
        ),

        "source_type": (
            handoff[
                "source_type"
            ]
        ),

        "packet_id": (
            packet[
                "packet_id"
            ]
        ),

        "packet_type": (
            packet[
                "packet_type"
            ]
        ),

        "event_id": (
            packet[
                "event_id"
            ]
        ),

        "person_id": (
            packet[
                "person_id"
            ]
        ),

        "display_name": (
            packet.get(
                "display_name"
            )
        ),

        "accepted_at_utc": (
            accepted_at
        ),

        "vault_status": (
            "VAULT_SEALED"
        ),

        "accepted": True,

        "sealed": True,

        "packet_integrity_hash": (
            packet[
                "packet_integrity_hash"
            ]
        ),

        "tower_event_integrity_hash": (
            packet.get(
                "tower_event_integrity_hash"
            )
        ),

        "source_handoff_snapshot": (
            deepcopy(
                handoff
            )
        ),

        "person_change_proof_packet": (
            deepcopy(
                packet
            )
        ),

        "application_level_sealed_record": True,

        "external_hardened_archive_storage": False,
    }


    acceptance_record[
        "vault_acceptance_integrity_hash"
    ] = _sha256({

        key: value

        for key, value
        in acceptance_record.items()

        if key
        != "vault_acceptance_integrity_hash"
    })


    appended = (
        _append_acceptance_record(

            acceptance_record,

            acceptance_path=(
                acceptance_path
            ),
        )
    )


    if not appended.get(
        "appended"
    ):

        return {

            "status": (
                "archive_vault_acceptance_write_failed"
            ),

            "accepted": False,

            "sealed": False,
        }


    return {

        "status": (
            "archive_vault_handoff_accepted"
        ),

        "accepted": True,

        "sealed": True,

        "vault_status": (
            "VAULT_SEALED"
        ),

        "handoff_id": (
            handoff[
                "handoff_id"
            ]
        ),

        "packet_id": (
            packet[
                "packet_id"
            ]
        ),

        "event_id": (
            packet[
                "event_id"
            ]
        ),

        "person_id": (
            packet[
                "person_id"
            ]
        ),

        "vault_acceptance_id": (
            acceptance_id
        ),

        "vault_receipt_id": (
            receipt_id
        ),

        "vault_record_reference": (
            appended[
                "record_reference"
            ]
        ),

        "acceptance_record": (
            acceptance_record
        ),

        "receipt": {

            "receipt_type": (
                "archive_vault_acceptance_receipt"
            ),

            "vault_receipt_id": (
                receipt_id
            ),

            "handoff_id": (
                handoff[
                    "handoff_id"
                ]
            ),

            "packet_id": (
                packet[
                    "packet_id"
                ]
            ),

            "person_id": (
                packet[
                    "person_id"
                ]
            ),

            "event_id": (
                packet[
                    "event_id"
                ]
            ),

            "accepted_at_utc": (
                accepted_at
            ),

            "vault_status": (
                "VAULT_SEALED"
            ),

            "vault_record_reference": (
                appended[
                    "record_reference"
                ]
            ),

            "vault_acceptance_integrity_hash": (
                acceptance_record[
                    "vault_acceptance_integrity_hash"
                ]
            ),
        },

        "storage_boundary": {

            "application_level_sealed_record": True,

            "external_hardened_archive_storage": False,
        },
    }


def record_person_vault_acceptance(
    acceptance_result: Dict[str, Any],
) -> Dict[str, Any]:

    if (
        acceptance_result.get(
            "status"
        )
        != "archive_vault_handoff_accepted"
    ):

        return {

            "status": (
                "person_vault_acceptance_not_recorded"
            ),

            "reason": (
                "vault_acceptance_required"
            ),
        }


    receipt = (
        acceptance_result[
            "receipt"
        ]
    )


    built = (
        build_person_event(

            acceptance_result[
                "person_id"
            ],

            event_type=(
                "PERSON_ARCHIVE_VAULT_ACCEPTED"
            ),

            action=(
                "archive_vault_acceptance"
            ),

            before_state={

                "source_event_id": (
                    acceptance_result[
                        "event_id"
                    ]
                ),

                "handoff_id": (
                    acceptance_result[
                        "handoff_id"
                    ]
                ),

                "vault_status": (
                    "VAULT_HANDOFF_QUEUED"
                ),
            },

            requested_state={

                "vault_acceptance": True,

                "packet_id": (
                    acceptance_result[
                        "packet_id"
                    ]
                ),
            },

            resulting_state={

                "vault_status": (
                    "VAULT_SEALED"
                ),

                "vault_acceptance_id": (
                    acceptance_result[
                        "vault_acceptance_id"
                    ]
                ),

                "vault_receipt_id": (
                    acceptance_result[
                        "vault_receipt_id"
                    ]
                ),

                "vault_record_reference": (
                    acceptance_result[
                        "vault_record_reference"
                    ]
                ),

                "vault_acceptance_integrity_hash": (
                    receipt[
                        "vault_acceptance_integrity_hash"
                    ]
                ),
            },

            reason=(
                "Archive Vault accepted and sealed "
                "the queued Tower person proof."
            ),

            owner_review_status=(
                "APPROVED"
            ),

            tower_validation={

                "vault_acceptance_verified": True,

                "vault_sealing_verified": True,

                "vault_receipt_present": True,

                "application_level_sealed_record": True,

                "external_hardened_archive_storage": False,
            },

            related_receipt_ids=[

                acceptance_result[
                    "vault_receipt_id"
                ],

                acceptance_result[
                    "handoff_id"
                ],

                acceptance_result[
                    "event_id"
                ],
            ],

            source=(
                "ARCHIVE_VAULT_INTAKE"
            ),
        )
    )


    if (
        built.get(
            "status"
        )
        != "person_event_built"
    ):

        return built


    appended = (
        append_person_event(
            built[
                "event"
            ]
        )
    )


    return {

        "status": (
            "person_vault_acceptance_recorded"
            if appended.get(
                "appended"
            )
            else "person_vault_acceptance_append_failed"
        ),

        "event": (
            built[
                "event"
            ]
        ),

        "append_result": (
            appended
        ),
    }


def accept_and_record_archive_vault_handoff(
    handoff_id: str,
) -> Dict[str, Any]:

    accepted = (
        accept_archive_vault_handoff(
            handoff_id
        )
    )


    if (
        accepted.get(
            "status"
        )
        == "archive_vault_handoff_already_accepted"
    ):

        return accepted


    if (
        accepted.get(
            "status"
        )
        != "archive_vault_handoff_accepted"
    ):

        return accepted


    person_history = (
        record_person_vault_acceptance(
            accepted
        )
    )


    return {

        **accepted,

        "person_history_result": (
            person_history
        ),
    }


def archive_vault_acceptance_payload() -> Dict[str, Any]:

    records = (
        _acceptance_records()
    )


    return {

        "status": (
            "archive_vault_acceptance_records_ready"
        ),

        "total": len(
            records
        ),

        "recent": (
            records[
                -25:
            ]
        ),

        "application_level_sealed_records": True,

        "external_hardened_archive_storage": False,
    }


def register_archive_vault_intake_acceptance(
    app,
):

    marker = (
        "_archive_vault_intake_acceptance_"
        "twr076_080_registered"
    )


    if getattr(
        app,
        marker,
        False,
    ):

        return app


    @app.route(
        "/tower/archive-vault/intake/<handoff_id>",
        methods=[
            "POST",
        ],
    )
    def tower_archive_vault_intake_post(
        handoff_id,
    ):

        if not owner_session_active():

            return redirect(
                "/tower/login"
            )


        result = (
            accept_and_record_archive_vault_handoff(
                handoff_id
            )
        )


        status = (
            result.get(
                "status"
            )
        )


        if status in {

            "archive_vault_handoff_accepted",

            "archive_vault_handoff_already_accepted",

        }:

            code = 200


        elif (
            status
            == "archive_vault_handoff_not_found"
        ):

            code = 404


        else:

            code = 400


        return jsonify(
            result
        ), code


    @app.route(
        "/tower/archive-vault/acceptance-records.json"
    )
    def tower_archive_vault_acceptance_records_json():

        if not owner_session_active():

            return redirect(
                "/tower/login"
            )


        return jsonify(
            archive_vault_acceptance_payload()
        )


    setattr(
        app,
        marker,
        True,
    )


    return app
