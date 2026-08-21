#!/usr/bin/env python3
"""
TWR086–TWR090 hosted candidate parity verifier.

Example AFTER an explicitly authorized staging deployment:

    python scripts/verify_tower_hosted_runtime_parity.py \
        --base-url https://example.onrender.com \
        --expected-revision <exact-candidate-sha>

Exit:
  0 -> exact hosted candidate parity passed
  2 -> parity failed
"""

from __future__ import annotations

import argparse
import json
import sys

from tower.hosted_runtime_parity import (
    probe_hosted_runtime,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Verify exact Tower hosted-runtime "
            "candidate parity."
        )
    )

    parser.add_argument(
        "--base-url",
        required=True,
        help=(
            "HTTPS root URL of the "
            "Tower staging service."
        ),
    )

    parser.add_argument(
        "--expected-revision",
        required=True,
        help=(
            "Exact Git revision expected "
            "to be served."
        ),
    )

    parser.add_argument(
        "--timeout",
        type=float,
        default=10.0,
    )

    parser.add_argument(
        "--allow-http",
        action="store_true",
        help=(
            "Allow HTTP only for explicit "
            "local development/tests."
        ),
    )

    args = parser.parse_args()

    result = (
        probe_hosted_runtime(
            base_url=args.base_url,
            expected_revision=(
                args.expected_revision
            ),
            timeout=args.timeout,
            allow_http=args.allow_http,
        )
    )

    print(
        json.dumps(
            result,
            indent=2,
            sort_keys=True,
        )
    )

    return (
        0
        if result[
            "parity_pass"
        ]
        else 2
    )


if __name__ == "__main__":
    sys.exit(
        main()
    )
