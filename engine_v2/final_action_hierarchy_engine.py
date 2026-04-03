from typing import Dict


def resolve_final_action(
    base_decision: Dict,
    enhanced_integration: Dict,
    truth_integration: Dict,
    behavior_intelligence: Dict,
) -> Dict:
    base_action = str(base_decision.get("action", "wait") or "wait")

    enhanced_package = enhanced_integration.get("enhanced_package", {}) if isinstance(enhanced_integration, dict) else {}
    enhanced_summary = enhanced_package.get("enhanced_summary", {}) if isinstance(enhanced_package, dict) else {}
    enhanced_action = str(enhanced_summary.get("final_action", base_action) or base_action)

    truth_package = truth_integration.get("truth_package", {}) if isinstance(truth_integration, dict) else {}
    truth_summary = truth_package.get("truth_summary", {}) if isinstance(truth_package, dict) else {}
    truth_action = str(truth_summary.get("final_action", enhanced_action) or enhanced_action)

    behavior_override = behavior_intelligence.get("behavior_override", {}) if isinstance(behavior_intelligence, dict) else {}
    behavior_action = str(behavior_override.get("behavior_final_action", truth_action) or truth_action)

    final_action = base_action
    source = "base_decision"
    reason = "base decision remains valid"

    if truth_action == "reject":
        final_action = "reject"
        source = "truth_enforcement"
        reason = "truth enforcement has final authority"
    elif behavior_action == "reject":
        final_action = "reject"
        source = "behavior_override"
        reason = "behavioral guardrail blocked execution"
    elif behavior_action == "wait" and truth_action not in {"reject"}:
        final_action = "wait"
        source = "behavior_override"
        reason = "behavior override reduced action to wait"
    elif enhanced_action != base_action:
        final_action = enhanced_action
        source = "enhanced_soulaana"
        reason = "enhanced Soulaana judgment adjusted the base action"
    else:
        final_action = base_action
        source = "base_decision"
        reason = "no higher-priority layer overrode the action"

    return {
        "final_action": final_action,
        "final_action_source": source,
        "final_action_reason": reason,
    }
