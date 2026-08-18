from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

SOULAANA = (
    ROOT / "web/static/ob/ob_market_map_soulaana.js"
).read_text(encoding="utf-8")

MAP_JS = (
    ROOT / "web/static/ob/ob_market_map.js"
).read_text(encoding="utf-8")


def test_obux033_soulaana_explains_full_market_map_read():
    for marker in [
        "what_i_see",
        "what_it_means",
        "what_changed",
        "what_needs_you",
        "what_can_wait",
        "next_best_move",
        "no_action_needed",
    ]:
        assert marker in SOULAANA


def test_obux033_soulaana_refuses_fake_truth():
    # The runtime sentence is assembled from adjacent JS string
    # fragments. Test the literal source fragments rather than requiring
    # a substring that does not exist contiguously in the JS file.
    assert "I am leaving the sky " in SOULAANA
    assert "quiet instead of carrying old stars forward." in SOULAANA

    assert "It is not a prediction" in SOULAANA
    assert "Attention is not permission" in SOULAANA


def test_obux033_live_change_detection_exists():
    assert "describeChange" in MAP_JS

    assert (
        "The latest canonical feed refresh did not materially "
        in MAP_JS
    )

    assert (
        "I cleared the prior sky instead of carrying stale visual truth forward"
        in MAP_JS
    )


def test_obux033_no_action_state_exists():
    assert "Nothing needs market action from this room" in SOULAANA
    assert "No move is required" in SOULAANA
