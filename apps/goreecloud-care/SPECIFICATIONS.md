# GoreeCloud Care — Development Specification

## Purpose
Provide a native GoreeCloud maintenance interface for the user's Zorin OS laptop without turning ordinary cleanup into a privileged or opaque operation. GoreeCloud Care may expand into maintenance intelligence, diagnostics, storage visibility, and guided system-health workflows only when those capabilities preserve the existing preview-first, least-privilege, privacy-first safety model.

## Users
Primary user: a person maintaining their own GoreeCloud/Zorin OS workstation.

## Safety model
- Preview first; cleanup never starts merely because a scan ran.
- User cache, thumbnail cache, and stale temporary files run as the logged-in user.
- Trash is a dedicated destructive action with an explicit, last-moment confirmation.
- Privilege is limited to allowlisted helper actions; the current Development helper exposes only `apt-clean` and `reclaim-memory`.
- Privileged helpers accept no arbitrary paths, commands, shell fragments, or free-form arguments.
- Symlinks are never followed during user-file scanning or deletion.
- Stale generic cache and temporary files use a 7-day threshold.
- Cleanup candidates are individual leaf nodes; broad recursive deletion of cache/temp directories is not used.
- Errors are surfaced and failed items are not counted as successful deletion.
- New cleanup categories must begin as read-only discovery unless their deletion semantics, ownership boundaries, undo/recovery behavior, and privilege requirements are separately specified and accepted.
- Scheduled capability may scan or remind, but unattended automatic deletion is excluded from this Development direction.

## Interface, accessibility, and appearance
- GoreeCloud Care opens in a light appearance by default on the target Zorin OS laptop.
- The application-local light preference must not change the desktop-wide Zorin OS appearance setting.
- System HighContrast presentation takes precedence over the application color mapping.
- Effective HighContrast detection must honor both `Gtk.Settings:gtk-theme-name` and an explicit process-local `GTK_THEME` override.
- Keyboard focus must remain visibly perceivable in both ordinary and HighContrast presentation.
- A focus-resilience provider may set only focus-indicator properties and must derive its focus color from the active GTK theme rather than reintroducing Care palette colors into HighContrast.
- The ordinary Care application CSS remains higher priority than the fallback focus provider so accepted normal-mode focus styling is preserved.
- Status feedback must communicate changed state with text plus a recognizable symbol and semantic surface/border treatment; color alone is not sufficient.
- Maintenance status surfaces must expose assistive-technology semantics and update their accessible name when operation state changes.
- User-initiated cancellation is an attention/changed-state condition, not an error or destructive warning.
- Interactive controls must remain reachable by keyboard and expose useful accessible names/descriptions through the GTK/ATK mapping.
- Category counts must remain associated with understandable category text for visual and assistive-technology users.
- Long status, system, description, and heading text must wrap instead of clipping.
- The primary desktop window must support a compact composition below the Development breakpoint: category amounts move below category content and the bottom action row becomes a vertical action stack.
- For the GTK `GDK_DPI_SCALE` large-text acceptance path, compact selection must account for text scale when interpreting allocated width.
- The compact HeaderBar may omit the Development subtitle while retaining the application title and primary Scan action.
- The Development minimum supported size is 480 × 420 logical pixels for current Care GTK windows.
- Current Stable Glaze UI V1.1 / 1.1.0 remains the governing design target; Development mappings do not establish conformance until rendered, accessibility, resilience, and platform-native evidence is accepted.

## Dev13 reporting contract
- `goreecloud-care --report` provides a human-readable read-only local maintenance report.
- `goreecloud-care --report-json` provides schema-versioned JSON suitable for local scripts and future governed GoreeCloud integration.
- `goreecloud-care --version` provides the installed Development version.
- Report generation may read the same local filesystem metadata, disk usage, and `/proc/meminfo` used by the normal Care scan.
- Report generation must not delete files, request PolicyKit authorization, invoke the privileged helper, or access the network.
- Reports must omit candidate file paths, local filenames, and raw scan-error strings by default.
- Reports may expose aggregate and per-category byte/item counts, scan-error counts, disk headroom, memory availability, file-cache estimates, report schema/version metadata, and explicit privacy/mode declarations.
- Disk-headroom classification is informational only and must not be represented as filesystem-health certification, failure prediction, or an automatic cleanup trigger.
- Exact runtime/source head `48049b6f634a05300e01bb0e85d718284b79d7ee` is representative-device accepted for this reporting slice: 38 local tests plus XML/source validation passed, `0.1.0~dev13` built and installed over dev12, and `--version`, `--report`, and `--report-json` all executed successfully.

