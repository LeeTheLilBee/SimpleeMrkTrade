"""
Managed staging WSGI entrypoint for Render.

This module intentionally imports the canonical Flask app from web.app.
It exists so managed hosts configured for web.managed_staging:app can
boot the same Tower-fronted application without duplicating app logic.

Safety:
- no production deployment authorization
- no broker submission
- no capital movement
- no Manual Live authorization
- no Live Auto authorization
- no STAGING_READY change
"""

from __future__ import annotations

from web.app import app as app


STAGING_ENTRYPOINT = "web.managed_staging:app"
PRODUCTION_DEPLOYMENT = False
BROKER_SUBMISSION = False
CAPITAL_MOVEMENT = False
MANUAL_LIVE_AUTHORIZED = False
LIVE_AUTO_AUTHORIZED = False
STAGING_READY = False


def managed_staging_status() -> dict[str, object]:
    """Return a tiny import-safe status contract for tests and deploy checks."""
    return {
        "entrypoint": STAGING_ENTRYPOINT,
        "app_imported": app is not None,
        "production_deployment": PRODUCTION_DEPLOYMENT,
        "broker_submission": BROKER_SUBMISSION,
        "capital_movement": CAPITAL_MOVEMENT,
        "manual_live_authorized": MANUAL_LIVE_AUTHORIZED,
        "live_auto_authorized": LIVE_AUTO_AUTHORIZED,
        "staging_ready": STAGING_READY,
    }
