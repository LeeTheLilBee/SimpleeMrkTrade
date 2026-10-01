# Tower → BuyBox authenticated browser bootstrap — 2026-10-01

## What this closes

BuyBox BBX131–135 (merged into its parent branch via PR #308) added the reviewed receiver-side bridge:

1. Tower authenticates the current owner and requires fresh ecosystem step-up.
2. Tower independently rechecks current BuyBox owner entitlement, hosted publication/health truth and signing readiness.
3. Tower issues the existing 60-second signed `tower.buybox.owner.handoff.v1` token.
4. Tower serves a private/no-store transition document whose only crossing is an exact HTTPS form POST to `BUYBOX_PUBLIC_ORIGIN/tower/bootstrap`.
5. A self-hosted Tower script submits that form; the visible button is a no-JavaScript fallback.
6. BuyBox verifies Tower Origin + exact BuyBox host/path + token before its same-origin page posts to `/tower/owner-exchange`.
7. BuyBox's existing exchange must independently verify the live Tower session/step-up/entitlement, consume the handoff once in durable storage, then create its opaque owner session.

## Tower safety boundary

The Tower route remains `GET /tower/launch/buybox` behind `require_human_owner` and fresh password step-up. The configured BuyBox destination must be a bare HTTPS origin: no HTTP, credentials, path other than `/`, query or fragment. The signed bearer is never put in a GET URL, redirect location, cookie, local/session storage, access receipt, or Tower query string.

The transition response is `private, no-store`, has `Referrer-Policy: no-referrer`, `X-Frame-Options: DENY`, and a CSP whose `form-action` allows only the exact configured BuyBox HTTPS origin. If issuance fails, Tower returns only `BUYBOX_HANDOFF_ISSUANCE_FAILED`; signer/provider details are not echoed.

No BuyBox route is made launchable merely by this source. `app_truth_by_id("buybox").launchable` must still prove implemented/published/environment/health/current owner entitlement and real Tower launch registration. BuyBox still independently requires its private runtime configuration, storage+restore attestor and live Tower session verifier.

## Cross-repository contract evidence

`tower-system-integrations.yml` pins the BuyBox parent exact SHA `f690e998a077154265eab5969c64147fd2b95517`, verifies an actual Tower-issued token with BuyBox's merged receiver, and checks the exact bootstrap Origin/host/path transport. This prevents Tower and BuyBox from drifting while the runtime remains unreleased.

## Explicit non-authority

This crossing grants no acquisition approval, seller contact, closing, Teller money/capacity readiness, Vault access, Grounds operational acceptance, broker submission, capital movement, Manual Live or Live Auto authority. No paid infrastructure is provisioned by this change.
