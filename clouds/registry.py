"""
The Clouds — canonical app and mission-lane registry.

Registry data is local and static in GP001.

No operational app is imported or called.
"""

from __future__ import annotations

try:
    from .contracts import (
        AppConnectionState,
        AppDefinition,
        MissionLaneDefinition,
    )
except ImportError:
    from contracts import (
        AppConnectionState,
        AppDefinition,
        MissionLaneDefinition,
    )


APPS = (
    AppDefinition(
        app_id="tower",
        app_name="The Tower",
        purpose=(
            "Identity, permission, step-up, approval, "
            "and secure application routing."
        ),
        owner_surface_route="/tower",
        authority_boundary=(
            "Tower alone controls identity and access."
        ),
        connection_state=(
            AppConnectionState.SUMMARY_READY.value
        ),
        display_order=10,
    ),
    AppDefinition(
        app_id="observatory",
        app_name="The Observatory",
        purpose=(
            "Investment intelligence, portfolio stewardship, "
            "and controlled capital execution."
        ),
        owner_surface_route="/tower/observatory",
        authority_boundary=(
            "Observatory alone owns trading and capital "
            "execution within Tower controls."
        ),
        connection_state=(
            AppConnectionState.SUMMARY_READY.value
        ),
        display_order=20,
    ),
    AppDefinition(
        app_id="archive_vault",
        app_name="Archive Vault",
        purpose=(
            "Sealed evidence, document memory, receipts, "
            "and protected historical records."
        ),
        owner_surface_route="/tower/vault",
        authority_boundary=(
            "Vault is sealed memory and is accessed through "
            "approved Tower workflows."
        ),
        connection_state=(
            AppConnectionState.SUMMARY_READY.value
        ),
        display_order=30,
    ),
    AppDefinition(
        app_id="teller",
        app_name="The Teller",
        purpose=(
            "Payroll, payments, people, vendors, agreements, "
            "and workflow operations."
        ),
        owner_surface_route="/tower/teller",
        authority_boundary=(
            "Teller owns payment and workflow operations; "
            "Clouds does not move money."
        ),
        connection_state=(
            AppConnectionState.RESERVED.value
        ),
        display_order=40,
    ),
    AppDefinition(
        app_id="grounds",
        app_name="The Grounds",
        purpose=(
            "Real-estate acquisition, stewardship, leasing, "
            "maintenance, and portfolio operations."
        ),
        owner_surface_route="/tower/grounds",
        authority_boundary=(
            "Grounds owns real-estate operations."
        ),
        connection_state=(
            AppConnectionState.RESERVED.value
        ),
        display_order=50,
    ),
    AppDefinition(
        app_id="clouds",
        app_name="The Clouds",
        purpose=(
            "Universal owner command, summaries, priorities, "
            "decisions, and navigation."
        ),
        owner_surface_route="/clouds",
        authority_boundary=(
            "Clouds observes and routes; it does not execute "
            "another application's work."
        ),
        connection_state=(
            AppConnectionState.CONNECTED.value
        ),
        display_order=60,
    ),
)


MISSION_LANES = (
    MissionLaneDefinition(
        lane_id="owner_command",
        lane_name="Owner Command",
        business_name="Simplee World",
        owning_app_id="clouds",
        purpose=(
            "Cross-business owner awareness and direction."
        ),
        active=True,
        display_order=10,
    ),
    MissionLaneDefinition(
        lane_id="investment_engine",
        lane_name="Investment Engine",
        business_name="SimpleeMrkTrade",
        owning_app_id="observatory",
        purpose=(
            "Investment research, portfolio management, "
            "risk, and controlled execution."
        ),
        active=True,
        display_order=20,
    ),
    MissionLaneDefinition(
        lane_id="trust_stewardship",
        lane_name="Trust Stewardship",
        business_name=(
            "Simplee Bowdre Living Irrevocable Trust"
        ),
        owning_app_id="archive_vault",
        purpose=(
            "Trust records, ownership evidence, and "
            "long-term stewardship."
        ),
        active=True,
        display_order=30,
    ),
    MissionLaneDefinition(
        lane_id="atm_operations",
        lane_name="ATM Operations",
        business_name="SimpleeOnTheGo",
        owning_app_id="teller",
        purpose=(
            "ATM route acquisition, vault cash, servicing, "
            "and business operations."
        ),
        active=True,
        display_order=40,
    ),
    MissionLaneDefinition(
        lane_id="real_estate",
        lane_name="Real Estate",
        business_name="The Grounds",
        owning_app_id="grounds",
        purpose=(
            "Office, apartment, and property acquisition "
            "and stewardship."
        ),
        active=True,
        display_order=50,
    ),
    MissionLaneDefinition(
        lane_id="people_and_payments",
        lane_name="People and Payments",
        business_name="Simplee World",
        owning_app_id="teller",
        purpose=(
            "Payroll, employees, vendors, agreements, "
            "and approved payments."
        ),
        active=False,
        display_order=60,
    ),
)


def list_apps() -> tuple[AppDefinition, ...]:
    return tuple(
        sorted(
            APPS,
            key=lambda item: (
                item.display_order,
                item.app_id,
            ),
        )
    )


def get_app(
    app_id: str,
) -> AppDefinition | None:
    for app in APPS:
        if app.app_id == app_id:
            return app

    return None


def list_mission_lanes() -> tuple[
    MissionLaneDefinition,
    ...
]:
    return tuple(
        sorted(
            MISSION_LANES,
            key=lambda item: (
                item.display_order,
                item.lane_id,
            ),
        )
    )


def get_mission_lane(
    lane_id: str,
) -> MissionLaneDefinition | None:
    for lane in MISSION_LANES:
        if lane.lane_id == lane_id:
            return lane

    return None
