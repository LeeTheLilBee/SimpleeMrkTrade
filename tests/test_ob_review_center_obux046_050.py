from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

TEMPLATE = (
    ROOT
    / "web"
    / "templates"
    / "review_center.html"
)

CONTROLLER = (
    ROOT
    / "web"
    / "static"
    / "ob"
    / "ob_review_center.js"
)

PROJECTION = (
    ROOT
    / "web"
    / "static"
    / "ob"
    / "ob_review_center_projection.js"
)

CSS = (
    ROOT
    / "web"
    / "static"
    / "ob"
    / "ob_review_center_obux.css"
)


def text(path):
    return path.read_text(
        encoding="utf-8"
    )


def test_review_center_files_exist():
    assert TEMPLATE.exists()
    assert CONTROLLER.exists()
    assert PROJECTION.exists()
    assert CSS.exists()


def test_review_center_is_canonical_obux_room():
    source = text(TEMPLATE)

    assert (
        'data-ob-review-version="OBUX046-OBUX050"'
        in source
    )

    assert (
        "ob_review_center_projection.js"
        in source
    )

    assert (
        "ob_review_center_obux.css"
        in source
    )


def test_old_static_review_rows_are_removed():
    source = text(CONTROLLER)

    banned = [
        "OB_REVIEW_ROWS",
        "+8.4%",
        "Reviewed Trades",
        "MU Option Premium Replay",
        "AMD Watch-to-Candidate Replay",
        "Demo Record Snapshot",
    ]

    for marker in banned:
        assert marker not in source


def test_no_fake_performance_fallback():
    source = text(PROJECTION)

    assert (
        "fake_performance_fallback_enabled: false"
        in source
    )

    assert (
        "fakePerformanceFallbackEnabled: false"
        in source
    )


def test_negative_dive_metrics_exist():
    source = text(PROJECTION)

    required = [
        "mae_pct",
        "mfe_pct",
        "deepest_drawdown_pct",
        "time_negative_minutes",
        "time_below_stop_minutes",
        "intended_hold_minutes",
        "actual_hold_minutes",
        "overtime_minutes",
    ]

    for field in required:
        assert field in source


def test_planned_actual_entry_exit_supported():
    source = text(PROJECTION)

    required = [
        "planned_entry_price",
        "actual_entry_price",
        "planned_exit_price",
        "actual_exit_price",
        "planned_entry_time",
        "planned_exit_time",
        "actual_entry_time",
        "actual_exit_time",
    ]

    for field in required:
        assert field in source


def test_outcome_and_process_are_separate():
    source = text(PROJECTION)

    assert "outcome_class" in source
    assert "process_quality" in source

    controller = text(CONTROLLER)

    assert "Outcome" in controller
    assert "Process" in controller

    assert (
        "Do not confuse getting paid with trading clean"
        in controller
    )

    assert (
        "A clean loss is not the same thing as a bad decision"
        in controller
    )


def test_issue_taxonomy_present():
    source = text(PROJECTION)

    required = [
        "late_exit",
        "stop_ignored",
        "stale_candidate",
        "fill_slippage",
        "alert_delay",
        "owner_hesitation",
        "broker_confirmation_gap",
        "market_reversal",
        "contract_decay",
        "spread_liquidity_failure",
        "mission_account_rule_stress",
        "thesis_deterioration",
        "entry_chase",
        "oversized_position",
        "hold_time_violation",
        "source_data_problem",
    ]

    for code in required:
        assert code in source


def test_causes_are_evidence_based_not_loss_assumptions():
    source = text(PROJECTION)

    assert (
        "We only surface evidence-supported causes"
        in source
    )

    assert (
        "loss = owner hesitation"
        in source
    )


def test_options_contract_identity_preserved():
    source = text(PROJECTION)

    required = [
        "contract_symbol",
        "right",
        "strike",
        "expiration",
        "multiplier",
        "entry_premium",
        "exit_premium",
        "premium_pnl",
        "premium_return_pct",
    ]

    for field in required:
        assert field in source


def test_options_multiplier_economics_present():
    source = text(PROJECTION)

    assert (
        "exit - entry"
        in source
    )

    assert (
        "* quantity * identity.multiplier"
        in source
    )


def test_truth_modes_are_separate():
    source = text(PROJECTION)

    required = [
        '"manual_live"',
        '"paper"',
        '"rehearsal"',
        '"proof"',
        '"quarantined"',
    ]

    for marker in required:
        assert marker in source


def test_unknown_mode_is_not_promoted_to_manual_live():
    source = text(PROJECTION)

    assert (
        'return "proof";'
        in source
    )


def test_official_performance_boundary():
    source = text(PROJECTION)

    assert (
        '"manual_live",'
        in source
    )

    assert (
        '"paper",'
        in source
    )

    assert "OFFICIAL_MODES" in source


def test_durable_outcome_sources_connected():
    source = text(PROJECTION)

    assert (
        "OBOutcomeReceiptMaterialization"
        in source
    )

    assert (
        "OBDryRunOutcomeFinalization"
        in source
    )


def test_existing_review_close_sources_are_loaded_before_projection():
    source = text(TEMPLATE)

    required = [
        "ob_receipts_review_foundation.js",
        "ob_position_monitor_exit_close_capture.js",
        "ob_final_trade_review_performance_receipt.js",
        "ob_manual_live_dry_run_outcome_finalization.js",
        "ob_manual_live_outcome_receipt_materialization.js",
    ]

    for marker in required:
        assert marker in source

    projection_index = source.index(
        "ob_review_center_projection.js"
    )

    for marker in required:
        assert source.index(marker) < projection_index


def test_review_center_does_not_gain_execution_capability():
    source = text(PROJECTION)

    required = [
        "broker_execution_enabled: false",
        "broker_read_enabled: false",
        "auto_close_enabled: false",
        "auto_execution_enabled: false",
        "live_auto_locked: true",
    ]

    for marker in required:
        assert marker in source


def test_controller_has_no_execution_calls():
    source = text(CONTROLLER).lower()

    banned = [
        "submitorder(",
        "placeorder(",
        "broker.submit",
        "broker.place",
        "autoexecute(",
        "autoclose(",
    ]

    for marker in banned:
        assert marker not in source


def test_missing_metrics_render_unavailable():
    source = text(CONTROLLER)

    assert '"Unavailable"' in source

    assert (
        "Review Center does not estimate MAE, MFE"
        in source
    )


def test_review_queue_is_attention_first():
    source = text(CONTROLLER)

    assert (
        'filter: "attention"'
        in source
    )

    assert "needsAttention" in source


def test_review_center_has_soulaana_explanation():
    source = text(CONTROLLER)

    assert "function soulaana" in source
    assert "Soulaana" in source


def test_review_center_is_not_old_tab_heavy_interface():
    source = text(TEMPLATE)

    banned = [
        "Performance",
        "Trade Replay",
        "Reports",
        "Journal / Receipts",
        "Proof / Demo Records",
    ]

    # Those old tab labels must not return as the primary nav.
    for marker in banned:
        assert marker not in source


def test_review_center_css_has_two_column_command_surface():
    source = text(CSS)

    assert (
        "grid-template-columns: minmax(260px, .36fr) minmax(0, 1fr)"
        in source
    )

    assert (
        ".obux-review-queue-panel"
        in source
    )

    assert (
        ".obux-review-hero-card"
        in source
    )


def test_private_live_auto_boundary_visible():
    source = text(TEMPLATE)

    assert "PRIVATE" in source
    assert "LIVE AUTO LOCKED" in source
