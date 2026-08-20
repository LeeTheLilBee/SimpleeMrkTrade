from flask import Flask

import tower.owner_person_vault_handoff_adapter as adapter


def build_app(monkeypatch):

    app = Flask(__name__)
    app.secret_key = "vault-adapter-test"

    monkeypatch.setattr(
        adapter,
        "owner_session_active",
        lambda: True,
    )

    @app.route("/tower/owner-dashboard/person/<person_id>")
    def room(person_id):
        return """
        <html>
        <body>
          <section data-tower-person-control-room="true"></section>
        </body>
        </html>
        """

    adapter.register_tower_person_vault_handoff_adapter(
        app
    )

    return app


def test_ui(monkeypatch):
    app = build_app(monkeypatch)

    response = app.test_client().get(
        "/tower/owner-dashboard/person/future-manager-seat"
    )

    body = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "tower-person-existing-vault-handoff-adapter-twr066-070" in body
    assert "Vault archive handoff" in body
    assert "Send approved event to Vault" in body
    assert "browser does not call Vault directly" in body


def test_unresolved_route_returns_503(monkeypatch):

    app = build_app(monkeypatch)

    monkeypatch.setattr(
        adapter,
        "deliver_person_event_to_existing_vault_handoff",
        lambda person_id, event_id: {
            "status": "existing_vault_handoff_not_resolved",
            "vault_delivery_performed": False,
        },
    )

    response = app.test_client().post(
        "/tower/owner-dashboard/person/future-manager-seat/event/event-1/vault-handoff",
        json={},
    )

    assert response.status_code == 503
