"use strict";
(() => {
  const root = "/grounds";
  const csrf = document.querySelector('meta[name="grounds-csrf"]').content;
  const $ = id => document.getElementById(id);
  const state = { me: null, view: null, property: "", unit: "", displayContext: "", busy: false, maintenanceRetry: null, loadGeneration: 0 };
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
  function clearPrivateView() {
    // The prior lease/property's text must not linger while a new request is
    // pending, fails, or discovers a revoked Tower grant.
    state.view = null;
    $("content").classList.add("hidden");
    $("locked").classList.add("hidden");
    for (const id of ["summary","lease-details","work-list","notice-list",
                      "safety-list","leasing-list","physical-list",
                      "my-home-list","daily-list","property-health-list",
                      "owner-portfolio-list","move-list","move-desk-list"]) clear($(id));
    $("rent-message").textContent = "Current Teller invoice not verified. An unavailable amount is not a zero balance or payment confirmation.";
    $("rent-service-status").textContent = "Awaiting Teller";
    $("soulaana-message").textContent = "Checking the current authorized source context.";
    $("soulaana-next").textContent = "";
    $("safety-count").textContent = "Checking";
    $("leasing-count").textContent = "Checking";
    $("physical-count").textContent = "Checking";
    $("property-state").textContent = "Checking";
    $("work-count").textContent = "—";
  }
  function verifyWorkspaceContext(data, propertyRef, unitRef) {
    if (!data || data.source !== "grounds" || data.property_ref !== propertyRef ||
        data.role !== state.me.role ||
        (state.me.role === "resident" && data.unit_ref !== unitRef)) {
      throw new Error("The returned workspace did not match the selected Tower context. No records were displayed.");
    }
  }
  async function refresh() {
    selected();
    const generation = ++state.loadGeneration;
    const propertyRef = state.property;
    const unitRef = state.unit;
    const nextContext = JSON.stringify([state.me.role, propertyRef,
      state.me.role === "resident" ? unitRef : null]);
    if (state.displayContext !== nextContext) {
      $("alert").textContent = "";
      $("alert").className = "alert hidden";
      state.displayContext = nextContext;
    }
    clearPrivateView();
    if (!propertyRef || (state.me.role === "resident" && !unitRef)) {
      $("locked").classList.remove("hidden");
      $("locked-reason").textContent = "Select an authorized property and, where required, your current unit.";
      return;
    }
    const qs = new URLSearchParams({ property_ref: propertyRef });
    if (state.me.role === "resident") qs.set("unit_ref", unitRef);
    try {
      const data = await request("workspace?" + qs);
      if (generation !== state.loadGeneration) return;
      verifyWorkspaceContext(data, propertyRef, unitRef);
      state.view = data; render(data);
      $("property-state").textContent = "Current";
      if (state.me.role === "resident") {
        try {
          const rent = await request("rent?" + qs);
          if (generation === state.loadGeneration && state.view === data) renderRent(rent);
        } catch {
          if (generation === state.loadGeneration) {
            $("rent-message").textContent = "A verified Teller invoice is unavailable right now. Do not infer that your balance is zero or that payment was recorded.";
            $("rent-service-status").textContent = "Unavailable";
          }
        }
      }
      if (["owner","property_manager","maintenance_supervisor"].includes(state.me.role)) {
        try {
          const desk = await request("safety-desk?" + new URLSearchParams({ property_ref: state.property }));
          if (generation === state.loadGeneration) renderSafetyDesk(desk);
        } catch {
          if (generation === state.loadGeneration) {
            clear($("safety-list"));
            $("safety-count").textContent = "Unavailable";
            $("safety-delivery").textContent =
              "Current human triage status could not be retrieved. Do not assume this property is clear or that anyone has been contacted.";
          }
        }
      }
      if (["owner","property_manager","leasing_agent"].includes(state.me.role)) {
        try {
          const leasing = await request("leasing?" + new URLSearchParams({ property_ref: state.property }));
          if (generation === state.loadGeneration) renderLeasingDesk(leasing);
        } catch {
          if (generation === state.loadGeneration) {
            clear($("leasing-list"));
            $("leasing-count").textContent = "Unavailable";
            $("leasing-status").textContent = "Current property leasing records could not be retrieved. No applications or tours were confirmed by this screen.";
          }
        }
      }
      if (["owner","property_manager","maintenance_supervisor"].includes(state.me.role)) {
        try {
          const physical = await request("physical-desk?" + new URLSearchParams({ property_ref: state.property }));
          if (generation === state.loadGeneration) renderPhysicalDesk(physical);
        } catch {
          if (generation === state.loadGeneration) {
            clear($("physical-list"));
            $("physical-count").textContent = "Unavailable";
            $("physical-status").textContent = "Current physical-operation records could not be retrieved. No inspection, turnover or external dispatch is certified.";
          }
        }
      }
      if (state.me.role === "resident") {
        try {
          const move = await request("move-concierge?" + qs);
          if (generation === state.loadGeneration) renderMoveConcierge(move);
        } catch {
          if (generation === state.loadGeneration) {
            clear($("move-list"));
            $("move-count").textContent = "Unavailable";
          }
        }
      }
      if (["owner","property_manager"].includes(state.me.role)) {
        try {
          const moveDesk = await request("move-desk?" + new URLSearchParams({ property_ref: state.property }));
          if (generation === state.loadGeneration) renderMoveDesk(moveDesk);
        } catch {
          if (generation === state.loadGeneration) {
            clear($("move-desk-list"));
            $("move-desk-count").textContent = "Unavailable";
          }
        }
      }
      if (state.me.role === "resident") {
        try {
          const home = await request("my-home?" + qs);
          if (generation === state.loadGeneration) renderMyHome(home);
        } catch {
          if (generation === state.loadGeneration) {
            clear($("my-home-list"));
            $("my-home-count").textContent = "Unavailable";
          }
        }
      }
      if (["owner","property_manager","maintenance_supervisor"].includes(state.me.role)) {
        try {
          const daily = await request("daily?" + new URLSearchParams({ property_ref: state.property }));
          if (generation === state.loadGeneration) renderDaily(daily);
        } catch {
          if (generation === state.loadGeneration) {
            clear($("daily-list"));
            $("daily-count").textContent = "Unavailable";
          }
        }
      }
      if (["owner","property_manager","regional_manager"].includes(state.me.role)) {
        try {
          const health = await request("property-health?" + new URLSearchParams({ property_ref: state.property }));
          if (generation === state.loadGeneration) renderPropertyHealth(health);
        } catch {
          if (generation === state.loadGeneration) {
            clear($("property-health-list"));
            $("property-health-count").textContent = "Unavailable";
          }
        }
      }
      if (state.me.role === "owner") {
        try {
          const portfolio = await request("owner-portfolio");
          if (generation === state.loadGeneration) renderOwnerPortfolio(portfolio);
        } catch {
          if (generation === state.loadGeneration) {
            clear($("owner-portfolio-list"));
            $("owner-portfolio-count").textContent = "Unavailable";
          }
        }
      }
    } catch (error) {
      if (generation !== state.loadGeneration) return;
      clearPrivateView(); $("locked").classList.remove("hidden");
      $("locked-reason").textContent = error.message;
      message(error.message, true);
    }
  }
  function renderMoveConcierge(data) {
    const target=$("move-list");clear(target);
    if(data?.source!=="grounds" || data.room!=="move_concierge" ||
       data.property_ref!==state.property || data.unit_ref!==state.unit ||
       !Array.isArray(data.phases) || data.deposit_return_approved!==false ||
       data.keys_received_confirmed!==false) {
      $("move-count").textContent="Unverified";return;
    }
    const generation=state.loadGeneration;
    $("move-count").textContent="Your planning checklist";
    for(const phase of data.phases){
      if(!["move_in","move_out"].includes(phase.phase) || !Array.isArray(phase.tasks)) continue;
      const panel=el("section",null,"move-phase");
      panel.append(el("h3",phase.phase==="move_in" ? "Welcome & move-in" : "Planning your move-out"),
        el("p",phase.self_reported_done_count+" / "+phase.task_count+
          " self-reported steps recorded; not a staff-approved completion.","footnote"));
      for(const item of phase.tasks){
        const tile=el("article",null,"experience-tile");
        tile.append(el("strong",item.label),el("p",item.hint),
          el("span",item.status.replaceAll("_"," ")+" · planning revision "+item.revision,"meta"));
        const next=item.status==="not_started" ? "planned" :
          item.status==="planned" ? "self_reported_done" : "planned";
        const label=next==="planned" ? "Record as planned" : "Mark personally reviewed";
        const payload={
          property_ref:data.property_ref,unit_ref:data.unit_ref,
          phase:phase.phase,task_ref:item.task_ref,
          status:next,expected_revision:item.revision,
        };
        const idempotency=newIdempotencyKey();
        tile.append(makeButton(label,async()=>{
          if(generation!==state.loadGeneration || state.property!==data.property_ref ||
             state.unit!==data.unit_ref)return;
          const result=await request("move-task",payload,idempotency);
          if(generation!==state.loadGeneration)return;
          message("Personal planning update recorded" +
            (result.replayed ? " (same request recovered)." : ".") +
            " No lease, deposit, key custody or inspection approval was recorded.");
          await refresh();
        }));
        panel.append(tile);
      }
      target.append(panel);
    }
  }
  function renderMoveDesk(data) {
    const target=$("move-desk-list");clear(target);
    if(data?.source!=="grounds" || data.room!=="move_desk" ||
       data.property_ref!==state.property || data.resident_identity_included!==false) {
      $("move-desk-count").textContent="Unverified";return;
    }
    $("move-desk-count").textContent="Recorded planning only";
    experienceTile(target,"Recorded lease end · 60 days",
      data.active_leases_with_recorded_end_within_60_days,
      "No automatic renewal or termination conclusion.");
    experienceTile(target,"Make-ready units",data.units_in_make_ready,
      "Source lifecycle only, not a certified final inspection.");
    experienceTile(target,"Unfinished turnovers",data.unfinished_turnovers,
      "Current recorded turnover workflows.");
    experienceTile(target,"Open turnover inspections",data.open_recorded_turnover_inspections,
      "Pending recorded inspections; no self-service sign-off.");
  }
  function experienceTile(target, label, value, detail, urgent = false) {
    const tile = el("article", null, "experience-tile" + (urgent ? " priority" : ""));
    tile.append(el("span", label), el("strong", value),
      el("p", detail || "Current recorded source snapshot"));
    target.append(tile);
  }
  function renderMyHome(home) {
    const target = $("my-home-list"); clear(target);
    if (home?.source !== "grounds" || home.room !== "my_home" ||
        home.property_ref !== state.property || home.unit_ref !== state.unit ||
        !home.lease || !Array.isArray(home.next_appointments)) {
      $("my-home-count").textContent = "Unverified"; return;
    }
    $("my-home-count").textContent = "Current lease";
    experienceTile(target,"Your recorded home",home.property_name + " · " + home.unit_label,
      "Lease dates: " + home.lease.start_on + " through " + home.lease.end_on);
    experienceTile(target,"Maintenance",home.open_my_request_count + " open",
      home.my_request_count + " of your recorded requests; no external dispatch implied.");
    experienceTile(target,"Notices",home.unread_in_app_count + " unread in Grounds",
      home.visible_notice_count + " visible. In-app read is not proof of delivered legal notice.");
    experienceTile(target,"Appointments",home.next_appointments.length + " recorded upcoming",
      home.next_appointments[0] ? asDate(home.next_appointments[0].start_at) + " · " +
        home.next_appointments[0].state : "No active appointments recorded.");
    experienceTile(target,"Rent and documents","Sources protected",
      "Teller invoice must be independently verified. Vault private document retrieval is not connected.");
  }
  function renderDaily(daily) {
    const target = $("daily-list"); clear(target);
    if (daily?.source !== "grounds" || daily.property_ref !== state.property ||
        daily.room !== "daily_grounds" || !daily.counts ||
        !Array.isArray(daily.urgent_work)) {
      $("daily-count").textContent = "Unverified";return;
    }
    const n=daily.counts;
    $("daily-count").textContent = n.unreviewed_urgent + " urgent to review";
    experienceTile(target,"Human triage",n.unreviewed_urgent + " waiting",
      "Source-recorded urgent intake; this card is not on-call acknowledgment or dispatch.",
      n.unreviewed_urgent > 0);
    experienceTile(target,"Older open requests",n.open_older_than_three_days,
      "Requests created more than " + daily.work_age_threshold_days + " days ago, not a certified SLA.");
    experienceTile(target,"Appointment decisions",n.pending_appointment_decisions,
      "Requested or proposed, awaiting an in-app decision.");
    experienceTile(target,"Preventive due",n.due_preventive,
      "Recorded plans due on or before today.");
    experienceTile(target,"Inspections",n.open_inspections,"Recorded open inspections.");
    if (daily.turnovers_authorized)
      experienceTile(target,"Turnovers",n.open_turnovers,"Recorded unfinished turnover workflow.");
    experienceTile(target,"Local notification intents",n.pending_local_notification_intents,
      "An intent is not external message delivery.");
  }
  function renderPropertyHealth(health) {
    const target = $("property-health-list"); clear(target);
    if (health?.source !== "grounds" || health.room !== "property_health" ||
        health.property_ref !== state.property || !health.counts) {
      $("property-health-count").textContent = "Unverified";return;
    }
    const n=health.counts;
    $("property-health-count").textContent = "Physical records only";
    experienceTile(target,"Occupancy recorded",n.occupied_units + " / " + n.units,
      "Unit lifecycle records; no lease-finance assumption.");
    experienceTile(target,"New maintenance · 30 days",n.new_requests_last_30_days,
      "Prior 30-day interval: " + n.new_requests_previous_30_days + ".");
    experienceTile(target,"Repeat unit/category patterns",n.repeat_unit_category_groups_last_30_days,
      "Groups with two or more recorded requests; no cause is established.");
    experienceTile(target,"Unresolved serious findings",n.unresolved_serious_inspection_findings,
      "Recorded major/urgent findings without a resolution.",n.unresolved_serious_inspection_findings > 0);
    experienceTile(target,"First-received response sample",
      health.first_received_elapsed_minutes_sample_mean === null ? "Unavailable" :
        health.first_received_elapsed_minutes_sample_mean + " minutes",
      health.response_sample_count + " eligible records (max " + health.response_sample_row_limit +
      (health.response_sample_may_be_truncated ? ", truncated" : "") + "). Not a service-level certification.");
    experienceTile(target,"Rent collections","Teller-only",
      "Grounds does not calculate collected rent or available investment capital.");
  }
  function renderOwnerPortfolio(portfolio) {
    const target = $("owner-portfolio-list"); clear(target);
    if (portfolio?.source !== "grounds" || portfolio.room !== "owner_portfolio" ||
        !Array.isArray(portfolio.properties) || portfolio.money_fields_included !== false) {
      $("owner-portfolio-count").textContent = "Unverified";return;
    }
    $("owner-portfolio-count").textContent = portfolio.total_scope_count + " granted properties";
    if (!portfolio.properties.length)
      target.append(el("p","No verified owned property records are in this scope.","footnote"));
    for (const item of portfolio.properties) {
      if (!state.me.property_refs.includes(item.property_ref)) continue;
      const n=item.counts;
      experienceTile(target,"Property " + item.property_ref,
        n.occupied_units + " / " + n.units + " recorded occupied",
        n.open_work + " open work · " + n.unreviewed_urgent + " unreviewed urgent · " +
          n.open_turnovers + " unfinished turnovers.");
    }
    if (portfolio.truncated) target.append(
      el("p","Only the first " + portfolio.visible_limit +
        " authorized properties are displayed. This is not a full portfolio roll-up.","footnote"));
  }
  function renderPhysicalDesk(desk) {
    const target = $("physical-list"); clear(target);
    if (desk?.source !== "grounds" || desk.property_ref !== state.property ||
        !Array.isArray(desk.assets) || !Array.isArray(desk.due_preventive_plans) ||
        !Array.isArray(desk.open_inspections) || !Array.isArray(desk.open_turnovers)) {
      $("physical-count").textContent = "Unverified";
      $("physical-status").textContent = "Current source data could not be verified.";
      return;
    }
    const counts = desk.counts || {};
    $("physical-count").textContent = (counts.due_preventive_plans ?? "—") + " preventive items due";
    $("physical-status").textContent = "Recorded: " + (counts.assets ?? "—") + " assets · " +
      (counts.open_inspections ?? "—") + " open inspections" +
      (desk.turnover_view_authorized ? " · " + counts.open_turnovers + " open turnovers" : "") +
      ". No provider dispatch, legal entry, certified inspection sign-off, Vault fetch or capital approval is implied.";
    if (!desk.due_preventive_plans.length && !desk.open_inspections.length && !desk.open_turnovers.length) {
      target.append(el("p", "No current due items are visible in this authorized snapshot. This is not a maintenance-completion or compliance certification.", "footnote"));
    }
    for (const plan of desk.due_preventive_plans) {
      const card = el("article", null, "item");
      card.append(el("h3", "Preventive plan · " + plan.plan_ref),
        el("p", "Asset " + plan.asset_ref + " · Recorded due date " + plan.next_due_on));
      target.append(card);
    }
    for (const inspection of desk.open_inspections) {
      const card = el("article", null, "item");
      card.append(el("h3", "Inspection · " + inspection.inspection_ref),
        el("p", inspection.category + " · " + inspection.state + " · Planned " + inspection.planned_on));
      target.append(card);
    }
    if (desk.turnover_view_authorized) for (const turnover of desk.open_turnovers) {
      const card = el("article", null, "item");
      card.append(el("h3", "Turnover · " + turnover.turnover_ref),
        el("p", "Unit " + turnover.unit_ref + " · State " + turnover.state));
      target.append(card);
    }
  }
  function renderLeasingDesk(desk) {
    const target = $("leasing-list"); clear(target);
    if (desk?.source !== "grounds" || desk.property_ref !== state.property ||
        !Array.isArray(desk.units) || !Array.isArray(desk.prospects) || !Array.isArray(desk.tours)) {
      $("leasing-count").textContent = "Unverified";
      $("leasing-status").textContent = "Leasing source data could not be verified.";
      return;
    }
    const ready = desk.units.filter(unit => unit.lifecycle === "ready").length;
    $("leasing-count").textContent = ready + " recorded ready units";
    $("leasing-status").textContent = desk.prospects.length + " recent opaque prospect records and " +
      desk.tours.length + " scheduled tour records shown (first 100 per collection). No actual contact, applicant decision or delivered notification is certified.";
    if (!desk.prospects.length && !desk.tours.length) {
      target.append(el("p", "No authorized prospect or tour records are available in this property snapshot. Applicant intake is not connected here.", "footnote"));
    }
    for (const prospect of desk.prospects) {
      const card = el("article", null, "item");
      card.append(el("h3", "Prospect · " + prospect.prospect_ref),
        el("p", "Recorded stage: " + prospect.stage +
          " · Preferred unit: " + (prospect.desired_unit_ref || "Not recorded")),
        el("span", "Updated: " + asDate(prospect.updated_at), "meta"));
      target.append(card);
    }
    for (const tour of desk.tours) {
      const card = el("article", null, "item");
      card.append(el("h3", "Tour · " + tour.tour_ref),
        el("p", "Unit " + tour.unit_ref + " · Scheduled " + asDate(tour.starts_at)),
        el("span", "Prospect reference: " + tour.prospect_ref + " · Delivery not confirmed", "meta"));
      target.append(card);
    }
  }
  function renderSafetyDesk(desk) {
    const target = $("safety-list"); clear(target);
    if (desk?.source !== "grounds" || desk.property_ref !== state.property ||
        !Array.isArray(desk.queue) || !Number.isSafeInteger(desk.unreviewed_urgent_count) ||
        !Number.isSafeInteger(desk.pending_local_event_intents)) {
      $("safety-count").textContent = "Unverified";
      $("safety-delivery").textContent = "Current safety data could not be verified.";
      return;
    }
    $("safety-count").textContent = desk.unreviewed_urgent_count + " awaiting human review";
    $("safety-delivery").textContent = desk.pending_local_event_intents +
      " internal event intents remain pending; " +
      (desk.verified_historical_delivery_event_count ?? 0) +
      " events have verified historical delivery receipts; " +
      (desk.verified_historical_human_acknowledged_event_count ?? 0) +
      " have historical human acknowledgment receipts. These do not prove current provider connectivity, on-call coverage, legal service or emergency dispatch.";
    if (!desk.queue.length) {
      target.append(el("p", "No unreviewed urgent intake is visible in the current property snapshot. This is not emergency coverage or dispatch confirmation.", "footnote"));
    }
    for (const item of desk.queue) {
      const card = el("article", null, "item");
      card.append(el("h3", item.category + " · Unit " + item.unit_ref),
        el("p", "Resident requested urgent human attention · " + asDate(item.created_at)));
      card.append(makeButton("Record human priority review", async () => {
        await request("urgency/review", { work_ref:item.work_ref, assessed_urgency:"priority" });
        message("Human priority review recorded. This does not contact an emergency service or establish provider delivery.");
        await refresh();
      }));
      target.append(card);
    }
    if (desk.unreviewed_urgent_count > desk.queue.length) {
      target.append(el("p", "Additional urgent items exist beyond this limited display. Refresh or use the authorized work queue.", "footnote"));
    }
  }
  function renderRent(data) {
    const target = $("rent-message");
    if (data?.status !== "verified_projection" ||
        !Number.isSafeInteger(data.amount_due_cents) ||
        data.amount_due_cents < 0 || data.currency !== "USD" ||
        data.checkout_execution_enabled !== false) {
      target.textContent = "Teller has not supplied a current verified invoice. Grounds cannot determine an amount due or take payment.";
      $("rent-service-status").textContent = "Unavailable";
      return;
    }
    const amount = (data.amount_due_cents / 100).toLocaleString(undefined, {
      style: "currency", currency: "USD"
    });
    $("rent-service-status").textContent = "Verified read-only";
    target.textContent = "Verified Teller snapshot: " + amount + " shown as amount due; invoice status " +
      data.invoice_status + "; due date " + data.due_on + ". This is a read-only status, not a payment or checkout confirmation.";
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
    const hasSafetyDesk = ["owner","property_manager","maintenance_supervisor"].includes(data.role);
    $("safety-panel").classList.toggle("hidden", !hasSafetyDesk);
    const hasLeasingDesk = ["owner","property_manager","leasing_agent"].includes(data.role);
    $("leasing-panel").classList.toggle("hidden", !hasLeasingDesk);
    const hasPhysicalDesk = ["owner","property_manager","maintenance_supervisor"].includes(data.role);
    $("physical-panel").classList.toggle("hidden", !hasPhysicalDesk);
    if (hasPhysicalDesk) {
      clear($("physical-list"));
      $("physical-count").textContent = "Checking";
      $("physical-status").textContent = "Checking source-owned physical status. No external dispatch or proof is confirmed.";
    }
    if (hasLeasingDesk) {
      clear($("leasing-list"));
      $("leasing-count").textContent = "Checking";
      $("leasing-status").textContent = "Checking current scoped property inventory. Private contact and application decisions are unavailable.";
    }
    if (hasSafetyDesk) {
      clear($("safety-list"));
      $("safety-count").textContent = "Checking";
      $("safety-delivery").textContent = "Checking internal triage records. External delivery and dispatch are not confirmed.";
    }
    $("move-panel").classList.toggle("hidden", data.role !== "resident");
    $("move-desk-panel").classList.toggle("hidden",
      !["owner","property_manager"].includes(data.role));
    $("move-count").textContent="Checking";
    $("move-desk-count").textContent="Checking";
    $("my-home-panel").classList.toggle("hidden", data.role !== "resident");
    $("daily-panel").classList.toggle("hidden",
      !["owner","property_manager","maintenance_supervisor"].includes(data.role));
    $("property-health-panel").classList.toggle("hidden",
      !["owner","property_manager","regional_manager"].includes(data.role));
    $("owner-portfolio-panel").classList.toggle("hidden", data.role !== "owner");
    $("my-home-count").textContent = "Checking";
    $("daily-count").textContent = "Checking";
    $("property-health-count").textContent = "Checking";
    $("owner-portfolio-count").textContent = "Checking";
    $("rent-panel").classList.toggle("hidden", data.role !== "resident");
    $("request-panel").classList.toggle("hidden", data.role !== "resident");
    $("notices-panel").classList.toggle("hidden", data.role !== "resident");
    if (data.role === "resident") {
      const lease = $("lease-details"); clear(lease);
      lease.append(el("span", "From: " + data.lease.start_on), el("span", "Through: " + data.lease.end_on));
      $("rent-message").textContent = "Teller has not supplied an authenticated invoice. Grounds cannot determine your balance or accept a payment.";
      $("rent-service-status").textContent = "Awaiting Teller";
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
        const generation=state.loadGeneration;
        const detail=await request("work?" + new URLSearchParams({work_ref:work.work_ref}));
        if (generation!==state.loadGeneration || detail.property_ref!==state.property ||
            (state.me.role==="resident" && detail.unit_ref!==state.unit)) return;
        message(detail.category + ": " + detail.description);
      }));
      actions.append(makeButton("Updates & conversation", async () => {
        await showWorkConversation(card,work);
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
        if (work.state==="scheduled" && work.revision !== undefined) {
          actions.append(makeButton("Assign technician", async () => showTechnicianForm(card,work)));
        }
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
  async function showWorkConversation(card,work) {
    const generation=state.loadGeneration;
    const property=state.property;
    const unit=state.unit;
    const data=await request("work-thread?" + new URLSearchParams({work_ref:work.work_ref}));
    if (generation!==state.loadGeneration || data?.source!=="grounds" ||
        data.work_ref!==work.work_ref || data.property_ref!==property ||
        (state.me.role==="resident" && data.unit_ref!==unit)) return;
    const previous=card.querySelector(".work-conversation");previous?.remove();
    const panel=el("section",null,"work-conversation stack");
    panel.setAttribute("aria-label","Maintenance update timeline and private conversation");
    panel.append(el("h4","Recorded updates and conversation"),
      el("p","Messages are recorded inside Grounds; no notification, legal notice or emergency dispatch is implied. Historical verified delivery receipts: " +
        data.verified_historical_delivered_event_count + ". Current provider status is not connected.","footnote"));
    if (!data.timeline.length)
      panel.append(el("p","No updates are recorded for this authorized request.","footnote"));
    for (const item of data.timeline) {
      const entry=el("article",null,"experience-tile timeline-entry");
      if(item.kind==="state")
        entry.append(el("strong","Status · " + item.state.replaceAll("_"," ")),
          el("p","Recorded action: " + item.action),
          el("span",asDate(item.occurred_at),"meta"));
      else
        entry.append(el("strong",item.role.replaceAll("_"," ") +
          (item.audience==="staff_internal" ? " · internal staff" : " · shared")),
          el("p",item.body),el("span",asDate(item.occurred_at),"meta"));
      panel.append(entry);
    }
    if(data.messages_truncated || data.state_events_truncated)
      panel.append(el("p","The first/last 100 records are displayed. This is not the complete historical archive.","footnote"));
    if(data.can_post){
      const form=el("form",null,"mini-form");
      const label=el("label","Add a plain-text update (no sensitive information)");
      const body=el("textarea");body.required=true;body.maxLength=1200;body.rows=3;
      label.append(body);form.append(label);
      const audience=el("select");
      for (const [value,caption] of [["shared","Shared with the request's authorized resident and staff"],
        ["staff_internal","Internal property management only"]]){
        if(value==="staff_internal" && !data.can_post_staff_internal) continue;
        const option=el("option",caption);option.value=value;audience.append(option);
      }
      const visibilityLabel=el("label","Visibility");visibilityLabel.append(audience);
      form.append(visibilityLabel);
      const send=el("button","Record in Grounds · not delivered externally","primary");
      send.type="submit";form.append(send);
      let retry=null;
      form.addEventListener("submit",async event=>{
        event.preventDefault();
        if (generation!==state.loadGeneration || property!==state.property ||
            (state.me.role==="resident" && unit!==state.unit)) return;
        send.disabled=true;
        try {
          const payload={work_ref:work.work_ref,body:body.value,audience:audience.value};
          const fingerprint=JSON.stringify(payload);
          if(!retry || retry.fingerprint!==fingerprint)
            retry={fingerprint,key:newIdempotencyKey()};
          const recorded=await request("work-message",payload,retry.key);
          if (generation!==state.loadGeneration) return;
          retry=null;
          message("Update recorded inside Grounds" +
            (recorded.replayed ? " (same request recovered)." : ".") +
            " No external message delivery or entry permission was established.");
          await showWorkConversation(card,work);
        }catch(error){ if(generation===state.loadGeneration)message(error.message,true); }
        finally{send.disabled=false;}
      });
      panel.append(form);
    }
    card.append(panel);
  }
  async function showTechnicianForm(card,work) {
    const roster=await request("technicians?" + new URLSearchParams({property_ref:state.property}));
    if(!roster.connected) {
      message("Tower's verified maintenance staff roster is not yet connected. No assignment was made.",true);
      return;
    }
    if (!Array.isArray(roster.technicians) || !roster.technicians.length) {
      message("No authorized maintenance technicians were returned for this property.",true);
      return;
    }
    card.querySelector(".mini-form")?.remove();
    const form=el("form",null,"mini-form");
    const label=el("label","Authorized technician");
    const choose=el("select");choose.required=true;
    for (const person of roster.technicians) {
      const option=el("option",person.label);option.value=person.staff_ref;
      choose.append(option);
    }
    label.append(choose);form.append(label);
    const submit=el("button","Record assignment","primary");
    submit.type="submit";form.append(submit);
    form.addEventListener("submit",async event=>{
      event.preventDefault();submit.disabled=true;
      try{
        const assigned=await request("work/assign",{
          work_ref:work.work_ref,technician_ref:choose.value,
          expected_revision:work.revision,
        });
        message("Assigned in Grounds. This does not prove staff notification or authorize entry.");
        form.remove();await refresh();
      }catch(error){message(error.message,true);}
      finally{submit.disabled=false;}
    });
    card.append(form);
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
      $("text-size-toggle").addEventListener("click", () => {
        const applied=document.documentElement.classList.toggle("comfortable-type");
        $("text-size-toggle").setAttribute("aria-pressed",String(applied));
        $("text-size-toggle").textContent=applied ? "Standard text" : "Larger text";
      });
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
