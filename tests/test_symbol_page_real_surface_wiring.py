from ob_owner_experience.symbol_page import (
    SYMBOL_PAGE_SECTION_HEADINGS,
    SYMBOL_PAGE_SURFACE_ORDER,
)
from ob_owner_experience.symbol_page_real_surface import (
    SYMBOL_PAGE_COLLAPSED_KEYS,
    SYMBOL_PAGE_FIRST_GLANCE_KEYS,
    SYMBOL_PAGE_REAL_SURFACE_IDENTITY,
    SYMBOL_PAGE_REAL_SURFACE_STATUS,
    build_symbol_context,
    build_symbol_page_component_tree,
    build_symbol_page_empty_state,
    build_symbol_page_error_state,
    build_symbol_page_loading_state,
    build_symbol_page_real_surface,
    build_symbol_page_real_surface_acceptance_contract,
    build_symbol_page_real_surface_takeover_handoff,
    build_symbol_page_section_component,
)
from ob_owner_experience.ui_surface_registry import PROTECTED_ROUTE_POLICY


def test_symbol_page_real_surface_identity_is_gp004():
    assert SYMBOL_PAGE_REAL_SURFACE_IDENTITY["package"] == (
        "ob_symbol_page_real_surface_wiring_gp004"
    )
    assert SYMBOL_PAGE_REAL_SURFACE_IDENTITY["room"] == "symbol_page"
    assert SYMBOL_PAGE_REAL_SURFACE_IDENTITY["display_title"] == "Asset Storybook"
    assert SYMBOL_PAGE_REAL_SURFACE_IDENTITY["primary_question"] == (
        "What do I need to understand about this asset?"
    )
    assert SYMBOL_PAGE_REAL_SURFACE_IDENTITY["decision"] == (
        "READY_FOR_SYMBOL_PAGE_REAL_SURFACE_WIRING_WITH_SAFETY_LOCKS_HELD"
    )


def test_symbol_page_component_tree_preserves_contract_order_and_headings():
    tree = build_symbol_page_component_tree(symbol="tsla")

    keys = [component["section_key"] for component in tree]
    headings = {
        component["section_key"]: component["heading"]
        for component in tree
    }

    assert keys == list(SYMBOL_PAGE_SURFACE_ORDER)

    for key in SYMBOL_PAGE_SURFACE_ORDER:
        assert headings[key] == SYMBOL_PAGE_SECTION_HEADINGS[key]["label"]

    assert headings["hero"] == "🔎 Asset Storybook"
    assert headings["soulaana"] == "🧭 Soulaana Explains"


def test_symbol_page_section_component_fails_closed_for_unknown_section():
    try:
        build_symbol_page_section_component("unknown")
    except KeyError as exc:
        assert "Unknown Symbol Page section" in str(exc)
    else:
        raise AssertionError("Unknown Symbol Page section should fail closed.")


def test_symbol_context_is_required_and_destination_only():
    context = build_symbol_context("msft")

    assert context["symbol"] == "MSFT"
    assert context["route_param"] == "MSFT"
    assert context["display_symbol"] == "MSFT"
    assert context["symbol_required"] is True
    assert context["destination_only"] is True
    assert context["safe_fallback_route"] == "/ob/market-map"


def test_symbol_page_real_surface_uses_registry_and_protected_policy():
    surface = build_symbol_page_real_surface(symbol="nvda")

    assert surface["package"] == "ob_symbol_page_real_surface_wiring_gp004"
    assert surface["room"] == "symbol_page"
    assert surface["display_title"] == "Asset Storybook"
    assert surface["symbol_context"]["symbol"] == "NVDA"
    assert surface["component_hint"] == "AssetStorybookSurface"
    assert surface["data_adapter_hint"] == "build_symbol_page_surface"
    assert surface["protected_route_policy"] == PROTECTED_ROUTE_POLICY
    assert surface["protected_route_policy"]["anonymous_access_allowed"] is False
    assert surface["protected_route_policy"]["owner_session_required"] is True


