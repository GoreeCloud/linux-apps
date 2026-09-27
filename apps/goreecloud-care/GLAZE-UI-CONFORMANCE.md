# GoreeCloud Care — GLAZE UI Conformance

## Current authority

- Care candidate: `0.2.0-dev3`
- Care lifecycle: **Development**
- Current required Stable Glaze target: **GLAZE UI V1.5 / `1.5.0`**
- Retained active optical implementation: **GLAZE UI `1.4.1`**
- Glaze Platform-System result: **applicable-migration-required**
- Care V1.5 consumer acceptance: **not established**
- Overall Care conformance: **nonconformant**

Current Glaze authority requires fresh repository-local migration and acceptance for every applicable consumer. Prior V1.4.1 evidence is retained as implementation and rollback provenance but does not establish V1.5 conformance.

## Verified upstream references

- GLAZE UI V1.5 Stable version: `1.5.0`
- V1.5 reviewed implementation anchor: `ee1032a0822ab8e103f8afe48e5c1859fde65cc9`
- V1.5 Stable integration provenance: `b7fa8164bfdeaa1dc0acb21b770e7601120da04e`
- Immediate rollback/optical baseline: `1.4.1`
- Authoritative central Platform Contract 0.2 Glaze-1.5 alignment: `398098d9391ac0369a79f228ca6b94d3c425fe39`

## Current Care evidence

### Retained V1.4.1 optical implementation

Care has substantive GTK3 V1.4.1 optical work in:

- `goreecloud_care/glaze_v14.py`
- `goreecloud_care/glaze_v14_global.py`
- `goreecloud_care/glaze_v14_optical.py`
- `tests/test_glaze_v14_contract.py`
- `GLAZE-UI-V1.4-MIGRATION.md`

That work remains the inherited visual/optical baseline and historical evidence. It is not current V1.5 acceptance.

### Bounded V1.5 source foundation

The current migration line now also contains:

- `goreecloud_care/glaze_v15.py`
- `tests/test_glaze_v15_contract.py`
- `GLAZE-UI-V1.5-MIGRATION.md`

The resolver is presentation-only. It consumes explicit capability/context facts, preserves provider/provenance information, fails closed on conflicting capability facts, exposes unavailable/degraded explanations, makes accessibility-precedence presentation explicit, and forbids automatic execution or fallback. Its privileged-maintenance adapter reports only whether the local Care helper and `pkexec` execution path are present; it does not grant PolicyKit authorization.

## Conformance status

Care is **not V1.5 conformant**. The active GTK entrypoint is still V1.4.1-based and the new V1.5 resolver is not yet wired across the main Care and Maintenance Insights surfaces. No application-specific rendered/native V1.5 acceptance has been completed for the current exact source identity.

The manifest must therefore continue to report:

- implemented Glaze version: `1.4.1`;
- required target: `1.5.0`;
- result: `applicable-migration-required`;
- overall conformance: `nonconformant`.

## Required before Care may claim V1.5 consumer acceptance

Care must still provide current exact-candidate evidence for all applicable V1.5 obligations, including:

1. wiring of Context + Capability Awareness to the real GTK surfaces while preserving V1.4.1 optical behavior;
2. authoritative-provider/fail-closed capability presentation without invented authorization;
3. explicit unavailable/degraded explanations and user-initiated recovery/fallback behavior;
4. no automatic permission, consequential action, maintenance execution, or navigation caused by presentation state;
5. accessibility precedence, HighContrast behavior, reduced motion/transparency, focus/keyboard, target sizing, and enlarged-text behavior;
6. representative rendered/native Zorin OS qualification for the exact candidate;
7. stable primary-action ordering and preserved confirmation/PolicyKit boundaries;
8. privacy-safe diagnostics and no telemetry requirement for ordinary presentation resolution;
9. exact-source application-specific Glaze acceptance evidence.

Even successful Glaze acceptance would not by itself establish Care production eligibility or Stable promotion. Privacy Shield, Wardveil Security, Everkeep, package lifecycle, representative-target, release, and other applicable Care gates remain independent.

## Historical evidence rule

Stable Care `0.1.0`, V1.2/V1.3/V1.4/V1.4.1 evidence, and earlier dev candidate runs remain audit and rollback context only. They must not be rebound to the current V1.5 migration identity.
