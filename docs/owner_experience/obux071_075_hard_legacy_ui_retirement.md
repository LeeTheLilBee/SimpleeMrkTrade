
# OBUX071–075 — Hard Legacy UI Retirement

## Root cause

The previous cleanup treated old UI as presentation residue.

That was insufficient.

Two historical JavaScript files remain active renderers:

- `ob_mission_accounts.js`
- `ob_room_data_polish.js`

The mission renderer can build `Current Mission Account`.

The V27 renderer can build `Room-Level Data Polish · V27`, including delayed
startup and repeated rendering after engine-feed updates.

The normal Dashboard also continued importing `ob_atmosphere.css`, while
modified modern assets retained older browser cache identities.

## New product boundary

Normal Dashboard:

- no mission-account initialization
- no mission-account bar
- no mission-account drawer
- no V27 panel
- no V27 room-data-polish state
- no OBUX027 atmosphere stylesheet dependency

Owner Dashboard remains the only `/ob/*` path where the historical mission
renderer is permitted to initialize.

V27 remains historical/proof code only and is denied on every `/ob/*`
product route.

## Defense in depth

A new cache-fresh `ob_product_surface_policy.js` is loaded in the normal
Dashboard head.

It removes forbidden legacy UI even if an older browser-cached producer is
somehow evaluated.

The source renderers themselves are also hard gated, so this is not merely
a CSS hide.

## Modern Dashboard sky

The normal Dashboard no longer depends on `ob_atmosphere.css`.

Required sky geometry and motion now live with the interchangeable modern
theme layer.

## Cache repair

Active changed assets now use the OBUX071–075 cache identity:

- theme CSS
- theme switcher
- beta surface cleanup
- session arrival
- product surface hard policy
