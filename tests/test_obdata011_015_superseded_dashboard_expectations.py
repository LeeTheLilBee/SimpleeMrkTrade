from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


SUPERSEDED_DASHBOARD_TESTS = (
    "tests/test_dashboard_account_health_obux007.py",
    "tests/test_dashboard_broken_geometry_obux013.py",
    "tests/test_dashboard_command_stage_obux016.py",
    "tests/test_dashboard_hot_now_obux009.py",
    "tests/test_dashboard_instrument_board_obux018.py",
    "tests/test_dashboard_less_data_more_explanation_obux015.py",
    "tests/test_dashboard_live_board_obux019.py",
    "tests/test_dashboard_normal_role_scope_obux020.py",
    "tests/test_dashboard_simplification_obux010.py",
    "tests/test_dashboard_since_you_were_here_obux008.py",
    "tests/test_dashboard_soulaana_hierarchy_obux017.py",
    "tests/test_dashboard_soulaana_market_brief_obux011.py",
    "tests/test_dashboard_soulaana_now_obux006.py",
    "tests/test_dashboard_soulaana_translation_obux012.py",
    "tests/test_dashboard_source_truth_obux006_010.py",
    "tests/test_ob_atmosphere_obux028_room_wiring.py",
)


CANONICAL_AUTHORITY = (
    "tests/test_ob_dual_dashboard_replacement_obux091_095.py"
)


def test_superseded_pre_obux091_dashboard_expectations_stay_retired():
    present = [
        relative
        for relative in SUPERSEDED_DASHBOARD_TESTS
        if (ROOT / relative).exists()
    ]

    assert present == [], (
        "Superseded pre-OBUX091 dashboard regression modules "
        "must not return: "
        + ", ".join(present)
    )


def test_obux091_095_dashboard_authority_remains_present():
    assert (ROOT / CANONICAL_AUTHORITY).is_file()


def test_current_user_and_owner_dashboard_surfaces_remain_present():
    assert (ROOT / "web/templates/dashboard.html").is_file()
    assert (ROOT / "web/templates/owner_dashboard.html").is_file()


def test_current_dashboard_runtime_contracts_remain_present():
    assert (ROOT / "web/static/ob/ob_dashboard.js").is_file()
    assert (ROOT / "web/static/ob/ob_dashboard_projection.js").is_file()
    assert (ROOT / "web/static/ob/ob_owner_dashboard_contract.js").is_file()
