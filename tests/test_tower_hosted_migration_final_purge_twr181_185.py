import ast
import json
from pathlib import Path

import web.hosted_tower as hosted

from tower.hosted_migration_contract import (
    BUILD_COMMAND,
    SERVICE_NAME,
    START_COMMAND,
    WSGI_ENTRYPOINT,
    validate_host_settings,
)

from tower.ob_product_landing import (
    PRODUCT_ENDPOINT,
    PRODUCT_PATH,
)

from tower.tower_human_login_ob_launch import (
    OBSERVATORY_LAUNCH_PATH,
    OBSERVATORY_WALKTHROUGH_PATH,
    OPERATIONAL_OB_ENTRY_PATH,
    TOWER_OPERATIONAL_OB_RECEIVE_PATH,
)


ROOT = Path(__file__).resolve().parents[1]


def retired_word():
    return "stag" + "ing"


def retired_token():
    return (
        "managed_"
        + retired_word()
    )


def test_181_retired_runtime_physically_absent():
    assert not (
        ROOT
        / "web"
        / (retired_token() + ".py")
    ).exists()

    assert not (
        ROOT
        / "deploy"
        / retired_token()
    ).exists()


def test_182_canonical_host_contract():
    assert SERVICE_NAME == "simplee-tower-ob"
    assert WSGI_ENTRYPOINT == "web.hosted_tower:app"

    assert BUILD_COMMAND == (
        "pip install -r "
        "deploy/hosted_tower/requirements.txt"
    )

    assert START_COMMAND == (
        "bash deploy/hosted_tower/start.sh"
    )


def test_182_rejects_retired_host_identity():
    result = validate_host_settings(
        {
            "service_name": (
                "simplee-tower-ob-"
                + retired_word()
            ),
            "build_command": BUILD_COMMAND,
            "start_command": START_COMMAND,
        }
    )

    assert result["ok"] is False


def test_183_runtime_identity_is_canonical():
    payload = (
        hosted
        .hosted_tower_runtime_manifest()
    )

    assert (
        payload["entrypoint"]
        == "web.hosted_tower:app"
    )

    assert (
        retired_word()
        not in json.dumps(
            payload
        ).lower()
    )

    assert (
        payload["critical_routes_present"]
        is True
    )


def test_184_real_ob_product_doorway():
    assert (
        OBSERVATORY_LAUNCH_PATH
        == "/tower/launch/observatory"
    )

    assert (
        TOWER_OPERATIONAL_OB_RECEIVE_PATH
        == "/tower/observatory/receive"
    )

    assert (
        OPERATIONAL_OB_ENTRY_PATH
        == "/ob/dashboard"
    )

    assert PRODUCT_PATH == "/ob/dashboard"
    assert PRODUCT_ENDPOINT == "ob_dashboard_v16"

    assert (
        OBSERVATORY_WALKTHROUGH_PATH
        != PRODUCT_PATH
    )


def test_184_dashboard_route_unique():
    matching = [
        rule
        for rule
        in hosted.app.url_map.iter_rules()
        if rule.rule == "/ob/dashboard"
    ]

    assert len(matching) == 1
    assert (
        matching[0].endpoint
        == "ob_dashboard_v16"
    )


def test_184_obsolete_response_rewriter_absent():
    tree = ast.parse(
        (
            ROOT
            / "web"
            / "app.py"
        ).read_text()
    )

    assert not any(
        isinstance(node, ast.FunctionDef)
        and node.name
        == (
            "_tower_obux006_010_"
            "dashboard_server_render_response"
        )
        for node in tree.body
    )


def test_185_safety_closed():
    payload = (
        hosted
        .hosted_tower_runtime_manifest()
    )

    for key in (
        "production_deployment",
        "broker_submission",
        "capital_movement",
        "manual_live_authorized",
        "live_auto_authorized",
    ):
        assert payload[key] is False
