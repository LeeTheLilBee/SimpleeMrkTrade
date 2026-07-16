from __future__ import annotations

import argparse
import json
from pathlib import Path

from tower.tower_ob_managed_staging_provider_provisioning_execution_authorization import (
    write_execution_authorization_worksheets,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Write fail-closed Tower–OB provider provisioning "
            "execution-authorization worksheets."
        )
    )
    parser.add_argument("--output-directory", required=True)
    parser.add_argument(
        "--repository-root",
        default=str(Path(__file__).resolve().parents[1]),
    )
    args = parser.parse_args()
    result = write_execution_authorization_worksheets(
        args.output_directory,
        repository_root=args.repository_root,
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
