# GoreeCloud Care — Glaze UI V1.4 Migration

**Status:** Implementation Candidate / Development  
**Runtime identity:** `0.2.0-dev1`  
**Debian identity:** `0.2.0~dev1`  
**Target:** Glaze UI `1.4.0`  
**Care branch:** `feat/goreecloud-care-glaze-ui-v1.4`  
**Glaze UI source revision:** `01c86323f8b747373d308026adc8b0881855cdc5`  
**Production / Stable claim:** Not granted

## Purpose

This migration revamps GoreeCloud Care around Glaze UI V1.4 while preserving Care's maintenance safety, privacy, accessibility, and fail-closed status semantics.

Glaze UI 1.4.0 is a form-factor evolution release built on the V1.3 expressive/material foundation. Care therefore retains the established V1.3 semantic material mapping as an implementation foundation and adds an application-specific V1.4 native desktop composition layer instead of replacing proven controls with unrelated visual effects.

The V1.4 revamp is intentionally a new `0.2.0` development line. Stable `0.1.0` remains an immutable historical artifact and is not silently replaced by new V1.4 bytes.

## Native Care mapping

GoreeCloud Care is a GTK3 desktop application. V1.4 is mapped into four resizable native window composition states:

- `compact` — narrow Care windows with reduced surface radius and visual density while retaining every task.
- `narrow-desktop` — single-reading-column composition before multi-pane presentation is appropriate.
- `desktop` — canonical Care desktop composition.
- `wide-desktop` — increased breathing room and hierarchy without inflating targets or text merely to consume width.

These are window composition states. They do not claim that the desktop Care binary is a Mobile, Tablet, or TV product.

Care resolves those states through its DPI-aware effective-width contract rather than raw physical window pixels.

## Visual and interaction changes

The V1.4 layer introduces:

- Functional-glass treatment restricted to command/navigation chrome.
- Stable, opaque or near-opaque reading and consequential-action surfaces.
- More deliberate hero, status, maintenance, and system-action surface geometry.
- Compact, Narrow Desktop, Desktop, and Wide Desktop responsive state classes.
- Compact-window simplification without task loss or focus-order changes.
- A 48 px minimum target contract at the Care mapping boundary.
- Strong visible focus treatment independent of material effects.
- Reduced-transparency, reduced-motion, border-emphasis, and HighContrast precedence.
- Application/window binding through the GTK application `window-added` lifecycle and `size-allocate` updates.
- Main Care presentation identity updated from the stale V1.3 `Adaptive Resonance preview` label to `Glaze UI V1.4`.

## Source architecture

V1.4 runtime modules:

- `goreecloud_care/glaze_v14.py` — V1.4 semantic mapping, form-factor resolution, CSS, and per-window controller.
- `goreecloud_care/glaze_v14_global.py` — process-level provider and window lifecycle synchronization.

The package entrypoint installs the V1.4 process controller instead of the V1.3 global provider.

The V1.3 implementation remains in-tree as the immediately preceding expressive/material foundation and historical compatibility reference. It is not the active Care product identity.

## Lifecycle and artifact identity

The V1.4 migration must never reuse the accepted Stable `0.1.0` package identity for different bytes.

Current identities are therefore:

- runtime: `0.2.0-dev1`;
- Debian package: `0.2.0~dev1`;
- lifecycle: Development;
- Platform Contract conformance: `nonconformant` until external/manual blockers are satisfied.

Stable `0.1.0` remains bound to source revision `bbc4779454c2887b810aa0ddc9e8a686a4c68ebd` and package SHA-256 `819cff6e0132bf6b09df0986682995c25b14c39e74982f725efd0b5a21b71160`.

The 0.2 lifecycle qualification rebuilds that Stable source and requires the resulting rollback package to match the accepted Stable SHA-256 exactly before downgrade testing proceeds.

## Acceptance policy

Green automation does not by itself make Care Stable or grant Glaze UI V1.4 consumer acceptance.

Before Care can claim V1.4 conformance or advance toward Stable, the exact candidate must still obtain:

1. representative Zorin OS 17.3 package/runtime acceptance for the exact source/package identity;
2. rendered/manual V1.4 review at Compact, Narrow Desktop, Desktop, and Wide Desktop sizes;
3. keyboard-only, visible-focus, Orca, and physical accessibility review;
4. physical Light, Dark, Deep Dark, HighContrast, Reduced Motion, Reduced Transparency, Show Borders, and enlarged-text review;
5. native window-control/compositor optical review;
6. exact-candidate Glaze UI consumer acceptance;
7. exact-candidate Privacy Shield runtime/production governance before production privacy status is claimed;
8. exact-candidate Wardveil governance before any Wardveil protection claim transfers;
9. exact-candidate Everkeep promotion before continuity can become `ready`;
10. a later explicit release-candidate and Stable promotion decision.

Until those gates pass for the exact candidate identity, the correct state remains **Development / Implementation Candidate / nonconformant**.

## Qualification records

Exact automated run IDs and package digests belong in pull-request/release evidence bound to the exact source head that produced them. Updating this migration specification itself creates a new source identity and therefore intentionally does not self-claim that earlier exact-head qualification automatically transfers.

## Follow-up direction

After V1.4 acceptance, the next Care design work should focus on improving system-health orchestration, information architecture, and task guidance without weakening the product boundary between maintenance truth and presentation. Any later Glaze UI migration must create a new application-specific evidence identity rather than inheriting this migration's acceptance automatically.
