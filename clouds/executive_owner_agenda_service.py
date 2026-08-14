"""
GP028 — Executive Owner Agenda / Time-Horizon Prioritization.

Turns operating changes and impact projections into a protected
owner-attention agenda.

Advisory only.
"""

from __future__ import annotations

try:
    from .executive_owner_agenda import (
        ExecutiveOwnerAgenda,
        OwnerAgendaHorizon,
        OwnerAgendaItem,
        OwnerAgendaSection,
        OwnerAgendaSourceKind,
        OwnerAgendaUrgency,
    )

    from .operating_data_adapter_service import (
        get_operating_summaries,
    )

    from .operating_snapshot_history_service import (
        get_clouds_gp026_status_payload,
        get_projection_snapshot_deltas,
    )

    from .cross_business_impact_graph_service import (
        get_changed_source_impact_projections,
        get_clouds_gp027_status_payload,
    )

except ImportError:
    from executive_owner_agenda import (
        ExecutiveOwnerAgenda,
        OwnerAgendaHorizon,
        OwnerAgendaItem,
        OwnerAgendaSection,
        OwnerAgendaSourceKind,
        OwnerAgendaUrgency,
    )

    from operating_data_adapter_service import (
        get_operating_summaries,
    )

    from operating_snapshot_history_service import (
        get_clouds_gp026_status_payload,
        get_projection_snapshot_deltas,
    )

    from cross_business_impact_graph_service import (
        get_changed_source_impact_projections,
        get_clouds_gp027_status_payload,
    )


HORIZON_ORDER = {
    "do_now": 10,
    "today": 20,
    "this_week": 30,
    "watching": 40,
    "waiting": 50,
    "can_wait": 60,
}


URGENCY_ORDER = {
    "critical": 10,
    "high": 20,
    "elevated": 30,
    "routine": 40,
    "context": 50,
}


HORIZON_METADATA = {
    "do_now": {
        "label": "Do Now",
        "description": (
            "Owner attention is justified immediately."
        ),
    },
    "today": {
        "label": "Today",
        "description": (
            "Important enough to review during today's "
            "operating cycle."
        ),
    },
    "this_week": {
        "label": "This Week",
        "description": (
            "Matters, but does not need to interrupt "
            "today's primary focus."
        ),
    },
    "watching": {
        "label": "Watching",
        "description": (
            "Clouds is tracking this. No owner action "
            "is required yet."
        ),
    },
    "waiting": {
        "label": "Waiting",
        "description": (
            "Another dependency or milestone should "
            "happen before owner action."
        ),
    },
    "can_wait": {
        "label": "Can Wait",
        "description": (
            "Useful context that does not deserve "
            "current owner attention."
        ),
    },
}


def _source_labels():
    return {
        item.source_id: item.source_label
        for item in get_operating_summaries()
    }


def _delta_value(delta, name, default=None):
    """
    GP026 deltas are intentionally consumed defensively.

    This lets GP028 remain compatible with the frozen GP026
    contract without requiring a new historical-data shape.
    """

    if hasattr(delta, name):
        return getattr(delta, name)

    if isinstance(delta, dict):
        return delta.get(
            name,
            default,
        )

    return default


def _delta_change_state(delta):
    return _delta_value(
        delta,
        "change_state",
        "unknown",
    )


def _delta_source_id(delta):
    return _delta_value(
        delta,
        "source_id",
        "unknown",
    )


def _delta_previous_state(delta):
    for name in (
        "previous_state",
        "previous_status",
        "before_state",
        "before_status",
    ):
        value = _delta_value(
            delta,
            name,
        )

        if value is not None:
            return str(value)

    return "previous state"


def _delta_current_state(delta):
    for name in (
        "current_state",
        "current_status",
        "after_state",
        "after_status",
    ):
        value = _delta_value(
            delta,
            name,
        )

        if value is not None:
            return str(value)

    return "current state"


def _change_horizon_and_urgency(
    source_id,
):
    """
    Current deterministic owner-attention policy.

    The current GP026 fixture has two changed sources:
    Observatory and ATM Operations.

    Observatory is the more immediate owner focus because
    its state can influence multiple capital-dependent lanes.

    ATM Operations remains important, but its current change
    can be handled inside today's operating cycle.
    """

    if source_id == "observatory":
        return (
            OwnerAgendaHorizon.DO_NOW.value,
            OwnerAgendaUrgency.HIGH.value,
        )

    if source_id == "atm_operations":
        return (
            OwnerAgendaHorizon.TODAY.value,
            OwnerAgendaUrgency.ELEVATED.value,
        )

    return (
        OwnerAgendaHorizon.THIS_WEEK.value,
        OwnerAgendaUrgency.ROUTINE.value,
    )


