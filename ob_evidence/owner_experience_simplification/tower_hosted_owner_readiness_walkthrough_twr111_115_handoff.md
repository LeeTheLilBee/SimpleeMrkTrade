# THE TOWER — TWR111–TWR115
## Hosted Release Readiness + Owner Walkthrough

Tower now gives its verified owner one honest, focused hosted-release walkthrough.
Hosted readiness requires the actual hosted runtime, its real HTTPS endpoint, the
exact deployed Git revision, secure owner credentials, protected Tower routes, and
separate confirmed durable storage for sealed packets and owner decision receipts.

- TWR111: Report real hosted configuration and storage blockers without exposing
  filesystem paths, owner-password hashes, session secrets, or hidden credentials.
- TWR112: Provide a beautiful owner-only Tower walkthrough with focused hosted
  identity, durable storage, release progress, and clear next-action cards.
- TWR113: Reuse genuine hosted HTTPS parity and the existing protected candidate
  publication route without weakening owner step-up, CSRF, or replay boundaries.
- TWR114: Continue the exact existing owner review and explicit approve, hold, or
  reject decision journey through an integrity-verified decision receipt.
- TWR115: Certify prerequisites only after verified owner approval; never change
  STAGING_READY or authorize staging, deployment, promotion, brokers, capital,
  Manual Live, or Live Auto.

Required hosted configuration:

- RENDER=true and RENDER_GIT_COMMIT=<the exact deployed Tower revision>
- TOWER_HOSTED_RELEASE_BASE_URL=https://your-real-hosted-tower
- TOWER_HOSTED_RELEASE_PACKET_PATH=/durable/tower/release-candidate.json
- TOWER_HOSTED_RELEASE_PACKET_STORE_DURABLE=true
- TOWER_RELEASE_RECEIPT_LEDGER_PATH=/durable/tower/owner-receipts.json
- TOWER_RELEASE_RECEIPT_STORE_DURABLE=true
- TOWER_OWNER_USERNAME=<real Tower owner>
- TOWER_OWNER_PASSWORD_HASH=<secure owner-password hash>
- TOWER_SESSION_SECRET=<strong hosted session secret>
- TOWER_LOCAL_WALKTHROUGH_MODE=false

Owner-facing protected routes:

- /tower/owner/release-review/walkthrough
- /tower/owner/release-review/readiness.json
- /tower/owner/release-review/walkthrough/certification.json

An expired same-revision candidate remains explicitly blocked because existing
replay protection prevents silently overwriting a candidate or bypassing its
owner decision. A distinct actual deployed revision is required.

Observatory remains untouched. No commit or push is created by this build.
