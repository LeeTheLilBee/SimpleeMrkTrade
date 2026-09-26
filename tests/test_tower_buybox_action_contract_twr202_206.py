"""TWR202-206: synthetic fail-closed BuyBox action and owner preflight tests."""
from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timedelta, timezone

import pytest
from flask import Flask

from tower.buybox_action_contract import (
    ACTION_PURPOSES, PROTECTED_ACTIONS, SCHEMA_VERSION, VERTICAL_IDS,
    BuyBoxActionDraftError, buybox_action_draft_fingerprint,
    draft_matches_current_opportunity, prepare_buybox_action_review,
    validate_buybox_action_draft,
)
from tower import buybox_owner_preflight as preflight

NOW = datetime(2026, 9, 26, 22, 30, tzinfo=timezone.utc)
SHA = "a" * 64


def draft(**changes):
    packet = {
        "schema_version": SCHEMA_VERSION,
        "source_app": "buybox",
        "destination": "tower",
        "request_id": "req-1",
        "idempotency_key": "req-1-1",
        "correlation_id": "corr-1",
        "opportunity_id": "op-1",
        "opportunity_revision": 7,
        "input_snapshot_digest": SHA,
        "vertical_id": "atm",
        "requester_identity_ref": "claimed-actor-ref",
        "requester_entity_ref": "claimed-entity-ref",
        "requested_action": "READ_OPPORTUNITY",
        "purpose": ACTION_PURPOSES["READ_OPPORTUNITY"],
        "issued_at": NOW.isoformat(),
        "valid_until": (NOW + timedelta(seconds=300)).isoformat(),
        "data_classification": "CONFIDENTIAL",
    }
    packet.update(changes)
    return packet


@pytest.mark.parametrize("vertical", sorted(VERTICAL_IDS))
def test_all_seven_source_verticals_supported_without_importing_buybox(vertical):
    valid = validate_buybox_action_draft(draft(vertical_id=vertical), now_utc=NOW)
    assert valid["vertical_id"] == vertical


@pytest.mark.parametrize("action", sorted(ACTION_PURPOSES))
def test_every_action_is_never_auto_authorized(action):
    outcome = prepare_buybox_action_review(
        draft(requested_action=action, purpose=ACTION_PURPOSES[action]), now_utc=NOW
    )
    assert outcome["authorizes_action"] is False
    assert outcome["state"] == "UNTRUSTED_DRAFT"
    assert outcome["issuer_receipt_present"] is False
    assert outcome["teller_readiness"] == "UNKNOWN"
    assert outcome["external_call_made"] is False
    assert outcome["action_class"] == (
        "PROTECTED" if action in PROTECTED_ACTIONS else "REVIEW_ONLY"
    )


@pytest.mark.parametrize("field,value", [
    ("schema_version", "other"), ("source_app", "observatory"),
    ("destination", "vault"), ("vertical_id", "unknown"),
    ("requested_action", "APPROVE_ALL"), ("opportunity_revision", True),
    ("opportunity_revision", 0), ("opportunity_revision", "7"),
    ("input_snapshot_digest", "NOT_SHA"), ("data_classification", "PUBLIC"),
    ("requester_identity_ref", ""), ("request_id", "../unsafe"),
])
def test_rejects_unknown_or_unsafe_fields(field, value):
    with pytest.raises(BuyBoxActionDraftError):
        validate_buybox_action_draft(draft(**{field: value}), now_utc=NOW)


@pytest.mark.parametrize("key", sorted(draft()))
def test_missing_fields_fail_closed(key):
    packet = draft()
    del packet[key]
    with pytest.raises(BuyBoxActionDraftError):
        validate_buybox_action_draft(packet, now_utc=NOW)


@pytest.mark.parametrize("additional", [
    {"approved": True}, {"tower_session_id": "fake"},
    {"access_token": "fake"}, {"broker_balance": "100000"},
])
def test_client_cannot_smuggle_extra_claims(additional):
    with pytest.raises(BuyBoxActionDraftError):
        validate_buybox_action_draft(draft(**additional), now_utc=NOW)


def test_intent_requires_exact_purpose_and_timezone():
    with pytest.raises(BuyBoxActionDraftError):
        validate_buybox_action_draft(draft(requested_action="AUTHORIZE_CLOSING"), now_utc=NOW)
    with pytest.raises(BuyBoxActionDraftError):
        validate_buybox_action_draft(draft(issued_at="2026-09-26T22:30:00"), now_utc=NOW)
    with pytest.raises(BuyBoxActionDraftError):
        validate_buybox_action_draft(draft(valid_until="2026-09-26T22:35:00"), now_utc=NOW)


