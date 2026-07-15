# TOWER_TEST_CANONICAL_SAFETY_BOUNDARY_PATH_V1
# TOWER_TEST_CANONICAL_ROOM_PARAMETERS_ASSERTIONS_V1
from __future__ import annotations

import ast
from pathlib import Path

import pytest
from flask import Flask, jsonify

from tower import tower_human_login_ob_launch as launch_module



# TOWER_TEST_CLEARANCE_FIXTURE_PAYLOAD_V1

TOWER_TEST_CLEARANCE_DECISION_REF = (
    'tower-human-native-test-clearance-a047ea06ca12'
)


def _tower_test_attach_clearance(
    payload,
):
    """
    Attach the required clearance-decision evidence to
    successful test fixtures only.
    """

    if not isinstance(
        payload,
        dict,
    ):
        raise TypeError(
            "Successful legacy fixture must be a mapping."
        )

    updated = dict(payload)

    updated.setdefault(
        "clearance_decision_ref",
        TOWER_TEST_CLEARANCE_DECISION_REF,
    )

    legacy_handoff = updated.get(
        "launch_handoff"
    )

    if isinstance(
        legacy_handoff,
        dict,
    ):
        updated_handoff = dict(
            legacy_handoff
        )

        updated_handoff.setdefault(
            "clearance_decision_ref",
            TOWER_TEST_CLEARANCE_DECISION_REF,
        )

        updated[
            "launch_handoff"
        ] = updated_handoff

    return updated


ROOT = Path(__file__).resolve().parents[1]

HUMAN_FILE = (
    ROOT
    / "tower"
    / "tower_human_login_ob_launch.py"
)


def _functions(tree, name):
    return [
        node
        for node in ast.walk(tree)
        if isinstance(
            node,
            (
                ast.FunctionDef,
                ast.AsyncFunctionDef,
            ),
        )
        and node.name == name
    ]


def _decorators(node):
    return [
        ast.unparse(decorator)
        for decorator in node.decorator_list
    ]


def _legacy_payload(
    *,
    path="/dashboard",
    room_id="dashboard",
    mission_account_id="",
    symbol="",
):
    return _tower_test_attach_clearance({
        "allowed": True,
        "owner_id": "owner-test-001",
        "tower_session_id": (
            "tower-session-test-001"
        ),
        "requested_path": path,
        "requested_mode": "manual_live",
        "step_up_verified": True,
        "clearance_verified": True,
        "room_id": room_id,
        "mission_account_id": (
            mission_account_id
        ),
        "symbol": symbol,
        "launch_handoff": {
            "owner_id": "owner-test-001",
            "tower_session_id": (
                "tower-session-test-001"
            ),
            "requested_path": path,
            "requested_mode": "manual_live",
            "step_up_verified": True,
            "clearance_verified": True,
            "room_id": room_id,
            "mission_account_id": (
                mission_account_id
            ),
            "symbol": symbol,
        },
    })


def test_public_wrapper_preserves_original_decorators():
    source = HUMAN_FILE.read_text(
        encoding="utf-8"
    )
    tree = ast.parse(source)

    public = _functions(
        tree,
        "launch_observatory",
    )
    legacy = _functions(
        tree,
        "_launch_observatory_legacy",
    )

    assert len(public) == 1
    assert len(legacy) == 1

    assert _decorators(public[0]) == [
        (
            "tower_human_login_bp.get("
            "OBSERVATORY_LAUNCH_PATH)"
        ),
        "require_human_owner",
    ]

    assert _decorators(legacy[0]) == []


def test_dashboard_allows_empty_optional_room_values(
    monkeypatch,
):
    payload = _legacy_payload()

    monkeypatch.setattr(
        launch_module,
        "_launch_observatory_legacy",
        lambda: payload,
    )

    monkeypatch.setattr(
        launch_module,
        "step_up_active",
        lambda: True,
    )

    app = Flask(__name__)
    app.secret_key = "test-secret"

    with app.test_request_context(
        "/tower/observatory/launch"
    ):
        result = (
            launch_module.launch_observatory.__wrapped__()
            if hasattr(
                launch_module.launch_observatory,
                "__wrapped__",
            )
            else launch_module.launch_observatory()
        )

    assert result["gp046_native_contract"] is True
    assert (
        result["runtime_contract_adapter_required"]
        is False
    )

    handoff = result["launch_handoff"]

    assert (
        handoff["contract_version"]
        == "ob.tower_protected_launch_handoff.v1"
    )

    assert handoff["room_parameters"]['mission_account_id'] == ""
    assert handoff["room_parameters"]['symbol'] == ""