def test_symbol_page_first_glance_and_collapsed_components_are_dynamic():
    surface = build_symbol_page_real_surface(symbol="aapl")

    assert SYMBOL_PAGE_FIRST_GLANCE_KEYS == [
        key
        for key in SYMBOL_PAGE_SURFACE_ORDER
        if key not in SYMBOL_PAGE_COLLAPSED_KEYS
    ]

    assert "AssetStorybookHeroCard" in surface["first_glance_components"]
    assert "AssetStorybookSoulaanaCard" in surface["first_glance_components"]
    assert "AssetStorybookNarrativeCard" in surface["first_glance_components"]
    assert "AssetStorybookRiskBeforeShineCard" in surface["first_glance_components"]
    assert "AssetStorybookDecisionPostureCard" in surface["first_glance_components"]

    assert "AssetStorybookDetailDrawerGroup" in surface["collapsed_components"]
    assert "AssetStorybookOwnerDrawer" in surface["collapsed_components"]

    collapsed_states = {
        component["section_key"]: component["default_state"]
        for component in surface["component_tree"]
    }

    assert any(
        value == "collapsed"
        for key, value in collapsed_states.items()
        if "drawer" in key or "detail" in key
    )


def test_symbol_page_states_are_safe_and_owner_readable():
    loading = build_symbol_page_loading_state("aapl")
    empty = build_symbol_page_empty_state("aapl")
    error = build_symbol_page_error_state("bad symbol feed", symbol="aapl")

    assert loading["state"] == "loading"
    assert loading["symbol_context"]["symbol"] == "AAPL"
    assert loading["show_soulaana_placeholder"] is True
    assert loading["dangerous_actions_available"] is False

    assert empty["state"] == "empty"
    assert empty["display_title"] == "Asset Storybook"
    assert empty["symbol_context"]["symbol"] == "AAPL"
    assert empty["details_hidden_by_default"] is True
    assert empty["dangerous_actions_available"] is False

    assert error["state"] == "error"
    assert error["message"] == "bad symbol feed"
    assert error["show_market_map_link"] is True
    assert error["show_owner_console_link"] is True
    assert error["broker_submission_enabled"] is False
    assert error["real_capital_movement_enabled"] is False
    assert error["live_auto_locked"] is True


def test_symbol_page_real_surface_safety_locks_hold():
    surface = build_symbol_page_real_surface(symbol="aapl")

    assert surface["surface_status"] == SYMBOL_PAGE_REAL_SURFACE_STATUS
    assert surface["surface_status"]["real_surface_adapter_ready"] is True
    assert surface["surface_status"]["symbol_context_route_ready"] is True
    assert surface["surface_status"]["real_html_rendered"] is False
    assert surface["surface_status"]["staging_ready"] is False
    assert surface["safety_summary"]["broker_submission_enabled"] is False
    assert surface["safety_summary"]["real_capital_movement_enabled"] is False
    assert surface["safety_summary"]["live_auto_locked"] is True
    assert "STAGING_READY" in surface["must_not_claim"]


def test_symbol_page_real_surface_acceptance_contract():
    contract = build_symbol_page_real_surface_acceptance_contract()

    assert contract["package"] == "ob_symbol_page_real_surface_wiring_gp004"
    assert contract["display_title"] == "Asset Storybook"
    assert contract["symbol_context_required"] is True
    assert "AssetStorybookHeroCard" in contract["must_show_at_first_glance"]
    assert "AssetStorybookSoulaanaCard" in contract["must_show_at_first_glance"]
    assert "AssetStorybookDetailDrawerGroup" in contract["must_hide_by_default"]
    assert "AssetStorybookOwnerDrawer" in contract["must_hide_by_default"]
    assert contract["must_include_states"] == ["loading", "empty", "error"]
    assert contract["safety_summary"]["broker_submission_enabled"] is False


def test_symbol_page_real_surface_takeover_handoff():
    handoff = build_symbol_page_real_surface_takeover_handoff()

    assert handoff["display_title"] == "Asset Storybook"
    assert handoff["symbol_context_required"] is True
    assert handoff["component_tree"]
    assert handoff["loading_state"]["state"] == "loading"
    assert handoff["empty_state"]["state"] == "empty"
    assert handoff["error_state"]["state"] == "error"
    assert "Keep Soulaana near the top." in handoff["next_builder_notes"]
    assert "Do not claim STAGING_READY." in handoff["next_builder_notes"]
