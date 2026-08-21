# Tower Hosted Revision Identity + Runtime Manifest / TWR081–TWR085

## Why this layer exists

The actual local Render WSGI app already contained the Archive Vault routes, while a previously hosted revision returned 404 for one of those routes.

That means route registration was not the missing local contract.

The next question is:

**What exact application revision is Render actually serving?**

## TWR081 — Revision identity

Managed staging resolves a safe revision fingerprint from managed-host revision variables, with a local Git fallback when available.

## TWR082 — Critical-route manifest

The runtime manifest reports booleans for critical Tower, Archive Vault, and OB routes.

It does not expose the complete internal route map.

## TWR083 — Runtime headers

Managed staging responses expose:

- X-Simplee-Entrypoint
- X-Simplee-Revision
- X-Simplee-Revision-Source

## TWR084 — Runtime manifest

`/tower/runtime-manifest.json`

returns safe runtime identity diagnostics.

## TWR085 — Proof

Tests instantiate the actual:

`web.managed_staging:app`

and prove:

- revision identity exists
- Archive Vault routes are present
- core Tower/OB routes are present
- runtime identity headers exist
- secrets/environment are not dumped
- all safety flags remain closed

## Promotion boundary

This layer is intentionally left before main promotion and Render deployment so additional Tower work can continue stacking.


## Middleware order

Runtime identity headers are installed as the outermost managed-staging middleware:

`Runtime Identity Headers → Health Middleware → canonical Flask app`

This ordering matters because the managed-staging health middleware short-circuits `/tower/healthz`.

If the identity middleware sits inside the health middleware, the health response bypasses the runtime headers.

TWR081–TWR085 explicitly tests the final middleware order and proves identity headers exist on:

- `/tower/healthz`
- `/tower/runtime-manifest.json`
- `/tower/login`
