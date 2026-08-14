"""
GP045 — Owner Memory / Persistent Attention State Foundation.

Persistent owner attention memory for Clouds.

This is attention-state memory only.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any


OWNER_MEMORY_SCHEMA_VERSION = (
    "clouds-owner-attention-memory-v1"
)

OWNER_MEMORY_FINGERPRINT_POLICY = (
    "owner-attention-material-v1"
)


class OwnerMemoryDisposition(str, Enum):
    ACTIVE = "active"
    ACKNOWLEDGED = "acknowledged"
    SNOOZED = "snoozed"
    DISMISSED = "dismissed"


@dataclass(frozen=True)
class OwnerAttentionMemoryRecord:
    record_id: str

    owner_id: str
    agenda_item_id: str

    source_id: str
    impacted_source_id: str | None

    agenda_fingerprint: str
    fingerprint_policy: str

    disposition: str

    pinned: bool

    snooze_until: str | None

    review_count: int

    last_owner_action: str

    owner_note: str | None

    created_at: str
    updated_at: str

    automatic_downstream_action_performed: bool
    downstream_execution_performed: bool

    def to_dict(self) -> dict[str, Any]:
        return self.__dict__.copy()

    @classmethod
    def from_dict(
        cls,
        payload: dict[str, Any],
    ):
        return cls(**payload)


@dataclass(frozen=True)
class OwnerAttentionMemoryLedger:
    schema_version: str

    owner_id: str

    records: tuple[
        OwnerAttentionMemoryRecord,
        ...
    ]

    record_count: int

    ledger_integrity_hash: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": (
                self.schema_version
            ),

            "owner_id": (
                self.owner_id
            ),

            "records": [
                record.to_dict()
                for record in self.records
            ],

            "record_count": (
                self.record_count
            ),

            "ledger_integrity_hash": (
                self.ledger_integrity_hash
            ),
        }
