"""Actual source-producer → independent Tower source-consumer interoperability.

No mocked signed payloads or network/hosted connection. Synthetic test keys
only. A valid source receipt is explicitly never owner/Tower/broker clearance.
"""
from dataclasses import asdict

import pytest

from web.ob_account_identity_truth import resolve_account_identity
from web.ob_tower_account_identity_export import (
    OBAccountIdentityExportError,
    create_ob_account_identity_export, source_export_contract,
)
from tower.obml_account_namespace_source import (
    NamespaceSourceRefused, verify_ob_account_namespace_source,
    namespace_source_contract, ISSUER, AUDIENCE,
)

TEST_SOURCE_KEY = b"test-only-key-ob-tower-namespace-interop-2026-abcdef0123456789"
WRONG_KEY = b"test-only-other-source-key-2026-abcdef0123456789012"
NOW = 2_000_000_000
ACCOUNTS = (
    "personal", "trust", "simplee_world_business",
    "simplee_on_the_go_atm", "the_grounds_apartment",
)


class SharedAtomicNonceStore:
    """Model a shared atomic store contract, NOT production persistence."""
    def __init__(self):
        self._seen = set()
        self.calls = 0

    def consume(self, account_key, nonce, expiry):
        self.calls += 1
        identity = (account_key, nonce)
        if identity in self._seen:
            return False
        self._seen.add(identity)
        return True


def export(account="trust", key=TEST_SOURCE_KEY, now=NOW):
    return create_ob_account_identity_export(
        account, now_epoch=now, signing_secret=key,
    )


def verify(token, storage, key=TEST_SOURCE_KEY, now=NOW):
    return verify_ob_account_namespace_source(
        token, now_epoch=now, verification_key=key,
        consume_once=storage.consume,
    )


@pytest.mark.parametrize("account", ACCOUNTS)
def test_exact_ob_producer_token_is_accepted_by_independent_tower_source_only(account):
    storage = SharedAtomicNonceStore()
    token = export(account)
    receipt = verify(token, storage)
    identity = resolve_account_identity(account)
    assert receipt.account_key == account
    assert receipt.account_identity_fingerprint == identity["identity_fingerprint"]
    assert receipt.issued_at_epoch == NOW
    assert receipt.expires_at_epoch == NOW + 60
    assert receipt.signature_verified_with_trusted_injected_key is True
    assert receipt.one_time_nonce_consumed_by_caller_store is True
    assert storage.calls == 1
    result = asdict(receipt)
    assert all(result[key] is False for key in (
        "owner_authentication_verified", "tower_session_verified",
        "tower_permission_verified", "tower_step_up_verified",
        "tower_revocation_verified", "broker_account_verified",
        "real_capital_verified", "manual_live_granted",
        "broker_order_api_authorized", "capital_movement_authorized",
    ))
    for forbidden in ("nonce", "token", "password", "secret", "balance",
                      "broker_account_id", "owner_session_id", "step_up_at_utc"):
        assert forbidden not in result
    assert token not in str(result)
    assert TEST_SOURCE_KEY.decode() not in str(result)


def test_two_actual_ob_tokens_are_unique_and_replay_is_denied_even_between_calls():
    storage = SharedAtomicNonceStore()
    token1 = export()
    token2 = export()
    assert token1 != token2
    assert verify(token1, storage).manual_live_granted is False
    with pytest.raises(NamespaceSourceRefused):
        verify(token1, storage)
    assert verify(token2, storage).manual_live_granted is False
    assert storage.calls == 3


def test_expiry_and_issuer_key_rotation_fail_before_nonce_consumption():
    storage = SharedAtomicNonceStore()
    token = export()
    with pytest.raises(NamespaceSourceRefused):
        verify(token, storage, key=WRONG_KEY)
    assert storage.calls == 0
    with pytest.raises(NamespaceSourceRefused):
        verify(token, storage, now=NOW+60)
    assert storage.calls == 0
    with pytest.raises(NamespaceSourceRefused):
        verify(token, storage, now=NOW-1)
    assert storage.calls == 0
    assert verify(token, storage).one_time_nonce_consumed_by_caller_store


def test_demo_and_unknown_cannot_cross_real_producer_consumer_boundary():
    for account in ("proof_demo", "nonexistent", "trust ", "", None):
        with pytest.raises(OBAccountIdentityExportError):
            export(account)


def test_source_signature_does_not_satisfy_tower_owner_or_manual_live_contract():
    source = source_export_contract()
    receiver = namespace_source_contract()
    assert source["schema_version"] == receiver["source_schema"]
    assert source["issuer"] == ISSUER
    assert source["audience"] == AUDIENCE
    assert source["max_lifetime_seconds"] == receiver["max_ttl_seconds"] == 60
    assert receiver["atomic_durable_nonce_consumption_required"] is True
    assert receiver["default_nonce_store_provided"] is False
    for key in ("source_export_is_tower_owner_authentication",
                "source_export_is_broker_account_authentication",
                "source_export_is_capital_truth",
                "source_export_issues_manual_live_clearance"):
        assert source[key] is False
    for key in ("source_signature_is_owner_authentication",
                "source_signature_is_tower_permission",
                "source_signature_is_real_broker_or_capital_truth",
                "manual_live_grant", "broker_order_api", "capital_movement"):
        assert receiver[key] is False
