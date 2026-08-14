"""
GP046 — Owner Attention Controls / Memory State Transitions.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class OwnerAttentionControlReceipt:
    receipt_id: str

    owner_id: str
    agenda_item_id: str

    owner_action: str

    previous_disposition: str
    current_disposition: str

    previous_pinned: bool
    current_pinned: bool

    snooze_until: str | None

    review_count: int

    memory_updated: bool

    downstream_authority_changed: bool
    downstream_execution_performed: bool

    soulaana_confirmation: str

    def to_dict(self) -> dict[str, Any]:
        return self.__dict__.copy()