## Dev14 Maintenance Insights contract
- `goreecloud-care --insights-ui` opens a dedicated local GTK read-only review surface. The desktop entry exposes the same capability as **Maintenance Insights (Read-only)**.
- The Insights engine may group stale application-cache candidates by top-level cache namespace using the established >7-day application-cache policy; thumbnail cache remains excluded from this grouping.
- Large-file discovery is currently limited to regular user-owned files of at least 250 MB under the standard folders `Downloads`, `Desktop`, `Documents`, `Pictures`, `Videos`, and `Music`.
- Stale Downloads review is currently limited to regular user-owned files at least 30 days old.
- User-folder discovery must not follow symlinks and must remain lexically within each configured standard root.
- Each refresh is bounded to at most 50,000 visited standard-folder entries. If the limit is reached, the interface must identify the result as partial rather than exhaustive.
- The interactive Insights view may show home-relative file paths because the user explicitly opened a local file-review surface. Default `--report` and `--report-json` output remains path-redacted.
- Insights findings are informational only. No finding is automatically selected for deletion, cleanup, movement, quarantine, package action, or privileged operation.
- The Insights engine/window must not contain a deletion, PolicyKit, privileged-helper, subprocess, or network execution path.
- The GTK results view is non-editable, vertically scrollable, and exposes a useful accessible name/description. Scan state is represented through an ATK status-bar role and accessible-name mutation.
- Dev14 source implementation does not establish rendered, keyboard, HighContrast, large-text, constrained-window, or assistive-technology acceptance until representative-device evidence is completed.

## Data and privacy
The application reads local filesystem metadata, `/proc/meminfo`, and disk usage. It sends nothing over the network and contains no telemetry. Default report outputs are path-redacted and omit raw scan-error text. The explicitly opened dev14 Insights window may show home-relative paths only for findings inside its governed standard-folder scope. Future diagnostic bundles that expose additional local details require explicit user approval, redaction rules, and separate governance.

## Platform and toolkit
Python 3 + GTK 3/PyGObject, selected to match the verified Zorin OS 17.3 GTK 3 environment. ATK semantics are exposed through GTK accessibility objects. PolicyKit is used only for privileged maintenance. The dev13 reporting and dev14 Insights engines are implemented in Python over the existing maintenance foundations and add no new external runtime dependency.

## Planned capability classes
Planned directions are not current implementation or release claims. See `CAPABILITIES.md` for the detailed roadmap. Remaining approved directions include duplicate discovery with manual review, optional user-controlled discovery scope, Flatpak/Snap/package visibility, SMART/NVMe/filesystem/battery/startup/crash insights, local maintenance history, safe quarantine/undo where feasible, privacy-redacted support exports, scheduled scan/reminders, and governed Manager/Metrics/Notify integration.

## Exclusions in this Development direction
- No automatic scheduled deletion.
- No browser-history, cookie, password, or credential deletion.
- No process killer or “one-click optimizer.”
- No swap manipulation.
- No automatic package autoremove or old-kernel removal.
- No registry-style tuning, CPU overclocking, or kernel-parameter tuning.
- No claim that dropping file caches permanently boosts RAM or performance.
- No arbitrary root shell execution.
- No unbounded whole-home or whole-filesystem discovery under the Maintenance Insights feature.
- No GoreeCloud cloud account requirement or remote management unless separately specified and governed in a future scope.

## Release status
Development / nonconformant. Core maintenance execution is representative-device verified through dev5; dev8 closes the combined `GDK_DPI_SCALE=2` + compact adaptive-layout blocker; dev10 closes the representative HighContrast focus/traversal slice. Dev12 exact runtime head `09c3a6bcbec094dd3cb0c828de88d084fcbd5a22` accepts the `GoreeCloud Care` AT-SPI application-root identity plus the current static roles/names/descriptions/checked/focused-state semantic slice. Dynamic AT-SPI event delivery and Orca announcement quality remain open.

Dev13 exact runtime/source head `48049b6f634a05300e01bb0e85d718284b79d7ee` is accepted for package build/install and read-only report execution on the representative laptop. Dev14 adds the bounded Maintenance Insights engine and GTK review surface, but that new slice remains source/package-only until exact-head repository validation and representative-device build/install/UI/accessibility testing are accepted. Supported appearance decisions, official branding, package rollback, final current-Stable Glaze UI V1.1 consumer acceptance, and remaining Integral Platform System evidence remain open.
