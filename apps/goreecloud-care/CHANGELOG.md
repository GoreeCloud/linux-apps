# Changelog

## 0.1.0-dev17 — 2026-09-06
- Recorded the representative-device dev16 enlarged-text screenshots at exact runtime/source head `02b7df9eb7543e7147dd7e81212d465daa15086e` as positive evidence for three previously open visual checkpoints: the compact HeaderBar fully displays `Insights`, the symbolic Refresh control shows a clearly perceivable keyboard-focus outline, and the findings viewport reaches its true bottom.
- The dev16 true-bottom screenshot showed 24,238 inspected user-folder entries with 0 scan errors. This is representative-device evidence, not a fixed product guarantee.
- Kept continuous-resize responsiveness open because the submitted dev16 evidence did not report how resizing behaved; no performance pass is inferred from screenshots.
- Identified a new presentation defect in the dev16 `Gtk.WrapMode.CHAR` findings surface: Pango inserted synthetic hyphens at character breaks under `GDK_DPI_SCALE=2`, producing fragments such as `da-` / `ys` and `in-` / `spected`.
- Replaced the findings `Gtk.TextView` with a selectable Pango-backed `Gtk.Label` using `Pango.WrapMode.WORD_CHAR` and `insert_hyphens='false'`. Long path-like strings can still fall back to character wrapping, but synthetic line-break hyphens are disabled.
- The dev17 rendering path escapes dynamic findings before inserting Pango markup and does not add zero-width break characters, so displayed/copied paths are not intentionally mutated to obtain wrapping.
- Preserved the independent findings scroller, 320-pixel minimum findings viewport, accessible result name/description, compact HeaderBar behavior, read-only semantics, local-only boundary, path-display boundary, and no-automatic-deletion guarantees.
- Added source-contract coverage and validation guards for the selectable results surface, Pango wrapping mode, hyphen suppression, markup escaping, and absence of the prior `Gtk.WrapMode.CHAR` path.
- Advanced runtime, Python project metadata, Debian package metadata, AppStream metadata, README, Platform Contract, validation guards, and CI package inspection to `0.1.0-dev17` / `0.1.0~dev17`.
- Dev17 remains Development and target-unaccepted until exact-head repository validation plus representative-device enlarged-text rendering and continuous-resize testing are complete.

## 0.1.0-dev16 — 2026-09-06
- Recorded representative-device dev15 validation/build/install success at exact head `e36707264a62b4b66083c909b62b55041b909d12`: all 48 local tests plus XML/source validation passed, `goreecloud-care_0.1.0~dev15_all.deb` built, the package upgraded from dev14, and `dpkg-query` reported `install ok installed 0.1.0~dev15`.
- Classified the dev15 constrained `GDK_DPI_SCALE=2` visual gate as failed/open because the compact HeaderBar title still ellipsized to `Insig…` beside the full text Refresh button. True-bottom findings reachability and continuous-resize responsiveness were not demonstrated in that checkpoint and remained open rather than inferred.
- Replaced the text-heavy HeaderBar Refresh button with the `view-refresh-symbolic` control while preserving an explicit accessible `Refresh` name, accessible description, tooltip, keyboard focusability, and unchanged read-only refresh behavior.
- Removed the extra `large` text role from the compact introductory heading while retaining bold hierarchy, shortened compact privacy/status copy, and reduced compact vertical spacing.
- Preserved the whole-page scroller, 320-pixel findings viewport, effective-width compact contract, local-only/no-network/no-telemetry guarantees, and no automatic file changes.
- Added/strengthened source-contract coverage and validation guards for the compact symbolic Refresh control and retained large-text reachability invariants.
- Exact dev16 repository validation passed before representative-device testing: GoreeCloud Care Development run `34045639862`, GoreeCloud Care Platform Contract run `34045640367`, and Validate theme source run `34045639856` were green for exact head `02b7df9eb7543e7147dd7e81212d465daa15086e`.
- Subsequent representative-device dev16 screenshots verified the fully readable `Insights` title, visible Refresh keyboard focus, and true-bottom findings reachability. Continuous-resize responsiveness remained unreported, and the screenshots exposed synthetic mid-word hyphenation in the `CHAR`-wrapped findings surface; dev17 addresses that presentation defect.

