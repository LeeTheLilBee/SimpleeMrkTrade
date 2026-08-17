from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
JS = (
    ROOT / "web/static/ob/ob_owner_dashboard_soulaana.js"
).read_text(encoding="utf-8")


def test_obux022_soulaana_is_the_owner_interpretation_layer():
    assert "SOULAANA · OWNER BRIEFING" in JS
    assert "what_i_see" in JS
    assert "your_missions" in JS
    assert "what_needs_you" in JS
    assert "readiness" in JS
    assert "system_trust" in JS
    assert "beta_state" in JS
    assert "what_changed" in JS
    assert "what_im_learning" in JS
    assert "what_can_wait" in JS
    assert "next_best_move" in JS
    assert "no_action_needed" in JS


def test_obux022_soulaana_refuses_to_invent_owner_truth():
    assert "I will not fake the missing truth." in JS
    assert "I will not pretend a goal is closer than the evidence proves." in JS
    assert "I will not invent a 'since you were here' story." in JS
    assert "I do not have enough verified cross-mission performance evidence" in JS


def test_obux022_owner_dashboard_role_is_distinct():
    assert "Normal Dashboard asks what is happening in the market." in JS
    assert "Owner Dashboard asks what is happening across your Observatory." in JS
    assert "broker_action_performed: false" in JS
    assert "capital_action_performed: false" in JS
    assert "permission_mutation_performed: false" in JS
    assert "live_auto_locked: true" in JS
