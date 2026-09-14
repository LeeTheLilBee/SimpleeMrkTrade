
#!/usr/bin/env python3
"""Operator-triggered genuine hosted candidate publication / TWR106-TWR107."""

from __future__ import annotations

import argparse
import json

from tower.hosted_release_candidate_publication import publish_hosted_release_candidate


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Probe real hosted Tower parity and atomically publish a sealed owner-review candidate."
    )
    parser.add_argument("--base-url", help="Trusted hosted Tower HTTPS root; defaults to server configuration.")
    parser.add_argument("--expected-revision", help="Trusted exact hosted candidate Git revision.")
    arguments = parser.parse_args()
    result = publish_hosted_release_candidate(
        base_url=arguments.base_url,
        expected_revision=arguments.expected_revision,
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result.get("published") else 1


if __name__ == "__main__":
    raise SystemExit(main())
