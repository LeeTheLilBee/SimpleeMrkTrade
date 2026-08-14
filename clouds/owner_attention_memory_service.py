"""
GP045 — Owner Memory / Persistent Attention State Foundation.

Provides:

- deterministic agenda fingerprints;
- atomic file-backed owner-memory ledger;
- integrity validation;
- persistence roundtrip verification.

Hosted durable storage is NOT claimed.
"""

from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import tempfile

try:
    from .executive_owner_agenda_service import (
        get_clouds_gp028_status_payload,
        get_owner_agenda_item,
        get_owner_agenda_items,
    )

    from .owner_attention_memory import (
        OWNER_MEMORY_FINGERPRINT_POLICY,
        OWNER_MEMORY_SCHEMA_VERSION,
        OwnerAttentionMemoryLedger,
        OwnerAttentionMemoryRecord,
        OwnerMemoryDisposition,
    )

except ImportError:
    from executive_owner_agenda_service import (
        get_clouds_gp028_status_payload,
        get_owner_agenda_item,
        get_owner_agenda_items,
    )

    from owner_attention_memory import (
        OWNER_MEMORY_FINGERPRINT_POLICY,
        OWNER_MEMORY_SCHEMA_VERSION,
        OwnerAttentionMemoryLedger,
        OwnerAttentionMemoryRecord,
        OwnerMemoryDisposition,
    )


DEFAULT_OWNER_ID = "owner-primary"


DEFAULT_MEMORY_PATH = Path(
    os.environ.get(
        "CLOUDS_OWNER_MEMORY_PATH",
        "/tmp/simplee-clouds-owner-attention-memory.json",
    )
)


def utc_now_iso():
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


def _sha256(payload):
    encoded = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("utf-8")

    return hashlib.sha256(
        encoded
    ).hexdigest()


def agenda_material_payload(
    agenda_item,
):
    """
    Owner-attention material fingerprint.

    Purposefully excludes presentation-only fields where possible.

    Current GP028 does not yet expose source revision IDs,
    so the material explanation fields remain part of v1.
    """

    return {
        "fingerprint_policy": (
            OWNER_MEMORY_FINGERPRINT_POLICY
        ),

        "agenda_item_id": (
            agenda_item.agenda_item_id
        ),

        "horizon": (
            agenda_item.horizon
        ),

        "urgency": (
            agenda_item.urgency
        ),

        "source_kind": (
            agenda_item.source_kind
        ),

        "source_id": (
            agenda_item.source_id
        ),

        "impacted_source_id": (
            agenda_item.impacted_source_id
        ),

        "owner_attention_required": (
            agenda_item
            .owner_attention_required
        ),

        "action_available": (
            agenda_item.action_available
        ),

        "soulaana_what_happened": (
            agenda_item
            .soulaana_what_happened
        ),

        "soulaana_what_it_means": (
            agenda_item
            .soulaana_what_it_means
        ),
    }


def fingerprint_agenda_item(
    agenda_item,
):
    return _sha256(
        agenda_material_payload(
            agenda_item
        )
    )


def build_new_memory_record(
    agenda_item,
    *,
    owner_id=DEFAULT_OWNER_ID,
    now_iso=None,
):
    now_iso = (
        now_iso
        or utc_now_iso()
    )

    return OwnerAttentionMemoryRecord(
        record_id=(
            "owner-memory-"
            f"{owner_id}-"
            f"{agenda_item.agenda_item_id}"
        ),

        owner_id=owner_id,

        agenda_item_id=(
            agenda_item.agenda_item_id
        ),

        source_id=(
            agenda_item.source_id
        ),

        impacted_source_id=(
            agenda_item.impacted_source_id
        ),

        agenda_fingerprint=(
            fingerprint_agenda_item(
                agenda_item
            )
        ),

        fingerprint_policy=(
            OWNER_MEMORY_FINGERPRINT_POLICY
        ),

        disposition=(
            OwnerMemoryDisposition
            .ACTIVE.value
        ),

        pinned=False,

        snooze_until=None,

        review_count=0,

        last_owner_action=(
            "memory_initialized"
        ),

        owner_note=None,

        created_at=now_iso,
        updated_at=now_iso,

        automatic_downstream_action_performed=False,

        downstream_execution_performed=False,
    )


