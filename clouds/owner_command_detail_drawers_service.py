"""
GP022 — Guided attention and progressive owner detail.

Dismiss / snooze are recommendations only.
No persistent state mutation occurs.
"""

from __future__ import annotations

try:
    from .owner_command_detail_drawers import (
        DetailDrawerDisclosure,
        DetailDrawerKind,
        GuidedAttentionAction,
        GuidedAttentionStep,
        GuidedAttentionSurface,
        OwnerCommandDetailExperience,
        OwnerCommandDrawer,
        filter_detail_experiences,
    )

    from .owner_command_experience_service import (
        get_clouds_gp021_status_payload,
        get_owner_command_cards,
    )

except ImportError:
    from owner_command_detail_drawers import (
        DetailDrawerDisclosure,
        DetailDrawerKind,
        GuidedAttentionAction,
        GuidedAttentionStep,
        GuidedAttentionSurface,
        OwnerCommandDetailExperience,
        OwnerCommandDrawer,
        filter_detail_experiences,
    )

    from owner_command_experience_service import (
        get_clouds_gp021_status_payload,
        get_owner_command_cards,
    )


def _drawer(
    source_id,
    *,
    kind,
    disclosure,
    title,
    content,
    order,
    technical=False,
    action_required=False,
):
    return OwnerCommandDrawer(
        drawer_id=(
            f"{source_id}-drawer-{kind}"
        ),
        source_id=source_id,
        kind=kind,
        disclosure_level=disclosure,
        title=title,
        content=content,
        hidden_by_default=True,
        owner_action_required=(
            action_required
        ),
        technical=technical,
        execution_performed=False,
        display_order=order,
    )


def _drawers(card):
    status_content = "; ".join(
        f"{chip.label}: {chip.value}"
        for chip in card.chips
    )

    evidence_content = (
        "Technical evidence is intentionally "
        "not expanded in the primary owner view. "
        "Use the source application or future evidence "
        "drawer integration for deeper proof."
    )

    return (
        _drawer(
            card.source_id,
            kind="explanation",
            disclosure="primary",
            title="Soulaana Explains",
            content=(
                card.soulaana_message
            ),
            order=10,
            action_required=(
                card.section_kind
                == "needs_you"
            ),
        ),

        _drawer(
            card.source_id,
            kind="why_it_matters",
            disclosure="primary",
            title="Why this matters",
            content=(
                card.why_it_matters
            ),
            order=20,
        ),

        _drawer(
            card.source_id,
            kind="current_state",
            disclosure="secondary",
            title="What is happening",
            content=(
                card.what_needs_attention
            ),
            order=30,
        ),

        _drawer(
            card.source_id,
            kind="can_wait",
            disclosure="secondary",
            title="What can wait",
            content=(
                card.what_can_wait
            ),
            order=40,
        ),

        _drawer(
            card.source_id,
            kind="next_step",
            disclosure="secondary",
            title="What you can do next",
            content=(
                card.owner_next_step
            ),
            order=50,
        ),

        _drawer(
            card.source_id,
            kind="status_details",
            disclosure="deep",
            title="Status details",
            content=status_content,
            order=60,
        ),

        _drawer(
            card.source_id,
            kind="evidence",
            disclosure="technical",
            title="Technical evidence",
            content=evidence_content,
            order=70,
            technical=True,
        ),
    )


def _guided_steps(card):
    steps = []

    if card.section_kind == "needs_you":
        steps.append(
            GuidedAttentionStep(
                step_id=(
                    f"{card.source_id}-review-now"
                ),
                source_id=card.source_id,
                action="review_now",
                label="Review now",
                explanation=(
                    "This is the current top owner "
                    "attention recommendation."
                ),
                recommended=True,
                mutates_persistent_state=False,
                executes_downstream_action=False,
                display_order=10,
            )
        )

    elif card.section_kind == "watching":
        steps.append(
            GuidedAttentionStep(
                step_id=(
                    f"{card.source_id}-watch"
                ),
                source_id=card.source_id,
                action="keep_watching",
                label="Keep watching",
                explanation=(
                    "Leave this visible without moving "
                    "it ahead of the current owner focus."
                ),
                recommended=True,
                mutates_persistent_state=False,
                executes_downstream_action=False,
                display_order=10,
            )
        )

        steps.append(
            GuidedAttentionStep(
                step_id=(
                    f"{card.source_id}-snooze"
                ),
                source_id=card.source_id,
                action="snooze",
                label="Snooze recommendation",
                explanation=(
                    "GP022 only describes this option. "
                    "No persistent snooze is written."
                ),
                recommended=False,
                mutates_persistent_state=False,
                executes_downstream_action=False,
                display_order=20,
            )
        )

    else:
        steps.append(
            GuidedAttentionStep(
                step_id=(
                    f"{card.source_id}-no-action"
                ),
                source_id=card.source_id,
                action="no_action",
                label="No action needed",
                explanation=(
                    "This can remain in the background."
                ),
                recommended=True,
                mutates_persistent_state=False,
                executes_downstream_action=False,
                display_order=10,
            )
        )

        steps.append(
            GuidedAttentionStep(
                step_id=(
                    f"{card.source_id}-dismiss"
                ),
                source_id=card.source_id,
                action="dismiss_informational",
                label="Dismiss informational card",
                explanation=(
                    "GP022 describes dismissal only. "
                    "No persistent preference is changed."
                ),
                recommended=False,
                mutates_persistent_state=False,
                executes_downstream_action=False,
                display_order=20,
            )
        )

    steps.append(
        GuidedAttentionStep(
            step_id=(
                f"{card.source_id}-details"
            ),
            source_id=card.source_id,
            action="open_details",
            label="Show me more",
            explanation=(
                "Open progressively deeper explanation "
                "inside Clouds."
            ),
            recommended=False,
            mutates_persistent_state=False,
            executes_downstream_action=False,
            display_order=80,
        )
    )

    if card.navigation.requires_tower:
        steps.append(
            GuidedAttentionStep(
                step_id=(
                    f"{card.source_id}-protected-app"
                ),
                source_id=card.source_id,
                action="open_protected_app",
                label="Go to the owning app",
                explanation=(
                    "Tower must mediate protected "
                    "application entry."
                ),
                recommended=False,
                mutates_persistent_state=False,
                executes_downstream_action=False,
                display_order=90,
            )
        )

    return tuple(
        sorted(
            steps,
            key=lambda item: (
                item.display_order,
                item.step_id,
            ),
        )
    )


