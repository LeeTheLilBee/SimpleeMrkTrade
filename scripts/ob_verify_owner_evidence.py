"""Verify an owner-downloaded SYNTHETIC Proof/Demo report chain offline.

Usage: python -m scripts.ob_verify_owner_evidence --file PATH
The hash verifies local byte-content integrity, NOT a third-party signature.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import stat

from tower.ob_hosted_owner_evidence import verify_downloaded_owner_evidence_packet

MAX_FILE_BYTES = 16 * 1024 * 1024


def _unique_pairs(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON field")
        result[key] = value
    return result


def _reject_nonfinite(_: str) -> object:
    raise ValueError("nonfinite JSON number")


def read_and_verify(path: Path) -> dict[str, object]:
    """Read a single bounded regular file without following a swapped symlink.

    Checking is_file()/is_symlink() and then Path.open() leaves a race between
    checking a path and opening it. This offline tool verifies an owner-chosen
    downloaded Proof/Demo file, not an arbitrary device, pipe or live archive.
    """
    path = Path(path)
    original = path.lstat()
    if not stat.S_ISREG(original.st_mode) or not 0 < original.st_size <= MAX_FILE_BYTES:
        raise ValueError("missing, symlinked or oversized owner proof packet")
    if not hasattr(os, "O_NOFOLLOW"):
        # Do not silently weaken the claimed no-symlink boundary on a platform
        # that cannot enforce it atomically at open time.
        raise ValueError("safe no-follow owner proof read unsupported here")
    flags = os.O_RDONLY | os.O_NOFOLLOW | getattr(os, "O_NONBLOCK", 0)
    flags |= getattr(os, "O_CLOEXEC", 0)
    fd = os.open(path, flags)
    with os.fdopen(fd, "rb") as file:
        opened = os.fstat(file.fileno())
        if (
            not stat.S_ISREG(opened.st_mode)
            or (opened.st_dev, opened.st_ino) != (original.st_dev, original.st_ino)
            or not 0 < opened.st_size <= MAX_FILE_BYTES
        ):
            raise ValueError("owner proof file changed or is not a bounded regular file")
        # A size check alone is not enough if a file grows while being read.
        raw = file.read(MAX_FILE_BYTES + 1)
    if not 0 < len(raw) <= MAX_FILE_BYTES:
        raise ValueError("owner proof packet is empty or oversized")
    packet = json.loads(
        raw.decode("utf-8"), object_pairs_hook=_unique_pairs,
        parse_constant=_reject_nonfinite,
    )
    return verify_downloaded_owner_evidence_packet(packet)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Verify only local synthetic OB rehearsal hash integrity.")
    parser.add_argument("--file", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        value = read_and_verify(args.file)
    except (ValueError, TypeError, OSError, UnicodeError, RecursionError):
        print("REJECTED: incomplete, tampered or invalid owner Proof/Demo packet. Not broker/Tower proof.")
        return 1
    print(
        f"VALID LOCAL INTEGRITY ONLY | {value['tick_count']} synthetic tick(s) | "
        f"packet hash {value['packet_hash']} | no Manual Live authority"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
