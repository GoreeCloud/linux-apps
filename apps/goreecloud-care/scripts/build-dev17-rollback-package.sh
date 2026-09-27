#!/bin/sh
set -eu

ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
REPO_ROOT=$(CDPATH= cd -- "$ROOT/../.." && pwd)
OUT=${1:-"$ROOT/dist/rollback"}
case "$OUT" in
  /*) ;;
  *) OUT="$ROOT/$OUT" ;;
esac

DEV17_SOURCE_REVISION="0fda6f90a545eaf3d1bed525aae98c6529ebbf7b"
DEV17_ARCHIVE_REVISION="1a57ccd9b3311000c99e273877eff1af06b06b38"
DEV17_ARCHIVE_TREE="7168db501e9e2fd7ce23496f607ffe958ab4c835"
EXPECTED_VERSION="0.1.0~dev17"
EXPECTED_PACKAGE="$OUT/goreecloud-care_${EXPECTED_VERSION}_all.deb"

for command_name in git sh dpkg-deb sha256sum mktemp mkdir rm; do
  command -v "$command_name" >/dev/null || {
    echo "Required command not found: $command_name" >&2
    exit 2
  }
done

git -C "$REPO_ROOT" cat-file -e "$DEV17_ARCHIVE_REVISION^{commit}" 2>/dev/null || {
  echo "The immutable dev17 archive revision is not present in this local clone: $DEV17_ARCHIVE_REVISION" >&2
  echo "Check out this repository with complete branch history, including archive/care-dev17, then rerun this local-only builder." >&2
  exit 2
}

actual_archive_tree=$(git -C "$REPO_ROOT" rev-parse "$DEV17_ARCHIVE_REVISION^{tree}")
[ "$actual_archive_tree" = "$DEV17_ARCHIVE_TREE" ] || {
  echo "Dev17 archive tree mismatch: expected=$DEV17_ARCHIVE_TREE actual=$actual_archive_tree" >&2
  exit 2
}

mkdir -p "$OUT"
WORKTREE_PARENT=$(mktemp -d)
WORKTREE="$WORKTREE_PARENT/dev17"
cleanup() {
  if [ -e "$WORKTREE/.git" ] || [ -f "$WORKTREE/.git" ]; then
    git -C "$REPO_ROOT" worktree remove --force "$WORKTREE" >/dev/null 2>&1 || true
  fi
  rm -rf "$WORKTREE_PARENT"
}
trap cleanup EXIT INT TERM

printf '%s\n' "Building a local rollback package from the immutable accepted dev17 archive."
printf '%s\n' "Original source revision: $DEV17_SOURCE_REVISION"
printf '%s\n' "Archive revision: $DEV17_ARCHIVE_REVISION"
printf '%s\n' "Archive tree: $DEV17_ARCHIVE_TREE"
printf '%s\n' "Expected package version: $EXPECTED_VERSION"
printf '%s\n' "Output directory: $OUT"
printf '%s\n' "This helper does not install/remove packages, invoke Care cleanup, or access the network."

git -C "$REPO_ROOT" worktree add --detach "$WORKTREE" "$DEV17_ARCHIVE_REVISION" >/dev/null
CARE_ROOT="$WORKTREE/apps/goreecloud-care"
[ -d "$CARE_ROOT" ] || {
  echo "Care source not found in immutable dev17 archive worktree" >&2
  exit 1
}

sh "$CARE_ROOT/scripts/build-deb.sh" "$OUT"
[ -f "$EXPECTED_PACKAGE" ] || {
  echo "Expected rollback package not produced: $EXPECTED_PACKAGE" >&2
  exit 1
}

actual_version=$(dpkg-deb -f "$EXPECTED_PACKAGE" Version)
[ "$actual_version" = "$EXPECTED_VERSION" ] || {
  echo "Rollback package version mismatch: expected=$EXPECTED_VERSION actual=$actual_version" >&2
  exit 1
}

sha256sum "$EXPECTED_PACKAGE" > "$OUT/goreecloud-care_${EXPECTED_VERSION}.sha256"
cat > "$OUT/goreecloud-care_${EXPECTED_VERSION}.SOURCE_REVISION" <<EOF
source_revision=$DEV17_SOURCE_REVISION
archive_revision=$DEV17_ARCHIVE_REVISION
archive_tree=$DEV17_ARCHIVE_TREE
package_version=$EXPECTED_VERSION
purpose=representative-development-rollback
EOF

printf '%s\n' "Dev17 rollback package preparation: passed"
printf '%s\n' "Package: $EXPECTED_PACKAGE"
printf '%s\n' "Checksum: $OUT/goreecloud-care_${EXPECTED_VERSION}.sha256"
printf '%s\n' "Provenance: $OUT/goreecloud-care_${EXPECTED_VERSION}.SOURCE_REVISION"
