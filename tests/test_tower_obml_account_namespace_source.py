"""Offline Tower-side source-signature acceptance, not owner authentication."""
from dataclasses import asdict, replace
import base64
import hashlib
import hmac
import json
from pathlib import Path

import pytest

from web.ob_account_identity_truth import resolve_account_identity, SCHEMA_VERSION
from tower.obml_account_namespace_source import (
    SOURCE_SCHEMA, RECEIPT_SCHEMA, ISSUER, AUDIENCE, PREFIX,
    NamespaceSourceRefused, verify_ob_account_namespace_source,
    namespace_source_contract,
)

SECRET = b"synthetic-source-key-for-offline-tests-not-a-production-key-0123456"
NOW = 2_000_000_000


class AtomicFixture:
    def __init__(self):
        self.used = set()
        self.calls = 0

    def __call__(self, account, nonce, expires):
        self.calls += 1
        key = (account, nonce)
        if key in self.used:
            return False
        self.used.add(key)
        return True


def claims_for(account="trust", **overrides):
    source = resolve_account_identity(account)
    base = {
        "schema_version": SOURCE_SCHEMA, "source_schema_version": SCHEMA_VERSION,
        "issuer": ISSUER, "audience": AUDIENCE,
        "account_key": account,
        "account_identity_fingerprint": source["identity_fingerprint"],
        "namespace_authority": source["namespace_authority"],
        "account_class": source.get("account_class"),
        "capital_truth_class": source.get("capital_truth_class"),
        "nonce": "a" * 32, "issued_at_epoch": NOW,
        "expires_at_epoch": NOW + 60,
        "owner_authentication_asserted": False, "broker_account_verified": False,
        "real_capital_verified": False, "manual_live_granted": False,
    }
    return {**base, **overrides}


