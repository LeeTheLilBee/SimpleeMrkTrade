from __future__ import annotations

import argparse
import json
from pathlib import Path

from tower.tower_ob_managed_staging_controlled_provider_provisioning_execution_session_opening_execution_preparation import (
    write_session_opening_execution_preparation_worksheets,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repository-root", required=True)
    parser.add_argument("--output-directory", required=True)
    args = parser.parse_args()
    paths = write_session_opening_execution_preparation_worksheets(
        Path(args.output_directory), repository_root=Path(args.repository_root)
    )
    print(json.dumps(paths, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
