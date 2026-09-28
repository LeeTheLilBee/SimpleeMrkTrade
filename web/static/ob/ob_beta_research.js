/* OBUX121–125: My Plays / Analysis Shelf / private reflection.
 * A volatile user-authored scratchpad. NOT Archive Vault, a broker ledger, or official P&L.
 */
(function (global) {
  "use strict";
  const C=global.OBBetaIntelligenceContract;if(!C)return;
  const KEY="ob.beta.x121.research.v1";
  const $=id=>document.getElementById(id);
  const esc=v=>String(v==null?"":v).replace(/&/g,"&amp;").replace(/</g,"&lt;")
    .replace(/>/g,"&gt;").replace(/"/g,"&quot;").replace(/'/g,"&#39;");
  const txt=v=>typeof v==="string"?v.trim():"";
  function session(){try{return String(global.OBSessionState.snapshot().ephemeral.sessionId||"");}catch(_){return "";}}
  const SID=session();
  function state(){try{const v=JSON.parse(global.sessionStorage.getItem(KEY)||"null");return v&&v.sessionId===SID&&Array.isArray(v.notes)?v.notes:[];}catch(_){return [];}}
  function persist(notes){try{global.sessionStorage.setItem(KEY,JSON.stringify({schema:1,sessionId:SID,notes}));return true;}catch(_){return false;}}
  function noteId(){return global.crypto&&global.crypto.randomUUID?global.crypto.randomUUID():
    "note-"+Date.now().toString(36)+"-"+Math.random().toString(36).slice(2,9);}
  const VALID=/^[A-Z0-9][A-Z0-9.-]{0,11}$/;
  function normalize(form){
    const symbol=txt(form.symbol).toUpperCase();
    if(!VALID.test(symbol))throw new Error("Enter a valid symbol (1–12 characters).");
    const thesis=txt(form.thesis).slice(0,600);
    if(!thesis)throw new Error("Enter a research question or observation.");
    const mode=form.mode==="Paper"?"Paper":"Survey";
    return Object.freeze({id:noteId(),symbol,mode,thesis,source_ref:txt(form.source_ref).slice(0,180),
      linked_review_id:txt(form.linked_review_id).slice(0,150),
      type:"user-authored-session-note",created_at:new Date().toISOString(),
      is_official:false,is_broker_receipt:false,is_backtest:false});
  }
  function add(form){const item=normalize(form),notes=state();if(notes.length>=15)throw new Error("Maximum 15 tab-local research notes. Export or clear notes before adding more.");
    if(!persist([item,...notes]))throw new Error("Session storage is unavailable. The note was not saved.");
    return item;
  }
  function remove(id){persist(state().filter(n=>n.id!==id));}
  function clear(){try{global.sessionStorage.removeItem(KEY);}catch(_){}}
  let host=null,prior=null;
  function close(){if(!host)return;host.remove();host=null;document.removeEventListener("keydown",keys);if(prior&&prior.focus)prior.focus();}
  function keys(e){if(!host)return;if(e.key==="Escape"){close();return;}if(e.key!=="Tab")return;
    const focusable=[...host.querySelectorAll('button:not([disabled]),a[href],input:not([disabled]),textarea:not([disabled]),select:not([disabled])')]
      .filter(x=>x.offsetParent!==null);if(!focusable.length)return;
    if(e.shiftKey&&document.activeElement===focusable[0]){e.preventDefault();focusable[focusable.length-1].focus();}
    else if(!e.shiftKey&&document.activeElement===focusable[focusable.length-1]){e.preventDefault();focusable[0].focus();}
  }
  function rows(){const notes=state();return notes.length?notes.map(n=>
    '<article class="obx-drawer-item"><span class="obx-eyebrow">'+esc(n.mode)+' · SESSION RESEARCH</span><strong>'+esc(n.symbol)+'</strong>'+
    '<p>'+esc(n.thesis)+'</p><small>Reference: '+esc(n.source_ref||"Not recorded")+' · '+esc(n.created_at)+'</small>'+
    '<div class="obx-drawer-actions"><button class="obx-button" type="button" data-obx-delete="'+esc(n.id)+'">Delete note</button></div></article>').join(""):
    '<div class="obx-quiet">Your Research Shelf is empty. This is personal scratch work; no strategy, return or trade will be fabricated.</div>';
  }
  function selection(name){return '<label class="obx-field">'+name+'<select id="obxCompare'+name+'"><option value="">Choose a note</option>'+
    state().map(n=>'<option value="'+esc(n.id)+'">'+esc(n.symbol)+' · '+esc(n.mode)+' · '+esc(n.created_at)+'</option>').join("")+'</select></label>';}
  function compare(){const l=state().find(n=>n.id===$("obxCompareLeft").value);
    const r=state().find(n=>n.id===$("obxCompareRight").value);
    const area=$("obxComparison");if(!l||!r||l.id===r.id){
      area.textContent="Choose two distinct research notes to compare their written assumptions.";return;}
    const c=C.strategyComparison(l,r);area.innerHTML=
      '<div class="obx-focusline"><article><strong>'+esc(c.left.symbol)+'</strong><p>'+esc(c.left.thesis)+'</p>'+
      '<small>'+esc(c.left.mode)+' · '+esc(c.left.source_ref)+'</small></article>'+
      '<article><strong>'+esc(c.right.symbol)+'</strong><p>'+esc(c.right.thesis)+'</p>'+
      '<small>'+esc(c.right.mode)+' · '+esc(c.right.source_ref)+'</small></article></div>'+
      '<p class="obx-muted">'+esc(c.explanation)+'</p>';
  }
  function exportSession(){const data={schema:"OB-RESEARCH-SHELF-EXPORT-V1",exported_at:new Date().toISOString(),
    label:"User-authored session notes only; not an official trading record",notes:state()};
    const blob=new Blob([JSON.stringify(data,null,2)],{type:"application/json"});
    const url=URL.createObjectURL(blob);const link=document.createElement("a");
    link.href=url;link.download="ob-session-research-notes.json";link.click();
    setTimeout(()=>URL.revokeObjectURL(url),1000);
  }
  function markup(){return '<aside class="obx-drawer" role="dialog" aria-modal="true" aria-label="My Plays research shelf">'+
    '<div class="obx-drawer-head"><div><span class="obx-eyebrow">THE OBSERVATORY · MY PLAYS</span>'+
    '<h2>Analysis Shelf</h2></div><button class="obx-button" data-obx-close type="button">Close ×</button></div>'+
    '<p>Session-only research and private reflections. This is NOT Archive Vault storage and never becomes official trade evidence automatically.</p>'+
    '<form id="obxResearchForm"><label class="obx-field">Symbol<input name="symbol" maxlength="12" required autocomplete="off" placeholder="e.g. a studied ticker" /></label>'+
    '<label class="obx-field">Context<select name="mode"><option value="Survey">Survey observation</option><option value="Paper">Paper research</option></select></label>'+
    '<label class="obx-field">What are you studying?<textarea name="thesis" maxlength="600" required placeholder="Write your observation, question, or rule."></textarea></label>'+
    '<label class="obx-field">Optional source/evidence reference<input name="source_ref" maxlength="180" placeholder="Your own citation or saved reference" /></label>'+
    '<div class="obx-drawer-actions"><button class="obx-button primary" type="submit">Save in this tab</button></div>'+
    '<p class="obx-muted" id="obxResearchStatus" role="status">Avoid confidential account details. Notes clear on OB session reset and may not survive browser restoration.</p></form>'+
    '<div class="obx-drawer-list" id="obxResearchRows">'+rows()+'</div>'+
    '<h3>Compare two of My Plays</h3><p class="obx-muted">Compare only your own written observations. Not a backtest, score or recommendation.</p>'+
    selection("Left")+selection("Right")+
    '<button class="obx-button" type="button" data-obx-compare>Compare notes</button><div id="obxComparison" class="obx-quiet">Choose two different entries.</div>'+
    '<div class="obx-drawer-actions"><button class="obx-button" type="button" data-obx-export>Export my session notes</button>'+
    '<button class="obx-button" type="button" data-obx-clear>Clear all notes</button></div></aside>';
  }
  function rerender(){const r=$("obxResearchRows");if(r)r.innerHTML=rows();const x=$("obxResearchStatus");if(x)x.textContent=state().length+" session-only notes stored in this tab.";}
  function open(){if(!SID)return; if(host)close();prior=document.activeElement;host=document.createElement("div");host.className="obx-cover";
    host.id="obResearchDrawer";host.innerHTML=markup();document.body.appendChild(host);
    document.addEventListener("keydown",keys);
    host.addEventListener("click",e=>{
      if(e.target===host||e.target.closest("[data-obx-close]")){close();return;}
      const del=e.target.closest("[data-obx-delete]");if(del){remove(del.dataset.obxDelete);rerender();return;}
      if(e.target.closest("[data-obx-compare]")){compare();return;}
      if(e.target.closest("[data-obx-export]")){exportSession();return;}
      if(e.target.closest("[data-obx-clear]")){clear();close();open();}
    });
    host.querySelector("form").addEventListener("submit",e=>{
      e.preventDefault();const f=e.currentTarget;try{const item=add(Object.fromEntries(new FormData(f).entries()));f.reset();rerender();
        const st=$("obxResearchStatus");st.textContent=item.symbol+" saved in this tab only.";
      }catch(err){$("obxResearchStatus").textContent=String(err.message||err);}
    });
    host.querySelector("[data-obx-close]").focus();
  }
  global.addEventListener("ob:session-cleared",clear);
  global.OBBetaResearch=Object.freeze({open,add,list:()=>[...state()],remove,clear,compare:C.strategyComparison,
    safety:{session_only:true,durable_archive:false,no_broker_records:true,no_order_execution:true}});
})(window);
