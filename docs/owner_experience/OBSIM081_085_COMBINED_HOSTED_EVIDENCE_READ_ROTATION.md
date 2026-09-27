# OBSIM081–085 — combined hosted rehearsal + finalized evidence rotation integrity

Two separate source patches landed against the same Tower branch at almost the same time: [#119](https://github.com/LeeTheLilBee/SimpleeMrkTrade/pull/119) added default-OFF owner-downloadable FINAL-only fictional evidence, and [#118](https://github.com/LeeTheLilBee/SimpleeMrkTrade/pull/118) made hosted status/sample GETs recheck their per-workspace token under the same lock as explicit /new rotation.

A new evidence GET was introduced by #119. It originally followed the earlier status pattern (check in before_request, get_workspace, then lock), and so did not consume the atomic current-token guard from #118. The evidence endpoint must revoke its old read capability too. It now uses `_current_read_item()` **inside** the shared lock before checking final status or constructing the report packet.

A deterministic two-browser-tab test places a legitimate /new POST precisely between a previous GET's before_request token approval and its view. The old status, sample **and finalized evidence** GETs must return 409; the new token can access new status/sample but cannot export evidence until that new session is explicitly finalized. Distinct unauthorized/missing-session, feature default-OFF, synthetic source/amount and no trading flags remain enforced.

Combined CI on exact reviewed head runs **both** previously accepted branches' HTTP and offline chain validation tests, canonical replay/archive/CSRF/route-default-deny and Tower/Teller smoke, plus browser syntax. It does not claim to repair unrelated nonhermetic historical Tower full-suite tests or prove a specific deployed hostname has been authenticated by its owner.

**Release status:** Source hardening only. No feature activation, paid Render, provider, real capital, live broker order, durable server report storage, new protected account grant or Hybrid/Auto unlock. Owner-site selection, exact live revision, explicit default-OFF flag review and actual current owner device walkthrough remain OPEN.
