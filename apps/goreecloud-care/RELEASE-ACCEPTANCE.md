# GoreeCloud Care Release Acceptance

## Governing lifecycle

GoreeCloud Care follows the governed lifecycle:

`Development -> Release Candidate -> Stable`

Lifecycle status is evidence-based. Source labels, a passing build, successful installation, a registry entry, a screenshot, a Care-produced status record, or an earlier accepted revision cannot independently promote a later candidate.

## Current Release Candidate source state

The current source line is nominated as **Release Candidate / nonconformant** while retaining the pre-release runtime/package version `0.1.0-dev22` / `0.1.0~dev22`.

The immediately preceding exact Development candidate `4f7aecd6fa5a6fdd6efb496e606c29457c18fefb` is valuable predecessor evidence, but its Privacy Shield, Wardveil, Everkeep, representative-target and package-SHA acceptance is exact-source/tree/package scoped and does not transfer to the RC source.

Release Candidate source status means the intended first-release functionality is frozen enough for final qualification. It does **not** mean RC-complete, Stable, production-approved, Protected by Wardveil, Everkeep-ready for this new exact source, or final Glaze-conformant.

## RC source qualification

Before the final RC SHA may be accepted as the immutable release candidate, all applicable automatable/source-level gates must pass at that exact revision:

- repository unit/source tests and static guards;
- Platform Contract structural validation with `lifecycle: release-candidate` and `status: nonconformant` until final production acceptance;
- canonical application/desktop/AppStream Release Candidate identity without `.dev` runtime identifiers;
- Privacy Shield, Wardveil, Everkeep and Glaze integration records that truthfully distinguish predecessor evidence from current exact-candidate acceptance;
- no known source-level security, privacy, recovery, data-integrity, packaging or accessibility blocker;
- package/runtime/application metadata agreement on `0.1.0-dev22` / `0.1.0~dev22` and Release Candidate lifecycle identity;
- isolated installed Python application/helper entrypoints that cannot resolve working-directory, `PYTHONPATH`, user-site or same-named-package shadowing;
- package install/remove behavior that removes fixed private bytecode and package-owned provenance correctly;
- rejection of dirty tracked Care source and untracked files that could enter the package;
- deterministic same-environment packaging;
- byte-identical package output on Ubuntu 22.04 and Ubuntu 24.04;
- package-owned root-controlled build provenance naming exact source revision, Care source tree, runtime/package version and deterministic source timestamp;
- immutable CI artifact evidence naming the exact RC source SHA and package SHA-256.

The package SHA-256 is external acceptance evidence because embedding a package's own digest inside itself is circular.

## Representative Zorin OS 17.3 exact-target acceptance

The exact frozen RC source/package must then pass representative Zorin OS 17.3 target qualification.

The authoritative automated runner is:

```sh
sh ./scripts/run-representative-acceptance.sh
```

Run it as the normal desktop user, not root. The runner may request `sudo` only for bounded package installation/evidence ownership operations. It must not invoke a Care cleanup action.

### Package lifecycle

The exact RC package must demonstrate:

- candidate install/upgrade;
- installed-state validation;
- complete package removal;
- fresh reinstall;
- downgrade/rollback to the immutable accepted dev17 package;
- post-rollback launch/report validation from a neutral working directory;
- restoration to the exact RC package;
- final installed-state validation;
- canonical desktop/AppStream/helper/policy/icon/provenance installation;
- application/helper working-directory shadow resistance;
- removal of private package bytecode/provenance residue when expected;
- final installed package-owned provenance matching the exact RC source revision, Care tree, runtime version and package version.

No unrelated personal content may be used as destructive test data.

## Continuity / Everkeep authority

Care produces evidence; Everkeep owns continuity governance.

After exact representative acceptance, Care may install only its target handoff at:

`/var/lib/goreecloud-care/acceptance/representative-target.json`

That record must name the exact RC source revision, Care tree, runtime/package versions, package SHA-256, Zorin target, local test count and package-lifecycle result. It must leave both promotion booleans false.

The Care target handoff alone may establish only:

`attention / target-accepted-governance-pending`

`ready / everkeep-promoted` requires a separate trusted Everkeep-owned record at:

