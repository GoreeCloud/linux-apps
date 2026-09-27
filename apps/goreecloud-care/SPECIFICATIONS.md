# GoreeCloud Care — Release Candidate Specification

**Lifecycle:** Release Candidate / nonconformant  
**Current source line:** `0.1.0-dev22`  
**Package line:** `0.1.0~dev22`  
**Canonical source:** `GoreeCloud/goreecloud-zorin-os/apps/goreecloud-care/`  
**Representative target:** Zorin OS 17.3  
**Official Stable design baseline:** GLAZE UI V1.2 / `1.2.0`  
**Forward design preview:** GLAZE UI V1.3 Adaptive Resonance (Proposed; consumer eligibility inactive)

## Purpose

GoreeCloud Care is a native, local-first desktop maintenance application for a person maintaining their own GoreeCloud/Zorin OS workstation. The first release scope is deliberately bounded: preview maintenance candidates, perform explicit user-authorized cleanup, provide local system/storage visibility, expose privacy-safe read-only reporting and offer read-only Maintenance Insights without introducing remote management, telemetry or unattended deletion.

The current source is a **Release Candidate source**, not an RC-complete or Stable release. Exact candidate package, representative-target and governed platform evidence must still be refreshed for the final frozen RC SHA.

## Safety model

- Preview first; scanning alone never deletes files.
- User cache, thumbnail cache and stale temporary-file cleanup run as the logged-in user.
- Trash is a separate irreversible action with an explicit confirmation.
- Privilege is limited to the fixed `apt-clean` and `reclaim-memory` helper actions.
- Privileged helpers accept no arbitrary paths, shell fragments or free-form commands.
- Symlinks are not followed during user-file scanning/deletion.
- Generic stale cache/temp eligibility uses a seven-day threshold.
- Cleanup operates on eligible leaf candidates rather than recursively deleting broad cache/temp roots.
- Errors are surfaced; failed items are not counted as success.
- New cleanup categories begin read-only until deletion semantics, ownership, recovery and privilege boundaries are separately specified and accepted.
- Scheduled behavior may scan or remind; unattended automatic deletion is excluded.
- Cancellation, PolicyKit denial, helper failure and partial failure are never represented as success.

## Interface, accessibility and Glaze UI

The official shared Stable compatibility baseline is **GLAZE UI V1.2 / `1.2.0`**. The RC source retains bounded forward-looking styling from Proposed **GLAZE UI V1.3 Adaptive Resonance**. This is not a claim that V1.3 Candidate is active, Care is an eligible V1.3 consumer, `accepted-v1` is granted, or the application is production Glaze-conformant.

Current native GTK3 behavior includes:

- neutral material surfaces with semantic/accent color separated from substrate color;
- compact/medium/expanded layout behavior that reorganizes content rather than merely scaling it;
- 48-pixel minimum target intent in the Glaze mappings;
- `GDK_DPI_SCALE`-aware effective-width handling for representative enlarged text;
- Light, Dark, preview Deep Dark and HighContrast support where claimed;
- system-authoritative HighContrast plus a focus-resilience provider;
- Reduced Transparency, Reduced Motion and Show Borders behavior;
- separate expression and clarity preview dimensions;
- explicit GLib/GTK application identity before GUI startup;
- ATK status-bar semantics and dynamic accessible status-name changes;
- keyboard-focus visibility and forward/reverse traversal requirements;
- selectable Maintenance Insights findings using Pango `WORD_CHAR` wrapping with synthetic hyphen insertion disabled.

Automated GTK/AT-SPI evidence does not manufacture final Orca speech quality, physical compositor/window-control rendering, canonical icon optical quality or desktop PolicyKit-agent experience. Those remain representative human/physical boundaries where applicable.

## Core maintenance contract

Current maintenance functions are:

- application-cache cleanup for eligible stale files;
- thumbnail-cache cleanup;
- eligible user-owned `/tmp` cleanup;
- Trash preview plus separately confirmed permanent emptying;
- APT package-cache preview plus PolicyKit-authorized cleanup;
- disk, available-memory and Linux file-cache status;
- separately warned and PolicyKit-authorized Linux file-cache reclaim.

Post-action refresh must preserve the final operation result. No-selection, stale-preview, cancellation, denial, failure and partial-success states must remain explicit.

## Read-only report contract

