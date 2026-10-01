// Fiction-only browser race/role-scoping regression. No DOM library, network or real users.
"use strict";
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

class FakeNode {
  constructor(tag = "div") {
    this.tagName = tag.toUpperCase();
    this.children = [];
    this.listeners = Object.create(null);
    this.textContent = "";
    this.value = "";
    this.disabled = false;
    this.classes = new Set();
    this.classList = {
      add: (...items) => items.forEach(item => this.classes.add(item)),
      remove: (...items) => items.forEach(item => this.classes.delete(item)),
      toggle: (name, force) => {
        const include = force === undefined ? !this.classes.has(name) : !!force;
        if (include) this.classes.add(name); else this.classes.delete(name);
        return include;
      },
      contains: name => this.classes.has(name),
    };
  }
  set className(value) { this.classes = new Set(String(value).split(/\s+/).filter(Boolean)); }
  get className() { return [...this.classes].join(" "); }
  append(...items) {
    for (const item of items) {
      this.children.push(item);
      if (this.tagName === "SELECT" && !this.value && item.tagName === "OPTION") {
        this.value = item.value;
      }
    }
  }
  replaceChildren(...items) {
    this.children = [];
    if (this.tagName === "SELECT") this.value = "";
    this.append(...items);
  }
  addEventListener(name, fn) { this.listeners[name] = fn; }
  querySelector() { return null; }
  reset() {}
  fire(name) {
    if (!this.listeners[name]) throw new Error("Missing listener " + name);
    return this.listeners[name]({preventDefault() {}, submitter: this});
  }
}
const nodes = new Map();
const $ = id => {
  if (!nodes.has(id)) nodes.set(id, new FakeNode(
    ["property-choice", "unit-choice"].includes(id) ? "select" : "div"
  ));
  return nodes.get(id);
};
const document = {
  querySelector: selector => {
    if (selector === 'meta[name="grounds-csrf"]') return {content: "synthetic-csrf"};
    throw new Error("Unexpected selector: " + selector);
  },
  createElement: tag => new FakeNode(tag),
  getElementById: $,
};
const tick = () => new Promise(resolve => setImmediate(resolve));
async function settle() { for (let i = 0; i < 12; i++) await tick(); }
function workspace(prop, unit) {
  return {
    source:"grounds", property_ref:prop, unit_ref:unit, role:"resident",
    lease:{lease_ref:prop+"-lease",start_on:"2026-09-28",end_on:"2027-09-27"},
    work_orders:[], notices:[{
      notice_ref:"n-"+prop,headline:"PRIVATE_NOTICE_"+prop,
      body:"For "+prop+" only",published_at:"2026-09-28T00:00:00Z",read_in_app:0,
    }],
    soulaana:{message:"PRIVATE_CONTEXT_"+prop,next_useful_action:"Read current notice"},
  };
}
const response = value => ({ok:true,status:200,json:async()=>value});
let lateP2 = null;
let holdP2 = false;
let p2Value = workspace("p2","u2");
let lateP1 = null;
let holdP1 = false;
async function fetchMock(url) {
  if (url.endsWith("/api/me")) return response({
    role:"resident",property_refs:["p1","p2"],unit_refs:["u1","u2"],
  });
  if (url.includes("/api/workspace?")) {
    const qs = new URL(url,"https://example.test").searchParams;
    const prop=qs.get("property_ref"),unit=qs.get("unit_ref");
    if (prop === "p2") {
      if (holdP2) return new Promise(resolve => {lateP2 = () => resolve(response(p2Value));});
      return response(p2Value);
    }
    if (prop === "p1" && holdP1)
      return new Promise(resolve => {lateP1 = () => resolve(response(workspace("p1","u1")));});
    return response(workspace(prop,unit));
  }
  if (url.includes("/api/rent?")) return response({
    status:"not_connected",amount_due_cents:null,checkout_url:null,
    checkout_execution_enabled:false,
  });
  throw new Error("Unexpected URL "+url);
}
async function main() {
  const source = fs.readFileSync(path.join(__dirname,"..","ui","app.js"),"utf8");
  const context = {
    document, fetch:fetchMock, URL, URLSearchParams, console,
    crypto:{randomUUID:()=> "00000000-0000-4000-8000-000000000001"},
  };
  vm.runInNewContext(source,context,{filename:"grounds/ui/app.js"});
  await settle();
  assert.equal($("content").classList.contains("hidden"),false,"first exact home loads");
  assert.equal($("lease-details").children.length,2,"first lease rendered");
  assert.equal($("soulaana-message").textContent,"PRIVATE_CONTEXT_p1");

  // A property switch must erase all old private text synchronously, not
  // leave old lease/notices visible while a second server request is pending.
  holdP2=true;
  $("property-choice").value="p2";
  $("unit-choice").value="u2";
  $("property-choice").fire("change");
  assert.equal($("content").classList.contains("hidden"),true,"old content hidden immediately");
  assert.equal($("lease-details").children.length,0,"prior lease cleared immediately");
  assert.equal($("notice-list").children.length,0,"prior notices cleared immediately");
  assert.equal($("soulaana-message").textContent.includes("PRIVATE_CONTEXT_p1"),false);
  await settle();
  assert.equal(typeof lateP2,"function");

  // A server response that claims the wrong property/unit must not render.
  p2Value=workspace("p1","u1");
  lateP2(); await settle();
  assert.equal($("content").classList.contains("hidden"),true);
  assert.equal($("locked").classList.contains("hidden"),false);
  assert.equal($("lease-details").children.length,0);

  // A subsequent current, correct response recovers without stale contents.
  holdP2=false;p2Value=workspace("p2","u2");
  $("refresh").fire("click");await settle();
  assert.equal($("content").classList.contains("hidden"),false);
  assert.equal($("soulaana-message").textContent,"PRIVATE_CONTEXT_p2");

  // A late response from a previous property cannot overwrite current data.
  holdP1=true;
  $("property-choice").value="p1";$("unit-choice").value="u1";
  $("property-choice").fire("change");await settle();
  assert.equal(typeof lateP1,"function");
  $("property-choice").value="p2";$("unit-choice").value="u2";
  $("property-choice").fire("change");await settle();
  assert.equal($("soulaana-message").textContent,"PRIVATE_CONTEXT_p2");
  lateP1(); await settle();
  assert.equal($("soulaana-message").textContent,"PRIVATE_CONTEXT_p2");
  assert.equal($("content").classList.contains("hidden"),false);

  // The zero-balance claim must never be displayed from a disconnected source.
  assert.equal($("rent-message").textContent.includes("Nothing is due"),false);
  assert.equal($("rent-service-status").textContent,"Unavailable");
  process.stdout.write("PASS: immediate scope clearing, wrong-context denial, late-response isolation, truthful disconnected rent\n");
}
main().catch(e => {console.error(e);process.exitCode=1;});
