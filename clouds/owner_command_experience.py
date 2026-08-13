"""
GP021 — Owner Command UX / Soulaana Executive Surface.

This is an owner-facing presentation contract.

Soulaana interpretation leads.
Technical detail remains progressively disclosed.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Iterable


class OwnerCommandSectionKind(str, Enum):
    NEEDS_YOU = "needs_you"
    WATCHING = "watching"
    QUIET = "quiet"
    ECOSYSTEM = "ecosystem"


class OwnerCommandCardState(str, Enum):
    ACTION = "action"
    WATCH = "watch"
    QUIET = "quiet"
    HEALTHY = "healthy"
    RESERVED = "reserved"


class OwnerCommandNavigationKind(str, Enum):
    CLOUDS_INTERNAL = "clouds_internal"
    TOWER_HANDOFF = "tower_handoff"
    NONE = "none"


class ProgressiveDisclosureLevel(str, Enum):
    GLANCE = "glance"
    EXPLAIN = "explain"
    DETAILS = "details"
    EVIDENCE = "evidence"


@dataclass(frozen=True)
class OwnerStatusChip:
    chip_id: str
    label: str
    value: str
    explanation: str
    display_order: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "chip_id": self.chip_id,
            "label": self.label,
            "value": self.value,
            "explanation": self.explanation,
            "display_order": self.display_order,
        }


@dataclass(frozen=True)
class OwnerCommandNavigation:
    navigation_id: str

    label: str
    kind: str

    destination_id: str | None
    route_reference: str | None

    requires_tower: bool
    requires_owner_permission: bool
    requires_step_up: bool

    clouds_executes_navigation: bool
    downstream_execution_performed: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "navigation_id": self.navigation_id,
            "label": self.label,
            "kind": self.kind,
            "destination_id": self.destination_id,
            "route_reference": (
                self.route_reference
            ),
            "requires_tower": (
                self.requires_tower
            ),
            "requires_owner_permission": (
                self.requires_owner_permission
            ),
            "requires_step_up": (
                self.requires_step_up
            ),
            "clouds_executes_navigation": (
                self.clouds_executes_navigation
            ),
            "downstream_execution_performed": (
                self.downstream_execution_performed
            ),
        }


@dataclass(frozen=True)
class OwnerCommandCard:
    card_id: str
    source_id: str
    source_label: str

    section_kind: str
    state: str

    title: str
    soulaana_message: str

    why_it_matters: str
    what_needs_attention: str
    what_can_wait: str
    owner_next_step: str

    chips: tuple[
        OwnerStatusChip,
        ...
    ]

    navigation: OwnerCommandNavigation

    default_disclosure_level: str
    evidence_hidden_by_default: bool

    source_integrity_verified: bool
    execution_performed: bool

    display_order: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "card_id": self.card_id,
            "source_id": self.source_id,
            "source_label": self.source_label,
            "section_kind": self.section_kind,
            "state": self.state,
            "title": self.title,
            "soulaana_message": (
                self.soulaana_message
            ),
            "why_it_matters": (
                self.why_it_matters
            ),
            "what_needs_attention": (
                self.what_needs_attention
            ),
            "what_can_wait": (
                self.what_can_wait
            ),
            "owner_next_step": (
                self.owner_next_step
            ),
            "chips": [
                chip.to_dict()
                for chip in self.chips
            ],
            "navigation": (
                self.navigation.to_dict()
            ),
            "default_disclosure_level": (
                self.default_disclosure_level
            ),
            "evidence_hidden_by_default": (
                self.evidence_hidden_by_default
            ),
            "source_integrity_verified": (
                self.source_integrity_verified
            ),
            "execution_performed": (
                self.execution_performed
            ),
            "display_order": self.display_order,
        }


@dataclass(frozen=True)
class OwnerCommandSection:
    section_id: str
    kind: str

    title: str
    soulaana_intro: str

    cards: tuple[
        OwnerCommandCard,
        ...
    ]

    card_count: int
    collapsed_by_default: bool

    display_order: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "section_id": self.section_id,
            "kind": self.kind,
            "title": self.title,
            "soulaana_intro": (
                self.soulaana_intro
            ),
            "cards": [
                card.to_dict()
                for card in self.cards
            ],
            "card_count": self.card_count,
            "collapsed_by_default": (
                self.collapsed_by_default
            ),
            "display_order": self.display_order,
        }


@dataclass(frozen=True)
class SoulaanaCommandHero:
    greeting: str
    headline: str
    explanation: str

    needs_you_count: int
    watching_count: int
    quiet_count: int

    top_focus_source_id: str | None
    top_focus_label: str | None

    def to_dict(self) -> dict[str, Any]:
        return {
            "greeting": self.greeting,
            "headline": self.headline,
            "explanation": self.explanation,
            "needs_you_count": (
                self.needs_you_count
            ),
            "watching_count": (
                self.watching_count
            ),
            "quiet_count": (
                self.quiet_count
            ),
            "top_focus_source_id": (
                self.top_focus_source_id
            ),
            "top_focus_label": (
                self.top_focus_label
            ),
        }


@dataclass(frozen=True)
class OwnerCommandExperience:
    title: str
    subtitle: str

    hero: SoulaanaCommandHero

    sections: tuple[
        OwnerCommandSection,
        ...
    ]

    section_count: int
    card_count: int

    proof_page_primary_experience: bool
    evidence_hidden_by_default: bool
    progressive_disclosure_enabled: bool

    raw_source_access_performed: bool
    downstream_execution_performed: bool

    boundary_notice: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "title": self.title,
            "subtitle": self.subtitle,
            "hero": self.hero.to_dict(),
            "sections": [
                section.to_dict()
                for section in self.sections
            ],
            "section_count": (
                self.section_count
            ),
            "card_count": self.card_count,
            "proof_page_primary_experience": (
                self.proof_page_primary_experience
            ),
            "evidence_hidden_by_default": (
                self.evidence_hidden_by_default
            ),
            "progressive_disclosure_enabled": (
                self.progressive_disclosure_enabled
            ),
            "raw_source_access_performed": (
                self.raw_source_access_performed
            ),
            "downstream_execution_performed": (
                self.downstream_execution_performed
            ),
            "boundary_notice": (
                self.boundary_notice
            ),
        }


def filter_owner_command_cards(
    cards: Iterable[
        OwnerCommandCard
    ],
    *,
    section_kind: str | None = None,
    state: str | None = None,
    source_id: str | None = None,
    requires_tower: bool | None = None,
) -> tuple[
    OwnerCommandCard,
    ...
]:
    result = []

    for card in cards:
        if (
            section_kind is not None
            and card.section_kind
            != section_kind
        ):
            continue

        if (
            state is not None
            and card.state != state
        ):
            continue

        if (
            source_id is not None
            and card.source_id
            != source_id
        ):
            continue

        if (
            requires_tower is not None
            and card.navigation.requires_tower
            is not requires_tower
        ):
            continue

        result.append(card)

    return tuple(
        sorted(
            result,
            key=lambda item: (
                item.display_order,
                item.card_id,
            ),
        )
    )
