"use strict";
(() => {
  const root = "/grounds";
  const csrf = document.querySelector('meta[name="grounds-csrf"]').content;
  const $ = id => document.getElementById(id);
  const state = { me: null, view: null, property: "", unit: "", busy: false, maintenanceRetry: null };
  function el(tag, text, klass) {
    const node = document.createElement(tag);
    if (text !== undefined && text !== null) node.textContent = String(text);
    if (klass) node.className = klass;
    return node;
  }
  function clear(node) { node.replaceChildren(); }
  function message(text, isError = false) {
    const alert = $("alert"); alert.textContent = text; alert.className = "alert " + (isError ? "error" : "ok");
  }
  function asDate(value) {
    if (!value) return "Not recorded";
    const date = new Date(value);
    return Number.isNaN(date.getTime()) ? String(value) : date.toLocaleString();
  }
  function newIdempotencyKey() {
    if (!globalThis.crypto || typeof globalThis.crypto.randomUUID !== "function") {
      throw new Error("A secure browser connection is required to create new requests.");
    }
    return globalThis.crypto.randomUUID();
  }
  async function request(path, data, idempotencyKey) {
    const options = { credentials: "same-origin", cache: "no-store", headers: { "Accept": "application/json" } };
    if (data !== undefined) {
      options.method = "POST";
      options.headers["Content-Type"] = "application/json";
      options.headers["X-Grounds-CSRF"] = csrf;
      if (idempotencyKey !== undefined) options.headers["X-Grounds-Idempotency-Key"] = idempotencyKey;
      options.body = JSON.stringify(data);
    }
    let response, result;
    try {
      response = await fetch(root + "/api/" + path, options);
      result = await response.json();
    } catch {
      throw new Error("Could not reach Grounds. Your changes may not have been saved.");
    }
    if (!response.ok) {
      if (response.status === 401) throw new Error("Your Tower session is no longer available. Return to Tower to sign in.");
      if (response.status === 403) throw new Error("Your session security check failed. Reload your Tower-approved page.");
      if (response.status === 404) throw new Error("That record is not available to your current access.");
      if (response.status === 409) throw new Error("The record changed or the action is not currently permitted. Refresh and review.");
      throw new Error("Grounds could not complete that request. No confirmation was issued.");
    }
    return result;
  }
  function stat(label, value) {
    const box = el("div", null, "stat"); box.append(el("strong", value), el("span", label)); return box;
  }
  function badge(value, urgent = false) { return el("span", value, "pill " + (urgent ? "priority" : "muted")); }
  function makeButton(label, onClick, klass = "outline") {
    const b = el("button", label, klass); b.type = "button";
    b.addEventListener("click", async () => {
      if (state.busy) return;
      state.busy = true; b.disabled = true;
      try { await onClick(); } catch (error) { message(error.message, true); }
      finally { b.disabled = false; state.busy = false; }
    });
    return b;
  }
  function addOptions(target, items) {
    clear(target);
    for (const item of items) {
      const option = el("option", item); option.value = item; target.append(option);
    }
    target.disabled = items.length === 0;
  }
  function selected() {
    state.property = $("property-choice").value || "";
    state.unit = $("unit-choice").value || "";
  }
  async function refresh() {
    selected();
    if (!state.property) return;
    const qs = new URLSearchParams({ property_ref: state.property });
    if (state.me.role === "resident") {
      if (!state.unit) return;
      qs.set("unit_ref", state.unit);
    }
    try {
      const data = await request("workspace?" + qs);
      state.view = data; render(data);
      $("property-state").textContent = "Current";
    } catch (error) {
      $("content").classList.add("hidden"); $("locked").classList.remove("hidden");
      $("locked-reason").textContent = error.message;
      message(error.message, true);
    }
  }
  function render(data) {
    if (data.locked) {
      $("content").classList.add("hidden"); $("locked").classList.remove("hidden");
      $("locked-reason").textContent = data.reason || "This role requires an exact Tower assignment.";
      return;
    }
    $("locked").classList.add("hidden"); $("content").classList.remove("hidden");
    $("role-badge").textContent = data.role.replaceAll("_", " ");
    const summary = $("summary"); clear(summary);
    const counts = data.operating_snapshot?.counts || data.property_pulse || {};
    if (data.role === "resident") {
      summary.append(stat("MY REQUESTS", data.work_orders.length),
        stat("VISIBLE NOTICES", data.notices.length),
        stat("CURRENT LEASE", data.lease?.end_on || "Active"));
    } else if (Object.keys(counts).length) {
      summary.append(stat("UNITS", counts.units ?? "—"),
        stat("OPEN WORK", counts.open_work_orders ?? "—"),
        stat("URGENT / UNTRIAGED", counts.untriaged_urgent_work ?? "—"));
    } else if (data.work_orders) {
      summary.append(stat("AUTHORIZED WORK", data.work_orders.length));
    } else if (data.units) { summary.append(stat("RECORDED UNITS", data.units.length)); }
    $("rent-panel").classList.toggle("hidden", data.role !== "resident");
    $("request-panel").classList.toggle("hidden", data.role !== "resident");
    $("notices-panel").classList.toggle("hidden", data.role !== "resident");
    if (data.role === "resident") {
      const lease = $("lease-details"); clear(lease);
      lease.append(el("span", "From: " + data.lease.start_on), el("span", "Through: " + data.lease.end_on));
      $("rent-message").textContent = "Teller has not supplied an authenticated invoice. Grounds cannot display an amount due or accept a payment yet.";
      renderNotices(data.notices || []);
    }
    const soulaana = data.soulaana;
    $("soulaana-message").textContent = soulaana?.message || "No explanation is available from this source context.";
    $("soulaana-next").textContent = soulaana?.next_useful_action ? "NEXT: " + soulaana.next_useful_action : "";
    renderWork(data);
  }
  function renderNotices(notices) {
    const target = $("notice-list"); clear(target);
    if (!notices.length) target.append(el("p", "No visible notices for your current lease.", "footnote"));
    for (const notice of notices) {
      const card = el("article", null, "item"); card.append(el("h3", notice.headline), el("p", notice.body),
        el("span", asDate(notice.published_at), "meta"));
      const actions = el("div", null, "actions");
      if (!notice.read_in_app) {
        actions.append(makeButton("Mark read in Grounds", async () => {
          await request("notice-read", { property_ref: state.property, unit_ref: state.unit, notice_ref: notice.notice_ref });
          message("Marked read inside Grounds. This is not delivery or legal service.");
          await refresh();
        }));
      } else actions.append(badge("Read in Grounds"));
      card.append(actions); target.append(card);
    }
  }
  const managerNext = {
    submitted: "received", received: "under_review", under_review: "scheduled",
    completed: "confirmation", confirmation: "closed", reopened: "under_review",
    waiting: "scheduled"
  };
  const techNext = { assigned: "in_progress", in_progress: "completed", waiting: "in_progress" };
  function renderWork(data) {
    const target = $("work-list"); clear(target);
    const works = data.work_orders || [];
    if (data.units) {
      $("work-heading").textContent = "Recorded property units";
      $("work-count").textContent = String(data.units.length);
      for (const unit of data.units) {
        const card = el("article", null, "item");
        card.append(el("h3", (unit.building_label || "Building") + " · " + (unit.unit_label || unit.unit_ref)),
          el("p", "Recorded lifecycle: " + unit.lifecycle));
        target.append(card);
      }
      return;
    }
    $("work-heading").textContent = data.role === "resident" ? "Your maintenance" : "Authorized maintenance";
    $("work-count").textContent = String(works.length);
    if (!works.length) { target.append(el("p", "No work records are available in your current scope.", "footnote")); return; }
    for (const work of works) {
      const card = el("article", null, "item"); const title=el("div", null, "item-top");
      title.append(el("h3", (work.category || "Work") + " · " + (work.unit_ref || data.unit_label || "Your unit")),
        badge(work.state, !!work.emergency_flag && work.state === "submitted"));
      card.append(title, el("p", "Status: " + work.state + (work.emergency_flag ? " · Urgency flagged for human review" : "")),
        el("span", "Updated: " + asDate(work.updated_at), "meta"));
      const actions=el("div", null, "actions");
      actions.append(makeButton("View authorized details", async () => {
        const detail=await request("work?" + new URLSearchParams({work_ref:work.work_ref}));
        message(detail.category + ": " + detail.description);
      }));
      if (data.role === "resident") {
        actions.append(makeButton("Request an appointment", async () => showAppointmentForm(card,work)));
        actions.append(makeButton("Entry preference", async () => showPreferenceForm(card,work)));
        actions.append(makeButton("Appointment status", async () => showAppointments(card,work)));
      } else if (["property_manager","maintenance_supervisor","owner"].includes(data.role)) {
        if (work.emergency_flag && work.state === "submitted") {
          actions.append(makeButton("Record urgent human review", async () => {
            await request("urgency/review",{work_ref:work.work_ref,assessed_urgency:"priority"});
            message("Human priority review recorded. This did not dispatch emergency services.");
            await refresh();
          }));
        }
        const next=managerNext[work.state];
        if (next && work.revision !== undefined) actions.append(makeButton("Move to " + next.replaceAll("_", " "), async () => {
          await request("work/transition",{work_ref:work.work_ref,next_state:next,expected_revision:work.revision});
          message("Work state changed in Grounds. No notification has been delivered.");
          await refresh();
        }));
        actions.append(makeButton("Appointment status", async () => showAppointments(card,work)));
      } else if (data.role==="maintenance_technician") {
        const next=techNext[work.state];
        if (next && work.revision !== undefined) actions.append(makeButton("Move to " + next.replaceAll("_", " "), async () => {
          await request("work/transition",{work_ref:work.work_ref,next_state:next,expected_revision:work.revision});
          message("Work state updated. This does not certify legal physical entry.");
          await refresh();
        }));
        actions.append(makeButton("Appointment status", async () => showAppointments(card,work)));
      }
      card.append(actions); target.append(card);
    }
  }
  function showAppointmentForm(card,work) {
    card.querySelector(".mini-form")?.remove();
    const form=el("form", null, "mini-form");
    function addDate(labelText) {
      const wrapper=el("label", labelText);
      const input=el("input"); input.type="datetime-local"; input.required=true;
      wrapper.append(input); form.append(wrapper); return input;
    }
    const start=addDate("Start"); const end=addDate("End");
    let retry=null;
    const submit=el("button","Send appointment request","primary full");submit.type="submit";form.append(submit);
    form.addEventListener("submit",async event => {
      event.preventDefault();submit.disabled=true;
      try {
        const startDate=new Date(start.value),endDate=new Date(end.value);
        if (Number.isNaN(startDate.getTime()) || Number.isNaN(endDate.getTime())) throw new Error("Choose valid start and end dates.");
        const payload={work_ref:work.work_ref,
          start_at:startDate.toISOString(),end_at:endDate.toISOString()};
        const fingerprint=JSON.stringify(payload);
        if(!retry || retry.fingerprint!==fingerprint){
          retry={fingerprint,key:newIdempotencyKey()};
        }
        const result=await request("appointment/request",payload,retry.key);
        retry=null;
        message("Appointment " + result.appointment_ref +
          (result.replayed ? " recovered after retry." : " requested in Grounds.") +
          " Not yet confirmed or dispatched.");
        form.remove();
      } catch(error) { message(error.message,true); } finally { submit.disabled=false; }
    });
    card.append(form);
  }
  function showPreferenceForm(card,work) {
    card.querySelector(".mini-form")?.remove();
    const form=el("form",null,"mini-form");const label=el("label","Entry preference");
    const select=el("select"); for(const [value,text] of [["contact_first","Contact first"],["no","Do not enter"],["yes","Discuss entry with staff"]]){
      const option=el("option",text);option.value=value;select.append(option);
    }
    label.append(select);form.append(label);const submit=el("button","Record preference","primary");submit.type="submit";form.append(submit);
    form.addEventListener("submit",async event => {
      event.preventDefault();submit.disabled=true;
      try {
        const record=await request("entry-preference?"+new URLSearchParams({work_ref:work.work_ref}));
        const result=await request("work/entry-preference",{work_ref:work.work_ref,
          preference:select.value,expected_revision:record.revision});
        message("Updated to " + result.preference + ". Entry is not legally authorized by this setting.");
        form.remove();
      } catch(error) { message(error.message,true); } finally{submit.disabled=false;}
    });card.append(form);
  }
  async function showAppointments(card,work) {
    const data=await request("appointments?" + new URLSearchParams({work_ref:work.work_ref}));
    const previous=card.querySelector(".appointment-panel");previous?.remove();
    const panel=el("div",null,"appointment-panel stack");
    if (!data.appointments.length) panel.append(el("p","No appointment is recorded for this authorized work item.","footnote"));
    for(const item of data.appointments){
      const row=el("div",null,"item");
      row.append(el("h3",item.state),el("p",asDate(item.start_at)+" – "+asDate(item.end_at)));
      const actions=el("div",null,"actions");
      if(state.me.role==="resident" && item.state==="proposed") actions.append(makeButton("Accept proposed time",async()=>{
        await request("appointment/accept",{appointment_ref:item.appointment_ref,expected_revision:item.revision});
        message("Time accepted in Grounds. This is not permission for physical entry or confirmed dispatch.");
        await showAppointments(card,work);
      }));
      if(item.state!=="cancelled" && ["resident","property_manager","maintenance_supervisor","owner"].includes(state.me.role)){
        actions.append(makeButton("Cancel appointment",async()=>{
          await request("appointment/cancel",{appointment_ref:item.appointment_ref,expected_revision:item.revision});
          message("Appointment cancelled in Grounds; delivery confirmation is not available.");
          await showAppointments(card,work);
        }));
      }
      if(item.state==="requested" && ["property_manager","maintenance_supervisor","owner"].includes(state.me.role)){
        actions.append(makeButton("Propose requested time",async()=>{
          await request("appointment/propose",{appointment_ref:item.appointment_ref,
            start_at:item.start_at,end_at:item.end_at,expected_revision:item.revision});
          message("Time proposed in Grounds; the resident must accept it.");
          await showAppointments(card,work);
        }));
      }
      row.append(actions);panel.append(row);
    }
    card.append(panel);
  }
  async function init() {
    try {
      state.me=await request("me");
      $("session-label").textContent="Active scoped session · " + state.me.role.replaceAll("_"," ");
      $("page-description").textContent="Current records for your authorized " + state.me.role.replaceAll("_"," ") + " context.";
      addOptions($("property-choice"),state.me.property_refs);
      if(state.me.role==="resident"){
        addOptions($("unit-choice"),state.me.unit_refs);
      } else $("unit-container").classList.add("hidden");
      $("property-choice").addEventListener("change",refresh);
      $("unit-choice").addEventListener("change",refresh);
      $("refresh").addEventListener("click",refresh);
      $("request-form").addEventListener("submit",async event=>{
        event.preventDefault();const button=event.submitter;button.disabled=true;
        try {
          selected();
          const payload={
            property_ref:state.property,unit_ref:state.unit,
            category:$("category").value,description:$("description").value,
            emergency_flag:$("urgent").checked,entry_permission:$("entry").value
          };
          const fingerprint=JSON.stringify(payload);
          if (!state.maintenanceRetry || state.maintenanceRetry.fingerprint!==fingerprint) {
            state.maintenanceRetry={fingerprint,key:newIdempotencyKey()};
          }
          const result=await request("work",payload,state.maintenanceRetry.key);
          state.maintenanceRetry=null;
          $("request-form").reset();
          message("Maintenance request " + result.work_ref +
            (result.replayed ? " recovered after retry." : " recorded.") +
            " It has not been externally delivered or dispatched.");
          await refresh();
        }catch(error){message(error.message,true);}finally{button.disabled=false;}
      });
      await refresh();
    } catch(error) {
      $("session-label").textContent="No authorized session";
      $("locked").classList.remove("hidden"); $("locked-reason").textContent=error.message;
      message(error.message,true);
    }
  }
  init();
})();
