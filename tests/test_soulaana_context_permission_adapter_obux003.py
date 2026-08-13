from engine.soulaana_context_permission_adapter import (
    apply_soulaana_context_permissions,
)


def universal_stub():
    return {
        "universal": {
            "canonical": {
                "what_it_is": "State",
            },
        },
    }


def test_obux003_owner_context_clears_without_leaking_secret_keys():

    result = apply_soulaana_context_permissions(
        universal_stub(),
        {
            "role": "owner",
            "mode": "Paper",
            "room": "Dashboard",
            "account": "Personal",
            "tower_clearance": True,
            "owner_only_context": {
                "beta_state": "controlled",
                "api_key": "SHOULD_NOT_APPEAR",
            },
        },
    )

    assert (
        result["allowed"]
        is True
    )

    assert (
        "api_key"
        not in result["visible_context"]
    )

    assert (
        result["raw_secrets_exposed"]
        is False
    )


def test_obux003_tester_owner_console_is_denied():

    result = apply_soulaana_context_permissions(
        universal_stub(),
        {
            "role": "tester",
            "mode": "Paper",
            "room": "Owner Console",
            "account": "Proof/Demo",
            "tower_clearance": True,
        },
    )

    assert (
        result["allowed"]
        is False
    )

    assert (
        "tester_owner_console_denied"
        in result["failures"]
    )


def test_obux003_tester_manual_live_is_denied():

    result = apply_soulaana_context_permissions(
        universal_stub(),
        {
            "role": "tester",
            "mode": "Manual Live",
            "room": "Trade Center",
            "account": "Proof/Demo",
            "tower_clearance": True,
        },
    )

    assert (
        result["allowed"]
        is False
    )

    assert (
        "tester_manual_live_denied"
        in result["failures"]
    )
