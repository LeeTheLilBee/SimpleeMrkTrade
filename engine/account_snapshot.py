from __future__ import annotations

"""
🔭 Observatory Account Snapshot

This is the display-friendly account view.

Canonical source:
- portfolio_summary() for cash, equity, open market value, official PnL,
  and performance filtering.
- strategy_performance only as a fallback if portfolio_summary is missing
  nested performance fields.

Compatibility preserved:
- account_snapshot()
- get_account_snapshot()
- build_account_snapshot()
- print_account_snapshot()
"""

from typing import Any, Dict, List

from engine.portfolio_summary import portfolio_summary


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None or isinstance(value, bool):
            return float(default)
        if isinstance(value, str):
            cleaned = value.replace("$", "").replace(",", "").strip()
            if cleaned == "":
                return float(default)
            value = cleaned
        return float(value)
    except Exception:
        return float(default)


def _safe_int(value: Any, default: int = 0) -> int:
    try:
        if value is None or isinstance(value, bool):
            return int(default)
        if isinstance(value, str):
            cleaned = value.replace(",", "").strip()
            if cleaned == "":
                return int(default)
            value = cleaned
        return int(float(value))
    except Exception:
        return int(default)


def _safe_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _first_present(payload: Dict[str, Any], keys: List[str], default: Any = None) -> Any:
    payload = _safe_dict(payload)

    for key in keys:
        if key in payload and payload.get(key) not in (None, ""):
            return payload.get(key)

    return default


def _strategy_performance_fallback() -> Dict[str, Any]:
    try:
        from engine.strategy_performance import strategy_performance_summary

        payload = strategy_performance_summary(include_excluded=False)
        return payload if isinstance(payload, dict) else {}
    except Exception:
        return {}


def _classifications_from_portfolio_or_performance(
    portfolio: Dict[str, Any],
    performance: Dict[str, Any],
) -> Dict[str, Any]:
    direct = _safe_dict(
        _first_present(
            portfolio,
            [
                "realized_pnl_classifications",
                "realized_classifications",
                "performance_classifications",
            ],
            {},
        )
    )

    if direct:
        return direct

    detail = _safe_dict(portfolio.get("realized_pnl_detail"))
    classification_pnl = _safe_dict(detail.get("classification_pnl"))
    classification_rows = _safe_dict(detail.get("classification_rows"))

    if classification_pnl:
        return {
            label: {
                "rows": _safe_int(classification_rows.get(label), 0),
                "trades": _safe_int(classification_rows.get(label), 0),
                "pnl": round(_safe_float(pnl, 0.0), 2),
            }
            for label, pnl in sorted(classification_pnl.items())
        }

    performance_classifications = _safe_dict(performance.get("classifications"))
    if performance_classifications:
        return performance_classifications

    return {}