## 0.1.0-dev15 — 2026-09-06
- Recorded representative-device dev14 Maintenance Insights evidence: normal-width rendering/focus and constrained normal-text HighContrast rendering/focus/scroll reachability were positive, including true-bottom findings access with 24,225 inspected entries and 0 scan errors.
- Classified the constrained `GDK_DPI_SCALE=2` dev14 run as failed/open because the findings viewport could not reach its true bottom, continuous resizing was reported as very slow, and HeaderBar title/subtitle text visibly truncated under width pressure.
- Wrapped the whole Insights page in a vertical scroller so enlarged fixed explanatory/status content cannot permanently push findings below the physical window.
- Guaranteed a 320-pixel minimum findings viewport while retaining its independent scroll position.
- Reused the shared `GDK_DPI_SCALE`-aware effective-width compact contract; compact mode shortens the HeaderBar title to `Insights`, removes the subtitle, and uses concise explanatory/privacy/status copy.
- Changed findings wrapping from `WORD_CHAR` to deterministic `CHAR` in an attempt to reduce continuous-resize relayout cost for long path-like strings.
- Added source-contract tests and validation guards for outer-page scrolling, minimum findings height, compact rendering, and deterministic wrapping.
- Advanced runtime/package/AppStream/README/CI metadata to `0.1.0-dev15` / `0.1.0~dev15`.
- Dev15 remained Development until exact-head target validation; its later representative-device pass confirmed package success but still showed compact HeaderBar title truncation.

## 0.1.0-dev14 — 2026-09-06
- Accepted the dev13 reporting slice on the representative Zorin OS laptop at exact runtime/source head `48049b6f634a05300e01bb0e85d718284b79d7ee`: all 38 tests plus XML/source validation passed, `0.1.0~dev13` built and upgraded over dev12, `dpkg-query` reported `install ok installed 0.1.0~dev13`, `--version` returned `0.1.0-dev13`, and both human and JSON read-only reports executed successfully.
- Recorded the dev13 representative report values as evidence rather than product guarantees: 74.7 GB free of 233.2 GB, 135.0 MB visible across 984 maintenance items, and zero scan errors. The human/JSON outputs agreed on the maintenance totals and exposed no candidate paths or raw scan-error strings.
- Added a read-only Maintenance Insights engine that groups stale (>7-day) application-cache candidates by top-level cache namespace while excluding thumbnails.
- Added read-only large-file discovery for regular user-owned files at least 250 MB under `Downloads`, `Desktop`, `Documents`, `Pictures`, `Videos`, and `Music`.
- Added read-only stale-Downloads review for regular user-owned files at least 30 days old.
- Kept the discovery scope symlink-safe and bounded: links are not followed and each standard-folder refresh is capped at 50,000 visited entries, with an explicit partial-results flag if the limit is reached.
- Added a dedicated GTK Maintenance Insights review window launched with `goreecloud-care --insights-ui`, plus a **Maintenance Insights (Read-only)** desktop action.
- The Insights window shows home-relative paths only in the explicitly opened local review surface; default `--report` and `--report-json` output remains path-redacted.
- Added a non-editable scrolling results view, accessible result name/description, ATK status-bar semantics, live accessible status-name updates, and a read-only Refresh action.
- Added source-level guards proving the Insights engine/window contains no deletion, PolicyKit, privileged-helper, subprocess, or network execution path.
- Added unit coverage for stale-cache grouping, large-file scope and symlink behavior, stale-Download age filtering, bounded discovery, home-relative rendering, and the read-only GTK source contract.
- Advanced runtime, Python project metadata, Debian package metadata, AppStream metadata, source-validation guards, desktop integration, documentation, and CI package inspection to `0.1.0-dev14` / `0.1.0~dev14`.
- Dev14 Maintenance Insights remains source/package-only until exact-head repository validation and representative-device build/install, rendered-result, keyboard/focus, HighContrast, large-text/constrained-window, and AT-SPI acceptance are completed.

