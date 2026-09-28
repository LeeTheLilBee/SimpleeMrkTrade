"""SC017: legacy/source Tower and Vault shapes must NEVER authorize Cloud.

These tests consume actual merged repository modules that pre-date the signed
private-service corridor. They exist to prevent an integration shortcut where a
queued handoff record, hosted owner identity projection, or verified_by_tower
boolean gets treated as cryptographic Cloud authority.
"""
import pytest

from simplee_cloud.contracts import AccessDenied
from simplee_cloud.tests.test_sc004b_bound_port import Harness, PEER
from tower.archive_vault_handoff import build_archive_vault_handoff_record
from tower.identity_authority import hosted_owner_identity_authority
from vault.real_operations_encrypted_storage import TowerStorageDecision


class MustNeverTouchProvider:
    def __init__(self):
        self.get_calls = 0
        self.put_calls = 0

    def put_if_absent(self, namespace, ref, body):
        self.put_calls += 1
        raise AssertionError("legacy authority shape must not reach provider PUT")

    def get(self, namespace, ref):
        self.get_calls += 1
        raise AssertionError("legacy authority shape must not reach provider GET")


def prepared(tmp_path):
    h = Harness(tmp_path)
    h.port.write(
        grant=h.grant("write-1", "WRITE_CIPHERTEXT"),
        authenticated_transport_peer=PEER,
        request_id="write-1", envelope=h.data,
    )
    signed = h.grant("read-legacy", "READ_CIPHERTEXT")
    expected = h.canonical[("read-legacy", "READ_CIPHERTEXT")]
    provider = MustNeverTouchProvider()
    h.source._backend = provider
    return h, expected, signed, provider


def legacy_handoff():
    return build_archive_vault_handoff_record(
        source_type="synthetic_security_event",
        source_id="event-1",
        title="Synthetic handoff",
        summary="Source-only queue item",
        related_object={"object_id": "example"},
        source_payload={"token": "must-never-survive"},
    )


def tower_storage_decision():
    return TowerStorageDecision(
        request_id="read-legacy",
        principal_ref="owner-source-shape",
        entity_id="trust",
        purpose="archive",
        operation="READ_CIPHERTEXT",
        evidence_id="evidence-source",
        document_version_id="version-source",
        verified_by_tower=True,
        approval_receipt_ref="approval-source",
        malware_scan_receipt_ref="scan-source",
    )


def test_actual_tower_archive_handoff_record_explicitly_stays_unready():
    record = legacy_handoff()
    assert record["status"] == "queued"
    assert record["destination"] == "Archive Vault"
    assert record["evidence_bundle_stub"]["ready_for_archive_vault"] is False
    assert "token" not in record["source_payload"]
    assert record["source_payload"]["__redacted_sensitive_field_count__"] == 1


@pytest.mark.parametrize("legacy", [
    lambda: legacy_handoff(),
    lambda: tower_storage_decision(),
    lambda: {"verified_by_tower": True, "operation": "READ_CIPHERTEXT"},
])
def test_legacy_authority_objects_never_substitute_for_signed_cloud_grant(tmp_path, legacy):
    h, expected, signed, provider = prepared(tmp_path)
    with pytest.raises(AccessDenied, match="trusted grant and scope required"):
        h.port.read_encrypted(
            grant=legacy(),
            authenticated_transport_peer=PEER,
            request_id="read-legacy",
        )
    assert provider.get_calls == 0
    assert provider.put_calls == 0
    assert h.nonces.count() == 1


def test_flipping_archival_stub_ready_flag_still_cannot_authorize_cloud(tmp_path):
    h, expected, signed, provider = prepared(tmp_path)
    forged = legacy_handoff()
    forged["evidence_bundle_stub"]["ready_for_archive_vault"] = True
    forged["ok"] = True
    forged["status"] = "ready"
    with pytest.raises(AccessDenied):
        h.port.read_encrypted(
            grant=forged,
            authenticated_transport_peer=PEER,
            request_id="read-legacy",
        )
    assert provider.get_calls == 0


def test_verified_by_tower_boolean_validates_only_its_own_old_typed_shape():
    decision = tower_storage_decision()
    decision.validate(operation="READ_CIPHERTEXT")
    assert decision.verified_by_tower is True


def test_actual_tower_owner_identity_projection_is_not_cloud_service_identity(
    tmp_path, monkeypatch,
):
    monkeypatch.setenv("TOWER_OWNER_USERNAME", "source-owner")
    monkeypatch.setenv("TOWER_OWNER_PASSWORD_HASH", "source-hash-present")
    monkeypatch.setenv("TOWER_LOCAL_WALKTHROUGH_MODE", "false")
    projection = hosted_owner_identity_authority()
    assert isinstance(projection, dict)
    assert projection.get("plaintext_password_exposed") is False
    assert projection.get("session_secret_exposed") is False

    h, expected, signed, provider = prepared(tmp_path)
    with pytest.raises(AccessDenied):
        h.port.read_encrypted(
            grant=projection,
            authenticated_transport_peer=PEER,
            request_id="read-legacy",
        )
    assert provider.get_calls == 0


def test_only_source_signed_grant_shape_gets_past_authority_type_gate(tmp_path):
    h, expected, signed, provider = prepared(tmp_path)
    h.source._backend = h.primary
    result = h.port.read_encrypted(
        grant=signed,
        authenticated_transport_peer=PEER,
        request_id="read-legacy",
    )
    assert result == h.data
    assert h.port.health()["real_tower_issuer_connected"] is False
    assert h.port.health()["independent_peer_transport_certified"] is False
    assert h.port.health()["production_authorized"] is False
