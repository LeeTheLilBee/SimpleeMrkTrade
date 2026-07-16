"""Managed staging WSGI entrypoint.

Provider start command:

    gunicorn --bind 0.0.0.0:$PORT web.managed_staging:app

The factory fails closed before importing ``web.app`` when required staging
references or owner approval are missing.
"""

from tower.tower_ob_managed_staging_runtime import (
    create_managed_staging_app,
)

app = create_managed_staging_app()
application = app

__all__ = ["app", "application"]
