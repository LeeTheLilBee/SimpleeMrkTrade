"""Synthetic SC004 Ed25519 grant/peer/revocation/replay adversarial tests.

All signing keys are generated in-memory by the test runner. None are from
Tower; no real transport or production identity connection is implied.
"""
import json
import os
from dataclasses import replace

import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from simplee_cloud.contracts import AccessDenied, CloudError
from simplee_cloud.tower_grants import (
    SQLiteNonceReplayStore, SignedTowerGrant, SourceOnlyTowerGrantVerifier,
    TrustedVaultScope,
)

NOW = 2_000_000_000
PEER = object()
REF = "objects/" + "a" * 48
BACKUP_REF = "backups/" + "b" * 48
DIGEST = "c" * 64


def key_pair():
    private = Ed25519PrivateKey.generate()
    public = private.public_key().public_bytes(
        encoding=serialization.Encoding.Raw, format=serialization.PublicFormat.Raw,
    )
    return private, public


def claims(**changes):
    data = {
        "schema": "simplee.cloud.tower-grant.v1", "iss": "tower",
        "aud": "simplee_sovereign_cloud", "service": "archive_vault",
        "request_id": "request-1", "entity_id": "trust",
        "decision_ref": "tower-decision-1", "purpose": "archival",
        "operation": "WRITE_CIPHERTEXT", "classification": "owner_private",
        "approval_ref": "approval-1", "step_up_ref": "stepup-1",
        "object_ref": REF, "ciphertext_sha256": DIGEST,
        "nonce": os.urandom(16).hex(), "iat": NOW - 5, "exp": NOW + 30,
    }
    data.update(changes)
    return data


def expected(c):
    return TrustedVaultScope(
        request_id=c["request_id"], entity_id=c["entity_id"],
        purpose=c["purpose"], operation=c["operation"],
        classification=c["classification"], object_ref=c["object_ref"],
        ciphertext_sha256=c["ciphertext_sha256"],
    )


def sign(c, private, *, key_id="synthetic-key-1", raw=None):
    payload = raw if raw is not None else json.dumps(
        c, sort_keys=True, separators=(",", ":"), ensure_ascii=True,
    ).encode()
    return SignedTowerGrant(key_id, payload, private.sign(payload))


def setup(tmp_path, *, peer=None, active=None, clock=None):
    private, public = key_pair()
    replay = SQLiteNonceReplayStore(
        tmp_path / "nonce-store" / "consumed.sqlite", mode="source_test",
    )
    verifier = SourceOnlyTowerGrantVerifier(
        tower_public_keys={"synthetic-key-1": public},
        peer_is_authenticated_vault=peer or (lambda value: value is PEER),
        tower_policy_is_current=active or (lambda policy: policy["decision_ref"] == "tower-decision-1" and policy["approval_ref"] == "approval-1" and policy["step_up_ref"] == "stepup-1"),
        replay_store=replay, now_epoch_seconds=clock or (lambda: NOW),
        mode="source_test",
    )
    return private, replay, verifier


def check(verifier, grant, c, peer=PEER, scope=None):
    return verifier.verify_and_consume(
        grant=grant, authenticated_transport_peer=peer,
        expected=scope or expected(c),
    )


def test_valid_scope_bound_grant_consumed_exactly_once(tmp_path):
    private, replay, verifier = setup(tmp_path)
    c = claims()
    grant = sign(c, private)
    result = check(verifier, grant, c)
    assert result.context.caller_service == "archive_vault"
    assert result.context.tower_decision_ref == "tower-decision-1"
    assert result.object_ref == REF and result.ciphertext_sha256 == DIGEST
    assert result.classification == "owner_private"
    assert replay.count() == 1
    with pytest.raises(AccessDenied, match="consumed"):
        check(verifier, grant, c)
    assert replay.count() == 1


@pytest.mark.parametrize("bad", [
    {"iss": "buybox"}, {"aud": "the_clouds"}, {"service": "teller"},
    {"operation": "DELETE_OBJECT"}, {"entity_id": ""}, {"approval_ref": ""},
    {"step_up_ref": ""}, {"nonce": "not-a-valid-nonce"},
    {"ciphertext_sha256": "bad"}, {"object_ref": "objects/../secret"},
    {"iat": NOW + 10}, {"exp": NOW}, {"exp": NOW + 500},
    {"iat": True},
])
def test_signed_malformed_or_wrong_grants_denied(tmp_path, bad):
    private, replay, verifier = setup(tmp_path)
    original = claims()
    bad_claim = dict(original, **bad)
    with pytest.raises(AccessDenied):
        check(verifier, sign(bad_claim, private), original)
    assert replay.count() == 0


