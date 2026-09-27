"""SC003 synthetic S3-compatible and provider-governance contract tests.

No network provider, credentials, real object storage or production certificate.
"""
import hashlib
import os

import pytest

from simplee_cloud.contracts import CloudError, IntegrityError
from simplee_cloud.s3_backend import S3CompatibleCiphertextBackend
from simplee_cloud.provider_review import (
    ProviderCandidate, required_provider_checks, review_candidate,
)

SCOPE = "a" * 64
REF = "objects/" + "c" * 48
BACKUP_REF = "backups/" + "e" * 48


class SyntheticStream:
    def __init__(self, body):
        self.body = body
        self.closed = False

    def read(self, count):
        return self.body[:count]

    def close(self):
        self.closed = True


class FakeS3:
    def __init__(self):
        self.rows = {}
        self.put_calls = 0
        self.put_args = None
        self.read_stream = None
        self.force_response = None
        self.reject_condition = False
        self.override_get = None

    def put_object(self, **kwargs):
        self.put_calls += 1
        self.put_args = kwargs
        if self.reject_condition:
            raise TypeError("IfNoneMatch not supported by this provider")
        if kwargs.get("IfNoneMatch") != "*":
            raise AssertionError("conditional PUT required")
        key = kwargs["Key"]
        if key in self.rows:
            raise RuntimeError("412 Precondition Failed")
        self.rows[key] = {
            "body": kwargs["Body"], "metadata": dict(kwargs["Metadata"]),
        }
        return (
            self.force_response if self.force_response is not None
            else {"ResponseMetadata": {"HTTPStatusCode": 200}}
        )

    def get_object(self, **kwargs):
        row = self.rows[kwargs["Key"]]
        stream = SyntheticStream(row["body"])
        self.read_stream = stream
        return self.override_get if self.override_get is not None else {
            "Body": stream, "ContentLength": len(row["body"]),
            "Metadata": dict(row["metadata"]), "ETag": '"not-a-trusted-digest"',
        }


def backend(client=None, purpose="primary", prefix="simplee/v1", bucket="private-test-store"):
    client = FakeS3() if client is None else client
    return S3CompatibleCiphertextBackend(
        client=client, bucket=bucket, prefix=prefix, purpose=purpose,
        mode="source_test",
    )


def test_private_conditional_write_and_bounded_integrity_read():
    fake = FakeS3()
    store = backend(fake)
    ciphertext = b"VLT1" + os.urandom(80)
    store.put_if_absent(SCOPE, REF, ciphertext)
    args = fake.put_args
    assert args["IfNoneMatch"] == "*"
    assert args["ContentType"] == "application/octet-stream"
    assert args["ServerSideEncryption"] == "AES256"
    assert args["Metadata"]["ciphertext-sha256"] == hashlib.sha256(ciphertext).hexdigest()
    assert args["Key"] == "simplee/v1/" + SCOPE + "/" + REF
    assert "ACL" not in args and "public" not in str(args)
    assert store.get(SCOPE, REF) == ciphertext
    assert fake.read_stream.closed is True
    assert not any(hasattr(store, method) for method in (
        "delete", "list", "presign", "get_public_url", "grant_access",
    ))
    with pytest.raises(RuntimeError, match="412"):
        store.put_if_absent(SCOPE, REF, ciphertext)
    assert fake.put_calls == 2
    assert len(fake.rows) == 1


def test_unsupported_condition_never_falls_back_to_unconditional_write():
    fake = FakeS3()
    fake.reject_condition = True
    store = backend(fake)
    with pytest.raises(TypeError, match="not supported"):
        store.put_if_absent(SCOPE, REF, b"VLT1" + os.urandom(48))
    assert fake.put_calls == 1
    assert not fake.rows


def test_missing_ack_is_uncertain_not_success():
    fake = FakeS3()
    fake.force_response = {}
    store = backend(fake)
    with pytest.raises(CloudError, match="acknowledgement"):
        store.put_if_absent(SCOPE, REF, b"VLT1" + os.urandom(48))
    assert len(fake.rows) == 1  # write may actually have succeeded


