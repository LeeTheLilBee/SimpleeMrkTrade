"use strict";
const assert=require("node:assert/strict");
const c=require("../web/static/ob/ob_beta_intelligence_contract.js");
assert.equal(c.VERSION,"OBUX111-135");
assert.equal(c.boundaries.broker_api,false);
assert.equal(c.boundaries.manual_live_grant,false);
assert.equal(c.boundaries.auto_execution,false);
assert.equal(c.boundaries.durable_archive,false);
const missing=c.evidence({});
assert.equal(missing.current,false);
assert.equal(missing.as_of,"Unverified");
assert.equal(c.evidence({projection_status:"fresh",display_eligible:true,current_eligible:true,source:"",as_of:"2026-09-28"}).current,false);
const real={projection_status:"fresh",display_eligible:true,current_eligible:true,source:"provider-evidence",as_of:"2026-09-28T12:00:00Z"};
assert.equal(c.evidence(real).current,true);
let empty=c.attention(real,{loaded:false,records:[]});
assert.equal(empty.length,1);
assert.equal(empty[0].kind,"status");
assert.equal(c.alertItems(real,{loaded:false,records:[]}).length,0);
let warning=c.alertItems({projection_status:"stale",display_eligible:false,current_eligible:false,source:"older",as_of:"2026-09-27",reason:"stale market feed"},{loaded:false,records:[]});
assert.equal(warning.length,1);
assert.equal(warning[0].severity,"safety");
assert.equal(warning[0].dismissible,false);
assert.equal(warning[0].title,"The current sky is not verified");
let record={
  review_id:"receipt-42",source_name:"review-ledger",truth_mode:"paper",symbol:"XYZ",
  process_quality:"REVIEW",outcome_class:"UNKNOWN",realized_return_pct:null,
  causes:[{label:"Evidence missing"}],rule_violations:[{reason:"Source stale"}],
  entry:{planned_time:"2026-09-28T08:30:00Z",actual_time:null},
  exit:{actual_time:null},lifecycle:{},raw_source:{decision:"rejected"}
};
let snap={loaded:true,records:[record]};
const rows=c.alertItems(real,snap);
assert.equal(rows.length,1);
assert.equal(rows[0].kind,"review");
assert.match(rows[0].id,/receipt-42/);
const why=c.whyPassed(record);
assert.equal(why.qualified,true);
assert.deepEqual(why.reasons,["Evidence missing","Source stale"]);
assert.equal(c.whyPassed({review_id:"x",source_name:"review-ledger",causes:["market"]}).qualified,false);
assert.equal(c.whyPassed({review_id:"x",source_name:"review-ledger",causes:["market"]}).reasons.length,0);
const life=c.orbit(record);
assert.equal(life.stages.length,7);
assert.equal(life.stages[3].name,"Entry");
assert.equal(life.stages[3].state,"not documented");
assert.equal(life.broker_fill_asserted,false);
const grouped=c.performance({loaded:true,records:[
  {...record,realized_return_pct:4,process_quality:"CLEAN"},
  {...record,review_id:"receipt-43",realized_return_pct:null,process_quality:"UNKNOWN"},
  {...record,review_id:"receipt-44",truth_mode:"proof",realized_return_pct:31,process_quality:"UNKNOWN"}
]});
assert.equal(grouped.groups.length,2);
const paper=grouped.groups.find(g=>g.mode==="paper");
const proof=grouped.groups.find(g=>g.mode==="proof");
assert.equal(paper.records,2);
assert.equal(paper.documented_returns,1);
assert.equal(paper.documented_mean_return_pct,4);
assert.equal(proof.documented_mean_return_pct,31);
assert.equal(paper.official_claim,false);
assert.equal(c.performance({loaded:false,records:[record]}).groups.length,0);
const comparison=c.strategyComparison({symbol:"AAA",thesis:"Observe range",mode:"Survey"},
  {symbol:"BBB",thesis:"Study volume",mode:"Paper"});
assert.equal(comparison.quantitative_comparison_available,false);
assert.equal(comparison.left.mode,"Survey");
console.log("OBUX111–135 pure source, alert, why-passed, orbit and mode-isolation tests passed");
