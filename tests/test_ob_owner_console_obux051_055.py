from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

TEMPLATE = (
    ROOT
    / "web/templates/owner_console.html"
)

JS = (
    ROOT
    / "web/static/ob/ob_owner_console.js"
)

PROJECTION = (
    ROOT
    / "web/static/ob/ob_owner_console_projection.js"
)

CSS = (
    ROOT
    / "web/static/ob/ob_owner_console_obux.css"
)


def text(path):
    return path.read_text(
        encoding="utf-8",
        errors="replace",
    )


def test_owner_console_files_exist():
    assert TEMPLATE.exists()
    assert JS.exists()
    assert PROJECTION.exists()
    assert CSS.exists()


def test_owner_console_is_obux051_055():
    source = text(TEMPLATE)

    assert (
        'data-ob-owner-console-version="OBUX051-OBUX055"'
        in source
    )

    assert (
        'id="ob-owner-console"'
        in source
    )


def test_owner_console_answers_four_questions():
    source = text(TEMPLATE)

    required = [
        "IS OB HEALTHY?",
        "IS MY MONEY SAFE?",
        "WHAT NEEDS ME?",
        "WHAT IS DEGRADED?",
    ]

    for marker in required:
        assert marker in source


def test_owner_console_is_attention_first():
    source = text(TEMPLATE)

    assert "Attention Queue" in source

    assert (
        source.index(
            "Attention Queue"
        )
        <
        source.index(
            "Observatory Health"
        )
    )


def test_old_hardcoded_v17_rows_removed():
    source = text(JS)

    banned = [
        "OB_OWNER_ROWS",
        "OB_OWNER_TABS",
        '"5 real rooms"',
        '"UI ready"',
        '"Tech bright"',
        '"Semis active"',
        '"Preview data"',
        '"5 / 6"',
    ]

    for marker in banned:
        assert marker not in source


def test_old_market_fixture_removed_from_owner_console():
    source = text(TEMPLATE)

    assert (
        "ob_market_data.js"
        not in source
    )


def test_owner_console_projection_loaded():
    source = text(TEMPLATE)

    assert (
        "ob_owner_console_projection.js"
        in source
    )

    assert (
        "ob_owner_console.js"
        in source
    )

    assert (
        source.index(
            "ob_owner_console_projection.js"
        )
        <
        source.index(
            "ob_owner_console.js"
        )
    )


def test_existing_diagnostics_stack_preserved():
    source = text(TEMPLATE)

    required = [
        "ob_engine_feed_diagnostics.js",
        "ob_engine_trust_labels.js",
        "ob_engine_room_mapping.js",
        "ob_owner_source_audit.js",
    ]

    for marker in required:
        assert marker in source


def test_existing_readiness_stack_preserved_after_mission_runtime_retirement():
    source = text(TEMPLATE)

    # OBUX086–090 retires the shared legacy Mission Account
    # runtime from canonical OB product rooms, including
    # Owner Console.
    assert (
        "ob_mission_accounts.js"
        not in source
    )

    # Owner Console readiness / safety infrastructure remains.
    required = [
        "ob_beta_readiness.js",
        "ob_beta_readiness_checkpoint.js",
        "ob_manual_live_l1_readiness_checkpoint.js",
        "ob_manual_live_pre_live_lock_wall.js",
    ]

    for marker in required:
        assert marker in source


def test_source_audit_and_diagnostics_are_used():
    source = text(PROJECTION)

    assert (
        "OB_ENGINE_FEED_DIAGNOSTICS_V33_API"
        in source
    )

    assert (
        "OB_OWNER_SOURCE_AUDIT_V36"
        in source
    )


def test_fallback_never_promotes_to_healthy():
    source = text(PROJECTION)

    assert (
        "if (fallbackActive)"
        in source
    )

    assert (
        "status = STATUS.GUARDED"
        in source
    )


def test_unknown_stays_unknown():
    source = text(PROJECTION)

    assert (
        "return STATUS.UNKNOWN"
        in source
    )

    assert (
        "fake_health_fallback:"
        in source
    )

    assert (
        "false"
        in source
    )


def test_no_fake_balance_truth():
    source = text(PROJECTION)

    required = [
        "capital_balance:",
        "available_capital:",
        "realized_pnl:",
        "risk_utilization:",
        "fake_balance_fallback:",
    ]

    for marker in required:
        assert marker in source

    assert (
        "Live balances and capital health"
        in text(TEMPLATE)
    )


