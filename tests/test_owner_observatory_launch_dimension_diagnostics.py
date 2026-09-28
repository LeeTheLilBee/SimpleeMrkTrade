"""Regression coverage for redacted owner OB launch failure dimensions (issue #146)."""
from unittest.mock import patch

import pytest

from tower.owner_observatory_handoff import (
    OwnerObservatoryHandoffError,
    _verified_owner_and_app,
)


def _identity():
    return {
        "verification_state": "VERIFIED",
        "configured": True,
        "record": {"role": "owner", "username": "owner"},
    }


@pytest.mark.parametrize("failed", [
    "implemented", "published", "environment_available", "health_verified",
    "user_entitled", "launch_route_configured",
])
def test_launch_denial_identifies_failed_dimension_without_bypass(failed):
    dimensions = {
        key: {"display_state": "VERIFIED", "display_value": True}
        for key in (
            "registered", "implemented", "published", "environment_available",
            "health_verified", "user_entitled", "launch_route_configured",
        )
    }
    dimensions[failed] = {"display_state": "NOT_CONFIGURED", "display_value": None}
    app = {
        "launchable": False,
        "display_dimensions": dimensions,
        "request_authorization_required": True,
    }
    with patch(
        "tower.owner_observatory_handoff.hosted_owner_identity_authority",
        return_value=_identity(),
    ), patch(
        "tower.owner_observatory_handoff.app_truth_by_id", return_value=app
    ):
        with pytest.raises(OwnerObservatoryHandoffError) as exc:
            _verified_owner_and_app({"username": "owner"})
    assert exc.value.code == "owner_observatory_app_not_launchable_" + failed


def test_absent_dimension_data_still_denies_with_original_error():
    with patch(
        "tower.owner_observatory_handoff.hosted_owner_identity_authority",
        return_value=_identity(),
    ), patch(
        "tower.owner_observatory_handoff.app_truth_by_id",
        return_value={"launchable": False},
    ):
        with pytest.raises(OwnerObservatoryHandoffError) as exc:
            _verified_owner_and_app({"username": "owner"})
    assert exc.value.code == "owner_observatory_app_not_launchable"
