"""TWR207-211: exact, sealed BuyBox receiver interoperability regression."""
from __future__ import annotations

import importlib.util
import sqlite3
import sys
import tempfile
from pathlib import Path

import pytest

from tower import buybox_handoff_wire as wire
from tower.app_registry import route_by_path
from tower.app_truth_projection import app_truth_by_id

ROOT = Path(__file__).resolve().parents[1]
RECEIVER_SOURCE = ROOT / "receiver-source" / "buybox" / "tower_owner_receiver.py"
if not RECEIVER_SOURCE.is_file():
    raise RuntimeError("Exact sealed BuyBox receiver checkout is required for interop CI.")
spec = importlib.util.spec_from_file_location("exact_buybox_receiver", RECEIVER_SOURCE)
receiver = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = receiver
spec.loader.exec_module(receiver)

NOW = 2_000_000_000
SECRET = "synthetic-cross-app-shared-secret-0123456789ABCDEF"


def claims(**changes):
    item = {
        "schema_version": wire.SCHEMA_VERSION,
        "issuer": wire.ISSUER,
        "audience": wire.AUDIENCE,
        "purpose": wire.PURPOSE,
        "handoff_id": "handoff_" + "a" * 32,
        "tower_session_ref": "tower_session_" + "b" * 32,
        "actor_ref": "actor_" + "c" * 32,
        "entity_ref": "entity_" + "d" * 32,
        "owner_entitlement_ref": "entitlement_" + "e" * 32,
        "issued_at_epoch": NOW,
        "expires_at_epoch": NOW + 60,
        "target_path": "/",
        "return_path": "/tower/access-home",
    }
    item.update(changes)
    return item


def sign(item, secret=SECRET):
    return wire._encode_verified_source_contract(
        item, shared_secret=secret, now_epoch=NOW
    )


def test_exact_tower_wire_matches_independent_sealed_buybox_receiver():
    token = sign(claims())
    verified = receiver.verify_tower_buybox_owner_handoff(
        token, shared_secret=SECRET, now_epoch=NOW
    )
    assert verified.claims["issuer"] == "tower"
    assert verified.claims["audience"] == "buybox-owner"
    assert verified.claims["target_path"] == "/"
    assert verified.claims["return_path"] == "/tower/access-home"
    assert verified.claims["expires_at_epoch"] - verified.claims["issued_at_epoch"] == 60
    with tempfile.TemporaryDirectory() as directory:
        file = Path(directory) / "ledger.sqlite3"
        with sqlite3.connect(file) as db:
            assert receiver.consume_verified_handoff(db, verified) is True
        with sqlite3.connect(file) as db:
            assert receiver.consume_verified_handoff(db, verified) is False


@pytest.mark.parametrize("change", [
    {"issuer": "buybox"}, {"audience": "teller-persistence"},
    {"target_path": "/unauthorized"}, {"return_path": "//evil.test"},
    {"purpose": "closing"}, {"actor_ref": "short"},
    {"owner_entitlement_ref": "short"},
    {"expires_at_epoch": NOW + 61}, {"issued_at_epoch": True},
    {"extra_granted_flag": True},
])
def test_private_tower_serializer_rejects_wrong_claims(change):
    with pytest.raises(wire.TowerBuyBoxWireError):
        sign(claims(**change))


def test_wrong_receiver_key_and_expired_timestamp_fail():
    valid = sign(claims())
    with pytest.raises(receiver.TowerBuyBoxHandoffError):
        receiver.verify_tower_buybox_owner_handoff(
            valid, shared_secret="unrelated-32-byte-key-01234567890", now_epoch=NOW
        )
    with pytest.raises(receiver.TowerBuyBoxHandoffError):
        receiver.verify_tower_buybox_owner_handoff(
            valid, shared_secret=SECRET, now_epoch=NOW + 61
        )


def test_public_issuer_unconditionally_blocked_even_on_forged_green_preflight(monkeypatch):
    monkeypatch.setattr(wire, "inspect_current_buybox_owner_preflight", lambda: {
        "app_id": "buybox", "state": "READY", "can_issue_handoff": True
    })
    with pytest.raises(wire.TowerBuyBoxWireError, match="BUYBOX_HOSTED_RECEIVER_NOT_CONNECTED"):
        wire.issue_current_owner_buybox_handoff()


def test_launch_gate_exists_without_manufacturing_product_entitlement():
    launch = route_by_path("/tower/launch/buybox")
    assert launch is not None
    assert launch["owner_only"] is True
    assert launch["requires_owner_session"] is True
    assert launch["requires_step_up"] is True
    assert launch["lock_state"] == "protected_fail_closed_launch_gate"
    assert route_by_path("/buybox") is None
    truth = app_truth_by_id("buybox")
    assert truth is not None
    assert truth["launchable"] is False
    assert wire.SCHEMA_VERSION == receiver.SCHEMA_VERSION
    assert wire.CLAIM_KEYS == receiver.HANDOFF_KEYS


def test_source_issuer_not_an_http_endpoint_or_buybox_direct_dependency():
    source = Path(wire.__file__).read_text(encoding="utf-8")
    assert "@app.route(" not in source
    assert "from buybox." not in source
    assert "from vault." not in source
    assert "from observatory." not in source
    assert "requests.post(" not in source
