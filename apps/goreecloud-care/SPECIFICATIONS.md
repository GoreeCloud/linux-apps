# GoreeCloud Care — Stable 0.1.0 Specification

**Lifecycle:** Stable  
**Released runtime/package:** `0.1.0` / `0.1.0`  
**Immutable release source:** `bbc4779454c2887b810aa0ddc9e8a686a4c68ebd`  
**Care source tree:** `ebe028347c978b6d09fb1d2af011729249f63bc3`  
**Released package SHA-256:** `819cff6e0132bf6b09df0986682995c25b14c39e74982f725efd0b5a21b71160`  
**Representative target:** Zorin OS 17.3  
**Stable design baseline:** GLAZE UI V1.2 / `1.2.0`

## Purpose and scope

GoreeCloud Care is a native, local-first desktop maintenance application for a person maintaining their own GoreeCloud/Zorin OS workstation. Stable `0.1.0` is deliberately bounded to local preview-first maintenance, explicit user-authorized cleanup, local storage/memory visibility, privacy-safe reporting, bounded Maintenance Insights, and narrow read-only platform-status integration.

The release does not provide remote administration, multi-user management, unattended deletion, cloud telemetry, cross-service maintenance execution, or a persistent application-owned user dataset.

## Release artifact authority

The Stable lifecycle promotes the already-qualified `goreecloud-care_0.1.0_all.deb` built from exact release source `bbc4779…`. The Stable governance revision is not a replacement package source and does not supersede package SHA `819cff6…`.

Any later rebuild, source change, privilege change, supported-platform change, or material platform-integration change is a new candidate/artifact and must satisfy the validation applicable to that change.

## Core maintenance contract

Stable `0.1.0` supports:

- stale application-cache cleanup;
- thumbnail-cache cleanup;
- eligible user-owned temporary-file cleanup;
- Trash preview plus separately confirmed permanent emptying;
- APT package-cache preview plus PolicyKit-authorized cleanup;
- disk, available-memory, and Linux file-cache status;
- separately warned and PolicyKit-authorized Linux file-cache reclaim.

Scanning never deletes. Cleanup uses current preview/selection state and explicit confirmation. No-selection, stale-preview, cancellation, authorization denial, helper failure, partial failure, and successful completion remain explicit and must never be conflated.

## Safety and privilege model

- Routine cache/temp cleanup runs as the logged-in user.
- Trash is a separate irreversible action with explicit confirmation.
- Privilege is restricted to the fixed `apt-clean` and `reclaim-memory` helper actions.
- The helper accepts no arbitrary path, shell fragment, or free-form command.
- Invalid helper actions fail closed; representative acceptance verified exit status `64`.
- Symlinks are not followed during user-file scanning/deletion.
- Generic stale cache/temp eligibility uses the established seven-day threshold.
- Confirmation dialogs default safely to cancellation.
- PolicyKit cancellation, denial, helper failure, and partial failure are never represented as success.
- Installed application/helper entrypoints remain isolated from working-directory and Python path shadowing.

## Real desktop PolicyKit acceptance

On the representative Zorin OS 17.3 laptop, all six required GUI checks passed for the exact released package:

1. APT cleanup — Care confirmation cancellation;
2. APT cleanup — PolicyKit authorization cancellation;
3. APT cleanup — privileged success;
4. file-cache reclaim — Care confirmation cancellation;
5. file-cache reclaim — PolicyKit authorization cancellation;
6. file-cache reclaim — privileged success.

Post-session installed validation, security status, and continuity status also passed.

## Read-only report and local API contract

Stable read-only modes are:

- `--version`;
- `--report`;
- `--report-json`;
- `--api-version`;
- `--health-json`;
- `--privacy-status-json`;
- `--security-status-json`;
- `--continuity-status-json`;
- `--insights-ui`.

Report/status modes do not delete files, request PolicyKit, invoke privileged maintenance, send telemetry, or access the network. Default reports omit candidate paths, filenames, and raw scan-error strings.

## Maintenance Insights

Maintenance Insights is read-only and bounded. It reviews:

- stale application-cache groups using the established >7-day policy;
- regular user-owned files of at least 250 MB in standard user folders;
- Downloads at least 30 days old;
- aggregate scan errors;
- bounded-discovery state.

Discovery does not follow symlinks and is capped. Findings are never automatically selected for deletion, movement, quarantine, package action, or privilege escalation.

