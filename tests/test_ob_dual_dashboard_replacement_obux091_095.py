
from pathlib import Path
import re


ROOT = (
    Path(__file__)
    .resolve()
    .parents[1]
)

DASH = (
    ROOT
    / "web/templates/dashboard.html"
)

DASH_JS = (
    ROOT
    / "web/static/ob/ob_dashboard.js"
)

DASH_PROJECTION = (
    ROOT
    / "web/static/ob/ob_dashboard_projection.js"
)

DASH_CSS = (
    ROOT
    / "web/static/ob/ob_dashboard_obux.css"
)

OWNER = (
    ROOT
    / "web/templates/owner_dashboard.html"
)

OWNER_JS = (
    ROOT
    / "web/static/ob/ob_owner_dashboard.js"
)

OWNER_CONTRACT = (
    ROOT
    / "web/static/ob/ob_owner_dashboard_contract.js"
)

OWNER_SOULAANA = (
    ROOT
    / "web/static/ob/ob_owner_dashboard_soulaana.js"
)

OWNER_CSS = (
    ROOT
    / "web/static/ob/ob_owner_dashboard.css"
)


def text(path):
    return path.read_text(
        encoding="utf-8",
        errors="replace",
    )


def compact(value):
    return re.sub(
        r"\s+",
        "",
        value,
    )


def test_obux091_both_dashboards_are_new_build():
    assert (
        'data-ob-build="OBUX091-095"'
        in text(DASH)
    )

    assert (
        'data-ob-build="OBUX091-095"'
        in text(OWNER)
    )


def test_obux091_user_dashboard_old_information_wall_is_gone():
    source = text(DASH)

    for forbidden in [
        "SINCE YOU WERE HERE",
        "YOUR ACTIVITY",
        "YOUR OPERATING LOOP",
        "MY OB",
        "Your account tools",
        "Account snapshot",
        "Your OB account",
        "ob-card-stack",
        "ob-tool-grid",
    ]:
        assert forbidden not in source


def test_obux092_user_dashboard_is_self_directed_and_restrained():
    source = text(DASH)

    for required in [
        "SOULAANA · MARKET BRIEFING",
        "MARKET GLANCE",
        "Three things max.",
        "See the sky",
        "Study a symbol",
        "Practice",
        "More from your Observatory",
        "self-directed-observation-and-paper",
    ]:
        assert required in source

    for forbidden in [
        "TODAY’S EDGE",
        "OWNER RESEARCH",
        "CAPITAL LANES",
        "Enter this lane",
    ]:
        assert forbidden not in source


def test_obux092_user_projection_cannot_project_owner_advice_payload():
    source = text(DASH_PROJECTION)

    for required in [
        "owner_capital_lanes:",
        "owner_candidate_payloads:",
        "personalized_security_recommendations:",
        "option_contract_recommendations:",
        "manual_live_recommendations:",
        "automatic_contract_selection:",
        "automatic_execution:",
        "live_auto_locked:",
    ]:
        assert required in source

    compacted = compact(source)

    for required in [
        "owner_capital_lanes:false",
        "owner_candidate_payloads:false",
        "personalized_security_recommendations:false",
        "option_contract_recommendations:false",
        "manual_live_recommendations:false",
        "automatic_contract_selection:false",
        "automatic_execution:false",
        "live_auto_locked:true",
    ]:
        assert required in compacted

    assert (
        "/ob/account-experience.json"
        not in source
    )

    assert (
        "strike:"
        not in source
    )

    assert (
        "entry_zone:"
        not in source
    )

    assert (
        "invalidation:"
        not in source
    )


def test_obux092_user_market_glance_is_hard_capped_at_three():
    source = text(DASH_JS)

    assert (
        ".slice(\n            0,\n            3"
        in source
    )

    assert (
        "obUserMarketGlance"
        in source
    )

    assert (
        "Study symbol"
        in source
    )


def test_obux093_owner_dashboard_is_intelligence_first():
    source = (
        text(OWNER)
        + "\n"
        + text(OWNER_JS)
    )

    for required in [
        "owner-intelligence-cockpit",
        "TODAY’S EDGE",
        "Now. Watch. Not yet.",
        "SOULAANA · OWNER BRIEFING",
        "WHAT NEEDS YOU",
        "More owner intelligence",
        "Show me why",
    ]:
        assert required in source


