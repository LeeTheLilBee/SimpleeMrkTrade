from __future__ import annotations

import argparse
import json
from pathlib import Path

from tower.tower_ob_managed_staging_service_creation import write_operator_worksheets


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repository-root", required=True)
    parser.add_argument("--output-directory", required=True)
    args = parser.parse_args()
    result = write_operator_worksheets(Path(args.repository_root), Path(args.output_directory))
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