## Accessibility and native presentation

Stable Care retains:

- explicit GLib/GTK application identity;
- ATK/AT-SPI status semantics and dynamic status updates;
- visible keyboard focus and forward/reverse traversal requirements;
- enlarged-text reflow through the shared effective-width contract;
- HighContrast system authority;
- Reduced Transparency, Reduced Motion, and Show Borders behavior;
- compact/medium/expanded composition;
- Light, Dark, and supported preview Deep Dark behavior;
- selectable Maintenance Insights findings and true-bottom reachability.

The predecessor frozen RC passed the governed seven-dimensional human/native acceptance. Exact `0.1.0` is accepted through the Glaze exact-source bridge because the release transition did not change governed Glaze implementation, icon, UI/focus/accessibility contract files, or runtime UI acceptance harness.

## Privacy Shield boundary

Privacy Shield authority `0af47f4817191541e1ea12928cff5c3458baf377` accepts the exact released source/tree/package for:

- telemetry minimization;
- data minimization;
- privacy status.

Care remains local-first, exports no raw private activity for status, and performs no remote tracker learning or telemetry.

## Wardveil Security boundary

Wardveil authority `e5c078a346a844c3a2a13e8eaa7fb98ba5fffa0f` accepts exact `0.1.0` runtime adoption after package/target and real-desktop PolicyKit acceptance.

Protection-claim permission is restricted to:

`GoreeCloud Care local-maintenance-privilege-boundary only`

No cross-service execution authority is granted. Care remains the technical authority for its local maintenance controls and produces bounded evidence rather than self-assigning Wardveil governance.

## Everkeep / continuity boundary

Everkeep authority `4586246aad87a4038c7f8984de809d32333f2599` governs exact `0.1.0` continuity readiness.

The trust chain is:

1. package-owned provenance at `/usr/share/goreecloud-care/build-provenance.json`;
2. Care-owned representative-target evidence at `/var/lib/goreecloud-care/acceptance/representative-target.json`;
3. Everkeep-owned governance at `/var/lib/goreecloud/everkeep/acceptance/goreecloud-care.target-runtime.json`.

On the accepted representative device, the Everkeep path is root-owned and non-writable (`0755` directory, `0644` record), and Care reports `ready / everkeep-promoted` with exact-build-bound freshness and no limitations.

## Glaze UI boundary

Stable `0.1.0` is an `accepted-v1` consumer of **GLAZE UI V1.2 / `1.2.0`** under Glaze authority `c3b077cd454825cd5a74cf21ba9e5dd4c25f94ae`.

Forward-looking Adaptive Resonance code remains bounded implementation detail, not a substitute for current Stable Glaze authority. A later officially promoted Glaze baseline requires fresh consumer migration/conformance evidence where applicable.

## Recovery and rollback

The accepted rollback checkpoint is `0.1.0~dev17`. Representative acceptance proved:

- exact `0.1.0` install/upgrade;
- removal;
- fresh reinstall;
- explicit downgrade to dev17;
- rollback launch/report functionality;
- restoration to exact `0.1.0`;
- final installed validation and provenance.

Care persists no substantial durable application-owned user dataset, so continuity centers on package reconstruction, exact provenance, rollback/restore, documentation, and truthful irreversible-maintenance boundaries.

## Release evidence

- exact source: `bbc4779454c2887b810aa0ddc9e8a686a4c68ebd`
- release qualification: `34180765807` / #421 / 143 tests
- Platform Contract: `34180766156` / #416
- theme validation: `34180765817` / #590
- package artifact: `10038827656`
- cross-environment artifact: `10038821545`
- package SHA-256: `819cff6e0132bf6b09df0986682995c25b14c39e74982f725efd0b5a21b71160`
- Privacy Shield: `0af47f4817191541e1ea12928cff5c3458baf377`
- Everkeep: `4586246aad87a4038c7f8984de809d32333f2599`
- Wardveil: `e5c078a346a844c3a2a13e8eaa7fb98ba5fffa0f`
- Glaze UI: `c3b077cd454825cd5a74cf21ba9e5dd4c25f94ae`

## Stable change rule

Stable does not mean permanently finished. Future controlled fixes and improvements are allowed, but a materially changed source/artifact does not inherit this exact-release acceptance automatically.
