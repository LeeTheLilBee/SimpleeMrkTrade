"""BBX107-130 deterministic Intelligence Studio projections.

Everything here derives from persisted BuyBox records and owner-authored
research. No external market fact, capital availability, legal conclusion,
seller truth, or operational authority is invented.
"""
from __future__ import annotations
from collections import Counter,defaultdict
from datetime import date,datetime
from decimal import Decimal
from hashlib import sha256
import json

from .core import evaluate,money,scenario_calculation
from .dealroom import current_tasks
from .financing import financing_snapshot
from .external_proof_gate import integration_readiness

PLAYBOOKS={
 "atm":["Verify serial-numbered machine inventory","Reconcile processor statements","Confirm location agreements","Verify ownership/lien transfer","Model vault and replenishment liquidity","Confirm service/connectivity obligations"],
 "multifamily":["Verify rent roll and leases","Inspect units/building systems","Review taxes/insurance","Model CapEx and reserves","Verify title/zoning","Prepare Grounds transition"],
 "commercial":["Verify leases/NOI","Inspect structure/systems","Review zoning/environmental","Model tenant concentration","Verify title/insurance"],
 "laundromat":["Verify machine inventory/age","Review utility history","Verify lease or real estate rights","Inspect plumbing/electrical","Model repair/replacement reserve"],
 "land_farm":["Verify title/survey/access","Review zoning/water/soil/environmental evidence","Model carrying/improvement costs","Confirm intended-use constraints"],
 "business":["Verify financial statements/tax support","Review contracts/customer concentration","Inspect liabilities/assets","Model working capital","Plan transition"],
 "equipment":["Verify serial/title/ownership","Inspect condition/maintenance","Compare replacement value","Model transport/install/repair costs"],
}

def owner_thesis_fit(op,thesis):
    text=" ".join([op.get("vertical",""),op.get("name",""),
      op.get("location",{}).get("city",""),op.get("location",{}).get("region","")]).lower()
    hits=[x for x in thesis.get("priorities",[]) if x.lower() in text]
    region_hits=[x for x in thesis.get("preferred_regions",[]) if x.lower() in text]
    avoids=[x for x in thesis.get("avoid",[]) if x.lower() in text]
    return {"priority_matches":hits,"region_matches":region_hits,"avoid_matches":avoids,
            "alignment":"CONFLICT" if avoids else "ALIGNED" if hits or region_hits else "UNSPECIFIED",
            "is_recommendation":False}

def command_map(opportunities):
    clusters=defaultdict(list)
    for op in opportunities:
        loc=op.get("location",{})
        key=(loc.get("city") or "Unknown city",loc.get("region") or "Unknown region")
        clusters[key].append(op)
    return [{"city":k[0],"region":k[1],"count":len(v),
             "verticals":dict(Counter(x["vertical"] for x in v)),
             "opportunity_ids":[x["id"] for x in v]} for k,v in sorted(clusters.items())]

def portfolio_fit(op,opportunities,thesis):
    same_vertical=sum(x["vertical"]==op["vertical"] and x["id"]!=op["id"] for x in opportunities)
    same_region=sum(x.get("location",{}).get("region") and
                    x.get("location",{}).get("region")==op.get("location",{}).get("region") and x["id"]!=op["id"]
                    for x in opportunities)
    return {"thesis":owner_thesis_fit(op,thesis),"same_vertical_pipeline":same_vertical,
            "same_region_pipeline":same_region,"portfolio_authority":"ANALYTICAL_ONLY"}

def acquisition_timeline(op,records):
    events=[]
    for task in current_tasks(op):
        events.append({"date":task["due_date"],"kind":"TASK","label":task["title"],"state":task["status"]})
    for q in financing_snapshot(op)["options"]:
        if q["quote"].get("expiration_date"):
            events.append({"date":q["quote"]["expiration_date"],"kind":"FINANCING_EXPIRY",
                           "label":q["quote"]["lender_label"],"state":"SOURCE_RECORDED"})
    for r in records:
        p=r["payload"]
        when=p.get("date") or p.get("due_date") or p.get("observed_on")
        if when: events.append({"date":when,"kind":r["kind"],"label":p.get("title") or p.get("name") or r["kind"],"state":"OWNER_RECORDED"})
    return sorted(events,key=lambda x:x["date"])

