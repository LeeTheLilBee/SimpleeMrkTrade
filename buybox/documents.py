"""Encrypted, private local intake for original acquisition evidence.

This is operational BuyBox intake storage, not Archive Vault. Transfer to
permanent Vault must later be mediated by Tower and its authenticated corridor.
Never render uploaded HTML or PDF inline from BuyBox.
"""
from __future__ import annotations
import os
import secrets
import stat
from io import BytesIO
from pathlib import Path
from cryptography.fernet import Fernet, InvalidToken
from .evidence import artifact_descriptor

SUPPORTED = {
    "application/pdf": ".pdf",
    "image/png": ".png",
    "image/jpeg": ".jpg",
    "text/plain": ".txt",
    "text/csv": ".csv",
}
MAX_UPLOAD = 25 * 1024 * 1024

def _check_magic(data, mime):
    if mime == "application/pdf": return data.startswith(b"%PDF-")
    if mime == "image/png": return data.startswith(b"\x89PNG\r\n\x1a\n")
    if mime == "image/jpeg": return data.startswith(b"\xff\xd8\xff")
    if mime in ("text/plain","text/csv"):
        if b"\x00" in data: return False
        try: data.decode("utf-8")
        except UnicodeDecodeError: return False
        return True
    return False

class PrivateDocumentStore:
    def __init__(self, root, encryption_key):
        path = Path(root).expanduser()
        if not path.is_dir() or path.is_symlink():
            raise RuntimeError("Document storage must be an existing private, non-symlink directory.")
        if stat.S_IMODE(path.stat().st_mode) & 0o077:
            raise RuntimeError("Document directory must exclude group/other access (chmod 700).")
        self.root = path
        self.cipher = Fernet(encryption_key.encode() if isinstance(encryption_key,str) else encryption_key)

    def ingest(self, *, contents, filename, mime, source_party):
        if not isinstance(contents,bytes) or not 0 < len(contents) <= MAX_UPLOAD:
            raise ValueError("INVALID_DOCUMENT_SIZE")
        if mime not in SUPPORTED or not _check_magic(contents,mime):
            raise ValueError("DOCUMENT_TYPE_NOT_VERIFIED")
        ref = secrets.token_hex(24)
        desc = artifact_descriptor(contents,filename=filename,mime=mime,
                                   storage_reference=ref,source_party=source_party)
        encrypted = self.cipher.encrypt(contents)
        fd = os.open(str(self.root / ref), os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
        try:
            with os.fdopen(fd,"wb") as output:
                output.write(encrypted)
                output.flush()
                os.fsync(output.fileno())
        except BaseException:
            (self.root/ref).unlink(missing_ok=True)
            raise
        return desc

    def read(self, descriptor):
        ref = descriptor["storage_reference"]
        if not isinstance(ref,str) or len(ref)!=48 or any(c not in "0123456789abcdef" for c in ref):
            raise ValueError("INVALID_DOCUMENT_REFERENCE")
        target = self.root / ref
        if target.is_symlink():
            raise ValueError("INVALID_DOCUMENT_TARGET")
        try:
            encrypted = target.read_bytes()
            data = self.cipher.decrypt(encrypted)
        except (FileNotFoundError,InvalidToken):
            raise ValueError("DOCUMENT_UNAVAILABLE")
        from hashlib import sha256
        if sha256(data).hexdigest()!=descriptor["sha256"] or len(data)!=descriptor["size_bytes"]:
            raise ValueError("DOCUMENT_INTEGRITY_FAILURE")
        return data
