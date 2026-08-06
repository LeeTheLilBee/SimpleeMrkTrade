from ob_owner_experience import (
    MUST_NOT_CLAIM,
    NEXT_OB_BUILD_ORDER,
    OB_REAL_SURFACE_THEME,
    PROTECTED_ROUTE_POLICY,
    SIX_ROOM_ORDER,
    UI_SURFACE_REGISTRY_IDENTITY,
    build_component_adapter_manifest,
    build_owner_walkthrough_hook_manifest,
    build_real_surface_adapter_contract,
    build_real_surface_registry,
    build_route_manifest,
    build_soulaana_surface_summary,
    build_surface_registry_entry,
    build_ui_registry_takeover_handoff,
    normalize_room_id,
)


def test_registry_identity_is_ready_for_ob_ui_wiring_not_staging():
    assert UI_SURFACE_REGISTRY_IDENTITY["package"] == "ob_six_room_real_surface_registry"
    assert UI_SURFACE_REGISTRY_IDENTITY["display_title"] == "Six-Room Real Surface Registry"
    assert UI_SURFACE_REGISTRY_IDENTITY["decision"] == (
        "READY_FOR_OB_UI_WIRING_WITH_SAFETY_LOCKS_HELD"
    )
    assert "STAGING_READY" in MUST_NOT_CLAIM


def test_surface_registry_has_all_six_rooms_in_order():
    registry = build_real_surface_registry()

    assert registry["room_count"] == 6
    assert registry["room_order"] == SIX_ROOM_ORDER
    assert [entry["room"] for entry in registry["entries"]] == SIX_ROOM_ORDER
    assert registry["theme"] == OB_REAL_SURFACE_THEME
    assert registry["safety_summary"]["broker_submission_enabled"] is False
    assert registry["safety_summary"]["real_capital_movement_enabled"] is False
    assert registry["safety_summary"]["live_auto_locked"] is True


def test_registry_entries_have_display_titles_headings_and_adapters():
    dashboard = build_surface_registry_entry("dashboard")
    market = build_surface_registry_entry("market-map")
    owner = build_surface_registry_entry("Owner Console")

    assert dashboard["display_title"] == "Today’s Command Nest"
    assert dashboard["hero_heading"] == "🌙 Today’s Command Nest"
    assert dashboard["soulaana_heading"] == "🧭 Soulaana Says"
    assert dashboard["component_hint"] == "DashboardTodayCommandNest"
    assert dashboard["data_adapter_hint"] == "build_dashboard_surface"

    assert market["display_title"] == "Market Weather"
    assert market["hero_heading"] == "🌦️ Market Weather"

    assert owner["display_title"] == "Owner Crown Room"
    assert owner["hero_heading"] == "👑 Owner Crown Room"
    assert owner["protected_route_policy"]["anonymous_access_allowed"] is False


def test_unknown_room_fails_closed():
    try:
        normalize_room_id("unknown room")
    except KeyError as exc:
        assert "Unknown OB real surface room" in str(exc)
    else:
        raise AssertionError("Unknown room should fail closed.")


def test_route_manifest_is_owner_session_only():
    manifest = build_route_manifest()

    assert len(manifest) == 6

    for route in manifest:
        assert route["owner_session_required"] is True
        assert route["anonymous_access_allowed"] is False
        assert route["tower_handoff_required"] is True
        assert route["dangerous_actions_require_step_up"] is True


def test_owner_walkthrough_hooks_are_stable():
    hooks = build_owner_walkthrough_hook_manifest()

    assert len(hooks) == 6
    assert [hook["room"] for hook in hooks] == SIX_ROOM_ORDER
    assert hooks[0]["acceptance_hook"] == "accept_dashboard_owner_surface"
    assert hooks[-1]["receipt_hook"] == "receipt_owner_console_owner_surface"

    for hook in hooks:
        assert hook["requires_owner_session"] is True
        assert hook["resume_key"].startswith("ob_walkthrough_")


def test_component_adapter_manifest_maps_each_room():
    manifest = build_component_adapter_manifest()

    assert list(manifest) == SIX_ROOM_ORDER
    assert manifest["dashboard"]["component_hint"] == "DashboardTodayCommandNest"
    assert manifest["market_map"]["component_hint"] == "MarketWeatherSurface"
    assert manifest["symbol_page"]["component_hint"] == "AssetStorybookSurface"
    assert manifest["trade_center"]["component_hint"] == "DecisionGardenSurface"
    assert manifest["review_center"]["component_hint"] == "ReflectionLibrarySurface"
    assert manifest["owner_console"]["component_hint"] == "OwnerCrownRoomSurface"


def test_adapter_contract_is_ready_for_ui_wiring_only():
    contract = build_real_surface_adapter_contract()

    assert contract["package"] == "ob_six_room_real_surface_registry"
    assert contract["ready_for_ob_ui_wiring"] is True
    assert contract["ready_for_tower_integration_review"] is True
    assert contract["ready_for_owner_walkthrough"] is False
    assert contract["staging_ready"] is False
    assert contract["protected_route_policy"] == PROTECTED_ROUTE_POLICY
    assert "STAGING_READY" in contract["must_not_claim"]
    assert "Tower return/session continuity repaired" in contract["must_not_claim"]
    assert "GP002 Dashboard real surface wiring" in contract["next_ob_build_order"]


def test_soulaana_surface_summary_warns_against_unlocks():
    summary = build_soulaana_surface_summary()

    assert summary["soulaana_visible"] is True
    assert "six simplified owner rooms" in summary["what_you_are_looking_at"].lower()
    assert "GP002 Dashboard real surface wiring" in summary["focus_on"]
    assert "broker submission" in summary["safe_to_ignore_for_now"]
    assert "Live Auto unlock" in summary["safe_to_ignore_for_now"]


def test_takeover_handoff_preserves_next_schedule_and_safety():
    handoff = build_ui_registry_takeover_handoff()

    assert handoff["display_title"] == "Six-Room Real Surface Registry"
    assert handoff["room_order"] == SIX_ROOM_ORDER
    assert handoff["safety_summary"]["broker_submission_enabled"] is False
    assert handoff["safety_summary"]["real_capital_movement_enabled"] is False
    assert handoff["safety_summary"]["live_auto_locked"] is True
    assert handoff["next_ob_build_order"] == NEXT_OB_BUILD_ORDER
    assert "Do not claim STAGING_READY." in handoff["next_builder_notes"]
