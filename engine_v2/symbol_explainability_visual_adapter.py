from typing import Dict

from engine_v2.explainability_package_engine import build_explainability_package
from engine_v2.explainability_tone_engine import build_explainability_tone
from engine_v2.pressure_visual_engine import build_pressure_visuals
from engine_v2.override_severity_engine import build_override_severity


def build_symbol_explainability_visuals(final_brain: Dict) -> Dict:
    explainability = build_explainability_package(final_brain)
    package = explainability.get("explainability_package", {}) if isinstance(explainability.get("explainability_package", {}), dict) else {}

    tone = build_explainability_tone(final_brain, explainability)
    pressure_visuals = build_pressure_visuals(explainability)
    override_visuals = build_override_severity(explainability)

    return {
        "headline": package.get("headline", ""),
        "subheadline": package.get("subheadline", ""),
        "summary_line": package.get("summary_line", ""),
        "story": package.get("story", ""),
        "supportive_pressures": package.get("supportive_pressures", []),
        "restrictive_pressures": package.get("restrictive_pressures", []),
        "memory_takeaway": package.get("memory_takeaway", ""),
        "override_line": package.get("override_line", ""),
        "override_reason": package.get("override_reason", ""),
        **tone,
        **pressure_visuals,
        **override_visuals,
    }
