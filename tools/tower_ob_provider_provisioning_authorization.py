#!/usr/bin/env python3
"""Write offline Tower–OB provider-provisioning authorization worksheets."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from tower.tower_ob_managed_staging_provider_provisioning_authorization import (
    write_provisioning_authorization_worksheets,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--write-worksheets",
        required=True,
        help="Output directory outside the repository.",
    )
    parser.add_argument(
        "--repository-root",
        required=True,
        help="Tower–Observatory integration repository root.",
    )
    args = parser.parse_args()

    output = Path(args.write_worksheets).expanduser().resolve()
    repository_root = Path(args.repository_root).expanduser().resolve()

    if output == repository_root or repository_root in output.parents:
        raise SystemExit(
            "Refusing to write operator worksheets inside the repository."
        )

    result = write_provisioning_authorization_worksheets(
        output,
        repository_root=repository_root,
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
