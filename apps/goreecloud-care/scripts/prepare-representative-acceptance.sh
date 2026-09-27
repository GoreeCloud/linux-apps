#!/bin/sh
set -eu

ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
REPO_ROOT=$(CDPATH= cd -- "$ROOT/../.." && pwd)
OUT=${1:-"$ROOT/dist/representative-acceptance"}
EXPECTED_RUNTIME_VERSION="0.2.0-dev2"
EXPECTED_PACKAGE_VERSION="0.2.0~dev2"
EXPECTED_PACKAGE="$ROOT/dist/goreecloud-care_${EXPECTED_PACKAGE_VERSION}_all.deb"
GLAZE_TARGET="2.2.0"
GLAZE_SOURCE_REVISION="6731098b28dd0393faa878c70d989a221d714a20"
GLAZE_RELEASE_TAG="v2.2.0"

for command_name in git python3 sha256sum dpkg-deb tee awk rm mktemp grep; do
  command -v "$command_name" >/dev/null || {
    echo "Required command not found: $command_name" >&2
    exit 2
  }
done

TRACKED_CHANGES=$(git -C "$REPO_ROOT" status --porcelain --untracked-files=no -- apps/goreecloud-care .github/workflows/care-ci.yml .github/workflows/care-platform-contract.yml)
[ -z "$TRACKED_CHANGES" ] || {
  echo "Tracked Care/CI changes are present. Commit/stash them before preparing exact-source Glaze UI 2.2 acceptance evidence." >&2
  printf '%s\n' "$TRACKED_CHANGES" >&2
  exit 2
}

SOURCE_REVISION=$(git -C "$REPO_ROOT" rev-parse HEAD)
SOURCE_BRANCH=$(git -C "$REPO_ROOT" symbolic-ref --quiet --short HEAD 2>/dev/null || printf '%s' detached)
RUNTIME_VERSION=$(PYTHONPATH="$ROOT" python3 -c 'from goreecloud_care import __version__; print(__version__)')
[ "$RUNTIME_VERSION" = "$EXPECTED_RUNTIME_VERSION" ] || {
  echo "Representative Glaze UI 2.2 harness expects runtime $EXPECTED_RUNTIME_VERSION; got $RUNTIME_VERSION" >&2
  exit 2
}
grep -Fx 'lifecycle: development' "$ROOT/goreecloud.platform.yaml" >/dev/null || {
  echo "Representative 0.2.0-dev2 preparation requires lifecycle: development." >&2
  exit 2
}
grep -F 'status: nonconformant' "$ROOT/goreecloud.platform.yaml" >/dev/null || {
  echo "0.2.0-dev2 must remain nonconformant until exact Glaze UI 2.2 and platform acceptance is promoted." >&2
  exit 2
}
grep -F 'glaze_ui_required: "2.2.0"' "$ROOT/goreecloud.platform.yaml" >/dev/null || {
  echo "Representative acceptance requires the Glaze UI 2.2.0 compatibility contract." >&2
  exit 2
}
grep -F "$GLAZE_SOURCE_REVISION" "$ROOT/goreecloud_care/glaze_v22.py" >/dev/null || {
  echo "Representative acceptance requires the pinned Glaze UI 2.2 source authority." >&2
  exit 2
}

INSTALLED_PROBE_DIR=$(mktemp -d)
cleanup() {
  rm -rf "$INSTALLED_PROBE_DIR"
}
trap cleanup EXIT INT TERM

mkdir -p "$OUT"

printf '%s\n' "Preparing read-only/non-destructive 0.2.0-dev2 Glaze UI 2.2 representative acceptance evidence."
printf '%s\n' "Source revision: $SOURCE_REVISION"
printf '%s\n' "Source branch:   $SOURCE_BRANCH"
printf '%s\n' "Runtime version: $RUNTIME_VERSION"
printf '%s\n' "Glaze UI:        $GLAZE_TARGET ($GLAZE_RELEASE_TAG @ $GLAZE_SOURCE_REVISION)"
printf '%s\n' "Output directory: $OUT"
printf '%s\n' "Installed-runtime probes use a clean neutral working directory."
printf '%s\n' "This preparation harness does not invoke Care cleanup, PolicyKit, pkexec, sudo, apt, or network operations."
printf '%s\n' "Stable promotion is not authorized by this preparation harness."

(
  cd "$ROOT"
  sh ./scripts/validate.sh
) 2>&1 | tee "$OUT/source-validation.log"

