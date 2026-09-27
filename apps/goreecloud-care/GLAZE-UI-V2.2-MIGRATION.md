# GoreeCloud Care — Glaze UI 2.2 Migration

**Status:** Implementation Candidate / Development adoption  
**Care line:** `0.2.0-dev2` / Debian `0.2.0~dev2`  
**Target Glaze UI:** `2.2.0` Stable  
**Canonical Glaze UI source revision:** `6731098b28dd0393faa878c70d989a221d714a20`  
**Canonical release tag:** `v2.2.0`  
**Human-approved Glaze visual source retained by 2.2:** `0411b0f6dd877aea30e2c5674e1acde0105fd97b`

## Why this migration exists

GoreeCloud Care completed a qualified Glaze UI V1.4 implementation candidate, but Glaze UI 2.2.0 is now the current Stable GoreeCloud design-system baseline. GoreeCloud policy requires user-facing applications to target the latest accepted Glaze UI before they can be considered Stable.

Therefore V1.4 remains historical migration/regression evidence only. It cannot satisfy current production-readiness or current Glaze conformance requirements.

The V1.4 candidate remains immutable at source revision:

`59e69b2ab0e2228e40598944fe927946f25ea237`

Its `0.2.0-dev1` / `0.2.0~dev1` artifact identity must not be rewritten or reused for 2.2 bytes.

## New candidate identity

The 2.2 migration uses a new development artifact identity:

- runtime: `0.2.0-dev2`
- Debian package: `0.2.0~dev2`
- lifecycle: Development
- Platform Contract conformance: nonconformant until exact-candidate evidence is accepted
- Stable promotion authorized: false

## Native scope

Care is a GTK3 Linux desktop application. Its supported Glaze product form-factor scope is:

- Desktop
- Wide Desktop

Compact and narrow window states are native resizable Desktop adaptation states. They are not claims that Care supports Phone, Tablet, TV, Foldable, Wearable, or Spatial product environments.

Unsupported form factors must remain explicit rather than being silently inferred from the design-system reference suite.

## 2.2 System Shell mapping

Care maps the Glaze UI 2.2 hierarchy conservatively:

- **Workspace:** host Linux desktop/window-management environment.
- **Application:** the GoreeCloud Care application window and Maintenance Insights application window.
- **System Overlay:** modal confirmation and result/notice dialogs only when invoked by Care.
- **System Panel:** Care does not claim a Glaze system-authority panel. The historical `.system-panel` CSS class is an application-local maintenance section only.
- **Critical System:** destructive or privileged confirmation moments use certainty-first, increasingly solid presentation.

Care does not rename Privacy Shield, Wardveil, Everkeep, Identity, or other producer-authoritative state into visual-only Glaze vocabulary.

## Material model

The active native mapping follows the current principle:

**Solid where users read or make explicit critical decisions. Glazed where users interact with transient navigation, command, control, or feedback chrome.**

For Care this means:

- maintenance lists, findings, status content, metrics, and consequential-action regions remain solid/near-solid;
- bounded Glaze is limited to appropriate command/navigation chrome;
- ordinary composition stays within one dominant Glaze surface plus at most three small floating Glaze controls;
- nested backdrop blur is not used;
- Reduced Transparency, Reduced Motion, Increased Contrast, HighContrast, Touch Assistance, and reduced-effects requests remove embellishment before hierarchy, state, target size, or focus.

## Accessibility and native equivalents

The 2.2 native adapter retains or adds:

- visible keyboard focus;
- 48 px governed target floor;
- 56 px Touch Assistance override when requested;
- GTK HighContrast/system-palette authority as the native equivalent for forced/high-contrast presentation;
- Reduced Motion;
- Reduced Transparency;
- Increased Contrast request support;
- effects-reduced fallback;
- DPI-aware reflow and compact/narrow/desktop/wide-desktop transformations;
- ATK/AT-SPI semantic status behavior;
- no state communicated by decorative material alone.

Representative acceptance still must verify 200% text-equivalent scaling/reflow, keyboard order, focus visibility/restoration, assistive technology, Light/Dark/Deep Dark, and real native rendering.

## Optional 2.2 system surfaces

Care does **not** currently implement or claim:

- Universal Search;
- Control Center;
- Glaze Intelligence components.

Those contracts therefore remain non-consumed rather than being simulated or cosmetically renamed.

## Historical V1.4 boundary

`glaze_v14.py` and `glaze_v14_global.py` remain in-tree as migration/regression evidence while the 2.2 line is under qualification. They are not imported by the active application entrypoint once the 2.2 switch is complete.

The 2.2 adapter may reuse qualified V1.4 window-adaptation behavior internally, but active window identity, provider identity, compatibility declarations, tests, packaging, and representative acceptance must all report 2.2.

## Qualification requirements

Before the dev2 branch can advance beyond Implementation Candidate, the exact final source/package identity must pass:

- source/unit/contract tests;
- active-provider and stale-version rejection tests;
- headless GTK runtime acceptance;
- System Shell/material-budget assertions;
- Light/Dark/Deep Dark contrast and hierarchy checks;
- HighContrast/system-palette authority;
- Reduced Motion and Reduced Transparency;
- Increased Contrast and Touch Assistance native equivalents;
- safe maintenance task-flow regression;
- live AT-SPI status and Maintenance Insights regression;
- reproducible Debian package construction;
- cross-environment package reproducibility;
- exact Stable `0.1.0` rollback reconstruction and checksum verification;
- install/remove/reinstall/downgrade/restore lifecycle;
- representative Zorin OS native/rendered/manual acceptance for the exact 2.2 candidate;
- exact-candidate Glaze UI consumer acceptance;
- independent Privacy Shield, Wardveil, Everkeep, and Platform Contract decisions where applicable.

## Promotion rule

A green build or green CI does not make Care Glaze UI 2.2 conformant or Stable.

Care may only claim current Glaze UI conformance when the exact 2.2 candidate satisfies every applicable current gate and application-specific native/product acceptance is complete. Stable Care promotion additionally remains subject to all applicable GoreeCloud platform-system and release-governance gates.
