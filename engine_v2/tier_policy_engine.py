from typing import Dict


def get_tier_policy(tier: str) -> Dict:
    normalized = str(tier or "free").strip().lower()

    policies = {
        "free": {
            "show_score": False,
            "show_reasons_count": 1,
            "show_narrative": False,
            "show_system_flags": False,
            "show_highlights_count": 2,
            "show_grade": False,
            "show_confidence": True,
            "voice_mode": "simple",
        },
        "starter": {
            "show_score": True,
            "show_reasons_count": 2,
            "show_narrative": False,
            "show_system_flags": False,
            "show_highlights_count": 3,
            "show_grade": True,
            "show_confidence": True,
            "voice_mode": "guided",
        },
        "pro": {
            "show_score": True,
            "show_reasons_count": 3,
            "show_narrative": True,
            "show_system_flags": True,
            "show_highlights_count": 3,
            "show_grade": True,
            "show_confidence": True,
            "voice_mode": "analytical",
        },
        "elite": {
            "show_score": True,
            "show_reasons_count": 99,
            "show_narrative": True,
            "show_system_flags": True,
            "show_highlights_count": 99,
            "show_grade": True,
            "show_confidence": True,
            "voice_mode": "full",
        },
    }

    return policies.get(normalized, policies["free"])