def test_vault_scope_mismatch_detected_before_nonce_consume(tmp_path):
    private, replay, verifier = setup(tmp_path)
    c = claims()
    for diff in (
        {"entity_id": "other"}, {"object_ref": "objects/" + "d" * 48},
        {"classification": "public"}, {"ciphertext_sha256": "f" * 64},
        {"purpose": "another_purpose"}, {"request_id": "request-2"},
    ):
        with pytest.raises(AccessDenied, match="trusted Vault"):
            check(verifier, sign(c, private),
                  c, scope=replace(expected(c), **diff))
    assert replay.count() == 0


def test_auth_peer_revocation_and_unavailable_authority_denied(tmp_path):
    private, replay, verifier = setup(tmp_path)
    c = claims()
    grant = sign(c, private)
    with pytest.raises(AccessDenied, match="unauthenticated"):
        check(verifier, grant, c, peer=object())
    assert replay.count() == 0
    revoked_private, _, revoked_verifier = setup(
        tmp_path / "revoked", active=lambda ref: False,
    )
    with pytest.raises(AccessDenied):
        check(revoked_verifier, sign(c, revoked_private), c)
    unavailable_private, _, unavailable = setup(
        tmp_path / "offline", active=lambda ref: (_ for _ in ()).throw(OSError("offline")),
    )
    with pytest.raises(AccessDenied, match="unavailable"):
        check(unavailable, sign(c, unavailable_private), c)


def test_signed_but_stale_approval_or_stepup_is_rechecked(tmp_path):
    private, replay, verifier = setup(tmp_path)
    canonical = claims()
    for altered in (
        claims(approval_ref="approval-revoked"),
        claims(step_up_ref="stepup-expired"),
    ):
        with pytest.raises(AccessDenied, match="revoked"):
            check(verifier, sign(altered, private), canonical)
    assert replay.count() == 0


def test_signature_tamper_unknown_key_and_duplicate_field_denied(tmp_path):
    private, replay, verifier = setup(tmp_path)
    c = claims()
    grant = sign(c, private)
    forged = replace(grant, payload=grant.payload[:-1] + b" ")
    with pytest.raises(AccessDenied, match="signature"):
        check(verifier, forged, c)
    with pytest.raises(AccessDenied):
        check(verifier, replace(grant, key_id="unknown"), c)
    # Even if a test private key signs duplicated JSON, canonical parsing
    # rejects the ambiguity before any capability can be consumed.
    duplicate = grant.payload.decode().replace(
        '"aud":"simplee_sovereign_cloud",',
        '"aud":"simplee_sovereign_cloud","aud":"simplee_sovereign_cloud",',
    ).encode()
    with pytest.raises(AccessDenied):
        check(verifier, sign(c, private, raw=duplicate), c)
    assert replay.count() == 0


def test_backup_specific_scope_and_distinct_nonce(tmp_path):
    private, replay, verifier = setup(tmp_path)
    c = claims(operation="VERIFY_BACKUP", object_ref=BACKUP_REF)
    result = check(verifier, sign(c, private), c)
    assert result.object_ref == BACKUP_REF
    wrong_ref = claims(operation="VERIFY_BACKUP", object_ref=REF)
    with pytest.raises(AccessDenied):
        check(verifier, sign(wrong_ref, private), wrong_ref)
    assert replay.count() == 1


def test_replay_persists_across_store_reopening(tmp_path):
    private, replay, verifier = setup(tmp_path)
    c = claims()
    grant = sign(c, private)
    check(verifier, grant, c)
    persisted = SQLiteNonceReplayStore(
        tmp_path / "nonce-store" / "consumed.sqlite", mode="source_test",
    )
    _, public = key_pair()
    # Use same public key from the original test private key, not this new one.
    public = private.public_key().public_bytes(
        encoding=serialization.Encoding.Raw, format=serialization.PublicFormat.Raw,
    )
    reopened = SourceOnlyTowerGrantVerifier(
        tower_public_keys={"synthetic-key-1": public},
        peer_is_authenticated_vault=lambda value: value is PEER,
        tower_policy_is_current=lambda policy: True,
        replay_store=persisted, now_epoch_seconds=lambda: NOW,
        mode="source_test",
    )
    with pytest.raises(AccessDenied, match="consumed"):
        check(reopened, grant, c)


def test_no_source_fixture_can_enable_production(tmp_path):
    private, replay, verifier = setup(tmp_path)
    _, public = key_pair()
    with pytest.raises(CloudError):
        SQLiteNonceReplayStore(tmp_path / "other.sqlite")
    with pytest.raises(CloudError):
        SourceOnlyTowerGrantVerifier(
            tower_public_keys={"synthetic-key-1": public},
            peer_is_authenticated_vault=lambda p: True,
            tower_policy_is_current=lambda policy: True,
            replay_store=replay, now_epoch_seconds=lambda: NOW,
        )
    assert replay.count() == 0
