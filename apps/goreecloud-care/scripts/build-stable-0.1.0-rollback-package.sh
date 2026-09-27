#!/bin/sh
set -eu

ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
REPO_ROOT=$(CDPATH= cd -- "$ROOT/../.." && pwd)
OUT=${1:-"$ROOT/dist/rollback"}
STABLE_REVISION="bbc4779454c2887b810aa0ddc9e8a686a4c68ebd"
EXPECTED_VERSION="0.1.0"
EXPECTED_SHA256="819cff6e0132bf6b09df0986682995c25b14c39e74982f725efd0b5a21b71160"
EXPECTED_PACKAGE="$OUT/goreecloud-care_${EXPECTED_VERSION}_all.deb"

for command_name in git sh dpkg-deb sha256sum awk mktemp mkdir rm; do
  command -v "$command_name" >/dev/null || {
    echo "Required command not found: $command_name" >&2
    exit 2
  }
done

git -C "$REPO_ROOT" cat-file -e "$STABLE_REVISION^{commit}" 2>/dev/null || {
  echo "The immutable Stable 0.1.0 source revision is not present locally: $STABLE_REVISION" >&2
  echo "Fetch the GoreeCloud Care history before preparing rollback evidence." >&2
  exit 2
}

mkdir -p "$OUT"
WORKTREE_PARENT=$(mktemp -d)
WORKTREE="$WORKTREE_PARENT/stable-0.1.0"
cleanup() {
  if [ -e "$WORKTREE/.git" ] || [ -f "$WORKTREE/.git" ]; then
    git -C "$REPO_ROOT" worktree remove --force "$WORKTREE" >/dev/null 2>&1 || true
  fi
  rm -rf "$WORKTREE_PARENT"
}
trap cleanup EXIT INT TERM

printf '%s\n' "Building the immutable Stable 0.1.0 rollback package."
printf '%s\n' "Source revision: $STABLE_REVISION"
printf '%s\n' "Expected package version: $EXPECTED_VERSION"
printf '%s\n' "Expected SHA-256: $EXPECTED_SHA256"
printf '%s\n' "This helper does not install/remove packages, invoke Care cleanup, or access the network."

git -C "$REPO_ROOT" worktree add --detach "$WORKTREE" "$STABLE_REVISION" >/dev/null
CARE_ROOT="$WORKTREE/apps/goreecloud-care"
[ -d "$CARE_ROOT" ] || {
  echo "Care source not found in Stable 0.1.0 worktree" >&2
  exit 1
}

sh "$CARE_ROOT/scripts/build-deb.sh" "$OUT"
[ -f "$EXPECTED_PACKAGE" ] || {
  echo "Expected Stable rollback package was not produced: $EXPECTED_PACKAGE" >&2
  exit 1
}

actual_version=$(dpkg-deb -f "$EXPECTED_PACKAGE" Version)
[ "$actual_version" = "$EXPECTED_VERSION" ] || {
  echo "Stable rollback package version mismatch: expected=$EXPECTED_VERSION actual=$actual_version" >&2
  exit 1
}

actual_sha=$(sha256sum "$EXPECTED_PACKAGE" | awk '{print $1}')
[ "$actual_sha" = "$EXPECTED_SHA256" ] || {
  echo "Stable rollback package bytes do not match the accepted immutable 0.1.0 artifact." >&2
  echo "Expected SHA-256: $EXPECTED_SHA256" >&2
  echo "Actual SHA-256:   $actual_sha" >&2
  exit 1
}

sha256sum "$EXPECTED_PACKAGE" > "$OUT/goreecloud-care_${EXPECTED_VERSION}.sha256"
cat > "$OUT/goreecloud-care_${EXPECTED_VERSION}.SOURCE_REVISION" <<EOF
source_revision=$STABLE_REVISION
package_version=$EXPECTED_VERSION
package_sha256=$EXPECTED_SHA256
purpose=stable-0.1.0-rollback-for-0.2-development
EOF

printf '%s\n' "Stable 0.1.0 rollback package preparation: passed"
printf '%s\n' "Package: $EXPECTED_PACKAGE"
printf '%s\n' "Checksum: $OUT/goreecloud-care_${EXPECTED_VERSION}.sha256"
printf '%s\n' "Provenance: $OUT/goreecloud-care_${EXPECTED_VERSION}.SOURCE_REVISION"
