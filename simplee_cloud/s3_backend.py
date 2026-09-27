"""SC003: injectable S3-compatible ciphertext backend; SOURCE TEST ONLY.

No provider, credentials, URL, bucket, billing, IAM, DNS or physical server is
selected or provisioned here. This adapter cannot certify bucket versioning,
object lock, IAM, public access blocking, logging or independent backups.
Its caller must use the SC002 durable intent/reconciliation service and must
independently authorize every operation. Never retry 409/412 automatically.
"""
from __future__ import annotations

import hashlib
import hmac
import re
from typing import Any

from .contracts import (
    CloudError, IntegrityError, MAX_ENVELOPE_BYTES, valid_backup_ref, valid_object_ref,
)

_BUCKET = re.compile(r"[a-z0-9][a-z0-9.-]{1,61}[a-z0-9]\Z")
_PREFIX_PART = re.compile(r"[a-z0-9][a-z0-9-]{0,31}\Z")
_NAMESPACE = re.compile(r"[0-9a-f]{64}\Z")


class S3CompatibleCiphertextBackend:
    """Implement the Cloud backend port using an explicitly injected fake client.

    A future runtime/security review must introduce a separately approved
    production construction path; no live client/configuration is provided here.
    """
    def __init__(
        self, *, client: Any, bucket: str, prefix: str,
        purpose: str, mode: str = "disabled",
    ):
        if mode != "source_test":
            raise CloudError("managed provider access is disabled")
        if client is None or not callable(getattr(client, "put_object", None)) or not callable(
            getattr(client, "get_object", None)
        ):
            raise CloudError("explicit compatible client required")
        if not isinstance(bucket, str) or not _BUCKET.fullmatch(bucket) or (
            ".." in bucket or ".-" in bucket or "-." in bucket
        ):
            raise CloudError("explicit valid private bucket label required")
        if not isinstance(prefix, str) or not 1 <= len(prefix) <= 64 or not all(
            _PREFIX_PART.fullmatch(part) for part in prefix.split("/")
        ):
            raise CloudError("explicit stable opaque root prefix required")
        if purpose not in ("primary", "backup"):
            raise CloudError("explicit primary or backup isolation required")
        self._client = client
        self._bucket = bucket
        self._prefix = prefix
        self._purpose = purpose
        self.mode = mode

    def _key(self, namespace: str, object_ref: str) -> str:
        if not isinstance(namespace, str) or not _NAMESPACE.fullmatch(namespace):
            raise CloudError("invalid opaque tenant namespace")
        valid = valid_object_ref(object_ref) if self._purpose == "primary" else valid_backup_ref(object_ref)
        if not valid:
            raise CloudError("invalid object reference for provider role")
        return f"{self._prefix}/{namespace}/{object_ref}"

    def _limit(self) -> int:
        return MAX_ENVELOPE_BYTES if self._purpose == "primary" else MAX_ENVELOPE_BYTES + 64

    def _magic(self) -> bytes:
        return b"VLT1" if self._purpose == "primary" else b"SCB1"

    def _envelope_version(self) -> str:
        return "v1" if self._purpose == "primary" else "backup-v1"

    def put_if_absent(self, namespace: str, object_ref: str, body: bytes) -> None:
        key = self._key(namespace, object_ref)
        if not isinstance(body, bytes) or not body.startswith(self._magic()) or not (
            33 <= len(body) <= self._limit()
        ):
            raise CloudError("only bounded encrypted ciphertext may be written")
        digest = hashlib.sha256(body).hexdigest()
        # The provider MUST implement atomic conditional PUT exactly.
        # No read-then-write, unconditional fallback, ACL, URL, listing or
        # automatic retry after ambiguous/conditional failure is permitted.
        response = self._client.put_object(
            Bucket=self._bucket, Key=key, Body=body,
            IfNoneMatch="*", ContentType="application/octet-stream",
            Metadata={
                "ciphertext-sha256": digest,
                "envelope-version": self._envelope_version(),
            },
            ServerSideEncryption="AES256",
        )
        # Failure after a provider accepted the PUT is uncertain; journal
        # reservation must persist and explicit physical reconciliation follows.
        if not isinstance(response, dict) or (
            not isinstance(response.get("ResponseMetadata"), dict)
        ) or response["ResponseMetadata"].get("HTTPStatusCode") != 200:
            raise CloudError("provider acknowledgement missing or uncertain")

    def get(self, namespace: str, object_ref: str) -> bytes:
        key = self._key(namespace, object_ref)
        response = self._client.get_object(Bucket=self._bucket, Key=key)
        if not isinstance(response, dict):
            raise IntegrityError("invalid provider response")
        size = response.get("ContentLength")
        if type(size) is not int or not 33 <= size <= self._limit():
            raise IntegrityError("missing or unbounded stored length")
        metadata = response.get("Metadata")
        if not isinstance(metadata, dict) or (
            metadata.get("envelope-version") != self._envelope_version()
        ):
            raise IntegrityError("missing expected encrypted envelope metadata")
        expected = metadata.get("ciphertext-sha256")
        if not isinstance(expected, str) or not re.fullmatch(r"[0-9a-f]{64}", expected):
            raise IntegrityError("missing ciphertext integrity metadata")
        stream = response.get("Body")
        if not callable(getattr(stream, "read", None)) or not callable(getattr(stream, "close", None)):
            raise IntegrityError("bounded, closable provider stream required")
        try:
            body = stream.read(self._limit() + 1)
        finally:
            stream.close()
        if not isinstance(body, bytes) or len(body) != size or not body.startswith(self._magic()):
            raise IntegrityError("ciphertext length/type mismatch")
        if not hmac.compare_digest(hashlib.sha256(body).hexdigest(), expected):
            raise IntegrityError("provider ciphertext integrity mismatch")
        # Provider-side metadata is NOT canonical. Caller independently checks
        # these bytes against Vault/SC002 trusted digest before any release.
        return body
