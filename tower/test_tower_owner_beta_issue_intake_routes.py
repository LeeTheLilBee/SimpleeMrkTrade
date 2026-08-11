from __future__ import annotations

from web.app import app


def test_issue_intake_routes_registered():
    rules = {rule.rule for rule in app.url_map.iter_rules()}

    assert "/tower/owner-beta/issues.json" in rules
    assert "/tower/owner-beta/review-receipts.json" in rules


def test_issue_intake_routes_require_owner_session(tmp_path, monkeypatch):
    monkeypatch.setenv("TOWER_OWNER_BETA_ISSUE_STORE", str(tmp_path / "issues.jsonl"))

    app.config["TESTING"] = True
    client = app.test_client()

    list_response = client.get("/tower/owner-beta/issues.json")
    post_response = client.post(
        "/tower/owner-beta/issues.json",
        json={
            "title": "Should not submit",
            "description": "Anonymous submit should be denied.",
        },
    )
    receipts_response = client.get("/tower/owner-beta/review-receipts.json")

    assert list_response.status_code in {401, 403}
    assert post_response.status_code in {401, 403}
    assert receipts_response.status_code in {401, 403}

    assert list_response.get_json()["reason"] == "owner_session_required"
    assert post_response.get_json()["reason"] == "owner_session_required"
    assert receipts_response.get_json()["reason"] == "owner_session_required"


def test_issue_intake_owner_session_submit_and_list(tmp_path, monkeypatch):
    monkeypatch.setenv("TOWER_OWNER_BETA_ISSUE_STORE", str(tmp_path / "issues.jsonl"))

    app.config["TESTING"] = True
    client = app.test_client()

    with client.session_transaction() as session:
        session["owner_id"] = "owner_solice"
        session["role"] = "owner"

    empty = client.get("/tower/owner-beta/issues.json")
    assert empty.status_code == 200
    assert empty.get_json()["issues"] == []

    created = client.post(
        "/tower/owner-beta/issues.json",
        json={
            "title": "Owner Beta card needs clearer copy",
            "description": "During walkthrough, make the cards easier to interpret.",
            "category": "tower_ui",
            "severity": "medium",
            "room": "Owner Beta Control Room",
            "soulaana_note": "Summarize the page in one calm sentence.",
            "owner_requested_action": "Make owner decision clearer.",
        },
    )

    assert created.status_code == 201

    created_payload = created.get_json()
    issue = created_payload["issue"]
    receipt = created_payload["review_receipt"]

    assert created_payload["dangerous_controls_locked"] is True
    assert issue["record_type"] == "tower_owner_beta_issue"
    assert issue["owner_id"] == "owner_solice"
    assert issue["dangerous_controls_locked"] is True
    assert receipt["record_type"] == "tower_owner_beta_review_receipt"
    assert receipt["issue_id"] == issue["issue_id"]

    listed = client.get("/tower/owner-beta/issues.json")
    assert listed.status_code == 200
    assert len(listed.get_json()["issues"]) == 1

    receipts = client.get("/tower/owner-beta/review-receipts.json")
    assert receipts.status_code == 200
    assert len(receipts.get_json()["review_receipts"]) == 1
