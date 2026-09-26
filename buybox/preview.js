"use strict";
// Presentation-only synthetic preview. No live feeds, account balances, or authorization.
const verticals = [
  ["all","All opportunities"],["atm","ATMs"],["multifamily","Apartments"],
  ["commercial","Commercial"],["laundromat","Laundromats"],["land_farm","Land / Farms"],
  ["business","Businesses"],["equipment","Equipment"]
];
const opportunities = [
  {id:"atm-1",type:"atm",name:"Georgia ATM Route",area:"Georgia",price:95000,units:"8 machines",icon:"▣",status:"missing",label:"Missing evidence",confidence:62,risk:"Ownership is verified for only six of eight machines.",next:"Request a revised serial-numbered asset schedule.",net:"Unverified",visual:"ROUTE"},
  {id:"atm-2",type:"atm",name:"Regional ATM Portfolio",area:"Southeast",price:145000,units:"16 machines",icon:"▤",status:"review",label:"Review",confidence:74,risk:"Location concentration needs additional diligence.",next:"Request location-by-location transaction history.",net:"Unverified",visual:"PORTFOLIO"},
  {id:"multi-1",type:"multifamily",name:"Garden Apartment Group",area:"Georgia",price:2350000,units:"25 units",icon:"▥",status:"missing",label:"Missing evidence",confidence:44,risk:"Rent roll and condition evidence are incomplete.",next:"Request current rent roll and T12.",net:"Unverified",visual:"PROPERTY"},
  {id:"comm-1",type:"commercial",name:"Commercial Operations Site",area:"Georgia",price:480000,units:"Single property",icon:"▧",status:"review",label:"Review",confidence:57,risk:"Lease and insurance details need verification.",next:"Request executed lease schedule.",net:"Unverified",visual:"PROPERTY"},
  {id:"laundry-1",type:"laundromat",name:"Neighborhood Laundry",area:"Southeast",price:180000,units:"Operating business",icon:"◉",status:"missing",label:"Missing evidence",confidence:39,risk:"Utility expenses and machine condition are unknown.",next:"Request utility and equipment records.",net:"Unverified",visual:"BUSINESS"},
  {id:"farm-1",type:"land_farm",name:"Agricultural Parcel",area:"Southeast",price:265000,units:"Land parcel",icon:"✳",status:"review",label:"Review",confidence:52,risk:"Water, access and zoning still need independent confirmation.",next:"Obtain water-rights and access evidence.",net:"Not applicable",visual:"LAND"},
  {id:"biz-1",type:"business",name:"Established Local Business",area:"Southeast",price:225000,units:"Company acquisition",icon:"◇",status:"missing",label:"Missing evidence",confidence:34,risk:"Reported cash flow has not been reconciled.",next:"Request statements and tax records.",net:"Unverified",visual:"BUSINESS"},
  {id:"equip-1",type:"equipment",name:"Operations Equipment Package",area:"Georgia",price:42000,units:"Equipment portfolio",icon:"⚙",status:"review",label:"Review",confidence:48,risk:"Ownership and remaining useful life require evidence.",next:"Request serial-numbered ownership records.",net:"Not applicable",visual:"EQUIPMENT"}
];
let active = "all";
let selected = new Set();
const $ = id => document.getElementById(id);
const usd = amount => new Intl.NumberFormat("en-US",{style:"currency",currency:"USD",maximumFractionDigits:0}).format(amount);
function element(tag, cls, value) {
  const node=document.createElement(tag); if(cls) node.className=cls;
  if(value!==undefined) node.textContent=value; return node;
}
function renderFilters() {
  const host=$("filters");host.replaceChildren();
  verticals.forEach(([key,label])=>{
    const button=element("button","",label);button.type="button";button.setAttribute("aria-pressed",String(active===key));
    button.addEventListener("click",()=>{active=key;renderFilters();renderCards()});
    host.append(button);
  });
}
function renderCards() {
  const needle=$("search-box").value.trim().toLowerCase();
  const visible=opportunities.filter(o=>(active==="all"||o.type===active)&&
    (o.name+" "+o.area+" "+o.type).toLowerCase().includes(needle));
  $("count").textContent=visible.length+" synthetic opportunities";
  const host=$("cards");host.replaceChildren();
  for(const o of visible){
    const article=element("article","deal");
    const visual=element("div","visual");visual.append(element("span","",o.icon),element("span","",o.visual));article.append(visual);
    const content=element("div","content");content.append(element("h3","",o.name),element("div","subtitle",o.area+" • "+o.units));
    const metrics=element("div","metrics");
    const ask=element("div");ask.append(element("b","",usd(o.price)),element("small","",""));ask.lastChild.textContent="Asking price";
    const conf=element("div");conf.append(element("b","",o.confidence+"%"),element("small","Evidence confidence"));
    metrics.append(ask,conf);content.append(metrics);
    content.append(element("span","status "+o.status,o.label),element("p","risk",o.risk));
    const actions=element("div","deal-actions");
    const open=element("button","", "Open dossier ↗");open.addEventListener("click",()=>openDossier(o.id));
    const compare=element("button","",selected.has(o.id)?"✓ Selected":"+ Compare");
    compare.setAttribute("aria-pressed",String(selected.has(o.id)));
    compare.addEventListener("click",()=>{
      if(selected.has(o.id)) selected.delete(o.id);
      else if(selected.size<4) selected.add(o.id);
      else {compare.textContent="Limit: 4 deals";return}
      renderCards();renderCompare();
    });
    actions.append(open,compare);content.append(actions);article.append(content);host.append(article);
  }
  if(!visible.length) host.append(element("p","","No matching opportunities. Try a different category or search."));
}
function openDossier(id) {
  const o=opportunities.find(x=>x.id===id);if(!o)return;
  $("dossier-title").textContent=o.name;
  const host=$("dossier-body");host.replaceChildren();
  const grid=element("div","dossier-grid");
  for(const [label,value] of [["Asking price",usd(o.price)],["Category",verticals.find(x=>x[0]===o.type)[1]],
       ["Evidence confidence",o.confidence+"%"],["Current judgment",o.label]]){
    const tile=element("div","dossier-panel");tile.append(element("small","",label),element("strong","",value));grid.append(tile);
  }
  host.append(grid);
  const explanation=element("div","soulaana");
  explanation.append(element("strong","","✧ Soulaana — illustrative briefing"),
    element("p","",o.risk),element("p","","Next useful action: "+o.next));
  host.append(explanation);
  host.append(element("p","subtitle","This is a UI demonstration with synthetic opportunities. No score, financial statement, Teller balance or Tower authorization is live."));
  $("dossier").showModal();
}
function renderCompare() {
  const host=$("compare-surface");host.replaceChildren();
  const chosen=opportunities.filter(o=>selected.has(o.id));
  if(chosen.length<2) {host.append(element("p","",chosen.length===1?"Select at least one more opportunity.":"Choose two to four opportunities using their Compare controls."));return;}
  for(const o of chosen){
    const tile=element("div","comparison");tile.append(element("h3","",o.name),element("small","",o.units),
      element("h2","",usd(o.price)),element("small","",o.label+" • "+o.confidence+"% evidence confidence"));
    host.append(tile);
  }
}
$("search-box").addEventListener("input",renderCards);
$("reset").addEventListener("click",()=>{$("search-box").value="";active="all";renderFilters();renderCards()});
$("focus-toggle").addEventListener("click",()=>{
  const on=document.body.classList.toggle("focus");
  $("focus-toggle").setAttribute("aria-pressed",String(on));
  $("focus-toggle").textContent=on?"Exit focus mode":"Focus mode";
});
$("close-dossier").addEventListener("click",()=>$("dossier").close());
$("show-changes").addEventListener("click",()=>$("changes").showModal());
$("close-changes").addEventListener("click",()=>$("changes").close());
$("compare").addEventListener("click",()=>document.getElementById("compare-surface").scrollIntoView({behavior:"smooth",block:"center"}));
document.querySelectorAll("[data-open]").forEach(button=>button.addEventListener("click",()=>openDossier(button.dataset.open)));
renderFilters();renderCards();renderCompare();
