"""Server-side, redacted read projection for a protected Market Data Desk.

No synthetic market data, source tokens, account identifiers, broker or order data.
Future Tower route must bind owner session/step-up before calling this projection.
"""
from __future__ import annotations

from datetime import datetime

from .contracts import ScanContext, _aware
from .desk_process import ProviderDeskProcess
from .gateway import UniversalMarketGateway


def build_desk_snapshot(*, gateway: UniversalMarketGateway,
                        process: ProviderDeskProcess,
                        context: ScanContext) -> dict[str, object]:
    """Reads internal state only; it never polls providers or opens a connection."""
    _aware(context.now, "desk snapshot time")
    providers = gateway.provider_status(context)["providers"]
    workflow = process.status(context.now)
    current = set(p["product_key"] for p in providers)
    cases = [case for case in workflow["cases"] if case["product_key"] in current]
    return {
        "schema": "OB_MARKET_DATA_DESK_V1",
        "as_of": context.now.isoformat(),
        "read_only": True,
        "source_only": True,
        "runtime_health_attached": False,
        "prices_attached": False,
        "connection_truth": "UNVERIFIED", # no fake heartbeat, no fabricated zeros
        "providers": providers,
        "cases": cases,
        "summary": {
            "catalog_products": len(providers),
            "onboarding_cases": len(cases),
            "actions_needing_review": sum(c["state"] in {
                "DISCOVERED", "RIGHTS_REVIEW", "CONFIGURATION_PENDING",
                "VERIFICATION_PENDING", "OWNER_APPROVAL", "HOLD",
            } for c in cases),
            "live_feeds_verified": None,
            "api_requests_remaining": None,
            "live_option_feeds_verified": None,
        },
        "traffic": {"state": "NOT_CONNECTED", "verified_usage": None,
                    "provider_quotas": None, "streams": None},
        "soulaana": {
            "headline": "Our connection catalog is available; no live feed is verified here.",
            "meaning": "Configured source mappings are not proof of authorized, current market prices.",
            "needs_owner": "Complete provider rights review and independent transport verification.",
            "next_step": "Use the provider cards to inspect scope; activate only through Tower-approved backend receipts.",
        },
        "safety": {"can_approve_in_browser": False, "can_execute": False,
                   "manual_live_unlocked": False, "invitee_prices_visible": False},
    }