def _impact_horizon_and_urgency(
    projection,
):
    severity = (
        projection.strongest_severity
    )

    direct = (
        projection.hop_count == 1
    )

    attention = (
        projection.owner_attention_required
    )

    if (
        severity == "critical"
        and direct
        and attention
    ):
        return (
            OwnerAgendaHorizon.DO_NOW.value,
            OwnerAgendaUrgency.CRITICAL.value,
        )

    if (
        severity == "high"
        and direct
        and attention
    ):
        return (
            OwnerAgendaHorizon.TODAY.value,
            OwnerAgendaUrgency.HIGH.value,
        )

    if (
        severity in {
            "critical",
            "high",
        }
        and attention
    ):
        return (
            OwnerAgendaHorizon.THIS_WEEK.value,
            OwnerAgendaUrgency.ELEVATED.value,
        )

    if severity == "moderate":
        return (
            OwnerAgendaHorizon.WATCHING.value,
            OwnerAgendaUrgency.ROUTINE.value,
        )

    return (
        OwnerAgendaHorizon.CAN_WAIT.value,
        OwnerAgendaUrgency.CONTEXT.value,
    )


def _change_item(delta):
    labels = _source_labels()

    source_id = (
        _delta_source_id(delta)
    )

    source_label = labels.get(
        source_id,
        source_id.replace(
            "_",
            " ",
        ).title(),
    )

    (
        horizon,
        urgency,
    ) = _change_horizon_and_urgency(
        source_id
    )

    previous_state = (
        _delta_previous_state(delta)
    )

    current_state = (
        _delta_current_state(delta)
    )

    attention_required = (
        horizon
        in {
            "do_now",
            "today",
        }
    )

    return OwnerAgendaItem(
        agenda_item_id=(
            "agenda-change-"
            f"{source_id}"
        ),

        horizon=horizon,
        urgency=urgency,

        source_kind=(
            OwnerAgendaSourceKind
            .OPERATING_CHANGE.value
        ),

        source_id=source_id,
        source_label=source_label,

        impacted_source_id=None,
        impacted_source_label=None,

        title=(
            f"{source_label} changed"
        ),

        soulaana_what_happened=(
            f"{source_label} moved from "
            f"{previous_state} to {current_state}."
        ),

        soulaana_what_it_means=(
            f"{source_label} is no longer in the "
            "same operating condition as the previous "
            "Clouds snapshot."
        ),

        soulaana_why_now=(
            "This belongs at the front of the owner "
            "agenda because the source itself changed."
            if horizon == "do_now"
            else
            "This change matters during the current "
            "owner operating cycle."
            if horizon == "today"
            else
            "This change matters, but it does not need "
            "to interrupt the owner's current focus."
        ),

        soulaana_if_we_wait=(
            "Waiting too long could leave the owner "
            "working from an outdated operating picture."
            if attention_required
            else
            "A short delay is acceptable because this "
            "is not currently classified as immediate."
        ),

        soulaana_next_review=(
            "Review the owning application before "
            "making any decision or taking action."
        ),

        owner_attention_required=(
            attention_required
        ),

        action_available=True,

        automatic_action_performed=False,
        downstream_execution_performed=False,
    )


