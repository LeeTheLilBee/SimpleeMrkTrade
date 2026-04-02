from typing import Dict


def build_fusion_summary(master_decision: Dict) -> Dict:
    symbol = master_decision.get("symbol", "")
    final_state = master_decision.get("final_state", "unknown")
    thesis_statement = (
        master_decision.get("thesis", {})
        .get("thesis", {})
        .get("thesis_statement", "")
    )
    threat_level = master_decision.get("threat_level", "low")
    timeline_phase = master_decision.get("timeline", {}).get("timeline_phase", "unknown")

    summary = (
        f"{symbol} is currently in {final_state} state. "
        f"Timeline phase is {timeline_phase}. "
        f"Threat level is {threat_level}. "
        f"{thesis_statement}"
    ).strip()

    return {
        "fusion_summary": summary
    }
