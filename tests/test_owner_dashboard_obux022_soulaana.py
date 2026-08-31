from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

JS = (
    ROOT / "web/static/ob/ob_owner_dashboard_soulaana.js"
).read_text(
    encoding="utf-8",
    errors="replace",
)


def test_obux022_soulaana_remains_owner_interpretation_layer():
    for marker in [
        "SOULAANA · OWNER BRIEFING",
        "what_i_see",
        "why_it_matters",
        "capital_read",
        "what_needs_you",
        "what_changed",
        "what_im_learning",
        "what_can_wait",
        "next_best_move",
        "no_action_needed",
        "owner_altitude",
        "evidence_rule",
    ]:
        assert marker in JS


def test_obux022_soulaana_refuses_to_invent_owner_truth():
    for marker in [
        "Some truth is still guarded.",
        "Unverified balances stay unverified.",
        "Nothing verified is forcing an owner decision.",
        "No forced move. Pick a Capital Lane",
        "I would rather show you less than invent certainty.",
        "Short answer first.",
    ]:
        assert marker in JS


def test_obux022_owner_dashboard_role_is_now_research_plus_capital_context():
    assert (
        "Normal Dashboard watches the Observatory."
        in JS
    )

    assert (
        "Owner Dashboard organizes your capital context"
        in JS
    )

    assert (
        "your private research intelligence."
        in JS
    )

    assert (
        "Deeper evidence stays collapsed until you ask."
        in JS
    )
