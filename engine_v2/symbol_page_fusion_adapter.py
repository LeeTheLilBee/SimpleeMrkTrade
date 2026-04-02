from typing import Dict


def build_symbol_page_fusion_view(product_fusion: Dict) -> Dict:
    master = product_fusion.get("master_decision", {})
    command = product_fusion.get("command_object", {})
    summary = product_fusion.get("fusion_summary", "")

    thesis_statement = (
        master.get("thesis", {})
        .get("thesis", {})
        .get("thesis_statement", "")
    )

    confirmations = (
        master.get("thesis", {})
        .get("confirmations", {})
        .get("confirmations", [])
    )

    invalidation = (
        master.get("thesis", {})
        .get("invalidation", {})
        .get("invalidation", [])
    )

    return {
        "hero_summary": summary,
        "hero_state": master.get("final_state", "unknown"),
        "hero_command": command.get("command", "stand_down"),
        "hero_threat": command.get("threat_level", "low"),
        "hero_timeline": command.get("timeline_phase", "unknown"),
        "hero_next_action": command.get("next_action", "wait"),
        "thesis_statement": thesis_statement,
        "confirmations": confirmations,
        "invalidation": invalidation,
        "fusion_issues": master.get("conflicts", {}).get("issues", []),
    }
