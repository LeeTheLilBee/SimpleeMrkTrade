from typing import Any, Dict, List

from engine_v2.engine_helpers import _save_json, _load_json, now_iso

LAYER_FILE = "/content/SimpleeMrkTrade/data_v2/map_layer_toggle_contract.json"


def build_map_layer_toggle_contract() -> Dict[str, Any]:
    payload = {
        "default_layer": "pressure",
        "layers": [
            {
                "key": "pressure",
                "label": "Pressure",
                "summary": "Shows where the strongest visual pressure is building.",
                "best_for": "Quick market scanning",
            },
            {
                "key": "confidence",
                "label": "Confidence",
                "summary": "Shows where the system has the highest belief in the setup.",
                "best_for": "Decision quality review",
            },
            {
                "key": "lane",
                "label": "Lane",
                "summary": "Separates equity intelligence from options intelligence.",
                "best_for": "Understanding how the system is framing the idea",
            },
            {
                "key": "bucket",
                "label": "Bucket",
                "summary": "Groups the map into calmer category zones like energy, tech, finance, and healthcare.",
                "best_for": "Big-picture sector scanning",
            },
        ],
        "interaction_model": {
            "single_select": True,
            "allow_quick_switch": True,
            "persist_user_choice": True,
            "calm_mode_prefers": "pressure",
        },
        "meta": {
            "rebuilt_at": now_iso(),
            "layer_count": 4,
        },
    }

    _save_json(LAYER_FILE, payload)
    return payload


def load_map_layer_toggle_contract() -> Dict[str, Any]:
    payload = _load_json(LAYER_FILE, {})
    return payload if isinstance(payload, dict) else {}
