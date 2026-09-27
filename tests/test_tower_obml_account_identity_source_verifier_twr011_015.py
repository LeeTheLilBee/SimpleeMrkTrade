"""TWR-OBML011-015: independent actual OB source signature and replay tests."""
from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile

import pytest

from tower import obml_account_identity_source_verifier as receiver

ROOT = Path(__file__).resolve().parents[1]
OB_ROOT = ROOT / "obai-source"
SECRET = "synthetic-ob-tower-identity-secret-0123456789"
NOW = 2_000_000_000


def source_export(account="trust"):
    assert (OB_ROOT / "web" / "ob_tower_account_identity_export.py").is_file()
    script = """
import json,sys
from web.ob_tower_account_identity_export import create_ob_account_identity_export, source_export_contract
from web.ob_account_identity_truth import resolve_account_identity
key = sys.argv[1]
identity = resolve_account_identity(key)
token = create_ob_account_identity_export(key, now_epoch=2000000000, signing_secret=sys.argv[2])
print(json.dumps({"token":token, "account_key":key,
                  "fingerprint":identity["identity_fingerprint"],
                  "contract":source_export_contract()}, sort_keys=True))
"""
    env = os.environ.copy()
    env["PYTHONPATH"] = str(OB_ROOT)
    run = subprocess.run(
        [sys.executable, "-c", script, account, SECRET],
        cwd=OB_ROOT, env=env, text=True, capture_output=True,
        check=True, timeout=15,
    )
    return json.loads(run.stdout)


def encode(payload, secret=SECRET):
    raw = json.dumps(
        payload, sort_keys=True, separators=(",", ":"), allow_nan=False,
    ).encode("utf-8")
    return sign_raw(raw, secret=secret)


def sign_raw(raw, secret=SECRET):
    p64 = base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")
    head = "obai1." + p64
    mac = hmac.new(secret.encode("utf-8"), head.encode("ascii"), hashlib.sha256).digest()
    return head + "." + base64.urlsafe_b64encode(mac).decode("ascii").rstrip("=")


def raw_claims(token):
    p64 = token.split(".")[1]
    return json.loads(base64.urlsafe_b64decode(p64 + "=" * (-len(p64) % 4)))


def verify(payload, token=None, now=NOW, secret=SECRET):
    return receiver.verify_signed_ob_account_source(
        payload["token"] if token is None else token,
        shared_secret=secret,
        expected_account_key=payload["account_key"],
        expected_current_fingerprint=payload["fingerprint"],
        now_epoch=now,
    )


@pytest.mark.parametrize("account", (
    "personal", "trust", "simplee_world_business",
    "simplee_on_the_go_atm", "the_grounds_apartment",
))
def test_actual_independently_pinned_ob_source_matches_tower_verifier(account):
    payload = source_export(account)
    verified = verify(payload)
    assert verified.claims["account_key"] == account
    assert verified.claims["account_identity_fingerprint"] == payload["fingerprint"]
    assert verified.source_namespace_signature_verified is True
    for false_field in (
        "tower_owner_authenticated", "broker_account_authenticated",
        "capital_verified", "manual_live_authorized",
    ):
        assert getattr(verified, false_field) is False
    summary = receiver.describe_verified_source(verified)
    assert summary["source_identity_signature_verified"] is True
    assert summary["tower_obml_permission_issued"] is False
    assert summary["manual_live_authorized"] is False
    assert summary["amounts_exposed"] is False
    assert summary["token_exposed"] is False
    assert payload["contract"]["source_export_is_tower_owner_authentication"] is False
    assert payload["contract"]["source_export_issues_manual_live_clearance"] is False


def test_replay_denied_across_distinct_database_connections():
    payload = source_export()
    verified = verify(payload)
    with tempfile.TemporaryDirectory() as dirname:
        path = Path(dirname) / "synthetic_source_nonce.sqlite3"
        with sqlite3.connect(path) as db:
            assert receiver.consume_signed_ob_account_source(
                db, payload["token"], shared_secret=SECRET,
                expected_account_key=payload["account_key"],
                expected_current_fingerprint=payload["fingerprint"],
                now_epoch=NOW,
            ) is True
        with sqlite3.connect(path) as db:
            assert receiver.consume_signed_ob_account_source(
                db, payload["token"], shared_secret=SECRET,
                expected_account_key=payload["account_key"],
                expected_current_fingerprint=payload["fingerprint"],
                now_epoch=NOW,
            ) is False
            assert db.execute(
                "SELECT COUNT(*) FROM tower_obml_account_source_nonce"
            ).fetchone()[0] == 1


def test_replay_ledger_never_commits_unrelated_caller_transaction():
    payload = source_export()
    verified = verify(payload)
    with sqlite3.connect(":memory:") as db:
        db.execute("CREATE TABLE unrelated (x INTEGER)")
        db.execute("INSERT INTO unrelated VALUES (1)")
        with pytest.raises(receiver.OBAccountSourceVerificationError,
                           match="FRESH_SOURCE_LEDGER_REQUIRED"):
            receiver.consume_signed_ob_account_source(
                db, payload["token"], shared_secret=SECRET,
                expected_account_key=payload["account_key"],
                expected_current_fingerprint=payload["fingerprint"],
                now_epoch=NOW,
            )
        assert db.in_transaction
        db.rollback()
        assert db.execute("SELECT COUNT(*) FROM unrelated").fetchone()[0] == 0


