#!/bin/sh
set -eu

ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
REPO_ROOT=$(CDPATH= cd -- "$ROOT/../.." && pwd)
OUT=${1:-"$ROOT/dist/representative-acceptance"}
EXPECTED_RUNTIME_VERSION="0.2.0-dev1"
EXPECTED_PACKAGE_VERSION="0.2.0~dev1"
EXPECTED_PACKAGE="$ROOT/dist/goreecloud-care_${EXPECTED_PACKAGE_VERSION}_all.deb"

for command_name in git python3 sha256sum dpkg-deb tee awk rm mktemp grep; do
  command -v "$command_name" >/dev/null || {
    echo "Required command not found: $command_name" >&2
    exit 2
  }
done

TRACKED_CHANGES=$(git -C "$REPO_ROOT" status --porcelain --untracked-files=no -- apps/goreecloud-care .github/workflows/care-ci.yml)
[ -z "$TRACKED_CHANGES" ] || {
  echo "Tracked Care/CI changes are present. Commit/stash them before preparing exact-source V1.4 acceptance evidence." >&2
  printf '%s\n' "$TRACKED_CHANGES" >&2
  exit 2
}

SOURCE_REVISION=$(git -C "$REPO_ROOT" rev-parse HEAD)
SOURCE_BRANCH=$(git -C "$REPO_ROOT" symbolic-ref --quiet --short HEAD 2>/dev/null || printf '%s' detached)
RUNTIME_VERSION=$(PYTHONPATH="$ROOT" python3 -c 'from goreecloud_care import __version__; print(__version__)')
[ "$RUNTIME_VERSION" = "$EXPECTED_RUNTIME_VERSION" ] || {
  echo "Representative V1.4 harness expects runtime $EXPECTED_RUNTIME_VERSION; got $RUNTIME_VERSION" >&2
  exit 2
}
grep -Fx 'lifecycle: development' "$ROOT/goreecloud.platform.yaml" >/dev/null || {
  echo "Representative 0.2.0-dev1 preparation requires lifecycle: development." >&2
  exit 2
}
grep -F 'status: nonconformant' "$ROOT/goreecloud.platform.yaml" >/dev/null || {
  echo "0.2.0-dev1 must remain nonconformant until exact V1.4 and platform acceptance is promoted." >&2
  exit 2
}
grep -F 'glaze_ui_required: "1.4.0"' "$ROOT/goreecloud.platform.yaml" >/dev/null || {
  echo "Representative acceptance requires the Glaze UI 1.4.0 compatibility contract." >&2
  exit 2
}

INSTALLED_PROBE_DIR=$(mktemp -d)
cleanup() {
  rm -rf "$INSTALLED_PROBE_DIR"
}
trap cleanup EXIT INT TERM

mkdir -p "$OUT"

printf '%s\n' "Preparing read-only/non-destructive 0.2.0-dev1 Glaze UI V1.4 representative acceptance evidence."
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
  echo "Representative V1.4 harness expects package $EXPECTED_PACKAGE_VERSION; got $PACKAGE_VERSION" >&2
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
glaze_ui_target=1.4.0
glaze_ui_source_revision=01c86323f8b747373d308026adc8b0881855cdc5
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
      "Installed Care runtime differs from the exact 0.2.0-dev1 candidate; candidate-only status snapshots were skipped." \
      > "$OUT/installed-status-snapshots-skipped.txt"
  fi
else
  printf '%s\n' "GoreeCloud Care is not currently installed; installed read-only status snapshots were skipped." > "$OUT/installed-version.txt"
  printf '%s\n' "No installed Care executable was found; candidate-only status snapshots were skipped." > "$OUT/installed-status-snapshots-skipped.txt"
fi

cat > "$OUT/MANUAL-CHECKLIST.txt" <<'EOF'
GoreeCloud Care 0.2.0-dev1 — Glaze UI V1.4 representative-device checklist
============================================================================

Record PASS or FAIL plus notes for every exercised item. A blank item is NOT accepted evidence.
Do not use unrelated personal files for destructive-flow testing; use disposable fixtures/test data.
This checklist does not authorize Stable promotion by itself.

Lifecycle note: 0.2.0-dev1 / 0.2.0~dev1 is a Development / nonconformant candidate. Stable 0.1.0 remains immutable historical release evidence and does not transfer Glaze, Privacy Shield, Wardveil, Everkeep, or representative-device acceptance to this candidate.

