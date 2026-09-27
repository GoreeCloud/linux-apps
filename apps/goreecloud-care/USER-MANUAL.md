# GoreeCloud Care User Manual

## Scan

Open GoreeCloud Care and choose **Scan**. Scanning is read-only and shows estimated size/item counts for Application cache, Thumbnail cache, Temporary files, Trash, and the APT package cache.

## Clean selected

Check any of Application cache, Thumbnail cache, and Temporary files, then choose **Clean selected**. A confirmation summarizes the estimated amount before deletion. Application-cache and temporary-file candidates use the seven-day age policy; temporary files must be owned by the current user. Symlinks are not followed.

## Empty Trash

Choose **Empty Trash…**. Care shows a separate warning because Trash deletion is permanent. Nothing is deleted if you cancel.

## Clean APT cache

Choose **Clean APT cache…** and confirm. PolicyKit asks for administrator authentication. The helper can run only the fixed `apt-get clean` action; it accepts no arbitrary command or path.

## Memory Refresh

Choose **Reclaim file cache…** only when you deliberately want Linux to release page/dentry/inode caches. Linux normally manages these caches automatically. Available memory may rise temporarily, but this is not a lasting performance boost and later file/app loads may be slower while caches rebuild.

## Read-only maintenance reports

```sh
goreecloud-care --report
goreecloud-care --report-json
goreecloud-care --version
```

The human report includes disk headroom, memory/file-cache information, visible maintenance totals, per-category byte/item counts, and scan-error counts. The JSON form is schema-versioned for local scripts and governed GoreeCloud consumers. Both are read-only: they do not delete files, request administrator authentication, invoke PolicyKit, run the helper, use telemetry, or access the network. Candidate paths, filenames, and raw scan-error strings are omitted by default.

Disk-headroom labels such as `comfortable`, `watch`, `low`, and `critical` are informational capacity signals. They are not filesystem-health certification and do not trigger cleanup automatically.

## Local status and platform integration — dev18

Dev18 exposes a local read-only command API. It does not open a network listener.

```sh
goreecloud-care --api-version
goreecloud-care --health-json
goreecloud-care --privacy-status-json
goreecloud-care --security-status-json
goreecloud-care --continuity-status-json
```

`--api-version` currently prints `1`. Health output is minimized and local-only. Privacy status is intentionally marked Development and not production-approved until Privacy Shield runtime acceptance is completed. Security status checks the fixed installed Care helper/PolicyKit boundary and does not make a broad **Protected by Wardveil** claim. Continuity status remains `attention` until package removal/downgrade/reinstall/rollback has been accepted on the target device.

These status commands are intended for local verification and future governed Manager/Mesh-style consumption. They do not grant another process maintenance authority and do not perform a maintenance action.

## Maintenance Insights

Open the read-only review surface with:

```sh
goreecloud-care --insights-ui
```

The installed desktop entry also provides **Maintenance Insights (Read-only)**.

Maintenance Insights reviews stale application cache older than seven days grouped by top-level namespace, files at least 250 MB in `Downloads`, `Desktop`, `Documents`, `Pictures`, `Videos`, and `Music`, and files in `Downloads` that are at least 30 days old. Choose the symbolic **Refresh** control to repeat the read-only scan.

The window may display home-relative paths such as `~/Downloads/example.iso` because you explicitly opened a local file-review view. Normal report/status output remains minimized. Insights does **not** select, move, quarantine, or delete a finding; does not request administrator authentication; does not invoke PolicyKit or the helper; does not launch subprocess maintenance commands; and does not access the network. Symlinks are not followed. Standard-folder discovery is capped at 50,000 visited entries per refresh and states when results are partial.

Review findings manually before changing them outside Care. A large file or old Download is not automatically junk and is not a recommendation to delete it.

Dev17 target validation accepted the targeted compact/wide rendering and reachability remediation: the `Insights` title remained visible, Refresh focus was perceivable, synthetic mid-word hyphens were removed, selectable findings rendered correctly, and the true bottom remained reachable. Complete Tab/Shift+Tab traversal through and beyond the selectable findings surface and continuous drag-resize responsiveness remain open acceptance checks.

## Keyboard and accessibility

Use **Tab** and **Shift+Tab** to move through controls. Care requires keyboard focus to be visibly perceivable. When a HighContrast system presentation suppresses Care's ordinary palette provider, a separate focus-only fallback uses the active GTK theme foreground color without redefining the application palette.

Accepted revision-scoped target evidence includes dev10 HighContrast palette/focus and requested core forward/reverse keyboard traversal, dev12 AT-SPI product identity plus static semantic roles/names/descriptions/checked/focused states, and dev17 targeted Insights rendering. Dynamic status-event delivery, Orca announcement quality, and full Insights keyboard/assistive-technology acceptance remain Development work.

Care remains vertically scrollable when text is enlarged or the window becomes shorter. Compact layouts place category values below their description and stack the bottom actions vertically. The Development 200%-text path includes GTK `GDK_DPI_SCALE` in the effective-width decision. Maintenance Insights has both whole-page scrolling and an independent findings scroller.

## Appearance

Care currently prefers a light application appearance. This application-local choice does not change the desktop-wide appearance setting. System HighContrast remains authoritative. The final supported appearance matrix is still part of the Release Candidate acceptance process.

## If an action fails

Care reports failure instead of treating it as success. Authorization cancellation is reported as cancellation rather than completion. A post-action refresh updates values without replacing the final outcome. No automatic retry performs a destructive action without another user invocation.

## Release status

`0.1.0-dev18` remains Development. Passing source tests or local status output does not make the application Release Candidate or Stable. See `RELEASE-ACCEPTANCE.md` in the source tree for the remaining governed acceptance requirements.
