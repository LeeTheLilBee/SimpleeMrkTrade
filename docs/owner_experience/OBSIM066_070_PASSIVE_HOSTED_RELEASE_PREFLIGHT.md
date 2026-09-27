# OBSIM066–070: Passive hosted Tower/OB release probe

The dedicated Tower branch contains a default-OFF hosted synthetic owner rehearsal with current Tower session, step-up, operational OB receipt and exact Origin/anti-CSRF enforcement. It now rotates its workspace token on explicit new session. **These facts from source tests do not prove that a specific onrender.com hostname is running that revision or that a real owner login worked.**

`scripts/ob_hosted_anonymous_release_probe.py` is a small Python-stdlib-only **read-only anonymous check** of the chosen owner's existing HTTPS origin. It accepts the exact expected 40-character commit SHA and calls only four fixed GET endpoints: Tower health, Tower runtime manifest, owner rehearsal page and its status endpoint. Redirects are *not followed*. It fails closed unless health is 200, manifest returns the exact expected revision and still reports broker/capital/manual/auto flags false, response revision headers (when present) are consistent, and both owner rehearsal URLs deny anonymous access. It never sends a credential, receives owner-specific data, follows a login redirect, changes Render, issues a trade, or claims a positive browser walkthrough.

Example using the documented original canonical owner front door (verify service identity/revision before interpreting the output):

```bash
python -m scripts.ob_hosted_anonymous_release_probe \
  --origin https://simplee-tower-ob.onrender.com \
  --expected-revision EXACT_40_CHARACTER_GIT_COMMIT
```

Exit codes: 0 = `PASS_ANONYMOUS_PREFLIGHT_ONLY`, 1 = `HOLD`, 2 = invalid input. In particular, even a 404 or 503 on a rehearsal endpoint can be compatible with anonymity or default-OFF feature state; it is **not** a hosted feature activation certificate.

**Current separate Render inventory:** the historical canonical `simplee-tower-ob.onrender.com` in the staging-named workspace uses manual deploy and its prior observed live revision was `1cfe40a3...` (September 14). A second workspace has auto-deployed `simplee-tower-ob-tunv.onrender.com` from the same Tower development branch. The unrelated `main`-tracking `simpleemrktrade.onrender.com` build remains misconfigured (missing root requirements and hosted start script on main). Do not choose a different URL just because its code is newer; do not quietly change a service's build command or point it to another app. Use the exact owner-approved canonical service and verify its actual live revision.

After passive preflight: separately confirm active current Tower owner login/step-up/OB receipt, hosted feature flag and exact configured origin, manual synthetic input, expiration, logout, browser session reset, storage volatility and runtime revision. Do **not** send owner login credentials to CI, a public probe or a chat. Default OFF remains in place until this distinct release review. Manual Live/Hybrid/Auto and paid resources remain HOLD.
