import pytest
from flask import Flask

from tower.tower_observatory_walkthrough_web import (
    owner_access_allowed,
    room_by_id,
    room_request_context,
    tower_ob_walkthrough_bp,
)


@pytest.fixture()
def app():
    app = Flask(__name__)
    app.secret_key = "walkthrough-test-secret"

    app.register_blueprint(
        tower_ob_walkthrough_bp
    )

    app.config.update(
        TESTING=True,
    )

    return app


@pytest.fixture()
def client(app):
    return app.test_client()


def set_owner_session(client):
    with client.session_transaction() as session:
        session["tower_role"] = "owner"
        session["owner_id"] = "owner_test"


def test_walkthrough_default_denies_without_owner(client):
    response = client.get(
        "/tower/observatory-walkthrough"
    )

    assert response.status_code == 403


def test_walkthrough_home_lists_six_rooms(client):
    set_owner_session(client)

    response = client.get(
        "/tower/observatory-walkthrough"
    )

    assert response.status_code == 200

    body = response.get_data(as_text=True)

    for room_name in [
        "Dashboard",
        "Market Map",
        "Symbol Page",
        "Trade Center",
        "Review Center",
        "Owner Console",
    ]:
        assert room_name in body


def test_room_review_page(client):
    set_owner_session(client)

    response = client.get(
        "/tower/observatory-walkthrough/"
        "room/ob_room_dashboard"
    )

    assert response.status_code == 200

    body = response.get_data(as_text=True)

    assert "Dashboard" in body
    assert "ob_owner_command" in body
    assert "Launch protected preview" in body


def test_dashboard_preview_launch_and_receipt(client):
    set_owner_session(client)

    response = client.post(
        "/tower/observatory-walkthrough/"
        "room/ob_room_dashboard/launch",
        follow_redirects=True,
    )

    assert response.status_code == 200

    body = response.get_data(as_text=True)

    assert "Protected launch passed" in body
    assert "Lockback verified" in body
    assert "Default deny restored" in body