def sign(claims, *, key=SECRET, raw=None):
    if raw is None:
        raw = json.dumps(claims, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
    payload = base64.urlsafe_b64encode(raw).decode().rstrip("=")
    head = PREFIX + "." + payload
    mac = hmac.new(key, head.encode("ascii"), hashlib.sha256).digest()
    return head + "." + base64.urlsafe_b64encode(mac).decode().rstrip("=")


@pytest.mark.parametrize("account", (
    "personal", "trust", "simplee_world_business",
    "simplee_on_the_go_atm", "the_grounds_apartment",
))
def test_exact_signed_mission_account_receipt_never_authorizes_live(account):
    replay = AtomicFixture()
    result = verify_ob_account_namespace_source(
        sign(claims_for(account)), now_epoch=NOW, verification_key=SECRET,
        consume_once=replay,
    )
    assert result.authority == RECEIPT_SCHEMA
    assert result.account_key == account
    assert result.signature_verified_with_trusted_injected_key is True
    assert result.one_time_nonce_consumed_by_caller_store is True
    assert replay.calls == 1
    for key in (
        "owner_authentication_verified", "tower_session_verified",
        "tower_permission_verified", "tower_step_up_verified",
        "tower_revocation_verified", "broker_account_verified",
        "real_capital_verified", "manual_live_granted",
        "broker_order_api_authorized", "capital_movement_authorized",
    ):
        assert getattr(result, key) is False
    assert not any(field in asdict(result) for field in (
        "nonce", "signed_token", "session_cookie", "broker_token", "secret",
        "balance", "settled_cash",
    ))


def test_atomic_consume_once_rejects_replay_both_same_and_distinct_account():
    replay = AtomicFixture()
    token = sign(claims_for())
    kw = dict(now_epoch=NOW, verification_key=SECRET, consume_once=replay)
    verify_ob_account_namespace_source(token, **kw)
    with pytest.raises(NamespaceSourceRefused):
        verify_ob_account_namespace_source(token, **kw)
    assert replay.calls == 2
    # A new nonce is a different source receipt, never permission.
    revised = sign(claims_for(nonce="b" * 32))
    assert verify_ob_account_namespace_source(revised, **kw).manual_live_granted is False


@pytest.mark.parametrize("override", (
    {"schema_version": "UNKNOWN"}, {"source_schema_version": "UNKNOWN"},
    {"issuer": "THE_TOWER"}, {"audience": "anything-else"},
    {"account_key": "proof_demo"}, {"account_key": "UNKNOWN"},
    {"account_class": "SIMULATED_PROOF_DEMO"},
    {"capital_truth_class": "CURRENT"},
    {"account_identity_fingerprint": "0"*64}, {"namespace_authority": "FORGED"},
    {"owner_authentication_asserted": True}, {"broker_account_verified": True},
    {"real_capital_verified": True}, {"manual_live_granted": True},
    {"nonce": "not-a-nonce"}, {"issued_at_epoch": NOW + 1},
    {"issued_at_epoch": True}, {"expires_at_epoch": NOW},
    {"expires_at_epoch": NOW + 61}, {"expires_at_epoch": True},
    {"account_key": "trust "}, {"surprise_access_token": "never"},
))
def test_signed_but_invalid_source_claim_fails_before_nonce(override):
    replay = AtomicFixture()
    with pytest.raises(NamespaceSourceRefused, match="OB_ACCOUNT_NAMESPACE_SOURCE_REFUSED"):
        verify_ob_account_namespace_source(
            sign(claims_for(**override)), now_epoch=NOW,
            verification_key=SECRET, consume_once=replay,
        )
    assert replay.calls == 0


def test_wrong_key_tamper_missing_secret_and_no_consumer_fail_closed():
    token = sign(claims_for())
    cases = [
        dict(verification_key=b"wrong-secret-value-long-enough-for-check-0123456789",
             consume_once=AtomicFixture(), now_epoch=NOW),
        dict(verification_key=b"short", consume_once=AtomicFixture(), now_epoch=NOW),
        dict(verification_key=SECRET, consume_once=None, now_epoch=NOW),
        dict(verification_key=SECRET, consume_once=AtomicFixture(), now_epoch=True),
        dict(verification_key=SECRET, consume_once=AtomicFixture(), now_epoch=NOW+60),
    ]
    for kw in cases:
        with pytest.raises(NamespaceSourceRefused):
            verify_ob_account_namespace_source(token, **kw)
    prefix, body, mac = token.split(".")
    modified = prefix + "." + body + "." + ("A" if mac[0] != "A" else "B") + mac[1:]
    replay = AtomicFixture()
    with pytest.raises(NamespaceSourceRefused):
        verify_ob_account_namespace_source(
            modified, now_epoch=NOW, verification_key=SECRET, consume_once=replay,
        )
    assert replay.calls == 0


def test_duplicate_json_claims_signed_with_valid_mac_still_denied():
    raw = json.dumps(claims_for(), separators=(",", ":")).encode()
    raw = raw.replace(b'"issuer":', b'"issuer":"evil","issuer":', 1)
    replay = AtomicFixture()
    with pytest.raises(NamespaceSourceRefused):
        verify_ob_account_namespace_source(
            sign(None, raw=raw), now_epoch=NOW, verification_key=SECRET,
            consume_once=replay,
        )
    assert replay.calls == 0


@pytest.mark.parametrize("bad", (
    "x", "", "obai1.a.b.c", " obai1.x.y", "obai1.x.y ",
    "a"*4097, "obai1.?.bad", "obai1.=.bad",
))
def test_invalid_transport_is_generic_denial_without_nonce(bad):
    replay = AtomicFixture()
    with pytest.raises(NamespaceSourceRefused, match="OB_ACCOUNT_NAMESPACE_SOURCE_REFUSED"):
        verify_ob_account_namespace_source(
            bad, now_epoch=NOW, verification_key=SECRET, consume_once=replay,
        )
    assert replay.calls == 0


def test_nonce_storage_outage_and_non_bool_return_fail_closed():
    token = sign(claims_for())
    def outage(*_):
        raise OSError("private data path")
    for callback in (outage, lambda *args: 1, lambda *args: None, lambda *args: False):
        with pytest.raises(NamespaceSourceRefused, match="OB_ACCOUNT_NAMESPACE_SOURCE_REFUSED"):
            verify_ob_account_namespace_source(
                token, now_epoch=NOW, verification_key=SECRET, consume_once=callback,
            )


def test_source_contract_explicitly_avoids_route_session_grant_or_paid_service():
    c = namespace_source_contract()
    assert c["atomic_durable_nonce_consumption_required"] is True
    assert c["trusted_server_side_key_injection_required"] is True
    for key in (
        "default_nonce_store_provided", "public_route_registered",
        "production_secret_configured", "source_signature_is_owner_authentication",
        "source_signature_is_tower_permission",
        "source_signature_is_real_broker_or_capital_truth",
        "manual_live_grant", "broker_order_api", "capital_movement",
        "paid_services_provisioned",
    ):
        assert c[key] is False
    import tower.obml_account_namespace_source as module
    text = Path(module.__file__).read_text()
    assert "@app.route(" not in text
    assert "requests.post(" not in text
    assert "os.environ" not in text
