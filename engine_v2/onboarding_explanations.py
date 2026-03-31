from typing import Dict, Any, List

from engine_v2.engine_helpers import _save_json, _load_json, now_iso
from engine_v2.experience_presets import load_experience_presets

ONBOARDING_FILE = "/content/SimpleeMrkTrade/data_v2/onboarding_modes.json"


def _safe_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _safe_list(value: Any) -> List[Any]:
    return value if isinstance(value, list) else []


def _build_mode_card(key: str, preset: Dict[str, Any]) -> Dict[str, Any]:
    preset = _safe_dict(preset)
    settings = _safe_dict(preset.get("settings"))

    return {
        "key": key,
        "label": preset.get("label", key.title()),
        "summary": preset.get("summary", ""),
        "why_use_it": _safe_list(preset.get("why_use_it", [])),
        "best_for": [],
        "what_changes": [
            f"Motion profile: {settings.get('motion_profile', 'full')}",
            f"Map intensity: {settings.get('map_intensity', 'standard')}",
            f"Visual density: {settings.get('visual_density', 'rich')}",
            f"Intervention sensitivity: {settings.get('intervention_sensitivity', 'standard')}",
        ],
        "recommended_when": "",
        "settings": settings,
    }


def build_onboarding_mode_explanations() -> Dict[str, Any]:
    presets_payload = load_experience_presets()
    presets = presets_payload.get("presets", {}) if isinstance(presets_payload, dict) else {}
    presets = presets if isinstance(presets, dict) else {}

    cards = {
        "balanced": _build_mode_card("balanced", presets.get("balanced", {})),
        "focus": _build_mode_card("focus", presets.get("focus", {})),
        "low_stim": _build_mode_card("low_stim", presets.get("low_stim", {})),
    }

    cards["balanced"]["best_for"] = [
        "Users who want the full system experience.",
        "People still exploring the platform.",
        "Default daily use.",
    ]
    cards["balanced"]["recommended_when"] = "Choose this when you want the full experience without reducing signal richness."

    cards["focus"]["best_for"] = [
        "Users who want less clutter.",
        "Decision-focused sessions.",
        "High-conviction setup review.",
    ]
    cards["focus"]["recommended_when"] = "Choose this when you want stronger prioritization and less noise."

    cards["low_stim"]["best_for"] = [
        "Users who get overwhelmed by visual intensity.",
        "Recovery periods after a lot of switching around.",
        "Calmer, lower-motion sessions.",
    ]
    cards["low_stim"]["recommended_when"] = "Choose this when you want a softer, calmer environment with more protective guidance."

    payload = {
        "modes": cards,
        "default_mode": "balanced",
        "meta": {
            "rebuilt_at": now_iso(),
            "mode_count": len(cards),
        },
    }

    _save_json(ONBOARDING_FILE, payload)
    return payload


def load_onboarding_mode_explanations() -> Dict[str, Any]:
    payload = _load_json(ONBOARDING_FILE, {})
    return payload if isinstance(payload, dict) else {}


def get_onboarding_mode_card(mode_key: str) -> Dict[str, Any]:
    payload = load_onboarding_mode_explanations()
    modes = payload.get("modes", {}) if isinstance(payload, dict) else {}
    modes = modes if isinstance(modes, dict) else {}

    mode_key = str(mode_key or "balanced").strip().lower()
    if mode_key in modes and isinstance(modes[mode_key], dict):
        return modes[mode_key]

    fallback = modes.get("balanced", {})
    return fallback if isinstance(fallback, dict) else {}