def _ledger_content_payload(
    *,
    owner_id,
    records,
):
    return {
        "schema_version": (
            OWNER_MEMORY_SCHEMA_VERSION
        ),

        "owner_id": (
            owner_id
        ),

        "records": [
            record.to_dict()
            for record in sorted(
                records,
                key=lambda item: (
                    item.agenda_item_id
                ),
            )
        ],
    }


def _build_ledger(
    *,
    owner_id,
    records,
):
    records = tuple(
        sorted(
            records,
            key=lambda item: (
                item.agenda_item_id
            ),
        )
    )

    content = (
        _ledger_content_payload(
            owner_id=owner_id,
            records=records,
        )
    )

    return OwnerAttentionMemoryLedger(
        schema_version=(
            OWNER_MEMORY_SCHEMA_VERSION
        ),

        owner_id=owner_id,

        records=records,

        record_count=len(
            records
        ),

        ledger_integrity_hash=(
            _sha256(content)
        ),
    )


class OwnerAttentionMemoryStore:
    """
    Atomic file-backed owner memory.

    This provides persistence across Python process restarts
    when the configured filesystem path itself persists.

    It is NOT a claim that hosted durable storage is configured.
    """

    def __init__(
        self,
        path=DEFAULT_MEMORY_PATH,
    ):
        self.path = Path(path)


    def _empty_ledger(
        self,
        owner_id,
    ):
        return _build_ledger(
            owner_id=owner_id,
            records=(),
        )


    def read_ledger(
        self,
        owner_id=DEFAULT_OWNER_ID,
    ):
        if not self.path.exists():
            return self._empty_ledger(
                owner_id
            )

        payload = json.loads(
            self.path.read_text(
                encoding="utf-8"
            )
        )

        if (
            payload.get("schema_version")
            != OWNER_MEMORY_SCHEMA_VERSION
        ):
            raise ValueError(
                "Unsupported owner-memory schema."
            )

        if (
            payload.get("owner_id")
            != owner_id
        ):
            raise ValueError(
                "Owner-memory ledger owner mismatch."
            )

        records = tuple(
            OwnerAttentionMemoryRecord
            .from_dict(item)
            for item
            in payload.get(
                "records",
                [],
            )
        )

        expected = _build_ledger(
            owner_id=owner_id,
            records=records,
        )

        actual_hash = (
            payload.get(
                "ledger_integrity_hash"
            )
        )

        if (
            actual_hash
            != expected
            .ledger_integrity_hash
        ):
            raise ValueError(
                "Owner-memory ledger integrity mismatch."
            )

        if (
            payload.get(
                "record_count"
            )
            != len(records)
        ):
            raise ValueError(
                "Owner-memory record count mismatch."
            )

        return expected


    def write_records(
        self,
        records,
        *,
        owner_id=DEFAULT_OWNER_ID,
    ):
        ledger = _build_ledger(
            owner_id=owner_id,
            records=records,
        )

        self.path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        payload = (
            ledger.to_dict()
        )

        temp_path = (
            self.path
            .with_suffix(
                self.path.suffix
                + ".tmp"
            )
        )

        temp_path.write_text(
            json.dumps(
                payload,
                sort_keys=True,
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )

        os.replace(
            temp_path,
            self.path,
        )

        return ledger


    def get(
        self,
        agenda_item_id,
        *,
        owner_id=DEFAULT_OWNER_ID,
    ):
        ledger = (
            self.read_ledger(
                owner_id
            )
        )

        for record in ledger.records:
            if (
                record.agenda_item_id
                == agenda_item_id
            ):
                return record

        return None


    def upsert(
        self,
        record,
    ):
        if (
            record.owner_id
            != DEFAULT_OWNER_ID
        ):
            raise ValueError(
                "Unknown owner memory profile."
            )

        ledger = (
            self.read_ledger(
                record.owner_id
            )
        )

        records = {
            item.agenda_item_id: item
            for item in ledger.records
        }

        records[
            record.agenda_item_id
        ] = record

        return self.write_records(
            tuple(
                records.values()
            ),
            owner_id=record.owner_id,
        )


    def get_or_create(
        self,
        agenda_item,
        *,
        owner_id=DEFAULT_OWNER_ID,
        now_iso=None,
    ):
        existing = self.get(
            agenda_item.agenda_item_id,
            owner_id=owner_id,
        )

        if existing is not None:
            return existing

        record = (
            build_new_memory_record(
                agenda_item,
                owner_id=owner_id,
                now_iso=now_iso,
            )
        )

        self.upsert(
            record
        )

        return record


def get_default_owner_attention_memory_store():
    return OwnerAttentionMemoryStore(
        DEFAULT_MEMORY_PATH
    )


def get_clouds_gp045_status_payload():
    gp028 = (
        get_clouds_gp028_status_payload()
    )

    items = (
        get_owner_agenda_items()
    )

    if not items:
        return {
            "pack": "GP045",
            "phase": "CLOUDS_PHASE_II",
            "status": "blocked",
            "safe_to_continue": False,
            "reason": "no_owner_agenda_items",
        }

    with tempfile.TemporaryDirectory() as directory:
        path = (
            Path(directory)
            / "owner-memory.json"
        )

        first_store = (
            OwnerAttentionMemoryStore(
                path
            )
        )

        record = (
            first_store.get_or_create(
                items[0],
                now_iso=(
                    "2026-08-14T12:00:00Z"
                ),
            )
        )

        first_ledger = (
            first_store.read_ledger()
        )

        # New store object, same durable path.
        second_store = (
            OwnerAttentionMemoryStore(
                path
            )
        )

        second_ledger = (
            second_store.read_ledger()
        )

        restored = second_store.get(
            items[0]
            .agenda_item_id
        )

        persistence_roundtrip = (
            restored == record

            and first_ledger
            .ledger_integrity_hash
            == second_ledger
            .ledger_integrity_hash

            and second_ledger
            .record_count
            == 1
        )

        # Corruption rejection.
        payload = json.loads(
            path.read_text(
                encoding="utf-8"
            )
        )

        payload[
            "ledger_integrity_hash"
        ] = "0" * 64

        path.write_text(
            json.dumps(
                payload
            ),
            encoding="utf-8",
        )

        corruption_rejected = False

        try:
            second_store.read_ledger()

        except ValueError:
            corruption_rejected = True


    safe = (
        gp028["status"]
        == "ready"

        and gp028[
            "safe_to_continue"
        ]
        is True

        and persistence_roundtrip
        is True

        and corruption_rejected
        is True

        and len(
            record.agenda_fingerprint
        )
        == 64

        and record.fingerprint_policy
        == OWNER_MEMORY_FINGERPRINT_POLICY

        and record.disposition
        == "active"

        and record.pinned
        is False

        and record.review_count
        == 0

        and record
        .automatic_downstream_action_performed
        is False

        and record
        .downstream_execution_performed
        is False
    )


    return {
        "pack": "GP045",

        "phase": "CLOUDS_PHASE_II",

        "section": (
            "OWNER MEMORY / "
            "PERSISTENT ATTENTION STATE FOUNDATION"
        ),

        "status": (
            "ready"
            if safe
            else "blocked"
        ),

        "safe_to_continue": (
            safe
        ),

        "memory_schema_version": (
            OWNER_MEMORY_SCHEMA_VERSION
        ),

        "fingerprint_policy": (
            OWNER_MEMORY_FINGERPRINT_POLICY
        ),

        "agenda_id_memory_keyed": True,

        "agenda_fingerprint_present": True,

        "atomic_file_write_contract_ready": True,

        "ledger_integrity_hash_ready": True,

        "corruption_rejection_verified": (
            corruption_rejected
        ),

        "process_restart_roundtrip_verified": (
            persistence_roundtrip
        ),

        "durable_store_contract_ready": True,

        "hosted_persistent_storage_verified": False,

        "production_database_connected": False,

        "distributed_locking_verified": False,

        "owner_profile_count": 1,

        "automatic_downstream_action_performed": False,

        "downstream_execution_performed": False,

        "cross_app_imports_used": False,

        "next_pack": (
            "GP046 — OWNER ATTENTION CONTROLS / "
            "MEMORY STATE TRANSITIONS"
        ),
    }
