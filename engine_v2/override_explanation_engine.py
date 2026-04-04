from typing import Dict


def build_override_explanation(final_brain: Dict) -> Dict:
    action_resolution = final_brain.get("final_action_resolution", {}) if isinstance(final_brain, dict) else {}
    confidence_resolution = final_brain.get("final_confidence_resolution", {}) if isinstance(final_brain, dict) else {}
    final_output = final_brain.get("final_output", {}) if isinstance(final_brain, dict) else {}
    truth_notes = final_output.get("truth_notes", {}) if isinstance(final_output, dict) else {}
    behavior_notes = final_output.get("behavior_notes", {}) if isinstance(final_output, dict) else {}
    behavior_override = behavior_notes.get("behavior_override", {}) if isinstance(behavior_notes.get("behavior_override", {}), dict) else {}

    action_source = str(action_resolution.get("final_action_source", "base_decision") or "base_decision")
    action_reason = str(action_resolution.get("final_action_reason", "No override reason available.") or "No override reason available.")
    confidence_source = str(confidence_resolution.get("final_confidence_source", "base_decision") or "base_decision")

    override_state = "none"
    override_line = "No higher-priority layer overrode the base decision."

    if action_source == "truth_enforcement":
        override_state = "truth_override"
        override_line = "Truth enforcement overrode the original idea."
    elif action_source == "behavior_override":
        override_state = "behavior_override"
        override_line = "Behavior protection overrode the original idea."
    elif action_source == "enhanced_soulaana":
        override_state = "judgment_override"
        override_line = "Enhanced Soulaana adjusted the original idea."

    if truth_notes.get("hard_reject"):
        override_state = "hard_reject"
        override_line = "The setup was hard-rejected by the final truth layer."

    if behavior_override.get("behavior_override") and override_state == "none":
        override_state = "behavior_override"
        override_line = "Behavior protection changed the final output."

    return {
        "override_state": override_state,
        "override_line": override_line,
        "override_action_source": action_source,
        "override_confidence_source": confidence_source,
        "override_reason": action_reason,
    }
