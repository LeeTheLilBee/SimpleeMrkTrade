# Tower source integration of accepted OBSIM — September 27

This branch overlays only the 30 files required to bring accepted OB's dormant local rehearsal source and its independent canonical replay/time/capital dependencies to Tower's active development branch. Existing Tower files and web.app are deliberately unchanged. The source inherits the same locally bound script, not a hosted route. The only imported OB file modified from main is a path-portable test that examines hosted_tower.py when managed_staging.py does not exist.

CI asserts local-only route isolation, canonical unchanged 30-second human tick, private single-host report verification and Tower's existing default-deny room guard. A follow-up hosted adapter must be reviewed independently, never by exposing the loopback server.

This does NOT alter the provider, broker, mode locks, deployment settings or any Render service. It does not imply Tower hosted identity is integrated with the replay. Tower remains the only identity/router authority and signed OB account source remains source-only. Existing main OBBETA011–015 owner dashboard source-label fix is not wholesale overwriting Tower's divergent dashboard contract in this source-only import.
