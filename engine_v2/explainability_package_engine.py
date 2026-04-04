from typing import Dict

from engine_v2.explanation_summary_engine import build_explanation_summary
from engine_v2.pressure_breakdown_engine import build_pressure_breakdown
from engine_v2.override_explanation_engine import build_override_explanation
from engine_v2.memory_takeaway_engine import build_memory_takeaway


def build_explainability_package(final_brain: Dict) -> Dict:
    summary = build_explanation_summary(final_brain)
    pressure = build_pressure_breakdown(final_brain)
    override = build_override_explanation(final_brain)
    memory = build_memory_takeaway(final_brain)

    return {
        "summary": summary,
        "pressure": pressure,
        "override": override,
        "memory": memory,
        "explainability_package": {
            "headline": summary.get("explanation_verdict", "No verdict available."),
            "subheadline": summary.get("explanation_insight", "No insight available."),
            "summary_line": summary.get("explanation_summary_line", ""),
            "story": summary.get("explanation_story", ""),
            "supportive_pressures": pressure.get("supportive_pressures", []),
            "restrictive_pressures": pressure.get("restrictive_pressures", []),
            "pressure_balance": pressure.get("pressure_balance", "mixed"),
            "override_line": override.get("override_line", ""),
            "override_reason": override.get("override_reason", ""),
            "memory_takeaway": memory.get("memory_takeaway", ""),
        },
    }