(
  cd "$ROOT"
  sh ./scripts/build-deb.sh dist
) 2>&1 | tee "$OUT/package-build.log"

PACKAGE=$EXPECTED_PACKAGE
[ -f "$PACKAGE" ] || {
  echo "Expected built package not found: $PACKAGE" >&2
  exit 1
}
PACKAGE_VERSION=$(dpkg-deb -f "$PACKAGE" Version)
[ "$PACKAGE_VERSION" = "$EXPECTED_PACKAGE_VERSION" ] || {
  echo "Representative Glaze UI 2.2 harness expects package $EXPECTED_PACKAGE_VERSION; got $PACKAGE_VERSION" >&2
  exit 2
}
sha256sum "$PACKAGE" > "$OUT/package.sha256"
PACKAGE_SHA256=$(awk '{print $1}' "$OUT/package.sha256")

cat > "$OUT/SOURCE_REVISION" <<EOF
source_revision=$SOURCE_REVISION
source_branch=$SOURCE_BRANCH
lifecycle=development
runtime_version=$RUNTIME_VERSION
package_version=$PACKAGE_VERSION
package_sha256=$PACKAGE_SHA256
glaze_ui_target=$GLAZE_TARGET
glaze_ui_release_tag=$GLAZE_RELEASE_TAG
glaze_ui_source_revision=$GLAZE_SOURCE_REVISION
glaze_ui_manual_acceptance=false
stable_promotion_authorized=false
EOF

rm -f \
  "$OUT/report.json" \
  "$OUT/health.json" \
  "$OUT/privacy-status.json" \
  "$OUT/security-status.json" \
  "$OUT/continuity-status.json" \
  "$OUT/installed-status-snapshots-skipped.txt"

if command -v goreecloud-care >/dev/null 2>&1; then
  INSTALLED_RUNTIME=$(cd "$INSTALLED_PROBE_DIR" && goreecloud-care --version 2>/dev/null || true)
  if [ "$INSTALLED_RUNTIME" = "$EXPECTED_RUNTIME_VERSION" ]; then
    {
      printf 'installed_version=%s\n' "$INSTALLED_RUNTIME"
      printf 'api_version='
      (cd "$INSTALLED_PROBE_DIR" && goreecloud-care --api-version)
    } > "$OUT/installed-version.txt"
    (cd "$INSTALLED_PROBE_DIR" && goreecloud-care --report-json) > "$OUT/report.json"
    (cd "$INSTALLED_PROBE_DIR" && goreecloud-care --health-json) > "$OUT/health.json"
    (cd "$INSTALLED_PROBE_DIR" && goreecloud-care --privacy-status-json) > "$OUT/privacy-status.json"
    (cd "$INSTALLED_PROBE_DIR" && goreecloud-care --security-status-json) > "$OUT/security-status.json"
    (cd "$INSTALLED_PROBE_DIR" && goreecloud-care --continuity-status-json) > "$OUT/continuity-status.json"
  else
    {
      printf 'installed_version=%s\n' "$INSTALLED_RUNTIME"
      printf 'expected_runtime=%s\n' "$EXPECTED_RUNTIME_VERSION"
      printf 'api_version=not-probed-runtime-mismatch\n'
    } > "$OUT/installed-version.txt"
    printf '%s\n' \
      "Installed Care runtime differs from the exact 0.2.0-dev2 candidate; candidate-only status snapshots were skipped." \
      > "$OUT/installed-status-snapshots-skipped.txt"
  fi
else
  printf '%s\n' "GoreeCloud Care is not currently installed; installed read-only status snapshots were skipped." > "$OUT/installed-version.txt"
  printf '%s\n' "No installed Care executable was found; candidate-only status snapshots were skipped." > "$OUT/installed-status-snapshots-skipped.txt"
fi

cat > "$OUT/MANUAL-CHECKLIST.txt" <<'EOF'
GoreeCloud Care 0.2.0-dev2 — Glaze UI 2.2 representative-device checklist
============================================================================

Record PASS or FAIL plus notes for every exercised item. A blank item is NOT accepted evidence.
Do not use unrelated personal files for destructive-flow testing; use disposable fixtures/test data.
This checklist does not authorize Stable promotion by itself.

Lifecycle note: 0.2.0-dev2 / 0.2.0~dev2 is a Development / nonconformant candidate. Stable 0.1.0 remains immutable historical release evidence. The qualified dev1/V1.4 candidate is regression evidence only and does not transfer current Glaze UI 2.2, Privacy Shield, Wardveil, Everkeep, Platform Contract, representative-device, or Stable acceptance to this candidate.

