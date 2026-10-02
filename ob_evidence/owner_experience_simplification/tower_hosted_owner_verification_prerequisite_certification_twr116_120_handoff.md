# THE TOWER — TWR116–TWR120
## Hosted Owner Verification + Release Prerequisite Certification

Tower now carries the completed TWR111–TWR115 hosted owner walkthrough into a
separate release-prerequisite certificate. The new certificate is issued only
when the current Tower owner session is freshly verified, the hosted walkthrough
is certified, the exact candidate is owner-approved, and the exact durable owner
decision receipt is integrity-valid and matches the candidate revision and packet.

- TWR116: Re-verify the fresh Tower owner context and the exact approved candidate,
  revision, packet integrity hash, receipt ID, and durable receipt chain.

- TWR117: Build a deterministic integrity-sealed prerequisite certificate from
  that verified chain. The certificate is a projection, not a new mutable runtime
  record, and it grants no release-execution authority.

- TWR118: Expose a focused owner-only certificate room plus protected verification
  and certification JSON surfaces behind the existing Tower owner step-up.

- TWR119: Hand the certified owner from the hosted walkthrough and owner dashboard
  into the prerequisite certificate without turning the certificate into a deploy
  button or weakening the existing release-review flow.

- TWR120: Verify the full genuine hosted candidate → explicit owner approval →
  verified receipt → prerequisite certificate path while every execution boundary
  remains false.

Protected owner routes:

- /tower/owner/release-review/prerequisites
- /tower/owner/release-review/prerequisites/verification.json
- /tower/owner/release-review/prerequisites/certification.json

The certificate means only: the release prerequisites proven by the current
hosted owner-verification chain are certified.

It does not set STAGING_READY, deploy or promote anything, authorize broker
submission or capital movement, or unlock Manual Live or Live Auto.

A separate release-execution gate remains mandatory.

Observatory remains untouched.

This build does not stage, commit, or push.
