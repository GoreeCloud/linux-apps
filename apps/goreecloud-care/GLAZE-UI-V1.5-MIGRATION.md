# GoreeCloud Care — GLAZE UI V1.5 Migration

## Status

- Care candidate: `0.2.0-dev3`
- Care lifecycle: **Development**
- Current required Stable Glaze target: **GLAZE UI V1.5 / `1.5.0`**
- Retained optical baseline: **GLAZE UI `1.4.1`**
- Consumer acceptance: **not established**
- Production eligibility: **not established**

This record supersedes V1.4.1 as the **current migration target** but does not erase `GLAZE-UI-V1.4-MIGRATION.md`. The V1.4.1 record remains historical implementation/provenance for the optical baseline that V1.5 inherits.

## Verified upstream authority

Current Glaze authority requires every applicable GoreeCloud user-facing consumer to migrate independently to GLAZE UI V1.5 / `1.5.0`. V1.5 retains the V1.4.1 optical foundation and adds Context + Capability Awareness. The current Stable Glaze reviewed implementation anchor is `ee1032a0822ab8e103f8afe48e5c1859fde65cc9`; stable integration provenance is `b7fa8164bfdeaa1dc0acb21b770e7601120da04e`.

Central Platform Contract `0.2` now also requires applicable consumers to target `1.5.0` on authoritative `GoreeCloud/GoreeCloud` main commit `398098d9391ac0369a79f228ca6b94d3c425fe39`.

## Current Care implementation truth

Care's active GTK presentation is still the V1.4.1 optical implementation. It remains Development/nonconformant and must not be called a V1.5 accepted consumer.

This migration slice adds a bounded V1.5 source foundation in `goreecloud_care/glaze_v15.py` with pure deterministic presentation resolution for explicit authoritative capability/context inputs. The foundation:

- preserves `1.4.1` as the optical baseline;
- records `1.5.0` as the current target;
- preserves Development and `consumer_eligible = false` state;
- accepts explicit capability state with provider and provenance;
- fails closed to `unknown` when provider facts conflict;
- exposes unavailable/degraded explanations rather than inventing support;
- makes accessibility-precedence presentation explicit;
- allows runtime/connectivity state to reduce or explain presentation without changing underlying capability truth;
- forbids automatic fallback execution and automatic consequential action;
- does not request permission, grant authorization, call PolicyKit, or run maintenance.

A bounded privileged-maintenance capability adapter describes whether the Care helper and `pkexec` execution path are locally present. It does **not** mean authorization has been granted; administrator authorization still belongs to PolicyKit at user action time.

## Current acceptance boundary

The V1.5 source resolver and unit tests are migration evidence only. They do not yet prove:

- V1.5 is wired to every Care GTK surface;
- rendered/native behavior on representative Zorin OS;
- accessibility acceptance of V1.5 contextual/capability presentation;
- current Stable Glaze consumer acceptance;
- Privacy Shield, Wardveil Security, or Everkeep acceptance for the dev3 identity;
- production readiness, release approval, deployment, or Stable promotion.

Care's `goreecloud.platform.yaml` therefore keeps the implemented Glaze version at `1.4.1`, marks Glaze as `applicable-migration-required`, and changes the required current target to `1.5.0`.

## Next bounded migration slice

Wire the V1.5 resolver into the Care GTK surfaces without replacing application/security authority. At minimum:

1. retain V1.4.1 optical styling as the visual baseline;
2. expose explicit V1.5 context/capability classes and explanations in the main maintenance and Insights surfaces;
3. disable privileged maintenance presentation when the local helper/PolicyKit execution path is unavailable while never treating availability as authorization;
4. preserve stable primary-action ordering and user confirmation boundaries;
5. verify HighContrast, reduced-motion, reduced-transparency, keyboard/focus, enlarged-text, and unavailable/degraded states;
6. run representative Zorin OS rendered/native acceptance on the exact candidate;
7. obtain fresh application-specific Glaze V1.5 acceptance before changing the manifest from `applicable-migration-required`.

No broader lifecycle or platform-system promotion is implied by completing this source foundation.
