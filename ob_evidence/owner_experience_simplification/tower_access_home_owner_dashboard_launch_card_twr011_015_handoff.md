# Tower Access Home Owner Dashboard Launch Card / TWR011–TWR015

- Base tower-dev: `1e28b730638da9a04d342df2928a6cb465b37948`
- Branch: `tower-access-home-owner-dashboard-launch-card-twr011-015`
- Built from: `tower-dev`
- Enhanced route:
  - `/tower/access-home`
- New JSON route:
  - `/tower/access-home-launches.json`
- New module:
  - `tower/access_home_owner_launches.py`

## What this layer does

This layer adds discoverable Access Home launch cards for:

- Tower Owner Dashboard / People Access Desk
- Tower Security Map

It preserves the existing Access Home page and injects an owner launch dock into the rendered HTML.

## Safety boundaries

- Does not replace Access Home.
- Does not create real accounts.
- Does not send invite emails.
- Does not grant real app access.
- Does not unlock Live Auto.
- Does not enable broker execution.
- Does not enable capital action.

## Owner visible goal

From `/tower/access-home`, Solice should be able to see buttons/cards for:

- `/tower/owner-dashboard`
- `/tower/security-map`