def negotiation_intelligence(op):
    rows=op.get("negotiations",[])
    amounts=[]
    for r in rows:
        x=money(r.get("amount"))
        if x is not None: amounts.append(x)
    return {"event_count":len(rows),"amount_events":[str(x) for x in amounts],
            "latest":rows[-1] if rows else None,"seller_behavior_inferred":False}

def deal_dna(op,opportunities):
    target=evaluate(op)
    matches=[]
    for other in opportunities:
        if other["id"]==op["id"]: continue
        score=0; reasons=[]
        if other["vertical"]==op["vertical"]: score+=2; reasons.append("same vertical")
        if other.get("location",{}).get("region") and other.get("location",{}).get("region")==op.get("location",{}).get("region"):
            score+=1; reasons.append("same region")
        if evaluate(other)["judgment"]==target["judgment"]: score+=1; reasons.append("same analytical judgment")
        if score: matches.append({"id":other["id"],"name":other["name"],"similarity_points":score,"reasons":reasons})
    return sorted(matches,key=lambda x:(-x["similarity_points"],x["name"]))[:6]

def predicted_vs_actual(op,records):
    predicted=scenario_calculation(op)
    actuals=[r for r in records if r["kind"]=="PERFORMANCE_ACTUAL"]
    latest=actuals[0]["payload"] if actuals else None
    variance=None
    if latest and predicted.get("net") is not None:
        a=money(latest.get("actual_net"))
        p=money(predicted.get("net"))
        if a is not None and p is not None: variance=str((a-p).quantize(Decimal("0.01")))
    return {"predicted":predicted,"latest_actual":latest,"net_variance":variance,
            "learning_state":"ACTUAL_AVAILABLE" if latest else "NO_POST_CLOSE_ACTUAL_YET"}

def lender_library(opportunities):
    lenders=defaultdict(lambda:{"options":0,"verticals":set(),"programs":set()})
    for op in opportunities:
        for q in financing_snapshot(op)["options"]:
            rec=q["quote"]; name=rec["lender_label"]; lenders[name]["options"]+=1
            lenders[name]["verticals"].add(op["vertical"]); lenders[name]["programs"].add(rec["program_label"])
    return [{"lender":k,"recorded_options":v["options"],"verticals":sorted(v["verticals"]),
             "programs":sorted(v["programs"]),"current_availability_claimed":False} for k,v in sorted(lenders.items())]

def acquisition_calendar(opportunities,record_lookup):
    items=[]
    for op in opportunities:
        for x in acquisition_timeline(op,record_lookup(op["id"])):
            items.append({**x,"opportunity_id":op["id"],"opportunity_name":op["name"]})
    return sorted(items,key=lambda x:x["date"])[:100]

def ic_packet(op,records,thesis):
    analysis=evaluate(op)
    return {"opportunity":{k:op.get(k) for k in ("id","name","vertical","asking_price","location","lifecycle")},
            "analysis":analysis,"portfolio_fit":portfolio_fit(op,[op],thesis),
            "timeline":acquisition_timeline(op,records),
            "why_not":why_not(op,records),"integration":integration_readiness(op),
            "authority":"OWNER_RESEARCH_PACKET_ONLY"}

def why_not(op,records):
    a=evaluate(op); questions=[]
    for f in a["findings"][:8]: questions.append("What evidence would resolve or worsen: "+f["reason"])
    for x in [r for r in records if r["kind"]=="CAPEX_ITEM"][:5]:
        questions.append("What could make the recorded repair item '"+x["payload"].get("title","repair")+"' cost more or take longer?")
    if not questions: questions=["What assumption would most damage the economics if it proved wrong?",
      "What source would most change the current view of this deal?"]
    return questions

