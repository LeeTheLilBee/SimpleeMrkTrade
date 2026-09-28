"""Focus snapshot from only actual persisted BuyBox opportunities and events."""
from datetime import date
from .dealroom import current_tasks

def build_focus(opportunities, activity_reader, *, as_of=None):
    today=as_of or date.today()
    if isinstance(today,str):
        today=date.fromisoformat(today)
    queue=[]
    changes=[]
    for op in opportunities:
        for item in current_tasks(op):
            if item["status"] not in ("OPEN","WAITING"):
                continue
            due=date.fromisoformat(item["due_date"])
            priority="OVERDUE" if due<today else "DUE_TODAY" if due==today else "UPCOMING"
            queue.append({"opportunity_id":op["id"],"opportunity_name":op["name"],
                          "title":item["title"],"due_date":item["due_date"],
                          "status":item["status"],"priority":priority,"task_id":item["id"]})
        for event in activity_reader(op["id"])[-3:]:
            if event["event_type"] not in (
                "MaterialChangeInvalidated","NegotiationHistoryRecorded",
                "OriginalDocumentReceived","EvidenceReviewed","MetricRecorded",
                "SourceAttached","ATMMachineRecorded","DealTaskCreated",
                "DealTaskStatusChanged",
                "SourceClaimRecorded", "SourceClaimDocumentReviewed",
                "DiligenceEvidenceTaskCreated",
                "OwnerFinancialStressRecorded","FinancingOptionRecorded","InsuranceDocumentRecorded","ComparableSourceRecorded","OwnerResearchDispositionRecorded","ClosingReviewRecorded","OwnerOfferScenarioRecorded",
            ):
                continue
            changes.append({"opportunity_id":op["id"],"opportunity_name":op["name"],
                            "event_type":event["event_type"],"occurred_at":event["occurred_at"]})
    priority_order={"OVERDUE":0,"DUE_TODAY":1,"UPCOMING":2}
    queue.sort(key=lambda x:(priority_order[x["priority"]],x["due_date"],x["title"]))
    changes.sort(key=lambda x:x["occurred_at"],reverse=True)
    return {"as_of":today.isoformat(),"tasks":queue,"changes":changes[:15],
            "total_opportunities":len(opportunities),
            "needs_attention":sum(x["priority"] in ("OVERDUE","DUE_TODAY") for x in queue)}
