from typing import Dict, List


def shape_voice_by_tier(
    verdict: str,
    command: str,
    message: str,
    narrative: str,
    reasons: List[str],
    voice_mode: str,
) -> Dict:
    if voice_mode == "simple":
        return {
            "verdict": verdict,
            "command": command,
            "message": message,
            "narrative": "",
            "reasons": reasons[:1],
        }

    if voice_mode == "guided":
        return {
            "verdict": verdict,
            "command": command,
            "message": message,
            "narrative": "",
            "reasons": reasons[:2],
        }

    if voice_mode == "analytical":
        return {
            "verdict": verdict,
            "command": command,
            "message": message,
            "narrative": narrative,
            "reasons": reasons[:3],
        }

    return {
        "verdict": verdict,
        "command": command,
        "message": message,
        "narrative": narrative,
        "reasons": reasons,
    }
