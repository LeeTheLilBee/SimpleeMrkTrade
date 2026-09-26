"""Real, owner-recorded ATM inventory. Ownership claims are never proof by themselves."""
from copy import deepcopy
from uuid import uuid4
from .core import now
from .workflow import invalidate_on_change

OWNERSHIP_TYPES=frozenset({"CLAIMED_SELLER_OWNED","THIRD_PARTY","UNKNOWN"})

def register_machine(op, *, serial_number, model="", location_name="",
                     ownership="UNKNOWN", evidence_id=None, source_reference=None):
    if op.get("vertical")!="atm":
        raise ValueError("ATM_VERTICAL_REQUIRED")
    serial=str(serial_number).strip()
    if not serial or len(serial)>120:
        raise ValueError("SERIAL_REQUIRED")
    if ownership not in OWNERSHIP_TYPES:
        raise ValueError("INVALID_OWNERSHIP_CLAIM")
    if not str(source_reference or "").strip():
        raise ValueError("MACHINE_SOURCE_REQUIRED")
    inventory=op.get("vertical_data",{}).get("machine_inventory",[])
    if any(str(m.get("id","")).casefold()==serial.casefold() for m in inventory):
        raise ValueError("DUPLICATE_MACHINE_SERIAL")
    if ownership=="CLAIMED_SELLER_OWNED" and evidence_id:
        supported=next((e for e in op.get("evidence",[])
           if e.get("id")==evidence_id and e.get("kind")=="ownership_documents"
           and e.get("status") in ("DOCUMENT_SUPPORTED","THIRD_PARTY_VERIFIED")),None)
        if not supported:
            raise ValueError("OWNERSHIP_EVIDENCE_NOT_REVIEWED")
    revised=deepcopy(op)
    record={"record_id":str(uuid4()),"id":serial,"serial_number":serial,
            "model":str(model).strip()[:160],
            "location_name":str(location_name).strip()[:160],
            "included":True,"source_reference":source_reference,
            "ownership":"SELLER_OWNED" if ownership=="CLAIMED_SELLER_OWNED" and evidence_id
                else ownership,
            "ownership_evidence_id":evidence_id if ownership=="CLAIMED_SELLER_OWNED" else None,
            "recorded_at":now(),"recorded_by":"local_owner",
            "title_and_lien_clearance":"UNVERIFIED"}
    revised.setdefault("vertical_data",{}).setdefault("machine_inventory",[]).append(record)
    revised=invalidate_on_change(revised,changed_fields=["machine_inventory"],
          reason="ATM asset inventory changed",source_reference=source_reference)
    return revised,record
