#!/bin/sh
set -eu

ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
REPO_ROOT=$(CDPATH= cd -- "$ROOT/../.." && pwd)
OUT=${1:-"$ROOT/dist/representative-runtime"}
EXPECTED_RUNTIME_VERSION="0.1.0"
EXPECTED_PACKAGE_VERSION="0.1.0"
CANDIDATE="$ROOT/dist/goreecloud-care_${EXPECTED_PACKAGE_VERSION}_all.deb"
ROLLBACK_DIR="$ROOT/dist/rollback"
ROLLBACK="$ROLLBACK_DIR/goreecloud-care_0.1.0~dev17_all.deb"
INSTALLED_PROVENANCE="/usr/share/goreecloud-care/build-provenance.json"
REPRESENTATIVE_RECORD="/var/lib/goreecloud-care/acceptance/representative-target.json"

[ "$(id -u)" -ne 0 ] || {
  echo "Run representative acceptance as the normal Zorin desktop user, not as root." >&2
  exit 2
}

for command_name in git python3 sha256sum dpkg-deb dpkg-query awk tee sudo install mkdir rm grep; do
  command -v "$command_name" >/dev/null || {
    echo "Required command not found: $command_name" >&2
    exit 2
  }
done

if [ ! -r /etc/os-release ]; then
  echo "Unable to identify the representative operating system." >&2
  exit 2
fi
# shellcheck disable=SC1091
. /etc/os-release
case "${PRETTY_NAME:-}" in
  *"Zorin OS 17.3"*) ;;
  *)
    echo "Representative acceptance requires Zorin OS 17.3; detected: ${PRETTY_NAME:-unknown}" >&2
    exit 2
    ;;
esac

TRACKED_CHANGES=$(git -C "$REPO_ROOT" status --porcelain --untracked-files=no -- apps/goreecloud-care .github/workflows/care-ci.yml)
[ -z "$TRACKED_CHANGES" ] || {
  echo "Tracked Care/CI changes are present. Commit or stash them before exact-candidate acceptance." >&2
  printf '%s\n' "$TRACKED_CHANGES" >&2
  exit 2
}

SOURCE_REVISION=$(git -C "$REPO_ROOT" rev-parse HEAD)
SOURCE_TREE=$(git -C "$REPO_ROOT" rev-parse HEAD:apps/goreecloud-care)
SOURCE_BRANCH=$(git -C "$REPO_ROOT" symbolic-ref --quiet --short HEAD 2>/dev/null || printf '%s' detached)
RUNTIME_VERSION=$(PYTHONPATH="$ROOT" python3 -c 'from goreecloud_care import __version__; print(__version__)')
[ "$RUNTIME_VERSION" = "$EXPECTED_RUNTIME_VERSION" ] || {
  echo "Expected Care runtime $EXPECTED_RUNTIME_VERSION; got $RUNTIME_VERSION" >&2
  exit 2
}

grep -F 'lifecycle: release-candidate' "$ROOT/goreecloud.platform.yaml" >/dev/null || {
  echo "Representative 0.1.0 artifact acceptance requires lifecycle: release-candidate in goreecloud.platform.yaml." >&2
  exit 2
}
grep -F 'status: nonconformant' "$ROOT/goreecloud.platform.yaml" >/dev/null || {
  echo "Representative 0.1.0 artifact acceptance must remain nonconformant until separate governed Stable promotion." >&2
  exit 2
}

mkdir -p "$OUT"
rm -f \
  "$OUT/source-validation.log" \
  "$OUT/reproducible-package.log" \
  "$OUT/rollback-package.log" \
  "$OUT/package-lifecycle.log" \
  "$OUT/package.sha256" \
  "$OUT/representative-target.json" \
  "$OUT/continuity-without-governance.json" \
  "$OUT/continuity-installed.json" \
  "$OUT/SOURCE_REVISION"

