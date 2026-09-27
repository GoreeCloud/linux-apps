# GoreeCloud Care

**Lifecycle:** Release Candidate source / nonconformant  
**Version:** `0.1.0-dev22`  
**Package:** `0.1.0~dev22`  
**Canonical source:** `GoreeCloud/goreecloud-zorin-os` → `apps/goreecloud-care/`  
**Representative target:** Zorin OS 17.3  
**Compatibility:** GTK 3 Linux desktops within the supported package/runtime boundary  
**License:** GPL-3.0-or-later

GoreeCloud Care is an original, local-first desktop maintenance application. It previews maintenance candidates before deletion, keeps routine cache/temp cleanup unprivileged, separates consequential and privileged actions, provides privacy-safe read-only reports, includes a bounded local Maintenance Insights review surface, and exposes narrow read-only platform-status interfaces for governed GoreeCloud integrations.

## Release Candidate boundary

This source line has entered the **Release Candidate lifecycle**, but it is intentionally still **nonconformant** and is not yet RC-complete, Stable, production-approved, Protected by Wardveil, or final Glaze-conformant.

The immediately preceding Development candidate `4f7aecd6fa5a6fdd6efb496e606c29457c18fefb` completed strong automated and representative-device qualification, including deterministic packaging, package lifecycle/rollback, trusted exact-source provenance, Privacy Shield runtime acceptance, Wardveil target evidence, and Everkeep integration/readiness promotion. Those records are exact-source/tree/package scoped and do **not** transfer to this Release Candidate source.

The Release Candidate intentionally keeps the pre-release runtime/package version `0.1.0-dev22` / `0.1.0~dev22`; lifecycle identity is carried separately by the Platform Contract, application metadata, package description, release records, and governed acceptance evidence. The exact RC package identity is therefore still bound by its new Git source revision, Care source-tree SHA, deterministic timestamp, and package SHA-256.

## Current release hardening

The RC source retains the dev22 maintenance implementation and hardening:

- Dark/Deep Dark HeaderBar contrast remediation and runtime contrast checks;
- enlarged-text GTK runtime acceptance;
- Clear/Balanced/Dense clarity-profile geometry checks;
- Reduced Motion application-owned behavior checks;
- live core Care and Maintenance Insights AT-SPI status/event delivery;
- safe task-flow automation for preview, selection, confirmation, cancellation and PolicyKit result mapping;
- deterministic Debian package construction using `SOURCE_DATE_EPOCH`, normalized staged modes/timestamps, Debian format 2.0 and `-Znone`;
- byte-for-byte Ubuntu 22.04 / Ubuntu 24.04 package comparison;
- exact package-owned build provenance;
- fail-closed rejection of dirty tracked source and untracked package inputs;
- installed Python application/helper isolation from working-directory, `PYTHONPATH`, user-site and same-named-package shadowing;
- full candidate install/remove/reinstall/dev17-downgrade/candidate-restore lifecycle prequalification;
- fail-closed Wardveil-compatible installed privilege-boundary evidence;
- evidence-derived Everkeep continuity that cannot self-promote.

## Core features

- Scan and clean stale application cache files.
- Clean the thumbnail cache.
- Scan and clean eligible user-owned temporary files.
- Preview Trash usage and empty Trash only after a separate permanent-deletion confirmation.
- Preview APT `.deb` cache and clean it through PolicyKit authorization.
- Display disk, available-memory and file-cache status.
- Reclaim Linux file caches only after a warning and PolicyKit authorization.
- Explicit cancellation, failure, partial-success and completion reporting.
- Post-action refresh that preserves the final action outcome.
- Privacy-safe human/JSON reports.
- Local health, Privacy Shield, Wardveil-compatible security and Everkeep continuity status output.
- Bounded, read-only Maintenance Insights for stale cache groups, large files and older Downloads.
- Canonical GoreeCloud Care branding and application identity.

## Safety model

Routine application-cache, thumbnail-cache and eligible user-owned temporary-file cleanup runs without administrator privileges. Permanent Trash deletion requires a separate irreversible-action confirmation. APT archive cleanup and Linux file-cache reclaim are isolated behind the fixed Care helper and PolicyKit.

Confirmation dialogs are fail-safe by default: Cancel is present, initially focused and the default response. PolicyKit cancellation, denial or failure is never represented as success. Installed application/helper launchers use isolated Python execution and package maintainer scripts touch only fixed Care-owned paths.

## Read-only reports and local API

```sh
goreecloud-care --version
goreecloud-care --report
goreecloud-care --report-json
goreecloud-care --api-version
goreecloud-care --health-json
goreecloud-care --privacy-status-json
goreecloud-care --security-status-json
goreecloud-care --continuity-status-json
```

Report/status modes do not delete files, authenticate, invoke the privileged helper or access the network. Default reports omit candidate paths, filenames and raw scan-error strings.