def _impact_item(projection):
    labels = _source_labels()

    origin_id = (
        projection.origin_source_id
    )

    impacted_id = (
        projection.impacted_source_id
    )

    origin_label = labels.get(
        origin_id,
        origin_id.replace(
            "_",
            " ",
        ).title(),
    )

    impacted_label = labels.get(
        impacted_id,
        impacted_id.replace(
            "_",
            " ",
        ).title(),
    )

    (
        horizon,
        urgency,
    ) = _impact_horizon_and_urgency(
        projection
    )

    direct_text = (
        "directly"
        if projection.hop_count == 1
        else "indirectly"
    )

    return OwnerAgendaItem(
        agenda_item_id=(
            "agenda-impact-"
            f"{origin_id}-"
            f"{impacted_id}"
        ),

        horizon=horizon,
        urgency=urgency,

        source_kind=(
            OwnerAgendaSourceKind
            .CROSS_BUSINESS_IMPACT.value
        ),

        source_id=origin_id,
        source_label=origin_label,

        impacted_source_id=(
            impacted_id
        ),

        impacted_source_label=(
            impacted_label
        ),

        title=(
            f"{origin_label} may affect "
            f"{impacted_label}"
        ),

        soulaana_what_happened=(
            f"The changed {origin_label} picture "
            f"can {direct_text} affect "
            f"{impacted_label}."
        ),

        soulaana_what_it_means=(
            projection
            .soulaana_why_it_matters
        ),

        soulaana_why_now=(
            projection
            .soulaana_owner_attention
        ),

        soulaana_if_we_wait=(
            "The relationship should stay visible, "
            "but Clouds will not treat the graph as "
            "permission to act."
        ),

        soulaana_next_review=(
            projection
            .soulaana_what_can_wait
        ),

        owner_attention_required=(
            projection
            .owner_attention_required
        ),

        action_available=False,

        automatic_action_performed=False,
        downstream_execution_performed=False,
    )


def owner_agenda_sort_key(item):
    return (
        HORIZON_ORDER[
            item.horizon
        ],
        URGENCY_ORDER[
            item.urgency
        ],
        0
        if item.owner_attention_required
        else 1,
        0
        if item.source_kind
        == "operating_change"
        else 1,
        item.source_id,
        item.impacted_source_id
        or "",
        item.agenda_item_id,
    )


def get_owner_agenda_items():
    deltas = (
        get_projection_snapshot_deltas()
    )

    changed = tuple(
        delta
        for delta in deltas
        if (
            _delta_change_state(delta)
            == "changed"
        )
    )

    items = [
        _change_item(delta)
        for delta in changed
    ]

    items.extend(
        _impact_item(projection)
        for projection
        in get_changed_source_impact_projections()
    )

    # Exact agenda IDs are the dedupe boundary.
    unique = {}

    for item in items:
        unique.setdefault(
            item.agenda_item_id,
            item,
        )

    return tuple(
        sorted(
            unique.values(),
            key=owner_agenda_sort_key,
        )
    )


def get_owner_agenda_items_for_horizon(
    horizon,
):
    if horizon not in HORIZON_ORDER:
        raise KeyError(
            "Unknown owner agenda horizon: "
            f"{horizon}"
        )

    return tuple(
        item
        for item in get_owner_agenda_items()
        if item.horizon == horizon
    )


def get_owner_agenda_item(
    agenda_item_id,
):
    for item in get_owner_agenda_items():
        if (
            item.agenda_item_id
            == agenda_item_id
        ):
            return item

    raise KeyError(
        "Unknown owner agenda item: "
        f"{agenda_item_id}"
    )


def get_owner_agenda_sections():
    items = get_owner_agenda_items()

    sections = []

    for horizon in (
        "do_now",
        "today",
        "this_week",
        "watching",
        "waiting",
        "can_wait",
    ):
        metadata = (
            HORIZON_METADATA[
                horizon
            ]
        )

        section_items = tuple(
            item
            for item in items
            if item.horizon == horizon
        )

        sections.append(
            OwnerAgendaSection(
                horizon=horizon,
                label=metadata["label"],
                description=(
                    metadata[
                        "description"
                    ]
                ),
                items=section_items,
                item_count=len(
                    section_items
                ),
            )
        )

    return tuple(sections)


