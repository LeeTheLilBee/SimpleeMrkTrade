"""Private S3-compatible managed ciphertext adapter.

No credentials, bucket, region or endpoint defaults. The caller injects an already
configured least-privilege client after deployment authorization. No public ACL,
presigned URL, list, delete or plaintext API is exposed.
"""
from __future__ import annotations
import hashlib
import re
from typing import Any
from vault.real_operations_encrypted_storage import StorageError

_BUCKET = re.compile(r"^[a-z0-9][a-z0-9.-]{2,62}$")
_KEY = re.compile(r"^objects/[a-f0-9]{48}$")

class PrivateManagedCiphertextStore:
    def __init__(self, *, client: Any, bucket: str):
        if client is None or not isinstance(bucket,str) or not _BUCKET.fullmatch(bucket):
            raise StorageError("explicit private managed client and bucket required")
        self._client = client
        self._bucket = bucket

    def put_if_absent(self, object_key: str, ciphertext: bytes) -> None:
        if not isinstance(object_key,str) or not _KEY.fullmatch(object_key):
            raise StorageError("invalid opaque object key")
        if not isinstance(ciphertext,bytes) or not ciphertext.startswith(b"VLT1"):
            raise StorageError("only encrypted envelopes may be stored")
        digest=hashlib.sha256(ciphertext).hexdigest()
        # S3 If-None-Match is an atomic create-only conditional write.
        # Provider must support this exact conditional; fail closed on errors.
        self._client.put_object(
            Bucket=self._bucket, Key=object_key, Body=ciphertext,
            IfNoneMatch="*", ContentType="application/octet-stream",
            Metadata={"ciphertext-sha256":digest,"envelope-version":"v1"},
            ServerSideEncryption="AES256",
        )

    def get(self, object_key: str) -> bytes:
        if not isinstance(object_key,str) or not _KEY.fullmatch(object_key):
            raise StorageError("invalid opaque object key")
        response=self._client.get_object(Bucket=self._bucket,Key=object_key)
        declared=response.get("ContentLength")
        max_envelope_bytes=25*1024*1024+64
        if type(declared) is not int or declared<33 or declared>max_envelope_bytes:
            raise StorageError("invalid managed ciphertext length")
        body=response["Body"].read(max_envelope_bytes+1)
        if len(body)!=declared:
            raise StorageError("managed ciphertext length mismatch")
        if not isinstance(body,bytes) or not body.startswith(b"VLT1"):
            raise StorageError("managed object is not an encrypted envelope")
        metadata=response.get("Metadata") or {}
        expected=metadata.get("ciphertext-sha256")
        if not isinstance(expected,str) or hashlib.sha256(body).hexdigest()!=expected:
            raise StorageError("managed ciphertext integrity mismatch")
        return body
