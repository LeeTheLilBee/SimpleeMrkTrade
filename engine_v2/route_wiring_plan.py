from typing import Any, Dict, List

from engine_v2.engine_helpers import _save_json, _load_json, now_iso

ROUTE_WIRING_FILE = "/content/SimpleeMrkTrade/data_v2/route_wiring_plan.json"


def build_route_wiring_plan() -> Dict[str, Any]:
    routes: List[Dict[str, Any]] = [
        {
            "route": "/dashboard",
            "target_contract": "dashboard_contract.json",
            "builder": "build_dashboard_contract(username)",
            "status": "ready",
            "notes": "Main command center should read the Stage 5 dashboard contract.",
        },
        {
            "route": "/spotlight",
            "target_contract": "spotlight_page_contract.json",
            "builder": "build_spotlight_page_contract(username)",
            "status": "ready",
            "notes": "Dedicated spotlight page should be driven by the spotlight page contract.",
        },
        {
            "route": "/market-map",
            "target_contract": "market_map.json + market_map_interaction_contract.json + map_layer_toggle_contract.json",
            "builder": "build_market_map() + build_market_map_interaction_contract() + build_map_layer_toggle_contract()",
            "status": "ready",
            "notes": "Map page should combine tiles, interactions, and layer toggles.",
        },
        {
            "route": "/signals/<symbol>",
            "target_contract": "symbol_hero_contract.json + symbol_deep_dive_contract.json + horizontal_hero_contract.json",
            "builder": "build_symbol_hero_contract(symbol) + build_symbol_deep_dive_contract(symbol) + build_horizontal_hero_contract()",
            "status": "ready",
            "notes": "Symbol page should use the deep-dive stack and horizontal hero strip.",
        },
        {
            "route": "/research/rejections",
            "target_contract": "rejection_feed.json",
            "builder": "build_rejection_feed()",
            "status": "ready",
            "notes": "Passed-over research page should be powered by rejection intelligence.",
        },
        {
            "route": "/settings",
            "target_contract": "experience_presets.json + onboarding_modes.json",
            "builder": "build_experience_presets() + build_onboarding_mode_explanations()",
            "status": "ready",
            "notes": "Settings and onboarding should reuse the adaptive UX contracts.",
        },
        {
            "route": "/admin/diagnostics",
            "target_contract": "integration_status_contract.json",
            "builder": "build_integration_status_contract()",
            "status": "ready",
            "notes": "Admin diagnostics should expose integration progress and readiness.",
        },
    ]

    payload = {
        "routes": routes,
        "summary": {
            "route_count": len(routes),
            "ready_count": sum(1 for row in routes if row.get("status") == "ready"),
        },
        "meta": {
            "rebuilt_at": now_iso(),
        },
    }

    _save_json(ROUTE_WIRING_FILE, payload)
    return payload


def load_route_wiring_plan() -> Dict[str, Any]:
    payload = _load_json(ROUTE_WIRING_FILE, {})
    return payload if isinstance(payload, dict) else {}
