"""Retired import path; delegates to the canonical hosted Tower runtime.

This compatibility file declares no routes, middleware, or runtime identity.
It may be removed after the host's startup command has been migrated.
"""
from web.hosted_tower import app, hosted_tower_runtime_manifest, hosted_tower_status

managed_staging_runtime_manifest = hosted_tower_runtime_manifest
managed_staging_status = hosted_tower_status
