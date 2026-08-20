from flask import Flask

import tower.owner_person_decision_workflow as decisions
import tower.owner_person_event_ledger as ledger


def build_app(monkeypatch, tmp_path):

    app = Flask(__name__)
    app.secret_key = "decision-test"

    path = tmp_path / "ledger.jsonl"

    monkeypatch.setattr(
        ledger,
        "_runtime_ledger_path",
        lambda: path,
    )

    monkeypatch.setattr(
        decisions,
        "read_person_events",
        ledger.read_person_events,
    )

    monkeypatch.setattr(
        decisions,
        "read_event_by_id",
        ledger.read_event_by_id,
    )

    monkeypatch.setattr(
        decisions,
        "append_person_event",
        ledger.append_person_event,
    )

    monkeypatch.setattr(
        decisions,
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

    decisions.register_tower_person_owner_decision(app)

    return app, path


def seed(path):
    event = ledger.build_person_event(
        "future-manager-seat",
        event_type="PERSON_CONTROL_DRAFT",
        action="designation",
        requested_state={"designation": "Manager"},
    )["event"]

    ledger.append_person_event(
        event,
        ledger_path=path,
    )

    return event


def test_ui(monkeypatch, tmp_path):
    app, path = build_app(monkeypatch, tmp_path)

    response = app.test_client().get(
        "/tower/owner-dashboard/person/future-manager-seat"
    )

    body = response.get_data(as_text=True)

    assert "tower-person-owner-decision-twr061-065" in body
    assert "Owner Decision Queue" in body
    assert "Record owner decision" in body


def test_decisions_json(monkeypatch, tmp_path):
    app, path = build_app(monkeypatch, tmp_path)
    seed(path)

    response = app.test_client().get(
        "/tower/owner-dashboard/person/future-manager-seat/decisions.json"
    )

    data = response.get_json()

    assert response.status_code == 200
    assert data["pending_count"] == 1


def test_approve_route(monkeypatch, tmp_path):
    app, path = build_app(monkeypatch, tmp_path)

    event = seed(path)

    response = app.test_client().post(
        f"/tower/owner-dashboard/person/future-manager-seat/event/{event['event_id']}/decision",
        json={
            "decision": "APPROVED",
            "reason": "Owner approved",
        },
    )

    data = response.get_json()

    assert response.status_code == 200
    assert data["decision"] == "APPROVED"
    assert data["decision_receipt"]["effective_vault_status"] == "READY_FOR_VAULT"
