from typing import Dict, List


def build_spotlight_fusion_cards(fusion_payloads: List[Dict]) -> Dict:
    cards = []

    for payload in fusion_payloads:
        master = payload.get("master_decision", {})
        command = payload.get("command_object", {})
        summary = payload.get("fusion_summary", "")

        cards.append({
            "symbol": master.get("symbol"),
            "company_name": master.get("company_name"),
            "final_state": master.get("final_state", "unknown"),
            "command": command.get("command", "stand_down"),
            "threat_level": command.get("threat_level", "low"),
            "timeline_phase": command.get("timeline_phase", "unknown"),
            "summary": summary,
        })

    cards = sorted(
        cards,
        key=lambda c: (
            c.get("command") == "deploy",
            c.get("final_state") == "actionable",
            c.get("threat_level") == "low",
        ),
        reverse=True,
    )

    return {
        "spotlight_cards": cards
    }
