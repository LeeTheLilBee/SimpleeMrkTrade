"""The Clouds contracts.

The Clouds is the owner command dashboard across Simplee apps/assets.

Boundary:
Clouds reads safe summaries and routes the owner to the owning app. Clouds does
not replace Vault, Tower, OB, Teller, ATM, Property, or any specialized system.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List


CLOUDS_VERSION = "clouds_giant_pack_001"


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


@dataclass(frozen=True)
class CloudsSourceContract:
    source_id: str
    source_app: str
    source_route: str
    source_label: str
    summary_only: bool
    redacted: bool
    tower_guard_required: bool
    owning_app_keeps_authority: bool
    clouds_allowed_actions: List[str] = field(default_factory=list)
    clouds_blocked_actions: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class CloudsCommandCard:
    card_id: str
    label: str
    value: Any
    unit: str
    source_app: str
    source_route: str
    status: str
    summary: str
    owner_next_action: str
    open_app_target: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class CloudsBoundary:
    boundary_id: str
    label: str
    enforced: bool
    summary: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
