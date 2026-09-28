"""Independent Tower-owned Grounds operational release authority boundary.

Identity and infrastructure readiness are deliberately insufficient to release
real resident/staff traffic. This module consumes a separately installed,
server-owned provider that must revalidate current owner acceptance, recovery,
privacy/legal review and operating coverage. It has no env Boolean bypass.
"""
from __future__ import annotations

from importlib import import_module
import os
import re
import time
from collections.abc import Mapping
from typing import Any

PROVIDER_ENV = "TOWER_GROUNDS_RELEASE_PROVIDER_MODULE"
SCHEMA = "tower.grounds.operational-release.v1"
OPAQUE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.:-]{7,191}$")


class GroundsOperationalReleaseAuthorityUnavailable(RuntimeError):
    pass


def _provider():
    module_name = str(os.getenv(PROVIDER_ENV, "") or "").strip()
    if not module_name or module_name.startswith(("tower.", "grounds.")):
        raise GroundsOperationalReleaseAuthorityUnavailable(
            "independent Grounds operational release provider is not configured"
        )
    try:
        provider = import_module(module_name)
    except Exception:
        raise GroundsOperationalReleaseAuthorityUnavailable(
            "independent Grounds operational release provider cannot be loaded"
        ) from None
    for name in ("current_release_decision", "health_check"):
        if not callable(getattr(provider, name, None)):
            raise GroundsOperationalReleaseAuthorityUnavailable(
                "independent Grounds operational release provider contract is incomplete"
            )
    return provider


def _decision(provider, *, now_epoch: int | None = None) -> dict[str, Any]:
    now = int(time.time()) if now_epoch is None else int(now_epoch)
    try:
        record = provider.current_release_decision()
    except Exception:
        raise GroundsOperationalReleaseAuthorityUnavailable(
            "Grounds operational release decision unavailable"
        ) from None
    expected = {
        "schema_version", "issuer", "audience", "status", "environment_id",
        "revision_id", "owner_acceptance_ref", "storage_restore_ref",
        "privacy_housing_review_ref", "operations_coverage_ref",
        "issued_at_epoch", "expires_at_epoch", "revocation_checked",
    }
    if not isinstance(record, Mapping) or set(record) != expected:
        raise GroundsOperationalReleaseAuthorityUnavailable(
            "Grounds operational release decision invalid"
        )
    refs = (
        "environment_id", "revision_id", "owner_acceptance_ref",
        "storage_restore_ref", "privacy_housing_review_ref",
        "operations_coverage_ref",
    )
    if (
        record["schema_version"] != SCHEMA
        or record["issuer"] != "tower"
        or record["audience"] != "grounds"
        or record["status"] != "APPROVED"
        or record["revocation_checked"] is not True
        or any(
            not isinstance(record[key], str) or OPAQUE.fullmatch(record[key]) is None
            for key in refs
        )
        or type(record["issued_at_epoch"]) is not int
        or type(record["expires_at_epoch"]) is not int
        or not record["issued_at_epoch"] <= now < record["expires_at_epoch"]
        or record["expires_at_epoch"] - record["issued_at_epoch"] > 300
    ):
        raise GroundsOperationalReleaseAuthorityUnavailable(
            "Grounds operational release is not current"
        )
    return dict(record)


def create_certified_grounds_operational_release_guard():
    provider = _provider()

    def guard(environ):
        try:
            _decision(provider)
            return provider.health_check() is True
        except Exception:
            return False

    def health_check():
        try:
            _decision(provider)
            return provider.health_check() is True
        except Exception:
            return False

    guard.health_check = health_check
    return guard
