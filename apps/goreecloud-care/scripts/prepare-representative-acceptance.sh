#!/bin/sh
set -eu

ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
REPO_ROOT=$(CDPATH= cd -- "$ROOT/../.." && pwd)
OUT=${1:-"$ROOT/dist/representative-acceptance"}
EXPECTED_RUNTIME_VERSION="0.1.0"
EXPECTED_PACKAGE_VERSION="0.1.0"
EXPECTED_PACKAGE="$ROOT/dist/goreecloud-care_${EXPECTED_PACKAGE_VERSION}_all.deb"

for command_name in git python3 sha256sum dpkg-deb tee awk rm mktemp grep; do
  command -v "$command_name" >/dev/null || {
    echo "Required command not found: $command_name" >&2
    exit 2
  }
done

TRACKED_CHANGES=$(git -C "$REPO_ROOT" status --porcelain --untracked-files=no)
[ -z "$TRACKED_CHANGES" ] || {
  echo "Tracked working-tree changes are present. Commit/stash them before preparing exact-source acceptance evidence." >&2
  printf '%s\n' "$TRACKED_CHANGES" >&2
  exit 2
}

SOURCE_REVISION=$(git -C "$REPO_ROOT" rev-parse HEAD)
SOURCE_BRANCH=$(git -C "$REPO_ROOT" symbolic-ref --quiet --short HEAD 2>/dev/null || printf '%s' detached)
RUNTIME_VERSION=$(PYTHONPATH="$ROOT" python3 -c 'from goreecloud_care import __version__; print(__version__)')
[ "$RUNTIME_VERSION" = "$EXPECTED_RUNTIME_VERSION" ] || {
  echo "Representative 0.1.0 artifact qualification harness expects runtime $EXPECTED_RUNTIME_VERSION; got $RUNTIME_VERSION" >&2
  exit 2
}
grep -F 'lifecycle: release-candidate' "$ROOT/goreecloud.platform.yaml" >/dev/null || {
  echo "Representative 0.1.0 artifact preparation requires lifecycle: release-candidate." >&2
  exit 2
}
grep -F 'status: nonconformant' "$ROOT/goreecloud.platform.yaml" >/dev/null || {
  echo "0.1.0 artifact qualification must remain fail-closed until governed Stable promotion." >&2
  exit 2
}

INSTALLED_PROBE_DIR=$(mktemp -d)
cleanup() {
  rm -rf "$INSTALLED_PROBE_DIR"
}
trap cleanup EXIT INT TERM

mkdir -p "$OUT"

printf '%s\n' "Preparing read-only/non-destructive 0.1.0 golden artifact representative acceptance evidence."
printf '%s\n' "Source revision: $SOURCE_REVISION"
printf '%s\n' "Source branch:   $SOURCE_BRANCH"
printf '%s\n' "Runtime version: $RUNTIME_VERSION"
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
  echo "Representative 0.1.0 artifact harness expects package $EXPECTED_PACKAGE_VERSION; got $PACKAGE_VERSION" >&2
  exit 2
}
sha256sum "$PACKAGE" > "$OUT/package.sha256"
PACKAGE_SHA256=$(awk '{print $1}' "$OUT/package.sha256")

cat > "$OUT/SOURCE_REVISION" <<EOF
source_revision=$SOURCE_REVISION
source_branch=$SOURCE_BRANCH
lifecycle=release-candidate
artifact_version=0.1.0
stable_promotion_authorized=false
runtime_version=$RUNTIME_VERSION
package_version=$PACKAGE_VERSION
package_sha256=$PACKAGE_SHA256
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
      "Installed Care runtime differs from the exact 0.1.0 artifact candidate; candidate-only status snapshots were skipped." \
      > "$OUT/installed-status-snapshots-skipped.txt"
  fi
else
  printf '%s\n' "GoreeCloud Care is not currently installed; installed read-only status snapshots were skipped." > "$OUT/installed-version.txt"
  printf '%s\n' "No installed Care executable was found; candidate-only status snapshots were skipped." > "$OUT/installed-status-snapshots-skipped.txt"
fi

cat > "$OUT/MANUAL-CHECKLIST.txt" <<'EOF'
GoreeCloud Care 0.1.0 golden artifact — representative-device checklist
=====================================================================

