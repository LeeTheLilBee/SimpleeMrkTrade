"""Tower composition for the protected, SOURCE-ONLY Observatory Market Data Desk.

No market transport, entitlement, credential, quote, streaming connection,
broker access, stateful approval workflow or public app route is created here.
A fresh disconnected catalog projection is built only after the exact Tower
owner/session/step-up and OB admission checks pass.
"""
from __future__ import annotations

from datetime import datetime, timezone
from flask import Flask

from engine.market_intake import ScanContext, UniversalMarketGateway
from engine.market_intake.desk_process import ProviderDeskProcess
from engine.market_intake.desk_projection import build_desk_snapshot
from tower.tower_human_login_ob_launch import (
    operational_ob_access_active,
    owner_session_active,
    step_up_active,
)
from web.ob_market_data_desk_route import create_market_data_desk_blueprint

MARKET_DATA_DESK_PATH = "/ob/data-desk"


def _tower_authorize_data_desk() -> bool:
    """Never infer read permission from page metadata or browser claims."""
    return (
        owner_session_active() is True
        and step_up_active() is True
        and operational_ob_access_active() is True
    )


def _unconnected_catalog_snapshot() -> dict:
    """Fresh *catalog* snapshot. No runtime provider status is asserted.

    New uninstalled instances are intentional: the product source is present,
    but provider accounts, rights, transport and persistent audit are not.
    Do not bind this to real price authority or show any fabricated live data.
    """
    context = ScanContext(now=datetime.now(timezone.utc))
    return build_desk_snapshot(
        gateway=UniversalMarketGateway(),
        process=ProviderDeskProcess(),
        context=context,
    )


def register_protected_ob_market_data_desk(app: Flask) -> Flask:
    if app.extensions.get("tower_ob_market_data_desk_source_only_v1"):
        return app
    existing = {rule.rule for rule in app.url_map.iter_rules()}
    if MARKET_DATA_DESK_PATH in existing:
        raise RuntimeError("Market Data Desk route already has a different owner")
    app.register_blueprint(create_market_data_desk_blueprint(
        tower_owner_authorize=_tower_authorize_data_desk,
        protected_snapshot=_unconnected_catalog_snapshot,
    ))
    from tower.ob_public_owner_connection import register_public_owner_connection
    register_public_owner_connection(app, owner_authorize=_tower_authorize_data_desk)
    from engine.market_intake.keyless_public_context import from_environment
    from web.ob_keyless_context_route import create_keyless_context_blueprint
    app.register_blueprint(create_keyless_context_blueprint(
        owner_authorize=_tower_authorize_data_desk,
        context_service=from_environment(),
    ))
    from tower.ob_provider_key_desk import register_provider_key_desk
    register_provider_key_desk(app, owner_authorize=_tower_authorize_data_desk)
    from tower.ob_keyed_provider_research import create_keyed_provider_research_blueprint
    app.register_blueprint(create_keyed_provider_research_blueprint(
        owner_authorize=_tower_authorize_data_desk,
        secret_reader=app.extensions["ob_provider_key_secret_reader_v1"],
    ))
    from web.ob_connection_truth_route import create_connection_truth_blueprint
    app.register_blueprint(create_connection_truth_blueprint(
        owner_authorize=_tower_authorize_data_desk,
        key_reader=app.extensions["ob_provider_key_status_reader_v1"],
        public_reader=app.extensions["ob_public_owner_status_reader_v1"],
    ))
    app.extensions["tower_ob_market_data_desk_source_only_v1"] = {
        "path": MARKET_DATA_DESK_PATH,
        "source_only": True,
        "runtime_provider_attached": False,
        "quote_data_attached": False,
        "browser_approval": False,
        "broker_execution": False,
        "paid_resources": False,
    }
    return app
