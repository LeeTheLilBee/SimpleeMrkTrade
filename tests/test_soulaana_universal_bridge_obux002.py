from engine.soulaana_universal_bridge import (
    build_universal_soulaana,
)


def test_obux002_can_wrap_existing_soulaana_payload():

    result = build_universal_soulaana(
        {
            "symbol": "AMD",
        },
        existing_payload={
            "headline": "AMD reviewed",
            "verdict": "WATCH",
            "assessment": "The setup is improving.",
            "why": "Confirmation improved.",
            "risk": "Entry is not confirmed.",
            "next_action": "Continue monitoring.",
        },
    )

    assert (
        result["existing_payload_used"]
        is True
    )

    assert (
        result["existing_soulaana_core_preserved"]
        is True
    )

    assert (
        result["parallel_intelligence_system_created"]
        is False
    )

    assert (
        result["universal"]["canonical"]["what_it_is"]
        == "AMD reviewed"
    )


def test_obux002_preserves_fusion_and_voice_architecture():

    result = build_universal_soulaana(
        {
            "subject": "Test state",
        },
        existing_payload={
            "headline": "Test state",
            "assessment": "State understood.",
            "why": "Because this is a test.",
            "risk": "None.",
            "next_action": "Continue monitoring.",
        },
    )

    assert (
        result["voice_layer_preserved"]
        is True
    )

    assert (
        result["explainability_layer_preserved"]
        is True
    )

    assert (
        result["fusion_layer_available"]
        is True
    )
