# THE TOWER — TWR106–TWR110
## Candidate Publication + Owner Decision State

Tower now generates a real release-review candidate only from passing HTTPS hosted
runtime parity, publishes its integrity-sealed packet atomically, and shows exact
owner decision state in the existing premium Tower dashboard and release room.

- TWR106: Probe genuine hosted health, runtime identity, and login surfaces; reject
  fake, failed, insecure, wrong-revision, or safety-opening parity.
- TWR107: Publish the canonical sealed candidate using file locking, a temporary
  file, fsync, atomic replacement, persisted integrity verification, and a
  same-revision replay block that preserves an existing owner decision.
- TWR108: Project no-candidate, stale, changed, ready, approved, held, and rejected
  states only after owner session, step-up, exact packet, and receipt verification.
- TWR109: Show one focused status chip on the existing owner dashboard; allow a
  protected genuine candidate check inside the existing Tower release room.
- TWR110: Certify candidate publication → owner review → explicit owner decision →
  verified decision receipt without opening any execution boundary.

Runtime configuration for genuine hosted publication:

- TOWER_HOSTED_RELEASE_BASE_URL=https://your-real-tower-host
- TOWER_HOSTED_RELEASE_PACKET_PATH=/your/durable/tower/release-candidate.json
- TOWER_HOSTED_RELEASE_PACKET_STORE_DURABLE=true
- Existing receipt storage remains subject to its separate durable-store requirement.

Deployment, promotion, production promotion, STAGING_READY changes, broker
submission, capital movement, Manual Live, and Live Auto remain unauthorized.
Observatory remains untouched. No commit or push is created by this build.
