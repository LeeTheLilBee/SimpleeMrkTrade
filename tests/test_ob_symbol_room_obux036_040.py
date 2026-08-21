import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

TEMPLATE = (
    ROOT
    / "web"
    / "templates"
    / "symbol_page.html"
)

MODES = (
    ROOT
    / "web"
    / "static"
    / "ob"
    / "ob_symbol_room_modes.js"
)

ROOM = (
    ROOT
    / "web"
    / "static"
    / "ob"
    / "ob_symbol_page.js"
)

CSS = (
    ROOT
    / "web"
    / "static"
    / "ob"
    / "ob_symbol_room.css"
)


def read(path):
    return path.read_text(
        encoding="utf-8"
    )


def test_symbol_template_is_clean_canonical_room():
    body = read(TEMPLATE)

    assert "OBUX036–040 SYMBOL ROOM" in body
    assert "ob_symbol_room.css" in body
    assert "ob_symbol_room_modes.js" in body
    assert "ob_symbol_page.js" in body

    # The quarantined static fixture must not be loaded.
    assert "ob_market_data.js" not in body

    # Symbol Room should not drag the historical proof/build stack
    # into the owner-facing room.
    forbidden = [
        "ob_private_beta_invite_packet.js",
        "ob_private_beta_issue_triage.js",
        "ob_private_beta_session_runbook.js",
        "ob_manual_live_dry_run_history_review.js",
        "ob_manual_live_proof_packet_review_queue.js",
        "ob_owner_practice_loop_board.js",
        "ob_tower_step_up_enforcement_prep.js",
    ]

    for item in forbidden:
        assert item not in body


def test_dependency_order_is_canonical_first():
    body = read(TEMPLATE)

    adapter = body.index(
        "ob_engine_feed_adapter.js"
    )
    contracts = body.index(
        "ob_data_contracts.js"
    )
    modes = body.index(
        "ob_symbol_room_modes.js"
    )
    room = body.index(
        "ob_symbol_page.js"
    )

    assert adapter < contracts < modes < room


def test_all_modes_have_explicit_behavior_contracts():
    body = read(MODES)

    required = [
        'SURVEY: "survey"',
        'PAPER: "paper"',
        'MANUAL_LIVE_1: "manual_live_1"',
        'HYBRID: "hybrid"',
        'AUTOMATED: "automated"',
        "objective_option_set",
        "contract_selection",
        "trade_handoff_kind",
    ]

    for marker in required:
        assert marker in body


def test_every_mode_keeps_execution_disabled():
    body = read(MODES)

    # One explicit false per mode minimum.
    assert body.count(
        "brokerage_execution: false"
    ) >= 5

    assert body.count(
        "automatic_execution: false"
    ) >= 5

    assert body.count(
        "automatic_contract_selection: false"
    ) >= 5

    assert body.count(
        "broker_api: false"
    ) >= 5


def test_mode_fallback_fails_closed_to_survey():
    body = read(MODES)

    assert (
        "The Symbol Room never grants itself Paper/Live/Hybrid."
        in body
    )

    assert (
        "return MODE.SURVEY;"
        in body
    )


def test_automated_is_explicitly_locked():
    body = read(MODES)

    assert (
        "Automated remains intentionally locked in OBUX036–040."
        in body
    )

    automated = body.split(
        "[MODE.AUTOMATED]"
    )[1]

    assert "locked: true" in automated


def test_manual_live_1_requires_owner_decision_and_owner_execution():
    body = read(MODES)

    manual = body.split(
        "[MODE.MANUAL_LIVE_1]"
    )[1].split(
        "[MODE.HYBRID]"
    )[0]

    assert (
        "owner_decision_required: true"
        in manual
    )

    assert (
        "user_chooses_contract: true"
        in manual
    )

    assert (
        "objective_option_set: false"
        in manual
    )

    assert (
        'trade_handoff_kind: "owner_review"'
        in manual
    )

    assert (
        "brokerage_execution: false"
        in manual
    )


def test_hybrid_has_objective_option_set_but_no_auto_choice():
    body = read(MODES)

    hybrid = body.split(
        "[MODE.HYBRID]"
    )[1].split(
        "[MODE.AUTOMATED]"
    )[0]

    assert (
        "objective_option_set: true"
        in hybrid
    )

    assert (
        "user_chooses_contract: true"
        in hybrid
    )

    assert (
        "automatic_contract_selection: false"
        in hybrid
    )

    assert (
        "brokerage_execution: false"
        in hybrid
    )


def test_symbol_room_has_no_old_fake_trade_context():
    body = read(ROOM)

    forbidden = [
        "+4.8%",
        "+1.6%",
        "-0.4%",
        "Confidence 82",
        "next monthly call",
        "Momentum continuation",
        "Approve for manual placement",
        "best option for you",
        "best contract for you",
    ]

    lower = body.lower()

    for marker in forbidden:
        assert marker.lower() not in lower


def test_symbol_room_has_no_independent_market_fetch():
    body = read(ROOM)

    # Canonical adapter event only.
    assert (
        "obEngineFeedAdapterUpdated"
        in body
    )

    # No direct market API/chain fetch logic.
    assert "fetch(" not in body
    assert "axios" not in body.lower()
    assert "websocket" not in body.lower()


def test_symbol_room_reads_canonical_contract():
    body = read(ROOM)

    assert (
        "window.OB_DATA_CONTRACTS_V22"
        in body
    )

    assert (
        "symbolPageContract"
        in body
    )

    assert (
        "window.OB_ENGINE_FEED_ADAPTER_V25"
        in body
    )


def test_options_layer_never_fabricates_missing_chain():
    body = read(ROOM)

    assert (
        "Options feed unavailable in the canonical projection."
        in body
    )

    assert (
        "does not invent strikes, Greeks, volume"
        in body
    )

    assert (
        "No canonical options chain"
        in read(TEMPLATE)
        or
        "Checking canonical options evidence"
        in read(TEMPLATE)
    )


def test_hybrid_requires_user_choice():
    body = read(ROOM)

    required = [
        "Surfaced because it matches the displayed objective filters.",
        "Order is not a recommendation ranking.",
        "THE USER chooses the contract.",
        "ob_selected_contract:",
        "owner_selected_contract:",
    ]

    for marker in required:
        assert marker in body

    assert re.search(
        r"ob_selected_contract\s*:\s*false",
        body,
    )


def test_trade_center_handoff_is_nonexecuting():
    body = read(ROOM)

    assert re.search(
        r'destination_room\s*:\s*"trade_center"',
        body,
    )

    assert "sessionStorage.setItem(" in body

    assert '"/ob/trade-center?symbol="' in body

    assert re.search(
        r"owner_decision_required\s*:\s*true",
        body,
    )

    assert re.search(
        r"owner_selected_contract\s*:\s*true",
        body,
    )

    assert re.search(
        r"ob_selected_contract\s*:\s*false",
        body,
    )

    assert re.search(
        r"broker_api\s*:\s*false",
        body,
    )

    assert re.search(
        r"brokerage_execution\s*:\s*false",
        body,
    )

    assert re.search(
        r"automatic_execution\s*:\s*false",
        body,
    )

    assert re.search(
        r"automatic_contract_selection\s*:\s*false",
        body,
    )


def test_symbol_room_visual_layer_exists():
    body = read(CSS)

    required = [
        ".ob-symbol-room",
        ".ob-options-sky",
        ".ob-chain-row",
        ".ob-option-set",
        ".ob-mode-banner",
    ]

    for marker in required:
        assert marker in body
