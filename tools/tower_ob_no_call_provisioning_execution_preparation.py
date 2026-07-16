from __future__ import annotations

import argparse
import json
from pathlib import Path

from tower.tower_ob_managed_staging_no_call_provisioning_execution_preparation import (
    write_execution_preparation_worksheets,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Write no-call Tower–OB provisioning execution-preparation worksheets.")
    parser.add_argument("--output-directory", required=True)
    parser.add_argument("--repository-root", default=str(Path(__file__).resolve().parents[1]))
    args = parser.parse_args()
    result = write_execution_preparation_worksheets(
        args.output_directory,
        repository_root=args.repository_root,
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