printf '%s\n' "GoreeCloud Care exact 0.1.0 golden artifact representative-target acceptance"
printf '%s\n' "Target:          ${PRETTY_NAME}"
printf '%s\n' "Source branch:   $SOURCE_BRANCH"
printf '%s\n' "Source revision: $SOURCE_REVISION"
printf '%s\n' "Source tree:     $SOURCE_TREE"
printf '%s\n' "Runtime:         $RUNTIME_VERSION"
printf '%s\n' "Governed lifecycle: Release Candidate"
printf '%s\n' "This runner performs package install/remove/reinstall/downgrade/restore through the existing lifecycle probe."
printf '%s\n' "It never invokes a Care cleanup action and never writes or promotes an Everkeep governance record."
printf '%s\n' "Stable promotion is not authorized by this runner."

(
  cd "$ROOT"
  sh ./scripts/validate.sh
) 2>&1 | tee "$OUT/source-validation.log"

LOCAL_TESTS=$(awk '/^Ran [0-9]+ tests? in / { count=$2 } END { if (!count) exit 1; print count }' "$OUT/source-validation.log") || {
  echo "Unable to derive the exact local unit-test count from source validation." >&2
  exit 1
}
case "$LOCAL_TESTS" in
  ''|*[!0-9]*) echo "Invalid local test count: $LOCAL_TESTS" >&2; exit 1 ;;
esac
[ "$LOCAL_TESTS" -gt 0 ]

(
  cd "$ROOT"
  sh ./scripts/build-deb.sh dist
) 2>&1 | tee "$OUT/package-build.log"
[ -f "$CANDIDATE" ] || {
  echo "Expected candidate package not found: $CANDIDATE" >&2
  exit 1
}
[ "$(dpkg-deb -f "$CANDIDATE" Version)" = "$EXPECTED_PACKAGE_VERSION" ]

(
  cd "$ROOT"
  sh ./scripts/verify-reproducible-package.sh "$CANDIDATE"
) 2>&1 | tee "$OUT/reproducible-package.log"

grep -F 'Reproducible package verification: passed' "$OUT/reproducible-package.log" >/dev/null
sha256sum "$CANDIDATE" > "$OUT/package.sha256"
PACKAGE_SHA256=$(awk '{print $1}' "$OUT/package.sha256")
printf '%s\n' "$PACKAGE_SHA256" | grep -Eq '^[0-9a-f]{64}$'

(
  cd "$ROOT"
  sh ./scripts/build-dev17-rollback-package.sh "$ROLLBACK_DIR"
) 2>&1 | tee "$OUT/rollback-package.log"
[ -f "$ROLLBACK" ] || {
  echo "Expected accepted dev17 rollback package not found: $ROLLBACK" >&2
  exit 1
}

(
  cd "$ROOT"
  sh ./scripts/validate-package-lifecycle.sh "$CANDIDATE" "$ROLLBACK"
) 2>&1 | tee "$OUT/package-lifecycle.log"
grep -F 'Representative package install/remove/reinstall/downgrade/rollback acceptance: passed' "$OUT/package-lifecycle.log" >/dev/null

installed=$(dpkg-query -W -f='${Status} ${Version}' goreecloud-care)
[ "$installed" = "install ok installed $EXPECTED_PACKAGE_VERSION" ] || {
  echo "Final installed package state is not the exact candidate: $installed" >&2
  exit 1
}
[ "$(goreecloud-care --version)" = "$EXPECTED_RUNTIME_VERSION" ]
[ -f "$INSTALLED_PROVENANCE" ] || {
  echo "Installed exact-source provenance is missing: $INSTALLED_PROVENANCE" >&2
  exit 1
}

python3 - "$INSTALLED_PROVENANCE" "$SOURCE_REVISION" "$SOURCE_TREE" "$EXPECTED_RUNTIME_VERSION" "$EXPECTED_PACKAGE_VERSION" <<'PY'
import json
import sys
from pathlib import Path

path, revision, tree, runtime_version, package_version = sys.argv[1:]
payload = json.loads(Path(path).read_text(encoding="utf-8"))
assert payload["schema_version"] == 1
assert payload["application"] == "GoreeCloud Care"
assert payload["producer"] == "GoreeCloud/goreecloud-zorin-os/apps/goreecloud-care"
assert payload["source_revision"] == revision
assert payload["source_tree"] == tree
assert payload["runtime_version"] == runtime_version
assert payload["package_version"] == package_version
assert payload["package_sha256_embedded"] is False
PY

