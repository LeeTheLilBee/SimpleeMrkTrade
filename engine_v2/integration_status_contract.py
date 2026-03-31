from pathlib import Path
from typing import Any, Dict

from engine_v2.engine_helpers import _save_json, _load_json, now_iso

INTEGRATION_STATUS_FILE = "/content/SimpleeMrkTrade/data_v2/integration_status_contract.json"


def _exists(path: str) -> bool:
    return Path(path).exists()


def build_integration_status_contract() -> Dict[str, Any]:
    checks = {
        "stage_1_core_system": all([
            _exists("/content/SimpleeMrkTrade/engine_v2/user_defaults.py"),
            _exists("/content/SimpleeMrkTrade/engine_v2/ui_state.py"),
            _exists("/content/SimpleeMrkTrade/engine_v2/mode_router.py"),
            _exists("/content/SimpleeMrkTrade/engine_v2/behavior_state.py"),
            _exists("/content/SimpleeMrkTrade/engine_v2/intervention_queue.py"),
            _exists("/content/SimpleeMrkTrade/engine_v2/overload_detection.py"),
        ]),
        "stage_2_engine_split": all([
            _exists("/content/SimpleeMrkTrade/engine_v2/engine_helpers.py"),
            _exists("/content/SimpleeMrkTrade/engine_v2/equity_engine.py"),
            _exists("/content/SimpleeMrkTrade/engine_v2/options_engine.py"),
            _exists("/content/SimpleeMrkTrade/engine_v2/hybrid_engine.py"),
        ]),
        "stage_3_output_layer": all([
            _exists("/content/SimpleeMrkTrade/engine_v2/spotlight_builder.py"),
            _exists("/content/SimpleeMrkTrade/engine_v2/market_map_builder.py"),
            _exists("/content/SimpleeMrkTrade/engine_v2/rejection_builder.py"),
        ]),
        "stage_4_adaptive_ux": all([
            _exists("/content/SimpleeMrkTrade/engine_v2/experience_presets.py"),
            _exists("/content/SimpleeMrkTrade/engine_v2/onboarding_explanations.py"),
            _exists("/content/SimpleeMrkTrade/engine_v2/preference_actions.py"),
        ]),
        "stage_5_dashboard_nav": all([
            _exists("/content/SimpleeMrkTrade/engine_v2/dashboard_contract.py"),
            _exists("/content/SimpleeMrkTrade/engine_v2/spotlight_page_contract.py"),
            _exists("/content/SimpleeMrkTrade/engine_v2/left_rail_contract.py"),
            _exists("/content/SimpleeMrkTrade/engine_v2/symbol_hero_contract.py"),
        ]),
        "stage_6_map_symbol_experience": all([
            _exists("/content/SimpleeMrkTrade/engine_v2/market_map_interaction_contract.py"),
            _exists("/content/SimpleeMrkTrade/engine_v2/map_layer_toggle_contract.py"),
            _exists("/content/SimpleeMrkTrade/engine_v2/symbol_deep_dive_contract.py"),
            _exists("/content/SimpleeMrkTrade/engine_v2/horizontal_hero_contract.py"),
        ]),
        "stage_7_behavior_coaching": all([
            _exists("/content/SimpleeMrkTrade/engine_v2/behavior_event_log.py"),
            _exists("/content/SimpleeMrkTrade/engine_v2/coaching_summary.py"),
            _exists("/content/SimpleeMrkTrade/engine_v2/pattern_detection.py"),
            _exists("/content/SimpleeMrkTrade/engine_v2/lesson_feed.py"),
        ]),
    }

    completed_count = sum(1 for v in checks.values() if v)

    payload = {
        "checks": checks,
        "summary": {
            "completed_group_count": completed_count,
            "total_group_count": len(checks),
            "ready_for_route_wiring": completed_count >= 7,
        },
        "meta": {
            "rebuilt_at": now_iso(),
        },
    }

    _save_json(INTEGRATION_STATUS_FILE, payload)
    return payload


def load_integration_status_contract() -> Dict[str, Any]:
    payload = _load_json(INTEGRATION_STATUS_FILE, {})
    return payload if isinstance(payload, dict) else {}
