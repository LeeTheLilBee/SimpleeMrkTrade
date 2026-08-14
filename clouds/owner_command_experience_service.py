"""
GP021 — Owner Command UX / Soulaana Executive Surface.

Presentation and navigation-reference composition only.
"""

from __future__ import annotations

try:
    from .executive_operating_snapshot_service import (
        get_clouds_gp020_status_payload,
        get_executive_operating_snapshot,
        get_executive_operating_source_cards,
    )

    from .owner_command_experience import (
        OwnerCommandCard,
        OwnerCommandCardState,
        OwnerCommandExperience,
        OwnerCommandNavigation,
        OwnerCommandNavigationKind,
        OwnerCommandSection,
        OwnerCommandSectionKind,
        OwnerStatusChip,
        ProgressiveDisclosureLevel,
        SoulaanaCommandHero,
        filter_owner_command_cards,
    )

except ImportError:
    from executive_operating_snapshot_service import (
        get_clouds_gp020_status_payload,
        get_executive_operating_snapshot,
        get_executive_operating_source_cards,
    )

    from owner_command_experience import (
        OwnerCommandCard,
        OwnerCommandCardState,
        OwnerCommandExperience,
        OwnerCommandNavigation,
        OwnerCommandNavigationKind,
        OwnerCommandSection,
        OwnerCommandSectionKind,
        OwnerStatusChip,
        ProgressiveDisclosureLevel,
        SoulaanaCommandHero,
        filter_owner_command_cards,
    )


SOURCE_DESTINATIONS = {
    "observatory": {
        "kind": "tower_handoff",
        "destination_id": "tower-observatory",
        "route_reference": "/tower/launch/observatory",
        "requires_tower": True,
        "requires_owner_permission": True,
        "requires_step_up": True,
    },

    "tower": {
        "kind": "tower_handoff",
        "destination_id": "tower-access-home",
        "route_reference": "/tower/access-home",
        "requires_tower": True,
        "requires_owner_permission": True,
        "requires_step_up": False,
    },

    "teller": {
        "kind": "tower_handoff",
        "destination_id": "tower-teller",
        "route_reference": None,
        "requires_tower": True,
        "requires_owner_permission": True,
        "requires_step_up": True,
    },

    "grounds": {
        "kind": "tower_handoff",
        "destination_id": "tower-grounds",
        "route_reference": None,
        "requires_tower": True,
        "requires_owner_permission": True,
        "requires_step_up": True,
    },

    "archive_vault": {
        "kind": "tower_handoff",
        "destination_id": "tower-archive-vault",
        "route_reference": None,
        "requires_tower": True,
        "requires_owner_permission": True,
        "requires_step_up": True,
    },

    "atm_operations": {
        "kind": "clouds_internal",
        "destination_id": "clouds-atm-operations",
        "route_reference": "/clouds/mission/atm-operations",
        "requires_tower": False,
        "requires_owner_permission": False,
        "requires_step_up": False,
    },
}


def _section_kind(card):
    if card.attention == "action_required":
        return OwnerCommandSectionKind.NEEDS_YOU.value

    if card.attention == "review":
        return OwnerCommandSectionKind.WATCHING.value

    return OwnerCommandSectionKind.QUIET.value


def _state(card):
    if card.attention == "action_required":
        return OwnerCommandCardState.ACTION.value

    if card.attention == "review":
        return OwnerCommandCardState.WATCH.value

    if card.readiness == "reserved":
        return OwnerCommandCardState.RESERVED.value

    if card.health == "healthy":
        return OwnerCommandCardState.HEALTHY.value

    return OwnerCommandCardState.QUIET.value


def _navigation(source_id):
    config = SOURCE_DESTINATIONS[
        source_id
    ]

    return OwnerCommandNavigation(
        navigation_id=(
            f"owner-command-nav-{source_id}"
        ),
        label=(
            "Open protected app"
            if config["requires_tower"]
            else "Review in Clouds"
        ),
        kind=config["kind"],
        destination_id=(
            config["destination_id"]
        ),
        route_reference=(
            config["route_reference"]
        ),
        requires_tower=(
            config["requires_tower"]
        ),
        requires_owner_permission=(
            config["requires_owner_permission"]
        ),
        requires_step_up=(
            config["requires_step_up"]
        ),
        clouds_executes_navigation=False,
        downstream_execution_performed=False,
    )


