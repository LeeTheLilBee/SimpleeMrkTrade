"""Universal acquisition coordination records. Never sends contracts or money."""
from __future__ import annotations
from copy import deepcopy
from datetime import date
from decimal import Decimal
from uuid import uuid4
from .core import now, money
from .workflow import invalidate_on_change

TASK_STATES = frozenset({"OPEN","WAITING","COMPLETE","CANCELED"})
NEGOTIATION_KINDS = frozenset({
    "SELLER_COMMUNICATION", "ASKING_PRICE_CHANGED", "OFFER_DOCUMENTED",
    "COUNTER_DOCUMENTED", "CONCESSION_DOCUMENTED", "TERM_DOCUMENTED",
    "AGREEMENT_REFERENCE",
})

def new_task(op, *, title, due_date, owner="local_owner", source_reference=None, notes=""):
    if not isinstance(title,str) or not title.strip() or len(title)>180:
        raise ValueError("INVALID_TASK_TITLE")
    if not isinstance(due_date,str):
        raise ValueError("INVALID_TASK_DUE_DATE")
    try:
        date.fromisoformat(due_date)
    except ValueError:
        raise ValueError("INVALID_TASK_DUE_DATE") from None
    if not owner or len(str(notes))>1000:
        raise ValueError("INVALID_TASK_INPUT")
    revised=deepcopy(op)
    task={"id":str(uuid4()),"title":title.strip(),"due_date":due_date,"owner":owner,
          "notes":str(notes).strip(),"source_reference":source_reference,
          "status":"OPEN","recorded_at":now(),"supersedes":None}
    revised.setdefault("tasks",[]).append(task)
    return revised,task

def update_task(op, *, task_id, status, notes=""):
    if status not in TASK_STATES or not isinstance(notes,str) or len(notes)>1000:
        raise ValueError("INVALID_TASK_CHANGE")
    revised=deepcopy(op)
    original=next((task for task in revised.get("tasks",[]) if task["id"]==task_id),None)
    if original is None:
        raise ValueError("UNKNOWN_TASK")
    if original["status"] in ("COMPLETE","CANCELED"):
        raise ValueError("TASK_FINAL")
    original["superseded_at"]=now()
    newer={**original,"id":str(uuid4()),"status":status,
           "notes":notes.strip() or original.get("notes",""),
           "recorded_at":now(),"supersedes":task_id}
    newer.pop("superseded_at",None)
    revised["tasks"].append(newer)
    return revised,newer

def record_negotiation(op, *, kind, description, source_reference,
                       amount=None, occurred_on=None):
    if kind not in NEGOTIATION_KINDS:
        raise ValueError("INVALID_NEGOTIATION_KIND")
    if not isinstance(description,str) or not 0<len(description.strip())<=1500:
        raise ValueError("NEGOTIATION_DESCRIPTION_REQUIRED")
    if not isinstance(source_reference,str) or not source_reference.strip():
        raise ValueError("NEGOTIATION_PROVENANCE_REQUIRED")
    if occurred_on is None:
        occurred_on=date.today().isoformat()
    try: date.fromisoformat(occurred_on)
    except (TypeError,ValueError):
        raise ValueError("INVALID_EVENT_DATE") from None
    value=money(amount) if amount not in ("",None) else None
    if amount not in ("",None) and (value is None or value<0):
        raise ValueError("INVALID_NEGOTIATION_AMOUNT")
    if kind=="ASKING_PRICE_CHANGED" and value is None:
        raise ValueError("NEW_ASKING_PRICE_REQUIRED")
    revised=deepcopy(op)
    event={"id":str(uuid4()),"kind":kind,"description":description.strip(),
           "source_reference":source_reference.strip(),"amount":str(value) if value is not None else None,
           "occurred_on":occurred_on,"recorded_at":now(),"actor":"local_owner",
           "record_type":"OWNER_RECORDED_EXTERNAL_EVENT","transmitted_by_buybox":False}
    revised.setdefault("negotiations",[]).append(event)
    if kind=="ASKING_PRICE_CHANGED":
        previous=revised.get("asking_price")
        event["previous_asking_price"]=previous
        revised["asking_price"]=str(value.quantize(Decimal("0.01")))
    if kind in ("ASKING_PRICE_CHANGED","OFFER_DOCUMENTED","COUNTER_DOCUMENTED",
                "CONCESSION_DOCUMENTED","TERM_DOCUMENTED"):
        changed=["negotiations"]
        if kind=="ASKING_PRICE_CHANGED":
            changed.append("asking_price")
        revised=invalidate_on_change(revised,changed_fields=changed,
            reason="Material acquisition terms were recorded from an identified source",
            source_reference=source_reference)
    return revised,event

def current_tasks(op):
    superseded={task.get("supersedes") for task in op.get("tasks",[]) if task.get("supersedes")}
    return sorted((task for task in op.get("tasks",[]) if task["id"] not in superseded),
                  key=lambda task:(task["status"] in ("COMPLETE","CANCELED"),task["due_date"]))