def test_symbol_preview_launch(client):
    set_owner_session(client)

    response = client.post(
        "/tower/observatory-walkthrough/"
        "room/ob_room_symbol_page/launch",
        data={
            "symbol": "amd",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200

    body = response.get_data(as_text=True)

    assert "/symbol/AMD" in body


def test_owner_console_preview_launch(client):
    set_owner_session(client)

    response = client.post(
        "/tower/observatory-walkthrough/"
        "room/ob_room_owner_console/launch",
        data={
            "mission_account_id": "proof_demo",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200

    body = response.get_data(as_text=True)

    assert "Owner Console" in body
    assert "validated" in body


def test_walkthrough_close_returns_locked_back(client):
    set_owner_session(client)

    client.post(
        "/tower/observatory-walkthrough/"
        "room/ob_room_dashboard/launch",
    )

    response = client.post(
        "/tower/observatory-walkthrough/close",
        follow_redirects=True,
    )

    assert response.status_code == 200

    body = response.get_data(as_text=True)

    assert "Returned to Tower" in body
    assert "Replay blocked" in body
    assert "Default deny restored" in body


def test_room_helpers():
    room = room_by_id(
        "ob_room_symbol_page"
    )

    assert room is not None

    context = room_request_context(
        room,
        {
            "symbol": "nvda",
        },
    )

    assert context["path"] == "/symbol/NVDA"

    assert context["object_context"] == {
        "symbol": "NVDA",
    }

# BEGIN REAL SURFACE WALKTHROUGH TESTS

from flask import Response

from tower.tower_ir_cert_p2433 import (
    REAL_ROOM_REGISTRY,
)
from tower.tower_observatory_walkthrough_web import (
    _inject_before_body_close,
    _real_surface_overlay_html,
    _real_surface_path_for_room,
    _real_surface_room_for_path,
    _tower_walkthrough_entry_html,
)


def test_real_surface_registry_paths():
    expected = {
        "/dashboard": "ob_room_dashboard",
        "/market-map": "ob_room_market_map",
        "/ob/symbol/AMD": "ob_room_symbol_page",
        "/ob/trade-center": "ob_room_trade_center",
        "/ob/review-center": "ob_room_review_center",
        "/ob/owner-console": "ob_room_owner_console",
    }

    for path, room_id in expected.items():
        room = _real_surface_room_for_path(
            path
        )

        assert room is not None
        assert room["room_id"] == room_id


def test_tower_entry_fragment():
    fragment = (
        _tower_walkthrough_entry_html()
    )

    assert "towerObWalkthroughEntry" in fragment

    assert (
        "/tower/observatory-walkthrough"
        in fragment
    )


def test_real_surface_overlay_fragment():
    room = REAL_ROOM_REGISTRY[0]

    state = {
        "walkthrough_id": "obwalk_test",
    }

    fragment = (
        _real_surface_overlay_html(
            room=room,
            state=state,
        )
    )

    assert "towerObRealSurfaceGuide" in fragment
    assert "Dashboard" in fragment
    assert "Room 1 of 6" in fragment
    assert "Preview authority only" in fragment


def test_html_injection_before_body():
    result = _inject_before_body_close(
        "<html><body>Room</body></html>",
        "<aside>Guide</aside>",
    )

    assert (
        "<aside>Guide</aside></body>"
        in result
    )


def test_symbol_real_surface_uses_launch_symbol():
    symbol_room = [
        room
        for room in REAL_ROOM_REGISTRY
        if room["room_id"]
        == "ob_room_symbol_page"
    ][0]

    state = {
        "launch_receipt": {
            "canonical_path": (
                "/symbol/NVDA"
            ),
        },
    }

    assert (
        _real_surface_path_for_room(
            symbol_room,
            state,
        )
        == "/ob/symbol/NVDA"
    )


def test_real_surface_open_requires_receipt(
    client,
):
    set_owner_session(client)

    response = client.get(
        "/tower/observatory-walkthrough/"
        "open/ob_room_dashboard",
        follow_redirects=True,
    )

    assert response.status_code == 200

    body = response.get_data(
        as_text=True
    )

    assert "Protected launch denied" in body
    assert (
        "tower_ob_real_surface_"
        "launch_receipt_missing"
        in body
    )


def test_launch_receipt_links_real_surface(
    client,
):
    set_owner_session(client)

    response = client.post(
        "/tower/observatory-walkthrough/"
        "room/ob_room_dashboard/launch",
        follow_redirects=True,
    )

    assert response.status_code == 200

    body = response.get_data(
        as_text=True
    )

    assert (
        "Open the real room surface"
        in body
    )

    assert (
        "/tower/observatory-walkthrough/"
        "open/ob_room_dashboard"
        in body
    )


def test_real_surface_open_redirects_to_dashboard(
    client,
):
    set_owner_session(client)

    client.post(
        "/tower/observatory-walkthrough/"
        "room/ob_room_dashboard/launch",
    )

    response = client.get(
        "/tower/observatory-walkthrough/"
        "open/ob_room_dashboard"
    )

    assert response.status_code == 302

    location = response.headers[
        "Location"
    ]

    assert location.startswith(
        "/dashboard?"
    )

    assert "tower_walkthrough=1" in location
    assert "walkthrough_id=" in location


def test_symbol_real_surface_redirect(
    client,
):
    set_owner_session(client)

    client.post(
        "/tower/observatory-walkthrough/"
        "room/ob_room_symbol_page/launch",
        data={
            "symbol": "nvda",
        },
    )

    response = client.get(
        "/tower/observatory-walkthrough/"
        "open/ob_room_symbol_page"
    )

    assert response.status_code == 302

    assert response.headers[
        "Location"
    ].startswith(
        "/ob/symbol/NVDA?"
    )


# END REAL SURFACE WALKTHROUGH TESTS

# BEGIN GUIDED SIX ROOM RUN TESTS

from tower.tower_observatory_walkthrough_web import (
    _GUIDED_ROOM_ORDER,
    _guided_expected_room_id,
    _guided_final_receipt,
    _new_guided_progress,
)


def test_guided_progress_contract():
    progress = _new_guided_progress(
        "obwalk_test"
    )

    assert progress["status"] == "in_progress"
    assert progress["completed_count"] == 0
    assert progress["total_room_count"] == 6

    assert progress["next_room_id"] == (
        "ob_room_dashboard"
    )


def test_guided_expected_room_sequence():
    progress = _new_guided_progress(
        "obwalk_test"
    )

    assert _guided_expected_room_id(
        progress
    ) == "ob_room_dashboard"

    progress["completed_room_ids"] = [
        "ob_room_dashboard",
        "ob_room_market_map",
    ]

    assert _guided_expected_room_id(
        progress
    ) == "ob_room_symbol_page"


def test_guided_start_route(client):
    set_owner_session(client)

    response = client.post(
        "/tower/observatory-walkthrough/guided-start"
    )

    assert response.status_code == 302

    assert response.headers[
        "Location"
    ].endswith(
        "/tower/observatory-walkthrough/"
        "room/ob_room_dashboard"
    )


def test_guided_progress_page(client):
    set_owner_session(client)

    client.post(
        "/tower/observatory-walkthrough/guided-start"
    )

    response = client.get(
        "/tower/observatory-walkthrough/progress"
    )

    assert response.status_code == 200

    body = response.get_data(
        as_text=True
    )

    assert "Guided Run Progress" in body
    assert "0" in body
    assert "Dashboard" in body
    assert "Next room" in body


def test_guided_sequence_rejects_wrong_room(client):
    set_owner_session(client)

    client.post(
        "/tower/observatory-walkthrough/guided-start"
    )

    response = client.post(
        "/tower/observatory-walkthrough/"
        "progress/complete/ob_room_market_map"
    )

    assert response.status_code == 409


def test_guided_dashboard_completion(client):
    set_owner_session(client)

    client.post(
        "/tower/observatory-walkthrough/guided-start"
    )

    client.post(
        "/tower/observatory-walkthrough/"
        "room/ob_room_dashboard/launch"
    )

    response = client.post(
        "/tower/observatory-walkthrough/"
        "progress/complete/ob_room_dashboard"
    )

    assert response.status_code == 302

    assert response.headers[
        "Location"
    ].endswith(
        "/tower/observatory-walkthrough/"
        "room/ob_room_market_map"
    )

    with client.session_transaction() as session:
        progress = session[
            "tower_ob_guided_progress"
        ]

        assert progress["completed_count"] == 1

        assert progress[
            "completed_room_ids"
        ] == [
            "ob_room_dashboard"
        ]

        assert (
            "ob_room_dashboard"
            in progress["room_receipts"]
        )


def test_guided_final_receipt_contract():
    progress = _new_guided_progress(
        "obwalk_test"
    )

    progress["completed_room_ids"] = list(
        _GUIDED_ROOM_ORDER
    )

    progress["room_receipts"] = {
        room_id: {
            "room_completion_receipt_id": (
                f"receipt_{index}"
            ),
            "default_deny_restored": True,
        }
        for index, room_id in enumerate(
            _GUIDED_ROOM_ORDER,
            start=1,
        )
    }

    receipt = _guided_final_receipt(
        progress
    )

    assert receipt["status"] == "completed"
    assert receipt["room_count"] == 6

    assert receipt[
        "all_default_deny_restored"
    ] is True

    assert receipt[
        "broker_order_submission"
    ] is False

    assert receipt[
        "production_manual_live_authorization"
    ] is False

    assert receipt[
        "final_completion_receipt_id"
    ].startswith(
        "obguidedcomplete_"
    )


def test_guided_reset(client):
    set_owner_session(client)

    client.post(
        "/tower/observatory-walkthrough/guided-start"
    )

    response = client.post(
        "/tower/observatory-walkthrough/"
        "progress/reset"
    )

    assert response.status_code == 302

    with client.session_transaction() as session:
        assert (
            "tower_ob_guided_progress"
            not in session
        )

        assert (
            "tower_ob_walkthrough"
            not in session
        )


# END GUIDED SIX ROOM RUN TESTS

# BEGIN GUIDED RUN PERSISTENCE TESTS

from tower.tower_observatory_walkthrough_store import (
    list_owner_runs as store_list_owner_runs,
    load_guided_run as store_load_guided_run,
)


def test_guided_start_persists_run(
    client,
):
    set_owner_session(client)

    client.post(
        "/tower/observatory-walkthrough/guided-start"
    )

    with client.session_transaction() as session:
        progress = session[
            "tower_ob_guided_progress"
        ]

        walkthrough_id = progress[
            "walkthrough_id"
        ]

    stored = store_load_guided_run(
        owner_id="owner_test",
        walkthrough_id=walkthrough_id,
    )

    assert stored is not None
    assert stored["status"] == "in_progress"
    assert stored["integrity_valid"] is True


def test_history_page_lists_saved_run(
    client,
):
    set_owner_session(client)

    client.post(
        "/tower/observatory-walkthrough/guided-start"
    )

    response = client.get(
        "/tower/observatory-walkthrough/history"
    )

    assert response.status_code == 200

    body = response.get_data(
        as_text=True
    )

    assert "Observatory Run History" in body
    assert "In progress" in body
    assert "Resume run" in body


def test_lost_session_resume(
    client,
):
    set_owner_session(client)

    client.post(
        "/tower/observatory-walkthrough/guided-start"
    )

    client.post(
        "/tower/observatory-walkthrough/"
        "room/ob_room_dashboard/launch"
    )

    client.post(
        "/tower/observatory-walkthrough/"
        "progress/complete/ob_room_dashboard"
    )

    with client.session_transaction() as session:
        progress = session[
            "tower_ob_guided_progress"
        ]

        walkthrough_id = progress[
            "walkthrough_id"
        ]

        session.pop(
            "tower_ob_guided_progress",
            None,
        )

        session.pop(
            "tower_ob_walkthrough",
            None,
        )

    response = client.post(
        "/tower/observatory-walkthrough/"
        f"history/resume/{walkthrough_id}"
    )

    assert response.status_code == 302

    assert response.headers[
        "Location"
    ].endswith(
        "/tower/observatory-walkthrough/"
        "room/ob_room_market_map"
    )

    with client.session_transaction() as session:
        restored = session[
            "tower_ob_guided_progress"
        ]

        assert restored[
            "completed_count"
        ] == 1

        assert restored[
            "next_room_id"
        ] == "ob_room_market_map"


def test_history_verify_json(
    client,
):
    set_owner_session(client)

    client.post(
        "/tower/observatory-walkthrough/guided-start"
    )

    with client.session_transaction() as session:
        walkthrough_id = session[
            "tower_ob_guided_progress"
        ]["walkthrough_id"]

    response = client.get(
        "/tower/observatory-walkthrough/"
        f"history/{walkthrough_id}/verify.json"
    )

    assert response.status_code == 200

    payload = response.get_json()

    assert payload["verified"] is True
    assert payload["status"] == "in_progress"
    assert payload["preview_only"] is True
    assert payload["vault_write_performed"] is False


# END GUIDED RUN PERSISTENCE TESTS

# BEGIN PERSISTENCE OPERATIONS TESTS

def test_operations_page_owner_only(
    client,
):
    response = client.get(
        "/tower/observatory-walkthrough/operations"
    )

    assert response.status_code == 403


def test_operations_page(
    client,
):
    set_owner_session(client)

    response = client.get(
        "/tower/observatory-walkthrough/operations"
    )

    assert response.status_code == 200

    body = response.get_data(
        as_text=True
    )

    assert "Walkthrough Storage Operations" in body
    assert "Ledger health" in body
    assert "Retention preview" in body
    assert "Recovery status" in body
    assert "No direct Vault write" in body


def test_operations_health_json(
    client,
):
    set_owner_session(client)

    response = client.get(
        "/tower/observatory-walkthrough/"
        "operations/health.json"
    )

    assert response.status_code == 200

    payload = response.get_json()

    assert payload["healthy"] is True
    assert payload[
        "direct_vault_write"
    ] is False


# END PERSISTENCE OPERATIONS TESTS

# BEGIN HOSTED PERSISTENCE ASSURANCE TESTS

def test_hosted_assurance_owner_only(
    client,
):
    response = client.get(
        "/tower/observatory-walkthrough/"
        "operations/assurance"
    )

    assert response.status_code == 403


def test_hosted_assurance_board(
    client,
):
    set_owner_session(client)

    response = client.get(
        "/tower/observatory-walkthrough/"
        "operations/assurance"
    )

    assert response.status_code == 200

    body = response.get_data(
        as_text=True
    )

    assert "Hosted Persistence Assurance" in body
    assert "Runtime gate" in body
    assert "Backup cadence" in body
    assert "Readiness blockers" in body
    assert "Fail closed" in body


def test_hosted_assurance_json(
    client,
):
    set_owner_session(client)

    response = client.get(
        "/tower/observatory-walkthrough/"
        "operations/assurance.json"
    )

    assert response.status_code == 200

    payload = response.get_json()

    assert payload["fail_closed"] is True
    assert payload[
        "automatic_restore"
    ] is False
    assert payload[
        "automatic_cleanup"
    ] is False
    assert payload[
        "direct_vault_write"
    ] is False


def test_retention_approval_preview_route(
    client,
):
    set_owner_session(client)

    response = client.post(
        "/tower/observatory-walkthrough/"
        "operations/assurance/"
        "retention-preview"
    )

    assert response.status_code == 200

    body = response.get_data(
        as_text=True
    )

    assert (
        "Retention Approval Preview Created"
        in body
    )

    assert "Cleanup performed:" in body
    assert "False" in body


def test_storage_incident_receipt_route(
    client,
):
    set_owner_session(client)

    response = client.post(
        "/tower/observatory-walkthrough/"
        "operations/assurance/incident",
        json={
            "incident_type": (
                "backup_cadence_review"
            ),
            "severity": "warning",
            "summary": (
                "Owner requested cadence review."
            ),
        },
    )

    assert response.status_code == 201

    payload = response.get_json()

    assert payload["created"] is True

    assert payload[
        "incident_id"
    ].startswith(
        "obstorageincident_"
    )

    assert payload["receipt"][
        "automatic_restore"
    ] is False


# END HOSTED PERSISTENCE ASSURANCE TESTS
