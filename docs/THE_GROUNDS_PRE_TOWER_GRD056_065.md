# Grounds — pre-Tower development checkpoint GRD056–065

**Branch:** `grounds-resident-operations-grd001-005` / [draft Grounds PR #51](https://github.com/LeeTheLilBee/SimpleeMrkTrade/pull/51). Tower's complementary review-only handoff remains [draft PR #52](https://github.com/LeeTheLilBee/SimpleeMrkTrade/pull/52). Do not merge, enable public ingress, use live tenant data, or provision paid Render until Tower/security/integration approval. Original historical 130-item inventory was not fully recovered; this checkpoint only claims the code listed below.

## Delivered independently of Tower

- **GRD056 — resident-list intersection.** Fixed a subtle narrowing issue: a resident with two genuine Grounds lease memberships but only one currently Tower-granted unit can list requests for **only the Tower-granted unit**, never both. Item-by-item and resident Home access already enforce both conditions. Regression tests cover same subject with two separate active units.
- **GRD057–059 — physical service log.** Source-only `work_resources.py` stores append-only, property/unit/job-keyed material counts and labor minutes for manager, supervisor, owner, or **actually assigned technician**. One transparent correction event may reverse an original (never deletes or edits history); resident, vendor, cross-property and unassigned reads/writes fail closed. Closed/confirming jobs cannot be silently corrected. It has **no dollars, pricing, inventory reservations, employee time-clock, payroll, vendor billing or financial entries**. All financial administration remains with Teller.
- **GRD060 — appointment database guard.** Added a unique index preventing two active appointments for the same work order at storage level, in addition to the service-level check. Cancelled appointment history is retained.
- **GRD061–062 — local synthetic-fixture integrity and backup.** `dev_integrity.py` checks SQLite integrity, foreign keys, active-lease/occupancy/member coherence, urgency triage, exact-turnover inspection, work/lease scope and reversal correctness using **aggregate counts only**. A deliberate developer action can make a new non-overwriting local snapshot via SQLite backup and verify the copy. It never uploads, schedules, encrypts, migrates or certifies a real tenant backup, and explicitly rejects damaged or inconsistent sources. Only use on fictional disposable developer fixtures.
- **GRD063 — Soulaana additions.** The read-only assistant can explain staff-only materials/minutes and property-scoped preventive plans due as of a named date; she never makes resident billing, payroll, inventory, dispatch or completion claims. Tests assert access failures for resident/cross-property scopes.
- **GRD064 — work-proof scope hardening.** The normalized output of a future **trusted** Tower/Vault verifier must match Vault source, Grounds audience, exact work, proof kind, actor, property and unit before an opaque evidence ref is recorded. No raw URLs or upload. Tests reject kind, actor, source, audience and property/unit substitution, as well as missing verifier and duplicate reference.
- **GRD065 — honest readiness snapshot.** Local work log, local integrity and fixture backup available; live staff resource ledger, hosted recovery proof, real Vault ingestion, payments and vendor payroll stay unavailable.

## Tower/Vault reconciliation needed

The eventual Vault proof adapter for work attachments must return an authenticated, normalized envelope like:

```text
source=vault; audience=grounds; status=verified_sealed
work_ref=<exact existing work ID>; kind=<approved proof kind>
actor_ref=<actual authenticated uploader>; property_ref=<work property>
unit_ref=<work unit>; proof_ref=<opaque sealed ref>
```

This illustration is **not** a production wire token or cryptographic protocol; Tower/Vault own signature, nonce, audience, expiry, session, replay, revocation and proof provenance. An identity `lambda` in a unit test is not a verifier. Uploaded content storage, scanning, privacy, retention, resident permissions, proof display and closing policy remain integration gates.

Other Tower decisions unchanged: separate resident/staff/owner sessions, certified co-tenant/occupant identity and lease/member revocation, assignment and expiry, entry and notice separation, urgent human response, audit and rollback. Neither this source batch nor a checklist licenses a hosted tenant app.

## Developer verification

```bash
python -m compileall -q grounds
python -m unittest discover -s grounds -p 'test_*.py' -v
```

The branch's GitHub Actions workflow runs these checks and Node syntax validation of `grounds/ui/preview.html`. Check the *latest head SHA* before asserting completion; older passing runs do not verify newer code. No merge or deployment follows automatically.
