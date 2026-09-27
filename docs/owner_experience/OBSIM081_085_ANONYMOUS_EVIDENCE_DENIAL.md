# OBSIM081–085 — anonymous denial check for owner evidence download

This is a passive follow-on to the accepted OBSIM076–080 owner-finalized fictional report export. The pre-existing anonymous exact-host release probe now also checks the fixed, read-only `/ob/owner-rehearsal/evidence.json` path. An unauthenticated response must be a denial or unavailable (redirect, 401, 403, 404, 409, 410, 503); a 2xx would produce `HOLD/ANONYMOUS_OWNER_REHEARSAL_DISCLOSURE`.

The owner evidence route returns report bytes **only** when accessed separately with current Tower owner session, step-up, an operational Observatory access receipt, the exact host, a session-specific token and finalized synthetic report. This probe sends none of those, never follows a login redirect and records only the status code, not any evidence body. The resulting two-host inventory copies only a fixed allowlist of redacted statuses and published revision.

This check does **not** verify a real owner session, select an official owner URL, turn on the hosted feature, certify report durability, deploy, or authorize real trading. A 404/503 can mean the feature is not enabled. It cannot substitute for an actual authenticated owner/device walkthrough.

Existing original candidate and secondary Tower host remain distinct, even if the secondary revision is newer. No Render resource/settings/secrets or paid service changes. Manual Live/Hybrid/Automated remain HOLD.