- `goreecloud-care --report` returns a human-readable local maintenance report.
- `goreecloud-care --report-json` returns schema-versioned JSON.
- `goreecloud-care --version` returns installed application version.
- Reports may read local filesystem metadata, disk usage and `/proc/meminfo` used by normal scanning.
- Reports must not delete files, authenticate, request PolicyKit, invoke the helper, use telemetry or access the network.
- Candidate file paths, local filenames and raw scan-error strings are omitted by default.
- Disk-headroom classification is informational only and is not filesystem-health certification or an automatic cleanup trigger.

## Maintenance Insights contract

`goreecloud-care --insights-ui` opens a dedicated local read-only review surface.

The current review scope includes:

- stale application-cache groups using the established >7-day policy;
- regular user-owned files of at least 250 MB in standard user folders;
- regular user-owned Downloads at least 30 days old;
- aggregate scan errors;
- bounded-discovery state.

Discovery does not follow symlinks and is capped at 50,000 visited standard-folder entries per refresh. Home-relative paths may appear only in this explicitly opened local review. Findings are informational and are never automatically selected for deletion, movement, quarantine, package action or privilege escalation. The Insights engine/window contains no deletion, PolicyKit, privileged-helper, subprocess or network execution path.

## Local platform integration API

The RC source exposes read-only local endpoints:

- `--api-version` → local API version `1`;
- `--health-json` → minimized local readiness/version status;
- `--privacy-status-json` → Privacy Shield-shaped status;
- `--security-status-json` → Wardveil-compatible status for the installed Care privilege boundary;
- `--continuity-status-json` → evidence-derived Everkeep continuity status.

Status modes remain GUI-lazy and must not delete files, authenticate, invoke privileged maintenance, send telemetry or access the network.

### Privacy Shield boundary

Repository-local declarations are `contracts/privacy-shield.application.json` and `contracts/privacy-shield.adapter.json`. Care declares only `telemetry-minimization`, `data-minimization` and `privacy-status`. Status output excludes raw private activity, credentials and identifiers.

The predecessor Development candidate has historical exact runtime evidence. That evidence does not transfer to the final RC SHA/package. Fresh exact-candidate runtime/application acceptance is required. Production approval is a separate Stable/production gate.

### Wardveil Security boundary

`WARDVEIL-INTEGRATION.md` defines the scoped producer model. Care is authoritative only for Care-owned installation/control facts such as the fixed helper and PolicyKit policy. Passing local evidence requires trusted fixed-file ownership/write boundaries and executable `pkexec`; evidence fails closed otherwise.

`protected_by_wardveil=false` remains authoritative until Wardveil explicitly accepts/promotes the exact RC candidate. A compatible status shape does not grant broad Wardveil protection or cross-service execution authority.

### Everkeep / continuity boundary

Care produces continuity evidence; Everkeep owns continuity governance.

The trust chain is:

1. `/usr/share/goreecloud-care/build-provenance.json`
   - root-controlled package-owned provenance;
   - exact repository revision and Care tree;
   - runtime/package versions;
   - deterministic source timestamp.

2. `/var/lib/goreecloud-care/acceptance/representative-target.json`
   - Care-owned representative Zorin OS 17.3 target handoff;
   - exact package SHA-256 captured externally;
   - exact source/tree/runtime/package binding;
   - source validation/local-test/package-lifecycle evidence;
   - Everkeep promotion booleans false by construction.

3. `/var/lib/goreecloud/everkeep/acceptance/goreecloud-care.target-runtime.json`
   - separate Everkeep-owned governance record;
   - must exact-match source/tree/runtime/package/target;
   - must use the same package SHA-256 as the Care target handoff;
   - must explicitly promote both integration and readiness.

Fail-closed states are:

- untrusted/missing provenance → `attention / provenance-unavailable`;
- no matching representative target → `attention / target-acceptance-required`;
- matching Care handoff without matching promoted Everkeep governance → `attention / target-accepted-governance-pending`;
- complete exact promoted chain → `ready / everkeep-promoted` with `freshness=exact-build-bound`.

Symlinked, malformed, oversized, writable, source-mismatched, target-mismatched, package-mismatched or unpromoted evidence cannot produce `ready`.

The predecessor Development candidate reached governed Everkeep readiness, but that exact evidence does not transfer to the RC source.

### Manager, Mesh and Identity applicability

For the intended first Stable scope, Care remains a local single-user utility and does not require central administration, cross-application coordination, accounts, multi-user behavior or delegated authorization. Manager, Mesh and Identity may remain `not-applicable-justified` only while that scope remains true. Any future remote, coordinated, account-based or delegated behavior reopens applicability.

