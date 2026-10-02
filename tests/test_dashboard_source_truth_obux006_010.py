# Historical OBUX006–020 checks inspect the exact archived V16 design.
# Active Dashboard uses separate modern product and security assertions.
from pathlib import Path


DASHBOARD = Path(
    "docs/historical/obux_v16_dashboard.js"
).read_text(
    encoding="utf-8"
)


def test_dashboard_does_not_consume_route_sample_signals():

    assert (
        "sample_signals"
        not in DASHBOARD
    )


def test_dashboard_prefers_existing_dashboard_contract():

    assert (
        "OB_DATA_CONTRACTS_V22"
        in DASHBOARD
    )

    assert (
        "dashboardContract"
        in DASHBOARD
    )


def test_dashboard_does_not_submit_or_execute():

    forbidden = (
        "placeOrder(",
        "submitOrder(",
        "broker.submit",
        "executeTrade(",
        "execute_order(",
    )

    for item in forbidden:
        assert item not in DASHBOARD