## 0.1.0-dev13 — 2026-09-06
- Added a privacy-safe, read-only maintenance-reporting layer over the existing Care scan engine.
- Added `goreecloud-care --report` for human-readable local maintenance snapshots and `goreecloud-care --report-json` for schema-versioned machine-readable output.
- Added `goreecloud-care --version` for installed Development-version verification.
- Added conservative disk-headroom classification (`comfortable`, `watch`, `low`, `critical`, `unknown`) as an informational capacity signal only; it never triggers cleanup and is not a filesystem-health/failure claim.
- Reports aggregate visible maintenance bytes/items, per-category byte/item counts, scan-error counts, disk headroom, memory availability, and file-cache estimates.
- Reports deliberately omit candidate file paths, local filenames, and raw scan-error strings by default, and explicitly declare that they do not use telemetry or the network.
- Report modes never delete files, invoke PolicyKit, call the privileged helper, or authenticate.
- Added pure unit coverage for disk-headroom bands, aggregate report totals, JSON machine readability, and path/raw-error redaction.
- Added `CAPABILITIES.md` and substantially expanded `BENEFITS.md`, `FEATURES.md`, the Development specification, README, and user manual with current and planned Care capabilities while preserving the preview-first/least-privilege boundaries.
- Advanced Python runtime metadata, Debian package metadata, AppStream metadata, source-validation guards, and CI package inspection to `0.1.0-dev13` / `0.1.0~dev13`.
- The latest representative dev12 AT-SPI polling output confirms all three routine cleanup selectors were unchecked and the live status bar could be read at its initial `Scan complete` value. The submitted output did not yet contain the post-click status mutation, so dynamic status-value/event delivery and Orca announcement quality remain open.
- Representative-device dev13 build/install/report execution is accepted at exact runtime/source head `48049b6f634a05300e01bb0e85d718284b79d7ee`; broader accessibility, rollback, branding, and Platform-System gates remain open.

## 0.1.0-dev12 — 2026-09-06
- Recorded representative-device dev11 AT-SPI revalidation as failed for application-root identity: the AT-SPI desktop tree remained readable, but the running Care process was still exposed as `__main__.py` rather than `GoreeCloud Care`, so product-name discovery still failed.
- Corrected the identity boundary by setting both `GLib.set_prgname("GoreeCloud Care")` and `GLib.set_application_name("GoreeCloud Care")` before `Gtk.Application` startup. The program identity is established first so `GApplication.run()` cannot inherit the Python module basename for assistive-technology discovery.
- Expanded accessibility identity regression coverage to require the program name and human-readable application name before launch, and to require program identity establishment before application identity.
- Strengthened local source validation to guard both GLib identity declarations.
- Advanced runtime, Python project metadata, Debian package, AppStream metadata, README, Platform Contract, validation guards, and CI package inspection to dev12.
- Representative-device dev12 AT-SPI identity revalidation now exposes the application root as `GoreeCloud Care`, closing the dev10/dev11 product-identity defect for this target slice.
- A follow-up static semantic-tree probe confirms a genuine `status bar`, useful accessible names/descriptions for Scan, the three cleanup selectors, Reclaim file cache…, Clean selected, Empty Trash…, and Clean APT cache…, and live focus/checked states. Treat application-root identity and static roles/names/descriptions/state semantics as accepted for this representative dev12 slice.
- A first dynamic `object:property-change:accessible-name` listener attempt produced no Care status events and again emitted the representative session's stale/unavailable AT-SPI socket warning. This is classified as inconclusive for Care dynamic semantics rather than a confirmed application defect because static AT-SPI reads continue to work and `set_status()` updates the accessible name and emits `visible-data-changed`. Read-only status-name polling during a manual Scan is the next discriminator between application semantic updates and event-subscription transport failure.
- Dynamic status-change/event delivery, screen-reader announcement quality, and broader Release Candidate gates remain open.