def test_rejects_plaintext_bad_keys_bad_config_and_default_disabled():
    fake = FakeS3()
    with pytest.raises(CloudError):
        S3CompatibleCiphertextBackend(
            client=fake, bucket="private-test-store", prefix="simplee/v1",
            purpose="primary",
        )
    with pytest.raises(CloudError):
        backend(fake, prefix="../secret")
    with pytest.raises(CloudError):
        backend(fake, bucket="a..b")
    with pytest.raises(CloudError):
        backend(fake, purpose="unknown")
    with pytest.raises(CloudError):
        backend(fake).put_if_absent(SCOPE, REF, b"PDF private body")
    with pytest.raises(CloudError):
        backend(fake).put_if_absent(SCOPE, "../escape", b"VLT1" + os.urandom(48))
    with pytest.raises(CloudError):
        backend(fake).get("trust", REF)
    with pytest.raises(CloudError):
        backend(fake).get(SCOPE, BACKUP_REF)
    assert fake.put_calls == 0


def test_backup_role_is_isolated_with_distinct_envelope_type():
    fake = FakeS3()
    store = backend(fake, purpose="backup", prefix="simplee-backup/v1")
    protected = b"SCB1" + os.urandom(64)
    store.put_if_absent(SCOPE, BACKUP_REF, protected)
    assert store.get(SCOPE, BACKUP_REF) == protected
    assert fake.put_args["Metadata"]["envelope-version"] == "backup-v1"
    with pytest.raises(CloudError):
        store.put_if_absent(SCOPE, REF, b"VLT1" + os.urandom(64))
    with pytest.raises(CloudError):
        backend(FakeS3()).put_if_absent(SCOPE, REF, protected)


@pytest.mark.parametrize("fault", [
    "wrong_digest", "missing_metadata", "wrong_envelope", "short_stream",
    "invalid_size", "oversize_declared", "missing_stream", "not_bytes",
])
def test_corrupt_provider_response_fails_closed(fault):
    fake = FakeS3()
    store = backend(fake)
    data = b"VLT1" + os.urandom(48)
    store.put_if_absent(SCOPE, REF, data)
    saved = next(iter(fake.rows.values()))
    if fault == "wrong_digest":
        saved["metadata"]["ciphertext-sha256"] = "0" * 64
    elif fault == "missing_metadata":
        saved["metadata"].pop("ciphertext-sha256")
    elif fault == "wrong_envelope":
        saved["metadata"]["envelope-version"] = "incorrect"
    elif fault == "short_stream":
        fake.override_get = {
            "Body": SyntheticStream(data[:-1]), "ContentLength": len(data),
            "Metadata": saved["metadata"],
        }
    elif fault == "invalid_size":
        fake.override_get = {
            "Body": SyntheticStream(data), "ContentLength": True,
            "Metadata": saved["metadata"],
        }
    elif fault == "oversize_declared":
        fake.override_get = {
            "Body": SyntheticStream(data), "ContentLength": 30 * 1024 * 1024,
            "Metadata": saved["metadata"],
        }
    elif fault == "missing_stream":
        fake.override_get = {
            "Body": object(), "ContentLength": len(data),
            "Metadata": saved["metadata"],
        }
    elif fault == "not_bytes":
        fake.override_get = {
            "Body": SyntheticStream("VLT1text"), "ContentLength": len(data),
            "Metadata": saved["metadata"],
        }
    with pytest.raises(IntegrityError):
        store.get(SCOPE, REF)


def test_provider_review_never_self_approves_even_with_all_claims():
    candidate = ProviderCandidate(
        provider_label="unselected-candidate",
        software_operator="candidate-operator",
        physical_server_owner="declared-hardware-operator",
        storage_jurisdiction="declared-jurisdiction",
        external_dependencies=("undetermined-network-operator",),
    )
    checks = required_provider_checks()
    assert "atomic_conditional_put_verified" in checks
    assert "data_location_and_physical_server_owner" in checks
    empty = review_candidate(candidate, {})
    assert empty.status == "NO_GO"
    assert empty.storage_runtime_authorized is False
    assert set(empty.missing) == set(checks)
    populated = review_candidate(
        candidate, {check: "review/placeholder-" + str(i) for i, check in enumerate(checks)},
    )
    assert populated.documentation_complete_for_review is True
    assert populated.status == "NO_GO"
    assert populated.owner_approved is False
    assert populated.provider_independently_verified is False
    with pytest.raises(CloudError):
        review_candidate(candidate, {"unsafe-claim": "any"})
    with pytest.raises(CloudError):
        review_candidate(candidate, {"atomic_conditional_put_verified": "\nsecret"})
