# GoreeCloud Care Changelog

## Release Candidate source transition — 2026-09-07

- Advanced the component lifecycle from Development to **Release Candidate / nonconformant** while retaining the established pre-release runtime/package version `0.1.0-dev22` / `0.1.0~dev22`.
- Based the transition directly on the fully hardened predecessor exact source `4f7aecd6fa5a6fdd6efb496e606c29457c18fefb`.
- Canonicalized the Release Candidate GTK/application identity to `com.goreecloud.care` and `com.goreecloud.care.insights` without changing maintenance behavior.
- Changed installed desktop/AppStream identities to the canonical runtime paths `com.goreecloud.care.desktop` and `com.goreecloud.care.metainfo.xml` while retaining the existing source packaging filenames during this bounded transition.
- Changed user-visible application/package metadata from Development to Release Candidate where lifecycle identity is presented.
- Preserved `0.1.0-dev22` / `0.1.0~dev22` as the pre-release version line; Release Candidate lifecycle is represented separately by the Platform Contract, application metadata, CI evidence and governed acceptance records.
- Reconciled `README.md`, `SPECIFICATIONS.md`, `RELEASE-ACCEPTANCE.md`, the Platform Contract, representative preparation/runner scripts and CI artifact provenance with the Release Candidate lifecycle.
- Added dedicated Release Candidate identity regression coverage so CI rejects reintroduction of `.dev` runtime application identity or a Development workflow/lifecycle label.
- Bound the representative Zorin OS 17.3 preparation and exact-target runner to `lifecycle: release-candidate`; the exact-target runner records `lifecycle=release-candidate` and still cannot write or promote Everkeep governance.
- Preserved deterministic Debian construction, caller-umask independence, same-environment rebuild verification, Ubuntu 22.04/24.04 byte-for-byte cross-environment verification, exact package-owned source provenance, isolated installed Python launchers, immutable dev17 rollback construction and full candidate package lifecycle testing.
- Preserved the fail-closed continuity chain: package-owned provenance → Care-owned representative-target evidence → separate Everkeep-owned governance. A Care handoff cannot self-promote.
- Preserved the Wardveil authority boundary: local Care security evidence remains scoped to the installed privileged-maintenance boundary and `protected_by_wardveil=false` remains authoritative until separate exact-RC Wardveil governance accepts otherwise.
- Preserved the Privacy Shield authority boundary: exact runtime/application acceptance must be refreshed for the final RC source/package and production approval remains a separate Stable/production gate.
- Preserved **GLAZE UI V1.2 / `1.2.0`** as the official Stable compatibility baseline. V1.3 Adaptive Resonance remains Proposed and consumer-ineligible; RC application lifecycle does not manufacture V1.3 Candidate/Stable status or final Glaze conformance.
- Predecessor representative-device, Privacy Shield, Wardveil and Everkeep evidence remains valuable historical evidence but is exact-source/tree/package scoped and does **not** transfer to the new Release Candidate source.
- Release Candidate completion still requires one frozen atomic source SHA with green exact-head CI, immutable package/checksum evidence, fresh representative Zorin OS 17.3 lifecycle acceptance and fresh exact-candidate Privacy Shield/Wardveil/Everkeep governance.
- Human-only acceptance such as final Orca spoken quality, physical Zorin native/compositor/window-control and canonical-icon optical review, and representative desktop PolicyKit-agent interaction quality may remain explicitly pending at RC only where the governing lifecycle permits it; Stable remains blocked until all applicable production-readiness gates are complete.
- No Stable, production approval, `Protected by Wardveil`, final Everkeep readiness for the new RC source, or V1.3 conformance claim is made by this transition.

## Immutable Development history

The detailed Development changelog for `0.1.0-dev1` through the fully hardened `0.1.0-dev22` predecessor is preserved at the exact source revision from which this Release Candidate transition was created:

- source revision: `4f7aecd6fa5a6fdd6efb496e606c29457c18fefb`
- file: `apps/goreecloud-care/CHANGELOG.md`
- canonical repository: `GoreeCloud/goreecloud-zorin-os`

That immutable predecessor record includes the complete dev1–dev22 sequence: initial maintenance foundations, safety and PolicyKit hardening, focus/HighContrast remediation, enlarged-text adaptation, AT-SPI identity/event work, read-only reporting, Maintenance Insights, package/launcher isolation, Glaze V1.2/V1.3 development mapping, Dark/Deep Dark contrast remediation, reproducible-package hardening, exact package provenance, representative lifecycle acceptance and governed continuity evidence.

Git history is the authoritative record for those historical entries. This RC changelog intentionally avoids rewriting historical Development statements as if they applied to the new exact source identity.