A. V1.4 product identity and composition
[ ] PASS [ ] FAIL  Main window title is GoreeCloud Care and subtitle reads Local maintenance • Glaze UI V1.4.
[ ] PASS [ ] FAIL  Maintenance Insights subtitle reads Read-only local review.
[ ] PASS [ ] FAIL  Compact window preserves all maintenance tasks without clipping or hidden consequential actions.
[ ] PASS [ ] FAIL  Narrow Desktop uses a readable single-column composition with stable task order.
[ ] PASS [ ] FAIL  Desktop uses the intended canonical Care composition.
[ ] PASS [ ] FAIL  Wide Desktop adds breathing room/hierarchy without giant targets, stretched copy, or gratuitous empty panes.
[ ] PASS [ ] FAIL  Launcher/AppStream surfaces show GoreeCloud Care and the canonical Care icon without stale V1.2/V1.3/RC labels.
Notes:

B. Native, accessibility, and optical review
[ ] PASS [ ] FAIL  Large text and continuous resize remain usable across V1.4 form-factor transitions.
[ ] PASS [ ] FAIL  Forward/reverse keyboard traversal and visible focus remain correct before and after resizing.
[ ] PASS [ ] FAIL  Orca scan/completion/cancellation/failure and Maintenance Insights announcements are understandable and truthful.
[ ] PASS [ ] FAIL  Light, Dark, Deep Dark, and HighContrast remain optically usable on the physical Zorin desktop.
[ ] PASS [ ] FAIL  Reduced Transparency, Reduced Motion, and Show Borders remove embellishment before meaning/focus/hierarchy.
[ ] PASS [ ] FAIL  Functional-glass chrome feels intentional; reading/status/findings/consequential surfaces remain stable and legible.
[ ] PASS [ ] FAIL  Native window controls/compositor behavior are polished and do not conflict with the Care shell.
Notes:

C. Maintenance safety regression
[ ] PASS [ ] FAIL  Scan is read-only and previews current maintenance state.
[ ] PASS [ ] FAIL  Routine cleanup preserves selection, confirmation, cancellation, failure, and success semantics.
[ ] PASS [ ] FAIL  Empty Trash remains explicitly permanent and confirmation-first.
[ ] PASS [ ] FAIL  APT and file-cache privileged flows preserve confirmation, PolicyKit cancellation, failure, and success truthfulness.
Notes:

D. 0.2 package lifecycle / continuity
[ ] PASS [ ] FAIL  Exact 0.2.0~dev1 package checksum/provenance matches the candidate source.
[ ] PASS [ ] FAIL  Candidate application/helper cannot be shadowed by the source working directory and leaves no private bytecode cache.
[ ] PASS [ ] FAIL  install/remove/reinstall/Stable-0.1.0-downgrade/0.2.0~dev1-restore/final-state probe passed.
[ ] PASS [ ] FAIL  Stable rollback package SHA-256 is exactly 819cff6e0132bf6b09df0986682995c25b14c39e74982f725efd0b5a21b71160.
Candidate package:
Stable rollback package:
Lifecycle log/evidence:

E. Platform-system acceptance boundaries
[ ] PASS [ ] FAIL  Glaze UI V1.4 exact-candidate human/native consumer review is complete for this exact source/package identity.
[ ] PASS [ ] FAIL  Privacy Shield exact-0.2 candidate runtime/application review is complete; production approval remains externally governed.
[ ] PASS [ ] FAIL  Wardveil exact-0.2 scoped adoption/runtime review is complete; no broad protection claim is inferred.
[ ] PASS [ ] FAIL  Everkeep exact-0.2 continuity evidence is complete and exact package provenance matches.
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
sh ./scripts/validate-package-lifecycle.sh './dist/goreecloud-care_0.2.0~dev1_all.deb' './dist/rollback/goreecloud-care_0.1.0_all.deb'
EOF

printf '%s\n' "0.2.0-dev1 Glaze UI V1.4 representative acceptance preparation: passed"
printf '%s\n' "Package: $PACKAGE_VERSION"
printf '%s\n' "SHA-256: $PACKAGE_SHA256"
printf '%s\n' "Manual checklist: $OUT/MANUAL-CHECKLIST.txt"
printf '%s\n' "Manual commands:  $OUT/MANUAL-COMMANDS.txt"
printf '%s\n' "Stable promotion authorized: false"
