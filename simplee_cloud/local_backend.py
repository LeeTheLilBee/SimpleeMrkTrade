"""Private local ciphertext backend for source tests and future owner-owned hardware.

Requires an isolated, process-private root. This alone is NOT a hardened
production object store, replication layer, or a replacement for independent DR.
"""
from __future__ import annotations

import os
import stat
from pathlib import Path

from .contracts import (
    AlreadyExists, CiphertextBackend, CloudError, IntegrityError,
    MAX_ENVELOPE_BYTES, ObjectMissing, valid_backup_ref, valid_object_ref,
)


class LocalPrivateCiphertextBackend(CiphertextBackend):
    def __init__(self, root: Path):
        self.root = Path(root)
        if self.root.is_symlink():
            raise CloudError("symlink storage root forbidden")
        self.root.mkdir(parents=True, exist_ok=True, mode=0o700)
        if not self.root.is_dir() or stat.S_IMODE(self.root.stat().st_mode) & 0o077:
            raise CloudError("storage root must be private (0700)")

    def _path(self, namespace: str, object_ref: str) -> Path:
        if not isinstance(namespace, str) or len(namespace) != 64 or any(
            c not in "0123456789abcdef" for c in namespace
        ):
            raise CloudError("invalid opaque namespace")
        if not (valid_object_ref(object_ref) or valid_backup_ref(object_ref)):
            raise CloudError("invalid opaque object reference")
        category, ident = object_ref.split("/")
        target = self.root / namespace / category
        for parent in (self.root / namespace, target):
            if parent.is_symlink():
                raise CloudError("symlink storage namespace forbidden")
            parent.mkdir(mode=0o700, exist_ok=True)
            if not parent.is_dir() or stat.S_IMODE(parent.stat().st_mode) & 0o077:
                raise CloudError("storage namespace not private")
        return target / ident

    def put_if_absent(self, namespace: str, object_ref: str, body: bytes) -> None:
        if not isinstance(body, bytes) or not 33 <= len(body) <= MAX_ENVELOPE_BYTES + 64:
            raise CloudError("invalid bounded ciphertext")
        if not body.startswith((b"VLT1", b"SCB1")):
            raise CloudError("unencrypted body forbidden")
        if (valid_object_ref(object_ref) and not body.startswith(b"VLT1")) or (
            valid_backup_ref(object_ref) and not body.startswith(b"SCB1")
        ):
            raise CloudError("ciphertext envelope kind mismatch")
        path = self._path(namespace, object_ref)
        flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
        if hasattr(os, "O_NOFOLLOW"):
            flags |= os.O_NOFOLLOW
        try:
            fd = os.open(path, flags, 0o600)
        except FileExistsError as exc:
            raise AlreadyExists("immutable object already exists") from exc
        try:
            with os.fdopen(fd, "wb") as out:
                out.write(body)
                out.flush()
                os.fsync(out.fileno())
            # Sync containing directory so the exclusive object name is durable.
            dir_fd = os.open(path.parent, os.O_RDONLY)
            try:
                os.fsync(dir_fd)
            finally:
                os.close(dir_fd)
        except BaseException:
            # An uncertain write is never silently reused as if acknowledged.
            raise

    def get(self, namespace: str, object_ref: str) -> bytes:
        path = self._path(namespace, object_ref)
        flags = os.O_RDONLY
        if hasattr(os, "O_NOFOLLOW"):
            flags |= os.O_NOFOLLOW
        try:
            fd = os.open(path, flags)
        except FileNotFoundError as exc:
            raise ObjectMissing("object not found") from exc
        try:
            info = os.fstat(fd)
            if not stat.S_ISREG(info.st_mode) or not 33 <= info.st_size <= MAX_ENVELOPE_BYTES + 64:
                raise IntegrityError("invalid stored object")
            with os.fdopen(fd, "rb") as inp:
                fd = -1
                body = inp.read(MAX_ENVELOPE_BYTES + 65)
            if len(body) != info.st_size:
                raise IntegrityError("stored object changed or length mismatch")
            return body
        finally:
            if fd != -1:
                os.close(fd)
