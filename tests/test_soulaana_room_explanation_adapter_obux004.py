import pytest

from engine_v2.soulaana_room_explanation_adapter import (
    ROOM_CONTRACTS,
    build_room_soulaana_experience,
)


@pytest.mark.parametrize(
    "room",
    list(
        ROOM_CONTRACTS.keys()
    ),
)
def test_obux004_all_six_rooms_have_explanation_contracts(
    room,
):

    role = (
        "owner"
        if room == "Owner Console"
        else
        "tester"
    )

    result = build_room_soulaana_experience(
        room,
        {
            "subject": room,
            "soulaana": {
                "headline": f"{room} reviewed",
                "assessment": "Soulaana understands the current state.",
                "why": "The room has meaningful user-facing information.",
                "risk": "Nothing urgent is hidden.",
                "next_action": "Continue monitoring.",
            },
            "key_facts": [],
            "actions": [],
            "visuals": [],
            "technical_evidence": [],
        },
        {
            "role": role,
            "mode": "Paper",
            "account": "Proof/Demo",
            "tower_clearance": True,
        },
    )

    assert (
        result["allowed"]
        is True
    )

    assert (
        result["soulaana_leads_surface"]
        is True
    )

    assert (
        result["sections"][0]["id"]
        == "soulaana"
    )

    assert (
        result["sections"][-1]["id"]
        == "evidence"
    )

    assert (
        result["sections"][-1]["default_open"]
        is False
    )


def test_obux004_detects_existing_empty_soulaana_slot():

    result = build_room_soulaana_experience(
        "Dashboard",
        {
            "subject": "Dashboard",
            "soulaana": {},
        },
        {
            "role": "owner",
            "mode": "Paper",
            "account": "Personal",
            "tower_clearance": True,
        },
    )

    assert (
        result["source_soulaana_empty"]
        is True
    )