def test_expired_source_reverified_before_nonce_insert():
    payload = source_export()
    with sqlite3.connect(":memory:") as db:
        with pytest.raises(receiver.OBAccountSourceVerificationError,
                           match="ACCOUNT_EXPORT_EXPIRED_OR_INVALID"):
            receiver.consume_signed_ob_account_source(
                db, payload["token"], shared_secret=SECRET,
                expected_account_key=payload["account_key"],
                expected_current_fingerprint=payload["fingerprint"],
                now_epoch=NOW + 61,
            )
        assert db.execute(
            "SELECT COUNT(*) FROM sqlite_master "
            "WHERE type='table' AND name='tower_obml_account_source_nonce'"
        ).fetchone()[0] == 0

def test_current_expected_fingerprint_and_exact_account_are_required():
    payload = source_export()
    with pytest.raises(receiver.OBAccountSourceVerificationError,
                       match="CURRENT_SOURCE_MISMATCH"):
        receiver.verify_signed_ob_account_source(
            payload["token"], shared_secret=SECRET,
            expected_account_key="personal",
            expected_current_fingerprint=payload["fingerprint"], now_epoch=NOW,
        )
    with pytest.raises(receiver.OBAccountSourceVerificationError,
                       match="CURRENT_SOURCE_MISMATCH"):
        receiver.verify_signed_ob_account_source(
            payload["token"], shared_secret=SECRET,
            expected_account_key=payload["account_key"],
            expected_current_fingerprint="0" * 64, now_epoch=NOW,
        )


@pytest.mark.parametrize("change", [
    {"issuer": "tower"}, {"audience": "buybox-owner"},
    {"account_key": "proof_demo"}, {"account_class": "SIMULATED_PROOF_DEMO"},
    {"real_capital_verified": True}, {"manual_live_granted": True},
    {"owner_authentication_asserted": True}, {"broker_account_verified": True},
    {"expires_at_epoch": NOW + 61}, {"issued_at_epoch": True},
    {"namespace_authority": "FAKE_NAMESPACE"},
    {"additional_balance": "100000"},
])
def test_even_synthetic_resigned_wrong_scope_or_capability_is_rejected(change):
    payload = source_export()
    claims = raw_claims(payload["token"])
    claims.update(change)
    with pytest.raises(receiver.OBAccountSourceVerificationError):
        verify(payload, token=encode(claims))


def test_wrong_key_tampering_missing_secret_and_expiration_fail():
    payload = source_export()
    wrong = "wrong-test-only-secret-0123456789-abcdef"
    with pytest.raises(receiver.OBAccountSourceVerificationError):
        verify(payload, secret=wrong)
    with pytest.raises(receiver.OBAccountSourceVerificationError):
        verify(payload, token=payload["token"][:-1] + "X")
    with pytest.raises(receiver.OBAccountSourceVerificationError):
        verify(payload, secret="short")
    with pytest.raises(receiver.OBAccountSourceVerificationError):
        verify(payload, now=NOW + 60)
    with pytest.raises(receiver.OBAccountSourceVerificationError):
        verify(payload, now=True)


def test_duplicate_json_field_and_oversized_token_denied():
    payload = source_export()
    claims = raw_claims(payload["token"])
    text = json.dumps(claims, sort_keys=True, separators=(",", ":"))
    duplicate = text.replace(
        '"issuer":"observatory-account-identity"',
        '"issuer":"observatory-account-identity","issuer":"observatory-account-identity"',
    )
    assert duplicate != text
    with pytest.raises(receiver.OBAccountSourceVerificationError):
        verify(payload, token=sign_raw(duplicate.encode("utf-8")))
    with pytest.raises(receiver.OBAccountSourceVerificationError):
        verify(payload, token="x" * 4097)


def test_caller_constructed_verified_wrapper_is_not_accepted_by_public_replay_entrypoint():
    payload = source_export()
    forged = receiver.VerifiedOBAccountSource(claims={"nonce": "a" * 32})
    with sqlite3.connect(":memory:") as db:
        with pytest.raises(receiver.OBAccountSourceVerificationError):
            receiver.consume_signed_ob_account_source(
                db, forged, shared_secret=SECRET,
                expected_account_key=payload["account_key"],
                expected_current_fingerprint=payload["fingerprint"],
                now_epoch=NOW,
            )
        assert db.execute(
            "SELECT COUNT(*) FROM sqlite_master "
            "WHERE type='table' AND name='tower_obml_account_source_nonce'"
        ).fetchone()[0] == 0


def test_verified_claims_immutable_and_no_public_grant_or_endpoint():
    payload = source_export()
    verified = verify(payload)
    with pytest.raises(TypeError):
        verified.claims["manual_live_granted"] = True
    source = Path(receiver.__file__).read_text(encoding="utf-8")
    for forbidden in (
        "@app.route(", "requests.post(", "from web.ob_account_identity_truth",
        "broker.place_order", "manual_live_enable(",
    ):
        assert forbidden not in source
    for key in ("balance", "broker_token", "owner_password"):
        assert key not in receiver.describe_verified_source(verified)