## 0.1.0-dev11 — 2026-09-06
- Attempted to correct the first AT-SPI application-root naming defect by setting `GLib.set_application_name("GoreeCloud Care")` before `Gtk.Application` startup.
- Added a source-level regression test and advanced Development package metadata to dev11.
- Representative-device dev11 validation/build/install succeeded with 31 tests plus XML/source validation and `install ok installed 0.1.0~dev11`.
- Fresh AT-SPI revalidation nevertheless still exposed the application root as `__main__.py`; dev11 therefore did not close the accessibility identity defect and must not be represented as accepted.

## 0.1.0-dev10 — 2026-09-05
- Recorded fresh representative-device dev9 HighContrast evidence. The system HighContrast presentation now visibly replaces GoreeCloud Care's light Development palette, confirming that the dev9 `GTK_THEME` takeover remediation works on the target laptop.
- Recorded a new blocking accessibility result from that same pass: pressing Tab produces no visibly perceivable focus response. This is negative keyboard-under-HighContrast evidence; it does not by itself prove whether logical GTK focus traversal stopped or whether focus merely became visually silent.
- Source inspection identified the most direct regression boundary: Care's normal application CSS contains the established explicit `button:focus, checkbutton:focus` ring, but HighContrast correctly detaches that entire provider to yield palette authority to the system theme. The target HighContrast theme did not provide a sufficiently perceivable replacement focus indication.
- Added a separate focus-resilience GTK provider that defines only a 3-pixel focus outline using `@theme_fg_color`. It is installed one priority level below Care's normal application CSS, preserving the established normal Care focus treatment while remaining available when the normal palette provider is removed for HighContrast.
- Added pure source-level regression coverage proving the fallback applies to buttons and checkbuttons, uses a theme-derived color, and does not define application palette/background colors.
- Advanced runtime, Python project metadata, Debian package, AppStream metadata, validation guards, and CI package inspection to dev10.
- Exact dev10 runtime head `3524a4a82da87ea51dcde08992a402190b54c130` is now repository-validated and representative-device built/installed. On the target Zorin OS laptop all 30 local tests plus XML/source validation passed, the `0.1.0~dev10` Debian package built successfully, the package upgraded from dev9 to `install ok installed 0.1.0~dev10`, and the app launched under `GTK_THEME=HighContrast`.
- Fresh HighContrast screenshots verify visibly perceivable keyboard focus on the HeaderBar Scan button, the Thumbnail cache checkbutton, and the Reclaim file cache button while system HighContrast remains authoritative for the palette. Treat the dev9 no-visible-Tab-response defect as closed for these representative dev10 checkpoints.
- Full keyboard-under-resilience acceptance remains open for the remaining bottom actions, complete forward and reverse traversal, constrained-width HighContrast, and assistive-technology semantics; dev10 remains Development/nonconformant.

## 0.1.0-dev9 — 2026-09-05
- Recorded the first representative-device HighContrast acceptance pass from an isolated `GTK_THEME=HighContrast goreecloud-care` launch. Screenshots verify clearly visible keyboard focus on Scan, a category checkbox, and Memory Refresh, plus readable unclipped normal-width layout.
- Classified HighContrast rendering itself as failed/open: the application still displayed the GoreeCloud light Development palette instead of yielding to the system HighContrast presentation.
- Source inspection identified the exact contract gap: Care detected HighContrast only from `Gtk.Settings:gtk-theme-name`, while the acceptance harness applies a process-local `GTK_THEME` override that is not guaranteed to be reflected by that settings property.
- Expanded the pure HighContrast contract so the effective state accepts either a HighContrast `Gtk.Settings` theme name or a HighContrast `GTK_THEME` override, including `HighContrast:dark`-style variants.
- Added unit coverage for explicit override values and live process-environment detection, and strengthened source validation so future Development changes cannot silently drop the override path.
- Advanced runtime/package/AppStream Development metadata to dev9. This is source remediation only; HighContrast target rendering remains unverified until dev9 is built, installed, and the representative-device acceptance pass is repeated.

