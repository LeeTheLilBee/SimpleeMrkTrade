#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
from pathlib import Path

from tower.hosted_candidate_release_gate import (
    build_hosted_candidate_release_packet,
)


def main() -> int:

    parser = argparse.ArgumentParser(
        description=(
            "Build a Tower owner-review release packet "
            "from a TWR086–TWR090 hosted parity JSON result."
        )
    )

    parser.add_argument(
        "--parity-json",
        required=True,
        help=(
            "Path to hosted candidate parity JSON."
        ),
    )

    parser.add_argument(
        "--output",
        help=(
            "Optional output JSON path. "
            "If omitted, packet prints to stdout."
        ),
    )

    args = (
        parser.parse_args()
    )


    parity_path = Path(
        args.parity_json
    )

    parity = json.loads(
        parity_path.read_text(
            encoding="utf-8"
        )
    )


    result = (
        build_hosted_candidate_release_packet(
            parity
        )
    )


    text = (
        json.dumps(
            result,
            indent=2,
            sort_keys=True,
        )
        + "\n"
    )


    if args.output:

        output = Path(
            args.output
        )

        output.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        output.write_text(
            text,
            encoding="utf-8",
        )

    else:

        print(
            text,
            end="",
        )


    return 0


if __name__ == "__main__":
    raise SystemExit(
        main()
    )