A. Glaze UI 2.2 identity, System Shell, and composition
[ ] PASS [ ] FAIL  Main window title is GoreeCloud Care and subtitle reads Local maintenance • Glaze UI 2.2.
[ ] PASS [ ] FAIL  Maintenance Insights remains an application-level read-only surface and does not impersonate a system-authority panel.
[ ] PASS [ ] FAIL  Care behaves as a native Desktop/Wide Desktop product; compact/narrow states are window adaptations, not Phone/Tablet/TV/Foldable/Wearable/Spatial claims.
[ ] PASS [ ] FAIL  Compact window preserves all maintenance tasks without clipping or hidden consequential actions.
[ ] PASS [ ] FAIL  Narrow Desktop uses a readable single-column composition with stable task order.
[ ] PASS [ ] FAIL  Desktop uses the intended canonical Care composition.
[ ] PASS [ ] FAIL  Wide Desktop adds breathing room/hierarchy without giant targets, stretched copy, or gratuitous panes.
[ ] PASS [ ] FAIL  Resizing across compact/narrow/desktop/wide thresholds does not change task authority or semantic order.
[ ] PASS [ ] FAIL  Launcher/AppStream surfaces show GoreeCloud Care and no stale V1.2/V1.3/V1.4/RC label as the active design identity.
Notes:

B. 2.2 material budget and critical-state certainty
[ ] PASS [ ] FAIL  Durable reading/status/findings/content surfaces remain solid or near-solid enough for reliable comprehension.
[ ] PASS [ ] FAIL  Glaze is bounded to appropriate transient command/navigation/feedback chrome.
[ ] PASS [ ] FAIL  Care stays within one dominant Glaze surface plus at most three small floating Glaze controls.
[ ] PASS [ ] FAIL  No nested backdrop blur or decorative glass stack is visible.
[ ] PASS [ ] FAIL  Destructive and privileged confirmation moments become more solid/certain rather than more decorative.
[ ] PASS [ ] FAIL  State, success, failure, cancellation, warning, and privilege authority are never conveyed by material alone.
Notes:

C. Native accessibility and optical review
[ ] PASS [ ] FAIL  Light appearance is readable and stable.
[ ] PASS [ ] FAIL  Dark appearance is readable and stable.
[ ] PASS [ ] FAIL  Deep Dark appearance is readable and stable.
[ ] PASS [ ] FAIL  GTK HighContrast/system palette authority is respected; Care does not seize palette authority.
[ ] PASS [ ] FAIL  Reduced Transparency removes embellishment before meaning, hierarchy, focus, or state.
[ ] PASS [ ] FAIL  Reduced Motion suppresses application-owned motion/elevation without removing meaning.
[ ] PASS [ ] FAIL  Increased Contrast preserves hierarchy and obvious focus.
[ ] PASS [ ] FAIL  Show Borders remains readable and useful.
[ ] PASS [ ] FAIL  Effects-reduced mode remains usable without decorative shadows/effects.
[ ] PASS [ ] FAIL  Default interactive targets meet the 48 px governed floor where applicable.
[ ] PASS [ ] FAIL  Touch Assistance mode raises Care interactive targets to the 56 px floor where applicable.
[ ] PASS [ ] FAIL  Large text / approximately 200% text-equivalent scaling reflows without clipped or unreachable primary actions.
[ ] PASS [ ] FAIL  Forward/reverse keyboard traversal reaches every interactive control in logical order.
[ ] PASS [ ] FAIL  Visible focus remains obvious before and after form-factor transitions.
[ ] PASS [ ] FAIL  Dialog close/cancel/confirmation focus behavior remains safe and understandable.
[ ] PASS [ ] FAIL  Orca/AT-SPI scan, completion, cancellation, failure, and Maintenance Insights announcements are truthful.
[ ] PASS [ ] FAIL  Native window controls/compositor behavior are polished and do not conflict with the Care shell.
Notes:

D. Maintenance safety regression
[ ] PASS [ ] FAIL  Scan remains read-only and previews current maintenance state.
[ ] PASS [ ] FAIL  Routine cleanup preserves selection, confirmation, cancellation, failure, and success semantics.
[ ] PASS [ ] FAIL  Empty Trash remains explicitly permanent and confirmation-first.
[ ] PASS [ ] FAIL  APT and file-cache privileged flows preserve confirmation, PolicyKit cancellation, failure, and success truthfulness.
[ ] PASS [ ] FAIL  Privilege denial/dismissal cannot become success.
[ ] PASS [ ] FAIL  Post-action refresh preserves the actual action result and does not overwrite success/failure truth.
Notes:

