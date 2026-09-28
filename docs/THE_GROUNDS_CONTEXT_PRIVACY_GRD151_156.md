# Grounds GRD151–156 — context switching and truthful resident balance UI

## Defect
The existing real browser kept the old unit/property's private workspace visible until a new `GET /grounds/api/workspace` finished. Even with generation guards on late responses, a pending, failed or denied new request could temporarily display the previous lease, private notice content, work cards or source-bound Soulaana text under the newly chosen property selector. The original static rent placeholder also said "Nothing is due based on this screen", which could mislead a resident when Teller was disconnected.

## Source fix
- `refresh()` increments a generation before any request; synchronously clears prior workspace, lease, notices, work/operational cards, rent projection, historical Soulaana text and status. Hides the previous content during authorization/response and shows only the selected authorized context.
- `verifyWorkspaceContext` independently checks the protected workspace response's `source=grounds`, exact property, current verified Tower role and (for residents) selected unit **before rendering any data**. This is browser defense-in-depth; the server's actual Tower/member/lease authorization remains mandatory.
- A mismatched response closes the view rather than falling back to old data. Generation and `state.view` checks prevent a late rent or workspace result from overwriting a newly selected property/unit. Source fetch errors leave the old private DOM erased.
- An invalid/no-selection state displays generic locked guidance. Context changes erase old transient alert content; same-context explicit action feedback is retained.
- Initial and disconnected Teller language now says the amount is *unknown*, never $0 or paid. The service badge distinguishes a validated read-only Teller snapshot from an unavailable/disconnected status, and the browser does not add checkout.
- The existing CSP, CSRF, Tower identity receiver, exact-lease rent projection and source-backed other desks remain unchanged.

## Regression evidence
`grounds/tests_js/context_switch.cjs` runs the actual `grounds/ui/app.js` in an isolated, fake DOM/Node VM, replacing fetch with deferred synthetic responses. It asserts initial authorized content, **immediate DOM clearing** on property change, refusal of a wrong property/unit response, successful recovery with correct property, late older response isolation, and no disconnected zero-balance assertion. `grounds/test_grounds_browser_context.py` runs this harness inside normal source CI, where Node is provisioned. No external website, person, production lease, provider or money is used.

The change is only source/privacy hardening. The independent external Tower operating-release/identity modules, private tenant DB and recovery, real Teller/Vault/delivery, legal/privacy/accessibility review and owner walkthrough remain mandatory for any hosted tenant use. Do not equate a passing fake-DOM test with an external accessibility audit or real-world production acceptance.
