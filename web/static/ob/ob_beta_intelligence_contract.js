/* OBUX111–135 — pure, source-bound beta expansion projections.
 * No provider fetch, no account balance reconstruction, no order/mode mutation.
 * This module may be tested in Node without a browser or storage.
 */
(function (root, factory) {
  "use strict";
  const api = factory();
  if (typeof module === "object" && module.exports) module.exports = api;
  if (root) root.OBBetaIntelligenceContract = api;
})(typeof window !== "undefined" ? window : null, function () {
  "use strict";
  const VERSION = "OBUX111-135";
  const object = value => value && typeof value === "object" && !Array.isArray(value) ? value : {};
  const array = value => Array.isArray(value) ? value : [];
  const string = (value, fallback = "") =>
    typeof value === "string" && value.trim() ? value.trim() : fallback;
  const number = value => value !== null && value !== undefined && value !== ""
    && Number.isFinite(Number(value)) ? Number(value) : null;
  const first = (...args) => args.find(x => x !== null && x !== undefined && x !== "") ?? null;
  const sourceRef = value => string(value, "Source unavailable");
  const id = value => string(value).replace(/[^a-zA-Z0-9:_./-]/g, "-").slice(0, 150);

  function evidence(projection) {
    const p = object(projection);
    const status = string(p.projection_status, "unavailable").toLowerCase();
    const source = string(p.source);
    const asOf = string(p.as_of);
    const current = p.current_eligible === true && p.display_eligible === true
      && status === "fresh" && !!source && !!asOf;
    return Object.freeze({current, status, source:sourceRef(source),
      as_of:asOf || "Unverified", reason:string(p.reason, "Current canonical evidence not verified.")});
  }

  function reviewRows(reviewSnapshot) {
    const r = object(reviewSnapshot);
    return r.loaded === true ? array(r.records).map(object)
      .filter(row => string(row.review_id) && string(row.source_name)) : [];
  }

  function whyPassed(record) {
    const r = object(record);
    const raw = object(r.raw_source);
    const decision = string(first(raw.decision, raw.review_decision, raw.disposition,
      raw.candidate_state, raw.status)).toLowerCase();
    const supported = /^(rejected|skipped|declined|passed|no_trade|not_taken|held|blocked|review_required)$/.test(decision);
    const reasons = array(r.causes).map(item => {
      const o = object(item); return string(first(o.label,o.reason,o.description,
        typeof item === "string" ? item : null));
    }).filter(Boolean).slice(0, 4);
    const extra = array(r.rule_violations).map(item =>
      string(first(object(item).label, object(item).reason,
        typeof item === "string" ? item : null))).filter(Boolean);
    const source = sourceRef(r.source_name);
    return Object.freeze({qualified:supported, decision:supported?decision:"unclassified",
      title:supported?"Why this setup did not advance":"No documented pass decision",
      reasons:supported?[...new Set([...reasons,...extra])].slice(0, 4):[],
      explanation:supported && (reasons.length || extra.length)
        ? "Only documented reasons are displayed; an outcome is not the same as process quality."
        : "No explicit reason is available. Do not infer a mistake, missed gain, or market cause.",
      source, review_id:string(r.review_id), truth_mode:string(r.truth_mode,"unknown")});
  }

  function orbit(record) {
    const r=object(record), life=object(r.lifecycle), entry=object(r.entry), exit=object(r.exit);
    const marks=[
      ["Discovery", first(r.created_at,life.discovered_at)],
      ["Research", first(life.researched_at,life.reviewed_at)],
      ["Decision", first(life.decision_at,life.approved_at)],
      ["Entry", first(entry.actual_time,life.entered_at)],
      ["Monitoring", first(life.monitored_at,life.managed_at)],
      ["Exit", first(exit.actual_time,life.closed_at)],
      ["Review", first(life.reviewed_at,life.finalized_at)]
    ];
    return Object.freeze({review_id:string(r.review_id),source:sourceRef(r.source_name),
      truth_mode:string(r.truth_mode,"unknown"), stages:marks.map(([name,time])=>({
        name, state:time?"documented":"not documented", time:time?String(time):null
      })), outcome:string(r.outcome_class,"UNKNOWN"), broker_fill_asserted:entry.actual_time != null});
  }

  function performance(snapshot) {
    const rows=reviewRows(snapshot);
    const groups={};
    for(const record of rows){
      const mode=string(record.truth_mode,"unknown");
      if(!groups[mode])groups[mode]={mode,records:0,documented_returns:0,return_sum:0,
        clean_process:0,unknown_process:0,pass_decisions:0};
      const g=groups[mode];g.records++;
      const value=number(record.realized_return_pct);
      if(value!==null){g.documented_returns++;g.return_sum+=value;}
      if(record.process_quality==="CLEAN")g.clean_process++;
      if(!record.process_quality || record.process_quality==="UNKNOWN")g.unknown_process++;
      if(whyPassed(record).qualified)g.pass_decisions++;
    }
    return Object.freeze({source_loaded:object(snapshot).loaded===true,
      groups:Object.values(groups).map(g=>({...g, documented_mean_return_pct:g.documented_returns
        ? g.return_sum/g.documented_returns:null,official_claim:false})),
      note:"Modes are separate. This browser summary is not a verified brokerage performance statement."});
  }

  function attention(projection, reviewSnapshot) {
    const p=object(projection), ev=evidence(p);
    const items=[];
    if(!ev.current) items.push({id:"source:"+id(ev.status),kind:"source",severity:"safety",
      title:"The current sky is not verified",detail:ev.reason,
      source:ev.source,as_of:ev.as_of,href:"/ob/market-map",dismissible:false});
    const rows=reviewRows(reviewSnapshot);
    const problems=rows.filter(row=>array(row.rule_violations).length ||
      row.process_quality==="REVIEW" || row.process_quality==="ADVERSE" ||
      row.process_quality==="UNKNOWN").slice(0,2);
    problems.forEach(row=>items.push({id:"review:"+id(row.source_name)+":"+id(row.review_id),
      kind:"review",severity:"review",title:"Review a documented process record",
      detail:string(row.symbol,"A record")+" · "+string(row.truth_mode,"unknown")+
        " · "+string(row.process_quality,"Process not classified"),
      source:sourceRef(row.source_name),as_of:string(row.created_at,"Unverified"),
      href:"/ob/review-center",dismissible:true}));
    if(!items.length)items.push({id:"quiet-sky",kind:"status",severity:"info",
      title:"Nothing needs to be forced",detail:"No new source-backed priority is asserted.",
      source:ev.source,as_of:ev.as_of,href:"/ob/market-map",dismissible:true});
    return Object.freeze(items.slice(0,3));
  }

  function alertItems(projection, reviewSnapshot) {
    const rows=attention(projection,reviewSnapshot).filter(x=>x.kind!=="status");
    // Only canonical source state or independently loaded review records, never sample tickers.
    const dedup=new Map();
    for(const item of rows){const group=item.kind+":"+item.id; if(!dedup.has(group))dedup.set(group,item);}
    return Object.freeze([...dedup.values()]);
  }

  function strategyComparison(left,right) {
    // Compare user-authored research labels only; do not create a backtest/return projection.
    const a=object(left),b=object(right);
    return Object.freeze({left:{symbol:string(a.symbol),thesis:string(a.thesis),
      source_ref:string(a.source_ref,"Not recorded"),mode:string(a.mode,"Survey")},
      right:{symbol:string(b.symbol),thesis:string(b.thesis),
      source_ref:string(b.source_ref,"Not recorded"),mode:string(b.mode,"Survey")},
      quantitative_comparison_available:false,
      explanation:"These are user research notes, not a simulation or investment recommendation."});
  }

  return Object.freeze({VERSION,evidence,whyPassed,orbit,performance,attention,alertItems,
    strategyComparison,boundaries:Object.freeze({read_only:true,broker_api:false,
      capital_movement:false,manual_live_grant:false,auto_execution:false,
      synthetic_market_fallback:false,durable_archive:false})});
});
