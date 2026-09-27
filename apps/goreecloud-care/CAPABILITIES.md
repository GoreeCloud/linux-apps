# GoreeCloud Care Capabilities

## Implemented Development capabilities

### Safe local maintenance
- Preview-first scanning for stale application cache, thumbnail cache, user-owned stale temporary files, Trash, and APT package archives.
- Unprivileged cleanup for routine user-owned cache/temp categories.
- Separate destructive confirmation for permanent Trash emptying.
- Fixed PolicyKit-authorized actions for APT archive cleanup and Linux file-cache reclaim.
- Symlink-safe deletion boundaries and ownership checks.

### Maintenance intelligence
- Disk free/total visibility.
- Available-memory and Linux file-cache visibility.
- Aggregate reclaimable-space and item counts by maintenance category.
- Conservative disk-headroom classification: `comfortable`, `watch`, `low`, `critical`, or `unknown`.
- Scan-error counts without exposing raw local error strings in generated reports.

### Privacy-safe reporting — dev13
- `goreecloud-care --report` produces a human-readable, read-only maintenance snapshot.
- `goreecloud-care --report-json` produces stable machine-readable JSON for local tooling and future GoreeCloud integrations.
- Reports omit candidate file paths, local filenames, and raw scan-error strings by default.
- Reports do not authenticate, delete files, invoke PolicyKit, use telemetry, or access the network.
- `goreecloud-care --version` exposes the installed Development version for support and package verification.
- Representative-device dev13 build/install/report execution is accepted at exact runtime/source head `48049b6f634a05300e01bb0e85d718284b79d7ee`.

### Maintenance Insights review — dev14
- `goreecloud-care --insights-ui` opens a dedicated GTK read-only review surface; the desktop entry also exposes **Maintenance Insights (Read-only)** as a desktop action.
- Per-application stale-cache breakdown groups >7-day application-cache candidates by top-level cache namespace and excludes thumbnails.
- Large-file discovery identifies files of at least 250 MB in the standard local user folders `Downloads`, `Desktop`, `Documents`, `Pictures`, `Videos`, and `Music`.
- Stale Downloads review identifies files at least 30 days old without selecting or deleting them.
- User-folder discovery never follows symlinks and is bounded to 50,000 visited entries per refresh.
- Results show home-relative paths only inside the explicitly opened local Insights window; the default report modes remain path-redacted.
- The Insights engine/window has no deletion, PolicyKit, privileged-helper, or network execution path.
- Scan status is exposed as an ATK status-bar role and result text is read-only.
- Dev14 source/package implementation does **not** establish representative-device UI/accessibility acceptance until target validation is completed.

### Accessibility and resilience
- Keyboard-only forward and reverse traversal for the accepted core Care control path.
- Theme-resilient focus treatment under system HighContrast.
- Compact-window and 200%-text adaptive composition.
- AT-SPI product identity, roles, names, descriptions, checked state, and focused state for the current representative semantic slice.
- Persistent accessible maintenance status surface.

### Privacy and security
- Local-only operation.
- Zero telemetry and no advertising.
- No GoreeCloud account requirement.
- Privileged helper accepts only allowlisted action names, not arbitrary paths or shell commands.
- Routine cleanup never requires root.

## Planned capability expansion

The following are planned directions, not current implementation or release claims.

### Storage intelligence
- Duplicate-file discovery using conservative hashing and manual review before deletion.
- Optional user-controlled scope expansion beyond the current standard-folder Maintenance Insights set.
- Storage-pressure trends and capacity forecasting from local historical snapshots when a governed persistence design is approved.
- Filesystem/mount-aware exclusion and removable/network-volume controls for broader future discovery scopes.

### Application and package maintenance
- Flatpak and Snap cache/inventory visibility where installed.
- Package-manager health checks, stale package-archive insights, and upgrade-state visibility.
- Old-kernel and orphan-package **review** workflows that never run removal automatically.
- Broken desktop-entry and stale launcher detection with repair guidance.

### System health
- SMART/NVMe health summaries through read-only platform tools where supported.
- Filesystem capacity and mount health visibility.
- Battery-health and charge-cycle summaries on supported laptops.
- Startup/service health insights with clear separation between informational findings and repair actions.
- Crash-log and application-failure summaries with privacy-safe redaction.

### Guided maintenance
- Conservative recommendations ranked by safety, reclaimable benefit, and privilege level.
- “Why this is suggested” explanations for every recommendation.
- Session-local maintenance history and before/after summaries.
- Quarantine/undo workflows where technically safe; permanent actions remain explicitly identified when undo is impossible.
- Scheduled **scan/reminder** workflows without unattended automatic deletion.

### Diagnostics and support
- User-approved redacted support bundles containing aggregate system and Care diagnostics without browsing history, credentials, or unrelated personal files.
- Exportable maintenance snapshots with schema versioning.
- Compare-before/after reports for troubleshooting and change verification.
- Optional local integration with GoreeCloud Manager, Metrics, and Notify after their applicable Platform Contract gates are satisfied.

### Accessibility
- Representative-device keyboard, HighContrast, constrained-window, and large-text acceptance for the new dev14 Maintenance Insights window.
- Verified dynamic AT-SPI status-event delivery.
- Orca announcement-quality acceptance for status changes, confirmations, errors, and completion.
- Continued HighContrast, large-text, keyboard-only, and constrained-window regression coverage as capabilities expand.

## Capability boundaries

GoreeCloud Care is not intended to become a generic “optimizer.” Planned and implemented features must preserve these boundaries:

- no automatic destructive cleanup by default;
- no browser-history, cookie, password, or credential deletion;
- no process-killer or RAM-booster claims;
- no arbitrary root shell execution;
- no package autoremove without explicit reviewed scope and governed acceptance;
- no remote maintenance or cloud account requirement unless separately specified, governed, and accepted;
- no telemetry requirement for core maintenance;
- no unbounded filesystem crawling disguised as a lightweight maintenance scan.
