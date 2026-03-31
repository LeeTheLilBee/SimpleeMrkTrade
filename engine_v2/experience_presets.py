from typing import Dict, Any

from engine_v2.engine_helpers import _save_json, _load_json, now_iso

PRESETS_FILE = "/content/SimpleeMrkTrade/data_v2/experience_presets.json"

EXPERIENCE_PRESETS = {
    "balanced": {
        "key": "balanced",
        "label": "Balanced Mode",
        "summary": "A full-featured experience with normal motion, full context, and standard visual intensity.",
        "why_use_it": [
            "Best default for most users.",
            "Keeps the system rich without being too stripped down.",
            "Good when you want the full experience."
        ],
        "settings": {
            "experience_mode": "balanced",
            "motion_profile": "full",
            "sidebar_collapsed": False,
            "map_intensity": "standard",
            "focus_filter": "off",
            "visual_density": "rich",
            "intervention_sensitivity": "standard",
        },
    },
    "focus": {
        "key": "focus",
        "label": "Focus Mode",
        "summary": "A cleaner view that dims the noise and emphasizes the strongest ideas and most relevant information.",
        "why_use_it": [
            "Helpful when you want less clutter.",
            "Pushes the strongest setups to the front.",
            "Good when you want to make cleaner decisions faster."
        ],
        "settings": {
            "experience_mode": "focus",
            "motion_profile": "reduced",
            "sidebar_collapsed": True,
            "map_intensity": "focused",
            "focus_filter": "high_conviction",
            "visual_density": "medium",
            "intervention_sensitivity": "standard",
        },
    },
    "low_stim": {
        "key": "low_stim",
        "label": "Low Stim Mode",
        "summary": "A calmer experience with softer motion, less visual pull, and more protective guidance when activity starts to spike.",
        "why_use_it": [
            "Helpful when the platform starts to feel too intense.",
            "Reduces motion and visual pull.",
            "Pairs well with overload detection and recovery prompts."
        ],
        "settings": {
            "experience_mode": "low_stim",
            "motion_profile": "minimal",
            "sidebar_collapsed": True,
            "map_intensity": "calm",
            "focus_filter": "guided",
            "visual_density": "light",
            "intervention_sensitivity": "high",
        },
    },
}


def build_experience_presets() -> Dict[str, Any]:
    payload = {
        "presets": EXPERIENCE_PRESETS,
        "default_preset": "balanced",
        "meta": {
            "rebuilt_at": now_iso(),
            "preset_count": len(EXPERIENCE_PRESETS),
        },
    }
    _save_json(PRESETS_FILE, payload)
    return payload


def load_experience_presets() -> Dict[str, Any]:
    payload = _load_json(PRESETS_FILE, {})
    return payload if isinstance(payload, dict) else {}


def get_experience_preset(preset_key: str) -> Dict[str, Any]:
    payload = load_experience_presets()
    presets = payload.get("presets", {}) if isinstance(payload, dict) else {}
    if not isinstance(presets, dict):
        presets = {}

    preset_key = str(preset_key or "balanced").strip().lower()
    if preset_key in presets:
        preset = presets.get(preset_key, {})
        return preset if isinstance(preset, dict) else {}

    fallback = presets.get("balanced", {})
    return fallback if isinstance(fallback, dict) else {}