### Privacy Shield

Care declares only bounded local-first `telemetry-minimization`, `data-minimization` and `privacy-status` capabilities. `runtime_acceptance_required=true` remains authoritative. Production approval is a separate governed production/Stable gate. Predecessor acceptance does not transfer to the RC source.

### Wardveil Security

`--security-status-json` reports only the installed Care-owned privilege boundary. Passing local evidence requires the fixed helper/policy installation boundary plus `pkexec` availability. `protected_by_wardveil=false` remains authoritative until Wardveil accepts and promotes the exact RC candidate. Care does not give Wardveil execution authority over maintenance actions.

### Everkeep

Continuity uses three separate trust layers:

1. package-owned provenance at `/usr/share/goreecloud-care/build-provenance.json`;
2. Care-owned representative-target evidence at `/var/lib/goreecloud-care/acceptance/representative-target.json`;
3. Everkeep-owned governance at `/var/lib/goreecloud/everkeep/acceptance/goreecloud-care.target-runtime.json`.

The Care target handoff cannot self-promote. `ready / everkeep-promoted` requires a separate trusted Everkeep record matching exact source revision, Care tree, runtime/package version, representative target and package SHA-256. Missing, malformed, writable, symlinked, mismatched or unpromoted evidence fails closed.

## Maintenance Insights

```sh
goreecloud-care --insights-ui
```

Maintenance Insights is read-only. It reviews stale application-cache groups, regular files of at least 250 MB in standard user folders, Downloads at least 30 days old, aggregate scan errors and bounded-discovery state. Symlinks are not followed and discovery is capped. Nothing is automatically selected or deleted.

## Accessibility and Glaze UI

Automated acceptance covers GTK/ATK identity, dynamic AT-SPI status delivery, enlarged-text adaptation, keyboard/focus behavior, Dark/Deep Dark command contrast, clarity profiles and Reduced Motion application-owned behavior.

Final representative Orca spoken quality and physical target optical/compositor review remain human acceptance boundaries.

Official compatibility baseline:

```text
GLAZE UI V1.2 / 1.2.0 — Stable
```

Forward-looking implementation target:

```text
GLAZE UI V1.3 — Adaptive Resonance
upstream lifecycle: Proposed
consumer eligible: no
pinned development source: dc5ee04b09bd7d2c06d6ac1456618cbd4b1f4b80
```

V1.3 preview styling does not establish upstream Candidate status, accepted-v1, production eligibility or final Glaze conformance.

## Build and automated qualification

```sh
sh ./scripts/validate.sh
sh ./scripts/build-deb.sh
sh ./scripts/verify-reproducible-package.sh ./dist/goreecloud-care_0.1.0~dev22_all.deb
```

`build-deb.sh` requires the authoritative Git checkout, refuses tracked dirty Care source and refuses untracked files that could enter the package. It embeds exact source revision/tree provenance and builds reproducibly. CI independently builds on Ubuntu 22.04 and Ubuntu 24.04 and byte-compares the results.

The full automated package lifecycle is:

```sh
sh ./scripts/build-dev17-rollback-package.sh
sh ./scripts/validate-package-lifecycle.sh \
  ./dist/goreecloud-care_0.1.0~dev22_all.deb \
  ./dist/rollback/goreecloud-care_0.1.0~dev17_all.deb
```

No Care cleanup action is invoked by that lifecycle probe.

## Representative Zorin acceptance

Read-only preparation:

```sh
sh ./scripts/prepare-representative-acceptance.sh
```

Exact representative-target handoff:

```sh
sh ./scripts/run-representative-acceptance.sh
```

The runner must execute as the normal desktop user on Zorin OS 17.3. It validates source, builds and verifies the deterministic package, constructs the immutable dev17 rollback package, runs the complete package lifecycle, verifies final installed provenance, computes the exact package SHA-256 and installs only the root-controlled Care-owned target handoff. It does not invoke Care cleanup and does not write or promote Everkeep governance.

## Local installation

```sh
sudo apt install ./dist/goreecloud-care_0.1.0~dev22_all.deb
```

Uninstall:

```sh
sudo apt remove goreecloud-care
```

## Remaining RC-completion and Stable boundaries

The Release Candidate source still requires exact-head CI on the final frozen SHA plus a fresh representative Zorin OS 17.3 package lifecycle for that same SHA/package. Exact Privacy Shield, Wardveil and Everkeep records must then be refreshed for the RC identity; predecessor records cannot be copied forward.

Human-only acceptance that may remain explicitly pending at RC includes final Orca announcement quality, physical Zorin native/compositor/window-control and canonical-icon optical review, and representative desktop PolicyKit-agent interaction quality. Stable additionally requires all applicable current Platform System production acceptance, final production-readiness review, immutable release evidence and synchronized governed lifecycle records.

No downstream Care document, CI result or local status producer may bypass those authorities.
