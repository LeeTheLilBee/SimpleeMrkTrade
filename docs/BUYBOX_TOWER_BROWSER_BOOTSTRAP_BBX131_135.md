# BBX131–135 — Tower browser bootstrap crossing

Tower PR #296 established the authenticated owner + step-up BuyBox launch gate and deliberately stopped at `BUYBOX_BROWSER_BOOTSTRAP_NOT_IMPLEMENTED`. BuyBox already had a strict same-origin `POST /tower/owner-exchange` receiver, so a direct cross-origin Tower form could not safely satisfy that contract.

BBX131–135 adds the missing receiver-side browser bridge without weakening the exchange.

## Transport

1. Tower performs its existing current owner/session/step-up/identity/entitlement/publication/signing preflight.
2. Tower issues the existing 60-second `tower.buybox.owner.handoff.v1` token.
3. Tower posts that token in a form body to BuyBox `POST /tower/bootstrap`.
4. BuyBox accepts the bootstrap only when the request Origin is the exact configured Tower HTTPS origin, the destination is the exact configured BuyBox HTTPS host/path, there is no query string, the content type is form-urlencoded, and the body contains exactly one `handoff`.
5. BuyBox verifies the token signature/claims/TTL before rendering anything.
6. The no-store BuyBox-origin bootstrap page immediately posts the same signed token to the existing `POST /tower/owner-exchange`.
7. The existing exchange independently re-verifies the token, live Tower session/step-up/entitlement truth, one-use durable handoff consumption, and server-side owner-session creation before issuing the opaque BuyBox browser cookie.

## Explicitly prohibited

- no bearer in a GET/query/fragment
- no localStorage/sessionStorage
- no handoff cookie
- no Tower-origin bypass on `/tower/owner-exchange`
- no loosening of one-use consumption
- no bypass of live Tower session verification
- no independent BuyBox login in Tower mode
- no broker, capital, closing, Vault, Teller or acquisition authority

This closes the BuyBox-side browser-bootstrap source gap only. Tower must separately adopt the reviewed `POST /tower/bootstrap` transport and the hosted BuyBox origin/runtime/storage/session verifier still require independent certification.
