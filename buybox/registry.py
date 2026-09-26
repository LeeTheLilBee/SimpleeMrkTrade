"""Versioned vertical manifests. A vertical adds knowledge; it never rewrites core.

The manifests define the same contract for all asset classes. Missing specialized
calculators are explicitly unavailable, not silently borrowed from another type.
"""
from copy import deepcopy

REGISTRY_VERSION = "1.0.0"

def manifest(label, icon, evidence, metrics, filters, shocks, handoff, location_mode,
             fields=(), calculations=()):
    return {
        "version": "1.0.0", "label": label, "icon": icon,
        "evidence": [{"kind": kind, "weight": weight, "critical": critical}
                     for kind, weight, critical in evidence],
        "metrics": list(metrics), "filters": list(filters),
        "shocks": list(shocks), "handoff": handoff,
        "location_mode": location_mode, "fields": list(fields),
        "calculations": list(calculations),
        "rooms": ["discover", "explore", "opportunity", "compare", "scenario",
                  "deal_room", "decision", "closing", "outcomes"],
        "decision_authority": "tower", "money_and_capacity_source": "teller",
        "explanation_layer": "soulaana",
    }

VERTICALS = {
    "atm": manifest(
        "ATM Routes & Businesses", "banknote",
        [("processor_statements", 5, True), ("machine_inventory", 5, True),
         ("ownership_documents", 5, True), ("location_agreements", 5, True),
         ("expense_records", 5, True), ("vault_records", 4, True),
         ("settlement_records", 3, False), ("maintenance_records", 2, False),
         ("lien_review", 3, True), ("transition_agreement", 2, False)],
        ["machine_count", "seller_owned_count", "verified_annual_net",
         "annual_revenue", "annual_expenses", "vault_requirement",
         "largest_location_share", "route_miles", "purchase_multiple"],
        ["price", "market", "machine_count", "seller_owned", "annual_net",
         "vault_requirement", "route_radius", "processor", "contract_term"],
        ["volume_minus_15", "volume_minus_25", "largest_location_lost",
         "maintenance_double", "vault_plus_25"], "simplee_on_the_go", "route",
        ["machine_inventory", "machine_placements", "route", "provider",
         "vault_profile", "contracts", "seller_transition"],
        ["normalized_cashflow", "purchase_multiple", "vault_liquidity",
         "route_coverage", "cash_on_cash"]),
    "multifamily": manifest(
        "Multifamily", "building-2",
        [("rent_roll", 5, True), ("t12", 5, True), ("leases", 4, True),
         ("insurance_quote", 4, True), ("tax_estimate", 4, True),
         ("condition_report", 5, True), ("title_review", 5, True),
         ("capex_plan", 4, True)],
        ["units", "buildings", "occupancy", "noi", "cap_rate", "dscr",
         "price_per_unit", "capex_required"],
        ["price", "market", "units", "occupancy", "noi", "condition"],
        ["occupancy_minus_10", "insurance_plus_35", "capex_plus_50",
         "tax_reassessment", "rate_plus_200bp"], "grounds", "property",
        ["buildings", "units", "leases", "utility_structure", "condition"],
        ["noi", "dscr", "cap_rate", "debt_yield", "capex"]),
    "commercial": manifest(
        "Commercial Property", "warehouse",
        [("leases", 5, True), ("operating_statements", 5, True),
         ("title_review", 5, True), ("condition_report", 5, True),
         ("insurance_quote", 3, True), ("tax_estimate", 3, True)],
        ["noi", "occupancy", "lease_term", "tenant_concentration", "dscr"],
        ["price", "market", "property_type", "noi", "occupancy"],
        ["tenant_loss", "vacancy_increase", "capex_plus_50", "rate_plus_200bp"],
        "grounds", "property", ["tenants", "lease_schedule", "building_use"],
        ["noi", "dscr", "tenant_concentration"]),
    "laundromat": manifest(
        "Laundromats", "washing-machine",
        [("sales_records", 5, True), ("utility_bills", 5, True),
         ("equipment_inventory", 5, True), ("lease", 5, True),
         ("expense_records", 5, True), ("maintenance_records", 3, True)],
        ["machine_count", "turns_per_day", "utility_cost", "annual_net",
         "equipment_replacement"],
        ["price", "market", "annual_net", "machine_count", "lease_term"],
        ["utility_plus_25", "sales_minus_20", "equipment_replacement"],
        "luxe_laundromat", "property", ["washers", "dryers", "lease", "utilities"],
        ["normalized_cashflow", "turns", "replacement_exposure"]),
    "land_farm": manifest(
        "Land & Farms", "sprout",
        [("deed", 5, True), ("survey", 5, True), ("zoning", 5, True),
         ("water_rights", 5, True), ("access_evidence", 5, True),
         ("soil_environmental", 4, True)],
        ["acreage", "usable_acres", "water_capacity", "price_per_acre",
         "development_cost"],
        ["price", "market", "acreage", "water", "zoning", "access"],
        ["water_unavailable", "access_loss", "development_cost_plus_50"],
        "simplee_farming", "parcels", ["parcels", "water", "soil", "access", "zoning"],
        ["price_per_usable_acre", "development_funding"]),
    "business": manifest(
        "Operating Businesses", "briefcase-business",
        [("financial_statements", 5, True), ("tax_records", 5, True),
         ("bank_reconciliation", 5, True), ("contracts", 4, True),
         ("ownership_structure", 5, True), ("employee_obligations", 4, True)],
        ["revenue", "normalized_earnings", "customer_concentration",
         "working_capital", "debt"],
        ["price", "market", "industry", "normalized_earnings", "employees"],
        ["revenue_minus_20", "top_customer_lost", "working_capital_plus_25"],
        "assigned_operating_company", "multi", ["entity", "customers", "employees"],
        ["normalized_earnings", "purchase_multiple", "working_capital"]),
    "equipment": manifest(
        "Equipment & Infrastructure", "cpu",
        [("asset_schedule", 5, True), ("ownership_documents", 5, True),
         ("condition_report", 5, True), ("cost_quote", 4, True),
         ("service_history", 3, True)],
        ["units", "replacement_cost", "remaining_life", "operating_cost"],
        ["price", "market", "equipment_type", "condition"],
        ["maintenance_double", "replacement_early", "delivery_delay"],
        "assigned_operating_company", "multi", ["assets", "warranties", "service"],
        ["lifecycle_cost", "replacement_exposure"]),
}

def get_vertical(vertical_id):
    if vertical_id not in VERTICALS:
        raise ValueError("Unregistered acquisition vertical: " + str(vertical_id))
    return deepcopy(VERTICALS[vertical_id])

def validate_registry():
    mandatory = {"version", "label", "icon", "evidence", "metrics", "filters",
                 "shocks", "handoff", "location_mode", "fields", "calculations",
                 "rooms", "decision_authority", "money_and_capacity_source",
                 "explanation_layer"}
    for key, vertical in VERTICALS.items():
        assert mandatory <= set(vertical), key
        assert vertical["money_and_capacity_source"] == "teller", key
        assert vertical["decision_authority"] == "tower", key
        names = [e["kind"] for e in vertical["evidence"]]
        assert len(names) == len(set(names)), key
        assert all(e["weight"] > 0 for e in vertical["evidence"]), key
    return True
