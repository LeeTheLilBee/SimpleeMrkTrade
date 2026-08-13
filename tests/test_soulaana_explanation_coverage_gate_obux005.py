from engine.soulaana_explanation_coverage_gate import (
    assess_canonical_explanation,
    enforce_new_surface_coverage,
    evaluate_calm_state,
)


def complete_explanation():
    return {
        "what_it_is": "AMD is being watched.",
        "what_it_means": "The setup is improving.",
        "why_it_matters": "Conditions are becoming more favorable.",
        "what_changed": "Momentum strengthened.",
        "needs_attention": "Watch confirmation.",
        "can_wait": "Entry can wait.",
        "next_action": "Continue monitoring.",
        "no_action_needed": True,
    }


def test_obux005_complete_new_surface_passes():

    result = assess_canonical_explanation(
        complete_explanation()
    )

    assert (
        result["coverage_ready"]
        is True
    )


def test_obux005_incomplete_new_surface_fails_closed():

    payload = complete_explanation()

    payload.pop(
        "why_it_matters"
    )

    result = enforce_new_surface_coverage(
        [
            payload
        ]
    )

    assert (
        result["coverage_gate_ready"]
        is False
    )

    assert (
        result["new_user_facing_states_may_ship_empty"]
        is False
    )


def test_obux005_interesting_does_not_equal_actionable():

    result = evaluate_calm_state(
        [
            {
                "label": "AMD",
                "interesting": True,
                "actionable": False,
                "urgent": False,
            },
            {
                "label": "NVDA",
                "interesting": True,
                "actionable": False,
                "urgent": False,
            },
        ]
    )

    assert (
        result["state"]
        == "CALM_NO_ACTION"
    )

    assert (
        result["no_action_needed"]
        is True
    )

    assert (
        result["interesting_equals_actionable"]
        is False
    )
