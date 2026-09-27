"""Verify an owner-downloaded SYNTHETIC Proof/Demo report chain offline.

Usage: python -m scripts.ob_verify_owner_evidence --file PATH
The hash verifies local byte-content integrity, NOT a third-party signature.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

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
    if not path.is_file() or path.is_symlink() or path.stat().st_size > MAX_FILE_BYTES:
        raise ValueError("missing, symlinked or oversized owner proof packet")
    with path.open("r", encoding="utf-8") as file:
        packet = json.load(
            file, object_pairs_hook=_unique_pairs, parse_constant=_reject_nonfinite,
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
