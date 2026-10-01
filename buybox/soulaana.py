"""Read-only contextual Soulaana intelligence for REAL owner records.

This is a grounded deterministic explanation service, not a live generative
model, not Tower authentication, and not any kind of approval authority.
Nothing here writes opportunity truth or invents unavailable integrations.
"""
from __future__ import annotations
from .core import evaluate, soulaana_brief
from .registry import get_vertical
from .dealroom import current_tasks

INTENTS = frozenset({
    "overview", "evidence", "diligence", "financing", "insurance", "valuation", "decision", "offer", "closing", "economics", "changes", "red_team", "next_action"
})

def context(op, intent="overview"):
    if intent not in INTENTS:
        raise ValueError("UNSUPPORTED_SOULAANA_INTENT")
    analysis = evaluate(op)
    manifest = get_vertical(op["vertical"])
    evidence = analysis["evidence"]
    entries=[]
    def note(kind, message, refs=None, label=None):
        entries.append({"classification":kind,"text":message,
                        "references":list(refs or []),"label":label})
    relevant = {
        "overview":{"evidence","economics","changes"},
        "evidence":{"evidence"},
        "diligence":{"diligence"},
        "financing":{"financing"},
        "insurance":{"insurance"},
        "valuation":{"valuation"},
        "decision":{"decision"},
        "offer":{"offer"},
        "closing":{"closing"},
        "economics":{"economics"},
        "changes":{"changes"},
        "red_team":{"economics","evidence"},
        "next_action":{"evidence","changes"},
    }[intent]
    if "evidence" in relevant:
        for row in evidence["rows"]:
            kind=row["kind"].replace("_"," ").title()
            if row["state"] in ("DOCUMENT_SUPPORTED","THIRD_PARTY_VERIFIED"):
                note("DOCUMENTARY_SUPPORT",
                    kind+" has recorded support; this does not independently certify the asset or claim.",
                    [row["reference"]] if row["reference"] else [],
                    row["state"])
            elif row["state"]=="CONFLICTED":
                note("CONFLICT",kind+" contains unresolved contradictory evidence.",
                     [row["reference"]] if row["reference"] else [],"REVIEW_REQUIRED")
            elif row["critical"]:
                note("MISSING_OR_UNVERIFIED",
                     kind+" is not established at the required documentary standard.",
                     [row["reference"]] if row["reference"] else [],row["state"])
    if "evidence" in relevant or "changes" in relevant:
        for snapshot in op.get("snapshots", []):
            if snapshot.get("archive_state") == "NOT_REQUESTED":
                refs=[snapshot.get("snapshot_id")]
                refs.extend(x.get("evidence_id") for x in snapshot.get("evidence_versions",[]))
                note("LOCAL_PROOF_SNAPSHOT",
                     "An original-document version was frozen locally at acquisition revision "+
                     str(snapshot.get("opportunity_revision"))+
                     ". Its source hash is preserved. Tower/Vault archival has NOT been requested or verified.",
                     [x for x in refs if x], "NOT_ARCHIVED")
    if "diligence" in relevant:
        from .diligence import diligence_snapshot
        queue=diligence_snapshot(op)
        note("RECORDED_DILIGENCE_STATE",
             (str(queue["documentary_supported_count"])+" of "+
              str(queue["total_requirements"])+" registered evidence categories have "+
              "recorded documentary support; "+
              str(queue["critical_outstanding"])+" critical categories remain "+
              "outstanding. This does not imply independent verification, "+
              "Vault archival or Tower closing authorization."),
             label="ACTUAL_RECORDS_NOT_CERTIFICATION")
        outstanding=[r for r in queue["requirements"]
                     if r["critical"] and not r["documentary_supported"]]
        for item in outstanding:
            note("DILIGENCE_REQUIREMENT",
                 (item["kind"].replace("_"," ").title()+": recorded status "+
                  item["recorded_state"].replace("_"," ").lower()+
                  ". Obtain/review the original before relying on this category."),
                 [item["evidence_id"]] if item["evidence_id"] else [],
                 "CRITICAL_OPEN")
        for item in queue["requirements"]:
            for task in item["open_tasks"]:
                note("OWNER_RECORDED_TASK",
                     (task["title"]+"; current state "+
                      task["status"].lower()+"; owner-entered deadline "+
                      task["due_date"]+". This does not contact the seller."),
                     [task["id"]], "PENDING_OWNER_ACTION")
    if "financing" in relevant:
        from .financing import financing_snapshot
        offers=financing_snapshot(op)
        note("EXTERNAL_READINESS_UNKNOWN",
             "Teller money and management readiness is UNKNOWN. Source documents and modeled loan payments are not approvals, signed funding or deployment authority.",
             label="NOT_APPROVED")
        for option in offers["options"]:
            q=option["quote"]; a=option["analysis"]
            note("SOURCE_LINKED_FINANCING",
                 (q["lender_label"]+" / "+q["program_label"]+
                  ": document-recorded principal $"+q["principal"]+
                  " at fixed APR "+q["apr_percent"]+"% for "+str(q["term_months"])+
                  " months. BuyBox models $"+a["modeled_monthly_payment"]+
                  " per month and unverified buyer cash gap $"+
                  a["unverified_buyer_cash_gap"]+". These calculations do not establish lender approval, protected cash or staff capacity."),
                 [q["id"],q["source_artifact_id"],q["source_evidence_id"]],
                 a["status"])
            if a["review_flags"]:
                note("FINANCING_RECHECK_REQUIRED",
                     "Reconfirm recorded terms against the original: "+
                     ", ".join(a["review_flags"])+". No outdated document is silently accepted.",
                     [q["id"]], "SOURCE_OR_PRICE_CHANGED")
        if not offers["options"]:
            note("FINANCING_MISSING",
                 "No current original-backed financing terms are recorded. BuyBox will not invent a lender, rate or bank commitment.",
                 label="NO_DOCUMENTED_OPTION")
    if "insurance" in relevant:
        from .insurance import insurance_snapshot
        insurance=insurance_snapshot(op)
        note("COVERAGE_AUTHORITY_UNKNOWN",
             "No live insurer/broker confirmation, policy binding, premium payment, lender compliance, Teller readiness or Tower closing authorization has been established by the BuyBox insurance records.",
             label="COVERAGE_IN_FORCE_UNKNOWN")
        for item in insurance["records"]:
            rec=item["record"]; review=item["assessment"]
            label=("$"+review["annual_premium"]+" annual premium" if review["annual_premium"] is not None
                   else "premium not stated")
            note("SOURCE_LINKED_INSURANCE",
                 rec["document_kind"].lower()+" as recorded from "+rec["carrier_label"]+
                 " ("+label+"). Owner-transcribed coverages: "+
                 ", ".join(rec["coverage_codes"])+
                 ". Original source and recorded effective/expiration dates must be independently checked; the document label alone does not confirm a policy is in force.",
                 [rec["id"],rec["source_evidence_id"],rec["source_artifact_id"]],
                 review["status"])
            if review["review_flags"]:
                note("INSURANCE_RECHECK_REQUIRED",
                     "Insurance source review flags: "+", ".join(review["review_flags"])+
                     ". Follow up with insurer/broker and any actual lender conditions.",
                     [rec["id"]], "NOT_INDEPENDENTLY_CONFIRMED")
        if not insurance["records"]:
            note("INSURANCE_NOT_RECORDED",
                 "No original-backed insurance record is entered. Ask an insurance professional about the actual asset's exposures, limits, exclusions, costs, timing and any lender requirements.",
                 label="INSURABILITY_NOT_ESTABLISHED")
    if "valuation" in relevant:
        from .comparables import market_evidence_report
        market=market_evidence_report(op)
        note("SOURCE_ONLY_MARKET_RESEARCH",
             "BuyBox has "+str(market["active_count"])+" original-backed owner-recorded comparison observations. These do not establish an independent appraisal, certified closed sale, price ceiling or lending decision.",
             label="NO_TARGET_VALUATION")
        for cohort in market["cohorts"]:
            identifiers=cohort["observation_ids"]
            if cohort["status"]=="DESCRIPTIVE_COHORT_ONLY":
                note("DESCRIPTIVE_COMPARABLE_COHORT",
                     cohort["market"]+" / "+cohort["basis"].replace("_"," ").lower()+
                     " / "+cohort["source_kind"].replace("_"," ").lower()+
                     ": "+str(cohort["distinct_subject_count"])+" recorded distinct subjects. Observed range "+
                     cohort["observed_min"]+" to "+cohort["observed_max"]+
                     ", median "+cohort["observed_median"]+" "+cohort["unit"]+
                     ". Original event dates run from "+cohort["earliest_event_date"]+
                     " to "+cohort["latest_event_date"]+". These are descriptive owner transcriptions, not a target valuation.",
                     identifiers+cohort["source_artifact_ids"],"NOT_APPRAISED")
            else:
                note("INSUFFICIENT_MARKET_EVIDENCE",
                     cohort["market"]+" / "+cohort["basis"].replace("_"," ").lower()+
                     " has fewer than two distinct sourced subjects of the same type. BuyBox will not invent a benchmark.",
                     identifiers,"INSUFFICIENT_DISTINCT_SUBJECTS")
        if not market["cohorts"]:
            note("MARKET_SOURCE_MISSING",
                 "No original-backed comparable evidence has been recorded for this opportunity.",
                 label="NO_DOCUMENTED_COMPARABLES")
    if "decision" in relevant:
        from .decision_desk import decision_dossier
        desk=decision_dossier(op)
        note("CURRENT_ANALYTICAL_CONTEXT",
             "Current BuyBox judgment "+desk["judgment"].replace("_"," ").lower()+
             "; "+str(desk["critical_diligence_outstanding"])+" critical diligence categories outstanding; "+
             str(desk["unresolved_source_discrepancies"])+" unresolved source discrepancies. Teller money/management readiness is UNKNOWN and Tower has not approved a protected action.",
             label="NOT_A_TRANSACTION_AUTHORIZATION")
        for decision in desk["historical_notes"][:10]:
            note("OWNER_RESEARCH_DISPOSITION",
                 "The owner recorded '"+decision["choice"].replace("_"," ").lower()+
                 "' against saved opportunity revision "+
                 str(decision["source_opportunity_revision"])+
                 ". This is a "+decision["display_state"].replace("_"," ").lower()+
                 "; it does not change lifecycle, contact a seller or authorize purchase.",
                 [decision["id"]]+decision["cited_evidence_ids"],"NON_AUTHORIZING_OWNER_NOTE")
        if not desk["historical_notes"]:
            note("OWNER_NOTE_NOT_YET_RECORDED",
                 "No source-bound owner research disposition has been preserved yet. Notes do not replace Tower permissions or Teller readiness.",
                 label="NO_OWNER_DISPOSITION")
    if "offer" in relevant:
        from .offer_lab import offer_lab_snapshot
        lab=offer_lab_snapshot(op)
        note("OFFER_AUTHORITY_ABSENT",
             "Offer Lab contains private owner scenarios only. No scenario was sent to a seller, converted into an LOI, approved by Tower, or funded by Teller.",
             label="PRIVATE_MODEL_ONLY")
        for row in lab["scenarios"]:
            analysis_row=row["analysis"]
            change=("unknown" if analysis_row["price_delta_from_current_asking"] is None
                    else "$"+analysis_row["price_delta_from_current_asking"])
            note("OWNER_PRIVATE_OFFER_SCENARIO",
                 (row["name"]+": proposed price $"+row["proposed_purchase_price"]+
                  ", delta from current asking "+change+
                  ", seller credit $"+row["requested_seller_credit"]+
                  ", diligence "+str(row["due_diligence_days"])+
                  " days, planned close "+row["planned_closing_date"]+
                  ". This is private modeling and not a transmitted offer."),
                 [row["id"],row["source_snapshot_digest"]],
                 analysis_row["status"])
            if analysis_row["review_flags"]:
                note("OFFER_SCENARIO_RECHECK_REQUIRED",
                     "Recheck this private scenario against current source records: "+
                     ", ".join(analysis_row["review_flags"])+".",
                     [row["id"]],"SOURCE_OR_ASSUMPTION_CHANGED")
        if not lab["scenarios"]:
            note("OFFER_SCENARIO_NOT_RECORDED",
                 "No private owner offer scenario is recorded. BuyBox will not invent a purchase price or seller terms.",
                 label="NO_PRIVATE_SCENARIO")
    if "closing" in relevant:
        from .closing_review import closing_review_snapshot
        closing=closing_review_snapshot(op)
        note("CLOSING_AUTHORITY_BLOCKED",
             ("BuyBox local source state is "+
              closing["local_source_state"].replace("_"," ").lower()+
              ". Protected closing is still blocked because Tower closing authorization, "+
              "Teller money/management readiness, title/ownership transfer, lender commitment, "+
              "insurance in force and settlement completion have not been independently established."),
             label="NOT_AUTHORIZED_TO_CLOSE")
        for code in closing["source_blockers"]:
            note("LOCAL_CLOSING_SOURCE_GAP",
                 code.replace("_"," ").title()+
                 ". This is a current BuyBox source/review gap, not permission to bypass it.",
                 label="REVIEW_REQUIRED")
        for code in closing["external_blockers"]:
            note("EXTERNAL_CLOSING_GATE",
                 code.replace("_"," ").title()+
                 ". BuyBox cannot self-certify this external authority or completion state.",
                 label="EXTERNAL_VERIFICATION_REQUIRED")
        if closing["historical_reviews"]:
            latest=closing["historical_reviews"][0]
            note("OWNER_LOCAL_CLOSING_REVIEW",
                 ("The owner froze a local closing review against opportunity revision "+
                  str(latest["source_opportunity_revision"])+
                  ". It remains historical source review only and did not move money, change lifecycle or contact an external system."),
                 [latest["id"],latest["local_snapshot_sha256"]],
                 "NON_AUTHORIZING_LOCAL_REVIEW")
        else:
            note("CLOSING_REVIEW_NOT_RECORDED",
                 "No local owner closing review snapshot has been preserved yet.",
                 label="NO_LOCAL_CLOSING_REVIEW")
    if "economics" in relevant:
        result=analysis["financials"]
        if result["status"]=="CALCULATED":
            revenue=op.get("metrics",{}).get("annual_revenue",{})
            expenses=op.get("metrics",{}).get("annual_expenses",{})
            refs=[x.get("evidence_id") for x in (revenue,expenses) if x.get("evidence_id")]
            note("BUYBOX_CALCULATION",
                 "Annual operating difference is $"+result["net"]+
                 " from the recorded revenue and expense figures for the same reported period. "
                 "It is not independently verified net profit or a complete acquisition valuation.",
                 refs,"PRELIMINARY_FORMULA")
        else:
            note("MISSING_OR_UNVERIFIED",
                 "Financial calculation is unavailable: "+result["status"].replace("_"," ").lower()+
                 ". Documented revenue and expenses must cover matching periods.",
                 label=result["status"])
    if "changes" in relevant:
        change=op.get("last_material_change")
        if change:
            note("RECORDED_EVENT",
                 change["reason"]+". Affected fields: "+", ".join(change["fields"])+
                 ". Previously held external readiness and protected approvals cannot be reused.",
                 [change["source_reference"]],"STALE_ANALYSIS")
        else:
            note("RECORDED_STATE","No material change has been recorded for this opportunity.")
    if "evidence" in relevant or intent in ("red_team", "next_action"):
        for discrepancy in analysis.get("deal_integrity", {}).get("discrepancies", []):
            note(
                "SOURCE_DISCREPANCY",
                ("The original documents disagree about "+
                 discrepancy["field"].replace("_", " ").lower()+
                 " for "+discrepancy["subject_id"]+" at "+
                 discrepancy["period_key"]+
                 ". Neither source has been selected as fact, and this blocks analytical qualification."),
                discrepancy["claim_ids"], "UNRESOLVED_DOCUMENT_CONFLICT")
    for finding in analysis["findings"]:
        note("POLICY_RESULT",finding["reason"],[finding["rule_id"]],finding["level"])
    if intent=="red_team":
        from .red_team import red_team_report
        report=red_team_report(op)
        for record in report["records"]:
            note("OWNER_RECORDED_STRESS",
                 (record["name"]+": recorded owner assumption uses revenue factor "+
                  record["revenue_factor"]+" and expense factor "+record["expense_factor"]+
                  " against the source-linked annual period "+record["reporting_period"]+
                  ". Modeled operating difference is $"+record["modeled_operating_difference"]+
                  ", compared with the documented base difference $"+
                  record["recorded_operating_difference"]+". Status: "+
                  record["freshness"].replace("_"," ").lower()+
                  ". This is an assumption, not historical performance or Teller authorization."),
                 [record["id"],record["source_snapshot_digest"]]+
                 [m["evidence_id"] for m in record["source_metrics"]],
                 record["freshness"])
        if not report["records"]:
            note("STRESS_NOT_RECORDED",
                 "No actual owner financial stress has been recorded for this opportunity. "
                 "A reviewed, original-backed matched-period annual base is required first.",
                 label="NO_INVENTED_STRESS")
        note("MODELING_LIMITATION",
             "The financial multiplier model does not account for asset-specific hazards, "
             "loan terms, replenishment timing, seller consent, independent audit, "
             "Teller deployment or Tower protected actions.",
             label="FINANCIAL_ONLY_NO_DECISION")
    if intent=="next_action":
        tasks=[x for x in current_tasks(op) if x["status"] in ("OPEN","WAITING")]
        if tasks:
            first=tasks[0]
            note("OWNER_RECORDED_TASK",
                 "Next recorded task: "+first["title"]+"; due "+first["due_date"]+".",
                 [first["id"]],first["status"])
        elif analysis.get("deal_integrity", {}).get("discrepancies"):
            first=analysis["deal_integrity"]["discrepancies"][0]
            note("RULE_DERIVED_ACTION",
                 "Compare the supporting documents and investigate the conflicting "+
                 first["field"].replace("_"," ").lower()+" statements in Deal Integrity.",
                 first["claim_ids"],"PROPOSED_NOT_EXECUTED")
        elif evidence["missing_critical"]:
            note("RULE_DERIVED_ACTION",
                 "Request or verify "+evidence["missing_critical"][0].replace("_"," ")+".",
                 label="PROPOSED_NOT_EXECUTED")
        else:
            note("RULE_DERIVED_ACTION",
                 "Review the dossier and applicable stage requirements. No protected action is authorized.",
                 label="PROPOSED_NOT_EXECUTED")
    brief=soulaana_brief(op,analysis)
    return {
        "speaker":"Soulaana", "mode":"DETERMINISTIC_GROUNDED_CONTEXT",
        "live_ai_connected":False, "opportunity_id":op["id"],
        "opportunity_revision":op.get("version"), "intent":intent,
        "vertical":manifest["label"],"judgment":analysis["judgment"],
        "summary":brief["summary"],"entries":entries,
        "readiness":analysis["teller_readiness"],
        "can_edit_evidence":False,"can_authorize":False,"can_send_offers":False,
        "source_note":"Owner-recorded inputs and BuyBox calculations; external integrations are not connected.",
    }
