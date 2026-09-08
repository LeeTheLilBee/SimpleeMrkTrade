#!/usr/bin/env bash
set -euo pipefail
# Retired launch path. All configuration belongs to the canonical script.
exec bash "$(dirname "$0")/../hosted_tower/start.sh"
