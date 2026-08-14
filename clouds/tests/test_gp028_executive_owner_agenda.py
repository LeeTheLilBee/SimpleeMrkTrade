import pytest

from clouds.executive_owner_agenda_service import (
    get_clouds_gp028_status_payload,
    get_executive_owner_agenda,
    get_executive_owner_agenda_payload,
    get_owner_agenda_item,
    get_owner_agenda_items,
    get_owner_agenda_items_for_horizon,
    get_owner_agenda_sections,
    owner_agenda_sort_key,
)


EXPECTED_HORIZONS = (
    "do_now",
    "today",
    "this_week",
    "watching",
    "waiting",
    "can_wait",
)


def test_gp028_has_six_fixed_horizons():
    sections = (
        get_owner_agenda_sections()
    )

    assert tuple(
        section.horizon
        for section in sections
    ) == EXPECTED_HORIZONS


def test_gp028_changed_sources_become_agenda_items():
    items = get_owner_agenda_items()

    changed = tuple(
        item
        for item in items
        if item.source_kind
        == "operating_change"
    )

    assert len(changed) == 2

    assert {
        item.source_id
        for item in changed
    } == {
        "observatory",
        "atm_operations",
    }


def test_gp028_observatory_change_is_do_now():
    item = get_owner_agenda_item(
        "agenda-change-observatory"
    )

    assert item.horizon == "do_now"
    assert item.urgency == "high"

    assert (
        item.owner_attention_required
        is True
    )


def test_gp028_atm_change_is_today():
    item = get_owner_agenda_item(
        "agenda-change-atm_operations"
    )

    assert item.horizon == "today"

    assert (
        item.urgency
        == "elevated"
    )

    assert (
        item.owner_attention_required
        is True
    )


def test_gp028_observatory_atm_impact_is_today():
    item = get_owner_agenda_item(
        "agenda-impact-observatory-atm_operations"
    )

    assert item.horizon == "today"
    assert item.urgency == "high"

    assert (
        item.impacted_source_id
        == "atm_operations"
    )


def test_gp028_observatory_grounds_impact_is_today():
    item = get_owner_agenda_item(
        "agenda-impact-observatory-grounds"
    )

    assert item.horizon == "today"
    assert item.urgency == "high"

    assert (
        item.impacted_source_id
        == "grounds"
    )


def test_gp028_items_are_deterministically_sorted():
    items = get_owner_agenda_items()

    assert list(items) == sorted(
        items,
        key=owner_agenda_sort_key,
    )


def test_gp028_do_now_precedes_today():
    items = get_owner_agenda_items()

    horizons = [
        item.horizon
        for item in items
    ]

    if (
        "do_now" in horizons
        and "today" in horizons
    ):
        assert (
            horizons.index("do_now")
            < horizons.index("today")
        )


def test_gp028_every_item_has_soulaana_explanation():
    for item in get_owner_agenda_items():
        assert (
            item.soulaana_what_happened
        )

        assert (
            item.soulaana_what_it_means
        )

        assert (
            item.soulaana_why_now
        )

        assert (
            item.soulaana_if_we_wait
        )

        assert (
            item.soulaana_next_review
        )


def test_gp028_no_item_executes():
    for item in get_owner_agenda_items():
        assert (
            item.automatic_action_performed
            is False
        )

        assert (
            item.downstream_execution_performed
            is False
        )


def test_gp028_horizon_filter():
    today = (
        get_owner_agenda_items_for_horizon(
            "today"
        )
    )

    assert today

    assert all(
        item.horizon == "today"
        for item in today
    )


def test_gp028_bad_horizon_fails_closed():
    with pytest.raises(KeyError):
        get_owner_agenda_items_for_horizon(
            "whenever"
        )


def test_gp028_missing_item_fails_closed():
    with pytest.raises(KeyError):
        get_owner_agenda_item(
            "missing-agenda-item"
        )


def test_gp028_sections_match_item_counts():
    sections = (
        get_owner_agenda_sections()
    )

    for section in sections:
        assert (
            section.item_count
            == len(section.items)
        )


def test_gp028_surface_counts_are_consistent():
    agenda = (
        get_executive_owner_agenda()
    )

    assert (
        agenda.item_count
        == len(agenda.items)
    )

    assert (
        agenda.item_count
        == (
            agenda.do_now_count
            + agenda.today_count
            + agenda.this_week_count
            + agenda.watching_count
            + agenda.waiting_count
            + agenda.can_wait_count
        )
    )


def test_gp028_surface_has_owner_focus():
    agenda = (
        get_executive_owner_agenda()
    )

    assert (
        agenda.soulaana_owner_focus
    )

    assert (
        "Start with"
        in agenda.soulaana_owner_focus
    )


def test_gp028_surface_protects_attention():
    agenda = (
        get_executive_owner_agenda()
    )

    assert (
        agenda
        .soulaana_attention_protection
    )

    assert (
        "false urgency"
        in agenda
        .soulaana_attention_protection
    )


def test_gp028_surface_executes_nothing():
    agenda = (
        get_executive_owner_agenda()
    )

    assert (
        agenda
        .automatic_action_performed
        is False
    )

    assert (
        agenda
        .downstream_execution_performed
        is False
    )


def test_gp028_payload_serializes():
    payload = (
        get_executive_owner_agenda_payload()
    )

    assert (
        payload["title"]
        == "Executive Owner Agenda"
    )

    assert len(
        payload["sections"]
    ) == 6

    assert (
        payload["item_count"]
        == len(payload["items"])
    )


def test_gp028_status_ready():
    status = (
        get_clouds_gp028_status_payload()
    )

    assert status["pack"] == "GP028"

    assert (
        status["phase"]
        == "CLOUDS_PHASE_II"
    )

    assert (
        status["status"]
        == "ready"
    )

    assert (
        status["safe_to_continue"]
        is True
    )

    assert (
        status["horizon_count"]
        == 6
    )

    assert (
        status["horizons"]
        == EXPECTED_HORIZONS
    )

    assert (
        status[
            "operating_change_item_count"
        ]
        == 2
    )

    assert (
        status[
            "cross_business_impact_item_count"
        ]
        >= 2
    )

    assert (
        status["do_now_count"]
        >= 1
    )

    assert (
        status["today_count"]
        >= 1
    )

    assert (
        status[
            "soulaana_explains_every_item"
        ]
        is True
    )

    assert (
        status[
            "attention_protection_enabled"
        ]
        is True
    )

    assert (
        status[
            "automatic_action_performed"
        ]
        is False
    )

    assert (
        status[
            "downstream_execution_performed"
        ]
        is False
    )

    assert (
        status[
            "capital_movement_performed"
        ]
        is False
    )

    assert (
        status[
            "tower_authority_changed"
        ]
        is False
    )

    assert status["next_pack"] == (
        "GP029 — OWNER DECISION PREP / "
        "DECISION PACKET SURFACE"
    )
