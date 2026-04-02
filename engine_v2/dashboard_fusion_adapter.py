from typing import Dict, List


def build_dashboard_fusion_view(fusion_payloads: List[Dict]) -> Dict:
    if not fusion_payloads:
        return {
            "dominant_symbol": None,
            "dashboard_posture": "stand_down",
            "dashboard_summary": "No fused opportunities available.",
        }

    sorted_payloads = sorted(
        fusion_payloads,
        key=lambda p: (
            p.get("command") == "deploy",
            p.get("final_state") == "actionable",
            p.get("threat_level") == "low",
        ),
        reverse=True,
    )

    lead = sorted_payloads[0]

    return {
        "dominant_symbol": lead.get("master_decision", {}).get("symbol"),
        "dashboard_posture": lead.get("command", "stand_down"),
        "dashboard_summary": lead.get("fusion_summary", ""),
        "blocked": lead.get("blocked", False),
    }
