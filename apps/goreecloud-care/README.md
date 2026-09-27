# GoreeCloud Care

**Lifecycle:** Development  
**Version:** `0.1.0-dev17`  
**Canonical source:** `GoreeCloud/goreecloud-zorin-os` → `apps/goreecloud-care/`  
**Target:** Zorin OS 17.3 and compatible GTK 3 Linux desktops  
**License:** GPL-3.0-or-later

GoreeCloud Care is an original, local-first GoreeCloud desktop maintenance application. It previews reclaimable storage before deletion, keeps routine cache/temp cleanup unprivileged, provides privacy-safe read-only reports, and has a bounded local Maintenance Insights review surface for understanding storage pressure before taking action.

## Current Development features

- Scan and clean application cache files older than 7 days.
- Clean the thumbnail cache.
- Scan and clean user-owned `/tmp` files older than 7 days.
- Preview Trash usage and empty Trash only after a separate permanent-deletion confirmation.
- Preview APT `.deb` cache and clean it through PolicyKit authorization.
- Display disk, available-memory, and file-cache status.
- “Memory Refresh” action that truthfully reclaims Linux file caches after a warning and PolicyKit authorization. It does **not** claim a lasting RAM/performance boost.
- Explicit cancellation, failure, partial-success, and completion reporting.
- Post-action refresh that updates scan values without replacing the final completion/exception status.
- Light appearance by default inside Care without changing the desktop-wide appearance setting.
- Adaptive compact layout, 200%-text effective-width behavior, vertical scrolling, and compact HeaderBar reduction.
- GTK/ATK/AT-SPI accessibility semantics, explicit Care application identity, visible focus, and HighContrast palette authority.
- No telemetry, advertising, cloud upload, remote service, or GoreeCloud account requirement.
- Symlink-safe user cleanup and fixed privileged-action boundaries.

## Privacy-safe read-only reports — accepted dev13 slice

```sh
goreecloud-care --report
goreecloud-care --report-json
goreecloud-care --version
```

`--report` produces a human-readable local maintenance snapshot. `--report-json` produces schema-versioned machine-readable JSON. Both modes are read-only: they scan the same maintenance categories but never delete files, authenticate, invoke PolicyKit, or access the network.

Reports include disk headroom, memory/file-cache summary, total visible reclaimable bytes/items, per-category byte/item counts, and scan-error counts. Candidate paths, filenames, and raw scan-error strings are deliberately omitted by default so the output is safer to copy into troubleshooting or local automation workflows.

Representative-device dev13 validation is accepted at exact runtime/source head `48049b6f634a05300e01bb0e85d718284b79d7ee`: 38 tests plus XML/source validation passed, `0.1.0~dev13` built and upgraded over dev12, `dpkg-query` reported `install ok installed 0.1.0~dev13`, `--version` returned `0.1.0-dev13`, and both human and JSON reports executed successfully on the Zorin OS laptop. The observed report showed 74.7 GB free of 233.2 GB, 135.0 MB visible across 984 maintenance items, and zero scan errors. These values are representative-device evidence from that run, not fixed product guarantees.

## Maintenance Insights — dev14 foundation, dev17 large-text refinement

Launch the Development review surface with:

```sh
goreecloud-care --insights-ui
```

The installed desktop entry also exposes **Maintenance Insights (Read-only)** as a desktop action.

The Insights engine is deliberately bounded and read-only. It currently reviews:

- largest stale application-cache groups using the same >7-day application-cache policy as routine Care cleanup, excluding thumbnails;
- large files of at least 250 MB in standard user folders (`Downloads`, `Desktop`, `Documents`, `Pictures`, `Videos`, and `Music`);
- Downloads at least 30 days old;
- aggregate scan-error count and whether the bounded discovery limit was reached.

Symlinks are not followed. The standard-folder crawl is capped at 50,000 visited entries per refresh so the feature cannot silently become an unbounded home-directory scan. Local file paths may be shown inside the explicitly requested interactive review window, while default Care reports remain path-redacted. No finding is automatically selected for deletion and the Insights modules contain no cleanup, PolicyKit, privileged-helper, or network execution path.