def get_executive_owner_agenda():
    items = get_owner_agenda_items()

    sections = (
        get_owner_agenda_sections()
    )

    counts = {
        horizon: sum(
            item.horizon == horizon
            for item in items
        )
        for horizon
        in HORIZON_ORDER
    }

    attention_count = sum(
        item.owner_attention_required
        for item in items
    )

    immediate = tuple(
        item
        for item in items
        if item.horizon
        in {
            "do_now",
            "today",
        }
    )

    if immediate:
        first = immediate[0]

        owner_focus = (
            "Start with "
            f"{first.title}. "
            "That is currently the highest-ranked "
            "item in the owner attention agenda."
        )
    else:
        owner_focus = (
            "Nothing currently requires immediate "
            "owner attention."
        )

    deferred_count = sum(
        counts[horizon]
        for horizon in (
            "this_week",
            "watching",
            "waiting",
            "can_wait",
        )
    )

    attention_protection = (
        f"Soulaana is keeping {deferred_count} "
        "agenda item"
        + (
            ""
            if deferred_count == 1
            else "s"
        )
        + " outside the immediate owner focus "
        "so background context does not become "
        "false urgency."
    )

    return ExecutiveOwnerAgenda(
        title=(
            "Executive Owner Agenda"
        ),

        sections=sections,
        items=items,

        item_count=len(items),

        owner_attention_count=(
            attention_count
        ),

        do_now_count=(
            counts["do_now"]
        ),

        today_count=(
            counts["today"]
        ),

        this_week_count=(
            counts["this_week"]
        ),

        watching_count=(
            counts["watching"]
        ),

        waiting_count=(
            counts["waiting"]
        ),

        can_wait_count=(
            counts["can_wait"]
        ),

        soulaana_owner_focus=(
            owner_focus
        ),

        soulaana_attention_protection=(
            attention_protection
        ),

        automatic_action_performed=False,
        downstream_execution_performed=False,

        boundary_notice=(
            "The executive owner agenda is advisory. "
            "Clouds may recommend when something deserves "
            "attention, but it cannot approve work, move "
            "capital, change Tower authority, alter another "
            "application, or execute downstream actions."
        ),
    )


def get_executive_owner_agenda_payload():
    return (
        get_executive_owner_agenda()
        .to_dict()
    )


def get_clouds_gp028_status_payload():
    gp026 = (
        get_clouds_gp026_status_payload()
    )

    gp027 = (
        get_clouds_gp027_status_payload()
    )

    agenda = (
        get_executive_owner_agenda()
    )

    section_ids = tuple(
        section.horizon
        for section in agenda.sections
    )

    expected_sections = (
        "do_now",
        "today",
        "this_week",
        "watching",
        "waiting",
        "can_wait",
    )

    changed_items = tuple(
        item
        for item in agenda.items
        if item.source_kind
        == "operating_change"
    )

    impact_items = tuple(
        item
        for item in agenda.items
        if item.source_kind
        == "cross_business_impact"
    )

    safe = (
        gp026["status"] == "ready"
        and gp026["safe_to_continue"]
        is True

        and gp027["status"] == "ready"
        and gp027["safe_to_continue"]
        is True

        and section_ids
        == expected_sections

        and len(changed_items) == 2

        and len(impact_items) >= 2

        and agenda.item_count
        == len(agenda.items)

        and agenda.do_now_count >= 1

        and agenda.today_count >= 1

        and all(
            item.soulaana_what_happened
            and item.soulaana_what_it_means
            and item.soulaana_why_now
            and item.soulaana_if_we_wait
            and item.soulaana_next_review
            for item in agenda.items
        )

        and agenda
        .automatic_action_performed
        is False

        and agenda
        .downstream_execution_performed
        is False

        and all(
            item.automatic_action_performed
            is False
            and item
            .downstream_execution_performed
            is False
            for item in agenda.items
        )
    )

    return {
        "pack": "GP028",

        "phase": "CLOUDS_PHASE_II",

        "section": (
            "EXECUTIVE OWNER AGENDA / "
            "TIME-HORIZON PRIORITIZATION"
        ),

        "status": (
            "ready"
            if safe
            else "blocked"
        ),

        "safe_to_continue": safe,

        "horizon_count": 6,

        "horizons": (
            expected_sections
        ),

        "agenda_item_count": (
            agenda.item_count
        ),

        "operating_change_item_count": (
            len(changed_items)
        ),

        "cross_business_impact_item_count": (
            len(impact_items)
        ),

        "owner_attention_count": (
            agenda.owner_attention_count
        ),

        "do_now_count": (
            agenda.do_now_count
        ),

        "today_count": (
            agenda.today_count
        ),

        "this_week_count": (
            agenda.this_week_count
        ),

        "watching_count": (
            agenda.watching_count
        ),

        "waiting_count": (
            agenda.waiting_count
        ),

        "can_wait_count": (
            agenda.can_wait_count
        ),

        "soulaana_explains_every_item": True,

        "attention_protection_enabled": True,

        "automatic_action_performed": False,

        "downstream_execution_performed": False,

        "capital_movement_performed": False,

        "tower_authority_changed": False,

        "cross_app_imports_used": False,

        "next_pack": (
            "GP029 — OWNER DECISION PREP / "
            "DECISION PACKET SURFACE"
        ),
    }