def test_expired_long_lived_future_and_zero_lifetime_fail_closed():
    bad = [
        draft(valid_until=NOW.isoformat()),
        draft(valid_until=(NOW + timedelta(seconds=301)).isoformat()),
        draft(issued_at=(NOW + timedelta(seconds=31)).isoformat(),
              valid_until=(NOW + timedelta(seconds=60)).isoformat()),
        draft(issued_at=(NOW + timedelta(seconds=10)).isoformat(),
              valid_until=(NOW + timedelta(seconds=10)).isoformat()),
    ]
    for packet in bad:
        with pytest.raises(BuyBoxActionDraftError):
            validate_buybox_action_draft(packet, now_utc=NOW)


def test_changed_opportunity_revision_or_digest_invalidates_draft():
    packet = draft()
    assert draft_matches_current_opportunity(
        packet, current_opportunity_id="op-1", current_revision=7,
        current_snapshot_digest=SHA, now_utc=NOW,
    )
    for item in [
        {"current_opportunity_id": "op-2", "current_revision": 7, "current_snapshot_digest": SHA},
        {"current_opportunity_id": "op-1", "current_revision": 8, "current_snapshot_digest": SHA},
        {"current_opportunity_id": "op-1", "current_revision": 7, "current_snapshot_digest": "b" * 64},
        {"current_opportunity_id": "op-1", "current_revision": True, "current_snapshot_digest": SHA},
    ]:
        assert not draft_matches_current_opportunity(packet, now_utc=NOW, **item)
    assert buybox_action_draft_fingerprint(packet, now_utc=NOW) != buybox_action_draft_fingerprint(
        draft(input_snapshot_digest="b" * 64), now_utc=NOW
    )
    assert buybox_action_draft_fingerprint(packet, now_utc=NOW) != buybox_action_draft_fingerprint(
        draft(opportunity_revision=8), now_utc=NOW
    )


def test_validator_does_not_mutate_caller_packet():
    packet = draft()
    before = deepcopy(packet)
    valid = validate_buybox_action_draft(packet, now_utc=NOW)
    valid["requested_action"] = "AUTHORIZE_CLOSING"
    assert packet == before


@pytest.mark.parametrize("signed_in,stepped_up,identity_verified,entitled,launchable", [
    (False, False, False, False, False),
    (True, False, True, True, True),
    (True, True, True, False, True),
    (True, True, True, True, False),
    (True, True, True, True, True),
])
def test_preflight_never_issues_handoff(
    monkeypatch, signed_in, stepped_up, identity_verified, entitled, launchable
):
    app = Flask(__name__)
    app.secret_key = "synthetic-test-only-secret"
    with app.test_request_context("/tower/app-registry"):
        monkeypatch.setattr(preflight, "owner_session_active", lambda: signed_in)
        monkeypatch.setattr(preflight, "step_up_active", lambda: stepped_up)
        monkeypatch.setattr(preflight, "hosted_owner_identity_authority", lambda: {
            "verification_state": "VERIFIED" if identity_verified else "NOT_CONFIGURED",
            "app_entitlements": [{
                "app_id": "buybox",
                "verification_state": "VERIFIED",
                "access_policy": "GRANTED",
            }] if entitled else [],
        })
        monkeypatch.setattr(preflight, "app_truth_by_id",
                            lambda _: {"app_id": "buybox", "launchable": launchable})
        response = preflight.inspect_current_buybox_owner_preflight()
    assert response["state"] == "BLOCKED"
    assert response["can_issue_handoff"] is False
    assert response["application_access_granted"] is False
    assert response["receiver_connected"] is False
    assert response["sensitive_data_returned"] is False
    assert "BUYBOX_HOSTED_RECEIVER_NOT_CONNECTED" in response["reason_codes"]


def test_contract_and_gate_never_import_foreign_systems_or_register_http_routes():
    from pathlib import Path
    import tower.buybox_action_contract as contract
    for module in (contract, preflight):
        source = Path(module.__file__).read_text(encoding="utf-8")
        assert "from buybox." not in source
        assert "from vault." not in source
        assert "from observatory." not in source
        assert "@app.route(" not in source
        assert "requests.post(" not in source