Representative-device dev14 screenshots accepted the normal-width rendering/focus slice and the constrained normal-text HighContrast rendering/focus/scroll slice. A subsequent `GDK_DPI_SCALE=2` constrained-width run exposed a large-text defect: fixed explanatory/status content could consume the visible allocation so the nested results viewport could not be scrolled to its true bottom, and continuous resizing was reported as very slow.

Dev15 introduced the whole-page vertical scroller, a 320-pixel minimum findings viewport, effective-width compact behavior, compact fixed copy, and `CHAR` result wrapping. Exact dev15 head `e36707264a62b4b66083c909b62b55041b909d12` passed all 48 local tests plus XML/source validation on the representative laptop, built `0.1.0~dev15`, and upgraded successfully to `install ok installed 0.1.0~dev15`. A fresh constrained-width `GDK_DPI_SCALE=2` screenshot confirmed compact mode was active, but the HeaderBar title still ellipsized to `Insig…` beside the full text Refresh action.

Dev16 replaced the text Refresh action with a symbolic button while preserving its accessible name, description, tooltip, and keyboard focus; reduced compact fixed-copy pressure; and retained the outer page/results scrolling contract. Representative-device dev16 screenshots now verify a fully readable `Insights` title, a clearly visible keyboard-focus ring on Refresh, and true-bottom findings reachability. The submitted evidence did not report continuous-resize responsiveness, so that performance checkpoint remains open rather than inferred. The same screenshots exposed a presentation defect from `CHAR` wrapping: Pango inserted synthetic hyphens at character breaks, producing fragments such as `da-` / `ys` and `in-` / `spected`.

Dev17 replaces the findings `Gtk.TextView` character-wrap surface with a selectable Pango-backed label using `WORD_CHAR` wrapping and `insert_hyphens='false'`. This retains character fallback for long path-like strings without inserting synthetic hyphens, does not add zero-width break characters to displayed/copied paths, and preserves the independent findings scroller, 320-pixel minimum viewport, accessible result name/description, and read-only behavior. Dev17 remains a Development remediation candidate until exact-head repository validation and representative-device rendering/resizing acceptance are complete.

See `CAPABILITIES.md` for the expanded current and planned capability set and `BENEFITS.md` for product/user benefits.

## Build and test

```sh
sh ./scripts/validate.sh
sh ./scripts/build-deb.sh
```

Representative Zorin OS testing through dev5 verifies the core cleanup and privileged-maintenance functions. Dev8 accepted the combined 200%-text + compact/minimum-width adaptive-layout slice for the core Care window. Dev10 accepted system HighContrast palette authority, visible focus, constrained-width composition, and complete requested forward/reverse keyboard traversal. Dev12 accepted the AT-SPI `GoreeCloud Care` application-root identity and the current static roles/names/descriptions/checked/focused-state semantic slice on exact runtime head `09c3a6bcbec094dd3cb0c828de88d084fcbd5a22`. Dev13 accepts the read-only reporting slice on exact runtime head `48049b6f634a05300e01bb0e85d718284b79d7ee`.

Dynamic assistive-technology event/announcement behavior remains open. A property-change listener did not receive status events in a session that also reported an unavailable/stale AT-SPI socket. A subsequent polling harness confirmed all three routine selectors were unchecked and successfully read the initial Care status, but the submitted output did not include a post-click status mutation result.

The generated Debian package remains Development software. Dev17 Maintenance Insights target revalidation, the still-unreported continuous-resize checkpoint, broader Maintenance Insights AT-SPI/Orca acceptance, dynamic core assistive-technology acceptance, package rollback, official GoreeCloud Care visual assets, full current-Stable Glaze UI acceptance, and broader GoreeCloud platform-system acceptance remain required before Release Candidate consideration.

## Install or upgrade a locally built Development package

```sh
sudo apt install ./dist/goreecloud-care_0.1.0~dev17_all.deb
```

Uninstall with:

```sh
sudo apt remove goreecloud-care
```

The canonical source-control authority is `GoreeCloud/goreecloud-zorin-os`. GoreeCloud Care is maintained as the `apps/goreecloud-care/` component so its Zorin OS packaging, desktop integration, target-device acceptance, and Platform Contract evidence remain coupled to the GoreeCloud Zorin OS development surface while preserving a distinct application boundary.
