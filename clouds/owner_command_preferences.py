"""
GP023 — Owner Settings / Command Preferences.

Preferences shape presentation only.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any


class SoulaanaVerbosity(str, Enum):
    CONCISE = "concise"
    BALANCED = "balanced"
    EXPLAIN_EVERYTHING = "explain_everything"


class EvidenceDisclosurePreference(str, Enum):
    HIDDEN = "hidden"
    ON_REQUEST = "on_request"
    EXPANDED = "expanded"


class QuietCardBehavior(str, Enum):
    COLLAPSED = "collapsed"
    VISIBLE = "visible"
    HIDDEN_UNLESS_CHANGED = "hidden_unless_changed"


class AttentionThreshold(str, Enum):
    ACTION_ONLY = "action_only"
    REVIEW_AND_ACTION = "review_and_action"
    ALL_CHANGES = "all_changes"


@dataclass(frozen=True)
class OwnerCommandPreferences:
    owner_id: str

    soulaana_verbosity: str
    evidence_disclosure: str
    quiet_card_behavior: str
    attention_threshold: str

    collapse_quiet_section: bool
    collapse_ecosystem_section: bool

    show_status_chips: bool
    show_owner_next_step: bool
    show_why_it_matters: bool

    preserve_tower_handoffs: bool
    preserve_step_up_requirements: bool
    preserve_downstream_authority: bool

    persistent_projection: bool
    downstream_authority_changed: bool
    execution_performed: bool

    def to_dict(self) -> dict[str, Any]:
        return self.__dict__.copy()


@dataclass(frozen=True)
class OwnerCommandPreferencesSurface:
    title: str
    preferences: OwnerCommandPreferences

    presentation_only: bool
    tower_boundary_preserved: bool
    downstream_authority_preserved: bool

    boundary_notice: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "title": self.title,
            "preferences": (
                self.preferences.to_dict()
            ),
            "presentation_only": (
                self.presentation_only
            ),
            "tower_boundary_preserved": (
                self.tower_boundary_preserved
            ),
            "downstream_authority_preserved": (
                self.downstream_authority_preserved
            ),
            "boundary_notice": (
                self.boundary_notice
            ),
        }
