from typing import Dict


def build_final_narrative(
    base_explainability: Dict,
    enhanced_integration: Dict,
    truth_integration: Dict,
    causality_intelligence: Dict,
    counterfactual_intelligence: Dict,
) -> Dict:
    enhanced_voice = enhanced_integration.get("enhanced_voice", {}) if isinstance(enhanced_integration, dict) else {}
    truth_override = truth_integration.get("truth_override", {}) if isinstance(truth_integration, dict) else {}
    truth_package = truth_integration.get("truth_package", {}) if isinstance(truth_integration, dict) else {}
    truth_summary = truth_package.get("truth_summary", {}) if isinstance(truth_package, dict) else {}

    causality_explainer = causality_intelligence.get("causality_explainer", {}) if isinstance(causality_intelligence, dict) else {}
    counterfactual_explainer = counterfactual_intelligence.get("counterfactual_explainer", {}) if isinstance(counterfactual_intelligence, dict) else {}

    final_verdict = str(
        truth_override.get("truth_verdict")
        or enhanced_voice.get("enhanced_verdict")
        or base_explainability.get("message")
        or "No final verdict available."
    )

    final_insight = str(
        truth_override.get("truth_insight")
        or enhanced_voice.get("enhanced_insight")
        or base_explainability.get("narrative")
        or "No final insight available."
    )

    causality_line = str(causality_explainer.get("causality_line", "") or "")
    counterfactual_line = str(counterfactual_explainer.get("counterfactual_line", "") or "")

    merged_story = " ".join(
        part for part in [
            final_insight,
            causality_line,
            counterfactual_line,
        ] if part
    ).strip()

    return {
        "final_verdict": final_verdict,
        "final_insight": final_insight,
        "causality_line": causality_line,
        "counterfactual_line": counterfactual_line,
        "merged_story": merged_story,
        "final_reasons": truth_summary.get("reasons", []),
    }
