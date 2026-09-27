"""OBML011-015: exact source-derived, amount-free OB identity export tests."""
import base64
import hashlib
import hmac
import json
from pathlib import Path

import pytest

from web.ob_account_identity_truth import resolve_account_identity
from web.ob_tower_account_identity_export import (
    AUDIENCE, EXPORT_SCHEMA, ISSUER, MAX_LIFETIME_SECONDS, PREFIX,
    OBAccountIdentityExportError, create_ob_account_identity_export,
    source_export_contract,
)

SECRET = "synthetic-test-obai-secret-0123456789-abcdef"
NOW = 2_000_000_000
MISSION = (
    "personal", "trust", "simplee_world_business",
    "simplee_on_the_go_atm", "the_grounds_apartment",
)


def unpack(token, key=SECRET):
    prefix, p64, s64 = token.split(".")
    assert prefix == PREFIX
    signing_input = (prefix + "." + p64).encode("ascii")
    expected = hmac.new(key.encode("utf-8"), signing_input, hashlib.sha256).digest()
    actual = base64.urlsafe_b64decode(s64 + "=" * (-len(s64) % 4))
    assert hmac.compare_digest(actual, expected)
    return json.loads(base64.urlsafe_b64decode(p64 + "=" * (-len(p64) % 4)))


@pytest.mark.parametrize("key", MISSION)
def test_real_account_namespace_is_signed_without_owner_or_capital_claim(key):
    identity = resolve_account_identity(key)
    token = create_ob_account_identity_export(
        key, now_epoch=NOW, signing_secret=SECRET
    )
    claims = unpack(token)
    assert claims["schema_version"] == EXPORT_SCHEMA
    assert claims["issuer"] == ISSUER
    assert claims["audience"] == AUDIENCE
    assert claims["account_key"] == key
    assert claims["account_identity_fingerprint"] == identity["identity_fingerprint"]
    assert claims["source_schema_version"] == identity["schema_version"]
    assert claims["namespace_authority"] == identity["namespace_authority"]
    assert claims["account_class"] == "MISSION_ACCOUNT"
    assert claims["capital_truth_class"] == "UNKNOWN_UNTIL_CAPITAL_AUTHORITY"
    assert claims["issued_at_epoch"] == NOW
    assert claims["expires_at_epoch"] == NOW + MAX_LIFETIME_SECONDS
    assert len(claims["nonce"]) == 32
    assert all(claims[name] is False for name in (
        "owner_authentication_asserted", "broker_account_verified",
        "real_capital_verified", "manual_live_granted",
    ))
    assert all(name not in claims for name in (
        "balance", "available_capital", "broker_token", "session_secret",
        "owner_password", "tower_session_id", "options_permission",
    ))


def test_nonce_is_random_per_source_export_not_recycled():
    first = unpack(create_ob_account_identity_export(
        "trust", now_epoch=NOW, signing_secret=SECRET
    ))
    second = unpack(create_ob_account_identity_export(
        "trust", now_epoch=NOW, signing_secret=SECRET
    ))
    assert first["nonce"] != second["nonce"]
    assert first["account_identity_fingerprint"] == second["account_identity_fingerprint"]


@pytest.mark.parametrize("key", (
    "proof_demo", "UNKNOWN", "", "trust ", " trust", None, True,
))
def test_unknown_simulated_or_nonexact_mission_account_never_exported(key):
    with pytest.raises(OBAccountIdentityExportError):
        create_ob_account_identity_export(
            key, now_epoch=NOW, signing_secret=SECRET
        )


@pytest.mark.parametrize("value", (None, "", "short", b"short"))
def test_missing_weak_secret_fails_closed(value):
    with pytest.raises(OBAccountIdentityExportError):
        create_ob_account_identity_export(
            "trust", now_epoch=NOW, signing_secret=value
        )


@pytest.mark.parametrize("when", (0, -1, True, 1.5, "2000000000"))
def test_invalid_export_time_fails_closed(when):
    with pytest.raises(OBAccountIdentityExportError):
        create_ob_account_identity_export(
            "trust", now_epoch=when, signing_secret=SECRET
        )


def test_wrong_key_cannot_validate_and_token_never_contains_key():
    token = create_ob_account_identity_export(
        "personal", now_epoch=NOW, signing_secret=SECRET
    )
    with pytest.raises(AssertionError):
        unpack(token, key="synthetic-other-secret-01234567890")
    assert SECRET not in token
    assert "synthetic-test" not in token


def test_contract_explicitly_separates_namespace_from_owner_and_broker():
    report = source_export_contract()
    assert report["max_lifetime_seconds"] == 60
    assert report["proof_demo_eligible_for_obml"] is False
    for field in (
        "source_export_is_tower_owner_authentication",
        "source_export_is_broker_account_authentication",
        "source_export_is_capital_truth",
        "source_export_issues_manual_live_clearance",
        "signed_token_contains_balances",
        "public_endpoint_registered",
    ):
        assert report[field] is False
    import web.ob_tower_account_identity_export as module
    source = Path(module.__file__).read_text(encoding="utf-8")
    assert "@app.route(" not in source
    assert "requests.post(" not in source
    assert "TOWER_SESSION_SECRET" not in source
    assert "BROKER_API_KEY" not in source
