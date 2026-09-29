# Owner Public API connection inside Tower/OB — September 29, 2026

This restores the actual owner workflow: Tower sign-in -> fresh Observatory step-up/launch -> Market Data Desk -> Connect Public. No Colab, terminal, code copying, GitHub key, or third-party connector.

## Exact source-only implementation

- The exact route /ob/data-desk/public (GET/POST) is listed explicitly in OB's route policy and protected HTTP allowlist. Handler independently requires owner_session_active(), step_up_active() and operational_ob_access_active(), plus the current Tower-generated random session ID. No public or invitee route.
- A POST connects only if OB_PUBLIC_OWNER_CONNECT_ENABLED=1. It requires HTTPS same-origin Origin, strict 8KB form ceiling and session-bound CSRF token. POST body (never URL parameters) carries key through approved protected service only. Secure endpoint TLS transport must be independently verified on deployed Render services.
- Public secret exchanged immediately via documented 15-minute token endpoint. The key is not stored by our code. One brokerage account must be uniquely returned from Public's read-only account list; no arbitrary first-account selection, portfolio or balance query. Backend temporarily retains ONLY its 10-minute bearer token and account ID in per-process memory, bound to Tower login session ID. Neither is stored in Flask's signed client-side cookie, browser JSON/HTML, file, repo, database or Render config.
- Disconnect deletes locally held bearer; expiry and worker restart also discard it. Public token itself is not revoked at Public by disconnect and expires under its JWT timeout. Owner must reconnect after Tower session change or ten minutes. At most 32 temporary sessions per worker. Durable credential management requires separately approved vault/KMS contract.
- Optional single quote checks stay disabled until distinct reviewed server flags for source/account use, internal non-display, owner display, marketdata scope and exact instrument. No code/checkbox/API response infers business redistribution, AI-use, SIP/OPRA, licensed real-time coverage, or broker execution. Successful vendor quote remains source-only, never UniversalMarketGateway installation or Manual Live clearance.
- Success/failure notices are predefined sanitized text. Content no-store/no-referrer/no-frame, without inline scripts, secrets or account identifiers. No unattended polling, stream, orders, extra Render service or paid resource.

## Safe activation on TWO existing services only

Current services on tower-hosted-runtime-identity-twr081-085:
- Simplee World Staging workspace tea-d9d6sqmq1p3s73cip83g, active service srv-dag3gn9594qs73fnd0kg.
- Simplee World workspace tea-dag3rfu1egvs73a6s72g, active service srv-dag3sv2jnfac73bjqj8g.

After exact CI and merger, deploy source; set ONLY OB_PUBLIC_OWNER_CONNECT_ENABLED=1 in each existing service (no API keys/entitlement flags from ChatGPT). No provisioning or plan change. Check revision, service state and owner authorization. Do not modify the retired staging or old main-branch service.

Owner visits actual HTTPS Tower URL, logs in through Tower, completes OB step-up, opens /ob/data-desk -> Connect Public, and enters saved key only in protected form once. Observe authenticated temporary connection; disconnect when finished.

Public publicly confirms API access for business accounts, while generic quote docs say individual investors and contain individual-use terms. Business internal research/owner display and especially beta, AI, redistribution and exact data-product rights require distinct review before quote-use flags. Do not set flags merely because owner has a key. Quote UI remains HOLD until reviewed.

Synthetic acceptance: protected access, unknown-route denial, CSRF and Origin rejection, default-off no-network, account discovery/no secret in session or HTML, equity quote only under exact entitlement, expiry/disconnect, rights revocation, existing Tower Desk regressions.