## Packaging and exact provenance

The Release Candidate Debian package remains architecture `all` and retains pre-release version `0.1.0~dev22`.

Packaging requirements:

- authoritative Git checkout required;
- tracked Care changes must be committed/stashed;
- every file that can enter the package must be tracked;
- source revision and Care tree SHA are embedded in package provenance;
- `SOURCE_DATE_EPOCH` defaults to exact `HEAD` commit time when not supplied;
- locale/timezone are deterministic (`C`, UTC);
- staged modes and timestamps are normalized;
- Debian format 2.0 with `-Znone` removes compressor-version variability;
- rebuilds must compare byte-for-byte equal;
- Ubuntu 22.04 and Ubuntu 24.04 CI builds must compare byte-for-byte equal;
- package removal must remove package-owned provenance and the fixed application/helper/policy/desktop/icon/AppStream/private-runtime files it owns.

The package installs canonical RC runtime identity at:

- `/usr/share/applications/com.goreecloud.care.desktop`;
- `/usr/share/metainfo/com.goreecloud.care.metainfo.xml`;
- GTK application IDs `com.goreecloud.care` and `com.goreecloud.care.insights`.

## Representative target acceptance

`scripts/prepare-representative-acceptance.sh` prepares read-only evidence and human checklists for the exact RC source.

`scripts/run-representative-acceptance.sh` is the automated exact-target handoff runner. On Zorin OS 17.3 as the normal desktop user, it requires `lifecycle: release-candidate`, validates source, builds/verifies the reproducible package, builds the immutable dev17 rollback package, executes the complete install/remove/reinstall/downgrade/restore lifecycle, verifies final installed provenance, computes package SHA-256, installs only the Care-owned target handoff and proves that handoff cannot self-promote Everkeep.

Neither runner invokes a Care cleanup action. The automated runner does not write Everkeep governance.

## Branding authority

The canonical product icon is `GoreeCloud/goreecloud-branding-assets/products/care/app-icon.svg`. The package carries a synchronized derivative at `packaging/icons/com.goreecloud.care.svg` and installs it in the freedesktop hicolor application-icon path. The consumer copy is not the branding authority.

## Data and privacy

Care reads local filesystem metadata, `/proc/meminfo`, disk usage and fixed installation metadata. It sends nothing over the network and contains no telemetry. Default reports/status are minimized. Maintenance Insights may show home-relative paths only in the explicitly opened local review surface.

## Platform and toolkit

- Python 3.10+
- GTK 3 / PyGObject
- ATK / AT-SPI
- Pango
- PolicyKit / `pkexec` for the two fixed privileged maintenance actions
- Debian architecture `all`
- GLAZE UI V1.2 Stable compatibility baseline plus bounded Proposed V1.3 preview mapping

## Exclusions

- No unattended scheduled deletion.
- No browser-history, cookie, password or credential deletion.
- No process killer or one-click optimizer.
- No swap manipulation.
- No automatic package autoremove or old-kernel removal.
- No arbitrary kernel tuning or root shell execution.
- No claim that dropping file caches permanently improves RAM/performance.
- No unbounded whole-home/whole-filesystem Insights discovery.
- No GoreeCloud account, remote management or cross-application execution authority in the first-release scope.
- No claim of compositor-wide GTK3 backdrop-blur fidelity.
- No Stable/production Privacy Shield, Wardveil, Everkeep or Glaze claim before the exact candidate satisfies the governing acceptance.

## Release status

GoreeCloud Care is now a **Release Candidate source / nonconformant**. The source transition freezes the intended first-release behavior and canonicalizes Release Candidate application/package metadata, but it does not transfer predecessor acceptance to the new exact source.

RC completion still requires the final atomic source SHA to pass all exact-head CI, deterministic/cross-environment package checks and representative Zorin OS 17.3 lifecycle acceptance. Privacy Shield, Wardveil and Everkeep exact-candidate governance must then be refreshed against that same source/tree/package SHA.

Human-only review may remain explicitly pending at RC where the governing lifecycle permits it. Stable remains blocked until all applicable production-readiness, Platform System, final Glaze/product, security/privacy/recovery, human/physical and immutable-release evidence gates are satisfied. `RELEASE-ACCEPTANCE.md` is the authoritative component-local promotion checklist.