def impact_summary(records):
    rows=[r["payload"] for r in records if r["kind"]=="COMMUNITY_IMPACT"]
    return {"entries":rows,"dimensions":dict(Counter(x.get("dimension","unspecified") for x in rows)),
            "financial_score_affected":False}

def deal_story(op,events,records):
    story=[{"at":x["occurred_at"],"kind":x["event_type"],"detail":"BuyBox event"} for x in events]
    story += [{"at":x["created_at"],"kind":x["kind"],"detail":x["payload"].get("title") or x["payload"].get("note") or x["kind"]} for x in records]
    return sorted(story,key=lambda x:x["at"])

def knowledge_graph(op,records):
    nodes={op["id"]:{"id":op["id"],"type":"opportunity","label":op["name"]}}; edges=[]
    for r in records:
        if r["kind"]=="COUNTERPARTY":
            name=r["payload"].get("name")
            if name:
                nid="counterparty:"+sha256(name.lower().encode()).hexdigest()[:12]
                nodes[nid]={"id":nid,"type":"counterparty","label":name}
                edges.append({"from":op["id"],"to":nid,"relationship":r["payload"].get("role","counterparty")})
    for q in financing_snapshot(op)["options"]:
        name=q["quote"]["lender_label"]; nid="lender:"+sha256(name.lower().encode()).hexdigest()[:12]
        nodes[nid]={"id":nid,"type":"lender","label":name}; edges.append({"from":op["id"],"to":nid,"relationship":"financing_source"})
    return {"nodes":list(nodes.values()),"edges":edges}

def geo_expansion(opportunities):
    groups=defaultdict(lambda:{"opportunities":0,"verticals":Counter()})
    for op in opportunities:
        loc=op.get("location",{}); key=(loc.get("city") or "Unknown city",loc.get("region") or "Unknown region")
        groups[key]["opportunities"]+=1; groups[key]["verticals"][op["vertical"]]+=1
    return [{"city":k[0],"region":k[1],"opportunities":v["opportunities"],
             "vertical_diversity":len(v["verticals"]),"verticals":dict(v["verticals"])}
            for k,v in groups.items()]

def capital_board(opportunities):
    rows=[]
    for op in opportunities:
        price=op.get("asking_price")
        ready=integration_readiness(op)
        rows.append({"id":op["id"],"name":op["name"],"asking_price":price,
                     "teller_proof_present":not any(x=="TELLER_MONEY_AND_MANAGEMENT" for x in ready["missing"]),
                     "deployable_amount":None,"direct_ob_access":False})
    return rows

def what_if(ops):
    total=Decimal("0"); known=True
    for op in ops:
        p=money(op.get("asking_price"))
        if p is None: known=False
        else: total+=p
    return {"count":len(ops),"asking_total":str(total.quantize(Decimal("0.01"))) if known else None,
            "verticals":dict(Counter(x["vertical"] for x in ops)),
            "regions":dict(Counter(x.get("location",{}).get("region") or "Unknown" for x in ops)),
            "capital_readiness_assumed":False}

def playbook(op): return {"vertical":op["vertical"],"steps":PLAYBOOKS[op["vertical"]],"legal_requirements_claimed":False}

def build_portfolio_studio(opportunities,thesis,record_lookup):
    return {"command_map":command_map(opportunities),"geo_expansion":geo_expansion(opportunities),
            "lender_library":lender_library(opportunities),
            "calendar":acquisition_calendar(opportunities,record_lookup),
            "capital_board":capital_board(opportunities)}

def build_deal_studio(op,opportunities,thesis,records,events):
    return {"portfolio_fit":portfolio_fit(op,opportunities,thesis),
      "timeline":acquisition_timeline(op,records),"negotiation":negotiation_intelligence(op),
      "deal_dna":deal_dna(op,opportunities),"predicted_actual":predicted_vs_actual(op,records),
      "impact":impact_summary(records),"story":deal_story(op,events,records),
      "knowledge_graph":knowledge_graph(op,records),"why_not":why_not(op,records),
      "playbook":playbook(op),"ic_packet":ic_packet(op,records,thesis)}