def test_trade_center_preserves_explicit_context(
    monkeypatch,
):
    payload = _legacy_payload(
        path="/trade-center",
        room_id="trade_center",
        mission_account_id="mission-trust",
        symbol="SPY",
    )

    monkeypatch.setattr(
        launch_module,
        "_launch_observatory_legacy",
        lambda: payload,
    )

    monkeypatch.setattr(
        launch_module,
        "step_up_active",
        lambda: True,
    )

    app = Flask(__name__)
    app.secret_key = "test-secret"

    with app.test_request_context(
        (
            "/tower/observatory/launch"
            "?mission_account_id=mission-trust"
            "&symbol=SPY"
            "&requested_path=/trade-center"
        )
    ):
        result = (
            launch_module.launch_observatory.__wrapped__()
            if hasattr(
                launch_module.launch_observatory,
                "__wrapped__",
            )
            else launch_module.launch_observatory()
        )

    handoff = result["launch_handoff"]

    assert (
        handoff["room_parameters"]['mission_account_id']
        == "mission-trust"
    )
    assert handoff["room_parameters"]['symbol'] == "SPY"
    assert handoff["room_id"] == "trade_center"


@pytest.mark.parametrize(
    "return_form",
    [
        "mapping",
        "tuple_mapping",
        "flask_json",
        "tuple_flask_json",
    ],
)
def test_supported_response_forms(
    monkeypatch,
    return_form,
):
    payload = _legacy_payload()

    app = Flask(__name__)
    app.secret_key = "test-secret"

    with app.test_request_context(
        "/tower/observatory/launch"
    ):
        if return_form == "mapping":
            legacy_result = payload

        elif return_form == "tuple_mapping":
            legacy_result = (
                payload,
                200,
            )

        elif return_form == "flask_json":
            legacy_result = jsonify(payload)

        else:
            legacy_result = (
                jsonify(payload),
                200,
            )

        monkeypatch.setattr(
            launch_module,
            "_launch_observatory_legacy",
            lambda: legacy_result,
        )

        monkeypatch.setattr(
            launch_module,
            "step_up_active",
            lambda: True,
        )

        result = (
            launch_module.launch_observatory.__wrapped__()
            if hasattr(
                launch_module.launch_observatory,
                "__wrapped__",
            )
            else launch_module.launch_observatory()
        )

        if isinstance(result, tuple):
            response_value = result[0]
        else:
            response_value = result

        if hasattr(response_value, "get_json"):
            result_payload = (
                response_value.get_json()
            )
        else:
            result_payload = response_value

    assert (
        result_payload["gp046_native_contract"]
        is True
    )
    assert (
        result_payload[
            "runtime_contract_adapter_required"
        ]
        is False
    )


def test_native_wrapper_fails_closed_without_identity(
    monkeypatch,
):
    payload = _legacy_payload()
    payload.pop("owner_id")
    payload["launch_handoff"].pop("owner_id")

    monkeypatch.setattr(
        launch_module,
        "_launch_observatory_legacy",
        lambda: payload,
    )

    monkeypatch.setattr(
        launch_module,
        "step_up_active",
        lambda: True,
    )

    app = Flask(__name__)
    app.secret_key = "test-secret"

    with app.test_request_context(
        "/tower/observatory/launch"
    ):
        with pytest.raises(
            RuntimeError,
            match=(
                "tower_ob_native_launch_context_missing"
            ),
        ):
            (
                launch_module
                .launch_observatory
                .__wrapped__()
                if hasattr(
                    launch_module.launch_observatory,
                    "__wrapped__",
                )
                else launch_module.launch_observatory()
            )


