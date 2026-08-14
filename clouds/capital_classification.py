"""
GP049 — Capital Classification / Money Reality Foundation.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any


class CapitalClassification(str, Enum):
    AVAILABLE = "available"
    COMMITTED = "committed"
    PROJECTED = "projected"
    TARGET = "target"
    NEED = "need"


class CapitalReality(str, Enum):
    VERIFIED_REAL = "verified_real"
    PLANNING_PROJECTION = "planning_projection"
    SIMULATION = "simulation"


@dataclass(frozen=True)
class CapitalEntry:
    entry_id: str

    source_id: str
    source_label: str

    classification: str
    reality: str

    amount_cents: int
    currency: str

    external_source_connected: bool
    external_connection_verified: bool

    source_claims_real: bool

    certification_fixture_only: bool

    evidence_reference: str | None

    note: str

    counts_as_verified_real_available: bool
    counts_as_verified_real_committed: bool

    counts_as_planning_available: bool
    counts_as_planning_committed: bool

    counts_as_projected: bool
    counts_as_simulated: bool

    counts_as_target: bool
    counts_as_need: bool

    capital_movement_performed: bool
    downstream_execution_performed: bool

    def to_dict(self) -> dict[str, Any]:
        return self.__dict__.copy()
