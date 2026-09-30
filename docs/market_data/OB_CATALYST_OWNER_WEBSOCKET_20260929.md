# Owner Catalyst Radar: hybrid REST + authenticated notification WebSocket

This builds on the existing commercially reusable official-source radar and Soulaana evidence timeline. It introduces **no** new source, licence, provider polling, API key, brokerage authentication, trade mode or paid Render resource.

## Transport

- Government publishers still use their officially supported REST endpoints. Their data is only requested by the existing owner-authorized radar snapshot GET, under the same independently reviewed source/automated/display/Soulaana-content flags and cache budgets.
- That same protected GET computes a small process-local content hash. If its validated source snapshot differs from the prior authorized read (including rights revocation or source failure), it increments an ephemeral cursor.
- Optional ASGI WebSocket /ob/research/catalysts/stream carries **only** stream_ready, snapshot_changed, resync_required and heartbeat metadata. No source text, original numeric values, provider credentials, subject identifiers, live quotes, options data, candidate ranking, orders or client-selected source URLs ever flow into socket messages.
- The browser authenticates normally through Tower and makes a fresh same-origin REST request when it receives an invalidation. After a disconnect or process restart, the browser performs the protected GET *before* reconnecting with its returned epoch/cursor. A bounded 64-event ring supports only best-effort replay; gaps force REST resynchronization.
- The same source data powers eight existing protected OB research surfaces, without separate provider API calls from each browser socket. No autonomous background publisher polling.
- Existing SEC EDGAR remains its separate reviewed Symbol Research corridor, not a sixth copy of source data.

## WebSocket security / readiness

The socket is routed by a narrow opt-in ASGI adapter wrapping the **same canonical Flask Tower** for every HTTP route. No parallel Tower login or unprotected Flask HTTP copy is started. Exact path only, HTTPS same-origin handshake, actual cryptographically signed Tower cookie loaded by Flask, owner session, step-up and consumed OB operational handoff are independently rechecked at accept, on notifications, and every 15 seconds. Browser-submitted role/clearance/permission claims have no authority. Maximum 4 subscribers per process, queues of 8 with overflow resync, no input command protocol, 2048-byte incoming WebSocket frame cap, 1 process. Use of multiple Render instances or more than one app worker requires a shared authorization/replay design first.

**Activation flag:** OB_CATALYST_WS_ASGI_ENABLED=1 opts the existing hosted startup into single-worker Uvicorn ASGI mode. Default 0 preserves the current Gunicorn WSGI startup and the browser does not attempt a socket. The flag must be enabled only following the test suite, authenticated owner browser walk-through, session expiry and logout/reconnect acceptance, and HTTP regression checks. A stock/options live feed is *not* asserted by this flag.

Render deployment steps on the existing free services (do not create paid infrastructure):
1. Merge after synthetic and broader Tower CI checks.
2. Verify primary/secondary service identity and branch, and choose one owner beta instance for a controlled transport rollout. No credentials or public event publishing.
3. Confirm ASGI starts, previously working Tower login/OB rooms remain functional, anonymous/foreign-Origin WS handshake denies before accept, authenticated owner receives only content-free stream_ready, source snapshot refresh triggers bounded notification and REST re-read.
4. Confirm owner logout or expired step-up causes deny/close; a killed socket or changed process epoch recovers from a REST snapshot. Disable flag to return to current WSGI if any regression.
5. Only after passing, consider enabling the same flag on the other instance. Neither instance shares a process-memory replay store; the browser always recovers truth through authenticated GET.

This is the **delivery transport foundation**, not continuous autonomous provider fetching. That later phase needs publisher-specific authorized schedules and rate budgets plus a durable, appropriately licensed event storage and independent monitoring plan.