def test_locked_safety_boundaries_remain_false_or_locked(
    monkeypatch,
):
    payload = _legacy_payload()

    monkeypatch.setattr(
        launch_module,
        "_launch_observatory_legacy",
        lambda: payload,
    )

    monkeypatch.setattr(
        launch_module,
        "step_up_active",
        lambda: True,
    )

    app = Flask(__name__)
    app.secret_key = "test-secret"

    with app.test_request_context(
        "/tower/observatory/launch"
    ):
        result = (
            launch_module.launch_observatory.__wrapped__()
            if hasattr(
                launch_module.launch_observatory,
                "__wrapped__",
            )
            else launch_module.launch_observatory()
        )

    handoff = result["launch_handoff"]
    safety = handoff['safety']

    assert safety["dry_run_only"] is True
    assert (
        safety["production_manual_live_authorized"]
        is False
    )
    assert (
        safety["broker_submission_enabled"]
        is False
    )
    assert (
        safety["real_capital_movement_enabled"]
        is False
    )
    assert (
        safety["direct_vault_upload_enabled"]
        is False
    )
    assert safety["live_auto_locked"] is True


# TOWER_TEST_REAL_HUMAN_REDIRECT_NATIVE_SESSION_HANDOFF_V1
def test_real_walkthrough_redirect_stores_native_handoff(
    monkeypatch,
):
    receipt_hash = "a" * 64

    receipt = {
        "receipt_type": (
            "tower_ob_human_launch"
        ),
        "owner_id": (
            "owner-real-human-test"
        ),
        "role": "owner",
        "created_at": (
            "2026-07-14T23:20:00+00:00"
        ),
        "destination": (
            launch_module
            .OBSERVATORY_WALKTHROUGH_PATH
        ),
        "step_up_verified": True,
        "default_deny": True,
        "broker_submission": False,
        "capital_movement": False,
        "manual_live_authorized": False,
        "live_auto_authorized": False,
        "receipt_hash": receipt_hash,
    }

    app = Flask(__name__)
    app.secret_key = (
        "real-human-native-session-test"
    )

    def successful_legacy_redirect():
        launch_module.session[
            launch_module
            .SESSION_OB_LAUNCH_RECEIPT
        ] = dict(receipt)

        launch_module.session[
            launch_module
            .SESSION_STEP_UP_UNTIL
        ] = (
            "2026-07-14T23:30:00+00:00"
        )

        return launch_module.redirect(
            launch_module
            .OBSERVATORY_WALKTHROUGH_PATH
        )

    monkeypatch.setattr(
        launch_module,
        "_launch_observatory_legacy",
        successful_legacy_redirect,
    )

    monkeypatch.setattr(
        launch_module,
        "step_up_active",
        lambda: True,
    )

    with app.test_request_context(
        "/tower/observatory/launch"
    ):
        launch_function = (
            launch_module.launch_observatory
        )

        result = (
            launch_function.__wrapped__()
            if hasattr(
                launch_function,
                "__wrapped__",
            )
            else launch_function()
        )

        stored = dict(
            launch_module.session[
                launch_module
                .SESSION_OB_NATIVE_LAUNCH_HANDOFF
            ]
        )

    assert result.status_code == 302

    assert result.headers[
        "Location"
    ].endswith(
        launch_module
        .OBSERVATORY_WALKTHROUGH_PATH
    )

    assert (
        stored["contract_version"]
        == "ob.tower_protected_launch_handoff.v1"
    )

    assert stored["issuer"] == "tower"

    assert (
        stored["app_id"]
        == "observatory"
    )

    assert (
        stored["owner_id"]
        == "owner-real-human-test"
    )

    assert (
        stored["clearance_decision_ref"]
        == receipt_hash
    )

    assert (
        stored["room_id"]
        == "dashboard"
    )

    assert (
        stored["canonical_route"]
        == "/dashboard"
    )

    assert (
        stored["room_parameters"][
            "mission_account_id"
        ]
        == ""
    )

    assert (
        stored["room_parameters"][
            "symbol"
        ]
        == ""
    )

    assert stored[
        "step_up_verified"
    ] is True

    assert stored[
        "single_use"
    ] is True

    assert (
        stored["safety"][
            "production_manual_live_authorized"
        ]
        is False
    )

    assert (
        stored["safety"][
            "broker_submission_enabled"
        ]
        is False
    )

    assert (
        stored["safety"][
            "real_capital_movement_enabled"
        ]
        is False
    )

    assert (
        stored["safety"][
            "direct_vault_upload_enabled"
        ]
        is False
    )

    assert (
        stored["safety"][
            "live_auto_locked"
        ]
        is True
    )