def _chips(card):
    return (
        OwnerStatusChip(
            chip_id=(
                f"{card.source_id}-health"
            ),
            label="Health",
            value=card.health,
            explanation=(
                "Current normalized operating health."
            ),
            display_order=10,
        ),

        OwnerStatusChip(
            chip_id=(
                f"{card.source_id}-readiness"
            ),
            label="Readiness",
            value=card.readiness,
            explanation=(
                "Current normalized readiness state."
            ),
            display_order=20,
        ),

        OwnerStatusChip(
            chip_id=(
                f"{card.source_id}-attention"
            ),
            label="Attention",
            value=card.attention,
            explanation=(
                "How much owner attention Clouds "
                "believes this source needs."
            ),
            display_order=30,
        ),
    )


def _owner_card(card):
    section_kind = _section_kind(
        card
    )

    return OwnerCommandCard(
        card_id=(
            f"owner-command-{card.source_id}"
        ),
        source_id=card.source_id,
        source_label=card.source_label,
        section_kind=section_kind,
        state=_state(card),
        title=card.source_label,
        soulaana_message=(
            card.what_needs_attention
            if section_kind
            != OwnerCommandSectionKind
            .QUIET.value
            else card.what_it_means
        ),
        why_it_matters=(
            card.why_it_matters
        ),
        what_needs_attention=(
            card.what_needs_attention
        ),
        what_can_wait=(
            card.what_can_wait
        ),
        owner_next_step=(
            card.owner_next_step
        ),
        chips=_chips(card),
        navigation=_navigation(
            card.source_id
        ),
        default_disclosure_level=(
            ProgressiveDisclosureLevel
            .GLANCE.value
        ),
        evidence_hidden_by_default=True,
        source_integrity_verified=True,
        execution_performed=False,
        display_order=card.display_order,
    )


def get_owner_command_cards():
    return tuple(
        _owner_card(card)
        for card
        in get_executive_operating_source_cards()
    )


def get_owner_command_card(
    source_id,
):
    for item in get_owner_command_cards():
        if item.source_id == source_id:
            return item

    raise KeyError(
        "Unknown owner command source: "
        f"{source_id}"
    )


def filter_owner_command_experience_cards(
    *,
    section_kind=None,
    state=None,
    source_id=None,
    requires_tower=None,
):
    return filter_owner_command_cards(
        get_owner_command_cards(),
        section_kind=section_kind,
        state=state,
        source_id=source_id,
        requires_tower=requires_tower,
    )


def _section(
    *,
    section_id,
    kind,
    title,
    intro,
    cards,
    collapsed,
    order,
):
    return OwnerCommandSection(
        section_id=section_id,
        kind=kind,
        title=title,
        soulaana_intro=intro,
        cards=tuple(cards),
        card_count=len(cards),
        collapsed_by_default=collapsed,
        display_order=order,
    )


def get_owner_command_sections():
    cards = get_owner_command_cards()

    needs = tuple(
        item
        for item in cards
        if item.section_kind == "needs_you"
    )

    watching = tuple(
        item
        for item in cards
        if item.section_kind == "watching"
    )

    quiet = tuple(
        item
        for item in cards
        if item.section_kind == "quiet"
    )

    return (
        _section(
            section_id="owner-command-needs-you",
            kind="needs_you",
            title="Needs You",
            intro=(
                "These are the things I would put "
                "in front of you first."
            ),
            cards=needs,
            collapsed=False,
            order=10,
        ),

        _section(
            section_id="owner-command-watching",
            kind="watching",
            title="Keep Watching",
            intro=(
                "These do not outrank your current focus, "
                "but I would keep them visible."
            ),
            cards=watching,
            collapsed=False,
            order=20,
        ),

        _section(
            section_id="owner-command-quiet",
            kind="quiet",
            title="Can Wait",
            intro=(
                "These are still part of the picture, "
                "but they do not need your attention now."
            ),
            cards=quiet,
            collapsed=True,
            order=30,
        ),

        _section(
            section_id="owner-command-ecosystem",
            kind="ecosystem",
            title="Simplee World",
            intro=(
                "Here is the full operating map when "
                "you want to look across everything."
            ),
            cards=cards,
            collapsed=True,
            order=40,
        ),
    )


