# GoreeCloud Care — Glaze UI consumer record

## Current development authority

GoreeCloud Care `0.2.0-dev2` is the active **Glaze UI 2.2 / `2.2.0` implementation candidate**.

It is **not yet a conformant or Stable Glaze UI 2.2 consumer**. Glaze UI 2.2.0 is the current Stable GoreeCloud design-system baseline, but design-system Stable status does not automatically certify downstream applications. Care must earn exact-source, exact-package, native/rendered, accessibility, product, representative-target, and authority-owned consumer acceptance.

Current design-system authority:

- Glaze UI target version: `2.2.0`
- canonical Glaze UI source revision: `6731098b28dd0393faa878c70d989a221d714a20`
- release tag: `v2.2.0`
- approved visual source retained by 2.2: `0411b0f6dd877aea30e2c5674e1acde0105fd97b`
- Care runtime identity: `0.2.0-dev2`
- Care Debian identity: `0.2.0~dev2`
- Care lifecycle: Development
- Platform Contract conformance: nonconformant
- Glaze consumer eligibility: false until exact Care acceptance is promoted

The active Care entrypoint installs `glaze_v22_global`. The main Care layout resolves through `glaze_v22.layout_environment`. Glaze UI V1.4 remains in-tree only as qualified migration/regression evidence and must not be treated as the current design-system authority.

## Current native product scope

Care is a GTK3 Linux desktop application. Its supported Glaze UI product form-factor scope is:

- Desktop
- Wide Desktop

Compact and Narrow Desktop are resizable-window adaptation states inside the Desktop product scope. They are not claims that Care supports Phone, Tablet, TV, Foldable, Wearable, or Spatial products.

The form-factor classifier remains DPI-aware so raw physical pixel width is not mistaken for logical composition width.

## System Shell mapping

Care maps the current System Shell hierarchy conservatively:

- **Workspace:** the host Linux desktop/window-management environment;
- **Application:** GoreeCloud Care and Maintenance Insights application windows;
- **System Overlay:** Care-owned modal confirmation/result/notice moments only;
- **System Panel:** Care does not claim a Glaze system-authority panel; the historical `.system-panel` class remains an application-local maintenance section;
- **Critical System:** destructive or privileged confirmation moments use certainty-first presentation.

Care must not visually rename Privacy Shield, Wardveil, Everkeep, Identity, or another producer-authoritative platform state into a local Glaze-only claim.

## Material and Glaze-budget contract

Care follows the current material rule:

**Solid where users read or make explicit critical decisions. Glazed where users interact with transient navigation, command, control, or feedback chrome.**

Required Care behavior:

- maintenance lists, status surfaces, findings, metrics, and consequential-action regions remain solid or near-solid;
- bounded Glaze is limited to appropriate command/navigation chrome;
- ordinary composition stays within one dominant Glaze surface plus at most three small floating Glaze controls;
- nested backdrop blur is not used;
- destructive and privileged moments become more certain, not more decorative;
- visual material alone never communicates success, failure, cancellation, warning, privilege, or authorization state;
- semantic shape roles are used instead of universal pills;
- repetitive cardification remains prohibited.

GTK3 does not claim compositor-authoritative backdrop behavior or rendering capabilities it cannot prove.

## Accessibility precedence

Care's 2.2 adaptation must remove embellishment before hierarchy, meaning, focus, state, or task completion.

Current native requirements include:

- GTK HighContrast/system palette authority as the native forced/high-contrast authority;
- Reduced Transparency;
- Reduced Motion;
- Increased Contrast;
- Show Borders;
- effects-reduced fallback;
- 48 px governed interactive target floor where applicable;
- 56 px Touch Assistance target floor where applicable;
- large-text / approximately 200% text-equivalent reflow without unreachable primary actions;
- explicit visible focus independent of material effects;
- logical forward/reverse keyboard order across composition changes;
- truthful ATK/AT-SPI status delivery;
- read-only Maintenance Insights accessibility;
- no state communicated by color, blur, glow, or material alone.

Safety-critical appearance/accessibility state resolves before asynchronous window binding. Allocation-derived Desktop adaptation remains window-specific.

## Optional current-system surfaces

Care does not currently consume or claim:

- Universal Search;
- Control Center;
- Glaze Intelligence components.

They remain explicitly non-consumed instead of being simulated or cosmetically renamed.

## Current automated qualification gates

The exact `0.2.0-dev2` candidate must pass at least:

