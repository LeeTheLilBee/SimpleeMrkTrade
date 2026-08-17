# Tower App Registry + Security Map Room / TWR001–TWR005

- Base main: `babb555c94b17c7820b2f43c6f83f26ae7ec02b2`
- Branch: `tower-app-registry-security-map-twr001-005`
- New Tower routes:
  - `/tower/security-map`
  - `/tower/security-map.json`
- New modules:
  - `tower/app_registry.py`
  - `tower/security_map_service.py`
  - `tower/security_map_web.py`

## What this layer does

This layer gives Tower an owner-only Security Map room that explains what Tower protects.

It registers current and future Simplee rooms:

- The Observatory
- The Teller
- Archive Vault
- The Clouds
- The Grounds

It shows current OB protected routes:

- `/ob/dashboard`
- `/ob/market-map`
- `/ob/symbol/<symbol>`
- `/ob/trade-center`
- `/ob/review-center`
- `/ob/owner-console`
- `/ob/owner-dashboard`

## Safety

- Unknown `/ob/*`: `403_default_deny`
- Owner-only routes:
  - `/ob/owner-console`
  - `/ob/owner-dashboard`
- Temporary placeholder:
  - `/ob/owner-dashboard`
- Live Auto: locked
- Broker execution: false
- Capital action: false

## Boundaries

- This does not redesign OB pages.
- This does not open Teller.
- This does not open Vault.
- This does not open Clouds.
- This does not open Grounds.
- This does not enable trading, broker execution, capital action, or Live Auto.

This makes Tower able to show the lock map instead of only enforcing it silently.