def _hero():
    snapshot = (
        get_executive_operating_snapshot()
    )

    cards = get_owner_command_cards()

    needs = [
        item
        for item in cards
        if item.section_kind == "needs_you"
    ]

    watching = [
        item
        for item in cards
        if item.section_kind == "watching"
    ]

    quiet = [
        item
        for item in cards
        if item.section_kind == "quiet"
    ]

    top = (
        needs[0]
        if needs
        else (
            watching[0]
            if watching
            else None
        )
    )

    return SoulaanaCommandHero(
        greeting="Good to see you.",
        headline=(
            snapshot.brief.headline
        ),
        explanation=(
            snapshot.brief.explanation
        ),
        needs_you_count=len(needs),
        watching_count=len(watching),
        quiet_count=len(quiet),
        top_focus_source_id=(
            top.source_id
            if top
            else None
        ),
        top_focus_label=(
            top.source_label
            if top
            else None
        ),
    )


def get_owner_command_experience():
    sections = (
        get_owner_command_sections()
    )

    cards = get_owner_command_cards()

    return OwnerCommandExperience(
        title="The Clouds",
        subtitle=(
            "Simplee World Owner Command"
        ),
        hero=_hero(),
        sections=sections,
        section_count=len(sections),
        card_count=len(cards),
        proof_page_primary_experience=False,
        evidence_hidden_by_default=True,
        progressive_disclosure_enabled=True,
        raw_source_access_performed=False,
        downstream_execution_performed=False,
        boundary_notice=(
            "Clouds leads with interpretation and "
            "progressive disclosure. Protected app entry "
            "remains Tower-mediated."
        ),
    )


def get_owner_command_experience_payload():
    return (
        get_owner_command_experience()
        .to_dict()
    )


def get_clouds_gp021_status_payload():
    gp020 = get_clouds_gp020_status_payload()

    experience = (
        get_owner_command_experience()
    )

    cards = get_owner_command_cards()

    safe = (
        gp020["status"] == "ready"
        and gp020["safe_to_continue"] is True
        and experience.section_count == 4
        and experience.card_count == 6
        and experience.hero.needs_you_count == 1
        and experience.hero.watching_count == 1
        and experience.hero.quiet_count == 4
        and experience.hero.top_focus_source_id
        == "observatory"
        and experience.proof_page_primary_experience
        is False
        and experience.evidence_hidden_by_default
        is True
        and experience.progressive_disclosure_enabled
        is True
        and all(
            item.source_integrity_verified
            is True
            and item.execution_performed
            is False
            and item.navigation
            .clouds_executes_navigation
            is False
            and item.navigation
            .downstream_execution_performed
            is False
            for item in cards
        )
    )

    return {
        "pack": "GP021",
        "section": (
            "OWNER COMMAND UX "
            "/ SOULAANA EXECUTIVE SURFACE"
        ),
        "status": (
            "ready"
            if safe
            else "blocked"
        ),
        "safe_to_continue": safe,
        "section_count": (
            experience.section_count
        ),
        "card_count": (
            experience.card_count
        ),
        "needs_you_count": (
            experience.hero.needs_you_count
        ),
        "watching_count": (
            experience.hero.watching_count
        ),
        "quiet_count": (
            experience.hero.quiet_count
        ),
        "top_focus_source": (
            experience.hero.top_focus_source_id
        ),
        "soulaana_leads": True,
        "proof_page_primary_experience": False,
        "evidence_hidden_by_default": True,
        "progressive_disclosure_enabled": True,
        "raw_source_access_performed": False,
        "downstream_execution_performed": False,
        "cross_app_imports_used": False,
        "next_pack": (
            "GP022 — OWNER COMMAND DETAIL DRAWERS "
            "/ GUIDED ATTENTION EXPERIENCE"
        ),
    }
