# GoreeCloud Care Local API

## Status

GoreeCloud Care exposes a narrow, local-only command API for integration with other GoreeCloud components. It is not an HTTP service and does not open a listening socket.

API version: `1`.

The API is intentionally read-only. None of the API modes deletes files, invokes PolicyKit, runs the privileged helper, authenticates a user, sends telemetry, or accesses the network.

## Version discovery

```bash
goreecloud-care --api-version
```

Returns the single line:

```text
1
```

## Maintenance snapshot

```bash
goreecloud-care --report-json
```

Returns the versioned privacy-safe maintenance snapshot defined by the existing report schema. Candidate file paths, local filenames, and raw scan-error strings are excluded.

Endpoint identity used by the GoreeCloud Platform Contract:

`local-cli://goreecloud-care/report`

## Health status

```bash
goreecloud-care --health-json
```

Returns a minimized local health record containing the product name, installed version, observation time, readiness state, and explicit local-only/no-network/no-telemetry/no-privileged-action properties.

Endpoint identity:

`local-cli://goreecloud-care/health`

## Privacy Shield status

```bash
goreecloud-care --privacy-status-json
```

Returns a record shaped to the current Privacy Shield status contract for the Care application adapter. The Development source reports runtime acceptance as required and production approval as false. No raw private activity, credentials, or identifiers are included.

Endpoint identity:

`local-cli://goreecloud-care/privacy-status`

## Wardveil-compatible security status

```bash
goreecloud-care --security-status-json
```

Checks only the fixed installed privileged-boundary locations: the Care helper, the Care PolicyKit policy, and `/usr/bin/pkexec`. It verifies regular-file/executable availability, root ownership where required, and that the helper/policy are not group- or world-writable.

The returned Wardveil status record is scoped to the GoreeCloud Care local-maintenance privilege boundary. Care remains the authoritative producer for those installation facts. `protected_by_wardveil` remains false because source-side contract use does not imply Wardveil enforcement or a broad `Protected by Wardveil` claim.

Endpoint identity:

`local-cli://goreecloud-care/security-status`

## Everkeep continuity status

```bash
goreecloud-care --continuity-status-json
```

Returns Care's evidence-derived continuity view for the Debian package restore/rollback dimension. The output is governed by `contracts/continuity.status.schema.json` and never accepts a caller-supplied readiness boolean.

The state is derived from three local evidence layers:

1. package-owned exact-source provenance at `/usr/share/goreecloud-care/build-provenance.json`;
2. a Care-owned representative Zorin OS 17.3 target record at `/var/lib/goreecloud-care/acceptance/representative-target.json`;
3. a separate Everkeep-owned governance record at `/var/lib/goreecloud/everkeep/acceptance/goreecloud-care.target-runtime.json`.

Possible stages are:

- `provenance-unavailable` — installed package provenance is absent, untrusted, malformed, or does not identify this runtime/package;
- `target-acceptance-required` — no trusted exact-candidate Zorin OS 17.3 lifecycle record matches the installed build;
- `target-accepted-governance-pending` — the Care-owned exact-candidate target record matches, but separate exact package identity / Everkeep promotion is incomplete;
- `everkeep-promoted` — the complete exact-match chain is trusted and the separate Everkeep record explicitly promotes integration and readiness.

Only `everkeep-promoted` may return `state=ready`, and that output also carries `freshness=exact-build-bound`. The Care-owned target record is generated with both Everkeep promotion flags false and cannot self-promote. A promoted Everkeep record must match the installed source revision, Care source-tree SHA, runtime/package versions, Zorin OS 17.3 representative target, and exact package SHA-256 recorded by the Care target handoff.

Regular evidence files and their immediate parent directories must be root-owned and not group/other writable. Symlinked, malformed, oversized, writable, source-mismatched, target-mismatched, package-mismatched, or unpromoted evidence fails closed to `attention`.

Endpoint identity:

`local-cli://goreecloud-care/continuity-status`

## Consumer requirements

Consumers must treat these outputs as scoped status/evidence, not as authority to perform maintenance. They must validate the declared schema/version they support, fail closed on malformed or unavailable data, preserve the local-only privacy boundary, and avoid surfacing path-level or raw diagnostic data that the default reports intentionally redact.

GoreeCloud Manager or Mesh integration must not reinterpret a `ready`, privacy, security, or continuity field outside its documented scope. Privacy Shield, Wardveil Security, Everkeep, Manager, and Mesh retain their own independent production-acceptance boundaries.
