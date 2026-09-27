"""GRD067: owner-only, minimal Grounds status envelope for future Clouds review.

No message transport, public endpoint, subscription, or real Clouds integration.
This is a source-only aggregate of Grounds physical operations without resident
identifiers, job descriptions, private documents, invoices, bank data or OB.
Tower must separately certify identity and the inter-system receiver.
"""
from __future__ import annotations

from .access import TowerScope
from .operations import GroundsOperations


def owner_operating_snapshot(actor:TowerScope,operations:GroundsOperations,*,
                             property_ref:str)->dict:
    if not isinstance(operations,GroundsOperations):
        raise TypeError("GroundsOperations required")
    actor=operations._scope(actor)
    actor.require_role("owner")
    actor.require_property(property_ref)
    pulse=operations.property_pulse(actor,property_ref=property_ref)
    return {
        "source":"grounds","intended_audience":"clouds",
        "mode":"local_aggregate_not_published",
        "property_ref":property_ref,
        "observed_at":pulse["source_observed_at"],
        "counts":{
            "units":pulse["units"],
            "occupied_units":pulse["occupied_units"],
            "open_work_orders":pulse["open_work_orders"],
            "untriaged_urgent_work":pulse["untriaged_urgent_work"],
            "open_turnovers":pulse["open_turnovers"],
            "unresolved_serious_inspection_findings":
                pulse["unresolved_serious_inspection_findings"],
        },
        "resident_identity_included":False,
        "job_description_included":False,
        "raw_vault_evidence_included":False,
        "rent_collections":None,
        "available_capital":None,
        "publisher_enabled":False,
        "identity_receiver_certified":False,
        "money_movement_enabled":False,
    }