def account_snapshot() -> Dict[str, Any]:
    portfolio = portfolio_summary()
    performance = _strategy_performance_fallback()

    realized_detail = _safe_dict(portfolio.get("realized_pnl_detail"))
    performance_source = _safe_dict(performance.get("source"))
    performance_summary = _safe_dict(performance.get("summary"))

    cash = round(_safe_float(portfolio.get("cash"), 0.0), 2)
    buying_power = round(_safe_float(portfolio.get("buying_power"), cash), 2)
    equity = round(_safe_float(portfolio.get("equity"), 0.0), 2)

    estimated_account_value = round(
        _safe_float(portfolio.get("estimated_account_value"), equity),
        2,
    )

    official_realized_pnl = round(
        _safe_float(
            _first_present(
                portfolio,
                [
                    "realized_pnl",
                    "official_realized_pnl",
                    "filtered_realized_pnl",
                ],
                realized_detail.get(
                    "official_realized_pnl",
                    performance_summary.get("pnl", 0.0),
                ),
            ),
            0.0,
        ),
        2,
    )

    unrealized_pnl = round(_safe_float(portfolio.get("unrealized_pnl"), 0.0), 2)

    realized_pnl_all_closed_records = round(
        _safe_float(
            _first_present(
                portfolio,
                [
                    "realized_pnl_all_closed_records",
                    "all_closed_records_pnl",
                    "realized_pnl_all_records",
                    "realized_pnl_unfiltered",
                ],
                realized_detail.get(
                    "raw_realized_pnl_all_closed_records",
                    official_realized_pnl,
                ),
            ),
            official_realized_pnl,
        ),
        2,
    )

    excluded_realized_pnl = round(
        _safe_float(
            _first_present(
                portfolio,
                [
                    "excluded_realized_pnl",
                    "realized_pnl_excluded",
                    "excluded_pnl",
                    "under_review_realized_pnl",
                ],
                realized_detail.get(
                    "excluded_realized_pnl",
                    realized_pnl_all_closed_records - official_realized_pnl,
                ),
            ),
            0.0,
        ),
        2,
    )

    official_closed_rows_used = _safe_int(
        _first_present(
            portfolio,
            [
                "official_closed_rows_used",
                "official_closed_rows",
                "closed_rows_used",
                "rows_used",
                "performance_rows_used",
            ],
            realized_detail.get(
                "official_rows_used",
                performance_source.get("rows_used", 0),
            ),
        ),
        0,
    )

    rows_excluded_from_performance = _safe_int(
        _first_present(
            portfolio,
            [
                "rows_excluded_from_performance",
                "closed_rows_excluded_from_performance",
                "rows_excluded",
                "excluded_rows_count",
                "performance_rows_excluded",
            ],
            realized_detail.get(
                "rows_excluded_from_performance",
                performance_source.get("rows_excluded_from_performance", 0),
            ),
        ),
        0,
    )

    realized_pnl_source = _first_present(
        portfolio,
        [
            "realized_pnl_source",
            "realized_source",
            "pnl_source",
            "performance_source",
        ],
        realized_detail.get(
            "realized_pnl_source",
            "strategy_performance_filtered" if performance else "portfolio_summary",
        ),
    )

    realized_classifications = _classifications_from_portfolio_or_performance(
        portfolio,
        performance,
    )

    net_official_pnl = round(official_realized_pnl + unrealized_pnl, 2)
    net_audit_pnl = round(realized_pnl_all_closed_records + unrealized_pnl, 2)

    account_math = _safe_dict(portfolio.get("account_math"))

    return {
        "cash": cash,
        "buying_power": buying_power,
        "equity": equity,
        "open_positions": _safe_int(portfolio.get("open_positions"), 0),
        "estimated_account_value": estimated_account_value,

        "realized_pnl": official_realized_pnl,
        "official_realized_pnl": official_realized_pnl,
        "realized_pnl_all_closed_records": realized_pnl_all_closed_records,
        "excluded_realized_pnl": excluded_realized_pnl,
        "unrealized_pnl": unrealized_pnl,
        "net_official_pnl": net_official_pnl,
        "net_audit_pnl": net_audit_pnl,

        "gross_capital_open": round(_safe_float(portfolio.get("gross_capital_open"), 0.0), 2),
        "total_market_value_open": round(_safe_float(portfolio.get("total_market_value_open"), 0.0), 2),
        "calculated_equity": round(_safe_float(portfolio.get("calculated_equity"), equity), 2),

        "official_closed_rows_used": official_closed_rows_used,
        "rows_excluded_from_performance": rows_excluded_from_performance,
        "realized_pnl_source": realized_pnl_source,
        "realized_pnl_classifications": realized_classifications,

        "vehicle_mix": portfolio.get("vehicle_mix", {}),
        "option_safety": portfolio.get("option_safety", {}),
        "account_math": account_math,

        "stale_account_state_warning": bool(account_math.get("stale_account_state_warning", False)),
        "double_count_warning": bool(account_math.get("double_count_warning", False)),
        "account_state_equity_gap": round(_safe_float(account_math.get("account_state_equity_gap"), 0.0), 2),
        "account_state_estimated_gap": round(_safe_float(account_math.get("account_state_estimated_gap"), 0.0), 2),
    }


def get_account_snapshot() -> Dict[str, Any]:
    return account_snapshot()


def build_account_snapshot() -> Dict[str, Any]:
    return account_snapshot()


def print_account_snapshot() -> None:
    snap = account_snapshot()

    print("ACCOUNT SNAPSHOT")
    print(f"Cash: {snap.get('cash')}")
    print(f"Buying Power: {snap.get('buying_power')}")
    print(f"Equity: {snap.get('equity')}")
    print(f"Open Positions: {snap.get('open_positions')}")
    print(f"Estimated Account Value: {snap.get('estimated_account_value')}")
    print()
    print("PNL VIEW")
    print(f"Official Realized PnL: {snap.get('official_realized_pnl')}")
    print(f"All Closed Records PnL: {snap.get('realized_pnl_all_closed_records')}")
    print(f"Excluded / Under Review PnL: {snap.get('excluded_realized_pnl')}")
    print(f"Unrealized PnL: {snap.get('unrealized_pnl')}")
    print(f"Net Official PnL: {snap.get('net_official_pnl')}")
    print(f"Net Audit PnL: {snap.get('net_audit_pnl')}")
    print()
    print("PERFORMANCE FILTERING")
    print(f"Official Closed Rows Used: {snap.get('official_closed_rows_used')}")
    print(f"Rows Excluded From Performance: {snap.get('rows_excluded_from_performance')}")
    print(f"Realized PnL Source: {snap.get('realized_pnl_source')}")

    account_math = _safe_dict(snap.get("account_math"))
    print()
    print("ACCOUNT MATH")
    print(f"Calculated Equity: {snap.get('calculated_equity')}")
    print(f"Stale Account State Warning: {snap.get('stale_account_state_warning')}")
    print(f"Double Count Warning: {snap.get('double_count_warning')}")
    print(f"Account State Equity Gap: {snap.get('account_state_equity_gap')}")
    print(f"Account State Estimated Gap: {snap.get('account_state_estimated_gap')}")
    print(f"Equity Source: {account_math.get('equity_source')}")
    print(f"Formula: {account_math.get('estimated_value_formula')}")

    classifications = _safe_dict(snap.get("realized_pnl_classifications", {}))
    if classifications:
        print()
        print("REALIZED PNL CLASSIFICATIONS")
        for label, row in sorted(classifications.items()):
            row = _safe_dict(row)
            print(
                f"{label}: rows={row.get('trades', row.get('rows', 0))} "
                f"pnl={row.get('pnl', 0.0)}"
            )


__all__ = [
    "account_snapshot",
    "get_account_snapshot",
    "build_account_snapshot",
    "print_account_snapshot",
]