def _experience(card):
    return OwnerCommandDetailExperience(
        source_id=card.source_id,
        source_label=(
            card.source_label
        ),
        soulaana_summary=(
            card.soulaana_message
        ),
        drawers=_drawers(card),
        guided_steps=(
            _guided_steps(card)
        ),
        drawer_count=7,
        guided_step_count=len(
            _guided_steps(card)
        ),
        evidence_hidden_by_default=True,
        persistent_state_mutated=False,
        downstream_execution_performed=False,
    )


def get_owner_command_detail_experiences():
    return tuple(
        _experience(card)
        for card in get_owner_command_cards()
    )


def get_owner_command_detail_experience(
    source_id,
):
    for item in (
        get_owner_command_detail_experiences()
    ):
        if item.source_id == source_id:
            return item

    raise KeyError(
        "Unknown owner detail source: "
        f"{source_id}"
    )


def filter_owner_command_detail_experiences(
    *,
    source_id=None,
    drawer_kind=None,
    action=None,
):
    return filter_detail_experiences(
        get_owner_command_detail_experiences(),
        source_id=source_id,
        drawer_kind=drawer_kind,
        action=action,
    )


def get_guided_attention_surface():
    experiences = (
        get_owner_command_detail_experiences()
    )

    needs = []
    watching = []
    quiet = []

    for experience in experiences:
        actions = {
            step.action
            for step
            in experience.guided_steps
        }

        if "review_now" in actions:
            needs.append(
                experience.source_id
            )

        elif "keep_watching" in actions:
            watching.append(
                experience.source_id
            )

        else:
            quiet.append(
                experience.source_id
            )

    return GuidedAttentionSurface(
        title=(
            "Owner Command Detail Drawers "
            "/ Guided Attention"
        ),
        experiences=experiences,
        source_count=len(experiences),
        primary_attention_source_id=(
            needs[0]
            if needs
            else None
        ),
        watch_source_ids=tuple(
            watching
        ),
        quiet_source_ids=tuple(
            quiet
        ),
        evidence_hidden_by_default=True,
        persistent_state_mutated=False,
        downstream_execution_performed=False,
        boundary_notice=(
            "GP022 provides progressive detail and "
            "guided recommendations only. Snooze and "
            "dismiss do not mutate persistent owner state."
        ),
    )


def get_guided_attention_surface_payload():
    return (
        get_guided_attention_surface()
        .to_dict()
    )


def get_clouds_gp022_status_payload():
    gp021 = get_clouds_gp021_status_payload()

    surface = (
        get_guided_attention_surface()
    )

    experiences = (
        surface.experiences
    )

    safe = (
        gp021["status"] == "ready"
        and gp021["safe_to_continue"] is True
        and surface.source_count == 6
        and surface.primary_attention_source_id
        == "observatory"
        and surface.watch_source_ids
        == ("atm_operations",)
        and len(surface.quiet_source_ids) == 4
        and surface.evidence_hidden_by_default
        is True
        and surface.persistent_state_mutated
        is False
        and surface.downstream_execution_performed
        is False
        and all(
            item.drawer_count == 7
            and item.evidence_hidden_by_default
            is True
            and item.persistent_state_mutated
            is False
            and item.downstream_execution_performed
            is False
            and all(
                drawer.execution_performed
                is False
                for drawer in item.drawers
            )
            and all(
                step.mutates_persistent_state
                is False
                and step.executes_downstream_action
                is False
                for step in item.guided_steps
            )
            for item in experiences
        )
    )

    return {
        "pack": "GP022",
        "section": (
            "OWNER COMMAND DETAIL DRAWERS "
            "/ GUIDED ATTENTION EXPERIENCE"
        ),
        "status": (
            "ready"
            if safe
            else "blocked"
        ),
        "safe_to_continue": safe,
        "source_count": (
            surface.source_count
        ),
        "drawer_count_per_source": 7,
        "primary_attention_source": (
            surface.primary_attention_source_id
        ),
        "watch_source_ids": (
            surface.watch_source_ids
        ),
        "quiet_source_count": (
            len(surface.quiet_source_ids)
        ),
        "evidence_hidden_by_default": True,
        "persistent_state_mutated": False,
        "downstream_execution_performed": False,
        "cross_app_imports_used": False,
        "next_pack": (
            "GP023 — OWNER SETTINGS "
            "/ COMMAND PREFERENCES SURFACE"
        ),
    }
