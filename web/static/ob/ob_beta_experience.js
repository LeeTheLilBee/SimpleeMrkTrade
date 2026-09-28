/* OBUX111–135 — room-local living intelligence, alerts, focus and owner evidence.
 * No external network calls or invented data. Existing room sources remain authoritative.
 */
(function (global) {
  "use strict";
  const C=global.OBBetaIntelligenceContract;
  if (!C) return;
  const room=String(document.body && document.body.dataset.obRoom || "");
  const $=id=>document.getElementById(id);
  const esc=v=>String(v==null?"":v).replace(/&/g,"&amp;").replace(/</g,"&lt;")
    .replace(/>/g,"&gt;").replace(/"/g,"&quot;").replace(/'/g,"&#39;");
  const obj=x=>x&&typeof x==="object"&&!Array.isArray(x)?x:{};
  const arr=x=>Array.isArray(x)?x:[];
  const string=x=>typeof x==="string"?x:"";
  const APP_KEY="ob.beta.x111.preferences.v1", READ_KEY="ob.beta.x111.read.v1";
  const DEFAULT={focus:false,quiet:true,sound:false,compact:false};
  function load(key,storage,fallback){try{return JSON.parse(storage.getItem(key)||"null")||fallback;}catch(_){return fallback;}}
  function save(key,storage,data){try{storage.setItem(key,JSON.stringify(data));return true;}catch(_){return false;}}
  let prefs=Object.assign({},DEFAULT,obj(load(APP_KEY,global.localStorage,DEFAULT)));
  let readIds=arr(load(READ_KEY,global.sessionStorage,[])).filter(x=>typeof x==="string");
  let review={loaded:false,records:[]}, selectedId=null, drawer=null, priorFocus=null;
  function proj(){
    const adapter=global.OB_ENGINE_FEED_ADAPTER_V25;
    try{return adapter&&typeof adapter.getProjection==="function"?adapter.getProjection():{};}catch(_){return {};}
  }
  function reviewSnapshot(){
    const api=global.OBReviewCenterProjection;
    if (api && typeof api.snapshot==="function") {
      try{return api.snapshot();}catch(_){}
    }
    return review;
  }
  function reviewRows(){const s=reviewSnapshot();return s.loaded===true?arr(s.records).filter(x=>x&&x.review_id&&x.source_name):[];}
  function activeReview(){
    const records=reviewRows();
    if(!records.length)return null;
    const other=global.OBReviewCenter;
    const selected=other&&typeof other.getState==="function"?obj(other.getState()).selectedId:null;
    return records.find(x=>x.review_id===(selectedId||selected))||records[0];
  }
  function statusMarkup(){const e=C.evidence(proj());return '<span class="obx-status">'+
    (e.current?"Source current":"Source HOLD")+" · "+esc(e.as_of)+"</span>";}
  function alertRows(){return C.alertItems(proj(),reviewSnapshot());}
  function markRead(id){if (!id || id.startsWith("source:"))return;
    readIds=[...new Set([...readIds,id])].slice(-120);save(READ_KEY,global.sessionStorage,readIds);
  }
  function alertsMarkup(){
    const alerts=alertRows();
    if(!alerts.length)return '<div class="obx-quiet">No verified new alerts. No demonstration tickers or pretend market events have been inserted.</div>';
    return alerts.map(item=>'<article class="obx-drawer-item"><span class="obx-eyebrow" data-severity="'+esc(item.severity)+'">'+esc(item.kind.toUpperCase())+'</span>'+
      '<strong>'+esc(item.title)+'</strong><p>'+esc(item.detail)+'</p><small>Source: '+esc(item.source)+' · As of: '+esc(item.as_of)+'</small>'+
      '<div class="obx-drawer-actions"><a class="obx-button" href="'+item.href+'">Open source room →</a>'+
      (item.dismissible?'<button class="obx-button" type="button" data-obx-read="'+esc(item.id)+'">'+
      (readIds.includes(item.id)?"Acknowledged":"Acknowledge")+'</button>':'<span class="obx-status">Safety holds remain visible</span>')+
      '</div></article>').join("");
  }
  function settingsMarkup(){return '<p>These preferences affect presentation only. They never change market truth, risk stops, permissions or execution.</p>'+
    '<label class="obx-setting"><span>Focus View · one task at a time</span><input type="checkbox" data-obx-pref="focus" '+(prefs.focus?"checked":"")+' /></label>'+
    '<label class="obx-setting"><span>Group repeated notices / quiet presentation</span><input type="checkbox" data-obx-pref="quiet" '+(prefs.quiet?"checked":"")+' /></label>'+
    '<label class="obx-setting"><span>Compact cards</span><input type="checkbox" data-obx-pref="compact" '+(prefs.compact?"checked":"")+' /></label>'+
    '<label class="obx-setting"><span>Optional sound on explicit interactions (default muted)</span><input type="checkbox" data-obx-pref="sound" '+(prefs.sound?"checked":"")+' /></label>'+
    '<p class="obx-muted">Urgent source problems are never hidden by quiet preferences. Research notes stay in this browser tab unless explicitly exported.</p>'+
    '<button class="obx-button" data-obx-preview type="button">Preview sound</button>';
  }
  function sound(){if(!prefs.sound)return;
    try {const Audio=global.AudioContext||global.webkitAudioContext;if(!Audio)return;
      const ctx=new Audio(),osc=ctx.createOscillator(),gain=ctx.createGain();osc.type="sine";
      osc.frequency.value=480;gain.gain.setValueAtTime(.025,ctx.currentTime);
      gain.gain.exponentialRampToValueAtTime(.001,ctx.currentTime+.12);
      osc.connect(gain);gain.connect(ctx.destination);osc.start();osc.stop(ctx.currentTime+.13);
      osc.onended=()=>ctx.close();}catch(_){}
  }
  function focus(v){prefs.focus=Boolean(v);save(APP_KEY,global.localStorage,prefs);
    document.body.dataset.obFocusView=prefs.focus?"true":"false";
    document.querySelectorAll("[data-obx-focus-toggle]").forEach(x=>x.setAttribute("aria-pressed",String(prefs.focus)));
  }
  function closeDrawer(){if(!drawer)return;drawer.remove();drawer=null;document.removeEventListener("keydown",keys);
    if(priorFocus&&typeof priorFocus.focus==="function")priorFocus.focus();}
  function keys(e){if(!drawer)return;if(e.key==="Escape"){e.preventDefault();closeDrawer();return;}
    if(e.key!=="Tab")return;const nodes=[...drawer.querySelectorAll('button:not([disabled]),a[href],input:not([disabled]),textarea:not([disabled]),select:not([disabled])')]
      .filter(x=>x.offsetParent!==null);if(!nodes.length)return;
    if(e.shiftKey&&document.activeElement===nodes[0]){e.preventDefault();nodes[nodes.length-1].focus();}
    else if(!e.shiftKey&&document.activeElement===nodes[nodes.length-1]){e.preventDefault();nodes[0].focus();}
  }
  function openDrawer(type){if(drawer)closeDrawer();priorFocus=document.activeElement;
    const title={alerts:"Source-backed alerts",settings:"Your Observatory settings",
      soulaana:"Soulaana · Mission Control"}[type]||"Observatory";
    const content=type==="alerts"?alertsMarkup():type==="settings"?settingsMarkup():soulaanaMarkup();
    drawer=document.createElement("div");drawer.className="obx-cover";drawer.id="obBetaDrawer";
    drawer.innerHTML='<aside class="obx-drawer" role="dialog" aria-modal="true" aria-label="'+esc(title)+'">'+
      '<div class="obx-drawer-head"><div><span class="obx-eyebrow">THE OBSERVATORY · PRIVATE</span><h2>'+esc(title)+'</h2></div>'+
      '<button class="obx-button" type="button" data-obx-close aria-label="Close drawer">Close ×</button></div>'+
      '<div class="obx-drawer-list">'+content+'</div></aside>';
    document.body.appendChild(drawer);document.addEventListener("keydown",keys);drawer.querySelector("[data-obx-close]").focus();
    drawer.addEventListener("click",e=>{if(e.target===drawer||e.target.closest("[data-obx-close]"))closeDrawer();});
    drawer.addEventListener("change",e=>{const el=e.target.closest("[data-obx-pref]");if(!el)return;
      if(el.dataset.obxPref==="focus"){focus(el.checked);return;}
      prefs[el.dataset.obxPref]=el.checked;save(APP_KEY,global.localStorage,prefs);
      document.body.dataset.obCompact=prefs.compact?"true":"false";
    });
    drawer.addEventListener("click",e=>{let el=e.target.closest("[data-obx-read]");
      if(el){markRead(el.dataset.obxRead);openDrawer("alerts");return;}
      if(e.target.closest("[data-obx-preview]"))sound();
    });
  }
  function soulaanaMarkup(){const e=C.evidence(proj()), priority=C.attention(proj(),reviewSnapshot());
    const first=priority[0];return '<div class="obx-quiet"><strong>'+esc(e.current?
      "I can show the source-backed sky.":"I cannot confirm a current market sky.")+'</strong><p>'+
      esc(e.current?"You decide what to study; I will not turn observation into an order.":e.reason)+'</p>'+
      '<small>Source: '+esc(e.source)+' · As of: '+esc(e.as_of)+'</small></div>'+
      priority.map(x=>'<article class="obx-drawer-item"><span class="obx-eyebrow">'+esc(x.kind)+'</span>'+
      '<strong>'+esc(x.title)+'</strong><p>'+esc(x.detail)+'</p>'+
      '<a class="obx-button" href="'+x.href+'">Inspect the evidence →</a></article>').join("")+
      '<p class="obx-muted">No personalized trading recommendation, broker connection or mode authorization is made here.</p>';
  }
  function renderDashboard(){const mount=$("obBetaFeatureMount");if(!mount)return;
    const e=C.evidence(proj()), items=C.attention(proj(),reviewSnapshot());
    mount.innerHTML='<section class="obx-card" aria-label="Soulaana Mission Control">'+
      '<div class="obx-feature-head"><div><span class="obx-eyebrow">SOULAANA · MISSION CONTROL</span><h2>What deserves your attention?</h2></div>'+
      statusMarkup()+'</div><div class="obx-focusline">'+
      items.slice(0,2).map((x,i)=>'<article><span class="obx-eyebrow">'+(i===0?"FIRST LOOK":"AFTER THAT")+'</span>'+
      '<strong>'+esc(x.title)+'</strong><p>'+esc(x.detail)+'</p>'+
      '<small>Source: '+esc(x.source)+'</small><div class="obx-drawer-actions"><a class="obx-button" href="'+x.href+'">Open room →</a></div></article>').join("")+
      '</div><div class="obx-drawer-actions"><button class="obx-button" type="button" data-obx-open="soulaana">Ask Soulaana why</button>'+
      '<button class="obx-button" data-obx-focus-toggle type="button" aria-pressed="'+String(prefs.focus)+'">Focus View</button></div>'+
      '<p class="obx-muted">Attention is observational and source-bound. No personal account capital is shown on this normal Dashboard.</p></section>';
  }
  function renderReview(){const mount=$("obBetaFeatureMount");if(!mount)return;const records=reviewRows();
    const current=activeReview();const explain=current?C.whyPassed(current):null;
    const report=C.performance(reviewSnapshot());const chosen=current?C.orbit(current):null;
    mount.innerHTML='<section class="obx-card" aria-label="Review extensions">'+
      '<div class="obx-feature-head"><div><span class="obx-eyebrow">REVIEW CENTER · RESEARCH + DISCIPLINE</span><h2>Why We Passed · Lifecycle Orbit</h2></div>'+
      '<span class="obx-status">'+records.length+' source-backed review records</span></div>'+
      (!records.length?'<p class="obx-quiet">No canonical review records loaded. No fake trade performance or assumed rejection reasons.</p>':
      '<label class="obx-field">Choose a source record<select id="obxReviewSelect">'+
      records.slice(0,30).map(x=>'<option value="'+esc(x.review_id)+'" '+(current&&x.review_id===current.review_id?"selected":"")+'>'+
      esc(string(x.symbol)||"Unspecified symbol")+' · '+esc(x.truth_mode)+' · '+esc(x.review_id)+'</option>').join("")+'</select></label>'+
      '<div class="obx-focusline"><article><span class="obx-eyebrow">WHY WE PASSED</span><strong>'+
      esc(explain.title)+'</strong><p>'+esc(explain.explanation)+'</p>'+
      (explain.reasons.length?'<small>Documented: '+explain.reasons.map(esc).join(" · ")+'</small>':'<small>No documented reason available.</small>')+
      '<p class="obx-muted">Source: '+esc(explain.source)+' · '+esc(explain.truth_mode)+'</p></article>'+
      '<article><span class="obx-eyebrow">PERFORMANCE BY RECORD CLASS</span><strong>Keep truth modes separate</strong>'+
      '<div class="obx-stat-rail">'+report.groups.map(g=>'<div class="obx-stat"><strong>'+
      g.records+'</strong><span>'+esc(g.mode)+' records</span><small>'+g.documented_returns+
      ' documented returns</small></div>').join("")+'</div><p>Figures here are record counts, not verified brokerage P&amp;L.</p></article></div>'+
      '<h3>Evidence lifecycle · not a simulated timeline</h3><div class="obx-orbit-stage" aria-label="Documented lifecycle stages">'+
      chosen.stages.map(s=>'<div class="obx-orbit-node" data-state="'+esc(s.state)+'"><small>'+esc(s.name)+'</small><i aria-hidden="true"></i><small>'+
      esc(s.time||"Not documented")+'</small></div>').join("")+'</div>')+
      '<div class="obx-drawer-actions"><button class="obx-button" type="button" data-obx-open="soulaana">Explain the evidence</button>'+
      '<button class="obx-button" type="button" data-obx-research>Open session research shelf</button>'+
      '<button class="obx-button" type="button" data-obx-focus-toggle aria-pressed="'+String(prefs.focus)+'">Focus View</button></div></section>';
    const select=$("obxReviewSelect");if(select)select.addEventListener("change",()=>{selectedId=select.value;renderReview();});
  }
  function renderTrade(){const mount=$("obBetaFeatureMount");if(!mount)return;
    const api=global.OBTradeCenter;const current=api&&typeof api.getState==="function"?obj(api.getState()):{};
    const trade=obj(current.activeTrade), symbol=string(trade.symbol);
    const known=reviewRows().find(r=>r.symbol===symbol);const life=known?C.orbit(known):null;
    mount.innerHTML='<section class="obx-card" aria-label="Trade research shelf">'+
      '<div class="obx-feature-head"><div><span class="obx-eyebrow">TRADE CENTER · RESEARCH SHELF</span>'+
      '<h2>My Plays · Flight Path</h2></div>'+statusMarkup()+'</div>'+
      '<p>Use the existing canonical Trade Center for contract research and Paper workflow. Saved research notes are not orders or broker receipts.</p>'+
      (life?'<div class="obx-orbit-stage" aria-label="Documented trade lifecycle">'+life.stages.map(s=>
      '<div class="obx-orbit-node" data-state="'+esc(s.state)+'"><small>'+esc(s.name)+'</small><i aria-hidden="true"></i><small>'+esc(s.time||"Unknown")+'</small></div>').join("")+'</div>':
      '<p class="obx-quiet">No matching canonical review record for this active symbol. The existing Flight Path stays available; no fill or exit history is invented.</p>')+
      '<div class="obx-drawer-actions"><button type="button" class="obx-button primary" data-obx-research>My Plays / Research Shelf</button>'+
      '<a class="obx-button" href="/ob/review-center">Open Review Center →</a></div></section>';
  }
  function renderOwner(){const mount=$("obBetaFeatureMount");if(!mount)return;
    mount.innerHTML='<section class="obx-card" aria-label="Owner intelligence source guard">'+
      '<div class="obx-feature-head"><div><span class="obx-eyebrow">OWNER · EVIDENCE OBSERVATORY</span>'+
      '<h2>Operational intelligence, not capital invention</h2></div>'+statusMarkup()+'</div>'+
      '<p>Review Center separates official, Paper and private rehearsal records. No balance, investable cash or lender readiness can be constructed from this panel.</p>'+
      '<div class="obx-drawer-actions"><a class="obx-button primary" href="/ob/review-center">Performance by truth mode →</a>'+
      '<button class="obx-button" type="button" data-obx-open="alerts">Source health alerts</button></div></section>';
  }
  function update(){if(room==="dashboard")renderDashboard();else if(room==="review-center")renderReview();
    else if(room==="trade-center")renderTrade();else if(room==="owner-console")renderOwner();
    const badge=$("obxAlertCount");if(badge)badge.textContent=String(alertRows().filter(x=>!x.dismissible||!readIds.includes(x.id)).length);
  }
  function createDock(){if($("obBetaDock"))return;const node=document.createElement("nav");
    node.className="obx-dock";node.id="obBetaDock";node.setAttribute("aria-label","Observatory quick actions");
    node.innerHTML='<button type="button" data-obx-open="soulaana">✦ Soulaana</button>'+
      '<button type="button" data-obx-open="alerts">Alerts <span id="obxAlertCount">0</span></button>'+
      '<button type="button" data-obx-research>My Plays</button>'+
      '<button type="button" data-obx-open="settings">Settings</button>';document.body.appendChild(node);
    if(room==="dashboard"&&document.documentElement.classList.contains("ob-entry-pending"))node.hidden=true;
    global.addEventListener("ob:arrival-complete",()=>{node.hidden=false;});
  }
  function boot(){document.body.dataset.obFocusView=prefs.focus?"true":"false";
    document.body.dataset.obCompact=prefs.compact?"true":"false";createDock();
    document.addEventListener("click",e=>{const el=e.target.closest("[data-obx-open]");
      if(el){openDrawer(el.dataset.obxOpen);return;}
      if(e.target.closest("[data-obx-research]")&&global.OBBetaResearch)global.OBBetaResearch.open();
      if(e.target.closest("[data-obx-focus-toggle]"))focus(!prefs.focus);
    });
    update();
  }
  global.addEventListener("obEngineFeedAdapterUpdated",update);
  global.addEventListener("ob:review-center-projection-updated",e=>{review=obj(e.detail);
    review.loaded=true;selectedId=null;update();});
  global.addEventListener("ob:trade-center:ready",update);
  global.OBBetaExperience=Object.freeze({update,openDrawer,alertRows,getPreferences:()=>({...prefs}),
    safety:{source_only:true,no_broker_submission:true,no_manual_live_unlock:true,
      no_capital_movement:true,quiet_cannot_suppress_safety:true}});
  if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",boot,{once:true});else boot();
})(window);
