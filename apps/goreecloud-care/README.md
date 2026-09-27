# GoreeCloud Care

**Lifecycle:** Stable  
**Version:** `0.1.0`  
**Released package:** `goreecloud-care_0.1.0_all.deb`  
**Immutable release source:** `bbc4779454c2887b810aa0ddc9e8a686a4c68ebd`  
**Released package SHA-256:** `819cff6e0132bf6b09df0986682995c25b14c39e74982f725efd0b5a21b71160`  
**Representative target:** Zorin OS 17.3  
**Canonical source:** `GoreeCloud/linux-apps/apps/goreecloud-care/`  
**License:** GPL-3.0-or-later

GoreeCloud Care is a local-first GTK3 desktop maintenance application for GoreeCloud/Zorin OS. It previews maintenance candidates before deletion, keeps routine cache/temp cleanup unprivileged, isolates privileged maintenance behind a fixed PolicyKit helper, provides privacy-safe read-only reports and Maintenance Insights, and exposes narrow local status interfaces for governed platform integration.

## Stable release boundary

Stable `0.1.0` promotes the already-qualified artifact built from exact source `bbc4779454c2887b810aa0ddc9e8a686a4c68ebd`. The Stable governance revision does **not** create or supersede that Debian artifact. Any later rebuild or source change is a new artifact/candidate and must receive the validation applicable to that change.

Exact release qualification passed:

- 143 unit/contract tests plus XML/source/platform validation;
- headless GTK runtime and safe task-flow acceptance;
- live core and Maintenance Insights AT-SPI acceptance;
- Dark/Deep Dark HeaderBar contrast, enlarged-text adaptation, clarity profiles, and Reduced Motion checks;
- deterministic same-environment package rebuilds;
- umask `0022` / `0002` byte identity;
- Ubuntu 22.04 / 24.04 byte identity;
- exact package-owned source provenance and launcher isolation;
- same-version install/upgrade, remove, fresh reinstall, accepted dev17 downgrade, exact `0.1.0` restore, and final installed-state validation on representative Zorin OS 17.3.

The representative package matched CI exactly at SHA-256 `819cff6e0132bf6b09df0986682995c25b14c39e74982f725efd0b5a21b71160`.

## Core features

- Scan stale application cache, thumbnail cache, and eligible user-owned temporary files.
- Preview candidates before cleanup; scanning never deletes by itself.
- Preview and permanently empty Trash only after a dedicated irreversible-action confirmation.
- Preview APT `.deb` cache and clean it through PolicyKit authorization.
- Show disk, available-memory, and Linux file-cache status.
- Reclaim Linux file cache only after a warning and PolicyKit authorization.
- Preserve explicit cancellation, denial, failure, partial-success, and completion states.
- Provide privacy-safe human/JSON reports and local health/platform status.
- Provide bounded read-only Maintenance Insights for stale cache groups, large files, and older Downloads.

## Safety and privilege model

Routine cache/temp cleanup runs as the logged-in user. Permanent Trash deletion is separate and explicitly confirmed. Only the fixed `apt-clean` and `reclaim-memory` privileged helper actions are allow-listed. The representative Stable acceptance verified confirmation cancellation, PolicyKit cancellation, privileged success for both actions, and invalid helper-action rejection with exit status `64`.

Installed application/helper launchers are isolated from working-directory, `PYTHONPATH`, user-site, and same-named-package shadowing. Package-owned provenance and fixed helper/policy files are validated against root-ownership/write boundaries.

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
goreecloud-care --insights-ui
```

Report/status modes do not delete files, authenticate, invoke privileged maintenance, send telemetry, or access the network. Default reports omit candidate paths, filenames, and raw scan-error strings.

## Platform governance

### Privacy Shield

Exact `0.1.0` Care-adapter runtime/production acceptance is governed by Privacy Shield revision `0af47f4817191541e1ea12928cff5c3458baf377`. The accepted scope is limited to `telemetry-minimization`, `data-minimization`, and `privacy-status`. Care remains local-first and does not export raw private activity for status.

### Wardveil Security

Exact `0.1.0` Wardveil adoption is governed by revision `e5c078a346a844c3a2a13e8eaa7fb98ba5fffa0f`. External protection-claim permission is narrowly limited to **GoreeCloud Care local-maintenance-privilege-boundary only**. Care does not grant Wardveil cross-service execution authority and its local status remains an evidence producer rather than a self-governance mechanism.

### Everkeep

Exact `0.1.0` continuity readiness is governed by Everkeep revision `4586246aad87a4038c7f8984de809d32333f2599`. On the representative target, the governed record is installed under the root-owned non-writable trust path and Care reports:

```text
ready / everkeep-promoted
```

The evidence remains exact-build-bound; mismatched, missing, malformed, writable, symlinked, or unpromoted evidence fails closed.

### Glaze UI

The current Stable compatibility baseline for this release is **GLAZE UI V1.2 / `1.2.0`**. Exact Care `0.1.0` is `accepted-v1` through Glaze authority `c3b077cd454825cd5a74cf21ba9e5dd4c25f94ae`.

That exact-source bridge preserves the predecessor seven-dimensional human/native acceptance because the RC-to-0.1.0 delta did not change Care's governed Glaze implementation, canonical icon, UI/focus/accessibility contract files, or runtime UI acceptance harness. It does not fabricate a second human review. Forward-looking Adaptive Resonance code remains non-authoritative for this Stable V1.2 consumer acceptance.

## Accessibility and adaptive behavior

The released implementation includes visible keyboard focus, forward/reverse traversal requirements, ATK/AT-SPI identity and dynamic status semantics, enlarged-text adaptation, HighContrast/system-authority handling, Reduced Transparency, Reduced Motion, Show Borders, compact/medium/expanded layouts, Dark/Deep Dark handling, and selectable Maintenance Insights findings.

The predecessor seven-dimensional human/native review covered final Orca spoken quality, compositor/window-control rendering, physical Dark/Deep Dark quality, canonical icon rendering, and confirmation/failure/task UX. The exact-source Glaze bridge transfers that acceptance only across unchanged governed presentation behavior.

## Recovery and rollback

The release retains the accepted `0.1.0~dev17` rollback checkpoint. Representative acceptance proved exact `0.1.0` install, removal, reinstall, explicit downgrade, rollback functionality, and restoration to the released package.

Care persists no substantial application-owned user dataset. Recovery therefore centers on package/source provenance, install/rollback reconstruction, explicit irreversible-maintenance boundaries, and Everkeep-governed exact recovery evidence.

## Release evidence

- Exact release source: `bbc4779454c2887b810aa0ddc9e8a686a4c68ebd`
- Care source tree: `ebe028347c978b6d09fb1d2af011729249f63bc3`
- Release qualification run: `34180765807` / #421
- Platform Contract run: `34180766156` / #416
- Theme validation: `34180765817` / #590
- Package artifact: `10038827656`
- Cross-environment artifact: `10038821545`
- Released package SHA-256: `819cff6e0132bf6b09df0986682995c25b14c39e74982f725efd0b5a21b71160`

See `RELEASE-ACCEPTANCE.md`, `RECOVERY.md`, `SECURITY.md`, `PRIVACY.md`, `WARDVEIL-INTEGRATION.md`, and `GLAZE-UI-CONFORMANCE.md` for the governed boundaries.