## 0.1.0-dev8 — 2026-09-05
- Recorded representative-device dev7 revalidation at exact head `6e81f119372cc0aa3eb5a9098266340d8bca540c`: 20 local tests, XML/source validation, dev7 Debian build, upgrade/install to `0.1.0~dev7`, and all three exact-head GitHub workflow families passed.
- Direct `GDK_DPI_SCALE=2` screenshots nevertheless proved the dev7 combined large-text/compact remediation did not activate at the narrowest reachable target-device window. The HeaderBar subtitle remained visible, category amounts remained right-aligned, and `Clean selected`, `Empty Trash…`, and `Clean APT cache…` remained horizontal. Text wrapping, vertical scrolling, and visible keyboard focus remained positive.
- Classified the dev7 result as a target-runtime adaptive-layout failure rather than a missing-evidence condition: raising the raw allocation breakpoint alone did not account for the GTK text-scale environment used by the 200%-text acceptance run.
- Added a pure text-scale-aware effective-width contract. When `GDK_DPI_SCALE` is greater than 1, the raw allocated width is divided by that scale before the 820-logical-pixel compact breakpoint is evaluated; normal-text behavior keeps the existing 820 threshold.
- Added regression coverage for explicit 200% effective width, default `GDK_DPI_SCALE=2` environment behavior, and invalid/subnormal scale fallback.
- Exact dev8 head `45b5f11a49f363ebcaf753c892245a31109bc9bb` passed GoreeCloud Care Development run `33976609005`, Validate theme source run `33976608933`, and GoreeCloud Care Platform Contract run `33976609331`.
- Representative-device dev8 validation passed 24 local tests plus XML/source validation, built and installed `goreecloud-care_0.1.0~dev8_all.deb`, and fresh `GDK_DPI_SCALE=2` screenshots verify the regular wide composition plus the compact narrow composition. At the narrowest reachable enlarged-text width the Development subtitle is omitted, category amounts reflow below their descriptions, long content wraps without horizontal clipping, scrolling reaches the bottom, and the three maintenance actions form a vertical full-width stack.
- Treat the combined 200%-text + compact/minimum-width adaptive-layout blocker as closed for this representative-device slice. GoreeCloud Care remains Development/nonconformant while HighContrast, full keyboard-under-resilience, assistive-technology semantics, supported appearance evidence, official branding, rollback, final current-Stable Glaze UI V1.1 acceptance, and remaining platform-system gates stay open.

## 0.1.0-dev7 — 2026-09-05
- Recorded direct representative-device negative evidence for the dev6 combined 200%-text/compact path: at the narrowest reachable `GDK_DPI_SCALE=2` window, the regular horizontal composition remained active, category amounts stayed right-aligned, and the bottom action group could not transition to the previously accepted compact stack.
- Raised the Development compact transition from 680 to 820 logical pixels so compact composition activates before the observed enlarged-text minimum-width floor.
- Reused the pure `is_compact_width()` contract in the GTK layout path and added regression coverage for the observed approximately 800-pixel enlarged-text range.
- Compact HeaderBar presentation now omits the Development subtitle instead of leaving it visibly ellipsized, reducing width pressure while preserving the product title and Scan action.
- This is a Development remediation candidate. Combined 200%-text/compact rendering remains unaccepted until the dev7 package is rebuilt, installed, and revalidated on the representative Zorin OS laptop.

## 0.1.0-dev6 — 2026-09-05
- Started the accessibility and adaptive-window acceptance phase after representative-device dev5 testing verified every current maintenance function, including controlled nonzero APT archive removal.
- Added a compact desktop composition below 680 logical pixels: category amounts move below their content and the primary bottom actions stack vertically instead of compressing horizontally.
- Defined a 480 × 420 logical-pixel minimum Development window and retained vertical scrolling so constrained-height and larger-text layouts remain reachable.
- Added text wrapping for system status and category headings to reduce clipping risk under constrained width or large text.
- Added GTK/ATK status semantics, dynamic accessible status names, action descriptions, selector descriptions, and descriptive accessible names for scanned category amounts.
- Added high-contrast resilience: common GTK HighContrast theme names suppress the application color provider so the system high-contrast theme can take precedence over GoreeCloud Care's light Development mapping.
- Added pure adaptive/high-contrast UI contract helpers and unit coverage without importing GTK into the test boundary.
- Added an explicit `gir1.2-atk-1.0` package dependency for the new ATK accessibility mapping.
- Dev6 source work does not establish rendered, large-text, high-contrast, screen-reader, or current-Stable Glaze UI acceptance until target-device evidence is completed.

