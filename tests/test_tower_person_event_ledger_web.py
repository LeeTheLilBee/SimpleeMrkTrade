from pathlib import Path

from flask import Flask

import tower.owner_person_event_ledger as ledger


def build_app(monkeypatch, tmp_path):
    app = Flask(__name__)
    app.secret_key = "person-event-ledger-test"

    monkeypatch.setattr(
        ledger,
        "owner_session_active",
        lambda: True,
    )

    ledger_path = tmp_path / "ledger.jsonl"

    monkeypatch.setattr(
        ledger,
        "_runtime_ledger_path",
        lambda: ledger_path,
    )

    @app.route(
        "/tower/owner-dashboard/person/<person_id>"
    )
    def person_room(person_id):
        return f"""
        <!doctype html>
        <html>
          <head></head>
          <body>
            <main>
              <section data-tower-person-control-room="true">
                <h1>{person_id}</h1>
              </section>
            </main>
          </body>
        </html>
        """

    ledger.register_tower_person_event_ledger(
        app
    )

    return app


def test_person_room_gets_history_ui(monkeypatch, tmp_path):
    app = build_app(
        monkeypatch,
        tmp_path,
    )

    response = app.test_client().get(
        "/tower/owner-dashboard/person/future-manager-seat"
    )

    body = response.get_data(
        as_text=True
    )

    assert response.status_code == 200

    assert "tower-person-event-ledger-vault-ready-twr056-060" in body

    assert "Person history + Vault archive" in body

    assert "/history.json" in body


def test_history_empty_initially(monkeypatch, tmp_path):
    app = build_app(
        monkeypatch,
        tmp_path,
    )

    response = app.test_client().get(
        "/tower/owner-dashboard/person/future-manager-seat/history.json"
    )

    data = response.get_json()

    assert response.status_code == 200

    assert data["status"] == "tower_person_history_ready"

    assert data["event_count"] == 0

    assert data["storage_boundary"]["production_archival_durability"] is False


def test_post_person_control_event(monkeypatch, tmp_path):
    app = build_app(
        monkeypatch,
        tmp_path,
    )

    response = app.test_client().post(
        "/tower/owner-dashboard/person/future-manager-seat/event",
        json={
            "action": "designation",
            "requested_designation": "Manager",
            "notes": "Owner review",
        },
    )

    data = response.get_json()

    assert response.status_code == 200

    assert data["status"] == "person_control_event_recorded"

    assert data["event"]["vault_status"] == "NOT_READY_FOR_VAULT"

    history = app.test_client().get(
        "/tower/owner-dashboard/person/future-manager-seat/history.json"
    ).get_json()

    assert history["event_count"] == 1


def test_vault_packet_preview_requires_approved_for_ready(monkeypatch, tmp_path):
    app = build_app(
        monkeypatch,
        tmp_path,
    )

    created = app.test_client().post(
        "/tower/owner-dashboard/person/future-manager-seat/event",
        json={
            "action": "designation",
            "requested_designation": "Manager",
        },
    ).get_json()

    event_id = created["event"]["event_id"]

    held = app.test_client().post(
        f"/tower/owner-dashboard/person/future-manager-seat/event/{event_id}/vault-packet.json",
        json={
            "owner_decision": "HOLD",
        },
    )

    held_data = held.get_json()

    assert held.status_code == 200

    assert held_data["status"] == "vault_person_packet_not_ready"

    approved = app.test_client().post(
        f"/tower/owner-dashboard/person/future-manager-seat/event/{event_id}/vault-packet.json",
        json={
            "owner_decision": "APPROVED",
            "decision_receipt_id": "decision-test",
        },
    )

    approved_data = approved.get_json()

    assert approved.status_code == 200

    assert approved_data["status"] == "vault_person_packet_ready"

    assert approved_data["packet"]["vault_status"] == "READY_FOR_VAULT"

    assert approved_data["vault_delivery_performed"] is False


def test_unknown_person_history_404(monkeypatch, tmp_path):
    app = build_app(
        monkeypatch,
        tmp_path,
    )

    response = app.test_client().get(
        "/tower/owner-dashboard/person/not-real/history.json"
    )

    assert response.status_code == 404


def test_registration_idempotent(monkeypatch, tmp_path):
    app = build_app(
        monkeypatch,
        tmp_path,
    )

    ledger.register_tower_person_event_ledger(
        app
    )

    response = app.test_client().get(
        "/tower/owner-dashboard/person/future-manager-seat"
    )

    body = response.get_data(
        as_text=True
    )

    assert body.count(
        "tower-person-event-ledger-vault-ready-twr056-060"
    ) == 1