def test_obux093_owner_contract_reads_existing_canonical_engine_projection():
    source = text(OWNER_CONTRACT)

    for required in [
        "OB_SERVER_DATA",
        "canonical_web_projection",
        "OB_ENGINE_FEED_SNAPSHOT_V25",
        "candidates_preview",
        "options_projection",
        "ranked_contracts",
        "research_contracts",
    ]:
        assert required in source


def test_obux093_owner_now_is_fail_closed():
    source = text(OWNER_CONTRACT)

    assert (
        "currentMarketVerified"
        in source
    )

    assert (
        'projection.projection_status === "fresh"'
        in source
    )

    assert (
        "return \"not_yet\""
        in source
    )

    assert (
        'return "now"'
        in source
    )


def test_obux093_options_first_does_not_become_auto_contract_selection():
    combined = (
        text(OWNER_CONTRACT)
        + "\n"
        + text(OWNER_JS)
    )

    for required in [
        "selection_authority:",
        '"OWNER"',
        "automatically_selected:",
        "false",
        "ranked_contract_is_not_selected_contract",
        "automatic_contract_selection_enabled:",
    ]:
        assert required in combined

    for forbidden in [
        "autoSelectContract(",
        "placeOrder(",
        "submitOrder(",
        "executeTrade(",
        "broker.submit(",
    ]:
        assert forbidden not in combined


def test_obux093_option_research_supports_real_contract_fields():
    source = text(OWNER_CONTRACT)

    for required in [
        "strike:",
        "expiration:",
        "bid:",
        "ask:",
        "volume:",
        "open_interest:",
        "implied_volatility:",
        "delta:",
        "gamma:",
        "theta:",
        "vega:",
    ]:
        assert required in source


def test_obux094_attention_architecture_is_explicit():
    source = (
        text(DASH)
        + "\n"
        + text(DASH_JS)
        + "\n"
        + text(OWNER_JS)
    )

    for required in [
        "Three things max.",
        "Only the top three.",
        "No giant queue.",
        "More owner intelligence",
        "More from your Observatory",
    ]:
        assert required in source


def test_obux094_no_default_table_or_ul_information_wall():
    combined = (
        text(DASH)
        + "\n"
        + text(OWNER)
        + "\n"
        + text(DASH_JS)
        + "\n"
        + text(OWNER_JS)
    ).lower()

    assert "<table" not in combined
    assert "<ul" not in combined


def test_obux094_drawers_are_keyboard_accessible():
    source = text(OWNER_JS)

    for required in [
        "trapFocus",
        'event.key === "Escape"',
        'aria-modal',
        "closeDrawer",
    ]:
        assert required in source


def test_obux094_reduced_motion_exists_on_both_dashboards():
    assert (
        "prefers-reduced-motion"
        in text(DASH_CSS)
    )

    assert (
        "prefers-reduced-motion"
        in text(OWNER_CSS)
    )


def test_obux094_owner_capital_lanes_are_secondary_not_primary():
    source = text(OWNER_JS)

    assert (
        "Capital context — secondary."
        in source
    )

    assert (
        "CURRENT CAPITAL LANE"
        in source
    )

    assert (
        "One lane at a time."
        in source
    )

    assert (
        "Enter this lane"
        in source
    )


def test_obux095_owner_and_user_payload_boundaries_are_explicit():
    user = compact(
        text(DASH_PROJECTION)
    )

    owner = compact(
        text(OWNER_CONTRACT)
    )

    assert (
        "non_owner_candidate_delivery:false"
        in owner
    )

    assert (
        "non_owner_capital_lane_delivery:false"
        in owner
    )

    assert (
        "owner_candidate_payloads:false"
        in user
    )

    assert (
        "owner_capital_lanes:false"
        in user
    )


def test_obux095_no_execution_capability_added():
    combined = "\n".join([
        text(DASH_JS),
        text(DASH_PROJECTION),
        text(OWNER_JS),
        text(OWNER_CONTRACT),
        text(OWNER_SOULAANA),
    ])

    for forbidden in [
        "placeOrder(",
        "submitOrder(",
        "executeTrade(",
        "autoSelectContract(",
        "broker.submit(",
    ]:
        assert forbidden not in combined

    assert (
        "Live Auto Locked"
        in text(OWNER)
    )

    assert (
        "Live Auto Locked"
        in text(DASH)
    )


def test_obux093_owner_template_loads_real_options_contract_before_engine_adapter():
    source = text(OWNER)

    options = (
        "ob_options_research_contract.js"
    )

    adapter = (
        "ob_engine_feed_adapter.js"
    )

    assert source.count(options) == 1
    assert source.count(adapter) == 1

    assert (
        source.index(options)
        < source.index(adapter)
    )