## 0.1.0-dev5 — 2026-09-05
- Fixed post-action status replacement that could hide successful privileged-action feedback behind the automatic refresh scan.
- Added an explicit completion notice after successful PolicyKit-authorized APT cache cleanup and Memory Refresh.
- Added a post-action refresh path that updates category/system values without overwriting the final success/exception status.
- Applied the same status-preservation behavior to normal selected cleanup and Trash refreshes so their final result remains visible after values refresh.
- If a maintenance action completes but the follow-up scan fails, GoreeCloud Care now preserves the completed-action fact while reporting the refresh failure as attention instead of falsely claiming a fully refreshed result.
- Repository validation is green; representative-device successful privileged-action execution remains a required acceptance gate before success is treated as verified.

## 0.1.0-dev4 — 2026-09-05
- Changed GoreeCloud Care to open in a light appearance by default without modifying the user's desktop-wide Zorin OS appearance setting.
- Reworked the persistent maintenance-status surface into a higher-salience semantic indicator with a symbol, bold state label, stronger border/surface treatment, and explicit text so changed state does not depend on color alone.
- Classified ordinary user cancellation as an attention/changed-state condition rather than a warning or error; cancellation now uses a prominent but non-critical presentation.
- Added distinct informational, attention, success, and error status treatments mapped from current Glaze UI V1.1 semantic roles while keeping final Glaze UI conformance/acceptance explicitly open.
- Preserved the representative-device-verified high-contrast keyboard-focus treatment.
- Added source validation checks for the light-default preference and attention-status implementation.

## 0.1.0-dev3 — 2026-09-05
- Preserved the dev2 keyboard-focus treatment after representative Zorin OS screenshots verified that focus is now visibly perceivable on checkboxes and buttons.
- Added explicit status feedback when a user cancels any GoreeCloud Care confirmation dialog, including cache cleanup, Trash emptying, APT cache cleanup, and memory-cache reclaim; cancellation now states that no corresponding changes were made.
- Hardened PolicyKit cancellation classification using the actual Zorin OS dismissal text (`Error executing command as another user: Request dismissed`) in addition to pkexec exit status 126.
- Added regression coverage proving that the observed Zorin OS `Request dismissed` result is treated as cancellation and never as success.
- Aligned the Python runtime version declaration with the Development package version.

## 0.1.0-dev2 — 2026-09-04
- Added an explicit high-contrast keyboard focus treatment and explicit focusability for interactive controls after representative Zorin OS testing found Tab traversal was not visibly perceivable.
- Moved operation status into a persistent near-top status banner so scan and maintenance results remain visible without scrolling to the bottom of the window.
- Added explicit PolicyKit/pkexec cancellation handling: exit status 126 now produces a visible cancellation dialog and states that the privileged maintenance command was not run and no privileged changes were made.
- Added explicit non-success handling for authorization errors and helper failures, with unit coverage for success, cancellation, authorization failure, and helper failure outcomes.
- Kept confirmation dialogs fail-safe by defaulting keyboard focus to Cancel.

## 0.1.0-dev1 — 2026-09-04
- Initial GoreeCloud Care Development bootstrap.
- Added safe cache, thumbnail, stale temp, Trash, APT cache, disk/memory status, and file-cache reclaim foundations.
- Added PolicyKit boundary, tests, Debian packaging, component-local GoreeCloud documentation, and a Platform Contract v0.2 component declaration.
- Integrated source ownership into `GoreeCloud/goreecloud-zorin-os` under `apps/goreecloud-care/`; no separate Care repository is authoritative.
