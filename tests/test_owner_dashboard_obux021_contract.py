from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]

CONTRACT = (
    ROOT / "web/static/ob/ob_owner_dashboard_contract.js"
).read_text(
    encoding="utf-8",
    errors="replace",
)


def compact(value):
    return re.sub(
        r"\s+",
        "",
        value,
    )


def test_obux021_guarded_owner_sources_remain_after_capital_lane_redesign():
    # Generic account-experience is deliberately retired from
    # the owner Capital Lane contract.
    assert (
        "/ob/account-experience.json"
        not in CONTRACT
    )

    for endpoint in [
        "/ob/engine-feed-trust-labels.json",
        "/ob/manual-live-operator-confidence-readiness-checkpoint.json",
        "/ob/private-beta-launch-control.json",
    ]:
        assert endpoint in CONTRACT

    assert "sourceLooksVerified" in CONTRACT

    assert (
        'credentials:"same-origin"'
        in compact(CONTRACT)
    )


def test_obux021_policy_never_becomes_fake_capital_truth():
    source = compact(
        CONTRACT
    )

    for marker in [
        "actual_capital_known:false",
        "actual_capital_value:null",
        "capital_progress_known:false",
        "capital_progress_percent:null",
        "verified_snapshot:false",
        "needs_attention:false",
    ]:
        assert marker in source

    assert (
        "OB_OWNER_CAPITAL_LANE_SNAPSHOT"
        in CONTRACT
    )


def test_obux021_execution_boundaries_remain_fail_closed():
    source = compact(
        CONTRACT
    )

    for marker in [
        "owner_only:true",
        "capital_lanes_owner_dashboard_only:true",
        "non_owner_capital_lane_delivery:false",
        "read_only_intelligence:true",
        "lane_selection_changes_context_only:true",
        "broker_api_enabled:false",
        "broker_order_submission_enabled:false",
        "real_capital_movement_enabled:false",
        "automatic_contract_selection_enabled:false",
        "auto_execution_enabled:false",
        "live_auto_locked:true",
    ]:
        assert marker in source


def test_obux021_does_not_resurrect_legacy_fake_position_logic():
    assert '["MU", "AMD", "INTC"]' not in CONTRACT

    assert "sample_signals" not in CONTRACT

    assert (
        "static_market_fallback_actionable"
        not in CONTRACT
    )