cat > "$OUT/SOURCE_REVISION" <<EOF
source_revision=$SOURCE_REVISION
source_tree=$SOURCE_TREE
source_branch=$SOURCE_BRANCH
lifecycle=release-candidate
artifact_version=0.1.0
stable_promotion_authorized=false
runtime_version=$EXPECTED_RUNTIME_VERSION
package_version=$EXPECTED_PACKAGE_VERSION
package_sha256=$PACKAGE_SHA256
representative_target=${PRETTY_NAME}
local_tests=$LOCAL_TESTS
source_validation=passed
reproducible_package_verification=passed
package_lifecycle=passed
everkeep_integration_promoted=false
everkeep_ready_promoted=false
EOF

python3 - "$OUT/representative-target.json" \
  "$SOURCE_REVISION" "$SOURCE_TREE" "$EXPECTED_RUNTIME_VERSION" \
  "$EXPECTED_PACKAGE_VERSION" "$PACKAGE_SHA256" "$LOCAL_TESTS" "$PRETTY_NAME" <<'PY'
import json
import sys
from pathlib import Path

(
    output,
    revision,
    tree,
    runtime_version,
    package_version,
    package_sha256,
    local_tests,
    target_name,
) = sys.argv[1:]
payload = {
    "schema_version": 1,
    "application": "GoreeCloud Care",
    "producer": "GoreeCloud/goreecloud-zorin-os/apps/goreecloud-care",
    "candidate": {
        "source_revision": revision,
        "source_tree": tree,
        "runtime_version": runtime_version,
        "package_version": package_version,
        "package_sha256": package_sha256,
    },
    "target": {
        "name": target_name,
        "representative": True,
        "status": "passed",
    },
    "dimensions": [
        "restore_capability",
        "migration",
        "documentation",
        "provenance",
    ],
    "evidence": {
        "local_tests": int(local_tests),
        "source_validation": "passed",
        "package_lifecycle": "passed",
        "references": [
            "source-validation.log",
            "reproducible-package.log",
            "package-lifecycle.log",
            "installed package-owned build-provenance.json",
        ],
    },
    "acceptance": {
        "target_runtime_status": "passed",
        "exact_revision_accepted": True,
        "everkeep_integration_promoted": False,
        "everkeep_ready_promoted": False,
        "freshness_rule": (
            "This Care-produced representative-target record applies only to the exact source revision, "
            "Care source tree, package version, package SHA-256, and representative target named here. "
            "It is target evidence only and cannot grant Everkeep integration, Everkeep readiness, or Stable promotion."
        ),
    },
}
Path(output).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
PY

sudo install -d -o root -g root -m 0755 /var/lib/goreecloud-care
sudo install -d -o root -g root -m 0755 /var/lib/goreecloud-care/acceptance
sudo install -o root -g root -m 0644 "$OUT/representative-target.json" "$REPRESENTATIVE_RECORD"

PYTHONPATH="$ROOT" python3 - "$OUT/continuity-without-governance.json" <<'PY'
import json
import sys
from pathlib import Path
from goreecloud_care.platform_status import build_continuity_status

payload = build_continuity_status(everkeep_acceptance_path="/nonexistent/goreecloud-care-everkeep.json")
assert payload["state"] == "attention"
assert payload["stage"] == "target-accepted-governance-pending"
assert payload["evidence_reference"] == "file:///var/lib/goreecloud-care/acceptance/representative-target.json"
assert payload["limitations"]
Path(sys.argv[1]).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
PY

goreecloud-care --continuity-status-json > "$OUT/continuity-installed.json"

printf '%s\n' "Representative 0.1.0 golden artifact target acceptance: passed"
printf '%s\n' "Local tests: $LOCAL_TESTS"
printf '%s\n' "Candidate SHA-256: $PACKAGE_SHA256"
printf '%s\n' "Care-owned target handoff: $OUT/representative-target.json"
printf '%s\n' "Protected local target handoff: $REPRESENTATIVE_RECORD"
printf '%s\n' "Everkeep promotion: not performed by this runner"
printf '%s\n' "Stable promotion authorized: false"
printf '%s\n' "The exact 0.1.0 golden artifact remains Release Candidate / nonconformant until separate platform governance, exact-source Glaze acceptance/bridge, immutable release evidence, and explicit governed Stable promotion are satisfied."
