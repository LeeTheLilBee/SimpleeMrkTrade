from typing import Dict

from engine_v2.explainability_package_engine import build_explainability_package


def build_symbol_explainability_context(final_brain: Dict) -> Dict:
    explainability = build_explainability_package(final_brain)
    package = explainability.get("explainability_package", {}) if isinstance(explainability.get("explainability_package", {}), dict) else {}

    return {
        "explainability_headline": package.get("headline", "No explainability headline available."),
        "explainability_subheadline": package.get("subheadline", "No explainability subheadline available."),
        "explainability_summary_line": package.get("summary_line", ""),
        "explainability_story": package.get("story", ""),
        "supportive_pressures": package.get("supportive_pressures", []),
        "restrictive_pressures": package.get("restrictive_pressures", []),
        "pressure_balance": package.get("pressure_balance", "mixed"),
        "override_line": package.get("override_line", ""),
        "override_reason": package.get("override_reason", ""),
        "memory_takeaway": package.get("memory_takeaway", ""),
        "raw_explainability": explainability,
    }
