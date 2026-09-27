# OBML026–030 — Monday, September 28 owner Manual Live L1 readiness desk

**Read-only source release checkpoint. This pack does NOT activate Manual Live.**
Owner's target: Monday 2026-09-28 America/New_York. Operational model:
OB detects and tracks → human owner reviews exact candidate/account/size/terms
→ if independently authorized, owner places any order in separate broker app
→ OB reconciles genuine provider receipt. Never OB API order execution, auto
selection, Hybrid, Live Auto, unrestricted capital access or tester Live.

## Verified parents

- Tower dedicated hosted branch parent \`5a4e7f49b121f71b978729357d5f767a3b8ab284\`,
  reported live on existing Render service. Previous Tower source account
  verifier and source-only OBML preflight are integrated. Its existing generic
  owner/OB operational handoff is NOT account/purpose-specific Manual Live.
- Independent OB production phase schema at merged PR #113,
  \`cced86992fabdb6a91de3fb3e48a1f1f4aaf0478\`, fixed the first-fill
  circular dependency. The six pre-access, four per-order (overlapping)
  and post-human-order gate IDs are asserted against pinned exact source in CI.
- Request PR #68 still draft/source-only, with no production owner OBML issuer
  or actual independently verified consumer.

## New owner-visible status, not an activation form

\`GET /tower/owner/manual-live-1/readiness.json\` on existing hosted Tower
runs behind current real \`require_human_owner\`, returns private/no-store
redacted readiness status and canonical preflight blocker codes. Anonymous
requests redirect to the existing Tower login. It exposes no account number,
balance, credentials or issuer receipt. GET parameters such as
\`verified=1\`/\`activate=1\` cannot affect server truth. POST is disallowed.
Even a forged optimistic preflight does not cause this module to mint a grant,
activate Manual Live, release floors or submit any broker order.

This is an operational checklist only. Source CI proves schema/route safety,
not authenticated owner acceptance, current account status or broker source
provenance. Existing owner \`/tower/launch/observatory\` and
\`/ob/dashboard\` retain their actual authorization boundaries.

## What must actually be completed to open owner review mode

Six independent pre-access proofs:
1. Real Tower owner + exact OB mission-account binding + purpose-specific
   fresh OBML step-up + revocation/nonce + one-time Tower→OB receiver.
2. Actual hosted owner crossing and exact deployed revision.
3. Independently authenticated brokerage account and approved instrument /
   options-level permissions for intended strategy and legal account entity.
4. Institution/Teller-authoritative actual available/settled spendable funds,
   held reserves and protected capital floors; zero funds or unknown = no
   order, and no trust/ATM sleeve pooling.
5. Fresh market/provider sources and current effective risk, recovery and
   kill-switch state.
6. Separate operating/security/compliance and owner acceptance for review
   access. Review access never self-approves an individual trade.

Before EACH owner manual broker order: recheck broker permission, actual
funds/protected floors, current safety/market state and separate human Review
Center decision for exact candidate, account, size, limit and terms.
Only AFTER any actual human order: reconcile genuine provider order/fill/
reject/cancel receipt. No first-order circular fill prerequisite, but no
synthetic receipt treated as a real broker fill either.

**If these proofs remain missing Sep 28:** keep Manual Live HOLD and use
Survey/Paper or independently authorized synthetic owner rehearsal; do not
silently switch by date. Owner can verify brokerage permissions privately
under IBKR Client Portal > User menu > Settings > Trading > Trading Permissions
(and Options Level). Do not post brokerage IDs/passwords, secret values,
amounts or account statements in public issues. Do not create paid hosting;
the owner has explicitly withheld paid BuyBox/other new provisioning.

Exact owner gate and next steps: [issue #115](https://github.com/LeeTheLilBee/SimpleeMrkTrade/issues/115).
