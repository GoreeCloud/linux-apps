# Features

## Implemented in Development source

### Maintenance execution
- User application-cache scan/cleanup for files older than 7 days.
- Thumbnail-cache scan/cleanup.
- User-owned stale `/tmp` scan/cleanup for files older than 7 days.
- Trash scan plus separately confirmed permanent emptying.
- APT archive-cache preview and PolicyKit-authorized `apt-get clean`.
- Disk, available-memory, and Linux file-cache status.
- PolicyKit-authorized Linux page/dentry/inode cache reclaim with a truthful warning.
- Explicit cancellation, failure, partial-success, and completion reporting.
- Post-action refresh that preserves the final action result.
- Conservative symlink handling, ownership checks, and a fixed privileged-action allowlist.

### Interface and accessibility
- Persistent semantic status presentation with non-color-only state communication.
- Visible keyboard-focus treatment and fail-safe Cancel-first confirmation dialogs.
- Light application appearance by default without changing the desktop-wide Zorin OS appearance.
- Adaptive compact-window composition for constrained desktop widths.
- Normal-text compact transition at 820 logical pixels.
- Effective-width adaptation for the `GDK_DPI_SCALE` 200%-text acceptance path.
- Compact HeaderBar reduction that omits the Development subtitle while preserving the application title and Scan action.
- GTK/ATK status, control-description, selector-description, and category-count accessibility semantics.
- Explicit GLib program/application identity so AT-SPI discovers `GoreeCloud Care` instead of Python's `__main__.py` basename.
- Effective HighContrast detection that honors both `Gtk.Settings` theme state and process-local `GTK_THEME` overrides.
- Theme-derived focus-resilience provider that keeps HighContrast authoritative while preserving visible keyboard focus.

### Privacy-safe maintenance reporting — dev13
- `goreecloud-care --report` for a human-readable read-only maintenance snapshot.
- `goreecloud-care --report-json` for machine-readable local integration and diagnostics.
- `goreecloud-care --version` for installed Development-version verification.
- Aggregate visible bytes/items across maintenance categories.
- Conservative disk-headroom classification: `comfortable`, `watch`, `low`, `critical`, or `unknown`.
- Per-category byte/item counts and scan-error counts.
- Report redaction that excludes candidate file paths, local filenames, and raw scan-error strings by default.
- Report modes never authenticate, delete files, invoke PolicyKit, use telemetry, or access the network.

### Maintenance Insights — dev14
- Dedicated GTK review surface launched with `goreecloud-care --insights-ui`.
- Desktop action named **Maintenance Insights (Read-only)**.
- Read-only breakdown of stale (>7-day) application cache grouped by top-level cache namespace, excluding thumbnail cache.
- Read-only discovery of files at least 250 MB in `Downloads`, `Desktop`, `Documents`, `Pictures`, `Videos`, and `Music`.
- Read-only review of Downloads at least 30 days old.
- Home-relative path presentation inside the explicitly opened local Insights view while default reports stay path-redacted.
- No symlink following in user-folder discovery.
- Bounded discovery capped at 50,000 visited entries per refresh, with partial-result disclosure when the limit is reached.
- Read-only GTK result surface, refresh action, ATK status-bar role, accessible result name/description, and visible-data change signaling.
- No deletion, PolicyKit, privileged helper, subprocess, or network path inside the Insights engine/window.

### Privacy and platform behavior
- Local-only operation and zero telemetry.
- No GoreeCloud account requirement.
- No browser-history or credential deletion.
- No package autoremove, process-killer, swap manipulation, or generic “optimizer” behavior.

## Representative-device verified
- Through dev5: Zorin OS 17.3 source validation, package build, upgrade/install, launch, keyboard focus visibility, first-stage and PolicyKit cancellation, successful PolicyKit-authorized Memory Refresh and APT cleanup, controlled nonzero Application cache / Thumbnail cache / Temporary files / Trash / APT archive deletion, completion reporting, and post-action values refresh.
- Dev6: normal-text compact/minimum-window adaptive composition, vertical reachability, full-width stacked bottom actions, category-amount reflow, and visible focus at the compact bottom control path.
- Dev8: combined 200%-text/compact acceptance at exact runtime head `45b5f11a49f363ebcaf753c892245a31109bc9bb`.
- Dev9: system HighContrast palette takeover accepted, but the first pass exposed a no-visible-Tab-response defect.
- Dev10: exact runtime head `3524a4a82da87ea51dcde08992a402190b54c130` accepted system HighContrast palette authority, visible focus, constrained-width composition, and complete requested forward/reverse keyboard traversal.
- Dev12: exact runtime head `09c3a6bcbec094dd3cb0c828de88d084fcbd5a22` accepted the `GoreeCloud Care` AT-SPI application root plus static roles, names, descriptions, checked state, and focused state for the current semantic slice.
- Dev13: exact runtime/source head `48049b6f634a05300e01bb0e85d718284b79d7ee` passed 38 tests plus XML/source validation on the representative laptop, built and installed `0.1.0~dev13`, returned `0.1.0-dev13` from `--version`, and successfully produced both human and JSON read-only reports. The observed run reported 74.7 GB free of 233.2 GB, 135.0 MB visible across 984 items, and zero scan errors. Treat the dev13 report-mode build/install/execution slice as accepted.

## Dev14 source status
- Maintenance Insights engine, bounded user-folder discovery, stale-cache grouping, large-file discovery, stale-Downloads review, GTK read-only review window, desktop action, tests, validation guards, documentation, package metadata, and CI package inspection are source-implemented.
- Dev14 representative-device package build/install, GTK launch, discovery-result correctness, keyboard/focus, HighContrast, constrained-window, large-text, and AT-SPI acceptance remain open.

## Planned capability expansion
- Duplicate-file discovery with conservative hashing and manual review before any removal.
- Optional user-controlled discovery scopes beyond the current standard folders.
- Flatpak/Snap cache and package inventory visibility where installed.
- Package-manager health, stale archive, old-kernel, and orphan-package review without automatic removal.
- SMART/NVMe, filesystem/mount, battery-health, startup/service, and crash-log insights where supported.
- Session-local maintenance history and before/after summaries.
- Quarantine/undo workflows where technically safe.
- Scheduled scan/reminder workflows without unattended deletion.
- Privacy-redacted support bundles and schema-versioned diagnostic exports.
- Optional governed integration with GoreeCloud Manager, Metrics, and Notify.

## Remaining before RC
- Dev14 representative build/install and Maintenance Insights target acceptance.
- Complete dynamic AT-SPI status-value/event verification and Orca announcement-quality acceptance.
- Additional supported appearance/resilience decisions and evidence, including dark/system appearance where applicable.
- Package uninstall/downgrade/rollback validation.
- Official GoreeCloud Care icon/branding from the canonical branding-assets source.
- GoreeCloud Care current-Stable Glaze UI V1.1 consumer acceptance with exact native evidence.
- Applicable Wardveil Security, Privacy Shield, Everkeep, Mesh, Manager, and Identity decisions/evidence.
