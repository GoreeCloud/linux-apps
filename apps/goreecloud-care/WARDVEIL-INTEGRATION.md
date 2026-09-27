# GoreeCloud Care — Wardveil Security Integration

## Scope

GoreeCloud Care uses the current Wardveil Security status semantics for a narrowly scoped security-evidence producer covering the installed Care privileged-maintenance boundary. This integration does not make Wardveil the executor of Care maintenance, does not grant Wardveil arbitrary command authority, and does not authorize a broad `Protected by Wardveil` product claim.

## Authoritative producer

GoreeCloud Care is authoritative only for these Care-owned facts:

- the installed fixed helper location;
- the installed Care PolicyKit policy location;
- whether those fixed files satisfy the expected root-ownership and write-permission constraints;
- whether `/usr/bin/pkexec` is available for the existing PolicyKit flow;
- the source-enforced helper action allowlist and no-arbitrary-shell/path boundary;
- whether the installed application/helper launchers use isolated Python path semantics so a user-controlled working directory, `PYTHONPATH`, or user site cannot shadow the installed Care package;
- whether the fixed private Care Python package directory is free of stale runtime bytecode that could affect cross-version execution.

PolicyKit, the operating system, and APT remain authoritative for their own behavior. Wardveil Security remains authoritative for Wardveil security semantics and any future Wardveil-native policy, scanning, quarantine, incident, or audit service.

## Installed launcher isolation

Representative dev18 package-lifecycle testing found that the pre-dev19 launchers used plain `python3 -m goreecloud_care...`. When the installed package had been downgraded to dev17 but the command was launched from a newer source directory, Python could resolve the working-tree package instead of the installed package. The privileged helper used the same ambient import pattern, so this was treated as a security-boundary defect rather than merely a test-harness issue.

Dev19 changed both installed entrypoints to `/usr/bin/python3 -I -B -m ...`. `-I` excludes the current working directory, `PYTHONPATH`, and user site from import resolution; `-B` prevents new runtime bytecode writes. Debian `postinst`/`postrm` scripts remove only the fixed private Care `__pycache__` path so bytecode created by earlier Development versions cannot survive an install/remove transition. Installed acceptance deliberately attempts same-named working-directory shadowing against both entrypoints.

Representative dev20 package-lifecycle evidence accepted that remediation on the Zorin OS target through install, remove, fresh reinstall, downgrade to accepted dev17, restore, and final-state validation. Dev22 retains the same boundary.

## Local status API

`goreecloud-care --security-status-json` returns a Wardveil-compatible `0.1.0` status record for the local Care privilege boundary.

A passing result requires the fixed helper and policy files to be regular files owned by the expected root UID, neither file to be group/world writable, the helper to be owner-executable, and `/usr/bin/pkexec` to be executable. Missing or non-passing evidence produces `attention` rather than a passing state.

The record is explicitly scoped to application `goreecloud-care`, identifies `GoreeCloud Care` / `local-maintenance-privilege-boundary` as the Care-owned authority, carries an observation timestamp and a short passing validity window, and fails closed when current evidence is unavailable.

The record deliberately sets `claim.protected_by_wardveil` to `false`. Care must not display or advertise `Protected by Wardveil` merely because it emits a Wardveil-compatible status record.

## Privacy boundary

The shared record omits user identity, arbitrary local file paths, raw privileged command output, credentials, secrets, private keys, recovery material, and unrestricted diagnostics. It reports only the scoped normalized state, observation/freshness data, a short summary, and explicit redaction metadata.

## Failure and freshness behavior

Missing helper/policy/pkexec evidence fails closed to a non-passing state. Writable privileged-boundary files also fail closed. A passing record receives a 15-minute validity interval so stale evidence cannot remain indefinitely reassuring. Consumers must re-evaluate after expiry.

State is communicated through explicit text fields (`state`, `source_state`, summary, authority and scope), so the evidence does not depend on color or iconography alone.

## High-impact actions

Care does not currently accept Wardveil runtime-authorization envelopes for `apt-clean`, file-cache reclaim, user-file cleanup, or Trash deletion. Existing Care actions retain their explicit local user confirmation, PolicyKit, ownership, fixed-allowlist, and application-specific authorization boundaries. Therefore Wardveil's high-impact cross-service executor requirements are not claimed as implemented by this integration.

## Exact-source automated prequalification

At exact Care source revision `96c731a35912edee113ad04eb8fd2c96b306bdf6`, GoreeCloud Care Development run `34139295536` passed the following Wardveil-relevant automated evidence on Ubuntu 24.04 CI:

- 106 source/unit tests, including passing and non-passing privilege-boundary states, exact scope/authority semantics, freshness, sensitive-field minimization and the explicit no-protection-claim invariant;
- installed `0.1.0~dev22` validation against real package paths and root-owned installed files;
- repeated installed status validation before and after a complete remove/reinstall/downgrade/restore lifecycle;
- working-directory Python shadow-resistance checks for both the normal application and privileged helper launchers;
- private-bytecode cleanup checks;
- current installed Wardveil-compatible evidence reported as passing, current, minimized and scoped while keeping `protected_by_wardveil=false`;
- immutable rollback construction from accepted dev17 source `0fda6f90a545eaf3d1bed525aae98c6529ebbf7b`;
- full candidate install, remove, fresh reinstall, downgrade to dev17, restore to dev22, and final candidate-state validation without invoking a Care cleanup action.

The same exact head passed Care Platform Contract run `34139295983` and theme-source run `34139295510`. CI package SHA-256 was `eaa09e1339e6f069590819db26ab6e60e89ff14a380e668b95c90598bbce7395`; preserved artifact ID `10025251334` contains the dev22 package plus the immutable dev17 rollback package and provenance files.

This is **source/install/lifecycle prequalification**, not target-device Wardveil production acceptance. Ubuntu CI does not replace the representative Zorin OS acceptance requirement, central Wardveil governance, or final product-lifecycle promotion.

## Acceptance boundary

Care-side source evidence now covers the Wardveil adoption requirements that can be automated locally: integration documentation, protected/non-passing status behavior, missing/writable fail-closed behavior, freshness, explicit text semantics, sensitive-field minimization, launcher isolation, private-bytecode cleanup, and exact-source CI evidence.

Still required before any production-conformant Wardveil claim:

- central Wardveil consumer-source evidence registration and validation;
- exact-candidate representative Zorin OS installed-boundary acceptance at the applicable release lifecycle stage;
- any remaining security-relevant desktop PolicyKit-agent acceptance required by release policy;
- exact-candidate Privacy Shield acceptance where it affects the shared security-evidence boundary;
- governed Wardveil adoption/promotion explicitly permitting the claim.

Until those steps complete, `goreecloud.platform.yaml` must remain fail-closed and `claim.protected_by_wardveil` must remain `false`.