Record PASS or FAIL plus notes for every exercised item. A blank item is NOT accepted evidence.
Do not use unrelated personal files for destructive-flow testing; use disposable fixtures/test data.
This checklist does not authorize Stable promotion by itself.

Lifecycle note: the artifact version is 0.1.0, but the governed source lifecycle remains Release Candidate / nonconformant until exact-source package, physical-target, platform-system, Glaze, and governance evidence are complete. GLAZE UI V1.2 / 1.2.0 remains the Stable compatibility baseline; V1.3 Adaptive Resonance remains Proposed / consumer-ineligible.

A. 0.1.0 identity delta
[ ] PASS [ ] FAIL  Main window title is GoreeCloud Care without Development/Release Candidate branding.
[ ] PASS [ ] FAIL  Main header subtitle reads Local maintenance • Adaptive Resonance preview and does not imply V1.3 conformance.
[ ] PASS [ ] FAIL  Maintenance Insights subtitle reads Read-only local review.
[ ] PASS [ ] FAIL  Launcher/AppStream surfaces show GoreeCloud Care and the canonical Care icon without clipping or stale RC labels.
Notes:

B. Regression bridge from the accepted RC
[ ] PASS [ ] FAIL  Large-text and continuous resize remain usable.
[ ] PASS [ ] FAIL  Forward/reverse keyboard traversal and visible focus remain correct.
[ ] PASS [ ] FAIL  Orca completion/cancellation/failure and Maintenance Insights status announcements remain understandable and truthful.
[ ] PASS [ ] FAIL  System Light, Dark, HighContrast, Reduced Transparency, Reduced Motion, Show Borders, expression, clarity, and preview Deep Dark remain optically usable.
[ ] PASS [ ] FAIL  Scan is read-only; routine cleanup, Trash, APT, and memory-cache flows preserve their accepted confirmation/cancellation/failure/success semantics.
Notes:

C. Package lifecycle / continuity
[ ] PASS [ ] FAIL  Exact 0.1.0 package checksum/provenance matches the qualified source.
[ ] PASS [ ] FAIL  Installed application/helper cannot be shadowed by the source working directory and leaves no private bytecode cache.
[ ] PASS [ ] FAIL  install/remove/reinstall/dev17-downgrade/0.1.0-restore/final-state probe passed.
Candidate package:
Previous package:
Lifecycle log/evidence:

D. Platform-system acceptance
[ ] PASS [ ] FAIL  Privacy Shield exact-0.1.0 runtime/application review complete; production approval is governed externally.
[ ] PASS [ ] FAIL  Wardveil exact-0.1.0 scoped adoption/runtime review complete; no broad protection claim is inferred.
[ ] PASS [ ] FAIL  Everkeep exact-0.1.0 continuity evidence is complete and package provenance matches.
[ ] PASS [ ] FAIL  Glaze V1.2 exact-0.1.0 consumer acceptance/bridge is governed; V1.3 remains Proposed / consumer-ineligible.
Notes:
EOF

cat > "$OUT/MANUAL-COMMANDS.txt" <<'EOF'
goreecloud-care
GDK_DPI_SCALE=2 goreecloud-care --insights-ui
GTK_THEME=HighContrast goreecloud-care
GOREECLOUD_CARE_APPEARANCE=dark goreecloud-care
GOREECLOUD_CARE_APPEARANCE=deep-dark goreecloud-care
GOREECLOUD_CARE_REDUCE_TRANSPARENCY=1 goreecloud-care
GOREECLOUD_CARE_REDUCE_MOTION=1 goreecloud-care
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

sh ./scripts/build-dev17-rollback-package.sh
sh ./scripts/validate-package-lifecycle.sh ./dist/goreecloud-care_0.1.0_all.deb ./dist/rollback/goreecloud-care_0.1.0~dev17_all.deb
EOF

printf '%s\n' "0.1.0 golden artifact representative acceptance preparation: passed"
printf '%s\n' "Package: $PACKAGE_VERSION"
printf '%s\n' "SHA-256: $PACKAGE_SHA256"
printf '%s\n' "Manual checklist: $OUT/MANUAL-CHECKLIST.txt"
printf '%s\n' "Manual commands:  $OUT/MANUAL-COMMANDS.txt"
printf '%s\n' "Stable promotion authorized: false"
