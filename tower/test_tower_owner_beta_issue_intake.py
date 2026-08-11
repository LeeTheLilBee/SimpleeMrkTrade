from __future__ import annotations

import json

import pytest

from tower.tower_owner_beta_issue_intake import (
    build_issue_record,
    create_issue,
    create_review_receipt,
    dangerous_controls_locked,
    intake_contract,
    issue_intake_cert,
    list_issues,
    list_review_receipts,
)


def test_intake_contract_is_owner_gated_and_safe():
    contract = intake_contract()

    assert contract["version"] == "tower_owner_beta_issue_intake_v1"
    assert contract["requires_owner_session"] is True
    assert contract["persistence"]["mode"] == "append_only_jsonl"
    assert contract["dangerous_controls_locked"] is True
    assert all(value is False for value in contract["dangerous_controls"].values())


def test_build_issue_record_requires_title_and_description():
    with pytest.raises(ValueError):
        build_issue_record({"description": "Missing title"})

    with pytest.raises(ValueError):
        build_issue_record({"title": "Missing description"})


def test_create_issue_persists_append_only_jsonl(tmp_path):
    store = tmp_path / "issues.jsonl"

    issue = create_issue(
        {
            "title": "Market Map needs calmer deep dives",
            "description": "During owner walkthrough, the Market Map needs clearer deep-dive pathing.",
            "category": "market_map",
            "severity": "high",
            "room": "Market Map",
            "soulaana_note": "Explain why this matters before showing more cards.",
            "owner_requested_action": "Make the page easier to read.",
        },
        owner_id="owner_solice",
        store_path=str(store),
    )

    assert issue["record_type"] == "tower_owner_beta_issue"
    assert issue["category"] == "market_map"
    assert issue["severity"] == "high"
    assert issue["classification"] == "market_map_deep_dive"
    assert issue["soulaana_note"]
    assert issue["dangerous_controls_locked"] is True

    issues = list_issues(store_path=str(store))
    assert len(issues) == 1
    assert issues[0]["issue_id"] == issue["issue_id"]


def test_review_receipt_links_issue_and_hash(tmp_path):
    store = tmp_path / "issues.jsonl"

    issue = create_issue(
        {
            "title": "Soulaana needs a stronger explanation",
            "description": "The owner needs the page to explain what changed and what to do next.",
            "category": "soulaana",
            "severity": "medium",
            "blocker_id": "soulaana_interpretation",
        },
        owner_id="owner_solice",
        store_path=str(store),
    )

    receipt = create_review_receipt(
        issue,
        reviewer_id="owner_solice",
        decision="triaged",
        notes="Review this before beta tester entry.",
        store_path=str(store),
    )

    assert receipt["record_type"] == "tower_owner_beta_review_receipt"
    assert receipt["issue_id"] == issue["issue_id"]
    assert receipt["issue_hash"] == issue["issue_hash"]
    assert receipt["blocker_id"] == "soulaana_interpretation"
    assert receipt["dangerous_controls_locked"] is True

    receipts = list_review_receipts(store_path=str(store))
    assert len(receipts) == 1
    assert receipts[0]["receipt_id"] == receipt["receipt_id"]


def test_issue_intake_certs_2573_to_2582():
    for pack in range(2573, 2583):
        cert = issue_intake_cert(pack)

        assert cert["pack"] == pack
        assert cert["status"] == "passed"
        assert cert["requires_owner_session"] is True
        assert cert["persistence_mode"] == "append_only_jsonl"
        assert cert["dangerous_controls_locked"] is True
        assert all(value is False for value in cert["dangerous_controls"].values())


def test_dangerous_controls_locked():
    assert dangerous_controls_locked() is True
