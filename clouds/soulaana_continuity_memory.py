"""
GP047 — Soulaana Continuity Memory / Change-Aware Reopen Rules.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any


class OwnerContinuityState(str, Enum):
    NEW_ITEM = "new_item"
    ACTIVE = "active"
    PINNED = "pinned"
    QUIET_UNCHANGED = "quiet_unchanged"
    SNOOZED = "snoozed"
    SNOOZE_EXPIRED = "snooze_expired"
    REOPENED_MATERIAL_CHANGE = (
        "reopened_material_change"
    )


@dataclass(frozen=True)
class OwnerContinuityItem:
    agenda_item_id: str

    source_id: str
    source_label: str

    impacted_source_id: str | None
    impacted_source_label: str | None

    title: str

    horizon: str
    urgency: str

    memory_present: bool
    memory_disposition: str | None

    pinned: bool

    fingerprint_changed: bool

    snooze_active: bool

    continuity_state: str

    should_surface: bool

    should_reopen: bool

    owner_attention_required_from_agenda: bool

    soulaana_what_you_told_me: str
    soulaana_what_changed: str
    soulaana_why_im_showing_or_hiding_this: str
    soulaana_next_step: str

    downstream_execution_performed: bool

    def to_dict(self) -> dict[str, Any]:
        return self.__dict__.copy()
