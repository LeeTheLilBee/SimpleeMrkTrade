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
        "capital_read",
        "what_needs_you",
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
        "Short answer first.",
    ]:
        assert marker in JS


def test_obux022_owner_dashboard_role_remains_distinct():
    assert (
        "Normal Dashboard watches the Observatory."
        in JS
    )

    assert (
        "Owner Dashboard organizes your capital context."
        in JS
    )

    assert (
        "Deeper evidence stays collapsed until you ask."
        in JS
    )
