# The Grounds — final visual system GRD212–218

The Grounds visual system is intentionally **Midnight Navy + Champagne Gold + Soft Aqua**. This is a product-level visual contract, not a generic Simplee World dark theme and not an Observatory/Tower clone.

## Locked core palette

- Midnight Navy background: `#090D19`
- Navy surface/input: `#121B2D`
- Smoky Navy glass: `rgba(21,29,49,.8)`
- Pearl White text: `#F1F5FE`
- Blue-Gray secondary text: `#ADBDD5`
- Champagne Gold: `#E7C684`
- Gold button gradient: `#E8CC91 → #CAA15C`
- Soft Aqua operational accent: `#A1E7D4`
- Muted Coral urgency: `#FF9D9D`

The page remains dark at every normal surface. White can appear only as tiny translucent light effects; no white page/card/input background is part of the Grounds theme.

## Cohesion pass

GRD212–215 centralizes previously scattered UI colors as CSS custom properties, keeps panels/cards/inputs in the same navy family, gives Soulaana a restrained champagne-tinted glass treatment, changes the keyboard skip link from a white default box to a high-contrast champagne control, and applies the same visual language to My Home, Daily Grounds, maintenance conversation, Move-In/Move-Out Concierge, Property Health, delivery status and privacy history.

The ambient layer adds restrained champagne, blue and aqua light rather than a bright celestial field. Gold remains a hierarchy/focus accent; aqua remains status/operational; coral remains urgency. Grounds does not adopt OB's market-map/starfield treatment or Tower's launcher chrome.

## Accessibility constraints

The declared opaque foreground/background pairs used for normal text are regression-tested at WCAG AA 4.5:1 or better. Existing larger-text and reduced-motion support remain. `prefers-contrast: more` increases borders and muted-text contrast and disables glass blur. Keyboard focus remains a visible champagne-gold outline. These are source-level protections only; real human accessibility testing is still required before live resident release.

## Release boundary

This theme pass changes no authority, role, lease, payment, document, provider, notification, emergency, legal-entry or deployment semantics. Grounds parent PR stays draft until the existing external certification and owner acceptance gates are genuinely satisfied.
