"""
GP020 — Soulaana executive interpretation foundation.

Soulaana explains trusted operating summaries before raw metrics.
"""

from __future__ import annotations

try:
    from .executive_operating_snapshot import (
        ExecutiveOperatingSnapshot,
        ExecutiveOperatingSourceCard,
        SoulaanaExecutiveBrief,
    )

    from .operating_data_adapter_service import (
        get_operating_summary,
    )

    from .operating_data_trust_service import (
        get_clouds_gp019_status_payload,
        get_operating_trust_records,
    )

except ImportError:
    from executive_operating_snapshot import (
        ExecutiveOperatingSnapshot,
        ExecutiveOperatingSourceCard,
        SoulaanaExecutiveBrief,
    )

    from operating_data_adapter_service import (
        get_operating_summary,
    )

    from operating_data_trust_service import (
        get_clouds_gp019_status_payload,
        get_operating_trust_records,
    )


def _card(record, order):
    source = get_operating_summary(
        record.source_id
    )

    if record.attention == "action_required":
        attention_text = (
            "This needs owner attention now."
        )

    elif record.attention == "review":
        attention_text = (
            "This should stay visible for review."
        )

    else:
        attention_text = (
            "No immediate owner action is required."
        )

    if record.attention in {
        "action_required",
        "review",
    }:
        wait_text = (
            "Lower-priority informational sources can wait."
        )
    else:
        wait_text = (
            "This source can remain in the background "
            "unless its health or readiness changes."
        )

    return ExecutiveOperatingSourceCard(
        source_id=source.source_id,
        source_label=source.source_label,
        health=record.health,
        readiness=record.readiness,
        attention=record.attention,
        what_it_means=source.explanation,
        why_it_matters=(
            f"{source.source_label} contributes to the "
            "Simplee owner operating picture without "
            "giving Clouds execution authority."
        ),
        what_needs_attention=attention_text,
        what_can_wait=wait_text,
        owner_next_step=source.owner_message,
        display_order=order,
    )


def get_executive_operating_source_cards():
    records = get_operating_trust_records()

    return tuple(
        _card(
            record,
            (index + 1) * 10,
        )
        for index, record in enumerate(records)
        if record.owner_visible
    )


def _brief(cards):
    needs_you = tuple(
        card.source_label
        for card in cards
        if card.attention
        == "action_required"
    )

    watching = tuple(
        card.source_label
        for card in cards
        if card.attention == "review"
    )

    can_wait = tuple(
        card.source_label
        for card in cards
        if card.attention
        == "informational"
    )

    no_action = tuple(
        card.source_label
        for card in cards
        if card.attention == "none"
    )

    if needs_you:
        headline = (
            "Here’s what needs you right now."
        )
    elif watching:
        headline = (
            "Nothing is urgent, but a few things "
            "deserve your attention."
        )
    else:
        headline = (
            "Your operating picture is stable."
        )

    explanation = (
        f"Clouds is currently interpreting "
        f"{len(cards)} trusted ecosystem summaries. "
        f"{len(needs_you)} requires immediate owner attention, "
        f"{len(watching)} should stay under review, and "
        f"{len(can_wait) + len(no_action)} can remain "
        f"in the background."
    )

    return SoulaanaExecutiveBrief(
        headline=headline,
        explanation=explanation,
        needs_you_now=needs_you,
        keep_watching=watching,
        can_wait=can_wait,
        no_action_needed=no_action,
    )


def get_executive_operating_snapshot():
    cards = (
        get_executive_operating_source_cards()
    )

    brief = _brief(cards)

    return ExecutiveOperatingSnapshot(
        title=(
            "Simplee Executive Operating Snapshot"
        ),
        brief=brief,
        source_cards=cards,
        source_count=len(cards),
        action_required_count=len(
            brief.needs_you_now
        ),
        watch_count=len(
            brief.keep_watching
        ),
        no_action_count=(
            len(brief.can_wait)
            + len(brief.no_action_needed)
        ),
        raw_source_access_performed=False,
        downstream_execution_performed=False,
        boundary_notice=(
            "Soulaana interprets trusted summaries only. "
            "Raw downstream application access and execution "
            "remain outside Clouds."
        ),
    )


def get_executive_operating_snapshot_payload():
    return (
        get_executive_operating_snapshot()
        .to_dict()
    )


def get_clouds_gp020_status_payload():
    gp019 = get_clouds_gp019_status_payload()

    snapshot = (
        get_executive_operating_snapshot()
    )

    safe = (
        gp019["status"] == "ready"
        and gp019["safe_to_continue"] is True
        and snapshot.source_count == 6
        and snapshot.action_required_count == 1
        and snapshot.watch_count == 1
        and snapshot.no_action_count == 4
        and snapshot.raw_source_access_performed
        is False
        and snapshot.downstream_execution_performed
        is False
        and snapshot.brief.needs_you_now
        == ("The Observatory",)
        and snapshot.brief.keep_watching
        == ("ATM Operations",)
    )

    return {
        "pack": "GP020",
        "section": (
            "EXECUTIVE OPERATING SNAPSHOT "
            "/ SOULAANA INTERPRETATION FOUNDATION"
        ),
        "status": "ready" if safe else "blocked",
        "safe_to_continue": safe,
        "source_count": snapshot.source_count,
        "action_required_count": (
            snapshot.action_required_count
        ),
        "watch_count": snapshot.watch_count,
        "no_action_count": (
            snapshot.no_action_count
        ),
        "top_owner_focus": "observatory",
        "watch_source": "atm_operations",
        "raw_source_access_performed": False,
        "downstream_execution_performed": False,
        "cross_app_imports_used": False,
        "next_pack": (
            "GP021 — OWNER COMMAND UX "
            "/ SOULAANA EXECUTIVE SURFACE"
        ),
    }
