# Tower Hosted Candidate Parity Gate / TWR086–TWR090

## Why this layer exists

TWR081–TWR085 established safe hosted-runtime identity:

- managed-staging entrypoint
- exact runtime revision
- revision source
- critical-route presence
- runtime identity headers

That solved:

**What application revision is the hosted service actually serving?**

TWR086–TWR090 closes the next diagnostic boundary:

**Does the hosted service exactly match the candidate revision that
Tower intended to test?**

This layer does not deploy anything.

---

## TWR086 — Safe hosted probe

The verifier probes only:

- `/tower/healthz`
- `/tower/runtime-manifest.json`
- `/tower/login`

The probe sends:

- no Authorization header
- no Cookie header
- no embedded URL credentials
- no secret-bearing query parameters

HTTPS is mandatory by default.

---

## TWR087 — Exact revision parity

Hosted parity requires exact equality between:

- expected candidate revision
- runtime manifest revision
- health response revision header
- manifest response revision header
- login response revision header

Missing, unknown, or inconsistent revisions fail closed.

---

## TWR088 — Runtime contract parity

Hosted parity also requires:

- `web.managed_staging:app`
- identity headers on all probe routes
- consistent revision source
- every critical-route boolean true
- `critical_routes_present == true`

---

## TWR089 — Safety parity

A candidate cannot pass parity unless all safety controls remain closed:

- production deployment = false
- broker submission = false
- capital movement = false
- Manual Live authorization = false
- Live Auto authorization = false
- STAGING_READY = false

A parity PASS is diagnostic proof only.

It is not deployment authorization.

---

## TWR090 — Fail-closed verifier

CLI:

`scripts/verify_tower_hosted_runtime_parity.py`

After an explicitly authorized staging deployment, usage is:

```bash
python scripts/verify_tower_hosted_runtime_parity.py \
  --base-url https://HOST \
  --expected-revision EXACT_GIT_SHA
```

Exit code:

- `0` — exact hosted candidate parity passed
- `2` — parity failed

The result identifies failed checks without dumping secrets,
sessions, environment contents, or application data.

---

## Promotion boundary

TWR086–TWR090 intentionally performs no:

- merge to `tower-dev`
- promotion to `main`
- Render deployment
- broker action
- capital action
- Manual Live authorization
- Live Auto authorization
- STAGING_READY change

The actual hosted parity check becomes meaningful only after a later,
explicitly authorized staging deployment.
