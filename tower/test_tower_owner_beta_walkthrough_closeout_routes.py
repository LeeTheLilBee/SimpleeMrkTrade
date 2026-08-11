from __future__ import annotations

from web.app import app


def test_walkthrough_closeout_routes_registered():
    rules = {rule.rule for rule in app.url_map.iter_rules()}

    assert "/tower/owner-beta/closeout.json" in rules
    assert "/tower/owner-beta/tester-entry-prep.json" in rules


def test_walkthrough_closeout_routes_require_owner_session():
    app.config["TESTING"] = True
    client = app.test_client()

    closeout = client.get("/tower/owner-beta/closeout.json")
    tester_prep = client.get("/tower/owner-beta/tester-entry-prep.json")

    assert closeout.status_code in {401, 403}
    assert tester_prep.status_code in {401, 403}
    assert closeout.get_json()["reason"] == "owner_session_required"
    assert tester_prep.get_json()["reason"] == "owner_session_required"


def test_walkthrough_closeout_routes_allowed_with_owner_session():
    app.config["TESTING"] = True
    client = app.test_client()

    with client.session_transaction() as session:
        session["owner_id"] = "owner_solice"
        session["role"] = "owner"

    closeout = client.get("/tower/owner-beta/closeout.json")
    tester_prep = client.get("/tower/owner-beta/tester-entry-prep.json")

    assert closeout.status_code == 200
    assert tester_prep.status_code == 200

    closeout_payload = closeout.get_json()
    prep_payload = tester_prep.get_json()

    assert closeout_payload["version"] == "tower_owner_beta_walkthrough_closeout_v1"
    assert closeout_payload["all_required_walkthrough_steps_ready"] is True
    assert closeout_payload["tester_entry_open"] is False
    assert closeout_payload["dangerous_controls_locked"] is True

    assert prep_payload["status"] == "prepared_not_open"
    assert prep_payload["tester_entry_open"] is False
    assert prep_payload["tester_invites_sent"] is False
    assert prep_payload["external_accounts_created"] is False
    assert prep_payload["dangerous_controls_locked"] is True