`/var/lib/goreecloud/everkeep/acceptance/goreecloud-care.target-runtime.json`

The Everkeep record must match the installed exact source/tree/runtime/package identity, Zorin OS 17.3 target and the same package SHA-256, and must explicitly promote both integration and readiness. Missing, malformed, oversized, writable, symlinked, mismatched or unpromoted evidence fails closed.

## Privacy Shield exact-candidate acceptance

The RC must refresh Privacy Shield runtime/application acceptance for the exact RC source/package. Care remains local-first and limited to the declared `telemetry-minimization`, `data-minimization` and `privacy-status` adapter capabilities.

Production approval is a separate Stable/production gate. A passing RC runtime record does not itself authorize production approval.

## Wardveil exact-candidate acceptance

The RC must refresh Wardveil source/target evidence for the exact source/tree/package and provide immutable RC regression evidence required by Wardveil governance.

Care's local security status is evidence for the Care-owned privileged-maintenance boundary only. `protected_by_wardveil=false` remains authoritative until Wardveil explicitly promotes the exact candidate. Wardveil receives no execution authority over Care maintenance actions.

## Glaze UI boundary

The official Stable compatibility baseline remains:

`GLAZE UI V1.2 / 1.2.0`

Care may retain bounded V1.3 Adaptive Resonance preview styling, but upstream V1.3 remains Proposed and consumer-ineligible until governed otherwise. No Care source label may manufacture V1.3 Candidate/Stable status, accepted-v1, or production eligibility.

Human-only visual/usability/accessibility review may remain explicitly pending at RC when permitted by the lifecycle standard; Stable still requires all applicable final Glaze/product acceptance.

## Core task-flow acceptance

The release scope must preserve:

- scan without deletion;
- routine selected cache/temp cleanup only after current preview and explicit confirmation;
- no-selection/stale-preview failure handling;
- irreversible Trash confirmation and cancellation boundary;
- APT PolicyKit success/cancel/denial/failure truthfulness;
- Linux file-cache warning, PolicyKit boundary and truthful completion;
- post-action refresh preserving the final result;
- symlink-safe and user-ownership boundaries.

Automated task-flow probes may use mocks/fixtures and must remain non-destructive. Real destructive-flow testing, if release policy requires it, must use disposable data only.

## Reports and local API

Qualification includes:

- `--version` / `--api-version`;
- human and JSON reports;
- health, Privacy Shield, Wardveil-compatible and Everkeep continuity status;
- path/raw-error minimization;
- malformed or conflicting CLI mode rejection;
- no network, authentication or privileged maintenance in read-only modes.

## Accessibility and adaptive behavior

Automatable RC evidence includes:

- constrained/enlarged-text GTK layout;
- HighContrast authority;
- visible focus and complete keyboard traversal;
- no focus trap in selectable findings;
- AT-SPI application identity, roles/names/descriptions and dynamic status mutation;
- Dark/Deep Dark command contrast;
- Clear/Balanced/Dense clarity behavior;
- Reduced Motion application-owned behavior;
- true-bottom findings/page reachability.

Final representative Orca spoken-announcement quality is a human acceptance boundary and must not be fabricated from AT-SPI event delivery alone.

## Physical target review

Physical Zorin review may remain explicitly pending at RC when lifecycle policy permits, but must be resolved before Stable wherever applicable. This includes native/compositor/window-control rendering, canonical icon optical quality and representative desktop PolicyKit-agent interaction quality.

## Stable promotion

Stable promotion requires the accepted immutable RC revision/package to complete production-readiness review with no release blocker. At that point the repository Platform Contract, application metadata, project specification, changelog, release artifact record and other material lifecycle records must be synchronized to Stable.

Stable additionally requires every applicable current Platform System acceptance, including Glaze UI, Privacy Shield, Wardveil and Everkeep. Manager, Mesh and Identity may remain `not-applicable-justified` only while the released scope genuinely remains local single-user maintenance without their authority.

## Fail-closed rule

Any unresolved required gate remains a blocker. Care must not be described as RC-complete or Stable when required evidence is absent, stale, contradictory, failed, mismatched, untrusted or not run.
