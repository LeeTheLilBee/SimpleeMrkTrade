#!/usr/bin/env sh
set -eu
exec gunicorn --bind 0.0.0.0:${PORT:?PORT is required} web.managed_staging:app
