from engine.soulaana_universal_contract import (
    canonicalize_soulaana_payload,
)


def test_obux001_maps_existing_legacy_fields_without_destroying_them():

    result = canonicalize_soulaana_payload(
        {
            "headline": "AMD signal reviewed",
            "verdict": "WATCH",
            "assessment": "Momentum is improving.",
            "why": "Multiple confirmation layers improved.",
            "risk": "Entry confirmation is not complete.",
            "next_action": "Continue monitoring.",
        },
        context={
            "what_changed": "Momentum strengthened.",
            "can_wait": "Entry can wait for confirmation.",
        },
    )

    assert (
        result["canonical"]["what_it_is"]
        == "AMD signal reviewed"
    )

    assert (
        result["canonical"]["what_it_means"]
        == "Momentum is improving."
    )

    assert (
        result["canonical"]["why_it_matters"]
        == "Multiple confirmation layers improved."
    )

    assert (
        result["canonical"]["what_changed"]
        == "Momentum strengthened."
    )

    assert (
        result["canonical"]["no_action_needed"]
        is True
    )

    assert (
        result["legacy_compatibility"]["verdict"]
        == "WATCH"
    )

    assert (
        result["parallel_soulaana_engine_created"]
        is False
    )


def test_obux001_tracks_missing_source_explanations_instead_of_hiding_them():

    result = canonicalize_soulaana_payload(
        {
            "headline": "Account reviewed",
        }
    )

    assert (
        result["source_complete"]
        is False
    )

    assert (
        result["source_gap_count"]
        > 0
    )

    assert (
        "why_it_matters"
        in result["source_gaps"]
    )