E. 0.2 package lifecycle / continuity
[ ] PASS [ ] FAIL  Exact 0.2.0~dev2 package checksum/provenance matches the candidate source.
[ ] PASS [ ] FAIL  Candidate application/helper cannot be shadowed by the source working directory and leaves no private bytecode cache.
[ ] PASS [ ] FAIL  install/remove/reinstall/Stable-0.1.0-downgrade/0.2.0~dev2-restore/final-state probe passed.
[ ] PASS [ ] FAIL  Stable rollback package SHA-256 is exactly 819cff6e0132bf6b09df0986682995c25b14c39e74982f725efd0b5a21b71160.
Candidate package:
Stable rollback package:
Lifecycle log/evidence:

F. Current-platform acceptance boundaries
[ ] PASS [ ] FAIL  Glaze UI 2.2 exact-candidate human/native consumer review is complete for this exact source/package identity.
[ ] PASS [ ] FAIL  Privacy Shield exact-dev2 runtime/application review is complete or explicitly pending external governance.
[ ] PASS [ ] FAIL  Wardveil exact-dev2 scoped adoption/runtime review is complete or explicitly pending external governance.
[ ] PASS [ ] FAIL  Everkeep exact-dev2 continuity review is complete or explicitly pending external governance.
[ ] PASS [ ] FAIL  Platform Contract exact-dev2 conformance decision is complete or explicitly pending central governance.
[ ] PASS [ ] FAIL  No local Care evidence is presented as granting another authority's acceptance.
Notes:
EOF

cat > "$OUT/MANUAL-COMMANDS.txt" <<'EOF'
goreecloud-care
GDK_DPI_SCALE=2 goreecloud-care
GDK_DPI_SCALE=2 goreecloud-care --insights-ui
GTK_THEME=HighContrast goreecloud-care
GOREECLOUD_CARE_APPEARANCE=dark goreecloud-care
GOREECLOUD_CARE_APPEARANCE=deep-dark goreecloud-care
GOREECLOUD_CARE_REDUCE_TRANSPARENCY=1 goreecloud-care
GOREECLOUD_CARE_REDUCE_MOTION=1 goreecloud-care
GOREECLOUD_CARE_INCREASED_CONTRAST=1 goreecloud-care
GOREECLOUD_CARE_TOUCH_ASSISTANCE=1 goreecloud-care
GOREECLOUD_CARE_REDUCE_EFFECTS=1 goreecloud-care
GOREECLOUD_CARE_SHOW_BORDERS=1 goreecloud-care
GOREECLOUD_CARE_GLAZE_EXPRESSION=calm goreecloud-care
GOREECLOUD_CARE_GLAZE_EXPRESSION=balanced goreecloud-care
GOREECLOUD_CARE_GLAZE_EXPRESSION=expressive goreecloud-care
GOREECLOUD_CARE_GLAZE_CLARITY=clear goreecloud-care
GOREECLOUD_CARE_GLAZE_CLARITY=balanced goreecloud-care
GOREECLOUD_CARE_GLAZE_CLARITY=dense goreecloud-care

goreecloud-care --version
goreecloud-care --api-version
goreecloud-care --report-json
goreecloud-care --health-json
goreecloud-care --privacy-status-json
goreecloud-care --security-status-json
goreecloud-care --continuity-status-json

sh ./scripts/build-stable-0.1.0-rollback-package.sh
sh ./scripts/validate-package-lifecycle.sh './dist/goreecloud-care_0.2.0~dev2_all.deb' './dist/rollback/goreecloud-care_0.1.0_all.deb'
EOF

printf '%s\n' "0.2.0-dev2 Glaze UI 2.2 representative acceptance preparation: passed"
printf '%s\n' "Package: $PACKAGE_VERSION"
printf '%s\n' "SHA-256: $PACKAGE_SHA256"
printf '%s\n' "Manual checklist: $OUT/MANUAL-CHECKLIST.txt"
printf '%s\n' "Manual commands:  $OUT/MANUAL-COMMANDS.txt"
printf '%s\n' "Glaze UI human/native acceptance: pending"
printf '%s\n' "External governance promotion: not performed"
printf '%s\n' "Stable promotion authorized: false"