1. source/unit/contract validation;
2. exact active-provider and stale-version rejection checks;
3. Glaze UI 2.2 System Shell/material-budget assertions;
4. DPI-aware Compact/Narrow/Desktop/Wide Desktop runtime adaptation;
5. safe maintenance task-flow acceptance;
6. live core and Maintenance Insights AT-SPI acceptance;
7. Dark and Deep Dark HeaderBar contrast at or above the existing runtime threshold;
8. Clear, Balanced, and Dense clarity behavior;
9. Reduced Motion and Reduced Transparency;
10. Increased Contrast, Touch Assistance, and effects-reduced native behavior;
11. GTK HighContrast palette-authority behavior;
12. deterministic same-environment package reproducibility;
13. Ubuntu 22.04 / Ubuntu 24.04 byte-for-byte package reproducibility;
14. immutable Stable `0.1.0` rollback reconstruction and SHA verification;
15. installed package lifecycle, launcher isolation, provenance, and Wardveil-compatible privilege-boundary prequalification.

Green automation is supporting evidence only. It does not establish human/native or authority acceptance.

## Required representative/native acceptance

Before Care can claim current Glaze UI 2.2 consumer acceptance, the exact candidate must pass representative Zorin OS review covering at least:

- rendered System Shell hierarchy and material budget;
- compact, narrow, desktop, and wide-desktop composition;
- Light, Dark, Deep Dark, and GTK HighContrast physical presentation;
- Reduced Transparency, Reduced Motion, Increased Contrast, Show Borders, effects-reduced, and Touch Assistance behavior;
- 48 px and 56 px target expectations where applicable;
- large-text / approximately 200% text-equivalent reflow;
- keyboard-only traversal, focus visibility, and focus restoration;
- Orca/AT-SPI scan, success, cancellation, failure, and Maintenance Insights quality;
- canonical Care launcher/icon/AppStream rendering;
- destructive and privileged confirmation/cancellation/denial/success behavior;
- native window-control/compositor quality;
- confirmation that unsupported product form factors and optional system surfaces are not claimed.

A blank, inherited, inferred, or screenshot-only result is not accepted evidence where physical/native interaction is required.

## Authority-owned acceptance

Current Glaze UI conformance requires a separate authority-owned Care consumer decision after representative evidence exists. Care cannot self-promote that decision.

Privacy Shield, Wardveil, Everkeep, Platform Contract, release, and Stable decisions remain separately governed and must not be inferred from Glaze acceptance.

## Historical V1.4 migration candidate

The qualified V1.4 candidate remains preserved as historical/regression evidence:

- source revision: `59e69b2ab0e2228e40598944fe927946f25ea237`
- runtime: `0.2.0-dev1`
- Debian package: `0.2.0~dev1`
- package SHA-256: `94b75ef2bf1138939e3dc77a73b71f476f0f6fa9688edeef13cab476d46bb07c`
- Glaze UI target: `1.4.0`
- Glaze source revision: `01c86323f8b747373d308026adc8b0881855cdc5`

That evidence remains useful for regression comparison and rollback analysis. It cannot satisfy current production or Stable Glaze UI alignment because 2.2.0 is the current Stable baseline.

## Historical Stable 0.1.0 authority

Stable GoreeCloud Care `0.1.0` remains an immutable historical accepted consumer of Glaze UI V1.2 / `1.2.0`:

- release source: `bbc4779454c2887b810aa0ddc9e8a686a4c68ebd`
- Care tree: `ebe028347c978b6d09fb1d2af011729249f63bc3`
- package SHA-256: `819cff6e0132bf6b09df0986682995c25b14c39e74982f725efd0b5a21b71160`
- representative target: Zorin OS 17.3
- Glaze authority: `c3b077cd454825cd5a74cf21ba9e5dd4c25f94ae`
- historical consumer status: `accepted-v1`
- target version: `1.2.0`

That historical release acceptance is preserved for audit and rollback. It does not transfer current Glaze conformance to dev2.

## Fail-closed rule

Glaze acceptance is exact-source, exact-package, version-specific, and product-scope-specific. Any change to Care presentation behavior, canonical icon, focus/accessibility behavior, supported product form factor, required Glaze version, runtime/package identity, active provider, or current Glaze authority invalidates assumptions that earlier acceptance transfers automatically.

`0.2.0-dev2` therefore remains **Development / Implementation Candidate / nonconformant** until its own exact 2.2 automated qualification, representative native review, application-specific Glaze authority acceptance, and all separately applicable GoreeCloud governance are complete.
