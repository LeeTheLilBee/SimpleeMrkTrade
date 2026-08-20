from flask import Flask

import tower.owner_person_archive_vault_queue_binding as binding


def build_app(
    monkeypatch,
):

    app = Flask(
        __name__
    )

    app.secret_key = (
        "archive-vault-queue-test"
    )


    monkeypatch.setattr(
        binding,
        "owner_session_active",
        lambda: True,
    )


    @app.route(
        "/tower/owner-dashboard/person/<person_id>"
    )
    def person_room(
        person_id,
    ):

        return """
        <html>
          <body>
            <section data-tower-person-control-room="true"></section>
          </body>
        </html>
        """


    binding.register_tower_person_archive_vault_queue_binding(
        app
    )


    return app


def test_person_room_gets_archive_queue_surface(
    monkeypatch,
):

    app = (
        build_app(
            monkeypatch
        )
    )


    response = (
        app.test_client().get(

            "/tower/owner-dashboard/person/"
            "future-manager-seat"
        )
    )


    body = (
        response.get_data(
            as_text=True
        )
    )


    assert (
        response.status_code
        == 200
    )


    assert (
        "tower-person-real-archive-vault-queue-binding-twr071-075"
        in body
    )


    assert (
        "Archive Vault handoff queue"
        in body
    )


    assert (
        "Queued does not mean Vault accepted or sealed"
        in body
    )


    assert (
        "Queue approved proof for Archive Vault"
        in body
    )


def test_queue_route_returns_real_queue_result(
    monkeypatch,
):

    app = (
        build_app(
            monkeypatch
        )
    )


    monkeypatch.setattr(

        binding,

        "queue_person_event_for_archive_vault",

        lambda person_id, event_id, owner_note="": {

            "status": (
                "person_archive_vault_handoff_queued"
            ),

            "vault_status": (
                "VAULT_HANDOFF_QUEUED"
            ),

            "handoff_id": (
                "archivehandoff-test"
            ),

            "vault_accepted": False,

            "vault_sealed": False,
        },
    )


    response = (
        app.test_client().post(

            "/tower/owner-dashboard/person/"
            "future-manager-seat/event/"
            "event-test/archive-vault-queue",

            json={
                "owner_note": "test",
            },
        )
    )


    data = (
        response.get_json()
    )


    assert (
        response.status_code
        == 200
    )


    assert (
        data[
            "vault_status"
        ]
        == "VAULT_HANDOFF_QUEUED"
    )


    assert (
        data[
            "vault_sealed"
        ]
        is False
    )


def test_registration_idempotent(
    monkeypatch,
):

    app = (
        build_app(
            monkeypatch
        )
    )


    binding.register_tower_person_archive_vault_queue_binding(
        app
    )


    response = (
        app.test_client().get(

            "/tower/owner-dashboard/person/"
            "future-manager-seat"
        )
    )


    body = (
        response.get_data(
            as_text=True
        )
    )


    assert (
        body.count(
            "tower-person-real-archive-vault-queue-binding-twr071-075"
        )
        == 1
    )