def test_owner_console_consumes_review_attention():
    source = text(PROJECTION)

    assert (
        "OBReviewCenterProjection"
        in source
    )

    assert (
        "poor_process"
        in source
    )

    assert (
        "overtime"
        in source
    )


def test_room_chain_is_canonical():
    source = text(PROJECTION)

    required = [
        '"market_map"',
        '"symbol_page"',
        '"trade_center"',
        '"review_center"',
        '"owner_console"',
    ]

    for marker in required:
        assert marker in source


def test_no_hardcoded_room_health():
    source = text(PROJECTION)

    assert (
        '"Market Map",'
        in source
    )

    assert (
        "status:"
        in source
    )

    assert (
        "Object.keys(candidate).length"
        in source
    )

    assert (
        "STATUS.UNKNOWN"
        in source
    )


def test_safety_truth_is_fail_closed():
    source = text(PROJECTION)

    required = [
        "broker_read:",
        "broker_execution:",
        "automatic_execution:",
        "automatic_contract_selection:",
        "auto_close:",
        "live_auto_locked:",
    ]

    for marker in required:
        assert marker in source


def test_safety_values_are_false_or_locked():
    source = text(PROJECTION)

    assert (
        "broker_read:\n        false"
        in source
    )

    assert (
        "broker_execution:\n        false"
        in source
    )

    assert (
        "automatic_execution:\n        false"
        in source
    )

    assert (
        "automatic_contract_selection:\n        false"
        in source
    )

    assert (
        "auto_close:\n        false"
        in source
    )

    assert (
        "live_auto_locked:\n        true"
        in source
    )


def test_controller_has_no_execution_calls():
    source = text(JS).lower()

    banned = [
        "placeorder(",
        "submitorder(",
        "executeorder(",
        "broker.submit",
        "broker.place",
        "autoclose(",
        "autoexecute(",
    ]

    for marker in banned:
        assert marker not in source


def test_owner_console_is_read_only():
    source = text(PROJECTION)

    assert (
        "owner_console_read_only:"
        in source
    )

    assert (
        "read_only:"
        in source
    )


def test_owner_console_does_not_modify_tower():
    source = text(PROJECTION)

    assert (
        "tower_files_modified:"
        in source
    )

    assert (
        "false"
        in source
    )


def test_soulaana_explains_unknown_truth():
    source = text(JS)

    assert (
        "Unknown stays unknown"
        in source
    )

    assert (
        "I will not call that healthy"
        in source
    )


def test_source_drawer_is_progressive_disclosure():
    source = text(TEMPLATE)

    assert (
        'id="oboc-source-drawer"'
        in source
    )

    location = source.index(
        'id="oboc-source-drawer"'
    )

    window = source[
        location - 100:
        location + 220
    ]

    assert "hidden" in window


def test_no_tab_heavy_v17_primary_ui():
    source = text(TEMPLATE)

    banned = [
        ">Monitoring<",
        ">Analytics<",
        ">Intelligence<",
        ">Diagnostics<",
        ">Security / Audit<",
        ">Preview Controls<",
    ]

    for marker in banned:
        assert marker not in source


def test_dark_glass_owner_deck():
    source = text(CSS)

    assert (
        "--oboc-bg: #06070c"
        in source
    )

    assert (
        "backdrop-filter"
        in source
    )

    assert (
        ".oboc-main-grid"
        in source
    )


def test_hard_safety_visible_in_template():
    source = text(TEMPLATE)

    required = [
        "Broker read",
        "Broker execution",
        "Auto close",
        "Auto execution",
        "Auto contract selection",
        "LIVE AUTO",
    ]

    for marker in required:
        assert marker in source


def test_compatibility_mount_hidden():
    source = text(TEMPLATE)

    assert (
        'id="oboc-compatibility"'
        in source
    )

    location = source.index(
        'id="oboc-compatibility"'
    )

    assert (
        "hidden"
        in source[
            location - 120:
            location + 180
        ]
    )


def test_exact_product_questions_stay_visible():
    source = text(TEMPLATE)

    assert (
        "System truth · Capital boundaries · Source health · Owner attention"
        in source
    )
