from pathlib import Path

from flask import Flask

from tower import tower_human_login_ob_launch as launch_module


ROOT = Path(__file__).resolve().parents[1]

TOWER = ROOT / "tower/tower_human_login_ob_launch.py"

CONSUMERS = [
    ROOT / "web/static/ob/ob_snapshot_display.js",
    ROOT / "web/static/ob/ob_candidate_cards.js",
    ROOT / "web/static/ob/ob_manual_live_receipts.js",
    ROOT / "web/static/ob/ob_private_beta_qa.js",
    ROOT / "web/static/ob/ob_engine_feed_expansion.js",
]


def text(path):
    return path.read_text(
        encoding="utf-8",
        errors="replace",
    )


def test_obux076_product_handoff_exists():
    source = text(TOWER)

    assert (
        "def _tower_ob_native_store_product_handoff():"
        in source
    )

    assert (
        '"handoff_type"'
        in source
    )

    assert (
        '"tower_ob_product_entry"'
        in source
    )

    assert (
        '"requested_path"'
        in source
    )

    assert (
        "OBSERVATORY_PRODUCT_ENTRY_PATH"
        in source
    )


def test_obux076_walkthrough_is_proof_metadata():
    source = text(TOWER)

    assert (
        '"proof_walkthrough_path"'
        in source
    )

    assert (
        '"walkthrough_required_for_product_entry"'
        in source
    )

    assert (
        '"proof_only_walkthrough"'
        in source
    )


def test_obux077_public_launch_uses_product_handoff():
    source = text(TOWER)

    start = source.index(
        "def launch_observatory():"
    )

    end = source.index(
        "@tower_human_login_bp.route(",
        start,
    )

    launch_source = source[
        start:end
    ]

    assert (
        "_tower_ob_native_store_product_handoff()"
        in launch_source
    )

    assert (
        "_tower_ob_native_store_walkthrough_handoff()"
        not in launch_source
    )

    assert (
        "OBSERVATORY_PRODUCT_ENTRY_PATH"
        in launch_source
    )


def test_obux077_legacy_walkthrough_producer_still_exists():
    source = text(TOWER)

    assert (
        "def _tower_ob_native_store_walkthrough_handoff"
        in source
    )

    assert (
        "/tower/observatory-walkthrough"
        in source
    )


def test_obux077_owner_launch_still_lands_dashboard(
    monkeypatch,
):
    app = Flask(__name__)

    app.secret_key = (
        "obux076-080"
    )

    monkeypatch.setattr(
        launch_module,
        "_launch_observatory_legacy",
        lambda: launch_module.redirect(
            launch_module
            .OBSERVATORY_WALKTHROUGH_PATH
        ),
    )

    monkeypatch.setattr(
        launch_module,
        "_tower_ob_native_store_walkthrough_handoff",
        lambda: {
            "legacy": True,
        },
    )

    with app.test_request_context(
        "/tower/launch/observatory"
    ):
        function = (
            launch_module
            .launch_observatory
        )

        result = (
            function.__wrapped__()
            if hasattr(
                function,
                "__wrapped__",
            )
            else function()
        )

    assert (
        result.status_code
        == 302
    )

    assert (
        result.headers[
            "Location"
        ].endswith(
            "/ob/dashboard"
        )
    )


def test_obux078_product_handoff_metadata(
    monkeypatch,
):
    app = Flask(__name__)

    app.secret_key = (
        "obux076-080-handoff"
    )

    monkeypatch.setattr(
        launch_module,
        "_tower_ob_native_store_walkthrough_handoff",
        lambda: {
            "handoff_type":
                "tower_ob_native_walkthrough",
            "requested_path":
                "/dashboard",
        },
    )

    with app.test_request_context(
        "/tower/launch/observatory"
    ):
        handoff = (
            launch_module
            ._tower_ob_native_store_product_handoff()
        )

    assert (
        handoff[
            "handoff_type"
        ]
        == "tower_ob_product_entry"
    )

    assert (
        handoff[
            "requested_path"
        ]
        == "/ob/dashboard"
    )

    assert (
        handoff[
            "destination"
        ]
        == "/ob/dashboard"
    )

    assert (
        handoff[
            "proof_walkthrough_path"
        ]
        == "/tower/observatory-walkthrough"
    )

    assert (
        handoff[
            "walkthrough_required_for_product_entry"
        ]
        is False
    )

    assert (
        handoff[
            "proof_only_walkthrough"
        ]
        is True
    )


def test_obux079_product_consumers_do_not_anchor_to_mission_or_route():
    forbidden = [
        'const missionBar = document.getElementById("obMissionBar")',
        'const routeBar = document.getElementById("obRouteBar")',
    ]

    for path in CONSUMERS:
        source = text(path)

        for token in forbidden:
            assert (
                token
                not in source
            ), (
                f"{token} remained in {path.name}"
            )


def test_obux079_product_consumers_do_not_anchor_to_v27():
    forbidden = [
        'const polish = document.getElementById("obRoomDataPolishPanel")',
        'const roomPolish = document.getElementById("obRoomDataPolishPanel")',
        'const roomPolishPanel = document.getElementById("obRoomDataPolishPanel")',
    ]

    for path in CONSUMERS:
        source = text(path)

        for token in forbidden:
            assert (
                token
                not in source
            ), (
                f"{token} remained in {path.name}"
            )


def test_obux080_no_execution_capability_added():
    source = "\n".join(
        text(path)
        for path
        in CONSUMERS
    )

    forbidden = [
        "placeOrder(",
        "submitOrder(",
        "executeTrade(",
        "autoSelectContract(",
        "automaticContractSelection = true",
    ]

    for token in forbidden:
        assert (
            token
            not in source
        )


def test_obux080_doorway_remains_fail_closed():
    source = text(TOWER)

    required = [
        '"broker_submission"',
        '"capital_movement"',
        '"manual_live_authorized"',
        '"live_auto_authorized"',
        '"dangerous_action_unlocked"',
    ]

    for token in required:
        assert (
            token
            in source
        )
